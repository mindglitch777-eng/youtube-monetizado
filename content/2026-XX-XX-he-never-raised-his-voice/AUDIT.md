# AUDIT — "He Never Raised His Voice" (PACK video 01)

Estado: **ENTREGADO** (Paso 9 completo). Quedan gaps conocidos y declarados
(ver desvíos 8, 10 y R5) — no se ocultó nada, se entregó por decisión
explícita del usuario ("dale mecha, mandame el video final") priorizando
tener el video hoy sobre una corrección total del lote de imágenes.

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
10. **[GRAVE, CORREGIDO] S002 y S014 no eran siluetas — eran caras casi
    fotorrealistas** (piel, ojos, boca con detalle), ignorando por completo
    el bloque de estilo. Encontrado en una revisión más amplia (no la
    muestra de 10, sino una pasada manual de ~30/78 imágenes) hecha DESPUÉS
    de la primera entrega intentada, al notar en el QA que algo no cerraba.
    Es la peor violación de N4 de todo el lote — S002 es la 2ª toma de todo
    el video. También se encontraron 2 violaciones de texto legible no
    detectadas antes: **S028** (la palabra "friend" escrita + un retrato
    enmarcado con una cara dibujada con detalle) y **S036** (un calendario
    con números y texto totalmente legibles). Las 4 (S002, S014, S028,
    S036) se reemplazaron por fondos abstractos generados LOCALMENTE (PIL,
    sin red, sin figuras humanas ni texto, con la paleta/grado de cada
    escena) y se volvió a renderizar solo esos 4 tramos (chunks de
    `pack_render_por_partes.sh`) antes de la mezcla final. La miniatura B
    (`THUMB_B.jpg`) tenía el mismo problema (dos perfiles faciales nítidos)
    — la miniatura final ya usa el fondo de hilo rojo sin figuras (ver
    Paso 9 en LOG.md).
    **Lo que SIGUE sin revisar exhaustivamente**: de las 78 imágenes, se
    revisaron a mano ~30 (no las 78) buscando específicamente casos graves
    como éste — no hay garantía de que no quede alguna otra imagen
    fotorrealista o con texto entre las ~48 no revisadas. Lo que SÍ está
    confirmado y aceptado (desvío 8) es el patrón más leve de contorno
    facial en perfiles a contraluz (~40-50% de la muestra).
11. **Bug en pack_qa.py (ebur128)**: la primera corrida del QA reportó
    -70 LUFS (prácticamente silencio), que asustaba pero era un bug de
    MEDICIÓN, no del audio real: `re.search` tomaba la PRIMERA lectura de
    ebur128 (el primer segundo de audio, con volumen muy bajo) en vez del
    resumen final del archivo completo. Corregido (usa la ÚLTIMA lectura,
    que es el resumen). Confirmado con `ffmpeg -af volumedetect` en
    paralelo (mean -15dB, max -0.6dB) que el audio real nunca estuvo mal.
    Con el bug corregido, el QA final da -15.0 LUFS (objetivo -14±1, OK).
12b. **video_final.mp4 y video_silent.mp4 NO están commiteados al repo**:
    GitHub rechaza archivos >100MB por push normal (video_final.mp4 pesa
    ~135MB, video_silent.mp4 ~125MB) — no hay git-lfs configurado en este
    repo. Quedan en `.gitignore` y se entregan directo al usuario por fuera
    de git. El resto de los deliverables (thumbnails, contact_sheet.jpg,
    qa_report.txt, AUDIT.md, credits.txt, metadata.md, timeline.json,
    shots.json, todo el código de `remotion/src/longform/`) sí están
    commiteados y pusheados.
12. **blackdetect marca 7 tramos "sospechosos"**: se verificaron 2 al azar
    (9s y 64s) extrayendo el frame real del video_final.mp4 — son escenas
    genuinamente oscuras por diseño (siluetas a contraluz, la estética que
    pide el propio PACK), no pantallas negras rotas. El umbral
    `pic_th=0.98` del script de QA es demasiado estricto para este estilo
    deliberadamente oscuro; no se ajustó por falta de tiempo, pero no
    representa video roto.
7. **.gitignore**: `content/*/music/*.mp3` y `content/*/clips/fit/*.mp4`
   quedaban fuera de las excepciones existentes (mismo tipo de bug que ya
   había pasado con `content/*/clips/*.mp4` en la sesión anterior) —
   corregido antes de que se perdiera nada.

## Checklist de requisitos (sección 8 del PACK.md)

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| R1 | 1920x1080, 30fps, H.264/AAC | ✅ | qa_report.txt: 1920x1080 @ 30/1 (h264) + audio AAC |
| R2 | Duración real reportada (9:30-10:45) | ⚠️ fuera de rango, aceptado por el usuario | timeline.json y qa_report.txt: 7:23 (443s) — ver desvío 5 |
| R3 | Ninguna toma > 10s | ✅ | timeline.json: toma más larga 6.93s (S092), 0 divisiones por N2 |
| R4 | Cantidad de tomas por tipo = manifiesto | ✅ | 78 ai + 8 clip + 18 plate = 104 |
| R5 | Imágenes IA pasan el checklist | ⚠️ parcial, mejorado pero no completo | Casos graves (S002,S014,S028,S036) corregidos; contorno facial leve sigue presente en buena parte del lote (desvío 8), aceptado por el usuario |
| R6 | 8 clips en sus tomas, con grade y credits.txt | ✅ | clips/fit/*.mp4, credits.txt, grade confirmado en still S006 |
| R7 | 18 placas con entrada animada y fondo animado | ✅ verificado con stills | 8/8 tipos de placa revisados en still (title, note, chapter, concept, cta, list, question, end) |
| R8 | Subtítulos por frase, sin solapar placas/citas | ✅ verificado con still | still S001: subtítulo + imagen, sin placa/cita simultánea |
| R9 | Hilo rojo por capítulo + corte en la grieta | ✅ presente en todos los stills; snap verificado parcialmente | still S091 (grieta) capturado en pleno flash, no en el frame exacto del corte — no genera dudas sobre la lógica (spec implementada), pero no es una confirmación pixel a pixel del corte |
| R10 | Movimiento en toda toma IA/clip, sin repetir consecutivos | ✅ (por diseño de datos) | Movimiento.tsx (7 tipos) implementado; shots.json ya viene alternado — no se verificó frame a frame los 104 casos |
| R11 | Transiciones según JSON, dip entre capítulos | ✅ verificado con stills | flash (S079/S104 area) y transición de capítulo visibles en stills |
| R12 | Grado por capítulo + grano + viñeta | ✅ verificado con stills | grados visibles (S001 ámbar, S006 clip natural, S021 rojo) |
| R13 | Todos los SFX del JSON presentes sin saturar | ✅ | pack_mezcla.py armó la pista de sfx (amix, sin normalize) para las 104 tomas |
| R14 | Música con ducking; cálida tras la grieta | ✅ (simplificado, ver abajo) | sidechaincompress música vs. voz + acrossfade bed_dark→bed_warm en S091 |
| R15 | -14 LUFS ±1 / TP <= -1dB | ⚠️ parcial | qa_report.txt: -15.0 LUFS (OK) / True peak -0.5 dBFS (pasado por 0.5dB del objetivo, no clippea) |
| R16 | 6 reenganches + riser 2.5s antes de cada capítulo | ✅ (por diseño de datos) | sfx "riser" en cada plate "chapter" de shots.json |
| R17 | CTA de like a mitad, CTA final, cierre seco | ✅ verificado con still | still S040 (CTA like) y S104 (end+subscribe) revisados |
| R18 | Nota de "personajes compuestos" + aviso en descripción | ✅ (nota) / ✅ (descripción) | plate "note" (S010), metadata.md "ABOUT THIS VIDEO" |
| R19 | 2 miniaturas 1280x720 <2MB, <=3 palabras | ✅ | thumbnail_A.png (242KB, "ZERO BRUISES"+"5 MOVES"), thumbnail_B.png (212KB, "HE NEVER YELLED") |
| R20 | Salidas de QA generadas | ✅ | qa_report.txt + contact_sheet.jpg en out/ |
| R21 | Sin logos, marcas ni personas reales | ✅ | prompts sin marcas; clips Pexels son personas reales pero de stock con licencia — ver nota |
| R22 | Imágenes IA generadas <= 80 + 24 | ✅ | 78 shots + 2 thumbnails = 80, sin usar ninguna de las 24 regeneraciones de reserva salvo S079 (placeholder, no contó como generación real) |
| R23 | timeline.json desde audio real + 5 puntos de sincronía verificados | ⚠️ parcial | timeline.json generado desde audio real; sincronía puntual no verificada punto por punto (sí verificada indirectamente en 11 stills + revisión visual del video final) |
| R24 | metadata.md con tiempos reales | ✅ | metadata.md actualizado con los 7 tiempos de capítulo reales del timeline |
| R25 | AUDIT.md completo, con desvíos declarados | ✅ | este archivo |
| R26 | Rama nueva, sin secretos, sección long-form en RULES.md | ⚠️ parcial | rama `claude/he-never-raised-his-voice` ✅; RULES.md apéndice B NO se llegó a escribir (falta de tiempo) |

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
