# Estrategia del canal — dos líneas en paralelo

Este archivo resume una decisión de dirección tomada por el usuario fuera
de este entorno (en una conversación con Claude en el chat de claude.ai) y
comunicada acá el 2026-09-29. Se guarda en la raíz del repo para no
perderla entre sesiones.

**Resumen en una línea**: no se abandona el canal cinematográfico
Knotwise — se SUMA una segunda línea de contenido, mucho más simple y
barata de producir, con el personaje "Kai", para llegar más rápido a los
umbrales de monetización de YouTube.

## Por qué

El video cinematográfico ("He Never Raised His Voice") tiene buena
calidad pero:
- Cuesta mucho tiempo de producción por pieza.
- Todavía no generó ningún dato real de audiencia (0 videos publicados
  con métricas).
- Los umbrales de monetización de YouTube son: 1.000 suscriptores + 4.000
  horas de watch time en 12 meses de long-form, O 10 millones de vistas
  de Shorts en 90 días.

Se evaluaron canales de TikTok con producción mínima (listicles simples,
un personaje ilustrado 2D fijo) que lograron hasta ~45.000 seguidores con
solo 9 videos. La conclusión: un formato mucho más simple, barato y
rápido de producir puede cruzar esos umbrales antes que seguir invirtiendo
solo en el formato cinematográfico.

## Línea 1 — Knotwise (sigue en pie, sin cambios)

- Canal en inglés, nicho de psicología de relaciones/manipulación.
- Personaje: Knot, búho marrón de ojos ámbar sosteniendo un ovillo de
  hilo rojo — ícono/marca de agua fijo, no narra ni actúa.
- Ya entregado: video largo cinematográfico "He Never Raised His Voice"
  (7:23, 1920x1080, historia dramatizada con Maya/Daniel, clips reales de
  Pexels, hilo rojo recurrente, subtítulos palabra por palabra) + 5 Shorts
  cortados de ese mismo video (uno por técnica), cada uno con tarjeta de
  cierre en pregunta sin responder + CTA al canal.
- Banner y foto de perfil ya diseñados (perfil: Knot en círculo; banner:
  negro con hilo rojo brillante + texto "YOU'VE BEEN MANIPULATED.").
- `RULES.md` (sección original, sin tocar) sigue vigente para este
  formato: duración libre hasta 180s en Shorts, densidad visual/sonora
  constante, paleta fría/cálida por sección, etc.

## Línea 2 — Kai (nueva, en paralelo)

- Personaje nuevo: "Kai" — humano simple, ilustración plana 2D, hoodie
  color mostaza fijo como distintivo. Separado de Knot, pensado para ser
  relatable (no un mascot animal).
- Formato de guion: listicle tipo "Top 5", SIEMPRE en cuenta regresiva
  (5→1), en segunda persona ("te pasó esto a vos").
- Imágenes: una por línea de guion, mostrando literalmente la escena que
  cuenta la voz (no solo la cara/emoción de Kai). Se generan A MANO por
  el usuario en Google Flow — no hay API integrada para esto todavía, así
  que el pipeline de esta línea NO genera imágenes solas: recibe los
  archivos ya generados y los ensambla con Edge-TTS + Remotion.
- Fórmula de retención de 13 puntos ya agregada a `RULES.md` como sección
  separada: "FÓRMULA DE RETENCIÓN — línea Kai / formato simple".
- Plan de monetización: los Shorts sueltos suman volumen para cruzar el
  umbral de 10M vistas/90 días; después se compilan varios en un video
  long-form del mismo material para mejor RPM.

## Pendiente de armar cuando se pida (todavía no existe)

- Estructura de carpetas para el contenido de Kai, separada de `content/`
  (que es de Knotwise). Propuesta: `content-kai/` — a confirmar con el
  usuario antes de crear la primera carpeta real.
- Scripts de ensamblado (voz + imágenes ya generadas + Remotion) para este
  formato — no reusar el pipeline de imágenes IA de Knotwise
  (`pack_imagenes.py` con Cloudflare) porque esta línea no genera
  imágenes por API.
- Composición Remotion nueva para el formato listicle (contador 1/5..5/5
  en pantalla, subtítulo palabra por palabra siempre activo, densidad
  visual con zoom/paneo sobre pocas imágenes reusadas) — separada de
  `LongForm`/`Short`/`Video` existentes, sin tocarlos (mismo criterio de
  N6 del PACK anterior: nunca modificar el trabajo de otro formato al
  construir uno nuevo).

## Herramientas evaluadas pero NO instaladas

- Leonardo.AI (API de generación con consistencia de personaje) —
  descartada por ahora a favor de Google Flow manual.
- OpusClip / Canva / Metricool (conectores para cortar shorts/publicar) —
  no conectados.
- Scrapling (servidor MCP de scraping, para investigar contenido de
  TikTok/YouTube sin gastar créditos de vidIQ) — instalación pedida por
  separado, ver el resultado en el mensaje de la tarea correspondiente o
  en el historial de este repo.

## Instrucción para las próximas sesiones

Cuando lleguen tareas mencionando "Kai", son de esta línea nueva,
separada del pipeline de Knotwise. No mezclar convenciones, carpetas ni
reglas de estilo entre las dos líneas.

## Scrapling — instalado 2026-09-29

Instalado en un venv aislado (`/opt/scrapling-venv`, no se tocó el Python
del sistema — el intento inicial con `pip install` a nivel sistema chocó
con un paquete PyJWT gestionado por Debian). Registrado como servidor MCP:

```
claude mcp add ScraplingServer -e PLAYWRIGHT_BROWSERS_PATH=/opt/scrapling-browsers -- /opt/scrapling-venv/bin/scrapling-mcp
```

`scrapling install` no pudo descargar Chromium/ffmpeg (mismo bloqueo de
red que Cloudflare/edge-tts/Pexels: cdn.playwright.dev y
playwright.download.prss.microsoft.com no están en la allowlist de este
entorno) — se resolvió sin descargar nada, apuntando
`PLAYWRIGHT_BROWSERS_PATH` a `/opt/scrapling-browsers`, una carpeta con
symlinks a los binarios de Chromium/ffmpeg que YA vienen preinstalados en
este entorno para Playwright (en `/opt/pw-browsers`), renombrados a la
revisión exacta que este Scrapling espera (1243). `install-deps` sí corrió
bien (paquetes del sistema vía apt).

**Prueba real hecha**: `Fetcher.get("https://pypi.org/project/scrapling/",
stealthy_headers=True)` → status 200, `.markdown()` devolvió el contenido
de la página convertido a Markdown limpio. Funciona.

**Limitación importante para el uso futuro**: la prueba contra un sitio
público arbitrario (example.com, en.wikipedia.org) fue RECHAZADA por la
política de red de este entorno de Claude Code (no es un bug de
Scrapling — hasta un `curl` directo a esos mismos sitios da el mismo
403). Solo funcionan los hosts que ya están en la allowlist de este
entorno (pypi.org, files.pythonhosted.org, GitHub, npm, etc.). Para
investigar TikTok/YouTube en la práctica, esta herramienta corriendo
DESDE ESTE ENTORNO va a chocar con la misma limitación que Cloudflare/
edge-tts/Pexels — probablemente haya que correrla desde otro lado (la
propia máquina del usuario, o un workflow de GitHub Actions) igual que se
resolvió para esos otros casos.
