#!/usr/bin/env python3
"""
Prepara las imágenes del video 2.

Muchas imágenes 16:9 vienen partidas en paneles con líneas verticales. Se busca
un par de cortes simétricos (x y 1-x) con un salto fuerte de color entre
columnas vecinas; si existe, se usa solo el panel del medio. Si hay un solo
corte fuerte, se usa el lado más ancho. Del panel elegido se recorta un 16:9
(un poco hacia arriba para no cortar cabezas) y se escala a 1920x1080.

Para los Shorts (1080x1920) se recorta un 9:16 del centro del panel; las
imágenes del bloque SHORTS (ya verticales) se usan completas.

Salida: video2/work/img16/<id>.jpg, video2/work/img916/<id>.jpg y
video2/work/recortes.json (qué se hizo con cada una).
"""
import json
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

V = Path(__file__).resolve().parent.parent
SRC = V / "imagenes"
O16 = V / "work" / "img16"
O916 = V / "work" / "img916"
O16.mkdir(parents=True, exist_ok=True)
O916.mkdir(parents=True, exist_ok=True)
FUERTE = 40
# paneles que el detector no ve (cortes suaves o asimétricos), medidos a ojo: id -> (izq, der)
PANELES = {"018": (0.27, 1.0), "034": (0.31, 0.688), "038": (0.34, 0.658), "040": (0.27, 0.666), "049": (0.333, 0.666),
           "076": (0.311, 0.664), "120": (0.341, 0.658), "121": (0.332, 0.666), "213": (0.34, 0.658), "224": (0.312, 0.688)}
# texto en inglés que no se puede mostrar: id -> cajas (x0, y0, x1, y1) relativas a la imagen original
TEXTO = {"011": [(0.575, 0.40, 0.66, 0.47)], "041": [(0.495, 0.37, 0.548, 0.43)], "071": [(0.36, 0.035, 0.65, 0.115)],
         "073": [(0.48, 0.315, 0.625, 0.38)], "080": [(0.365, 0.88, 0.455, 0.92), (0.55, 0.88, 0.655, 0.92)],
         "090": [(0.85, 0.37, 1.0, 0.50)], "138": [(0.30, 0.30, 0.49, 0.39)], "191": [(0.865, 0.915, 0.955, 0.995)],
         "221": [(0.05, 0.15, 0.15, 0.33), (0.39, 0.17, 0.465, 0.36)], "175": [(0.645, 0.62, 0.725, 0.70), (0.40, 0.75, 0.52, 0.85)],
         "084": [(0.0, 0.39, 0.19, 0.48)], "092": [(0.0, 0.33, 0.12, 0.42)]}


def tapar(im, cajas):
    """Rellena cada caja con el color del borde que la rodea y suaviza: el texto desaparece."""
    W, H = im.size
    a = np.asarray(im).copy()
    for x0, y0, x1, y1 in cajas:
        X0, Y0, X1, Y1 = int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H)
        m = 4
        anillo = np.concatenate([a[max(0, Y0 - m):Y0, X0:X1].reshape(-1, 3), a[Y1:Y1 + m, X0:X1].reshape(-1, 3),
                                 a[Y0:Y1, max(0, X0 - m):X0].reshape(-1, 3), a[Y0:Y1, X1:X1 + m].reshape(-1, 3)])
        a[Y0:Y1, X0:X1] = np.median(anillo, axis=0)
    out = Image.fromarray(a)
    for x0, y0, x1, y1 in cajas:
        X0, Y0, X1, Y1 = int(x0 * W) - 6, int(y0 * H) - 6, int(x1 * W) + 6, int(y1 * H) + 6
        X0, Y0 = max(0, X0), max(0, Y0)
        out.paste(out.crop((X0, Y0, X1, Y1)).filter(ImageFilter.GaussianBlur(3)), (X0, Y0))
    return out


def cortes(a):
    d = np.abs(a[:, 1:] - a[:, :-1]).mean(axis=(0, 2))
    w = len(d)
    picos = []
    for x in range(20, w - 20):
        loc = np.median(d[max(0, x - 30):x + 30])
        if d[x] > max(4 * loc, 18) and d[x] == d[max(0, x - 3):x + 4].max():
            picos.append((x / w, d[x]))
    # par simétrico más fuerte
    mejor = None
    for xl, sl in picos:
        if not 0.08 < xl < 0.45:
            continue
        for xr, sr in picos:
            if abs((1 - xr) - xl) < 0.015:
                s = min(sl, sr)
                if s < FUERTE and max(sl, sr) < 50:  # par débil: solo vale si los dos cortes son claros
                    continue
                if mejor is None or s > mejor[2]:
                    mejor = (xl, xr, s)
    if mejor:
        return mejor[0] + 0.006, mejor[1] - 0.006, "panel central"
    fuertes = [p for p in picos if p[1] >= 80 and 0.1 < p[0] < 0.9]
    if len(fuertes) == 1:
        x = fuertes[0][0]
        return (x + 0.006, 1.0, "lado derecho") if x < 0.5 else (0.0, x - 0.006, "lado izquierdo")
    return 0.0, 1.0, "entera"


def recorte(im, l, r, aspecto, alto_rel=0.45):
    W, H = im.size
    x0, x1 = int(l * W), int(r * W)
    pw = x1 - x0
    if pw / H > aspecto:  # el panel es más ancho que el aspecto: recorto a lo ancho
        cw = int(H * aspecto)
        cx = x0 + (pw - cw) // 2
        return im.crop((cx, 0, cx + cw, H))
    ch = int(pw / aspecto)
    cy = int((H - ch) * alto_rel)
    return im.crop((x0, cy, x1, cy + ch))


def panel_sobre_fondo(im, l, r):
    W, H = im.size
    pan = im.crop((int(l * W), 0, int(r * W), H))
    fw = int(pan.size[0] * 1080 / H)
    frente = pan.resize((fw, 1080), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 60, 2))
    esc = max(1920 / pan.size[0], 1080 / H)
    fondo = pan.resize((int(pan.size[0] * esc) + 2, int(H * esc) + 2), Image.LANCZOS)
    fx, fy = (fondo.size[0] - 1920) // 2, (fondo.size[1] - 1080) // 2
    fondo = fondo.crop((fx, fy, fx + 1920, fy + 1080)).filter(ImageFilter.GaussianBlur(28))
    fondo = Image.eval(fondo, lambda v: int(v * 0.5))
    x = (1920 - fw) // 2
    sombra = Image.new("L", (fw + 60, 1080), 0)
    from PIL import ImageDraw
    ImageDraw.Draw(sombra).rectangle((30, 0, fw + 30, 1080), fill=150)
    sombra = sombra.filter(ImageFilter.GaussianBlur(18))
    fondo.paste((0, 0, 0), (x - 30, 0), sombra)
    fondo.paste(frente, (x, 0))
    return fondo


def main():
    info = {}
    for f in sorted(os.listdir(SRC)):
        i = f[:3]
        im = Image.open(SRC / f).convert("RGB")
        if i in TEXTO:
            im = tapar(im, TEXTO[i])
        if im.size[0] < im.size[1]:  # vertical (Shorts y transiciones)
            im.resize((1080, 1920), Image.LANCZOS).save(O916 / f"{i}.jpg", quality=92)
            r16 = recorte(im, 0, 1, 16 / 9)
            r16.resize((1920, 1080), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 60, 2)).save(O16 / f"{i}.jpg", quality=92)
            info[i] = {"tipo": "vertical", "zoom16": round(1920 / r16.size[0], 2)}
            continue
        a = np.asarray(im, dtype=float)
        l, r, que = (*PANELES[i], "panel central (a mano)") if i in PANELES else cortes(a)
        r16 = recorte(im, l, r, 16 / 9)
        zoom = 1920 / r16.size[0]
        if zoom > 3:
            # panel angosto (un tercio): recortarlo a 16:9 deja solo un tercio del alto y corta caras.
            # Se muestra el panel entero en el centro, sobre una copia ampliada, desenfocada y oscurecida.
            out = panel_sobre_fondo(im, l, r)
            que += " (entero sobre fondo)"
        else:
            out = r16.resize((1920, 1080), Image.LANCZOS)
            if zoom > 1.6:
                out = out.filter(ImageFilter.UnsharpMask(1.5, 70, 2))
        out.save(O16 / f"{i}.jpg", quality=92)
        r9 = recorte(im, l, r, 9 / 16, 0.5)
        r9.resize((1080, 1920), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 60, 2)).save(O916 / f"{i}.jpg", quality=92)
        info[i] = {"tipo": que, "l": round(l, 3), "r": round(r, 3), "zoom16": round(zoom, 2)}
    (V / "work" / "recortes.json").write_text(json.dumps(info, indent=1))
    from collections import Counter
    print(Counter(v["tipo"] for v in info.values()))
    print("zoom > 3:", [k for k, v in info.items() if v["zoom16"] > 3])


if __name__ == "__main__":
    main()
