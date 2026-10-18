# Video "Así morirías en la Edad de Piedra": estado de los archivos

Para la sesión de Claude Code que arme el video: la tarea completa está en `INSTRUCCION_CLAUDE_CODE.md`.

| Archivo | Estado |
|---|---|
| `INSTRUCCION_CLAUDE_CODE.md` | ✅ en la raíz |
| `imagenes/` | ✅ 109 imágenes (`img_001.jpg` … `img_109.jpg`), todas de 768x1376, sacadas de 6 zips (tandas 1 a 6). Los nombres son los originales de los zips, no los ids del manifest. |
| `guion_v3.md` | ❌ **FALTA**: no vino con los archivos subidos |
| `manifest_imagenes.json` | ❌ **FALTA**: no vino con los archivos subidos (según la instrucción tiene 112 entradas; hay 109 imágenes) |

Sin `guion_v3.md` y `manifest_imagenes.json` no se pueden emparejar las imágenes ni generar la voz: hay que subirlos a la raíz del repo antes de empezar.
