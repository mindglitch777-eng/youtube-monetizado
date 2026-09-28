# PACK — Video 01 · "He Never Raised His Voice. She Lost Herself Anyway." (canal Knotwise)

> Para Claude Code. Este pack define UN video largo terminado y publicable. Todo lo de abajo es especificación, no sugerencia.
> **Regla de oro:** nada se omite en silencio. Si un requisito no se puede cumplir, se registra en `AUDIT.md` con la causa. Antes de decir "terminado" hay que completar `AUDIT.md` (sección 8).

## 1. Qué es y cifras clave
- Historia dramatizada (personajes ficticios compuestos: Maya y Daniel), narrada en inglés, sobre 5 movimientos de manipulación. Formato **horizontal 16:9, 1920×1080, 30 fps** (NO es un Short).
- Duración estimada: **10:09 (610 s)** (calculada con 2,07 palabras/seg; la real se mide con el audio y manda). Palabras: **1236**.
- Tomas: **104** = 78 imágenes IA + 8 clips de Pexels + 18 placas tipográficas. Toma más larga (estimada): 8.8 s.
- Capítulos (inicio estimado): HOOK 0:00 · C1 0:54 · C2 2:28 · C3 3:58 · C4 5:29 · C5 7:01 · C6 8:24.
- Reenganches (cada ~90 s): 2:21, 3:54, 5:21, 6:56, 8:16, 9:53. CTA de "like" a mitad: 3:41. "Primera grieta" (la ruptura de los hilos rojos): 8:43.
- Imágenes IA a generar: **80** (78 + 2 miniaturas) ≈ 7,680 neurons de ~10.000/día (cálculo previo: ~96 neurons por imagen a 8 pasos; verificar). Reserva para regenerar: ~24 imágenes.

## 2. Reglas innegociables
N1. Formato 1920×1080, 30 fps, H.264 + AAC. Video mudo renderizado en Remotion; audio mezclado aparte con ffmpeg y muxeado.
N2. **Nunca más de 10 s sin un cambio visual** (medido sobre el timeline real). Objetivo: cambio cada 3-8 s. Si con el audio real una toma supera 9,5 s → dividirla en dos con un cambio de encuadre (otro movimiento + flash corto). Reportar cuántas se dividieron.
N3. Las tomas están en `shots.json` y se anclan al TEXTO narrado (no a segundos). Los tiempos del JSON son solo estimaciones.
N4. Todas las figuras humanas son **siluetas sólidas sin rasgos**. Sin caras, sin personas reales, sin logos ni marcas, sin texto dentro de las imágenes.
N5. Imágenes IA solo las del manifiesto (+ máx. 24 regeneraciones). Si Cloudflare devuelve error de cuota: PARAR, guardar estado, informar y poder reanudar (idempotente: no regenerar lo que ya existe).
N6. No tocar `remotion/src/Short` ni `Video.tsx` de producción. Todo va en `remotion/src/longform/`.
N7. No correr `validar_guion.py` (este guion no tiene el formato de 6 bloques).
N8. No subir nada a YouTube. No commitear secretos. Commitear en una rama nueva.
N9. Subtítulos y placas nunca muestran la misma oración completa al mismo tiempo (bug de versiones anteriores).
N10. No dejar pantallas casi negras con solo subtítulos: las placas tienen fondo animado; las tomas IA/clip siempre tienen movimiento.

## 3. Contenido del pack
```
PACK.md            este archivo (instrucciones)
shots.json         las 104 tomas: narración, tipo, prompt completo, movimiento, transición, sfx, grade, overlays
guion.txt          narración por capítulo (para TTS)
assets.json        clips de Pexels (principal + respaldo), prompts de miniaturas, estilo, sfx, música
metadata.md        título, descripción, tags, comentario fijado, spec de miniatura
sfx/               8 efectos sintetizados (wav) listos para usar
music/             bed_dark.mp3 y bed_warm.mp3 (bases sintetizadas, placeholder)
```
Carpeta de trabajo: `content/2026-XX-XX-he-never-raised-his-voice/` (copiar el pack ahí). Crear `img/`, `clips/`, `audio/`, `out/`.

## 4. Pipeline (en este orden; escribir una línea por paso en `LOG.md`)

**Paso 0 — Preflight.** Verificar: ffmpeg/ffprobe, node + remotion, secretos de Cloudflare (`CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`), acceso a `videos.pexels.com` con `curl -I`. Si algo falta, informar y detenerse (no inventar).

**Paso 1 — Voz.** Leer `guion.txt` (bloques por capítulo). Sintetizar con Edge-TTS **por bloque** (7 bloques) usando la voz ya configurada del canal (si no hay: `en-US-AndrewNeural`, rate −4%). Capturar eventos `WordBoundary`. Unir bloques con 0,3 s de silencio → `audio/voice.wav`. Medir duración real con ffprobe y reportarla.
- Alineación: normalizar (minúsculas, solo alfanuméricos) y emparejar palabra por palabra en orden con el texto de cada toma. Si más del 2 % de palabras no matchea, sintetizar por toma (104 llamadas) y concatenar con 0,18 s de hueco.
- Salida: `timeline.json` con inicio/fin (segundos y frames a 30 fps) de cada toma. Inicio = primera palabra; fin = inicio de la siguiente; última toma termina 0,8 s tras la última palabra (cierre seco).
- Reportar: duración total, toma más larga, cuántas tomas > 9,5 s.

**Paso 2 — Prueba de imágenes (3).** Generar SOLO las 3 marcadas `test_batch` (S001, S023, S079) con Cloudflare `@cf/black-forest-labs/flux-1-schnell`, `steps: 8`, prompt = `ai.prompt` de cada toma (ya trae estilo + paleta + escena + negativo; no exceder 2048 caracteres). La respuesta trae la imagen en base64 → guardar como `img/S###.jpg`. La API devuelve 1024×1024 (ignora el tamaño pedido). **Mirar las 3 imágenes** y contrastar con el checklist: (a) sin texto/letras, (b) siluetas sin rasgos, (c) sujeto en la franja central, (d) paleta correcta. Si fallan, ajustar el bloque de estilo (no las escenas) y repetir (cuenta contra la reserva). Escribir en `LOG.md` qué se ajustó.

**Paso 3 — Lote de imágenes.** Generar el resto de las toma `type: ai` en orden de toma, con reintentos (3, backoff) ante 429/5xx/timeout y guardia de cuota (N5). Al final, las 2 miniaturas (`assets.json → thumbnails`). Cada 12 imágenes: armar una hoja de contactos y revisarla con el checklist; regenerar las que fallen (máx. 1 reintento c/u).

**Paso 4 — Clips.** Descargar los 8 clips de `assets.json → clips` con `curl -L` a `clips/A.mp4 … H.mp4` (si la URL falla, usar `backup`). `ffprobe` cada uno. Reglas de encaje: si el clip es más corto que la toma → loop con crossfade de 0,4 s (o reducir hasta 0,85× de velocidad); si es más largo → recortar desde t=0,5 s. Los de 720p se escalan a 1080p (llevan grano y viñeta, se nota poco). Generar `credits.txt` con autor y URL de cada clip usado.

**Paso 5 — Sonido.** Ver sección 6.

**Paso 6 — Remotion.** Ver sección 5. Copiar assets a `remotion/public/<slug>/`. Composición `LongForm` que lee `timeline.json` + `shots.json`.

**Paso 7 — Render.** `npx remotion render LongForm out/video_silent.mp4 --codec=h264 --crf=18`. Usar `OffthreadVideo` para clips. Si el entorno corta renders largos: renderizar por capítulos con `--frames=a-b` (mismos parámetros) y unir con `ffmpeg -f concat -c copy`.

**Paso 8 — Mezcla y muxeo.** Sección 6. Resultado: `out/video_final.mp4`.

**Paso 9 — QA + miniaturas + metadata.** Sección 7, más `out/thumbnail_A.png` y `out/thumbnail_B.png` (spec en `metadata.md`), `metadata.md` con tiempos reales de capítulos, y `AUDIT.md`.

## 5. Especificación Remotion (`remotion/src/longform/`)
**Imágenes IA (`ShotImage`).** Fuente 1024², escalada para cubrir 1920 de ancho (×1,875 → 1920×1920); la ventana visible es de 1080 px de alto (56 %). Movimientos (campo `motion`), duración = la de la toma + 0,4 s de solape, easing cúbico in-out:
- `push_in`: escala 1,00→1,12 · `pull_out`: 1,12→1,00 · `pan_up`: translateY +130→−130 px con escala 1,06 · `pan_down`: al revés · `push_in_left`/`push_in_right`: push_in con foco en x=0,38 / 0,62 · `pull_out_up`: pull_out con foco y 0,62→0,50. El recorrido vertical total no debe pasar de ±260 px.
- Nunca dos tomas seguidas con el mismo movimiento (ya viene alternado en el JSON; respetarlo).

**Clips (`ShotClip`).** `OffthreadVideo`, cover, silenciado, push_in lento 1,00→1,05, mismo grade + grano + viñeta que las imágenes.

**Placas (`Plate`)** — 18 en total, `plate.kind`: `title`, `note`, `chapter`, `concept`, `cta`, `list`, `question`, `end`.
- Tipografía: display serif (Playfair Display 800 o DM Serif Display) para los términos; Inter para subtítulos y etiquetas. Cargar con `@remotion/google-fonts`; si no hay red, fuentes del sistema como respaldo.
- Tamaños: término/título 130-160 px; `chapter`: "MOVE n" a 34 px con tracking 0,4 em en el color de acento + título a 128 px + número gigante "n" fantasma (≈520 px, 6 % de opacidad) detrás; `note` 64 px + sub 26 px; `list` 72 px, la línea nueva resaltada, `reveal_from` marca desde qué línea entran nuevas; `cta`/`question` 100-110 px; `end` 110 px + pastilla "SUBSCRIBE".
- Fondo (NUNCA negro plano): degradado #050505→#0d0d12 + 2-3 franjas de luz difusas y diagonales moviéndose ~40 px/s al 4-6 % + resplandor radial del color de acento al 18 % detrás del texto + grano.
- Entrada: palabras escalonadas 0,07 s con `spring` (damping 14, stiffness 120), blur 14→0 y translateY 28→0. Salida: fade de 6 frames. Durante la placa, push_in lento 1,00→1,04.
- Acentos: red #ff2d55 · blue #2d9bff · amber #ffb020.

**Overlay `pullquote` (12 tomas).** Cita entre comillas grandes (itálica serif, 72 px, centrada sobre la franja de subtítulos), entra con blur+resorte. **Los subtítulos se ocultan mientras la cita está visible** (`hide_captions_during`).

**Subtítulos (`Captions`).** Abajo al centro, Inter 700 a 46 px, blanco, sombra `0 3px 12px rgba(0,0,0,.85)`, máx. 2 líneas y ~7 palabras por frase, tiempos de las palabras del TTS, fade de 3 frames. Apagados donde `captions:false`. Nunca dentro de los 60 px inferiores.

**Hilo rojo (motivo recurrente, `RedThread`).** SVG en el borde inferior, trazo #ff2d55 de 3 px con glow. Cantidad de hilos = `thread.count` de cada toma (HOOK 0, C1 1 … C5 5). Cada hilo nuevo entra deslizándose en 0,6 s al iniciar su capítulo; cuanto más hilos, menos "caída" (sag) del trazo (amplitud ≈ 60 − 9·n px). En la toma con `thread.state: "snap"` (la primera grieta, ~8:43) los 5 hilos se cortan y retroceden en 10 frames con `hit_deep`; en el capítulo final no hay hilos. No se explica nunca con palabras: es el elemento visual que se resuelve solo.

**Global.** Viñeta `radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,.55) 100%)`. Grano: filtro SVG `feTurbulence` (baseFrequency 0,85, numOctaves 2, seed = floor(frame/2) % 24) al ~10 % con `mix-blend-mode: overlay` (NO generar un video de grano: pesa 20 MB). Grade por toma (`grade`): `cold-neon` contrast 1.10 + overlay rgba(20,60,255,.05) · `amber-warm` contrast 1.06 saturate 1.12 sepia .12 + rgba(255,170,60,.07) · `cool-blue` contrast 1.10 saturate .92 + rgba(40,110,255,.07) · `desat-cold` saturate .65 contrast 1.15 + rgba(60,90,140,.06) · `red-tint` contrast 1.10 + rgba(255,30,60,.08) · `warm-hope` brightness 1.03 saturate 1.10 + rgba(255,190,90,.08).

**Transiciones (`transition_in`).** `cut` (nada) · `flash` (8 frames, blanco cálido #fff5e0, opacidad 0→0,85→0) · `dip` (10 frames a negro; se usa al entrar a cada capítulo) · `glitch` (8 frames: 3 copias con desplazamiento RGB ±10 px + cortes horizontales). Los `sfx` de cada toma ya están en el JSON.

## 6. Sonido y mezcla (ffmpeg, determinista)
- **Voz:** `audio/voice.wav`. Objetivo: −16 LUFS antes de mezclar.
- **SFX:** cada toma trae `sfx: [{name, offset_s}]`; `offset_s` es relativo al inicio de la toma (el `riser` va con −2,5 s: suena justo antes de la placa de capítulo). Construir `audio/sfx_track.wav` con `adelay` + `amix=normalize=0`. Volúmenes: whoosh_a 0,55 · whoosh_b 0,60 · hit_deep 0,80 · hit_soft 0,50 · tick 0,35 · riser 0,50 · glitch 0,45 · sting_end 0,90.
- **Música:** `bed_dark.mp3` en bucle (crossfade de 2 s) desde el inicio hasta ~1,5 s antes de la "primera grieta"; luego crossfade a `bed_warm.mp3` hasta el final. Si el usuario dejó `music/tension.mp3` y `music/warm.mp3`, usar esos en su lugar. Nivel base −22 dB y **sidechain** contra la voz (`sidechaincompress` threshold 0.02, ratio 8, attack 20 ms, release 500 ms). Subida de +3 dB en los 2,5 s del riser.
- **Cierre seco:** el audio corta 0,35 s después de la última palabra, con `sting_end` en la placa final. Sin cola de música.
- **Master:** `loudnorm=I=-14:TP=-1.5:LRA=11` (dos pasadas). Muxear: `-c:v copy -c:a aac -b:a 192k`.

## 7. QA automático (`qa.py` → `out/qa_report.txt`)
1. Duración real y cuadro de tomas: máxima duración entre cambios visuales (debe ser ≤ 10 s).
2. `blackdetect=d=0.4:pic_th=0.98`: solo se admiten los `dip` (< 0,5 s). `freezedetect=n=-60dB:d=2`: no debe haber congelados > 2 s.
3. `ebur128`: integrado −14 ±1 LUFS, true peak ≤ −1 dB.
4. Hoja de contactos `out/contact_sheet.jpg` (un frame por toma, ~104) y frames al inicio de cada capítulo + 5 puntos de sincronía de subtítulos.
5. Mirar la hoja de contactos y anotar problemas visibles (texto en imágenes, caras, cortes raros, placas vacías).

## 8. Checklist de requisitos (copiar a `AUDIT.md` con estado y evidencia)
R1 1920×1080, 30 fps, H.264/AAC · R2 duración real reportada (rango esperado 9:30-10:45) · R3 ninguna toma > 10 s · R4 cantidad de tomas por tipo = manifiesto · R5 imágenes IA pasan el checklist (sin texto, siluetas sin rasgos, sujeto centrado) · R6 8 clips en sus tomas, con grade y `credits.txt` · R7 18 placas con entrada animada y fondo animado · R8 subtítulos por frase, sin solaparse con placas ni citas · R9 hilo rojo por capítulo + corte en la grieta · R10 movimiento en toda toma IA/clip, sin repetir consecutivos · R11 transiciones según JSON, `dip` entre capítulos · R12 grade por capítulo + grano + viñeta · R13 todos los SFX del JSON presentes y sin saturar · R14 música con ducking; cálida tras la grieta · R15 −14 LUFS ±1 / TP ≤ −1 dB · R16 6 reenganches + riser 2,5 s antes de cada capítulo · R17 CTA de like a mitad, CTA final, cierre seco · R18 nota de "personajes compuestos" presente + descripción con aviso · R19 2 miniaturas 1280×720 < 2 MB, ≤ 3 palabras · R20 salidas de QA generadas · R21 sin logos, marcas ni personas reales · R22 imágenes IA generadas ≤ 80 + 24 · R23 `timeline.json` desde audio real y 5 puntos de sincronía verificados · R24 `metadata.md` con tiempos reales · R25 `AUDIT.md` completo, con desvíos declarados · R26 rama nueva, sin secretos, y sección "long-form" añadida a `RULES.md` (apéndice B).

## 9. Si algo falla
- Cuota de Cloudflare agotada → parar, guardar estado, avisar cuántas imágenes faltan; se reanuda otro día.
- Imagen con texto o caras → 1 reintento con el bloque de estilo reforzado ("no text, no faces"); si sigue mal, marcar en `AUDIT.md`.
- Clip caído (403/404) → usar `backup`; si tampoco, reemplazar por una toma IA y declararlo.
- Render cortado → por capítulos (Paso 7).
- Duración real fuera de 9:30-10:45 → NO recortar guion por cuenta propia: informar y proponer opciones.

## 10. Entregables
`out/video_final.mp4` · `out/thumbnail_A.png` · `out/thumbnail_B.png` · `out/contact_sheet.jpg` · `out/qa_report.txt` · `AUDIT.md` · `credits.txt` · `metadata.md` (tiempos reales) · `timeline.json` · `LOG.md`. Al terminar: resumen de decisiones técnicas + `AUDIT.md`, sin declarar "listo" si algún R quedó incumplido.

---
## Apéndice A — Estilo de imagen (ya incluido en cada `ai.prompt`)
Ilustración tipo novela gráfica oscura, composición de fotograma 16:9 con el sujeto en la franja central, alto contraste, sombras duras, formas vectoriales planas con degradados pictóricos suaves, **siluetas sólidas sin rasgos**, sin texto. Paletas: `neon`, `amber-neon` (capítulo 1), `cold-blue`, `cold-desat` (capítulo 3), `red-dominant` (capítulo 4), `warm` (tramo final tras la grieta). La paleta cálida es exclusiva del cierre.

## Apéndice B — Reglas a agregar a `RULES.md` (sección "Long-form")
- Formato largo 16:9; cambio visual como máximo cada 10 s (objetivo 3-8 s).
- Reenganche (pregunta/promesa) cada 80-100 s; capítulos con placa y riser.
- Historias dramatizadas: siempre personajes compuestos + nota visible + aviso de contenido sintético al subir.
- Contenido sensible (abuso, manipulación): incluir recursos de ayuda y no glorificar ni dar instrucciones.
- No subir el ritmo de publicación a tasa "masiva": guion y edición propios en cada video (política de contenido inauténtico).
- Nada se omite en silencio: `AUDIT.md` obligatorio.
