import React from "react";
import { AbsoluteFill, OffthreadVideo, staticFile, useCurrentFrame } from "remotion";
import { ConGrado } from "./Estilos";
import { transformDeMovimiento } from "./Movimiento";

// Clip real, ya ajustado a la duración exacta de la toma (+0,4s de solape)
// por scripts/pack_prep_clips.py (recorte, loop+crossfade o desacelerado
// según haga falta — ver Paso 4 del PACK). Acá solo se reproduce con el
// mismo push_in lento y el mismo grado que las imágenes.
export const ShotClip: React.FC<{ archivo: string; grade: string; duracionFrames: number }> = ({ archivo, grade, duracionFrames }) => {
  const frame = useCurrentFrame();
  const avance = duracionFrames > 0 ? frame / duracionFrames : 0;
  const { transform, transformOrigin } = transformDeMovimiento("push_in", avance);

  return (
    <ConGrado grade={grade}>
      <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#050505" }}>
        <OffthreadVideo
          src={staticFile(archivo)}
          muted
          style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", transform, transformOrigin }}
        />
      </AbsoluteFill>
    </ConGrado>
  );
};
