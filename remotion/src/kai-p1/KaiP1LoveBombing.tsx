import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import "../kai/Fuentes";
import { CapaSfx } from "./CapaSfx";
import { MusicaConDucking } from "./MusicaConDucking";
import { Toma } from "./Toma";
import type { TimelineKaiP1 } from "./tipos";

// content-kai/parte1-love-bombing — ensamblado según las instrucciones del
// video (instrucciones-claude-code-kai-parte1.md) + RULES.md, REGLA DE
// SONIDO: voz al 100%, música oscura con ducking, SFX puntuales, silencio
// antes del CTA. Última línea corta seco al terminar el audio, sin
// pantalla de cierre.
export const KaiP1LoveBombing: React.FC<{
  timeline: TimelineKaiP1; sfxDisponibles: string[]; musicaArchivo: string | null;
}> = ({ timeline, sfxDisponibles, musicaArchivo }) => {
  const disponibles = React.useMemo(() => new Set(sfxDisponibles), [sfxDisponibles]);
  return (
    <AbsoluteFill style={{ backgroundColor: "#000000" }}>
      <Audio src={staticFile(timeline.audio)} />
      {musicaArchivo && <MusicaConDucking archivo={musicaArchivo} pausasSinVoz={timeline.pausasSinVoz} />}
      <CapaSfx eventos={timeline.sfxEventos} disponibles={disponibles} />
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
