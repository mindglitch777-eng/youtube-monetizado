"""Voz de "parte1-love-bombing" (línea Kai, formato con script.json de líneas
sueltas — distinto del guion.txt continuo de kai_voz.py): sintetiza CADA
línea por separado con edge-tts (un mp3 por línea, como pide el .md de
instrucciones), con boundary de palabra para los subtítulos.

Corre en GitHub Actions (Microsoft bloquea edge-tts desde Claude Code).

Uso:
    python scripts/kai_p1_voz.py content-kai/parte1-love-bombing [voz] [rate]
"""

import asyncio
import json
import sys
from pathlib import Path


async def sintetizar_linea(texto, voz, rate, destino_mp3):
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
    if len(sys.argv) < 2:
        sys.exit("Uso: python scripts/kai_p1_voz.py <carpeta> [voz] [rate]")
    carpeta = Path(sys.argv[1]).resolve()
    voz = sys.argv[2] if len(sys.argv) > 2 else "en-US-AndrewNeural"
    rate = sys.argv[3] if len(sys.argv) > 3 else "+8%"

    script = json.loads((carpeta / "script.json").read_text(encoding="utf-8"))
    carpeta_audio = carpeta / "audio"
    carpeta_audio.mkdir(exist_ok=True)

    async def correr_todas():
        resultado = []
        for linea in script["lineas"]:
            n = linea["n"]
            destino = carpeta_audio / f"line-{n:02d}.mp3"
            print(f"Sintetizando línea {n}: {linea['texto'][:50]!r} -> {destino.name}")
            r = await sintetizar_linea(linea["texto"], voz, rate, destino)
            resultado.append({"n": n, "archivo": destino.name, **r})
        return resultado

    resultado = asyncio.run(correr_todas())
    destino_json = carpeta_audio / "voz.json"
    destino_json.write_text(json.dumps({"voz": voz, "rate": rate, "lineas": resultado}, indent=2, ensure_ascii=False),
                             encoding="utf-8")
    total = sum(r["duracion"] for r in resultado)
    print(f"\nListo: {len(resultado)} líneas, {total:.1f}s de audio total -> {destino_json}")


if __name__ == "__main__":
    main()
