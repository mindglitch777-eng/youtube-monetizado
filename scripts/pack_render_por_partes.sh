#!/bin/bash
# Renderiza LongForm en pedazos chicos (para que un reinicio del entorno
# pierda como mucho un pedazo, no todo el render). Reanudable: no vuelve a
# renderizar un pedazo cuyo archivo ya existe. Al final concatena todo con
# ffmpeg (concat demuxer, mismo códec, sin recodificar) en
# out/video_silent.mp4.
#
# Uso: bash scripts/pack_render_por_partes.sh <carpeta-content> [frames_por_parte]
set -euo pipefail

CARPETA="$1"
FRAMES_POR_PARTE="${2:-1000}"
cd "$(dirname "$0")/../remotion"

TOTAL=$(python3 -c "import json; print(json.load(open('public/timeline.json'))['tomas'][-1]['endFrame'])")
PARTES_DIR="../$CARPETA/out/partes"
mkdir -p "$PARTES_DIR"

echo "Total de frames: $TOTAL, en pedazos de $FRAMES_POR_PARTE"

INICIO=0
NUM=0
LISTA_CONCAT="$PARTES_DIR/lista.txt"
> "$LISTA_CONCAT"
while [ "$INICIO" -lt "$TOTAL" ]; do
  FIN=$((INICIO + FRAMES_POR_PARTE - 1))
  if [ "$FIN" -ge "$TOTAL" ]; then FIN=$((TOTAL - 1)); fi
  ARCHIVO="$PARTES_DIR/parte_$(printf '%03d' $NUM).mp4"
  echo "file 'parte_$(printf '%03d' $NUM).mp4'" >> "$LISTA_CONCAT"
  if [ -f "$ARCHIVO" ]; then
    echo "[$NUM] $ARCHIVO ya existe, salteo ($INICIO-$FIN)"
  else
    echo "[$NUM] renderizando frames $INICIO-$FIN -> $ARCHIVO"
    npx remotion render LongForm "$ARCHIVO" --codec=h264 --crf=18 --concurrency=4 \
      --frames="$INICIO-$FIN"
  fi
  INICIO=$((FIN + 1))
  NUM=$((NUM + 1))
done

echo "Concatenando $NUM partes -> out/video_silent.mp4 ..."
(cd "$PARTES_DIR" && ffmpeg -y -f concat -safe 0 -i lista.txt -c copy "../video_silent.mp4")
echo "Listo: $CARPETA/out/video_silent.mp4"
