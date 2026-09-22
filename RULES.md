# Reglas obligatorias del canal — Knot

Estas reglas son no negociables. Ningún guion, imagen o video se produce 
o publica si rompe alguna de estas reglas. Si un paso del pipeline detecta 
que una regla no se cumple, debe detenerse y avisar en vez de continuar.

## Personaje
- El personaje fijo del canal es Knot, un búho de plumaje marrón cálido, 
  penachos en la cabeza, ojos grandes color ámbar.
- Knot sostiene siempre una bola de hilo roja y enredada como estado por 
  defecto (miniaturas, portada del canal, inicio y cuerpo de cada video).
- El hilo empieza completamente rojo y enredado en el bloque 1 de cada 
  video, y nunca se muestra resuelto en la miniatura ni al principio.
- En el Pago de los bloques 1 a 5, el hilo se afloja un poco más en cada 
  uno (menos enredado, pero se mantiene rojo) — es un indicador visual de 
  progreso a lo largo del video, nunca retrocede a un estado más enredado.
- Recién en el Pago del bloque 6 (el último), el hilo cambia de color a 
  verde agua/celeste, y así se mantiene en el CTA final.
- Mismo estilo de ilustración en todos los videos, sin excepción.

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
- La cara de Knot ocupa aproximadamente un tercio del cuadro.
- Texto en pantalla mínimo o inexistente.
- El título/miniatura nunca promete algo que el video no cumple.

## Sonido
- Se usan siempre los mismos 3-4 archivos de sonido de marca guardados en 
  /assets/sonido — nunca se generan sonidos nuevos por video.
- whoosh = transición de bloque | ding = confirmación de dato importante | 
  click = separador entre ejemplos | sting = cierre
- La energía del sonido siempre coincide con la energía de la imagen en ese momento.

## Producción
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
