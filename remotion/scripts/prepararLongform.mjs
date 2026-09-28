// Copia a remotion/public/ todo lo que usa la composición LongForm:
// shots.json, timeline.json, img/*.jpg, clips/fit/*.mp4 (como fit/*.mp4,
// que es como los busca ShotClip.tsx) y las fuentes (Inter, Playfair
// Display, igual patrón que Montserrat en preparar.mjs).
// Uso: node scripts/prepararLongform.mjs ../content/<nombre-video-pack>
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const remotion = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const publico = path.join(remotion, "public");

const carpetaVideo = process.argv[2];
if (!carpetaVideo) {
  console.error("Uso: node scripts/prepararLongform.mjs ../content/<nombre-video-pack>");
  process.exit(1);
}
const carpeta = path.resolve(process.cwd(), carpetaVideo);

const rutaShots = path.join(carpeta, "shots.json");
const rutaTimeline = path.join(carpeta, "timeline.json");
if (!fs.existsSync(rutaShots) || !fs.existsSync(rutaTimeline)) {
  console.error(`Faltan shots.json o timeline.json en ${carpeta}.`);
  process.exit(1);
}

fs.rmSync(publico, { recursive: true, force: true });
fs.mkdirSync(publico, { recursive: true });

fs.cpSync(path.join(remotion, "fuentes"), path.join(publico, "fuentes"), { recursive: true });
fs.copyFileSync(rutaShots, path.join(publico, "shots.json"));
fs.copyFileSync(rutaTimeline, path.join(publico, "timeline.json"));

const shots = JSON.parse(fs.readFileSync(rutaShots, "utf-8")).shots;

fs.mkdirSync(path.join(publico, "img"), { recursive: true });
fs.mkdirSync(path.join(publico, "fit"), { recursive: true });

const faltantes = [];
for (const s of shots) {
  if (s.type === "ai" && s.ai) {
    const origen = path.join(carpeta, s.ai.file);
    if (fs.existsSync(origen)) {
      fs.copyFileSync(origen, path.join(publico, s.ai.file));
    } else {
      faltantes.push(s.ai.file);
    }
  }
  if (s.type === "clip" && s.clip) {
    const origen = path.join(carpeta, "clips", "fit", `${s.clip.id}.mp4`);
    if (fs.existsSync(origen)) {
      fs.copyFileSync(origen, path.join(publico, "fit", `${s.clip.id}.mp4`));
    } else {
      faltantes.push(`clips/fit/${s.clip.id}.mp4`);
    }
  }
}

if (faltantes.length) {
  console.warn(`Faltan ${faltantes.length} archivos (LongForm se arma sin ellos, van a verse negros):`);
  faltantes.forEach((f) => console.warn(`  - ${f}`));
} else {
  console.log(`Listo: ${shots.length} tomas de datos + assets copiados a remotion/public/.`);
}
console.log(`Render: npx remotion render LongForm ${path.relative(remotion, path.join(carpeta, "out", "video_silent.mp4"))} --codec=h264 --crf=18`);
