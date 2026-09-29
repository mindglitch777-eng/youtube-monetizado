import React from "react";
import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from "remotion";
import type { PalabraAbs } from "./tipos";

const MAX_PALABRAS = 5;

type Franja = { palabras: PalabraAbs[]; desde: number; hasta: number };

// Igual criterio que remotion/src/longform/Captions.tsx pero SIEMPRE
// activo (regla 8: subtítulo palabra por palabra el 100% del tiempo, sin
// excepción — a diferencia de Knotwise, acá no hay placas ni citas que lo
// tapen). Recibe palabras en tiempo LOCAL a la toma (ya relativas a su
// propio startS) porque este componente vive DENTRO del <Sequence> de la
// toma — evita el bug de tiempo absoluto/relativo que tuvo LongForm.
function armarFranjas(palabras: PalabraAbs[], finToma: number): Franja[] {
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
    franja.hasta = siguiente ? siguiente.palabras[0].inicio : Math.min(franja.palabras[franja.palabras.length - 1].fin + 0.5, finToma);
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

  const entrada = spring({ frame: frame - Math.round(franja.desde * fps), fps, config: { damping: 200 }, durationInFrames: 3 });

  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-end", paddingBottom: Math.max(140, height * 0.16) }}>
      <div
        style={{
          fontFamily: "Inter, sans-serif", fontWeight: 800, fontSize: 58, color: "#FFFFFF", textAlign: "center",
          maxWidth: "86%", lineHeight: 1.2, textShadow: "0 3px 14px rgba(0,0,0,0.9)", opacity: entrada,
        }}
      >
        {franja.palabras.map((p, i) => (
          <span key={i} style={{ margin: "0 0.16em" }}>{p.texto}</span>
        ))}
      </div>
    </AbsoluteFill>
  );
};
