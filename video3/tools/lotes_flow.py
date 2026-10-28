#!/usr/bin/env python3
"""
Arma los lotes para las extensiones de generación en masa de Google Flow
(TryAIToday Flow Automator, SuperFlow, Auto Flow, etc.): un archivo .txt por lote,
un prompt por línea, todos los planos de un lote con las MISMAS imágenes de referencia
adjuntas (las extensiones suelen poner las referencias para todo el lote).

Salida: video3/flow_lotes/NN_nombre.txt, video3/flow_lotes/lotes.json (orden → id del
plano, para renombrar lo que bajen) y la página video3/docs/lotes_flow.html.

  python3 video3/tools/lotes_flow.py
"""
import json
import re
from pathlib import Path

V = Path(__file__).resolve().parent.parent
OUT = V / "flow_lotes"
DOCS = V / "docs"

# (nombre, referencias a adjuntar, formato, regla)  — el orden de la lista es la prioridad
LOTES = [
    ("medico", ["MEDICO", "CONSULTORIO", "PIJAMA"], "16:9", lambda s, b: "MEDICO" in s or "CONSULTORIO" in s),
    ("nena", ["NENA", "PIJAMA", "ESTABLO"], "16:9", lambda s, b: "NENA" in s and b != "S"),
    ("shorts_verticales", ["PIJAMA", "PULGA", "NENA"], "9:16", lambda s, b: b == "S"),
    ("pulga", ["PULGA", "PIJAMA"], "16:9", lambda s, b: "PULGA" in s),
    ("despertador", ["DESPERTADOR", "PIJAMA"], "16:9", lambda s, b: "DESPERTADOR" in s),
    ("pijama_establo", ["PIJAMA", "ESTABLO"], "16:9", lambda s, b: "PIJAMA" in s and "ESTABLO" in s),
    ("pijama_ciudad", ["PIJAMA", "CALLE", "PLAZA"], "16:9", lambda s, b: "PIJAMA" in s and ("CALLE" in s or "PLAZA" in s)),
    ("pijama_camino", ["PIJAMA", "CAMINO"], "16:9", lambda s, b: "PIJAMA" in s and "CAMINO" in s),
    ("pijama_villa", ["PIJAMA", "VILLA"], "16:9", lambda s, b: "PIJAMA" in s and "VILLA" in s),
    ("pijama_bosque", ["PIJAMA", "BOSQUE"], "16:9", lambda s, b: "PIJAMA" in s and "BOSQUE" in s),
    ("pijama_solo", ["PIJAMA", "PIJAMA_CARAS"], "16:9", lambda s, b: "PIJAMA" in s),
    ("lugares_sin_personajes", [], "16:9", lambda s, b: True),
]


def limpiar(prompt, refs):
    """Una sola línea, y la frase de referencias apuntando a lo que se adjunta en el lote."""
    p = re.sub(r"Use the reference images: [^.]*\.", "", prompt)
    if refs:
        p = p.replace(" Color and light:", f" Keep characters and places exactly as in the attached reference images ({', '.join(refs)}). Color and light:", 1)
    return re.sub(r"\s+", " ", p).strip()


def main():
    d = json.loads((DOCS / "visual_v3.json").read_text())
    OUT.mkdir(exist_ok=True)
    for f in OUT.glob("*.txt"):
        f.unlink()
    lotes = [{"n": 0, "nombre": "ingredientes", "refs": [], "formato": "16:9",
              "nota": "Sin referencias. Son las hojas de personajes y los lugares: elegí la mejor de cada uno y guardala con el nombre exacto.",
              "items": [{"id": i["nombre"], "prompt": re.sub(r"\s+", " ", i["prompt"])} for i in d["ingredientes"]]}]
    asignados = {}
    for pl in d["planos"]:
        s = set(x.strip() for x in pl["ingredientes"].split(",") if x.strip())
        if "PIJAMA_CARAS" in s:
            s.add("PIJAMA")
        for nombre, refs, fmt, regla in LOTES:
            if regla(s, pl["bloque"]):
                asignados.setdefault(nombre, []).append({"id": pl["id"], "prompt": limpiar(pl["prompt"], refs)})
                break
    for k, (nombre, refs, fmt, _) in enumerate(LOTES, 1):
        if nombre in asignados:
            lotes.append({"n": k, "nombre": nombre, "refs": refs, "formato": fmt, "nota": "", "items": asignados[nombre]})
    lotes.append({"n": len(LOTES) + 1, "nombre": "miniaturas", "refs": ["PIJAMA", "PULGA", "MEDICO"], "formato": "16:9",
                  "nota": "Las 3 ideas de miniatura.", "items": [{"id": f"MIN{i+1}", "prompt": limpiar(m["prompt"], ["PIJAMA", "PULGA", "MEDICO"])}
                                                                for i, m in enumerate(d["miniaturas"])]})
    for i, l in enumerate(lotes):
        l["archivo"] = f"{i:02d}_{l['nombre']}.txt"
        (OUT / l["archivo"]).write_text("\n".join(x["prompt"] for x in l["items"]) + "\n")
    (OUT / "lotes.json").write_text(json.dumps(lotes, ensure_ascii=False, indent=1))
    total = sum(len(l["items"]) for l in lotes)
    for l in lotes:
        print(f"{l['archivo']:34} {len(l['items']):3}  refs: {', '.join(l['refs']) or '—'}  {l['formato']}")
    print("total", total)
    tpl = (V / "tools" / "lotes_flow_plantilla.html").read_text()
    (DOCS / "lotes_flow.html").write_text(tpl.replace("__DATA__", json.dumps(lotes, ensure_ascii=False)))


if __name__ == "__main__":
    main()
