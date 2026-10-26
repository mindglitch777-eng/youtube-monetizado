#!/usr/bin/env python3
"""
Bot de Google Flow (web) para GitHub Actions, con UNA cuenta y su sesión ya iniciada.

No escribe contraseñas: usa las cookies de una sesión abierta (secret FLOW_COOKIES,
formato cookies.txt de Netscape o JSON exportado por una extensión). Usa el Chrome
que ya viene instalado en los runners (sin apt).

  python3 video3/tools/flow_bot.py probe     -> abre Flow, saca capturas y un mapa de
                                                botones/campos a flow_out/ para escribir el bot
"""
import json
import os
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path("flow_out")
URL = "https://labs.google/fx/tools/flow"


def leer_cookies(txt):
    txt = txt.strip()
    if txt.startswith("[") or txt.startswith("{"):
        d = json.loads(txt)
        d = d.get("cookies", d) if isinstance(d, dict) else d
        out = []
        for c in d:
            ck = {"name": c["name"], "value": c["value"], "domain": c["domain"], "path": c.get("path", "/"),
                  "secure": bool(c.get("secure", True)), "httpOnly": bool(c.get("httpOnly", False))}
            exp = c.get("expirationDate") or c.get("expires")
            if exp and exp > 0:
                ck["expires"] = int(exp)
            ss = (c.get("sameSite") or "").lower()
            ck["sameSite"] = {"strict": "Strict", "lax": "Lax", "none": "None", "no_restriction": "None"}.get(ss, "Lax")
            out.append(ck)
        return out
    out = []
    for l in txt.splitlines():
        if not l.strip() or (l.startswith("#") and not l.startswith("#HttpOnly_")):
            continue
        http_only = l.startswith("#HttpOnly_")
        p = l.replace("#HttpOnly_", "").split("\t")
        if len(p) < 7:
            continue
        dom, _, path, sec, exp, name, val = p[:7]
        ck = {"name": name, "value": val, "domain": dom, "path": path, "secure": sec.upper() == "TRUE",
              "httpOnly": http_only, "sameSite": "Lax"}
        if exp.isdigit() and int(exp) > 0:
            ck["expires"] = int(exp)
        out.append(ck)
    return out


def mapa(page):
    """Lista lo que se puede tocar en la página, para escribir el bot con selectores reales."""
    return page.evaluate("""() => [...document.querySelectorAll('button,a,textarea,input,[role=button],[contenteditable=true]')]
      .filter(e => e.offsetParent !== null).slice(0, 300).map(e => ({
        tag: e.tagName, text: (e.innerText || e.value || '').trim().slice(0, 60),
        aria: e.getAttribute('aria-label'), placeholder: e.getAttribute('placeholder'),
        role: e.getAttribute('role'), id: e.id, cls: (e.className || '').toString().slice(0, 60)}))""")


def probe():
    OUT.mkdir(exist_ok=True)
    cookies = leer_cookies(os.environ.get("FLOW_COOKIES", ""))
    print(f"cookies leídas: {len(cookies)} ({len([c for c in cookies if 'google' in c['domain']])} de google)")
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True, args=["--disable-blink-features=AutomationControlled"])
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="es-419",
                            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36")
        if cookies:
            ctx.add_cookies(cookies)
        page = ctx.new_page()
        log = []
        page.on("console", lambda m: log.append(f"{m.type}: {m.text}"[:300]))
        page.goto(URL, wait_until="domcontentloaded", timeout=90000)
        time.sleep(12)
        page.screenshot(path=str(OUT / "1_inicio.png"), full_page=False)
        info = {"url": page.url, "titulo": page.title(), "elementos": mapa(page)}
        texto = page.inner_text("body")[:4000]
        info["sesion"] = "no" if any(s in texto for s in ("Sign in", "Iniciar sesión", "Acceder")) and "accounts.google" in page.url else "probable"
        # si hay un botón para entrar a la herramienta o crear proyecto, probarlo y capturar
        for etiqueta in ("Create with Flow", "Crear con Flow", "New project", "Nuevo proyecto"):
            loc = page.get_by_text(etiqueta, exact=False)
            if loc.count():
                loc.first.click()
                time.sleep(10)
                page.screenshot(path=str(OUT / "2_despues_de_entrar.png"))
                info["despues"] = {"url": page.url, "elementos": mapa(page)}
                break
        (OUT / "mapa.json").write_text(json.dumps(info, ensure_ascii=False, indent=1))
        (OUT / "texto.txt").write_text(texto)
        (OUT / "consola.txt").write_text("\n".join(log[-200:]))
        print("url final:", page.url, "· sesión:", info["sesion"])
        b.close()


if __name__ == "__main__":
    {"probe": probe}[sys.argv[1]]()
