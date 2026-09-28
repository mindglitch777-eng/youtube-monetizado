"""Paso 5 + 8 del PACK de video largo: arma la mezcla final de audio
(voz + sfx + música con ducking) y la muxea sobre el render mudo de
Remotion.

Uso:
    python scripts/pack_mezcla.py content/<carpeta-pack> [--video-mudo out/video_silent.mp4]

Necesita ffmpeg (instalado en este entorno vía apt) — no necesita red.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

VOLUMENES_SFX = {
    "whoosh_a": 0.55, "whoosh_b": 0.60, "hit_deep": 0.80, "hit_soft": 0.50,
    "tick": 0.35, "riser": 0.50, "glitch": 0.45, "sting_end": 0.90,
}
CROSSFADE_MUSICA_S = 2.0
COLA_CIERRE_S = 0.35


def ffprobe_dur(ruta):
    salida = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ruta)],
        capture_output=True, text=True, check=True,
    )
    return float(salida.stdout.strip())


def armar_sfx_track(carpeta, shots, timeline, destino):
    """adelay por cada instancia + amix, en un solo wav de la duración total."""
    tomas = {t["id"]: t for t in timeline["tomas"]}
    entradas, filtros_delay, etiquetas = [], [], []
    for s in shots:
        toma = tomas.get(s["id"])
        if not toma or not s.get("sfx"):
            continue
        for sfx in s["sfx"]:
            archivo = carpeta / "sfx" / f"{sfx['name']}.wav"
            if not archivo.exists():
                print(f"::warning::sfx {sfx['name']} no existe ({archivo})")
                continue
            inicio_abs = toma["startS"] + sfx["offset_s"]
            ms = max(0, round(inicio_abs * 1000))
            idx = len(entradas)
            entradas.append(str(archivo))
            vol = VOLUMENES_SFX.get(sfx["name"], 0.5)
            filtros_delay.append(f"[{idx}:a]volume={vol},adelay={ms}|{ms}[s{idx}]")
            etiquetas.append(f"[s{idx}]")

    if not entradas:
        print("Sin sfx para mezclar (raro) — genero un silencio.")
        subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                        "-t", str(timeline["duracionTotal"]), str(destino)], check=True, capture_output=True)
        return

    cmd = ["ffmpeg", "-y"]
    for e in entradas:
        cmd += ["-i", e]
    filtro = ";".join(filtros_delay) + ";" + "".join(etiquetas) + f"amix=inputs={len(etiquetas)}:normalize=0[mix]"
    cmd += ["-filter_complex", filtro, "-map", "[mix]", "-t", str(timeline["duracionTotal"]), str(destino)]
    subprocess.run(cmd, check=True, capture_output=True)


def armar_musica(carpeta, timeline, snap_shot_id, destino):
    """bed_dark hasta 1.5s antes de la grieta, crossfade de 2s a bed_warm, -22dB."""
    musica_dir = carpeta / "music"
    oscura = musica_dir / ("tension.mp3" if (musica_dir / "tension.mp3").exists() else "bed_dark.mp3")
    calida = musica_dir / ("warm.mp3" if (musica_dir / "warm.mp3").exists() else "bed_warm.mp3")

    tomas = {t["id"]: t for t in timeline["tomas"]}
    grieta_s = tomas[snap_shot_id]["startS"] if snap_shot_id in tomas else timeline["duracionTotal"] * 0.85
    corte_s = max(0.0, grieta_s - 1.5)
    duracion_total = timeline["duracionTotal"]

    dur_oscura = ffprobe_dur(oscura)
    dur_calida = ffprobe_dur(calida)
    reps_oscura = max(1, int((corte_s + CROSSFADE_MUSICA_S) // dur_oscura) + 2)
    reps_calida = max(1, int((duracion_total - corte_s) // dur_calida) + 2)

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", str(reps_oscura), "-i", str(oscura),
        "-stream_loop", str(reps_calida), "-i", str(calida),
        "-filter_complex",
        f"[0:a]atrim=0:{corte_s + CROSSFADE_MUSICA_S},volume=-22dB[a0];"
        f"[1:a]atrim=0:{duracion_total - corte_s},volume=-22dB[a1];"
        f"[a0][a1]acrossfade=d={CROSSFADE_MUSICA_S}:c1=tri:c2=tri[mus]",
        "-map", "[mus]", "-t", str(duracion_total), str(destino),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("carpeta")
    parser.add_argument("--video-mudo", default="out/video_silent.mp4")
    args = parser.parse_args()
    carpeta = Path(args.carpeta).resolve()

    shots = json.loads((carpeta / "shots.json").read_text(encoding="utf-8"))["shots"]
    timeline = json.loads((carpeta / "timeline.json").read_text(encoding="utf-8"))
    snap_shot_id = next((s["id"] for s in shots if s.get("thread", {}).get("state") == "snap"), None)

    carpeta_out = carpeta / "out"
    carpeta_out.mkdir(exist_ok=True)
    voz = carpeta / "audio" / "voice.wav"
    voz_norm = carpeta_out / "_voz_norm.wav"
    sfx_track = carpeta_out / "_sfx_track.wav"
    musica_track = carpeta_out / "_musica.wav"
    premix = carpeta_out / "_premix.wav"
    master = carpeta_out / "_master.wav"

    print("Voz: normalizando a -16 LUFS ...")
    subprocess.run(["ffmpeg", "-y", "-i", str(voz), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                    str(voz_norm)], check=True, capture_output=True)

    print("SFX: armando pista ...")
    armar_sfx_track(carpeta, shots, timeline, sfx_track)

    print(f"Música: bed_dark -> crossfade {CROSSFADE_MUSICA_S}s -> bed_warm en la grieta ({snap_shot_id}) ...")
    armar_musica(carpeta, timeline, snap_shot_id, musica_track)

    print("Mezclando voz + sfx + música (sidechain de música contra la voz) ...")
    duracion_total = timeline["duracionTotal"]
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(voz_norm), "-i", str(sfx_track), "-i", str(musica_track),
        "-filter_complex",
        "[2:a][0:a]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=500[musduck];"
        "[0:a][1:a][musduck]amix=inputs=3:normalize=0[premix]",
        "-map", "[premix]", "-t", str(duracion_total + COLA_CIERRE_S), str(premix),
    ], check=True, capture_output=True)

    print("Master: loudnorm -14 LUFS, TP -1.5dB ...")
    subprocess.run(["ffmpeg", "-y", "-i", str(premix), "-af",
                    "loudnorm=I=-14:TP=-1.5:LRA=11", str(master)], check=True, capture_output=True)

    video_mudo = carpeta / args.video_mudo
    if not video_mudo.exists():
        print(f"::warning::No existe {video_mudo} todavía (correr el Paso 7 de Remotion antes) — "
              f"la mezcla de audio quedó en {master}, falta muxear.")
        return

    destino = carpeta_out / "video_final.mp4"
    print(f"Muxeando sobre {video_mudo.name} -> {destino.name} ...")
    subprocess.run(["ffmpeg", "-y", "-i", str(video_mudo), "-i", str(master),
                    "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", str(destino)], check=True, capture_output=True)
    print(f"Listo: {destino}")


if __name__ == "__main__":
    main()
