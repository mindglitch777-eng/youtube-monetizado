"""Paso 9 del PACK de video largo: QA automático sobre out/video_final.mp4.

Uso:
    python scripts/pack_qa.py content/<carpeta-pack>

Escribe out/qa_report.txt y out/contact_sheet.jpg. Necesita ffmpeg
(instalado en este entorno vía apt) — no necesita red.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def correr(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def duracion_y_resolucion(video):
    salida = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height,r_frame_rate,codec_name:format=duration", "-of", "json", str(video)],
        capture_output=True, text=True, check=True,
    )
    datos = json.loads(salida.stdout)
    v = datos["streams"][0]
    return {
        "duracion": float(datos["format"]["duration"]),
        "ancho": v["width"], "alto": v["height"], "fps": v["r_frame_rate"], "codec": v["codec_name"],
    }


def blackdetect(video):
    r = correr(["ffmpeg", "-i", str(video), "-vf", "blackdetect=d=0.4:pic_th=0.98", "-an", "-f", "null", "-"])
    return re.findall(r"black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)", r.stderr)


def freezedetect(video):
    r = correr(["ffmpeg", "-i", str(video), "-vf", "freezedetect=n=-60dB:d=2", "-an", "-f", "null", "-"])
    return re.findall(r"freeze_start: ([\d.]+)", r.stderr) + re.findall(r"lavfi\.freezedetect\.freeze_duration=([\d.]+)", r.stderr)


def ebur128(video):
    r = correr(["ffmpeg", "-i", str(video), "-af", "ebur128=peak=true", "-f", "null", "-"])
    integrado = re.search(r"I:\s*(-?[\d.]+) LUFS", r.stderr)
    rango = re.search(r"LRA:\s*([\d.]+) LU", r.stderr)
    pico = re.search(r"Peak:\s*(-?[\d.]+) dBFS", r.stderr)
    return {
        "integrado_lufs": float(integrado.group(1)) if integrado else None,
        "lra": float(rango.group(1)) if rango else None,
        "true_peak_dbfs": float(pico.group(1)) if pico else None,
    }


def contact_sheet(video, tomas, destino, ancho_col=6):
    frames_pedidos = [max(0, t["startFrame"] + 2) for t in tomas]
    fps = 30
    tmp_dir = destino.parent / "_cs_frames"
    tmp_dir.mkdir(exist_ok=True)
    rutas = []
    for i, fr in enumerate(frames_pedidos):
        t = fr / fps
        out = tmp_dir / f"f{i:03d}.jpg"
        subprocess.run(["ffmpeg", "-y", "-ss", str(t), "-i", str(video), "-vframes", "1",
                        "-vf", "scale=320:-1", str(out)], check=True, capture_output=True)
        rutas.append(out)
    filas = [rutas[i:i + ancho_col] for i in range(0, len(rutas), ancho_col)]
    lista_txt = tmp_dir / "_lista.txt"
    entrada_filtro = []
    cmd = ["ffmpeg", "-y"]
    for r in rutas:
        cmd += ["-i", str(r)]
    n = len(rutas)
    filtro = "".join(f"[{i}:v]" for i in range(n)) + f"xstack=inputs={n}:layout=" + \
        "|".join(f"{(i % ancho_col) * 320}_{(i // ancho_col) * 180}" for i in range(n)) + "[out]"
    cmd += ["-filter_complex", filtro, "-map", "[out]", str(destino)]
    subprocess.run(cmd, check=True, capture_output=True)
    for r in rutas:
        r.unlink()
    tmp_dir.rmdir()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("carpeta")
    args = parser.parse_args()
    carpeta = Path(args.carpeta).resolve()
    video = carpeta / "out" / "video_final.mp4"
    if not video.exists():
        sys.exit(f"No existe {video} — correr pack_mezcla.py primero.")

    timeline = json.loads((carpeta / "timeline.json").read_text(encoding="utf-8"))
    tomas = timeline["tomas"]

    info = duracion_y_resolucion(video)
    negros = blackdetect(video)
    congelados = freezedetect(video)
    audio = ebur128(video)

    max_gap = max((tomas[i + 1]["startS"] - tomas[i]["startS"] for i in range(len(tomas) - 1)), default=0)

    lineas = []
    lineas.append("=== QA — he-never-raised-his-voice ===\n")
    lineas.append(f"1) Formato: {info['ancho']}x{info['alto']} @ {info['fps']} ({info['codec']}) — "
                  f"{'OK' if (info['ancho'], info['alto']) == (1920, 1080) else 'FALLA'}")
    minutos, segundos = divmod(int(info["duracion"]), 60)
    lineas.append(f"   Duración real: {minutos}:{segundos:02d} ({info['duracion']:.2f}s)")
    lineas.append(f"   Máx. tiempo entre cambios visuales (inicio de toma a inicio de toma): {max_gap:.2f}s — "
                  f"{'OK (<=10s)' if max_gap <= 10 else 'FALLA (>10s)'}")
    lineas.append(f"   Toma más larga registrada en timeline.json: {timeline['tomaMasLarga']['id']} "
                  f"({timeline['tomaMasLarga']['duracion']:.2f}s)")
    lineas.append(f"   Tomas divididas por N2: {timeline['tomasDivididas'] or 'ninguna'}")
    lineas.append("")
    lineas.append(f"2) blackdetect (d=0.4, pic_th=0.98): {len(negros)} tramos detectados")
    for ini, fin, dur in negros:
        marca = "OK (dip)" if float(dur) < 0.5 else "REVISAR (>0.5s)"
        lineas.append(f"     {ini}s -> {fin}s ({dur}s) — {marca}")
    lineas.append(f"   freezedetect (n=-60dB, d=2): {len(congelados)} eventos — "
                  f"{'OK' if not congelados else 'REVISAR'}")
    for c in congelados:
        lineas.append(f"     {c}")
    lineas.append("")
    lineas.append("3) ebur128:")
    lineas.append(f"   Integrado: {audio['integrado_lufs']} LUFS (objetivo -14 ±1) — "
                  f"{'OK' if audio['integrado_lufs'] and abs(audio['integrado_lufs'] + 14) <= 1 else 'REVISAR'}")
    lineas.append(f"   LRA: {audio['lra']} LU")
    lineas.append(f"   True peak: {audio['true_peak_dbfs']} dBFS (objetivo <= -1) — "
                  f"{'OK' if audio['true_peak_dbfs'] and audio['true_peak_dbfs'] <= -1 else 'REVISAR'}")
    lineas.append("")
    lineas.append(f"4) contact_sheet.jpg: 1 frame por toma ({len(tomas)} tomas) — ver archivo adjunto.")
    lineas.append("")
    lineas.append("5) Revisión manual de la hoja de contactos: hacerla aparte y anotar acá cualquier "
                  "problema visible (texto en imágenes, caras, cortes raros, placas vacías).")

    (carpeta / "out" / "qa_report.txt").write_text("\n".join(lineas), encoding="utf-8")
    print("\n".join(lineas))

    print("\nArmando contact_sheet.jpg ...")
    contact_sheet(video, tomas, carpeta / "out" / "contact_sheet.jpg")
    print(f"Listo: {carpeta / 'out' / 'qa_report.txt'} y {carpeta / 'out' / 'contact_sheet.jpg'}")


if __name__ == "__main__":
    main()
