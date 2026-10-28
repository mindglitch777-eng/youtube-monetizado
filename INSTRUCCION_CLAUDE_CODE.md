# INSTRUCCIÓN PARA CLAUDE CODE: armar el video completo

Objetivo: producir (A) el video largo "Así morirías en la Edad de Piedra (la #1 NO es un animal)", 1920x1080, ~7:20, español, y (B) un Short vertical 1080x1920 de 60-90 s, usando las mismas imágenes. El objetivo es el RITMO MÁS VIRAL POSIBLE. Todo gratis: sin APIs de pago, sin servicios con cuenta.

Trabajá de punta a punta sin pedirme confirmaciones. Si algo falla, probá el plan B que se indica. Solo preguntame si falta algo imposible de resolver (por ejemplo, imágenes que no están). Yo estoy solo con el celular, así que NO me pidas renombrar archivos ni correr comandos.

## 0. Archivos de entrada (en la raíz del repo)

- `guion_v3.md`: guion con tiempos, líneas de voz y etiquetas. 🖼 = imagen de Flow (varias separadas por ‖ = cortes rápidos), 🎞 = tarjeta que se dibuja en Remotion, 🔊 = sonido.
- `manifest_imagenes.json`: 112 entradas en `imagenes` (id, file, tipo, block, quote, overlay, prompt). `quote` es la frase del guion donde va esa imagen. `montaje_gancho` es el montaje de 30 cortes de los primeros ~32 s. `estilo` y `personajes` describen el look.
- `imagenes/`: las imágenes que generé en Google Flow. **Los nombres de archivo NO son los del manifest** (nombres al azar, y pueden estar desordenadas, repetidas o faltar algunas). No las voy a renombrar.

## 1. Emparejar imágenes con prompts (paso crítico)

1. Listá `imagenes/` y calculá un hash para detectar duplicados exactos. **Las imágenes vienen VERTICALES (768x1376, 9:16)**, no 16:9. Hay dos tipos y hay que detectarlos automáticamente (analizá filas de color uniforme arriba y abajo):
   - **Tipo A, con franja ancha**: el dibujo ocupa una banda horizontal en el medio (~768x430) y el resto son bandas vacías de un color liso. Recortá esa banda y escalala a 1920x1080 (guardá `work/img16/NNN.png`). Si el recorte sale con baja resolución, aplicá un escalado suave (lanczos) y no lo muestres a más de 1,08x de zoom.
   - **Tipo B, vertical completa**: el dibujo ocupa todo el alto. Para el video LARGO ponelo en un cuadro 1920x1080 con la imagen entera centrada (alto completo, `contain`) sobre un fondo formado por la misma imagen ampliada y muy desenfocada (blur fuerte, oscurecida un 25 %), con zoom lento suave. Nunca recortes cabezas ni pies. Para el SHORT usalas tal cual (9:16 nativo) con `cover`.
   - En el Short, las imágenes tipo A se centran sobre fondo desenfocado igual que arriba pero al revés (banda ancha dentro de 1080x1920 con la imagen ampliada y desenfocada detrás).
   Guardá en `work/img_info.json` el tipo de cada una (A/B) y el cuadro recortado.
   Además hay imágenes con personajes que no son Pijama (067 niño explorador, 070 niño de pelo negro, 051 silueta con sombrero): usalas igual, no son un error.
2. Armá "hojas de contactos" (contact sheets) de 12 imágenes cada una con el número de archivo bien visible, y MIRÁ cada hoja con la herramienta de lectura de imágenes. Para cada imagen anotá una descripción corta (qué personaje, qué pasa, objetos, color).
3. Emparejá cada imagen con el `id` del manifest comparando su descripción con el campo `prompt` y `quote`. Pistas fijas:
   - 001, 002, 003 son hojas de personajes (Pijama, León, gérmenes): tres poses en fondo crema. No van en el video.
   - Pijama: hombre ~30, pelo castaño revuelto, pijama celeste con estrellas blancas, descalzo. León: dibujo de león con melena dorada. Gérmenes: bolitas verdes con pinchos y sonrisa maligna.
   - Algunas escenas tienen un León diminuto escondido (020, 038, 053, 062, 070, entre otras): sirve para el gag final "¿viste al león?".
4. Si dos imágenes cubren el mismo id, quedate con la más fiel al prompt y más limpia (sin texto ni letras raras, sin personajes deformados, mismo diseño de personaje que las hojas) y guardá la otra como `alt`.
5. Escribí `work/emparejado.json` (id → archivo, confianza alta/media/baja, alternativas) y `work/faltan.txt` con los ids sin imagen o con imagen mala.
6. Si faltan imágenes, NO te frenes: sustituí por la imagen más cercana del mismo bloque (o la reacción del bloque) y listalo en `faltan.txt`. Al final decime los ids que faltan para que los genere.
7. Copiá cada imagen emparejada a `assets/img/NNN_slug.png` con el nombre del manifest.

## 2. Voz (gratis, en español)

Ritmo: ~170 palabras/min, energético, con pausas cortas de 0.25-0.4 s entre frases y una pausa de 0.6 s antes de los golpes ("Es mentira.", "La número uno ni siquiera la ves.").

Orden de preferencia:
1. `edge-tts` (voces `es-AR-TomasNeural` o `es-MX-JorgeNeural`, rate `+8%`). Usá `--write-subtitles` para obtener los tiempos de palabras.
2. Si no hay red hacia ese servicio: Piper TTS con un modelo en español (por ejemplo `es_MX-claude-high` o `es_ES-davefx-medium`) descargado de Hugging Face. Verificá que se pueda.
3. Último recurso: `espeak-ng -v es+m3 -s 175`.

Procedimiento:
- Extraé del guion cada línea de voz (las líneas que no empiezan con 🖼 🎞 🔊 ni #). Generá un audio por línea en `work/voz/NNN.wav` y medí la duración real con ffprobe. Concatená con las pausas en `work/voz_completa.wav` y normalizá a -16 LUFS (loudnorm).
- **La duración real del audio manda**: el video se arma sobre los tiempos medidos, no sobre los tiempos del guion. Guardá `work/linea_tiempos.json` con inicio/fin de cada línea y de cada palabra (si el TTS no da tiempos de palabras, repartilos proporcionalmente por cantidad de letras).
- Si el total supera 7:40, subí la velocidad de a +3% hasta que entre en ~7:20-7:30.

## 3. Sonido y música (todo generado por código, sin descargas)

Generá con Python (numpy + scipy) y FFmpeg en `assets/sfx/`:
- `clic.wav`: clic metálico seco corto (candados). Siete clics seguidos con 0.12 s de separación para el gancho.
- `golpe_piedra.wav`: golpe grave con caída (tarjetas de número) y `golpe_fuerte.wav` más fuerte para el #1.
- `whoosh.wav`: barrido de ruido filtrado, 0.3 s (cortes de energía, transiciones).
- `latido.wav`: dos pulsos graves (gancho) y `acorde_asombro.wav`: acorde mayor sostenido 1.5 s con reverb.
- `bostezo.wav`: glide de tono con ruido filtrado (sirve cualquier aproximación cómica).
- `viento.wav`, `tictac.wav`, `vidrio_roto.wav` (reloj que se rompe), `pop.wav` (aparece texto), `ding.wav` (dato), `respiracion.wav`.
- Música: una base oscura de misterio (`musica_misterio.wav`, tonos graves + pulso suave, loop 60 s) y una más cálida para el cierre (`musica_calida.wav`). Volumen general -22 dB bajo la voz, con ducking (sidechain) cuando habla, y silencio total en: la línea "Es mentira.", el golpe del #1 y en "Casi todo eso lo resolvía tu grupo" (el efecto se corta y vuelve).
- Colocación según las etiquetas 🔊 del guion: clic al abrirse cada candado, golpe de piedra en cada tarjeta de número, viento en el #7, música de misterio en el #5 y el #1, "la música se corta" antes del #1, etc. Además: whoosh en los cortes de zoom grandes y `pop` cuando aparece un overlay de texto.

## 4. Edición en Remotion (proyecto `remotion/`)

Creá un proyecto Remotion (TypeScript) con una composición `Largo` (1920x1080, 30 fps) y otra `Short` (1080x1920, 30 fps). Un script `build_timeline.py` genera `work/timeline.json` desde guion + emparejado + tiempos de voz, y las composiciones solo leen ese JSON.

### Reglas de ritmo (basadas en el análisis del video más viral del nicho: 11,5 M de vistas)
- **Gancho (0:00 a ~0:32)**: usá `montaje_gancho` del manifest: 30 cortes de ~1,1 s, TODOS cortes duros, sin transición, sin texto salvo los overlays indicados (HACE 20.000 AÑOS, NO ES EL LEÓN). Cada corte con micro zoom in. Los 7 clics suenan seguidos en la imagen 014.
- **Resto del video**: promedio 3,8 s por imagen, rango 2-6 s (nunca más de 6 s sin cambiar de plano; si una frase es larga, repartila entre 2 o 3 imágenes del mismo bloque, o usá la `reaccion` del bloque). Si una frase tiene varias imágenes, repartirlas en orden cada 3-4 s.
- Cortes: 90% cortes duros. Fundidos (0,4 s) SOLO en: fade a negro hacia la tarjeta de número, y la tarjeta final.
- Cámara: 60% fija, 30% zoom in lento (1.0 → 1.08), 10% paneo lento. Nunca zoom out salvo en el cierre ("Pijama sentado en el grupo": zoom hacia atrás lento).
- Cada imagen entra con un golpe de vida sutil (escala 1.03 → 1.0 en 6 frames) para que no se sienta estática.
- Cutaways de reacción: las imágenes `tipo: reaccion` van de 1,0-1,5 s entre frases.
- Overlays (campo `overlay` del manifest): texto grande, blanco con borde negro grueso, fuente Impact/Anton o similar (instalar desde Google Fonts vía `@remotion/google-fonts`), entra con pop de 4 frames, en el tercio inferior (largo) o superior (Short).

### Subtítulos
- Quemados, palabra por palabra, en grandes (alto ~7% de la pantalla), amarillo `#FFE600` con borde negro grueso 8 px, máximo 3-4 palabras por línea, la palabra activa en blanco con escala 1.12. Centrados en tercio inferior (largo) o a media pantalla baja (Short, dentro de zona segura 9:16, sin tapar el 10% superior ni el 20% inferior).

### Tarjetas hechas en código (🎞)
1. **Tarjetas de número (7,6,5,4,3,2,1)**: fade a negro 0,4 s → tarjeta de piedra (fondo textura de piedra gris dibujada con SVG/CSS, número enorme tallado, con sombra) con zoom in lento 1,0 → 1,12 durante 1,6 s → `golpe_piedra` en el frame 0 de la tarjeta (el #1 con `golpe_fuerte` y música de misterio). Cada tarjeta lleva debajo el nombre del bloque en texto: SIN AGUA, GRANDES ANIMALES, LO QUE COMES, LA NOCHE, OTRAS PERSONAS, UN RASGUÑO, LOS GÉRMENES.
2. **Los 7 candados**: dibujados en SVG, con los mismos íconos que la imagen 014: gota de agua, ojo de león, fruto rojo, luna creciente con copo, lanza, espina, y el séptimo casi invisible (contorno punteado fantasma). Mostrarlos al inicio de cada bloque en un rincón (esquina superior izquierda, pequeños) para dar progreso: se abren con `clic` al final de cada bloque, con animación de arco que sube. En el bloque 7 de 7 los candados se abren todos con `acorde_asombro`.
3. **Reloj de 24 h**: reloj redondo con aguja roja que avanza hasta la hora indicada en cada candado (9:00, 12:00, 19:00, 22:00, 3:00, 7:00 del día siguiente), con tictac.
4. **Tarjetas de dato** (según el guion): 12 personitas donde 1 se pone gris (MENOS DE 1 DE CADA 12), 8 personitas con 1 gris al lado de la anterior (1 DE CADA 8), 10 personitas donde 7 se ponen verdes (7 DE 10). Entran con `ding` y las personitas se pintan una por una.
5. **Ranking final (el de verdad)**: fondo oscuro, 3 barras horizontales que crecen una por una, apto para captura de pantalla, basado en los datos del estudio de cazadores-recolectores de Gurven y Kaplan (2007, 3.328 muertes, todas las edades). Debe coincidir con lo que dice la voz ("Enfermedad: 7 de cada 10. Violencia: 1 de cada 8. Accidentes, con el león incluido: menos de 1 de cada 12"). Cifras exactas a mostrar, una barra por línea, apareciendo en sincronía con la voz:
   - ENFERMEDAD Y GÉRMENES: 7 DE CADA 10 (~70 %)
   - VIOLENCIA (otras personas): 1 DE CADA 8 (12,5 %)
   - ACCIDENTES, LEÓN INCLUIDO: MENOS DE 1 DE CADA 12 (8,1 %)
   Pie de la tarjeta, texto pequeño: "Gurven y Kaplan, 2007. Grupos de cazadores-recolectores recientes; no son datos de hace 20.000 años." No incluyas cifras que no estén aquí.
6. **Cierre**: collage de escenas con círculo rojo marcando el León escondido (usá las imágenes 020, 038, 053, 062, 070 y las que tengan el león diminuto; dibujá el círculo rojo animado), seguido de la imagen de WhatsApp (085) y pantalla final con "Suscríbete" y nombre del canal en blanco (texto sencillo, sin logo).

### Música y mezcla
- Voz a 0 dB, música a -22 dB con ducking, sfx a -8 dB. Mezclá todo en Remotion con `<Audio>` y `<Sequence>`, o preferentemente generá la mezcla de audio con FFmpeg (`work/mezcla.wav`) y usá un único `<Audio>` en Remotion para evitar desincronización.

## 5. El Short (60-90 s, 9:16)

Misma voz y mismas imágenes, sin recortes feos (usar `object-fit: cover` con el sujeto centrado; las imágenes ya vienen con el sujeto centrado). Estructura:
1. 0-3 s: gancho extremo, imagen del Pijama con los ojos abiertos + frase "Cierras los ojos y despiertas hace 20.000 años" (cortes de ~1 s).
2. 3-25 s: salto rápido por los 6 primeros candados (un clic por cada uno, 2-3 s por bloque, una imagen fuerte por bloque + el overlay con el nombre) sin explicar.
3. 25-50 s: la #1 (gérmenes): negro con gérmenes que aparecen, la ficha rota, el ranking de 3 barras.
4. 50-70 s: "¿Cuánto duras tú? Yo diría que unas 20 horas." + la imagen de los abuelos felices ("Eso de que moríamos a los 30 es mentira") + "Tu mejor arma era tu gente".
5. Cierre (últimos 5 s): "El video completo está en mi canal" con flecha hacia abajo y la miniatura del video largo (si existe `assets/miniatura.png`).
- Pausar al final con loop limpio: la última frase enlaza visualmente con el inicio para que se repita sin corte.
- Guardá `out/short.mp4` (H.264, 1080x1920, 30 fps, ≤ 90 s, AAC).

## 6. Render final

- `npx remotion render Largo out/largo.mp4 --codec=h264 --crf=18` y `out/short.mp4`.
- Con FFmpeg: normalizar audio final a -14 LUFS (YouTube), añadir 0,5 s de silencio al final, generar `out/largo_preview.mp4` en 720p para revisar rápido.
- Verificá el resultado: duración total, que no haya ningún plano de más de 6 s, que ningún subtítulo se salga del cuadro, que ningún audio se pise con otro, que haya silencio donde se pidió. Sacá 12 fotogramas al azar (con ffmpeg) y revisalos. Corregí lo que encuentres.
- Entregá: `out/largo.mp4`, `out/short.mp4`, `out/faltan.txt` (ids de imagen faltantes o malas), `out/mapa_imagenes.csv` (id, archivo original, archivo usado, confianza).

## 7. Reglas generales

- Idioma: todo el texto en pantalla y la voz en español.
- Sin música ni sonidos con copyright. Todo se sintetiza por código.
- No agregues datos ni cifras que no estén en el guion o en este documento.
- Si algo del guion contradice este documento, mandá este documento, salvo en las líneas de voz, que se leen tal cual.
- Al terminar, mostrame un resumen corto: duración de cada video, cuántas imágenes se usaron, cuáles faltaron, y qué voz se utilizó.
