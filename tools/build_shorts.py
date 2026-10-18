#!/usr/bin/env python3
"""Serie de Shorts: uno por cada forma de morir (#7 a #1) + Short 0 con el gancho.
Genera remotion/src/data/shorts/short_NN.json con planos, voz (pausas recortadas), subtítulos,
efectos y música; y work/regenerar_vertical.txt. Reutiliza voz, imágenes y plan del video largo."""
import json
import math
import re
import sys
from pathlib import Path

R = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(R / "tools"))
import build_timeline as BT  # noqa: E402  (PLAN, VOZ, MAN, GANCHO...)

OUT = R / "remotion/src/data/shorts"
OUT.mkdir(parents=True, exist_ok=True)
LINEAS = BT.LINEAS
BEATS = BT.BEATS
MAN = BT.MAN
MAPA = BT.MAPA
EXTRA = {l["n"]: json.loads((R / f"work/voz_extra/{l['n']}.json").read_text())
         for l in json.loads((R / "work/voz_extra.json").read_text())["lineas"]}
PAUSA, PAUSA_GOLPE, GAP_MAX, GAP_NUEVO = 0.22, 0.5, 0.30, 0.18
TIPO = {i: m["tipo"] for i, m in MAPA.items()}  # A / B


def por_texto(t):
    return [l for l in LINEAS if l["texto"].startswith(t)][0]


def lineas_de(tramos, quitar=()):
    out = []
    for tr in tramos:
        for l in LINEAS:
            if l["tramo"] == tr and not any(l["texto"].startswith(q) for q in quitar):
                out.append(l)
    return out


SERIE = [
    dict(num=7, slug="07_sin_agua", nombre="SIN AGUA", gancho=[por_texto("Son las 9"), por_texto("Tu boca ya sabe")], gancho_img=["018", "019"],
         desarrollo=lineas_de(range(10, 17)), cliff="c7", sfx_extra=[("viento", 0.45)]),
    dict(num=6, slug="06_grandes_animales", nombre="GRANDES ANIMALES", gancho=["h6"], gancho_img=["089", "011"],
         desarrollo=lineas_de(range(19, 26)), cliff="c6"),
    dict(num=5, slug="05_lo_que_comes", nombre="LO QUE COMES", gancho=["h5"], gancho_img=["038", "039"],
         desarrollo=lineas_de(range(29, 36), quitar=("Y entonces los ves", "Tu cerebro dice")), cliff="c5"),
    dict(num=4, slug="04_la_noche", nombre="LA NOCHE", gancho=[por_texto("El sol se va."), por_texto("Y con él se va")], gancho_img=["044", "045"],
         desarrollo=lineas_de(range(39, 45)) + [por_texto("El fuego lo cuidaba alguien"), por_texto("Sin grupo. Sin saber")], cliff="c4", sfx_extra=[("respiracion", 0.55)]),
    dict(num=3, slug="03_otras_personas", nombre="OTRAS PERSONAS", gancho=["h3"], gancho_img=["101", "052"],
         desarrollo=lineas_de(range(47, 51)) + [por_texto("Un humano de esa época")], cliff="c3"),
    dict(num=2, slug="02_un_rasguno", nombre="UN RASGUÑO", gancho=[por_texto("Pero lo peor ni siquiera"), por_texto("Llega con una espina")],
         gancho_img=["058", "104"], desarrollo=lineas_de(range(54, 59)) + [por_texto("Lo peor: muchas veces"), por_texto("Se nota horas después"), por_texto("Sin vacunas"), por_texto("Y si te enfermabas")], cliff="c2"),
    dict(num=1, slug="01_germenes", nombre="LOS GÉRMENES", gancho=["h1"], gancho_img=["067", "068"],
         desarrollo=lineas_de(range(62, 72), quitar=("No tiene colmillos", "Por eso en la miniatura", "El león sí sabe")), cliff="c1"),
]
# imágenes de cada tramo para los Shorts (las del largo, sin tarjetas que no aplican)
PLAN = dict(BT.PLAN)
PLAN[24] = ["011", "dato12"]
PLAN[71] = ["ranking"]
POOL = {7: ["018", "019", "020", "086", "021", "022", "023", "087", "024", "025", "026", "088"],
        6: ["027", "028", "029", "030", "090", "031", "032", "092", "011", "033", "091", "089"],
        5: ["036", "093", "037", "094", "038", "039", "040", "041", "042", "095", "043", "096"],
        4: ["044", "045", "046", "047", "097", "048", "100", "098", "049", "050", "099", "051"],
        3: ["052", "053", "102", "054", "103", "055", "101", "056", "057", "058"],
        2: ["058", "104", "059", "060", "061", "062", "105", "063", "064", "065", "066", "071"],
        1: ["067", "068", "016", "069", "070", "106", "071", "072", "073"]}
REACCION = {7: "088", 6: "092", 5: "096", 4: "100", 3: "103", 2: "105", 1: "106"}
CARTA_ANCLA = {"dato12": "12", "dato8": "8", "dato10": "7"}
# imagen propia para las frases tomadas de otros bloques
POR_LINEA = {"El fuego lo cuidaba alguien": "082", "Y si te enfermabas": "083", "Sin grupo. Sin saber": "074",
             "Un humano de esa época": "090", "Lo peor: muchas veces": "095", "Se nota horas después": "043", "Sin vacunas": "071"}


def voz_de(n):
    if isinstance(n, str):
        d = EXTRA[n]
        return d, f"work/voz_extra/{n}.mp3"
    return BT.VOZ[n], f"work/voz/{n:03d}.mp3"


def colocar(n, t, voz, subs, texto_display=None):
    """Coloca una línea en t recortando las pausas internas > 0,30 s a 0,18 s. Devuelve el fin."""
    d, archivo = voz_de(n)
    p = d["palabras"]
    toks = re.findall(r"\S+", texto_display or d["texto"])
    # trozos separados por pausas largas
    trozos, cur = [], [0]
    for k in range(1, len(p)):
        if p[k]["ini"] - p[k - 1]["fin"] > GAP_MAX:
            trozos.append(cur)
            cur = []
        cur.append(k)
    trozos.append(cur)
    mapeo = len(toks) == len(p)
    inicio = t
    tiempos = {}
    for j, tr in enumerate(trozos):
        if j > 0:
            t += GAP_NUEVO
        a = max(0.0, p[tr[0]]["ini"] - 0.03)
        b = p[tr[-1]]["fin"] + 0.05
        voz.append(dict(archivo=archivo, ini=round(t, 3), src_ini=round(a, 3), dur=round(b - a, 3)))
        for k in tr:
            tiempos[k] = (t + p[k]["ini"] - a, t + p[k]["fin"] - a)
        t += b - a
    if mapeo:
        for k, tk in enumerate(toks):
            subs.append(dict(w=tk, ini=tiempos[k][0], fin=tiempos[k][1]))
    else:
        ini, fin = inicio + (p[0]["ini"] - p[0]["ini"]), t
        largo = sum(len(re.sub(r"\W", "", x)) or 1 for x in toks)
        c = inicio
        for tk in toks:
            dd = (fin - inicio) * (len(re.sub(r"\W", "", tk)) or 1) / largo
            subs.append(dict(w=tk, ini=c, fin=c + dd))
            c += dd
    return inicio, t


def construir(cfg, parte):
    voz, subs, planos, sfx = [], [], [], []
    t = 0.0
    spans = []  # (ini, fin, tramo|None, línea)
    # gancho
    for k, n in enumerate(cfg["gancho"]):
        if k:
            t += PAUSA
        a, b = colocar(n if isinstance(n, str) else n["n"], t, voz, subs)
        spans.append((a, b, "gancho", n))
        t = b
    fin_gancho = t
    # desarrollo
    for l in cfg["desarrollo"]:
        t += PAUSA_GOLPE if l["texto"] in BT.GOLPES else PAUSA
        a, b = colocar(l["n"], t, voz, subs)
        spans.append((a, b, l["tramo"], l))
        t = b
    t += PAUSA
    c0, c1 = colocar(cfg["cliff"], t, voz, subs)
    t = c1 + 0.9  # el candado se abre y el loop vuelve al inicio
    total = t
    num = cfg["num"]
    # ---- planos ----
    gi = cfg["gancho_img"]
    if len(gi) == 1:
        planos.append(dict(ini=0.0, fin=fin_gancho + 0.1, tipo="img", id=gi[0], cam="zoom"))
    else:
        mid = spans[0][1] + 0.05 if len(spans) > 1 and spans[0][2] == "gancho" and spans[1][2] == "gancho" else fin_gancho / 2
        planos.append(dict(ini=0.0, fin=mid, tipo="img", id=gi[0], cam="zoom"))
        planos.append(dict(ini=mid, fin=fin_gancho + 0.1, tipo="img", id=gi[1], cam="zoom"))
    usados_seq = {}
    pool = POOL[num]
    ultimo = planos[-1]["id"]
    s = planos[-1]["fin"]
    dev = [x for x in spans if x[2] != "gancho"]
    fin_dev = c0 - 0.1
    # tarjetas: posición fija
    tarjetas = []
    for a, b, tr, l in dev:
        for carta in [c for c in PLAN.get(tr, []) if c in CARTA_ANCLA or c == "ranking"]:
            if carta == "ranking":
                ls = [x for x in dev if x[2] == tr]
                r0 = ls[1][0] - 0.25
                tarjetas.append(dict(tipo="ranking", ini=r0, fin=ls[-1][1] + 0.05, barras=[ls[j][0] - r0 for j in (1, 2, 3)]))
                break
            ws = [w for w in subs if a - 0.01 <= w["ini"] <= b + 0.01]
            anc = [w for w in ws if w["w"].strip(".,") == CARTA_ANCLA[carta]]
            if anc and not any(x["tipo"] == carta for x in tarjetas):
                ini = anc[0]["ini"] - 0.35
                fin = min(ini + 3.4, max(b + 0.15, ini + 2.4))
                tarjetas.append(dict(tipo=carta, ini=ini, fin=fin))
    tarjetas.sort(key=lambda x: x["ini"])

    def tramo_en(tt):
        for a, b, tr, l in dev:
            if a - 0.3 <= tt <= b + 0.3:
                for k_, v_ in POR_LINEA.items():
                    if l["texto"].startswith(k_):
                        return ("linea", v_)
                return tr
        return dev[-1][2]

    usos = {}
    for g in gi:
        usos[g] = 99  # la del gancho queda reservada para el loop final

    def elegir(tr):
        nonlocal ultimo
        if isinstance(tr, tuple):
            propias = [tr[1]]
        else:
            propias = [c for c in PLAN.get(tr, []) if c not in CARTA_ANCLA and c != "ranking" and c in MAPA]
        cands = propias + [c for c in pool if c not in propias]
        # preferir las del tramo si se usaron menos de 2 veces; si no, la menos usada del bloque
        orden = sorted(cands, key=lambda c: (usos.get(c, 0) >= 2 if c in propias else 1, usos.get(c, 0), cands.index(c)))
        for c in orden:
            if c != ultimo:
                usos[c] = usos.get(c, 0) + 1
                ultimo = c
                return c
        return orden[0]

    cams = ["zoom", "zoom", "micro", "zoom", "paneo", "zoom"]
    nc = 0
    while s < fin_dev - 0.4:
        tj = next((x for x in tarjetas if x["ini"] <= s + 0.05 < x["fin"]), None)
        if tj:
            planos.append(dict(tj))
            s = tj["fin"]
            ultimo = tj["tipo"]
            continue
        prox_tarjeta = next((x["ini"] for x in tarjetas if x["ini"] > s), 1e9)
        limite = min(prox_tarjeta, fin_dev)
        # cortar en un inicio de línea entre 2,0 y 3,2 s; si no hay, a los 2,6 s
        bordes = [a for a, b, tr, l in dev if s + 2.0 <= a - 0.08 <= s + 3.2]
        e = (bordes[0] - 0.08) if bordes else s + 2.6
        e = min(e, limite)
        if limite - e < 1.2:
            e = limite if limite - s <= 3.5 else s + (limite - s) / 2
        tr = tramo_en((s + e) / 2)
        i = elegir(tr)
        planos.append(dict(ini=s, fin=e, tipo="img", id=i, cam=cams[nc % len(cams)], overlay=MAN[i]["overlay"]))
        if MAN[i]["overlay"]:
            sfx.append(dict(f="pop", t=s + 0.1, g=-10))
        nc += 1
        s = e
    # cambio de patrón a la mitad: reacción rápida con zoom 1.12
    mitad = total / 2
    k = min(range(len(planos)), key=lambda j: abs(planos[j]["ini"] - mitad) if planos[j]["tipo"] == "img" else 1e9)
    p = planos[k]
    reac = REACCION[num]
    if p["tipo"] == "img" and p["id"] != reac and p["fin"] - p["ini"] >= 2.2 and reac not in (planos[k - 1].get("id"), planos[k + 1].get("id") if k + 1 < len(planos) else None):
        corte = p["ini"] + 1.2
        planos.insert(k, dict(ini=p["ini"], fin=corte, tipo="img", id=reac, cam="zoom112"))
        p["ini"] = corte
        sfx.append(dict(f="whoosh", t=planos[k]["ini"], g=-12))
    # cliffhanger + loop: una imagen más del bloque y al final vuelve la imagen del gancho
    corte_loop = max(planos[-1]["fin"] + 1.0, total - 2.4)
    if corte_loop - planos[-1]["fin"] > 0.3:
        planos.append(dict(ini=planos[-1]["fin"], fin=corte_loop, tipo="img", id=elegir(dev[-1][2]), cam="zoom"))
    planos.append(dict(ini=planos[-1]["fin"], fin=total, tipo="img", id=gi[0], cam="zoom"))
    for j in range(1, len(planos)):
        planos[j]["ini"] = planos[j - 1]["fin"]
    sfx += [dict(f="golpe_piedra", t=0.02, g=-12), dict(f="whoosh", t=fin_gancho, g=-12), dict(f="pop", t=c0 + 0.1, g=-10),
            dict(f="clic", t=total - 0.8, g=-5)]
    for tj in tarjetas:
        if tj["tipo"] != "ranking":
            sfx.append(dict(f="ding", t=tj["ini"] + 0.1, g=-10))
    for f, frac in cfg.get("sfx_extra", []):
        sfx.append(dict(f=f, t=total * frac, g=-12))
    insignia = dict(num=num, nombre=cfg["nombre"], abiertos=[i for i in range(7) if 7 - i > num], actual=7 - num, abre_en=total - 0.8,
                    cliff_ini=c0, cliff_texto=("PARTE 7 DE 7 · VIDEO COMPLETO EN MI CANAL" if num == 1 else f"PARTE {parte} DE 7 · SIGUE EN MI CANAL"))
    tl = dict(fps=30, ancho=1080, alto=1920, duracion=round(total, 3), voz=voz, subs=subs, planos=planos, sfx=sfx,
              musica=[dict(f="musica_misterio", ini=0.0, fin=total)], silencios=[], hud=[], insignia=insignia)
    return tl


def construir_gancho():
    voz, subs, planos, sfx = [], [], [], []
    t = 0.0
    spans = {}
    for l in [x for x in LINEAS if x["tramo"] <= 7]:
        if l["n"] > 1:
            t += PAUSA_GOLPE if l["texto"] in BT.GOLPES else PAUSA
        a, b = colocar(l["n"], t, voz, subs)
        spans.setdefault(l["tramo"], [a, b])[1] = b
        t = b
    total = t + 1.4
    grupos = {0: range(0, 5), 1: range(5, 8), 2: range(8, 12), 3: range(12, 15), 4: range(15, 19), 5: range(19, 23), 6: range(23, 26), 7: range(26, 29)}
    for tr, rg in grupos.items():
        a = spans[tr][0] if tr else 0.0
        b = spans[tr + 1][0] if tr < 7 else total - 1.4
        items = [BT.GANCHO[i] for i in rg]
        tot = sum(x["segundos"] for x in items)
        cur = a
        for x in items:
            d = (b - a) * x["segundos"] / tot
            planos.append(dict(ini=cur, fin=cur + d, tipo="img", id=x["imagen"][:3], cam="micro",
                               overlay=x["overlay"] if x["overlay"] and "parpadea" not in x["overlay"] else ""))
            cur += d
    planos.append(dict(ini=total - 1.4, fin=total, tipo="img", id="004", cam="zoom", overlay="MAÑANA: FORMA #7 · SIGUE EN MI CANAL"))
    for j in range(1, len(planos)):
        planos[j]["ini"] = planos[j - 1]["fin"]
    i14 = next(p for p in planos if p["id"] == "014")
    sfx += [dict(f="latido", t=0.05, g=-6), dict(f="siete_clics", t=i14["ini"] + 0.15, g=-8), dict(f="bostezo", t=spans[3][0] + 0.2, g=-9)]
    return dict(fps=30, ancho=1080, alto=1920, duracion=round(total, 3), voz=voz, subs=subs, planos=planos, sfx=sfx,
                musica=[dict(f="musica_misterio", ini=0.0, fin=total)], silencios=[], hud=[], insignia=None)


if __name__ == "__main__":
    indice = []
    for parte, cfg in enumerate(SERIE, 1):
        tl = construir(cfg, parte)
        (OUT / f"short_{cfg['slug'][:2]}.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1))
        d = [p["fin"] - p["ini"] for p in tl["planos"]]
        rep = sum(1 for a, b in zip(tl["planos"], tl["planos"][1:]) if a.get("id") and a.get("id") == b.get("id"))
        print(f"#{cfg['num']} {tl['duracion']:.1f} s, {len(d)} planos, media {sum(d) / len(d):.2f}, máx {max(d):.1f} "
              f"({tl['planos'][d.index(max(d))]['tipo']}), repetidas seguidas {rep}")
        indice.append(dict(id=f"short_{cfg['slug'][:2]}", slug=cfg["slug"], duracion=tl["duracion"]))
    g = construir_gancho()
    (OUT / "short_00.json").write_text(json.dumps(g, ensure_ascii=False, indent=1))
    indice.insert(0, dict(id="short_00", slug="00_gancho", duracion=g["duracion"]))
    print(f"#0 gancho {g['duracion']:.1f} s, {len(g['planos'])} planos")
    (OUT / "indice.json").write_text(json.dumps(indice, ensure_ascii=False, indent=1))
    # imágenes para regenerar en vertical: bloques con menos de 4 tipo B
    lineas = ["Bloques con menos de 4 imágenes verticales completas (tipo B). Conviene rehacer en vertical estos ids:"]
    for num, ids in POOL.items():
        b = [i for i in ids if TIPO.get(i) == "B"]
        if len(b) < 4:
            lineas.append(f"\n#{num} ({len(b)} tipo B): " + ", ".join(f"{i} {MAN[i]['file']}" for i in ids if TIPO.get(i) == "A"))
    (R / "work/regenerar_vertical.txt").write_text("\n".join(lineas) + "\n")
