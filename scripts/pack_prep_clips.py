"""Termina el Paso 4 del PACK: ajusta cada clip real a la duración exacta de
su toma (+0,4s de solape, igual que las imágenes) con ffmpeg — recorte,
desaceleración o loop+crossfade según haga falta (sección "Reglas de
encaje" del PACK.md).

Uso:
    python scripts/pack_prep_clips.py content/<carpeta-pack>

No necesita red (los clips ya están descargados por pack_clips.py). Escribe
clips/fit/<ID>.mp4 — eso es lo que lee remotion/src/longform/ShotClip.tsx.
"""

import json
import subprocess
import sys
from pathlib import Path

FPS = 30
OVERLAP_S = 0.4
RECORTE_DESDE_S = 0.5
VELOCIDAD_MIN = 0.85


def duracion_de(ruta):
    salida = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(ruta)],
        capture_output=True, text=True, check=True,
    )
    return float(json.loads(salida.stdout)["format"]["duration"])


def ajustar(origen, destino, objetivo_s):
    fuente_s = duracion_de(origen)
    disponible = fuente_s - RECORTE_DESDE_S

    if disponible >= objetivo_s:
        # Recorte simple desde 0.5s.
        subprocess.run(
            ["ffmpeg", "-y", "-ss", str(RECORTE_DESDE_S), "-i", str(origen), "-t", str(objetivo_s),
             "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", str(destino)],
            check=True, capture_output=True,
        )
        return "recorte"

    if fuente_s / VELOCIDAD_MIN >= objetivo_s:
        # Desacelerar (mínimo 0.85x) para estirar sin necesidad de loop.
        velocidad = max(VELOCIDAD_MIN, fuente_s / objetivo_s)
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(origen), "-t", str(objetivo_s / velocidad if velocidad < 1 else objetivo_s),
             "-vf", f"setpts={1/velocidad:.4f}*PTS", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             str(destino)],
            check=True, capture_output=True,
        )
        return f"desacelerado x{velocidad:.2f}"

    # Loop con crossfade de 0.4s en el punto de empalme.
    xfade_en = max(0.1, fuente_s - OVERLAP_S)
    filtro = f"[0:v][0:v]xfade=transition=fade:duration={OVERLAP_S}:offset={xfade_en:.2f}[v]"
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(origen), "-i", str(origen), "-filter_complex",
         f"[0:v][1:v]xfade=transition=fade:duration={OVERLAP_S}:offset={xfade_en:.2f}[v]",
         "-map", "[v]", "-t", str(objetivo_s), "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
         str(destino)],
        check=True, capture_output=True,
    )
    return "loop+crossfade"


def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: python scripts/pack_prep_clips.py content/<carpeta-pack>")
    carpeta = Path(sys.argv[1]).resolve()
    shots = json.loads((carpeta / "shots.json").read_text(encoding="utf-8"))["shots"]
    tomas = {t["id"]: t for t in json.loads((carpeta / "timeline.json").read_text(encoding="utf-8"))["tomas"]}

    carpeta_fit = carpeta / "clips" / "fit"
    carpeta_fit.mkdir(parents=True, exist_ok=True)

    for s in shots:
        if s["type"] != "clip":
            continue
        toma = tomas[s["id"]]
        objetivo = round(toma["endS"] - toma["startS"] + OVERLAP_S, 3)
        origen = carpeta / "clips" / f"{s['clip']['id']}.mp4"
        destino = carpeta_fit / f"{s['clip']['id']}.mp4"
        if not origen.exists():
            print(f"::warning::Falta el clip {origen.name} para la toma {s['id']}")
            continue
        metodo = ajustar(origen, destino, objetivo)
        print(f"  {s['clip']['id']}.mp4 -> {objetivo}s ({metodo})")

    print(f"\nListo: clips ajustados en {carpeta_fit}")


if __name__ == "__main__":
    main()
