#!/usr/bin/env python3
"""
Lote reducido de 40 imágenes para el video 3 (hojas de personaje, planos clave y miniaturas).
Cada prompt lleva adentro la descripción de sus personajes y lugares, así no hace falta adjuntar
referencias en Flow. Lo agrega como PRIMER lote de video3/flow_lotes/lotes.json (el panel lo elige solo).

  python3 video3/tools/lote_40.py
"""
import json
import re
from pathlib import Path

V = Path(__file__).resolve().parent.parent
LOTES = V / "flow_lotes" / "lotes.json"
INGR = ["PIJAMA", "PIJAMA_CARAS", "PULGA", "MEDICO", "NENA"]
PLANOS = ["002", "004", "005", "010", "013",            # 0 · despertar en 1348
          "016", "017", "027", "028",                   # 1 · agua y establo
          "034", "036", "039", "045", "047",            # 2 · la nena y la puerta
          "050", "054", "056", "061", "064",            # 3 · la pulga y el médico
          "067", "069", "072",                          # 4 · fiebre
          "078", "085", "088", "091",                   # 5 · flagelantes
          "094", "098", "099", "104",                   # 6 · la villa
          "110", "111", "115"]                          # 7 · día 30
MINIS = [0, 2]  # A · La pulga gigante, C · Elegí bien


def descripcion(prompt):
    """Lo que dice la hoja del ingrediente después de 'background:' (o del primer punto del lugar)."""
    m = re.search(r"background[^:.]*:\s*(.*?)(?:\.\s*(?:Front|Four|Six|No text)|$)", prompt)
    if m:
        return m.group(1).strip()
    cuerpo = re.sub(r"^Cinematic 2D.*?film grain\.\s*", "", prompt)
    cuerpo = re.sub(r"^Empty location plate, no characters:\s*", "", cuerpo)
    return re.sub(r"\s*No text, letters or logos\.?", "", cuerpo).strip().rstrip(".")


def main():
    d = json.loads((V / "docs" / "visual_v3.json").read_text())
    ing = {i["nombre"]: i for i in d["ingredientes"]}
    desc = {k: descripcion(v["prompt"]) for k, v in ing.items()}
    planos = {p["id"]: p for p in d["planos"]}
    items = [{"id": k, "prompt": re.sub(r"\s+", " ", ing[k]["prompt"])} for k in INGR]
    for pid in PLANOS:
        p = planos[pid]
        nombres = [x.strip() for x in p["ingredientes"].split(",") if x.strip()]
        if "PIJAMA_CARAS" in nombres:
            nombres = ["PIJAMA" if x == "PIJAMA_CARAS" else x for x in nombres]
        nombres = list(dict.fromkeys(nombres))
        quien = " ".join(f"{n} = {desc[n]}." for n in nombres if n in desc)
        txt = re.sub(r"Use the reference images: [^.]*\.", "", p["prompt"])
        txt = txt.replace(" Color and light:", f" Who and where: {quien} Same character design in every image. Color and light:", 1)
        txt = txt.replace("PIJAMA_CARAS", "PIJAMA")
        items.append({"id": pid, "prompt": re.sub(r"\s+", " ", txt).strip()})
    for k in MINIS:
        m = d["miniaturas"][k]
        quien = " ".join(f"{n} = {desc[n]}." for n in ["PIJAMA", "PULGA", "MEDICO"] if n in m["prompt"])
        txt = m["prompt"].replace("No text, letters or logos", f"Who: {quien} No text, letters or logos", 1)
        items.append({"id": f"MIN{k + 1}", "prompt": re.sub(r"\s+", " ", txt).strip()})
    assert len(items) == 40, len(items)
    lote = {"n": 0, "nombre": "esenciales_40", "refs": [], "formato": "16:9", "archivo": "E0_esenciales_40.txt",
            "nota": "Lote corto: 5 hojas de personaje, 33 planos clave y 2 miniaturas. Sin referencias para adjuntar.",
            "items": items}
    (V / "flow_lotes" / lote["archivo"]).write_text("\n".join(x["prompt"] for x in items) + "\n")
    lotes = [l for l in json.loads(LOTES.read_text()) if l["nombre"] != "esenciales_40"]
    LOTES.write_text(json.dumps([lote] + lotes, ensure_ascii=False, indent=1))
    print(len(items), "prompts ·", lote["archivo"])


if __name__ == "__main__":
    main()
