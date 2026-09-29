import React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { CTA } from "./CTA";
import { Contador } from "./Contador";
import { ElementoRecurrente } from "./ElementoRecurrente";
import "./Fuentes";
import { ImagenConBeats } from "./ImagenConBeats";
import { Subtitulos } from "./Subtitulos";
import { TripleEnfasis } from "./TripleEnfasis";
import type { PalabraAbs, ShotsKai, TimelineKai } from "./tipos";

// Formato listicle "Top 5" de la línea Kai (RULES.md, "FÓRMULA DE
// RETENCIÓN — línea Kai / formato simple"). A diferencia de LongForm, acá
// TODO vive dentro del <Sequence> de su propia toma (nunca arriba, con
// frame absoluto) — evita a propósito el bug de tiempo absoluto/relativo
// que tuvo LongForm con los subtítulos (ver AUDIT.md de
// "he-never-raised-his-voice", desvío 13).
export const KaiListicle: React.FC<{ shots: ShotsKai; timeline: TimelineKai }> = ({ shots, timeline }) => {
  const puntoPorN = new Map(shots.puntos.map((p) => [p.n, p]));

  return (
    <AbsoluteFill style={{ backgroundColor: "#000000" }}>
      {timeline.tomas.map((t) => {
        const duracion = t.endFrame - t.startFrame;
        const palabrasLocal: PalabraAbs[] = t.palabras.map((p) => ({
          texto: p.texto, inicio: p.inicio - t.startS, fin: p.fin - t.startS,
        }));

        if (t.id === "CTA") {
          return (
            <Sequence key={t.id} from={t.startFrame} durationInFrames={duracion} layout="none">
              <CTA texto={shots.cta} />
            </Sequence>
          );
        }

        const n = t.id === "HOOK" ? null : Number(t.id.slice(1));
        const punto = n !== null ? puntoPorN.get(n) : undefined;
        const imagen = punto?.imagen ?? shots.puntos[0]?.imagen;

        return (
          <Sequence key={t.id} from={t.startFrame} durationInFrames={duracion} layout="none">
            {imagen && <ImagenConBeats archivo={imagen} duracionFrames={duracion} />}
            {n !== null && <Contador n={n} total={shots.puntos.length} />}
            {punto?.elementoRecurrente && shots.elementoRecurrente && (
              <ElementoRecurrente imagen={shots.elementoRecurrente.imagen} />
            )}
            {n === shots.puntoFraseTriple && (
              <TripleEnfasis frase={shots.fraseTriple} inicioS={Math.max(0, (t.endS - t.startS) * 0.35)} />
            )}
            <Subtitulos palabras={palabrasLocal} duracionSeg={t.endS - t.startS} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
