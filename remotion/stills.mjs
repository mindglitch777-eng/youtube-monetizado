// Renderiza cuadros sueltos de una composición con un solo empaquetado: node stills.mjs <id> <carpeta> <frame> [<frame> ...]
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import path from 'node:path';
const [id, dir, ...frames] = process.argv.slice(2);
const B = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const composition = await selectComposition({serveUrl, id, browserExecutable: B});
for (const f of frames) {
  await renderStill({serveUrl, composition, frame: Number(f), output: path.join(dir, `f_${String(f).padStart(6, '0')}.jpg`), imageFormat: 'jpeg', browserExecutable: B});
}
console.log('listo', frames.length);
