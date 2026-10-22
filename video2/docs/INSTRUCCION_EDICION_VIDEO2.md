# INSTRUCCIÓN DE EDICIÓN · Video 2 · "Te despiertas en pijama en 8 épocas: ¿en cuál mueres primero?"
Canal: "Explicado en Pijamas" · español neutro · 1 video largo (~10:30) + 9 Shorts.

## 0. Reglas de oro
1. **No supongas.** Si algo no se entiende, falta un archivo o dos instrucciones chocan: escribí una lista corta de dudas y esperá mi respuesta.
2. Herramientas gratis solamente. No imprimas claves. No toques el video 1 ni sus Shorts.
3. **Eficiencia sobre cantidad.** Cada efecto tiene que servir a un chiste, a un dato o a la retención. Si no, no va. No agregues nada que no esté acá.
4. **La meta es retención.** Todo corte, sonido y texto se decide con esta pregunta: ¿esto hace que siga mirando?
5. Comedia en Pijama y el Despertador, **nunca en las víctimas reales**. En Pompeya y Tenochtitlan, tono serio al hablar de las personas que murieron.

## 1. Archivos
- `guion_video2_v3.md`: guion, voz, tabla C (duración), D (Shorts), E (estilo por época), F (verificaciones).
- `manifest_imagenes_v2.json`: 230 ids (con huecos a propósito) con archivo, frase donde va, cámara `cam`, transición `tr`, texto en pantalla `overlay`, punto de vista `pov`.
- Imágenes `NNN_slug.jpg` en 2 zips (juntalas en una carpeta). Las normales son 16:9; las del bloque SHORTS (ids 228–240) son verticales 9:16.
- **Ids sin imagen (decisión mía, no inventes):** 001–007, 032, 036, 069, 070, 099, 100, 196. Cubrí esas frases con el plano vecino o con un texto/HUD, y avisame cuáles quedaron cubiertas.
- Imágenes con defectos conocidos: algunas traen franjas verticales a los costados y pocas tienen texto suelto en inglés. Regla: **si hay franja, escalá y recortá al tercio central; si hay texto, tapalo con un overlay o recortalo.** Nunca muestres texto en inglés.

## 2. Voz y audio
**Voces.** (a) Narrador: cálido, rápido, ~170 palabras/min. (b) **Despertador** (líneas 🕰): otra voz, seca y sarcástica, con filtro metálico leve y un "tic" al empezar. Orden de motores: edge-tts → Piper → espeak-ng; usá el primero que funcione. Probá antes la pronunciación (Deir el-Medina, Vesubio, Tenochtitlan, Tambora, Cuitláhuac, Ginebra, John Snow). Si suena mal, corregí con ortografía fonética y avisame.

**Control de duración (obligatorio).** Generá un audio por bloque, medilo y compará con la tabla C (total calculado 10:32). Entregame la tabla "calculado vs real". Si el total real queda fuera de 9:45–11:15, frená y avisame.

**Mezcla (números fijos).**
- Volumen final: **−14 LUFS integrado**, pico real máx. −1 dBTP (largo y Shorts).
- Voz siempre arriba. Música **−18 a −22 dB bajo la voz**, con 4 dB más de bajada mientras habla el narrador.
- SFX suaves, nunca más fuertes que la voz. Única excepción: el timbre de muerte (breve).
- Música procedural, tranquila, con un color por época (tabla de la sección 7). Nada de golpes que tapen la voz. Tenochtitlan: se corta la música y queda silencio real.
- Sonido firma del canal: el "tic" del reloj. Aparece al cambiar de voz, en cada muerte y en el último plano.

## 3. Montaje base
- Cortes secos. Plano medio de 3 a 4 s. **Gancho (0:00–0:51): un corte cada ~1,1 s (~30 cortes).** Nunca la misma imagen dos veces seguidas.
- Cámara según columna `cam` del manifest: zoom lento, paneo o fijo. Movimiento suave; temblor solo donde lo pide la tabla de la sección 7.
- **Regla de retención:** ningún plano dura más de 5 s sin un cambio (zoom, texto, cambio de plano o sonido). Cada ~25 s tiene que pasar algo nuevo (dato grande, chiste, cartel).
- Largo: sin subtítulos de la voz; el texto en pantalla son solo los `overlay` del manifest. Tipografía bold sans (Montserrat ExtraBold o Bebas Neue), blanco con contorno negro, máx. 6 palabras, **nunca sobre la cara**.

## 4. Transiciones (columna `tr`)
`FLASH` flash blanco · `PUNCH` zoom de impacto con rampa de velocidad · `SMASH` corte seco al negro + timbre · `WHIP` barrido rápido · `GAME` el cartel sube desde abajo como pantalla de videojuego · `MATCH` corte por coincidencia (usá las imágenes 249–252 de puente: círculo, columna, arco, mano).
- Entre épocas, **siempre igual:** timbre del despertador → negro → flash blanco → arranca ya en movimiento. Sin fundidos, excepto **uno**: en Tenochtitlan el color se drena a gris.
- Cuadro de cine mudo (cuadrado con grano) al final de 1816 y al inicio de 1854.

## 5. Tiempo cómico (esto es lo que lo hace gracioso)
1. **Remate = 0,4–0,6 s de silencio antes y un golpe visual en la palabra clave** (zoom de impacto o corte).
2. **Frase del Despertador:** su pantalla aparece un instante antes de hablar; después de su frase, corte inmediato a Pijama reaccionando (1 s).
3. **Muerte:** freeze-frame de 0,5 s → SMASH al negro → timbre → tarjeta "LOGRO DESBLOQUEADO" (1,5 s) → cae el contador de AURA.
4. **Datos grandes:** siempre con la comparación visual del guion (Everest apilados, estadios, sésamo, pan a 8 dólares). El número sale en overlay justo cuando se dice.
5. Un chiste por idea. No repitas el mismo efecto cómico dos veces seguidas.
6. El Despertador cambia de actitud: épocas 1–4 se burla; 5–6 se queda sin chistes (en Tenochtitlan: dos segundos de silencio y "no voy a hacer ningún chiste"); 7–8 está de su lado; al final, "te lo mereces". Reflejalo en la música: del tic seco al tic más lento y suave.

## 6. HUD y juego (consistente, no recargado)
- Arriba, fijo: cronómetro "TU VIDA", "ÉPOCA N/8", corazones, contador AURA. Se actualizan solo cuando pasa algo.
- Cartel "JEFE: …" al arrancar cada época (1,5 s). Tarjeta "LOGRO DESBLOQUEADO" en las muertes marcadas. Tabla S–F de cierre: una fila por época, de a una.
- Mostrar 3 veces el cartel "Tiempos de Pijama = simulación".
- El **67** aparece solo 3 veces (aura −67, "6:07", "67 mil likes"). No agregues más.

## 7. Estilo por época
Solo cambian color y sonido; la estética base no cambia.
| # | Época | Color | Cámara y ritmo | Sonido firma |
|---|---|---|---|---|
| 1 | Hielo | azul-blanco, aliento visible | zooms rápidos a los pies | viento, dientes, silencio brusco |
| 2 | Egipto | dorado | planos fijos, humor seco | cincel, campana |
| 3 | Pompeya | naranja-gris | cámara que se sacude, zoom a la columna | temblor, estruendo, silencio |
| 4 | Roma | rojo-dorado, marcador | cámara lenta, repeticiones | multitud, relator, rugido |
| 5 | 1348 | verde apagado, niebla | planos largos | latidos, toses, carreta |
| 6 | 1519 | turquesa → gris | zoom estilo dron, luego quietud | flautas, tambores, silencio |
| 7 | 1816 | azul grisáceo, lluvia | planos lentos | lluvia, trueno, estómago |
| 8 | Londres | sepia | zoom al mapa | gotas, tic-tac, campanas |
| Cierre | Hoy | cálido | plano lento | canilla, sorbo, "ahh" |

## 8. Shorts (9 en total, mapa D del guion)
- Short 0 = tráiler; Shorts 1–8 = una época cada uno. Armado: línea 1 (gancho propio) → línea ⚑ de contexto → cuerpo **sin** las líneas ✂ → última línea (cliffhanger).
- Planos 16:9: recortá el centro a 9:16 (~432 px de ancho) y escalá a 1080×1920. Verticales del bloque SHORTS: usalas completas. Dejá libre el tercio superior para recap y título.
- Arriba: barra de recap con vidas y notas de épocas anteriores (imagen 240). Al final: tarjeta "PARTE N DE 8 · EL VIDEO COMPLETO ESTÁ EN MI CANAL" (imagen 239).
- Los primeros 2 s enganchan: gancho en voz + imagen fuerte + subtítulo grande. Corte cada 1,5–2,5 s.
- Duración 50–61 s. Subtítulos grandes palabra por palabra, con color de acento en la palabra dicha. Archivos `short_N_epoca.mp4` y tabla de duración real.

## 9. Exportación
- Largo: 1920×1080, 30 fps, H.264 (CRF ~18) + AAC 192 kbps, −14 LUFS. Shorts: 1080×1920, 30 fps, mismo códec.
- Sin marca de agua. Miniatura: NO (la hago aparte).

## 10. Flujo y verificación (en este orden)
1. **Primero:** tabla "calculado vs real" de la voz + lista de dudas (ids sin imagen, imágenes con defecto). **Esperá mi OK.**
2. Después: video largo y los 9 Shorts.
3. **Checklist antes de entregar** (reporte corto, cada ítem ✔/✘):
   - Ninguna imagen repetida seguida; ningún plano > 5 s sin cambio.
   - Ningún texto tapa una cara; ningún texto en inglés visible.
   - Música más baja que la voz; −14 LUFS medido, no supuesto.
   - Duración final = la medida, no la supuesta.
   - El 67 aparece exactamente 3 veces; "simulación" 3 veces.
   - Cada muerte lleva freeze + SMASH + timbre + logro; cada cambio de época, la transición fija.
   - Shorts: 50–61 s, gancho en los primeros 2 s, texto en el tercio central, tarjeta final.
4. Lista de la sección F del guion: marcá cada dato "verificado con fuente" o "dudoso" (con link). Lo dudoso lo suavizamos o lo sacamos.
5. Commit solo de archivos nuevos del video 2, en la rama actual.
