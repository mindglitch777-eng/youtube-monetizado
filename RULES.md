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
- El ícono de Knot es opcional por video, no obligatorio en cada pieza — 
  por ejemplo, un short 100% de tipografía cinética/íconos SVG/clips reales 
  (sin escenas ilustradas) puede no llevarlo.

## Contenido visual
- Las imágenes generadas por IA dejan de ser la base por defecto del 
  contenido visual (reemplaza la regla vieja de "1 imagen IA cada 2s"). El 
  contenido visual se arma con: tipografía cinética, íconos simples 
  dibujados en SVG/Remotion, y 2-3 clips reales de Pexels por video para 
  momentos concretos/realistas (no para metáforas abstractas).
- Generar una imagen nueva con IA requiere justificación explícita antes de 
  hacerlo — ya no es el recurso por defecto. Si un componente de Remotion 
  necesita algo que no resuelven tipografía/íconos SVG/clips reales, parar 
  y explicar por qué antes de generarla.
- Personaje animado con rig propio en Remotion (silueta articulada con 
  huesos/joints para animar poses): descartado, no se usa.
- Si en algún momento se retoma ilustración de personaje animado: 2D gana 
  sobre 3D real (Three.js) — confirmado por prueba propia (Fase 0 del 
  sistema de animación): ~2x más rápido de renderizar y mejor legibilidad 
  de silueta plana, sin las sombras duras que genera la luz direccional 3D 
  real.
- Cuando SÍ se usan imágenes generadas por IA (ver bloque de estilo más 
  abajo), aplican las reglas de esta sección sin excepción.

## Estilo visual de las escenas humanas (cuando se generan imágenes IA)
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

### Estructura de engagement
- Hook amplio/universal: si el tema abarca varios tipos de vínculo (pareja, 
  amigo, familia), el hook los incluye a todos, no se acota a uno solo.
- Gancho de retención a mitad del hook: anticipa cuál va a ser el punto más 
  fuerte del video y pide guardarlo, antes de entregar el primer punto de 
  contenido real.
- Regla de tres rítmica en el punto más fuerte del guion: repetición triple 
  de una frase o palabra clave.
- En series de varias partes, un elemento de puzzle visual recurrente sin 
  resolver — se resuelve solo en la parte final (ver "Series de varias 
  partes").
- El CTA es de una sola palabra (ej: "comentá 'X'"), nunca pide un número u 
  otra acción de fricción alta — y va solo en la ÚLTIMA parte de una serie. 
  Las partes anteriores cierran en cliffhanger puro, sin CTA.
- Cierre abrupto, sin despedida, para favorecer el loop (excepto cuando el 
  cierre real es alivio/validación de un video de una sola parte — ver 
  regla de "Guion" más arriba).

## Series de varias partes
- Cuando el contenido no entra cómodo en una sola pieza bien ritmada, se 
  divide en partes independientes, cada una con su propio hook (no solo 
  "continuación de la parte anterior") y su propio cliffhanger real al 
  cierre.
- Se genera y revisa la primera parte antes de producir el resto de la 
  serie.

## Miniatura y título
- El protagonismo visual de la miniatura es la escena humana del Hook. 
  Knot aparece solo como ícono fijo chico en una esquina (knot-icono.png).
- Texto en pantalla mínimo o inexistente.
- El título/miniatura nunca promete algo que el video no cumple.
- Miniatura obligatoria en cada video: elemento numérico grande (si el 
  contenido lo tiene, ej. "5 tactics"), la escena/momento más impactante, 
  texto mínimo, alto contraste — tiene que destacar en un feed a tamaño 
  chico de celular.

## Sonido
- Los videos educativos/tono cálido del canal usan siempre los mismos 3-4 
  archivos de sonido de marca guardados en /assets/sonido — nunca se 
  generan sonidos nuevos por video para ese tono.
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
- Excepción — series de tono oscuro/tenso (ej. manipulación, red flags): 
  pueden sumar sonidos propios nuevos que no están en la librería de marca 
  (golpe/impacto en textos de impacto, drone/bajo de tensión de fondo a 
  volumen bajo y constante, sting distinto y más duro en cada cliffhanger 
  de cierre de serie), siempre de bancos libres/gratuitos con licencia 
  comercial clara (Mixkit, Pexels Audio u otro equivalente). El whoosh de 
  corte de escena/transición se mantiene el de marca (transicion.mp3).
- Crédito de assets de terceros: el autor de cada clip de video real usado 
  (ej. Pexels) se guarda en un archivo de créditos junto al video, aunque 
  la licencia no lo exija.

## Cámara y tono visual
- Cámara nunca estática — zoom/paneo constante + motion blur real 
  (@remotion/motion-blur, ver Fase 0 del sistema de animación), 
  intensificado automáticamente en los momentos de impacto marcados.
- Paleta de series de tono oscuro/tenso: negro puro (no gris) + acentos 
  neón saturados (rojo/azul/naranja) para la tensión; el cálido/abierto 
  (ver "Estilo visual de las escenas humanas") queda reservado para el 
  cierre de la serie, no se usa antes.

## Tipografía
- La tipografía es un elemento protagonista de la escena, nunca solo un 
  subtítulo pasivo. Mínimo 4 tratamientos distintos, todos con entrada 
  animada (resorte, blur, escala) — nunca texto estático:
  - Hook: agresivo/grande, la primera impresión del video.
  - Subtítulo narrativo palabra por palabra con resaltado: la capa base 
    permanente (ver "Subtítulos"), activa el 100% del tiempo sin excepción, 
    incluso sobre clips reales e íconos.
  - Revelación/giro: con blur y/o impacto de entrada, más grande que el 
    subtítulo base.
  - Banner fijo superior: lleva la tesis/estructura del video (ej. "Part 1 
    of 3"), tipografía distinta a la del subtítulo, se mantiene varias 
    líneas.

## Subtítulos
- Franjas cortas, máximo 5-6 palabras en pantalla a la vez.
- Tipografía sans-serif gruesa, blanca con sombra/contorno oscuro.
- Una sola palabra por frase resaltada en amarillo con leve salto de tamaño, 
  en los puntos marcados <!-- sonido: ding --> del guion.
- Posición: tercio superior-medio de la pantalla.
- Es la capa base permanente del video (ver "Tipografía"): activa el 100% 
  del tiempo sin excepción, incluso sobre clips reales e íconos SVG.

## Shorts
- 1 short reciclado por cada bloque del video largo (6 por video).
- Duración hasta 180 segundos (3 minutos) — el límite real de YouTube 
  Shorts desde oct. 2024, no 60 s (dato viejo, corregido). No hay 
  presupuesto de palabras fijo obligatorio: lo que sostiene la retención es 
  la densidad visual/sonora constante (subtítulo activo siempre, cambio 
  visual ~cada 2s, cámara nunca estática — ver "Cámara y tono visual"), no 
  la duración en sí. Un short dura lo que el contenido necesite hasta 180 s.
- Usa las mismas imágenes del bloque recortadas al centro: nunca se generan 
  imágenes nuevas para un short (ver "Contenido visual" para shorts 
  standalone sin imágenes IA).
- Mismos subtítulos, sonidos de marca e ícono de Knot que el video largo 
  (salvo excepción de tono oscuro/tenso, ver "Sonido", y el ícono de Knot 
  opcional, ver "Personaje").
- El CTA del video largo no va en los shorts; el short cierra con el sting 
  (o, en series de varias partes, con cliffhanger — ver "Series de varias 
  partes").
- En los shorts los subtítulos van en el tercio superior de la pantalla, lejos 
  del ícono de Knot.
- Si un short standalone pasa de 180 s, se divide en partes cortando en un 
  momento de suspenso.

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

## Restricciones
- Nunca usar logos ni marcas registradas de terceros en ningún elemento 
  gráfico.
- El ícono de Knot es opcional por video (ver "Personaje").
- Guardar el crédito del autor de cada clip de terceros usado (ej. Pexels), 
  en un archivo junto al video (ver "Sonido").
