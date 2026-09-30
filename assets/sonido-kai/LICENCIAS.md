# Sonidos Kai — fuentes y licencias

Todos vienen de [Mixkit](https://mixkit.co/free-sound-effects/) y
[Mixkit Music](https://mixkit.co/free-stock-music/), bajo la **Mixkit Sound
Effects Free License** / **Mixkit Stock Music Free License**: uso comercial
libre (incluido YouTube monetizado), sin atribución obligatoria.
Licencias: https://mixkit.co/license/#sfxFree y https://mixkit.co/license/#musicFree

Los descarga `.github/workflows/descargar-sonidos-kai.yml` (best-effort por
categoría/palabra clave — si Mixkit cambia sus páginas puede no encontrar
nada, sin romper el resto del workflow).

| Archivo | Uso (RULES.md, REGLA DE SONIDO) | Mixkit (ID) |
|---|---|---|
| sonido-kai/whoosh.mp3 | whoosh en cortes de gancho y cambios de contador | 1489 |
| sonido-kai/impacto-contador.mp3 | impacto corto en cada cambio de contador | 788 |
| sonido-kai/latido.mp3 | golpe grave/latido al inicio de cada gancho | 488 |
| sonido-kai/riser.mp3 | riser antes del zoom a la grilla (línea 4) | 1492 |
| sonido-kai/notificacion.mp3 | notificación/vibración cuando el celular es protagonista | 2870 |
| musica-kai/loop-oscuro.mp3 | música de fondo oscura en loop (-22dB, ducking -6dB con voz) | 188 |

Para cambiar alguno: borrar el mp3 viejo (y su línea en
`fuentes-encontradas.txt`), ajustar el patrón/categoría en el workflow si
hace falta, y hacer push — el workflow baja el nuevo y lo commitea.
