#!/usr/bin/env python3
"""Copia las imágenes emparejadas a assets/img/ con el nombre del manifest y arma
los cuadros listos para el video: work/img16/NNN.png (largo, 1920x1080) y work/img916/NNN.png (Short, 1080x1920).
Tipo A (franja ancha): si la franja es casi 16:9 se recorta a 16:9; si no, va entera sobre fondo desenfocado.
Tipo B (vertical completa): en el largo, entera (contain) sobre fondo desenfocado; en el Short, cover."""
import json
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance

R = Path(__file__).resolve().parent.parent
man = {x["id"]: x for x in json.loads((R / "manifest_imagenes.json").read_text())["imagenes"]}
emp = json.loads((R / "work/emparejado.json").read_text())
info = json.loads((R / "work/img_info.json").read_text())
SUST = {"034": ("089", "no hay imagen del afiche; uso el león de película contra el león vago (mismo bloque, misma idea)"),
        "084": ("079", "no hay imagen de Pijama sentado en el grupo; uso Pijama con el grupo junto a la fogata"),
        "110": ("074", "no hay imagen de Pijama recordando; uso Pijama mirando a cámara en la sabana"),
        "111": ("080", "no hay imagen de alguien dándole agua; uso el grupo en el río")}
for d in ("assets/img", "work/img16", "work/img916"):
    (R / d).mkdir(parents=True, exist_ok=True)


def fondo(src, W, H):
    s = max(W / src.width, H / src.height)
    bg = src.resize((int(src.width * s) + 1, int(src.height * s) + 1), Image.LANCZOS)
    x, y = (bg.width - W) // 2, (bg.height - H) // 2
    bg = bg.crop((x, y, x + W, y + H)).filter(ImageFilter.GaussianBlur(40))
    return ImageEnhance.Brightness(bg).enhance(0.75)


def contain(src, W, H):
    bg = fondo(src, W, H)
    s = min(W / src.width, H / src.height)
    fg = src.resize((round(src.width * s), round(src.height * s)), Image.LANCZOS)
    bg.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2))
    return bg


def cover(src, W, H):
    s = max(W / src.width, H / src.height)
    im = src.resize((round(src.width * s), round(src.height * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))


mapa = {}
for i, x in man.items():
    if x["tipo"] == "hoja":
        continue
    usado, nota = i, ""
    if i not in emp or not emp[i]["archivo"]:
        usado, nota = SUST[i]
    f = emp[usado]["archivo"]
    v = info[f]
    im = Image.open(R / "imagenes" / f).convert("RGB")
    im.save(R / "assets/img" / x["file"])
    if v["tipo"] == "A":
        band = im.crop((0, v["top"], im.width, v["bottom"]))
        ratio = band.width / band.height
        largo = cover(band, 1920, 1080) if abs(ratio / (16 / 9) - 1) < 0.12 else contain(band, 1920, 1080)
        short = contain(band, 1080, 1920)
    else:
        largo = contain(im, 1920, 1080)
        short = cover(im, 1080, 1920)
    largo.save(R / "work/img16" / f"{i}.png")
    short.save(R / "work/img916" / f"{i}.png")
    mapa[i] = dict(archivo_original=f, archivo_usado=x["file"], fuente_id=usado, tipo=v["tipo"],
                   confianza=emp[usado]["confianza"] if usado == i else "sustituida", nota=nota or emp.get(i, {}).get("nota", ""))
(R / "work/mapa.json").write_text(json.dumps(mapa, ensure_ascii=False, indent=1))
print(len(mapa), "imágenes preparadas")
