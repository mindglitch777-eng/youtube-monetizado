import React, { useMemo } from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { armarFranjas } from "../Subtitulos";
import type { LineaTimeline } from "./tipos";

const AMARILLO = "#FFD83D";

// Capa base permanente: subtítulos palabra por palabra abajo de pantalla,
// blanco con la palabra clave en amarillo, activa el 100% del tiempo sin
// excepción — incluso sobre clips reales e íconos (por eso se monta encima
// de todo en ManipulacionParte1.tsx, con su propio fondo/sombra para seguir
// siendo legible sobre cualquier fondo).
export const CapaSubtitulos: React.FC<{ lineas: LineaTimeline[] }> = ({ lineas }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  // Todas las palabras de la narración completa, en tiempo absoluto — así
  // armarFranjas corta en las mismas pausas naturales que el resto del
  // pipeline, sin reiniciar en cada línea.
  const { palabras, destacadas, finTotal } = useMemo(() => {
    const todas = lineas.flatMap((l) => l.palabras.map((p) => ({ texto: p.texto, inicio: l.inicio + p.inicio, fin: l.inicio + p.fin })));
    const marcadas = new Set(
      lineas
        .filter((l) => l.destacada !== null)
        .map((l) => {
          const p = l.palabras[l.destacada as number];
          return l.inicio + p.inicio;
        }),
    );
    return { palabras: todas, destacadas: marcadas, finTotal: lineas[lineas.length - 1]?.inicio + lineas[lineas.length - 1]?.duracion || 0 };
  }, [lineas]);

  const franja = useMemo(() => armarFranjas(palabras, finTotal).find((f) => t >= f.desde && t < f.hasta), [palabras, finTotal, t]);
  if (!franja) return null;

  const entrada = spring({ frame: frame - Math.round(franja.desde * fps), fps, config: { damping: 200 }, durationInFrames: 6 });

  return (
    <div
      style={{
        position: "absolute", bottom: "9%", left: 56, right: 56, textAlign: "center",
        fontFamily: "Montserrat, sans-serif", fontWeight: 900, fontSize: 72, lineHeight: 1.15,
        color: "white", WebkitTextStroke: "11px rgba(0,0,0,0.95)", paintOrder: "stroke fill",
        textShadow: "0 8px 24px rgba(0,0,0,0.6)", transform: `scale(${0.94 + 0.06 * entrada})`,
      }}
    >
      {franja.palabras.map(({ palabra, indice }) => {
        const esDestacada = destacadas.has(palabra.inicio) && t >= palabra.inicio;
        const salto = esDestacada
          ? spring({ frame: frame - Math.round(palabra.inicio * fps), fps, config: { damping: 9, stiffness: 180 } })
          : 0;
        return (
          <span
            key={indice}
            style={{ display: "inline-block", margin: "0 0.14em", color: esDestacada ? AMARILLO : "white", fontSize: `${1 + 0.18 * salto}em` }}
          >
            {palabra.texto}
          </span>
        );
      })}
    </div>
  );
};
