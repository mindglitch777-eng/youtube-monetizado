// ==UserScript==
// @name         Flow Pijama · generador por lotes
// @namespace    explicado-en-pijamas
// @version      0.1.0
// @description  Genera en Google Flow los prompts del video 3 en orden, de a uno, y baja cada imagen con el número de su plano.
// @match        https://labs.google/*
// @grant        GM_xmlhttpRequest
// @grant        GM_setValue
// @grant        GM_getValue
// @connect      raw.githubusercontent.com
// @run-at       document-idle
// ==/UserScript==

(function () {
  "use strict";
  const LOTES_URL = "https://raw.githubusercontent.com/mindglitch777-eng/youtube-monetizado/ccr-7438d09b-3odr1g/video3/flow_lotes/lotes.json";
  const ESPERA_MAX = 180000; // 3 min por imagen como máximo
  let lotes = [], corriendo = false, parar = false;

  // ---------- panel ----------
  const css = `#fp{position:fixed;right:8px;bottom:8px;z-index:2147483647;width:min(340px,94vw);background:#16161c;color:#eee;
    font:13px/1.4 system-ui,sans-serif;border-radius:14px;box-shadow:0 6px 30px #0008;padding:10px;display:grid;gap:6px}
    #fp.min>*:not(.h){display:none}#fp .h{display:flex;justify-content:space-between;align-items:center;font-weight:700}
    #fp select,#fp button,#fp input{font:600 13px system-ui;border-radius:9px;border:0;padding:8px}
    #fp button{background:#c4472b;color:#fff}#fp button.s{background:#333}#fp .r{display:flex;gap:6px;flex-wrap:wrap}
    #fp #log{max-height:150px;overflow:auto;background:#0c0c10;border-radius:8px;padding:6px;white-space:pre-wrap;font:11px ui-monospace,monospace}`;
  const st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);
  const p = document.createElement("div"); p.id = "fp";
  p.innerHTML = `<div class="h"><span>🛌 Flow Pijama</span><button class="s" id="fpmin">–</button></div>
    <select id="fplote"><option>Cargando lotes…</option></select>
    <div class="r"><label>Desde #<input id="fpdesde" type="number" min="1" value="1" style="width:60px"></label>
      <label>Pausa s <input id="fppausa" type="number" min="3" value="8" style="width:56px"></label></div>
    <div class="r"><button id="fpuno">Probar 1</button><button id="fpgo">Generar lote</button><button class="s" id="fpstop">Parar</button></div>
    <div class="r"><button class="s" id="fpdiag">Diagnóstico (copiar)</button></div>
    <div id="log">Listo. Abrí un proyecto de Flow en modo imagen y elegí un lote.</div>`;
  document.body.appendChild(p);
  const $ = (id) => document.getElementById(id);
  const log = (t) => { const l = $("log"); l.textContent = t + "\n" + l.textContent.slice(0, 4000); };
  $("fpmin").onclick = () => p.classList.toggle("min");

  // ---------- lotes desde el repo ----------
  GM_xmlhttpRequest({
    method: "GET", url: LOTES_URL + "?t=" + Date.now(),
    onload: (r) => {
      try {
        lotes = JSON.parse(r.responseText);
        $("fplote").innerHTML = lotes.map((l, i) => `<option value="${i}">${l.archivo.slice(0, 2)} · ${l.nombre} (${l.items.length}) · ${l.formato}${l.refs.length ? " · ref: " + l.refs.join("+") : ""}</option>`).join("");
        const g = GM_getValue("fp_estado"); if (g) { $("fplote").value = g.lote; $("fpdesde").value = g.desde; }
        log(`Lotes cargados: ${lotes.length}`);
      } catch (e) { log("No pude leer los lotes: " + e); }
    },
    onerror: () => log("No pude bajar los lotes (sin internet?)"),
  });

  // ---------- piezas de Flow (heurísticas; el Diagnóstico sirve para ajustarlas) ----------
  const visible = (e) => e && e.offsetParent !== null;
  function cajaPrompt() {
    const c = [...document.querySelectorAll("textarea,[contenteditable=true],[role=textbox]")].filter(visible);
    return c.sort((a, b) => b.getBoundingClientRect().width - a.getBoundingClientRect().width)[0];
  }
  function escribir(el, texto) {
    el.focus();
    if (el.tagName === "TEXTAREA" || el.tagName === "INPUT") {
      const set = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(el), "value").set;
      set.call(el, texto);
      el.dispatchEvent(new Event("input", { bubbles: true }));
    } else {
      document.execCommand("selectAll", false, null);
      document.execCommand("insertText", false, texto);
    }
  }
  function botonCrear() {
    const bs = [...document.querySelectorAll("button,[role=button]")].filter(visible).filter((b) => !p.contains(b));
    const rx = /(create|crear|generar|generate|send|enviar|arrow_forward|submit)/i;
    return bs.find((b) => rx.test((b.getAttribute("aria-label") || "") + " " + (b.innerText || ""))) || null;
  }
  function imagenes() {
    return [...document.querySelectorAll("img")].filter((i) => !p.contains(i) && i.naturalWidth >= 256 && i.naturalHeight >= 256);
  }
  const dormir = (ms) => new Promise((r) => setTimeout(r, ms));

  async function bajar(src, nombre) {
    const b = await (await fetch(src, { credentials: "include" })).blob();
    const ext = (b.type.split("/")[1] || "png").replace("jpeg", "jpg");
    const a = document.createElement("a");
    a.href = URL.createObjectURL(b); a.download = `${nombre}.${ext}`;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 30000);
  }

  async function generarUno(item, nombre) {
    const caja = cajaPrompt();
    if (!caja) throw new Error("no encuentro la caja del prompt (tocá Diagnóstico)");
    const antes = new Set(imagenes().map((i) => i.currentSrc || i.src));
    escribir(caja, item.prompt);
    await dormir(800);
    const b = botonCrear();
    if (b && !b.disabled) b.click(); else { caja.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", code: "Enter", bubbles: true })); }
    const t0 = Date.now();
    while (Date.now() - t0 < ESPERA_MAX) {
      await dormir(2500);
      if (parar) throw new Error("parado");
      const nuevas = imagenes().filter((i) => !antes.has(i.currentSrc || i.src) && (i.currentSrc || i.src));
      if (nuevas.length) {
        await dormir(2500); // que terminen de cargar todas las variantes
        const todas = imagenes().filter((i) => !antes.has(i.currentSrc || i.src));
        for (let k = 0; k < todas.length; k++) await bajar(todas[k].currentSrc || todas[k].src, todas.length > 1 ? `${nombre}_${String.fromCharCode(97 + k)}` : nombre);
        return todas.length;
      }
    }
    throw new Error("se pasó el tiempo esperando la imagen");
  }

  async function correr(soloUno) {
    if (corriendo) return;
    const l = lotes[+$("fplote").value]; if (!l) return log("Elegí un lote.");
    corriendo = true; parar = false;
    let i = Math.max(1, +$("fpdesde").value) - 1;
    log(`▶ ${l.archivo}: adjuntá en Flow las referencias ${l.refs.join(", ") || "(ninguna)"} y formato ${l.formato}.`);
    try {
      for (; i < l.items.length; i++) {
        const it = l.items[i];
        const nombre = `v3_${l.archivo.slice(0, 2)}_${it.id}`;
        log(`(${i + 1}/${l.items.length}) ${it.id}…`);
        const n = await generarUno(it, nombre);
        log(`✓ ${it.id}: ${n} imagen(es) bajadas`);
        $("fpdesde").value = i + 2; GM_setValue("fp_estado", { lote: $("fplote").value, desde: i + 2 });
        if (soloUno) break;
        await dormir(Math.max(3, +$("fppausa").value) * 1000);
      }
      if (!soloUno) log(`🏁 Lote ${l.archivo} terminado.`);
    } catch (e) { log(`✗ ${e.message} · para seguir desde acá: #${i + 1}`); }
    corriendo = false;
  }
  $("fpuno").onclick = () => correr(true);
  $("fpgo").onclick = () => correr(false);
  $("fpstop").onclick = () => { parar = true; log("Parando después de la imagen actual…"); };

  // ---------- diagnóstico: mapa de la página para ajustar el script ----------
  $("fpdiag").onclick = async () => {
    const els = [...document.querySelectorAll("button,textarea,input,[role=button],[role=textbox],[contenteditable=true],[role=tab],[role=menuitem],img")]
      .filter((e) => visible(e) && !p.contains(e)).slice(0, 250).map((e) => {
        const r = e.getBoundingClientRect();
        return [e.tagName, (e.getAttribute("aria-label") || "").slice(0, 40), (e.innerText || e.placeholder || "").trim().slice(0, 40),
          e.getAttribute("type") || "", e.getAttribute("role") || "", Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height),
          e.tagName === "IMG" ? (e.src || "").slice(0, 40) : ""].join("|");
      });
    const txt = "FLOW-DIAG " + location.pathname + "\n" + els.join("\n").replace(/[\w.+-]+@[\w-]+\.[\w.]+/g, "<correo>");
    try { await navigator.clipboard.writeText(txt); log("Diagnóstico copiado: pegámelo en el chat."); }
    catch (e) { log(txt.slice(0, 3000)); }
  };
})();
