# Remotion — ensamblado del video

Arma el video final con las imágenes, la narración, los subtítulos, los
sonidos de marca y el ícono de Knot, a partir de `content/<video>/timeline.json`
(lo genera `scripts/generar_audio.py`).

```bash
npm install                                    # una sola vez
npm run preparar -- ../content/<nombre-video>  # copia todo a public/
npm run studio                                 # vista previa en el navegador
npx remotion render Video ../content/<nombre-video>/output.mp4
# shorts: uno por bloque (1 a 6)
npx remotion render Short ../content/<nombre-video>/short-1.mp4 --props='{"bloque":1}'
```

El render se hace a mano (no corre en GitHub Actions).

- `Video`: 1920×1080, 30 fps. La duración sale del timeline.
- `Short`: 1080×1920 (9:16), un bloque del video largo con las mismas imágenes
  recortadas al centro, sin generar imágenes nuevas. Deja afuera el CTA y
  cierra con el sting al terminar el Pago. Si el bloque dura 180 s o más, el
  render se detiene con un error (RULES.md, sección Shorts).
- Subtítulos: franjas de máximo 5 palabras, Montserrat 900 blanca con contorno
  oscuro, en el tercio superior-medio. La palabra en **negrita** de cada
  sección con `<!-- sonido: ding -->` se resalta en amarillo con un leve salto.
- Sonidos: whoosh antes de cada bloque nuevo, click entre ejemplos, ding en la palabra
  resaltada y sting al final del CTA (archivos de `assets/sonido/`).
- La fuente (`fuentes/Montserrat.woff2`, licencia SIL Open Font License) está
  en el repo para que el render no dependa de internet.
