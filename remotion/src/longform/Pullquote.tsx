import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

// Cita entre comillas grandes, centrada sobre la franja de subtítulos —
// los subtítulos se ocultan mientras esta está visible (lo decide el
// padre, LongForm.tsx, no montando <Captions/> en ese shot).
export const Pullquote: React.FC<{ texto: string }> = ({ texto }) => {
  const frame = useCurrentFrame();
  const { fps, height } = useVideoConfig();
  const t = spring({ frame, fps, config: { damping: 16, stiffness: 140 } });
  const blur = interpolate(t, [0, 1], [16, 0], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-end", paddingBottom: Math.max(60, height * 0.09) }}>
      <div
        style={{
          fontFamily: "'Playfair Display', Georgia, serif", fontStyle: "italic", fontWeight: 700, fontSize: 72,
          color: "#FFFFFF", textAlign: "center", maxWidth: "80%", lineHeight: 1.2,
          textShadow: "0 4px 20px rgba(0,0,0,0.85)", opacity: interpolate(t, [0, 1], [0, 1]), filter: `blur(${blur}px)`,
        }}
      >
        &ldquo;{texto}&rdquo;
      </div>
    </AbsoluteFill>
  );
};
