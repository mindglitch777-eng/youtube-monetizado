# Sonidos de marca — fuentes y licencias

Los 4 sonidos de marca vienen de [Mixkit](https://mixkit.co/free-sound-effects/)
y se usan bajo la **Mixkit Sound Effects Free License**, que permite el uso
comercial (incluido YouTube monetizado) sin atribución obligatoria.
Licencia: https://mixkit.co/license/#sfxFree

| Archivo | Uso | Sonido en Mixkit (ID) |
|---|---|---|
| transicion.mp3 | whoosh — transición de bloque | Fast small sweep transition (166) |
| revelacion.mp3 | ding — dato importante | Correct answer tone (2870) |
| bloque.mp3 | click — separador entre ejemplos | Positive interface click (1107) |
| cierre.mp3 | sting — cierre | Achievement bell (600) |

Los descarga el workflow `.github/workflows/descargar-sonidos.yml` a partir de
`fuentes.tsv`. Para cambiar un sonido: editar su ID y nombre en `fuentes.tsv`,
borrar el mp3 viejo y hacer push; el workflow baja el nuevo y lo commitea.

## Música de fondo

`assets/musica/fondo.mp3` es la pista 614 de Mixkit
(https://assets.mixkit.co/music/614/614.mp3, sacada de la página "mood: sad"),
bajo la **Mixkit Stock Music Free License**: uso gratuito en videos, incluido
YouTube. La baja el mismo workflow a partir de `assets/musica/fuente.txt`.
