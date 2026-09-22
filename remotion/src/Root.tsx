import React from "react";
import { CalculateMetadataFunction, Composition, staticFile } from "remotion";
import type { Props, Timeline } from "./tipos";
import { Video } from "./Video";

const FPS = 30;

// Lee public/timeline.json (lo copia scripts/preparar.mjs) y ajusta la duración.
const calcularMetadata: CalculateMetadataFunction<Props> = async () => {
  const respuesta = await fetch(staticFile("timeline.json"));
  if (!respuesta.ok) return { props: { timeline: null }, durationInFrames: FPS * 5 };
  const timeline = (await respuesta.json()) as Timeline;
  return { props: { timeline }, durationInFrames: Math.ceil(timeline.duracionTotal * FPS) };
};

export const Root: React.FC = () => (
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
);
