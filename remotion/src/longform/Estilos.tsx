// Grados de color por toma (sección 5 del PACK, "Global"), acentos de las
// placas, y el grano SVG global (feTurbulence — NUNCA un video de grano,
// pesaría ~20MB).
import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";

const GRADOS: Record<string, { filter: string; overlayColor: string }> = {
  "cold-neon": { filter: "contrast(1.10)", overlayColor: "rgba(20,60,255,0.05)" },
  "amber-warm": { filter: "contrast(1.06) saturate(1.12) sepia(0.12)", overlayColor: "rgba(255,170,60,0.07)" },
  "cool-blue": { filter: "contrast(1.10) saturate(0.92)", overlayColor: "rgba(40,110,255,0.07)" },
  "desat-cold": { filter: "saturate(0.65) contrast(1.15)", overlayColor: "rgba(60,90,140,0.06)" },
  "red-tint": { filter: "contrast(1.10)", overlayColor: "rgba(255,30,60,0.08)" },
  "warm-hope": { filter: "brightness(1.03) saturate(1.10)", overlayColor: "rgba(255,190,90,0.08)" },
};

export const ACENTOS: Record<string, string> = {
  red: "#ff2d55",
  blue: "#2d9bff",
  amber: "#ffb020",
};

// Envuelve cualquier toma (imagen/clip) con su grado de color + viñeta.
export const ConGrado: React.FC<{ grade: string; children: React.ReactNode }> = ({ grade, children }) => {
  const estilo = GRADOS[grade] ?? GRADOS["cool-blue"];
  return (
    <AbsoluteFill style={{ filter: estilo.filter }}>
      {children}
      <AbsoluteFill style={{ background: estilo.overlayColor }} />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.55) 100%)" }} />
    </AbsoluteFill>
  );
};

// Grano SVG (feTurbulence), ~10% de opacidad, mix-blend overlay. El seed
// cambia cada 2 frames para que no sea un patrón fijo pegado a la pantalla.
export const Grano: React.FC = () => {
  const frame = useCurrentFrame();
  const seed = Math.floor(frame / 2) % 24;
  return (
    <AbsoluteFill style={{ mixBlendMode: "overlay", opacity: 0.1, pointerEvents: "none" }}>
      <svg width="100%" height="100%">
        <filter id="grano">
          <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves={2} seed={seed} stitchTiles="stitch" />
          <feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.5 0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#grano)" />
      </svg>
    </AbsoluteFill>
  );
};
