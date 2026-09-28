import React, { useMemo } from "react";
import { AbsoluteFill, Sequence, useCurrentFrame, useVideoConfig } from "remotion";
import { Captions } from "./Captions";
import { Grano } from "./Estilos";
import "./Fuentes";
import { Plate } from "./Plate";
import { Pullquote } from "./Pullquote";
import { RedThread, type PuntoHilo } from "./RedThread";
import { ShotClip } from "./ShotClip";
import { ShotImage } from "./ShotImage";
import { Transicion } from "./Transiciones";
import type { PalabraAbs, Shot, Timeline } from "./tipos";

const OVERLAP_S = 0.4;

export const LongForm: React.FC<{ shots: Shot[]; timeline: Timeline }> = ({ shots, timeline }) => {
  const { fps, durationInFrames } = useVideoConfig();
  const overlapFrames = Math.round(OVERLAP_S * fps);

  const porId = useMemo(() => new Map(timeline.tomas.map((t) => [t.id, t])), [timeline]);

  const puntosHilo: PuntoHilo[] = useMemo(
    () =>
      shots.map((s) => {
        const t = porId.get(s.id);
        return { startFrame: t ? t.startFrame : 0, count: s.thread.count, state: s.thread.state };
      }),
    [shots, porId],
  );

  // Toma activa en el frame absoluto actual (para subtítulos y pullquote,
  // que viven arriba de todas las tomas, no dentro de cada Sequence).
  const frame = useCurrentFrame();
  const activa = useMemo(() => {
    for (const t of timeline.tomas) {
      if (frame >= t.startFrame && frame < t.endFrame) return t;
    }
    return null;
  }, [timeline, frame]);
  const shotActivo = activa ? shots.find((s) => s.id === activa.id) : undefined;

  const palabrasLocal = (t: (typeof timeline.tomas)[number]): PalabraAbs[] =>
    t.palabras.map((p) => ({ texto: p.texto, inicio: p.inicio - t.startS, fin: p.fin - t.startS }));

  return (
    <AbsoluteFill style={{ backgroundColor: "#000000" }}>
      {timeline.tomas.map((t) => {
        const shot = shots.find((s) => s.id === t.id);
        if (!shot) return null;
        const duracionSeq = Math.min(t.endFrame - t.startFrame + overlapFrames, durationInFrames - t.startFrame);
        return (
          <Sequence key={t.id} from={t.startFrame} durationInFrames={duracionSeq} layout="none">
            {shot.type === "ai" && shot.ai && (
              <ShotImage archivo={shot.ai.file} motion={shot.motion as never} grade={shot.grade} duracionFrames={duracionSeq} />
            )}
            {shot.type === "clip" && shot.clip && (
              <ShotClip archivo={`fit/${shot.clip.id}.mp4`} grade={shot.grade} duracionFrames={duracionSeq} />
            )}
            {shot.type === "plate" && shot.plate && <Plate data={shot.plate} duracionFrames={duracionSeq} />}
            <Transicion tipo={t.transitionOverride ?? shot.transition_in} />
          </Sequence>
        );
      })}

      {/* Grieta/hilo rojo: motivo continuo, vive arriba de todas las tomas. */}
      <RedThread puntos={puntosHilo} />

      {/* Subtítulos / cita: una sola instancia global que mira la toma
          activa por frame absoluto (nunca la misma oración completa que
          una placa o una cita al mismo tiempo — N9). */}
      {activa && shotActivo && shotActivo.overlay?.kind === "pullquote" && (
        <Pullquote texto={shotActivo.overlay.text} />
      )}
      {activa && shotActivo && shotActivo.captions && !shotActivo.overlay?.hide_captions_during && (
        <Captions palabras={palabrasLocal(activa)} duracionSeg={activa.endS - activa.startS} />
      )}

      <Grano />
    </AbsoluteFill>
  );
};
