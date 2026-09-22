import { loadFont } from "@remotion/fonts";
import React from "react";
import { spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import type { Palabra } from "./tipos";

// RULES.md, sección Subtítulos.
const MAX_PALABRAS = 5;
const AMARILLO = "#FFD83D";

// Montserrat (licencia OFL) guardada en remotion/fuentes/: el render no depende de internet.
const fontFamily = "Montserrat";
loadFont({ family: fontFamily, url: staticFile("fuentes/Montserrat.woff2"), weight: "900" });

type Franja = { palabras: { palabra: Palabra; indice: number }[]; desde: number; hasta: number };

// Corta la narración en franjas cortas: máximo 5 palabras, y corta antes
// si termina una frase (o en una coma, si la franja ya tiene 3 palabras).
export function armarFranjas(palabras: Palabra[], finSegmento: number): Franja[] {
  const franjas: Franja[] = [];
  let actual: Franja["palabras"] = [];
  palabras.forEach((palabra, indice) => {
    actual.push({ palabra, indice });
    const fin = /[.!?]["”']?$/.test(palabra.texto);
    const coma = /[,;:—]["”']?$/.test(palabra.texto) && actual.length >= 3;
    if (actual.length >= MAX_PALABRAS || fin || coma) {
      franjas.push({ palabras: actual, desde: 0, hasta: 0 });
      actual = [];
    }
  });
  if (actual.length) franjas.push({ palabras: actual, desde: 0, hasta: 0 });

  franjas.forEach((franja, n) => {
    franja.desde = franja.palabras[0].palabra.inicio;
    const ultima = franja.palabras[franja.palabras.length - 1].palabra;
    const siguiente = franjas[n + 1];
    franja.hasta = siguiente ? siguiente.palabras[0].palabra.inicio : Math.min(ultima.fin + 0.5, finSegmento);
  });
  return franjas;
}

export const Subtitulos: React.FC<{ palabras: Palabra[]; destacada: number | null; duracion: number }> = ({
  palabras,
  destacada,
  duracion,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const vertical = height > width; // shorts 9:16
  const t = frame / fps;
  const franja = armarFranjas(palabras, duracion).find((f) => t >= f.desde && t < f.hasta);
  if (!franja) return null;

  const entrada = spring({ frame: frame - Math.round(franja.desde * fps), fps, config: { damping: 200 }, durationInFrames: 6 });

  return (
    <div
      style={{
        position: "absolute",
        top: "30%",
        left: vertical ? 60 : 120,
        right: vertical ? 60 : 120,
        textAlign: "center",
        fontFamily,
        fontWeight: 900,
        fontSize: vertical ? 76 : 84,
        lineHeight: 1.15,
        color: "white",
        WebkitTextStroke: "12px rgba(20, 14, 10, 0.95)",
        paintOrder: "stroke fill",
        textShadow: "0 8px 24px rgba(0, 0, 0, 0.55)",
        transform: `scale(${0.94 + 0.06 * entrada})`,
      }}
    >
      {franja.palabras.map(({ palabra, indice }) => {
        const esDestacada = indice === destacada && t >= palabra.inicio;
        const salto = esDestacada
          ? spring({ frame: frame - Math.round(palabra.inicio * fps), fps, config: { damping: 9, stiffness: 180 } })
          : 0;
        return (
          <span
            key={indice}
            style={{
              display: "inline-block",
              margin: "0 0.14em",
              color: esDestacada ? AMARILLO : "white",
              // Crece con el tamaño de letra (no con scale) para no pisar a las vecinas.
              fontSize: `${1 + 0.18 * salto}em`,
            }}
          >
            {palabra.texto}
          </span>
        );
      })}
    </div>
  );
};
