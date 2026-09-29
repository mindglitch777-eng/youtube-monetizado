// Formato de content-kai/<video>/shots.json (guion + imágenes) y
// timeline.json (lo arma scripts/kai_timeline.py a partir del audio real).
// Ver RULES.md, sección "FÓRMULA DE RETENCIÓN — línea Kai / formato simple".

export type PuntoKai = {
  n: number; // cuenta SIEMPRE regresiva: 5,4,3,2,1
  titulo: string; // etiqueta corta del punto (para el contador/placas, no se lee)
  imagen: string; // ruta bajo public/, una sola imagen por punto (provista a mano)
  elementoRecurrente?: boolean; // este punto muestra el elemento visual sin resolver
};

export type ShotsKai = {
  titulo: string;
  identidad: string; // a quién le pasó esto (pareja/amigo/familia — amplio, regla 2)
  puntoMasFuerte: number; // n del punto más fuerte, para el gancho de retención a mitad del hook
  puntos: PuntoKai[]; // siempre 5, en orden 5→1
  elementoRecurrente?: { descripcion: string; imagen: string };
  fraseTriple: string; // frase repetida 3 veces en el punto de mayor impacto (regla 6)
  puntoFraseTriple: number; // n del punto donde va la frase triple
  cta: string; // una sola palabra (regla 11)
};

// Palabra cronometrada real (edge-tts), tiempo ABSOLUTO en segundos sobre
// audio/voice.mp3 completo — mismo esquema que remotion/src/longform/tipos.ts.
export type PalabraAbs = { texto: string; inicio: number; fin: number };

export type TomaKai = {
  id: string; // "HOOK" | "P5".."P1" | "CTA"
  startS: number;
  endS: number;
  startFrame: number;
  endFrame: number; // exclusivo
  palabras: PalabraAbs[];
};

export type TimelineKai = {
  fps: number;
  audio: string;
  duracionTotal: number;
  tomas: TomaKai[];
};
