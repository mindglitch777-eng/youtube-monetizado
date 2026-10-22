# Fossil · «How Long You'd Last in Every Prehistoric Era» · análisis corte por corte

Video: https://www.youtube.com/watch?v=nAWpLtG-kNs · duración real 16:11 (971 s) · publicado 2026-08-10
Datos de la API de YouTube (14/10/2026): 11.490.282 vistas · 82.252 likes · 4.122 comentarios · canal de 37.800 subs creado el 01/03/2026 · factor outlier x63.5 (vistas ÷ mediana de sus últimos 10 videos).

## Cómo se hizo

- API de Gemini, plan gratis, sin facturación. Se le pasó el link de YouTube y Google mira el video de su lado; no se bajó nada.
- **17 trozos de 60 s** con `videoMetadata.startOffset/endOffset` (la API lo acepta: un trozo de prueba de 10 s gastó 947 tokens, contra los ~85.000 del video entero) a **2 cuadros por segundo** y resolución alta.
- Gemini tiene que dar los tiempos en segundos absolutos del video completo; el script marca cualquier tiempo fuera del tramo pedido.
- Modelo: gemini-3.8-flash en 13 de 13 trozos. Los trozos que primero hizo el modelo liviano (gemini-3.5-flash-lite) se repitieron con el principal, porque el liviano listaba un corte cada 1,0 s exacto: ese es el intervalo con que mira los cuadros, no cortes reales. Esos resultados viejos quedan guardados en el JSON bajo `lite` para comparar.
- **Trozos sin datos del modelo principal: 480-540, 660-720, 720-780, 960-971** (el modelo estuvo saturado; ver «Qué no se pudo obtener»).

## Control de desfase

La vez anterior los tiempos llegaron hasta 22:13 en un video de 16:11. Esta vez hice dos controles:

1. **Tiempos fuera del tramo:** ninguno en los 13 trozos. El último tiempo reportado es 16:00.0, dentro de los 16:11.
2. **Títulos de era contra los capítulos del creador** (referencia independiente, sacada de la descripción del video):

| Era | Capítulo del creador | Título visto por Gemini | Diferencia |
|---|---|---|---|
| Pre-Cambrian | 0:33.0 | 0:34.1 («Pre Cambrian 538 - 485 Million Years Ago») | +1.1 s |
| Cambrian | 1:03.0 | 1:03.8 («Cambrian») | +0.8 s |
| Ordovician | 2:37.0 | 2:37.0 («Ordovician») | +0.0 s |
| Silurian | 3:42.0 | 3:43.1 («Silurian») | +1.1 s |
| Devonian | 5:05.0 | 5:05.5 («Devonian») | +0.5 s |
| Carboniferous | 6:01.0 | 6:02.3 («Carboniferous») | +1.3 s |
| Permian | 7:18.0 | 7:20.0 («Permian») | +2.0 s |
| Early Triassic | 8:37.0 | 8:38.0 («Early Triassic [modelo liviano]») | +1.0 s |
| Mid-Late Triassic | 9:56.0 | 9:57.8 («Mid-Late Triassic») | +1.8 s |
| Jurassic | 10:42.0 | 10:43.5 («Jurassic») | +1.5 s |
| Cretaceous | 11:26.0 | 11:26.5 («Cretaceous [modelo liviano]») | +0.5 s |
| Paleogene | 12:28.0 | no detectado en ese tramo | — |
| Miocene | 13:31.0 | 13:32.5 («Miocene») | +1.5 s |
| Pliocene | 14:10.0 | 14:11.8 («Pliocene») | +1.8 s |
| Pleistocene | 14:50.0 | 14:51.8 («Pleistocene») | +1.8 s |

Los capítulos del creador están redondeados al segundo y Gemini mira 2 cuadros por segundo, así que diferencias de ±1,5 s son esperables. Una diferencia que crezca a lo largo del video indicaría desfase.

## 1. Cada corte entre 0:00 y 2:30

Corte = momento en que entra un plano nuevo. Duración = hasta el corte siguiente. Los límites de 1:00 y 2:00 son límites de trozo, no cortes reales: el plano que cruza ese límite aparece partido en dos filas.

| Corte | Duración | Tipo | Qué se ve | Cámara | Transición | Texto en pantalla | Efectos de sonido | Música | Qué se dice |
|---|---|---|---|---|---|---|---|---|---|
| 0:00.0 | 1.2 s | animación 3D | Hombre de espaldas transformándose en homínido. | fijo | fundido | — | no detectado | entra | Imagine for a second, you had a time machine |
| 0:01.2 | 1.6 s | animación 3D | Homínido caminando por la sabana de perfil. | paneo | corte seco | — | no detectado | sigue igual | — |
| 0:02.8 | 0.9 s | animación 3D | Mamut en ventisca de nieve. | fijo | corte seco | — | no detectado | sigue igual | and it got stuck during a random part |
| 0:03.7 | 1.5 s | animación 3D | Primer plano de cabeza de pterosaurio. | fijo | corte seco | — | no detectado | sigue igual | of Earth's history. |
| 0:05.2 | 1.4 s | animación 3D | Carnotauro corriendo por llanura desértica. | paneo | corte seco | — | no detectado | sigue igual | Which era |
| 0:06.6 | 1.3 s | animación 3D | Cefalópodo gigante submarino. | zoom in | corte seco | — | no detectado | sigue igual | would you have the best chance of surviving? |
| 0:07.9 | 1.2 s | animación 3D | Hombre primitivo sosteniendo una lanza. | fijo | corte seco | — | no detectado | sigue igual | — |
| 0:09.1 | 1.5 s | animación 3D | Homínido mirando al cielo en la pradera. | fijo | corte seco | — | no detectado | sigue igual | Would it be with the dinosaurs? |
| 0:10.6 | 1.2 s | animación 3D | Dinosaurio carnívoro atacando cerca de un río. | fijo | corte seco | — | no detectado | sigue igual | — |
| 0:11.8 | 1.2 s | animación 3D | Sinápsido bebiendo de un charco de agua. | fijo | corte seco | — | no detectado | sigue igual | What about walking next to eight foot millipedes? |
| 0:13.0 | 1.1 s | animación 3D | Arthropleura arrastrándose en el bosque. | fijo | corte seco | — | no detectado | sigue igual | — |
| 0:14.1 | 1.1 s | animación 3D | Dientes de sable saltando sobre un mamut en la nieve. | fijo | corte seco | — | no detectado | sigue igual | How about the Ice Age, |
| 0:15.2 | 1.3 s | animación 3D | Primer plano de un tigre dientes de sable. | fijo | corte seco | — | no detectado | sigue igual | living in a cave |
| 0:16.5 | 1.3 s | animación 3D | Oso gigante erguido rugiendo junto a lobos. | fijo | corte seco | — | no detectado | sigue igual | where everything around you is a killing machine? |
| 0:17.8 | 1.1 s | animación 3D | Oso persiguiendo a un carnívoro en el pasto. | paneo | corte seco | — | no detectado | sigue igual | — |
| 0:18.9 | 1.0 s | animación 3D | Manada de dinosaurios corriendo entre palmeras. | paneo | corte seco | — | no detectado | sigue igual | Or the bare lands |
| 0:19.9 | 1.1 s | animación 3D | Paraceratherium caminando por paisaje árido. | paneo | corte seco | — | no detectado | sigue igual | after the dinosaurs went extinct? |
| 0:21.0 | 1.0 s | animación 3D | Megaterio devorando una presa. | fijo | corte seco | — | no detectado | sigue igual | Is there any era a human could survive, |
| 0:22.0 | 1.1 s | animación 3D | Anomalocaris nadando bajo el agua. | paneo | corte seco | — | no detectado | sigue igual | — |
| 0:23.1 | 1.0 s | animación 3D | Hombre primitivo blandiendo una lanza. | fijo | corte seco | — | no detectado | sigue igual | just you, yourself, |
| 0:24.1 | 1.0 s | animación 3D | Reptil marino prehistórico nadando en caverna submarina. | fijo | corte seco | — | no detectado | sigue igual | no tools, no equipment, |
| 0:25.1 | 1.2 s | animación 3D | Arthropleura subiendo por tronco en pantano. | fijo | corte seco | — | no detectado | sigue igual | — |
| 0:26.3 | 0.9 s | animación 3D | Gorgonópsido revolcándose en el suelo. | fijo | corte seco | — | no detectado | sigue igual | making use of the land around you? |
| 0:27.2 | 0.9 s | animación 3D | Humano primitivo frente a una fogata. | fijo | corte seco | — | no detectado | sigue igual | — |
| 0:28.1 | 1.0 s | animación 3D | Humanos primitivos corriendo con palos. | fijo | corte seco | — | no detectado | sigue igual | Let's find out. |
| 0:29.1 | 1.2 s | animación 3D | Pterosaurio volando sobre selva y río. | paneo | corte seco | — | no detectado | sigue igual | — |
| 0:30.3 | 0.9 s | animación 3D | Tiranosaurio rugiendo al atardecer. | fijo | corte seco | — | no detectado | sigue igual | — |
| 0:31.2 | 1.0 s | animación 3D | Espinosaurio frente a dinosaurio con presa en la boca. | fijo | corte seco | — | no detectado | sigue igual | — |
| 0:32.2 | 1.1 s | animación 3D | Dicynodonte comiendo vegetación desértica. | fijo | corte seco | — | no detectado | sigue igual | — |
| 0:33.3 | 0.8 s | otro | Pantalla negra de transición. | fijo | fundido | — | no detectado | sigue igual | — |
| 0:34.1 | 2.5 s | texto | Título de la era Precámbrico sobre fondo oscuro. | zoom in | fundido | «Pre Cambrian» (0:34.1); «538 - 485 Million Years Ago» (0:34.1) | no detectado | sigue igual | — |
| 0:36.6 | 3.6 s | gráfico | Tier list vacía con categorías temporales de supervivencia. | fijo | corte seco | — | no detectado | sigue igual | Okay, so the first era is the Pre-Cambrian. Now there's technically |
| 0:40.2 | 2.9 s | gráfico | Diagrama en bloques de eras y eones geológicos. | paneo | corte seco | «Precambrian or Cryptozoic Eon» (0:40.2) | no detectado | sigue igual | a few eras in the Pre-Cambrian, but |
| 0:43.1 | 3.7 s | gráfico | Tier list vacía en pantalla. | fijo | corte seco | — | no detectado | sigue igual | you're toast in all of them. I'll put it simply for all these periods, |
| 0:46.8 | 5.1 s | ilustración | Paisaje volcánico con estromatolitos y luna gigante. | fijo | corte seco | — | no detectado | sigue igual | you just couldn't breathe in any of them, there was no oxygen. |
| 0:51.9 | 5.0 s | ilustración | Paisaje del eón Hádico con lava, humo y meteoritos. | fijo | corte seco | — | no detectado | sigue igual | The Hadean starts to molten, impacts keep resurfacing so you wouldn't have any ground to stand on. |
| 0:56.9 | 3.1 s | mapa | Mapa global de paleogeografía del Proterozoico tardío. | zoom in | corte seco | «Late Proterozoic 650 Ma» (0:56.9) | no detectado | sigue igual | The Proterozoic runs two billion years |
| 1:00.0 | 1.9 s | mapa | Mapa paleogeográfico del Proterozoico tardío. | fijo | corte seco | «Late Proterozoic 650 Ma» (1:00.0) | no detectado | sigue igual | and the planet freezes over twice. |
| 1:01.9 | 1.9 s | otro | Cursor arrastra la ficha Pre Cambrian a la fila Hours en la tier list. | fijo | corte seco | «Pre Cambrian» (1:01.9) | clic (1:02.9, en «You're cooked.») | sigue igual | You're cooked. |
| 1:03.8 | 3.5 s | texto | Título Cambrian sobre fondo marino difuminado. | fijo | corte seco | «Cambrian» (1:03.8); «538 - 485 Million Years Ago» (1:04.9) | no detectado | sigue igual | The Cambrian. Yeah, we're far, far back. |
| 1:07.3 | 4.1 s | mapa | Mapa paleogeográfico del Cámbrico tardío. | zoom in | corte seco | «Late Cambrian 514 Ma» (1:07.3) | no detectado | sigue igual | Before the continents even merged into Pangea. Okay, let's look around, |
| 1:11.4 | 6.4 s | ilustración | Paisaje árido y rocoso con meme Wojak serio superpuesto. | fijo | corte seco | — | no detectado | sigue igual | and yeah, that's a pretty big problem because there's nothing here. The Cambrian had nothing on Earth's surface. |
| 1:17.8 | 3.5 s | gráfico | Gráfico de líneas del contenido de oxígeno en la atmósfera terrestre. | fijo | corte seco | «Oxygen Content of Earth's Atmosphere» (1:17.8) | no detectado | sigue igual | It was about 5 to 10% oxygen, and breathing would be like |
| 1:21.3 | 2.4 s | video real | Alpinistas cruzando un glaciar nevado en el Everest. | paneo | corte seco | — | no detectado | sigue igual | breathing at the top of Mount Everest. |
| 1:23.7 | 5.2 s | texto | Pico montañoso que se difumina y aparece texto de temperatura. | zoom in | corte seco | «20 - 22 Degrees Celcius» (1:24.8) | no detectado | sigue igual | And you know what though, temperature's actually fine at around 20 to 22° Celsius. |
| 1:28.9 | 2.4 s | animación 3D | Fondo marino del Cámbrico con fauna bentónica primitiva. | fijo | corte seco | — | no detectado | sigue igual | And even more good news is you can drink the water. |
| 1:31.3 | 8.5 s | video real | Castor nadando en un río rodeado de bosque. | paneo | corte seco | — | no detectado | sigue igual | Because diseases that make water dangerous need a host animal shedding into the water. There's no animal, so you can drink the water. |
| 1:39.8 | 4.1 s | animación 3D | Homínido primitivo caminando en sabana soleada. | fijo | corte seco | — | no detectado | sigue igual | But of course you're gonna start to get hungry. Thankfully, nothing's gonna eat you, |
| 1:43.9 | 5.9 s | ilustración | Ecosistema marino cámbrico con anomalocáridos y trilobites. | fijo | corte seco | — | no detectado | sigue igual | because everything is in the water. But to find any sort of food, that's also where you need to go. |
| 1:49.8 | 7.9 s | animación 3D | Anomalocaris nadando en aguas profundas. | fijo | corte seco | — | no detectado | sigue igual | Luckily, the apex predator of this time, Anomalocaris, though a little scary looking, wouldn't harm you, and everything is just |
| 1:57.7 | 2.3 s | animación 3D | Criaturas marinas extrañas en el lecho marino. | fijo | corte seco | — | no detectado | sigue igual | everything's just so alien here. |
| 2:00.0 | 3.6 s | animación 3D | Fondo marino del Cámbrico con diversas criaturas marinas primitivas | paneo | corte seco | — | no detectado | sigue igual | If we want any chance of eating, we have to look in the tidal zone. |
| 2:03.6 | 5.3 s | animación 3D | Primer plano de un trilobite caminando sobre una roca submarina | fijo | corte seco | — | no detectado | sigue igual | And out of everything you could find here, you'd probably want to eat trilobites. |
| 2:08.9 | 5.2 s | ilustración | Ilustración artística detallada de un trilobite en el lecho marino | zoom in | corte seco | — | no detectado | sigue igual | They're arthropods, so they're structurally the same proposition as a crab, and they're abundant. But they're small, like only a few centimeters. |
| 2:14.1 | 5.0 s | video real | Mano sosteniendo una pequeña roca con un fósil de trilobite incrustado | fijo | corte seco | «*They Varied in size» (2:14.8) | no detectado | sigue igual | You could try and dive deeper and get something that's just completely alien. |
| 2:19.1 | 5.2 s | animación 3D | Recreación de una criatura con múltiples espinas (Hallucigenia) en el lecho marino | fijo | corte seco | — | no detectado | sigue igual | I don't even know how it would taste or what you would do with it. |
| 2:24.3 | 2.1 s | stickman | Figura de palo caminando con dificultad y agarrándose el pecho por falta de aire sobre suelo rocoso | fijo | corte seco | — | no detectado | sigue igual | But the hypoxia from the lack of oxygen... |
| 2:26.4 | 3.3 s | stickman | Figura de palo arrastrándose a gatas sobre las rocas | fijo | corte seco | — | no detectado | sigue igual | ...would have you so short of breath that it probably wouldn't even be possible. |
| 2:29.7 | 3.5 s | stickman | Figura de palo totalmente colapsada en el suelo boca abajo | fijo | corte seco | — | no detectado | sigue igual | It would ultimately be the thing that slowly takes you out. |

## 2. Muestreo de 3 bloques a lo largo del video

Elegí tres bloques de 60 s que contienen un cambio de era, para ver cómo se repite (o no) la estructura.

### 5:00.0–6:00.0 · Silúrico → Devónico (capítulo 5:05)

Modelo: gemini-3.8-flash

| Corte | Duración | Tipo | Qué se ve | Cámara | Transición | Texto en pantalla | Efectos de sonido | Música | Qué se dice |
|---|---|---|---|---|---|---|---|---|---|
| 5:00.0 | 1.2 s | animación 3D | escorpión marino nadando en el fondo del océano | fijo | corte seco | — | no detectado | sigue igual | be my guest. The water's clean, which is good, so |
| 5:01.2 | 3.6 s | gráfico | tier list con categorías de tiempo de supervivencia; se arrastra la casilla de Silurian a la fila Days | fijo | corte seco | «A year or more» (5:01.2); «Most of a year» (5:01.2); «Months» (5:01.2); «Weeks» (5:01.2); «Days» (5:01.2); «Hours» (5:01.2); «Ordovician» (5:01.2); «Silurian» (5:01.2); «Pre cambrian» (5:01.2); «Cambrian» (5:01.2) | no detectado | sigue igual | the Silurian would probably give you a few days. |
| 5:04.8 | 2.9 s | texto | pantalla negra que transiciona a fondo borroso con el título de Devonian | fijo | fundido | «Devonian» (5:05.5); «419 - 358 Million Years Ago» (5:06.9) | no detectado | sigue igual | The Devonian. |
| 5:07.7 | 3.5 s | mapa | globo terráqueo del Devónico temprano mostrando la distribución de las masas continentales | fijo | corte seco | «Early Devonian 390 Ma» (5:07.7) | no detectado | sigue igual | The Devonian map looks more of the same, but this is where the big bodies start showing up in the water. |
| 5:11.2 | 3.5 s | animación 3D | pez acorazado Dunkleosteus nadando hacia la cámara en aguas submarinas | zoom in | corte seco | — | no detectado | sigue igual | In good news, oxygen levels |
| 5:14.7 | 8.1 s | ilustración | paisaje terrestre primitivo con Prototaxites que luego se desenfoca para mostrar porcentajes de oxígeno | fijo | corte seco | «15 - 20%» (5:15.6); «21%» (5:19.6) | no detectado | sigue igual | are about 15 to 20%, so it's actually getting closer to modern levels, which are about 21%. So the air won't actually be the problem, |
| 5:22.8 | 1.7 s | ilustración | paisaje pantanoso devónico con vegetación primitiva y un volcán al fondo | fijo | fundido | — | no detectado | sigue igual | and temperature wouldn't be a problem either. |
| 5:24.5 | 5.3 s | ilustración | bosque primigenio devónico con árboles grandes y helechos | fijo | corte seco | — | no detectado | sigue igual | There's also trees now, like really big trees, so you could make fire. |
| 5:29.8 | 6.9 s | ilustración | varios Dunkleosteus y tiburones primitivos devónicos cazando amonites bajo el agua | fijo | corte seco | — | no detectado | sigue igual | Even though there are large predators in the ocean like Dunkleosteus, we don't have to worry about them because we're staying in fresh water. |
| 5:36.7 | 4.9 s | animación 3D | fondo marino con peces acorazados primitivos nadando entre anémonas y algas | paneo | corte seco | — | no detectado | sigue igual | The Devonian had lots of fish, so if you managed to catch a fish, you could cook it and eat it. |
| 5:41.6 | 5.1 s | animación 3D | euripterido Jaekelopterus sobre el lecho marino con grandes pinzas | fijo | corte seco | «Jaekelopterus» (5:44.4) | no detectado | sigue igual | What you may want to look out for, though, is the Jaekelopterus, 2 1/2 m, |
| 5:46.7 | 6.4 s | gráfico | diagrama comparativo de tamaño entre un humano de 2m y dos especies de Jaekelopterus | fijo | corte seco | «Jaekelopterus rhenaniae» (5:46.7); «Jaekelopterus howelli» (5:46.7); «2m» (5:46.7); «Jaekelopterus» (5:46.7) | no detectado | sigue igual | the largest arthropod that ever lived, and it's fresh water, which is exactly where you'd be fishing. |
| 5:53.1 | 6.9 s | gráfico | tier list; se arrastra la casilla de Devonian a la fila Weeks | fijo | corte seco | «A year or more» (5:53.1); «Most of a year» (5:53.1); «Months» (5:53.1); «Weeks» (5:53.1); «Days» (5:53.1); «Hours» (5:53.1); «Ordovician» (5:53.1); «Silurian» (5:53.1); «Devonian» (5:58.9) | no detectado | sigue igual | I'd probably say weeks, given it would be hard to catch the fish, and that would pretty much be the only thing worth eating. |

### 10:00.0–11:00.0 · Triásico medio-tardío → Jurásico (capítulo 10:42)

Modelo: gemini-3.8-flash

| Corte | Duración | Tipo | Qué se ve | Cámara | Transición | Texto en pantalla | Efectos de sonido | Música | Qué se dice |
|---|---|---|---|---|---|---|---|---|---|
| 10:00.0 | 1.3 s | texto | Título Mid-Late Triassic sobre fondo borroso | fijo | corte seco | «Mid-Late Triassic» (10:00.0); «247 - 201 Million Years Ago» (10:00.0) | no detectado | sigue igual | Later on in the Triassic, |
| 10:01.3 | 4.0 s | animación 3D | Reptil prehistórico junto a la orilla del agua con montañas al fondo | zoom in | corte seco | — | no detectado | sigue igual | the planet is cooled and we've recovered from that wasteland. |
| 10:05.3 | 4.3 s | ilustración | Paisaje con dinosaurios tempranos y cinodontes cerca de un río | zoom in | corte seco | — | no detectado | sigue igual | Oxygen is somewhere in the mid to high teens, which it's low, but it's manageable. |
| 10:09.6 | 6.6 s | ilustración | Paisaje vegetal triásico con coníferas y helechos junto a un arroyo | zoom in | corte seco | — | no detectado | sigue igual | We got conifers, ferns, cycads, seed ferns. But again, it's the same problem. |
| 10:16.2 | 5.7 s | animación 3D | Volcán humeante al fondo detrás de un lago y vegetación primitiva | zoom in | corte seco | — | no detectado | sigue igual | These would actually be worse to eat. So we're back to fish and small animals again. |
| 10:21.9 | 6.8 s | ilustración | Dinosaurios carnívoros tempranos cazando en un bosque pantanoso | zoom in | corte seco | — | no detectado | sigue igual | Dinosaurs actually showed up in this period, but they were later on and they were like the size of a coyote, so they're not going to be a problem. |
| 10:28.7 | 4.0 s | ilustración | Esquema comparativo de Postosuchus con un humano | zoom in | corte seco | «Postosuchus kirkpatricki» (10:29.0); «50 cm» (10:29.0) | no detectado | sigue igual | What will be a problem is Postosuchus, around 13 feet, |
| 10:32.7 | 6.0 s | ilustración | Postosuchus caminando en un paisaje árido con cícadas | zoom in | corte seco | — | no detectado | sigue igual | built like a land crocodile, but it's a reptile, a reptile that weighs around 600 lb. |
| 10:38.7 | 4.0 s | gráfico | Tier list donde se arrastra Mid-Late Triassic a la categoría Weeks | fijo | corte seco | «Mid-Late Triassic» (10:39.0) | clic o golpe seco al soltar el icono (10:40.8, en «Permian») | sigue igual | It's probably the same story as Devonian and Permian. |
| 10:42.7 | 5.6 s | texto | Fondo negro que pasa a título Jurassic con fechas | fijo | corte seco | «Jurassic» (10:43.5); «201 - 145 Million Years Ago» (10:44.4) | no detectado | sigue igual | The Jurassic. The Jurassic is where you're going to have to learn to run. |
| 10:48.3 | 4.3 s | mapa | Globo terráqueo del Jurásico Tardío (152 Ma) mostrando la separación de Pangea | zoom in | corte seco | «Late Jurassic 152 Ma» (10:48.3) | no detectado | sigue igual | Jurassic is in the middle of the three dinosaur periods and the continents are starting to drift apart. |
| 10:52.6 | 5.2 s | ilustración | Ecosistema jurásico repleto de dinosaurios carnívoros, herbívoros y aves primitivas | zoom in | corte seco | — | no detectado | sigue igual | The climate is stable and the oxygen is fine. But again, there were no berries |
| 10:57.8 | 2.2 s | ilustración | Saurópodo y terópodos caminando en un bosque de coníferas | zoom in | corte seco | — | no detectado | sigue igual | or anything, crops hadn't evolved yet |

### 14:00.0–15:00.0 · Plioceno → Pleistoceno (capítulo 14:50)

Modelo: gemini-3.8-flash

| Corte | Duración | Tipo | Qué se ve | Cámara | Transición | Texto en pantalla | Efectos de sonido | Música | Qué se dice |
|---|---|---|---|---|---|---|---|---|---|
| 14:00.0 | 4.2 s | ilustración | Ilustración de un depredador mamífero prehistórico persiguiendo a una presa junto a la orilla de un río. | fijo | corte seco | — | no detectado | sigue igual | around 1300 pounds. These are ambush hunters in an open country, and you'd be visible. |
| 14:04.2 | 2.0 s | animación 3D | Dos homínidos primitivos corriendo con palos bajo un cielo despejado. | fijo | corte seco | — | no detectado | sigue igual | It'd be rough, |
| 14:06.2 | 5.0 s | gráfico | Tabla de clasificación (tier list) donde el cursor arrastra el icono de 'Miocene' a la categoría 'Most of a year'. | fijo | fundido | «A year or more» (14:06.2); «Most of a year» (14:06.2); «Months» (14:06.2); «Weeks» (14:06.2); «Days» (14:06.2); «Hours» (14:06.2); «Miocene» (14:06.2) | no detectado | sigue igual | but you know what? You could probably make it most of a year. A-tier. |
| 14:11.2 | 5.6 s | texto | Pantalla de título con la palabra 'Pliocene' y fechas sobre un fondo borroso de fauna prehistórica. | fijo | fundido | «Pliocene» (14:11.8); «5 - 2.5 Million Years Ago» (14:12.8) | no detectado | sigue igual | The Pliocene. The Pliocene map looks the same, the climate is warm and stable, |
| 14:16.8 | 5.0 s | ilustración | Ilustración de la megafauna del Plioceno en un paisaje de sabana y bosque, incluyendo mastodontes, rinocerontes y ciervos. | fijo | corte seco | — | no detectado | sigue igual | the air is nothing to worry about. And what's growing is savanna and woodland mixed together, |
| 14:21.8 | 5.4 s | ilustración | Ilustración de un valle verde con camélidos prehistóricos, flores, mariposas, árboles y montañas al fondo. | fijo | corte seco | — | no detectado | sigue igual | open grass with patches of forest, which means you've got fruit trees, nuts in the woodland. |
| 14:27.2 | 4.0 s | animación 3D | Reconstrucción facial en 3D de un Australopithecus mirando de frente con la boca entreabierta sobre fondo negro. | fijo | corte seco | — | no detectado | sigue igual | Australopithecus was even walking around. |
| 14:31.2 | 6.6 s | ilustración | Pintura de un gran felino dientes de sable parado sobre el cadáver de una presa en un entorno boscoso. | fijo | corte seco | — | no detectado | sigue igual | There are predators: sabertooths, Megantereon, hyenas, which some people do think specialized in hunting early hominins. |
| 14:37.8 | 6.4 s | video real | Un hombre primitivo en la oscuridad sosteniendo una antorcha de fuego entre chispas. | fijo | corte seco | — | no detectado | sigue igual | So you're prey here. You would have to boil the water here and in the Miocene, but that's doable. |
| 14:44.2 | 6.6 s | gráfico | Tabla de clasificación donde el cursor arrastra el icono de 'Pliocene' hasta el nivel más alto, 'A year or more'. | fijo | fundido | «A year or more» (14:44.2); «Pliocene» (14:44.2) | no detectado | sigue igual | But you know what? We're actually at the pinnacle here. It's not going to get better than this. S-tier. |
| 14:50.8 | 5.7 s | texto | Pantalla de título con la palabra 'Pleistocene' y fechas sobre un fondo borroso de mamuts lanudos en la nieve. | fijo | fundido | «Pleistocene» (14:51.8); «2.5 MYA - 11,700 Years Ago» (14:52.8) | no detectado | sigue igual | Finally, the Pleistocene, also known as the Ice Age. |
| 14:56.5 | 3.5 s | ilustración | Grupo de humanos primitivos vestidos con pieles y portando lanzas caminando sobre un paisaje nevado con pinos y montañas. | fijo | corte seco | — | no detectado | sigue igual | This is going to be interesting, because we actually survived the Pleistocene. |

## 3. Resumen

- **Ojo:** las cifras de este resumen salen de 13 de 17 trozos (13 de 16 minutos aprox.); faltan 480-540, 660-720, 720-780, 960-971.
- **Planos analizados:** 207 en 13 trozos (incluye los planos partidos en los límites de trozo, que bajan un poco la duración media).
- **Duración media del plano en todo el video:** 3.8 s (mediana 3.6 s).
- **Gancho (0:00–0:33):** 28 cortes en los primeros 33 segundos, con planos de 1.1 s de promedio. Es un montaje rápido de criaturas (mamut, pterosaurio, cefalópodo, dientes de sable, oso gigante, T-rex) mientras la voz hace preguntas.
- **Resto del video (desde 0:33):** planos de 4.2 s de promedio (mediana 4.0 s). El ritmo baja a menos de la mitad que en el gancho.
- **Transiciones:** corte seco: 188, fundido: 19.
- **Tipos de plano:** animación 3D: 63, ilustración: 63, gráfico: 23, video real: 19, texto: 15, mapa: 9, stickman: 9, otro: 6.
- **Movimiento de cámara:** fijo: 126, zoom in: 63, paneo: 18.

### Cómo es el paso de una era a la siguiente

Secuencia de los 3 planos alrededor de cada título de era (el plano anterior, el título y el siguiente):

- **Pre-Cambrian:** 0:33.3 otro (Pantalla negra de transición.; entra con fundido) → 0:34.1 texto (Título de la era Precámbrico sobre fondo oscuro.; entra con fundido) → 0:36.6 gráfico (Tier list vacía con categorías temporales de supervivencia.; entra con corte seco)
- **Cambrian:** 1:01.9 otro (Cursor arrastra la ficha Pre Cambrian a la fila Hours en la ; entra con corte seco) → 1:03.8 texto (Título Cambrian sobre fondo marino difuminado.; entra con corte seco) → 1:07.3 mapa (Mapa paleogeográfico del Cámbrico tardío.; entra con corte seco)
- **Ordovician:** 2:33.2 gráfico (Tabla de clasificación (tier list) arrastrando la etiqueta '; entra con corte seco) → 2:37.0 texto (Pantalla de título de la era sobre fondo borroso de criatura; entra con corte seco) → 2:40.4 mapa (Mapa paleogeográfico ovalado del planeta Tierra durante el p; entra con corte seco)
- **Silurian:** 3:39.7 otro (Tabla clasificatoria donde el cursor coloca la tarjeta de 'O; entra con corte seco) → 3:43.1 texto (Fondo negro con el título 'Silurian' y el rango temporal '44; entra con corte seco) → 3:45.8 mapa (Mapa paleogeográfico global del Silúrico Medio (Middle Silur; entra con corte seco)
- **Devonian:** 5:01.2 gráfico (tier list con categorías de tiempo de supervivencia; se arra; entra con corte seco) → 5:04.8 texto (pantalla negra que transiciona a fondo borroso con el título; entra con fundido) → 5:07.7 mapa (globo terráqueo del Devónico temprano mostrando la distribuc; entra con corte seco)
- **Carboniferous:** 6:00.0 gráfico (Tier list en pantalla con los períodos ya clasificados, que ; entra con corte seco) → 6:02.3 texto (Título del período sobre fondo oscuro desenfocado con texto ; entra con fundido) → 6:06.0 ilustración (Bosque carbonífero pantanoso con una libélula gigante y un A; entra con corte seco)
- **Permian:** 7:17.5 otro (Pantalla en negro.; entra con fundido) → 7:20.0 texto (Título del período Pérmico y rango temporal.; entra con fundido) → 7:24.0 mapa (Planisferio que ilustra la formación de Pangea.; entra con corte seco)
- **Early Triassic (8:37.0):** título no detectado.
- **Mid-Late Triassic:** 9:57.3 otro (Pantalla negra de transición; entra con corte seco) → 9:57.8 texto (Título en letras blancas sobre fondo oscuro desenfocado anun; entra con corte seco) → 10:00.0 texto (Título Mid-Late Triassic sobre fondo borroso; entra con corte seco)
- **Jurassic:** 10:38.7 gráfico (Tier list donde se arrastra Mid-Late Triassic a la categoría; entra con corte seco) → 10:42.7 texto (Fondo negro que pasa a título Jurassic con fechas; entra con corte seco) → 10:48.3 mapa (Globo terráqueo del Jurásico Tardío (152 Ma) mostrando la se; entra con corte seco)
- **Cretaceous (11:26.0):** título no detectado.
- **Paleogene (12:28.0):** título no detectado.
- **Miocene:** 13:31.2 otro (Pantalla negra de transición; entra con fundido) → 13:32.4 texto (Título en letras blancas 'Miocene' sobre fondo borroso de fa; entra con fundido) → 13:37.3 ilustración (Ilustración de un ecosistema boscoso del Mioceno con calicot; entra con corte seco)
- **Pliocene:** 14:06.2 gráfico (Tabla de clasificación (tier list) donde el cursor arrastra ; entra con fundido) → 14:11.2 texto (Pantalla de título con la palabra 'Pliocene' y fechas sobre ; entra con fundido) → 14:16.8 ilustración (Ilustración de la megafauna del Plioceno en un paisaje de sa; entra con corte seco)
- **Pleistocene:** 14:44.2 gráfico (Tabla de clasificación donde el cursor arrastra el icono de ; entra con fundido) → 14:50.8 texto (Pantalla de título con la palabra 'Pleistocene' y fechas sob; entra con fundido) → 14:56.5 ilustración (Grupo de humanos primitivos vestidos con pieles y portando l; entra con corte seco)

### Dónde aparece el medidor de tier list

| Aparece | Hasta | Qué muestra |
|---|---|---|
| 0:36.6 | 0:40.2 | Tabla clasificatoria vacía con filas de tiempo: A year or more, Most of a year, Months, Weeks, Days, Hours. |
| 0:43.1 | 0:46.8 | Misma tabla clasificatoria vacía mostrada previamente. |
| 1:01.9 | 1:03.8 | Se clasifica la imagen de Pre Cambrian en la fila Hours. |
| 2:33.2 | 2:37.0 | Tabla clasificatoria de supervivencia dividida en filas (Weeks, Days, Hours). El cursor arrastra la imagen representativa de 'Cambrian' desde el banco inferior hasta colocarla en la fila 'Hours', junto a 'Pre Cambrian'. |
| 3:39.7 | 3:43.1 | Tabla clasificatoria por tiempo de supervivencia con niveles 'Months', 'Weeks', 'Days' y 'Hours'. Se arrastra la imagen de 'Ordovician' al nivel 'Days'. |
| 5:01.2 | 5:04.8 | Tier list con categorías de tiempo (A year or more, Most of a year, Months, Weeks, Days, Hours). Se coloca Silurian en la categoría Days junto a Ordovician. |
| 5:53.1 | 6:00.0 | Tier list con categorías de tiempo. Se arrastra la casilla de Devonian y se ubica en la categoría Weeks. |
| 6:00.0 | 6:01.5 | Tabla clasificatoria de períodos geológicos por tiempo de supervivencia humana, con filas desde 'A year or more' hasta 'Hours', mostrando los períodos anteriores ya ubicados. |
| 7:10.0 | 7:17.5 | El ícono de Carboniferous se arrastra a la fila Months. |
| 8:32.0 | 9:00.0 | Se coloca el Pérmico en la categoría de semanas y se muestra el Triásico dividido. [modelo liviano, menos confiable] |
| 9:50.3 | 9:57.3 | Tabla clasificatoria de tiempo de supervivencia con rangos de 'A year or more' a 'Hours'. El cursor arrastra 'Early Triassic' a la categoría 'Hours'. |
| 10:38.7 | 10:42.7 | Tabla de clasificación de supervivencia donde el icono Mid-Late Triassic se coloca en el nivel Weeks junto a Devonian y Permian. |
| 11:16.6 | 11:26.0 | Una tier list vacía donde se coloca la tarjeta de 'Jurassic' en la categoría de 'Weeks'. [modelo liviano, menos confiable] |
| 12:01.5 | 12:08.5 | Se coloca 'Cretaceous' en el nivel B. [modelo liviano, menos confiable] |
| 13:25.4 | 13:31.2 | Tier list con categorías de tiempo de supervivencia donde el cursor arrastra la etiqueta 'Paleogene' a la fila 'Months' |
| 14:06.2 | 14:11.2 | Tabla clasificatoria de eras geológicas por tiempo de supervivencia; el cursor coloca 'Miocene' en el nivel 'Most of a year'. |
| 14:44.2 | 14:50.8 | Tabla clasificatoria donde el cursor coloca 'Pliocene' en el nivel superior 'A year or more'. |
| 15:55.4 | 16:00.0 | Tabla clasificatoria de tiempo de supervivencia en diferentes periodos geológicos. El cursor arrastra la imagen de 'Pleistocene' desde la sección inferior hasta el rango 'Most of a year'. |
| 16:00.0 | 16:08.3 | Tier list con seis niveles: A year or more, Most of a year, Months, Weeks, Days y Hours, con varias eras posicionadas en cada uno [modelo liviano, menos confiable] |

**Ranking que se arma en la tier list** (según la lectura de Gemini de cada arrastre; los marcados vienen del modelo liviano):

| Era | Fila de la tier list |
|---|---|
| Pre-Cambrian | Hours |
| Cambrian | Hours |
| Ordovician | Days |
| Silurian | Days |
| Devonian | Weeks |
| Carboniferous | Months |
| Permian | Weeks [liviano] |
| Early Triassic | Hours |
| Mid-Late Triassic | Weeks |
| Jurassic | Weeks [liviano] |
| Cretaceous | no se pudo leer (el liviano dice «nivel B», que no existe en la tabla) |
| Paleogene | Months |
| Miocene | Most of a year |
| Pliocene | A year or more |
| Pleistocene | Most of a year |

Según la tabla, la mejor era para sobrevivir no es la de los humanos (Pleistoceno) sino el Plioceno, la única en «A year or more». Que eso funcione como remate sorpresa es mi lectura (opinión).

## 4. Por qué se volvió viral

**Medido (API de YouTube):** 11,5 millones de vistas en unos 2 meses, en un canal que tenía 7 meses y menos de 40.000 subs; 63,5 veces la mediana de sus otros videos. 82.252 likes y 4.122 comentarios.

**Lo que dice la audiencia** (los comentarios más votados, medido):

- 19626 likes: «Bruh I'd be cooked in the wild even today»
- 12637 likes: «Lowkey you overestimate the average person, most people don't even know how to start a fire or hunt.»
- 6033 likes: «You missed the part with "how long would I survive in Poland today" with my salary from 1999.»
- 4412 likes: «We'd probably just die from a disease our immune system cannot recognize.»
- 3499 likes: «I’d love a video game where you play as some kind of time traveler whose device malfunctions, sending you through these periods in history. Your main goal is to reach the next loca»
- 2933 likes: «"Yeah, just avoid them." they were everywhere.»

**Mi lectura de la estructura** (opinión basada en los datos de arriba):

1. **Una pregunta que cualquiera se hizo de chico** («¿en qué era sobrevivirías?»), en segunda persona y con viaje en el tiempo. No hace falta saber nada para engancharse.
2. **El gancho es un tráiler:** 28 cortes de criaturas espectaculares en 33 segundos, sin texto ni datos. Promete todo lo que viene.
3. **Un formato de juego que se completa:** la tier list aparece vacía al principio y se va llenando era por era con un arrastre y un clic. El espectador quiere ver el ranking final, y eso sostiene la retención hasta el último minuto.
4. **Estructura repetida y previsible:** en las 11 eras con título detectado que vienen después de la primera, la era anterior termina con su ficha arrastrada a la tier list (de 3 a 7 s). Después entra el título de la era nueva (en 6 casos con fundido a negro) y luego, en 6 de 12 casos, un mapa del planeta en esa época; en las eras más recientes, una ilustración del paisaje. En el medio: oxígeno, temperatura, comida y peligros. Según los capítulos, cada era dura entre 40 s y 1,5 minutos, así que siempre hay una «próxima era» cerca.
5. **Tono de amigo, no de documental:** frases como «you're toast» o «you're cooked», algún meme (Gemini vio un Wojak en 1:11) y stickmen sufriendo en 9 planos. Hace que la ciencia se sienta liviana.
6. **La música genera asombro:** el comentario más votado (1.724 likes) es sobre la música («sense of wonder… dinosaur books»).
7. **Datos concretos y comparables:** porcentaje de oxígeno, grados, tamaño de los bichos en pies. Los comentarios discuten esos números («10 FEET TALL?!», «Bear Dog»), y eso suma comentarios.

## 5. Qué no se pudo obtener o es poco confiable

- **Trozos sin análisis del modelo principal:** 480-540, 660-720, 720-780, 960-971. El modelo principal (gemini-3.8-flash) primero estuvo saturado (error 503) y después se agotó el cupo gratis del día (error 429, sin cobro). Para esos tramos solo uso los títulos de era y la tier list del modelo liviano, marcados «[modelo liviano]»; sus cortes no entran en las cifras. Se pueden completar mañana, cuando se reinicie el cupo (medianoche del Pacífico, 4:00 de Argentina).
- **Efectos de sonido:** Gemini detectó muy pocos (algún «clic» al soltar la ficha en la tier list). Que no los detecte no significa que no haya; el análisis de audio fino no es su punto fuerte. Donde dice «no detectado», no hay dato.
- **Música:** la mayoría de los planos dicen «sigue igual». Gemini no da niveles de volumen; no se pudo medir cuándo sube o baja con precisión. Para eso hace falta el audio y ffmpeg, y YouTube bloquea la descarga desde acá.
- **Segundo exacto del corte:** con 2 cuadros por segundo, cada corte tiene un margen de ±0,5 s. Los fundidos cortos pueden quedar sin detectar.
- **Textos en pantalla y narración:** son la lectura de Gemini, no subtítulos oficiales; puede haber diferencias menores de palabras. La narración está en inglés, tal cual se dice.
- **Límites de trozo:** el plano que cruza 1:00, 2:00, etc. aparece partido en dos filas. Eso agrega unos 16 planos falsos y baja levemente la duración media.

Datos crudos: `research/analisis_gemini/nAWpLtG-kNs_trozos.json`. Script: `research/gemini_cortes.py`.