# Knot — Prompts del personaje

Referencia fija del personaje del canal. Usar estos prompts en Gemini
(app normal o API) para generar cualquier imagen nueva de Knot, siempre
partiendo de este mismo diseño para mantener consistencia.

## Prompt maestro — Knot completo (cuerpo entero)

<!-- PENDIENTE: el texto del prompt maestro no llegó en el mensaje; pegarlo acá. -->

## Cómo mantener consistencia en producción automática

Cuando el script llame a la API oficial de Gemini para generar las
escenas de cada video, pasarle knot-referencia.png junto con la
descripción de cada escena nueva, para que el modelo mantenga la misma
cara, plumaje y proporciones sin repetir la descripción completa cada vez.
