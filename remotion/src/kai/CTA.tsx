import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

// Regla 11 + 12: CTA de una sola palabra, cierre seco, sin despedida — para
// favorecer el loop automático. Nada de fade-out largo ni tarjeta de
// suscripción: aparece rápido y el video corta.
export const CTA: React.FC<{ texto: string }> = ({ texto }) => {
  const frame = useCurrentFrame();
  const entrada = interpolate(frame, [0, 6], [0, 1], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: "#000000", alignItems: "center", justifyContent: "center" }}>
      <div
        style={{
          fontFamily: "Anton, Inter, sans-serif", fontWeight: 900, fontSize: 88, color: "#FFFFFF",
          textTransform: "uppercase", opacity: entrada, letterSpacing: "0.03em",
        }}
      >
        {texto}
      </div>
    </AbsoluteFill>
  );
};
