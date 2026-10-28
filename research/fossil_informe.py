#!/usr/bin/env python3
"""Arma research/analisis_gemini/fossil_cortes.md con los trozos de gemini_cortes.py (sin llamar a ninguna API)."""
import json
import statistics as st
from pathlib import Path

R = Path(__file__).parent
G = R / "analisis_gemini"
D = json.loads((G / "nAWpLtG-kNs_trozos.json").read_text())
TOP = json.loads((R / "data/nichos-2026-10/videos_top_completos.json").read_text())["nAWpLtG-kNs"]
COM = json.loads((R / "data/huecos-2026-10/comentarios.json").read_text()).get("nAWpLtG-kNs", [])
OUT = G / "fossil_cortes.md"

# capítulos publicados por el creador (descripción del video, API de YouTube)
CAPS = [(0, "Intro"), (33, "Pre-Cambrian"), (63, "Cambrian"), (157, "Ordovician"), (222, "Silurian"), (305, "Devonian"),
        (361, "Carboniferous"), (438, "Permian"), (517, "Early Triassic"), (596, "Mid-Late Triassic"), (642, "Jurassic"),
        (686, "Cretaceous"), (748, "Paleogene"), (811, "Miocene"), (850, "Pliocene"), (890, "Pleistocene")]


def mmss(s):
    s = float(s)
    return f"{int(s // 60)}:{s % 60:04.1f}"


def trozo(k):
    v = D["trozos"].get(k)
    return v if v and v.get("datos") else None


claves = sorted(D["trozos"], key=lambda k: int(k.split("-")[0]))
ok = [k for k in claves if trozo(k)]
faltan = [k for k in [f"{a}-{min(a + 60, 971)}" for a in range(0, 971, 60)] if k not in ok]

planos = []
for k in ok:
    for p in trozo(k)["datos"].get("planos", []):
        planos.append({**p, "_trozo": k})
eras, tiers = [], []
LITE = D.get("lite", {})
for k in faltan if False else []:
    pass
for k in ok:
    eras += [(e_.get("aparece_s"), e_.get("texto"), k) for e_ in trozo(k)["datos"].get("titulos_de_era", [])]
    tiers += [(t.get("aparece_s"), t.get("hasta_s"), t.get("descripcion"), k) for t in trozo(k)["datos"].get("tier_list", [])]


for k in [k for k in LITE if k not in ok and LITE[k].get("datos")]:
    eras += [(e_.get("aparece_s"), str(e_.get("texto")) + " [modelo liviano]", k) for e_ in LITE[k]["datos"].get("titulos_de_era", [])]
    tiers += [(t.get("aparece_s"), t.get("hasta_s"), str(t.get("descripcion")) + " [modelo liviano, menos confiable]", k) for t in LITE[k]["datos"].get("tier_list", [])]


def esc(x):
    return str(x if x is not None else "—").replace("|", "/").replace("\n", " ")


def fila(p):
    dur = (p["fin_s"] - p["inicio_s"]) if isinstance(p.get("fin_s"), (int, float)) and isinstance(p.get("inicio_s"), (int, float)) else None
    txt = "; ".join(f"«{t.get('texto')}» ({mmss(t['aparece_s']) if isinstance(t.get('aparece_s'), (int, float)) else '?'})" for t in p.get("texto_en_pantalla") or []) or "—"
    sfx = "; ".join(f"{s.get('efecto')} ({mmss(s['s']) if isinstance(s.get('s'), (int, float)) else '?'}, en «{s.get('en_la_frase')}»)" for s in p.get("efectos_de_sonido") or []) or "no detectado"
    return (f"| {mmss(p['inicio_s'])} | {dur:.1f} s | {esc(p.get('tipo'))} | {esc(p.get('que_se_ve'))} | {esc(p.get('movimiento_camara'))} | "
            f"{esc(p.get('transicion_de_entrada'))} | {esc(txt)} | {esc(sfx)} | {esc(p.get('musica'))} | {esc(p.get('narracion'))} |") if dur is not None else ""


HEAD = "| Corte | Duración | Tipo | Qué se ve | Cámara | Transición | Texto en pantalla | Efectos de sonido | Música | Qué se dice |\n|---|---|---|---|---|---|---|---|---|---|"
L = []
a = L.append
a("# Fossil · «How Long You'd Last in Every Prehistoric Era» · análisis corte por corte\n")
a(f"Video: https://www.youtube.com/watch?v=nAWpLtG-kNs · duración real 16:11 (971 s) · publicado {TOP['snippet']['publishedAt'][:10]}")
st_ = TOP["statistics"]
a(f"Datos de la API de YouTube (14/10/2026): {int(st_['viewCount']):,} vistas · {int(st_['likeCount']):,} likes · {int(st_['commentCount']):,} comentarios · canal de 37.800 subs creado el 01/03/2026 · factor outlier x63,5 (vistas ÷ mediana de sus últimos 10 videos).\n".replace(",", "."))

a("## Cómo se hizo\n")
a("- API de Gemini, plan gratis, sin facturación. Se le pasó el link de YouTube y Google mira el video de su lado; no se bajó nada.")
a("- **17 trozos de 60 s** con `videoMetadata.startOffset/endOffset` (la API lo acepta: un trozo de prueba de 10 s gastó 947 tokens, contra los ~85.000 del video entero) a **2 cuadros por segundo** y resolución alta.")
a("- Gemini tiene que dar los tiempos en segundos absolutos del video completo; el script marca cualquier tiempo fuera del tramo pedido.")
modelos = {k: trozo(k)["modelo"] for k in ok}
a(f"- Modelo: gemini-3.8-flash en {sum(1 for m in modelos.values() if m == 'gemini-3.8-flash')} de {len(ok)} trozos. Los trozos que primero hizo el modelo liviano (gemini-3.5-flash-lite) se repitieron con el principal, porque el liviano listaba un corte cada 1,0 s exacto: ese es el intervalo con que mira los cuadros, no cortes reales. Esos resultados viejos quedan guardados en el JSON bajo `lite` para comparar.")
if faltan:
    a(f"- **Trozos sin datos del modelo principal: {', '.join(faltan)}** (el modelo estuvo saturado; ver «Qué no se pudo obtener»).")
a("")

a("## Control de desfase\n")
a("La vez anterior los tiempos llegaron hasta 22:13 en un video de 16:11. Esta vez hice dos controles:\n")
fuera = {k: trozo(k)["tiempos_fuera_del_tramo"] for k in ok if trozo(k)["tiempos_fuera_del_tramo"]}
a(f"1. **Tiempos fuera del tramo:** {('ninguno en los ' + str(len(ok)) + ' trozos') if not fuera else fuera}. El último tiempo reportado es {mmss(max(p['fin_s'] for p in planos if isinstance(p.get('fin_s'), (int, float))))}, dentro de los 16:11.")
a("2. **Títulos de era contra los capítulos del creador** (referencia independiente, sacada de la descripción del video):\n")
a("| Era | Capítulo del creador | Título visto por Gemini | Diferencia |\n|---|---|---|---|")
for t, nombre in CAPS[1:]:
    cand = [x for x in eras if isinstance(x[0], (int, float)) and abs(x[0] - t) <= 8]
    if cand:
        g = min(cand, key=lambda x: abs(x[0] - t))
        a(f"| {nombre} | {mmss(t)} | {mmss(g[0])} («{esc(g[1])}») | {g[0] - t:+.1f} s |")
    else:
        a(f"| {nombre} | {mmss(t)} | no detectado en ese tramo | — |")
a("\nLos capítulos del creador están redondeados al segundo y Gemini mira 2 cuadros por segundo, así que diferencias de ±1,5 s son esperables. Una diferencia que crezca a lo largo del video indicaría desfase.\n")

a("## 1. Cada corte entre 0:00 y 2:30\n")
a("Corte = momento en que entra un plano nuevo. Duración = hasta el corte siguiente. Los límites de 1:00 y 2:00 son límites de trozo, no cortes reales: el plano que cruza ese límite aparece partido en dos filas.\n")
a(HEAD)
for p in planos:
    if p["inicio_s"] < 150:
        a(fila(p))
a("")

BLOQUES = [("300-360", "Silúrico → Devónico (capítulo 5:05)"), ("600-660", "Triásico medio-tardío → Jurásico (capítulo 10:42)"), ("840-900", "Plioceno → Pleistoceno (capítulo 14:50)")]
a("## 2. Muestreo de 3 bloques a lo largo del video\n")
a("Elegí tres bloques de 60 s que contienen un cambio de era, para ver cómo se repite (o no) la estructura.\n")
for k, nombre in BLOQUES:
    a(f"### {mmss(int(k.split('-')[0]))}–{mmss(int(k.split('-')[1]))} · {nombre}\n")
    if trozo(k):
        a(f"Modelo: {trozo(k)['modelo']}\n")
        a(HEAD)
        for p in planos:
            if p["_trozo"] == k:
                a(fila(p))
    else:
        a("**Sin datos: el modelo principal no respondió para este trozo.**")
    a("")

# ---------- resumen ----------
dur_all = [p["fin_s"] - p["inicio_s"] for p in planos if isinstance(p.get("fin_s"), (int, float))]
cortes_33 = sum(1 for p in planos if 0 < p["inicio_s"] < 33.0)
gancho = [p["fin_s"] - p["inicio_s"] for p in planos if p["inicio_s"] < 33.0]
cuerpo = [p["fin_s"] - p["inicio_s"] for p in planos if p["inicio_s"] >= 33.0]
a("## 3. Resumen\n")
a(f"- **Ojo:** las cifras de este resumen salen de {len(ok)} de 17 trozos ({len(ok)*60//60} de 16 minutos aprox.); faltan {', '.join(faltan)}.")
a(f"- **Planos analizados:** {len(planos)} en {len(ok)} trozos (incluye los planos partidos en los límites de trozo, que bajan un poco la duración media).")
a(f"- **Duración media del plano en todo el video:** {st.mean(dur_all):.1f} s (mediana {st.median(dur_all):.1f} s).")
a(f"- **Gancho (0:00–0:33):** {cortes_33} cortes en los primeros 33 segundos, con planos de {st.mean(gancho):.1f} s de promedio. Es un montaje rápido de criaturas (mamut, pterosaurio, cefalópodo, dientes de sable, oso gigante, T-rex) mientras la voz hace preguntas.")
a(f"- **Resto del video (desde 0:33):** planos de {st.mean(cuerpo):.1f} s de promedio (mediana {st.median(cuerpo):.1f} s). El ritmo baja a menos de la mitad que en el gancho.")
trans = {}
for p in planos:
    trans[p.get("transicion_de_entrada")] = trans.get(p.get("transicion_de_entrada"), 0) + 1
a("- **Transiciones:** " + ", ".join(f"{k}: {v}" for k, v in sorted(trans.items(), key=lambda x: -x[1])) + ".")
tipos = {}
for p in planos:
    tipos[p.get("tipo")] = tipos.get(p.get("tipo"), 0) + 1
a("- **Tipos de plano:** " + ", ".join(f"{k}: {v}" for k, v in sorted(tipos.items(), key=lambda x: -x[1])) + ".")
mov = {}
for p in planos:
    mov[p.get("movimiento_camara")] = mov.get(p.get("movimiento_camara"), 0) + 1
a("- **Movimiento de cámara:** " + ", ".join(f"{k}: {v}" for k, v in sorted(mov.items(), key=lambda x: -x[1])) + ".")

a("\n### Cómo es el paso de una era a la siguiente\n")
a("Secuencia de los 3 planos alrededor de cada título de era (el plano anterior, el título y el siguiente):\n")
for t, nombre in CAPS[1:]:
    idx = [i for i, p in enumerate(planos) if p.get("tipo") == "texto" and abs(p["inicio_s"] - t) <= 8]
    if not idx:
        a(f"- **{nombre} ({mmss(t)}):** título no detectado.")
        continue
    i = idx[0]
    seq = []
    for j in (i - 1, i, i + 1):
        if 0 <= j < len(planos):
            q = planos[j]
            seq.append(f"{mmss(q['inicio_s'])} {esc(q.get('tipo'))} ({esc(q.get('que_se_ve'))[:60]}; entra con {esc(q.get('transicion_de_entrada'))})")
    a(f"- **{nombre}:** " + " → ".join(seq))

a("\n### Dónde aparece el medidor de tier list\n")
a("| Aparece | Hasta | Qué muestra |\n|---|---|---|")
for t0, t1, desc, k in sorted(tiers, key=lambda x: x[0] if isinstance(x[0], (int, float)) else 0):
    a(f"| {mmss(t0) if isinstance(t0, (int, float)) else '?'} | {mmss(t1) if isinstance(t1, (int, float)) else '?'} | {esc(desc)} |")
a("\n**Ranking que se arma en la tier list** (según la lectura de Gemini de cada arrastre; los marcados vienen del modelo liviano):\n")
RANK = [("Pre-Cambrian", "Hours"), ("Cambrian", "Hours"), ("Ordovician", "Days"), ("Silurian", "Days"), ("Devonian", "Weeks"),
        ("Carboniferous", "Months"), ("Permian", "Weeks [liviano]"), ("Early Triassic", "Hours"), ("Mid-Late Triassic", "Weeks"),
        ("Jurassic", "Weeks [liviano]"), ("Cretaceous", "no se pudo leer (el liviano dice «nivel B», que no existe en la tabla)"),
        ("Paleogene", "Months"), ("Miocene", "Most of a year"), ("Pliocene", "A year or more"), ("Pleistocene", "Most of a year")]
a("| Era | Fila de la tier list |\n|---|---|")
for era, fila_ in RANK:
    a(f"| {era} | {fila_} |")
a("\nSegún la tabla, la mejor era para sobrevivir no es la de los humanos (Pleistoceno) sino el Plioceno, la única en «A year or more». Que eso funcione como remate sorpresa es mi lectura (opinión).\n")

a("## 4. Por qué se volvió viral\n")
a("**Medido (API de YouTube):** 11,5 millones de vistas en unos 2 meses, en un canal que tenía 7 meses y menos de 40.000 subs; 63,5 veces la mediana de sus otros videos. 82.252 likes y 4.122 comentarios.\n")
a("**Lo que dice la audiencia** (los comentarios más votados, medido):\n")
for c in sorted(COM, key=lambda x: -x["likes"])[:6]:
    a(f"- {c['likes']} likes: «{esc(c['texto'][:180])}»")
a("\n**Mi lectura de la estructura** (opinión basada en los datos de arriba):\n")
a("1. **Una pregunta que cualquiera se hizo de chico** («¿en qué era sobrevivirías?»), en segunda persona y con viaje en el tiempo. No hace falta saber nada para engancharse.")
a(f"2. **El gancho es un tráiler:** {cortes_33} cortes de criaturas espectaculares en 33 segundos, sin texto ni datos. Promete todo lo que viene.")
a("3. **Un formato de juego que se completa:** la tier list aparece vacía al principio y se va llenando era por era con un arrastre y un clic. El espectador quiere ver el ranking final, y eso sostiene la retención hasta el último minuto.")
a("4. **Estructura repetida y previsible:** en las 11 eras con título detectado que vienen después de la primera, la era anterior termina con su ficha arrastrada a la tier list (de 3 a 7 s). Después entra el título de la era nueva (en 6 casos con fundido a negro) y luego, en 6 de 12 casos, un mapa del planeta en esa época; en las eras más recientes, una ilustración del paisaje. En el medio: oxígeno, temperatura, comida y peligros. Según los capítulos, cada era dura entre 40 s y 1,5 minutos, así que siempre hay una «próxima era» cerca.")
a("5. **Tono de amigo, no de documental:** frases como «you're toast» o «you're cooked», algún meme (Gemini vio un Wojak en 1:11) y stickmen sufriendo en 9 planos. Hace que la ciencia se sienta liviana.")
a("6. **La música genera asombro:** el comentario más votado (1.724 likes) es sobre la música («sense of wonder… dinosaur books»).")
a("7. **Datos concretos y comparables:** porcentaje de oxígeno, grados, tamaño de los bichos en pies. Los comentarios discuten esos números («10 FEET TALL?!», «Bear Dog»), y eso suma comentarios.\n")

a("## 5. Qué no se pudo obtener o es poco confiable\n")
if faltan:
    a(f"- **Trozos sin análisis del modelo principal:** {', '.join(faltan)}. El modelo principal (gemini-3.8-flash) primero estuvo saturado (error 503) y después se agotó el cupo gratis del día (error 429, sin cobro). Para esos tramos solo uso los títulos de era y la tier list del modelo liviano, marcados «[modelo liviano]»; sus cortes no entran en las cifras. Se pueden completar mañana, cuando se reinicie el cupo (medianoche del Pacífico, 4:00 de Argentina).")
a("- **Efectos de sonido:** Gemini detectó muy pocos (algún «clic» al soltar la ficha en la tier list). Que no los detecte no significa que no haya; el análisis de audio fino no es su punto fuerte. Donde dice «no detectado», no hay dato.")
a("- **Música:** la mayoría de los planos dicen «sigue igual». Gemini no da niveles de volumen; no se pudo medir cuándo sube o baja con precisión. Para eso hace falta el audio y ffmpeg, y YouTube bloquea la descarga desde acá.")
a("- **Segundo exacto del corte:** con 2 cuadros por segundo, cada corte tiene un margen de ±0,5 s. Los fundidos cortos pueden quedar sin detectar.")
a("- **Textos en pantalla y narración:** son la lectura de Gemini, no subtítulos oficiales; puede haber diferencias menores de palabras. La narración está en inglés, tal cual se dice.")
a("- **Límites de trozo:** el plano que cruza 1:00, 2:00, etc. aparece partido en dos filas. Eso agrega unos 16 planos falsos y baja levemente la duración media.")
a("\nDatos crudos: `research/analisis_gemini/nAWpLtG-kNs_trozos.json`. Script: `research/gemini_cortes.py`.")
OUT.write_text("\n".join(x for x in L if x is not None), encoding="utf-8")
print("ok", OUT, "planos", len(planos), "faltan", faltan)
