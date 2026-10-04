// Convierte un guion en texto plano (fácil de escribir a mano) al
// script.json que necesita el editor de Remotion. Conversión por reglas
// fijas, sin IA — siempre el mismo resultado para el mismo texto.
//
// Formato, una línea por renglón:
//   <id> | <texto> | <n_imagenes> [| flags]
//
// Flags (separados por coma, todos opcionales):
//   HOOK              corte seco + 0.15s de aire antes de la línea siguiente
//   COUNTER:5          (o 4,3,2,1,off) cambia el número en pantalla
//   FINAL             última línea: corta la música, sin SFX
//   RISER             dispara un riser + impacto antes del corte al panel
//                     (se usa junto con GRID, en la MISMA línea)
//   GRID:Título;Etiqueta1;Etiqueta2;Etiqueta3;Etiqueta4;Etiqueta5
//                     línea de presentación de la serie: la primera imagen
//                     de la línea es la grilla (zoom al primer panel), con
//                     título y hasta 5 etiquetas superpuestas
//   SILENCE:0.5       segundos de silencio antes de que arranque la voz
//                     de esta línea (además del aire normal de HOOK)
//   NOTIFICATION      sonido de notificación/vibración en la primera
//                     imagen de la línea (escenas donde el celular es
//                     protagonista)
//
// Las imágenes se numeran solas, en orden, sumando los <n_imagenes> de
// cada línea de arriba hacia abajo — tienen que coincidir con el orden en
// que se suben en la página.

function parseGuion({ slug, lang, voice, rate, prefix, texto }) {
  const errores = [];
  const lineasTexto = texto
    .split("\n")
    .map((l) => l.trim())
    .filter((l) => l && !l.startsWith("#"));

  if (!lineasTexto.length) {
    throw new Error("El guion está vacío.");
  }

  let cursorImagen = 1;
  const lines = [];

  lineasTexto.forEach((renglon, i) => {
    const partes = renglon.split("|").map((p) => p.trim());
    if (partes.length < 3) {
      errores.push(`Línea ${i + 1}: falta algún "|" (formato: id | texto | n_imagenes | flags)`);
      return;
    }
    const [idStr, texto, nImgStr, flagsStr] = partes;
    const id = Number(idStr);
    const nImg = Number(nImgStr);
    if (!Number.isInteger(id) || id < 1) {
      errores.push(`Línea ${i + 1}: el id "${idStr}" no es un número válido`);
      return;
    }
    if (!Number.isInteger(nImg) || nImg < 1) {
      errores.push(`Línea ${i + 1}: la cantidad de imágenes "${nImgStr}" no es un número válido`);
      return;
    }
    if (!texto) {
      errores.push(`Línea ${i + 1}: falta el texto de la voz`);
      return;
    }

    const flags = (flagsStr || "").split(",").map((f) => f.trim()).filter(Boolean);
    const linea = { id, text: texto, images: [] };

    const esGrid = flags.find((f) => f.startsWith("GRID:"));
    for (let k = 0; k < nImg; k++) {
      const n = cursorImagen++;
      if (esGrid && k === 0) {
        linea.images.push({ n, effect: { kind: "zoomToPoint", focus: [0.25, 0.22], scaleTo: 2.6 } });
      } else {
        linea.images.push({ n });
      }
    }

    if (flags.includes("HOOK")) linea.hook = true;
    if (flags.includes("RISER")) linea.riser = true;
    if (flags.includes("FINAL")) linea.final = true;

    const counterFlag = flags.find((f) => f.startsWith("COUNTER:"));
    if (counterFlag) linea.counter = counterFlag.split(":")[1];

    const silenceFlag = flags.find((f) => f.startsWith("SILENCE:"));
    if (silenceFlag) linea.silenceBefore = Number(silenceFlag.split(":")[1]);

    if (flags.includes("NOTIFICATION") && linea.images[0]) {
      linea.images[0].sfx = ["notification"];
    }

    if (esGrid) {
      const partesGrid = esGrid.slice("GRID:".length).split(";").map((p) => p.trim());
      const [titulo, ...etiquetas] = partesGrid;
      const posiciones = [
        [0.5, 0.055], [0.25, 0.345], [0.75, 0.345], [0.25, 0.61], [0.75, 0.61], [0.5, 0.865],
      ];
      linea.overlays = [{ text: titulo, x: posiciones[0][0], y: posiciones[0][1], style: "title", onlyFirstImage: true }];
      etiquetas.forEach((et, idx) => {
        const pos = posiciones[idx + 1];
        if (pos && et) linea.overlays.push({ text: et, x: pos[0], y: pos[1], style: "label", onlyFirstImage: true });
      });
    }

    lines.push(linea);
  });

  if (errores.length) {
    throw new Error(errores.join(" · "));
  }

  return {
    slug,
    lang,
    part: 1,
    voice,
    rate,
    imagePrefix: prefix,
    imageCount: cursorImagen - 1,
    lines,
  };
}

module.exports = { parseGuion };
