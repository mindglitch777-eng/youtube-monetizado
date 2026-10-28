#!/bin/bash
# Prepara todo lo necesario para renderizar el video 2 en GitHub Actions:
# imágenes procesadas, voz recortada, sonidos y línea de tiempo.
# Uso: video2/tools/ci_prep.sh [largo|short N|nada]  -> además mezcla el audio pedido.
set -e
cd "$(dirname "$0")/../.."
python3 video2/tools/preparar.py
python3 video2/tools/voz.py
python3 video2/tools/sonidos.py
python3 video2/tools/timeline.py
(cd video2/tools && python3 shorts.py)
mkdir -p remotion/public/v2
rm -rf remotion/public/v2/img16 remotion/public/v2/img916
cp -r video2/work/img16 video2/work/img916 remotion/public/v2/
if [ "$1" = "largo" ]; then
  python3 video2/tools/mezcla.py video2/work/largo_audio.json remotion/public/v2_largo.wav
elif [ "$1" = "short" ]; then
  python3 video2/tools/mezcla.py video2/work/short_$2_audio.json remotion/public/v2_short_$2.wav
fi
