#!/usr/bin/env python3
"""Mezcla de audio desde un timeline: voz (0 dB), música (-22 dB con ducking bajo la voz y
silencios pedidos) y efectos (gain por evento). Salida: WAV estéreo 44.1 kHz.
Uso: python3 mezcla.py work/timeline.json remotion/public/mezcla.wav"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.io import wavfile

R = Path(__file__).resolve().parent.parent
SR = 44100


def leer(path):
    """Decodifica cualquier audio a float32 mono 44.1 kHz con ffmpeg."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def db(x):
    return 10 ** (x / 20)


def main(tl_path, out_path):
    tl = json.loads(Path(tl_path).read_text())
    n = int(SR * (tl["duracion"] + 0.5))
    voz = np.zeros(n, np.float32)
    sfx = np.zeros(n, np.float32)
    mus = np.zeros(n, np.float32)
    # voz
    for v in tl["voz"]:
        a = leer(R / f"work/voz/{v['n']:03d}.mp3")
        s0 = int(v["src_ini"] * SR)
        seg = a[s0:s0 + int(v["dur"] * SR)]
        f = int(0.01 * SR)
        seg[:f] *= np.linspace(0, 1, f)
        seg[-f:] *= np.linspace(1, 0, f)
        i = int(v["ini"] * SR)
        voz[i:i + len(seg)] += seg[: n - i]
    # normalizar voz a un nivel de referencia (pico de habla ~ -3 dBFS)
    voz *= 0.7 / (np.percentile(np.abs(voz[voz != 0]), 99.5) + 1e-9)
    # efectos
    cache = {}
    for e in tl["sfx"]:
        if e["f"] not in cache:
            cache[e["f"]] = leer(R / f"assets/sfx/{e['f']}.wav")
        a = cache[e["f"]] * db(e.get("g", -8)) * 1.4
        i = int(e["t"] * SR)
        if i >= n:
            continue
        sfx[i:i + len(a)] += a[: n - i]
    # música (loop)
    for m in tl["musica"]:
        a = leer(R / f"assets/sfx/{m['f']}.wav")
        i0, i1 = int(m["ini"] * SR), min(n, int(m["fin"] * SR))
        largo = i1 - i0
        reps = int(np.ceil(largo / len(a)))
        seg = np.tile(a, reps)[:largo]
        f = int(0.8 * SR)
        seg[:f] *= np.linspace(0, 1, f)
        seg[-f:] *= np.linspace(1, 0, f)
        mus[i0:i1] += seg
    mus *= db(-22) / (np.sqrt(np.mean(mus[mus != 0] ** 2)) + 1e-9) * 0.25  # RMS base bajo la voz
    # ducking: envolvente de la voz suavizada
    w = int(0.05 * SR)
    envv = np.convolve(np.abs(voz), np.ones(w) / w, mode="same")
    activa = (envv > 0.02).astype(np.float32)
    k = int(0.25 * SR)
    activa = np.convolve(activa, np.ones(k) / k, mode="same").clip(0, 1)
    mus *= 1 - 0.5 * activa  # -6 dB extra mientras hay voz
    # silencios pedidos
    gate = np.ones(n, np.float32)
    for a, b in tl["silencios"]:
        i, j = int(a * SR), int(b * SR)
        gate[i:j] = 0
    k = int(0.12 * SR)
    gate = np.convolve(gate, np.ones(k) / k, mode="same")
    mus *= gate
    mix = voz + mus + sfx
    pico = np.max(np.abs(mix))
    if pico > 0.98:
        mix *= 0.98 / pico
    st = np.stack([mix, mix], axis=1)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(out_path, SR, (st * 32767).astype(np.int16))
    print("ok", out_path, f"{len(mix) / SR:.1f} s")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
