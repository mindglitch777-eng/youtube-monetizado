import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { ConGrado } from "./Estilos";
import { transformDeMovimiento, type Motion } from "./Movimiento";

// Imagen IA: fuente 1024² escalada ×1,875 (1920×1920) — la ventana visible
// es de 1080 de alto (56%), centrada: offset -420px. El movimiento de
// cámara se anima sobre la duración total del Sequence que lo contiene
// (que ya incluye el solape de 0,4s, ver LongForm.tsx).
export const ShotImage: React.FC<{ archivo: string; motion: Motion; grade: string; duracionFrames: number }> = ({
  archivo,
  motion,
  grade,
  duracionFrames,
}) => {
  const frame = useCurrentFrame();
  const avance = duracionFrames > 0 ? frame / duracionFrames : 0;
  const { transform, transformOrigin } = transformDeMovimiento(motion, avance);

  return (
    <ConGrado grade={grade}>
      <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#050505" }}>
        <Img
          src={staticFile(archivo)}
          style={{ position: "absolute", left: 0, top: -420, width: 1920, height: 1920, objectFit: "cover", transform, transformOrigin }}
        />
      </AbsoluteFill>
    </ConGrado>
  );
};
