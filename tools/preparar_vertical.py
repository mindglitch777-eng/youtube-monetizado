#!/usr/bin/env python3
"""Cuadros 1080x1920 para la serie de Shorts (work/img916v/NNN.png).
Tipo B: pantalla completa (cover). Tipo A: franja a ancho completo con su borde superior en y=560;
arriba y abajo, el color liso del borde de la propia imagen con un degradado suave (sin blur)."""
import json
from pathlib import Path

import numpy as np
from PIL import Image

R = Path(__file__).resolve().parent.parent
MAPA = json.loads((R / "work/mapa.json").read_text())
INFO = json.loads((R / "work/img_info.json").read_text())
OUT = R / "work/img916v"
OUT.mkdir(parents=True, exist_ok=True)
W, H, Y0 = 1080, 1920, 560


def cover(im):
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))


for i, m in MAPA.items():
    f = m["archivo_original"]
    v = INFO[f]
    im = Image.open(R / "imagenes" / f).convert("RGB")
    if v["tipo"] == "B":
        cover(im).save(OUT / f"{i}.png")
        continue
    band = im.crop((0, v["top"], im.width, v["bottom"]))
    s = W / band.width
    band = band.resize((W, round(band.height * s)), Image.LANCZOS)
    a = np.asarray(band).astype(float)
    top_c, bot_c = a[:6].reshape(-1, 3).mean(0), a[-6:].reshape(-1, 3).mean(0)
    lienzo = np.zeros((H, W, 3))
    lienzo[:] = bot_c
    lienzo[:Y0] = top_c
    # degradado suave: el color del borde se oscurece un poco hacia los extremos (legibilidad de insignia y textos)
    yy = np.arange(Y0)[:, None]
    lienzo[:Y0] = (top_c * (0.72 + 0.28 * (yy / Y0)))[:, None, :]
    y1 = Y0 + band.height
    yb = np.arange(H - y1)[:, None]
    lienzo[y1:] = (bot_c * (1 - 0.30 * (yb / max(1, H - y1))))[:, None, :]
    out = Image.fromarray(lienzo.clip(0, 255).astype(np.uint8))
    out.paste(band, (0, Y0))
    out.save(OUT / f"{i}.png")
print("ok", len(MAPA))
