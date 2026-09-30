// Copia a remotion/public/ lo que usa la composición KaiP1LoveBombing:
// out/timeline.json, las 46 imágenes (a kai-p1-images/) y el audio
// concatenado. Uso: node scripts/prepararKaiP1.mjs ../content-kai/parte1-love-bombing
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const remotion = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const publico = path.join(remotion, "public");

const carpetaVideo = process.argv[2];
if (!carpetaVideo) {
  console.error("Uso: node scripts/prepararKaiP1.mjs ../content-kai/parte1-love-bombing");
  process.exit(1);
}
const carpeta = path.resolve(process.cwd(), carpetaVideo);

const rutaTimeline = path.join(carpeta, "out", "timeline.json");
if (!fs.existsSync(rutaTimeline)) {
  console.error(`Falta ${rutaTimeline}. Correr antes scripts/kai_p1_voz.py + scripts/kai_p1_timeline.py.`);
  process.exit(1);
}

fs.rmSync(publico, { recursive: true, force: true });
fs.mkdirSync(publico, { recursive: true });

// Otras composiciones del mismo bundle cargan Montserrat a nivel de
// módulo sin importar cuál composición se esté renderizando.
fs.cpSync(path.join(remotion, "fuentes"), path.join(publico, "fuentes"), { recursive: true });

const timeline = JSON.parse(fs.readFileSync(rutaTimeline, "utf-8"));
fs.copyFileSync(rutaTimeline, path.join(publico, "kai-p1-timeline.json"));

fs.mkdirSync(path.join(publico, "kai-p1-images"), { recursive: true });
const faltantes = [];
for (const linea of timeline.lineas) {
  for (const img of linea.imagenes) {
    const origen = path.join(carpeta, "images", img.archivo);
    const destino = path.join(publico, "kai-p1-images", img.archivo);
    if (!fs.existsSync(origen)) {
      faltantes.push(img.archivo);
      continue;
    }
    fs.copyFileSync(origen, destino);
  }
}

const origenAudio = path.join(carpeta, timeline.audio);
const destinoAudio = path.join(publico, timeline.audio);
fs.mkdirSync(path.dirname(destinoAudio), { recursive: true });
fs.copyFileSync(origenAudio, destinoAudio);

// Sonidos de la línea Kai (RULES.md, REGLA DE SONIDO): música de fondo +
// SFX puntuales, bajados por .github/workflows/descargar-sonidos-kai.yml.
// Si algún archivo todavía no se descargó, simplemente no se copia (la
// composición se entera por la ausencia del archivo en public/, ver Root.tsx).
const raiz = path.resolve(remotion, "..");
const copiarCarpetaDeSonido = (origenRel, destinoRel) => {
  const origen = path.join(raiz, origenRel);
  const copiados = [];
  if (!fs.existsSync(origen)) return copiados;
  fs.mkdirSync(path.join(publico, destinoRel), { recursive: true });
  for (const archivo of fs.readdirSync(origen)) {
    if (!archivo.endsWith(".mp3")) continue;
    fs.copyFileSync(path.join(origen, archivo), path.join(publico, destinoRel, archivo));
    copiados.push(archivo);
  }
  return copiados;
};
const sfxDisponibles = copiarCarpetaDeSonido("assets/sonido-kai", "sonido-kai");
const musicaDisponible = copiarCarpetaDeSonido("assets/musica-kai", "musica-kai");
fs.writeFileSync(
  path.join(publico, "kai-p1-sonidos.json"),
  JSON.stringify({ sfxDisponibles, musicaArchivo: musicaDisponible[0] ?? null }, null, 2),
);
if (!musicaDisponible.length) console.warn("Sin música de fondo todavía (assets/musica-kai vacío).");
if (sfxDisponibles.length < 5) console.warn(`Solo ${sfxDisponibles.length}/5 SFX de Kai disponibles.`);

if (faltantes.length) {
  console.warn(`Faltan ${faltantes.length} imágenes (van a verse negras):`);
  faltantes.forEach((f) => console.warn(`  - ${f}`));
} else {
  console.log(`Listo: ${timeline.lineas.length} líneas, audio y assets copiados a remotion/public/.`);
}
console.log("Preview: npx remotion studio (composición KaiP1LoveBombing)");
