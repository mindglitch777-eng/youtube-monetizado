#!/usr/bin/env python3
"""
Mide la voz real del video 2 por bloque y la compara con la tabla C del guion.

Para el video largo se usan todas las líneas menos las ⚑ (solo para Shorts).
Voz real de un bloque = suma de la duración de cada línea + 0,25 s de aire por
línea + 0,6 s extra por cada frase del Despertador (su efecto), igual que el
método de la tabla C. Los "extras" (separadores, tabla, pausas) se toman de la
tabla C tal cual, porque no son voz.

  python3 video2/medir_voz.py <carpeta_narrador> <carpeta_despertador>
"""
import json
import subprocess
import sys
from pathlib import Path

V = Path(__file__).parent
L = json.loads((V / "voz" / "lineas.json").read_text())
# tabla C del guion: bloque -> (voz calculada en s, extras en s)
TABLA = {"H": (50, 2), "E1": (53, 4), "E2": (56, 4), "E3": (65, 4), "E4": (48, 4), "M": (16, 4),
         "E5": (53, 4), "E6": (55, 6), "E7": (70, 4), "E8": (54, 4), "C": (60, 14)}
NOMBRE = {"H": "Gancho-tráiler", "E1": "Época 1 · Hielo", "E2": "Época 2 · Egipto", "E3": "Época 3 · Pompeya",
          "E4": "Época 4 · Roma", "M": "Mitad · tabla parcial", "E5": "Época 5 · 1348", "E6": "Época 6 · Tenochtitlan",
          "E7": "Época 7 · 1816", "E8": "Época 8 · Londres", "C": "Cierre y tabla"}


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]))


def mmss(s):
    return f"{int(s // 60)}:{s % 60:04.1f}"


def main(narr, desp):
    filas, tot_c, tot_r = [], 0, 0
    for b, (voz_c, extra) in TABLA.items():
        real = 0
        for l in L:
            if l["bloque"] != b or l["solo_short"]:
                continue
            carpeta = desp if l["rol"] == "despertador" else narr
            real += dur(V / "voz" / carpeta / f"{l['n']}.mp3") + 0.25 + (0.6 if l["rol"] == "despertador" else 0)
        filas.append((NOMBRE[b], voz_c, round(real, 1), extra))
        tot_c += voz_c + extra
        tot_r += real + extra
    print("| Bloque | Voz calculada (s) | Voz real (s) | Diferencia | Extras (s) |")
    print("|---|---|---|---|---|")
    for n, c, r, e in filas:
        print(f"| {n} | {c} | {r} | {r - c:+.1f} | {e} |")
    print(f"| **TOTAL con extras** | **{mmss(tot_c)}** | **{mmss(tot_r)}** | {tot_r - tot_c:+.1f} s | |")
    return tot_r


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
