#!/usr/bin/env python3
"""
Prepara la voz del video 2 línea por línea (sin silencios).

- Narrador: video2/voz/narr_r16 (+16 %). Despertador: video2/voz/desp_alonso_r10.
- Se corta el silencio del principio y del final, y toda pausa entre palabras
  mayor a PAUSA_MAX queda en PAUSA_MAX. Los tiempos de cada palabra se
  recalculan sobre el audio ya recortado (sirven para los subtítulos de los Shorts).
- Despertador: "tic" al empezar + filtro metálico leve.
- Relator de Roma (E4_01, E4_05): filtro de estadio (megáfono + eco).

Salida: video2/work/voz/<id>.wav (mono 48 kHz) y video2/work/voz.json
"""
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

V = Path(__file__).resolve().parent.parent
OUT = V / "work" / "voz"
OUT.mkdir(parents=True, exist_ok=True)
SR = 48000
PAUSA_MAX = 0.15
NARR, DESP = "narr_r16", "desp_alonso_r10"
RELATOR = {"E4_01", "E4_05"}
FX_DESP = "highpass=f=250,lowpass=f=4200,aecho=0.8:0.6:7|13:0.35|0.25,volume=1.15"
FX_RELATOR = "highpass=f=350,lowpass=f=3800,aecho=0.8:0.7:60|110:0.3|0.2,volume=1.1"


def leer(p):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(p), "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"])
    return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768


def escribir(p, x):
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


def filtrar(x, fx):
    tmp = OUT / "_tmp.wav"
    escribir(tmp, x)
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(tmp), "-af", fx, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"])
    tmp.unlink()
    return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768


def tic():
    t = np.arange(int(0.045 * SR)) / SR
    return (np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 140) * 0.5).astype(np.float32)


def main():
    L = json.loads((V / "voz" / "lineas.json").read_text())
    info = {}
    for l in L:
        carpeta = DESP if l["rol"] == "despertador" else NARR
        base = V / "voz" / carpeta / l["n"]
        p = json.loads(base.with_suffix(".json").read_text())["palabras"]
        x = leer(base.with_suffix(".mp3"))
        # tramos a conservar
        tramos = [[max(0.0, p[0]["ini"] - 0.02), p[0]["fin"]]]
        for a, b in zip(p, p[1:]):
            if b["ini"] - a["fin"] > PAUSA_MAX:
                tramos[-1][1] = a["fin"] + PAUSA_MAX / 2
                tramos.append([b["ini"] - PAUSA_MAX / 2, b["fin"]])
            else:
                tramos[-1][1] = b["fin"]
        tramos[-1][1] = min(len(x) / SR, tramos[-1][1] + 0.06)
        # recorte y nuevos tiempos de palabra
        partes, nuevo, acum = [], [], 0.0
        for a, b in tramos:
            partes.append(x[int(a * SR):int(b * SR)])
            for w in p:
                if a - 1e-6 <= w["ini"] < b:
                    nuevo.append({"w": w["w"], "ini": round(acum + w["ini"] - a, 3), "fin": round(acum + min(w["fin"], b) - a, 3)})
            acum += b - a
        y = np.concatenate(partes)
        # fundidos de 5 ms para que no haya clics en los cortes
        f = int(0.005 * SR)
        y[:f] *= np.linspace(0, 1, f)
        y[-f:] *= np.linspace(1, 0, f)
        if l["rol"] == "despertador":
            y = filtrar(y, FX_DESP)
            t = tic()
            y = np.concatenate([t, np.zeros(int(0.03 * SR), np.float32), y])
            corr = (len(t) + int(0.03 * SR)) / SR
            nuevo = [{**w, "ini": round(w["ini"] + corr, 3), "fin": round(w["fin"] + corr, 3)} for w in nuevo]
        elif l["n"] in RELATOR:
            y = filtrar(y, FX_RELATOR)
        escribir(OUT / f"{l['n']}.wav", y)
        info[l["n"]] = {"dur": round(len(y) / SR, 3), "palabras": nuevo, "rol": l["rol"], "texto": l["texto"],
                        "bloque": l["bloque"], "corte_short": l["corte_short"], "solo_short": l["solo_short"]}
    (V / "work" / "voz.json").write_text(json.dumps(info, ensure_ascii=False, indent=1))
    largo = sum(v["dur"] for v in info.values() if not v["solo_short"])
    print(f"{len(info)} líneas; voz del largo {largo:.1f} s")


if __name__ == "__main__":
    main()
