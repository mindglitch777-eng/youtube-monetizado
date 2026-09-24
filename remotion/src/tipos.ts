// Formato de content/<video>/timeline.json (lo generan scripts/generar_audio.py
// para videos largos y scripts/generar_short.py para shorts standalone).

export type Palabra = { texto: string; inicio: number; fin: number };

export type Sonido = { archivo: string; en: number; volumen?: number };

export type Segmento = {
  id: string;
  tipo: string;
  bloque: number | null;
  inicio: number;
  duracion: number;
  // Audio propio del segmento (video largo). En un short standalone es null y
  // la narración completa está en Timeline.audio.
  audio: string | null;
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
  // "short" = short standalone (generar_short.py): se usa entero, sin recortar.
  formato?: "largo" | "short";
  audio?: string | null;
  // Música de fondo (la agrega scripts/preparar.mjs si existe assets/musica/fondo.mp3).
  musica?: string | null;
};

export type Props = { timeline: Timeline | null };

// Short vertical: un bloque del video largo (1 a 6), o un short standalone entero.
export type PropsShort = Props & { bloque: number };
