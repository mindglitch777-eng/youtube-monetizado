# Kai Studio Web

Sitio chico (HTML + funciones serverless) para cargar el guion y las
imágenes de un episodio de Kai directo al repo de GitHub, sin terminal y
sin pasar por Claude Code. El push que hacen las funciones dispara el
pipeline que ya existe (`.github/workflows/kai-studio-pipeline.yml`):
organiza las imágenes, genera la voz y renderiza el video final.

Hosteado en **Cloudflare Pages** (antes estuvo en Netlify; se migró
porque la cuenta de Netlify se quedó sin créditos de build gratuitos y
dejó de desplegar cambios nuevos — Cloudflare Pages tiene un límite
gratuito mucho más generoso para un sitio de este tamaño).

## Por qué existe

Un Artifact de Claude no puede hablar con la API de GitHub directamente
(la sandbox del navegador se lo bloquea). Un sitio hosteado en Cloudflare
Pages sí puede — mete la llamada a GitHub en una función que corre del
lado del servidor (Cloudflare Pages Functions), con el token guardado
como variable de entorno, nunca expuesto al navegador.

## Configuración (una sola vez)

### 1. Generar un token de GitHub

En GitHub → Settings → Developer settings → **Fine-grained personal access tokens** → Generate new token:
- **Resource owner**: tu usuario (`mindglitch777-eng`)
- **Repository access**: Only select repositories → `youtube-monetizado`
- **Permissions**:
  - Contents: **Read and write**
  - Actions: **Read-only** (para que la página pueda mostrar el estado del pipeline)
- Generá el token y copialo (no lo vas a volver a ver).

### 2. Crear el proyecto en Cloudflare Pages

1. [dash.cloudflare.com](https://dash.cloudflare.com) → **Workers & Pages → Create → Pages → Connect to Git** → elegí `mindglitch777-eng/youtube-monetizado`.
2. En la configuración de build:
   - **Framework preset**: None
   - **Build command**: (vacío — no hay build, es HTML estático + funciones)
   - **Build output directory**: `/` (la raíz del proyecto, una vez que fijás el root de abajo)
   - **Root directory (advanced)**: `kai-studio-web`
3. Antes de deployar, en **Settings → Environment variables** agregá:
   - `GITHUB_TOKEN` = el token que generaste en el paso 1
   - `GITHUB_OWNER` = `mindglitch777-eng` (opcional, ya es el valor por defecto)
   - `GITHUB_REPO` = `youtube-monetizado` (opcional, ya es el valor por defecto)
   - `GITHUB_BRANCH` = la rama donde querés que escriba (por defecto `claude/knot-youtube-automation-17ild6`)
4. Deploy. Cloudflare te da una URL (`algo.pages.dev`) — esa es la página.

### 3. Listo

Cada vez que entrás a esa URL: pegás el guion (texto plano, una línea por
cosa que se dice), soltás las imágenes, apretás "Enviar y armar el
video". La página hace los commits directo al repo con tu token — el
pipeline de GitHub Actions arranca solo. "Ver estado" te dice en qué paso
va (imágenes, voz, video final).

## Archivos

```
index.html                          la página (todo en un archivo, sin build)
functions/_shared/github.js         helper compartido (API de GitHub)
functions/_shared/parse-guion.js    convierte el guion en texto plano a script.json
functions/_shared/json.js           helper chico para respuestas JSON
functions/api/upload-image.js       sube UNA imagen a inbox/<slug>/
functions/api/submit-scripts.js     valida y sube el script.json
functions/api/preview-script.js     convierte el guion sin escribir nada (vista previa)
functions/api/status.js             estado (imágenes/voz/video) + último run del pipeline
```

Los archivos dentro de `_shared/` no son rutas — Cloudflare Pages
Functions ignora cualquier carpeta/archivo que empiece con `_`, así que
sirven solo como helpers que importan los archivos de `api/`.
