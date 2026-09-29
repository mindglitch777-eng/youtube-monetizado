// Copia a remotion/public/ lo que usa la composición KaiListicle:
// kai-shots.json, kai-timeline.json y las imágenes de cada punto (+ la del
// elemento recurrente, si hay). Las imágenes de Kai se generan a mano en
// Google Flow (no hay pipeline de IA acá) — este script solo las copia.
// Uso: node scripts/prepararKai.mjs ../content-kai/<carpeta-video>
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const remotion = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const publico = path.join(remotion, "public");

const carpetaVideo = process.argv[2];
if (!carpetaVideo) {
  console.error("Uso: node scripts/prepararKai.mjs ../content-kai/<carpeta-video>");
  process.exit(1);
}
const carpeta = path.resolve(process.cwd(), carpetaVideo);

const rutaShots = path.join(carpeta, "shots.json");
const rutaTimeline = path.join(carpeta, "kai-timeline.json");
if (!fs.existsSync(rutaShots) || !fs.existsSync(rutaTimeline)) {
  console.error(`Faltan shots.json o kai-timeline.json en ${carpeta}. Correr antes kai_voz.py + kai_timeline.py.`);
  process.exit(1);
}

fs.rmSync(publico, { recursive: true, force: true });
fs.mkdirSync(publico, { recursive: true });

// Otras composiciones del mismo bundle (Video/Short) cargan Montserrat a
// nivel de módulo (../Subtitulos.tsx) sin importar cuál composición se
// esté renderizando — hace falta que exista igual.
fs.cpSync(path.join(remotion, "fuentes"), path.join(publico, "fuentes"), { recursive: true });

const shots = JSON.parse(fs.readFileSync(rutaShots, "utf-8"));
fs.copyFileSync(rutaShots, path.join(publico, "kai-shots.json"));
fs.copyFileSync(rutaTimeline, path.join(publico, "kai-timeline.json"));

fs.mkdirSync(path.join(publico, "img"), { recursive: true });

const faltantes = [];
const copiar = (relativo) => {
  const origen = path.join(carpeta, relativo);
  if (!fs.existsSync(origen)) {
    faltantes.push(relativo);
    return;
  }
  const destino = path.join(publico, relativo);
  fs.mkdirSync(path.dirname(destino), { recursive: true });
  fs.copyFileSync(origen, destino);
};

for (const punto of shots.puntos) copiar(punto.imagen);
if (shots.elementoRecurrente) copiar(shots.elementoRecurrente.imagen);

if (faltantes.length) {
  console.warn(`Faltan ${faltantes.length} imágenes (van a verse negras):`);
  faltantes.forEach((f) => console.warn(`  - ${f}`));
} else {
  console.log(`Listo: ${shots.puntos.length} imágenes de punto + assets copiados a remotion/public/.`);
}
console.log("Preview: npx remotion studio (composición KaiListicle)");
