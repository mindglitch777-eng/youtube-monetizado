import React from "react";
import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from "remotion";
import type { PalabraAbs } from "./tipos";

const MAX_PALABRAS = 7;

type Franja = { palabras: PalabraAbs[]; desde: number; hasta: number };

// Corta en franjas cortas (máx. 7 palabras): primero en pausas naturales
// (fin de frase, coma con al menos 3 palabras ya acumuladas), después
// pareja si un tramo pasa de 7. Igual criterio que ../Subtitulos.tsx
// (armarFranjas) pero con el máximo de palabras que pide este PACK.
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

// Subtítulos abajo al centro (N9: nunca la misma oración completa que una
// placa/cita al mismo tiempo — por eso este componente no se monta cuando
// el shot tiene captions:false o un overlay con hide_captions_during).
//
// `palabras` y `finTomaS` vienen en tiempo ABSOLUTO de la composición
// (igual que timeline.json) — Captions no vive dentro de un Sequence (está
// arriba de todas las tomas, en LongForm.tsx), así que useCurrentFrame()
// acá SIEMPRE es el frame absoluto. Antes se le pasaban palabras
// convertidas a tiempo relativo a cada toma, que solo por coincidencia
// coincidía con el frame absoluto en la primera toma (arranca en 0) — en
// cualquier otra toma la franja activa nunca se encontraba y no se veía
// ningún subtítulo salvo en el primer shot del video.
export const Captions: React.FC<{ palabras: PalabraAbs[]; finTomaS: number }> = ({ palabras, finTomaS }) => {
  const frame = useCurrentFrame();
  const { fps, height } = useVideoConfig();
  const t = frame / fps;
  const franjas = React.useMemo(() => armarFranjas(palabras, finTomaS), [palabras, finTomaS]);
  const franja = franjas.find((f) => t >= f.desde && t < f.hasta);
  if (!franja) return null;

  const entrada = spring({ frame: frame - Math.round(franja.desde * fps), fps, config: { damping: 200 }, durationInFrames: 3 });

  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-end", paddingBottom: Math.max(60, height * 0.09) }}>
      <div
        style={{
          fontFamily: "Inter, sans-serif", fontWeight: 700, fontSize: 46, color: "#FFFFFF", textAlign: "center",
          maxWidth: "78%", lineHeight: 1.25, textShadow: "0 3px 12px rgba(0,0,0,0.85)", opacity: entrada,
        }}
      >
        {franja.palabras.map((p, i) => (
          <span key={i} style={{ margin: "0 0.14em" }}>{p.texto}</span>
        ))}
      </div>
    </AbsoluteFill>
  );
};
