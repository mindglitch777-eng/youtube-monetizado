# ESPECIFICACIÓN DE PRODUCCIÓN Y GUION MAESTRO: VIDEO 3
# CANAL: Explicado en Pijamas
# TÍTULO: Sobreviví 30 Días a la Peste Negra (en pijama)

Versión 2. Escrita por la IA de YouTube (Studio, "Ideas para tus videos") a partir del guion v1. Transcrita textual de las capturas del usuario el 26/10/2026. Esta es la versión que manda.

======================================================================
1. GUÍA DE EDICIÓN PROGRAMÁTICA (REMOTION + FFMPEG + CLAUDE CODE)
======================================================================

[ESTRUCTURA DE COMPOSICIÓN EN REMOTION]
La composición debe operar con 5 capas (layers) apiladas en Z-Index:

- Layer 0: BackgroundLayer (Visuales)
  * Cero fotogramas estáticos: cada imagen aplica `interpolate(frame, [0, duration], [1.0, 1.08])` para un zoom/pan continuo (efecto Ken Burns programático).
  * Cortes visuales cada 1.8 a 2.5 segundos. Transición por corte seco (hard cut) o flash de 2 frames a negro.

- Layer 1: AtmosphericParticles (Canvas Overlay)
  * Render de partículas en loop semitransparente: cenizas/polvo en la ciudad, moscas negras flotando en las escenas de peste, lluvia fina en la fuga.

- Layer 2: CameraShake & FX Layer
  * Al activarse un evento de daño (pérdida de vida / fiebre): sacudida sinusoidal en X/Y durante 10 frames (`Math.sin(frame * 1.5) * intensity`) combinada con viñeta roja periférica parpadeante.

- Layer 3: HUD Permanente (Gaming UI)
  * Esquina superior izquierda: `DayCounter` ("DÍA {N} / 30"). En cada cambio de día: animación de escala `spring({ from: 1.3, to: 1.0 })`.
  * Esquina superior derecha: `HealthBar` (3 corazones vectoriales). Al perder vida: el corazón parpadea en blanco y desaparece con efecto de rotura.
  * Debajo de vidas: `InfectionBar` (barra horizontal 0-100%). Gradiente dinámico de verde tóxico (#39FF14) a rojo sangre (#FF073A).
  * Centro-derecha: `AuraMeter` con interpolación de números enteros (+50, +100, +1348).

- Layer 4: InteractiveDecisionModal (Tarjetas A/B)
  * Se activa exactamente en los timestamps de las 5 decisiones.
  * Congela/atenúa el fondo un 40%.
  * Muestra dos tarjetas estilizadas tipo RPG (Opción A vs Opción B).
  * Barra de tiempo regresiva de 3.5 segundos con audio de tictac.
  * La opción incorrecta se tacha con cruz roja y sonido seco; la correcta se ilumina en verde neón.

[MEZCLA DE AUDIO Y SFX (FFMPEG / REMOTION AUDIO)]
- Voz Narrador: Normalizada a -14 LUFS, compresión dinámica dura (ratio 4:1) para presencia absoluta. Velocidad configurada al +16% en edge-tts.
- Voz Despertador: Filtro pasaaltos (high-pass a 800 Hz) con efecto de radio/altavoz metálico.
- Ducking Automático: La pista musical de tensión debe reducirse -6 dB automáticamente mientras la voz esté activa, subiendo a 0 dB durante los 3.5 segundos de cada tarjeta de decisión.
- SFX obligatorios:
  * Segundo 0:00: `sub_bass_drop.wav` + `glitch_power_on.wav`.
  * Cada cambio de día: `clock_tick_heavy.wav`.
  * Pérdida de vida: `retro_damage_hit.wav` + `heartbeat_low.wav`.
  * Decisión correcta: `retro_success_chime.wav`.
  * Día 30: `retro_achievement_fanfare.wav`.

======================================================================
2. GUION COMPLETO (PALABRA POR PALABRA)
======================================================================

[0:00 - 0:28] BLOQUE 0: EL GANCHO
(HUD: DÍA 1 / 30 · ❤️❤️❤️ · INF 0% · AURA 0)
(SFX: Sub-drop grave + glitch de encendido. Pantalla tiembla levemente.)

Cierras los ojos en tu cama.
Los abres en un charco de lodo.
Descalzo. En pijama.
Huele a humo y a carne podrida.
Es el año 1348.
En esta ciudad, uno de cada dos humanos va a terminar arrojado a una fosa antes de que termine el mes.
Tienes tres vidas. Un cronómetro de treinta días.
Y tu sistema inmune del siglo veintiuno no tiene idea de lo que se le viene encima.
¿Te mata una rata? ¿El frío? ¿O tu propio vecino?
Spoiler: te va a matar algo que ni siquiera puedes ver con un microscopio.
Cinco decisiones. Si fallas una, pierdes un corazón.
Si te quedas en cero, no hay respawn.
Haz tu apuesta.
Vamos a ver cuántos días duras vivo.
[DESPERTADOR]: «Día uno. El reloj arranca... ya.»

---

[0:28 - 1:25] BLOQUE 1: DÍAS 1–3 · LA TRAMPA LÍQUIDA Y EL ESTABLO
(HUD: DÍA 1 / 30 avanza a DÍA 3 / 30 · ❤️❤️❤️ · INF 0%)

Son las tres de la tarde.
Tu garganta arde como si hubieras tragado arena.
Ves una fuente de piedra en la plaza. El agua parece tentadora.
Error de novato: a cinco metros, un tipo está lavando tripas de cerdo en el canal.
Si tomas de esa agua, te da cólera o disentería y te deshidratas hasta morir en doce horas.
En 1348 nadie toma agua. Hasta los nenes de cinco años toman cerveza fermentada o vino agrio: es lo único con suficiente alcohol para no pudrirte el estómago.
Le das un botón de tu pijama a un tabernero por un trago de vino rancio.
Cae la noche. La temperatura se desploma a cuatro grados.
Sin abrigo, te mueres de hipotermia antes del amanecer.
Primera decisión.

[DECISIÓN 1]
(UI: Tarjeta en pantalla: A) Cama en posada caliente | B) Establo con caballos)
(SFX: Reloj corriendo: tic, tic, tic...)
Tres. Dos. Uno.
Si elegiste la posada, acabas de cometer tu primer error letal.
Fuego y sopa, sí. Pero la cama de paja tiene a veinte extraños roncando pegados a ti... y un enjambre de cientos de pulgas hambrientas saltando de piel en piel.
En una plaga, la comodidad es una trampa.
Pijama se mete al establo.
Huele inmundo. Le tiemblan las rodillas.
Pero está completamente solo. Y la soledad es la única armadura que existe en este siglo.
(HUD: INF 5% · AURA +50)
[DESPERTADOR]: «Aura: más cincuenta. Apestas a caballo, pero sigues con tres corazones.»

---

[1:25 - 2:40] BLOQUE 2: DÍAS 4–7 · EL ASESINO INVISIBLE Y LA PUERTA
(HUD: DÍA 4 / 30 avanza a DÍA 7 / 30 · ❤️❤️❤️ · INF 5%)

Día cuatro.
Las campanas de las iglesias se callan.
El gobierno las prohibió: había tantos muertos diarios que el repique constante estaba enloqueciendo a los sobrevivientes.
Día cinco. El vecino de enfrente no sale a trabajar.
Por la tarde, tres hombres con trapos en la cara entran a su casa y sacan un bulto envuelto en una sábana blanca.
Así empieza: dolor de cabeza atroz, vómitos oscuros y un dolor punzante en la ingle.
De pronto, te brota una masa negra del tamaño de una manzana.
Un bubón. Hirviendo de pus.
Si la bacteria salta a tus pulmones, toses sangre y en cuarenta y ocho horas tu corazón se detiene.
Día seis. Un golpe desesperado en la madera de tu establo.
Una nena. Su familia está ardiendo en fiebre adentro. Te suplica que entres a ayudarlos.
Segunda decisión.

[DECISIÓN 2]
(UI: Tarjeta en pantalla: A) Entrar a salvarlos | B) Dejar pan en el piso y trabar la puerta)
(SFX: Reloj corriendo: tic, tic, tic...)
Tres. Dos. Uno.
Tu moral moderna te dice que entres. Tu instinto biológico te dice que ni respires.
Cuando un cuerpo muere, su temperatura baja. Las pulgas infectadas abandonan el cadáver de inmediato buscando un nuevo huésped caliente. Si cruzas esa puerta, tú eres ese huésped.
Pijama deja el pan en la tierra. Da dos pasos hacia atrás. Y atranca la puerta de madera.
Sobreviviste a la culpa. Pero sigues respirando.
(HUD: INF 15%)
Día siete. Marcan todas las casas de la cuadra con cruces de cal blanca.
Quedarse en esta ciudad es jugar a la ruleta rusa con cinco balas en el tambor.

---

[2:40 - 4:00] BLOQUE 3: DÍAS 8–11 · LA CARNICERÍA DEL DOCTOR
(HUD: DÍA 8 / 30 avanza a DÍA 11 / 30 · ❤️❤️❤️ · INF 15%)
(SFX: Alerta cardíaca rápida)

Día ocho.
Sientes un ardor en el tobillo. Te rascas sin pensar.
Una marca roja. Una sola pulga del tamaño de una semilla.
[DESPERTADOR]: «Alerta roja en pantalla: Infección detectada en torrente sanguíneo.»
Corres a buscar a un médico.
Olvídate del tipo con máscara de pájaro y lentes oscuros: ese disfraz ridículo lo inventan en trescientos años.
El médico de 1348 lleva una túnica manchada de sangre seca, huele a cebolla podrida y apoya una cuchilla oxidada sobre una mesa mugrienta.
Te jura que la peste es culpa de los planetas y que tu sangre está "envenenada".
Tercera decisión.

[DECISIÓN 3]
(UI: Tarjeta en pantalla: A) Aceptar sangría con cuchilla | B) Huir y lavarte con vinagre)
(SFX: Reloj corriendo: tic, tic, tic...)
Tres. Dos. Uno.
Si eliges la sangría médica, te drenan medio litro de sangre vital, te bajan las defensas a cero y el óxido de la cuchilla te regala una infección bacteriana letal en dos días.
Pijama patea la banqueta, agarra la botella de vinagre y corre como un desquiciado.
El vinagre no destruye la bacteria interna, pero limpia la piel y el ardor insoportable espanta a nuevos bichos.
Aun así, la bacteria ya está adentro.
Día once. Cuarenta de fiebre.
La vista se te apaga. Escuchas el zumbido de tu propia sangre en los oídos.
(SFX: Golpe de impacto fuerte + Sacudida de cámara violenta + Pantalla roja)
(HUD: VIDA -1 · Corazón destruido · Quedan 2 vidas · INF 45%)
Pierdes un corazón. Te quedan dos vidas.
Un error más y se acabó el juego.

---

[4:00 - 5:15] BLOQUE 4: DÍAS 12–17 · EL POZO OSCURO
(HUD: DÍA 12 / 30 avanza a DÍA 17 / 30 · ❤️❤️ · INF 50%)

Día doce.
Ya no existen los funerales.
Pasan carretas por la noche arrojando decenas de cuerpos a zanjas gigantescas cubiertas con cal viva.
Pijama cae de rodillas sobre la paja del establo.
Tiembla sin control. Delira con su casa, con su cama, con una ducha caliente.
Pasa tres días sin comer, bebiendo vino tibio a gotas.
Día quince. Se pasa los dedos temblorosos por el cuello y las axilas con puro terror.
Buscando el bulto.
Nada.
No era la peste pulmonar. Era una neumonía brutal por el frío del establo y las defensas bajas.
Tu sistema inmune ganó el asalto... pero tu cuerpo quedó al borde del colapso.
(SFX: Alarma visual de pantalla: VIDA CRÍTICA)
(HUD: VIDA -1 · Corazón destruido · Queda 1 sola vida)
Te queda una sola vida.
El más mínimo rasguño a partir de ahora significa Game Over permanente.

---

[5:15 - 6:35] BLOQUE 5: DÍAS 18–21 · LA FUGA DE LOS RICOS Y LA SECTA
(HUD: DÍA 18 / 30 avanza a DÍA 21 / 30 · ❤️ · INF 35%)

Día dieciocho.
En la plaza, diez jóvenes de familias nobles cargan caballos con baúles de comida y seda.
Se escapan al campo. A encerrarse en una mansión en las colinas hasta que la ciudad termine de pudrirse.
Esto ocurrió en la vida real: el escritor Giovanni Boccaccio escribió un libro entero sobre ellos, el Decamerón.
Básicamente: la primera cuarentena VIP de la historia.
Cuarta decisión.

[DECISIÓN 4]
(UI: Tarjeta en pantalla: A) Quedarte en el establo | B) Seguir los carruajes 30 km a pie)
(SFX: Reloj corriendo: tic, tic, tic...)
Tres. Dos. Uno.
Quedarte en Florencia es sentarte a esperar que te toque el turno de la zanja.
Pijama echa a correr detrás de los caballos. Descalzo. Tragando polvo por senderos de piedra.
Día veinte. A mitad de la ruta te topas con una escena de pesadilla:
Cincuenta tipos semidesnudos marchando en fila, azotándose la espalda con látigos con púas de plomo hasta arrancarse pedazos de piel.
Los flagelantes. Creen que sangrando van a calmar el castigo de Dios.
Lo que no saben es que van regando sangre infectada y pulgas de pueblo en pueblo.
Pijama se tira de cabeza a una zanja llena de barro hasta que la caravana pasa de largo.
(HUD: AURA +100)
[DESPERTADOR]: «Esquivaste la secta. Te queda un corazón latiendo en el pecho.»

---

[6:35 - 7:55] BLOQUE 6: DÍAS 22–27 · EL TRAIDOR EN LA MANSIÓN Y EL SECRETO
(HUD: DÍA 22 / 30 avanza a DÍA 27 / 30 · ❤️ · INF 20% sube a INF 60%)

Día veintidós. Llegas a la villa en la montaña.
Te dejan entrar a los jardines porque creen que tu pijama a rayas es un traje de seda de algún noble exótico.
Pan blanco. Aire puro. Cero ratas a la vista.
Tu barra de infección cae en picada al verde.
Por primera vez en tres semanas, crees que ganaste la partida.
Día veinticinco. La cena está servida en una mesa larga.
De pronto, el criado que está vertiendo el vino suelta la copa, se dobla en dos y tose sangre directo sobre la comida.
Tiene los ojos rojos como brasas.
El salón entero se congela. La pesadilla rompió el perímetro.
Última decisión del juego.

[DECISIÓN 5]
(UI: Tarjeta en pantalla: A) Encerrarte en un cuarto de la mansión | B) Huir a la intemperie del bosque)
(SFX: Reloj corriendo: tic, tic, tic...)
Tres. Dos. Uno.
Peste pulmonar encerrada entre cuatro paredes. Si respiras ese aire, no llegas al desayuno.
Pijama revienta una ventana trasera, manotea un pedazo de pan y se pierde en la negrura del bosque.
Encuentra una choza de cazador abandonada entre los árboles.
Y aquí está el dato que te va a volar la cabeza:
Años más tarde, las autoridades portuarias obligaron a los barcos sospechosos a fondear mar adentro exactamente treinta días sin tocar tierra.
Lo llamaron trentino. Treinta días.
Luego lo aumentaron a cuarenta: quaranta.
De ahí nació la palabra que hoy conoces: cuarentena.
Esta simulación de treinta días... fue la primera cuarentena de la humanidad.

---

[7:55 - 8:45] BLOQUE 7: DÍAS 28–30 · VICTORIA Y LA PARADOJA FINAL
(HUD: DÍA 28 / 30 avanza a DÍA 30 / 30 · ❤️ · INF 0%)
(SFX: Explosión digital + Fanfarria retro de logro)

Día veintiocho. Solo en la choza.
Día veintinueve. Ni fiebre, ni tos, ni frío.
Día treinta.
Abres la puerta de madera astillada.
El sol baña el valle.
Treinta días completados. Una sola vida en reserva. Cero bubones en el cuerpo.
Sobreviviste al mes más letal del siglo catorce. En pijama.
[DESPERTADOR]: «Logro supremo desbloqueado. Aura final: más mil trescientos cuarenta y ocho puntos.»
Y aquí está el remate histórico que nadie te enseña:
Murió tanta mano de obra en Europa que los campesinos y siervos que quedaron vivos pudieron exigir el doble de dinero por su trabajo diario, destruyendo para siempre el poder feudal de la nobleza.
Literalmente: esquivaste a la muerte negra... y conseguiste el aumento de sueldo más descomunal de la historia.

---

[8:45 - 9:05] BLOQUE 8: RESULTADOS Y RETENCIÓN DE COMENTARIOS
(UI: Tabla completa de decisiones completándose con checks verdes:
 1. Establo, jamás la posada.
 2. Pan en la puerta sin entrar.
 3. Huir del médico y usar vinagre.
 4. Escapar al campo abierto.
 5. Cuarentena solitaria en el bosque.)

Tu tarjeta de supervivencia: cinco de cinco.
¿Cuántas acertaste tú en tiempo real?
Escríbemelo en los comentarios: ¿llegaste al día treinta con vida o te liquidó el médico en el día ocho con su cuchilla oxidada?
Comenta tu puntuación exacta ahora mismo.
