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
   recortar guion por cuenta propia: informar y proponer opciones"), se
   consultó con el usuario antes de fijar el timeline definitivo.
   **DECIDIDO por el usuario: aceptar 7:23 tal cual, sin tocar el guion.**
   `metadata.md` ya tiene los tiempos de capítulo reales.
6. **Paso 2 (checklist de estilo)**: S079 mostró contorno facial (dos
   siluetas de perfil enfrentadas a contraluz). Ajustado el bloque de
   estilo compartido (shots.json + assets.json, no las escenas) — S001 y
   S023 pasaron limpio con el ajuste; S079 sigue mostrando el contorno
   porque es la COMPOSICIÓN de la escena (no el estilo) la que lo genera.
   Marcada para reintento dirigido en la revisión del lote completo.
8. **Violación sistémica de N4 en una porción del lote de 78 imágenes**:
   revisando una muestra de 10 (cada 8ª imagen), 6 muestran contorno
   facial nítido (nariz/labios/mentón) — NO es un caso aislado de S079.
   Causa: cualquier silueta DE PERFIL mirando hacia una fuente de luz
   cercana (ventana, lámpara, pantalla) dibuja el contorno por la
   geometría del borde luz/sombra, sin importar el texto del prompt — ya
   se intentó reforzar el bloque de estilo (desvío 6) y no alcanza contra
   la geometría. Las tomas de espaldas, con cabeza inclinada hacia abajo,
   o pequeñas/lejanas en el encuadre SÍ pasan limpio. Encontradas además 2
   violaciones de "sin texto/números": S033 (carteles "UT PAK"/"476" de
   fondo legibles) y S044 (reloj de pared con números 1-12 legibles).
   **DECIDIDO por el usuario: entregar el video ahora ("dale mecha") sin
   esperar el reset de cuota de Cloudflare (00:00 UTC) para corregir esto**
   — priorizó tener el video completo hoy sobre la corrección total de
   este hallazgo. Este video, tal como se entrega, TIENE estas
   imágenes sin corregir (no es una lista completa: solo se revisó una
   muestra de 10/78 antes de la decisión de entregar; el resto no se
   auditó imagen por imagen). Si se quiere corregir después: reformular la
   escena (perfil-mirando-la-luz → de espaldas/cabeza inclinada) de cada
   toma afectada + agregar "sin señalética/relojes con números legibles"
   al bloque de estilo, y regenerar solo esas tomas cuando la cuota de
   Cloudflare resetee — no hace falta rehacer el video entero, alcanza con
   reemplazar esas imágenes y volver a renderizar (Remotion no cachea).
9. **S079: sin imagen real** — Cloudflare agotó la cuota antes de poder
   generar la escena reformulada (abrazo de espaldas). Para no dejar la
   toma en negro, se generó LOCALMENTE (sin red, con PIL, sin ninguna
   figura humana) un fondo de degradado ámbar/frío que respeta la paleta
   de la escena. Es un placeholder visible, no una imagen del pack real.
   Reemplazar cuando la cuota permita generar la escena real.
7. **.gitignore**: `content/*/music/*.mp3` y `content/*/clips/fit/*.mp4`
   quedaban fuera de las excepciones existentes (mismo tipo de bug que ya
   había pasado con `content/*/clips/*.mp4` en la sesión anterior) —
   corregido antes de que se perdiera nada.

## Checklist de requisitos (sección 8 del PACK.md)

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| R1 | 1920x1080, 30fps, H.264/AAC | ⏳ verificar en video_final.mp4 (Paso 9) | render en curso a 1920x1080@30 |
| R2 | Duración real reportada (9:30-10:45) | ⚠️ fuera de rango, aceptado por el usuario | timeline.json: 7:23 — ver desvío 5 |
| R3 | Ninguna toma > 10s | ✅ | timeline.json: toma más larga 6.93s (S092), 0 divisiones por N2 |
| R4 | Cantidad de tomas por tipo = manifiesto | ✅ | 78 ai + 8 clip + 18 plate = 104 |
| R5 | Imágenes IA pasan el checklist | ❌ no cumplido en esta entrega | ~50-60% de fallo estimado en una muestra de 10/78 — ver desvío 8, aceptado por el usuario para entregar hoy |
| R6 | 8 clips en sus tomas, con grade y credits.txt | ✅ | clips/fit/*.mp4, credits.txt, grade confirmado en still S006 |
| R7 | 18 placas con entrada animada y fondo animado | ✅ verificado con stills | 8/8 tipos de placa revisados en still (title, note, chapter, concept, cta, list, question, end) |
| R8 | Subtítulos por frase, sin solapar placas/citas | ✅ verificado con still | still S001: subtítulo + imagen, sin placa/cita simultánea |
| R9 | Hilo rojo por capítulo + corte en la grieta | ✅ presente en todos los stills; snap verificado parcialmente | still S091 (grieta) capturado en pleno flash, no en el frame exacto del corte — no genera dudas sobre la lógica (spec implementada), pero no es una confirmación pixel a pixel del corte |
| R10 | Movimiento en toda toma IA/clip, sin repetir consecutivos | ✅ (por diseño de datos) | Movimiento.tsx (7 tipos) implementado; shots.json ya viene alternado — no se verificó frame a frame los 104 casos |
| R11 | Transiciones según JSON, dip entre capítulos | ✅ verificado con stills | flash (S079/S104 area) y transición de capítulo visibles en stills |
| R12 | Grado por capítulo + grano + viñeta | ✅ verificado con stills | grados visibles (S001 ámbar, S006 clip natural, S021 rojo) |
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
| R24 | metadata.md con tiempos reales | ✅ | metadata.md actualizado con los 7 tiempos de capítulo reales del timeline |
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
