"""Arma el timeline final de content-kai/parte1-love-bombing a partir de
script.json (líneas + imágenes + flags) y audio/voz.json (duración real y
palabras cronometradas de cada línea, generadas por kai_p1_voz.py en
GitHub Actions). Local, no necesita red — solo ffmpeg (ya instalado).

Hace dos cosas:
  1. Concatena los 32 mp3 en un solo audio/voz_completa.mp3, insertando
     0.15s de silencio después de cada línea HOOK (para que "el gancho
     respire", como pide el .md de instrucciones).
  2. Escribe out/timeline.json con el armado cuadro a cuadro: duración de
     cada línea = duración de su audio (+ la pausa si es HOOK), reparto de
     imágenes dentro de la línea (mínimo 1.2s cada una, movimiento
     zoom/pan según si el número de imagen es impar/par), estado del
     contador en cada línea, y el frame de disparo del zoom de la línea 4
     (grilla de 5 -> panel de love bombing), buscado en las palabras
     reales por la palabra "Today".

Uso:
    python scripts/kai_p1_timeline.py content-kai/parte1-love-bombing
"""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

FPS = 30
MIN_S_POR_IMAGEN = 1.2
PAUSA_HOOK_S = 0.15


def numero_imagen(archivo):
    m = re.search(r"(\d+)\.png$", archivo)
    return int(m.group(1))


def repartir_imagenes(imagenes, duracion_s):
    n = len(imagenes)
    cada = duracion_s / n
    if cada < MIN_S_POR_IMAGEN and duracion_s >= MIN_S_POR_IMAGEN:
        # si alcanza, forzamos el mínimo y la/s última/s imagen/es absorben el resto
        cada = MIN_S_POR_IMAGEN
    partes = []
    acumulado = 0.0
    for i, archivo in enumerate(imagenes):
        es_ultima = i == n - 1
        dur = (duracion_s - acumulado) if es_ultima else cada
        num = numero_imagen(archivo)
        partes.append({
            "archivo": archivo,
            "duracionS": round(dur, 3),
            "movimiento": "zoom" if num % 2 == 1 else "pan",
        })
        acumulado += dur
    return partes


def buscar_trigger_today(palabras):
    for p in palabras:
        if re.sub(r"[^a-zA-Z]", "", p["texto"]).lower() == "today":
            return p["inicio"]
    return None


def concatenar_audio(carpeta, lineas_voz, lineas_script, destino):
    carpeta_audio = carpeta / "audio"
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        silencio = tmp / "silencio.mp3"
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=24000:cl=mono", "-t", str(PAUSA_HOOK_S),
             "-q:a", "9", str(silencio)],
            check=True, capture_output=True,
        )
        flags_por_n = {l["n"]: l.get("flags", []) for l in lineas_script}

        entradas = []
        partes_filtro = []
        for i, lv in enumerate(lineas_voz):
            entradas += ["-i", str(carpeta_audio / lv["archivo"])]
            partes_filtro.append(f"[{len(entradas)//2 - 1}:a]")
            if "HOOK" in flags_por_n.get(lv["n"], []):
                entradas += ["-i", str(silencio)]
                partes_filtro.append(f"[{len(entradas)//2 - 1}:a]")

        filtro = "".join(partes_filtro) + f"concat=n={len(partes_filtro)}:v=0:a=1[out]"
        cmd = ["ffmpeg", "-y", *entradas, "-filter_complex", filtro, "-map", "[out]", str(destino)]
        subprocess.run(cmd, check=True, capture_output=True)


def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: python scripts/kai_p1_timeline.py <carpeta>")
    carpeta = Path(sys.argv[1]).resolve()

    script = json.loads((carpeta / "script.json").read_text(encoding="utf-8"))
    voz = json.loads((carpeta / "audio" / "voz.json").read_text(encoding="utf-8"))
    voz_por_n = {l["n"]: l for l in voz["lineas"]}

    print("Concatenando audio (con pausas de 0.15s después de cada HOOK) ...")
    destino_audio = carpeta / "audio" / "voz_completa.mp3"
    concatenar_audio(carpeta, voz["lineas"], script["lineas"], destino_audio)

    contador_valor = None
    lineas_out = []
    cursor_s = 0.0
    for linea in script["lineas"]:
        n = linea["n"]
        flags = linea.get("flags", [])
        lv = voz_por_n[n]
        duracion_audio_s = lv["duracion"]

        for f in flags:
            if f.startswith("CONTADOR_"):
                contador_valor = int(f.split("_")[1])
        contador_visible = 5 <= n <= 28

        imagenes = repartir_imagenes(linea["imagenes"], duracion_audio_s)

        trigger_today = None
        if n == 4:
            trigger_today = buscar_trigger_today(lv["palabras"])

        pausa_s = PAUSA_HOOK_S if "HOOK" in flags else 0.0

        start_s = cursor_s
        end_s = start_s + duracion_audio_s + pausa_s
        lineas_out.append({
            "n": n,
            "texto": linea["texto"],
            "flags": flags,
            "startS": round(start_s, 3),
            "endS": round(end_s, 3),
            "startFrame": round(start_s * FPS),
            "endFrame": round(end_s * FPS),
            "duracionAudioFrames": round(duracion_audio_s * FPS),
            "pausaFrames": round(pausa_s * FPS),
            "imagenes": imagenes,
            "palabras": lv["palabras"],  # ya en tiempo local a la línea
            "contadorVisible": contador_visible,
            "contadorValor": contador_valor,
            "esGridIntro": n == 4,
            "triggerTodayS": trigger_today,
        })
        cursor_s = end_s

    timeline = {
        "fps": FPS, "ancho": 1080, "alto": 1920,
        "audio": "audio/voz_completa.mp3",
        "duracionTotal": round(cursor_s, 3),
        "lineas": lineas_out,
    }
    destino = carpeta / "out"
    destino.mkdir(exist_ok=True)
    (destino / "timeline.json").write_text(json.dumps(timeline, indent=2, ensure_ascii=False), encoding="utf-8")

    minutos, segundos = divmod(round(cursor_s), 60)
    print(f"Listo: {len(lineas_out)} líneas, duración total {minutos}:{segundos:02d} ({cursor_s:.1f}s)")
    print(f"  {destino / 'timeline.json'}")
    print(f"  {destino_audio}")


if __name__ == "__main__":
    main()
