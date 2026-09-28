"""Paso 1 del PACK de video largo: sintetiza la narración por capítulo con
edge-tts (7 bloques: HOOK, C1..C6) capturando los tiempos de cada palabra.

Uso:
    python scripts/pack_voz.py content/<carpeta-pack>

Lee guion.txt (secciones "### <CAPITULO> — <nombre>"), sintetiza cada bloque
por separado con la voz configurada del canal (EDGE_TTS_VOICE, o
en-US-AndrewNeural si no hay ninguna) a rate -4%, y guarda:
  audio/bloque-<CAPITULO>.mp3
  audio/bloque-<CAPITULO>.json   (texto + palabras con offset/duración en s)

Corre en GitHub Actions: Microsoft bloquea edge-tts desde Claude Code. El
join de bloques con silencio, la conversión a wav y el alineado con
shots.json para armar timeline.json se hacen aparte, localmente, con
scripts/pack_timeline.py (no necesita red).
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


def leer_bloques(ruta_guion):
    texto = Path(ruta_guion).read_text(encoding="utf-8")
    bloques = []
    actual = None
    for linea in texto.splitlines():
        m = ENCABEZADO.match(linea.strip())
        if m:
            actual = {"capitulo": m.group(1), "nombre": m.group(2), "lineas": []}
            bloques.append(actual)
            continue
        if actual is not None and linea.strip():
            actual["lineas"].append(linea.strip())
    return bloques


async def sintetizar_bloque(texto, voz, rate, destino_mp3):
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
        except Exception as error:  # noqa: BLE001 - edge-tts a veces corta la conexión sin motivo
            if intento == 3:
                raise
            espera = 5 * (intento + 1)
            print(f"    {error}, reintentando en {espera}s ({intento + 1}/3)", flush=True)
            await asyncio.sleep(espera)


async def main_async(args):
    carpeta = Path(args.carpeta).resolve()
    ruta_guion = carpeta / "guion.txt"
    if not ruta_guion.exists():
        sys.exit(f"No existe {ruta_guion}")
    bloques = leer_bloques(ruta_guion)
    if len(bloques) != 7:
        print(f"::warning::Se esperaban 7 bloques (HOOK+C1..C6), se encontraron {len(bloques)}")

    sys.path.insert(0, str(RAIZ / "scripts"))
    from segmentos import cargar_env
    cargar_env()
    voz = os.environ.get("EDGE_TTS_VOICE", "en-US-AndrewNeural")
    rate = "-4%"

    carpeta_audio = carpeta / "audio"
    carpeta_audio.mkdir(parents=True, exist_ok=True)

    resumen = []
    for bloque in bloques:
        texto = " ".join(bloque["lineas"])
        base = carpeta_audio / f"bloque-{bloque['capitulo']}"
        mp3, meta = base.with_suffix(".mp3"), base.with_suffix(".json")
        if mp3.exists() and meta.exists():
            datos = json.loads(meta.read_text(encoding="utf-8"))
            if datos.get("texto") == texto and datos.get("voz") == voz and datos.get("rate") == rate:
                print(f"  {mp3.name} ya existe (texto sin cambios), no se regenera.")
                resumen.append((bloque["capitulo"], datos["duracion"]))
                continue
        print(f"  Generando {mp3.name} ({len(texto.split())} palabras) ...", flush=True)
        datos = await sintetizar_bloque(texto, voz, rate, mp3)
        datos.update(texto=texto, voz=voz, rate=rate, capitulo=bloque["capitulo"], nombre=bloque["nombre"])
        meta.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
        resumen.append((bloque["capitulo"], datos["duracion"]))

    print(f"\nVoz: {voz}  rate: {rate}")
    total = 0.0
    for capitulo, duracion in resumen:
        print(f"  {capitulo:>5}: {duracion:6.2f} s")
        total += duracion
    print(f"Suma de bloques (sin los 0.3s de silencio entre ellos): {total:.2f} s")
    print("Correr ahora scripts/pack_timeline.py para unir, convertir a wav y alinear con shots.json.")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("carpeta")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
