// Formato de content/<pack>/shots.json (104 tomas) y timeline.json (lo
// arma scripts/pack_timeline.py a partir del audio real + shots.json).

export type Sfx = { name: string; offset_s: number };
export type Thread = { count: number; state: "tension" | "snap" };

export type PlateKind = "title" | "note" | "chapter" | "concept" | "cta" | "list" | "question" | "end";
export type PlateData = {
  kind: PlateKind;
  lines: string[];
  sub?: string;
  accent: "red" | "blue" | "amber";
  n?: number;
  reveal_from?: number;
};

export type Overlay = { kind: "pullquote"; text: string; hide_captions_during: boolean };

export type Shot = {
  id: string;
  n: number;
  chapter: string;
  chapter_name: string;
  type: "ai" | "clip" | "plate";
  narration: string;
  words: number;
  est_start_s: number;
  est_dur_s: number;
  transition_in: "cut" | "flash" | "dip" | "glitch";
  grade: string;
  captions: boolean;
  rehook: boolean;
  thread: Thread;
  motion: string;
  ai?: { file: string; palette: string; scene: string; prompt: string; test_batch?: boolean };
  clip?: { id: string; file: string };
  plate?: PlateData;
  overlay?: Overlay;
  sfx: Sfx[];
};

export type ShotsFile = { video: string; wps_assumed: number; total_est_s: number; shots: Shot[] };

// Palabra cronometrada real (edge-tts), tiempo ABSOLUTO en segundos sobre
// audio/voice.wav completo.
export type PalabraAbs = { texto: string; inicio: number; fin: number };

export type ShotTiempo = {
  id: string;
  startS: number;
  endS: number;
  startFrame: number;
  endFrame: number; // exclusivo
  palabras: PalabraAbs[]; // las palabras de este shot (subset de voice, tiempo absoluto)
  dividida?: boolean; // true si esta entrada es una mitad de un shot que se dividió (N2 del PACK)
  transitionOverride?: Shot["transition_in"]; // la 2da mitad de una división fuerza "flash"
};

export type Timeline = {
  fps: number;
  audio: string; // ruta relativa a public/, ej. "content/<pack>/audio/voice.wav"
  duracionTotal: number;
  tomas: ShotTiempo[];
  tomaMasLarga: { id: string; duracion: number };
  tomasDivididas: string[];
};
