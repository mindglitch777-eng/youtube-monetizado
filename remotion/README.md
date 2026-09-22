# Remotion — ensamblado del video

Arma el video final con las imágenes, la narración, los subtítulos, los
sonidos de marca y el ícono de Knot, a partir de `content/<video>/timeline.json`
(lo genera `scripts/generar_audio.py`).

```bash
npm install                                    # una sola vez
npm run preparar -- ../content/<nombre-video>  # copia todo a public/
npm run studio                                 # vista previa en el navegador
npx remotion render Video ../content/<nombre-video>/output.mp4
```

- 1920×1080, 30 fps. La duración sale del timeline.
- Subtítulos: franjas de máximo 5 palabras, Montserrat 900 blanca con contorno
  oscuro, en el tercio superior-medio. La palabra en **negrita** de cada
  sección con `<!-- sonido: ding -->` se resalta en amarillo con un leve salto.
- Sonidos: whoosh en cada transición, click entre ejemplos, ding en la palabra
  resaltada y sting al final del CTA (archivos de `assets/sonido/`).
- La fuente (`fuentes/Montserrat.woff2`, licencia SIL Open Font License) está
  en el repo para que el render no dependa de internet.
