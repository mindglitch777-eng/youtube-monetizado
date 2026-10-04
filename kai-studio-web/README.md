# Kai Studio Web

Sitio chico (HTML + funciones de Netlify) para cargar el guion y las
imágenes de un episodio de Kai directo al repo de GitHub, sin terminal y
sin pasar por Claude Code. El push que hacen las funciones dispara el
pipeline que ya existe (`.github/workflows/kai-studio-pipeline.yml`):
organiza las imágenes, genera la voz y renderiza el video final.

## Por qué existe

Un Artifact de Claude no puede hablar con la API de GitHub directamente
(la sandbox del navegador se lo bloquea). Un sitio hosteado en Netlify sí
puede — mete la llamada a GitHub en una función que corre del lado del
servidor, con el token guardado como variable de entorno, nunca expuesto
al navegador.

## Configuración (una sola vez)

### 1. Generar un token de GitHub

En GitHub → Settings → Developer settings → **Fine-grained personal access tokens** → Generate new token:
- **Resource owner**: tu usuario (`mindglitch777-eng`)
- **Repository access**: Only select repositories → `youtube-monetizado`
- **Permissions**:
  - Contents: **Read and write**
  - Actions: **Read-only** (para que la página pueda mostrar el estado del pipeline)
- Generá el token y copialo (no lo vas a volver a ver).

### 2. Crear el sitio en Netlify

1. [netlify.com](https://netlify.com) → **Add new site → Import an existing project** → GitHub → elegí `mindglitch777-eng/youtube-monetizado`.
2. En la configuración del sitio:
   - **Base directory**: `kai-studio-web`
   - **Build command**: dejalo como está (ya lo define `netlify.toml`)
   - **Publish directory**: `kai-studio-web` (o `.` si Netlify ya lo resuelve relativo a la base)
3. Antes de darle "Deploy", andá a **Site configuration → Environment variables** y agregá:
   - `GITHUB_TOKEN` = el token que generaste en el paso 1
   - `GITHUB_OWNER` = `mindglitch777-eng` (opcional, ya es el valor por defecto)
   - `GITHUB_REPO` = `youtube-monetizado` (opcional, ya es el valor por defecto)
   - `GITHUB_BRANCH` = la rama donde querés que escriba (por defecto `claude/knot-youtube-automation-17ild6`)
4. Deploy. Netlify te da una URL (`algo.netlify.app`) — esa es la página.

### 3. Listo

Cada vez que entrás a esa URL: pegás el guion (JSON) de cada idioma, soltás
las imágenes, apretás "Enviar y armar el video". La página hace los commits
directo al repo con tu token — el pipeline de GitHub Actions arranca solo.
"Ver estado" te dice en qué paso va (imágenes, voz, video final).

## Si todavía no tenés el guion en formato JSON

Pedíselo a Claude en el chat ("armame el script.json de este guion") — te
lo devuelve listo para pegar en los dos campos (EN y ES) de esta página.
El formato es el mismo que ya usan los episodios existentes en
`kai-studio/episodes/<slug>/<lang>/script.json`.

## Archivos

```
index.html                           la página (todo en un archivo, sin build)
netlify/functions/_github.js         helper compartido (API de GitHub)
netlify/functions/upload-image.js    sube UNA imagen a inbox/<slug>/
netlify/functions/submit-scripts.js  valida y sube los dos script.json
netlify/functions/status.js          estado (imágenes/voz/video) + último run del pipeline
```
