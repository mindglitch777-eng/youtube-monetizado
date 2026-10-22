#!/usr/bin/env python3
"""Arma work/timeline.json (video largo) y work/timeline_short.json a partir de:
guion (work/beats_guion.json), voz medida (work/voz/*.json), imágenes (work/mapa.json) y manifest.
La duración REAL de la voz manda: todos los tiempos salen de los audios medidos."""
import json
import re
from pathlib import Path

R = Path(__file__).resolve().parent.parent
FPS = 30
BEATS = json.loads((R / "work/beats_guion.json").read_text())
LINEAS = json.loads((R / "work/voz_lineas.json").read_text())["lineas"]
VOZ = {l["n"]: json.loads((R / f"work/voz/{l['n']:03d}.json").read_text()) for l in LINEAS}
MAN = {x["id"]: x for x in json.loads((R / "manifest_imagenes.json").read_text())["imagenes"]}
MAPA = json.loads((R / "work/mapa.json").read_text())
INFO = json.loads((R / "work/img_info.json").read_text())
GANCHO = json.loads((R / "manifest_imagenes.json").read_text())["montaje_gancho"]

PAUSA_LINEA, PAUSA_TRAMO, PAUSA_GOLPE = 0.30, 0.38, 0.60
GOLPES = ("Es mentira.", "La número uno ni siquiera la ves.")
DUR_NUMERO, DUR_CANDADO = 2.0, 2.6
BLOQUES = {8: (7, "SIN AGUA"), 18: (6, "GRANDES ANIMALES"), 28: (5, "LO QUE COMES"), 37: (4, "LA NOCHE"),
           46: (3, "OTRAS PERSONAS"), 53: (2, "UN RASGUÑO"), 61: (1, "LOS GÉRMENES")}
# candado k se abre en el tramo t, con la hora del reloj y la imagen de fondo
CANDADOS = {17: (1, "9:00", "026"), 27: (2, "12:00", "035"), 36: (3, "19:00", "044"), 45: (4, "22:00", None),
            52: (5, "3:00", "058"), 60: (6, "7:00", "066"), 70: (7, None, None)}
# imágenes por tramo (ids del manifest). "dato12/dato8/dato10/ranking/reloj_roto/collage" son tarjetas hechas en código.
PLAN = {
    9: ["018"], 10: ["019"], 11: ["020", "086"], 12: ["021"], 13: ["022"], 14: ["023", "087"], 15: ["024"], 16: ["088", "025"],
    19: ["027"], 20: ["028"], 21: ["029", "030"], 22: ["090", "031"], 23: ["032", "092"], 24: ["011", "dato12"], 25: ["033", "091"],
    26: ["089"], 29: ["036"], 30: ["093", "037"], 31: ["094", "038"], 32: ["039", "040"], 33: ["041"], 34: ["042"],
    35: ["095", "043"], 38: ["045"], 39: ["046"], 40: ["047", "097"], 41: ["048", "100"], 42: ["098", "049"], 43: ["050"],
    44: ["099", "051"], 47: ["052", "053", "102"], 48: ["054", "103", "055"], 49: ["101", "dato8"], 50: ["056", "057"],
    51: ["058"], 54: ["104", "059", "060", "061"], 55: ["062", "071"], 56: ["063"], 57: ["064", "105"], 58: ["065"], 59: ["066"],
    62: ["067"], 63: ["068"], 64: ["016", "069"], 65: ["dato10"], 66: ["070", "106"], 67: ["071"], 68: ["072"], 69: ["073"],
    71: ["ranking"], 72: ["074", "reloj_roto"], 73: ["107", "075"], 74: ["108", "076", "077", "109"], 75: ["078"], 76: ["079"],
    77: ["080", "081", "082", "083"], 78: ["084"], 79: ["collage"], 80: ["085", "final"],
}
REACCION = {k for k, v in MAN.items() if v["tipo"] == "reaccion"}
# El 071 (sin vacunas) se reserva para el #1; en el tramo 55 lo cambio por la reacción del bloque
PLAN[55] = ["062", "105"]
PLAN[57] = ["064"]
# León escondido: posición aproximada en la imagen original (fracción de ancho y alto)
LEONES = {"020": (0.72, 0.51), "038": (0.27, 0.475), "053": (0.33, 0.55), "062": (0.83, 0.56), "070": (0.92, 0.56), "050": (0.85, 0.79)}


def clip(n):
    p = VOZ[n]["palabras"]
    a = max(0.0, p[0]["ini"] - 0.04)
    b = p[-1]["fin"] + 0.06
    return a, b


def palabras_display(n, t0):
    """Tiempos absolutos por palabra usando el texto original (con números) y la voz medida."""
    p = VOZ[n]["palabras"]
    a, b = clip(n)
    toks = re.findall(r"\S+", VOZ[n]["texto"])
    if len(toks) == len(p):
        return [dict(w=tk, ini=t0 + w["ini"] - a, fin=t0 + w["fin"] - a) for tk, w in zip(toks, p)]
    ini, fin = p[0]["ini"] - a, p[-1]["fin"] - a
    largo = sum(len(re.sub(r"\W", "", tk)) or 1 for tk in toks)
    out, cur = [], ini
    for tk in toks:
        d = (fin - ini) * (len(re.sub(r"\W", "", tk)) or 1) / largo
        out.append(dict(w=tk, ini=t0 + cur, fin=t0 + cur + d))
        cur += d
    return out


def img_info16(i):
    """Transformación imagen original -> cuadro 1920x1080 (igual que preparar_imagenes.py)."""
    v = INFO[MAPA[i]["archivo_original"]]
    if v["tipo"] == "A":
        bw, bh = 768, v["bottom"] - v["top"]
        r = bw / bh
        s = max(1920 / bw, 1080 / bh) if abs(r / (16 / 9) - 1) < 0.12 else min(1920 / bw, 1080 / bh)
        ox, oy = (1920 - bw * s) / 2, (1080 - bh * s) / 2
        return lambda fx, fy: (ox + fx * 768 * s, oy + (fy * 1376 - v["top"]) * s)
    s = 1080 / 1376
    ox = (1920 - 768 * s) / 2
    return lambda fx, fy: (ox + fx * 768 * s, fy * 1376 * s)


def construir_largo():
    voz, subs, planos, sfx, tarjetas = [], [], [], [], []
    t = 0.0
    tramo_ini = {}
    linea_ini = {}
    por_tramo = {}
    for l in LINEAS:
        por_tramo.setdefault(l["tramo"], []).append(l)
    for bi, b in enumerate(BEATS):
        if bi > 0:
            t += PAUSA_TRAMO
        tramo_ini[bi] = t
        if bi in BLOQUES:
            t += DUR_NUMERO
            continue
        if bi in CANDADOS:
            t += DUR_CANDADO + (0.6 if bi == 70 else 0)
            continue
        for k, l in enumerate(por_tramo.get(bi, [])):
            if k > 0:
                t += PAUSA_LINEA
            if l["texto"] in GOLPES:
                t += PAUSA_GOLPE - PAUSA_LINEA
            a, bb = clip(l["n"])
            voz.append(dict(n=l["n"], ini=round(t, 3), src_ini=round(a, 3), dur=round(bb - a, 3)))
            linea_ini[l["n"]] = t
            for w in palabras_display(l["n"], t):
                subs.append(w)
            t += bb - a
    tramo_ini[len(BEATS)] = t + 0.4
    total = t + 1.6  # cola para la pantalla final

    def fin_tramo(bi):
        return tramo_ini[bi + 1] if bi + 1 < len(BEATS) else total

    # ---- gancho: montaje del manifest, escalado a la voz de cada tramo ----
    grupos = {0: range(0, 5), 1: range(5, 8), 2: range(8, 12), 3: range(12, 15), 4: range(15, 19), 5: range(19, 23), 6: range(23, 26), 7: range(26, 30)}
    for bi, rg in grupos.items():
        a, b = tramo_ini[bi], fin_tramo(bi)
        items = [GANCHO[i] for i in rg]
        tot = sum(x["segundos"] for x in items)
        cur = a
        for x in items:
            d = (b - a) * x["segundos"] / tot
            idimg = x["imagen"][:3] if x["imagen"] else None
            planos.append(dict(ini=cur, fin=cur + d, tipo="img" if idimg else "negro", id=idimg, cam="microzoom",
                               overlay=x["overlay"] if x["overlay"] and "parpadea" not in x["overlay"] else "",
                               parpadeo=bool(x["overlay"] and "parpadea" in x["overlay"]), gancho=True))
            if idimg == "014":
                sfx.append(dict(f="siete_clics", t=cur + 0.15, g=-8))
            cur += d
    sfx += [dict(f="latido", t=0.05, g=-6), dict(f="golpe_piedra", t=linea_ini[2], g=-10), dict(f="bostezo", t=tramo_ini[3] + 0.2, g=-9),
            dict(f="tictac", t=tramo_ini[1] + 0.6, g=-12)]

    # ---- resto de los tramos ----
    camaras = ["fijo", "zoom", "fijo", "paneo", "fijo", "zoom", "fijo", "zoom", "fijo", "paneo"]
    ncam = 0
    for bi, b in enumerate(BEATS):
        a, z = tramo_ini[bi], fin_tramo(bi)
        if bi < 8:
            continue
        if bi in BLOQUES:
            num, nombre = BLOQUES[bi]
            planos.append(dict(ini=a, fin=z, tipo="numero", num=num, nombre=nombre))
            sfx.append(dict(f="whoosh", t=a, g=-12))
            sfx.append(dict(f="golpe_fuerte" if num == 1 else "golpe_piedra", t=a + 0.4, g=-6 if num == 1 else -8))
            continue
        if bi in CANDADOS:
            k, hora, fondo = CANDADOS[bi]
            planos.append(dict(ini=a, fin=z, tipo="candados", abre=k, hora=hora, fondo=fondo))
            if k < 7:
                sfx.append(dict(f="clic", t=a + 0.7, g=-6))
                sfx.append(dict(f="tictac", t=a + 0.2, g=-12))
            else:
                for j in range(7):
                    sfx.append(dict(f="clic", t=a + 0.4 + 0.12 * j, g=-8))
                sfx.append(dict(f="acorde_asombro", t=a + 1.3, g=-8))
            continue
        ids = PLAN[bi]
        lns = por_tramo.get(bi, [])
        # cortes alineados al inicio de las líneas cuando se puede
        fijos = [i for i in ids if i in REACCION]
        n_norm = len(ids)
        cortes = [a]
        if len(lns) >= n_norm and n_norm > 1:
            for j in range(1, n_norm):
                ln = lns[round(j * len(lns) / n_norm)]
                cortes.append(linea_ini[ln["n"]] - 0.08)
        else:
            dur_r = 1.2
            libre = (z - a) - dur_r * len(fijos)
            normales = n_norm - len(fijos)
            cur = a
            for i in ids[:-1]:
                cur += dur_r if i in REACCION else libre / max(1, normales)
                cortes.append(cur)
        cortes.append(z)
        for j, i in enumerate(ids):
            ini, fin = cortes[j], cortes[j + 1]
            segs = [(ini, fin)]
            if i not in ("dato12", "dato8", "dato10", "ranking", "collage", "final", "reloj_roto") and fin - ini > 6.0:
                n = int((fin - ini) // 4.5) + 1
                segs = [(ini + (fin - ini) * q / n, ini + (fin - ini) * (q + 1) / n) for q in range(n)]
            for q, (s0, s1) in enumerate(segs):
                if i in ("dato12", "dato8", "dato10", "ranking", "reloj_roto", "collage", "final"):
                    pl = dict(ini=s0, fin=s1, tipo=i)
                else:
                    cam = "zoomout" if (i == "084") else camaras[ncam % len(camaras)]
                    ncam += 1
                    ov = MAN[i]["overlay"] if q == 0 else ""
                    pl = dict(ini=s0, fin=s1, tipo="img", id=i, cam=cam, overlay=ov)
                    if ov:
                        sfx.append(dict(f="pop", t=s0 + 0.1, g=-10))
                planos.append(pl)
    # whoosh en algunos cortes grandes (cambio de escena tras tarjeta)
    # datos
    for p in planos:
        if p["tipo"] in ("dato12", "dato8", "dato10"):
            sfx.append(dict(f="ding", t=p["ini"] + 0.15, g=-10))
        if p["tipo"] == "reloj_roto":
            sfx.append(dict(f="vidrio_roto", t=p["ini"] + 0.6, g=-8))
    # ranking: barras sincronizadas con las líneas 2-4 del tramo 71
    l71 = por_tramo[71]
    for p in planos:
        if p["tipo"] == "ranking":
            p["barras"] = [linea_ini[l71[j]["n"]] - p["ini"] for j in (1, 2, 3)]
    # collage de leones
    for p in planos:
        if p["tipo"] == "collage":
            items = []
            for i, (fx, fy) in LEONES.items():
                x, y = img_info16(i)(fx, fy)
                items.append(dict(id=i, x=round(x), y=round(y)))
            p["items"] = items
    sfx.append(dict(f="viento", t=tramo_ini[16], g=-12))
    sfx.append(dict(f="respiracion", t=tramo_ini[42] + 1.5, g=-10))
    # ---- música: misterio con cortes; cálida en el cierre ----
    l74 = por_tramo[74][0]
    l76 = [l for l in por_tramo[76] if l["texto"].startswith("Casi todo eso")][0]
    silencios = [(tramo_ini[59] + 0.6, tramo_ini[61] + 1.4),               # "la música se corta" hasta después del golpe del #1
                 (linea_ini[l74["n"]] - 0.4, linea_ini[l74["n"]] + 1.2),    # "Es mentira."
                 (linea_ini[l76["n"]] - 0.2, linea_ini[l76["n"]] + 2.4)]    # "Casi todo eso lo resolvía tu grupo"
    musica = [dict(f="musica_misterio", ini=0.0, fin=tramo_ini[72]), dict(f="musica_calida", ini=tramo_ini[72], fin=total)]
    # HUD de candados: bloque k (1..7) activo desde su tarjeta hasta su candado
    hud = []
    orden = sorted(BLOQUES)
    for j, bi in enumerate(orden):
        cand = [c for c, v in CANDADOS.items() if v[0] == j + 1][0]
        hud.append(dict(ini=tramo_ini[bi] + DUR_NUMERO, fin=tramo_ini[cand], abiertos=j))
    tl = dict(fps=FPS, ancho=1920, alto=1080, duracion=round(total, 3), voz=voz, subs=subs, planos=planos, sfx=sfx,
              musica=musica, silencios=silencios, hud=hud)
    (R / "work/timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1))
    durs = [p["fin"] - p["ini"] for p in planos]
    print(f"largo: {total:.1f} s ({int(total // 60)}:{total % 60:04.1f}), {len(planos)} planos, máx {max(durs):.1f} s, "
          f"media fuera del gancho {sum(d for p, d in zip(planos, durs) if not p.get('gancho')) / sum(1 for p in planos if not p.get('gancho')):.2f} s")
    return tl, linea_ini, tramo_ini, por_tramo


def construir_short(linea_ini_largo):
    """Short 9:16: se reutilizan frases de la misma voz, re-espaciadas."""
    por_n = {l["n"]: l for l in LINEAS}

    def n_de(texto):
        return [l["n"] for l in LINEAS if l["texto"].startswith(texto)][0]

    voz, subs, planos, sfx = [], [], [], []
    t = 0.0

    def decir(texto, pausa=0.25):
        nonlocal t
        n = n_de(texto)
        a, b = clip(n)
        voz.append(dict(n=n, ini=round(t, 3), src_ini=round(a, 3), dur=round(b - a, 3)))
        subs.extend(palabras_display(n, t))
        t0 = t
        t += (b - a) + pausa
        return t0, t

    # 1. gancho extremo
    a0, _ = decir("Cierras los ojos en tu cama.", 0.1)
    a1, b1 = decir("Los abres", 0.3)
    planos += [dict(ini=0, fin=a1, tipo="img", id="004", cam="microzoom"), dict(ini=a1, fin=a1 + 1.0, tipo="img", id="005", cam="microzoom"),
               dict(ini=a1 + 1.0, fin=b1, tipo="img", id="006", cam="microzoom", overlay="HACE 20.000 AÑOS")]
    sfx += [dict(f="latido", t=0.05, g=-6), dict(f="golpe_piedra", t=a1, g=-10), dict(f="pop", t=a1 + 1.1, g=-10)]
    # 2. los 6 primeros candados, rápido
    c0, c1 = decir("Hoy cuento las 7 formas de morir", 0.2)
    planos.append(dict(ini=c0, fin=c1, tipo="img", id="014", cam="microzoom"))
    sfx.append(dict(f="siete_clics", t=c0 + 0.2, g=-8))
    rapido = [("018", "SIN AGUA"), ("027", "GRANDES ANIMALES"), ("038", "LO QUE COMES"), ("049", "LA NOCHE"), ("054", "OTRAS PERSONAS"), ("064", "UN RASGUÑO")]
    for k, (i, nombre) in enumerate(rapido):
        planos.append(dict(ini=t, fin=t + 2.4, tipo="img", id=i, cam="microzoom", overlay=f"#{7 - k} {nombre}", candado=k + 1))
        sfx += [dict(f="clic", t=t + 1.6, g=-6), dict(f="pop", t=t + 0.1, g=-12)]
        t += 2.4
    # 3. la #1
    planos.append(dict(ini=t, fin=t + 1.6, tipo="numero", num=1, nombre="LOS GÉRMENES"))
    sfx += [dict(f="golpe_fuerte", t=t + 0.4, g=-6)]
    t += 1.8
    g0, _ = decir("No tiene colmillos", 0.2)
    _, g1 = decir("Ni siquiera la puedes ver.", 0.25)
    planos.append(dict(ini=g0 - 0.2, fin=g1, tipo="img", id="067", cam="zoom"))
    h0, _ = decir("Son los gérmenes.", 0.15)
    _, h1 = decir("La enfermedad.", 0.25)
    planos.append(dict(ini=h0, fin=h1, tipo="img", id="068", cam="microzoom"))
    r0, r1 = decir("¿Recuerdas tu apuesta?", 0.25)
    planos.append(dict(ini=r0, fin=r1, tipo="img", id="069", cam="microzoom"))
    k0, _ = decir("El ranking de verdad.", 0.25)
    bar = [decir(x, 0.3)[0] for x in ("Enfermedad: 7 de cada 10", "Violencia: 1 de cada 8", "Accidentes, con el león incluido")]
    planos.append(dict(ini=k0, fin=t, tipo="ranking", barras=[x - k0 for x in bar]))
    # 4. cierre
    d0, _ = decir("¿Cuánto duras tú?", 0.2)
    _, d1 = decir("Yo diría que unas 20 horas", 0.3)
    planos.append(dict(ini=d0, fin=d1, tipo="img", id="074", cam="microzoom", overlay="TÚ DURAS ~20 HORAS"))
    sfx.append(dict(f="pop", t=d0 + 0.1, g=-10))
    e0, _ = decir("Seguro oíste que en la Edad de Piedra", 0.5)
    planos.append(dict(ini=e0, fin=t, tipo="img", id="075", cam="microzoom"))
    m0, m1 = decir("Es mentira.", 0.3)
    planos.append(dict(ini=m0 - 0.1, fin=m1, tipo="img", id="109", cam="zoom"))
    f0, _ = decir("Tu mejor arma no era la lanza.", 0.2)
    _, f1 = decir("Era tu gente.", 0.3)
    planos.append(dict(ini=f0, fin=f1, tipo="img", id="079", cam="zoom"))
    # 5. cierre: video completo
    planos.append(dict(ini=t, fin=t + 4.5, tipo="cta"))
    sfx.append(dict(f="whoosh", t=t, g=-10))
    t += 4.5
    musica = [dict(f="musica_misterio", ini=0.0, fin=t)]
    silencios = [(m0 - 0.3, m0 + 1.0)]
    tl = dict(fps=FPS, ancho=1080, alto=1920, duracion=round(t, 3), voz=voz, subs=subs, planos=planos, sfx=sfx, musica=musica,
              silencios=silencios, hud=[])
    (R / "work/timeline_short.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1))
    print(f"short: {t:.1f} s, {len(planos)} planos")


if __name__ == "__main__":
    tl, linea_ini, tramo_ini, por_tramo = construir_largo()
    construir_short(linea_ini)
