"""Genera la narración de un video con edge-tts y arma timeline.json para Remotion.

Uso:
    python scripts/generar_audio.py content/<nombre-video>/guion.md [--forzar]

Genera un mp3 por sección (Intro, Hook, Gancho 2, cada ejemplo del Cuerpo,
Pago, Transición y CTA) en content/<nombre-video>/audio/, junto con un .json
con el tiempo de cada palabra (para los subtítulos). Los audios que ya
existen se saltean salvo con --forzar, así se puede volver a correr solo para
reconstruir timeline.json después de generar las imágenes.

RULES.md: Edge-TTS se usa solo en fase de prueba. Antes de publicar contenido
monetizado, la voz tiene que migrar a una opción con licencia comercial.
"""

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path

from segmentos import RAIZ, cargar_env, leer_guion, nombre_audio, nombre_base, validar_o_salir

# Sonidos de marca (RULES.md, sección Sonido).
SONIDOS = {
    "whoosh": "assets/sonido/transicion.mp3",
    "ding": "assets/sonido/revelacion.mp3",
    "click": "assets/sonido/bloque.mp3",
    "sting": "assets/sonido/cierre.mp3",
}
KNOT_REFERENCIA = "assets/personaje/knot-referencia.png"
KNOT_RESUELTO = "assets/personaje/knot-resuelto.png"
KNOT_ICONO = "assets/personaje/knot-icono.png"

PAUSA = {"pago": 0.7, "transicion": 0.4}
PAUSA_DEFAULT = 0.35
COLA_FINAL = 2.5  # segundos después del CTA para que suene el sting


def normalizar_palabra(texto):
    return re.sub(r"[^\w']", "", texto.lower()).replace("'", "")


async def sintetizar(texto, voz, destino_mp3):
    import edge_tts
    from edge_tts.constants import MP3_BITRATE_BPS, TICKS_PER_SECOND

    comunicador = edge_tts.Communicate(texto, voz, boundary="WordBoundary")
    audio = bytearray()
    palabras = []
    async for parte in comunicador.stream():
        if parte["type"] == "audio":
            audio.extend(parte["data"])
        elif parte["type"] == "WordBoundary":
            inicio = parte["offset"] / TICKS_PER_SECOND
            palabras.append({"texto": parte["text"], "inicio": round(inicio, 3),
                             "fin": round(inicio + parte["duration"] / TICKS_PER_SECOND, 3)})
    destino_mp3.write_bytes(audio)
    # El mp3 de edge-tts es de bitrate constante: la duración sale del tamaño.
    duracion = len(audio) * 8 / MP3_BITRATE_BPS
    return {"duracion": round(duracion, 3), "palabras": palabras}


def alinear_puntuacion(texto, palabras):
    """Recupera la puntuación del guion para cada palabra (sirve para cortar frases)."""
    tokens = texto.split()
    i = 0
    for palabra in palabras:
        buscada = normalizar_palabra(palabra["texto"])
        for j in range(i, min(i + 4, len(tokens))):
            if buscada and buscada in normalizar_palabra(tokens[j]):
                palabra["texto"] = tokens[j]
                i = j + 1
                break
    return palabras


def indice_destacada(segmento, palabras):
    if not segmento["ding"]:
        return None
    if segmento["destacada"]:
        buscada = normalizar_palabra(segmento["destacada"].split()[0])
        for n, palabra in enumerate(palabras):
            if normalizar_palabra(palabra["texto"]) == buscada:
                return n
        print(f"  ! {segmento['id']}: no encontré '{segmento['destacada']}' en el audio")
    else:
        print(f"  ! {segmento['id']}: tiene ding pero ninguna palabra en **negrita**; "
              f"resalto la más larga")
    return max(range(len(palabras)), key=lambda n: len(palabras[n]["texto"])) if palabras else None


def sonidos_de(segmento, datos, destacada):
    sonidos = []
    if segmento["tipo"] == "transicion":
        sonidos.append({"archivo": SONIDOS["whoosh"], "en": 0})
    if segmento["tipo"] == "ejemplo" and segmento["ejemplo"] > 1:
        sonidos.append({"archivo": SONIDOS["click"], "en": 0})
    if destacada is not None:
        sonidos.append({"archivo": SONIDOS["ding"], "en": datos["palabras"][destacada]["inicio"]})
    if segmento["tipo"] == "cta":
        sonidos.append({"archivo": SONIDOS["sting"], "en": datos["duracion"]})
    return sonidos


def imagen_de(segmento, carpeta_imagenes, anterior):
    if segmento["ilustrar"]:
        encontradas = sorted(carpeta_imagenes.glob(nombre_base(segmento) + ".*"))
        if encontradas:
            return encontradas[0].relative_to(RAIZ).as_posix()
        print(f"  ! falta la imagen {nombre_base(segmento)} (se verá un fondo liso)")
        return None
    if segmento["tipo"] == "intro":
        return KNOT_REFERENCIA
    if segmento["tipo"] == "cta":
        if (RAIZ / KNOT_RESUELTO).exists():
            return KNOT_RESUELTO
        print(f"  ! falta {KNOT_RESUELTO} (Knot con el hilo verde agua); uso la referencia")
        return KNOT_REFERENCIA
    return anterior  # transición: mantiene la última escena


async def main_async(args):
    ruta_guion = Path(args.guion).resolve()
    validar_o_salir(ruta_guion)
    cargar_env()
    voz = os.environ.get("EDGE_TTS_VOICE", "en-US-JennyNeural")

    titulo, segmentos = leer_guion(ruta_guion)
    carpeta_video = ruta_guion.parent
    carpeta_audio = carpeta_video / "audio"
    carpeta_audio.mkdir(parents=True, exist_ok=True)

    timeline = []
    inicio = 0.0
    imagen = None
    for segmento in segmentos:
        base = carpeta_audio / nombre_audio(segmento)
        mp3, meta = base.with_suffix(".mp3"), base.with_suffix(".json")
        if args.forzar or not (mp3.exists() and meta.exists()):
            print(f"  {mp3.name} ...", flush=True)
            datos = await sintetizar(segmento["texto"], voz, mp3)
            datos["palabras"] = alinear_puntuacion(segmento["texto"], datos["palabras"])
            meta.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
        datos = json.loads(meta.read_text(encoding="utf-8"))

        destacada = indice_destacada(segmento, datos["palabras"])
        imagen = imagen_de(segmento, carpeta_video / "imagenes", imagen)
        timeline.append({
            "id": segmento["id"],
            "tipo": segmento["tipo"],
            "bloque": segmento["bloque"],
            "inicio": round(inicio, 3),
            "duracion": datos["duracion"],
            "audio": mp3.relative_to(RAIZ).as_posix(),
            "imagen": imagen,
            "palabras": datos["palabras"],
            "destacada": destacada,
            "sonidos": sonidos_de(segmento, datos, destacada),
        })
        inicio += datos["duracion"] + PAUSA.get(segmento["tipo"], PAUSA_DEFAULT)

    salida = {
        "titulo": titulo,
        "video": carpeta_video.relative_to(RAIZ).as_posix(),
        "voz": voz,
        "icono": KNOT_ICONO,
        "duracionTotal": round(inicio + COLA_FINAL, 3),
        "segmentos": timeline,
    }
    (carpeta_video / "timeline.json").write_text(
        json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")
    minutos, segundos = divmod(int(salida["duracionTotal"]), 60)
    print(f"{len(timeline)} secciones, duración total {minutos}:{segundos:02d}.")
    print(f"Timeline: {carpeta_video / 'timeline.json'}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("guion")
    parser.add_argument("--forzar", action="store_true", help="regenera todos los audios")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
