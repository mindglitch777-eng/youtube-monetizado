"""Paso 1 (parte local, sin red) del PACK de video largo: une los bloques de
voz ya sintetizados (scripts/pack_voz.py), los convierte a wav, alinea cada
palabra con su toma de shots.json y arma timeline.json.

Uso:
    python scripts/pack_timeline.py content/<carpeta-pack>

No necesita red: corre acá mismo (edge-tts ya generó los bloques en GitHub
Actions). Sí necesita ffmpeg/ffprobe (instalados en este entorno vía apt).

N2 del PACK: ninguna toma puede durar más de 9,5s de audio real — si una
toma calculada supera eso, se divide en dos mitades (mismo id, dos tramos
en timeline.json) con un cambio de encuadre (flash) en el corte.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

FPS = 30
SILENCIO_ENTRE_BLOQUES = 0.3
COLA_FINAL = 0.8
MAX_TOMA_S = 9.5
CAPITULOS = ["HOOK", "C1", "C2", "C3", "C4", "C5", "C6"]


def normalizar(texto):
    return re.sub(r"[^a-z0-9']", "", texto.lower())


def alinear_capitulo(shots_cap, palabras_bloque):
    """Reparte las palabras ya sintetizadas (con tiempo relativo al bloque)
    entre las tomas de ese capítulo, en orden — mismo algoritmo de
    caminar-tokens que scripts/generar_short.py (repartir_palabras)."""
    tokens = [(s["id"], t) for s in shots_cap for t in s["narration"].split()]
    i = 0
    asignadas = {s["id"]: [] for s in shots_cap}
    for palabra in palabras_bloque:
        buscada = normalizar(palabra["texto"])
        if not buscada:
            if i > 0:
                asignadas[tokens[i - 1][0]].append(palabra)
            continue
        encontrada = False
        for j in range(i, min(i + 6, len(tokens))):
            if buscada in normalizar(tokens[j][1]):
                asignadas[tokens[j][0]].append(palabra)
                i = j + 1
                encontrada = True
                break
        if not encontrada and i > 0:
            asignadas[tokens[i - 1][0]].append(palabra)
    return asignadas


def ffmpeg_concat_con_silencios(mp3s, destino_wav, silencio_s):
    """Concatena mp3s con un silencio de silencio_s entre cada uno, en un
    único wav (mono 44.1kHz no hace falta; se deja el sample rate nativo)."""
    tmp = destino_wav.parent
    silencio = tmp / "_silencio.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=24000:cl=mono", "-t", str(silencio_s), str(silencio)],
        check=True, capture_output=True,
    )
    lista = tmp / "_concat.txt"
    partes = []
    for k, mp3 in enumerate(mp3s):
        wav_parte = tmp / f"_parte{k}.wav"
        subprocess.run(["ffmpeg", "-y", "-i", str(mp3), str(wav_parte)], check=True, capture_output=True)
        partes.append(wav_parte)
        if k < len(mp3s) - 1:
            partes.append(silencio)
    lista.write_text("\n".join(f"file '{p.name}'" for p in partes), encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lista), "-c", "pcm_s16le", str(destino_wav)],
                   check=True, capture_output=True, cwd=tmp)
    silencio.unlink(missing_ok=True)
    lista.unlink(missing_ok=True)
    for k in range(len(mp3s)):
        (tmp / f"_parte{k}.wav").unlink(missing_ok=True)


def duracion_de(ruta_wav):
    salida = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(ruta_wav)],
        capture_output=True, text=True, check=True,
    )
    return float(json.loads(salida.stdout)["format"]["duration"])


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("carpeta")
    args = parser.parse_args()
    carpeta = Path(args.carpeta).resolve()

    shots = json.loads((carpeta / "shots.json").read_text(encoding="utf-8"))["shots"]
    carpeta_audio = carpeta / "audio"

    bloques_meta = []
    for cap in CAPITULOS:
        meta = json.loads((carpeta_audio / f"bloque-{cap}.json").read_text(encoding="utf-8"))
        bloques_meta.append(meta)

    # --- Unir en un solo wav ---
    mp3s = [carpeta_audio / f"bloque-{cap}.mp3" for cap in CAPITULOS]
    voice_wav = carpeta_audio / "voice.wav"
    print("Uniendo bloques con ffmpeg (silencio de 0.3s entre cada uno) ...")
    ffmpeg_concat_con_silencios(mp3s, voice_wav, SILENCIO_ENTRE_BLOQUES)
    duracion_real_wav = duracion_de(voice_wav)
    print(f"audio/voice.wav: {duracion_real_wav:.2f}s")

    # --- Offset absoluto de cada bloque dentro del wav unido ---
    offsets = {}
    cursor = 0.0
    for cap, meta in zip(CAPITULOS, bloques_meta):
        offsets[cap] = cursor
        cursor += meta["duracion"] + SILENCIO_ENTRE_BLOQUES

    # --- Alinear palabras por capítulo ---
    palabras_abs_por_shot = {}
    for cap, meta in zip(CAPITULOS, bloques_meta):
        shots_cap = [s for s in shots if s["chapter"] == cap]
        asignadas = alinear_capitulo(shots_cap, meta["palabras"])
        offset = offsets[cap]
        for shot_id, palabras in asignadas.items():
            palabras_abs_por_shot[shot_id] = [
                {"texto": p["texto"], "inicio": round(p["inicio"] + offset, 3), "fin": round(p["fin"] + offset, 3)}
                for p in palabras
            ]

    # --- Chequeo de alineación: % de tomas sin ninguna palabra asignada ---
    sin_palabras = [s["id"] for s in shots if not palabras_abs_por_shot.get(s["id"])]
    if sin_palabras:
        print(f"::warning::{len(sin_palabras)} tomas sin ninguna palabra alineada: {sin_palabras}")

    # --- Armar tomas: inicio = primera palabra, fin = inicio de la siguiente ---
    tomas = []
    for idx, s in enumerate(shots):
        palabras = palabras_abs_por_shot.get(s["id"], [])
        inicio = palabras[0]["inicio"] if palabras else offsets[s["chapter"]]
        if idx + 1 < len(shots):
            siguiente_palabras = palabras_abs_por_shot.get(shots[idx + 1]["id"], [])
            fin = siguiente_palabras[0]["inicio"] if siguiente_palabras else inicio + s["est_dur_s"]
        else:
            fin = (palabras[-1]["fin"] if palabras else inicio) + COLA_FINAL
        tomas.append({"id": s["id"], "startS": round(inicio, 3), "endS": round(fin, 3), "palabras": palabras})

    # --- N2: dividir tomas > 9.5s ---
    tomas_finales = []
    divididas = []
    for t in tomas:
        duracion = t["endS"] - t["startS"]
        if duracion <= MAX_TOMA_S:
            tomas_finales.append(t)
            continue
        divididas.append(t["id"])
        mitad = t["startS"] + duracion / 2
        # la palabra más cercana a la mitad marca el corte real
        corte = min((p["inicio"] for p in t["palabras"]), key=lambda x: abs(x - mitad), default=mitad)
        tomas_finales.append({"id": t["id"], "startS": t["startS"], "endS": round(corte, 3),
                              "palabras": [p for p in t["palabras"] if p["inicio"] < corte], "dividida": True})
        tomas_finales.append({"id": t["id"], "startS": round(corte, 3), "endS": t["endS"],
                              "palabras": [p for p in t["palabras"] if p["inicio"] >= corte], "dividida": True,
                              "transitionOverride": "flash"})
    if divididas:
        print(f"Tomas > {MAX_TOMA_S}s divididas en dos: {divididas}")

    for t in tomas_finales:
        t["startFrame"] = round(t["startS"] * FPS)
        t["endFrame"] = round(t["endS"] * FPS)

    duracion_total = tomas_finales[-1]["endS"]
    toma_mas_larga = max(tomas_finales, key=lambda t: t["endS"] - t["startS"])

    timeline = {
        "fps": FPS,
        "audio": f"{carpeta.name}/audio/voice.wav",
        "duracionTotal": round(duracion_total, 3),
        "tomas": tomas_finales,
        "tomaMasLarga": {"id": toma_mas_larga["id"], "duracion": round(toma_mas_larga["endS"] - toma_mas_larga["startS"], 3)},
        "tomasDivididas": divididas,
    }
    (carpeta / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")

    minutos, segundos = divmod(int(duracion_total), 60)
    print(f"\nDuración real: {minutos}:{segundos:02d} ({duracion_total:.2f}s)")
    print(f"Toma más larga: {toma_mas_larga['id']} ({toma_mas_larga['endS'] - toma_mas_larga['startS']:.2f}s)")
    print(f"Tomas divididas por N2 (>{MAX_TOMA_S}s): {len(divididas)}")
    print(f"timeline.json: {carpeta / 'timeline.json'}")


if __name__ == "__main__":
    main()
