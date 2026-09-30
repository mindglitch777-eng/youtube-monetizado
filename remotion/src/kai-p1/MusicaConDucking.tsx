import React from "react";
import { Audio, interpolate, staticFile } from "remotion";

const DB = (db: number) => Math.pow(10, db / 20);
const NIVEL_BASE = DB(-22); // RULES.md, REGLA DE SONIDO
const NIVEL_DUCKED = DB(-28); // -22 - 6 mientras habla la voz
const RAMPA_FRAMES = 4; // transición suave, no un salto brusco de volumen

// Música de fondo en loop con ducking: baja -6dB mientras hay voz, sube al
// nivel base en los tramos sin voz (pausas HOOK y el silencio pre-CTA).
export const MusicaConDucking: React.FC<{ archivo: string; pausasSinVoz: Array<[number, number]> }> = ({
  archivo, pausasSinVoz,
}) => {
  const volumen = (frame: number) => {
    for (const [desde, hasta] of pausasSinVoz) {
      if (frame >= desde - RAMPA_FRAMES && frame < hasta + RAMPA_FRAMES) {
        if (frame < desde) return interpolate(frame, [desde - RAMPA_FRAMES, desde], [NIVEL_DUCKED, NIVEL_BASE]);
        if (frame > hasta - RAMPA_FRAMES) return interpolate(frame, [hasta - RAMPA_FRAMES, hasta], [NIVEL_BASE, NIVEL_DUCKED]);
        return NIVEL_BASE;
      }
    }
    return NIVEL_DUCKED;
  };

  return <Audio src={staticFile(`musica-kai/${archivo}`)} loop volume={volumen} />;
};
