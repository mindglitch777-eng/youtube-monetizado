import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig, Easing } from "remotion";
import type { Effect } from "../types";

type Props = { src: string; dur: number; effect?: Effect; index: number };

/** One still with slow movement. Odd images zoom in, even images pan, unless an explicit effect is set. */
export const KaiImage: React.FC<Props> = ({ src, dur, effect, index }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const p = Math.min(1, Math.max(0, frame / Math.max(1, dur - 1)));

  const kind = effect?.kind ?? (index % 2 === 0 ? "zoomIn" : index % 4 === 1 ? "panLeft" : "panRight");

  let scale = 1;
  let tx = 0;
  let originX = 0.5;
  let originY = 0.5;

  if (kind === "zoomIn") {
    scale = interpolate(p, [0, 1], [1.0, 1.12]);
  } else if (kind === "zoomOut") {
    scale = interpolate(p, [0, 1], [1.14, 1.0]);
  } else if (kind === "panLeft") {
    scale = 1.12;
    tx = interpolate(p, [0, 1], [width * 0.035, -width * 0.035]);
  } else if (kind === "panRight") {
    scale = 1.12;
    tx = interpolate(p, [0, 1], [-width * 0.035, width * 0.035]);
  } else if (kind === "zoomToPoint") {
    const focus = effect?.focus ?? [0.5, 0.5];
    const to = effect?.scaleTo ?? 2.4;
    originX = focus[0];
    originY = focus[1];
    // hold briefly so the grid can be read, then accelerate into the panel ("zoom hit")
    const e = interpolate(p, [0.35, 1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.in(Easing.cubic) });
    scale = 1 + (to - 1) * e;
  }

  void height;
  return (
    <AbsoluteFill style={{ backgroundColor: "#0b1020", overflow: "hidden" }}>
      <Img
        src={staticFile(src)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `translateX(${tx}px) scale(${scale})`,
          transformOrigin: `${originX * 100}% ${originY * 100}%`,
        }}
      />
    </AbsoluteFill>
  );
};
