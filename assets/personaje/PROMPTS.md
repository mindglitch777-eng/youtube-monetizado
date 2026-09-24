# Prompts de las escenas humanas

Prompts fijos para generar las escenas de cada video con Cloudflare Workers AI 
(flux-1-schnell). Son el mismo texto que usa `scripts/generar_imagenes.py` y 
que exige RULES.md ("Estilo visual de las escenas humanas").

Knot no se genera nunca: aparece solo como ícono fijo (`knot-icono.png`), y 
nunca en estas escenas.

## Bloque de estilo (siempre, al principio del prompt)

> Flat vector-style illustration, minimalist character design, soft painterly 
> digital art, muted desaturated color palette, gentle color gradients, clean 
> simple linework. Human figures shown as simple silhouettes with featureless 
> or barely suggested faces — no detailed facial features. Editorial 
> illustration style, like a modern animated explainer video or picture book, 
> never photorealistic, never photographic.

## Variante "exagerada" (en prueba)

Se suma al final del bloque de estilo, no lo reemplaza. Se usa en los shorts 
que tienen `Estilo: exagerado` en el guion (primera prueba: 
`content/2026-XX-XX-5-manipulation-tactics`); después se evalúa si queda fija.

> …bold high-contrast accents, sharper shadow edges. Human figures shown as 
> simple silhouettes with exaggerated, dramatic body language — bigger 
> gestures, tenser posture, more dynamic poses than a neutral illustration.

## Variante de color y encuadre (según la sección)

| Sección | Variante |
|---|---|
| Hook y Gancho 2 (tono medio) | balanced medium tones, neither cool nor warm, medium framing |
| Cuerpo (frío y cerrado) | cool blue-gray tones, desaturated, tight and slightly claustrophobic framing, low ambient light, soft shadows |
| Pago (cálido y abierto) | warm amber and soft golden tones, gentle warm light, wide open framing with breathing space around the figures, calm and reassuring |

## Descripción de la escena

> Scene in an everyday, recognizable setting, one or two simple human 
> silhouettes whose posture and body language show this moment: "<texto 
> narrado de la sección>"

## Bloque negativo (no se envía con flux-1-schnell)

flux-1-schnell no acepta prompt negativo, y ponerlo dentro del prompt 
("Avoid: …") es contraproducente: el modelo no entiende negaciones y dibuja lo 
que se nombra (en las pruebas aparecieron búhos y una firma falsa). Queda 
documentado para usarlo si se cambia a un modelo que sí acepte prompt negativo:

> photorealistic, photograph, realistic skin texture, detailed facial features, 
> detailed eyes, extra limbs, extra fingers, deformed hands, blurry, text, 
> watermark, logo, signature, low quality, distorted anatomy, 3d render, CGI, 
> grainy, film grain, realistic lighting
