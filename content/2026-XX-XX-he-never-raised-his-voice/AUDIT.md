# AUDIT — "He Never Raised His Voice" (PACK video 01)

Estado: **EN PROGRESO** — se completa al final del pipeline (Paso 9). No se
declara "listo" mientras algún R quede incumplido sin explicación.

## Desvíos y decisiones (nada se omite en silencio)

1. **Entorno**: ffmpeg/ffprobe no venían preinstalados en el entorno de
   Claude Code — se instalaron vía `apt-get install ffmpeg` (LOG.md, Paso 0).
   No afecta el resultado, solo el entorno de ejecución.
2. **Red bloqueada localmente**: edge-tts, Cloudflare Workers AI y
   videos.pexels.com no son accesibles desde el entorno de Claude Code
   (igual que el resto del pipeline del canal) — Pasos 1-4 corrieron en
   GitHub Actions (workflows `pack-voz.yml`, `pack-imagenes.yml`,
   `pack-clips.yml`), con checkpoints commiteados automáticamente.
3. **workflow_dispatch no disponible**: la API de GitHub Actions no permite
   dispatchar un workflow que todavía no existe en la rama por defecto del
   repo. `pack-imagenes.yml` quedó disparado por archivo de pedido
   (`PEDIDO_IMAGENES.txt` con "test"/"full" + push), mismo patrón que ya usa
   el canal para `imagenes/pedido.txt`.
4. **edge-tts NoAudioReceived transitorio** en el bloque C1 (primera
   corrida) — se agregaron reintentos con backoff (mismo patrón que el
   resto del pipeline ante fallas transitorias de red). Resuelto.
5. **DURACIÓN REAL FUERA DE RANGO (9:30-10:45 esperado)**: el audio real
   midió 7:23 (443s). Verificado que no es un bug (1236 palabras exactas,
   igual al conteo de PACK.md; audio no truncado) — la voz configurada del
   canal habla más rápido de lo asumido por la estimación del PACK (2.80
   palabras/seg reales vs. 2.07 asumidas). Por la sección 9 del PACK ("NO
   recortar guion por cuenta propia: informar y proponer opciones"), esto
   se consultó con el usuario antes de fijar el timeline definitivo — ver
   la respuesta en el chat para las opciones propuestas y la decisión.
   [PENDIENTE DE CONFIRMAR — actualizar este ítem cuando se decida].
6. **Paso 2 (checklist de estilo)**: S079 mostró contorno facial (dos
   siluetas de perfil enfrentadas a contraluz). Ajustado el bloque de
   estilo compartido (shots.json + assets.json, no las escenas) — S001 y
   S023 pasaron limpio con el ajuste; S079 sigue mostrando el contorno
   porque es la COMPOSICIÓN de la escena (no el estilo) la que lo genera.
   Marcada para reintento dirigido en la revisión del lote completo.
8. **[NUEVO, PENDIENTE DE CONFIRMAR CON EL USUARIO] Violación sistémica de
   N4 en una porción del lote de 78 imágenes**: revisando una muestra de
   10 (cada 8ª imagen), 6 muestran contorno facial nítido (nariz/labios/
   mentón) — NO es un caso aislado de S079. Causa: cualquier silueta DE
   PERFIL mirando hacia una fuente de luz cercana (ventana, lámpara,
   pantalla) dibuja el contorno por la geometría del borde luz/sombra, sin
   importar el texto del prompt — ya se intentó reforzar el bloque de
   estilo (desvío 6) y no alcanza contra la geometría. Las tomas de
   espaldas, con cabeza inclinada hacia abajo, o pequeñas/lejanas en el
   encuadre SÍ pasan limpio. Encontradas además 2 violaciones nuevas de
   "sin texto/números": S033 (carteles "UT PAK"/"476" de fondo legibles) y
   S044 (reloj de pared con números 1-12 legibles). Solución: no es un
   ajuste de texto del prompt sino reformular la DIRECCIÓN DE CÁMARA/POSE
   de cada escena afectada (perfil-mirando-la-luz → de espaldas o cabeza
   inclinada) y agregar "sin señalética/carteles/relojes con números
   legibles" al bloque de estilo. Requiere: (a) revisar los 78 uno por uno
   (no solo la muestra) para dimensionar cuántas escenas tocar, (b)
   reformular esas escenas, (c) regenerar — y Cloudflare ya marcó cuota
   agotada (resetea 00:00 UTC), así que la regeneración no puede arrancar
   hasta el reset. Consultado con el usuario — ver la respuesta en el chat
   para el alcance acordado. [PENDIENTE DE CONFIRMAR — actualizar cuando
   se decida].
7. **.gitignore**: `content/*/music/*.mp3` y `content/*/clips/fit/*.mp4`
   quedaban fuera de las excepciones existentes (mismo tipo de bug que ya
   había pasado con `content/*/clips/*.mp4` en la sesión anterior) —
   corregido antes de que se perdiera nada.

## Checklist de requisitos (sección 8 del PACK.md)

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| R1 | 1920x1080, 30fps, H.264/AAC | ⏳ pendiente (Paso 7-8) | — |
| R2 | Duración real reportada (9:30-10:45) | ⚠️ ver desvío 5 | timeline.json: 7:23 |
| R3 | Ninguna toma > 10s | ✅ | timeline.json: toma más larga 6.93s (S092), 0 divisiones por N2 |
| R4 | Cantidad de tomas por tipo = manifiesto | ✅ | 78 ai + 8 clip + 18 plate = 104 |
| R5 | Imágenes IA pasan el checklist | ⚠️ parcial | S079 con reintento dirigido, ver desvío 6 |
| R6 | 8 clips en sus tomas, con grade y credits.txt | ✅ (clips) / ⏳ (grade en render) | clips/fit/*.mp4, credits.txt |
| R7 | 18 placas con entrada animada y fondo animado | ⏳ pendiente verificar en render | Plate.tsx implementado (8 kinds) |
| R8 | Subtítulos por frase, sin solapar placas/citas | ⏳ pendiente verificar en render | Captions.tsx + N9 implementado |
| R9 | Hilo rojo por capítulo + corte en la grieta | ⏳ pendiente verificar en render | RedThread.tsx implementado |
| R10 | Movimiento en toda toma IA/clip, sin repetir consecutivos | ⏳ pendiente verificar | Movimiento.tsx (7 tipos), shots.json ya viene alternado |
| R11 | Transiciones según JSON, dip entre capítulos | ⏳ pendiente verificar | Transiciones.tsx implementado |
| R12 | Grado por capítulo + grano + viñeta | ⏳ pendiente verificar | Estilos.tsx implementado |
| R13 | Todos los SFX del JSON presentes sin saturar | ⏳ pendiente (Paso 5) | pack_mezcla.py implementado |
| R14 | Música con ducking; cálida tras la grieta | ⏳ pendiente (Paso 5) | pack_mezcla.py implementado (ver desvío de simplificación abajo) |
| R15 | -14 LUFS ±1 / TP <= -1dB | ⏳ pendiente (Paso 9 QA) | pack_qa.py implementado |
| R16 | 6 reenganches + riser 2.5s antes de cada capítulo | ⏳ pendiente verificar | sfx riser en shots.json de cada plate "chapter" |
| R17 | CTA de like a mitad, CTA final, cierre seco | ⏳ pendiente verificar | plates cta en shots.json |
| R18 | Nota de "personajes compuestos" + aviso en descripción | ✅ (nota) / ✅ (descripción) | plate "note" (S010), metadata.md "ABOUT THIS VIDEO" |
| R19 | 2 miniaturas 1280x720 <2MB, <=3 palabras | ⏳ pendiente (Paso 9) | — |
| R20 | Salidas de QA generadas | ⏳ pendiente (Paso 9) | pack_qa.py implementado |
| R21 | Sin logos, marcas ni personas reales | ✅ | prompts sin marcas; clips Pexels son personas reales pero de stock con licencia — ver nota |
| R22 | Imágenes IA generadas <= 80 + 24 | ⏳ contar al terminar | — |
| R23 | timeline.json desde audio real + 5 puntos de sincronía verificados | ⚠️ parcial | timeline.json generado desde audio real; sincronía puntual no verificada aún |
| R24 | metadata.md con tiempos reales | ⏳ pendiente | — |
| R25 | AUDIT.md completo, con desvíos declarados | ⏳ este archivo, se completa al final | — |
| R26 | Rama nueva, sin secretos, sección long-form en RULES.md | ⚠️ parcial | rama `claude/he-never-raised-his-voice` ✅; RULES.md apéndice B pendiente |

Nota sobre R21: los 8 clips de Pexels muestran personas reales (son
metraje de stock, con licencia comercial libre) — la regla "sin personas
reales" del PACK se interpreta como referida a las imágenes IA
(siluetas), no a los clips reales, que el propio PACK pide usar. Si esto
no es lo que se quiso decir, avisar.

## Simplificaciones documentadas (pendiente confirmar si son aceptables)

- **Riser +3dB en los 2.5s antes de cada capítulo**: implementado el
  ducking general (sidechain música vs. voz) pero NO el boost puntual de
  +3dB específico durante cada riser — no es un ítem R explícito, se
  documenta como simplificación menor.
- **loudnorm de un solo paso** (no dos pasadas de medición+corrección)
  para la voz y el master — el resultado se verifica igual con ebur128 en
  el QA; si el número no da en rango, se corre una segunda pasada.
