import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import "../kai/Fuentes";
import { Toma } from "./Toma";
import type { TimelineKaiP1 } from "./tipos";

// content-kai/parte1-love-bombing — ensamblado según las instrucciones del
// video (instrucciones-claude-code-kai-parte1.md): último audio, imágenes
// provistas a mano, sin música ni logos. Última línea corta seco al
// terminar el audio, sin pantalla de cierre.
export const KaiP1LoveBombing: React.FC<{ timeline: TimelineKaiP1 }> = ({ timeline }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#000000" }}>
      <Audio src={staticFile(timeline.audio)} />
      {timeline.lineas.map((linea) => {
        const duracionTotal = linea.endFrame - linea.startFrame;
        return (
          <Sequence key={linea.n} from={linea.startFrame} durationInFrames={duracionTotal} layout="none">
            <Sequence from={0} durationInFrames={linea.duracionAudioFrames} layout="none">
              <Toma linea={linea} />
            </Sequence>
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
