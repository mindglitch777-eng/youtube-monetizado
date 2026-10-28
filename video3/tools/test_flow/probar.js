// Prueba flow_pijama.user.js contra el simulador de Flow (simulador.js) en Chromium y Firefox.
// Cada caso tiene condiciones que se tienen que cumplir; si alguna falla, sale con error.
//   node probar.js            (todos los casos, los dos navegadores)
//   SOLO=chromium node probar.js
const { chromium, firefox } = require("playwright");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const RAIZ = path.resolve(__dirname, "../../..");
const SCRIPT = fs.readFileSync(path.join(RAIZ, "video3/tools/flow_pijama.user.js"), "utf8");
const SIM = fs.readFileSync(path.join(__dirname, "simulador.bundle.js"), "utf8");

// PNG liso de w×h (las imágenes que "genera" el simulador)
function png(w, h) {
  const crc = (b) => { let c = ~0; for (const x of b) { c ^= x; for (let k = 0; k < 8; k++) c = (c >>> 1) ^ (0xedb88320 & -(c & 1)); } return ~c >>> 0; };
  const chunk = (t, d) => { const l = Buffer.alloc(4); l.writeUInt32BE(d.length); const td = Buffer.concat([Buffer.from(t), d]); const c = Buffer.alloc(4); c.writeUInt32BE(crc(td)); return Buffer.concat([l, td, c]); };
  const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4); ihdr[8] = 8; ihdr[9] = 2;
  const fila = Buffer.concat([Buffer.from([0]), Buffer.alloc(w * 3, 120)]);
  const raw = Buffer.concat(Array.from({ length: h }, () => fila));
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk("IHDR", ihdr), chunk("IDAT", zlib.deflateSync(raw)), chunk("IEND", Buffer.alloc(0))]);
}
const PNG_GRANDE = png(1024, 576), PNG_CHICA = png(200, 112);
const imgPara = (url) => (/=s200/.test(url) ? PNG_CHICA : PNG_GRANDE);

const LOTE = [{ archivo: "T0_prueba.txt", nombre: "prueba", formato: "16:9", refs: [], items: [1, 2, 3, 4].map((n) => ({ id: "P" + n,
  prompt: `Prompt de prueba numero ${n}: a cartoon man in light-blue pajamas with white stars standing in a medieval street at dawn.` })) }];

const HTML = `<!doctype html><html><head><meta charset="utf-8"><style>
body{margin:0;background:#000;color:#eee;font:14px sans-serif}
#top{display:flex;gap:8px;padding:8px}#top input{flex:1}
#main{display:flex;height:calc(100vh - 40px)}nav{width:170px}#grid{flex:1;display:flex;flex-wrap:wrap;gap:8px;align-content:flex-start;overflow:auto}
#grid img{width:300px}aside{width:300px;display:flex;flex-direction:column}#chat{flex:1;overflow:auto}#chat .thumb{width:110px}
</style></head><body>
<div id="top"><button aria-label="Inicio">⌂</button><input placeholder="Buscar" id="busca"><button aria-label="Filtros">≡</button></div>
<div id="main"><nav><button>Todos los elementos</button><button><mat-icon>add</mat-icon> Crear herramienta</button></nav>
<div id="grid"></div><aside><div>Sesión sin título</div><div id="chat"><p>Hola, ¿qué te gustaría crear?</p></div><div id="pbox"></div></aside></div>
</body></html>`;

const CASOS = [
  { nombre: "normal (2 imágenes por prompt, de otro dominio)", esc: {}, items: 3, espera: (r) => r.descargas === "P1_a P1_b P2_a P2_b P3_a P3_b" && r.enviados === 3 },
  { nombre: "el botón no responde, solo Enter", esc: { botonMuerto: true }, items: 2, espera: (r) => r.descargas === "P1_a P1_b P2_a P2_b" && /enviado con: Enter/.test(r.log) },
  { nombre: "Flow tarda 2,5 s en activar el botón", esc: { lag: 2500 }, items: 2, espera: (r) => r.descargas === "P1_a P1_b P2_a P2_b" },
  { nombre: "el agente pregunta en vez de generar", esc: { preguntas: 1 }, items: 1, espera: (r) => r.descargas === "P1_a P1_b" && r.enviados === 2 && /Generate the image now/.test(r.ultimoEnviado) },
  { nombre: "el agente se niega siempre (sigue con el siguiente)", esc: { rechazo: true }, items: 2, espera: (r) => r.descargas === "" && /0 bien, 2 con error/.test(r.log) && r.enviados === 4 },
  { nombre: "Flow vuelve a armar la caja después de cada envío", esc: { rerender: true }, items: 3, espera: (r) => r.descargas === "P1_a P1_b P2_a P2_b P3_a P3_b" },
  { nombre: "el panel tapa el botón de enviar", esc: {}, items: 2, panelEncima: true, espera: (r) => r.descargas === "P1_a P1_b P2_a P2_b" },
  { nombre: "una sola imagen, mismo dominio", esc: { nImgs: 1, origen: "same" }, items: 1, espera: (r) => r.descargas === "P1" },
  { nombre: "hay imágenes viejas y Flow les cambia la firma", esc: { previas: 3, refrescoTokens: true }, items: 2, espera: (r) => r.descargas === "P1_a P1_b P2_a P2_b" && r.todas === 4 },
  { nombre: "se recarga la página a mitad del lote y sigue", esc: {}, items: 4, reanudar: true, espera: (r) => r.descargas === "P1_a P1_b P2_a P2_b P3_a P3_b P4_a P4_b" },
];

async function caso(motor, c) {
  const b = await motor.launch();
  const ctx = await b.newContext({ viewport: { width: 980, height: 1600 }, acceptDownloads: true });
  const errores = [], descargas = [];
  await ctx.exposeBinding("__gmImg", (_s, url) => imgPara(url).toString("base64"));
  await ctx.route("https://flow.google.com/project/**", (r) => r.fulfill({ contentType: "text/html; charset=utf-8", headers: { "content-security-policy": "require-trusted-types-for 'script'" }, body: HTML }));
  // imágenes: lh3 SIN CORS (el fetch normal falla y el script tiene que usar GM_xmlhttpRequest); mismo dominio normal
  await ctx.route("https://lh3.googleusercontent.com/**", (r) => r.fulfill({ contentType: "image/png", body: imgPara(r.request().url()) }));
  await ctx.route("https://flow.google.com/media/**", (r) => r.fulfill({ contentType: "image/png", body: imgPara(r.request().url()) }));
  const lote = [{ ...LOTE[0], items: LOTE[0].items.slice(0, c.items) }];
  const cfgInicial = { lote: 0, desde: 1, pausa: 3, esperaMax: 60, abierto: true, tab: "log", ...(c.panelEncima ? { x: 980 - 300, y: 1600 - 120 } : {}) };
  const stubs = `
    const __ls = { get: (k) => { try { return JSON.parse(localStorage.getItem("gm_" + k)); } catch (_) { return undefined; } }, set: (k, v) => localStorage.setItem("gm_" + k, JSON.stringify(v)) };
    if (!localStorage.getItem("gm_fp_cfg")) __ls.set("fp_cfg", ${JSON.stringify(cfgInicial)});
    window.GM_getValue = (k) => __ls.get(k); window.GM_setValue = (k, v) => __ls.set(k, v); window.GM_registerMenuCommand = () => {};
    window.GM_xmlhttpRequest = (o) => {
      if (/lotes\\.json/.test(o.url)) return setTimeout(() => o.onload({ responseText: ${JSON.stringify(JSON.stringify(lote))} }), 10);
      window.__gmImg(o.url).then((b64) => { const bin = atob(b64), u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); o.onload({ response: new Blob([u], { type: "image/png" }) }); }, o.onerror);
    };`;
  await ctx.addInitScript({ content: `window.ESC=${JSON.stringify(c.esc)};window.addEventListener("DOMContentLoaded",()=>{${SIM}\n${stubs}\n${SCRIPT}\n});` });
  const pg = await ctx.newPage();
  pg.on("pageerror", (e) => errores.push(e.message));
  pg.on("download", (d) => descargas.push(d.suggestedFilename()));
  const leerLog = async () => { try { return await pg.locator("#flow-pijama-host .log").innerText({ timeout: 2000 }); } catch (_) { return ""; } };
  const esperarLog = async (re, ms) => { const t0 = Date.now(); while (Date.now() - t0 < ms) { const l = await leerLog(); if (re.test(l)) return l; await pg.waitForTimeout(500); } return await leerLog(); };
  const arrancar = async () => { await pg.locator("#flow-pijama-host").getByText("Generar", { exact: true }).click(); await pg.locator("#flow-pijama-host").getByText("▶ Generar lote").click(); await pg.locator("#flow-pijama-host").getByText("Registro").click(); };
  await pg.goto("https://flow.google.com/project/prueba");
  await pg.waitForTimeout(1200);
  await arrancar();
  let log;
  if (c.reanudar) {
    await esperarLog(/✓ P2/, 120000);
    await pg.reload(); await pg.waitForTimeout(1500);
    await arrancar();
  }
  log = await esperarLog(/lote terminado/, 60000 * c.items + 60000);
  await pg.waitForTimeout(800);
  const enviados = await pg.evaluate(() => window.enviados || []);
  // con items < 4 el lote sigue: se juntan solo las descargas de los planos pedidos
  const pedidos = new Set(LOTE[0].items.slice(0, c.items).map((i) => i.id));
  const nombres = descargas.map((f) => f.replace(/^v3_T0_/, "").replace(/\.\w+$/, ""));
  const r = {
    descargas: nombres.filter((n) => pedidos.has(n.split("_")[0])).join(" "),
    duplicadas: nombres.length !== new Set(nombres).size,
    todas: nombres.length,
    enviados: enviados.filter((e) => [...pedidos].some((id) => e.includes("numero " + id.slice(1) + ":"))).length,
    ultimoEnviado: enviados[enviados.length - 1] || "",
    log, errores,
  };
  await b.close();
  return r;
}

(async () => {
  const motores = [["Chromium", chromium], ["Firefox", firefox]].filter(([n]) => !process.env.SOLO || n.toLowerCase() === process.env.SOLO);
  let fallas = 0;
  for (const [n, m] of motores) {
    for (const c of CASOS) {
      if (process.env.CASO && !c.nombre.includes(process.env.CASO)) continue;
      let r;
      try { r = await caso(m, c); } catch (e) { r = { error: e.message.slice(0, 300), log: "" }; }
      const ok = !r.error && !r.duplicadas && !(r.errores || []).length && c.espera(r);
      if (!ok) fallas++;
      console.log(`${ok ? "✅" : "❌"} ${n} · ${c.nombre}`);
      if (!ok) console.log("   ", JSON.stringify({ ...r, log: (r.log || "").split("\n").slice(0, 14) }, null, 1).slice(0, 2500));
    }
  }
  console.log(fallas ? `\n${fallas} caso(s) fallaron` : "\nTodos los casos pasaron");
  process.exitCode = fallas ? 1 : 0;
})();
