// ==UserScript==
// @name         Flow Pijama · generador por lotes
// @namespace    explicado-en-pijamas
// @version      0.3.0
// @description  Panel flotante para Google Flow: genera los prompts del video en orden, de a uno, y baja cada imagen con el número de su plano.
// @match        https://flow.google.com/*
// @grant        GM_xmlhttpRequest
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_registerMenuCommand
// @inject-into  content
// @connect      raw.githubusercontent.com
// @run-at       document-idle
// ==/UserScript==

(function () {
  "use strict";
  const LOTES_URL = "https://raw.githubusercontent.com/mindglitch777-eng/youtube-monetizado/ccr-7438d09b-3odr1g/video3/flow_lotes/lotes.json";

  // ---------- estado guardado ----------
  const cfg = Object.assign({
    x: null, y: null, abierto: true, tab: "gen", lote: 0, desde: 1, pausa: 8, esperaMax: 180,
    boton: null, caja: null, hechos: {},
  }, GM_getValue("fp_cfg") || {});
  const guardar = () => GM_setValue("fp_cfg", cfg);
  let lotes = [], corriendo = false, parar = false;

  // ---------- utilidades (sin innerHTML: Google exige Trusted Types) ----------
  function el(tag, props, ...hijos) {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(props || {})) {
      if (k === "class") e.className = v;
      else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
      else if (k === "style") e.style.cssText = v;
      else e.setAttribute(k, v);
    }
    hijos.flat().forEach((h) => h != null && e.append(h));
    return e;
  }
  const dormir = (ms) => new Promise((r) => setTimeout(r, ms));

  // ---------- panel en Shadow DOM (el CSS de Flow no lo toca) ----------
  const host = el("div", { id: "flow-pijama-host" });
  const sh = host.attachShadow({ mode: "open" });
  const css = el("style");
  css.textContent = `
  :host{all:initial}
  *{box-sizing:border-box;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
  .bub{position:fixed;width:58px;height:58px;border-radius:50%;display:grid;place-items:center;font-size:28px;cursor:grab;
    background:radial-gradient(circle at 30% 30%,#ff8a5c,#c4361b);box-shadow:0 8px 24px #0009,0 0 0 3px #ffffff22;touch-action:none;user-select:none;z-index:2147483647}
  .bub .dot{position:absolute;top:2px;right:2px;width:14px;height:14px;border-radius:50%;background:#2ecc71;border:2px solid #16161c;display:none}
  .bub.run .dot{display:block;animation:p 1s infinite}
  @keyframes p{50%{opacity:.3}}
  .pan{position:fixed;width:min(360px,94vw);max-height:78vh;display:flex;flex-direction:column;background:#15151b;color:#ececf1;
    border-radius:18px;box-shadow:0 18px 50px #000b,0 0 0 1px #ffffff14;overflow:hidden;z-index:2147483647}
  .hd{display:flex;align-items:center;gap:8px;padding:10px 12px;background:linear-gradient(135deg,#2a1a17,#1b1b24);cursor:grab;touch-action:none;user-select:none}
  .hd .t{font-weight:800;font-size:15px;flex:1}.hd .t small{display:block;font-weight:500;font-size:11px;color:#a9a9b8}
  .ib{width:34px;height:34px;border-radius:10px;border:0;background:#ffffff14;color:#fff;font-size:16px;cursor:pointer}
  .tabs{display:flex;gap:4px;padding:6px 8px;background:#1b1b22}
  .tab{flex:1;border:0;border-radius:10px;padding:8px 0;background:transparent;color:#a9a9b8;font-weight:700;font-size:13px;cursor:pointer}
  .tab.on{background:#ff6a3d22;color:#ff8a5c}
  .bd{padding:12px;overflow:auto;display:grid;gap:10px}
  .card{background:#1e1e27;border-radius:14px;padding:10px;display:grid;gap:8px}
  label.l{font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#8d8d9c}
  select,input{width:100%;font-size:14px;padding:10px;border-radius:10px;border:1px solid #33333f;background:#121218;color:#fff}
  .chips{display:flex;flex-wrap:wrap;gap:6px}
  .chip{font-size:12px;padding:4px 9px;border-radius:99px;background:#2a2a36;color:#d6d6e0}
  .chip.a{background:#ff6a3d;color:#1a0b06;font-weight:700}
  .bar{height:10px;border-radius:99px;background:#2a2a36;overflow:hidden}.bar i{display:block;height:100%;width:0;background:linear-gradient(90deg,#ff8a5c,#ffcf5c);transition:width .3s}
  .row{display:flex;gap:8px;align-items:center}
  .big{flex:1;border:0;border-radius:12px;padding:13px 10px;font-weight:800;font-size:15px;cursor:pointer;background:#ff6a3d;color:#1a0b06}
  .big.s{background:#2a2a36;color:#fff}.big.g{background:#2ecc71;color:#06210f}
  .stp{display:flex;align-items:center;gap:6px}.stp button{width:38px;height:38px;border-radius:10px;border:0;background:#2a2a36;color:#fff;font-size:18px}
  .stp input{text-align:center;width:70px}
  .now{font-size:12px;color:#c9c9d6;background:#121218;border-radius:10px;padding:8px;max-height:64px;overflow:hidden}
  .list{display:grid;gap:4px;max-height:190px;overflow:auto}
  .it{display:flex;gap:8px;align-items:center;font-size:12px;padding:6px 8px;border-radius:9px;background:#18181f;cursor:pointer;color:#cfcfda}
  .it .d{width:10px;height:10px;border-radius:50%;background:#44445a;flex:none}
  .it.ok .d{background:#2ecc71}.it.err .d{background:#ff4d4d}.it.cur{outline:2px solid #ff8a5c}
  .it span{overflow:hidden;white-space:nowrap;text-overflow:ellipsis}
  .log{font:11px/1.45 ui-monospace,Menlo,monospace;white-space:pre-wrap;background:#0e0e13;border-radius:10px;padding:8px;max-height:240px;overflow:auto;color:#b9b9c6}
  .toast{position:fixed;left:50%;top:14px;transform:translateX(-50%);background:#ececf1;color:#15151b;padding:10px 16px;border-radius:99px;font-weight:700;font-size:14px;z-index:2147483647;box-shadow:0 8px 24px #0008}
  .pick{position:fixed;left:0;right:0;bottom:0;background:#ff6a3d;color:#1a0b06;font-weight:800;text-align:center;padding:14px;z-index:2147483647}
  .hl{position:fixed;border:3px solid #ff6a3d;border-radius:10px;pointer-events:none;z-index:2147483646;box-shadow:0 0 0 9999px #0006}
  img.th{width:100%;border-radius:10px}`;
  sh.append(css);

  const bub = el("div", { class: "bub", title: "Flow Pijama" }, "🛌", el("div", { class: "dot" }));
  const pan = el("div", { class: "pan" });
  sh.append(bub, pan);

  // ---------- arrastrar (dedo o mouse), posición guardada ----------
  function posicionar() {
    const w = innerWidth, h = innerHeight;
    const x = cfg.x == null ? w - 16 - 58 : Math.min(Math.max(4, cfg.x), w - 62);
    const y = cfg.y == null ? h - 100 - 58 : Math.min(Math.max(4, cfg.y), h - 62);
    bub.style.left = x + "px"; bub.style.top = y + "px";
    const pw = Math.min(360, w * 0.94);
    pan.style.left = Math.min(Math.max(4, x + 58 - pw), w - pw - 4) + "px";
    // anclado al lado de la burbuja y con alto máximo hasta el borde: nunca se sale de la pantalla
    if (y > h / 2) { const b = Math.max(4, h - (y + 58)); pan.style.top = "auto"; pan.style.bottom = b + "px"; pan.style.maxHeight = (h - b - 8) + "px"; }
    else { const t = Math.max(4, y); pan.style.bottom = "auto"; pan.style.top = t + "px"; pan.style.maxHeight = (h - t - 8) + "px"; }
  }
  function arrastrable(asa, alTocar) {
    let ini = null;
    asa.addEventListener("pointerdown", (e) => {
      if (e.target.closest && e.target.closest("button,select,input")) return;
      ini = { px: e.clientX, py: e.clientY, x: parseFloat(bub.style.left), y: parseFloat(bub.style.top), mov: false };
      try { asa.setPointerCapture(e.pointerId); } catch (_) {}
    });
    asa.addEventListener("pointermove", (e) => {
      if (!ini) return;
      const dx = e.clientX - ini.px, dy = e.clientY - ini.py;
      if (Math.abs(dx) + Math.abs(dy) > 6) ini.mov = true;
      if (ini.mov) { cfg.x = ini.x + dx; cfg.y = ini.y + dy; posicionar(); }
    });
    const fin = () => {
      if (ini && !ini.mov && alTocar) alTocar();
      if (ini && ini.mov) guardar();
      ini = null;
    };
    asa.addEventListener("pointerup", fin);
    asa.addEventListener("pointercancel", () => { ini = null; });
  }
  arrastrable(bub, () => { cfg.abierto = true; guardar(); pintar(); });
  addEventListener("resize", posicionar);

  // ---------- avisos y registro ----------
  let tt;
  function toast(t) {
    sh.querySelectorAll(".toast").forEach((x) => x.remove());
    const d = el("div", { class: "toast" }, t); sh.append(d);
    clearTimeout(tt); tt = setTimeout(() => d.remove(), 2600);
  }
  const registro = [];
  function log(t) { registro.unshift(new Date().toLocaleTimeString() + "  " + t); registro.length = Math.min(registro.length, 200); if (cfg.tab === "log" && cfg.abierto) pintar(); }

  // ---------- piezas de Flow ----------
  const fuera = (e) => e && !host.contains(e) && e !== host;
  const visible = (e) => e && fuera(e) && e.getClientRects().length && getComputedStyle(e).visibility !== "hidden";
  function descriptor(e) {
    const r = e.getBoundingClientRect();
    return { tag: e.tagName, aria: e.getAttribute("aria-label"), texto: (e.innerText || "").trim().slice(0, 40),
      testid: e.getAttribute("data-testid"),
      icono: ((e.querySelector && e.querySelector("i,mat-icon,.material-icons,.material-symbols-outlined,.google-symbols")) || {}).textContent?.trim() || "",
      cx: (r.x + r.width / 2) / innerWidth, cy: (r.y + r.height / 2) / innerHeight };
  }
  function buscar(desc, selector) {
    if (!desc) return null;
    let mejor = null, pm = -1;
    for (const c of [...document.querySelectorAll(selector)].filter(visible)) {
      const d = descriptor(c);
      let s = 0;
      if (desc.testid && d.testid === desc.testid) s += 6;
      if (desc.aria && d.aria === desc.aria) s += 5;
      if (desc.icono && d.icono === desc.icono) s += 4;
      if (desc.texto && d.texto === desc.texto) s += 3;
      if (d.tag === desc.tag) s += 1;
      s += 2 - Math.min(2, Math.hypot(d.cx - desc.cx, d.cy - desc.cy) * 6);
      if (s > pm) { pm = s; mejor = c; }
    }
    return pm >= 3 ? mejor : null;
  }
  const SEL_CAJA = "textarea,[contenteditable=true],[contenteditable=''],[role=textbox],input[type=text]";
  function cajaPrompt() {
    const aprendida = buscar(cfg.caja, SEL_CAJA);
    if (aprendida) return aprendida;
    return [...document.querySelectorAll(SEL_CAJA)].filter(visible)
      .sort((a, b) => b.getBoundingClientRect().width - a.getBoundingClientRect().width)[0] || null;
  }
  function botonCrear(caja) {
    const sel = "button,[role=button]";
    const aprendido = buscar(cfg.boton, sel);
    if (aprendido) return aprendido;
    const bs = [...document.querySelectorAll(sel)].filter(visible);
    const rx = /(create|crear|generar|generate|send|enviar|arrow_forward|arrow_upward|submit)/i;
    const porNombre = bs.find((b) => rx.test([b.getAttribute("aria-label"), b.innerText, descriptor(b).icono].join(" ")));
    if (porNombre) return porNombre;
    if (!caja) return null;
    const rc = caja.getBoundingClientRect(); // si no: el botón más a la derecha pegado a la caja
    const cerca = bs.map((b) => [b, b.getBoundingClientRect()])
      .filter(([, r]) => r.left >= rc.left - 10 && r.top >= rc.top - 40 && r.top <= rc.bottom + 80)
      .sort((a, b) => (b[1].right - a[1].right) || (b[1].bottom - a[1].bottom));
    return cerca.length ? cerca[0][0] : null;
  }
  function escribir(e, texto) {
    e.focus();
    if (e.tagName === "TEXTAREA" || e.tagName === "INPUT") {
      const set = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(e), "value").set;
      set.call(e, texto);
      e.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertText", data: texto }));
      e.dispatchEvent(new Event("change", { bubbles: true }));
    } else {
      document.execCommand("selectAll", false, null);
      document.execCommand("insertText", false, texto);
      e.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertText", data: texto }));
    }
    e.dispatchEvent(new KeyboardEvent("keyup", { bubbles: true, key: " " }));
  }
  function tocar(b) {
    const r = b.getBoundingClientRect();
    const o = { bubbles: true, cancelable: true, clientX: r.x + r.width / 2, clientY: r.y + r.height / 2, pointerType: "touch", isPrimary: true };
    b.dispatchEvent(new PointerEvent("pointerdown", o)); b.dispatchEvent(new MouseEvent("mousedown", o));
    b.dispatchEvent(new PointerEvent("pointerup", o)); b.dispatchEvent(new MouseEvent("mouseup", o));
    b.click();
  }
  const srcDe = (i) => i.currentSrc || i.src;
  const imagenes = () => [...document.querySelectorAll("img")].filter((i) => fuera(i) && i.naturalWidth >= 256 && i.naturalHeight >= 256 && srcDe(i));

  function blobGM(src) {
    return new Promise((ok, mal) => GM_xmlhttpRequest({ method: "GET", url: src, responseType: "blob", onload: (r) => ok(r.response), onerror: mal }));
  }
  async function bajar(src, nombre) {
    let b;
    try { b = await (await fetch(src, { credentials: "include" })).blob(); }
    catch (e) { if (src.startsWith("http")) b = await blobGM(src); else throw e; }
    const ext = ((b.type || "image/png").split("/")[1] || "png").replace("jpeg", "jpg");
    const url = URL.createObjectURL(b);
    const a = el("a", { href: url, download: `${nombre}.${ext}` });
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 60000);
    return url;
  }

  // ---------- modo "enseñar": el usuario toca el botón o la caja de Flow ----------
  function ensenar(que) {
    cfg.abierto = false; pintar();
    const aviso = el("div", { class: "pick" }, que === "boton" ? "👉 Tocá el botón de CREAR / GENERAR de Flow" : "👉 Tocá la caja donde se escribe el prompt");
    const hl = el("div", { class: "hl" });
    sh.append(aviso, hl);
    const mover = (e) => {
      const t = e.target; if (!fuera(t)) return;
      const r = t.getBoundingClientRect();
      Object.assign(hl.style, { left: r.x - 4 + "px", top: r.y - 4 + "px", width: r.width + 8 + "px", height: r.height + 8 + "px" });
    };
    const elegir = (e) => {
      let t = e.target; if (!fuera(t)) return;
      e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation();
      t = que === "boton" ? (t.closest("button,[role=button]") || t) : (t.closest("textarea,[contenteditable],[role=textbox],input") || t);
      cfg[que] = descriptor(t); guardar();
      document.removeEventListener("pointerover", mover, true);
      document.removeEventListener("click", elegir, true);
      aviso.remove(); hl.remove();
      cfg.abierto = true; cfg.tab = "aj"; pintar();
      toast(que === "boton" ? "✅ Botón de crear aprendido" : "✅ Caja del prompt aprendida");
      log(`aprendí ${que}: ${JSON.stringify(cfg[que])}`);
    };
    document.addEventListener("pointerover", mover, true);
    document.addEventListener("click", elegir, true);
  }

  // ---------- generar ----------
  let ultimaImg = null;
  async function generarUno(item, nombre) {
    const caja = cajaPrompt();
    if (!caja) throw new Error("no encuentro la caja del prompt → Ajustes › Enseñar caja");
    const antes = new Set(imagenes().map(srcDe));
    escribir(caja, item.prompt);
    let b = null;
    for (let k = 0; k < 20; k++) { // esperar que Flow habilite el botón
      await dormir(250);
      b = botonCrear(caja);
      if (b && !b.disabled && b.getAttribute("aria-disabled") !== "true") break;
    }
    if (b) { tocar(b); log(`toqué: ${(b.getAttribute("aria-label") || b.innerText || descriptor(b).icono || b.tagName).slice(0, 30)}`); }
    else { caja.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", code: "Enter", keyCode: 13, bubbles: true })); log("sin botón: probé Enter"); }
    const t0 = Date.now();
    let avisado = false;
    while (Date.now() - t0 < cfg.esperaMax * 1000) {
      await dormir(2000);
      if (parar) throw new Error("pausado");
      if (!avisado && Date.now() - t0 > 25000 && ((caja.value || caja.innerText || "").length > 20)) {
        avisado = true; log("⚠ el prompt sigue en la caja: puede que no haya apretado crear → Ajustes › Enseñar botón");
      }
      if (imagenes().some((i) => !antes.has(srcDe(i)))) {
        await dormir(3000); // que terminen de cargar todas las variantes
        const todas = imagenes().filter((i) => !antes.has(srcDe(i)));
        for (let k = 0; k < todas.length; k++) ultimaImg = await bajar(srcDe(todas[k]), todas.length > 1 ? `${nombre}_${"abcd"[k] || k}` : nombre);
        return todas.length;
      }
    }
    throw new Error("no apareció ninguna imagen nueva a tiempo");
  }
  async function correr(soloUno) {
    if (corriendo) return;
    const l = lotes[cfg.lote]; if (!l) { toast("Elegí un lote"); return; }
    corriendo = true; parar = false; bub.classList.add("run"); pintar();
    log(`▶ lote ${l.archivo} desde #${cfg.desde}`);
    try {
      for (let i = cfg.desde - 1; i < l.items.length; i++) {
        cfg.desde = i + 1; guardar(); pintar();
        const it = l.items[i], clave = l.archivo + ":" + it.id;
        try {
          const n = await generarUno(it, `v3_${l.archivo.slice(0, 2)}_${it.id}`);
          cfg.hechos[clave] = "ok"; log(`✓ ${it.id} (${n} imagen/es)`);
        } catch (e) {
          if (e.message !== "pausado") { cfg.hechos[clave] = "err"; toast("✗ " + e.message); }
          guardar(); log(`✗ ${it.id}: ${e.message}`); throw e;
        }
        cfg.desde = i + 2; guardar(); pintar();
        if (soloUno) break;
        await dormir(cfg.pausa * 1000);
      }
      if (!soloUno && cfg.desde > l.items.length) { toast("🏁 Lote terminado"); log("🏁 lote terminado"); }
    } catch (e) { /* ya avisado */ }
    corriendo = false; bub.classList.remove("run"); pintar();
  }

  // ---------- diagnóstico ----------
  async function diagnostico() {
    const els = [...document.querySelectorAll("button,textarea,input,[role=button],[role=textbox],[contenteditable],[role=tab],[role=menuitem],img")]
      .filter(visible).slice(0, 250).map((e) => {
        const d = descriptor(e), r = e.getBoundingClientRect();
        return [e.tagName, d.aria || "", d.texto.replace(/\n/g, " "), d.icono, e.getAttribute("role") || "", e.disabled ? "disabled" : "",
          Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height), e.tagName === "IMG" ? srcDe(e).slice(0, 30) : ""].join("|");
      });
    const txt = `FLOW-DIAG v0.3 ${location.pathname}\nboton=${JSON.stringify(cfg.boton)}\ncaja=${JSON.stringify(cfg.caja)}\n` +
      els.join("\n").replace(/[\w.+-]+@[\w-]+\.[\w.]+/g, "<correo>") + "\n--- registro ---\n" + registro.slice(0, 40).join("\n");
    try { await navigator.clipboard.writeText(txt); toast("📋 Diagnóstico copiado: pegámelo en el chat"); }
    catch (e) { registro.unshift(txt); cfg.tab = "log"; pintar(); toast("Copialo desde el registro"); }
  }

  // ---------- dibujar el panel ----------
  function pintar() {
    bub.style.display = cfg.abierto ? "none" : "grid";
    pan.style.display = cfg.abierto ? "flex" : "none";
    if (!cfg.abierto) { posicionar(); return; }
    const l = lotes[cfg.lote];
    const hd = el("div", { class: "hd" },
      el("div", { class: "t" }, "🛌 Flow Pijama", el("small", {}, corriendo ? "Generando… podés seguir mirando Flow" : "Arrastrá esta barra para moverlo")),
      el("button", { class: "ib", title: "Minimizar", onclick: () => { cfg.abierto = false; guardar(); pintar(); } }, "—"));
    arrastrable(hd);
    const tab = (id, txt) => el("button", { class: "tab" + (cfg.tab === id ? " on" : ""), onclick: () => { cfg.tab = id; guardar(); pintar(); } }, txt);
    const tabs = el("div", { class: "tabs" }, tab("gen", "Generar"), tab("aj", "Ajustes"), tab("log", "Registro"));
    const bd = el("div", { class: "bd" });
    const set = (k, v) => { cfg[k] = v; guardar(); pintar(); };

    if (cfg.tab === "gen") {
      if (!l) bd.append(el("div", { class: "card" }, "Cargando lotes del repo…"));
      else {
        const sel = el("select", { onchange: (e) => { cfg.lote = +e.target.value; set("desde", 1); } },
          lotes.map((x, i) => { const o = el("option", { value: String(i) }, `${x.archivo.slice(0, 2)} · ${x.nombre.replace(/_/g, " ")} (${x.items.length})`); if (i === cfg.lote) o.selected = true; return o; }));
        const listos = l.items.filter((it) => cfg.hechos[l.archivo + ":" + it.id] === "ok").length;
        bd.append(el("div", { class: "card" },
          el("label", { class: "l" }, "Lote"), sel,
          el("div", { class: "chips" }, el("span", { class: "chip a" }, "Formato " + l.formato),
            l.refs.length ? l.refs.map((r) => el("span", { class: "chip" }, "📎 " + r)) : el("span", { class: "chip" }, "sin referencias")),
          el("div", { class: "row", style: "justify-content:space-between;font-size:12px;color:#a9a9b8" },
            el("span", {}, `${listos} de ${l.items.length} listas`), el("span", {}, `próxima: #${cfg.desde}`)),
          el("div", { class: "bar" }, el("i", { style: `width:${(100 * listos / l.items.length).toFixed(0)}%` }))));
        const it = l.items[cfg.desde - 1];
        if (it) bd.append(el("div", { class: "card" }, el("label", { class: "l" }, `Próximo · ${it.id}`), el("div", { class: "now" }, it.prompt.slice(0, 220) + "…")));
        const inp = el("input", { type: "number", min: "1", max: String(l.items.length), value: String(cfg.desde),
          onchange: (e) => set("desde", Math.min(Math.max(1, +e.target.value || 1), l.items.length)) });
        bd.append(el("div", { class: "card" },
          el("div", { class: "row" },
            el("div", { class: "stp" }, el("button", { onclick: () => set("desde", Math.max(1, cfg.desde - 1)) }, "−"), inp,
              el("button", { onclick: () => set("desde", Math.min(l.items.length, cfg.desde + 1)) }, "+")),
            el("span", { style: "font-size:12px;color:#a9a9b8" }, "empezar desde")),
          corriendo
            ? el("div", { class: "row" }, el("button", { class: "big s", onclick: () => { parar = true; toast("Pausa al terminar esta imagen"); } }, "⏸ Pausar"))
            : el("div", { class: "row" }, el("button", { class: "big s", onclick: () => correr(true) }, "Probar 1"), el("button", { class: "big", onclick: () => correr(false) }, "▶ Generar lote"))));
        bd.append(el("div", { class: "card" }, el("label", { class: "l" }, "Planos (tocá uno para empezar ahí)"),
          el("div", { class: "list" }, l.items.map((x, i) => {
            const est = cfg.hechos[l.archivo + ":" + x.id];
            return el("div", { class: "it" + (est ? " " + est : "") + (i === cfg.desde - 1 ? " cur" : ""), onclick: () => { if (!corriendo) set("desde", i + 1); } },
              el("div", { class: "d" }), el("b", {}, x.id), el("span", {}, x.prompt.slice(0, 60)));
          }))));
        if (ultimaImg) bd.append(el("div", { class: "card" }, el("label", { class: "l" }, "Última bajada"), el("img", { class: "th", src: ultimaImg })));
      }
    } else if (cfg.tab === "aj") {
      bd.append(el("div", { class: "card" },
        el("label", { class: "l" }, "Enseñarle Flow al script"),
        el("div", { style: "font-size:13px;color:#c9c9d6" }, "Si no aprieta crear o no escribe el prompt, enseñale una vez dónde están. Queda guardado."),
        el("button", { class: "big" + (cfg.boton ? " g" : ""), onclick: () => ensenar("boton") }, cfg.boton ? "✓ Botón crear (tocar para cambiar)" : "Enseñar botón crear"),
        el("button", { class: "big s" + (cfg.caja ? " g" : ""), onclick: () => ensenar("caja") }, cfg.caja ? "✓ Caja del prompt (tocar para cambiar)" : "Enseñar caja del prompt"),
        el("button", { class: "big s", onclick: () => { cfg.boton = null; cfg.caja = null; guardar(); pintar(); toast("Olvidado"); } }, "Olvidar lo aprendido")));
      const num = (k, min, txt) => el("div", { class: "row" }, el("span", { style: "flex:1;font-size:13px" }, txt),
        el("input", { type: "number", min: String(min), value: String(cfg[k]), style: "width:90px", onchange: (e) => { cfg[k] = Math.max(min, +e.target.value || min); guardar(); } }));
      bd.append(el("div", { class: "card" }, el("label", { class: "l" }, "Tiempos"), num("pausa", 3, "Pausa entre imágenes (s)"), num("esperaMax", 30, "Espera máxima por imagen (s)")));
      bd.append(el("div", { class: "card" }, el("label", { class: "l" }, "Progreso"),
        el("button", { class: "big s", onclick: () => { cfg.hechos = {}; set("desde", 1); toast("Marcas borradas"); } }, "Borrar marcas de hecho")));
    } else {
      bd.append(el("div", { class: "card" },
        el("button", { class: "big", onclick: diagnostico }, "📋 Copiar diagnóstico para Claude"),
        el("div", { class: "log" }, registro.join("\n") || "Sin actividad todavía.")));
    }
    pan.replaceChildren(hd, tabs, bd);
    posicionar();
  }

  // ---------- montar y mantener el panel ----------
  function montar() { if (document.body && !host.isConnected) document.body.appendChild(host); }
  montar(); pintar();
  setInterval(montar, 1500); // Flow redibuja la página al navegar: si saca el panel, vuelve
  try { GM_registerMenuCommand("Mostrar panel", () => { cfg.abierto = true; guardar(); montar(); pintar(); }); } catch (e) {}

  GM_xmlhttpRequest({
    method: "GET", url: LOTES_URL + "?t=" + Date.now(),
    onload: (r) => {
      try { lotes = JSON.parse(r.responseText); if (!lotes[cfg.lote]) cfg.lote = 0; log(`lotes cargados: ${lotes.length}`); pintar(); }
      catch (e) { log("no pude leer los lotes: " + e); toast("No pude leer los lotes"); }
    },
    onerror: () => { log("no pude bajar los lotes"); toast("Sin conexión al repo"); },
  });
})();
