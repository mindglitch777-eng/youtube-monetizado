import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";

// Regla 9: elemento visual recurrente sin resolver — aparece 2-3 veces en
// el video sin explicación, se resuelve en la parte/video siguiente. Un
// ícono chico en una esquina fija, discreto, nunca explicado en pantalla.
export const ElementoRecurrente: React.FC<{ imagen: string }> = ({ imagen }) => {
  const frame = useCurrentFrame();
  const entrada = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ alignItems: "flex-end", justifyContent: "flex-start", padding: 40 }}>
      <div style={{ width: 84, height: 84, opacity: entrada * 0.92, filter: "drop-shadow(0 2px 10px rgba(0,0,0,0.6))" }}>
        <Img src={staticFile(imagen)} style={{ width: "100%", height: "100%", objectFit: "contain" }} />
      </div>
    </AbsoluteFill>
  );
};
