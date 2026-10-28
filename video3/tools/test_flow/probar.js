const { chromium, firefox } = require('playwright');
const fs = require('fs');
async function probar(tipo, motor) {
  const b = await motor.launch(); const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } }); const pg = await ctx.newPage();
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  const bundle = fs.readFileSync('video3/tools/test_flow/editor.bundle.js', 'utf8');
  const html = `<html><body style="background:#000;color:#fff;font:14px sans-serif">
   <div style="display:flex;gap:8px;padding:8px"><input id=busca style="width:900px" placeholder="Buscar"></div>
   <nav><button><mat-icon class="google-symbols">add</mat-icon>Crear herramienta</button></nav><div id=grid></div>
   <aside style="position:fixed;right:0;bottom:0;width:320px"><flow-prompt-box><flow-base-prompt-box><div class="base-prompt-box">
     <flow-rich-text-editor class="prompt-input"><span class="prosemirror-placeholder">¿Qué quieres crear?</span><div class="prosemirror-editor"><div role="textbox" aria-multiline="true"></div></div></flow-rich-text-editor>
     <div class="bottom-controls"><button aria-label="Agregar"><mat-icon>add</mat-icon></button><div class="submit-controls"><button class="settings-trigger-button" aria-label="Botón de configuración">⚙</button>
     <flow-generate-icon-button><button type="submit" class="generate-icon-button" aria-label="Iniciar generación" disabled><mat-icon>arrow_forward</mat-icon></button></flow-generate-icon-button></div></div>
   </div></flow-base-prompt-box></flow-prompt-box></aside></body></html>`;
  await pg.route('https://flow.google.com/project/x', r => r.fulfill({ contentType: 'text/html; charset=utf-8', body: html }));
  const stubs = `window.GM_xmlhttpRequest=o=>setTimeout(()=>o.onload({responseText:${JSON.stringify(fs.readFileSync('video3/flow_lotes/lotes.json','utf8'))}}),10);let _v={};window.GM_setValue=(k,v)=>_v[k]=v;window.GM_getValue=k=>_v[k];window.GM_registerMenuCommand=()=>{};`;
  const src = fs.readFileSync('video3/tools/flow_pijama.user.js', 'utf8');
  await ctx.addInitScript({ content: "window.addEventListener('DOMContentLoaded',()=>{" + bundle + "\n" + stubs + "\n" + src + "\n});" });
  const descargas = []; pg.on('download', d => descargas.push(d.suggestedFilename()));
  await pg.goto('https://flow.google.com/project/x'); await pg.waitForTimeout(1000);
  await pg.locator('#flow-pijama-host').getByText('Probar 1').click();
  await pg.waitForTimeout(12000);
  const env = await pg.evaluate(() => window.enviados);
  await pg.locator('#flow-pijama-host').getByText('Registro').click(); await pg.waitForTimeout(200);
  const reg = await pg.locator('#flow-pijama-host .log').innerText();
  console.log(`== ${tipo}: enviado a Flow: ${env.length} (${(env[0]||'').slice(0,40)}…) | buscador: "${await pg.inputValue('#busca')}" | descargas: ${descargas} | errores: ${errs}`);
  console.log(reg.split('\n').slice(0,6).join('\n'));
  await b.close();
}
(async () => { for (const [n, m] of [['Chromium', chromium], ['Firefox', firefox]]) { try { await probar(n, m); } catch (e) { console.log(n, 'falló:', e.message.slice(0, 300)); process.exitCode = 1; } } })();
