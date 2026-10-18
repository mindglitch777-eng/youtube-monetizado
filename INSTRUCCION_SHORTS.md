# INSTRUCCIÓN PARA CLAUDE CODE: serie de 7 Shorts (uno por cada forma de morir)

Esto REEMPLAZA la sección 5 ("El Short") de INSTRUCCION_CLAUDE_CODE.md y descarta el short resumido anterior (`short.mp4`). No quiero un solo Short que resuma todo. Quiero **7 Shorts independientes, uno por cada forma de morir (#7 a #1)**, más un Short 0 opcional con el gancho. Reutilizá la misma voz, las mismas imágenes, el mismo proyecto Remotion y las mismas funciones de la instrucción principal.

## 0. Qué salió mal en el Short anterior (no repetirlo)

Analicé `short.mp4` (63 s, 1080x1920):
1. **Los 6 primeros candados pasan en 2,5 s cada uno** (de 8 s a 24 s), solo con una imagen y el título "#N". Casi no hay voz ahí: queda música y silencio. No se entiende nada y no engancha.
2. **Tarjeta de ranking de ~14 s casi estática**, fondo negro, texto diminuto y con textos pisados (la etiqueta "ACCIDENTES, LEÓN INCLUIDO" se superpone con el subtítulo).
3. **La misma imagen del niño explorador se repite 3 veces seguidas** en la parte de los gérmenes.
4. **Las imágenes con franja ancha quedan chiquitas en el centro con bandas enormes desenfocadas arriba y abajo.** Más de la mitad de la pantalla es borroso.
5. Silencios de 0,5 a 0,7 s entre frases y un final con voz cortada; el cierre "El video completo está en mi canal" aparece con un segundo de silencio.
6. Subtítulos demasiado pequeños en las tarjetas de datos.

## 1. Qué hay que hacer: 7 Shorts, uno por bloque

Cada Short = un bloque del guion (`## #7 · SIN AGUA` ... `## #1 · LOS GÉRMENES`), con **su propio gancho al inicio y su propio cliffhanger al final**. Duraciones del bloque original: #7 50 s, #6 51 s, #5 51 s, #4 45 s, #3 49 s, #2 33 s, #1 59 s. Objetivo: **40-58 s cada uno** (el #1 puede llegar a 70 s). Nombrá los archivos `out/short_07_sin_agua.mp4`, `short_06_grandes_animales.mp4`, `short_05_lo_que_comes.mp4`, `short_04_la_noche.mp4`, `short_03_otras_personas.mp4`, `short_02_un_rasguno.mp4`, `short_01_germenes.mp4` y (opcional) `short_00_gancho.mp4` (el gancho de ~32 s con los 30 cortes, formato vertical).

### Estructura de cada Short
1. **0-2,5 s, GANCHO.** Empezá directo con la frase más fuerte del bloque sobre la imagen más llamativa, sin tarjeta de piedra, sin silencio. Ejemplos de la primera frase (podés ajustarla tomando una línea del propio bloque):
   - #7: "Son las 9 de la mañana. Tu boca ya sabe a lija."
   - #6: "El león sale en todas las películas. Pero casi nunca te mata."
   - #5: "Frutos rojos, brillantes, perfectos. Y tu cerebro dice: come."
   - #4: "El sol se va, y con él todo lo que veías."
   - #3: "Lo que más mataba era otra persona."
   - #2: "Una espina te abre el pie. Nada grave. Un corte chiquito."
   - #1: "La número uno no tiene colmillos. No tiene garras. No hace ruido."
2. **Insignia permanente arriba (zona segura):** "FORMA #N DE 7" y debajo los 7 candados pequeños (los ya mostrados abiertos, el actual cerrado). Al final del Short el candado actual se abre con `clic`.
3. **2,5 s - final-6 s, DESARROLLO.** La narración del bloque tal cual está en `guion_v3.md`, sin tarjeta de piedra larga (si querés conservarla, que dure 0,7 s y que el `golpe_piedra` suene al empezar la primera palabra, no antes).
4. **Últimos 5-6 s, CLIFFHANGER + LOOP.** Frase nueva (grabarla con la misma voz) que conecte con el siguiente y enlace visual con la primera imagen para que el Short se repita sin corte:
   - #7 → "Pero la sed no es lo peor. La siguiente tiene garras."
   - #6 → "Y el león no era el problema. Mira lo que te llevas a la boca."
   - #5 → "Hasta aquí sobrevivías. Ahora cae la noche."
   - #4 → "Pasas la noche. Pero alguien te está mirando."
   - #3 → "Escapas del grupo. Pero pisas una espina."
   - #2 → "Un rasguño. Y ahí entra el verdadero jefe."
   - #1 → "Y tú duras unas 20 horas. ¿Cuánto durarías tú? Cuéntamelo en los comentarios."
   Superpuesto en pantalla: "PARTE N DE 7 · SIGUE EN MI CANAL" (texto grande, sin repetir la voz).

## 2. Reglas para eliminar los silencios y el ritmo flojo

- **Cero aire muerto.** Procesá la voz de cada Short con `silenceremove` o equivalente: cualquier pausa mayor a 0,30 s se recorta a 0,18 s. Entre frases, pausa máxima 0,25 s (salvo 0,5 s antes de un golpe: "Es mentira.", "La número uno ni siquiera la ves").
- **Siempre hay voz o hay un sonido de efecto.** Si el bloque tiene un tramo sin narración, quitalo o rellenalo con una línea de voz del propio guion.
- **Ritmo:** un cambio de imagen cada 2-3 s (promedio 2,5 s, máximo 3,5 s). Corte duro. Cada imagen con zoom lento (1,0 → 1,08) o un micro movimiento. Un cambio de patrón (reacción, golpe de sonido, texto grande) a la mitad.
- **Nunca repitas la misma imagen seguida**. Si el bloque tiene pocas imágenes, alterná con las de `tipo: reaccion` del mismo bloque y con las del manifest que tengan el mismo `block`.
- **Música a -22 dB** con ducking bajo la voz. Efectos de 8 dB sobre la música. Normalizá a -14 LUFS al final.

## 3. Imágenes en formato vertical (esto arregla el 80 % de lo malo que se ve)

Las imágenes vienen 768x1376 y de dos tipos (ver `work/img_info.json` de la instrucción principal):
- **Tipo B (vertical completa):** usalas a pantalla completa con `cover`, el sujeto centrado. Es la mejor opción para el Short; priorizalas.
- **Tipo A (franja ancha en el medio):** NO las dejes pequeñas rodeadas de blur. Ponelas ancho completo (1080 px de ancho) en el centro de la pantalla, y convertí el espacio de arriba y de abajo en elementos útiles: arriba la insignia "FORMA #N DE 7" + candados + un título en letras grandes, abajo los subtítulos grandes. El fondo de esos espacios: un color liso tomado del borde de la imagen (no el blur), con degradado suave hacia la imagen. Máximo 40 % de blur oscurecido si se usa.
- Si en un bloque hay menos de 4 imágenes tipo B, generá una lista `work/regenerar_vertical.txt` con los ids y yo las rehago en vertical.
- Las imágenes de reacción (tipo B) van como cortes rápidos de 1-1,5 s con zoom de 1.12.

## 4. Subtítulos y texto en pantalla

- Subtítulos palabra por palabra, **altura mínima de letra 72 px a 1080 de ancho**, amarillo `#FFE600` con borde negro 8 px, palabra activa en blanco con escala 1.12, 3-4 palabras por línea, ubicados entre el 60 % y el 75 % del alto de la pantalla (zona segura de Shorts: no tapar el 10 % superior ni el 20 % inferior).
- Texto de overlay (campo `overlay` del manifest): tamaño grande, borde negro, entrada con pop de 4 frames. Nunca dos textos pisándose: si hay un overlay, el subtítulo sube 80 px.
- Las tarjetas de datos (12 personitas, 8 personitas, 7 de 10) a pantalla completa vertical, con números enormes (mínimo 160 px), personitas grandes y la animación sincronizada con la voz.

## 5. Short #1: el ranking final

Rediseñá la tarjeta del ranking para vertical: fondo oscuro, **3 barras grandes** (ancho completo, alto 160 px) que crecen una por una exactamente cuando la voz dice cada cifra. Texto de cada barra mínimo 64 px, sin texto diminuto. Debe durar **máximo 9 s**, no 14. Cifras (las mismas que dice la voz, de Gurven y Kaplan 2007, 3.328 muertes, todas las edades):
- ENFERMEDAD Y GÉRMENES · 7 DE CADA 10 (~70 %)
- VIOLENCIA (OTRAS PERSONAS) · 1 DE CADA 8 (12,5 %)
- ACCIDENTES, LEÓN INCLUIDO · MENOS DE 1 DE CADA 12 (8,1 %)
Pie pequeño y legible (32 px): "Gurven y Kaplan, 2007. Grupos de cazadores-recolectores recientes, no de hace 20.000 años."
En la parte de los gérmenes usá varias imágenes distintas (negro con gérmenes, Pijama verde, las tres puertas, el vaso de agua sucia, León con mascarilla), no la misma tres veces.

## 6. Metadatos para publicar (generá `out/publicacion.md`)

Para cada Short escribí: título (máx. 60 caracteres, con gancho y número, por ejemplo "Forma #7 de morir en la Edad de Piedra: SIN AGUA"), descripción de 2 líneas, 5 hashtags (#shorts #edaddepiedra #historia #curiosidades #supervivencia), el comentario fijado ("Parte 2 de 7 aquí 👇" y el enlace al video completo), y el orden y la hora de publicación sugerida: **uno por día, de la #7 a la #1** (la #1 el último día, y el Short 0 de gancho el día anterior a la #7). En la descripción del primero y del último dejá claro el enlace al video largo.

## 7. Verificación antes de entregar

Para cada Short comprobá y corregí: duración entre 40 y 70 s; ninguna pausa de voz de más de 0,4 s; ningún plano de más de 3,5 s ni la misma imagen dos veces seguidas; ningún texto fuera de la zona segura ni superpuesto; el candado del bloque se abre con `clic` al final; audio a -14 LUFS; que el primer segundo ya tenga voz y una imagen potente. Extraé 12 fotogramas por Short y revisalos. Entregá `out/short_*.mp4`, `out/publicacion.md` y `out/regenerar_vertical.txt`.
