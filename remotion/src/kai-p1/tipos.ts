// Formato de content-kai/parte1-love-bombing/out/timeline.json, armado por
// scripts/kai_p1_timeline.py a partir de script.json + audio/voz.json real.
// Ver las instrucciones .md del video (instrucciones-claude-code-kai-parte1.md).

export type PalabraAbs = { texto: string; inicio: number; fin: number };

export type ImagenEnLinea = {
  archivo: string;
  duracionS: number;
  movimiento: "zoom" | "pan";
};

export type LineaTimeline = {
  n: number;
  texto: string;
  flags: string[];
  startS: number;
  endS: number;
  startFrame: number;
  endFrame: number;
  duracionAudioFrames: number;
  pausaFrames: number;
  imagenes: ImagenEnLinea[];
  palabras: PalabraAbs[]; // tiempo LOCAL a la línea (offset 0 al arrancar el audio de la línea)
  contadorVisible: boolean;
  contadorValor: number | null;
  esGridIntro: boolean;
  triggerTodayS: number | null;
};

export type SfxEvento = {
  tipo: "whoosh" | "impacto" | "latido" | "riser" | "notificacion";
  frame: number;
  hasta?: number;
};

export type TimelineKaiP1 = {
  fps: number;
  ancho: number;
  alto: number;
  audio: string;
  duracionTotal: number;
  lineas: LineaTimeline[];
  sfxEventos: SfxEvento[];
  pausasSinVoz: Array<[number, number]>;
};
