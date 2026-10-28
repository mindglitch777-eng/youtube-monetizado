#!/usr/bin/env python3
"""
Corre en GitHub Actions (internet abierto). Baja:
  - miniaturas de research/miniaturas.json -> research/miniaturas/<canal>.jpg
    (una hoja por canal: el video más visto + 3 recientes, con etiqueta)
  - transcripciones de research/transcribir.txt -> research/transcripciones/<id>.txt
    probando varios métodos en orden y anotando cuál funcionó.

Métodos de transcripción (se usa el primero que devuelva texto):
  1. youtube-transcript-api
  2. yt-dlp + proveedor de PO token (bgutil, servidor local en :4416)
  3. instancias públicas de Invidious (/api/v1/captions)
  4. yt-dlp con otros clientes del reproductor
"""
import io
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"}
log = []


def note(msg):
    print(msg, flush=True)
    log.append(msg)


# ---------------- miniaturas ----------------
def thumb(vid):
    for q in ("maxresdefault", "hqdefault", "mqdefault"):
        r = requests.get(f"https://i.ytimg.com/vi/{vid}/{q}.jpg", headers=UA, timeout=20)
        if r.status_code == 200 and len(r.content) > 2000:
            return Image.open(io.BytesIO(r.content)).convert("RGB")
    return None


def miniaturas():
    spec = json.loads((ROOT / "miniaturas.json").read_text())
    out = ROOT / "miniaturas"
    out.mkdir(exist_ok=True)
    font = ImageFont.load_default(size=22)
    for canal, ids in spec.items():
        safe = re.sub(r"[^\w-]+", "_", canal).strip("_")[:40] or "canal"
        if (out / f"{safe}.jpg").exists():
            continue
        imgs = [(v, thumb(v)) for v in ids]
        imgs = [(v, i.resize((480, 270))) for v, i in imgs if i]
        if not imgs:
            note(f"miniaturas FALLO {canal}")
            continue
        sheet = Image.new("RGB", (480 * len(imgs), 270 + 34), "white")
        d = ImageDraw.Draw(sheet)
        for k, (v, im) in enumerate(imgs):
            sheet.paste(im, (480 * k, 34))
            d.text((480 * k + 6, 6), ("MÁS VISTO " if k == 0 else "reciente ") + v, fill="black", font=font)
        safe = re.sub(r"[^\w-]+", "_", canal).strip("_")[:40] or "canal"
        sheet.save(out / f"{safe}.jpg", quality=80)
        note(f"miniaturas OK {canal} ({len(imgs)})")


# ---------------- transcripciones ----------------
def vtt_to_text(vtt):
    lines, last, ts = [], None, 0
    for raw in vtt.splitlines():
        m = re.match(r"(\d\d):(\d\d):(\d\d)\.\d+ -->", raw)
        if m:
            ts = int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3])
            continue
        t = re.sub(r"<[^>]+>", "", raw).strip()
        if not t or t == last or raw.startswith(("WEBVTT", "Kind:", "Language:")) or "-->" in raw:
            continue
        lines.append(f"[{ts // 60:02d}:{ts % 60:02d}] {t}")
        last = t
    return "\n".join(lines)


def m_transcript_api(vid, lang, proxy=None):
    from youtube_transcript_api import YouTubeTranscriptApi
    kw = {}
    if proxy:
        from youtube_transcript_api.proxies import GenericProxyConfig
        kw["proxy_config"] = GenericProxyConfig(http_url=proxy.replace("socks5://", "socks5h://"), https_url=proxy.replace("socks5://", "socks5h://"))
    t = YouTubeTranscriptApi(**kw).fetch(vid, languages=[lang, "en", "es", "pt"])
    return "\n".join(f"[{int(s.start) // 60:02d}:{int(s.start) % 60:02d}] {s.text}" for s in t.snippets)


def m_ytdlp(vid, lang, extra):
    with tempfile.TemporaryDirectory() as d:
        cmd = ["yt-dlp", "--skip-download", "--write-subs", "--write-auto-subs",
               "--sub-langs", f"{lang}-orig,{lang},{lang}.*", "--sub-format", "vtt",
               "-o", f"{d}/%(id)s", *extra, f"https://www.youtube.com/watch?v={vid}"]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        files = sorted(Path(d).glob("*.vtt"))
        if not files:
            raise RuntimeError((p.stderr.strip().splitlines() or ["sin vtt"])[-1][:200])
        return vtt_to_text(files[0].read_text(encoding="utf-8"))


INVIDIOUS = ["https://inv.nadeko.net", "https://yewtu.be", "https://invidious.nerdvpn.de",
             "https://invidious.f5.si", "https://inv.tux.pizza", "https://invidious.privacyredirect.com"]


def m_invidious(vid, lang):
    errs = []
    for base in INVIDIOUS:
        try:
            r = requests.get(f"{base}/api/v1/captions/{vid}", headers=UA, timeout=20)
            caps = r.json().get("captions", [])
            if not caps:
                errs.append(f"{base}: sin captions")
                continue
            pick = next((c for c in caps if c.get("language_code", c.get("languageCode", "")).startswith(lang)), caps[0])
            vtt = requests.get(base + pick["url"], headers=UA, timeout=30).text
            txt = vtt_to_text(vtt)
            if txt:
                return txt
        except Exception as e:  # noqa: BLE001
            errs.append(f"{base}: {type(e).__name__}")
    raise RuntimeError("; ".join(errs)[:300])


METHODS = [
    ("youtube-transcript-api", m_transcript_api),
    ("yt-dlp+po-token", lambda v, l: m_ytdlp(v, l, ["--extractor-args", "youtubepot-bgutilhttp:base_url=http://127.0.0.1:4416"])),
    ("invidious", m_invidious),
    ("yt-dlp mweb", lambda v, l: m_ytdlp(v, l, ["--extractor-args", "youtube:player_client=mweb"])),
    ("yt-dlp tv_simply", lambda v, l: m_ytdlp(v, l, ["--extractor-args", "youtube:player_client=tv_simply"])),
]


def transcripciones():
    out = ROOT / "transcripciones"
    out.mkdir(exist_ok=True)
    for line in (ROOT / "transcribir.txt").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        vid, lang = (line.split() + ["en"])[:2]
        if (out / f"{vid}.txt").exists():
            continue
        for name, fn in METHODS:
            try:
                txt = fn(vid, lang)
                if txt and len(txt) > 200:
                    (out / f"{vid}.txt").write_text(f"# método: {name}\n{txt}", encoding="utf-8")
                    note(f"transcripción OK {vid} con {name} ({len(txt)} caracteres)")
                    break
                note(f"transcripción {vid} {name}: vacío")
            except Exception as e:  # noqa: BLE001
                note(f"transcripción {vid} {name}: {type(e).__name__}: {str(e)[:160]}")
        else:
            note(f"transcripción FALLO {vid}: ningún método funcionó")


# ---------------- videos: bajar y analizar cuadro por cuadro ----------------
def run(cmd, timeout=900):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def bajar_video(vid, dest):
    for name, extra in (("directo", []),):
        p = run(["yt-dlp", "-f", "bv*[height<=480]+ba/b[height<=480]/b", "--merge-output-format", "mp4",
                 "-o", str(dest), *extra, f"https://www.youtube.com/watch?v={vid}"])
        if dest.exists():
            note(f"video OK {vid} vía {name}")
            return True
        note(f"video {vid} vía {name}: {(p.stderr.strip().splitlines() or ['?'])[-1][:160]}")
    return False


def analizar(vid, mp4, out):
    """Cortes de escena, ritmo, volumen, y hojas de cuadros (gancho cada 2 s + video entero cada 15 s)."""
    dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)]).stdout.strip() or 0)
    sc = run(["ffmpeg", "-i", str(mp4), "-vf", "select='gt(scene,0.3)',showinfo", "-an", "-f", "null", "-"]).stderr
    cuts = [float(x) for x in re.findall(r"pts_time:([\d.]+)", sc)]
    loud = run(["ffmpeg", "-i", str(mp4), "-af", "ebur128", "-vn", "-f", "null", "-"]).stderr
    lufs = re.findall(r"I:\s+(-?[\d.]+) LUFS", loud)
    sil = run(["ffmpeg", "-i", str(mp4), "-af", "silencedetect=n=-35dB:d=0.4", "-vn", "-f", "null", "-"]).stderr
    silences = len(re.findall(r"silence_end", sil))
    tramos = {}
    for a, b in ((0, 30), (30, 60), (60, 180), (180, 600), (600, 10**6)):
        if dur > a:
            n_ = sum(1 for c in cuts if a <= c < b)
            tramos[f"{a}-{min(b, int(dur))}s"] = round(n_ / ((min(b, dur) - a) / 60), 1)
    info = {"video_id": vid, "duracion_s": round(dur), "cortes_total": len(cuts),
            "cortes_por_minuto": round(len(cuts) / (dur / 60), 1) if dur else None,
            "duracion_media_plano_s": round(dur / (len(cuts) + 1), 1) if dur else None,
            "cortes_por_minuto_por_tramo": tramos, "lufs_integrado": float(lufs[-1]) if lufs else None,
            "pausas_de_silencio_>0.4s": silences, "tiempos_de_corte_primeros_60s": [round(c, 1) for c in cuts if c < 60]}
    (out / f"{vid}.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    font = ImageFont.load_default(size=18)
    for nombre, paso, hasta, cols in (("gancho", 2, 60, 6), ("completo", 15, dur, 8)):
        with tempfile.TemporaryDirectory() as d:
            run(["ffmpeg", "-i", str(mp4), "-t", str(hasta), "-vf", f"fps=1/{paso},scale=320:-2", f"{d}/f%04d.jpg"])
            fr = sorted(Path(d).glob("*.jpg"))[:96]
            if not fr:
                continue
            w, h = Image.open(fr[0]).size
            rows = (len(fr) + cols - 1) // cols
            sheet = Image.new("RGB", (cols * w, rows * (h + 22)), "white")
            dr = ImageDraw.Draw(sheet)
            for k, f in enumerate(fr):
                x, y = (k % cols) * w, (k // cols) * (h + 22)
                sheet.paste(Image.open(f), (x, y + 22))
                t = k * paso
                dr.text((x + 4, y + 2), f"{t // 60}:{t % 60:02d}", fill="black", font=font)
            sheet.save(out / f"{vid}_{nombre}.jpg", quality=75)
    note(f"análisis OK {vid}: {info['cortes_por_minuto']} cortes/min, {info['lufs_integrado']} LUFS")


def videos():
    lst = ROOT / "videos_analizar.txt"
    if not lst.exists():
        return
    out = ROOT / "analisis_video"
    out.mkdir(exist_ok=True)
    for line in lst.read_text().splitlines():
        vid = line.split("#")[0].strip()
        if not vid or (out / f"{vid}.json").exists():
            continue
        with tempfile.TemporaryDirectory() as d:
            mp4 = Path(d) / f"{vid}.mp4"
            if bajar_video(vid, mp4):
                try:
                    analizar(vid, mp4, out)
                except Exception as e:  # noqa: BLE001
                    note(f"análisis {vid} falló: {e}")


if __name__ == "__main__":
    what = sys.argv[1:] or ["miniaturas", "transcripciones", "videos"]
    if "miniaturas" in what:
        miniaturas()
    if "transcripciones" in what:
        transcripciones()
    if "videos" in what:
        videos()
    (ROOT / "media_referencia.log").write_text("\n".join(log), encoding="utf-8")
