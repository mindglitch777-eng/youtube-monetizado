#!/usr/bin/env python3
"""
Dirección visual v3 del video 3 (guion v2 de la IA de YouTube).

Arma docs/visual_v3.json (ingredientes + planos) y docs/prompts_v3.html
(página para el celular: copiar prompt, qué ingredientes adjuntar en Flow web,
intención de cada plano, marcar hechos).

Reglas de la v3 (ver docs/direccion_visual_v3.md):
- cada plano = una idea, lo que dice la voz en ese momento, legible en 0,5 s en un celular
- mezcla de puntos de vista: POV (primera persona, "tú"), tercera persona, sobre el hombro,
  macro, la cámara de la Pulga y planos generales
- continuidad con ingredientes con nombre en Flow web: personajes y lugares
- luz y color cuentan la emoción (guion de color por bloque)
- nada de sangre ni heridas: se sugiere con sombras, siluetas y sábanas blancas

  python3 video3/tools/visual_v3.py
"""
import json
from pathlib import Path

V = Path(__file__).resolve().parent.parent
DOCS = V / "docs"

ESTILO = ("Cinematic 2D animated film still. Bold cartoon characters with clean thick outlines and very expressive faces; "
          "painterly, detailed backgrounds with real depth; dramatic cinematic lighting (rim light, volumetric light rays, deep "
          "soft shadows); rich color grading; shallow depth of field; subtle film grain.")
FORMATO = ("16:9 horizontal. Main subject large and inside the central third, readable at phone size. Keep the top 15% of the "
           "frame calm (game HUD goes there). No text, letters, numbers, logos or watermarks anywhere.")
FORMATO_V = ("9:16 vertical. Main subject large in the center, readable at phone size. Keep the top 20% calm for titles. "
             "No text, letters, numbers, logos or watermarks anywhere.")
NOGORE = "No blood, no wounds, no visible corpses."

# Ingredientes con nombre: se generan primero y se suben a Flow con ESTE nombre exacto
ING = [
    ("PIJAMA", "personaje", "Character turnaround of PIJAMA on a plain light-gray background: a modern man around 30, round head, messy brown hair, big expressive eyes, light-blue pajamas with small white stars, barefoot. Front, three-quarter, side and back views, neutral pose, full body. Same style as the film: bold clean outlines, cinematic soft light."),
    ("PIJAMA_CARAS", "personaje", "Expression sheet of PIJAMA (same man, light-blue pajamas with white stars) on a plain light-gray background: six head-and-shoulders expressions in a grid: terror, disgust, relief, exhausted fever, sly smile, triumphant shout."),
    ("DESPERTADOR", "personaje", "Character turnaround of DESPERTADOR on a plain light-gray background: a chunky retro twin-bell alarm clock worn on a wrist strap, round glowing screen face with big expressive cartoon eyes, tiny arms, sarcastic attitude. Front, side, laughing, worried."),
    ("PULGA", "personaje", "Character sheet of PULGA on a plain light-gray background, drawn large: a cartoon flea villain, dark brown glossy armored body, long spring legs, tiny wicked grin with little fangs, red glinting eyes. Four poses: grin, mid-jump, rubbing hands, laughing."),
    ("MEDICO", "personaje", "Character turnaround of MEDICO on a plain light-gray background: a skinny 1348 Florentine physician, long dirty dark-red robe, round red cap, big crooked nose, stubble, holding a small glass flask and a rusty little knife; shifty eyes. NO bird mask. Front, side, lecturing, grinning."),
    ("NENA", "personaje", "Character sheet of NENA on a plain light-gray background: a thin 8-year-old girl from 1348 Florence, brown braid, patched beige dress, barefoot, huge sad eyes. Front, side, knocking, crying softly."),
    ("ESTABLO", "lugar", "Empty location plate, no characters: a small medieval stable in Florence, 1348, at night. Wooden stalls, hay piles, one tired brown horse, a hanging lantern, broken plank door, moonlight through gaps."),
    ("CALLE", "lugar", "Empty location plate, no characters: a narrow residential street in Florence, 1348. Tall ochre and terracotta stone houses, dark green wooden shutters, laundry lines, wet cobblestones, a bell tower at the end of the street."),
    ("PLAZA", "lugar", "Empty location plate, no characters: a Florentine piazza in 1348 with a stone fountain, a church facade, market stalls with awnings, the unfinished cathedral with scaffolding and NO dome in the background."),
    ("CONSULTORIO", "lugar", "Empty location plate, no characters: a cramped medieval physician's room in 1348 Florence. Shelves of murky glass flasks, dried herbs hanging from beams, a planet chart painted on the wall, a filthy wooden table, a stool, candles."),
    ("VILLA", "lugar", "Empty location plate, no characters: a Tuscan hill villa in 1348. Stone arches, a garden with roses and lemon trees, a long table under a vine pergola, cypress trees, golden hills behind."),
    ("BOSQUE", "lugar", "Empty location plate, no characters: a dark Tuscan pine forest with a small abandoned hunter's wooden hut, moss, a tiny fire pit, morning mist."),
    ("CAMINO", "lugar", "Empty location plate, no characters: a dusty stone country road through Tuscan hills, olive groves, rows of tall dark cypress trees, a wide sky."),
]

# Guion de color por bloque (emoción)
COLOR = {
    "0": "Color and light: muddy browns, smoky orange dawn haze, cold teal shadows. Mood: dread and disorientation.",
    "1": "Color and light: warm golden afternoon turning into cold blue night. Mood: thirst, temptation, then cold fear.",
    "2": "Color and light: overcast gray-green daylight, chalk-white accents, long shadows. Mood: unease, silence.",
    "3": "Color and light: sickly amber candlelight with green shadows. Mood: dark comedy and disgust.",
    "4": "Color and light: almost monochrome night blue, one small warm candle; fever dream moments in surreal hot red. Mood: despair.",
    "5": "Color and light: dusty gold daylight under a heavy storm sky, dark cypress silhouettes. Mood: escape and awe-fear.",
    "6": "Color and light: saturated sunny paradise (lemon yellow, rose, sky blue) that turns dark crimson-shadowed when danger hits. Mood: false safety then shock.",
    "7": "Color and light: deep forest night blue turning into a glorious pink-gold sunrise. Mood: exhaustion then triumph.",
    "8": "Color and light: clean bold game-screen colors, gold and deep navy. Mood: victory and challenge.",
    "S": "Color and light: high contrast, saturated, eye-catching.",
}

POV = {
    "POV": "First-person POV shot through PIJAMA's eyes: we see his own hands and/or bare feet at the bottom of the frame",
    "3P": "Third-person shot",
    "OTS": "Over-the-shoulder shot from behind PIJAMA",
    "MACRO": "Extreme macro close-up",
    "PULGA": "Tiny low ground-level shot from the PULGA's point of view, huge foreground, wide-angle distortion",
    "GENERAL": "Wide establishing shot",
    "AEREO": "High aerial bird's-eye shot",
    "CU": "Tight close-up on the face",
}

# (bloque, pov, emoción, línea del guion, ingredientes, escena)
P = [
    # ---------------- BLOQUE 0 · GANCHO ----------------
    ("0", "CU", "calma rota", "Cierras los ojos en tu cama.", "PIJAMA",
     "PIJAMA asleep in a cozy modern bed at night, peaceful face, a phone glowing on the nightstand, warm lamp light."),
    ("0", "POV", "shock", "Los abres en un charco de lodo.", "PIJAMA, CALLE",
     "POV looking down: his own bare feet sunk in a dark mud puddle on the cobblestones of CALLE, his pajama sleeves visible, morning fog."),
    ("0", "3P", "desorientación", "Descalzo. En pijama.", "PIJAMA, CALLE",
     "PIJAMA standing knee-deep in mud in the middle of CALLE, arms open, utterly confused, medieval people stopping to stare."),
    ("0", "CU", "asco", "Huele a humo y a carne podrida.", "PIJAMA_CARAS",
     "PIJAMA pinching his nose with a disgusted face, eyes watering, thick yellowish smoke curling around him."),
    ("0", "GENERAL", "presagio", "Es el año 1348.", "PLAZA",
     "Epic wide shot of medieval Florence at dawn: red roofs, towers, the unfinished cathedral, smoke columns rising from several points of the city, crows in the sky."),
    ("0", "AEREO", "terror", "En esta ciudad, uno de cada dos humanos va a terminar arrojado a una fosa…", "CALLE",
     "Bird's-eye view of a crowd in the street where every second person is drawn as a pale gray fading silhouette while the others stay in color. " + NOGORE),
    ("0", "MACRO", "tensión", "Tienes tres vidas. Un cronómetro de treinta días.", "DESPERTADOR",
     "Macro on DESPERTADOR on a wrist: its screen face glowing, three small red hearts floating above it, a sand-like digital countdown glow."),
    ("0", "3P", "ironía", "Y tu sistema inmune del siglo veintiuno no tiene idea de lo que se le viene encima.", "PIJAMA",
     "Cartoon cutaway inside PIJAMA's body: tiny white-blood-cell soldiers in modern sneakers and headphones relaxing on couches, totally unprepared."),
    ("0", "PULGA", "amenaza", "¿Te mata una rata? ¿El frío? ¿O tu propio vecino?", "PULGA, CALLE",
     "Ground-level view: a big black rat in the foreground, a coughing neighbor in a doorway behind, frost on the cobblestones; three threats lined up."),
    ("0", "MACRO", "revelación", "Spoiler: te va a matar algo que ni siquiera puedes ver…", "PULGA",
     "Macro of PULGA sitting on a single hair of skin, grinning straight at the camera, red eyes glinting, dark background."),
    ("0", "OTS", "desafío", "Cinco decisiones. Si fallas una, pierdes un corazón.", "PIJAMA, CALLE",
     "Over the shoulder of PIJAMA facing five glowing doorways along the street, each door with a different colored light."),
    ("0", "CU", "riesgo", "Si te quedas en cero, no hay respawn.", "PIJAMA_CARAS, DESPERTADOR",
     "PIJAMA gulping, sweat drop, DESPERTADOR on his wrist with a smug grin pointing at the viewer."),
    ("0", "3P", "arranque", "Día uno. El reloj arranca... ya.", "PIJAMA, DESPERTADOR, CALLE",
     "PIJAMA sprinting toward the camera down CALLE, DESPERTADOR on his wrist ringing wildly, mud splashing, motion blur."),

    # ---------------- BLOQUE 1 · DÍAS 1–3 ----------------
    ("1", "GENERAL", "calor", "Son las tres de la tarde.", "PLAZA",
     "Hot golden afternoon in PLAZA, heat haze shimmering, a stray dog panting in the shade."),
    ("1", "CU", "sed", "Tu garganta arde como si hubieras tragado arena.", "PIJAMA_CARAS",
     "PIJAMA holding his throat, cracked dry lips, tongue out, sand grains swirling stylized around his neck."),
    ("1", "POV", "tentación", "Ves una fuente de piedra en la plaza. El agua parece tentadora.", "PIJAMA, PLAZA",
     "POV: his own hands reaching toward the sparkling stone fountain of PLAZA, glittering water, sun reflections."),
    ("1", "OTS", "asco", "A cinco metros, un tipo está lavando tripas de cerdo en el canal.", "PIJAMA, PLAZA",
     "Over the shoulder of PIJAMA: a butcher washing pig guts in the water channel that feeds the fountain, brown swirls in the water."),
    ("1", "MACRO", "peligro", "Si tomas de esa agua, te enfermas y te deshidratas en horas.", "PULGA",
     "Macro inside a drop of water: cartoon germs with angry faces swimming like a pool party."),
    ("1", "3P", "sorpresa", "Hasta los nenes de cinco años toman cerveza o vino agrio.", "PLAZA",
     "Medieval family at a tavern table outdoors, a 5-year-old boy drinking from a big clay mug, PIJAMA in the background with jaw dropped."),
    ("1", "MACRO", "trueque", "Le das un botón de tu pijama a un tabernero…", "PIJAMA",
     "Macro: PIJAMA's fingers placing one white pajama button in the rough palm of a tavern keeper, golden light, like a precious coin."),
    ("1", "3P", "alivio", "…por un trago de vino rancio.", "PIJAMA",
     "PIJAMA drinking from a clay cup with eyes closed in relief, then a tiny grimace at the sour taste."),
    ("1", "GENERAL", "frío", "Cae la noche. La temperatura se desploma a cuatro grados.", "CALLE",
     "CALLE at night, cold blue moonlight, breath vapor from a passing guard, frost forming on the stones."),
    ("1", "CU", "miedo", "Sin abrigo, te mueres de hipotermia antes del amanecer.", "PIJAMA_CARAS",
     "PIJAMA hugging himself, shivering, blue lips, frost on his eyebrows, his breath a white cloud."),
    ("1", "OTS", "decisión", "Primera decisión.", "PIJAMA, CALLE",
     "Over the shoulder of PIJAMA at a fork in the night street: left, a warm glowing noisy inn; right, a dark quiet stable."),
    ("1", "GENERAL", "opción A", "A) Cama en posada caliente.", "CALLE",
     "Inside a cheap crowded inn: twenty strangers packed on straw mattresses, warm fire, soup pot, everyone scratching themselves."),
    ("1", "GENERAL", "opción B", "B) Establo con caballos.", "ESTABLO",
     "ESTABLO at night: empty, quiet, one horse, moonlight, a single hay pile."),
    ("1", "MACRO", "asco", "Un enjambre de cientos de pulgas hambrientas saltando de piel en piel.", "PULGA",
     "Macro of a straw mattress like a jungle: dozens of fleas jumping from sleeping body to body, PULGA leading them like a general."),
    ("1", "3P", "alivio sucio", "Pijama se mete al establo. Huele inmundo.", "PIJAMA, ESTABLO",
     "PIJAMA tiptoeing into ESTABLO holding his nose, the horse turning its head to stare at him."),
    ("1", "3P", "soledad segura", "La soledad es la única armadura que existe en este siglo.", "PIJAMA, ESTABLO",
     "PIJAMA curled up alone in the hay, a moonbeam falling on him like a protective spotlight, the rest of the stable dark."),
    ("1", "CU", "humor", "Aura: más cincuenta. Apestas a caballo.", "DESPERTADOR",
     "DESPERTADOR holding its nose with one tiny arm and giving a thumbs up with the other, golden sparkles."),

    # ---------------- BLOQUE 2 · DÍAS 4–7 ----------------
    ("2", "AEREO", "silencio", "Día cuatro. Las campanas de las iglesias se callan.", "CALLE",
     "Looking up a bell tower: the big bronze bell completely still, its rope tied, pigeons leaving."),
    ("2", "3P", "inquietud", "El gobierno las prohibió: había tantos muertos diarios…", "PLAZA",
     "A town crier reading a decree in a nearly empty PLAZA, a few people with cloths over their mouths listening from far."),
    ("2", "OTS", "sospecha", "Día cinco. El vecino de enfrente no sale a trabajar.", "PIJAMA, CALLE",
     "Over the shoulder of PIJAMA peeking from the stable door at a closed house across CALLE, shutters closed, a pair of work boots left outside."),
    ("2", "GENERAL", "pavor", "Tres hombres con trapos en la cara sacan un bulto envuelto en una sábana blanca.", "CALLE",
     "From far away: three men with cloths over their faces carrying a long white-sheet bundle out of a doorway at dusk, neighbors watching from windows. " + NOGORE),
    ("2", "3P", "malestar", "Así empieza: dolor de cabeza atroz, vómitos y un dolor punzante en la ingle.", "CALLE",
     "A sick medieval man sitting on his doorstep holding his head, gray-green face, dizzy spiral lines, simple and not graphic."),
    ("2", "MACRO", "horror contenido", "Te brota una masa negra del tamaño de una manzana. Un bubón.", "PIJAMA",
     "Stylized medical-diagram look: silhouette of a body with a glowing dark circle under the armpit and an apple drawn next to it for size. Not realistic, no skin detail."),
    ("2", "3P", "peligro", "Si la bacteria salta a tus pulmones, en cuarenta y ocho horas tu corazón se detiene.", "PULGA",
     "Stylized x-ray of lungs filling with dark smoky clouds, a red heart icon cracking, a 48-hour hourglass beside it."),
    ("2", "CU", "urgencia", "Día seis. Un golpe desesperado en la madera de tu establo.", "ESTABLO",
     "Close-up of a small fist knocking hard on the old plank door of ESTABLO, dust shaking off."),
    ("2", "POV", "culpa", "Una nena. Su familia está ardiendo en fiebre adentro. Te suplica que entres.", "NENA, PIJAMA, ESTABLO",
     "POV through the gap of the stable door: NENA outside looking up at us with huge wet eyes, hands together pleading."),
    ("2", "GENERAL", "opción A", "A) Entrar a salvarlos.", "CALLE",
     "A dark doorway of a small house with a warm sick-room glow inside, the open door inviting and ominous."),
    ("2", "GENERAL", "opción B", "B) Dejar pan en el piso y trabar la puerta.", "ESTABLO",
     "A loaf of bread on the ground in front of a closed plank door with a wooden bar across it."),
    ("2", "CU", "conflicto", "Tu moral moderna te dice que entres. Tu instinto biológico te dice que ni respires.", "PIJAMA_CARAS",
     "PIJAMA split by light: half of his face warm and kind, the other half in cold shadow, eyes torn."),
    ("2", "PULGA", "amenaza", "Las pulgas abandonan el cuerpo frío buscando un nuevo huésped caliente.", "PULGA",
     "Ground-level: a row of fleas led by PULGA marching out of a dark doorway toward the camera, following a glowing heat trail. " + NOGORE),
    ("2", "MACRO", "revelación", "Si cruzas esa puerta, tú eres ese huésped.", "PULGA, PIJAMA",
     "PULGA in macro pointing at a giant out-of-focus PIJAMA in the background, licking its lips."),
    ("2", "3P", "dolor", "Pijama deja el pan en la tierra. Da dos pasos hacia atrás. Y atranca la puerta.", "PIJAMA, NENA, ESTABLO",
     "PIJAMA stepping back from a loaf of bread on the ground, NENA receiving it with both hands, both looking at each other with sadness."),
    ("2", "CU", "peso moral", "Sobreviviste a la culpa. Pero sigues respirando.", "PIJAMA_CARAS",
     "PIJAMA sitting with his back against the closed door, eyes shut, one tear, moonlight."),
    ("2", "AEREO", "opresión", "Día siete. Marcan todas las casas de la cuadra con cruces de cal blanca.", "CALLE",
     "Aerial view of CALLE where every door has a big white chalk cross painted on it, a man with a bucket and brush walking away."),
    ("2", "MACRO", "ruleta", "Quedarse en esta ciudad es jugar a la ruleta rusa con cinco balas.", "PIJAMA",
     "Macro of an old wooden spinning wheel of fortune with six slots, five painted black and one white, PIJAMA's finger about to spin it."),

    # ---------------- BLOQUE 3 · DÍAS 8–11 ----------------
    ("3", "MACRO", "alarma", "Día ocho. Sientes un ardor en el tobillo.", "PIJAMA",
     "Macro of PIJAMA's ankle with a tiny red dot glowing like an alarm light."),
    ("3", "PULGA", "villano", "Una marca roja. Una sola pulga del tamaño de una semilla.", "PULGA, PIJAMA",
     "PULGA standing triumphantly on PIJAMA's ankle like a mountain climber planting a tiny flag, a sesame seed next to it for scale."),
    ("3", "CU", "pánico", "Alerta roja: infección detectada.", "DESPERTADOR",
     "DESPERTADOR screaming, its screen face flashing red, bells shaking, sweat flying."),
    ("3", "3P", "urgencia", "Corres a buscar a un médico.", "PIJAMA, CALLE",
     "PIJAMA running down CALLE holding his ankle, hopping on one foot, dramatic speed lines."),
    ("3", "3P", "chiste", "Olvídate del tipo con máscara de pájaro: ese disfraz lo inventan en trescientos años.", "PIJAMA",
     "A thought bubble with a classic plague doctor in a bird mask, with a big red cartoon X stamped over it."),
    ("3", "3P", "repulsión", "El médico de 1348 lleva una túnica sucia y huele a cebolla podrida.", "MEDICO, CONSULTORIO",
     "MEDICO greeting from his doorway in CONSULTORIO with a creepy wide smile, green smell lines and buzzing flies around him."),
    ("3", "MACRO", "amenaza", "…y apoya una cuchilla oxidada sobre una mesa mugrienta.", "CONSULTORIO",
     "Macro of a rusty little knife and a copper bowl on a filthy wooden table, candle reflection on the blade."),
    ("3", "3P", "absurdo", "Te jura que la peste es culpa de los planetas.", "MEDICO, CONSULTORIO",
     "MEDICO pointing dramatically at the planet chart on the wall of CONSULTORIO, Saturn, Jupiter and Mars with angry cartoon faces."),
    ("3", "POV", "decisión", "Tercera decisión.", "MEDICO, PIJAMA, CONSULTORIO",
     "POV sitting on the stool: MEDICO leaning toward us holding the rusty knife in one hand and a vinegar bottle in the other, like offering a choice."),
    ("3", "MACRO", "opción A", "A) Aceptar sangría con cuchilla.", "CONSULTORIO",
     "The rusty knife and empty copper bowl, ominous red-amber light."),
    ("3", "MACRO", "opción B", "B) Huir y lavarte con vinagre.", "CONSULTORIO",
     "A clay bottle of vinegar and a bundle of herbs, soft green clean light."),
    ("3", "3P", "debilidad", "Te bajan las defensas a cero.", "PIJAMA",
     "A pale medieval patient slumped in a chair after a bloodletting, white as paper, an empty battery icon floating above his head. " + NOGORE),
    ("3", "3P", "acción cómica", "Pijama patea la banqueta, agarra el vinagre y corre como un desquiciado.", "PIJAMA, MEDICO, CONSULTORIO",
     "PIJAMA kicking the stool flying, grabbing the vinegar bottle mid-air, MEDICO falling backward with the knife, comic chaos."),
    ("3", "CU", "ardor", "El ardor insoportable espanta a nuevos bichos.", "PIJAMA_CARAS",
     "PIJAMA splashing vinegar on his arms with eyes squeezed shut, steam-like smell waves, fleas jumping away."),
    ("3", "MACRO", "temor", "Aun así, la bacteria ya está adentro.", "PULGA",
     "Stylized bloodstream tunnel (cartoon tube) with tiny dark germ cells sneaking in like burglars."),
    ("3", "POV", "fiebre", "Día once. Cuarenta de fiebre. La vista se te apaga.", "PIJAMA, ESTABLO",
     "POV with blurred, double vision: the stable ceiling spinning, the edges of the frame darkening, heat shimmer."),
    ("3", "CU", "golpe", "Pierdes un corazón. Te quedan dos vidas.", "PIJAMA_CARAS",
     "PIJAMA collapsing in the hay, a big red heart shattering into shards above him, red vignette."),

    # ---------------- BLOQUE 4 · DÍAS 12–17 ----------------
    ("4", "GENERAL", "luto", "Día doce. Ya no existen los funerales.", "PLAZA",
     "An empty church square at night, the church doors closed, a single candle on the steps, total silence."),
    ("4", "GENERAL", "horror lejano", "Pasan carretas por la noche hacia zanjas gigantescas.", "CALLE",
     "Far away at night: a silhouette of a cart pulled by a tired figure with a lantern, white sheets in the cart, heading out of the city gate. " + NOGORE),
    ("4", "AEREO", "escala", "…zanjas gigantescas cubiertas con cal viva.", "CAMINO",
     "Extremely far aerial view outside the city walls: long pale trenches like scars in the earth dusted with white lime, tiny figures with shovels. " + NOGORE),
    ("4", "3P", "derrumbe", "Pijama cae de rodillas sobre la paja del establo.", "PIJAMA, ESTABLO",
     "PIJAMA falling to his knees in the hay of ESTABLO, one hand on the ground, shaking, cold blue light."),
    ("4", "POV", "delirio", "Delira con su casa, con su cama, con una ducha caliente.", "PIJAMA",
     "Fever-dream POV: the stable walls melting into his modern bathroom with a hot shower and his cozy bed, surreal hot red and orange colors."),
    ("4", "3P", "agotamiento", "Pasa tres días sin comer, bebiendo vino tibio a gotas.", "PIJAMA, ESTABLO",
     "PIJAMA lying weak, letting single drops fall from a cup into his mouth, the horse lowering its head next to him."),
    ("4", "POV", "terror", "Día quince. Se pasa los dedos temblorosos por el cuello y las axilas.", "PIJAMA",
     "POV: his own trembling fingers touching his neck, lit by one candle, deep shadows."),
    ("4", "CU", "suspenso", "Buscando el bulto.", "PIJAMA_CARAS",
     "Extreme tension close-up of PIJAMA's eyes wide open, a single sweat drop rolling down."),
    ("4", "CU", "alivio", "Nada.", "PIJAMA_CARAS",
     "PIJAMA exhaling, eyes closed, a faint warm light returning to his face."),
    ("4", "3P", "explicación", "Era una neumonía brutal por el frío del establo y las defensas bajas.", "PIJAMA, ESTABLO",
     "Wind and snowflakes blowing through the gaps of the stable onto PIJAMA under thin straw, cold blue."),
    ("4", "CU", "crítico", "Te queda una sola vida.", "DESPERTADOR",
     "DESPERTADOR with a cracked screen showing one single red heart, alarm red light pulsing."),
    ("4", "3P", "amenaza final", "El más mínimo rasguño a partir de ahora significa Game Over.", "PIJAMA, PULGA",
     "PIJAMA standing up slowly, behind him on the wall a huge shadow of PULGA looming like a monster."),

    # ---------------- BLOQUE 5 · DÍAS 18–21 ----------------
    ("5", "GENERAL", "privilegio", "En la plaza, diez jóvenes nobles cargan caballos con baúles de comida y seda.", "PLAZA",
     "Ten elegant young nobles in bright silk loading horses and mules with chests and baskets in PLAZA, gray city around them."),
    ("5", "3P", "envidia", "Se escapan al campo, a una mansión en las colinas.", "VILLA",
     "The young nobles riding away toward a sunny villa on a hill while gray smoke rises from the city behind them."),
    ("5", "3P", "dato real", "El escritor Giovanni Boccaccio escribió un libro sobre ellos: el Decamerón.", "PLAZA",
     "A chubby medieval writer (Boccaccio) at a desk by candlelight writing in a big leather book, winking at the viewer."),
    ("5", "CU", "humor", "La primera cuarentena VIP de la historia.", "DESPERTADOR",
     "DESPERTADOR wearing tiny sunglasses and a tiny velvet rope behind it like a VIP club entrance."),
    ("5", "OTS", "decisión", "Cuarta decisión.", "PIJAMA, CAMINO",
     "Over the shoulder of PIJAMA at the city gate: behind him the gray city, ahead the dusty road to the sunny hills."),
    ("5", "GENERAL", "opción A", "A) Quedarte en el establo.", "ESTABLO",
     "The dark stable in the gray city, a rat peeking from the hay."),
    ("5", "GENERAL", "opción B", "B) Seguir los carruajes 30 km a pie.", "CAMINO",
     "The long dusty road into golden hills with the noble caravan far ahead."),
    ("5", "POV", "esfuerzo", "Pijama echa a correr detrás de los caballos. Descalzo.", "PIJAMA, CAMINO",
     "POV running: his own bare feet on hot stones of CAMINO, the horses' dust cloud ahead."),
    ("5", "GENERAL", "paisaje", "Tragando polvo por senderos de piedra.", "PIJAMA, CAMINO",
     "Tiny PIJAMA crossing endless golden hills between cypress lines, dramatic sky, tiny caravan far ahead."),
    ("5", "GENERAL", "pesadilla", "Día veinte. A mitad de la ruta te topas con una escena de pesadilla.", "CAMINO",
     "Storm clouds over the road; on the hill a long procession of hooded figures carrying a cross appears in silhouette."),
    ("5", "3P", "fanatismo", "Cincuenta hombres marchando en fila, azotándose la espalda con látigos.", "CAMINO",
     "Stylized silhouettes of penitents in a line raising small whips against a red-orange stormy sky, faces hidden by hoods. No blood, no wounds."),
    ("5", "CU", "fe ciega", "Los flagelantes. Creen que sufriendo van a calmar el castigo de Dios.", "CAMINO",
     "Close-up of a hooded penitent singing with closed eyes, candlelight on his face, intense and serious."),
    ("5", "MACRO", "ironía", "Van llevando pulgas de pueblo en pueblo.", "PULGA",
     "PULGA riding on the hood of a penitent like a passenger on a bus, waving a tiny handkerchief."),
    ("5", "3P", "escondite", "Pijama se tira de cabeza a una zanja llena de barro hasta que pasan.", "PIJAMA, CAMINO",
     "PIJAMA diving head-first into a muddy ditch beside the road, only his eyes above the mud, the procession passing above."),
    ("5", "CU", "orgullo", "Esquivaste la secta. Te queda un corazón latiendo.", "DESPERTADOR",
     "DESPERTADOR covered in mud, still grinning, one red heart beating above it."),

    # ---------------- BLOQUE 6 · DÍAS 22–27 ----------------
    ("6", "GENERAL", "llegada", "Día veintidós. Llegas a la villa en la montaña.", "PIJAMA, VILLA",
     "PIJAMA arriving at the villa gate covered in dry mud, the sunny garden of VILLA opening behind the gate like paradise."),
    ("6", "3P", "comedia", "Creen que tu pijama de estrellas es un traje de seda de algún noble exótico.", "PIJAMA, VILLA",
     "A young noblewoman touching PIJAMA's starry pajama sleeve with amazement, sparkles on the fabric, PIJAMA doing a fancy noble pose."),
    ("6", "POV", "paraíso", "Pan blanco. Aire puro. Cero ratas a la vista.", "PIJAMA, VILLA",
     "POV at the long table of VILLA: his hands reaching for white bread, grapes, cheese, lemons, sunlight through the vines."),
    ("6", "3P", "alivio", "Tu barra de infección cae en picada al verde.", "PIJAMA, VILLA",
     "PIJAMA lying on the grass of the villa garden smiling with eyes closed, butterflies around."),
    ("6", "GENERAL", "falsa calma", "Día veinticinco. La cena está servida en una mesa larga.", "VILLA",
     "Golden-hour dinner at the long table of VILLA, ten nobles laughing, candles, wine, lute player."),
    ("6", "3P", "shock", "El criado que está sirviendo el vino suelta la copa…", "VILLA",
     "A servant dropping a wine cup in slow motion, the cup in mid-air, everyone turning their heads."),
    ("6", "CU", "horror", "…se dobla en dos y tose sobre la comida.", "VILLA",
     "The servant bent over coughing into his elbow, a dark smoky cartoon cloud spreading over the food. " + NOGORE),
    ("6", "CU", "miedo", "Tiene los ojos rojos como brasas.", "VILLA",
     "Close-up of the servant's feverish red eyes, sweat, dark red shadows."),
    ("6", "GENERAL", "pánico", "El salón entero se congela.", "VILLA",
     "Wide frozen moment: all the nobles stopped mid-gesture, the sunny scene suddenly drained to dark crimson shadows."),
    ("6", "GENERAL", "opción A", "A) Encerrarte en un cuarto de la mansión.", "VILLA",
     "A small closed room inside the villa with one tiny window, stale air, dust floating."),
    ("6", "GENERAL", "opción B", "B) Huir a la intemperie del bosque.", "BOSQUE",
     "The dark open pine forest at night, cold but with fresh moving air and stars."),
    ("6", "3P", "acción", "Pijama revienta una ventana trasera y se pierde en el bosque.", "PIJAMA, VILLA",
     "PIJAMA jumping through a back window of the villa holding bread, wooden shutters flying, night forest behind."),
    ("6", "GENERAL", "refugio", "Encuentra una choza de cazador abandonada entre los árboles.", "PIJAMA, BOSQUE",
     "PIJAMA discovering the abandoned hunter's hut in BOSQUE, a moonbeam on its door."),
    ("6", "GENERAL", "dato", "Las autoridades obligaron a los barcos a esperar treinta días sin tocar tierra.", "CAMINO",
     "A medieval Adriatic harbor with stone walls: wooden ships anchored far out at sea, a guard on the pier holding up his hand, a big hourglass on the dock."),
    ("6", "MACRO", "revelación", "Lo llamaron trentino. Luego cuarenta: quaranta. Cuarentena.", "PIJAMA_CARAS",
     "PIJAMA with a mind-blown face, cartoon explosion of stars around his head."),

    # ---------------- BLOQUE 7 · DÍAS 28–30 ----------------
    ("7", "3P", "espera", "Día veintiocho. Solo en la choza.", "PIJAMA, BOSQUE",
     "PIJAMA sitting by a tiny fire inside the hut, carving tally marks on the wooden wall, night."),
    ("7", "CU", "esperanza", "Día veintinueve. Ni fiebre, ni tos, ni frío.", "PIJAMA_CARAS",
     "PIJAMA touching his own forehead and smiling slightly, first light of dawn on his face."),
    ("7", "POV", "triunfo", "Día treinta. Abres la puerta de madera astillada.", "PIJAMA, BOSQUE",
     "POV: his own hands pushing open the splintered hut door, blinding golden sunrise light pouring in."),
    ("7", "GENERAL", "gloria", "El sol baña el valle.", "PIJAMA, BOSQUE",
     "PIJAMA standing at the edge of the forest with arms wide open over a Tuscan valley bathed in pink-gold sunrise."),
    ("7", "GENERAL", "épica", "Sobreviviste al mes más letal del siglo catorce. En pijama.", "PIJAMA, DESPERTADOR",
     "Low angle hero shot of PIJAMA raising a golden trophy shaped like a pillow, DESPERTADOR ringing with joy, light rays."),
    ("7", "MACRO", "victoria", "Aura final: más mil trescientos cuarenta y ocho.", "DESPERTADOR",
     "DESPERTADOR exploding with golden fireworks and confetti, eyes turned into stars."),
    ("7", "GENERAL", "giro", "Murió tanta mano de obra que los que quedaron vivos pudieron exigir el doble.", "CAMINO",
     "Empty wheat fields with abandoned scythes, a nervous landlord facing a group of peasants with crossed arms."),
    ("7", "3P", "remate", "Esquivaste a la muerte negra… y conseguiste el aumento de sueldo más descomunal de la historia.", "PIJAMA",
     "PIJAMA in his starry pajamas holding a scythe and a fat bag of gold coins, giving a thumbs up, peasants cheering."),

    # ---------------- BLOQUE 8 · RESULTADOS ----------------
    ("8", "3P", "reto", "Tu tarjeta de supervivencia: cinco de cinco.", "PIJAMA, DESPERTADOR",
     "PIJAMA and DESPERTADOR standing proudly in front of a big wooden medieval scoreboard with five empty rows (no text)."),
    ("8", "CU", "comentarios", "¿Cuántas acertaste tú? Escríbelo en los comentarios.", "DESPERTADOR",
     "DESPERTADOR pointing straight at the viewer with a tiny quill, a cheeky challenging grin."),
    ("8", "3P", "burla", "¿O te liquidó el médico en el día ocho?", "MEDICO",
     "MEDICO waving goodbye at the viewer with his rusty knife and a creepy smile."),

    # ---------------- SHORTS: primer cuadro vertical de cada uno ----------------
    ("S", "POV", "gancho", "SHORT 0 · Los abres en un charco de lodo. Es 1348.", "PIJAMA, CALLE",
     "Vertical POV looking down at his own bare feet in mud on medieval cobblestones, a crowd of medieval legs around, smoke."),
    ("S", "3P", "gancho", "SHORT 1 · El agua parece tentadora.", "PIJAMA, PLAZA",
     "PIJAMA about to drink from the fountain while behind him a butcher washes guts in the same water."),
    ("S", "POV", "gancho", "SHORT 2 · Una nena te suplica que entres.", "NENA, ESTABLO",
     "Vertical POV through a door gap: NENA pleading with huge wet eyes."),
    ("S", "MACRO", "gancho", "SHORT 3 · Una sola pulga.", "PULGA, PIJAMA",
     "PULGA planting a tiny flag on PIJAMA's ankle, grinning at camera."),
    ("S", "POV", "gancho", "SHORT 4 · Buscando el bulto.", "PIJAMA",
     "Vertical POV of trembling fingers touching his neck by candlelight."),
    ("S", "3P", "gancho", "SHORT 5 · Una escena de pesadilla en el camino.", "PIJAMA, CAMINO",
     "PIJAMA hiding in a muddy ditch with only his eyes visible while hooded silhouettes pass against a storm sky."),
    ("S", "3P", "gancho", "SHORT 6 · El criado suelta la copa.", "VILLA",
     "A wine cup frozen mid-air falling, nobles' shocked faces around the table."),
    ("S", "POV", "gancho", "SHORT 7 · Día treinta.", "PIJAMA, BOSQUE",
     "Vertical POV pushing open a hut door into a blinding golden sunrise."),
    ("S", "3P", "gancho", "SHORT 8 · ¿Cuántas acertaste?", "PIJAMA, DESPERTADOR",
     "PIJAMA holding up five fingers next to DESPERTADOR, in front of a wooden scoreboard."),
]

MINIATURAS = [
    ("A · La pulga gigante", "PIJAMA_CARAS, PULGA",
     "YouTube thumbnail composition, 16:9: on the left, PIJAMA's face in extreme terror (huge eyes, mouth open, sweat); on the right, PULGA drawn GIANT and close to the camera, grinning with fangs, red eyes glowing. Dark crimson background with a hint of medieval Florence silhouette. Very high contrast, rim light, simple, readable at tiny size. Leave the top-left corner empty for big text."),
    ("B · Día 30 en la fosa", "PIJAMA, DESPERTADOR",
     "YouTube thumbnail composition, 16:9: PIJAMA standing on the edge of a dark pit, looking back at the camera with a desperate face, DESPERTADOR on his wrist glowing red; a huge glowing countdown light behind him. Deep blue night, red rim light, extremely simple and bold. Leave the right third empty for big text. " + NOGORE),
    ("C · Elegí bien", "PIJAMA_CARAS, MEDICO",
     "YouTube thumbnail composition, 16:9: split in two by a glowing line; left side MEDICO grinning with a rusty knife in sickly green light; right side a vinegar bottle in clean golden light; PIJAMA's terrified face in the center between them. Bold, high contrast, few elements. Leave the top strip empty for text."),
]


def prompt(b, pov, ings, escena):
    v = b == "S"
    # primero qué se ve (plano + escena + referencias), después luz, estilo y formato
    partes = [f"{POV[pov]}.", escena, f"Use the reference images: {ings}." if ings else "", COLOR[b], ESTILO,
              FORMATO_V if v else FORMATO]
    return " ".join(x for x in partes if x)


def main():
    planos = []
    for i, (b, pov, emo, linea, ings, escena) in enumerate(P, 1):
        planos.append({"id": f"{i:03d}", "bloque": b, "pov": pov, "emocion": emo, "linea": linea,
                       "ingredientes": ings, "prompt": prompt(b, pov, ings, escena)})
    ingredientes = [{"nombre": n, "tipo": t, "prompt": f"{ESTILO} {p} No text, letters or logos."} for n, t, p in ING]
    minis = [{"nombre": n, "ingredientes": ing, "prompt": f"{ESTILO} {p} No text, letters or logos."} for n, ing, p in MINIATURAS]
    data = {"ingredientes": ingredientes, "planos": planos, "miniaturas": minis}
    (DOCS / "visual_v3.json").write_text(json.dumps(data, ensure_ascii=False, indent=1))
    from collections import Counter
    print(len(ingredientes), "ingredientes ·", len(planos), "planos ·", len(minis), "miniaturas")
    print("puntos de vista:", dict(Counter(p["pov"] for p in planos)))
    tpl = (V / "tools" / "prompts_v3_plantilla.html").read_text()
    (DOCS / "prompts_v3.html").write_text(tpl.replace("__DATA__", json.dumps(data, ensure_ascii=False)))


if __name__ == "__main__":
    main()
