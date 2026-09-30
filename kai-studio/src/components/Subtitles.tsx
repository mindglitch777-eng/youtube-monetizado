import React from "react";
import { AbsoluteFill, Sequence, useCurrentFrame, useVideoConfig } from "remotion";
import type { TChunk } from "../types";
import { FONT, MUSTARD, STROKE, SUBTITLE_Y } from "../theme";

const Chunk: React.FC<{ chunk: TChunk; start: number }> = ({ chunk, start }) => {
  const frame = useCurrentFrame() + start; // absolute frame
  const { height } = useVideoConfig();
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          left: 60,
          right: 60,
          top: height * SUBTITLE_Y,
          transform: "translateY(-50%)",
          textAlign: "center",
          fontFamily: FONT,
          fontWeight: 800,
          fontSize: 92,
          lineHeight: 1.12,
          color: "#fff",
          WebkitTextStroke: `10px ${STROKE}`,
          paintOrder: "stroke fill",
          textTransform: "none",
        }}
      >
        {chunk.words.map((w, i) => {
          const active = frame >= w.from && frame < w.to;
          return (
            <span key={i} style={{ color: active ? MUSTARD : "#fff", marginRight: 18 }}>
              {w.text}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

/** Word-by-word captions, active 100% of the voice time. The active word is mustard. */
export const Subtitles: React.FC<{ chunks: TChunk[] }> = ({ chunks }) => (
  <>
    {chunks.map((c, i) => {
      // hold each chunk until the next one starts so captions never flicker off between chunks
      const next = chunks[i + 1];
      const to = next ? Math.max(c.to, Math.min(next.from, c.to + 10)) : c.to + 4;
      return (
        <Sequence key={i} from={c.from} durationInFrames={Math.max(3, to - c.from)}>
          <Chunk chunk={c} start={c.from} />
        </Sequence>
      );
    })}
  </>
);
