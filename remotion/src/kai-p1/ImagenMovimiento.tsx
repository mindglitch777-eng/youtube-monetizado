import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";

// Movimiento lento y continuo por imagen (regla del .md: "zoom-in lento en
// las imágenes impares, paneo lento en las pares. Corte seco entre
// imágenes, sin fundidos" — el corte seco lo da el <Sequence> del padre,
// que cambia de imagen sin transición).
export const ImagenMovimiento: React.FC<{ archivo: string; duracionFrames: number; movimiento: "zoom" | "pan" }> = ({
  archivo, duracionFrames, movimiento,
}) => {
  const frame = useCurrentFrame();
  const avance = duracionFrames > 0 ? Math.min(1, frame / duracionFrames) : 0;

  let transform: string;
  if (movimiento === "zoom") {
    const escala = interpolate(avance, [0, 1], [1.0, 1.12]);
    transform = `scale(${escala})`;
  } else {
    const escala = 1.16;
    const x = interpolate(avance, [0, 1], [-6, 6]);
    transform = `scale(${escala}) translateX(${x}%)`;
  }

  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000000" }}>
      <Img
        src={staticFile(`kai-p1-images/${archivo}`)}
        style={{
          position: "absolute", inset: 0, width: "100%", height: "100%",
          objectFit: "cover", transform, transformOrigin: "center",
        }}
      />
    </AbsoluteFill>
  );
};
