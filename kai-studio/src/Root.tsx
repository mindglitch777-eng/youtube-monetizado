import React from "react";
import { Composition, staticFile } from "remotion";
import type { CalculateMetadataFunction } from "remotion";
import { Episode } from "./Episode";
import type { KaiProps, Script, SfxManifest, Timing } from "./types";
import { buildTimeline, FPS } from "./lib/timeline";

const getJson = async <T,>(path: string): Promise<T | null> => {
  try {
    const res = await fetch(staticFile(path));
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  }
};

const calculateMetadata: CalculateMetadataFunction<KaiProps> = async ({ props }) => {
  const base = `episodes/${props.slug}/${props.lang}`;
  const script = await getJson<Script>(`${base}/script.json`);
  const timing = await getJson<Timing>(`${base}/timing.json`);
  if (!script) throw new Error(`Missing public/${base}/script.json`);
  if (!timing) throw new Error(`Missing public/${base}/timing.json (run: python tools/make_audio.py ${props.slug} ${props.lang})`);

  const manifest = await getJson<SfxManifest>("sfx/manifest.json");
  const files = new Set((manifest?.files ?? []).map((f) => f.replace(/\.(mp3|wav|ogg)$/i, "")));
  const sfxNames = new Set([...files].filter((f) => f !== "music"));

  const timeline = buildTimeline(script, timing, sfxNames, FPS);
  if (!files.has("music")) timeline.warnings.push("__no_music__");
  timeline.warnings
    .filter((w) => w !== "__no_music__")
    .forEach((w) => console.warn("[kai]", w));

  return {
    durationInFrames: timeline.totalFrames,
    fps: FPS,
    width: 1080,
    height: 1920,
    props: { ...props, timeline, script },
  };
};

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Kai"
    component={Episode}
    durationInFrames={FPS * 60}
    fps={FPS}
    width={1080}
    height={1920}
    defaultProps={{ slug: "love-bombing", lang: "en" } as KaiProps}
    calculateMetadata={calculateMetadata}
  />
);
