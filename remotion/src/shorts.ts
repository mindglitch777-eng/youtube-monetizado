import type { Timeline } from "./tipos";

// RULES.md, sección Shorts: 1 por bloque, menos de 60 s, vertical 9:16, con las
// mismas imágenes, subtítulos, sonidos e ícono del video largo.
export const MAX_SEGUNDOS = 60;
const COLA = 1.5; // segundos después del Pago para que suene el sting
const STING = "assets/sonido/cierre.mp3";

// Recorta el timeline completo a los segmentos de un bloque, con los tiempos
// empezando en 0. El CTA queda afuera: pertenece solo al video largo.
export function recortarBloque(timeline: Timeline, bloque: number): Timeline {
  const segmentos = timeline.segmentos.filter((s) => s.bloque === bloque && s.tipo !== "cta");
  if (!segmentos.length) throw new Error(`El timeline no tiene un bloque ${bloque}.`);
  const desde = segmentos[0].inicio;
  const recortados = segmentos.map((s) => ({
    ...s,
    inicio: s.inicio - desde,
    // El whoosh de entrada al bloque suena antes del segundo 0: en el short no va.
    sonidos: s.sonidos.filter((sonido) => s.inicio - desde + sonido.en >= 0),
  }));
  const ultimo = recortados[recortados.length - 1];
  const fin = ultimo.inicio + ultimo.duracion;
  ultimo.sonidos = [...ultimo.sonidos, { archivo: STING, en: ultimo.duracion }];
  const duracionTotal = fin + COLA;
  if (duracionTotal >= MAX_SEGUNDOS) {
    throw new Error(
      `El short del bloque ${bloque} dura ${duracionTotal.toFixed(1)} s; ` +
        `RULES.md pide menos de ${MAX_SEGUNDOS} s. Hay que acortar el texto de ese bloque.`,
    );
  }
  return { ...timeline, duracionTotal, segmentos: recortados };
}
