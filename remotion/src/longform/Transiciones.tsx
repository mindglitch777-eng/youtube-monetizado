import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import type { Shot } from "./tipos";

// Efecto de entrada de una toma (transition_in), como overlay sobre sus
// primeros frames — `cut` no renderiza nada.
export const Transicion: React.FC<{ tipo: Shot["transition_in"] }> = ({ tipo }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();

  if (tipo === "cut") return null;

  if (tipo === "flash") {
    const op = interpolate(frame, [0, 3, 8], [0, 0.85, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    if (op <= 0) return null;
    return <AbsoluteFill style={{ background: "#fff5e0", opacity: op, pointerEvents: "none" }} />;
  }

  if (tipo === "dip") {
    const op = interpolate(frame, [0, 10], [1, 0], { extrapolateRight: "clamp" });
    if (op <= 0) return null;
    return <AbsoluteFill style={{ background: "#000000", opacity: op, pointerEvents: "none" }} />;
  }

  // glitch: 8 frames, 3 franjas con corrimiento RGB + cortes horizontales.
  const activo = frame < 8;
  if (!activo) return null;
  const intensidad = interpolate(frame, [0, 2, 8], [1, 1, 0], { extrapolateRight: "clamp" });
  const bandas = [0.22, 0.5, 0.74];
  return (
    <AbsoluteFill style={{ pointerEvents: "none", overflow: "hidden" }}>
      {bandas.map((y, i) => {
        const alto = height * 0.08;
        const offset = (i % 2 === 0 ? 1 : -1) * 18 * intensidad * Math.sin(frame * 3 + i);
        const color = ["#ff2d55", "#2d9bff", "#ffffff"][i];
        return (
          <div
            key={i}
            style={{
              position: "absolute", left: 0, top: y * height - alto / 2, width, height: alto,
              background: color, opacity: 0.35 * intensidad, mixBlendMode: "screen",
              transform: `translateX(${offset}px)`,
            }}
          />
        );
      })}
      <AbsoluteFill style={{ background: "#ffffff", opacity: 0.06 * intensidad, mixBlendMode: "overlay" }} />
    </AbsoluteFill>
  );
};
