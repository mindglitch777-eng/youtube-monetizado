#!/bin/bash
# Renderiza los 8 Shorts y los normaliza a -14 LUFS (sin silencio extra al final, para que el loop sea limpio)
cd "$(dirname "$0")/../remotion"
B=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell
declare -A NOMBRE=([00]=00_gancho [01]=01_germenes [02]=02_un_rasguno [03]=03_otras_personas [04]=04_la_noche [05]=05_lo_que_comes [06]=06_grandes_animales [07]=07_sin_agua)
for n in 07 06 05 04 03 02 01 00; do
  npx remotion render src/index.ts Short$n ../out/raw_short_$n.mp4 --codec=h264 --crf=18 --browser-executable=$B --concurrency=4 --log=error || exit 1
  ffmpeg -v error -y -i ../out/raw_short_$n.mp4 -c:v copy -af "loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 -c:a aac -b:a 192k -movflags +faststart ../out/short_${NOMBRE[$n]}.mp4
  echo "listo $n"
done
