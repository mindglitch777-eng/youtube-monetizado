import React from "react";
import { CalculateMetadataFunction, Composition, staticFile } from "remotion";
import { EscenaFase0 } from "./fase0/EscenaFase0";
import { Personaje2D } from "./fase0/Personaje2D";
import { Personaje3D } from "./fase0/Personaje3D";
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
  </>
);
