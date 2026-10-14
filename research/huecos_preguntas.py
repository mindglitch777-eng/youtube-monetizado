#!/usr/bin/env python3
"""
Las 30 preguntas candidatas (ronda 2, octubre 2026) + cálculo de puntaje.
El contenido de cada pregunta (títulos, gancho, bloques, fuentes) es redacción
propia; la evidencia numérica sale de research/data/ (API de YouTube).
Genera research/data/huecos-2026-10/preguntas.csv y preguntas.json.
"""
import csv
import gzip
import json
import math
from pathlib import Path

D = Path(__file__).parent / "data"
OUT = D / "huecos-2026-10"

# ---------- índice de videos/canales ya bajados (costo 0) ----------
OUTL = {x["video_id"]: x for x in json.loads((D / "nichos-2026-10/outliers.json").read_text())}
CH = json.load(gzip.open(D / "nichos-2026-10/canales.json.gz", "rt"))
CH.update(json.loads((OUT / "canales.json").read_text()))
VID = {}
for k, x in json.load(gzip.open(D / "nichos-2026-10/videos_busqueda.json.gz", "rt")).items():
    VID[k] = (x["snippet"]["title"], int(x["statistics"].get("viewCount", 0)), x["snippet"]["channelId"], x["snippet"]["channelTitle"])
for k, x in json.loads((OUT / "videos.json").read_text()).items():
    VID[k] = (x["snippet"]["title"], int(x["statistics"].get("viewCount", 0)), x["snippet"]["channelId"], x["snippet"]["channelTitle"])
for k, x in json.load(gzip.open(D / "nichos-2026-10/videos_canales_resumen.json.gz", "rt")).items():
    if k not in VID:
        VID[k] = (x["title"], int(x.get("viewCount") or 0), x["channelId"], "")


def analogo(vid):
    t, v, cid, cname = VID[vid]
    ch = CH.get(cid, {})
    return {"video_id": vid, "titulo": t, "vistas": v, "canal": cname or ch.get("snippet", {}).get("title", ""),
            "subs": int(ch.get("statistics", {}).get("subscriberCount", 0) or 0),
            "canal_creado": ch.get("snippet", {}).get("publishedAt", "")[:10],
            "factor_outlier": OUTL.get(vid, {}).get("factor_outlier")}


# ---------- las 30 preguntas ----------
# es_50k: videos largos en español con ≥50k vistas sobre ESE ángulo (medido en búsquedas/títulos guardados)
# copiado: True si ya hay una traducción de un éxito en inglés sobre el mismo ángulo
# original: 0-20 (OPINIÓN) qué tan nuevo es el ángulo y cuánto le habla al público hispano
# riesgo_pen: 0, 5 o 10 (OPINIÓN)
Q = [
 dict(n=1, tema="frío", titulo="Si afuera hacía −40 °C, ¿por qué no se iban al sur?",
      alt=["El error que todos cometen sobre la Edad de Hielo: ¿por qué se quedaban en el frío?", "¿Por qué los humanos de hace 30.000 años eligieron vivir en el hielo?"],
      analogo="0tSwA12rEtk", es_50k=0, copiado=False, original=17,
      es_txt="Tema frío: 37 videos largos en ES y 11 con ≥50k, pero todos sobre 'cómo dormían/sobrevivían'. Ninguno sobre por qué no migraban. La pregunta aparece 2 veces en comentarios ('why not just move southward???', '¿os pensáis que eran tontos?').",
      gancho="Imagina que vives en una estepa a 40 grados bajo cero y que a mil kilómetros al sur hay bosques templados, a dos meses de caminata. Tus antepasados no se fueron. No eran tontos: tenían una razón más inteligente que cualquier plan que se te ocurra.",
      bloques=["¿Hacía tanto frío todo el año o solo en invierno?", "¿Qué había en la estepa que no había en el bosque? (mamuts, renos, comida concentrada)", "¿Por qué el sur ya estaba 'ocupado'?", "¿Cuánto costaba mudar a un grupo entero con niños y ancianos?", "¿Se movían de verdad? Migraciones de temporada que sí hacían", "Veredicto: ¿te habrías quedado?"],
      fuentes=["Hoffecker, J. (2005). A Prehistory of the North: Human Settlement of the Higher Latitudes. Rutgers University Press.", "Pidoplichko, I. (1998). Upper Palaeolithic Dwellings of Mammoth Bones in the Ukraine. BAR. (verificar edición)", "Pitulko, V. et al. (2004). The Yana RHS site: humans in the Arctic before the Last Glacial Maximum. Science 303."],
      riesgo="Bajo. Imágenes de recreación, no simular fotos.", riesgo_pen=0),
 dict(n=2, tema="higiene", titulo="Seis meses encerrados en una cueva: ¿dónde hacían sus necesidades?",
      alt=["El problema más incómodo de la Edad de Hielo (y cómo lo resolvieron)", "¿Qué hacían con la caca cuando nevaba durante meses?"],
      analogo="aNDI_PNJwO0", es_50k=0, copiado=False, original=16,
      es_txt="Higiene/baño en ES: 5 videos largos, ninguno ≥50k. En títulos guardados con 'caca/letrina/heces' en ES: 0 sobre prehistoria. Preguntas reales en comentarios: '¿Qué hacían con los desechos?' y la de la diarrea en el iglú.",
      gancho="Es pleno invierno, hace semanas que nieva y tú vives con otras veinte personas dentro de una cueva de la que nadie puede salir. Ahora piensa en lo que ningún documental te cuenta: ¿adónde iba todo eso? La arqueología tiene la respuesta, y está literalmente en el suelo.",
      bloques=["¿Por qué los coprolitos son un tesoro para los científicos?", "¿Había un 'rincón baño' dentro del campamento?", "¿Cómo evitaban enfermarse por sus propios desechos?", "¿Qué hacían los inuit dentro de un iglú?", "¿Qué usaban en lugar de papel?", "Veredicto: ¿eran más limpios de lo que crees?"],
      fuentes=["Gilbert, M. T. P. et al. (2008). DNA from pre-Clovis human coprolites in Oregon, North America. Science 320.", "Sistiaga, A. et al. (2014). The Neanderthal meal: a new perspective using faecal biomarkers. PLoS ONE 9(6).", "Reinhard, K. (verificar obra exacta sobre paleoescatología)."],
      riesgo="Bajo-medio: tema escatológico; mantener tono educativo para no perder anunciantes.", riesgo_pen=0),
 dict(n=3, tema="fuego/leña", titulo="¿De dónde sacaban leña para cinco meses de invierno sin un hacha de metal?",
      alt=["Sin árboles y a −30 °C: ¿qué quemaban para no morir congelados?", "Quemaban huesos de mamut: el combustible secreto de la Edad de Hielo"],
      analogo="bG2ZcmBQHTA", es_50k=0, copiado=False, original=18,
      es_txt="Fuego en ES: 4 videos largos, ninguno ≥50k (máximo 25k). Títulos con 'leña': 0 en 51.881 títulos guardados. Pregunta textual en comentarios de CAVERNICOLAS: '¿De dónde sacaban tanta leña para tantos meses?'.",
      gancho="Imagina que tienes que pasar cinco meses de invierno en la estepa, donde casi no hay árboles y no existe el hacha de metal. Si se te apaga el fuego, te mueres. Entonces, ¿qué quemas para seguir vivo?",
      bloques=["¿Cuánta madera necesitaba de verdad un campamento por día?", "¿Cómo cortaban árboles con piedra?", "¿Se puede quemar hueso? Las casas de mamut de Mezhyrich", "Grasa y lámparas: fuego sin leña", "¿Cómo mantenían brasas vivas durante días?", "Veredicto: ¿cuánto durarías tú sin encendedor?"],
      fuentes=["Théry-Parisot, I. (2001). Économie des combustibles au Paléolithique. CNRS Éditions. (verificar)", "Wrangham, R. (2009). Catching Fire: How Cooking Made Us Human. Basic Books.", "Soffer, O. (1985). The Upper Paleolithic of the Central Russian Plain. Academic Press."],
      riesgo="Bajo.", riesgo_pen=0),
 dict(n=4, tema="sueño", titulo="Tus antepasados se despertaban a las 2 de la mañana a propósito",
      alt=["El 'primer sueño' y el 'segundo sueño': cómo dormía la humanidad hasta hace 200 años", "Si te despiertas de madrugada, quizás no estás enfermo: el sueño en dos partes"],
      analogo="J4W6AhaRcqA", es_50k=0, copiado=False, original=14,
      es_txt="Sueño es el tema más saturado en ES (34 largos, 14 ≥50k) PERO ninguno en ES sobre el sueño en dos partes. En EN solo hay un Short (1,5M). El comentario con más likes sobre sueño en Ink Explainer (39): 'siempre me despierto después de 4 horas'.",
      gancho="Son las dos de la mañana, te despiertas sin motivo y piensas que algo anda mal. Hace trescientos años eso era tan normal que tenía nombre: el final de tu 'primer sueño'. Y lo que la gente hacía en esa hora despierta te va a sorprender.",
      bloques=["¿Qué descubrió un historiador leyendo diarios y juicios antiguos?", "¿Qué hacían durante la hora despiertos?", "¿Por qué desapareció? La luz artificial", "¿Los cazadores-recolectores actuales duermen así? (el estudio que dice que no)", "¿Deberías dormir en dos partes tú?", "Veredicto: el sueño 'normal' es más moderno de lo que crees"],
      fuentes=["Ekirch, A. R. (2005). At Day's Close: Night in Times Past. W. W. Norton.", "Ekirch, A. R. (2001). Sleep We Have Lost: Pre-industrial Slumber in the British Isles. American Historical Review 106(2).", "Yetish, G. et al. (2015). Natural sleep and its seasonal variations in three pre-industrial societies. Current Biology 25(21)."],
      riesgo="Bajo. Evitar consejos médicos.", riesgo_pen=0),
 dict(n=5, tema="agua", titulo="¿Cómo tomaban agua de un charco sin morir de diarrea?",
      alt=["Sin filtros ni hervir: el agua que bebían hace 20.000 años", "¿Por qué el agua mataba más que los leones?"],
      analogo="OaV16iSA51Y", es_50k=0, copiado=False, original=13,
      es_txt="Agua en ES: 9 videos largos, ninguno ≥50k (máximo 11.872, Mango Explica). Hay varias copias de canales de <200 subs con ese mismo ángulo y casi cero vistas. En PT el análogo tiene 374k.",
      gancho="Tienes sed, y el único agua es un charco donde también toman los animales, sin ollas para hervirla ni filtros. Tu cuerpo moderno se enfermaría en un día. Ellos lo hacían todos los días, y sobrevivían.",
      bloques=["¿Qué tan peligrosa era el agua sin tratar?", "¿Elegían el agua? Manantiales, nieve y la regla del agua que corre", "¿Su estómago era distinto al tuyo?", "¿Cuándo empezaron a hervir agua? (la cerámica llegó tarde)", "¿Cuántos morían por el agua?", "Veredicto: ¿tomarías de ese charco?"],
      fuentes=["Lee, R. B. (1979). The !Kung San: Men, Women and Work in a Foraging Society. Cambridge University Press.", "Gurven, M. & Kaplan, H. (2007). Longevity among hunter-gatherers: a cross-cultural examination. Population and Development Review 33(2).", "Barrett, R. et al. (1998). Emerging and re-emerging infectious diseases: the third epidemiologic transition. Annual Review of Anthropology 27."],
      riesgo="Medio: el ángulo ya está muy copiado por canales chicos. Diferenciarse con datos.", riesgo_pen=0),
 dict(n=6, tema="medicina", titulo="Si te cortabas hace 30.000 años, ¿te morías de infección?",
      alt=["Antibióticos de la Edad de Piedra: lo que masticaban los neandertales", "Una herida, cero médicos: así sobrevivían"],
      analogo="7MgqNR8oxSU", es_50k=0, copiado=False, original=15,
      es_txt="Medicina en ES: 2 videos largos encontrados, máximo 749 vistas. Pregunta textual en Homo Curioso: 'te cortabas con algo y si se infectaba la herida en una semana te morías'.",
      gancho="Te haces un corte profundo en la pierna cazando, y no hay alcohol, ni antibióticos, ni puntos. Hace treinta mil años eso podía ser una sentencia de muerte. Pero los huesos curados que encontramos dicen otra cosa.",
      bloques=["¿Cuántos esqueletos muestran heridas curadas?", "¿Qué plantas usaban? El sarro de los neandertales de El Sidrón", "¿Sabían limpiar heridas?", "¿Quién cuidaba a los heridos?", "¿De qué se moría realmente la gente?", "Veredicto: ¿habrías sobrevivido a ese corte?"],
      fuentes=["Weyrich, L. et al. (2017). Neanderthal behaviour, diet, and disease inferred from ancient DNA in dental calculus. Nature 544.", "Gurven, M. & Kaplan, H. (2007). Longevity among hunter-gatherers. Population and Development Review 33(2).", "Berger, T. & Trinkaus, E. (1995). Patterns of trauma among the Neandertals. Journal of Archaeological Science 22."],
      riesgo="Bajo. No dar consejos médicos actuales.", riesgo_pen=0),
 dict(n=7, tema="medicina/cuidado", titulo="Sin un brazo, casi ciego y sordo, este neandertal sobrevivió años: ¿quién lo cuidó?",
      alt=["Shanidar 1: la prueba de que los neandertales no abandonaban a los suyos", "Sordo, ciego de un ojo y sin brazo: el neandertal que nadie dejó atrás"],
      analogo="7MgqNR8oxSU", es_50k=0, copiado=False, original=19,
      es_txt="'Shanidar' aparece 0 veces en 51.881 títulos guardados. Análogo lejano (salud en el pasado).",
      gancho="Imagina que pierdes un brazo y quedas casi ciego y medio sordo, en un mundo donde todos tienen que cazar para comer. Lo lógico sería que no duraras ni un invierno. Hace unos 50.000 años, un neandertal vivió así durante años, porque alguien decidió que valía la pena.",
      bloques=["¿Qué encontraron en la cueva de Shanidar?", "¿Qué le pasó a su cuerpo?", "¿Cómo sabemos que vivió años después de las heridas?", "¿Hay otros casos? (el niño de Romito)", "¿Era compasión o conveniencia?", "Veredicto: ¿qué dice esto de nosotros?"],
      fuentes=["Solecki, R. (1971). Shanidar: The First Flower People. Knopf.", "Trinkaus, E. (1983). The Shanidar Neandertals. Academic Press.", "Tilley, L. (2015). Theory and Practice in the Bioarchaeology of Care. Springer."],
      riesgo="Bajo.", riesgo_pen=0),
 dict(n=8, tema="dientes", titulo="Dentistas hace 9.000 años: el taladro de piedra que encontraron en Pakistán",
      alt=["¿Tenían caries los humanos antiguos? (y quién se las arreglaba)", "Les hacían agujeros en las muelas sin anestesia: los primeros dentistas"],
      analogo="yeOn5CtPbpQ", es_50k=0, copiado=False, original=17,
      es_txt="Dientes en ES: 8 videos largos, ninguno ≥50k (máximo 2.463). Pero el Short en ES '¿Cómo se lavaban los dientes ANTES de la pasta?' tiene 589k: hay demanda en ES, falta el video largo bueno. Ojo: ese Short es de un canal grande (5,5M).",
      gancho="Abre la boca: si tienes una caries, alguien con anestesia y un taladro eléctrico la arregla en media hora. Hace nueve mil años, en lo que hoy es Pakistán, alguien hizo un agujero perfecto en la muela de una persona viva. Con una piedra.",
      bloques=["¿Tenían caries los cazadores-recolectores?", "¿Por qué la agricultura arruinó los dientes?", "¿Qué encontraron en Mehrgarh?", "¿Cómo se limpiaban la boca? (palillos y surcos en los dientes)", "¿Dolía? ¿Usaban algo para el dolor?", "Veredicto: ¿confiarías en ese dentista?"],
      fuentes=["Coppa, A. et al. (2006). Early Neolithic tradition of dentistry. Nature 440.", "Cohen, M. N. & Armelagos, G. (eds.) (1984). Paleopathology at the Origins of Agriculture. Academic Press.", "Adler, C. et al. (2013). Sequencing ancient calcified dental plaque shows changes in oral microbiota with dietary shifts. Nature Genetics 45."],
      riesgo="Bajo.", riesgo_pen=0),
 dict(n=9, tema="niños", titulo="¿Con qué jugaban los niños hace 30.000 años?",
      alt=["Los juguetes más antiguos del mundo (y las huellas de niños en las cuevas)", "Ser niño en la Edad de Hielo: juegos, tareas y miedos"],
      analogo="zK2jFCC3BhA", es_50k=0, copiado=False, original=15,
      es_txt="Niños/juguetes prehistóricos en ES: 0 videos largos encontrados (los títulos con 'juguetes' son unboxing infantiles). Análogo: el video de placer de Stickstory (914k), que tiene un bloque sobre niños.",
      gancho="Piensa en tu juguete favorito de cuando eras chico. Ahora imagina a un niño de seis años en una cueva de Francia, hace treinta mil años, dejando las marcas de sus dedos en el techo. No estaba trabajando: estaba jugando.",
      bloques=["¿Cómo se sabe que había niños en las cuevas? Huellas y dedos", "¿Qué juguetes sobrevivieron?", "¿A qué edad empezaban a trabajar?", "¿Aprendían jugando? (lanzas chiquitas y muñecos)", "¿Qué les daba miedo?", "Veredicto: ¿la infancia era mejor o peor que la tuya?"],
      fuentes=["Nowell, A. (2021). Growing Up in the Ice Age. Oxbow Books.", "Lancy, D. (2008). The Anthropology of Childhood: Cherubs, Chattel, Changelings. Cambridge University Press.", "Sharpe, K. & Van Gelder, L. (2006). Evidence for cave marking by Palaeolithic children. Antiquity 80. (verificar)"],
      riesgo="Bajo. No mostrar violencia contra niños.", riesgo_pen=0),
 dict(n=10, tema="depredadores", titulo="¿Qué animal mataba más humanos en la Edad de Hielo? (no es el que piensas)",
      alt=["Durante millones de años fuimos presa: los animales que nos cazaban", "Ni el mamut ni el oso: el verdadero asesino de humanos prehistóricos"],
      analogo="ZNTUDh6MDdk", es_50k=1, copiado=False, original=12,
      es_txt="Depredadores en ES: 24 videos largos, 1 con ≥50k (Pepe Explica, 236k, ángulo distinto: 'por qué nosotros dábamos miedo'). El análogo en EN tiene x300 sobre su canal.",
      gancho="Si te pregunto qué animal mataba más humanos hace cien mil años, vas a decir el tigre dientes de sable o el oso de las cavernas. Casi todos dicen lo mismo. Pero los huesos encontrados en cuevas cuentan otra historia, y el verdadero cazador de humanos era mucho más silencioso.",
      bloques=["¿Cómo se sabe qué animal mordió un hueso?", "¿Leopardos, hienas o felinos gigantes?", "¿Por qué los niños eran el blanco?", "¿Cuándo dejamos de ser presa?", "¿Y las enfermedades? El asesino invisible", "Veredicto: ¿habrías sobrevivido a una noche afuera?"],
      fuentes=["Brain, C. K. (1981). The Hunters or the Hunted? An Introduction to African Cave Taphonomy. University of Chicago Press.", "Hart, D. & Sussman, R. (2005). Man the Hunted: Primates, Predators, and Human Evolution. Westview Press.", "Berger, L. & McGraw, W. S. (2006). Further evidence for eagle predation of, and feeding damage on, the Taung child. South African Journal of Science 102."],
      riesgo="Bajo-medio: evitar imágenes gore de ataques.", riesgo_pen=0),
 dict(n=11, tema="depredadores", titulo="Hace 2,8 millones de años un águila se llevó a un niño: la prueba está en su cráneo",
      alt=["El niño de Taung: la pista de un crimen de 3 millones de años", "Los ojos del cráneo tenían marcas de garras: el caso del niño de Taung"],
      analogo="ZNTUDh6MDdk", es_50k=0, copiado=False, original=19,
      es_txt="'Taung' aparece 0 veces en 51.881 títulos guardados. Comparte análogo con la pregunta 10.",
      gancho="Imagina que tienes tres años y juegas al borde de un bosque en Sudáfrica, hace casi tres millones de años. No ves venir al águila. Lo sabemos porque tu cráneo, encontrado en 1924, todavía tiene las marcas de sus garras en los ojos.",
      bloques=["¿Quién era el niño de Taung y por qué cambió la ciencia?", "¿Qué tenían de raro los huesos encontrados junto a él?", "¿Qué marcas dejan las águilas hoy?", "¿Un águila puede levantar a un niño? (los números)", "¿Qué otros 'crímenes' resolvió la paleontología?", "Veredicto: el cielo también era peligroso"],
      fuentes=["Berger, L. & Clarke, R. (1995). Eagle involvement in accumulation of the Taung child fauna. Journal of Human Evolution 29.", "Berger, L. & McGraw, W. S. (2006). Further evidence for eagle predation of, and feeding damage on, the Taung child. South African Journal of Science 102.", "Dart, R. (1925). Australopithecus africanus: the man-ape of South Africa. Nature 115."],
      riesgo="Medio: no mostrar al niño siendo atacado; usar diagramas del cráneo.", riesgo_pen=5),
 dict(n=12, tema="violencia", titulo="El asesinato más antiguo del mundo ocurrió en España hace 430.000 años",
      alt=["Cráneo 17 de Atapuerca: el primer caso policial de la humanidad", "Dos golpes en la frente: el crimen que resolvió la ciencia forense"],
      analogo="B5Lmnh_BHOU", es_50k=0, copiado=False, original=19,
      es_txt="'Atapuerca' o 'Cráneo 17': 4 títulos en ES, el mayor con 1.728 vistas. Tema propio del mundo hispano, sin cobertura buena. Black Mango (658k) habla de la prehistoria en formato podcast con personas, no es el mismo formato.",
      gancho="Imagina que caes al fondo de un pozo en Burgos con dos golpes idénticos en la frente. Pasan 430.000 años y unos forenses arman tu cráneo con 52 pedazos. Su conclusión es incómoda: no fue un accidente.",
      bloques=["¿Qué es la Sima de los Huesos y por qué hay tantos cuerpos?", "¿Cómo se armó el cráneo 17 con 52 pedazos?", "¿Por qué dos golpes descartan un accidente?", "¿Quién pudo hacerlo y con qué?", "¿Tiraron los cuerpos al pozo a propósito? (el primer ritual)", "Veredicto: ¿siempre fuimos violentos?"],
      fuentes=["Sala, N. et al. (2015). Lethal interpersonal violence in the Middle Pleistocene. PLoS ONE 10(5).", "Arsuaga, J. L. & Martínez, I. (1998). La especie elegida. Temas de Hoy.", "Carbonell, E. & Mosquera, M. (2006). The emergence of a symbolic behaviour: the sepulchral pit of Sima de los Huesos. Comptes Rendus Palevol 5."],
      riesgo="Medio: violencia; mostrar el cráneo y reconstrucciones, no la agresión explícita.", riesgo_pen=5),
 dict(n=13, tema="violencia", titulo="La primera guerra fue hace 10.000 años junto a un lago de Kenia",
      alt=["Nataruk: 27 personas, una masacre y la pregunta de si la guerra es natural", "¿Los cazadores-recolectores hacían la guerra? Lo que encontraron en Turkana"],
      analogo="pSwhPbKMp6Q", es_50k=0, copiado=False, original=17,
      es_txt="'Nataruk' aparece 0 veces en 51.881 títulos guardados. Muerte/violencia en ES: 11 largos, solo 1 ≥50k (podcast).",
      gancho="Te dijeron que la guerra empezó cuando hubo campos y graneros que defender. Ahora imagina un lago en Kenia hace diez mil años, donde veintisiete cazadores-recolectores mueren el mismo día. Alguien los había rodeado.",
      bloques=["¿Qué encontraron en Nataruk?", "¿Cómo se sabe que murieron al mismo tiempo?", "¿Qué armas usaron?", "¿Por qué pelearían cazadores-recolectores?", "¿La guerra es natural en los humanos? (el debate)", "Veredicto: lo que este lago dice de nosotros"],
      fuentes=["Mirazón Lahr, M. et al. (2016). Inter-group violence among early Holocene hunter-gatherers of West Turkana, Kenya. Nature 529.", "Kelly, R. C. (2000). Warless Societies and the Origin of War. University of Michigan Press.", "Stojanowski, C. et al. (2016). Contextualizing the 'massacre' at Nataruk. Nature 539 (crítica)."],
      riesgo="Medio: violencia; sin gore.", riesgo_pen=5),
 dict(n=14, tema="comida", titulo="¿Por qué cocinar te dio un cerebro más grande?",
      alt=["El fuego cambió tu cuerpo: lo que pasó cuando el humano empezó a cocinar", "Si comieras todo crudo, necesitarías masticar 6 horas al día"],
      analogo="1BXyVB0vx5w", es_50k=0, copiado=False, original=13,
      es_txt="Comida en ES: 17 largos, ninguno ≥50k (máximo 45.603). Análogo en EN débil (99k, canal chico). Demanda medida modesta.",
      gancho="Un chimpancé pasa casi la mitad del día masticando. Tú masticas, como mucho, una hora. Esa diferencia no es casualidad: según un antropólogo de Harvard, empezó la primera vez que alguien acercó un pedazo de carne al fuego.",
      bloques=["¿Cuánto tiempo masticaría un humano si comiera crudo?", "¿Qué le hace el fuego a la comida?", "¿Cuándo empezamos a cocinar? (Wonderwerk)", "¿Cómo cambió el intestino y el cerebro?", "¿Se puede vivir comiendo crudo hoy?", "Veredicto: cocinar nos hizo humanos (o no tanto)"],
      fuentes=["Wrangham, R. (2009). Catching Fire: How Cooking Made Us Human. Basic Books.", "Berna, F. et al. (2012). Microstratigraphic evidence of in situ fire in the Acheulean strata of Wonderwerk Cave. PNAS 109(20).", "Carmody, R. & Wrangham, R. (2009). The energetic significance of cooking. Journal of Human Evolution 57."],
      riesgo="Bajo. Es una hipótesis discutida: decirlo.", riesgo_pen=0),
 dict(n=15, tema="comida", titulo="Colgados de una soga por un poco de miel: la pintura de unos 8.000 años de Valencia",
      alt=["El primer dulce de la humanidad costaba la vida", "La Cueva de la Araña: así conseguían azúcar antes del azúcar"],
      analogo="4mB7NIrEIHI", es_50k=0, copiado=False, original=18,
      es_txt="Títulos con 'miel' en ES: todos sobre el tejón de la miel o gastronomía; 0 sobre miel prehistórica. Tema con raíz española.",
      gancho="Imagina que estás colgado de una soga sobre un barranco, con la mano dentro de una colmena y cientos de abejas encima. Todo por algo que hoy compras en el súper por monedas. En una pared de Valencia alguien pintó esa escena hace unos ocho mil años.",
      bloques=["¿Qué muestra la pintura de la Cueva de la Araña?", "¿Por qué el cerebro humano ama el azúcar?", "¿Cómo sacaban miel sin trajes ni humo?", "¿Los hadza todavía lo hacen? El pájaro que los guía", "¿Desde cuándo criamos abejas?", "Veredicto: ¿te colgarías tú por un poco de miel?"],
      fuentes=["Crane, E. (1999). The World History of Beekeeping and Honey Hunting. Routledge.", "Roffet-Salque, M. et al. (2015). Widespread exploitation of the honeybee by early Neolithic farmers. Nature 527.", "Spottiswoode, C. et al. (2016). Reciprocal signaling in honeyguide-human mutualism. Science 353."],
      riesgo="Bajo.", riesgo_pen=0),
 dict(n=16, tema="ropa/cuerpo", titulo="¿Cuándo aparecieron los primeros zapatos? Lo dicen los dedos de tus pies",
      alt=["Los huesos de los pies delatan al primer humano con calzado", "Sandalias de 10.000 años: la historia del zapato que nadie cuenta"],
      analogo="TaMhhe9BKYE", es_50k=0, copiado=False, original=15,
      es_txt="Zapatos en ES: 3 títulos, máximo 15.958. El análogo directo en EN es flojo (36k-62k); uso como análogo el de ropa de Mack (363k, x278).",
      gancho="Mírate el dedo chico del pie. Es más débil que el de un humano de hace 100.000 años. Esa diferencia la descubrió un antropólogo, y con ella pudo calcular algo que ningún zapato fosilizado podía decirnos: cuándo empezamos a usar calzado.",
      bloques=["¿Por qué no hay zapatos fósiles de 40.000 años?", "¿Qué le pasa a un pie que nunca usó calzado?", "¿Qué dicen los dedos de Tianyuan?", "Las sandalias de Fort Rock: las más viejas conservadas", "¿Caminaban descalzos sobre la nieve?", "Veredicto: ¿el zapato nos debilitó?"],
      fuentes=["Trinkaus, E. (2005). Anatomical evidence for the antiquity of human footwear use. Journal of Archaeological Science 32.", "Trinkaus, E. & Shang, H. (2008). Anatomical evidence for the antiquity of human footwear: Tianyuan and Sunghir. Journal of Archaeological Science 35.", "Connolly, T. et al. (2016). Getting beyond the point: textiles of the terminal Pleistocene/early Holocene in the northwestern Great Basin. American Antiquity 81. (verificar)"],
      riesgo="Bajo.", riesgo_pen=0),
 dict(n=17, tema="religión/muerte", titulo="¿Por qué los humanos empezaron a enterrar a sus muertos?",
      alt=["La primera tumba de la historia (y lo que pusieron adentro)", "Flores, ocre y conchas: los primeros funerales de la humanidad"],
      analogo="GbhjusSbXcY", es_50k=1, copiado=False, original=12,
      es_txt="Religión en ES: 3 largos encontrados, 1 con ≥50k (Andrey Viarens, 59k, sobre la primera religión). Ángulo de entierros: sin videos largos dedicados en lo guardado.",
      gancho="Si ves un animal muerto en el campo, sigues de largo. Hace más de cien mil años, alguien como tú cavó un pozo, acomodó un cuerpo con cuidado y lo cubrió. Ningún otro animal hace eso, y vas a ver por qué empezó.",
      bloques=["¿Cuál es la tumba más antigua que se conoce?", "¿Los neandertales enterraban a los suyos?", "¿Qué ponían en las tumbas y por qué?", "¿Creían en otra vida?", "¿El Homo naledi enterraba? (el debate actual)", "Veredicto: el día que inventamos el recuerdo"],
      fuentes=["Pettitt, P. (2011). The Palaeolithic Origins of Human Burial. Routledge.", "Martinón-Torres, M. et al. (2021). Earliest known human burial in Africa. Nature 593 (Panga ya Saidi).", "Berger, L. et al. (2023). Evidence for deliberate burial of the dead by Homo naledi. eLife (preprint revisado; muy discutido)."],
      riesgo="Bajo-medio: no tratar religión actual; presentar el debate.", riesgo_pen=0),
 dict(n=18, tema="poder", titulo="Durante 290.000 años no hubo reyes: ¿qué pasó para que apareciera el primero?",
      alt=["¿Quién mandaba antes de que existieran los jefes?", "Los cazadores se burlaban del que quería mandar: así nació (y murió) la igualdad"],
      analogo="k2CXi4XPi7U", es_50k=0, copiado=True, original=9,
      es_txt="Sin un video en ES sobre reyes, pero Estrictamente ya traduce a Deep Epoch (países 272k, esclavitud 149k). Es probable que lo copie pronto: lo marco como 'ya en la mira de los copiones'.",
      gancho="Imagina que vuelves al campamento con el ciervo más grande del año y te agrandas un poco. Tu grupo se burla de tu presa hasta que bajas la cabeza. Durante casi toda la historia humana, mandar sobre otros estaba mal visto: ¿cómo terminamos con reyes?",
      bloques=["¿Cómo evitaban los cazadores que alguien mandara?", "¿Qué cambió con los graneros y la acumulación?", "¿Quién fue el primer jefe con nombre?", "¿Por qué la gente aceptó obedecer?", "¿Hubo sociedades que volvieron a la igualdad?", "Veredicto: ¿los reyes eran inevitables?"],
      fuentes=["Boehm, C. (1999). Hierarchy in the Forest: The Evolution of Egalitarian Behavior. Harvard University Press.", "Flannery, K. & Marcus, J. (2012). The Creation of Inequality. Harvard University Press.", "Graeber, D. & Wengrow, D. (2021). The Dawn of Everything. Farrar, Straus and Giroux."],
      riesgo="Bajo-medio: evitar lecturas políticas actuales.", riesgo_pen=0),
 dict(n=19, tema="supervivencia", titulo="¿Cuánto durarías en cada época de la historia de México?",
      alt=["De la Edad de Hielo a la Revolución: ¿en qué época de México sobrevivirías?", "Viaje en el tiempo por México: en cuál te morías en una semana"],
      analogo="nAWpLtG-kNs", es_50k=0, copiado=False, original=17,
      es_txt="Formato con prueba enorme (Fossil 11,5M, canal de 7 meses). En ES hay 8 ganadores de 'supervivencia', todos genéricos o traducidos; ninguno aplicado a la historia de un país latinoamericano en lo guardado.",
      gancho="Imagina que una máquina del tiempo se descompone y te deja en México, sin saber en qué siglo: con mamuts, en Tenochtitlan o en plena epidemia de 1576. En algunas épocas durarías años. En otras, no llegarías al domingo.",
      bloques=["Hace 15.000 años: mamuts y lobos gigantes", "Teotihuacan: ¿te dejarían entrar?", "Tenochtitlan en 1500: comida, agua y sacrificios", "1520 y 1576: las epidemias", "Siglo XIX: guerras, bandidos y cólera", "Veredicto: el ranking final de épocas"],
      fuentes=["Ardelean, C. et al. (2020). Evidence of human occupation in Mexico around the Last Glacial Maximum. Nature 584. (hallazgo discutido)", "Sahagún, B. de (c. 1577). Historia general de las cosas de la Nueva España (Códice Florentino).", "Acuna-Soto, R. et al. (2002). Megadrought and megadeath in 16th century Mexico. Emerging Infectious Diseases 8(4)."],
      riesgo="Medio: sacrificios y epidemias; evitar estereotipos y gore.", riesgo_pen=5),
 dict(n=20, tema="supervivencia", titulo="¿Cuánto durarías en la Sudamérica de la Edad de Hielo?",
      alt=["Perezosos de 4 toneladas y tigres dientes de sable: la Argentina de hace 12.000 años", "Megaterios, gliptodontes y smilodones: sobrevive una semana en las Pampas"],
      analogo="nAWpLtG-kNs", es_50k=0, copiado=False, original=18,
      es_txt="Mi búsqueda específica de megafauna sudamericana devolvió 0 resultados (consulta demasiado larga; dato perdido). En títulos guardados: 6 en ES sobre smilodon/megaterio/gliptodonte, máximo 6.478.",
      gancho="Imagina que llegas a las Pampas hace doce mil años y ves un perezoso del tamaño de un elefante, un armadillo grande como un auto y un felino con colmillos de veinticinco centímetros. Entre ellos caminan los primeros humanos de Sudamérica. ¿Cuánto durarías tú?",
      bloques=["¿Cómo era el paisaje de las Pampas?", "Megaterio: ¿peligroso o tranquilo?", "Smilodon populator: el felino más grande", "¿Cómo cazaban los humanos a un perezoso gigante? (Campo Laborde)", "¿Por qué desaparecieron todos?", "Veredicto: tu tiempo de supervivencia"],
      fuentes=["Fariña, R., Vizcaíno, S. & De Iuliis, G. (2013). Megafauna: Giant Beasts of Pleistocene South America. Indiana University Press.", "Politis, G. et al. (2019). Campo Laborde: a Late Pleistocene giant ground sloth kill and butchering site in the Pampas. Science Advances 5(3).", "Prevosti, F. & Vizcaíno, S. (2006). Paleoecology of the large carnivore guild from the late Pleistocene of Argentina. Acta Palaeontologica Polonica 51."],
      riesgo="Bajo.", riesgo_pen=0),
 dict(n=21, tema="vida cotidiana LatAm", titulo="Un día en la vida de un niño mexica (y por qué temía al humo de chile)",
      alt=["Ser niño en Tenochtitlan: escuela, tareas y castigos", "Lo que comía, aprendía y temía un niño azteca de 10 años"],
      analogo="U_eV4WbL6Vw", es_50k=0, copiado=False, original=15,
      es_txt="Vida mexica en ES: 2 videos ≥50k (245k de un canal de 4,46M y 201k de 'Un Día En La Historia'). Sobre niños mexicas: ninguno en lo guardado.",
      gancho="Tienes once años, vives en Tenochtitlan y acabas de mentirle a tu padre. En vez de un reto, tu padre va a quemar chiles secos y ponerte sobre el humo. Lo sabemos porque un códice de 1541 lo dibujó.",
      bloques=["¿Qué es el Códice Mendoza y quién lo pintó?", "¿Cuántas tortillas comía un niño según su edad?", "¿Iban a la escuela? Telpochcalli y calmécac", "¿Qué tareas hacían niñas y niños?", "¿Cómo eran los castigos y por qué?", "Veredicto: ¿te habría gustado ser niño mexica?"],
      fuentes=["Códice Mendoza (c. 1541). Bodleian Library, Oxford (folios 57-60).", "Berdan, F. & Anawalt, P. (1992). The Codex Mendoza. University of California Press.", "Sahagún, B. de (c. 1577). Historia general de las cosas de la Nueva España."],
      riesgo="Medio: castigos a niños; mostrar el códice, no recrear el castigo.", riesgo_pen=5),
 dict(n=22, tema="vida cotidiana LatAm", titulo="Pescado fresco en Cusco, a cientos de kilómetros del mar: el correo inca que corría día y noche",
      alt=["Los chasquis: el sistema de mensajes más rápido antes del telégrafo", "¿Cómo se enteraba el emperador inca de todo en días, sin caballos ni escritura?"],
      analogo="U_eV4WbL6Vw", es_50k=0, copiado=False, original=17,
      es_txt="Inca en ES: 23 títulos, solo 1 ≥50k y es un Short de 'qué pasaría si'. Ningún video largo sobre chasquis en lo guardado. Análogo lejano (vida cotidiana antigua).",
      gancho="Imagina que eres el emperador inca y quieres pescado fresco en Cusco, a más de tres mil metros y a cientos de kilómetros del mar. No tienes caballos, ni ruedas, ni escritura. Y aun así, según los cronistas, el pescado llegaba.",
      bloques=["¿Quiénes eran los chasquis y cómo los elegían?", "¿Cuántos kilómetros recorría un mensaje por día?", "¿Cómo era el camino inca?", "¿Cómo mandaban mensajes sin escribir? Los quipus", "¿Era verdad lo del pescado fresco?", "Veredicto: ¿más rápido que el correo moderno?"],
      fuentes=["Hyslop, J. (1984). The Inka Road System. Academic Press.", "Garcilaso de la Vega, I. (1609). Comentarios Reales de los Incas.", "Urton, G. (2003). Signs of the Inka Khipu. University of Texas Press. (Distancia diaria de los relevos: verificar cifra)"],
      riesgo="Bajo-medio: la historia del pescado es una tradición de cronistas; presentarla como tal.", riesgo_pen=0),
 dict(n=23, tema="frío/ropa LatAm", titulo="Casi desnudos bajo la nieve: cómo resistían el frío los yaganes de Tierra del Fuego",
      alt=["Darwin no podía creerlo: gente sin ropa a 0 °C en el fin del mundo", "¿Por qué los pueblos del fin del mundo casi no usaban ropa?"],
      analogo="TaMhhe9BKYE", es_50k=0, copiado=False, original=19,
      es_txt="Yagán/selk'nam/Tierra del Fuego: 0 títulos en ES sobre el tema (los 7 con 'Patagonia' son de misterio o terror). Análogo directo en EN: 'Ancient Humans Didn't Wear Clothes To Stay Warm' (363k, x278, canal de 1.430 subs).",
      gancho="Imagina que estás en Tierra del Fuego con un abrigo de lana y aun así tiemblas bajo el aguanieve. En la orilla ves a una mujer amamantando a su bebé casi sin ropa. Eso vio la tripulación de Darwin en 1832, y no podían entender cómo seguía viva.",
      bloques=["¿Quiénes eran los yaganes y dónde vivían?", "¿Por qué casi no usaban ropa? Grasa, fuego y agua", "¿Su cuerpo era distinto? El metabolismo del frío", "¿Por qué vivían en canoas?", "¿Qué les pasó después del contacto con europeos?", "Veredicto: lo que el frío nos enseña del cuerpo humano"],
      fuentes=["Darwin, C. (1839). Journal of Researches (El viaje del Beagle), capítulo sobre Tierra del Fuego.", "Gusinde, M. (1937). Die Feuerland-Indianer, tomo II: Die Yamana. (verificar edición en español)", "Chapman, A. (2010). European Encounters with the Yamana People of Cape Horn, Before and After Darwin. Cambridge University Press."],
      riesgo="Medio: pueblo real con descendientes vivos; tratarlo con respeto, no como curiosidad 'primitiva'. No recrear fotos históricas reales.", riesgo_pen=5),
 dict(n=24, tema="poblamiento LatAm", titulo="Monte Verde: los primeros sudamericanos comían algas hace 14.500 años",
      alt=["El campamento chileno que cambió la historia de América", "Llegaron antes de lo que decían los libros: el secreto de Monte Verde"],
      analogo="hZfVSlKLe_M", es_50k=0, copiado=False, original=17,
      es_txt="'Monte Verde': 0 títulos guardados. Análogo en ES directo: Tiempos Antiguos, cruce de Bering (1,36M, canal de 15.500 subs): hay demanda en ES para el poblamiento de América.",
      gancho="Durante décadas te enseñaron que los primeros americanos llegaron cazando mamuts por el norte, hace unos trece mil años. Pero en el sur de Chile, bajo una turbera, apareció un campamento con chozas, carne y algas marinas mil años más viejo. Y estaba en la otra punta del continente.",
      bloques=["¿Qué encontró Tom Dillehay en Monte Verde?", "¿Cómo se conservó madera de 14.500 años?", "¿Por qué algas? Comida y medicina", "¿Cómo llegaron tan al sur tan rápido? (la ruta de la costa)", "¿Por qué tardaron 20 años en aceptarlo?", "Veredicto: la historia de América que no te contaron"],
      fuentes=["Dillehay, T. (1997). Monte Verde: A Late Pleistocene Settlement in Chile, vol. 2. Smithsonian Institution Press.", "Dillehay, T. et al. (2008). Monte Verde: seaweed, food, medicine, and the peopling of South America. Science 320.", "Meltzer, D. (2009). First Peoples in a New World. University of California Press."],
      riesgo="Bajo.", riesgo_pen=0),
 dict(n=25, tema="agua LatAm", titulo="Sin ríos ni lagos: cómo tomaban agua los mayas durante sequías de años",
      alt=["Cenotes: los pozos sagrados que mantuvieron viva a una civilización", "La sequía que derrumbó a los mayas (y cómo resistieron siglos antes)"],
      analogo="1QQZHTD0zJs", es_50k=0, copiado=False, original=16,
      es_txt="Maya en ES: 29 títulos, 2 ≥50k (uno de animales y uno de exploración). Sobre agua y cenotes: ninguno largo en lo guardado. Análogo EN: egipcios y calor del desierto (1,15M, x106).",
      gancho="Imagina que vives en una tierra sin ríos ni lagos, donde pasan meses sin llover. Así es la península de Yucatán, y ahí vivieron millones de mayas durante siglos. Su agua estaba bajo tus pies, en pozos que creían puertas al inframundo.",
      bloques=["¿Por qué en Yucatán no hay ríos?", "¿Qué es un cenote y cómo se formó? (el asteroide)", "¿Cómo guardaban agua de lluvia? Chultunes y reservorios", "¿Qué pasó en las grandes sequías?", "¿Por qué tiraban ofrendas a los cenotes?", "Veredicto: el agua decidió el destino maya"],
      fuentes=["Lucero, L. (2006). Water and Ritual: The Rise and Fall of Classic Maya Rulers. University of Texas Press.", "Haug, G. et al. (2003). Climate and the collapse of Maya civilization. Science 299.", "Scarborough, V. (1998). Ecology and ritual: water management and the Maya. Latin American Antiquity 9. (verificar)"],
      riesgo="Bajo.", riesgo_pen=0),
 dict(n=26, tema="higiene LatAm", titulo="Los mexicas se bañaban todos los días; los conquistadores, casi nunca",
      alt=["El choque de dos higienes en 1519", "¿Quién olía peor en Tenochtitlan? Lo que escribieron los cronistas"],
      analogo="7MgqNR8oxSU", es_50k=0, copiado=False, original=18,
      es_txt="Higiene en ES: 0 ≥50k. El análogo en EN (vikingos limpios contra Europa sucia, 1,12M, x88) usa el mismo contraste. Sin versión latinoamericana en lo guardado.",
      gancho="Imagina que eres un soldado español en noviembre de 1519, con meses de marcha encima y la misma ropa. Entras a Tenochtitlan y encuentras baños de vapor y calles barridas. Uno de tus compañeros escribirá que el emperador se bañaba todos los días.",
      bloques=["¿Cómo era la higiene en la España de 1500?", "¿Qué era el temazcal y quién lo usaba?", "¿Con qué se lavaban los mexicas? (el jabón de raíz)", "¿Cómo limpiaban una ciudad de 200.000 personas?", "¿Qué escribieron los cronistas?", "Veredicto: el mito del 'salvaje sucio'"],
      fuentes=["Díaz del Castillo, B. (1632). Historia verdadera de la conquista de la Nueva España. (verificar pasaje sobre los baños de Moctezuma)", "Sahagún, B. de (c. 1577). Historia general de las cosas de la Nueva España.", "Vigarello, G. (1985). Lo limpio y lo sucio. La higiene del cuerpo desde la Edad Media. Alianza."],
      riesgo="Medio: tema colonial sensible; contrastar con fuentes y evitar exagerar.", riesgo_pen=5),
 dict(n=27, tema="cuerpo/agricultura", titulo="Los primeros agricultores eran más bajos que los cazadores: lo que dicen los esqueletos",
      alt=["La agricultura te achicó: lo que dicen los esqueletos", "¿Por qué los humanos se volvieron más bajos al inventar el pan?"],
      analogo="49_Ph2q6uIM", es_50k=1, copiado=True, original=8,
      es_txt="Es parte del video de Ink Explainer (13,9M) y su traducción en ES (Homo Curioso, 473k) ya toca los esqueletos. Lo marco como cubierto en parte.",
      gancho="Si pudieras poner en fila a un cazador de hace quince mil años y a un agricultor de hace siete mil, el cazador probablemente le sacaría media cabeza. La agricultura nos dio pan, pueblos y civilizaciones. También nos achicó.",
      bloques=["¿Cómo se mide la altura de un esqueleto?", "¿Cuánto bajó la estatura con la agricultura? (la cifra cambia por región: verificar)", "¿Qué faltaba en la dieta del agricultor?", "¿Más gente pero más enferma?", "¿Cuándo recuperamos la altura?", "Veredicto: ¿fue buen negocio la agricultura?"],
      fuentes=["Mummert, A. et al. (2011). Stature and robusticity during the agricultural transition: evidence from the bioarchaeological record. Economics & Human Biology 9(3).", "Cohen, M. N. & Armelagos, G. (eds.) (1984). Paleopathology at the Origins of Agriculture. Academic Press.", "Larsen, C. S. (1995). Biological changes in human populations with agriculture. Annual Review of Anthropology 24."],
      riesgo="Bajo.", riesgo_pen=0),
 dict(n=28, tema="animales", titulo="El perro que enterraron con dos humanos hace 14.000 años estaba enfermo y lo cuidaron",
      alt=["Bonn-Oberkassel: la primera prueba de amor entre humanos y perros", "Antes de ser útil, el perro ya era familia"],
      analogo="UfMktyXUycE", es_50k=0, copiado=False, original=16,
      es_txt="Perros en ES tienen mucha demanda (13 títulos ≥50k en lo guardado, casi todos Shorts de animales), pero ninguno sobre el perro prehistórico. Análogo lejano en EN: 'Why Do Humans Love Cats?' (125k).",
      gancho="Imagina que cuidas durante semanas a un cachorro enfermo que nunca va a cazar ni a cuidar nada. Hace catorce mil años, en Alemania, alguien hizo exactamente eso. Cuando el cachorro murió, lo enterraron junto a dos personas.",
      bloques=["¿Qué encontraron en Bonn-Oberkassel en 1914?", "¿Cómo se sabe que el cachorro estuvo enfermo?", "¿Por qué cuidar un animal que no sirve?", "¿Cuándo se separó el perro del lobo?", "¿Los perros nos cambiaron a nosotros?", "Veredicto: el amor más antiguo"],
      fuentes=["Janssens, L. et al. (2018). A new look at an old dog: Bonn-Oberkassel reconsidered. Journal of Archaeological Science 92.", "Germonpré, M. et al. (2009). Fossil dogs and wolves from Palaeolithic sites in Belgium, the Ukraine and Russia. Journal of Archaeological Science 36.", "Bergström, A. et al. (2020). Origins and genetic legacy of prehistoric dogs. Science 370."],
      riesgo="Bajo.", riesgo_pen=0),
 dict(n=29, tema="supervivencia medieval", titulo="¿Cuánto durarías en la España de 1348, cuando llegó la peste negra?",
      alt=["La peste en Valencia y Barcelona: sobrevive una semana en 1348", "Tu vida en 1348: la mitad de tu pueblo no llega a Navidad"],
      analogo="IwH-pfPpLko", es_50k=0, copiado=False, original=12,
      es_txt="Vida medieval en ES: 30 largos y 6 ≥50k (incluye un canal de historias para dormir), pero sobre la peste en España no hay ninguno en lo guardado. Competencia media.",
      gancho="Es junio de 1348, vives en un puerto del Mediterráneo español y llegan barcos con marineros enfermos. En pocos meses, una de cada dos personas que conoces va a morir. ¿Te quedas, huyes o rezas?",
      bloques=["¿Cómo llegó la peste a la península?", "¿Qué hacía un médico en 1348?", "¿Huir servía de algo?", "¿A quién culparon? (los ataques a juderías)", "¿Qué cambió para los que sobrevivieron?", "Veredicto: tus chances reales"],
      fuentes=["Benedictow, O. (2004). The Black Death 1346-1353: The Complete History. Boydell Press.", "Spyrou, M. et al. (2022). The source of the Black Death in fourteenth-century central Eurasia. Nature 606.", "Amasuno, M. (1996). La peste en la Corona de Castilla durante la segunda mitad del siglo XIV. Junta de Castilla y León. (verificar)"],
      riesgo="Medio: persecuciones a judíos; tratarlas con cuidado y contexto.", riesgo_pen=5),
 dict(n=30, tema="altura/cuerpo LatAm", titulo="Vivir a 4.500 metros sin oxígeno extra: los primeros humanos de los Andes",
      alt=["Hace 12.000 años ya vivían donde tú no podrías respirar", "El campamento más alto de la Edad de Hielo está en Perú"],
      analogo="hZfVSlKLe_M", es_50k=0, copiado=False, original=17,
      es_txt="Sin videos en lo guardado sobre los primeros pobladores de los Andes. Análogo en ES: poblamiento de América (1,36M).",
      gancho="Sube a cuatro mil quinientos metros: te falta el aire, te duele la cabeza y cada paso pesa el doble. Ahí, en un refugio de roca en Perú, vivía gente hace doce mil años. Criaban a sus hijos donde tú apenas podrías dormir.",
      bloques=["¿Qué es el mal de altura y por qué mata?", "¿Qué encontraron en Cuncaicha?", "¿Cómo se adaptó el cuerpo andino?", "¿Qué comían a esa altura?", "¿Por qué subir tan alto?", "Veredicto: ¿podrías vivir ahí?"],
      fuentes=["Rademaker, K. et al. (2014). Paleoindian settlement of the high-altitude Peruvian Andes. Science 346.", "Beall, C. (2007). Two routes to functional adaptation: Tibetan and Andean high-altitude natives. PNAS 104.", "Haas, R. et al. (2020). Female hunters of the early Americas. Science Advances 6. (relacionado, Wilamaya Patjxa)"],
      riesgo="Bajo.", riesgo_pen=0),
]


CERCANIA = {1: 'parcial', 2: 'parcial', 3: 'parcial', 4: 'directo', 5: 'directo', 6: 'parcial', 7: 'lejano', 8: 'directo', 9: 'parcial', 10: 'directo', 11: 'parcial', 12: 'lejano', 13: 'parcial', 14: 'directo', 15: 'parcial', 16: 'parcial', 17: 'parcial', 18: 'directo', 19: 'parcial', 20: 'parcial', 21: 'parcial', 22: 'lejano', 23: 'parcial', 24: 'parcial', 25: 'parcial', 26: 'parcial', 27: 'directo', 28: 'lejano', 29: 'parcial', 30: 'parcial'}
FACTOR_CERCANIA = {"directo": 1.0, "parcial": 0.7, "lejano": 0.4}


def puntaje(q):
    a = q["analogo_datos"]
    v = max(a["vistas"], 1)
    q["cercania"] = CERCANIA[q["n"]]                                              # OPINIÓN: qué tan parecido es el análogo
    dem = round(35 * min(1, max(0, (math.log10(v) - 4.7) / 2.4)) * FACTOR_CERCANIA[q["cercania"]], 1)  # MEDIDO x cercanía
    f = a["factor_outlier"] or 1
    out = round(15 * min(1, max(0, math.log10(f) / 2.5)), 1)                    # MEDIDO
    hueco = 0 if q["copiado"] else (30 if q["es_50k"] == 0 else 15 if q["es_50k"] == 1 else 5)  # MEDIDO
    total = round(dem + out + hueco + q["original"] - q["riesgo_pen"], 1)        # + OPINIÓN
    return dict(demanda=dem, outlier=out, hueco_es=hueco, originalidad=q["original"], riesgo=-q["riesgo_pen"], total=total)


def main():
    rows = []
    for q in Q:
        q["analogo_datos"] = analogo(q["analogo"])
        q["puntaje"] = puntaje(q)
        rows.append(q)
    rows.sort(key=lambda q: -q["puntaje"]["total"])
    for i, q in enumerate(rows, 1):
        q["ranking"] = i
    (OUT / "preguntas.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    with open(OUT / "preguntas.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["ranking", "n", "tema", "titulo", "alternativa_1", "alternativa_2", "puntaje_total", "demanda_medido", "outlier_medido",
                    "hueco_es_medido", "cercania_analogo_opinion", "originalidad_opinion", "penalizacion_riesgo_opinion", "analogo_url", "analogo_titulo", "analogo_vistas",
                    "analogo_canal", "analogo_subs", "analogo_canal_creado", "analogo_factor_outlier", "evidencia_es", "gancho", "bloques", "fuentes", "riesgo"])
        for q in rows:
            a, p = q["analogo_datos"], q["puntaje"]
            w.writerow([q["ranking"], q["n"], q["tema"], q["titulo"], q["alt"][0], q["alt"][1], p["total"], p["demanda"], p["outlier"], p["hueco_es"],
                        q["cercania"], p["originalidad"], p["riesgo"], f"https://www.youtube.com/watch?v={a['video_id']}", a["titulo"], a["vistas"], a["canal"], a["subs"],
                        a["canal_creado"], a["factor_outlier"] or "", q["es_txt"], q["gancho"], " | ".join(q["bloques"]), " | ".join(q["fuentes"]), q["riesgo"]])
    for q in rows[:8]:
        print(q["ranking"], q["puntaje"]["total"], q["titulo"])
    return rows


if __name__ == "__main__":
    main()
