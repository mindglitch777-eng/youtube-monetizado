#!/usr/bin/env python3
"""Arma research/informe/nichos-faceless.html a partir de los datos crudos de
research/data/nichos-2026-10 (no gasta cuota de la API)."""
import gzip, html, json, re, statistics as st
from pathlib import Path

D = Path(__file__).parent.parent / "data" / "nichos-2026-10"
OUT = Path(__file__).parent / "nichos-faceless.html"
M = {x["channel_id"]: x for x in json.loads((D / "canales_metricas.json").read_text())}
O = json.loads((D / "outliers.json").read_text())
TOP = json.loads((D / "videos_top_completos.json").read_text())
Q = json.loads((D / "cuota.json").read_text())
CH = json.load(gzip.open(D / "canales.json.gz", "rt"))
e = html.escape


def dur(s):
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s or "")
    return sum(int(x or 0) * k for x, k in zip(m.groups(), (86400, 3600, 60, 1))) if m else 0


def n(x):
    return f"{x:,}".replace(",", ".")


best_factor = {}
for o in O:
    if (o["duracion_s"] or 0) >= 240:
        best_factor[o["channel_id"]] = max(best_factor.get(o["channel_id"], 0), o["factor_outlier"])

# ---------- 1. ranking ----------
W = {"demanda": 25, "competencia": 20, "velocidad": 20, "costo": 10, "politica": 15, "rpm": 10}
RANK = [
    # nombre, formato, notas{criterio: (nota, por qué)}
    ("Vida y supervivencia de humanos antiguos (ES)", "Largo 12–25 min · ilustraciones IA + voz IA",
     dict(demanda=(4, "EN probado (13,9M, 11,5M, 2,3M vistas). En ES hay hits de 0,4–1,3M en canales de 3–16k subs"),
          competencia=(3, "En inglés ya está saturado de copias. En español aparecieron muchos canales en 2026, pero pocos de calidad"),
          velocidad=(4, "Cronología de la Humanidad (6,4k subs, 434k), WUFO Español (1,5 meses, 2,4M totales), Pepe Explica (2,2k subs, 235k)"),
          costo=(5, "Solo imágenes IA, voz IA y edición. No hace falta grabar ni comprar material"),
          politica=(4, "Educativo y apto para anunciantes. Riesgo bajo si el guion es propio (no plantilla masiva)"),
          rpm=(3, "Historia/educación en español: estimado US$1–3 por 1.000 vistas"))),
    ("Espacio / astronomía documental (ES)", "Largo 12–20 min · imágenes NASA/ESA + voz IA",
     dict(demanda=(5, "Mediana de los videos largos en ES: 269k. Astrovía 2,9M, ABISMO 2,5M, Neurika 2,1M"),
          competencia=(2, "5 canales de más de 1M de subs en los resultados en español, y muchos copiando el formato 'James Webb acaba de...'"),
          velocidad=(4, "5 de 12 canales jóvenes de formato largo tienen mediana ≥20k"),
          costo=(5, "Las imágenes de la NASA son de dominio público"),
          politica=(3, "Los títulos alarmistas tipo 'acaba de detectar' rozan la desinformación"),
          rpm=(3, "Ciencia en español: estimado US$1–3"))),
    ("Animales prehistóricos / megafauna (ES)", "Largo 10–20 min · ilustraciones IA de criaturas",
     dict(demanda=(4, "Bestias Míticas 4,1M (4 meses), Mundo Extinto 2,1M, BananomiES 934k"),
          competencia=(3, "ZooExtinto (274k subs) y Planeta Antiguo ya ocupan el lugar. La mediana en ES baja (1,2k) muestra muchos intentos flojos"),
          velocidad=(3, "1 de 23 canales jóvenes en ES con mediana ≥20k; en EN, 11 de 36"),
          costo=(4, "Las imágenes IA de criaturas tienen que verse consistentes y creíbles"),
          politica=(4, "Educativo"),
          rpm=(3, "Estimado US$1–3"))),
    ("Historias bíblicas animadas (ES)", "Largo 20–40 min · animación IA",
     dict(demanda=(5, "Mediana de los videos largos en ES: 666k"),
          competencia=(2, "9 canales de más de 1M de subs en los resultados en español"),
          velocidad=(3, "3 de 7 canales jóvenes de formato largo en ES con mediana ≥20k"),
          costo=(4, "Animación IA de personajes consistentes"),
          politica=(3, "Tema religioso: comentarios polarizados y riesgo de errores doctrinales"),
          rpm=(3, "Estimado US$1–3"))),
    ("Misterios / civilizaciones perdidas", "Largo 20–40 min",
     dict(demanda=(4, "Mediana de los videos largos: 345k en EN y 147k en ES"),
          competencia=(2, "12 canales grandes en EN"),
          velocidad=(3, "3 de 7 canales jóvenes de formato largo"),
          costo=(5, "Imágenes IA + voz"),
          politica=(2, "La pseudoarqueología ('la IA reanalizó las pirámides...') choca con las reglas de desinformación"),
          rpm=(3, "Estimado US$1–4"))),
    ("Vida salvaje documental (ES)", "Largo 20–60 min",
     dict(demanda=(5, "Mediana de los videos largos en ES: 1,49M (la muestra es chica: 26 videos)"),
          competencia=(3, "Pocos canales, pero con mucha producción"),
          velocidad=(4, "Sin Coordenadas (3 meses, 2,9M), CortexSilvestre (2 semanas, 1,7M)"),
          costo=(2, "Necesita material de animales reales: stock pago o metraje ajeno"),
          politica=(2, "Alto riesgo de reclamos de copyright y de 'contenido reutilizado'"),
          rpm=(3, "Estimado US$1–3"))),
    ("Ingeniería / megaobras", "Mayormente Shorts 3D",
     dict(demanda=(3, "Mediana de los videos largos: 142k en EN; en ES casi todo son Shorts"),
          competencia=(3, "Pocos canales hacen formato largo"),
          velocidad=(3, "3 de 9 canales jóvenes de formato largo"),
          costo=(3, "Una buena animación 3D lleva mucho trabajo"),
          politica=(4, "Educativo"),
          rpm=(4, "Técnico: estimado US$2–5"))),
    ("Estoicismo / frases", "Largo 10–40 min",
     dict(demanda=(3, "Mediana de los videos largos en ES: 222k"),
          competencia=(1, "Saturado de canales casi idénticos"),
          velocidad=(2, "2 de 13 canales jóvenes"),
          costo=(5, "Muy barato"),
          politica=(2, "El típico caso de 'contenido inauténtico/masivo'"),
          rpm=(3, "Estimado US$1–3"))),
    ("Finanzas / economía explicada", "Largo 10–20 min",
     dict(demanda=(2, "EN 246k, pero en ES la mediana de los videos largos es solo 20k"),
          competencia=(2, "10 canales grandes en EN"),
          velocidad=(2, "2 de 12 canales jóvenes"),
          costo=(5, "Gráficos + voz"),
          politica=(4, "OK mientras no sea consejo financiero"),
          rpm=(5, "El más alto: estimado US$5–15 en EN y US$2–5 en ES"))),
    ("Psicología explicada", "Shorts + largo",
     dict(demanda=(2, "EN 285k, pero en ES la mediana de los videos largos es 784"),
          competencia=(1, "48 canales jóvenes de formato largo y solo 1 con mediana ≥20k"),
          velocidad=(1, "Es el peor resultado medido"),
          costo=(5, "Muy barato"),
          politica=(3, "'Psicología oscura' y temas de salud mental son sensibles"),
          rpm=(4, "Estimado US$2–5"))),
    ("Ciencia / curiosidades (Shorts)", "Shorts < 60 s",
     dict(demanda=(5, "Mediana de 800k en EN, pero el 90% son Shorts"),
          competencia=(2, "Mucha competencia"),
          velocidad=(3, "Monetizar requiere 10M de vistas de Shorts en 90 días"),
          costo=(4, "Barato"),
          politica=(3, "Riesgo de contenido repetitivo"),
          rpm=(1, "Shorts: estimado US$0,03–0,10"))),
    ("Batallas / comparación de tamaño 3D", "Largo 5–10 min con simulador de juego",
     dict(demanda=(4, "Animals Beast Revolt 7M con 13,7k subs"),
          competencia=(2, "Muchos clones"),
          velocidad=(4, "Varios canales con menos de 1 año y millones de vistas"),
          costo=(3, "Necesita PC y un juego pago"),
          politica=(1, "Metraje de videojuego repetitivo, público infantil (contenido 'para niños' paga muy poco)"),
          rpm=(1, "Infantil: estimado US$0,1–0,5"))),
]
rows = []
for name, fmt, s in RANK:
    tot = sum(W[k] * s[k][0] for k in W) / 5
    rows.append((tot, name, fmt, s))
rows.sort(key=lambda r: -r[0])

# ---------- 2. evidencia ----------
EVID = ["Ink Explainer", "Fossil", "Rome Unscrolled", "inkly", "ZENO", "Stickstory", "Deep Epoch", "Vikings Life",
        "Before Civilization", "Sleepy Old World", "Um Documentário", "Tito Primitivo", "Tiempos Antiguos", "WUFO Español",
        "Cronología de la Humanidad", "Estrictamente", "Pepe Explica", "KROG", "Homo Curioso", "Kron TV", "Mango Explica SP",
        "Bestias Míticas", "Mundo Extinto", "Planeta Antiguo", "BananomiES", "Astrovía", "ABISMO", "Neurika",
        "Sin Coordenadas", "CortexSilvestre", "Animals Beast Revolt", "Mavora", "Uso dos porquês", "Нулевая Земля",
        "Efecto Sombra | Psicología Oscura", "Domina Tu Mente"]
byname = {}
for x in M.values():
    byname.setdefault(x["canal"].strip(), x)
ev = []
for nm in EVID:
    x = byname.get(nm) or next((y for k, y in byname.items() if k.startswith(nm)), None)
    if x:
        ev.append(x)
    else:
        print("sin datos:", nm)

# ---------- 3. top videos ----------
order = ["49_Ph2q6uIM", "nAWpLtG-kNs", "t-xY-KR2IHE", "OlCQZbYGVtk", "XJhKBgiP-Ic", "0tSwA12rEtk", "4vAlEh9RN5Y",
         "U_eV4WbL6Vw", "JV1IICDwvI8", "hZfVSlKLe_M", "7MgqNR8oxSU", "cAqWSE1mjpc", "zK2jFCC3BhA", "Hb6l9pRvHOc", "k2CXi4XPi7U"]
fac = {o["video_id"]: o["factor_outlier"] for o in O}

young = [x for x in M.values() if x["meses_de_vida"] < 12]
css = """
:root{--bg:#fbfaf7;--fg:#1d1d1b;--mut:#66625a;--line:#e3dfd6;--card:#fff;--acc:#a8541e;--good:#2f7a3e;--warn:#9a6a00;--bad:#a33;--chip:#f1ede4}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#161513;--fg:#ece9e2;--mut:#a39e93;--line:#34312c;--card:#1f1e1b;--acc:#e08a4f;--good:#6cc27c;--warn:#e0b04a;--bad:#ff7b7b;--chip:#2a2824}}
:root[data-theme="dark"]{--bg:#161513;--fg:#ece9e2;--mut:#a39e93;--line:#34312c;--card:#1f1e1b;--acc:#e08a4f;--good:#6cc27c;--warn:#e0b04a;--bad:#ff7b7b;--chip:#2a2824}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1060px;margin:0 auto;padding:28px 16px 80px}h1{font-size:1.9rem;line-height:1.2;margin:.2em 0}h2{margin-top:2.4em;border-bottom:2px solid var(--line);padding-bottom:.3em}h3{margin-top:1.6em}
.mut{color:var(--mut)}.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin:14px 0}
.tag{display:inline-block;font-size:.75rem;font-weight:600;padding:1px 8px;border-radius:99px;background:var(--chip);margin-right:4px}
.medido{color:var(--good)}.estimado{color:var(--warn)}.opinion{color:var(--acc)}
.tw{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--card)}table{border-collapse:collapse;width:100%;font-size:.86rem}
th,td{padding:7px 9px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{position:sticky;top:0;background:var(--chip);font-weight:600;white-space:nowrap}
td.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}a{color:var(--acc)}.big{font-size:1.15rem;font-weight:700}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}.kpi b{display:block;font-size:1.5rem}
.bar{height:8px;border-radius:4px;background:var(--acc)}details{margin:8px 0}summary{cursor:pointer;font-weight:600}pre{white-space:pre-wrap;font-size:.8rem;background:var(--chip);padding:10px;border-radius:8px;max-height:260px;overflow:auto}
.warn{border-left:4px solid var(--warn)}.rec{border-left:4px solid var(--good)}
"""
H = []
a = H.append
a(f"<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Nichos faceless 2026</title><style>{css}</style></head><body><main>")
a("<p class='mut'>Investigación con la API de YouTube Data v3 · datos del 14/10/2026</p><h1>¿Qué nicho faceless conviene para un canal nuevo con presupuesto cero?</h1>")
a("<p><span class='tag medido'>MEDIDO</span> = viene de la API &nbsp; <span class='tag estimado'>ESTIMADO</span> = cálculo o referencia externa (RPM, ingresos) &nbsp; <span class='tag opinion'>OPINIÓN</span> = criterio mío</p>")
a("<div class='kpis'>")
for lbl, val in [("búsquedas", Q["search_calls"]), ("unidades gastadas", n(Q["total"])), ("canales encontrados", n(len(CH))),
                 ("canales < 200k analizados", n(len(M))), ("canales < 12 meses", n(len(young))), ("videos medidos", "50.688")]:
    a(f"<div class='kpi'><b>{val}</b><span class='mut'>{lbl}</span></div>")
a("</div>")

a("<h2>Resumen en 6 líneas</h2><div class='card rec'><ol>")
a("<li><b>Lo más fuerte medido</b> en canales jóvenes y faceless son los videos largos (10–25 min) que contestan <i>preguntas concretas sobre cómo vivían o sobrevivían los humanos antiguos</i>. Por ejemplo, 'What Did Ancient Humans Actually Do All Day?' (13,9M vistas, canal de 6 meses) y 'How Long You'd Last in Every Prehistoric Era' (11,5M, canal de 7 meses). <span class='tag medido'>MEDIDO</span></li>")
a("<li><b>En inglés ese subnicho ya está lleno de copias</b>: en la segunda ronda aparecieron decenas de canales de 2026 con títulos casi idénticos. <span class='tag medido'>MEDIDO</span></li>")
a("<li><b>En español está empezando</b>: hay canales de 2.000 a 16.000 subs con videos de 200k a 1,3M (Tiempos Antiguos, WUFO Español, Cronología de la Humanidad, Pepe Explica, KROG). Pero también se llena rápido de traducciones de los éxitos en inglés. <span class='tag medido'>MEDIDO</span> La ventana está abierta, aunque no por mucho tiempo. <span class='tag opinion'>OPINIÓN</span></li>")
a("<li><b>Espacio en español</b> sale segundo: tiene buena demanda y las imágenes de la NASA son gratis, pero hay más canales grandes. <span class='tag medido'>MEDIDO</span></li>")
a("<li><b>Psicología, estoicismo y finanzas en español</b> salieron mal: muchos canales nuevos y casi ninguno despega. <span class='tag medido'>MEDIDO</span></li>")
a("<li><b>Los Shorts</b> dan muchas vistas, pero pagan muy poco. Para monetizar rápido conviene el formato largo (4.000 horas de reproducción). <span class='tag estimado'>ESTIMADO</span></li></ol></div>")

a("<h2>1. Ranking de nichos y formatos</h2>")
a("<p>Pesos: " + " · ".join(f"<b>{k}</b> {v}%" for k, v in W.items()) + ". Notas de 1 a 5 (5 = mejor; en <i>competencia</i> y <i>riesgo de política</i>, 5 significa <i>poca</i> competencia o <i>poco</i> riesgo). Puntaje = suma ponderada sobre 100.</p>")
a("<p class='mut'>Demanda, competencia y velocidad se basan en datos <span class='tag medido'>MEDIDO</span>, pero la nota final que les puse es <span class='tag opinion'>OPINIÓN</span>. El RPM es <span class='tag estimado'>ESTIMADO</span>: son rangos públicos típicos de la industria, no salen de la API (la API no da ingresos de canales ajenos). Costo y política son <span class='tag opinion'>OPINIÓN</span>.</p>")
a("<div class='tw'><table><tr><th>#</th><th>Nicho / formato</th><th>Puntaje</th>" + "".join(f"<th>{k}</th>" for k in W) + "</tr>")
for i, (tot, name, fmt, s) in enumerate(rows, 1):
    a(f"<tr><td>{i}</td><td><b>{e(name)}</b><br><span class='mut'>{e(fmt)}</span></td><td class='n'><span class='big'>{tot:.0f}</span><div class='bar' style='width:{tot:.0f}%'></div></td>"
      + "".join(f"<td><b>{s[k][0]}</b><br><span class='mut'>{e(s[k][1])}</span></td>" for k in W) + "</tr>")
a("</table></div>")

a("<h3>Números por tema e idioma (videos de los últimos 90 días)</h3><p class='mut'>Velocidad = de los canales jóvenes (menos de 12 meses) de formato largo, cuántos tienen una mediana de vistas ≥20k en sus últimos 10 videos. <span class='tag medido'>MEDIDO</span></p>")
TT = [("historia_cotidiana|en", "Vida cotidiana antigua EN", 66212, "11/103"), ("historia_cotidiana|es", "Vida cotidiana antigua ES", 1672, "6/73"),
      ("animales_prehistoricos|en", "Animales prehistóricos EN", 71350, "11/36"), ("animales_prehistoricos|es", "Animales prehistóricos ES", 1216, "1/23"),
      ("espacio|en", "Espacio EN", 473060, "2/4"), ("espacio|es", "Espacio ES", 268939, "3/8"), ("vida_salvaje|es", "Vida salvaje ES", 1485737, "3/4"),
      ("historias_biblicas|es", "Historias bíblicas ES", 666429, "3/7"), ("misterios|en", "Misterios EN", 345299, "2/5"), ("misterios|es", "Misterios ES", 147459, "1/2"),
      ("psicologia|en", "Psicología EN", 284783, "1/5"), ("psicologia|es", "Psicología ES", 784, "0/26"), ("estoicismo|es", "Estoicismo ES", 222247, "2/6"),
      ("finanzas|en", "Finanzas EN", 245969, "2/8"), ("finanzas|es", "Finanzas ES", 19736, "0/5"), ("ingenieria|en", "Ingeniería EN", 142133, "3/5"), ("ciencia|en", "Ciencia EN", 117752, "2/5")]
a("<div class='tw'><table><tr><th>Tema</th><th>Mediana de vistas de videos largos (≥4 min) encontrados</th><th>Canales jóvenes de formato largo con mediana ≥20k</th></tr>")
for _, lbl, med, vel in TT:
    a(f"<tr><td>{lbl}</td><td class='n'>{n(med)}</td><td class='n'>{vel}</td></tr>")
a("</table></div><p class='mut'>Ojo: las medianas bajas en ES (vida cotidiana, prehistoria, psicología) no significan que no haya público. Significan que <b>hay muchísimos videos flojos</b> y pocos buenos. Los buenos sí explotan (ver la tabla de evidencia).</p>")

a("<h2>2. Tabla de evidencia</h2><p class='mut'>Mediana = mediana de vistas de los últimos 10 videos. Factor outlier = vistas del mejor video largo ÷ esa mediana (solo videos ≥4 min, ≥50k vistas y ≥3x). El 'video más visto' sale de los últimos 50 subidos (la API no da el más visto de toda la historia sin gastar 100 unidades por canal). <span class='tag medido'>MEDIDO</span></p>")
a("<div class='tw'><table><tr><th>Canal</th><th>Creado</th><th>Subs</th><th>Vistas totales</th><th>Videos</th><th>Mediana ult. 10</th><th>Vistas/sub</th><th>Factor outlier</th><th>% Shorts</th><th>Video más visto</th></tr>")
for x in ev:
    nf = " <span class='tag' style='color:var(--bad)'>NO faceless</span>" if x["canal"].startswith("BananomiES") else ""
    a(f"<tr><td><a href='{x['url']}'>{e(x['canal'])}</a>{nf}</td><td>{x['creado']}<br><span class='mut'>{x['meses_de_vida']} m</span></td><td class='n'>{n(x['subs'])}</td><td class='n'>{n(x['vistas_totales'])}</td><td class='n'>{x['videos']}</td>"
      f"<td class='n'>{n(x['mediana_ult10'])}</td><td class='n'>{x['vistas_por_sub']}</td><td class='n'>{('x' + str(best_factor[x['channel_id']])) if x['channel_id'] in best_factor else '—'}</td><td class='n'>{x['pct_shorts_ult10']}%</td>"
      f"<td><a href='https://www.youtube.com/watch?v={x['top_video_id']}'>{e(x['top_video_titulo'][:80])}</a><br><span class='mut'>{n(x['top_video_vistas'])} vistas</span></td></tr>")
a("</table></div>")
a("<div class='card'><b>Faceless verificado con miniaturas.</b> Un workflow de GitHub Actions bajó el video más visto y 3 recientes de los 36 canales (<code>research/miniaturas/</code>). <b>35 de 36 son faceless</b> (ilustración IA, render o texto). <b>BananomiES no lo es</b>: el presentador aparece recortado en las miniaturas, así que lo dejé marcado y no cuenta como evidencia. <span class='tag medido'>VERIFICADO A OJO</span></div>")

a("<h2>3. Los 15 videos más fuertes</h2><p class='mut'>Todos son de canales con menos de 200k subs y en su mayoría con menos de 12 meses. Los títulos, las descripciones y los tags son exactos de la API. <span class='tag medido'>MEDIDO</span></p>")
for vid in order:
    x = TOP[vid]; s = x["snippet"]; sti = x["statistics"]; cm = M[s["channelId"]]
    a(f"<div class='card'><div class='big'><a href='https://www.youtube.com/watch?v={vid}'>{e(s['title'])}</a></div>"
      f"<div class='mut'>{e(s['channelTitle'])} · {n(cm['subs'])} subs · canal de {cm['meses_de_vida']} meses · publicado {s['publishedAt'][:10]} · {dur(x['contentDetails']['duration'])//60} min {dur(x['contentDetails']['duration'])%60} s</div>"
      f"<p><b>{n(int(sti.get('viewCount',0)))}</b> vistas · {n(int(sti.get('likeCount',0) or 0))} likes · {n(int(sti.get('commentCount',0) or 0))} comentarios · factor outlier <b>x{fac.get(vid,'—')}</b> · vistas/subs del canal {round(int(sti.get('viewCount',0))/max(cm['subs'],1),1)}</p>"
      f"<details><summary>Tags ({len(s.get('tags') or [])})</summary><p>{e(', '.join(s.get('tags') or ['(sin tags)']))}</p></details>"
      f"<details><summary>Descripción completa</summary><pre>{e(s.get('description',''))}</pre></details></div>")

a("<h2>3b. Lo que muestran las miniaturas</h2>")
a("<p class='mut'>Cada hoja muestra el video más visto (a la izquierda) y 3 recientes del mismo canal. <span class='tag medido'>VERIFICADO A OJO</span></p>")
a("<div class='card warn'><b>El hallazgo más importante: casi todo el subnicho usa la misma plantilla.</b> Unos 15 canales (Ink Explainer, Before Civilization, Deep Epoch, Stickstory, Cronología de la Humanidad, KROG, Homo Curioso, Kron TV, Mango Explica, Pepe Explica, Tito Primitivo, Uso dos porquês, Estrictamente, inkly, Rome Unscrolled) repiten lo mismo: <b>un muñequito tipo meme con piel de cavernícola + 2 o 3 palabras en mayúsculas amarillas con signo de pregunta</b> ('NO JOBS', '¿CÓMO DORMÍAN?', '¿PRIMER JABÓN?'). Tito Primitivo (ES) y Uso dos porquês (PT) tienen hasta los mismos temas y dibujos ('¿POR QUÉ BLANCO?' / 'POR QUE FICOU BRANCO?', '¿PRIMER RACISMO?' / 'PRIMEIRO RACISMO?'). <span class='tag opinion'>OPINIÓN</span>: el formato funciona, pero ya está muy copiado. Entrar con la misma plantilla te pone a competir contra 15 canales iguales.</div>")
a("<div class='card'><b>Los otros estilos que también ganan:</b><ul>"
  "<li><b>Documental cinematográfico realista</b> (Tiempos Antiguos, WUFO Español, Um Documentário, Planeta Antiguo, Mundo Extinto): una imagen IA fotorrealista, título corto en tipografía de película, sin flechas ni caras exageradas. <b>En español hay menos canales con este estilo</b> en el tema de humanos antiguos. <span class='tag opinion'>OPINIÓN</span>: es la diferenciación más clara disponible.</li>"
  "<li><b>Pintura oscura y dramática</b> (Fossil): criatura amenazante + un número grande ('12 Minutes', '9 Minutes' = cuánto durarías).</li>"
  "<li><b>Antes/después</b> (Bestias Míticas, Mavora): 'EXTINTO → VIVO' en rojo y verde, con foto falsa en blanco y negro. Funciona, pero simula fotos históricas: es un riesgo de desinformación.</li>"
  "<li><b>Alarmista</b> (Astrovía, Neurika): 'ÚLTIMA HORA', '¡NASA EN PÁNICO!', 'NO DEBÍA EXISTIR'. Confirma el riesgo de política del nicho de espacio.</li></ul></div>")
for f, cap in [("Ink_Explainer", "Ink Explainer (EN): el modelo original"), ("Cronologa_de_la_Humanidad", "Cronología de la Humanidad (ES): mismo estilo"), ("KROG", "KROG (ES)"), ("Pepe_Explica", "Pepe Explica (ES)"),
               ("Tito_Primitivo", "Tito Primitivo (ES)"), ("Uso_dos_porqus", "Uso dos porquês (PT): mismos temas que Tito Primitivo"), ("Estrictamente", "Estrictamente (ES): traduce a Rome Unscrolled"),
               ("Tiempos_Antiguos", "Tiempos Antiguos (ES): estilo documental realista"), ("WUFO_Espaol", "WUFO Español (ES): estilo documental realista"), ("Fossil", "Fossil (EN): pintura oscura + número"),
               ("Bestias_Mticas", "Bestias Míticas (ES): antes/después"), ("Astrova", "Astrovía (ES): alarmista"), ("BananomiES", "BananomiES: NO faceless (presentador en cámara)")]:
    a(f"<figure style='margin:14px 0'><img src='miniaturas/{f}.jpg' alt='{e(cap)}' style='width:100%;height:auto;border-radius:8px;border:1px solid var(--line)'><figcaption class='mut'>{e(cap)}</figcaption></figure>")

a("<h2>4. Estructura de los mejores videos</h2>")

G = Path(__file__).parent.parent / "analisis_gemini"
GV = [("49_Ph2q6uIM", "Ink Explainer"), ("nAWpLtG-kNs", "Fossil"), ("t-xY-KR2IHE", "Bestias Míticas"), ("cAqWSE1mjpc", "Tito Primitivo"),
      ("hZfVSlKLe_M", "Tiempos Antiguos"), ("YhB3V1i75po", "Cronología de la Humanidad")]


def mmss(t):
    p_ = [int(x) for x in t.split(":")]
    return p_[0] * 60 + p_[1] if len(p_) == 2 else p_[0] * 3600 + p_[1] * 60 + p_[2]


a("<div class='card'><b>Cómo se hizo.</b> YouTube bloquea la descarga de guiones y videos desde servidores (probé 7 métodos). La solución fue la <b>API de Gemini</b> de Google: se le pasa el link y Gemini mira el video desde los servidores de Google. Por cada video pedí (1) la transcripción con tiempos y (2) un análisis de imagen y audio. Plan gratis, sin facturación. "
  "<span class='tag estimado'>HECHO POR IA</span> La transcripción es de Gemini escuchando el audio, <b>no</b> los subtítulos oficiales: puede cambiar alguna palabra (por ejemplo 'Mirá' en vez de 'Mira'). Los números visuales (cambios de imagen por minuto) son aproximados. Los textos completos están en <code>research/transcripciones/</code> y <code>research/analisis_gemini/</code>.</div>")
a("<div class='tw'><table><tr><th>Video</th><th>Gancho (técnica y primeras palabras)</th><th>Bloques</th><th>Cierre</th><th>Imagen</th><th>Audio</th></tr>")
for vid, canal in GV:
    d = json.loads((G / f"{vid}.json").read_text()); an = d.get("analisis") or {}
    gk = an.get("gancho_0_30s", {}); bl = an.get("bloques", []); ci = an.get("cierre", {}); vi = an.get("visual", {}); au = an.get("audio", {})
    durs = [mmss(b["fin"]) - mmss(b["inicio"]) for b in bl if b.get("fin") and b.get("inicio")]
    primeras = " ".join(l.split("] ", 1)[-1] for l in d["transcripcion"].splitlines()[:3] if "sin narración" not in l)[:140]
    vt = TOP.get(vid, {}).get("snippet", {}).get("title") or vid
    a(f"<tr><td><b>{e(canal)}</b><br><a href='https://www.youtube.com/watch?v={vid}'>{e(vt[:60])}</a></td>"
      f"<td><b>{e(str(gk.get('tecnica','')))}</b><br><i>“{e(primeras)}…”</i></td>"
      f"<td>{len(bl)} bloques<br><span class='mut'>{(round(st.mean(durs)/60,1) if durs else '—')} min promedio</span></td>"
      f"<td>{e(str(ci.get('que_hace',''))[:160])}<br><span class='mut'>pide suscripción: {'sí' if ci.get('pide_suscripcion_o_like', ci.get('pidesuscripcion_o_like')) else 'no'} · pregunta a comentarios: {'sí' if ci.get('pregunta_a_comentarios') else 'no'}</span></td>"
      f"<td>{e(str(vi.get('estilo',''))[:140])}<br><span class='mut'>~{vi.get('cambios_de_imagen_aprox_por_minuto','?')} cambios/min · {e(str(vi.get('tipo_de_movimiento','')))}</span></td>"
      f"<td>{e(str(au.get('voz',''))[:110])}<br><span class='mut'>{e(str(au.get('musica',''))[:90])}</span></td></tr>")
a("</table></div>")
for vid, canal in GV:
    d = json.loads((G / f"{vid}.json").read_text()); an = d.get("analisis") or {}
    a(f"<details class='card'><summary>{e(canal)}: bloques, retención y frases de ejemplo</summary><ol>"
      + "".join(f"<li><b>{e(b.get('inicio',''))}–{e(b.get('fin',''))}</b> {e(b.get('tema',''))} <span class='mut'>· abre: {e(b.get('como_abre',''))} · engancha: {e(b.get('como_cierra_o_engancha_al_siguiente',''))}</span></li>" for b in an.get("bloques", []))
      + "</ol><p><b>Técnicas de retención:</b></p><ul>" + "".join(f"<li>{e(t)}</li>" for t in an.get("tecnicas_de_retencion", []))
      + "</ul><p><b>Frases cortas de ejemplo:</b> " + " · ".join(f"“{e(f)}”" for f in an.get("frases_cortas_de_ejemplo", [])[:5])
      + f"</p><p><b>Por qué se hizo viral (opinión de Gemini):</b> {e(str(an.get('por_que_creo_que_se_hizo_viral','')))}</p>"
      + f"<p class='mut'>Cara humana en cámara: {'sí' if an.get('cara_humana_real_en_camara') else 'no'}</p></details>")
a("<h3>Patrón común de los 6 videos <span class='tag opinion'>MI LECTURA de los análisis</span></h3><ul>"
  "<li><b>Los primeros 30 s ponen al espectador DENTRO de la escena, en segunda persona</b>: 'Mirá tu mano ahora mismo', 'Esta mañana una máquina te gritó hasta despertarte' (Ink Explainer), 'Cierra los ojos e imagina unas manos' (Cronología), 'Imagine you got a time machine' (Fossil). Cuatro de seis lo hacen claramente; Tiempos Antiguos narra en tercera persona pero mete 'como tú la entiendes hoy'. Nadie se presenta ni dice el nombre del canal.</li>"
  "<li><b>Contraste moderno contra antiguo</b> en el gancho: el despertador contra el cavernícola sin horario; tu piel hoy contra la de tus ancestros. Hace que un tema viejo se sienta personal.</li>"
  "<li><b>Promesa de algo contraintuitivo</b> a los 20–40 s: 'el T-Rex solo llega al número 2', 'no fue un accidente', 'los esqueletos antiguos eran más sanos'. Y en la mitad del video, un giro que la cumple.</li>"
  "<li><b>Bloques de 1–3 min en los videos de lista</b> (Fossil: 13 bloques de ~1 min; Bestias Míticas: 12 de ~1,7 min) y <b>de 3–5 min en los ensayos</b> (Tito Primitivo, Tiempos Antiguos, Cronología: 4–6 bloques).</li>"
  "<li><b>El cierre vuelve a la pregunta inicial</b> con una reflexión ('Cada tono de piel es una respuesta a una pregunta hecha por una estrella'). Solo 3 de 6 piden suscripción y la piden al final, no al principio.</li>"
  "<li><b>Imagen: entre 6 y 15 cambios por minuto</b> (una imagen nueva cada 4–10 s), casi siempre imágenes fijas con zoom o paneo, no animación real. Es barato de producir.</li>"
  "<li><b>Voz masculina pausada (120–160 palabras/min), música instrumental suave de fondo y efectos de sonido puntuales</b> (despertador, viento, fuego).</li>"
  "<li><b>Se citan estudios reales</b>: Richard Lee, Polly Wiessner, Marshall Sahlins. Eso da credibilidad y es lo que diferencia a los ensayos que funcionan de los genéricos.</li></ul>")
a("<div class='card warn'><b>Dos alertas que salieron del análisis</b><ul>"
  "<li><b>Bestias Míticas usa fragmentos de películas</b> (Jurassic Park, The Meg) según Gemini. Eso es riesgo de reclamos de copyright y de desmonetización. No lo copies.</li>"
  "<li><b>Cronología de la Humanidad se parece mucho en contenido a 'What Did Ancient Humans Do For Pleasure?' de Stickstory</b> (EN, publicado antes): el mismo tema, la flauta de hueso, la 'sociedad opulenta' de Sahlins y el cierre sobre el tiempo libre. Es una señal más de que en español se están adaptando los éxitos del inglés, y por eso tu diferencia tiene que estar en las preguntas y el estilo.</li></ul></div>")
a("<h3>Capítulos publicados por los creadores</h3><p class='mut'>Complementa lo de arriba con otros videos que no pasé por Gemini. <span class='tag medido'>MEDIDO</span></p>")
STRUCT = [
    ("Fossil — How Long You'd Last in Every Prehistoric Era (16:11)", "Gancho de 33 s. Después, 15 bloques de unos 40–95 s, uno por era geológica, en orden cronológico (Precámbrico → Pleistoceno). Cada bloque contesta la misma pregunta ('¿cuánto durarías acá?'). No tiene un cierre separado: termina en la era más cercana a la nuestra. Lo que muestra la descripción: 'No myths, no romanticized dinosaurs, just biology, climate, predators, and physics working against the human body'."),
    ("Stickstory — What Did Ancient Humans Do For Pleasure? (13:23)", "Gancho de 51 s que reformula el título como pregunta al espectador ('Do You Have More Free Time Than a Hunter-Gatherer?'). Después, 13 bloques de unos 30–120 s, cada uno con una actividad (música, danza, juegos, relatos, arte, humor, romance, niños, perros). Cierra con 'Final Verdict', que vuelve a la pregunta del principio (unos 45 s)."),
    ("Tito Primitivo — ¿Por Qué Los Humanos Pasaron de Negros a Blancos? (14:35)", "Introducción de 48 s. Después, 7 bloques de unos 45 s a 3 min que van de causa a consecuencia (radiación UV → melanina → folato → salida de África → vitamina D → Neolítico → genética). Cierre 'filosófico' de unos 3 min. El estilo es dibujo tipo MS Paint con humor (según sus tags)."),
    ("Vikings Life — Why Vikings Rarely Got Sick (23:00)", "Gancho de 1:20 con una escena concreta ('Sixty-five men. One open ship. Three weeks at sea. No toilet.'). Después, contraste con el 'otro bando' (3 min) y 5 bloques de 2–4,5 min. Cierra con 'The System That Outlasted Empires' (unos 2 min)."),
    ("Rome Unscrolled — What Did People in Ancient Rome Actually Do All Day? (36:13)", "Ordenado como un día completo, del amanecer a la noche, en 5 bloques largos de 4–9 min. El gancho pone al espectador en la escena en segunda persona: 'It's about the version of you who would have lived there'."),
    ("inkly — Why Desert People Wear More Clothes in Extreme Heat? (10:12)", "Gancho de 1:19 con una paradoja ('The Counterintuitive Logic'). Después, 4 bloques de 1–2,5 min: el problema, la solución, el mecanismo y un segundo misterio (la ropa negra al sol)."),
    ("CortexSilvestre — Por Qué Ningún Depredador Ataca a Un Gorila Espalda Plateada (21:23)", "Gancho de 1:25 que desmiente una frase conocida ('es verdad solo a medias, y la mitad que no lo es resulta la más interesante'). Después, 5 bloques de 1,5–5 min, y cierra con 'sus verdaderos enemigos' (la gente, las enfermedades y la pérdida de hábitat)."),
]
for t, d in STRUCT:
    a(f"<div class='card'><b>{e(t)}</b><p>{e(d)}</p></div>")
a("<h3>Patrón común <span class='tag opinion'>INFERIDO de 7 videos con capítulos</span></h3><ul>"
  "<li><b>Gancho: 30–85 s</b> (mediana de unos 50 s). Abre con una paradoja, una creencia falsa que se va a desmentir o una escena en segunda persona ('vos ahí'), nunca con 'hola, bienvenidos'.</li>"
  "<li><b>Cuerpo: una lista de bloques</b> que contestan la misma pregunta desde distintos ángulos: eras, actividades, horas del día o causas encadenadas. En los videos de 10–16 min los bloques duran de 45 s a 2 min; en los de 20 min o más, de 3 a 9 min.</li>"
  "<li><b>Cierre: vuelve a la pregunta del título</b> con un 'veredicto' o una reflexión. Ninguno cierra pidiendo la suscripción como punto principal.</li></ul>")

a("<h2>5. Patrones de títulos y descripciones</h2>")
a("<div class='card'><b>Títulos</b> <span class='tag medido'>MEDIDO</span>: comparé 791 videos largos ganadores (≥3x la mediana de su canal y ≥100k vistas) con 13.036 videos largos 'normales' de los mismos canales del núcleo (historia antigua y prehistoria).<ul>"
  "<li>Largo mediano: <b>64 caracteres / 11 palabras</b> en los dos grupos. El largo no hace la diferencia.</li>"
  "<li>Formato pregunta: <b>20%</b> en ganadores contra 30% en el resto. <b>La pregunta sola no garantiza nada</b> (es un dato que contradice la intuición). Lo que funciona es la pregunta <i>concreta y rara</i> ('How Did ANCIENT INUIT Igloos Stay Warm at -50°C With NO Electricity?'), no la genérica.</li>"
  "<li>Números: <b>38%</b> en ganadores contra 28% en el resto: listas ('12 monstruos', '28 Last Photos') y cifras de contraste ('-50°C', '3 minutos').</li>"
  "<li>Arranques más repetidos en ganadores (todos los temas): '¿Por qué…' (25), 'How did…' (20), 'Your life…' (16), 'Así era…' (15), 'What did…' (11).</li>"
  "<li>Palabras que más se repiten en ganadores del núcleo: <i>actually</i> (\"What Did Ancient Humans <b>Actually</b> Do All Day?\"), <i>extinct</i>, <i>prehistoric</i>, <i>creatures</i>, <i>depredadores</i>, <i>salvaje</i>.</li>"
  "<li>Fórmula que se repite en EN y ya se está copiando en ES: <b>'¿Qué hacían realmente [grupo antiguo] [situación cotidiana]?'</b> y <b>'¿Cómo sobrevivían [grupo] a [condición extrema] sin [tecnología moderna]?'</b></li></ul></div>")
a("<div class='card'><b>Descripciones</b> <span class='tag medido'>MEDIDO, muestra chica: 16 videos</span><ul>"
  "<li>Largo mediano: unos 1.780 caracteres (bastante larga).</li><li>14 de 16 tienen hashtags; 15 de 16 tienen tags (mediana: 17 tags).</li>"
  "<li>7 de 16 tienen capítulos con tiempos; 6 de 16 citan fuentes o estudios (Ink Explainer pone la bibliografía completa).</li>"
  "<li>La primera línea repite el gancho o la pregunta del video, no 'suscribite'. Solo 5 de 16 arrancan con un signo de pregunta; el resto abre con una escena o un dato.</li>"
  "<li>Estructura típica: gancho (1–3 líneas) → 'en este video vas a ver…' con viñetas → capítulos → fuentes → hashtags.</li></ul></div>")

a("<h2>6. Recomendación (HIPÓTESIS A PROBAR)</h2>")
a("<div class='card rec'><p class='big'>Nicho: vida diaria y supervivencia de los humanos antiguos y prehistóricos, en español.</p>"
  "<p class='big'>Formato: video largo de 12–18 min con ilustraciones IA de estilo propio y consistente, voz IA y fuentes en la descripción.</p>"
  "<p><b>Por qué</b> <span class='tag medido'>MEDIDO</span>: es el subnicho con más videos ganadores en canales nuevos y chicos (13,9M y 11,5M en EN; 0,2–1,3M en ES con canales de 2.000 a 16.000 subs). Sirve para cualquier país hispanohablante y no necesita grabar ni comprar metraje.</p>"
  "<p><b>Lo que no te va a gustar</b> <span class='tag opinion'>OPINIÓN basada en datos</span>: en inglés ya está saturado, y en español aparecieron al menos 10 canales en 2026 que traducen esos mismos éxitos (Estrictamente tradujo literal el título de Rome Unscrolled). Copiar títulos de inglés no te va a diferenciar. La ventaja tiene que venir de <b>preguntas que nadie hizo todavía en español</b> y de un estilo visual propio. Las miniaturas muestran que unos 15 canales usan la misma plantilla de muñequito cavernícola; el estilo documental realista (como Tiempos Antiguos o WUFO Español) está menos ocupado en este tema. <span class='tag opinion'>OPINIÓN</span></p>"
  "<p><b>Cuánto hace falta para monetizar</b> <span class='tag estimado'>ESTIMADO</span>: el requisito es 1.000 subs y 4.000 horas de reproducción (240.000 minutos) en 12 meses. Con videos de 15 min y una retención promedio de unos 6 min por vista, son unas <b>40.000 vistas acumuladas</b>. Un solo video como los de Cronología de la Humanidad o KROG (200–430k) alcanzaría. La mayoría de los canales no lo logra: en este tema, solo 6 de 73 canales jóvenes de formato largo en ES tienen mediana ≥20k.</p></div>")
a("<h3>Títulos modelo (hipótesis)</h3><ul>"
  "<li>¿Cómo dormían los humanos prehistóricos a −30 °C sin fuego toda la noche?</li>"
  "<li>¿Qué hacían realmente los humanos antiguos cuando se enfermaban?</li>"
  "<li>¿Cuánto durarías en cada época de la humanidad? (formato Fossil, aplicado a la historia humana en vez de las eras geológicas)</li>"
  "<li>Así era un día completo en una aldea de hace 10.000 años</li></ul>")
a("<h3>Descripción modelo (hipótesis)</h3><pre>"
  + e("""Hace 20.000 años, en plena Edad de Hielo, una noche podía bajar a −30 °C. Y aun así, nuestros antepasados se despertaban vivos al día siguiente. ¿Cómo lo hacían?

En este video vas a ver:
▸ Por qué el fuego no alcanzaba para pasar la noche
▸ Las pieles, los refugios semienterrados y el calor del grupo
▸ Lo que dicen los restos arqueológicos sobre cómo dormían
▸ Qué haría tu cuerpo si te tocara vivir esa noche

0:00 La noche que no debería sobrevivirse
0:50 El problema: perder calor durmiendo
...
14:10 Veredicto: ¿podrías sobrevivir vos?

📚 Fuentes:
▸ [estudio / libro, autor, año]
▸ [estudio / libro, autor, año]

Las imágenes de este video fueron creadas con IA con fines ilustrativos.

#prehistoria #humanosantiguos #historia""") + "</pre>")
a("<h3>Estructura de video modelo (hipótesis, basada en los capítulos medidos)</h3><div class='tw'><table><tr><th>Tramo</th><th>Duración</th><th>Qué pasa</th></tr>"
  "<tr><td>Gancho</td><td>0:00–0:40</td><td>Escena en segunda persona ('Imaginá que esta noche te toca dormir a −30 °C…') + contraste con tu vida de hoy + promesa de algo contraintuitivo. Sin presentación ni nombre del canal. (Así arrancan 4 de los 6 videos analizados con Gemini.)</td></tr>"
  "<tr><td>Planteo</td><td>0:50–2:00</td><td>Por qué el problema era grave (datos concretos: temperatura, calorías).</td></tr>"
  "<tr><td>Bloques 1–6</td><td>2:00–13:00</td><td>Una solución o actividad por bloque (de 1,5 a 2 min cada uno). Cada bloque abre con una pregunta chica y cierra con un dato sorprendente que lleva al siguiente.</td></tr>"
  "<tr><td>Veredicto</td><td>13:00–15:00</td><td>Vuelve a la pregunta del título con una frase de reflexión que conecte con el presente. Pedí la suscripción solo acá, al final, y cerrá con una pregunta para los comentarios.</td></tr>"
  "<tr><td>Producción</td><td>todo el video</td><td>Una imagen nueva cada 5–8 s (8–12 por minuto) con zoom o paneo lento, voz pausada (unas 140 palabras/min), música instrumental suave y efectos de sonido puntuales. Citá 1 o 2 estudios reales con nombre.</td></tr></table></div>")
a("<h3>Cómo probarlo sin perder tiempo <span class='tag opinion'>OPINIÓN</span></h3><ol>"
  "<li>Publicá 6 videos en 6 semanas: 3 del tipo '¿Cómo sobrevivían…?' y 3 de '¿Qué hacían realmente…?'.</li>"
  "<li>Medí en YouTube Studio el CTR (sirve si supera el 5%) y la retención en el minuto 1 (sirve si supera el 60%).</li>"
  "<li>Si a los 6 videos ninguno pasa de 5.000 vistas, probá el plan B: <b>espacio en español</b> (segundo en el ranking), con imágenes de la NASA, que son de dominio público.</li>"
  "<li>Marcá el contenido como IA cuando corresponda: YouTube exige declararlo si es realista. Escribí cada guion desde cero: la política de 'contenido inauténtico' penaliza los videos en serie hechos con plantilla.</li></ol>")

a("<h2>7. Límites de esta investigación</h2><ul>"
  f"<li>Analicé <b>{len(M)}</b> canales de menos de 200k subs (de {len(CH)} encontrados) con {Q['search_calls']} búsquedas. La muestra es grande en total, pero <b>chica en algunos cruces</b>: vida salvaje EN (4 videos largos), geografía (2) e ingeniería ES (3).</li>"
  "<li>La búsqueda de la API ordena por vistas: favorece a los ganadores (sesgo de supervivencia). Los canales que fracasaron y no aparecen no se ven.</li>"
  "<li>El faceless se verificó con 4 miniaturas por canal. Los guiones y el análisis visual de 6 videos los hizo Gemini (IA): sirven para la estructura, pero no son citas oficiales palabra por palabra.</li>"
  "<li>El RPM y los ingresos son estimaciones generales, no datos de estos canales.</li>"
  "<li>'Video más visto' = el más visto entre los últimos 50 subidos de cada canal.</li>"
  "<li>Los datos crudos están en <code>research/data/nichos-2026-10/</code> (búsquedas, canales, métricas, outliers y videos en CSV/JSON).</li></ul>")
a("</main></body></html>")
OUT.write_text("\n".join(H), encoding="utf-8")
print("ok", OUT, len(ev), "canales en evidencia")
