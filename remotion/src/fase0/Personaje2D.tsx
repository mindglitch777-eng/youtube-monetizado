import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

// PRUEBA DE CONCEPTO — Fase 0, rama 2D (CSS/SVG puro, sin WebGL).
// Mismo personaje-silueta y misma pose objetivo que Personaje3D.tsx, pero la
// "luz" y el "volumen" se simulan con gradientes y un drop-shadow proyectado,
// no con geometría e iluminación real. Sirve para comparar tiempo de render
// y diferencia visual contra la rama 3D real.

const COLOR_CUERPO_CLARO = "#B08D63";
const COLOR_CUERPO_OSCURO = "#5E4830";
const COLOR_PISO = "#241A12";
const COLOR_FONDO = "#100C08";

export const Personaje2D: React.FC<{ cambioEnFrame: number }> = ({ cambioEnFrame }) => {
  const frame = useCurrentFrame();
  const { fps, width, height, durationInFrames } = useVideoConfig();

  const t = spring({ frame: frame - cambioEnFrame, fps, config: { damping: 11, stiffness: 90, mass: 1.1 } });

  // Misma cámara que la rama 3D: nunca estática, paneo + acercamiento continuo,
  // simulado acá con transform en el contenedor del personaje.
  const avance = frame / (durationInFrames || 1);
  const panX = interpolate(avance, [0, 1], [-24, 24]);
  const escala = interpolate(avance, [0, 1], [1, 1.12]);

  const anguloHombro = interpolate(t, [0, 1], [8, -95]); // grados, brazo pegado -> extendido
  const anguloCodo = interpolate(t, [0, 1], [10, -8]);
  const inclinacionTorso = interpolate(t, [0, 1], [0, -7]);

  const cx = width / 2;
  const cy = height / 2;

  return (
    <AbsoluteFill style={{ backgroundColor: COLOR_FONDO }}>
      <svg width={width} height={height} style={{ position: "absolute", inset: 0 }}>
        <defs>
          {/* Gradiente diagonal simulando luz direccional desde arriba-derecha,
              igual que la directionalLight de la rama 3D. */}
          <linearGradient id="luzCuerpo" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={COLOR_CUERPO_CLARO} />
            <stop offset="100%" stopColor={COLOR_CUERPO_OSCURO} />
          </linearGradient>
          <radialGradient id="sombraPiso" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#000000" stopOpacity="0.55" />
            <stop offset="100%" stopColor="#000000" stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* Piso, sombra proyectada dibujada a mano (óvalo con blur), no calculada. */}
        <ellipse cx={cx} cy={cy + 245} rx={150} ry={34} fill="url(#sombraPiso)" />
        <rect x={0} y={cy + 250} width={width} height={height - (cy + 250)} fill={COLOR_PISO} opacity={0.5} />

        <g transform={`translate(${cx + panX}, ${cy}) scale(${escala}) rotate(${inclinacionTorso})`}>
          {/* Brazo izquierdo: quieto */}
          <rect x={-92} y={-30} width={30} height={150} rx={15} fill="url(#luzCuerpo)" transform="rotate(7 -77 -30)" />

          {/* Torso */}
          <rect x={-60} y={-90} width={120} height={210} rx={60} fill="url(#luzCuerpo)" />
          {/* Cabeza, sin rasgos (RULES.md) */}
          <circle cx={0} cy={-150} r={58} fill="url(#luzCuerpo)" />

          {/* Brazo derecho: el que anima la pose (hombro + codo articulados) */}
          <g transform={`translate(85, -30) rotate(${anguloHombro})`}>
            <rect x={-15} y={0} width={30} height={130} rx={15} fill="url(#luzCuerpo)" />
            <g transform={`translate(0, 130) rotate(${anguloCodo})`}>
              <rect x={-13} y={0} width={26} height={105} rx={13} fill="url(#luzCuerpo)" />
            </g>
          </g>
        </g>
      </svg>
    </AbsoluteFill>
  );
};
