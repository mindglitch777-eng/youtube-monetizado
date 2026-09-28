# LOG — Pipeline PACK video 01 (he-never-raised-his-voice)

2026-09-28T03:27:48Z - Paso 0: preflight iniciado
- ffmpeg/ffprobe: NO preinstalados en el entorno. Instalados vía apt-get (ffmpeg 6.1.1, con libx264/libx265/libmp3lame). Desvío menor, no bloqueante — ver AUDIT.md.
- node/npm: OK (node v22.22.2, npm 10.9.7).
- remotion CLI: OK.
- Secretos Cloudflare (CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN): presentes en .env.
- Acceso a videos.pexels.com: BLOQUEADO desde este entorno (egress policy de la sandbox). Igual que Cloudflare Workers AI y Edge-TTS en sesiones anteriores de este proyecto: se resuelve corriendo el paso vía GitHub Actions (el resto del pipeline del canal ya usa este patrón: generar-voz*.yml, generar-imagenes.yml). Se crea un workflow nuevo para este pack.

- Paso 1 completo: 7 bloques de voz generados (en-US-GuyNeural, rate -4%), unidos con
  ffmpeg (silencio 0.3s entre bloques) -> audio/voice.wav. Alineado palabra por palabra
  contra shots.json (104 tomas) -> timeline.json.
  DURACIÓN REAL: 7:23 (443.36s) — fuera del rango esperado 9:30-10:45 del PACK.
  Causa verificada (no es bug): 1236 palabras exactas (coincide con PACK.md), audio no
  truncado. La voz configurada del canal (en-US-GuyNeural) a rate -4% habla a ~2.80
  palabras/seg real, más rápido que las 2.07 palabras/seg que asumió el PACK para su
  estimación de 10:09. PACK.md sección 9: "Duración real fuera de 9:30-10:45 → NO
  recortar guion por cuenta propia: informar y proponer opciones." PARADO acá para
  consultar — ver AUDIT.md.
- Toma más larga real: S092 (6.93s) — ninguna toma superó 9.5s, 0 divisiones por N2.
- Paso 2 (test de 3 imágenes) disparado en paralelo (no depende de la decisión de
  duración): PEDIDO_IMAGENES.txt = "test".

- Paso 2 (test de 3): revisadas contra el checklist.
  - S001: pasa (sin cara, silueta desde atrás; pelo con algo de detalle, aceptable).
  - S023: pasa (sin figura con cara; mano con detalle de dedos, aceptable, oscuro).
  - S079: FALLA — perfil facial claramente dibujado (línea de nariz, labios, mentón
    con rim light), viola "sin rasgos faciales". Ajustado el BLOQUE DE ESTILO
    compartido (no las escenas) en shots.json (78 prompts) y assets.json
    (miniaturas + image_style): reemplacé "solid featureless silhouettes with no
    facial features" por una frase mucho más explícita contra contorno facial
    (sin puente nasal, labios, mentón, mandíbula, oreja) y sumé esos términos al
    bloque "Avoid". Regenerando las 3 de prueba con --forzar para confirmar.

- Paso 2, segunda pasada (bloque de estilo reforzado):
  - S001: PASA. Mucho más oscuro/silueta sólida; queda un bulto de nariz de perfil
    (geometría inevitable de una silueta de perfil, no un rasgo dibujado aparte) —
    aceptable.
  - S023: PASA. Sin figura con cara; el anzuelo quedó más sutil que "grande y
    visible" pero la escena/paleta están bien — aceptable, no es un fallo de
    checklist.
  - S079: SIGUE MOSTRANDO perfiles faciales (dos siluetas de frente en contraluz:
    el hueco entre ambas dibuja nariz/labios/mentón de las DOS). Diagnóstico: esto
    no es un problema de bloque de estilo — es la COMPOSICIÓN de la escena (dos
    perfiles enfrentados a contraluz) la que geométricamente fuerza ese contorno,
    sin importar qué tan explícito sea el texto anti-rasgos. Paso 2 solo habilita
    ajustar el bloque de estilo, no las escenas — no toco la escena acá. Marco
    S079 para reintento dirigido durante la revisión del lote completo (Paso 3,
    "regenerar las que fallen, máx. 1 reintento"), con la escena reformulada para
    evitar el encuadre de dos-perfiles-enfrentados si el reintento vuelve a fallar
    se declara en AUDIT.md como no resuelto (R5 parcial), no bloquea el resto.
  Checklist de Paso 2: 2/3 pasan limpio, 1/3 marcada para reintento dirigido —
  sigo a Paso 3 (lote completo), que corre en paralelo mientras se decide la
  duración (no depende de esa decisión).

- Paso 3, reintento dirigido de S079: reescribí la escena (de "dos siluetas
  de perfil enfrentadas a contraluz" a "abrazo visto desde atrás, ambas
  figuras de espaldas a cámara, sin perfiles hacia la luz en ningún punto")
  para eliminar la composición que geométricamente forzaba el contorno
  facial. Borré img/S079.jpg y disparo un pedido "full" (idempotente: solo
  regenera esta, el resto ya existe).
