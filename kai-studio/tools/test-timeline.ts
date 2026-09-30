// Prueba rápida del armado de tiempos (sin renderizar). Uso: npm test
import fs from "node:fs";
import path from "node:path";
import { buildTimeline, musicVolume, dbToGain } from "../src/lib/timeline";
import type { Script, Timing } from "../src/types";

const root = path.resolve(__dirname, "..");
let failed = 0;
const ok = (cond: boolean, msg: string) => {
  console.log(`${cond ? "PASS" : "FAIL"}  ${msg}`);
  if (!cond) failed++;
};

for (const lang of ["en", "es"] as const) {
  const base = path.join(root, "public/episodes/love-bombing", lang);
  const scriptPath = path.join(root, "episodes/love-bombing", lang, "script.json");
  const timingPath = path.join(base, "timing.json");
  if (!fs.existsSync(timingPath)) {
    console.log(`SKIP  ${lang}: falta timing.json (python tools/make_audio.py love-bombing ${lang} --estimate)`);
    continue;
  }
  const script: Script = JSON.parse(fs.readFileSync(scriptPath, "utf8"));
  const timing: Timing = JSON.parse(fs.readFileSync(timingPath, "utf8"));
  const sfx = new Set(["whoosh", "impact", "thud", "riser", "notification"]);
  const tl = buildTimeline(script, timing, sfx);

  console.log(`\n== ${lang}: ${tl.totalFrames} frames (${(tl.totalFrames / tl.fps).toFixed(1)} s)`);
  const segmentosEsperados = script.lines.reduce((acc, l) => acc + l.images.length, 0);
  ok(tl.images.length === segmentosEsperados, `${lang}: ${tl.images.length} segmentos de imagen en el timeline (esperados ${segmentosEsperados})`);
  // contiguous coverage
  let contiguous = tl.images[0].from === 0;
  for (let i = 1; i < tl.images.length; i++) {
    if (tl.images[i].from !== tl.images[i - 1].from + tl.images[i - 1].dur) contiguous = false;
  }
  const last = tl.images[tl.images.length - 1];
  ok(contiguous && last.from + last.dur === tl.totalFrames, `${lang}: las imágenes cubren el video completo sin huecos ni solapes`);
  // n tiene que estar dentro de 1..imageCount (no referenciar un archivo
  // que no existe). No se exige orden creciente: el número de archivo es
  // solo un identificador — no tiene que coincidir con el orden narrativo
  // (p.ej. la grilla de la línea 4 puede ser el archivo 1 aunque la línea
  // 1 use archivos más altos).
  const enRango = tl.images.every((im) => im.n >= 1 && im.n <= script.imageCount);
  ok(enRango, `${lang}: todas las imágenes referencian un archivo entre 1 y ${script.imageCount}`);
  ok(tl.voices.length === script.lines.length, `${lang}: una voz por línea (${tl.voices.length})`);
  const counts = tl.counter.map((c) => c.value).join(",");
  ok(counts === "off,5,4,3,2,1,off", `${lang}: contador ${counts}`);
  const hooks = script.lines.filter((l) => l.hook).length;
  ok(tl.sfx.filter((s) => s.name === "thud").length === hooks, `${lang}: ${hooks} golpes graves (uno por gancho)`);
  ok(tl.sfx.some((s) => s.name === "riser"), `${lang}: riser antes del zoom de la línea 4`);
  ok(tl.finalCutFrame !== null && musicVolume(tl.finalCutFrame + 1, tl) === 0, `${lang}: música cortada antes de la línea final`);
  const vw = tl.voiceWindows[5];
  const mid = Math.floor((vw.from + vw.to) / 2);
  const ducked = musicVolume(mid, tl);
  ok(Math.abs(ducked - dbToGain(-28)) < 1e-6, `${lang}: música a -28 dB (-22 base, -6 extra) mientras habla la voz`);
  ok(tl.chunks.length > 0 && tl.chunks.every((c) => c.to > c.from), `${lang}: subtítulos palabra por palabra (${tl.chunks.length} bloques)`);
  const short = tl.warnings.filter((w) => w.includes("on screen"));
  console.log(`      avisos de imágenes cortas (<1.0 s): ${short.length}`);
  short.slice(0, 5).forEach((w) => console.log("      ", w));
}

if (failed) {
  console.log(`\n${failed} prueba(s) fallaron`);
  process.exit(1);
}
console.log("\ntodo OK");
