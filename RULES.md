# Reglas obligatorias del canal — Knot

Estas reglas son no negociables. Ningún guion, imagen o video se produce 
o publica si rompe alguna de estas reglas. Si un paso del pipeline detecta 
que una regla no se cumple, debe detenerse y avisar en vez de continuar.

## Personaje
- El personaje fijo del canal es Knot, un búho de plumaje marrón cálido, 
  penachos en la cabeza, ojos grandes color ámbar.
- El ícono de Knot es fijo y no cambia de estado en ningún momento del 
  video — siempre el hilo rojo enredado, la misma imagen del principio 
  al final.
- Mismo estilo de ilustración en todos los videos, sin excepción.

## Estilo visual de las escenas humanas
- Las personas se muestran como siluetas simples, sin rasgos detallados.
- Paleta más fría en el Cuerpo y cálida en el Pago.
- Ambientación cotidiana y reconocible (living, cocina, dormitorio, auto, etc.).
- Encuadre cerrado en el Cuerpo y abierto en el Pago.
- Knot nunca aparece en estas escenas.

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
