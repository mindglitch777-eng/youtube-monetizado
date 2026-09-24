# Reglas obligatorias del canal — Knotwise

Estas reglas son no negociables. Ningún guion, imagen o video se produce 
o publica si rompe alguna de estas reglas. Si un paso del pipeline detecta 
que una regla no se cumple, debe detenerse y avisar en vez de continuar.

## Personaje
- El personaje fijo del canal es Knot, un búho de plumaje marrón cálido, 
  penachos en la cabeza, ojos grandes color ámbar.
- Knot es solo un ícono fijo de marca de agua: no se narra, no tiene 
  transiciones habladas y no aparece en las escenas humanas.
- El ícono de Knot es fijo y no cambia de estado en ningún momento del 
  video — siempre la misma imagen del principio al final: Knot sosteniendo 
  un ovillo de hilo rojo prolijo, bien enrollado y ordenado.
- Knot nunca se vuelve a generar; se usa siempre el archivo fijo 
  knot-icono.png.

## Estilo visual de las escenas humanas
- Mismo estilo de ilustración en todos los videos, sin excepción.
- Las personas se muestran como siluetas simples, sin rasgos detallados.
- Ambientación cotidiana y reconocible (living, cocina, dormitorio, auto, etc.).
- Knot nunca aparece en estas escenas.
- Toda escena se genera con este bloque de estilo:
  "Flat vector-style illustration, minimalist character design, soft 
  painterly digital art, muted desaturated color palette, gentle color 
  gradients, clean simple linework. Human figures shown as simple 
  silhouettes with featureless or barely suggested faces — no detailed 
  facial features. Editorial illustration style, like a modern animated 
  explainer video or picture book, never photorealistic, never photographic."
- Y con este bloque negativo (solo en modelos que aceptan prompt negativo; 
  con flux-1-schnell no se envía porque el modelo dibuja lo que se nombra):
  "photorealistic, photograph, realistic skin texture, detailed facial 
  features, detailed eyes, extra limbs, extra fingers, deformed hands, 
  blurry, text, watermark, logo, signature, low quality, distorted 
  anatomy, 3d render, CGI, grainy, film grain, realistic lighting"
- Variante de color y encuadre según la sección:
  - Hook y Gancho 2: tonos medios, ni fríos ni cálidos, encuadre medio.
  - Cuerpo: frío y cerrado — "cool blue-gray tones, desaturated, tight and 
    slightly claustrophobic framing, low ambient light, soft shadows".
  - Pago: cálido y abierto — tonos ámbar y dorados suaves, luz cálida, 
    encuadre amplio con aire alrededor de las figuras.
- Los prompts completos están en assets/personaje/PROMPTS.md.

## Guion
- El hook (0-3s) usa "you/your" y contradice una creencia común del espectador.
- Nunca se diagnostica al espectador ni se da consejo personalizado de 
  salud mental, finanzas o legal — todo en tono educativo/observacional.
- El cuerpo tiene exactamente 3 ejemplos concretos, nunca menos, nunca más.
- El cierre siempre termina en alivio o validación, nunca en tensión sin resolver.
- El CTA pide algo específico y de bajo esfuerzo (ej: "comment 'this is me'"), 
  nunca "like and subscribe" genérico.
- Nunca citar textualmente fuentes de investigación — siempre parafrasear.
- Nunca repetir el mismo tipo de gancho/título más de 2 videos seguidos.
- La palabra clave SEO objetivo del video se dice en voz alta dentro del 
  guion y va en las primeras 5 palabras del título.

## Miniatura y título
- El protagonismo visual de la miniatura es la escena humana del Hook. 
  Knot aparece solo como ícono fijo chico en una esquina (knot-icono.png).
- Texto en pantalla mínimo o inexistente.
- El título/miniatura nunca promete algo que el video no cumple.

## Sonido
- Se usan siempre los mismos 3-4 archivos de sonido de marca guardados en 
  /assets/sonido — nunca se generan sonidos nuevos por video.
- whoosh = transición de bloque | ding = confirmación de dato importante | 
  click = separador entre ejemplos | sting = cierre
- La energía del sonido siempre coincide con la energía de la imagen en ese momento.
- Archivos de marca: transicion.mp3 = whoosh | revelacion.mp3 = ding | 
  bloque.mp3 = click | cierre.mp3 = sting.
- Los sonidos de marca son gratuitos y con licencia comercial clara 
  (preferentemente Mixkit o Pixabay Audio). La fuente y la licencia de cada 
  archivo quedan anotadas en /assets/sonido.
- El ding suena en la palabra resaltada del subtítulo: en el guion se marca 
  con <!-- sonido: ding --> en la sección y la palabra en **negrita**.

## Subtítulos
- Franjas cortas, máximo 5-6 palabras en pantalla a la vez.
- Tipografía sans-serif gruesa, blanca con sombra/contorno oscuro.
- Una sola palabra por frase resaltada en amarillo con leve salto de tamaño, 
  en los puntos marcados <!-- sonido: ding --> del guion.
- Posición: tercio superior-medio de la pantalla.

## Shorts
- 1 short reciclado por cada bloque del video largo (6 por video).
- Duración menor a 60 segundos, formato vertical 9:16.
- Usa las mismas imágenes del bloque recortadas al centro: nunca se generan 
  imágenes nuevas para un short.
- Mismos subtítulos, sonidos de marca e ícono de Knot que el video largo.
- El CTA del video largo no va en los shorts; el short cierra con el sting.

## Producción
- Calendario: 2 videos largos por semana, más sus shorts reciclados 
  (1 por bloque de cada video).
- Ningún video se publica sin revisión humana completa antes de subir.
- Se puede generar contenido en lote (varios videos de una), pero la 
  publicación se espacia según el calendario, nunca se sube todo junto.
- Edge-TTS se usa solo en fase de prueba. Antes de publicar contenido real 
  y monetizado, la voz debe migrar a una opción con licencia comercial 
  (OpenAI TTS o ElevenLabs plan pago).

## Comunidad
- Los comentarios genuinos se responden al menos una vez por semana, con 
  el mismo tono cálido del guion.

## Seguridad y herramientas
- Ninguna API key se escribe directamente en el código. Todas van en 
  variables de entorno (.env), y .env siempre está en .gitignore.
