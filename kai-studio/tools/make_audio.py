#!/usr/bin/env python3
"""
Genera la voz (Edge-TTS) de un episodio, un mp3 por línea + timing.json con los tiempos de cada palabra.

Uso:
  python tools/make_audio.py love-bombing en
  python tools/make_audio.py love-bombing es --voice es-MX-DaliaNeural
  python tools/make_audio.py love-bombing en --only 1        # solo la línea 1 (para probar voces)
  python tools/make_audio.py love-bombing en --estimate      # sin internet: tiempos estimados (solo para probar el video)

Requiere: pip install edge-tts   y   ffprobe (viene con ffmpeg).
Salida:   public/episodes/<slug>/<lang>/{script.json,timing.json,audio/line-NN.mp3}
"""
import argparse, asyncio, json, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return float(out)


def spread_words(text: str, duration: float):
    """Fallback: reparte las palabras en el tiempo según su largo (sin WordBoundary)."""
    words = text.split()
    weights = [max(2, len(re.sub(r"\W", "", w))) + (4 if re.search(r"[.,;:!?]$", w) else 0) for w in words]
    total = sum(weights) or 1
    t = 0.0
    res = []
    for w, wt in zip(words, weights):
        d = duration * wt / total
        res.append({"text": w, "start": round(t, 3), "end": round(t + d * 0.92, 3)})
        t += d
    return res


def estimate_line(text: str):
    words = text.split()
    dur = 0.0
    for w in words:
        dur += 0.15 + 0.045 * len(re.sub(r"\W", "", w))
        if re.search(r"[.,;:!?]$", w):
            dur += 0.22
    dur = max(dur, 0.8)
    return dur, spread_words(text, dur)


async def synth_line(text: str, voice: str, rate: str, out: Path):
    import edge_tts  # noqa
    try:
        comm = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    except TypeError:  # versiones viejas
        comm = edge_tts.Communicate(text, voice, rate=rate)
    words = []
    with open(out, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / 1e7
                words.append({"text": chunk["text"], "start": round(start, 3),
                              "end": round(start + chunk["duration"] / 1e7, 3)})
    return words


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("lang", choices=["en", "es"])
    ap.add_argument("--voice")
    ap.add_argument("--rate")
    ap.add_argument("--only", type=int, help="solo esta línea (id)")
    ap.add_argument("--estimate", action="store_true", help="no usa internet; tiempos estimados")
    a = ap.parse_args()

    src = ROOT / "episodes" / a.slug / a.lang / "script.json"
    script = json.loads(src.read_text(encoding="utf-8"))
    voice = a.voice or script["voice"]
    rate = a.rate or script.get("rate", "+0%")

    out_dir = ROOT / "public" / "episodes" / a.slug / a.lang
    (out_dir / "audio").mkdir(parents=True, exist_ok=True)
    shutil.copy(src, out_dir / "script.json")

    timing_path = out_dir / "timing.json"
    timing = {"lines": []}
    if a.only and timing_path.exists():
        timing = json.loads(timing_path.read_text(encoding="utf-8"))
    by_id = {l["id"]: l for l in timing["lines"]}

    for line in script["lines"]:
        if a.only and line["id"] != a.only:
            continue
        fname = f"line-{line['id']:02d}.mp3"
        mp3 = out_dir / "audio" / fname
        if a.estimate:
            dur, words = estimate_line(line["text"])
        else:
            words = asyncio.run(synth_line(line["text"], voice, rate, mp3))
            dur = probe_duration(mp3)
            if not words:
                words = spread_words(line["text"], dur)
        by_id[line["id"]] = {"id": line["id"], "file": fname, "duration": round(dur, 3), "words": words}
        print(f"line {line['id']:02d}  {dur:5.2f}s  {line['text'][:60]}")

    timing["lines"] = [by_id[i] for i in sorted(by_id)]
    timing["voice"] = voice
    timing["estimated"] = bool(a.estimate)
    timing_path.write_text(json.dumps(timing, ensure_ascii=False, indent=1), encoding="utf-8")
    total = sum(l["duration"] for l in timing["lines"])
    print(f"\nlistas {len(timing['lines'])} líneas · voz {total:.1f}s · voz usada: {voice}")
    if a.estimate:
        print("OJO: tiempos ESTIMADOS (sin audio). Corré de nuevo sin --estimate para la voz real.")


if __name__ == "__main__":
    sys.exit(main())
