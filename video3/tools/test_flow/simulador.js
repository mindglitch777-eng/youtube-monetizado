// Simulador del chat del agente de Google Flow para probar flow_pijama.user.js.
// Copia lo que se sabe del código real de Flow (flow-creative-agent-prompt-box > flow-base-prompt-box >
// flow-rich-text-editor con ProseMirror, flow-generate-icon-button "Iniciar generación",
// flow-stop-icon-button mientras genera) y lo que se ve en las capturas (respuesta del agente con
// miniaturas en el chat + las mismas imágenes grandes en la grilla).
// El escenario se elige con window.ESC (ver probar.js).
import {EditorState} from "prosemirror-state";
import {EditorView} from "prosemirror-view";
import {schema} from "prosemirror-schema-basic";
import {keymap} from "prosemirror-keymap";
import {baseKeymap} from "prosemirror-commands";

const ESC = Object.assign({lag: 0, botonMuerto: false, preguntas: 0, rechazo: false, rerender: false, demora: 1500, nImgs: 2, origen: "cross", previas: 0, refrescoTokens: false, soloHumano: false}, window.ESC || {});
window.enviados = [];
let preguntasQuedan = ESC.preguntas, contador = 0, view = null, generando = false;

function h(tag, attrs, ...hijos) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) e.setAttribute(k, v);
  hijos.forEach((c) => e.append(c));
  return e;
}
const chat = document.getElementById("chat");
const grid = document.getElementById("grid");
const pbox = document.getElementById("pbox");

function slot() { return document.querySelector(".submit-button-slot"); }
function pintarSlot() {
  const s = slot(); if (!s) return;
  s.replaceChildren();
  if (generando) {
    const b = h("button", {type: "button", class: "stop-icon-button stop-button", "aria-label": "Detener"}, h("mat-icon", {}, "stop"));
    s.append(h("flow-stop-icon-button", {}, b));
  } else {
    const b = h("button", {type: "submit", class: "generate-icon-button", "aria-label": "Iniciar generación"}, h("mat-icon", {}, "arrow_forward"));
    b.disabled = !(view && view.state.doc.textContent.trim());
    // como Flow real: con generación gratis, el submit ignora los eventos que no son de un dedo (isTrusted)
    b.addEventListener("click", (e) => { if (ESC.soloHumano && !e.isTrusted) return; if (!ESC.botonMuerto && !b.disabled) enviar(); });
    s.append(h("flow-generate-icon-button", {}, b));
  }
}

function montarCaja() {
  if (view) { view.destroy(); view = null; }
  pbox.replaceChildren();
  const tb = h("div", {role: "textbox", "aria-multiline": "true"});
  const caja = h("flow-creative-agent-prompt-box", {},
    h("flow-base-prompt-box", {},
      h("div", {class: "base-prompt-box"},
        h("flow-rich-text-editor", {class: "prompt-input"}, h("span", {class: "prosemirror-placeholder"}, "¿Qué quieres crear?"), h("div", {class: "prosemirror-editor"}, tb)),
        h("div", {class: "bottom-controls"},
          h("button", {type: "button", "aria-label": "Agregar"}, h("mat-icon", {}, "add")),
          h("div", {class: "submit-controls"}, h("button", {type: "button", class: "settings-trigger-button", "aria-label": "Botón de configuración"}, "⚙"), h("div", {class: "submit-button-slot"}))))));
  pbox.append(caja);
  view = new EditorView(tb, {
    state: EditorState.create({schema, plugins: [keymap(baseKeymap)]}),
    handleKeyDown(v, e) { if (e.key !== "Enter" || e.shiftKey) return false; if (!ESC.soloHumano || e.isTrusted) enviar(); return true; },
    dispatchTransaction(tr) {
      const ns = view.state.apply(tr); view.updateState(ns);
      // Angular actualiza el botón un rato después (change detection)
      setTimeout(pintarSlot, ESC.lag);
    },
  });
  pintarSlot();
}

function mensaje(quien, texto) { chat.append(h("div", {class: "msg " + quien}, texto)); chat.scrollTop = 1e9; }

function urlImg(id, tam) {
  const tok = ESC.refrescoTokens ? `?t=${Math.random().toString(36).slice(2)}` : "";
  if (ESC.origen === "same") return `https://flow.google.com/media/img${id}=s${tam}${tok}`;
  return `https://lh3.googleusercontent.com/fake/img${id}=s${tam}${tok}`;
}

function enviar() {
  if (generando || !view) return;
  const t = view.state.doc.textContent.trim(); if (!t) return;
  window.enviados.push(t);
  mensaje("yo", t.slice(0, 80) + "…");
  view.dispatch(view.state.tr.delete(0, view.state.doc.content.size));
  generando = true; pintarSlot();
  if (ESC.rerender) setTimeout(montarCaja, 200); // Angular vuelve a crear la caja después de enviar
  mensaje("agente", "Analyzing the Request");
  setTimeout(() => {
    if (preguntasQuedan > 0) { preguntasQuedan--; mensaje("agente", "Do you want it more realistic or more cartoon?"); }
    else if (ESC.rechazo) mensaje("agente", "I can't generate that image.");
    else {
      mensaje("agente", `I'll generate ${ESC.nImgs} images of the character using Nano Banana 2.1.`);
      const fila = h("div", {class: "thumbs"});
      chat.append(fila);
      for (let k = 0; k < ESC.nImgs; k++) {
        const id = ++contador;
        fila.append(h("img", {src: urlImg(id, 200), class: "thumb"}));         // miniatura del chat
        const g = h("img", {class: "tile"}); grid.prepend(g);                   // grande en la grilla, carga después
        setTimeout(() => { g.src = urlImg(id, 1024); }, 600 + k * 300);
      }
    }
    setTimeout(() => { generando = false; pintarSlot(); }, ESC.rechazo || preguntasQuedan >= 0 ? 1600 : 1600);
  }, ESC.demora);
}

montarCaja();
// imágenes que ya estaban en el proyecto antes de empezar (no se tienen que bajar)
for (let k = 0; k < ESC.previas; k++) { const id = 900 + k; grid.append(h("img", {class: "tile", src: urlImg(id, 1024), "data-id": id})); }
// Flow a veces vuelve a pedir las imágenes con otra firma: la misma imagen con otra URL
if (ESC.refrescoTokens) setInterval(() => document.querySelectorAll("#grid img[src]").forEach((i) => { i.src = i.src.replace(/\?t=[^&]*$/, "") + `?t=${Math.random().toString(36).slice(2)}`; }), 2000);
