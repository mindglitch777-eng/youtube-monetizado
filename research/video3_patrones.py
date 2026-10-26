#!/usr/bin/env python3
"""Agrupa los videos del barrido del video 3 por familia de formato (título) y mide rendimiento."""
import json, re, statistics as st
from pathlib import Path
D = Path(__file__).parent / "data" / "video3-2026-10"
T = json.loads((D / "tabla.json").read_text())
FAM = [
 ("cuanto_durarias", r"how long (would )?you('d| would)? (last|survive)|cuánto durarías|cuanto durarias|could you survive|sobrevivirías|you'?d last"),
 ("que_hacian_todo_el_dia", r"(what did|qué hacía|que hacia|qué hacían).*(all day|todo el día|before|cuando|when)|ancient humans (do|actually)"),
 ("dia1_a_dia30_supervivencia", r"day 1 to|día 1 al|30 days|1 year|un año|100 days|100 días|bunker|survival \d|surviv(e|al) .*(days|year)"),
 ("que_pasaria_si", r"what if|qué pasaría si|que pasaria si|what (would )?happens? (to|if)|qué pasa si|qué le pasa"),
 ("every_x_explained", r"every .* explained|cada .* explicad|every level|niveles de|levels of|iceberg"),
 ("peores_de_la_historia", r"worst .* (in|of) history|peores? .* historia|most (brutal|painful|disgusting)|más (crueles|brutales|asquerosas)"),
 ("vs_pelea", r" vs\.? | could you beat|podrías vencer|dominate|ganaría"),
 ("asi_era_hace_x", r"así era|asi era|how .* looked|hace [\d\.]+ (millones de )?años|years ago"),
 ("pov_segunda_persona", r"^pov|pov:|eres un|you are a|you were born|si nacieras|naciste"),
 ("sentir_cuerpo", r"lo que sientes|what it feels like|qué se siente|what it was like|cómo se siente"),
 ("dormir_compilado", r"sleep|dormir|fall asleep|hours? of"),
 ("lista_numero", r"^\d+ |^los \d+|^las \d+|top \d+"),
 ("misterio_perdido", r"lost|perdid|mister|myster|unexplained|no puede explicar|no logra"),
]
def fam(t):
    t = t.lower()
    return [k for k, rx in FAM if re.search(rx, t)] or ["otros"]
def es(r):
    return r["idioma"].startswith("es") or any(c.startswith("es:") for c in r["consultas"]) and re.search(r"[áéíóúñ¿¡]| de | la | el | en ", r["titulo"].lower()) is not None
res = {}
for r in T:
    if r["dur"] < 180: continue
    r["fam"] = fam(r["titulo"]); r["es"] = bool(es(r))
    chico = r["subs"] is not None and r["subs"] <= 100000
    for f in r["fam"]:
        g = res.setdefault(f, {"n":0,"chicos":0,"vd":[],"vd_chicos":[],"es":0,"es_vd":[],"outl":[]})
        g["n"] += 1; g["vd"].append(r["vistas_dia"]); g["outl"].append(r["outlier_vs_prom"])
        if chico: g["chicos"] += 1; g["vd_chicos"].append(r["vistas_dia"])
        if r["es"]: g["es"] += 1; g["es_vd"].append(r["vistas_dia"])
out = []
for f, g in res.items():
    med = lambda x: round(st.median(x)) if x else 0
    out.append({"familia": f, "videos": g["n"], "mediana_vistas_dia": med(g["vd"]), "canales_chicos": g["chicos"],
                "mediana_vd_chicos": med(g["vd_chicos"]), "videos_es": g["es"], "mediana_vd_es": med(g["es_vd"]),
                "mediana_outlier": round(st.median(g["outl"]),1)})
out.sort(key=lambda x: -x["mediana_vd_chicos"])
(D / "familias.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
json.dump(T, open(D / "tabla.json", "w"), ensure_ascii=False)
for o in out: print(o)
