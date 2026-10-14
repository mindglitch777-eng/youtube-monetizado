#!/usr/bin/env python3
"""Arma research/informe/huecos-preguntas.html con los datos de research/data/huecos-2026-10 (no gasta cuota)."""
import html
import json
from pathlib import Path

R = Path(__file__).parent.parent
D = R / "data" / "huecos-2026-10"
OUT = Path(__file__).parent / "huecos-preguntas.html"
e = html.escape
Q = json.loads((D / "preguntas.json").read_text())
P1 = json.loads((D / "paso1_temas_ganadores.json").read_text())
P2 = json.loads((D / "paso2_oferta_es.json").read_text())
P3 = json.loads((D / "paso3_preguntas_comentarios.json").read_text())
CU = json.loads((D / "cuota.json").read_text())
COM = json.loads((D / "comentarios.json").read_text())
n_com = sum(len(v) for v in COM.values() if isinstance(v, list))


def n(x):
    return f"{int(x):,}".replace(",", ".")


def edad(fecha):
    if not fecha:
        return "s/d"
    y, m = int(fecha[:4]), int(fecha[5:7])
    meses = (2026 - y) * 12 + (10 - m)
    return f"{meses} meses" if meses < 24 else f"{meses // 12} años"


LATAM = {19, 20, 21, 22, 23, 24, 25, 26, 30, 12, 15, 29}
TOP5 = [20, 1, 24, 6, 19]
POR_QUE = {
    20: "Repite el formato con más prueba de todo el estudio (Fossil, 11,5M con un canal de 7 meses), pero aplicado a la megafauna de Argentina, que nadie cubrió en español. Sirve para abrir una serie.",
    1: "Sale de preguntas reales de la audiencia y se apoya en el tema más demandado (el frío), pero con un ángulo que nadie tituló. No compite con los 11 videos de 'cómo dormían'.",
    24: "Es el análogo más fuerte en español (el cruce de Bering, 1,36M en un canal de 15.500 subs) y Monte Verde no aparece en ningún título guardado. Le habla directo al público sudamericano.",
    6: "Responde una pregunta textual de los comentarios ('si se infectaba la herida, en una semana te morías') y en español hay 2 videos largos en total, con 749 vistas como máximo.",
    19: "El mismo formato de supervivencia por épocas, en el país con más hispanohablantes. Si funciona, se puede repetir con Perú, Argentina o Colombia. Tiene riesgo medio (epidemias, sacrificios): hay que cuidarlo.",
}

css = """
/* Layout: columna de lectura de 72rem; tabla filtrable que se expande por fila; acento ocre (pigmento de las cuevas) sobre gris piedra */
:root{
 --bg:#f6f6f3;--surface:#ffffff;--ink:#1f2326;--muted:#5d646a;--line:#dcdcd5;--accent:#b0661a;--accent-soft:#f3e5d4;
 --good:#2f7a4a;--warn:#9a6a00;--bad:#b03a2e;--chip:#ecebe5;
 --f-display:"Bricolage Grotesque",ui-sans-serif,system-ui,sans-serif;--f-body:"IBM Plex Sans",ui-sans-serif,system-ui,sans-serif;--f-data:"IBM Plex Mono",ui-monospace,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#15181a;--surface:#1d2124;--ink:#e8e8e3;--muted:#a3a9ad;--line:#33393d;--accent:#e39a4f;--accent-soft:#3a2a1a;--good:#6cc58c;--warn:#e3b54f;--bad:#ff8a7a;--chip:#272c2f;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#15181a;--surface:#1d2124;--ink:#e8e8e3;--muted:#a3a9ad;--line:#33393d;--accent:#e39a4f;--accent-soft:#3a2a1a;--good:#6cc58c;--warn:#e3b54f;--bad:#ff8a7a;--chip:#272c2f;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font:16px/1.6 var(--f-body);padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
main{max-width:72rem;margin:0 auto;padding-block:32px 96px;display:grid;gap:8px}
h1,h2,h3{font-family:var(--f-display);text-wrap:balance;line-height:1.15;margin:0}
h1{font-size:clamp(1.9rem,4vw,2.8rem);font-weight:700;letter-spacing:-.01em}
h2{font-size:1.55rem;margin-top:48px;padding-bottom:8px;border-bottom:2px solid var(--line)}
h3{font-size:1.15rem;margin-top:24px}
p,li{max-width:70ch}
a{color:var(--accent)}a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.eyebrow{font:600 .75rem/1 var(--f-data);letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}
.muted{color:var(--muted)}.small{font-size:.85rem}
.tag{display:inline-block;font:600 .68rem/1.6 var(--f-data);letter-spacing:.05em;text-transform:uppercase;padding:0 7px;border-radius:4px;background:var(--chip);color:var(--muted);white-space:nowrap}
.tag.medido{color:var(--good)}.tag.opinion{color:var(--accent)}.tag.estimado{color:var(--warn)}.tag.riesgo{color:var(--bad)}
.verdict{background:var(--accent-soft);border-left:4px solid var(--accent);padding:16px 20px;border-radius:0 8px 8px 0;display:grid;gap:8px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-top:8px}
.kpi{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:12px 14px}
.kpi b{display:block;font:700 1.5rem/1.2 var(--f-data);font-variant-numeric:tabular-nums}
.tw{overflow-x:auto;border:1px solid var(--line);border-radius:8px;background:var(--surface)}
table{border-collapse:collapse;width:100%;font-size:.88rem}
th,td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{font:600 .72rem/1.3 var(--f-data);letter-spacing:.05em;text-transform:uppercase;color:var(--muted);background:var(--chip);white-space:nowrap}
td.num{text-align:right;font-family:var(--f-data);font-variant-numeric:tabular-nums;white-space:nowrap}
.filters{display:flex;flex-wrap:wrap;gap:10px;align-items:end;margin:12px 0}
.filters label{display:grid;gap:4px;font:600 .72rem/1 var(--f-data);text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}
.filters input,.filters select{font:inherit;font-size:.95rem;padding:7px 10px;border:1px solid var(--line);border-radius:6px;background:var(--surface);color:var(--ink);min-width:0}
.filters input{width:min(320px,100%)}
.score{display:grid;gap:4px;min-width:96px}
.score b{font:700 1.15rem/1 var(--f-data)}
.bar{display:flex;height:7px;border-radius:4px;overflow:hidden;background:var(--chip)}
.bar span{display:block;height:100%}
.s-dem{background:var(--good)}.s-out{background:color-mix(in srgb,var(--good) 55%,var(--surface))}.s-hue{background:var(--accent)}.s-ori{background:color-mix(in srgb,var(--accent) 45%,var(--surface))}
.legend{display:flex;flex-wrap:wrap;gap:12px;font-size:.8rem;color:var(--muted)}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:4px;vertical-align:-1px}
button.more{font:600 .8rem var(--f-body);border:1px solid var(--line);background:var(--surface);color:var(--accent);border-radius:6px;padding:4px 10px;cursor:pointer;white-space:nowrap}
tr.detail td{background:var(--bg)}
.detail-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:16px;padding:6px 2px}
.detail-grid > div{min-width:0}
.detail-grid h4{font:600 .75rem/1.2 var(--f-data);text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin:0 0 6px}
.hook{font-style:italic;border-left:3px solid var(--accent);padding-left:12px;margin:0}
ol,ul{padding-left:1.2rem;margin:4px 0}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr));gap:12px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:16px;display:grid;gap:8px;align-content:start}
.rank{font:700 2rem/1 var(--f-display);color:var(--accent)}
.empty{padding:16px;color:var(--muted)}
@media (prefers-reduced-motion:no-preference){tr.detail{animation:fade .18s ease-out}@keyframes fade{from{opacity:.4}to{opacity:1}}}
"""

H = []
a = H.append
a('<title>Preguntas originales para el canal</title><meta name="claude:viewport-fit-sides" content="cover">')
a('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
a('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700&family=IBM+Plex+Mono:wght@500;600;700&family=IBM+Plex+Sans:ital,wght@0,400;0,600;1,400&display=swap">')
a(f"<style>{css}</style><main>")
a('<p class="eyebrow">Ronda 2 · humanos antiguos en español · 14/10/2026</p>')
a("<h1>30 preguntas que todavía nadie contestó bien en español</h1>")
a('<p class="muted">Buscadas con la API de YouTube a partir de los 229 videos ganadores del nicho, 20 búsquedas nuevas en español y los comentarios de 10 videos virales. <span class="tag medido">Medido</span> = viene de la API. <span class="tag opinion">Opinión</span> = criterio mío. <span class="tag estimado">Estimado</span> = cálculo o fuente externa.</p>')

a('<div class="kpis">')
for lbl, val in [("búsquedas nuevas", CU["search"]), ("unidades esta ronda", n(CU["total"])), ("unidades hoy (total)", n(7571 + CU["total"])),
                 ("videos en español medidos", n(452)), ("comentarios leídos", n(n_com)), ("ganadores del nicho analizados", 229)]:
    a(f'<div class="kpi"><b>{val}</b><span class="muted small">{lbl}</span></div>')
a("</div>")

a('<h2>Lo que hay que saber antes de elegir</h2><div class="verdict">'
  "<p><b>El nicho en español está saturado de intentos, no de videos buenos.</b> En las 20 búsquedas aparecieron 326 canales. En temas como diversión, agua o parto, la mayoría de los canales tiene menos de 1.000 suscriptores, se creó en 2026 y sus videos rondan entre 18 y 300 vistas (mediana). Ejemplo: en 'cómo se divertían los humanos prehistóricos', 25 de 29 canales tienen menos de 1.000 subs. <span class='tag medido'>Medido</span></p>"
  "<p><b>Eso cambia qué es un 'hueco'.</b> Casi ningún tema está vacío: está lleno de copias que no despegan. Un video de calidad tiene lugar, pero el título solo no te diferencia, porque los copiones usan los mismos. <span class='tag opinion'>Opinión</span></p>"
  "<p><b>Lo que sí está vacío</b> son los ángulos <b>latinoamericanos y españoles</b> (megafauna de las Pampas, Monte Verde, Atapuerca, chasquis, mayas y agua) y los <b>casos concretos con nombre</b> (Shanidar, Nataruk, Taung). En 51.881 títulos guardados aparecen 0 o casi 0 veces. Por eso 12 de las 30 preguntas apuntan ahí. <span class='tag medido'>Medido</span></p>"
  "<p><b>Ya cubiertos en español</b> (los saqué): cómo dormían (14 videos con 50k o más), frío (11), placer (Cronología, 435k), qué hacían todo el día (Homo Curioso, 473k), por qué empezaron a usar ropa (235k), parto (310k), sal (90k), cerveza (194k), conservar alimentos (66k). <span class='tag medido'>Medido</span></p>"
  "</div>")

# ---------- tabla filtrable ----------
a("<h2>Las 30 preguntas</h2>")
a('<p class="muted small">Tocá <b>Ver</b> en una fila para abrir el gancho, los bloques, las fuentes y el riesgo. Puntaje sobre 100: demanda del video análogo (hasta 35, ajustada por cuánto se parece el análogo), factor outlier del análogo (hasta 15), hueco en español (hasta 30), todo eso <span class="tag medido">medido</span>, más originalidad (hasta 20) y penalización por riesgo (0 a −10), que son <span class="tag opinion">opinión</span>.</p>')
a('<div class="legend"><span><i class="s-dem"></i>demanda</span><span><i class="s-out"></i>outlier</span><span><i class="s-hue"></i>hueco ES</span><span><i class="s-ori"></i>originalidad</span></div>')
temas = sorted({q["tema"] for q in Q})
a('<div class="filters"><label for="f-text">Buscar<input id="f-text" type="search" placeholder="Ej.: mexica, frío, neandertal"></label>'
  '<label for="f-tema">Tema<select id="f-tema"><option value="">Todos</option>' + "".join(f'<option>{e(t)}</option>' for t in temas) + '</select></label>'
  '<label for="f-origen">Enfoque<select id="f-origen"><option value="">Todos</option><option value="latam">Latinoamérica / España</option><option value="general">General</option></select></label>'
  '<label for="f-riesgo">Riesgo<select id="f-riesgo"><option value="">Todos</option><option value="0">Bajo</option><option value="5">Medio</option></select></label>'
  '<label for="f-sort">Ordenar<select id="f-sort"><option value="score">Puntaje</option><option value="views">Vistas del análogo</option><option value="hueco">Hueco en español</option></select></label></div>')
a('<div class="tw"><table id="qt"><thead><tr><th>#</th><th>Pregunta</th><th>Puntaje</th><th>Video análogo</th><th>En español hoy</th><th></th></tr></thead><tbody>')
for q in Q:
    p, an = q["puntaje"], q["analogo_datos"]
    seg = "".join(f'<span class="{c}" style="width:{max(0, v)}%"></span>' for c, v in (("s-dem", p["demanda"]), ("s-out", p["outlier"]), ("s-hue", p["hueco_es"]), ("s-ori", p["originalidad"])))
    origen = "latam" if q["n"] in LATAM else "general"
    search = e(" ".join([q["titulo"], *q["alt"], q["tema"], q["es_txt"]]).lower())
    rid = f"q{q['n']}"
    a(f'<tr class="row" data-tema="{e(q["tema"])}" data-origen="{origen}" data-riesgo="{q["riesgo_pen"]}" data-score="{p["total"]}" data-views="{an["vistas"]}" data-hueco="{p["hueco_es"]}" data-search="{search}">'
      f'<td class="num">{q["ranking"]}</td>'
      f'<td style="min-width:240px"><b>{e(q["titulo"])}</b><br><span class="tag">{e(q["tema"])}</span> {"<span class=\'tag opinion\'>LatAm/España</span>" if origen == "latam" else ""} {"<span class=\'tag riesgo\'>riesgo medio</span>" if q["riesgo_pen"] else ""}</td>'
      f'<td><div class="score"><b>{p["total"]:.0f}</b><div class="bar" aria-hidden="true">{seg}</div><span class="muted small">análogo {e(q["cercania"])}</span></div></td>'
      f'<td style="min-width:200px"><a href="https://www.youtube.com/watch?v={an["video_id"]}" target="_blank" rel="noopener">{e(an["titulo"][:70])}</a><br>'
      f'<span class="muted small">{e(an["canal"])} · <b>{n(an["vistas"])}</b> vistas · {n(an["subs"])} subs · canal de {edad(an["canal_creado"])}{" · x" + str(an["factor_outlier"]) if an["factor_outlier"] else ""}</span></td>'
      f'<td style="min-width:220px" class="small">{e(q["es_txt"])}</td>'
      f'<td><button class="more" type="button" aria-expanded="false" aria-controls="{rid}">Ver</button></td></tr>')
    a(f'<tr class="detail" id="{rid}" hidden><td></td><td colspan="5"><div class="detail-grid">'
      f'<div><h4>Títulos alternativos</h4><ul>' + "".join(f"<li>{e(x)}</li>" for x in q["alt"]) + '</ul>'
      f'<h4 style="margin-top:12px">Gancho (primeros 40 s)</h4><p class="hook">{e(q["gancho"])}</p></div>'
      f'<div><h4>Bloques</h4><ol>' + "".join(f"<li>{e(b)}</li>" for b in q["bloques"]) + '</ol></div>'
      f'<div><h4>Fuentes</h4><ul class="small">' + "".join(f"<li>{e(f)}</li>" for f in q["fuentes"]) + '</ul>'
      f'<h4 style="margin-top:12px">Riesgo de política</h4><p class="small">{e(q["riesgo"])}</p>'
      f'<h4 style="margin-top:12px">Puntaje</h4><p class="small mono">demanda {p["demanda"]} · outlier {p["outlier"]} · hueco {p["hueco_es"]} · originalidad {p["originalidad"]} · riesgo {p["riesgo"]} = <b>{p["total"]}</b></p></div>'
      f'</div></td></tr>')
a('</tbody></table><p class="empty" id="empty" hidden>Ninguna pregunta coincide con el filtro. Probá con otra palabra o elegí "Todos".</p></div>')
a('<p class="muted small">Fuentes marcadas "verificar": no estoy seguro del detalle exacto (edición, página o cifra). No cité frases de ningún libro. Las cifras de los títulos (años, metros, grados) salen de esos estudios; antes de publicar, chequealas en la fuente.</p>')

# ---------- top 5 ----------
a("<h2>Los 5 para empezar</h2>")
a('<p class="muted">No son exactamente los 5 de mayor puntaje: elegí dos formatos para probar al mismo tiempo, "¿cuánto durarías?" (20 y 19) y "pregunta concreta" (1, 24 y 6), y que el canal arranque con identidad latinoamericana. <span class="tag opinion">Opinión</span></p><div class="cards">')
byn = {q["n"]: q for q in Q}
for i, k in enumerate(TOP5, 1):
    q = byn[k]
    a(f'<div class="card"><span class="rank">{i}</span><h3 style="margin:0">{e(q["titulo"])}</h3><p class="small muted">Puntaje {q["puntaje"]["total"]:.0f} · puesto {q["ranking"]} de 30</p><p class="small">{e(POR_QUE[k])}</p></div>')
a("</div>")

# ---------- paso 1 ----------
a("<h2>Paso 1. Temas que ganan en el nicho</h2>")
a(f'<p class="muted small">Videos largos (≥4 min) con ≥100k vistas y ≥3x la mediana de su canal, de canales de menos de 200k subs del núcleo "humanos antiguos". Saqué las batallas de animales, lo infantil y las novelas. Muestra: 229 videos. Un video puede contar en más de un tema. Clasificado por palabras del título, así que es aproximado. <span class="tag medido">Medido</span></p>')
a('<div class="tw"><table><tr><th>Tema</th><th>Ganadores</th><th>En inglés</th><th>Vistas EN</th><th>En español</th><th>Vistas ES</th><th>Ejemplo más visto</th></tr>')
for r in P1:
    top = r["videos"][0]
    a(f'<tr><td>{e(r["tema"])}</td><td class="num">{r["ganadores"]}</td><td class="num">{r["en"]}</td><td class="num">{n(r["vistas_en"])}</td><td class="num">{r["es"]}</td><td class="num">{n(r["vistas_es"])}</td><td class="small">{e(top["titulo"][:70])} <span class="muted">({n(top["vistas"])})</span></td></tr>')
a("</table></div>")

# ---------- paso 2 ----------
a("<h2>Paso 2. Qué hay en español por tema</h2>")
a('<p class="muted small">Una búsqueda por tema (relevanceLanguage=es, últimos 12 meses, orden por vistas, máximo 50 resultados). Cuento solo videos largos (≥8 min) con título en español. El sesgo: la búsqueda muestra lo más visto, así que los canales que fracasaron casi del todo pueden no aparecer. <span class="tag medido">Medido</span></p>')
a('<div class="tw"><table><tr><th>Tema</th><th>Consulta</th><th>Largos ES</th><th>Con ≥50k</th><th>Canales</th><th>&lt;1.000 subs</th><th>Creados en 2026</th><th>Mediana vistas</th><th>Máximo</th></tr>')
for r in P2:
    a(f'<tr><td>{e(r["tema"])}</td><td class="small">{e(r["consulta"])}</td><td class="num">{r["largos_es"]}</td><td class="num">{r["largos_es_50k"]}</td><td class="num">{r["canales"]}</td><td class="num">{r["canales_menos_1000_subs"]}</td><td class="num">{r["canales_creados_2026"]}</td><td class="num">{n(r["mediana_vistas"])}</td><td class="num">{n(r["max_vistas"])}</td></tr>')
a('<tr><td>latam: vida mexica</td><td class="small">cómo era un día en la vida de un mexica azteca</td><td class="num">10</td><td class="num">2</td><td colspan="5" class="small muted">245k (canal de 4,46M) y 201k (Un Día En La Historia, 9.880 subs). Ninguno sobre niños mexicas.</td></tr>')
a('<tr><td>latam: megafauna sudamericana</td><td class="small">megafauna sudamericana humanos edad de hielo megaterio gliptodonte</td><td colspan="7" class="small muted">0 resultados: la consulta fue demasiado larga y se perdieron 100 unidades. En los títulos guardados hay 6 en español sobre smilodon, megaterio o gliptodonte, el más visto con 6.478.</td></tr>')
a("</table></div>")

# ---------- paso 3 ----------
a("<h2>Paso 3. Lo que pregunta la audiencia</h2>")
a(f'<p class="muted small">Leí {n_com} comentarios (los 100 más relevantes de 10 videos ganadores, 1 unidad cada video). Encontré 94 con preguntas o pedidos; estos son los que se convirtieron en ideas. Muestra chica. <span class="tag medido">Medido</span></p><ul>')
for txt, uso in [
    ("'why not just move southward???' y '¿os pensáis que eran tontos?' (videos del iglú y de CAVERNICOLAS)", "pregunta 1"),
    ("'¿Qué hacían con los desechos?' y 'You live in an igloo. It's −50 °C. Suddenly you develop diarrhea.'", "pregunta 2"),
    ("'¿De dónde sacaban tanta leña para tantos meses?'", "pregunta 3"),
    ("'I always wake up after 4 hours of sleep… thanks for letting me know it is normal' (39 likes, Ink Explainer)", "pregunta 4"),
    ("'y la esperanza de vida? te cortabas con algo y si se infectaba la herida en una semana te morías' (Homo Curioso)", "pregunta 6"),
    ("'What about the Greeks, the Persians, the Egyptians…' (26 likes, Rome Unscrolled)", "preguntas 21, 22 y 25: llevar el formato a culturas que el público hispano siente propias"),
    ("'me gustaría que en la descripción pongan la bibliografía' (Homo Curioso)", "fuentes reales en cada descripción"),
    ("Varias quejas de 'AI slop' y animaciones que no coinciden con la narración (video del iglú)", "la calidad de imagen se nota y se castiga"),
    ("Preguntas sobre ojos, nariz y 'razas' (411 likes, Tito Primitivo)", "las descarté: mucha demanda, pero riesgo alto de comentarios racistas y de política"),
]:
    a(f"<li><span class='small'>{e(txt)}</span> <span class='muted small'>→ {e(uso)}</span></li>")
a("</ul>")

# ---------- estilos ----------
a("<h2>Tres estilos visuales distintos al muñequito</h2>")
a('<p class="muted small">Costos estimados para producir <b>sin computadora</b>, con el celular y herramientas gratis. Los límites de los planes gratis cambian seguido; no los pude verificar hoy. Hay un dato en contra: según una guía de terceros, los modelos de imagen de Gemini no tienen plan gratis (<a href="https://www.aifreeapi.com/en/posts/google-gemini-api-free-tier" target="_blank" rel="noopener">aifreeapi.com</a>), así que tu clave de Gemini no sirve para generar imágenes sin pagar. <span class="tag estimado">Estimado</span></p><div class="cards">')
for nombre, que, como, costo, riesgo in [
    ("Documental realista", "Imágenes fotorrealistas con luz de cine y títulos sobrios, como Tiempos Antiguos o WUFO Español. Es el estilo que más se diferencia del muñequito en este tema.",
     "Generador de imágenes con plan gratis desde el celular + el pipeline del repo para voz y armado.", "US$0, pero es el más lento: para 12-15 min hacen falta unas 100 a 150 imágenes (una cada 6 a 8 s). Con límites diarios gratis, calculá entre 3 y 5 días de generación por video. Lo más difícil es que el mismo personaje se vea igual en todas.",
     "Si parecen fotos de época reales, YouTube pide marcarlo como contenido alterado o sintético. Poné 'Recreación' en pantalla."),
    ("Pintura oscura", "Óleo dramático y en penumbra, con poco detalle, como Fossil. La pincelada disimula los errores típicos de la IA (manos, caras).",
     "El mismo generador con un estilo fijo ('pintura al óleo oscura') y menos personajes recurrentes.", "US$0. Más rápido que el realista porque tolera imágenes menos perfectas y planos más largos (8 a 10 s): unas 80 a 100 imágenes por video, 2 o 3 días con plan gratis.",
     "Bajo. Evitar sangre explícita en ataques de animales."),
    ("Mapas, grabados y códices", "Mapas animados, grabados del siglo XIX y láminas de códices. Para los temas latinoamericanos, el Códice Mendoza, los grabados del viaje del Beagle y los mapas antiguos son de dominio público.",
     "Imágenes de dominio público de Wikimedia Commons y bibliotecas, mapas simples hechos con plantillas, y la IA solo para la miniatura.", "US$0 y el más rápido de producir (1 o 2 días), y es el más seguro legalmente. La contra es que es menos llamativo: la miniatura tiene que compensarlo.",
     "Muy bajo. Revisá la licencia de cada imagen (que diga 'public domain' o CC0)."),
]:
    a(f'<div class="card"><h3 style="margin:0">{nombre}</h3><p class="small">{e(que)}</p><p class="small"><b>Cómo:</b> {e(como)}</p><p class="small"><b>Costo real:</b> {e(costo)}</p><p class="small"><b>Riesgo:</b> {e(riesgo)}</p></div>')
a("</div>")
a('<p class="small muted">Edición sin computadora: según el README de <code>kai-studio-web</code>, el repo tiene un pipeline de GitHub Actions que arma la voz y renderiza el video a partir de las imágenes. Ese workflow está en otra rama y no lo revisé en esta ronda. <span class="tag opinion">Verificar</span></p>')

# ---------- horas ----------
a("<h2>¿Cuántas vistas hacen falta para 8.000 horas?</h2>")
a('<p class="small">Desde el <b>1 de febrero de 2027</b>, los canales nuevos van a necesitar <b>1.000 suscriptores y 8.000 horas de reproducción en 12 meses</b>, o 20 millones de vistas de Shorts en 90 días (hoy son 4.000 horas o 10 millones). Fuentes de prensa: '
  '<a href="https://www.business-standard.com/technology/tech-news/technology-tech-news-youtube-partner-program-monetisation-rules-2027-watch-hours-shorts-views-126081100708_1.html" target="_blank" rel="noopener">Business Standard</a>, '
  '<a href="https://streamer.guide/blog/youtube-partner-program-2027-monetization-changes" target="_blank" rel="noopener">streamer.guide</a>, '
  '<a href="https://socialday.live/features/youtube-raises-partner-program-entry-bar-to-8-000-watch-hours-from-february-2027" target="_blank" rel="noopener">socialday.live</a>. '
  'Según esas notas, YouTube lo anunció en su blog el 10 de agosto de 2026. No pude abrir el anuncio oficial desde acá. Los canales que ya están en el programa no cambian. <span class="tag estimado">Estimado: fuente de prensa</span></p>')
a('<p class="small muted">Cuenta: 8.000 horas = 480.000 minutos. Vistas necesarias = 480.000 ÷ (duración × retención promedio).</p>')
a('<div class="tw"><table><tr><th>Duración</th><th>Retención 35%</th><th>Retención 45%</th><th>Retención 55%</th></tr>')
for L in (12, 15, 18):
    a(f"<tr><td>{L} min</td>" + "".join(f'<td class="num">{n(round(480000 / (L * r)))}</td>' for r in (0.35, 0.45, 0.55)) + "</tr>")
a("</table></div>")
a('<p class="small">Con 15 minutos y 45% de retención hacen falta unas <b>71.000 vistas</b> en el año. Como referencia del paso 2: en temas como agua, diversión o parto, la mediana de un video largo en español está entre 18 y 300 vistas. Llegar a 71.000 exige uno o dos videos que exploten, no constancia sola. Y si apuntás a calificar antes del 1/2/2027 con el umbral viejo (4.000 horas = la mitad de esas vistas), hay que entrar antes de esa fecha: no sé si las solicitudes que ya están en revisión ese día mantienen las reglas viejas, así que verificalo. <span class="tag opinion">Opinión</span></p>')

# ---------- límites ----------
a("<h2>Límites de esta ronda</h2><ul class='small'>"
  f"<li>Cuota: {CU['search']} búsquedas y {CU['otras']} consultas baratas = <b>{n(CU['total'])} unidades</b> en esta ronda. Hoy en total: unas {n(7571 + CU['total'])} de 10.000. Una búsqueda (megafauna) no devolvió resultados.</li>"
  "<li>Sesgo de supervivencia: las búsquedas devuelven lo más visto. No vemos los miles de videos que fracasaron del todo, así que el panorama real es todavía más duro.</li>"
  "<li>Paso 1 clasifica por palabras del título (229 videos): es aproximado.</li>"
  "<li>Comentarios: 10 videos y 986 comentarios. Es una muestra chica para medir demanda; sirve para encontrar ideas.</li>"
  "<li>Para varias preguntas el video análogo es 'parcial' o 'lejano' (lo dice la tabla). Esa demanda es una pista, no una prueba.</li>"
  "<li>Las fuentes son de memoria. Las marcadas 'verificar' necesitan chequeo, y conviene chequear todas antes de grabar.</li>"
  "<li>Datos crudos: <code>research/data/huecos-2026-10/</code> (búsquedas, videos, canales, comentarios, paso1-3, preguntas.csv).</li></ul>")
a("</main>")
a("""<script>
(function(){
  const rows=[...document.querySelectorAll('#qt tr.row')];
  const tbody=document.querySelector('#qt tbody');
  const $=id=>document.getElementById(id);
  function apply(){
    const t=$('f-text').value.trim().toLowerCase(), tema=$('f-tema').value, o=$('f-origen').value, r=$('f-riesgo').value, s=$('f-sort').value;
    const key=s==='views'?'views':s==='hueco'?'hueco':'score';
    rows.sort((a,b)=>Number(b.dataset[key])-Number(a.dataset[key])||Number(b.dataset.score)-Number(a.dataset.score));
    let shown=0;
    rows.forEach(row=>{
      const det=row.nextElementSibling;
      const ok=(!t||row.dataset.search.includes(t))&&(!tema||row.dataset.tema===tema)&&(!o||row.dataset.origen===o)&&(!r||row.dataset.riesgo===r);
      row.hidden=!ok; if(!ok) det.hidden=true; else if(row.querySelector('button').getAttribute('aria-expanded')==='true') det.hidden=false;
      tbody.appendChild(row); tbody.appendChild(det);
      if(ok) shown++;
    });
    $('empty').hidden=shown>0;
  }
  ['f-text','f-tema','f-origen','f-riesgo','f-sort'].forEach(id=>$(id).addEventListener('input',apply));
  tbody.addEventListener('click',ev=>{
    const b=ev.target.closest('button.more'); if(!b) return;
    const d=document.getElementById(b.getAttribute('aria-controls'));
    const open=b.getAttribute('aria-expanded')!=='true';
    b.setAttribute('aria-expanded',String(open)); b.textContent=open?'Cerrar':'Ver'; d.hidden=!open;
  });
})();
</script>""")
OUT.write_text("\n".join(H), encoding="utf-8")
print("ok", OUT)
