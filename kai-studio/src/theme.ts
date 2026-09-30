import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// Fuentes locales (public/fonts/): @remotion/google-fonts pide las suyas a
// fonts.gstatic.com en cada render, y el entorno de Claude Code no tiene
// salida de red a ese host — con loadFont + staticFile no depende de
// internet (mismo criterio que ../remotion/src/kai/Fuentes.tsx).
loadFont({ family: "Anton", url: staticFile("fonts/Anton.ttf"), weight: "800" });

export const FONT = `Anton, "Arial Black", Arial, sans-serif`;
export const MUSTARD = "#E1A11B";
export const STROKE = "#000000";

// Layout (1080x1920). Top 15% and bottom 20% are kept free for platform UI.
export const SUBTITLE_Y = 0.67; // fraction of height where subtitles sit
export const COUNTER_Y = 0.075; // fraction of height where the 5..1 counter sits
