#!/usr/bin/env python3
"""
Sintetiza los efectos y la música del video 2 con numpy/scipy: nada descargado,
nada con derechos de autor. Salida: video2/work/sfx/*.wav (48 kHz).

Efectos: timbre del despertador, golpe (smash), flash, whoosh, punch, sonido de
"juego" (cartel que sube), y un ambiente por época (viento, cincel, temblor,
multitud, latidos/toses, flautas/tambores, lluvia, gotas/tic-tac, canilla).
Música: un loop tranquilo por época, con su propio color (tonalidad, tempo e
instrumento), pensado para ir por debajo de la voz.
"""
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
OUT = Path(__file__).resolve().parent.parent / "work" / "sfx"
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(11)


def t(d):
    return np.arange(int(SR * d)) / SR


def tn(n):
    return np.arange(n) / SR


def env(n, a=0.002, r=0.1):
    x = np.arange(n) / SR
    return np.minimum(1, x / max(a, 1e-4)) * np.exp(-x / max(r, 1e-4))


def filt(x, kind, f, order=4):
    return sosfilt(butter(order, f, kind, fs=SR, output="sos"), x)


def reverb(x, dur=1.5, mix=0.3):
    n = int(SR * dur)
    ir = filt(rng.standard_normal(n), "low", 5000) * np.exp(-np.arange(n) / SR / (dur / 5))
    w = fftconvolve(x, ir)[:len(x)]
    w /= np.max(np.abs(w)) + 1e-9
    return (1 - mix) * x / (np.max(np.abs(x)) + 1e-9) + mix * w


def save(name, x, peak=0.9):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    x = x / (np.max(np.abs(x)) + 1e-9) * peak
    wavfile.write(OUT / f"{name}.wav", SR, (x * 32767).astype(np.int16))


def pad(x, d):
    y = np.zeros(int(SR * d))
    y[:min(len(x), len(y))] = x[:len(y)]
    return y


# ------------------------------------------------------------------ efectos
# timbre de despertador mecánico: martillo sobre dos campanas (0,9 s)
x = t(0.9)
timbre = np.zeros(len(x))
for k in range(int(0.9 * 22)):
    i = int(SR * k / 22)
    n = len(x) - i
    golpe = (np.sin(2 * np.pi * 2350 * tn(n)) + 0.7 * np.sin(2 * np.pi * 3120 * tn(n)) + 0.3 * np.sin(2 * np.pi * 5200 * tn(n)))
    timbre[i:] += golpe * env(n, 0.0005, 0.03)
timbre *= np.minimum(1, (0.9 - x) / 0.08)
save("timbre", timbre, 0.8)
# timbre lento (Tenochtitlan y 1348): menos golpes, más grave
x = t(1.4)
lento = np.zeros(len(x))
for k in range(7):
    i = int(SR * k * 0.2)
    n = len(x) - i
    lento[i:] += (np.sin(2 * np.pi * 1700 * tn(n)) + 0.5 * np.sin(2 * np.pi * 2260 * tn(n))) * env(n, 0.001, 0.08)
save("timbre_lento", reverb(lento, 1.2, 0.3), 0.7)

# golpe seco para el SMASH (impacto grave corto)
x = t(0.6)
f = 120 * (35 / 120) ** (x / 0.6)
smash = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(x), 0.001, 0.12) + 0.5 * filt(rng.standard_normal(len(x)), "low", 700) * env(len(x), 0.0005, 0.04)
save("smash", smash)

# punch (zoom de impacto): golpe medio con "thump"
x = t(0.3)
punch = np.sin(2 * np.pi * 90 * x) * env(len(x), 0.001, 0.06) + 0.4 * filt(rng.standard_normal(len(x)), "band", [800, 3000]) * env(len(x), 0.0005, 0.02)
save("punch", punch, 0.7)

# flash: brillo que sube (0,35 s)
x = t(0.35)
fl = filt(rng.standard_normal(len(x)), "high", 2500) * (x / 0.35) ** 2 * np.minimum(1, (0.35 - x) / 0.02)
save("flash", fl, 0.5)

# whoosh (barrido)
x = t(0.35)
w = rng.standard_normal(len(x))
w = np.concatenate([filt(w[i:i + 1200], "band", [300 + 3000 * i / len(x), 900 + 5000 * i / len(x)], 2) for i in range(0, len(x), 1200)])[:len(x)]
save("whoosh", w * np.sin(np.pi * x / 0.35) ** 2, 0.6)

# "juego": cartel que sube (dos notas tipo videojuego)
x = t(0.25)
juego = np.concatenate([np.sign(np.sin(2 * np.pi * 660 * x[:len(x) // 2])), np.sign(np.sin(2 * np.pi * 990 * x[len(x) // 2:]))])
save("juego", filt(juego, "low", 4000) * env(len(x), 0.002, 0.12), 0.35)

# logro: arpegio corto brillante
x = t(0.6)
logro = sum(np.sin(2 * np.pi * fr * x) * ((x > d) * env(len(x), 0.002, 0.25) if True else 1) for fr, d in ((784, 0), (988, 0.08), (1175, 0.16), (1568, 0.24)))
save("logro", reverb(logro * np.minimum(1, (0.6 - x) / 0.1), 1.0, 0.25), 0.45)

# ------------------------------------------------------------------ ambientes (loops de 8 s)
D = 8.0
x = t(D)
ruido = rng.standard_normal(len(x))
borde = np.minimum(1, x / 0.3) * np.minimum(1, (D - x) / 0.3)

viento = filt(ruido, "band", [200, 1100], 2) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.3 * x) * np.sin(2 * np.pi * 0.11 * x))
save("amb_hielo", viento * borde, 0.5)

cincel = np.zeros(len(x))
for s in np.arange(0.3, D, 0.62) + rng.uniform(-0.05, 0.05, int(D / 0.62) + 1)[:len(np.arange(0.3, D, 0.62))]:
    i = int(s * SR)
    n = min(int(0.12 * SR), len(x) - i)
    cincel[i:i + n] += (filt(rng.standard_normal(n), "band", [2500, 7000]) + 0.6 * np.sin(2 * np.pi * 3400 * tn(n))) * env(n, 0.0005, 0.02)
save("amb_egipto", (cincel + 0.15 * filt(ruido, "band", [300, 900], 2)) * borde, 0.45)

temblor = filt(ruido, "low", 90) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 0.4 * x)))
save("amb_pompeya", temblor * borde, 0.6)

multitud = sum(filt(rng.standard_normal(len(x)), "band", [f, f * 1.6], 2) * (0.6 + 0.4 * np.sin(2 * np.pi * r * x + p))
               for f, r, p in ((300, 0.5, 0), (600, 0.7, 1), (1100, 0.9, 2), (1800, 0.6, 3)))
save("amb_roma", multitud * borde, 0.5)

peste = np.zeros(len(x))
for s in np.arange(0.2, D, 1.0):
    i = int(s * SR)
    for d, a in ((0, 1), (0.25, 0.8)):
        n = int(0.18 * SR)
        j = i + int(d * SR)
        if j + n < len(x):
            peste[j:j + n] += a * np.sin(2 * np.pi * 52 * t(0.18)) * env(n, 0.004, 0.05)
for s in (2.3, 5.6):  # toses lejanas
    i, n = int(s * SR), int(0.25 * SR)
    peste[i:i + n] += 0.3 * filt(rng.standard_normal(n), "band", [400, 2200]) * env(n, 0.003, 0.06)
save("amb_1348", filt(peste, "low", 2500) * borde + 0.05 * filt(ruido, "low", 400), 0.55)

# flauta y tambores (Tenochtitlan): pentatónica tranquila
fl = np.zeros(len(x))
notas = [392, 440, 523, 587, 659, 587, 523, 440]
for k, fr in enumerate(notas):
    i, n = int(k * SR), int(0.95 * SR)
    tt = t(0.95)
    fl[i:i + n] += np.sin(2 * np.pi * fr * tt + 0.02 * np.sin(2 * np.pi * 5 * tt)) * np.minimum(1, tt / 0.08) * np.minimum(1, (0.95 - tt) / 0.2)
tam = np.zeros(len(x))
for s in np.arange(0, D, 0.5):
    i, n = int(s * SR), int(0.3 * SR)
    tam[i:i + n] += (1 if int(s * 2) % 2 == 0 else 0.6) * np.sin(2 * np.pi * 75 * t(0.3)) * env(n, 0.002, 0.07)
save("amb_tenochtitlan", (0.35 * fl + 0.7 * tam) * borde, 0.5)

lluvia = filt(ruido, "high", 1500) * 0.5
for s in rng.uniform(0, D, 140):
    i, n = int(s * SR), int(0.02 * SR)
    if i + n < len(x):
        lluvia[i:i + n] += rng.uniform(0.3, 1) * filt(rng.standard_normal(n), "band", [2000, 6000]) * env(n, 0.0003, 0.004)
save("amb_1816", lluvia * borde, 0.4)
x2 = t(2.5)
f = 60 * (30 / 60) ** (x2 / 2.5)
save("trueno", filt(rng.standard_normal(len(x2)), "low", 220) * env(len(x2), 0.05, 0.7) + 0.4 * np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(x2), 0.02, 0.6), 0.8)

gotas = np.zeros(len(x))
for s in np.arange(0.4, D, 0.9):
    i, n = int(s * SR), int(0.15 * SR)
    tt = t(0.15)
    gotas[i:i + n] += np.sin(2 * np.pi * (1200 + 900 * np.exp(-tt * 40)) * tt) * env(n, 0.001, 0.03)
tictac = np.zeros(len(x))
for k in range(int(D * 2)):
    i, n = int(k * 0.5 * SR), int(0.03 * SR)
    tictac[i:i + n] += filt(rng.standard_normal(n), "band", [3000 if k % 2 else 1800, 7000]) * env(n, 0.0003, 0.006)
save("amb_londres", (0.6 * gotas + 0.5 * tictac) * borde, 0.45)

x3 = t(2.5)
canilla = filt(rng.standard_normal(len(x3)), "band", [500, 4000], 2) * np.minimum(1, x3 / 0.1) * np.minimum(1, (2.5 - x3) / 0.3)
save("canilla", canilla, 0.4)

# ------------------------------------------------------------------ música: un loop de 16 s por época
def nota(fr, d, forma="seno"):
    tt = t(d)
    if forma == "seno":
        s = np.sin(2 * np.pi * fr * tt)
    elif forma == "suave":
        s = np.sin(2 * np.pi * fr * tt) + 0.3 * np.sin(4 * np.pi * fr * tt)
    else:  # pluck
        s = np.sin(2 * np.pi * fr * tt) * np.exp(-tt * 5) + 0.3 * np.sin(4 * np.pi * fr * tt) * np.exp(-tt * 8)
    return s * np.minimum(1, tt / 0.03) * np.minimum(1, (d - tt) / 0.15)


def musica(nombre, acordes, tempo, forma, bajo=True, D=16.0):
    n = int(D * SR)
    y = np.zeros(n)
    paso = 60 / tempo
    for k in range(int(D / (paso * 4))):
        ac = acordes[k % len(acordes)]
        i = int(k * paso * 4 * SR)
        for fr in ac:  # colchón
            s = 0.25 * nota(fr, paso * 4, "suave")
            y[i:i + len(s)] += s[:n - i]
        for b in range(4):  # arpegio
            j = i + int(b * paso * SR)
            s = 0.35 * nota(ac[b % len(ac)] * 2, paso * 0.95, forma)
            y[j:j + len(s)] += s[:n - j]
        if bajo:
            s = 0.4 * nota(ac[0] / 2, paso * 4, "seno")
            y[i:i + len(s)] += s[:n - i]
    y = reverb(filt(y, "low", 5000), 2.0, 0.3)
    f = int(0.05 * SR)
    y[:f] *= np.linspace(0, 1, f)
    y[-f:] *= np.linspace(1, 0, f)
    save(nombre, y, 0.6)


H = lambda *n: [261.63 * 2 ** (k / 12) for k in n]
musica("mus_gancho", [H(0, 4, 7), H(-3, 0, 4), H(-7, -3, 0), H(-5, -1, 2)], 112, "pluck")
musica("mus_hielo", [H(-3, 0, 4), H(-7, -3, 0), H(-5, -2, 2), H(-3, 0, 4)], 84, "seno")
musica("mus_egipto", [H(2, 5, 9), H(1, 5, 8), H(2, 5, 9), H(0, 3, 7)], 96, "pluck")
musica("mus_pompeya", [H(-3, 0, 3), H(-4, -1, 3), H(-3, 0, 3), H(-5, -2, 2)], 90, "seno")
musica("mus_roma", [H(0, 4, 7), H(5, 9, 12), H(7, 11, 14), H(0, 4, 7)], 120, "pluck")
musica("mus_1348", [H(-3, 0, 3), H(-3, 0, 3), H(-4, -1, 3), H(-4, -1, 3)], 66, "seno", bajo=True)
musica("mus_tenochtitlan", [H(2, 7, 11), H(0, 4, 9), H(2, 7, 11), H(-1, 4, 7)], 100, "pluck")
musica("mus_1816", [H(-3, 0, 4), H(-8, -3, 0), H(-5, -1, 2), H(-3, 0, 4)], 70, "seno")
musica("mus_londres", [H(-5, -2, 2), H(-3, 0, 3), H(-5, -2, 2), H(-7, -3, 0)], 80, "pluck")
musica("mus_cierre", [H(0, 4, 7), H(5, 9, 12), H(-3, 0, 4), H(7, 11, 14)], 92, "suave")
print("listo:", len(list(OUT.glob("*.wav"))), "archivos")
