"""Paso 1 de un video de la línea Kai: sintetiza el guion COMPLETO en una
sola pasada de edge-tts (a diferencia del PACK cinematográfico, acá no se
separa por capítulo — son Shorts cortos, una sola voz continua alcanza) y
guarda los tiempos de cada palabra.

Uso:
    python scripts/kai_voz.py content-kai/<carpeta-video>

Lee guion.txt (secciones "### <ID> — <nombre opcional>", ID en
HOOK/P5/P4/P3/P2/P1/CTA), concatena todas las líneas en un solo texto
(con las cabeceras de sección quitadas), sintetiza con la voz configurada
del canal (EDGE_TTS_VOICE, o en-US-AndrewNeural si no hay ninguna) y
guarda:
  audio/voz.mp3
  audio/voz.json   (texto completo + palabras con offset/duración en s)

Corre en GitHub Actions: Microsoft bloquea edge-tts desde Claude Code. El
alineado de estas palabras con las secciones de shots.json para armar
kai-timeline.json se hace aparte, localmente, con scripts/kai_timeline.py
(no necesita red).
"""

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ENCABEZADO = re.compile(r"^###\s+(\S+)\s+—\s+(.*)$")


def leer_guion_completo(ruta_guion):
    """Devuelve (texto_completo, [(id, texto_seccion), ...]) — el texto
    completo es lo que se sintetiza; las secciones se usan después en
    kai_timeline.py para saber cuántas palabras le tocan a cada toma."""
    texto = Path(ruta_guion).read_text(encoding="utf-8")
    secciones = []
    actual = None
    for linea in texto.splitlines():
        m = ENCABEZADO.match(linea.strip())
        if m:
            actual = {"id": m.group(1), "lineas": []}
            secciones.append(actual)
            continue
        if actual is not None and linea.strip():
            actual["lineas"].append(linea.strip())
    completo = " ".join(" ".join(s["lineas"]) for s in secciones)
    return completo, [(s["id"], " ".join(s["lineas"])) for s in secciones]


async def sintetizar(texto, voz, rate, destino_mp3):
    import edge_tts
    from edge_tts.constants import MP3_BITRATE_BPS, TICKS_PER_SECOND

    for intento in range(4):
        try:
            comunicador = edge_tts.Communicate(texto, voz, rate=rate, boundary="WordBoundary")
            audio = bytearray()
            palabras = []
            async for parte in comunicador.stream():
                if parte["type"] == "audio":
                    audio.extend(parte["data"])
                elif parte["type"] == "WordBoundary":
                    inicio = parte["offset"] / TICKS_PER_SECOND
                    palabras.append({"texto": parte["text"], "inicio": round(inicio, 3),
                                     "fin": round(inicio + parte["duration"] / TICKS_PER_SECOND, 3)})
            if not audio:
                raise RuntimeError("audio vacío")
            destino_mp3.write_bytes(audio)
            duracion = len(audio) * 8 / MP3_BITRATE_BPS
            return {"duracion": round(duracion, 3), "palabras": palabras}
        except Exception as error:
            if intento == 3:
                raise
            espera = 5 * (intento + 1)
            print(f"  {error}, reintentando en {espera}s ({intento + 1}/3)", flush=True)
            await asyncio.sleep(espera)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("carpeta")
    args = parser.parse_args()
    carpeta = Path(args.carpeta).resolve()

    completo, secciones = leer_guion_completo(carpeta / "guion.txt")
    if not secciones:
        sys.exit("guion.txt no tiene ninguna sección '### ID — nombre'.")

    voz = os.environ.get("EDGE_TTS_VOICE", "en-US-AndrewNeural")
    carpeta_audio = carpeta / "audio"
    carpeta_audio.mkdir(exist_ok=True)
    destino_mp3 = carpeta_audio / "voz.mp3"
    destino_json = carpeta_audio / "voz.json"

    print(f"Sintetizando guion completo ({len(secciones)} secciones, voz {voz}) ...")
    resultado = asyncio.run(sintetizar(completo, voz, "-4%", destino_mp3))
    resultado["secciones"] = [{"id": sid, "texto": txt} for sid, txt in secciones]
    destino_json.write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Listo: {destino_mp3} ({resultado['duracion']:.1f}s), {destino_json}")


if __name__ == "__main__":
    main()
