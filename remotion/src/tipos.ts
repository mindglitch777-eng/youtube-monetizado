// Formato de content/<video>/timeline.json (lo genera scripts/generar_audio.py).

export type Palabra = { texto: string; inicio: number; fin: number };

export type Sonido = { archivo: string; en: number };

export type Segmento = {
  id: string;
  tipo: string;
  bloque: number | null;
  inicio: number;
  duracion: number;
  audio: string;
  imagen: string | null;
  palabras: Palabra[];
  destacada: number | null;
  sonidos: Sonido[];
};

export type Timeline = {
  titulo: string;
  video: string;
  voz: string;
  icono: string;
  duracionTotal: number;
  segmentos: Segmento[];
};

export type Props = { timeline: Timeline | null };
