import React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { Contador } from "./Contador";
import { GridIntro } from "./GridIntro";
import { ImagenMovimiento } from "./ImagenMovimiento";
import { Subtitulos } from "./Subtitulos";
import type { LineaTimeline } from "./tipos";

const FPS = 30;

// Contenido de UNA línea durante la parte con audio (sin la pausa post-HOOK,
// que se deja en blanco/negro afuera de este componente). Vive dentro del
// <Sequence> local de su línea — todo en tiempo LOCAL, mismo criterio que
// remotion/src/kai/KaiListicle.tsx.
export const Toma: React.FC<{ linea: LineaTimeline }> = ({ linea }) => {
  let cursorFrame = 0;
  const bloquesImagen = linea.imagenes.map((img, i) => {
    const duracionFrames = Math.round(img.duracionS * FPS);
    const from = cursorFrame;
    cursorFrame += duracionFrames;
    return { ...img, from, duracionFrames, key: i };
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#000000" }}>
      {linea.esGridIntro ? (
        <GridIntro
          archivoGrid={linea.imagenes[0].archivo}
          archivoPanel={linea.imagenes[1].archivo}
          triggerFrame={Math.round((linea.triggerTodayS ?? linea.endS - linea.startS) * FPS)}
        />
      ) : (
        bloquesImagen.map((b) => (
          <Sequence key={b.key} from={b.from} durationInFrames={b.duracionFrames} layout="none">
            <ImagenMovimiento archivo={b.archivo} duracionFrames={b.duracionFrames} movimiento={b.movimiento} />
          </Sequence>
        ))
      )}
      {linea.contadorVisible && linea.contadorValor !== null && <Contador valor={linea.contadorValor} />}
      <Subtitulos palabras={linea.palabras} duracionSeg={linea.duracionAudioFrames / FPS} />
    </AbsoluteFill>
  );
};
