#!/usr/bin/env python3
"""Genera la voz con edge-tts (sin cuenta) a partir de work/voz_lineas.json.
Por cada línea: work/voz/NNN.mp3 y work/voz/NNN.json con los tiempos de cada palabra (en segundos).
Corre en GitHub Actions porque el servicio de voz no es accesible desde el entorno de Claude."""
import asyncio
import json
import sys
from pathlib import Path

import edge_tts

R = Path(__file__).resolve().parent.parent
cfg = json.loads((R / "work/voz_lineas.json").read_text())
OUT = R / "work/voz"
OUT.mkdir(parents=True, exist_ok=True)
rate = sys.argv[1] if len(sys.argv) > 1 else cfg["rate"]


async def una(l):
    mp3, js = OUT / f"{l['n']:03d}.mp3", OUT / f"{l['n']:03d}.json"
    try:
        com = edge_tts.Communicate(l["texto_tts"], cfg["voz"], rate=rate, boundary="WordBoundary")
    except TypeError:
        com = edge_tts.Communicate(l["texto_tts"], cfg["voz"], rate=rate)
    palabras, audio = [], bytearray()
    async for ch in com.stream():
        if ch["type"] == "audio":
            audio += ch["data"]
        elif ch["type"] == "WordBoundary":
            palabras.append({"w": ch["text"], "ini": ch["offset"] / 1e7, "fin": (ch["offset"] + ch["duration"]) / 1e7})
    mp3.write_bytes(bytes(audio))
    js.write_text(json.dumps({"n": l["n"], "texto": l["texto"], "voz": cfg["voz"], "rate": rate, "palabras": palabras}, ensure_ascii=False))
    print(l["n"], len(palabras), "palabras", flush=True)


async def main():
    for l in cfg["lineas"]:
        for intento in range(4):
            try:
                await una(l)
                break
            except Exception as e:  # noqa: BLE001
                print("reintento", l["n"], e, flush=True)
                await asyncio.sleep(3 * (intento + 1))
        else:
            raise SystemExit(f"falló la línea {l['n']}")

asyncio.run(main())
