import React from "react";
import { AbsoluteFill, Sequence, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import type { TOverlay } from "../types";
import { FONT, STROKE } from "../theme";

const One: React.FC<{ o: TOverlay }> = ({ o }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const fade = interpolate(frame, [0, 6], [0, 1], { extrapolateRight: "clamp" });
  const isTitle = o.style === "title";
  return (
    <AbsoluteFill style={{ pointerEvents: "none", opacity: fade }}>
      <div
        style={{
          position: "absolute",
          left: isTitle ? 40 : o.x * width,
          right: isTitle ? 40 : undefined,
          top: o.y * height,
          transform: isTitle ? "translateY(-50%)" : "translate(-50%, -50%)",
          textAlign: "center",
          width: isTitle ? undefined : 440,
          fontFamily: FONT,
          fontWeight: 800,
          fontSize: isTitle ? 70 : 38,
          lineHeight: 1.05,
          color: "#fff",
          WebkitTextStroke: `${isTitle ? 9 : 7}px ${STROKE}`,
          paintOrder: "stroke fill",
        }}
      >
        {o.text}
      </div>
    </AbsoluteFill>
  );
};

export const Overlays: React.FC<{ overlays: TOverlay[] }> = ({ overlays }) => (
  <>
    {overlays.map((o, i) => (
      <Sequence key={i} from={o.from} durationInFrames={Math.max(1, o.dur)}>
        <One o={o} />
      </Sequence>
    ))}
  </>
);
