# LOG — Pipeline PACK video 01 (he-never-raised-his-voice)

2026-09-28T03:27:48Z - Paso 0: preflight iniciado
- ffmpeg/ffprobe: NO preinstalados en el entorno. Instalados vía apt-get (ffmpeg 6.1.1, con libx264/libx265/libmp3lame). Desvío menor, no bloqueante — ver AUDIT.md.
- node/npm: OK (node v22.22.2, npm 10.9.7).
- remotion CLI: OK.
- Secretos Cloudflare (CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN): presentes en .env.
- Acceso a videos.pexels.com: BLOQUEADO desde este entorno (egress policy de la sandbox). Igual que Cloudflare Workers AI y Edge-TTS en sesiones anteriores de este proyecto: se resuelve corriendo el paso vía GitHub Actions (el resto del pipeline del canal ya usa este patrón: generar-voz*.yml, generar-imagenes.yml). Se crea un workflow nuevo para este pack.
