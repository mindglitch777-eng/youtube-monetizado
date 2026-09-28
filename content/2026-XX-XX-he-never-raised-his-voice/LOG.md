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

- Paso 3, lote completo (80/80 generadas) + revisión de muestra (10/78,
  cada 8): PARADO ACÁ — ver AUDIT.md y la respuesta al usuario. Hallazgo:
  el problema de S079 (contorno facial nítido por geometría de
  contraluz-en-perfil) NO es un caso aislado. De 10 imágenes revisadas
  (S001,S013,S023,S033,S044,S055,S064,S074,S079,S080,S093), 6 muestran
  perfil facial claramente dibujado (nariz/labios/mentón) porque la
  silueta está de perfil MIRANDO hacia una fuente de luz cercana (ventana,
  lámpara, pantalla de celular) — el borde luz/sombra en esa geometría
  dibuja el contorno facial sin importar el texto del prompt. Las que SÍ
  pasan limpio son las que están de espaldas, con la cabeza inclinada
  hacia abajo, o lejos/pequeñas en el encuadre (S064, S093, S001). Además
  encontré 2 violaciones nuevas de "no texto/números": S033 (carteles de
  local "UT PAK" y "476" legibles de fondo) y S044 (reloj de pared con
  números 1-12 legibles). Por escala (~50-60% de la muestra), esto
  probablemente afecta a una porción grande de las 78 — no lo resuelvo
  reescribiendo el bloque de estilo una vez más (ya lo intenté con S079 y
  el texto no alcanza contra la geometría); hace falta reformular la
  DIRECCIÓN DE CÁMARA/POSE en cada escena afectada (de perfil-mirando-la-
  luz a de-espaldas o cabeza-inclinada) y volver a generar. Cloudflare
  además marcó cuota agotada en el intento de regenerar solo S079 (0
  generadas, resetea a las 00:00 UTC). Consulto con el usuario antes de
  decidir cuántas escenas reformular y disparar el lote de regeneración,
  porque afecta tiempo (hay que esperar el reset de cuota) y alcance
  (cuántas de las 78 tocar). Sigo mientras tanto con lo que no depende de
  esto: preparar Remotion, hacer stills de verificación con las imágenes
  que sí están bien, escribir metadata.md.

- Paso 3, reintento dirigido de S079: reescribí la escena (de "dos siluetas
  de perfil enfrentadas a contraluz" a "abrazo visto desde atrás, ambas
  figuras de espaldas a cámara, sin perfiles hacia la luz en ningún punto")
  para eliminar la composición que geométricamente forzaba el contorno
  facial. Borré img/S079.jpg y disparo un pedido "full" (idempotente: solo
  regenera esta, el resto ya existe).

- Decisión del usuario: duración real (7:23) aceptada tal cual, sin tocar
  el guion (metadata.md actualizado con tiempos reales de capítulo).
  "Dale mecha, pásame el video final" — sigo sin esperar el reset de
  cuota de Cloudflare (00:00 UTC, ~14h desde este punto). Para no dejar
  la toma S079 sin imagen, genero LOCALMENTE (sin red, con PIL) un
  placeholder de degradado (ámbar cálido + esquinas frías + acento rojo
  fino) que respeta la paleta "amber-neon" de la escena y no tiene
  ninguna figura humana — cero riesgo de N4. Marcado en AUDIT.md como
  gap conocido y visible, no oculto: la escena real (abrazo de espaldas)
  queda pendiente de generarse cuando resetee la cuota, y en ese momento
  se puede volver a renderizar solo esa toma sin tocar el resto.

- Miniaturas finales (Paso 9): THUMB_A.jpg pasa el checklist limpio (cabeza
  inclinada hacia abajo, sin contorno facial) y se usó tal cual como fondo
  de thumbnail_A.png. THUMB_B.jpg SÍ mostraba perfiles faciales nítidos de
  ambas figuras (mismo problema sistémico del desvío 8) — al ser la
  miniatura el asset más visible públicamente, no lo dejé así: generé
  LOCALMENTE (PIL, sin red, sin figuras) un fondo alternativo con el motivo
  del hilo rojo entrelazado, coherente con "HE NEVER YELLED". Compuse las
  2 miniaturas finales (scripts/pack_miniaturas.py, fuente Anton descargada
  de Google Fonts) con el texto de metadata.md: thumbnail_A.png ("ZERO
  BRUISES" + chip "5 MOVES") y thumbnail_B.png ("HE NEVER YELLED"). Ambas
  1280x720, bien por debajo de 2MB.

- Arreglo puntual pedido por el usuario (2 puntos):
  1) Reformulé las escenas de S002, S014, S028, S036 (mismo criterio que
     S079: de espaldas/cabeza inclinada/objeto solo, nunca perfil mirando
     la luz, sin carteles/calendarios/relojes/retratos con texto). Borré
     los 5 placeholders locales (S002,S014,S028,S036,S079) y disparo
     regeneración real con Cloudflare.
  2) BUG REAL encontrado y corregido: los subtítulos NO aparecían en el
     video exportado salvo en la toma S001. Causa: Captions.tsx compara
     el tiempo de reproducción contra `frame/fps` (tiempo ABSOLUTO de toda
     la composición, porque <Captions/> vive arriba de todos los
     Sequence, no adentro de uno) pero LongForm.tsx le pasaba las palabras
     ya convertidas a tiempo RELATIVO al inicio de cada toma
     (`palabrasLocal`). Coincidían por casualidad solo en S001 porque esa
     toma arranca en el frame 0 (relativo == absoluto ahí). Verificado con
     `remotion still --frame=1200` (toma S010, ~40s) ANTES (sin subtítulo)
     y DESPUÉS del fix (subtítulo correcto: "that therapists describe
     again and again", que coincide exacto con las palabras reales de esa
     toma en ese momento). Fix: Captions ahora recibe las palabras y el
     fin de toma en tiempo ABSOLUTO (activa.palabras, activa.endS)
     directamente desde timeline.json, sin la conversión intermedia.
