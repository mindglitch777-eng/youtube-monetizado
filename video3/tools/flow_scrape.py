#!/usr/bin/env python3
"""
Radiografía de Google Flow (sin sesión) con Chromium completo, para escribir el script
con datos reales y no a ciegas.

Guarda en flow_scrape/:
  - capturas de cada página visitada (escritorio y celular)
  - el HTML final de cada página
  - TODO el JavaScript que carga la aplicación (y los chunks que lista el manifiesto)
  - el registro de red (qué URLs pide, con qué método y estado)
  - un índice de textos útiles encontrados en el código (placeholder del prompt,
    aria-labels, rutas de la API de generación)
"""
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright

OUT = Path("flow_scrape")
JS = OUT / "js"
PAGINAS = ["https://flow.google.com/", "https://flow.google.com/project/nuevo", "https://flow.google.com/about"]
BUSCAR = [
    r"Qu[eé] quieres crear", r"What do you want to create", r"placeholder", r"aria-label", r"arrow_forward", r"arrow_upward",
    r"batchGenerate\w*", r"generateImage\w*", r"runImage\w*", r"flowMedia\w*", r"aisandbox[\w.-]*", r"/v1[:/]\w[\w:/.-]*",
    r"api/auth/session", r"access_token", r"imageModel\w*", r"NANO_BANANA\w*", r"IMAGEN_\w+", r"GEM_PIX\w*", r"aspectRatio\w*",
    r"IMAGE_ASPECT_RATIO_\w+", r"recaptcha\w*", r"mediaGenerationId", r"workflowId", r"projectId",
]


def guardar_js(url, cuerpo):
    nombre = re.sub(r"[^\w.-]", "_", urlparse(url).path.strip("/"))[-150:] or "raiz.js"
    (JS / nombre).write_bytes(cuerpo)


def main():
    OUT.mkdir(exist_ok=True)
    JS.mkdir(exist_ok=True)
    red, vistos = [], set()
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True, args=["--disable-blink-features=AutomationControlled"])
        for nombre_ctx, opciones in [("escritorio", {"viewport": {"width": 1440, "height": 900}}),
                                     ("celular", p.devices["Pixel 7"])]:
            ctx = b.new_context(locale="es-419", **opciones)
            page = ctx.new_page()

            def resp(r):
                try:
                    red.append({"ctx": nombre_ctx, "url": r.url[:300], "metodo": r.request.method, "estado": r.status,
                                "tipo": r.request.resource_type})
                    if r.request.resource_type == "script" and r.url not in vistos and r.ok:
                        vistos.add(r.url)
                        guardar_js(r.url, r.body())
                except Exception:
                    pass
            page.on("response", resp)
            for i, url in enumerate(PAGINAS):
                try:
                    page.goto(url, wait_until="networkidle", timeout=60000)
                except Exception as e:
                    print("goto", url, e)
                time.sleep(4)
                base = f"{nombre_ctx}_{i}"
                page.screenshot(path=str(OUT / f"{base}.png"), full_page=True)
                (OUT / f"{base}.html").write_text(page.content())
                (OUT / f"{base}.url.txt").write_text(page.url)
                print(nombre_ctx, url, "→", page.url)
            # chunks de Next.js que no se cargaron todavía (las páginas del editor)
            try:
                manif = page.evaluate("() => (window.__BUILD_MANIFEST ? JSON.stringify(window.__BUILD_MANIFEST) : '')")
                if manif:
                    (OUT / "build_manifest.json").write_text(manif)
                    m = json.loads(manif)
                    rutas = {f for v in m.values() if isinstance(v, list) for f in v if f.endswith(".js")}
                    base = re.search(r"https://[^/]+", page.url).group(0)
                    for r in sorted(rutas):
                        u = urljoin(base + "/_next/", r)
                        if u in vistos:
                            continue
                        rr = ctx.request.get(u)
                        if rr.ok:
                            vistos.add(u)
                            guardar_js(u, rr.body())
            except Exception as e:
                print("manifest", e)
            ctx.close()
        b.close()
    (OUT / "red.json").write_text(json.dumps(red, indent=1))
    # índice de textos útiles en el código
    indice = {}
    for f in JS.glob("*"):
        txt = f.read_text(errors="ignore")
        for pat in BUSCAR:
            for m in re.finditer(pat, txt):
                ctx = txt[max(0, m.start() - 160): m.end() + 160].replace("\n", " ")
                indice.setdefault(pat, [])
                if len(indice[pat]) < 25:
                    indice[pat].append({"archivo": f.name, "contexto": ctx})
    (OUT / "indice.json").write_text(json.dumps(indice, ensure_ascii=False, indent=1))
    print("js guardados:", len(list(JS.glob("*"))), "· patrones con resultados:", {k: len(v) for k, v in indice.items()})


if __name__ == "__main__":
    main()
