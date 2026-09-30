import React from "react";
import { CalculateMetadataFunction, Composition, staticFile } from "remotion";
import { EscenaFase0 } from "./fase0/EscenaFase0";
import { Personaje2D } from "./fase0/Personaje2D";
import { Personaje3D } from "./fase0/Personaje3D";
import { KaiListicle } from "./kai/KaiListicle";
import type { ShotsKai, TimelineKai } from "./kai/tipos";
import { KaiP1LoveBombing } from "./kai-p1/KaiP1LoveBombing";
import type { TimelineKaiP1 } from "./kai-p1/tipos";
import { ManipulacionParte1 } from "./manipulacion-parte1/ManipulacionParte1";
import { Miniatura } from "./manipulacion-parte1/Miniatura";
import type { TimelineStandalone } from "./manipulacion-parte1/tipos";
import { prepararShort } from "./shorts";
import type { Props, PropsShort, Timeline } from "./tipos";
import { Video } from "./Video";

const FPS = 30;

// Lee public/timeline.json (lo copia scripts/preparar.mjs).
async function leerTimeline(): Promise<Timeline | null> {
  const respuesta = await fetch(staticFile("timeline.json"));
  return respuesta.ok ? ((await respuesta.json()) as Timeline) : null;
}

const calcularMetadata: CalculateMetadataFunction<Props> = async () => {
  const timeline = await leerTimeline();
  if (!timeline) return { props: { timeline: null }, durationInFrames: FPS * 5 };
  return { props: { timeline }, durationInFrames: Math.ceil(timeline.duracionTotal * FPS) };
};

// Short: un bloque del video largo o un short standalone (RULES.md, sección Shorts).
const calcularMetadataShort: CalculateMetadataFunction<PropsShort> = async ({ props }) => {
  const completo = await leerTimeline();
  if (!completo) return { props: { ...props, timeline: null }, durationInFrames: FPS * 5 };
  const timeline = prepararShort(completo, props.bloque);
  return { props: { ...props, timeline }, durationInFrames: Math.ceil(timeline.duracionTotal * FPS) };
};

// Mismo componente que el video largo; el recorte lo hace calcularMetadataShort.
const Short: React.FC<PropsShort> = ({ timeline }) => <Video timeline={timeline} />;

export const Root: React.FC = () => (
  <>
    <Composition
      id="Video"
      component={Video}
      width={1920}
      height={1080}
      fps={FPS}
      durationInFrames={FPS * 5}
      defaultProps={{ timeline: null } as Props}
      calculateMetadata={calcularMetadata}
    />
    <Composition
      id="Short"
      component={Short}
      width={1080}
      height={1920}
      fps={FPS}
      durationInFrames={FPS * 5}
      defaultProps={{ timeline: null, bloque: 1 } as PropsShort}
      calculateMetadata={calcularMetadataShort}
    />
    {/* Fase 0 — pruebas temporales de comparación 3D vs 2D. Borrar tras decidir. */}
    <Composition
      id="Fase0-Personaje3D"
      component={Personaje3D}
      width={1080}
      height={1920}
      fps={FPS}
      durationInFrames={FPS * 8}
      defaultProps={{ cambioEnFrame: FPS * 3 }}
    />
    <Composition
      id="Fase0-Personaje2D"
      component={Personaje2D}
      width={1080}
      height={1920}
      fps={FPS}
      durationInFrames={FPS * 8}
      defaultProps={{ cambioEnFrame: FPS * 3 }}
    />
    <Composition
      id="Fase0-Escena"
      component={EscenaFase0}
      width={1080}
      height={1920}
      fps={FPS}
      durationInFrames={FPS * 7}
    />
    <Composition
      id="ManipulacionParte1"
      component={ManipulacionParte1}
      width={1080}
      height={1920}
      fps={FPS}
      durationInFrames={FPS * 5}
      defaultProps={{ timeline: null as unknown as TimelineStandalone }}
      calculateMetadata={async () => {
        const respuesta = await fetch(staticFile("timeline.json"));
        const timeline = (await respuesta.json()) as TimelineStandalone;
        return { props: { timeline }, durationInFrames: Math.ceil(timeline.duracionTotal * FPS) };
      }}
    />
    <Composition id="ManipulacionParte1-Miniatura" component={Miniatura} width={1080} height={1920} fps={FPS} durationInFrames={1} />
    <Composition
      id="KaiListicle"
      component={KaiListicle}
      width={1080}
      height={1920}
      fps={FPS}
      durationInFrames={FPS * 5}
      defaultProps={{ shots: null as unknown as ShotsKai, timeline: null as unknown as TimelineKai }}
      calculateMetadata={async () => {
        const [respShots, respTimeline] = await Promise.all([
          fetch(staticFile("kai-shots.json")),
          fetch(staticFile("kai-timeline.json")),
        ]);
        const shots = (await respShots.json()) as ShotsKai;
        const timeline = (await respTimeline.json()) as TimelineKai;
        return { props: { shots, timeline }, durationInFrames: timeline.tomas.at(-1)?.endFrame ?? FPS * 5 };
      }}
    />
    <Composition
      id="KaiP1LoveBombing"
      component={KaiP1LoveBombing}
      width={1080}
      height={1920}
      fps={FPS}
      durationInFrames={FPS * 5}
      defaultProps={{ timeline: null as unknown as TimelineKaiP1 }}
      calculateMetadata={async () => {
        const respuesta = await fetch(staticFile("kai-p1-timeline.json"));
        const timeline = (await respuesta.json()) as TimelineKaiP1;
        return { props: { timeline }, durationInFrames: Math.ceil(timeline.duracionTotal * FPS) };
      }}
    />
  </>
);
