#!/bin/bash
# Renderiza los 9 Shorts del video 2 (el largo se renderiza aparte) y deja los mp4 en out/video2/
cd "$(dirname "$0")/../../remotion"
B=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell
mkdir -p ../out/video2
declare -A NOMBRE=([0]=0_trailer [1]=1_hielo [2]=2_egipto [3]=3_pompeya [4]=4_roma [5]=5_1348 [6]=6_tenochtitlan [7]=7_1816 [8]=8_londres)
for n in 0 1 2 3 4 5 6 7 8; do
  npx remotion render src/index.ts V2Short$n ../out/video2/short_${NOMBRE[$n]}.mp4 --codec=h264 --crf=18 --audio-codec=aac --audio-bitrate=192k --browser-executable=$B --concurrency=4 --log=error || exit 1
  echo "listo short $n"
done
