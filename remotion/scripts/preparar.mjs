// Copia a remotion/public/ todo lo que usa un video: timeline.json, audios,
// imágenes, sonidos de marca y el ícono de Knot.
// Uso: npm run preparar -- ../content/<nombre-video>
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const remotion = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const raiz = path.resolve(remotion, "..");
const publico = path.join(remotion, "public");

const carpetaVideo = process.argv[2];
if (!carpetaVideo) {
  console.error("Uso: npm run preparar -- ../content/<nombre-video>");
  process.exit(1);
}
const rutaTimeline = path.resolve(process.cwd(), carpetaVideo, "timeline.json");
if (!fs.existsSync(rutaTimeline)) {
  console.error(`No existe ${rutaTimeline}. Correr antes scripts/generar_audio.py.`);
  process.exit(1);
}
const timeline = JSON.parse(fs.readFileSync(rutaTimeline, "utf-8"));

fs.rmSync(publico, { recursive: true, force: true });
fs.mkdirSync(publico, { recursive: true });

fs.cpSync(path.join(remotion, "fuentes"), path.join(publico, "fuentes"), { recursive: true });

const faltantes = [];
const copiar = (relativo) => {
  const origen = path.join(raiz, relativo);
  if (!fs.existsSync(origen)) return false;
  const destino = path.join(publico, relativo);
  fs.mkdirSync(path.dirname(destino), { recursive: true });
  fs.copyFileSync(origen, destino);
  return true;
};

if (!copiar(timeline.icono)) faltantes.push(timeline.icono);
if (timeline.audio && !copiar(timeline.audio)) faltantes.push(timeline.audio);
for (const s of timeline.segmentos) {
  if (s.audio && !copiar(s.audio)) faltantes.push(s.audio);
  if (s.imagen && !copiar(s.imagen)) {
    faltantes.push(s.imagen);
    s.imagen = null;
  }
  s.sonidos = s.sonidos.filter((sonido) => {
    if (copiar(sonido.archivo)) return true;
    faltantes.push(sonido.archivo);
    return false;
  });
}
fs.writeFileSync(path.join(publico, "timeline.json"), JSON.stringify(timeline, null, 2));

const unicos = [...new Set(faltantes)];
if (unicos.length) {
  console.warn(`Faltan ${unicos.length} archivos (el video se arma sin ellos):`);
  unicos.forEach((f) => console.warn(`  - ${f}`));
}
if (unicos.some((f) => f.includes("/audio/"))) {
  console.error("Falta narración: correr scripts/generar_audio.py (o generar_short.py) antes de renderizar.");
  process.exit(1);
}
console.log(`Listo: ${timeline.segmentos.length} secciones de ${timeline.video} en remotion/public/.`);
if (timeline.formato === "short") {
  console.log(`Short: npx remotion render Short ../${timeline.video}/output.mp4`);
} else {
  console.log(`Video: npx remotion render Video ../${timeline.video}/output.mp4`);
  console.log(`Short: npx remotion render Short ../${timeline.video}/short-1.mp4 --props='{"bloque":1}'`);
}
