#!/usr/bin/env python3
"""
Arma la línea de tiempo del video largo del video 2.

Lee la voz ya recortada (work/voz.json), el manifest de imágenes y las reglas
de la instrucción de edición, y escribe:
  - remotion/src/data/v2/largo.json : todo lo que se dibuja (planos, textos, HUD, carteles)
  - video2/work/largo_audio.json    : dónde va cada línea de voz, cada efecto y la música

Las líneas ⚑ (solo para Shorts) no van en el largo.
"""
import json
import re
import unicodedata
from pathlib import Path

V = Path(__file__).resolve().parent.parent
R = V.parent
VOZ = json.loads((V / "work" / "voz.json").read_text())
MAN = json.loads((V / "docs" / "manifest_imagenes_v2.json").read_text())["imagenes"]
REC = json.loads((V / "work" / "recortes.json").read_text())

BLOQUES = ["H", "E1", "E2", "E3", "E4", "M", "E5", "E6", "E7", "E8", "C"]
MBLOQUE = {"H": "H", "E1": "1", "E2": "2", "E3": "3", "E4": "4", "M": "M", "E5": "5", "E6": "6", "E7": "7", "E8": "8", "C": "C"}
GAP = 0.08            # aire entre líneas (pedido: sin silencios)
REMATE = 0.3          # pausa corta antes de un remate
FREEZE = 0.5          # congelado antes de una muerte
NEGRO = 0.15          # golpe a negro (SMASH)
REMATES = {"H_06", "E1_12", "E3_11", "E4_11", "E5_14", "E7_14"}
SILENCIO_LARGO = {"E6_19": 2.0}   # Tenochtitlan: dos segundos de silencio antes del "no voy a hacer ningún chiste"

EPOCAS = {
    "E1": dict(n=1, jefe="EL FRÍO", muerte="E1_13", tiempo="2 H 14 MIN", culpable="EL FRÍO", nota="F", estilo="hielo",
               logro="MORIR CONGELADO EN PIJAMA", aura=-67, logro_linea="E1_14", puente=None),
    "E2": dict(n=2, jefe="LA REUNIÓN DE LUNES", muerte="E2_12", tiempo="41 AÑOS", culpable="LA VEJEZ", nota="A", estilo="egipto",
               logro="NIVEL TUTORIAL COMPLETADO", aura=1000, logro_linea="E2_13", puente="249"),
    "E3": dict(n=3, jefe="EL VESUBIO", muerte="E3_15", tiempo="19 HORAS", culpable="LA CURIOSIDAD", nota="D", estilo="pompeya",
               logro="MIRAR UN VOLCÁN DE CERCA", aura=0, logro_linea="E3_16", puente="250"),
    "E4": dict(n=4, jefe="UN LEÓN CON BARBIJO", muerte="E4_16", tiempo="6:07", culpable="EL ESPECTÁCULO", nota="C", estilo="roma",
               logro="CULPABLE: EL ESPECTÁCULO", aura=0, logro_linea=None, puente="251"),
    "E5": dict(n=5, jefe="UNA PULGA", muerte="E5_15", tiempo="11 DÍAS", culpable="UNA PULGA", nota="F", estilo="1348",
               logro="CULPABLE: UNA PULGA", aura=0, logro_linea=None, puente=None),
    "E6": dict(n=6, jefe="???", muerte="E6_18", tiempo="9 MESES", culpable="LA VIRUELA", nota="B", estilo="tenochtitlan",
               logro="CULPABLE: LA VIRUELA", aura=0, logro_linea=None, puente=None),
    "E7": dict(n=7, jefe="UN VERANO QUE NO LLEGA", muerte="E7_12", tiempo="17 DÍAS", culpable="EL HAMBRE", nota="D", estilo="1816",
               logro="CULPABLE: EL HAMBRE", aura=0, logro_linea=None, puente=None),
    "E8": dict(n=8, jefe="UN VASO DE AGUA", muerte="E8_17", tiempo="3 DÍAS", culpable="UN VASO DE AGUA", nota="F", estilo="londres",
               logro="CULPABLE: UN VASO DE AGUA", aura=0, logro_linea=None, puente=None),
}
NOMBRE_EPOCA = {"E1": "HIELO", "E2": "EGIPTO", "E3": "POMPEYA", "E4": "ROMA", "E5": "1348", "E6": "TENOCHTITLAN", "E7": "1816", "E8": "LONDRES"}
MUSICA = {"H": "mus_gancho", "E1": "mus_hielo", "E2": "mus_egipto", "E3": "mus_pompeya", "E4": "mus_roma", "M": "mus_gancho",
          "E5": "mus_1348", "E6": "mus_tenochtitlan", "E7": "mus_1816", "E8": "mus_londres", "C": "mus_cierre"}
AMBIENTE = {"E1": "amb_hielo", "E2": "amb_egipto", "E3": "amb_pompeya", "E4": "amb_roma", "E5": "amb_1348",
            "E6": "amb_tenochtitlan", "E7": "amb_1816", "E8": "amb_londres"}
# imágenes sin frase propia en el guion v3, ubicadas a mano: línea -> [(proporción, id, overlay o None)]
EXTRA = {"E4_05": [(0.0, "095", None), (0.45, "097", "REPETICIÓN")], "E2_08": [(0.5, "062", None)], "E2_12": [(0.0, "072", "41 AÑOS")]}
# overlays del manifest que ya dibuja otro componente (logro, tabla) o que no van
SIN_OVERLAY = {"049", "071", "092", "197"}


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.findall(r"[a-z0-9]+", s)


def lineas_de(bloque):
    return [(k, v) for k, v in VOZ.items() if v["bloque"] == bloque]


def posicion(quote, linea_txt):
    """Índice (proporción 0..1) donde empieza la cita dentro de la línea, o None si no está."""
    q, l = norm(quote), norm(linea_txt)
    if not q:
        return None
    for i in range(len(l)):
        if l[i:i + min(3, len(q))] == q[:min(3, len(q))]:
            return i / max(1, len(l))
    inter = len(set(q) & set(l)) / len(set(q))
    return 0.0 if inter >= 0.6 else None


def asignar_imagenes():
    """Para cada línea del largo: lista de (proporción_inicio, imagen) en orden."""
    por_linea = {}
    for img in MAN:
        b = [k for k, v in MBLOQUE.items() if v == img["block"]]
        if not b or img["tipo"] != "imagen" or img["id"] not in REC:
            continue
        mejor = None
        for k, v in lineas_de(b[0]):
            if v["solo_short"]:
                continue
            p = posicion(img["quote"], v["texto"])
            if p is not None:
                mejor = (k, p)
                break
        if mejor:
            por_linea.setdefault(mejor[0], []).append([mejor[1], img])
    porid = {i["id"]: i for i in MAN}
    for k, lst in EXTRA.items():
        if k == "E4_05":
            por_linea[k] = []
        for prop, iid, ov in lst:
            img = dict(porid[iid])
            if ov is not None:
                img["overlay"] = ov
            por_linea.setdefault(k, []).append([prop, img])
    # imágenes con la misma cita (ej. mamut/volcán/león/pulga): se reparten el tramo de la cita
    for k, lst in por_linea.items():
        grupos = {}
        for item in lst:
            grupos.setdefault(item[0], []).append(item)
        orden = sorted(grupos)
        for gi, p in enumerate(orden):
            sig = orden[gi + 1] if gi + 1 < len(orden) else 1.0
            g = grupos[p]
            for j, item in enumerate(g):
                item[0] = p + (sig - p) * j / len(g)
        lst.sort(key=lambda it: it[0])
    return por_linea


def tiempo_en_linea(k, prop):
    pal = VOZ[k]["palabras"]
    if prop <= 0 or not pal:
        return 0.0
    i = min(len(pal) - 1, int(round(prop * len(pal))))
    return max(0.0, pal[i]["ini"] - 0.05)


def main():
    por_linea = asignar_imagenes()
    planos, textos, carteles, hud, color, audio = [], [], [], [], [], {"voz": [], "sfx": [], "musica": [], "ambiente": [], "silencios": []}
    t = 0.0
    vidas, aura, epoca_n, vida_txt = 8, 0, 0, ""
    usados = []

    def plano(ini, tipo, **kw):
        if planos:
            planos[-1]["fin"] = round(ini, 3)
        planos.append({"ini": round(ini, 3), "fin": None, "tipo": tipo, **kw})

    def estado_hud(ini):
        hud.append({"ini": round(ini, 3), "epoca": epoca_n, "vidas": vidas, "aura": aura, "vida": vida_txt})

    def sfx(nombre, ini, gain=1.0):
        audio["sfx"].append({"t": round(ini, 3), "nombre": nombre, "gain": gain})

    def transicion(ini, n_epoca, puente):
        """timbre → negro → (puente) → 'ÉPOCA N DE 8' → flash. Devuelve el tiempo final."""
        lento = n_epoca in (6, 7)
        sfx("timbre_lento" if lento else "timbre", ini, 0.8)
        plano(ini, "negro")
        x = ini + 0.15
        if puente:
            plano(x, "img", id=puente, cam="zoom", tr="", epoca=n_epoca - 1)
            x += 0.45
        plano(x, "titulo_epoca", texto=f"ÉPOCA {n_epoca} DE 8")
        sfx("whoosh", x, 0.6)
        x += 0.75
        sfx("flash", x - 0.1, 0.7)
        return x

    def separador(ini, e):
        d = EPOCAS[e]
        sfx("timbre_lento" if d["n"] in (5, 6) else "timbre", ini, 0.8)
        plano(ini, "negro")
        plano(ini + 0.12, "fin", culpable=d["culpable"], nota=d["nota"], tiempo=d["tiempo"], epoca=d["n"])
        sfx("logro", ini + 0.3, 0.5)
        return ini + 0.12 + 1.5

    estado_hud(0)
    audio["musica"].append({"ini": 0.0, "nombre": MUSICA["H"]})
    for b in BLOQUES:
        # ---------------------------------------------------- entrada al bloque
        if b in EPOCAS:
            d = EPOCAS[b]
            if b in ("E1", "E5"):
                t = transicion(t, d["n"], d["puente"])
            epoca_n = d["n"]
            vida_txt = ""
            estado_hud(t)
            color.append({"ini": round(t, 3), "estilo": d["estilo"]})
            carteles.append({"ini": round(t + 0.35, 3), "fin": round(t + 1.85, 3), "tipo": "jefe", "texto": f"JEFE: {d['jefe']}"})
            sfx("juego", t + 0.35, 0.5)
            if b == "E1":
                carteles.append({"ini": round(t + 2.0, 3), "fin": round(t + 4.0, 3), "tipo": "simulacion", "texto": "TIEMPOS DE PIJAMA = SIMULACIÓN"})
            audio["musica"].append({"ini": round(t, 3), "nombre": MUSICA[b]})
            audio["ambiente"].append({"ini": round(t, 3), "nombre": AMBIENTE[b]})
        elif b == "M":
            color.append({"ini": round(t, 3), "estilo": "juego"})
            carteles.append({"ini": round(t + 0.2, 3), "fin": round(t + 2.2, 3), "tipo": "simulacion", "texto": "TIEMPOS DE PIJAMA = SIMULACIÓN"})
            audio["musica"].append({"ini": round(t, 3), "nombre": MUSICA["M"]})
            audio["ambiente"].append({"ini": round(t, 3), "nombre": None})
        elif b == "C":
            epoca_n = 0  # en casa no hay HUD
            estado_hud(t)
            color.append({"ini": round(t, 3), "estilo": "casa"})
            audio["musica"].append({"ini": round(t, 3), "nombre": MUSICA["C"]})
            audio["ambiente"].append({"ini": round(t, 3), "nombre": None})
            sfx("canilla", t + 2.0, 0.35)
        if b == "H":
            color.append({"ini": 0.0, "estilo": "gancho"})

        for k, v in lineas_de(b):
            if v["solo_short"]:
                continue
            # ------------------------------------------------ pausas y muertes antes de la línea
            es_muerte = b in EPOCAS and EPOCAS[b]["muerte"] == k
            if k in SILENCIO_LARGO:
                audio["silencios"].append({"ini": round(t, 3), "fin": round(t + SILENCIO_LARGO[k], 3)})
                t += SILENCIO_LARGO[k]
            elif k in REMATES:
                t += REMATE
            if es_muerte:
                if planos:
                    planos[-1]["congelar"] = round(t, 3)
                t += FREEZE
                plano(t, "negro")
                sfx("smash", t, 1.0)
                sfx("timbre_lento" if EPOCAS[b]["n"] in (5, 6) else "timbre", t, 0.6)
                t += NEGRO
            # ------------------------------------------------ planos de la línea
            imgs = por_linea.get(k, [])
            for prop, img in imgs:
                ini = t + tiempo_en_linea(k, prop)
                tr = img["tr"].split(":")[0].strip()
                plano(ini, "img", id=img["id"], cam=img["cam"], tr=tr, epoca=epoca_n, linea=k)
                usados.append(img["id"])
                if img["overlay"] and img["id"] not in SIN_OVERLAY:
                    textos.append({"ini": round(ini + 0.1, 3), "texto": img["overlay"], "id": img["id"]})
                if tr == "PUNCH":
                    sfx("punch", ini, 0.6)
                elif tr == "GAME":
                    sfx("juego", ini, 0.45)
                elif tr == "WHIP":
                    sfx("whoosh", ini, 0.6)
                elif tr == "FLASH":
                    sfx("flash", ini - 0.05, 0.6)
            audio["voz"].append({"t": round(t, 3), "id": k, "dur": v["dur"], "rol": v["rol"]})
            # ------------------------------------------------ estado después de la línea
            if es_muerte:
                vidas -= 1
                vida_txt = EPOCAS[b]["tiempo"]
                estado_hud(t)
                if not EPOCAS[b]["logro_linea"]:
                    carteles.append({"ini": round(t + v["dur"], 3), "fin": round(t + v["dur"] + 1.6, 3), "tipo": "logro",
                                     "texto": EPOCAS[b]["logro"]})
                    sfx("logro", t + v["dur"], 0.5)
            if b in EPOCAS and EPOCAS[b]["logro_linea"] == k:
                carteles.append({"ini": round(t, 3), "fin": round(t + max(1.6, v["dur"]), 3), "tipo": "logro",
                                 "texto": EPOCAS[b]["logro"], "aura": EPOCAS[b]["aura"]})
                sfx("logro", t, 0.5)
                aura += EPOCAS[b]["aura"]
                estado_hud(t + v["dur"] * 0.8)
            # Tenochtitlan: el color se va y la música se corta desde la viruela
            if k == "E6_13":
                color.append({"ini": round(t, 3), "estilo": "drenaje", "fin_rampa": None})
                audio["musica"].append({"ini": round(t, 3), "nombre": None})
                audio["ambiente"].append({"ini": round(t, 3), "nombre": None})
            if k == "E6_16":
                color[-1]["fin_rampa"] = round(t + v["dur"], 3)
            if k == "E7_15":
                color.append({"ini": round(t, 3), "estilo": "mudo"})
            if k == "E8_04":
                color.append({"ini": round(t, 3), "estilo": "londres"})
            if k == "E7_02":
                sfx("trueno", t + 1.0, 0.5)
            t += v["dur"] + GAP

        # ---------------------------------------------------- salida del bloque
        if b in EPOCAS:
            t = separador(t, b)
            if b == "E8":
                plano(t, "img", id="197", cam="WS", tr="FLASH", epoca=8)
                sfx("flash", t - 0.05, 0.6)
                textos.append({"ini": round(t + 0.1, 3), "texto": "PRÓXIMO: LOS RESULTADOS", "id": "197"})
                t += 1.6
            elif b != "E4":
                siguiente = BLOQUES[BLOQUES.index(b) + 1]
                t = transicion(t, EPOCAS[siguiente]["n"], EPOCAS[siguiente]["puente"])
            else:
                plano(t, "titulo_epoca", texto="MITAD DEL JUEGO")
                sfx("whoosh", t, 0.6)
                t += 0.75
            if b == "E7":
                color.append({"ini": round(t, 3), "estilo": "mudo"})
        elif b == "M":
            t = transicion(t, 5, None)
        elif b == "H":
            t = transicion(t, 1, None)

    # ---------------------------------------------------- tabla final, fuentes y loop
    filas = [{"epoca": NOMBRE_EPOCA[e], "nota": EPOCAS[e]["nota"], "tiempo": EPOCAS[e]["tiempo"], "culpable": EPOCAS[e]["culpable"]} for e in EPOCAS]
    plano(t, "tabla", filas=filas, llenar=4.0)
    for i in range(8):
        sfx("punch", t + 0.3 + i * 0.45, 0.4)
    carteles.append({"ini": round(t + 4.5, 3), "fin": round(t + 9.0, 3), "tipo": "simulacion", "texto": "TIEMPOS DE PIJAMA = SIMULACIÓN"})
    carteles.append({"ini": round(t + 4.5, 3), "fin": round(t + 9.0, 3), "tipo": "fuentes", "texto": "FUENTES EN LA DESCRIPCIÓN"})
    t += 9.0
    plano(t, "img", id="008", cam="zoom", tr="FLASH", epoca=0)
    sfx("timbre", t, 0.8)
    audio["voz"].append({"t": round(t + 0.2, 3), "id": "tic_final", "dur": 0.1, "rol": "tic"})
    t += 1.6
    planos[-1]["fin"] = round(t, 3)

    # overlays: duran hasta el final del plano (mínimo 1,2 s) y nunca se pisan
    fin_plano = {p["id"]: p["fin"] for p in planos if p.get("id")}
    for i, x in enumerate(textos):
        fin = max(fin_plano.get(x["id"], x["ini"] + 1.2), x["ini"] + 1.2)
        if i + 1 < len(textos):
            fin = min(fin, textos[i + 1]["ini"] - 0.05)
        x["fin"] = round(fin, 3)

    # golpes de zoom dentro de planos largos (regla: nada más de 5 s sin cambio)
    for p in planos:
        d = p["fin"] - p["ini"]
        if p["tipo"] == "img" and d > 4.5:
            n = int(d // 3.5)
            p["golpes"] = [round(p["ini"] + d * (j + 1) / (n + 1), 3) for j in range(n)]

    out = {"duracion": round(t, 3), "planos": planos, "textos": textos, "carteles": carteles, "hud": hud, "color": color}
    (R / "remotion" / "src" / "data" / "v2").mkdir(parents=True, exist_ok=True)
    (R / "remotion" / "src" / "data" / "v2" / "largo.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    audio["duracion"] = round(t, 3)
    (V / "work" / "largo_audio.json").write_text(json.dumps(audio, ensure_ascii=False, indent=1))
    sin_usar = sorted(i["id"] for i in MAN if i["tipo"] == "imagen" and i["id"] in REC and i["id"] not in usados and i["block"] not in "STX")
    seguidas = [planos[i]["id"] for i in range(1, len(planos)) if planos[i].get("id") and planos[i].get("id") == planos[i - 1].get("id")]
    largos = [(p.get("id"), round(p["fin"] - p["ini"], 1)) for p in planos if p["fin"] - p["ini"] > 5]
    print(f"duración {int(t // 60)}:{t % 60:04.1f}  planos {len(planos)}  textos {len(textos)}")
    print("imágenes sin usar en el largo:", sin_usar)
    print("repetidas seguidas:", seguidas, " planos > 5 s:", largos)


if __name__ == "__main__":
    main()
