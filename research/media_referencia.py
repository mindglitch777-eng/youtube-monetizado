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


def m_transcript_api(vid, lang):
    from youtube_transcript_api import YouTubeTranscriptApi
    t = YouTubeTranscriptApi().fetch(vid, languages=[lang, "en", "es", "pt"])
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


if __name__ == "__main__":
    what = sys.argv[1:] or ["miniaturas", "transcripciones"]
    if "miniaturas" in what:
        miniaturas()
    if "transcripciones" in what:
        transcripciones()
    (ROOT / "media_referencia.log").write_text("\n".join(log), encoding="utf-8")
