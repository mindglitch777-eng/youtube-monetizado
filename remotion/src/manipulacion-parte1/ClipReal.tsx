import React from "react";
import { AbsoluteFill, interpolate, OffthreadVideo, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

// Clip real de Pexels (ver clips/creditos.md). Encuadre 9:16 recortado al
// centro + zoom lento continuo — la cámara nunca está estática ni sobre los
// clips reales, igual que sobre la tipografía y los íconos.
export const ClipReal: React.FC<{ archivo: string; desdeFrame: number; duracionFrames: number; recortarDesde?: number }> = ({
  archivo,
  desdeFrame,
  duracionFrames,
  recortarDesde = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const avance = Math.min(Math.max((frame - desdeFrame) / duracionFrames, 0), 1);
  const escala = interpolate(avance, [0, 1], [1.05, 1.22]);

  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <OffthreadVideo
        src={staticFile(archivo)}
        startFrom={Math.round(recortarDesde * fps)}
        muted
        style={{
          position: "absolute", top: "50%", left: "50%", width: "100%", height: "100%",
          objectFit: "cover", transform: `translate(-50%, -50%) scale(${escala})`,
          filter: "saturate(0.75) contrast(1.15) brightness(1.05)",
        }}
      />
      {/* Velo oscuro para que el subtítulo blanco/amarillo siga siendo legible. */}
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0.15) 40%, rgba(0,0,0,0.6) 100%)" }} />
    </AbsoluteFill>
  );
};
