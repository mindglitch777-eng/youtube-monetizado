"""Prueba de voces edge-tts para un video Kai: sintetiza UN texto de muestra
con varias voces candidatas, para elegir antes de sintetizar todo el guion.

Corre en GitHub Actions (Microsoft bloquea edge-tts desde Claude Code, igual
que kai_voz.py).

Uso:
    python scripts/kai_voces_preview.py "<texto>" <carpeta-destino> voz1 voz2 [voz3...]

Guarda <carpeta-destino>/<voz>.mp3 por cada voz.
"""

import asyncio
import sys
from pathlib import Path


async def sintetizar(texto, voz, destino_mp3, rate="+5%"):
    import edge_tts

    for intento in range(4):
        try:
            comunicador = edge_tts.Communicate(texto, voz, rate=rate)
            audio = bytearray()
            async for parte in comunicador.stream():
                if parte["type"] == "audio":
                    audio.extend(parte["data"])
            if not audio:
                raise RuntimeError("audio vacío")
            destino_mp3.write_bytes(audio)
            return
        except Exception as error:
            if intento == 3:
                raise
            espera = 5 * (intento + 1)
            print(f"  {voz}: {error}, reintentando en {espera}s", flush=True)
            await asyncio.sleep(espera)


def main():
    if len(sys.argv) < 4:
        sys.exit("Uso: python scripts/kai_voces_preview.py \"<texto>\" <carpeta-destino> voz1 voz2 [voz3...]")
    texto = sys.argv[1]
    carpeta = Path(sys.argv[2])
    voces = sys.argv[3:]
    carpeta.mkdir(parents=True, exist_ok=True)

    async def correr_todas():
        for voz in voces:
            destino = carpeta / f"{voz}.mp3"
            print(f"Sintetizando con {voz} -> {destino}")
            await sintetizar(texto, voz, destino)
    asyncio.run(correr_todas())
    print("Listo.")


if __name__ == "__main__":
    main()
