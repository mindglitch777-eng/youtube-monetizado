# Cómo se renderiza (y qué aprendimos con el video 2)

## El proceso limpio (para el video 3 en adelante)

1. **Preparar en local** (rápido, sin render):
   - imágenes → `tools/preparar.py`
   - voz → `voz.py`
   - sonidos → `sonidos.py`
   - línea de tiempo → `timeline.py` y `shorts.py`
   
   Revisar 20 o 30 cuadros sueltos con `remotion/stills.mjs`: un solo empaquetado y cuadros en serie.
2. **Commit y push**.
3. **Render en GitHub Actions, nunca en el contenedor de Claude.** Hay que escribir algo en `videoN/render.txt` y hacer push. El workflow `render_video2.yml` reparte el largo en 10 tramos y los Shorts en un trabajo cada uno, todos en paralelo (≈ 5 minutos). Después une el largo con su audio y sube los mp4 a la rama `video2-render`.
4. **Bajar la rama** (`git fetch origin video2-render`), volver a armar los archivos partidos (`cat x.parte* > x`) y mandarlos.
5. **Si una parte falla**, se anota en `videoN/faltan.json` y se hace push. `render_video2_faltantes.yml` renderiza solo esas partes y vuelve a unir.

## Errores que ya pasaron y su solución permanente

| Problema | Causa | Solución que quedó |
|---|---|---|
| El render local se cortó a mitad de camino | El contenedor de Claude se reinicia solo cada tanto y tiene solo 4 núcleos (≈ 2,5 cuadros/s) | Todo render va a GitHub Actions, en paralelo. |
| `--concurrency=6` falló | El máximo es la cantidad de núcleos | En los workflows se usa `--concurrency=$(nproc)`. |
| 5 trabajos se colgaron 15+ minutos | `apt-get install ffmpeg` se trabó en los servidores de GitHub | ffmpeg sale de pip (`imageio-ffmpeg`), sin apt. Cada trabajo tiene un tope de 25 minutos. |
| Falló la mezcla con el ffmpeg de pip | Ese ffmpeg escribe más texto después del informe de volumen | `mezcla.py` busca el último bloque `{…}` con una expresión regular. |
| Falló la unión final | Le faltaba preparar las imágenes antes de armar la línea de tiempo | La unión usa el mismo `ci_prep.sh largo` que los demás pasos: un solo camino para preparar todo. |
| No se podían bajar los videos desde Claude | La red de Claude bloquea las descargas de artifacts de GitHub | El workflow sube los mp4 a una rama, partidos en trozos de 90 MB (límite de GitHub: 100 MB por archivo). |
| Cuadros sueltos lentísimos | `npx remotion still` vuelve a empaquetar todo en cada cuadro | `remotion/stills.mjs` empaqueta una vez y renderiza todos los cuadros. |
| Una cadena de comandos se cortó sin avisar | `script | head -1` mata el script por SIGPIPE y `&&` corta el resto | No usar `head` en medio de una cadena con `&&`. |
| Se usó una muerte sin imagen (pantalla negra larga) | La frase de la muerte no tenía imagen propia en el manifest | El armado lista las líneas sin imagen; se asignan a mano en `EXTRA`. |
