import type { Script, Timing, Timeline, TImage, TVoice, TChunk, TSfx, TOverlay, LineTiming } from "../types";

export const FPS = 30;
export const GAP_AFTER = 0.08; // s between lines
export const GAP_AFTER_HOOK = 0.15; // s of air after a hook line
export const MIN_IMAGE_SECONDS = 1.0; // warn below this
export const MAX_WORDS_PER_CHUNK = 3;

export const dbToGain = (db: number) => Math.pow(10, db / 20);

const cleanWord = (w: string) => w.replace(/[.,;:"“”«»¡¿()]/g, "").trim();
const endsPhrase = (w: string) => /[.,;:!?]["”»)]?$/.test(w);

export function buildTimeline(
  script: Script,
  timing: Timing,
  availableSfx: Set<string>,
  fps: number = FPS,
): Timeline {
  const warnings: string[] = [];
  const f = (sec: number) => Math.round(sec * fps);
  const lines = script.lines;

  const byId = new Map<number, LineTiming>();
  timing.lines.forEach((l) => byId.set(l.id, l));

  // 1) absolute voice start/end (seconds) for every line
  const voiceStart: number[] = [];
  const voiceEnd: number[] = [];
  let t = 0;
  lines.forEach((line, i) => {
    const lt = byId.get(line.id);
    if (!lt) throw new Error(`timing.json has no entry for line ${line.id}`);
    const before = line.silenceBefore ?? 0;
    const start = t + before;
    voiceStart.push(start);
    voiceEnd.push(start + lt.duration);
    const after = line.hook ? GAP_AFTER_HOOK : GAP_AFTER;
    t = start + lt.duration + (i === lines.length - 1 ? 0 : after);
  });
  const totalFrames = f(voiceEnd[voiceEnd.length - 1]);

  // 2) image segments: [voiceStart_i , voiceStart_{i+1}) — the gap of a line is held by its last image
  const images: TImage[] = [];
  const voices: TVoice[] = [];
  const chunks: TChunk[] = [];
  const counter: Timeline["counter"] = [{ from: 0, value: "off" }];
  const overlays: TOverlay[] = [];
  const sfx: TSfx[] = [];
  const voiceWindows: Timeline["voiceWindows"] = [];
  let finalCutFrame: number | null = null;

  const pushSfx = (name: string, from: number) => {
    if (availableSfx.has(name)) sfx.push({ name, from: Math.max(0, from) });
    else warnings.push(`sfx "${name}" not found in public/sfx (skipped at frame ${Math.max(0, from)})`);
  };

  lines.forEach((line, i) => {
    const lt = byId.get(line.id)!;
    const segStart = i === 0 ? 0 : voiceStart[i];
    const segEnd = i === lines.length - 1 ? voiceEnd[i] : voiceStart[i + 1];
    const n = line.images.length;
    const segFrames = f(segEnd) - f(segStart);
    const imgFrameStarts: number[] = [];
    line.images.forEach((im, k) => {
      const from = f(segStart + ((segEnd - segStart) * k) / n);
      const to = f(segStart + ((segEnd - segStart) * (k + 1)) / n);
      imgFrameStarts.push(from);
      if ((to - from) / fps < MIN_IMAGE_SECONDS) {
        warnings.push(`line ${line.id} image ${im.n}: only ${((to - from) / fps).toFixed(2)}s on screen (target >= ${MIN_IMAGE_SECONDS}s)`);
      }
      images.push({ n: im.n, from, dur: Math.max(1, to - from), effect: im.effect, lineId: line.id, index: images.length });
      (im.sfx ?? []).forEach((name) => pushSfx(name, from - 2));
    });
    void segFrames;

    // voice
    const vFrom = f(voiceStart[i]);
    const vDur = Math.max(1, f(voiceEnd[i]) - vFrom);
    voices.push({ src: `episodes/${script.slug}/${script.lang}/audio/${lt.file}`, from: vFrom, dur: vDur, lineId: line.id });
    voiceWindows.push({ from: vFrom, to: vFrom + vDur });

    // subtitles (word by word, grouped in chunks)
    let cur: TChunk["words"] = [];
    const flush = () => {
      if (!cur.length) return;
      chunks.push({ words: cur, from: cur[0].from, to: cur[cur.length - 1].to });
      cur = [];
    };
    lt.words.forEach((w) => {
      const text = cleanWord(w.text);
      if (!text) return;
      const from = f(voiceStart[i] + w.start);
      const to = Math.max(from + 3, f(voiceStart[i] + w.end));
      cur.push({ text, from, to });
      if (cur.length >= MAX_WORDS_PER_CHUNK || endsPhrase(w.text)) flush();
    });
    flush();

    // counter
    if (line.counter) counter.push({ from: vFrom, value: line.counter });

    // overlays
    (line.overlays ?? []).forEach((o) => {
      const first = images.find((im) => im.lineId === line.id)!;
      const from = first.from;
      const dur = o.onlyFirstImage ? first.dur : f(segEnd) - f(segStart);
      overlays.push({ ...o, from, dur });
    });

    // sfx rules
    if (!line.final) {
      const counterChange = !!line.counter && line.counter !== "off";
      if (line.hook) {
        pushSfx("thud", vFrom);
        pushSfx("whoosh", vFrom - 3);
      } else if (counterChange) {
        pushSfx("impact", vFrom - 2);
        pushSfx("whoosh", vFrom - 3);
      }
      if (line.hook && counterChange) pushSfx("impact", vFrom - 2);
      if (line.riser) {
        const zoomIdx = line.images.findIndex((im) => im.effect?.kind === "zoomToPoint");
        if (zoomIdx >= 0 && zoomIdx + 1 < line.images.length) {
          const cut = imgFrameStarts[zoomIdx + 1];
          pushSfx("riser", cut - Math.round(1.6 * fps));
          pushSfx("impact", cut - 2);
        }
      }
    } else {
      finalCutFrame = f(voiceStart[i] - (line.silenceBefore ?? 0));
    }
  });

  // remove duplicate sfx at the exact same frame+name
  const seen = new Set<string>();
  const uniq = sfx.filter((s) => {
    const k = `${s.name}@${s.from}`;
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });

  return { fps, totalFrames, images, voices, chunks, counter, overlays, sfx: uniq, voiceWindows, finalCutFrame, warnings };
}

/** music volume at a given absolute frame: base level, ducked while voice plays, cut before the final line. */
export function musicVolume(frame: number, tl: Timeline, baseDb = -22, duckDb = -6, rampFrames = 8): number {
  const base = dbToGain(baseDb);
  const duck = dbToGain(duckDb);
  let d = Infinity; // distance in frames to the nearest voice window (0 when inside)
  for (const w of tl.voiceWindows) {
    const dist = frame < w.from ? w.from - frame : frame > w.to ? frame - w.to : 0;
    if (dist < d) d = dist;
  }
  const duckFactor = d === 0 ? duck : duck + (1 - duck) * Math.min(1, d / rampFrames);
  let v = base * duckFactor;
  if (tl.finalCutFrame !== null) {
    const fadeLen = 12;
    if (frame >= tl.finalCutFrame) return 0;
    if (frame >= tl.finalCutFrame - fadeLen) v *= (tl.finalCutFrame - frame) / fadeLen;
  }
  return v;
}
