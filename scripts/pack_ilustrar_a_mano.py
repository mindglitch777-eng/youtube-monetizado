"""Ilustra a mano (sin IA) las tomas que no se pudieron generar con
Cloudflare por cuota agotada. Mismo estilo gráfico-novela del resto del
video (siluetas planas + luz de borde + degradado), respetando N4
(siluetas sin rasgos faciales, de espaldas o con la cabeza inclinada) y
sin texto/números/carteles.

Uso: python scripts/pack_ilustrar_a_mano.py content/<carpeta-pack>
"""
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

W = H = 1024


def lienzo_con_glow(rgb_fondo, glow_cx, glow_cy, glow_r, glow_color, fuerza=0.9):
    img = Image.new("RGB", (W, H), rgb_fondo)
    d = ImageDraw.Draw(img)
    for i in range(glow_r, 0, -4):
        t = i / glow_r
        r = int(rgb_fondo[0] + (glow_color[0] - rgb_fondo[0]) * (1 - t) ** 1.7 * fuerza)
        g = int(rgb_fondo[1] + (glow_color[1] - rgb_fondo[1]) * (1 - t) ** 1.7 * fuerza)
        b = int(rgb_fondo[2] + (glow_color[2] - rgb_fondo[2]) * (1 - t) ** 1.7 * fuerza)
        d.ellipse([glow_cx - i, glow_cy - i, glow_cx + i, glow_cy + i], fill=(r, g, b))
    return img.filter(ImageFilter.GaussianBlur(6))


def puntos_silueta_de_espaldas(cx, base_y, alto, ancho_hombros, cabeza_inclinada=0.0, escala=1.0):
    """Devuelve (centro_cabeza, radio_cabeza, contorno_cuerpo_completo)
    para una figura humana vista de espaldas, como UN SOLO polígono suave
    (cuello entallado, hombros redondeados, cintura, piernas) — evita el
    aspecto de "muñeco de trapecios" del primer intento."""
    alto_cabeza = alto * 0.11 * escala
    cy_cabeza = base_y - alto * escala + alto_cabeza * 0.75 + cabeza_inclinada * alto * 0.04
    r_cabeza = alto_cabeza * 0.62
    cx_cabeza = cx + cabeza_inclinada * ancho_hombros * 0.05

    aw = ancho_hombros * escala
    y_cuello = cy_cabeza + r_cabeza * 0.75
    y_hombros = y_cuello + alto * 0.02 * escala
    y_cintura = base_y - alto * 0.44 * escala
    y_cadera = base_y - alto * 0.40 * escala
    y_separacion_piernas = y_cadera + alto * 0.04 * escala

    ancho_cuello = aw * 0.20
    ancho_cintura = aw * 0.34
    ancho_cadera = aw * 0.40
    ancho_tobillo = aw * 0.11
    sep = aw * 0.05

    contorno = [
        (cx - ancho_cuello / 2, y_cuello),
        (cx - aw / 2, y_hombros),
        (cx - aw * 0.46, y_hombros + (y_cintura - y_hombros) * 0.35),
        (cx - ancho_cintura / 2, y_cintura),
        (cx - ancho_cadera / 2, y_cadera),
        (cx - ancho_cadera / 2, y_separacion_piernas),
        (cx - sep - ancho_tobillo, base_y),
        (cx - sep - ancho_tobillo * 0.3, base_y),
        (cx - sep, y_separacion_piernas + (base_y - y_separacion_piernas) * 0.4),
        (cx - sep * 0.3, base_y),
        (cx + sep * 0.3, base_y),
        (cx + sep, y_separacion_piernas + (base_y - y_separacion_piernas) * 0.4),
        (cx + sep + ancho_tobillo * 0.3, base_y),
        (cx + sep + ancho_tobillo, base_y),
        (cx + ancho_cadera / 2, y_separacion_piernas),
        (cx + ancho_cadera / 2, y_cadera),
        (cx + ancho_cintura / 2, y_cintura),
        (cx + aw * 0.46, y_hombros + (y_cintura - y_hombros) * 0.35),
        (cx + aw / 2, y_hombros),
        (cx + ancho_cuello / 2, y_cuello),
    ]
    return (cx_cabeza, cy_cabeza, r_cabeza), contorno


def dibujar_figura(draw, cx, base_y, alto, ancho_hombros, fill, cabeza_inclinada=0.0, escala=1.0):
    (ccx, ccy, cr), contorno = puntos_silueta_de_espaldas(cx, base_y, alto, ancho_hombros, cabeza_inclinada, escala)
    draw.polygon(contorno, fill=fill)
    draw.ellipse([ccx - cr, ccy - cr * 1.08, ccx + cr, ccy + cr * 1.12], fill=fill)


def figura_con_borde_de_luz(img, cx, base_y, alto, ancho_hombros, color_borde, cabeza_inclinada=0.0):
    """Contorno fino de contraluz: dibuja la silueta apenas más grande en
    el color de rim-light, la difumina poco (borde nítido-suave, no un
    halo grueso), y encima la silueta negra a tamaño normal."""
    capa_borde = Image.new("RGB", (W, H), (0, 0, 0))
    d1 = ImageDraw.Draw(capa_borde)
    dibujar_figura(d1, cx, base_y, alto, ancho_hombros, fill=color_borde, cabeza_inclinada=cabeza_inclinada, escala=1.025)
    capa_borde = capa_borde.filter(ImageFilter.GaussianBlur(2.2))
    mascara = capa_borde.convert("L").point(lambda p: min(255, int(p * 0.85)))
    img.paste(capa_borde, (0, 0), mascara)
    d2 = ImageDraw.Draw(img)
    dibujar_figura(d2, cx, base_y, alto, ancho_hombros, fill=(4, 4, 5), cabeza_inclinada=cabeza_inclinada, escala=1.0)


def guardar(img, destino):
    img.save(destino, quality=94)
    print(f"  {destino}")


def hacer_S002(destino):
    img = lienzo_con_glow((2, 2, 3), W * 0.5, H * 0.40, 480, (255, 175, 70), fuerza=0.85)
    d = ImageDraw.Draw(img)
    d.rectangle([W * 0.30, H * 0.10, W * 0.70, H * 0.85], outline=(35, 20, 8), width=10)
    figura_con_borde_de_luz(img, W * 0.5, H * 0.86, H * 0.60, W * 0.20, (90, 160, 255))
    d = ImageDraw.Draw(img)
    d.polygon([(W * 0.42, H * 0.855), (W * 0.58, H * 0.855), (W * 0.66, H * 0.99), (W * 0.34, H * 0.99)], fill=(5, 5, 6))
    guardar(img, destino)


def hacer_S014(destino):
    img = lienzo_con_glow((3, 3, 7), W * 0.5, H * 0.60, 380, (255, 210, 150), fuerza=1.0)
    d = ImageDraw.Draw(img)
    d.rectangle([W * 0.30, H * 0.72, W * 0.70, H * 0.76], fill=(10, 10, 14))
    d.rectangle([W * 0.33, H * 0.76, W * 0.37, H * 0.95], fill=(8, 8, 12))
    d.rectangle([W * 0.63, H * 0.76, W * 0.67, H * 0.95], fill=(8, 8, 12))
    d.rounded_rectangle([W * 0.42, H * 0.635, W * 0.58, H * 0.71], radius=10, fill=(6, 6, 8))
    d.rounded_rectangle([W * 0.435, H * 0.645, W * 0.565, H * 0.70], radius=6, fill=(215, 235, 255))
    img = img.filter(ImageFilter.GaussianBlur(1.2))
    capa_burbujas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    db = ImageDraw.Draw(capa_burbujas)
    random.seed(14)
    for i in range(16):
        x = W * 0.5 + random.uniform(-130, 130)
        y = H * 0.62 - random.uniform(20, 400)
        r = random.uniform(4, 18)
        alpha = max(15, 130 - int(y / 3.2))
        col = (140, 210, 255) if i % 2 == 0 else (255, 200, 140)
        db.ellipse([x - r, y - r, x + r, y + r], fill=(*col, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), capa_burbujas.filter(ImageFilter.GaussianBlur(2))).convert("RGB")
    guardar(img, destino)


def hacer_S028(destino):
    img = lienzo_con_glow((3, 8, 10), W * 0.5, H * 0.32, 560, (50, 150, 170), fuerza=0.5)
    d = ImageDraw.Draw(img)
    d.rectangle([W * 0.68, H * 0.14, W * 0.86, H * 0.34], outline=(60, 35, 18), width=7)
    d.rectangle([W * 0.695, H * 0.155, W * 0.845, H * 0.325], fill=(14, 26, 30))
    d.rectangle([0, H * 0.72, W, H * 0.76], fill=(9, 15, 17))
    figura_con_borde_de_luz(img, W * 0.40, H * 0.76, H * 0.46, W * 0.15, (60, 190, 210), cabeza_inclinada=1.4)
    figura_con_borde_de_luz(img, W * 0.58, H * 0.76, H * 0.50, W * 0.17, (60, 190, 210), cabeza_inclinada=0.4)
    guardar(img, destino)


def hacer_S036(destino):
    img = lienzo_con_glow((4, 4, 8), W * 0.62, H * 0.40, 460, (60, 120, 160), fuerza=0.45)
    d = ImageDraw.Draw(img)
    random.seed(36)
    for fila in range(4):
        for col in range(6):
            x = W * 0.55 + col * 48 + random.uniform(-6, 6)
            y = H * 0.16 + fila * 60 + random.uniform(-6, 6)
            tam = 13
            color = (225, 45, 45) if random.random() > 0.35 else (70, 25, 25)
            d.line([(x - tam, y - tam), (x + tam, y + tam)], fill=color, width=4)
            d.line([(x - tam, y + tam), (x + tam, y - tam)], fill=color, width=4)
    img = img.filter(ImageFilter.GaussianBlur(0.5))
    figura_con_borde_de_luz(img, W * 0.34, H * 0.90, H * 0.55, W * 0.17, (70, 150, 190), cabeza_inclinada=2.2)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([W * 0.295, H * 0.715, W * 0.345, H * 0.795], radius=4, fill=(2, 2, 2))
    guardar(img, destino)


def hacer_S079(destino):
    img = lienzo_con_glow((2, 2, 3), W * 0.5, H * 0.28, 540, (255, 180, 75), fuerza=1.0)
    figura_con_borde_de_luz(img, W * 0.44, H * 0.92, H * 0.62, W * 0.19, (255, 150, 60), cabeza_inclinada=0.6)
    figura_con_borde_de_luz(img, W * 0.58, H * 0.90, H * 0.58, W * 0.17, (255, 150, 60), cabeza_inclinada=-0.4)
    d = ImageDraw.Draw(img)
    d.polygon([(W * 0.52, H * 0.55), (W * 0.60, H * 0.53), (W * 0.66, H * 0.62), (W * 0.60, H * 0.66)], fill=(4, 3, 3))
    guardar(img, destino)


def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: python scripts/pack_ilustrar_a_mano.py content/<carpeta-pack>")
    carpeta = Path(sys.argv[1]).resolve()
    img_dir = carpeta / "img"
    hacer_S002(img_dir / "S002.jpg")
    hacer_S014(img_dir / "S014.jpg")
    hacer_S028(img_dir / "S028.jpg")
    hacer_S036(img_dir / "S036.jpg")
    hacer_S079(img_dir / "S079.jpg")
    print("Listo.")


if __name__ == "__main__":
    main()
