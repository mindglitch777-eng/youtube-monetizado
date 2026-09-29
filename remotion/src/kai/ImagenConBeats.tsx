import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

const DURACION_BEAT_S = 2.4; // regla 7: cambio en pantalla cada 2-3s máximo

// 3 puntos de interés (offset de paneo) para ciclar sin generar imágenes
// nuevas: zoom lento y continuo (Ken Burns) + un "corte" duro de encuadre
// cada ~2.4s (salto de offset sin interpolar) — dos mecanismos de cambio
// visual sobre UNA sola imagen (regla 7 de RULES.md, línea Kai).
const PUNTOS_DE_INTERES: Array<{ x: number; y: number }> = [
  { x: 0, y: 0 },
  { x: -6, y: -4 },
  { x: 5, y: 3 },
];

export const ImagenConBeats: React.FC<{ archivo: string; duracionFrames: number }> = ({ archivo, duracionFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const avance = duracionFrames > 0 ? frame / duracionFrames : 0;
  const escala = interpolate(avance, [0, 1], [1.08, 1.22], { extrapolateRight: "clamp" });

  const beatActual = Math.floor(frame / fps / DURACION_BEAT_S) % PUNTOS_DE_INTERES.length;
  const { x, y } = PUNTOS_DE_INTERES[beatActual];

  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#050505" }}>
      <Img
        src={staticFile(archivo)}
        style={{
          position: "absolute", left: `${x}%`, top: `${y}%`, width: "100%", height: "100%",
          objectFit: "cover", transform: `scale(${escala})`, transformOrigin: "center",
        }}
      />
    </AbsoluteFill>
  );
};
