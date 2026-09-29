import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

// Contador numérico visible en pantalla (regla 5) — fijo mientras dura el
// punto activo, no solo al arrancarlo.
export const Contador: React.FC<{ n: number; total: number }> = ({ n, total }) => {
  const frame = useCurrentFrame();
  const entrada = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ alignItems: "flex-start", justifyContent: "flex-start", padding: 48 }}>
      <div
        style={{
          fontFamily: "Anton, Inter, sans-serif", fontWeight: 900, fontSize: 64, color: "#FFFFFF",
          textShadow: "0 3px 14px rgba(0,0,0,0.9)", opacity: entrada, letterSpacing: "0.02em",
          display: "flex", alignItems: "baseline", gap: 4,
        }}
      >
        <span>{n}</span>
        <span style={{ fontSize: 34, opacity: 0.75 }}>/{total}</span>
      </div>
    </AbsoluteFill>
  );
};
