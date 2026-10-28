// Copia mínima del chat de Flow para probar flow_pijama.user.js:
// editor ProseMirror real + botón "Iniciar generación" que se habilita con texto + botón stop mientras genera.
// window.MODO = "boton" (el botón manda) | "enter" (el botón no hace nada, solo Enter manda)
import {EditorState} from "prosemirror-state"; import {EditorView} from "prosemirror-view";
import {schema} from "prosemirror-schema-basic"; import {keymap} from "prosemirror-keymap"; import {baseKeymap} from "prosemirror-commands";
const host = document.querySelector("flow-rich-text-editor div[role=textbox]");
const btn = document.querySelector("flow-generate-icon-button button");
const stop = document.querySelector("flow-stop-icon-button");
window.enviados = [];
function enviar(v) {
  const t = v.state.doc.textContent.trim(); if (!t) return false;
  window.enviados.push(t);
  v.dispatch(v.state.tr.delete(0, v.state.doc.content.size));
  stop.style.display = "inline-block";
  setTimeout(() => {
    const c = document.createElement("canvas"); c.width = c.height = 600; c.getContext("2d").fillRect(0, 0, 600, 600);
    c.toBlob((b) => { const i = document.createElement("img"); i.src = URL.createObjectURL(b); document.getElementById("grid").append(i); stop.style.display = "none"; });
  }, 1500);
  return true;
}
const view = new EditorView(host, {
  state: EditorState.create({schema, plugins: [keymap({Enter: (s, d, v) => enviar(v)}), keymap(baseKeymap)]}),
  dispatchTransaction(tr) { const ns = view.state.apply(tr); view.updateState(ns); btn.disabled = !ns.doc.textContent.trim(); },
});
btn.addEventListener("click", () => { if (window.MODO !== "enter" && !btn.disabled) enviar(view); });
