"""Arma el timeline final de content-kai/parte1-love-bombing a partir de
script.json (líneas + imágenes + flags) y audio/voz.json (duración real y
palabras cronometradas de cada línea, generadas por kai_p1_voz.py en
GitHub Actions). Local, no necesita red — solo ffmpeg (ya instalado).

Hace tres cosas:
  1. Concatena los 32 mp3 en un solo audio/voz_completa.mp3, insertando
     0.15s de silencio después de cada línea HOOK (para que "el gancho
     respire") y 0.5s de silencio antes del CTA final (RULES.md, REGLA
     DE SONIDO).
  2. Escribe out/timeline.json con el armado cuadro a cuadro: duración de
     cada línea, reparto de imágenes (mínimo 1.2s cada una, zoom/pan
     según impar/par), estado del contador, el frame de disparo del zoom
     de la línea 4, y los eventos de SFX (whoosh/impacto/latido/riser/
     notificación) con su frame — 2-3 frames antes del corte que
     acompañan, como pide la regla.
  3. Calcula los tramos sin voz (pausas) para el ducking de la música de
     fondo en Remotion.

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
SILENCIO_PRE_CTA_S = 0.5
ADELANTO_SFX_FRAMES = 2  # "2-3 frames ANTES del corte visual"
LINEA_PRE_CTA = 31  # línea justo antes del CTA (n=32)
LINEAS_NOTIFICACION = {12, 14, 15}  # mencionan teléfono/texto explícitamente


def numero_imagen(archivo):
    m = re.search(r"(\d+)\.png$", archivo)
    return int(m.group(1))


def repartir_imagenes(imagenes, duracion_s):
    n = len(imagenes)
    cada = duracion_s / n
    if cada < MIN_S_POR_IMAGEN and duracion_s >= MIN_S_POR_IMAGEN:
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


def concatenar_audio(carpeta, lineas_voz, pausa_por_n, destino):
    carpeta_audio = carpeta / "audio"
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        silencios_cache = {}

        def silencio_de(duracion_s):
            if duracion_s not in silencios_cache:
                ruta = tmp / f"silencio_{duracion_s}.mp3"
                subprocess.run(
                    ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", str(duracion_s),
                     "-q:a", "9", str(ruta)],
                    check=True, capture_output=True,
                )
                silencios_cache[duracion_s] = ruta
            return silencios_cache[duracion_s]

        entradas = []
        partes_filtro = []
        for lv in lineas_voz:
            entradas += ["-i", str(carpeta_audio / lv["archivo"])]
            partes_filtro.append(f"[{len(entradas)//2 - 1}:a]")
            pausa_s = pausa_por_n.get(lv["n"], 0.0)
            if pausa_s > 0:
                entradas += ["-i", str(silencio_de(pausa_s))]
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

    # pausa (silencio) DESPUÉS de cada línea, por n: HOOK respira 0.15s,
    # la línea previa al CTA agrega 0.5s de silencio total (regla de sonido).
    pausa_por_n = {}
    for linea in script["lineas"]:
        flags = linea.get("flags", [])
        pausa = PAUSA_HOOK_S if "HOOK" in flags else 0.0
        if linea["n"] == LINEA_PRE_CTA:
            pausa = SILENCIO_PRE_CTA_S
        if pausa:
            pausa_por_n[linea["n"]] = pausa

    print("Concatenando audio (pausas HOOK de 0.15s + 0.5s de silencio antes del CTA) ...")
    destino_audio = carpeta / "audio" / "voz_completa.mp3"
    concatenar_audio(carpeta, voz["lineas"], pausa_por_n, destino_audio)

    contador_valor = None
    lineas_out = []
    sfx_eventos = []
    pausas_sin_voz = []  # [inicioFrame, finFrame] para ducking de música
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
        cambia_contador = any(f.startswith("CONTADOR_") for f in flags)
        es_hook = "HOOK" in flags
        es_grid = n == 4

        imagenes = repartir_imagenes(linea["imagenes"], duracion_audio_s)

        trigger_today = buscar_trigger_today(lv["palabras"]) if es_grid else None

        start_s = cursor_s
        start_frame = round(start_s * FPS)

        # Eventos de SFX, 2-3 frames antes del corte que acompañan (acá: 2).
        if es_hook:
            sfx_eventos.append({"tipo": "whoosh", "frame": max(0, start_frame - ADELANTO_SFX_FRAMES)})
            sfx_eventos.append({"tipo": "latido", "frame": max(0, start_frame - ADELANTO_SFX_FRAMES)})
        if cambia_contador:
            sfx_eventos.append({"tipo": "whoosh", "frame": max(0, start_frame - ADELANTO_SFX_FRAMES)})
            sfx_eventos.append({"tipo": "impacto", "frame": max(0, start_frame - ADELANTO_SFX_FRAMES)})
        if n in LINEAS_NOTIFICACION:
            sfx_eventos.append({"tipo": "notificacion", "frame": max(0, start_frame - ADELANTO_SFX_FRAMES)})
        if es_grid and trigger_today is not None:
            trigger_frame_abs = start_frame + round(trigger_today * FPS)
            riser_inicio = max(0, trigger_frame_abs - round(1.5 * FPS))
            sfx_eventos.append({"tipo": "riser", "frame": riser_inicio, "hasta": trigger_frame_abs})
            sfx_eventos.append({"tipo": "impacto", "frame": max(0, trigger_frame_abs - ADELANTO_SFX_FRAMES)})

        pausa_s = pausa_por_n.get(n, 0.0)
        end_s = start_s + duracion_audio_s + pausa_s
        if pausa_s > 0:
            pausas_sin_voz.append([round((start_s + duracion_audio_s) * FPS), round(end_s * FPS)])

        lineas_out.append({
            "n": n,
            "texto": linea["texto"],
            "flags": flags,
            "startS": round(start_s, 3),
            "endS": round(end_s, 3),
            "startFrame": start_frame,
            "endFrame": round(end_s * FPS),
            "duracionAudioFrames": round(duracion_audio_s * FPS),
            "pausaFrames": round(pausa_s * FPS),
            "imagenes": imagenes,
            "palabras": lv["palabras"],
            "contadorVisible": contador_visible,
            "contadorValor": contador_valor,
            "esGridIntro": es_grid,
            "triggerTodayS": trigger_today,
        })
        cursor_s = end_s

    timeline = {
        "fps": FPS, "ancho": 1080, "alto": 1920,
        "audio": "audio/voz_completa.mp3",
        "duracionTotal": round(cursor_s, 3),
        "lineas": lineas_out,
        "sfxEventos": sfx_eventos,
        "pausasSinVoz": pausas_sin_voz,
    }
    destino = carpeta / "out"
    destino.mkdir(exist_ok=True)
    (destino / "timeline.json").write_text(json.dumps(timeline, indent=2, ensure_ascii=False), encoding="utf-8")

    minutos, segundos = divmod(round(cursor_s), 60)
    print(f"Listo: {len(lineas_out)} líneas, {len(sfx_eventos)} eventos de SFX, "
          f"duración total {minutos}:{segundos:02d} ({cursor_s:.1f}s)")
    print(f"  {destino / 'timeline.json'}")
    print(f"  {destino_audio}")


if __name__ == "__main__":
    main()
