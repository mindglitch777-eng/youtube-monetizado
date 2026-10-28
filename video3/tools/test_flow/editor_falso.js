import {EditorState} from "prosemirror-state"; import {EditorView} from "prosemirror-view";
import {schema} from "prosemirror-schema-basic"; import {keymap} from "prosemirror-keymap"; import {baseKeymap} from "prosemirror-commands";
const host=document.querySelector("flow-rich-text-editor div[role=textbox]");
const btn=document.querySelector("flow-generate-icon-button button");
window.enviados=[];
function enviar(v){const t=v.state.doc.textContent.trim(); if(!t) return false; window.enviados.push(t);
  v.dispatch(v.state.tr.delete(0,v.state.doc.content.size)); btn.disabled=true;
  setTimeout(()=>{const c=document.createElement('canvas');c.width=c.height=600;c.getContext('2d').fillRect(0,0,600,600);c.toBlob(b=>{const i=document.createElement('img');i.src=URL.createObjectURL(b);document.getElementById('grid').append(i)})},1500); return true;}
const view=new EditorView(host,{state:EditorState.create({schema,plugins:[keymap({Enter:(s,d,v)=>enviar(v)}),keymap(baseKeymap)]}),
 dispatchTransaction(tr){const ns=view.state.apply(tr);view.updateState(ns);btn.disabled=!ns.doc.textContent.trim();}});
btn.addEventListener('click',()=>{ if(!btn.disabled) enviar(view); });
