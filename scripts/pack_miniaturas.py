"""Paso 9 del PACK de video largo: compone las 2 miniaturas finales
(1280x720, <2MB) a partir del fondo IA (o el placeholder) + texto, según
metadata.md ("Miniatura"). No necesita red (usa fuentes locales).

Uso:
    python scripts/pack_miniaturas.py content/<carpeta-pack>
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 720
FUENTE = Path(__file__).resolve().parent.parent / "remotion" / "fuentes" / "Anton.ttf"


def texto_con_glow(base, texto, tamano, xy, color=(255, 255, 255), glow=(220, 20, 20), anchor="lm"):
    fuente = ImageFont.truetype(str(FUENTE), tamano)
    capa_glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    dg = ImageDraw.Draw(capa_glow)
    dg.text(xy, texto, font=fuente, fill=(*glow, 255), anchor=anchor)
    capa_glow = capa_glow.filter(ImageFilter.GaussianBlur(10))
    base.alpha_composite(capa_glow)
    d = ImageDraw.Draw(base)
    d.text(xy, texto, font=fuente, fill=(*color, 255), anchor=anchor, stroke_width=2, stroke_fill=(0, 0, 0, 255))


def armar(fondo_path, destino, titulo, sub=None):
    fondo = Image.open(fondo_path).convert("RGB")
    # la imagen IA es 1024x1024: recorto a 1280x720 manteniendo el ancho completo
    escala = W / fondo.width
    fondo = fondo.resize((W, round(fondo.height * escala)), Image.LANCZOS)
    if fondo.height > H:
        recorte_arriba = (fondo.height - H) // 2
        fondo = fondo.crop((0, recorte_arriba, W, recorte_arriba + H))
    else:
        lienzo = Image.new("RGB", (W, H), (2, 2, 2))
        lienzo.paste(fondo, (0, (H - fondo.height) // 2))
        fondo = lienzo

    lienzo = fondo.convert("RGBA")
    x_texto = round(W * 0.56)
    y = round(H * 0.38)
    texto_con_glow(lienzo, titulo[0], 128, (x_texto, y))
    if len(titulo) > 1:
        y += 118
        texto_con_glow(lienzo, titulo[1], 128, (x_texto, y))

    if sub:
        y += 130
        d = ImageDraw.Draw(lienzo)
        fuente_chip = ImageFont.truetype(str(FUENTE), 40)
        caja = d.textbbox((0, 0), sub, font=fuente_chip)
        ancho_chip, alto_chip = caja[2] - caja[0] + 56, caja[3] - caja[1] + 30
        chip = Image.new("RGBA", (ancho_chip, alto_chip), (0, 0, 0, 0))
        dc = ImageDraw.Draw(chip)
        dc.rounded_rectangle([0, 0, ancho_chip - 1, alto_chip - 1], radius=alto_chip // 2,
                              fill=(255, 176, 32, 235))
        dc.text((ancho_chip / 2, alto_chip / 2), sub, font=fuente_chip, fill=(10, 10, 10, 255), anchor="mm")
        lienzo.alpha_composite(chip, (x_texto, y))

    lienzo.convert("RGB").save(destino, quality=90, optimize=True)
    print(f"  {destino} ({destino.stat().st_size // 1024} KB)")


def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: python scripts/pack_miniaturas.py content/<carpeta-pack>")
    carpeta = Path(sys.argv[1]).resolve()
    if not FUENTE.exists():
        sys.exit(f"Falta la fuente {FUENTE} (Anton.ttf) — descargarla antes (ver LOG.md).")

    out = carpeta / "out"
    out.mkdir(exist_ok=True)

    armar(carpeta / "img" / "THUMB_A.jpg", out / "thumbnail_A.png", ["ZERO", "BRUISES"], sub="5 MOVES")
    fondo_b = carpeta / "img" / "THUMB_B_placeholder.jpg"
    if not fondo_b.exists():
        fondo_b = carpeta / "img" / "THUMB_B.jpg"
    armar(fondo_b, out / "thumbnail_B.png", ["HE NEVER", "YELLED"])


if __name__ == "__main__":
    main()
