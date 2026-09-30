export type EffectKind = "zoomIn" | "zoomOut" | "panLeft" | "panRight" | "zoomToPoint";

export type Effect = {
  kind: EffectKind;
  /** normalized focus point (0-1) for zoomToPoint */
  focus?: [number, number];
  scaleTo?: number;
};

export type ScriptImage = {
  n: number;
  effect?: Effect;
  /** sfx names played at the start of this image, e.g. ["notification"] */
  sfx?: string[];
};

export type Overlay = {
  text: string;
  x: number; // 0-1
  y: number; // 0-1
  style: "title" | "label";
  /** only show while the first image of the line is on screen */
  onlyFirstImage?: boolean;
};

export type ScriptLine = {
  id: number;
  text: string;
  images: ScriptImage[];
  hook?: boolean;
  /** "5".."1" shows that number, "off" hides the counter; omitted = keep previous state */
  counter?: string;
  /** extra silence (s) before this line's voice starts. No music/sfx in that gap if final. */
  silenceBefore?: number;
  overlays?: Overlay[];
  /** riser before the zoom-cut of this line (line 4) */
  riser?: boolean;
  /** last line: music cut, no sfx */
  final?: boolean;
};

export type Script = {
  slug: string;
  lang: "en" | "es";
  part: number;
  voice: string;
  rate: string;
  imagePrefix: string;
  imageCount: number;
  lines: ScriptLine[];
};

export type WordTiming = { text: string; start: number; end: number };
export type LineTiming = { id: number; file: string; duration: number; words: WordTiming[] };
export type Timing = { lines: LineTiming[] };

export type SfxManifest = { files: string[] };

// ---------- computed timeline ----------
export type TImage = { n: number; from: number; dur: number; effect?: Effect; lineId: number; index: number };
export type TVoice = { src: string; from: number; dur: number; lineId: number };
export type TChunk = { words: { text: string; from: number; to: number }[]; from: number; to: number };
export type TSfx = { name: string; from: number };
export type TOverlay = Overlay & { from: number; dur: number };

export type Timeline = {
  fps: number;
  totalFrames: number;
  images: TImage[];
  voices: TVoice[];
  chunks: TChunk[];
  counter: { from: number; value: string }[];
  overlays: TOverlay[];
  sfx: TSfx[];
  voiceWindows: { from: number; to: number }[];
  finalCutFrame: number | null;
  warnings: string[];
};

export type KaiProps = {
  slug: string;
  lang: "en" | "es";
  timeline?: Timeline;
  script?: Script;
};
