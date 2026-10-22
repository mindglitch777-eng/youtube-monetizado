#!/usr/bin/env python3
"""
Arma los 9 Shorts del video 2 (mapa D del guion).

Short 0 = tráiler (gancho). Shorts 1–8 = una época cada uno:
línea 1 (gancho) → línea ⚑ de contexto → cuerpo sin las líneas ✂ → última línea (cliffhanger)
→ tarjeta "PARTE N DE 8 · EL VIDEO COMPLETO ESTÁ EN MI CANAL" (1,5 s).

- Imágenes 9:16 (work/img916); las verticales del bloque SHORTS (228–238) abren su Short.
- Un corte cada 1,5–2,5 s: si un plano dura más, se alterna con otra imagen de la misma época.
- Subtítulos palabra por palabra (con la puntuación del guion), en el tercio central.
- Arriba: barra de recap con vidas y notas de las épocas anteriores.

Escribe remotion/src/data/v2/short_N.json y video2/work/short_N_audio.json.
"""
import json
import re
from pathlib import Path

import timeline as TLM

V = Path(__file__).resolve().parent.parent
R = V.parent
VOZ, MAN = TLM.VOZ, TLM.MAN
EPOCAS, NOMBRE = TLM.EPOCAS, TLM.NOMBRE_EPOCA
GAP = 0.08
CORTE_MAX = 2.5
TARJETA = 1.5
VERTICAL = {"H": ["228", "229"], "E1": ["230", "231"], "E2": ["232"], "E3": ["233"], "E4": ["234"], "E5": ["235"],
            "E6": ["236"], "E7": ["237"], "E8": ["238"]}
NOMBRES_ARCHIVO = {0: "short_0_trailer", 1: "short_1_hielo", 2: "short_2_egipto", 3: "short_3_pompeya", 4: "short_4_roma",
                   5: "short_5_1348", 6: "short_6_tenochtitlan", 7: "short_7_1816", 8: "short_8_londres"}


def palabras_con_puntuacion(k):
    pal = VOZ[k]["palabras"]
    texto = VOZ[k]["texto"].replace("«", "").replace("»", "")
    toks = texto.split()
    if len(toks) == len(pal):
        return [{**w, "w": tok} for w, tok in zip(pal, toks)]
    return pal


def asignar(bloque):
    """Imágenes por línea para el Short: las del largo (incluye ⚑) + las verticales propias."""
    porid = {i["id"]: i for i in MAN}
    por_linea = {}
    mb = TLM.MBLOQUE[bloque]
    for img in MAN:
        if img["tipo"] not in ("imagen", "short") or img["id"] not in TLM.REC:
            continue
        q = img["quote"]
        if img["block"] == "S":
            m = re.match(r"SHORT (\d) · (.*)", q)
            if not m or VERTICAL.get(bloque, [""])[0] not in VERTICAL.get(bloque, []) or img["id"] not in VERTICAL.get(bloque, []):
                continue
            q = m.group(2)
        elif img["block"] != mb:
            continue
        for k, v in TLM.lineas_de(bloque):
            if v["corte_short"]:
                continue
            p = TLM.posicion(q, v["texto"])
            if p is not None:
                por_linea.setdefault(k, []).append([p, img])
                break
    for k, lst in TLM.EXTRA.items():
        if TLM.VOZ[k]["bloque"] == bloque:
            for prop, iid, ov in lst:
                img = dict(porid[iid])
                if ov is not None:
                    img["overlay"] = ov
                por_linea.setdefault(k, []).append([prop, img])
    for k, lst in por_linea.items():
        # la vertical propia va primero en su línea
        lst.sort(key=lambda it: (it[0], it[1]["block"] != "S"))
        grupos = {}
        for item in lst:
            grupos.setdefault(item[0], []).append(item)
        orden = sorted(grupos)
        for gi, p in enumerate(orden):
            sig = orden[gi + 1] if gi + 1 < len(orden) else 1.0
            for j, item in enumerate(grupos[p]):
                item[0] = p + (sig - p) * j / len(grupos[p])
        lst.sort(key=lambda it: it[0])
    return por_linea


def construir(n):
    bloque = "H" if n == 0 else f"E{n}"
    d = EPOCAS.get(bloque)
    por_linea = asignar(bloque)
    pool = [img for lst in por_linea.values() for _, img in lst]
    planos, textos, subs, voz, sfx = [], [], [], [], []
    t = 0.0
    lineas = [(k, v) for k, v in TLM.lineas_de(bloque) if not v["corte_short"]]
    for i, (k, v) in enumerate(lineas):
        es_muerte = d and d["muerte"] == k
        if k in TLM.SILENCIO_LARGO:
            t += 1.0  # en el Short el silencio se acorta a 1 s
        elif k in TLM.REMATES:
            t += 0.2
        if es_muerte:
            if planos:
                planos[-1]["congelar"] = round(t, 3)
            t += 0.3
            planos.append({"ini": round(t, 3), "tipo": "negro"})
            sfx.append({"t": round(t, 3), "nombre": "smash", "gain": 1.0})
            sfx.append({"t": round(t, 3), "nombre": "timbre_lento" if d["n"] in (5, 6) else "timbre", "gain": 0.6})
            t += 0.12
        for prop, img in por_linea.get(k, []):
            ini = t + TLM.tiempo_en_linea(k, prop)
            planos.append({"ini": round(ini, 3), "tipo": "img", "id": img["id"], "cam": img["cam"], "tr": img["tr"].split(":")[0].strip(),
                           "epoca": n, "vertical": img["block"] == "S"})
            if img["overlay"] and img["id"] not in TLM.SIN_OVERLAY:
                textos.append({"ini": round(ini + 0.1, 3), "texto": img["overlay"], "id": img["id"]})
            if img["tr"].startswith("PUNCH"):
                sfx.append({"t": round(ini, 3), "nombre": "punch", "gain": 0.5})
        voz.append({"t": round(t, 3), "id": k, "dur": v["dur"], "rol": v["rol"]})
        for w in palabras_con_puntuacion(k):
            subs.append({"w": w["w"], "ini": round(t + w["ini"], 3), "fin": round(t + w["fin"], 3)})
        if d and d.get("logro_linea") == k or (es_muerte and d and not d.get("logro_linea")):
            pass
        t += v["dur"] + GAP
    fin_voz = t
    planos.append({"ini": round(t, 3), "tipo": "tarjeta", "n": n})
    sfx.append({"t": round(t, 3), "nombre": "timbre" if n else "juego", "gain": 0.5})
    t += TARJETA
    # cierre de planos y cortes cada ≤ 2,5 s
    for j, p in enumerate(planos):
        p["fin"] = planos[j + 1]["ini"] if j + 1 < len(planos) else round(t, 3)
    final = []
    for j, p in enumerate(planos):
        dur = p["fin"] - p["ini"]
        if p["tipo"] != "img" or dur <= CORTE_MAX or p.get("congelar"):
            final.append(p)
            continue
        partes = int(dur // 2.0) + (1 if dur % 2.0 > 0.6 else 0)
        partes = max(2, partes)
        paso = dur / partes
        alternas = [img for img in pool if img["id"] != p["id"]]
        for q in range(partes):
            if q % 2 == 0:
                final.append({**p, "ini": round(p["ini"] + q * paso, 3), "fin": round(p["ini"] + (q + 1) * paso, 3), "tr": p["tr"] if q == 0 else ""})
            else:
                # alterna con otra imagen de la misma época que no sea la de antes ni la de después
                vecinos = {final[-1].get("id"), planos[j + 1].get("id") if j + 1 < len(planos) else None, p["id"]}
                cand = [a for a in alternas if a["id"] not in vecinos] or alternas
                a = cand[(j + q) % len(cand)]
                final.append({"ini": round(p["ini"] + q * paso, 3), "fin": round(p["ini"] + (q + 1) * paso, 3), "tipo": "img", "id": a["id"],
                              "cam": "CU", "tr": "PUNCH" if q == 1 else "", "epoca": n, "vertical": a["block"] == "S"})
    # textos: hasta el final de su plano, sin pisarse
    fin_id = {}
    for p in final:
        if p.get("id"):
            fin_id.setdefault(p["id"], p["fin"])
    for i, x in enumerate(textos):
        f = max(x["ini"] + 1.2, fin_id.get(x["id"], x["ini"] + 1.2))
        if i + 1 < len(textos):
            f = min(f, textos[i + 1]["ini"] - 0.05)
        x["fin"] = round(min(f, fin_voz), 3)
    previas = [{"epoca": NOMBRE[f"E{m}"], "nota": EPOCAS[f"E{m}"]["nota"]} for m in range(1, n)]
    recap = {"vidas": 8 - max(0, n - 1), "previas": previas,
             "titulo": "TRÁILER" if n == 0 else f"ÉPOCA {n} DE 8 · {NOMBRE[bloque]}",
             "jefe": f"JEFE: {d['jefe']}" if d else ""}
    out = {"duracion": round(t, 3), "n": n, "planos": final, "textos": textos, "subs": subs, "recap": recap,
           "estilo": d["estilo"] if d else "gancho", "fin_voz": round(fin_voz, 3)}
    (R / "remotion" / "src" / "data" / "v2" / f"short_{n}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    musica = TLM.MUSICA[bloque]
    audio = {"duracion": round(t, 3), "voz": voz, "sfx": sfx, "musica": [{"ini": 0.0, "nombre": musica}],
             "ambiente": [{"ini": 0.0, "nombre": TLM.AMBIENTE.get(bloque)}], "silencios": []}
    if bloque == "E6":  # Tenochtitlan: la música se corta con la viruela
        corte = next(x["t"] for x in voz if x["id"] == "E6_13")
        audio["musica"].append({"ini": corte, "nombre": None})
        audio["ambiente"].append({"ini": corte, "nombre": None})
        out["drenaje"] = [corte, next(x["t"] + x["dur"] for x in voz if x["id"] == "E6_16")]
        (R / "remotion" / "src" / "data" / "v2" / f"short_{n}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    (V / "work" / f"short_{n}_audio.json").write_text(json.dumps(audio, ensure_ascii=False, indent=1))
    largos = [round(p["fin"] - p["ini"], 1) for p in final if p["tipo"] == "img" and p["fin"] - p["ini"] > 2.6]
    seguidas = sum(1 for a, b in zip(final, final[1:]) if a.get("id") and a.get("id") == b.get("id"))
    print(f"Short {n}: {t:.1f} s, {len(final)} planos, más largos que 2,6 s: {largos}, repetidas seguidas: {seguidas}")
    return t


if __name__ == "__main__":
    for n in range(9):
        construir(n)
