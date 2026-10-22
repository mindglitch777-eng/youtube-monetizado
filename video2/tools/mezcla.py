#!/usr/bin/env python3
"""
Mezcla el audio del video 2 a partir de un archivo de eventos (voz, efectos, música, ambiente).

Números fijos de la instrucción:
  - música 20 dB por debajo de la voz, y 4 dB más abajo mientras habla alguien;
  - ambiente un poco más bajo que la música, también con bajada bajo la voz;
  - efectos nunca más fuertes que la voz (salvo el timbre, breve);
  - volumen final −14 LUFS integrado y pico real máximo −1 dBTP (ffmpeg loudnorm en dos pasadas).

  python3 video2/tools/mezcla.py <eventos.json> <salida.wav>
"""
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.ndimage import uniform_filter1d

V = Path(__file__).resolve().parent.parent
SR = 48000


def leer_wav(p):
    sr, x = wavfile.read(p)
    x = x.astype(np.float32) / 32768
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    assert sr == SR, p
    return x


def rms(x):
    return float(np.sqrt(np.mean(x ** 2)) + 1e-9)


def db(v):
    return 10 ** (v / 20)


def main(eventos, salida):
    ev = json.loads(Path(eventos).read_text())
    n = int((ev["duracion"] + 0.5) * SR)
    voz = np.zeros((n, 2), np.float32)
    for e in ev["voz"]:
        if e["rol"] == "tic":
            tt = np.arange(int(0.045 * SR)) / SR
            x = np.sin(2 * np.pi * 3200 * tt) * np.exp(-tt * 140) * 0.5
            x = np.stack([x, x], 1)
        else:
            x = leer_wav(V / "work" / "voz" / f"{e['id']}.wav")
        i = int(e["t"] * SR)
        voz[i:i + len(x)] += x[:n - i]
    hablado = np.abs(voz[:, 0]) > 0.01
    ref = rms(voz[hablado]) if hablado.any() else 0.1
    # actividad de voz suavizada (para la bajada de la música)
    act = uniform_filter1d(hablado.astype(np.float32), int(0.25 * SR))
    act = np.clip(act * 3, 0, 1)

    def pista(segmentos, nivel_db, bajada_db):
        y = np.zeros((n, 2), np.float32)
        for k, s in enumerate(segmentos):
            if not s["nombre"]:
                continue
            ini = int(s["ini"] * SR)
            fin = int(segmentos[k + 1]["ini"] * SR) if k + 1 < len(segmentos) else n
            x = leer_wav(V / "work" / "sfx" / f"{s['nombre']}.wav")
            x = x / rms(x) * ref * db(nivel_db)
            reps = int(np.ceil((fin - ini) / len(x))) + 1
            loop = np.tile(x, (reps, 1))[:fin - ini]
            f = min(int(0.3 * SR), len(loop) // 2)
            if f:
                loop[:f] *= np.linspace(0, 1, f)[:, None]
                loop[-f:] *= np.linspace(1, 0, f)[:, None]
            y[ini:fin] += loop
        return y * (1 - act * (1 - db(-bajada_db)))[:, None]

    musica = pista(ev["musica"], -20, 4)
    ambiente = pista(ev["ambiente"], -24, 4)
    for s in ev.get("silencios", []):
        a, b = int(s["ini"] * SR), int(s["fin"] * SR)
        musica[a:b] = 0
        ambiente[a:b] = 0
    efectos = np.zeros((n, 2), np.float32)
    pico_voz = float(np.max(np.abs(voz))) + 1e-9
    for e in ev["sfx"]:
        x = leer_wav(V / "work" / "sfx" / f"{e['nombre']}.wav")
        tope = 0.9 if e["nombre"].startswith("timbre") else 0.6
        x = x / (np.max(np.abs(x)) + 1e-9) * pico_voz * tope * e["gain"]
        i = int(e["t"] * SR)
        if i < 0:
            x, i = x[-i:], 0
        efectos[i:i + len(x)] += x[:n - i]
    mez = voz + musica + ambiente + efectos
    mez /= max(1.0, float(np.max(np.abs(mez))) / 0.95)
    tmp = Path(salida).with_suffix(".premix.wav")
    with wave.open(str(tmp), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mez * 32767).astype("<i2").tobytes())
    # loudnorm en dos pasadas
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(tmp), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"):])
    filtro = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
              f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-af", filtro, "-ar", str(SR), str(salida)], check=True)
    tmp.unlink()
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(salida), "-af", "loudnorm=I=-14:TP=-1:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"):])
    print(f"{salida}: {m['input_i']} LUFS, pico {m['input_tp']} dBTP, {ev['duracion']:.1f} s")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
