#!/usr/bin/env python3
"""
Arma el informe de ideas (ronda 3) en Markdown y HTML a partir de los datos de
research/data/ideas-2026-10/. Los números de cada video se leen de los datos
(no se escriben a mano): en el texto, [[ID]] se reemplaza por el título con
link, vistas, suscriptores del canal y fecha.

  python3 research/informe/build_ideas.py
"""
import json
import re
from pathlib import Path

import markdown

R = Path(__file__).resolve().parents[1]
D = R / "data" / "ideas-2026-10"
V = {f["id"]: f for f in json.loads((D / "videos_metricas.json").read_text())}
P = json.loads((D / "puntajes.json").read_text())
C = json.loads((D / "comentarios.json").read_text())


def n(x):
    return f"{x:,}".replace(",", ".")


def ref(m):
    f = V[m.group(1)]
    subs = "subs ocultos" if f["subs"] is None else f"canal de {n(f['subs'])} subs"
    d = f["publicado"].split("-")
    return f"[{f['titulo'].strip()}]({f['url']}) — **{n(f['vistas'])} vistas**, {subs}, {d[2]}/{d[1]}/{d[0]}"


def num(m):
    return n(V[m.group(1)]["vistas"])


VEREDICTO = {"hacer": "✅ HACER", "probar": "🟡 PROBAR", "descartar": "❌ DESCARTAR"}


def tabla():
    filas = ["| # | Idea | Matriz (OPINIÓN) | Demanda | Competencia | Canales chicos | Pijama | **Final** | Videos ES / canales | Veredicto |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for f in P:
        filas.append(f"| {f['puesto']} | {f['nombre']} (idea {f['idea']}) | {f['matriz_promedio']} | {f['demanda']} | {f['competencia']} | "
                     f"{f['prueba_canal_chico']} | {f['encaje_pijama']} | **{f['final']}** | {f['videos_es']} / {f['canales_es']} | {VEREDICTO[f['veredicto']]} |")
    return "\n".join(filas)


def matriz():
    crit = ["gancho", "alcance", "curiosidad", "identificacion", "emocion", "compartir", "rewatch", "visual", "serie", "largo"]
    cab = "| Idea | " + " | ".join(c[:6] for c in crit) + " | Por qué (resumen) |"
    filas = [cab, "|" + "---|" * (len(crit) + 2)]
    for f in P:
        filas.append(f"| {f['idea']}. {f['nombre'][:38]} | " + " | ".join(str(f[c]) for c in crit) + f" | {f['por_que']} |")
    return "\n".join(filas)


TEXTO = open(Path(__file__).with_name("ideas_texto.md")).read()


def main():
    md = TEXTO.replace("{{TABLA}}", tabla()).replace("{{MATRIZ}}", matriz())
    md = re.sub(r"\[\[([\w-]{11})\]\]", ref, md)
    md = re.sub(r"\{\{v:([\w-]{11})\}\}", num, md)
    (R / "informe" / "ideas-pijama-2026-10.md").write_text(md)
    # Python-Markdown necesita una línea en blanco antes de cada lista
    lineas = md.split("\n")
    out = []
    for k, l in enumerate(lineas):
        es_lista = re.match(r"\s*([-*]|\d+\.) ", l)
        prev = lineas[k - 1] if k else ""
        if es_lista and prev.strip() and not re.match(r"\s*([-*]|\d+\.) ", prev) and not prev.startswith("  "):
            out.append("")
        out.append(l)
    cuerpo = markdown.markdown("\n".join(out), extensions=["tables", "sane_lists"])
    html = HTML.replace("{{CUERPO}}", cuerpo)
    (R / "informe" / "ideas-pijama-2026-10.html").write_text(html)
    print("ok", len(md), len(html))


HTML = """<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ideas para Pijama</title>
<style>
:root{--bg:#fbfaf7;--fg:#1d1d1f;--mut:#5d5d63;--line:#e3e0d8;--card:#fff;--acc:#1f5fbf;--med:#0f7b4a;--est:#9a6400;--opi:#7a3fb0}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#141416;--fg:#ececee;--mut:#a3a3aa;--line:#2c2c31;--card:#1c1c20;--acc:#7fb0ff;--med:#4fd497;--est:#f0b74a;--opi:#c79bf0}}
:root[data-theme="dark"]{--bg:#141416;--fg:#ececee;--mut:#a3a3aa;--line:#2c2c31;--card:#1c1c20;--acc:#7fb0ff;--med:#4fd497;--est:#f0b74a;--opi:#c79bf0}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:860px;margin:0 auto;padding:24px 16px 64px}
h1{font-size:1.7rem;line-height:1.25;margin:.2em 0 .4em}
h2{font-size:1.3rem;margin:2.2em 0 .6em;padding-top:.6em;border-top:1px solid var(--line)}
h3{font-size:1.1rem;margin:1.8em 0 .4em}
a{color:var(--acc);overflow-wrap:anywhere}
p,li{overflow-wrap:break-word}
table{border-collapse:collapse;font-size:.82rem;display:block;overflow-x:auto;max-width:100%;margin:1em 0}
th,td{border:1px solid var(--line);padding:6px 8px;vertical-align:top;text-align:left}
th{background:var(--card);position:sticky;top:0}
blockquote{margin:1em 0;padding:.6em 1em;background:var(--card);border-left:4px solid var(--acc);border-radius:6px}
code{font-size:.9em}
img{max-width:100%;height:auto;border-radius:8px;border:1px solid var(--line)}
strong{font-weight:650}
</style></head><body><main>
{{CUERPO}}
</main></body></html>
"""

if __name__ == "__main__":
    main()
