import React from "react";
import { AbsoluteFill, useVideoConfig } from "remotion";

// Contador en pantalla (número de la señal, 5→1): blanco con borde negro,
// grande, arriba dentro del 15% libre. Visible/oculto y valor los decide
// scripts/kai_p1_timeline.py línea por línea (regla del .md).
export const Contador: React.FC<{ valor: number }> = ({ valor }) => {
  const { height } = useVideoConfig();
  return (
  <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-start", paddingTop: height * 0.06 }}>
    <div
      style={{
        fontFamily: "Anton, sans-serif", fontSize: 140, color: "#FFFFFF", lineHeight: 1,
        WebkitTextStroke: "6px #000000", paintOrder: "stroke fill",
      }}
    >
      {valor}
    </div>
  </AbsoluteFill>
  );
};
