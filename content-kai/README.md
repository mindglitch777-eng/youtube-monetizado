# content-kai/ — línea de contenido "Kai"

Carpeta separada de `content/` (que es del canal cinematográfico Knotwise
— no se mezclan). Ver `ESTRATEGIA.md` en la raíz para el contexto completo
y `RULES.md`, sección "FÓRMULA DE RETENCIÓN — línea Kai / formato simple",
para las 13 reglas de guion que todo video de esta línea tiene que cumplir.

Convención: una carpeta por video, `content-kai/<fecha>-<slug>/`, por
ejemplo `content-kai/2026-XX-XX-top5-red-flags/`. Ver `_plantilla/` para
la estructura exacta y copiarla como punto de partida.

## Archivos de cada video

- **`guion.txt`** — el texto que se sintetiza con edge-tts, dividido en
  secciones con encabezados `### ID — nombre opcional` (mismo formato que
  usa el PACK cinematográfico). IDs válidos y orden obligatorio:
  `HOOK`, `P5`, `P4`, `P3`, `P2`, `P1`, `CTA`. La cuenta va SIEMPRE 5→1
  (regla 4) — nunca se invierte el orden de los IDs.
- **`shots.json`** — la estructura visual: título, identidad amplia,
  cuál punto es el más fuerte (para el gancho de retención del hook),
  las 5 imágenes (una por punto, provistas a mano — ver abajo), el
  elemento recurrente sin resolver (opcional) y la frase de énfasis
  triple. Esquema exacto en `remotion/src/kai/tipos.ts` (tipo `ShotsKai`).
- **`img/`** — las imágenes de cada punto. **Se generan A MANO en Google
  Flow por el usuario** (no hay pipeline de IA para esto todavía) — este
  repo solo las recibe y las ensambla. Una imagen por punto (regla del
  formato: "una por línea de guion"), más la del elemento recurrente si
  hay. Deben mostrar literalmente la escena que cuenta la voz en ese
  punto, no solo la cara/emoción de Kai.
- **`audio/`** (se genera solo) — `voz.mp3` + `voz.json` (palabras
  cronometradas), vía GitHub Actions (`kai_voz.py`, edge-tts está
  bloqueado desde Claude Code).
- **`kai-timeline.json`** (se genera solo, local) — alineación real de
  palabras por sección, vía `kai_timeline.py`.

## Pipeline (una vez que `guion.txt` + `shots.json` + `img/` ya están)

1. `python scripts/kai_voz.py content-kai/<carpeta>` — dispara solo, o
   empuja el commit de `guion.txt` para que lo dispare
   `.github/workflows/kai-voz.yml` en GitHub Actions.
2. `python scripts/kai_timeline.py content-kai/<carpeta>` — local, sin red.
3. `cd remotion && npm run preparar:kai -- ../content-kai/<carpeta>`
4. `npx remotion render KaiListicle ../content-kai/<carpeta>/out/video_silent.mp4`
5. Mezcla de audio — todavía no tiene script propio (el de Knotwise,
   `pack_mezcla.py`, está armado para el esquema de sfx/música del PACK
   cinematográfico; Kai es más simple, solo voz — puede alcanzar con un
   mux directo `ffmpeg -i video_silent.mp4 -i audio/voz.mp3 -c:v copy -c:a
   aac -shortest video_final.mp4`, se arma un script dedicado cuando haga
   falta música/sfx de verdad).

## Qué falta para la primera pieza real

- Un guion real (13 reglas de RULES.md).
- Las 5 imágenes + la del elemento recurrente, generadas en Google Flow.
- Decidir si esta primera pieza necesita música/sfx de fondo o solo voz.
