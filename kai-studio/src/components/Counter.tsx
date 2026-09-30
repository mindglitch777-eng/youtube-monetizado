import React from "react";
import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COUNTER_Y, FONT, STROKE } from "../theme";

type Props = { states: { from: number; value: string }[] };

export const Counter: React.FC<Props> = ({ states }) => {
  const frame = useCurrentFrame();
  const { fps, height } = useVideoConfig();

  let current = states[0];
  for (const s of states) if (s.from <= frame) current = s;
  if (!current || current.value === "off") return null;

  const pop = spring({ frame: frame - current.from, fps, config: { damping: 9, stiffness: 180, mass: 0.6 } });
  const scale = 0.6 + 0.4 * Math.min(1.25, pop);

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: height * COUNTER_Y,
          textAlign: "center",
          fontFamily: FONT,
          fontWeight: 800,
          fontSize: 230,
          lineHeight: 1,
          color: "#fff",
          WebkitTextStroke: `14px ${STROKE}`,
          paintOrder: "stroke fill",
          transform: `scale(${scale})`,
        }}
      >
        {current.value}
      </div>
    </AbsoluteFill>
  );
};
