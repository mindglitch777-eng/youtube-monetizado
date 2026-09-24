"""Produce un short standalone: voz (edge-tts), escenas (Cloudflare) y timeline.json.

Uso:
    python scripts/generar_short.py content/<nombre-short>/guion.md [opciones]

Opciones:
    --forzar        Regenera la voz y todas las imágenes aunque ya existan.
    --sin-imagenes  Solo voz y timeline (por ejemplo, si faltan las credenciales).

El guion empieza con "Formato: short" y se divide en "# Escena N". Cada línea de
texto es una línea narrada (la palabra en **negrita** se resalta en el
subtítulo); cada escena lleva un comentario "imagen:" con la descripción de la
imagen y "variante:" (media, fria o calida). No pasa por validar_guion.py: no
es un video largo de 6 bloques.

La narración se genera en una sola llamada a edge-tts (entonación continua) y
los tiempos de cada línea salen de los tiempos de sus palabras. Resultado:
    audio/narracion.mp3 + audio/narracion.json
    imagenes/escena-N.jpg (una por escena, estilo de PROMPTS.md)
    timeline.json (formato "short", para la composición Short de Remotion)
"""

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path

from generar_audio import KNOT_ICONO, SONIDOS, normalizar_palabra, sintetizar
from generar_imagenes import ESTILO, VARIANTE_POR_TIPO, generar
from segmentos import RAIZ, cargar_env

VARIANTES = {
    "media": "",
    "fria": VARIANTE_POR_TIPO["ejemplo"],   # Cuerpo: frío y cerrado
    "calida": VARIANTE_POR_TIPO["pago"],    # Pago: cálido y abierto
}
COLA_FINAL = 1.5      # segundos después de la última palabra para el sting
ADELANTO_WHOOSH = 0.25  # el whoosh arranca un poco antes del corte de escena
MAX_SEGUNDOS = 60     # RULES.md, sección Shorts

COMENTARIO = re.compile(r"<!--(.*?)-->", re.DOTALL)
ESCENA = re.compile(r"^#\s+escena\s+(\d+)\s*$", re.IGNORECASE)


def leer_short(ruta):
    texto = Path(ruta).read_text(encoding="utf-8")
    if not re.match(r"\s*formato\s*:\s*short\b", texto, re.IGNORECASE):
        sys.exit(f"{ruta} no empieza con 'Formato: short'.")
    # Los comentarios de varias líneas (documentación) no forman parte del guion.
    texto = re.sub(r"<!--(?:(?!-->)[^\n])*\n.*?-->", "", texto, flags=re.DOTALL)

    escenas, lineas = [], []
    for crudo in texto.splitlines():
        crudo = crudo.strip()
        if m := ESCENA.match(crudo):
            escenas.append({"numero": int(m.group(1)), "imagen": "", "variante": "media",
                            "whoosh": False})
            continue
        if not escenas or not crudo:
            continue
        comentarios = [c.strip() for c in COMENTARIO.findall(crudo)]
        narrado = COMENTARIO.sub("", crudo).strip()
        if not narrado:  # línea que es solo un comentario de la escena
            for c in comentarios:
                clave, _, valor = c.partition(":")
                clave = clave.strip().lower()
                if clave == "imagen":
                    escenas[-1]["imagen"] = valor.strip()
                elif clave == "variante":
                    escenas[-1]["variante"] = valor.strip().lower()
                elif clave == "sonido" and valor.strip().lower() == "whoosh":
                    escenas[-1]["whoosh"] = True
            continue
        negritas = re.findall(r"\*\*(.+?)\*\*", narrado)
        lineas.append({
            "numero": len(lineas) + 1,
            "escena": escenas[-1]["numero"],
            "texto": narrado.replace("**", ""),
            "destacada": negritas[0] if negritas else None,
            "ding": any(re.match(r"sonido\s*:\s*ding\b", c, re.IGNORECASE) for c in comentarios),
        })
    for e in escenas:
        if not e["imagen"]:
            sys.exit(f"La escena {e['numero']} no tiene descripción de imagen.")
        if e["variante"] not in VARIANTES:
            sys.exit(f"Escena {e['numero']}: variante '{e['variante']}' desconocida.")
    return escenas, lineas


def armar_prompt(escena):
    variante = VARIANTES[escena["variante"]]
    variante = f" {variante}." if variante else ""
    # Sin "Avoid: ...": flux-1-schnell no entiende negaciones y termina dibujando
    # lo que se nombra (búhos, firmas). Ver generar_imagenes.py.
    return f"{ESTILO}{variante} {escena['imagen']}"


def repartir_palabras(lineas, palabras):
    """Asigna cada palabra del audio a su línea, recorriendo las palabras del texto."""
    tokens = [(linea["numero"], t) for linea in lineas for t in linea["texto"].split()]
    i = 0
    for palabra in palabras:
        buscada = normalizar_palabra(palabra["texto"])
        for j in range(i, min(i + 5, len(tokens))):
            if buscada and buscada in normalizar_palabra(tokens[j][1]):
                palabra["linea"], palabra["texto"] = tokens[j][0], tokens[j][1]
                i = j + 1
                break
        else:
            palabra["linea"] = tokens[i - 1][0] if i else 1
    return palabras


async def main_async(args):
    ruta = Path(args.guion).resolve()
    carpeta = ruta.parent
    escenas, lineas = leer_short(ruta)
    cargar_env()
    voz = os.environ.get("EDGE_TTS_VOICE", "en-US-JennyNeural")

    # --- Voz: una sola narración ---
    (carpeta / "audio").mkdir(exist_ok=True)
    mp3, meta = carpeta / "audio" / "narracion.mp3", carpeta / "audio" / "narracion.json"
    texto = " ".join(linea["texto"] for linea in lineas)
    datos = json.loads(meta.read_text(encoding="utf-8")) if meta.exists() else None
    if args.forzar or not mp3.exists() or not datos or datos.get("texto") != texto \
            or datos.get("voz") != voz:
        print("Generando la narración con edge-tts ...", flush=True)
        datos = await sintetizar(texto, voz, mp3)
        datos["palabras"] = repartir_palabras(lineas, datos["palabras"])
        datos.update(texto=texto, voz=voz)
        meta.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")

    # --- Imágenes: una por escena ---
    carpeta_img = carpeta / "imagenes"
    carpeta_img.mkdir(exist_ok=True)
    prompts = {f"escena-{e['numero']}": armar_prompt(e) for e in escenas}
    (carpeta_img / "prompts.json").write_text(
        json.dumps(prompts, ensure_ascii=False, indent=2), encoding="utf-8")
    cuenta, token = os.environ.get("CLOUDFLARE_ACCOUNT_ID"), os.environ.get("CLOUDFLARE_API_TOKEN")
    if not args.sin_imagenes and not (cuenta and token):
        print("! Faltan CLOUDFLARE_ACCOUNT_ID / CLOUDFLARE_API_TOKEN: no se generan imágenes.")
    for nombre, prompt in prompts.items():
        existentes = sorted(carpeta_img.glob(nombre + ".*"))
        if args.sin_imagenes or not (cuenta and token) or (existentes and not args.forzar):
            continue
        print(f"  {nombre} ...", flush=True)
        imagen = generar(cuenta, token, prompt)
        for viejo in existentes:
            viejo.unlink()
        extension = ".png" if imagen[:8] == b"\x89PNG\r\n\x1a\n" else ".jpg"
        (carpeta_img / (nombre + extension)).write_bytes(imagen)

    # --- Timeline: un segmento por línea ---
    palabras = datos["palabras"]
    inicios = {}
    for p in palabras:
        inicios.setdefault(p["linea"], p["inicio"])
    fin_narracion = palabras[-1]["fin"]
    duracion_total = round(fin_narracion + COLA_FINAL, 3)

    escena_de = {e["numero"]: e for e in escenas}
    imagenes = {}
    for e in escenas:
        encontradas = sorted(carpeta_img.glob(f"escena-{e['numero']}.*"))
        imagenes[e["numero"]] = encontradas[0].relative_to(RAIZ).as_posix() if encontradas else None
        if not encontradas:
            print(f"  ! falta la imagen de la escena {e['numero']} (se verá un fondo liso)")

    segmentos, escena_anterior = [], None
    for n, linea in enumerate(lineas):
        inicio = inicios.get(linea["numero"], 0.0)
        siguiente = inicios.get(linea["numero"] + 1, duracion_total) if n + 1 < len(lineas) else duracion_total
        propias = [dict(p, inicio=round(p["inicio"] - inicio, 3), fin=round(p["fin"] - inicio, 3))
                   for p in palabras if p["linea"] == linea["numero"]]
        destacada = None
        if linea["destacada"]:
            buscada = normalizar_palabra(linea["destacada"].split()[0])
            destacada = next((k for k, p in enumerate(propias)
                              if normalizar_palabra(p["texto"]) == buscada), None)
        sonidos = []
        if linea["escena"] != escena_anterior and escena_de[linea["escena"]]["whoosh"]:
            sonidos.append({"archivo": SONIDOS["whoosh"], "en": -ADELANTO_WHOOSH})
        if linea["ding"] and destacada is not None:
            sonidos.append({"archivo": SONIDOS["ding"], "en": propias[destacada]["inicio"]})
        if n == len(lineas) - 1:
            sonidos.append({"archivo": SONIDOS["sting"], "en": round(fin_narracion - inicio, 3)})
        segmentos.append({
            "id": f"l{linea['numero']:02d}",
            "tipo": "linea",
            "bloque": None,
            "escena": linea["escena"],
            "inicio": round(inicio, 3),
            "duracion": round(siguiente - inicio, 3),
            "audio": None,
            "imagen": imagenes[linea["escena"]],
            "palabras": propias,
            "destacada": destacada,
            "sonidos": sonidos,
        })
        escena_anterior = linea["escena"]

    salida = {
        "titulo": "",
        "video": carpeta.relative_to(RAIZ).as_posix(),
        "voz": voz,
        "icono": KNOT_ICONO,
        "formato": "short",
        "audio": mp3.relative_to(RAIZ).as_posix(),
        "duracionTotal": duracion_total,
        "segmentos": segmentos,
    }
    (carpeta / "timeline.json").write_text(
        json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{'línea':>5} {'escena':>6} {'inicio':>7}  texto")
    for s, linea in zip(segmentos, lineas):
        print(f"{linea['numero']:>5} {linea['escena']:>6} {s['inicio']:>6.2f}s  {linea['texto']}")
    print(f"\nNarración: {fin_narracion:.2f} s. Duración total del short: {duracion_total:.2f} s.")
    if duracion_total >= MAX_SEGUNDOS:
        print(f"! El short dura {MAX_SEGUNDOS} s o más: Remotion va a frenar el render (RULES.md).")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("guion")
    parser.add_argument("--forzar", action="store_true")
    parser.add_argument("--sin-imagenes", action="store_true")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
