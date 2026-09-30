import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import type { KaiProps } from "./types";
import { KaiImage } from "./components/KaiImage";
import { Counter } from "./components/Counter";
import { Subtitles } from "./components/Subtitles";
import { Overlays } from "./components/Overlays";
import { dbToGain, musicVolume } from "./lib/timeline";

const VOICE_GAIN = 1.0;
const SFX_DB = -12;

const pad = (n: number) => String(n).padStart(2, "0");

export const Episode: React.FC<KaiProps> = ({ slug, timeline: tl, script, lang }) => {
  if (!tl || !script) return <AbsoluteFill style={{ backgroundColor: "#0b1020" }} />;
  const hasMusic = !tl.warnings.includes("__no_music__");

  return (
    <AbsoluteFill style={{ backgroundColor: "#0b1020" }}>
      {/* images */}
      {tl.images.map((im) => (
        <Sequence key={`img-${im.index}`} from={im.from} durationInFrames={im.dur}>
          <KaiImage
            src={`episodes/${slug}/images/${script.imagePrefix}${pad(im.n)}.png`}
            dur={im.dur}
            effect={im.effect}
            index={im.index}
          />
        </Sequence>
      ))}

      <Overlays overlays={tl.overlays} />
      <Counter states={tl.counter} />
      <Subtitles chunks={tl.chunks} />

      {/* voice (one mp3 per line) */}
      {tl.voices.map((v) => (
        <Sequence key={`v-${v.lineId}`} from={v.from} durationInFrames={v.dur + 2}>
          <Audio src={staticFile(v.src)} volume={VOICE_GAIN} />
        </Sequence>
      ))}

      {/* music: -22 dB, -6 dB more while the voice plays, cut before the final line */}
      {hasMusic ? (
        <Audio src={staticFile("sfx/music.mp3")} loop volume={(f) => musicVolume(f, tl)} />
      ) : null}

      {/* sfx: -12 dB, 2-3 frames BEFORE the visual cut (already offset in the timeline) */}
      {tl.sfx.map((s, i) => (
        <Sequence key={`sfx-${i}`} from={s.from}>
          <Audio src={staticFile(`sfx/${s.name}.mp3`)} volume={dbToGain(SFX_DB)} />
        </Sequence>
      ))}
      <div data-lang={lang} style={{ display: "none" }} />
    </AbsoluteFill>
  );
};
