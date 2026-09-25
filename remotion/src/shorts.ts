import type { Timeline } from "./tipos";

// RULES.md, sección Shorts: 1 por bloque, hasta 180 s (límite real de YouTube
// Shorts desde oct. 2024), vertical 9:16, con las mismas imágenes, subtítulos,
// sonidos e ícono del video largo.
export const MAX_SEGUNDOS = 180;
const COLA = 1.5; // segundos después del Pago para que suene el sting
const STING = "assets/sonido/cierre.mp3";

// Arma el timeline de un short: un short standalone se usa entero; un video
// largo se recorta al bloque pedido. En los dos casos, debe durar menos de 180 s.
export function prepararShort(timeline: Timeline, bloque: number): Timeline {
  const short = timeline.formato === "short" ? timeline : recortarBloque(timeline, bloque);
  if (short.duracionTotal >= MAX_SEGUNDOS) {
    const que = timeline.formato === "short" ? "El short" : `El short del bloque ${bloque}`;
    throw new Error(
      `${que} dura ${short.duracionTotal.toFixed(1)} s; RULES.md pide menos de ` +
        `${MAX_SEGUNDOS} s. Hay que acortar el texto.`,
    );
  }
  return short;
}

// Recorta el timeline completo a los segmentos de un bloque, con los tiempos
// empezando en 0. El CTA queda afuera: pertenece solo al video largo.
function recortarBloque(timeline: Timeline, bloque: number): Timeline {
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
  return { ...timeline, duracionTotal: fin + COLA, segmentos: recortados };
}
