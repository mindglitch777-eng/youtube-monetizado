// Formato de content/<short>/timeline.json que genera
// scripts/generar_voz_standalone.py (shorts "standalone-animado": sin
// imágenes IA). Distinto del Timeline de ../tipos.ts (ese es del pipeline
// de imágenes/Ken Burns).

export type PalabraLinea = { texto: string; inicio: number; fin: number };

export type LineaTimeline = {
  n: number;
  texto: string;
  inicio: number; // segundos, absoluto sobre toda la narración
  duracion: number;
  palabras: PalabraLinea[]; // inicio/fin relativos al inicio de la línea
  destacada: number | null; // índice en `palabras`
};

export type TimelineStandalone = {
  video: string;
  voz: string;
  formato: "standalone-animado";
  audio: string;
  duracionNarracion: number;
  duracionTotal: number;
  segmentos: LineaTimeline[];
};
