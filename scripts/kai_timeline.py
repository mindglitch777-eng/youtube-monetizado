"""Paso 2 de un video de la línea Kai (parte local, sin red): arma
kai-timeline.json a partir de audio/voz.json (palabras reales cronometradas
por kai_voz.py) y shots.json (las 5 escenas + hook + cta).

Uso:
    python scripts/kai_timeline.py content-kai/<carpeta-video>

Como kai_voz.py sintetiza el guion COMPLETO en una sola pasada (concatenando
el texto de cada sección en orden), alinear es simple: cada sección se
queda con tantas palabras del stream continuo como palabras tiene su
propio texto (por conteo, no por fuzzy-match — no hace falta walking de
tokens como en el PACK cinematográfico, que sintetiza cada capítulo por
separado y podía perder alguna palabra entre bloques).

Escribe content-kai/<carpeta>/kai-timeline.json:
  {fps, audio, duracionTotal, tomas:[{id,startS,endS,startFrame,endFrame,palabras}]}
"""

import json
import re
import sys
from pathlib import Path

FPS = 30


def normalizar(palabra):
    return re.sub(r"[^\w']", "", palabra.lower())


def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: python scripts/kai_timeline.py content-kai/<carpeta-video>")
    carpeta = Path(sys.argv[1]).resolve()

    voz = json.loads((carpeta / "audio" / "voz.json").read_text(encoding="utf-8"))
    palabras_reales = voz["palabras"]
    secciones = voz["secciones"]

    cursor = 0
    tomas = []
    for seccion in secciones:
        palabras_esperadas = seccion["texto"].split()
        n = len(palabras_esperadas)
        tramo = palabras_reales[cursor:cursor + n]
        if len(tramo) != n:
            sys.exit(f"Desalineado en la sección {seccion['id']}: se esperaban {n} palabras, "
                      f"quedan {len(palabras_reales) - cursor} en el stream.")
        # sanity check liviano: compara la primera y última palabra normalizadas
        if tramo and normalizar(tramo[0]["texto"]) != normalizar(palabras_esperadas[0]):
            print(f"::warning::sección {seccion['id']}: primera palabra no coincide "
                  f"('{tramo[0]['texto']}' vs '{palabras_esperadas[0]}') — revisar a mano.")
        cursor += n

        if not tramo:
            continue
        start_s = tramo[0]["inicio"]
        end_s = tramo[-1]["fin"] + (0.6 if seccion["id"] == "CTA" else 0.15)
        tomas.append({
            "id": seccion["id"],
            "startS": round(start_s, 3),
            "endS": round(end_s, 3),
            "startFrame": round(start_s * FPS),
            "endFrame": round(end_s * FPS),
            "palabras": [{"texto": p["texto"], "inicio": p["inicio"], "fin": p["fin"]} for p in tramo],
        })

    if cursor != len(palabras_reales):
        print(f"::warning::sobran {len(palabras_reales) - cursor} palabras del audio sin asignar a ninguna sección.")

    duracion_total = tomas[-1]["endS"] if tomas else voz["duracion"]
    timeline = {"fps": FPS, "audio": "audio/voz.mp3", "duracionTotal": round(duracion_total, 3), "tomas": tomas}
    (carpeta / "kai-timeline.json").write_text(json.dumps(timeline, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Listo: {carpeta / 'kai-timeline.json'} ({len(tomas)} tomas, {duracion_total:.1f}s)")
    for t in tomas:
        print(f"  {t['id']:>5}  {t['startS']:6.2f}s -> {t['endS']:6.2f}s")


if __name__ == "__main__":
    main()
