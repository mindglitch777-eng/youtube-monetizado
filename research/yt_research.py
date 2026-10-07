#!/usr/bin/env python3
"""
Herramienta de investigación de estilo de video (imágenes IA + narración +
cortes) para encontrar y medir canales reales. Corre dentro de GitHub
Actions (tiene internet real) — no se usa localmente en el sandbox de
Claude, que tiene la red bloqueada.

Tres modos:

  discover  Busca candidatos reales por texto (sin API key, yt-dlp) y los
            ordena por una señal simple de "crecimiento rápido" (vistas
            sobre antigüedad del video). Devuelve JSON a stdout.

  frames    Saca 4-6 frames de muestra de UN video (sin bajar el archivo
            completo — usa la URL directa del stream) para que un humano
            o Claude confirme a ojo si el estilo visual calza (dibujo IA,
            formato de subtítulos, etc.) antes de gastar tiempo en el
            análisis completo.

  analyze   Baja el video elegido, mide cortes de escena, volumen (LUFS),
            silencios, y junta metadata real (vistas, fecha, canal,
            suscriptores si yt-dlp los expone, fecha del video más viejo
            del canal como aproximación de antigüedad). Devuelve JSON a
            stdout y también lo imprime en formato tabla para el Summary
            de Actions.

Requiere: pip install yt-dlp  /  apt-get install ffmpeg
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yt_dlp


def log(msg):
    print(msg, file=sys.stderr)


def discover(query, limit, content_type):
    ydl_opts_flat = {
        "quiet": True,
        "extract_flat": "in_playlist",
        "skip_download": True,
    }
    search_prefix = f"ytsearch{limit}"
    with yt_dlp.YoutubeDL(ydl_opts_flat) as ydl:
        info = ydl.extract_info(f"{search_prefix}:{query}", download=False)
    entries = info.get("entries") or []

    candidates = []
    for e in entries:
        if not e:
            continue
        video_id = e.get("id")
        if not video_id:
            continue
        candidates.append({
            "id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "title": e.get("title"),
            "channel": e.get("channel") or e.get("uploader"),
            "channel_url": e.get("channel_url") or e.get("uploader_url"),
            "duration": e.get("duration"),
            "view_count_flat": e.get("view_count"),
        })

    # Para los primeros N (por orden de aparición en la búsqueda), sacamos
    # metadata real (vistas exactas, fecha, suscriptores si están expuestos).
    enriched = []
    ydl_opts_full = {"quiet": True, "skip_download": True}
    with yt_dlp.YoutubeDL(ydl_opts_full) as ydl:
        for c in candidates:
            try:
                full = ydl.extract_info(c["url"], download=False)
            except Exception as err:
                log(f"no pude leer {c['url']}: {err}")
                continue
            upload_date = full.get("upload_date")  # YYYYMMDD
            view_count = full.get("view_count")
            days_old = None
            views_per_day = None
            if upload_date:
                try:
                    d = datetime.strptime(upload_date, "%Y%m%d").replace(tzinfo=timezone.utc)
                    days_old = max(1, (datetime.now(timezone.utc) - d).days)
                    if view_count:
                        views_per_day = round(view_count / days_old, 1)
                except ValueError:
                    pass
            is_short = (full.get("duration") or 0) <= 70
            if content_type == "short" and not is_short:
                continue
            if content_type == "long" and is_short:
                continue
            enriched.append({
                "id": c["id"],
                "url": c["url"],
                "title": full.get("title"),
                "channel": full.get("channel") or full.get("uploader"),
                "channel_id": full.get("channel_id"),
                "channel_url": full.get("channel_url") or full.get("uploader_url"),
                "channel_follower_count": full.get("channel_follower_count"),
                "duration_seconds": full.get("duration"),
                "view_count": view_count,
                "upload_date": upload_date,
                "days_since_upload": days_old,
                "views_per_day": views_per_day,
            })

    enriched.sort(key=lambda x: (x["views_per_day"] or 0), reverse=True)
    print(json.dumps({"query": query, "content_type": content_type, "candidates": enriched}, indent=2, ensure_ascii=False))


def frames(video_url, count, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    ydl_opts = {"quiet": True, "skip_download": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
    duration = info.get("duration") or 30

    # URL directa del mejor formato progresivo (video+audio juntos si existe,
    # si no el mejor de video) para poder "seekear" con ffmpeg sin bajar
    # el archivo entero.
    direct_url = None
    fmts = info.get("formats") or []
    progressive = [f for f in fmts if f.get("vcodec") != "none" and f.get("acodec") != "none" and f.get("url")]
    pick_from = progressive if progressive else [f for f in fmts if f.get("vcodec") != "none" and f.get("url")]
    if pick_from:
        pick_from.sort(key=lambda f: (f.get("height") or 0))
        direct_url = pick_from[-1]["url"]

    if not direct_url:
        print(json.dumps({"error": "no encontré una URL directa de video para sacar frames"}))
        return

    timestamps = [max(1, int(duration * frac)) for frac in
                  [0.05, 0.25, 0.45, 0.65, 0.85, 0.95][:count]]

    saved = []
    for i, t in enumerate(timestamps, 1):
        out_path = out / f"frame_{i:02d}_t{t}s.jpg"
        cmd = [
            "ffmpeg", "-y", "-ss", str(t), "-i", direct_url,
            "-frames:v", "1", "-q:v", "3", str(out_path),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if out_path.exists():
            saved.append(str(out_path))
        else:
            log(f"no pude sacar frame en t={t}s: {res.stderr[-500:]}")

    print(json.dumps({
        "video_url": video_url,
        "title": info.get("title"),
        "duration": duration,
        "frames": saved,
    }, indent=2, ensure_ascii=False))


def _channel_earliest_video_date(channel_url):
    """Aproxima la antigüedad del canal con la fecha de su video más viejo
    visible (yt-dlp no expone de forma confiable la fecha de creación del
    canal en sí)."""
    try:
        ydl_opts = {"quiet": True, "extract_flat": "in_playlist", "skip_download": True, "playlistend": 500}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
        entries = [e for e in (info.get("entries") or []) if e]
        # extract_flat no siempre trae upload_date; si no está, devolvemos None
        dates = [e.get("upload_date") or e.get("timestamp") for e in entries]
        dates = [d for d in dates if d]
        if not dates:
            return None, len(entries)
        # upload_date es string YYYYMMDD; timestamp es epoch — normalizamos a string comparable
        str_dates = []
        for d in dates:
            if isinstance(d, str):
                str_dates.append(d)
            else:
                str_dates.append(datetime.fromtimestamp(d, tz=timezone.utc).strftime("%Y%m%d"))
        return min(str_dates), len(entries)
    except Exception as err:
        log(f"no pude estimar antigüedad del canal: {err}")
        return None, None


def analyze(video_url, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    video_path = out / "video.mp4"

    ydl_opts = {
        "quiet": True,
        "outtmpl": str(video_path),
        "format": "best[ext=mp4]/best",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)

    channel_url = info.get("channel_url") or info.get("uploader_url")
    earliest_date, channel_videos_seen = (None, None)
    if channel_url:
        earliest_date, channel_videos_seen = _channel_earliest_video_date(channel_url)

    # 1) Cortes de escena
    cuts = []
    cmd_cuts = [
        "ffmpeg", "-i", str(video_path),
        "-vf", "select='gt(scene,0.3)',showinfo",
        "-f", "null", "-",
    ]
    res = subprocess.run(cmd_cuts, capture_output=True, text=True, timeout=600)
    for line in res.stderr.splitlines():
        if "pts_time:" in line:
            try:
                t = float(line.split("pts_time:")[1].split()[0])
                cuts.append(round(t, 2))
            except (IndexError, ValueError):
                pass

    # 2) Volumen (loudnorm, da el LUFS integrado real)
    loudness = None
    cmd_loud = [
        "ffmpeg", "-i", str(video_path),
        "-af", "loudnorm=print_format=json",
        "-f", "null", "-",
    ]
    res = subprocess.run(cmd_loud, capture_output=True, text=True, timeout=300)
    try:
        json_start = res.stderr.rindex("{")
        json_end = res.stderr.rindex("}") + 1
        loudness = json.loads(res.stderr[json_start:json_end])
    except (ValueError, json.JSONDecodeError):
        pass

    # 3) Silencios
    silences = []
    cmd_sil = [
        "ffmpeg", "-i", str(video_path),
        "-af", "silencedetect=noise=-30dB:d=0.3",
        "-f", "null", "-",
    ]
    res = subprocess.run(cmd_sil, capture_output=True, text=True, timeout=300)
    cur_start = None
    for line in res.stderr.splitlines():
        if "silence_start:" in line:
            try:
                cur_start = float(line.split("silence_start:")[1].split()[0])
            except (IndexError, ValueError):
                cur_start = None
        elif "silence_end:" in line and cur_start is not None:
            try:
                end = float(line.split("silence_end:")[1].split("|")[0].strip())
                silences.append({"start": round(cur_start, 2), "end": round(end, 2), "dur": round(end - cur_start, 2)})
            except (IndexError, ValueError):
                pass
            cur_start = None

    duration = info.get("duration") or 0
    cuts_per_sec = round(len(cuts) / duration, 3) if duration else None

    result = {
        "video_url": video_url,
        "title": info.get("title"),
        "channel": info.get("channel") or info.get("uploader"),
        "channel_url": channel_url,
        "channel_follower_count": info.get("channel_follower_count"),
        "channel_earliest_video_seen": earliest_date,
        "channel_videos_seen_count": channel_videos_seen,
        "upload_date": info.get("upload_date"),
        "view_count": info.get("view_count"),
        "like_count": info.get("like_count"),
        "duration_seconds": duration,
        "cuts_timestamps": cuts,
        "cuts_count": len(cuts),
        "cuts_per_second": cuts_per_sec,
        "integrated_loudness_lufs": (loudness or {}).get("input_i"),
        "true_peak_dbtp": (loudness or {}).get("input_tp"),
        "silences": silences,
        "silence_total_seconds": round(sum(s["dur"] for s in silences), 2),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)

    p1 = sub.add_parser("discover")
    p1.add_argument("--query", required=True)
    p1.add_argument("--limit", type=int, default=15)
    p1.add_argument("--content-type", choices=["short", "long"], default="short")

    p2 = sub.add_parser("frames")
    p2.add_argument("--video-url", required=True)
    p2.add_argument("--count", type=int, default=6)
    p2.add_argument("--out-dir", default="out_frames")

    p3 = sub.add_parser("analyze")
    p3.add_argument("--video-url", required=True)
    p3.add_argument("--out-dir", default="out_analyze")

    args = ap.parse_args()
    if args.mode == "discover":
        discover(args.query, args.limit, args.content_type)
    elif args.mode == "frames":
        frames(args.video_url, args.count, args.out_dir)
    elif args.mode == "analyze":
        analyze(args.video_url, args.out_dir)


if __name__ == "__main__":
    main()
