// Copia a remotion/public/ lo que usa un short "standalone-animado" (sin
// imágenes IA: tipografía cinética + íconos SVG + clips reales — ver
// scripts/generar_voz_standalone.py). A diferencia de preparar.mjs (pipeline
// de imágenes), acá no hay timeline.segmentos[].imagen/sonidos: los sonidos y
// clips están fijos por convención, no en el timeline.
//
// Uso: npm run preparar:standalone -- ../content/<nombre-short>
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const remotion = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const raiz = path.resolve(remotion, "..");
const publico = path.join(remotion, "public");

const carpetaVideo = process.argv[2];
if (!carpetaVideo) {
  console.error("Uso: npm run preparar:standalone -- ../content/<nombre-short>");
  process.exit(1);
}
const rutaTimeline = path.resolve(process.cwd(), carpetaVideo, "timeline.json");
if (!fs.existsSync(rutaTimeline)) {
  console.error(`No existe ${rutaTimeline}. Correr antes scripts/generar_voz_standalone.py.`);
  process.exit(1);
}
const timeline = JSON.parse(fs.readFileSync(rutaTimeline, "utf-8"));
const carpetaVideoAbs = path.resolve(process.cwd(), carpetaVideo);

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

if (!copiar(timeline.audio)) faltantes.push(timeline.audio);

// Sonidos fijos de este tipo de short (ver RULES.md, excepción de tono
// oscuro/tenso): whoosh de marca + golpe/sting nuevos (o su fallback) +
// música de fondo a bajo volumen como bajo de tensión.
for (const s of ["assets/sonido/transicion.mp3", "assets/sonido/impacto.mp3",
                  "assets/sonido/cierre-duro.mp3", "assets/musica/fondo.mp3"]) {
  if (!copiar(s)) faltantes.push(s);
}

// Clips reales: todo lo que haya en la carpeta clips/ del video (menos el
// pedido.tsv y creditos.md, que no son media).
const carpetaClips = path.join(carpetaVideoAbs, "clips");
if (fs.existsSync(carpetaClips)) {
  for (const archivo of fs.readdirSync(carpetaClips)) {
    if (archivo.endsWith(".mp4")) {
      const relativo = path.relative(raiz, path.join(carpetaClips, archivo));
      if (!copiar(relativo)) faltantes.push(relativo);
    }
  }
}

fs.writeFileSync(path.join(publico, "timeline.json"), JSON.stringify(timeline, null, 2));

const unicos = [...new Set(faltantes)];
if (unicos.length) {
  console.warn(`Faltan ${unicos.length} archivos:`);
  unicos.forEach((f) => console.warn(`  - ${f}`));
}
console.log(`Listo: ${timeline.segmentos.length} líneas de ${timeline.video} en remotion/public/.`);
