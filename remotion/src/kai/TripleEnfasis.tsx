import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

// Regla 6: una frase repetida exactamente 3 veces en el punto de mayor
// impacto del guion. Cada repetición entra con un golpe de escala (punch)
// más marcado que la anterior, para que se sienta como un remate, no una
// simple repetición de texto.
const DURACION_POR_REPETICION_S = 0.85;

export const TripleEnfasis: React.FC<{ frase: string; inicioS: number }> = ({ frase, inicioS }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const frameInicio = Math.round(inicioS * fps);
  const framePorRepeticion = Math.round(DURACION_POR_REPETICION_S * fps);
  const relativo = frame - frameInicio;
  if (relativo < 0) return null;
  const repeticion = Math.min(2, Math.floor(relativo / framePorRepeticion));
  const frameDeEstaRepeticion = relativo - repeticion * framePorRepeticion;

  const golpe = spring({ frame: frameDeEstaRepeticion, fps, config: { damping: 10, stiffness: 220 + repeticion * 60 } });
  const escala = interpolate(golpe, [0, 1], [1.35 + repeticion * 0.08, 1]);
  const opacidad = interpolate(frameDeEstaRepeticion, [0, 3, framePorRepeticion - 6, framePorRepeticion], [0, 1, 1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  if (relativo >= framePorRepeticion * 3) return null;

  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
      <div
        style={{
          fontFamily: "Anton, Inter, sans-serif", fontWeight: 900, fontSize: 96, color: "#FFFFFF", textAlign: "center",
          textTransform: "uppercase", maxWidth: "88%", lineHeight: 1.05, textShadow: "0 6px 24px rgba(0,0,0,0.9)",
          transform: `scale(${escala})`, opacity: opacidad,
        }}
      >
        {frase}
      </div>
    </AbsoluteFill>
  );
};
