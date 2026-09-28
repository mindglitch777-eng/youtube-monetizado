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
