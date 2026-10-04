#!/usr/bin/env python3
"""Estado de cada episodio/idioma: cuántas imágenes hay, si ya llegó la
voz, y si el video final ya está. Mismo cálculo que hace el workflow de
GitHub Actions antes de decidir si renderiza.

Uso:
    python tools/status.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    filas = []
    for script_path in sorted(ROOT.glob("episodes/*/*/script.json")):
        lang = script_path.parent.name
        slug = script_path.parent.parent.name
        script = json.loads(script_path.read_text(encoding="utf-8"))
        expected = script["imageCount"]
        img_dir = ROOT / "public" / "episodes" / slug / "images"
        have = len(list(img_dir.glob("*.png"))) if img_dir.exists() else 0
        timing = ROOT / "public" / "episodes" / slug / lang / "timing.json"
        video = ROOT / "out" / f"{slug}-{lang}.mp4"
        filas.append((slug, lang, have, expected, timing.exists(), video.exists()))

    ancho_slug = max((len(f[0]) for f in filas), default=8)
    print(f"{'episodio':<{ancho_slug}}  idioma  imágenes   voz     video final")
    for slug, lang, have, expected, voz_ok, video_ok in filas:
        imagenes = f"{have}/{expected}" + (" " if have == expected else "  FALTAN")
        voz = "lista " if voz_ok else "falta "
        video = "LISTO ✅" if video_ok else "falta"
        print(f"{slug:<{ancho_slug}}  {lang:<6}  {imagenes:<10} {voz} {video}")


if __name__ == "__main__":
    main()
