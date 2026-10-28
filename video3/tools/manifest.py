#!/usr/bin/env python3
"""
Arma el manifest de imágenes del video 3 (docs/manifest_imagenes_v3.json) y la
página de prompts con botón de copiar (docs/prompts_video3.html), con el mismo
formato que el video 2. Las escenas siguen el guion v1, línea por línea.

  python3 video3/tools/manifest.py
"""
import json
import re
from pathlib import Path

V = Path(__file__).resolve().parent.parent
DOCS = V / "docs"

ESTILO = ("Flat 2D vector cartoon illustration, thick black outlines, bold flat colors, no gradients, no shadows, "
          "exaggerated funny expressions, simple shapes, strong contrast, dramatic composition. Horizontal 16:9 widescreen "
          "image that fills the entire frame edge to edge. Put the main character and the key action in the center of the "
          "frame, inside the middle third of the width, so a vertical 9:16 crop of the center still works. The left and right "
          "sides are a natural continuation of the same scene with no important details. Do not draw any frame, border, black "
          "bars, panels, split screens or letterbox lines. Absolutely no text, no letters, no numbers, no logos, no watermarks.")
ESTILO_SHORT = ("Flat 2D vector cartoon illustration, thick black outlines, bold flat colors, no gradients, no shadows, "
                "exaggerated funny expressions, simple shapes, strong contrast, dramatic composition. Vertical 9:16 image that "
                "fills the entire frame edge to edge, with a calm empty zone in the upper third for later text. Do not draw any "
                "frame, border or black bars. Absolutely no text, no letters, no numbers, no logos, no watermarks.")

PERSONAJES = {
    "P": "Pijama (a modern man around 30, round head, messy brown hair, big expressive eyes, light-blue pajamas with small white stars, bare feet)",
    "D": "the Despertador (a chunky retro twin-bell alarm clock with a round screen face, big expressive eyes, tiny arms and legs, and a wrist strap, sarcastic personality)",
    "F": "the Pulga (a tiny cartoon flea villain the size of a sesame seed, shown big only in close-ups: dark brown shiny body, long jumping legs, a wicked little grin and tiny fangs)",
    "M": "the 1348 doctor (a skinny medieval Italian physician in a long dark red robe and a round red cap, a big nose, holding a small glass urine flask and a bundle of herbs; NO bird mask)",
}

PALETAS = {
    "X": "",
    "H": "Palette: dawn orange, deep night navy, terracotta, cream.",
    "1": "Palette: warm terracotta, ochre, cream, Renaissance red, sky blue.",
    "2": "Palette: ochre turning to cold gray-blue, dark green shutters, pale stone.",
    "3": "Palette: amber candlelight, dark wood brown, herb green, glass teal.",
    "4": "Palette: desaturated ash gray, bone white, deep night blue, a single cold candle yellow.",
    "5": "Palette: Tuscan olive green, dark cypress green, golden hills, dusty road beige.",
    "6": "Palette: bright cream, lemon yellow, sky blue, rose pink, garden green.",
    "7": "Palette: pine green, pink-gold sunrise, warm wood brown.",
    "R": "Palette: bold flat colors, gold, cream, deep navy.",
    "S": "Palette: bold saturated colors fitting the scene.",
}

LUGARES = {
    "CALLEJON": "Florence, Italy, April 1348: a narrow medieval stone alley at dawn, tall ochre and terracotta houses with wooden shutters, laundry lines, a stone gutter, a church bell tower in the distance.",
    "MERCADO": "Florence, Italy, spring 1348: the busy Mercato Vecchio, wooden market stalls with bread, cheese, onions and bolts of colored wool cloth, merchants in long tunics and hoods, women with baskets, stone houses around, the unfinished cathedral with scaffolding and NO dome in the background.",
    "TABERNA": "A small medieval Florentine tavern in 1348: dark wooden beams, a long table, clay jugs of watered wine, a fireplace, rough clay cups, a chubby tavern keeper.",
    "POSADA": "A crowded cheap medieval inn room in 1348: twenty sleeping travelers packed on straw mattresses on the floor, one small fire, wooden beams, dirty blankets.",
    "ESTABLO": "A small medieval stable in Florence in 1348: wooden stalls, hay piles, one tired brown horse, a lantern, a broken door, night sky through the gaps.",
    "CALLE": "A narrow residential street in Florence in 1348: closed dark green shutters, wooden doors, stone walls, a few worried neighbors at windows, a dog, gray light.",
    "CASA": "Inside a poor medieval Florentine house in 1348: one room, a wooden bed with linen sheets, a clay water jug, a small window, straw on the floor.",
    "MEDICO": "A medieval physician's study in Florence in 1348: shelves with glass flasks and clay jars, bundles of dried herbs hanging from the ceiling, an astrology chart of planets on the wall, a big old book, candles, a small skeleton model.",
    "AVIGNON": "The papal palace in Avignon in 1348: a grand stone hall with tall windows, red and gold tapestries, an old pope in white and red robes sitting on a chair between two huge roaring bonfires.",
    "CIUDAD_GRIS": "Florence in summer 1348 seen at dusk: empty streets, shuttered houses, a silent bell tower, smoke from small fires, a few distant figures with cloth over their faces, gray sky.",
    "FOSA": "The edge of Florence in 1348: a wide burial trench seen from far away, filled with rows of simple white linen-wrapped shapes (no bodies visible, no blood), a few mourners with lowered heads, cypress trees, gray sky.",
    "PLAZA": "A Florentine piazza in 1348: a stone fountain, a church facade, ten elegant young nobles (seven young women in colorful gowns and three young men in fine tunics) talking quietly in a group.",
    "CAMINO": "A Tuscan country road in 1348: golden rolling hills, olive groves, tall dark cypress trees, a dusty dirt path, a small stone bridge.",
    "VILLA": "A sunny Tuscan villa in the hills in 1348: a stone house with arches, a garden with roses and lemon trees, a long table under a pergola with white bread, fruit and wine, a well, ten young nobles in fine clothes.",
    "RAGUSA": "The medieval port city of Ragusa (Dubrovnik) on the Adriatic coast in 1377: stone city walls, a harbor with wooden sailing ships, a small island with a quarantine hut, deep blue sea.",
    "CHOZA": "A small wooden hut alone in a pine forest in Tuscany in 1348: moss, a tiny campfire, a wooden door, morning mist, birds.",
    "NEUTRO": "A plain bold flat-color background.",
    "LAB": "A clean modern science-style backdrop with a big magnifying glass.",
}

CAMS = {"WS": "Wide shot", "MS": "Medium shot", "CU": "Close-up", "EC": "Extreme close-up", "LA": "Low angle shot",
        "HA": "High angle top-down shot", "OTS": "Over-the-shoulder shot", "FE": "Fisheye shot"}
TRS = {"": "", "FLASH": "Entra con flash blanco", "PUNCH": "Zoom de impacto", "SMASH": "Corte seco al negro + timbre",
       "WHIP": "Barrido rápido", "GAME": "El cartel sube como pantalla de videojuego", "MATCH": "Corte por coincidencia",
       "SHAKE": "Sacudida de cámara (pérdida de vida o susto)"}

# (bloque, lugar, cámara, transición, cita del guion, escena en inglés)
E = [
    # ---------- HOJAS DE REFERENCIA ----------
    ("X", "NEUTRO", "WS", "", "Hoja de Pijama: si ya tenés la del video 2 (001), usá esa misma",
     "Character reference sheet of {P}. Four poses side by side on a plain cream background: neutral standing, scared with wide eyes and hands on cheeks, tired with eyes closed and head down, and proud with fists on hips."),
    ("X", "NEUTRO", "WS", "", "Hoja del Despertador: si ya tenés la del video 2 (002), usá esa misma",
     "Character reference sheet of {D}. Four poses side by side on a plain cream background: smug grin, laughing, shouting with bells ringing, and worried with sweat drops."),
    ("X", "NEUTRO", "WS", "", "Hoja de la Pulga (personaje nuevo): subirla como referencia en todas las de la pulga",
     "Character reference sheet of {F}, drawn big. Four poses side by side on a plain cream background: evil grin, mid-jump with legs stretched, rubbing its tiny hands, and laughing."),
    ("X", "NEUTRO", "WS", "", "Hoja del médico de 1348 (personaje nuevo)",
     "Character reference sheet of {M}. Four poses side by side on a plain cream background: lecturing with one finger up, sniffing herbs, holding the flask to the light, and shrugging."),
    # ---------- GANCHO ----------
    ("H", "CALLEJON", "EC", "FLASH", "Florencia. Abril de 1348. Día uno.",
     "Extreme close-up of {P}'s eye snapping open, a stone wall and morning light reflected in it."),
    ("H", "CALLEJON", "HA", "", "Abres los ojos en un callejón. Descalzo. En pijama. Otra vez.",
     "Top-down view of {P} lying on his back on the stone ground of the alley, arms spread, confused face, a pigeon standing on his chest."),
    ("H", "CALLEJON", "LA", "", "Abres los ojos en un callejón. Descalzo. En pijama. Otra vez.",
     "Low angle of {P} standing up slowly in the alley, looking up at the tall medieval houses, mouth open."),
    ("H", "CALLEJON", "CU", "PUNCH", "¿Te acuerdas de la peste negra? Duraste once días.",
     "Close-up of {D} strapped on {P}'s wrist, smirking, one eyebrow raised, holding up one tiny finger."),
    ("H", "CALLEJON", "MS", "", "Revancha. Dificultad: realista.",
     "{D} on {P}'s wrist wearing a tiny red headband like a fighter, punching the air, {P} looks nervous."),
    ("H", "CALLEJON", "WS", "", "Esta vez no tienes que llegar lejos. Tienes que llegar al día treinta.",
     "Wide shot of {P} at the start of the long alley, the alley stretching far like a game level, a faint glowing finish line far at the end."),
    ("H", "CALLEJON", "CU", "", "Tres vidas. Una barra de infección. Y cada tanto, una decisión.",
     "{P} holding up three fingers with a determined face, three small glowing red hearts floating above his hand."),
    ("H", "CALLEJON", "MS", "", "Tú eliges. Yo te digo si sobrevives.",
     "{D} pointing straight at the viewer with a tiny arm, confident grin, {P} behind him shrugging."),
    ("H", "MERCADO", "WS", "", "En los próximos meses, en esta ciudad, va a morir más o menos la mitad de la gente.",
     "Wide shot of the busy market crowd, half of the people drawn in color and the other half drawn as pale gray ghostly silhouettes, {P} in the middle noticing it in shock."),
    ("H", "MERCADO", "CU", "", "Mira a la persona que tengas al lado. Uno de los dos… no llega al verano.",
     "Close-up of two medieval neighbors side by side looking at each other suspiciously, one of them slightly pale, a tiny {F} jumping between them."),
    ("H", "CALLEJON", "LA", "WHIP", "Treinta días. Empieza… ya.",
     "{P} sprinting out of the alley toward the camera, arms pumping, {D} on his wrist yelling with bells ringing, dust flying."),
    # ---------- DÍAS 1–3 ----------
    ("1", "MERCADO", "CU", "", "Día uno. Tu primer enemigo no es la peste. Es el hambre.",
     "Close-up of {P}'s stomach growling with visible cartoon sound lines, he holds it with both hands, a bread stall behind him."),
    ("1", "MERCADO", "WS", "GAME", "Florencia tiene unas cien mil personas. Es una de las ciudades más ricas de Europa.",
     "Big wide establishing shot of medieval Florence from a hill: red tiled roofs, towers, the river Arno with bridges, the cathedral without dome, tiny {P} in the foreground amazed."),
    ("1", "MERCADO", "MS", "", "Bancos, telas de lana, y una catedral gigante a medio construir.",
     "A rich Florentine banker counting gold florins at a green cloth table, piles of colored wool cloth behind him, {P} peeking at the coins."),
    ("1", "MERCADO", "LA", "", "La cúpula todavía no existe. Faltan casi cien años.",
     "Low angle of the unfinished cathedral with a big empty round hole on top and wooden scaffolding, {P} looking up and scratching his head."),
    ("1", "MERCADO", "MS", "", "Nadie te mira raro por el pijama. Porque nadie mira a nadie a los ojos.",
     "{P} walking through the market crowd, everyone looking down or away with nervous eyes, nobody noticing his pajamas."),
    ("1", "MERCADO", "CU", "", "En el mercado hay rumores. Que a Sicilia llegaron barcos con la tripulación muerta.",
     "Two market women whispering behind a hand, a thought bubble above them showing a ghost ship with torn sails at sea."),
    ("1", "MERCADO", "MS", "", "Que en Pisa ya empezó.",
     "A merchant with a donkey cart arriving from the road, covered in dust, the crowd stepping back from him."),
    ("1", "MERCADO", "CU", "PUNCH", "Spoiler: acá también.",
     "{D} on {P}'s wrist doing a dramatic side-eye at the viewer, a tiny {F} waving hello from a rat's back in the corner."),
    ("1", "CALLE", "MS", "", "Tienes sed. Y el agua del río… no. Eso ya lo aprendiste en Londres.",
     "{P} kneeling at the muddy river bank about to drink, then freezing with a horrified face, dirty water with floating garbage."),
    ("1", "TABERNA", "MS", "", "Acá casi todos toman vino aguado o cerveza. Hasta los chicos.",
     "A medieval family at the tavern table, even the small children drinking from clay cups, {P} watching in surprise."),
    ("1", "TABERNA", "CU", "", "En una taberna te dan vino aguado a cambio de un botón del pijama.",
     "Close-up of {P}'s hand trading a small white pajama button to the chubby tavern keeper, who inspects it like a jewel."),
    ("1", "TABERNA", "MS", "", "Primer trueque. Aura: más diez.",
     "{P} proudly drinking from a clay cup, {D} giving a thumbs up, golden sparkles around them."),
    ("1", "CALLE", "WS", "", "Día dos. Duermes en un portal. Te despierta un perro. Te persigue un panadero.",
     "Comic chase: {P} running down the street, a small barking dog and an angry baker with a rolling pin chasing him."),
    ("1", "ESTABLO", "WS", "", "Día tres. Cae la noche. Y llega la primera decisión.",
     "Night falls over Florence, {P} standing alone at a crossroads holding a lantern, one path to a noisy glowing inn and the other to a dark quiet stable."),
    ("1", "POSADA", "WS", "", "A: una posada barata, con fuego y llena de gente.",
     "Option A: the crowded cheap inn, twenty travelers packed on straw mattresses, warm fire, everybody scratching."),
    ("1", "ESTABLO", "WS", "", "B: un establo, solo, con los caballos.",
     "Option B: the quiet stable at night, one horse, a hay pile, moonlight, empty and calm."),
    ("1", "POSADA", "EC", "", "Y cada colchón es un hotel de pulgas.",
     "Extreme close-up of a straw mattress like a tiny hotel full of cartoon fleas: a flea reception desk, fleas jumping on the straw like a trampoline, {F} as the hotel manager."),
    ("1", "ESTABLO", "MS", "", "Pijama elige el establo.",
     "{P} lying happily in a hay pile in the stable, the horse sniffing his hair, {D} holding his nose."),
    # ---------- DÍAS 4–7 ----------
    ("2", "CALLE", "MS", "", "Día cuatro. Un vecino de la calle no abre la ventana.",
     "A closed dark green window shutter on a stone house, a cat waiting on the sill, {P} looking up from the street, worried."),
    ("2", "CALLE", "WS", "", "Día cinco. Abren su puerta. Y lo sacan envuelto en una sábana.",
     "Wide shot from far: two men carrying a long white linen-wrapped shape out of a doorway (no body visible), neighbors watching from windows, {P} frozen at the corner."),
    ("2", "CASA", "CU", "", "Así empieza. Fiebre. Escalofríos. Dolor de cabeza. Como una gripe.",
     "A sick medieval man in bed sweating and shivering under a blanket, a wet cloth on his forehead, simple cartoon style, not gory."),
    ("2", "LAB", "MS", "", "Después aparece un bulto, del tamaño de un huevo, en la axila o en la ingle.",
     "Simple medical diagram style: a cartoon outline of a human body with a glowing circle under the armpit and another at the groin, an egg drawn next to it for size."),
    ("2", "LAB", "CU", "", "Se llama bubón. Por eso le dicen peste bubónica.",
     "A cartoon egg with a tiny worried face labeled only by a red circle around it, a magnifying glass over it."),
    ("2", "CALLE", "MS", "", "Y en tres a siete días… casi siempre se termina.",
     "A wall calendar of seven days with dark crosses appearing, {P} reading it and gulping."),
    ("2", "CALLE", "CU", "", "Hay una versión peor: cuando llega a los pulmones. Se contagia tosiendo.",
     "A medieval man coughing a big green cartoon cloud full of tiny {F}-style germs, {P} leaning far back to avoid it."),
    ("2", "CALLE", "CU", "", "Tranquilo. Eso no te va a pasar.",
     "{D} patting {P}'s hand reassuringly with a fake smile."),
    ("2", "CALLE", "EC", "PUNCH", "…Probablemente.",
     "Extreme close-up of {D}'s eyes looking sideways, one sweat drop."),
    ("2", "CALLE", "WS", "", "Lo que nadie sabe en 1348 es quién la trae.",
     "Townspeople pointing fingers at each other in a circle in the street, everyone blaming someone else, confusion."),
    ("2", "CALLE", "LA", "PUNCH", "No son los vecinos. Son las pulgas.",
     "Low angle reveal: a huge cartoon rat in the shadows with {F} riding on its back like a cowboy, grinning."),
    ("2", "CALLE", "MS", "", "Viajan en las ratas, en la ropa, en las telas que vende esta ciudad.",
     "Bolts of wool cloth on a merchant cart with tiny fleas jumping out of the folds, a rat running along a rope."),
    ("2", "LAB", "CU", "", "Nadie acá sabe lo que es un germen. Faltan más de quinientos años.",
     "A medieval man looking through a broken empty frame like a magnifying glass and seeing nothing, a modern microscope floating far away in a time bubble."),
    ("2", "ESTABLO", "MS", "", "Día seis. La familia del vecino golpea tu establo. Piden ayuda.",
     "A poor mother and her little girl knocking at the stable door at dusk, {P} peeking out from behind the door."),
    ("2", "CASA", "WS", "", "A: entras a su casa a ayudar.",
     "Option A: the dark small house with a sick man in bed, fleas visible on the blanket, an open door inviting in."),
    ("2", "CALLE", "WS", "", "B: les dejas pan en la puerta, sin entrar.",
     "Option B: a loaf of bread left on a doorstep, the door closed, warm light from the window."),
    ("2", "CALLE", "MS", "", "Esta es la más difícil del juego. Lo correcto y lo seguro no siempre son lo mismo.",
     "{P} torn between two paths, a small angel and a small devil on his shoulders, both looking unsure."),
    ("2", "CALLE", "CU", "", "Pijama deja pan en la puerta. Golpea dos veces. Y se va.",
     "{P} gently placing bread on the doorstep and knocking with two knuckles, kind but careful face."),
    ("2", "CALLE", "MS", "", "Desde la ventana, una nena le dice gracias.",
     "A little girl at a window waving softly at {P}, who waves back from the street, a warm small moment."),
    ("2", "CIUDAD_GRIS", "WS", "", "Día siete. Ya no es un vecino. Es la calle entera.",
     "Wide view down the street: every window shutter closed, white crosses painted on several doors, an empty street."),
    # ---------- DÍAS 8–11 ----------
    ("3", "ESTABLO", "CU", "SHAKE", "Día ocho. Te pica la pierna. Te pica mucho.",
     "Close-up of {P}'s leg with a tiny red dot, his hand scratching furiously, cartoon itch lines."),
    ("3", "ESTABLO", "CU", "", "No. No, no, no.",
     "{D} screaming in panic on {P}'s wrist, bells shaking, eyes popping."),
    ("3", "MEDICO", "WS", "", "Vas a ver a un médico. Esperas al tipo con máscara de pájaro.",
     "{P} entering the physician's study and imagining, in a thought bubble, a scary plague doctor with a long bird beak mask."),
    ("3", "MEDICO", "MS", "PUNCH", "Ese disfraz todavía no existe. Lo inventan en trescientos años. Llegaste temprano.",
     "{D} holding up a big red cartoon 'X' sign over the bird mask thought bubble, the real {M} standing there with a normal face and red cap."),
    ("3", "MEDICO", "MS", "", "El médico de 1348 tiene otra teoría: la culpa es del aire podrido.",
     "{M} pointing at green stinky cartoon clouds floating in the air, holding his nose dramatically."),
    ("3", "MEDICO", "LA", "", "Y de los planetas. Literal.",
     "{M} pointing up at a painted ceiling chart of Saturn, Jupiter and Mars lined up, with cartoon angry faces on the planets."),
    ("3", "MEDICO", "WS", "", "Los médicos más famosos de París escribieron que todo empezó por Saturno, Júpiter y Marte, juntos en el cielo.",
     "A serious group of medieval Paris professors in academic robes around a giant book, one pointing at three planets in a starry window."),
    ("3", "NEUTRO", "CU", "", "Bro le echó la culpa a Saturno.",
     "Saturn as a cartoon planet character with a shocked face, pointing at itself like 'who, me?'."),
    ("3", "MEDICO", "MS", "", "Los remedios: oler flores y hierbas.",
     "{M} pushing a huge bouquet of herbs and flowers into {P}'s face, {P} sneezing."),
    ("3", "MEDICO", "CU", "", "Lavarte con vinagre.",
     "{P} being splashed with vinegar from a clay jug, his face scrunched by the smell, green smell lines."),
    ("3", "MEDICO", "MS", "", "No dormir de día. Y sacarte sangre.",
     "{M} holding a small curved blade and a bowl, smiling too happily, {P} backing away."),
    ("3", "CALLE", "CU", "", "Algunos caminan con una naranja llena de clavos de olor pegada a la nariz.",
     "A medieval nobleman walking with an orange studded with cloves pressed to his nose, looking very proud."),
    ("3", "CALLE", "CU", "", "Desodorante de ambiente, versión 1348.",
     "{D} holding a tiny clove orange like an air freshener, winking."),
    ("3", "AVIGNON", "WS", "", "Al papa le recomendaron sentarse todo el día entre dos hogueras enormes.",
     "The old pope sitting on his chair between two gigantic bonfires, sweating buckets, fanning himself, servants adding more wood."),
    ("3", "AVIGNON", "CU", "", "Y sobrevivió. Pero de casualidad: a las pulgas no les gusta el calor.",
     "Close-up of tiny {F} with sunglasses running away from the fire, sweating, carrying a tiny suitcase."),
    ("3", "MEDICO", "MS", "", "Día nueve. El médico te ofrece la cura.",
     "{M} presenting two choices on a wooden table like a game show host, {P} sitting nervously."),
    ("3", "MEDICO", "CU", "", "A: te saca sangre con una cuchilla.",
     "Option A: a small blade and a copper bowl on the table, ominous candlelight."),
    ("3", "MEDICO", "CU", "", "B: te da un ramo de hierbas y una botella de vinagre.",
     "Option B: a bundle of herbs tied with string and a clay bottle of vinegar, soft green light."),
    ("3", "MEDICO", "MS", "", "La sangría te deja pálido, débil y con menos defensas.",
     "A pale weak medieval patient after a bloodletting, slumped in a chair, white as paper, a tiny battery icon empty above his head."),
    ("3", "MEDICO", "MS", "", "Pijama elige el vinagre. Huele a ensalada. Pero sigue entero.",
     "{P} walking out smelling of vinegar, flies avoiding him, a lettuce leaf stuck on his head, {D} laughing."),
    ("3", "ESTABLO", "EC", "", "Lo de la pierna era una pulga. Una sola. Del tamaño de una semilla de sésamo.",
     "Extreme close-up: a sesame seed next to {F} on {P}'s skin, the flea the same size as the seed, waving evilly."),
    ("3", "ESTABLO", "CU", "SHAKE", "Día once. Te sube la temperatura.",
     "{P} with a red face and a thermometer-like steam cloud above his head, one heart shattering into pieces above him."),
    ("3", "ESTABLO", "MS", "", "Pierdes una vida. Te quedan dos. Día once: igual que la última vez. Ahora no.",
     "{D} on {P}'s wrist looking serious and determined, two hearts left glowing, {P} clenching his fist."),
    # ---------- DÍAS 12–17 (serio) ----------
    ("4", "CIUDAD_GRIS", "LA", "", "Día doce. Las campanas dejaron de sonar.",
     "Low angle of a silent stone bell tower at dusk, a big bronze bell completely still, birds flying away."),
    ("4", "CIUDAD_GRIS", "MS", "", "Antes tocaban por cada muerto. Ahora las prohibieron.",
     "A town crier reading a decree in an empty square, a bell rope tied up with a knot, no people around. Serious tone."),
    ("4", "FOSA", "WS", "", "Ya no hay entierros de uno en uno. Hay fosas grandes.",
     "Very wide shot from far away of the burial trench at the edge of the city with rows of white linen-wrapped shapes, small and distant, cypress trees, gray sky. Respectful, no gore."),
    ("4", "FOSA", "WS", "", "Y se llenan por capas.",
     "Side silhouette view of the trench with neat layers of white cloth and earth, two tired gravediggers with shovels as dark silhouettes against a pale sky. Respectful, no gore."),
    ("4", "CIUDAD_GRIS", "MS", "", "Los que tienen dinero cierran sus casas y se van.",
     "A rich family loading a carriage with chests in a hurry, servants closing the heavy palace doors."),
    ("4", "CIUDAD_GRIS", "MS", "", "Muchos médicos se van. Los que se quedan son los que no tienen adónde ir.",
     "A poor old woman and a boy sitting on a doorstep watching a carriage leave the city gate."),
    ("4", "CIUDAD_GRIS", "WS", "", "En Siena, a cincuenta kilómetros, un hombre llamado Agnolo di Tura escribió…",
     "The medieval city of Siena on its hill at dusk, its tall striped bell tower, quiet and gray."),
    ("4", "CIUDAD_GRIS", "CU", "", "…que enterró a sus cinco hijos con sus propias manos.",
     "A medieval man seen from behind writing by candlelight at a wooden desk, a quill and parchment, his shoulders bent with grief. No faces of children, very respectful."),
    ("4", "CIUDAD_GRIS", "WS", "", "Y que nadie lloraba. Porque todos esperaban morir.",
     "A silent row of townspeople standing in the gray square, heads down, nobody crying, very still. Respectful."),
    ("4", "ESTABLO", "MS", "", "Acá no hay chiste.",
     "{D} on {P}'s wrist with his screen face dimmed, eyes closed, silent; {P} sitting with knees up in the dark stable."),
    ("4", "ESTABLO", "CU", "SHAKE", "Día quince. Fiebre. De la fuerte.",
     "{P} shivering violently under straw, red face, sweat drops flying, the infection meter idea shown as a green-red glowing aura around him."),
    ("4", "ESTABLO", "CU", "", "Ok. Ahora sí, no es broma.",
     "{D} looking at {P} with real worry, tiny hand on his shoulder."),
    ("4", "ESTABLO", "WS", "", "Pijama se tapa con paja en el establo. Tiembla. Dos días.",
     "Wide shot of the dark stable with only {P}'s face poking out of a hay pile, the horse standing guard next to him."),
    ("4", "ESTABLO", "CU", "", "No come. Toma vino aguado. Y se revisa las axilas cada hora.",
     "{P} nervously lifting his arm to check his armpit with a small candle, eyes squinting."),
    ("4", "ESTABLO", "MS", "", "Día diecisiete. La fiebre baja. Y no hay ningún bulto.",
     "Morning light entering the stable, {P} sitting up weak but relieved, wiping his forehead."),
    ("4", "ESTABLO", "CU", "SHAKE", "Te queda una vida. Una.",
     "Close-up of a single glowing red heart floating above {P}, the other two hearts broken and gray beside it."),
    # ---------- DÍAS 18–21 ----------
    ("5", "PLAZA", "WS", "", "Día dieciocho. En la plaza, unos chicos ricos hablan bajito.",
     "Wide shot of the piazza with the ten young nobles whispering in a group, {P} hiding behind the fountain listening."),
    ("5", "PLAZA", "MS", "", "Son diez. Se van al campo, a una villa en las colinas.",
     "The young nobles pointing toward the hills in the distance, servants loading mules with baskets and lutes."),
    ("5", "PLAZA", "CU", "", "Van a pasar los días contando cuentos.",
     "One young woman telling a story with big hand gestures while the others laugh, a thought bubble with a little knight and a donkey."),
    ("5", "CALLE", "MS", "", "Un escritor de esta misma ciudad, Boccaccio, lo usó para su libro más famoso: el Decamerón.",
     "A chubby medieval writer with a quill (Boccaccio) at his desk surrounded by piles of paper, winking at the viewer."),
    ("5", "VILLA", "WS", "", "Diez jóvenes. Diez días. Cien cuentos. Mientras Florencia se moría.",
     "Split by distance in one image: the bright sunny villa on a hill in the front and gray smoky Florence far below in the valley."),
    ("5", "VILLA", "CU", "", "Básicamente, el primer grupo de amigos que se fue de vacaciones en una pandemia.",
     "{D} wearing tiny sunglasses and holding a tiny lute, the young nobles posing like a vacation group photo behind him."),
    ("5", "ESTABLO", "WS", "", "A: te quedas en tu establo, que ya conoces.",
     "Option A: the gray stable in the gray city, a rat looking out of the hay."),
    ("5", "CAMINO", "WS", "", "B: los sigues al campo, sin saber si te van a dejar entrar.",
     "Option B: the sunny road into the green hills, a far villa on top, uncertain but bright."),
    ("5", "CAMINO", "WS", "", "Huir era lo que hacía el que podía. Y era lo que mejor funcionaba.",
     "A long line of people with carts and mules leaving the city gate toward the hills."),
    ("5", "CAMINO", "MS", "", "Pijama los sigue. Descalzo. Por el camino.",
     "{P} walking barefoot on the dusty road behind the nobles' mule caravan, keeping a careful distance."),
    ("5", "CAMINO", "WS", "", "Treinta kilómetros de colinas, olivos y cipreses.",
     "Beautiful wide Tuscan landscape, the tiny caravan and tiny {P} crossing golden hills between cypress lines."),
    ("5", "CAMINO", "WS", "", "Día veinte. Se cruzan con algo raro.",
     "{P} stopping suddenly on the road, hand up, as a strange procession appears over the hill."),
    ("5", "CAMINO", "WS", "", "Una fila de hombres sin camisa que se golpean la espalda con látigos.",
     "A procession of medieval penitents in white hoods walking in line on the road carrying a cross and small whips, seen from a distance, stylized and not gory."),
    ("5", "CAMINO", "MS", "", "Cantan. Rezan. Van de pueblo en pueblo.",
     "The penitents singing with mouths open, villagers watching from a doorway, stylized, no blood."),
    ("5", "CAMINO", "CU", "", "Pero con ellos, de pueblo en pueblo… viaja la peste.",
     "Close-up of a penitent's hood with tiny {F} riding on top of it, grinning."),
    ("5", "CAMINO", "CU", "PUNCH", "Bro. No te sumes a la fila.",
     "{D} holding {P} back by his pajama collar with both tiny arms, shaking his head."),
    ("5", "CAMINO", "MS", "", "Pijama se esconde detrás de un ciprés hasta que pasan.",
     "{P} hiding behind a very thin cypress tree, obviously still visible on both sides, holding his breath."),
    # ---------- DÍAS 22–27 ----------
    ("6", "VILLA", "WS", "", "Día veintidós. Llegas a la villa.",
     "Wide shot of {P} arriving at the villa gate, dusty and tired, the nobles looking at him from the garden."),
    ("6", "VILLA", "CU", "", "Te dejan pasar porque creen que el pijama es de seda.",
     "A young noblewoman touching {P}'s pajama sleeve with amazement, sparkles on the fabric, {P} playing along with a fancy pose."),
    ("6", "VILLA", "MS", "", "Primera vez en tres videos que el pijama sirve para algo. Aura: más quinientos.",
     "{D} throwing golden confetti, {P} doing a proud pose in the garden."),
    ("6", "VILLA", "WS", "", "Pan blanco. Aire limpio. Agua de pozo.",
     "The long table under the pergola full of white bread, grapes, figs and cheese, {P} sitting with huge happy eyes."),
    ("6", "VILLA", "MS", "", "Y diez chicos contando cuentos todo el día.",
     "The young nobles sitting in a circle on the grass telling stories, one playing a lute, {P} listening with a cup."),
    ("6", "VILLA", "CU", "", "Algunos son tan picantes que la Iglesia los prohibió durante siglos.",
     "A medieval monk covering his eyes with both hands while reading a book, very red face."),
    ("6", "VILLA", "CU", "", "No los vamos a leer. Tenemos anunciantes.",
     "{D} slamming a book shut with a tiny 'censored' black bar shape over it (no letters)."),
    ("6", "VILLA", "MS", "SHAKE", "Día veinticinco. Uno de los criados tose.",
     "A servant carrying a tray coughs into his elbow, everyone at the table freezes mid-bite."),
    ("6", "VILLA", "WS", "", "La villa entera se queda callada.",
     "Wide frozen moment: all the nobles staring at the servant, a dark cloud shadow passing over the sunny garden."),
    ("6", "VILLA", "WS", "", "A: te quedas en la villa, con comida y con gente.",
     "Option A: the villa table full of food and people, but a dark cloud above."),
    ("6", "CHOZA", "WS", "", "B: te vas solo a una choza del bosque, hasta el día treinta.",
     "Option B: the lonely wooden hut in the misty pine forest, quiet and safe."),
    ("6", "CAMINO", "MS", "", "Pijama se va. Solo. Con pan, vinagre y su pijama de seda.",
     "{P} walking into the forest with a loaf of bread under one arm and a vinegar bottle in the other hand, determined."),
    ("6", "RAGUSA", "WS", "GAME", "En 1377, la ciudad de Ragusa, en la costa de Croacia, inventó una regla nueva.",
     "Wide establishing shot of medieval Ragusa: stone walls, a busy harbor with wooden ships, deep blue Adriatic sea."),
    ("6", "RAGUSA", "MS", "", "El que llegaba de un lugar con peste tenía que esperar aislado treinta días antes de entrar.",
     "Sailors waiting on a small island hut outside the city, a guard at the gate holding up his hand, a big sand hourglass next to them."),
    ("6", "RAGUSA", "CU", "", "Lo llamaron trentino. Treinta días.",
     "A city official in a fancy hat stamping a big wax seal on a parchment decree (no readable text)."),
    ("6", "RAGUSA", "MS", "", "Después lo subieron a cuarenta. En italiano, cuarenta se dice quaranta.",
     "A Venetian official adding ten more marks to a tally on a wall with a smug face, sailors groaning."),
    ("6", "RAGUSA", "CU", "PUNCH", "De ahí viene la palabra cuarentena.",
     "{P} with a mind-blown face, cartoon explosion stars around his head."),
    ("6", "CHOZA", "CU", "", "O sea que este juego… era una cuarentena. Te engañé. De nada.",
     "{D} bowing like a magician with a tiny top hat, {P} pointing at him in disbelief."),
    # ---------- DÍAS 28–30 ----------
    ("7", "CHOZA", "WS", "", "Día veintiocho.",
     "{P} sitting by a tiny campfire outside the hut at night, stars, calm."),
    ("7", "CHOZA", "MS", "", "Día veintinueve.",
     "{P} carving marks on the hut door with a stone, many marks, almost done."),
    ("7", "CHOZA", "WS", "FLASH", "Día treinta. Abres la puerta. Sale el sol. Sigues vivo.",
     "{P} opening the hut door to a glorious pink-gold sunrise over the forest, arms wide open, birds flying."),
    ("7", "CHOZA", "MS", "", "Treinta días. Una vida. Una pulga. Y cero bultos.",
     "{P} proudly holding up one finger, a tiny defeated {F} lying on its back on a leaf, one glowing heart above {P}."),
    ("7", "CHOZA", "LA", "GAME", "Logro desbloqueado: sobrevivir treinta días a la peste negra. En pijama.",
     "Low angle of {P} raising a golden trophy shaped like a pillow, {D} ringing his bells with joy, golden light rays."),
    ("7", "CHOZA", "CU", "", "Aura: más mil trescientos cuarenta y ocho.",
     "{D} exploding with golden sparkles and fireworks around him, eyes as stars."),
    ("7", "CAMINO", "WS", "", "Murió tanta gente que faltaban manos para trabajar.",
     "Empty wheat fields with no workers, abandoned tools and a lonely scarecrow, a worried landlord looking around."),
    ("7", "CAMINO", "MS", "", "Los que quedaron empezaron a pedir más sueldo.",
     "A group of peasants with crossed arms facing a nervous landlord holding a small bag of coins."),
    ("7", "CAMINO", "CU", "", "En algunos lugares, el sueldo de un trabajador casi se duplicó.",
     "A peasant's open hand receiving double the coins, his eyes sparkling."),
    ("7", "CAMINO", "MS", "", "Sobreviviste y te subieron el sueldo. Mejor final imposible.",
     "{P} in his pajamas holding a scythe and a bag of coins, giving a thumbs up, {D} dancing."),
    # ---------- RESULTADOS ----------
    ("R", "NEUTRO", "WS", "GAME", "Tus resultados.",
     "{P} and {D} standing in front of a big empty scoreboard frame drawn as a medieval wooden board with five empty rows (no text)."),
    ("R", "NEUTRO", "MS", "", "¿Cuántas acertaste tú? Escríbelo en los comentarios.",
     "{D} pointing at the viewer with a tiny quill, {P} holding up five fingers proudly."),
    ("R", "NEUTRO", "WS", "", "Y elige la próxima partida: la Roma de los gladiadores, la Edad de Hielo… o un barco pirata.",
     "Three glowing doors side by side: one with a Roman colosseum behind it, one with snowy mountains and a mammoth, one with a pirate ship on the sea; {P} in front choosing."),
    ("R", "NEUTRO", "CU", "", "Y no: todavía no puedes apagarme.",
     "{D} grinning straight at the viewer, bells ringing, close and cheeky."),
    # ---------- SHORTS (verticales) ----------
    ("S", "CALLEJON", "LA", "FLASH", "SHORT 0 · Florencia. Abril de 1348. Día uno.",
     "{P} waking up on the stone ground of a narrow medieval alley, looking up at tall houses, {D} on his wrist grinning."),
    ("S", "MERCADO", "MS", "", "SHORT 1 · Tu primer enemigo no es la peste. Es el hambre.",
     "{P} holding his growling stomach in front of a bread stall in the medieval market."),
    ("S", "CALLE", "MS", "", "SHORT 2 · Un vecino de la calle no abre la ventana.",
     "A closed green shutter high on a stone house, {P} looking up from below, worried."),
    ("S", "ESTABLO", "CU", "", "SHORT 3 · Te pica la pierna. Te pica mucho.",
     "{P} scratching his leg furiously, a tiny {F} on his skin grinning."),
    ("S", "CIUDAD_GRIS", "LA", "", "SHORT 4 · Las campanas dejaron de sonar.",
     "A silent bell tower at dusk in gray Florence, the bell still, birds leaving. Serious."),
    ("S", "PLAZA", "MS", "", "SHORT 5 · Diez chicos ricos se van al campo a contar cuentos.",
     "Ten young nobles with mules and lutes leaving the piazza toward the hills, {P} watching from behind the fountain."),
    ("S", "VILLA", "MS", "", "SHORT 6 · Te dejan pasar porque creen que el pijama es de seda.",
     "A noblewoman touching {P}'s sparkling pajama sleeve in amazement in a sunny villa garden."),
    ("S", "CHOZA", "LA", "", "SHORT 7 · Día treinta.",
     "{P} opening a forest hut door to a golden sunrise, arms wide open."),
    ("S", "NEUTRO", "MS", "", "SHORT 8 · Cinco decisiones. ¿Cuántas acertaste?",
     "{P} and {D} in front of a wooden scoreboard with five empty rows, {P} holding up five fingers."),
]


def slug(s, n=4):
    w = re.sub(r"[^a-z0-9 ]", "", s.lower().replace("ñ", "n").translate(str.maketrans("áéíóú", "aeiou"))).split()
    return "_".join(w[:n])


def main():
    imgs = []
    for i, (b, lugar, cam, tr, quote, scene) in enumerate(E, 1):
        idx = f"{i:03d}"
        short = b == "S"
        hoja = b == "X"
        txt = scene.format(**PERSONAJES)
        partes = [ESTILO_SHORT if short else ESTILO]
        if not hoja:
            partes.append(f"SETTING (where this happens): {LUGARES[lugar]} {PALETAS[b]}".strip())
        partes.append(f"SCENE: {txt}")
        if not hoja:
            partes.append(f"Camera: {CAMS[cam]}.")
        nota = " · ".join(x for x in [f"Lugar: {lugar}" if not hoja else "", f"Cámara: {CAMS[cam]}", TRS[tr] and f"Transición: {TRS[tr]}"] if x)
        imgs.append({"id": idx, "file": f"{idx}_{b.lower()}_{slug(scene)}.png", "tipo": "hoja" if hoja else ("short" if short else "imagen"),
                     "block": b, "quote": quote, "cam": cam, "tr": tr, "lugar": lugar, "nota": nota, "overlay": "",
                     "prompt": " ".join(partes)})
    man = {"estilo": ESTILO, "estilo_short": ESTILO_SHORT, "personajes": PERSONAJES, "paletas": PALETAS, "imagenes": imgs}
    (DOCS / "manifest_imagenes_v3.json").write_text(json.dumps(man, ensure_ascii=False, indent=1))
    # página de prompts: misma plantilla que la del video 2, con los datos nuevos
    tpl = (V.parent / "video2" / "docs" / "prompts_pijama_botones.html").read_text()
    datos = [{k: d[k] for k in ("id", "file", "tipo", "block", "quote", "nota", "overlay", "prompt")} for d in imgs]
    nombres = {"X": "HOJAS", "S": "SHORTS", "H": "GANCHO", "R": "FINAL", "1": "DÍAS 1–3", "2": "DÍAS 4–7", "3": "DÍAS 8–11",
               "4": "DÍAS 12–17", "5": "DÍAS 18–21", "6": "DÍAS 22–27", "7": "DÍAS 28–30"}
    for d in datos:
        d["block"] = nombres[d["block"]]
    html = re.sub(r"var DATA = \[.*?\];\n", lambda m: "var DATA = " + json.dumps(datos, ensure_ascii=False) + ";\n", tpl, count=1, flags=re.S)
    html = html.replace("Prompts · Te despiertas en pijama en 8 épocas", "Prompts video 3 · 30 días en la peste negra")
    html = html.replace("prompts-pijama-8-epocas-v1", "prompts-pijama-peste-30-v1")
    html = html.replace("<b>Empieza por las hojas (001 a 007)</b> y súbelas como referencia en todas las demás.",
                        "<b>Empieza por las hojas (001 a 004).</b> Si guardaste las de Pijama y el Despertador del video 2, usá esas y generá solo la Pulga (003) y el médico (004). Súbelas como referencia en todas las demás.")
    (DOCS / "prompts_video3.html").write_text(html)
    from collections import Counter
    print(len(imgs), "imágenes", dict(Counter(d["tipo"] for d in imgs)))


if __name__ == "__main__":
    main()
