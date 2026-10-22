# Video 2 · Paso 1: voz medida y dudas

La voz se generó con edge-tts. El narrador es **es-MX-JorgeNeural**, la misma voz del video 1, grabado a dos velocidades: +0 % y +8 %. El Despertador se grabó con dos voces candidatas: **es-US-AlonsoNeural** y **es-CO-GonzaloNeural**. Las líneas ⚑ (solo para Shorts) no cuentan para el video largo. Los "extras" (separadores, tabla y pausas) se toman de la tabla C, porque no son voz.

## 1. Duración: calculado vs. real

edge-tts agrega cerca de 1 s de silencio al principio y al final de cada línea, y una pausa de unos 0,86 s en cada punto dentro de una línea. Por eso la duración depende de cuánto se recorte:

| Versión | Narrador +0 % | Narrador +8 % (como el video 1) |
|---|---|---|
| Audio tal cual sale (sin recortar nada) | 14:24 ❌ | 13:35 ❌ |
| Recortando solo el silencio del principio y del final de cada línea | 11:38 ❌ | **10:59 ✅** |
| Además, pausas dentro de la línea de 0,86 s a 0,4 s | 10:50 ✅ | 10:16 ✅ |

Rango pedido: 9:45 a 11:15. Calculado en la tabla C: 10:34 (10:32 en el guion).

**Por bloque**, con la versión recomendada (+8 %, recortando solo los bordes):

| Bloque | Voz calculada (s) | Voz real (s) | Diferencia |
|---|---|---|---|
| Gancho-tráiler | 50 | 56,4 | +6,4 |
| Época 1 · Hielo | 53 | 52,6 | −0,4 |
| Época 2 · Egipto | 56 | 63,8 | +7,8 |
| Época 3 · Pompeya | 65 | 67,7 | +2,7 |
| Época 4 · Roma | 48 | 51,1 | +3,1 |
| Mitad · tabla parcial | 16 | 15,3 | −0,7 |
| Época 5 · 1348 | 53 | 55,7 | +2,7 |
| Época 6 · Tenochtitlan | 55 | 51,3 | −3,7 |
| Época 7 · 1816 | 70 | 71,8 | +1,8 |
| Época 8 · Londres | 54 | 57,6 | +3,6 |
| Cierre y tabla | 60 | 61,4 | +1,4 |
| **Total con extras (54 s)** | **10:34** | **10:59** | **+25 s** |

**Shorts** (+8 %, sin las líneas ✂, más 1,5 s de tarjeta final; meta 50–61 s):

| Short | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|---|
| Segundos | 57,9 | 53,0 | **65,9** | **64,5** | 57,4 | 60,3 | 58,0 | **64,2** | 58,3 |

Los Shorts 2, 3 y 7 se pasan de 61 s.

## 2. Dudas (espero tu respuesta antes de armar el video)

1. **Velocidad y recorte.** Recomiendo **+8 % recortando solo los bordes (10:59)**: es la voz del video 1 y mantiene las pausas naturales. ¿Va así, o preferís +0 % con las pausas acortadas (10:50)?
2. **Voz del Despertador.** ¿Alonso o Gonzalo? (muestras `2_despertador_*.mp3`). Las dos ya llevan el "tic" y el filtro metálico leve.
3. **Pronunciación** (muestra `1_pronunciacion.mp3`): Deir el-Medina, Vesubio, Tenochtitlan, Tambora, Cuitláhuac, Ginebra, John Snow, Plinio y Soho. Cuitláhuac y Ginebra no están en la voz del guion; las probé igual. Decime si alguna suena mal y la corrijo escribiéndola como se pronuncia.
4. **Imágenes con franjas.** No son "algunas": más de la mitad de las 16:9 vienen partidas en 3 paneles con líneas negras. Recortar el centro, como dice la instrucción, en las de 3 paneles significa agrandarlas unas 4 veces: se ven blandas y a veces se corta la cabeza o el cuerpo. Te mandé la comparación de las opciones A, B y C. ¿Cuál usamos?
5. **Texto en inglés** en 12 imágenes. Lo tapo con un overlay o lo recorto:
   - 011 "OFF" y 041 "CLICK!";
   - 071 "LEVEL COMPLETE";
   - 073, 080 y 090 "BAKERY", y 084 y 092 "BAKERIE";
   - 138 "RING! RING!";
   - 191 "SOHO London Map";
   - 221 "GAME" y "S TIER / A TIER";
   - probablemente nombres chicos en el mapa de la 175.
6. **Transiciones 249–252:** vienen verticales (9:16), pero son para cortes entre épocas en el video largo (16:9). ¿Las uso con la opción que elijas en el punto 4, o solo en los Shorts?
7. **Ids sin imagen.** Así los cubro; los 001–007 son hojas de referencia y no van en pantalla:
   - **032** "Y no, no puedes apagarme" → sigue la 031 con zoom de impacto y "tic".
   - **036** "Y ya no los sientes" → zoom a los pies de la 035 y escarcha que avanza.
   - **069/070** "Cuarenta y un años" → la 068 con el cronómetro del HUD saltando a "41 AÑOS".
   - **099/100** "Miren cómo camina… Descalzo. Con estrellas." → la 095, y después la 097 en cámara lenta con el cartel "REPETICIÓN".
   - **196** "Algo suena diferente" → la 195, y corte a la 197 (cartel de resultados).
8. **Líneas entre comillas que no son del Despertador:**
   - el relator de Roma (E4_01 y E4_05);
   - el grito de Egipto ("¡Tú! ¡A trabajar!");
   - "Qué espectáculo", que dice Pijama;
   - el cartel de la huelga.
   
   Propongo que las diga el narrador, con un filtro de megáfono o estadio solo para el relator. ¿Va?
9. **Shorts 2, 3 y 7 duran entre 64 y 66 s** (máximo pedido: 61). ¿Acorto las pausas solo en esos tres, o sacamos alguna línea más de cada uno?
