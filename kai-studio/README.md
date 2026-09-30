# kai-studio

Kit para producir los Shorts de Kai (canal EN y canal ES): organizador de imágenes, voz con tiempos por palabra y proyecto Remotion completo.
Las reglas están en **RULES.md** (pegalo en el CLAUDE.md de Claude Code).

## Instalación (una vez)
```bash
npm install
pip install edge-tts pillow        # ffmpeg/ffprobe tiene que estar instalado
```

## Flujo de un episodio (ejemplo: love-bombing)
```bash
# 1. Imágenes: tirá las 47 de Flow en inbox/ y corré
python tools/organize_images.py love-bombing
#    -> revisá out/contact_sheet_01..04.jpg (número + línea de voz). Si algo está fuera de lugar,
#       movelo de línea en inbox/order.txt y repetí. Cuando esté bien:
python tools/organize_images.py love-bombing --apply
python tools/organize_images.py love-bombing --check        # debe decir 47 de 47

# 2. Sonidos: poné whoosh.mp3, impact.mp3, thud.mp3, riser.mp3, notification.mp3 y music.mp3 en public/sfx/
#    + public/sfx/LICENCIAS.md (fuente y licencia). Después:
python tools/check_sfx.py

# 3. Voz (probá primero una línea con 2-3 voces)
python tools/make_audio.py love-bombing en --only 1 --voice en-US-AndrewNeural
python tools/make_audio.py love-bombing en
python tools/make_audio.py love-bombing es --voice es-MX-JorgeNeural

# 4. Verificar tiempos y ver el video
npm test                 # prueba el armado de tiempos
npm run studio           # vista previa interactiva
npm run preview:en       # render chico (out/preview-en.mp4) para aprobar
npm run render:en        # render final  (out/kai-p1-en.mp4)
npm run render:es        # render final  (out/kai-p1-es.mp4)
```

## Nuevo episodio
1. Copiá `episodes/love-bombing/` a `episodes/<nuevo-slug>/` (con `en/` y `es/`).
2. Editá `script.json` de cada idioma: `lines` (texto, imágenes por línea, `hook`, `counter`), `imagePrefix` (`kai-p2-`), `imageCount`.
3. Corré el flujo de arriba cambiando el slug (en `package.json`, los scripts `render:*` tienen el slug fijo: cambialo o usá `--props`).

## Qué se probó y qué no
- Probado: compila sin errores (TypeScript), empaqueta con Remotion, el armado de tiempos pasa `npm test` para EN y ES, y el organizador detecta faltantes/duplicados y arma las hojas de contacto con imágenes de prueba.
- NO probado: el render final (no hay navegador en el entorno donde se armó) ni la voz real de Edge-TTS (sin internet a ese servicio). La primera vez corré `npm run preview:en` y mirá el resultado antes del render final. Si `make_audio.py` no trae tiempos por palabra con alguna voz, reparte las palabras automáticamente según su largo.

## Estructura
```
episodes/<slug>/<lang>/script.json   guion, imágenes por línea, ganchos, contador, zoom, sfx
inbox/                               imágenes crudas de Flow
public/episodes/<slug>/images/       kai-pN-NN.png (las crea el organizador)
public/episodes/<slug>/<lang>/       script.json, timing.json, audio/line-NN.mp3 (las crea make_audio.py)
public/sfx/                          sonidos y música + LICENCIAS.md
prompts/kai-character.md             bloques fijos de Kai para los prompts
tracking/videos.csv                  medición por video
tools/                               organize_images.py, make_audio.py, check_sfx.py, test-timeline.ts
src/                                 proyecto Remotion
```
