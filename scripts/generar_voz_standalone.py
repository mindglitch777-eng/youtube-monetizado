"""Genera la narración (edge-tts) de un short 100% animado en Remotion — sin
imágenes IA: tipografía cinética, íconos SVG y clips reales, armados a mano
en un componente de Remotion propio de ese video.

Uso:
    python scripts/generar_voz_standalone.py content/<nombre-short>/guion.md [--forzar]

Lee las líneas narradas de la sección "## Guion narrado" del guion (una
línea de texto = una unidad narrada), sintetiza toda la narración en una
sola llamada a edge-tts y reparte los tiempos de palabra de vuelta a cada
línea. Escribe audio/narracion.mp3 y timeline.json (un segmento por línea,
con su propio array de palabras cronometradas — el mapeo visual línea por
línea vive en el componente de Remotion, no acá).

Corre en GitHub Actions (.github/workflows/generar-voz-standalone.yml):
Microsoft bloquea edge-tts desde el entorno de Claude Code.

RULES.md: Edge-TTS se usa solo en fase de prueba; antes de publicar
contenido monetizado la voz migra a una opción con licencia comercial.
"""

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path

from generar_audio import normalizar_palabra, sintetizar
from segmentos import RAIZ, cargar_env, checkpoint

MARCADOR = re.compile(r"^\s*formato\s*:\s*standalone-animado\s*$", re.IGNORECASE)
ENCABEZADO_GUION = re.compile(r"^##\s*guion\s+narrado\s*$", re.IGNORECASE)
NEGRITA = re.compile(r"\*\*(.+?)\*\*")
COLA_FINAL = 1.5  # segundos después de la última palabra (para el sting de cierre)


def leer_lineas(ruta):
    texto = Path(ruta).read_text(encoding="utf-8")
    if not MARCADOR.search(texto.splitlines()[0] if texto.splitlines() else ""):
        sys.exit(f"{ruta} no empieza con 'Formato: standalone-animado'.")
    # Los bloques de comentario HTML (documentación) no son parte del guion.
    texto = re.sub(r"<!--.*?-->", "", texto, flags=re.DOTALL)
    lineas_archivo = texto.splitlines()

    dentro = False
    lineas = []
    for cruda in lineas_archivo:
        cruda = cruda.strip()
        if ENCABEZADO_GUION.match(cruda):
            dentro = True
            continue
        if not dentro:
            continue
        if cruda.startswith("#"):
            break  # siguiente sección: fin del guion narrado
        if not cruda:
            continue
        negritas = NEGRITA.findall(cruda)
        lineas.append({
            "numero": len(lineas) + 1,
            "texto": cruda.replace("**", ""),
            "destacada": negritas[0] if negritas else None,
        })
    if not lineas:
        sys.exit(f"{ruta}: no encontré ninguna línea narrada bajo '## Guion narrado'.")
    return lineas


def repartir_palabras(lineas, palabras):
    """Asigna cada palabra sintetizada a su línea de origen (mismo algoritmo que
    generar_short.py: recorre los tokens del guion en orden, tolerando signos
    sueltos y palabras con guion que edge-tts entrega partidas)."""
    tokens = [(linea["numero"], t) for linea in lineas for t in linea["texto"].split()]
    i = 0
    resultado = []
    for palabra in palabras:
        while i < len(tokens) and not re.search(r"\w", tokens[i][1]):
            if resultado and resultado[-1]["linea"] == tokens[i][0]:
                resultado[-1]["texto"] += " " + tokens[i][1]
            i += 1
        buscada = normalizar_palabra(palabra["texto"])
        if resultado and i and buscada and buscada in normalizar_palabra(tokens[i - 1][1]) \
                and not (i < len(tokens) and buscada in normalizar_palabra(tokens[i][1])):
            resultado[-1]["fin"] = palabra["fin"]
            continue
        for j in range(i, min(i + 5, len(tokens))):
            if buscada and buscada in normalizar_palabra(tokens[j][1]):
                palabra["linea"], palabra["texto"] = tokens[j][0], tokens[j][1]
                i = j + 1
                break
        else:
            palabra["linea"] = tokens[i - 1][0] if i else 1
        resultado.append(palabra)
    return resultado


async def main_async(args):
    ruta = Path(args.guion).resolve()
    carpeta = ruta.parent
    lineas = leer_lineas(ruta)
    cargar_env()
    voz = os.environ.get("EDGE_TTS_VOICE", "en-US-JennyNeural")

    (carpeta / "audio").mkdir(exist_ok=True)
    mp3 = carpeta / "audio" / "narracion.mp3"
    meta = carpeta / "audio" / "narracion.json"
    texto_completo = " ".join(linea["texto"] for linea in lineas)

    datos = json.loads(meta.read_text(encoding="utf-8")) if meta.exists() else None
    if args.forzar or not mp3.exists() or not datos or datos.get("texto") != texto_completo \
            or datos.get("voz") != voz:
        print("Generando la narración con edge-tts ...", flush=True)
        datos = await sintetizar(texto_completo, voz, mp3)
        datos.update(texto=texto_completo, voz=voz)
    datos["palabras"] = repartir_palabras(lineas, [dict(p) for p in datos["palabras"]])
    meta.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    checkpoint("Checkpoint: narración standalone generada (edge-tts)")

    palabras = datos["palabras"]
    inicios = {}
    for p in palabras:
        inicios.setdefault(p["linea"], p["inicio"])
    fin_narracion = palabras[-1]["fin"]
    duracion_total = round(fin_narracion + COLA_FINAL, 3)

    segmentos = []
    for n, linea in enumerate(lineas, 1):
        inicio = inicios.get(n, 0.0)
        siguiente = inicios.get(n + 1, duracion_total)
        propias = [dict(p, inicio=round(p["inicio"] - inicio, 3), fin=round(p["fin"] - inicio, 3))
                   for p in palabras if p["linea"] == n]
        destacada = None
        if linea["destacada"]:
            buscada = normalizar_palabra(linea["destacada"].split()[0])
            destacada = next((k for k, p in enumerate(propias)
                              if normalizar_palabra(p["texto"].split()[0]) == buscada), None)
        segmentos.append({
            "n": n,
            "texto": linea["texto"],
            "inicio": round(inicio, 3),
            "duracion": round(siguiente - inicio, 3),
            "palabras": propias,
            "destacada": destacada,
        })

    salida = {
        "video": carpeta.relative_to(RAIZ).as_posix(),
        "voz": voz,
        "formato": "standalone-animado",
        "audio": mp3.relative_to(RAIZ).as_posix(),
        "duracionNarracion": round(fin_narracion, 3),
        "duracionTotal": duracion_total,
        "segmentos": segmentos,
    }
    (carpeta / "timeline.json").write_text(
        json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")
    checkpoint("Checkpoint: timeline.json standalone actualizado")

    print(f"\n{'línea':>5} {'inicio':>7}  texto")
    for s in segmentos:
        print(f"{s['n']:>5} {s['inicio']:>6.2f}s  {s['texto']}")
    print(f"\nNarración: {fin_narracion:.2f} s. Duración total: {duracion_total:.2f} s.")
    print(f"Timeline: {carpeta / 'timeline.json'}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("guion")
    parser.add_argument("--forzar", action="store_true")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
