// Convierte un guion en texto plano (fácil de escribir a mano) al
// script.json que necesita el editor de Remotion. Conversión por reglas
// fijas, sin IA — siempre el mismo resultado para el mismo texto.
//
// Lo único obligatorio es el texto. Una línea de texto = una línea hablada:
//
//   Alguien te dice "alma gemela" a los tres días? Eso no es amor.
//   Estas son las cinco señales.
//   La número uno es la que te atrapa.
//
// La cantidad de imágenes de cada línea se calcula sola a partir de cuánto
// dura hablándola (ver calcularImagenesAuto). El prefijo de los archivos de
// imagen se calcula solo a partir del slug (<slug>-01.jpg, <slug>-02.jpg...).
//
// Si en algún momento se necesita control fino, se puede agregar, por
// línea, cantidad de imágenes y/o flags — pero nunca es obligatorio:
//
//   <texto>                             (lo normal: todo automático)
//   <texto> | <n_imagenes>              (fijar cuántas imágenes tiene esta línea)
//   <texto> | <n_imagenes> | <flags>    (control total; n_imagenes puede ir vacío = automático)
//
// Flags (separados por coma):
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
// Las imágenes se numeran solas, en orden, de arriba hacia abajo — tienen
// que coincidir con el orden en que se suben en la página.

const PALABRAS_POR_SEGUNDO = 2.3; // ritmo de habla conversacional, aprox.
const SEGUNDOS_POR_IMAGEN = 3.2; // cada cuánto conviene cambiar de imagen

function calcularImagenesAuto(texto) {
  const palabras = texto.split(/\s+/).filter(Boolean).length;
  const segundos = palabras / PALABRAS_POR_SEGUNDO;
  return Math.min(4, Math.max(1, Math.round(segundos / SEGUNDOS_POR_IMAGEN)));
}

function parseGuion({ slug, lang, voice, rate, texto }) {
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
    if (partes.length > 3) {
      errores.push(`Línea ${i + 1}: demasiados "|" (formato: texto [| n_imagenes] [| flags])`);
      return;
    }
    const lineaTexto = partes[0];
    if (!lineaTexto) {
      errores.push(`Línea ${i + 1}: falta el texto de la voz`);
      return;
    }

    // El segundo campo es n_imagenes solo si es un número; si no, son flags
    // directamente (para no obligar a escribir "| |" cuando no hace falta
    // fijar la cantidad de imágenes pero sí se quiere poner un flag).
    let nImgStr = "";
    let flagsStr = "";
    if (partes.length === 2) {
      if (/^\d+$/.test(partes[1])) nImgStr = partes[1];
      else flagsStr = partes[1];
    } else if (partes.length === 3) {
      nImgStr = partes[1];
      flagsStr = partes[2];
    }

    let nImg;
    if (nImgStr === "") {
      nImg = calcularImagenesAuto(lineaTexto);
    } else {
      nImg = Number(nImgStr);
      if (!Number.isInteger(nImg) || nImg < 1) {
        errores.push(`Línea ${i + 1}: la cantidad de imágenes "${nImgStr}" no es un número válido`);
        return;
      }
    }

    const flags = (flagsStr || "").split(",").map((f) => f.trim()).filter(Boolean);
    const linea = { id: i + 1, text: lineaTexto, images: [] };

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
    imagePrefix: `${slug}-`,
    imageCount: cursorImagen - 1,
    lines,
  };
}

module.exports = { parseGuion };
