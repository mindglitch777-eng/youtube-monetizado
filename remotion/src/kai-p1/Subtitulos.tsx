import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import type { PalabraAbs } from "./tipos";

const MAX_PALABRAS = 5;
const COLOR_ACTIVA = "#E1A11B";

type Franja = { palabras: PalabraAbs[]; desde: number; hasta: number };

// Subtítulo palabra por palabra, activo el 100% del tiempo (regla del
// .md), blanco con borde negro y la palabra activa en mostaza. Recibe
// palabras en tiempo LOCAL a la línea porque vive dentro del <Sequence>
// de esa línea (mismo criterio que remotion/src/kai/Subtitulos.tsx).
function armarFranjas(palabras: PalabraAbs[], finLinea: number): Franja[] {
  const tramos: PalabraAbs[][] = [];
  let actual: PalabraAbs[] = [];
  palabras.forEach((p) => {
    actual.push(p);
    const pausa = /[.!?—:;]["")’]?$/.test(p.texto);
    const coma = /,["')’]?$/.test(p.texto) && actual.length >= 3;
    if (pausa || coma) {
      tramos.push(actual);
      actual = [];
    }
  });
  if (actual.length) tramos.push(actual);

  const franjas: Franja[] = [];
  for (const tramo of tramos) {
    const partes = Math.ceil(tramo.length / MAX_PALABRAS);
    const tamano = Math.ceil(tramo.length / partes);
    for (let k = 0; k < tramo.length; k += tamano) {
      franjas.push({ palabras: tramo.slice(k, k + tamano), desde: 0, hasta: 0 });
    }
  }
  franjas.forEach((franja, n) => {
    franja.desde = franja.palabras[0].inicio;
    const siguiente = franjas[n + 1];
    franja.hasta = siguiente ? siguiente.palabras[0].inicio : Math.min(franja.palabras[franja.palabras.length - 1].fin + 0.5, finLinea);
  });
  return franjas;
}

export const Subtitulos: React.FC<{ palabras: PalabraAbs[]; duracionSeg: number }> = ({ palabras, duracionSeg }) => {
  const frame = useCurrentFrame();
  const { fps, height } = useVideoConfig();
  const t = frame / fps;
  const franjas = React.useMemo(() => armarFranjas(palabras, duracionSeg), [palabras, duracionSeg]);
  const franja = franjas.find((f) => t >= f.desde && t < f.hasta) ?? franjas[franjas.length - 1];
  if (!franja) return null;

  // padding-top en % es relativo al ANCHO del contenedor, no al alto —
  // por eso se calcula el offset en px a partir de la altura real
  // (regla del .md: subtítulos ~65-70% de la altura).
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-start", paddingTop: height * 0.67 }}>
      <div style={{ maxWidth: "88%", textAlign: "center", lineHeight: 1.25 }}>
        {franja.palabras.map((p, i) => {
          const activa = t >= p.inicio && t < p.fin;
          return (
            <span
              key={i}
              style={{
                fontFamily: "Inter, sans-serif", fontWeight: 800, fontSize: 60,
                color: activa ? COLOR_ACTIVA : "#FFFFFF",
                WebkitTextStroke: "3px #000000", paintOrder: "stroke fill",
                margin: "0 0.16em", display: "inline-block",
              }}
            >
              {p.texto}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
