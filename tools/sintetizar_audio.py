#!/usr/bin/env python3
"""Sintetiza todos los efectos y la música del video con numpy/scipy (sin descargas ni copyright).
Salida: assets/sfx/*.wav (44.1 kHz, mono salvo la música en estéreo)."""
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
OUT = Path(__file__).resolve().parent.parent / "assets/sfx"
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(7)


def t(d):
    return np.arange(int(SR * d)) / SR


def env(n, a=0.002, r=0.1):
    x = np.arange(n) / SR
    e = np.minimum(1, x / max(a, 1e-4)) * np.exp(-x / max(r, 1e-4))
    return e


def bp(x, lo, hi, order=4):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x)


def lp(x, f, order=4):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x)


def hp(x, f, order=4):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x)


def reverb(x, dur=1.6, mix=0.35):
    n = int(SR * dur)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR / (dur / 5))
    ir = lp(ir, 6000)
    w = fftconvolve(x, ir)[: len(x) + n]
    w /= np.max(np.abs(w)) + 1e-9
    y = np.concatenate([x, np.zeros(n)])[: len(w)]
    return (1 - mix) * y / (np.max(np.abs(y)) + 1e-9) + mix * w


def save(name, x, peak=0.9):
    x = np.asarray(x, dtype=np.float64)
    x = x / (np.max(np.abs(x)) + 1e-9) * peak
    wavfile.write(OUT / f"{name}.wav", SR, (x * 32767).astype(np.int16))


# clic metálico seco (candado)
n = int(SR * 0.09)
clic = bp(rng.standard_normal(n), 2500, 7000) * env(n, 0.0005, 0.012)
clic += 0.6 * np.sin(2 * np.pi * 3200 * t(0.09)) * env(n, 0.0005, 0.02)
clic += 0.4 * np.sin(2 * np.pi * 5100 * t(0.09)) * env(n, 0.0005, 0.015)
save("clic", clic)
# siete clics seguidos (0.12 s)
siete = np.zeros(int(SR * (0.12 * 6 + 0.12)))
for k in range(7):
    i = int(SR * 0.12 * k)
    siete[i:i + len(clic)] += clic
save("siete_clics", siete)

# golpe de piedra y golpe fuerte
def golpe(d, f0, f1, ruido):
    x = t(d)
    f = f0 * (f1 / f0) ** (x / d)
    tono = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(x), 0.002, d / 4)
    rr = lp(rng.standard_normal(len(x)), 900) * env(len(x), 0.001, 0.06) * ruido
    return tono + rr


save("golpe_piedra", golpe(0.8, 110, 40, 0.9))
save("golpe_fuerte", reverb(golpe(1.3, 90, 28, 1.4) + 0.6 * golpe(1.3, 55, 25, 0.5), 2.0, 0.3))

# whoosh
x = t(0.3)
w = rng.standard_normal(len(x))
w = np.concatenate([bp(w[i:i + 1323], 300 + 4000 * (i / len(x)), 800 + 6000 * (i / len(x)), 2) for i in range(0, len(x), 1323)])[: len(x)]
save("whoosh", w * np.sin(np.pi * x / 0.3) ** 2, 0.7)

# latido (dos pulsos graves)
def pulso(d=0.18, f=55):
    x = t(d)
    return np.sin(2 * np.pi * f * x) * env(len(x), 0.004, 0.05)


lat = np.zeros(int(SR * 0.7))
p = pulso()
lat[: len(p)] += p
lat[int(SR * 0.25): int(SR * 0.25) + len(p)] += 0.8 * pulso(0.18, 50)
save("latido", lp(lat, 300))

# acorde de asombro (mayor, 1.5 s, reverb)
x = t(1.5)
ac = sum(np.sin(2 * np.pi * f * x) * (0.6 if f < 300 else 0.35) for f in (261.63, 329.63, 392.0, 523.25, 659.25))
ac *= np.minimum(1, x / 0.15) * np.exp(-x / 1.2)
save("acorde_asombro", reverb(ac, 2.0, 0.4), 0.8)

# bostezo cómico: glide hacia abajo con ruido
x = t(1.2)
f = 420 * (180 / 420) ** (x / 1.2)
bo = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.6 + 0.4 * bp(rng.standard_normal(len(x)), 300, 1500)
bo *= np.sin(np.pi * x / 1.2)
save("bostezo", lp(bo, 2500), 0.7)

# viento
x = t(4.0)
vi = rng.standard_normal(len(x))
mod = 0.6 + 0.4 * np.sin(2 * np.pi * 0.35 * x) * np.sin(2 * np.pi * 0.13 * x)
vi = bp(vi, 200, 1200, 2) * mod * np.minimum(1, x / 0.8) * np.minimum(1, (4 - x) / 0.8)
save("viento", vi, 0.6)

# tictac
tt = np.zeros(int(SR * 2.0))
for k in range(4):
    i = int(SR * 0.5 * k)
    c = bp(rng.standard_normal(1500), 1500 if k % 2 else 2200, 5000) * env(1500, 0.0003, 0.006)
    tt[i:i + 1500] += c
save("tictac", tt, 0.7)

# vidrio roto
x = t(0.9)
vr = hp(rng.standard_normal(len(x)), 3000) * env(len(x), 0.001, 0.15)
for f in (2900, 4100, 5300, 6800, 7900):
    st = rng.integers(0, int(SR * 0.4))
    seg = np.sin(2 * np.pi * f * t(0.3)) * env(int(SR * 0.3), 0.0005, 0.05)
    vr[st:st + len(seg)] += 0.4 * seg[: len(vr) - st]
save("vidrio_roto", vr, 0.8)

# pop (aparece texto)
x = t(0.12)
f = 900 * (300 / 900) ** (x / 0.12)
save("pop", np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(x), 0.001, 0.03), 0.8)

# ding (dato)
x = t(1.2)
di = sum(np.sin(2 * np.pi * f * x) * a for f, a in ((1318.5, 1), (2637, 0.35), (3955, 0.15))) * env(len(x), 0.001, 0.35)
save("ding", di, 0.7)

# respiración
x = t(2.4)
re = np.zeros(len(x))
for k in (0, 1.2):
    i = int(SR * k)
    seg = bp(rng.standard_normal(int(SR * 1.0)), 400, 2200, 2) * np.sin(np.pi * t(1.0) / 1.0) ** 2
    re[i:i + len(seg)] += seg
save("respiracion", re, 0.6)

# ---------- música ----------
def musica_misterio(d=60.0):
    x = t(d)
    # pedal grave D2 con quinta, pulso suave de 72 bpm, pad que respira
    pad = (np.sin(2 * np.pi * 73.42 * x) + 0.6 * np.sin(2 * np.pi * 110 * x) + 0.3 * np.sin(2 * np.pi * 146.83 * x))
    pad *= 0.6 + 0.4 * np.sin(2 * np.pi * x / 8)
    pad = lp(pad, 800)
    puls = np.zeros(len(x))
    beat = 60 / 72
    for k in range(int(d / beat)):
        i = int(SR * k * beat)
        p = pulso(0.25, 49 if k % 4 else 55)
        puls[i:i + len(p)] += p[: len(puls) - i]
    # notas sueltas inquietantes (menor)
    mel = np.zeros(len(x))
    notas = [293.66, 349.23, 311.13, 261.63, 233.08, 277.18]
    for k in range(int(d / 4)):
        i = int(SR * (k * 4 + 1.5))
        nd = t(2.5)
        s = np.sin(2 * np.pi * notas[k % len(notas)] * nd) * np.minimum(1, nd / 0.4) * np.exp(-nd / 1.0)
        mel[i:i + len(s)] += 0.25 * s[: len(mel) - i]
    m = 0.55 * pad + 0.5 * puls + mel
    m = reverb(m, 2.5, 0.3)[: len(x)]
    # loop limpio: fundido de 1 s en los bordes
    f = int(SR * 1.0)
    m[:f] *= np.linspace(0, 1, f)
    m[-f:] *= np.linspace(1, 0, f)
    return m


def musica_calida(d=60.0):
    x = t(d)
    acordes = [(261.63, 329.63, 392.0), (220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (196.0, 246.94, 293.66)]
    m = np.zeros(len(x))
    for k in range(int(d / 4)):
        i = int(SR * k * 4)
        nd = t(4.2)
        ch = sum(np.sin(2 * np.pi * f * nd) + 0.3 * np.sin(2 * np.pi * 2 * f * nd) for f in acordes[k % 4])
        ch *= np.minimum(1, nd / 0.6) * np.minimum(1, (4.2 - nd) / 0.6)
        m[i:i + len(ch)] += ch[: len(m) - i]
        for j in range(8):  # arpegio suave
            ii = i + int(SR * j * 0.5)
            s = np.sin(2 * np.pi * acordes[k % 4][j % 3] * 2 * t(0.6)) * env(int(SR * 0.6), 0.005, 0.25)
            m[ii:ii + len(s)] += 0.5 * s[: len(m) - ii]
    m = reverb(lp(m, 4000), 2.0, 0.25)[: len(x)]
    f = int(SR * 1.0)
    m[:f] *= np.linspace(0, 1, f)
    m[-f:] *= np.linspace(1, 0, f)
    return m


for nombre, fn in (("musica_misterio", musica_misterio), ("musica_calida", musica_calida)):
    m = fn()
    est = np.stack([m, np.roll(m, int(SR * 0.012))], axis=1)  # ancho estéreo leve
    est = est / (np.max(np.abs(est)) + 1e-9) * 0.8
    wavfile.write(OUT / f"{nombre}.wav", SR, (est * 32767).astype(np.int16))
print("ok", sorted(p.name for p in OUT.glob("*.wav")))
