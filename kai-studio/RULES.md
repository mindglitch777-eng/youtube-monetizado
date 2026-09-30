# REGLAS KAI — fuente única (pegar en el CLAUDE.md / reglas de Claude Code)

Dos canales, **Kai (inglés)** y **Kai (español)**. Mismo personaje, mismas imágenes, misma estructura. Cambian la voz, los subtítulos y los textos en pantalla.
Objetivo: monetizar. Se logra con volumen + ganchos fuertes + iteración con datos, no con una sola jugada.

---
## 1. Estructura de cada Short "Top 5" (fórmula de retención)
1. **Hook en segunda persona** que acusa al espectador en la primera frase. Nada de "hoy vamos a hablar de".
2. **Promesa numérica** con identidad amplia ("5 señales de…") y **gancho a mitad del hook**: el número 1 se promete al inicio y se entrega al final ("Stay for number one").
3. **Línea de presentación de la serie** tras el gancho: grilla de 5 paneles con las 5 tácticas (Kai exagerado) + zoom rápido al tema del día.
4. **Cuenta regresiva 5→1**, contador visible en pantalla; cada número escala (el 5 incomoda, el 3 duele, el 1 es el que se niega).
5. **Cada número cierra con un gancho** que promete algo peor en el siguiente.
6. **Regla de tres** rítmica en el punto más fuerte y **una opinión discutible** que haga comentar.
7. **Un remate corto y chistoso por número** (tono: agresivo + chistoso). El humor va contra la situación o la conducta, nunca contra una persona o grupo.
8. **CTA de una sola acción** ("Comment your number." / "Comenta tu número.") y **cierre seco**: corte al terminar el audio, sin despedida ni pantalla final.
9. Compilados largos: reenganche cada 80-100 s.

## 2. Guion (agresivo, pero seguro para monetizar)
- Frases cortas y cortantes: **8-10 palabras máximo**. Sin relleno.
- Hablar de **conductas, nunca de personas**: "eso que hace", no "es un narcisista". Sin diagnósticos clínicos, sin consejos médicos/terapéuticos, sin nombres reales, sin grupos protegidos como blanco del chiste.
- Cada línea muestra una **situación cotidiana y actual** con la que el espectador se identifica.
- Entregar siempre: guion línea por línea **EN**, cuántas imágenes lleva cada línea, **2 versiones de gancho de apertura** para probar, y luego la **adaptación al español neutro** (no traducción literal; sin modismos de un solo país: "tú", no "vos").
- Antes de escribir, revisar los datos ya investigados (primeros 2 s de los mejores videos del nicho y comentarios). Se copia la **estructura**, nunca frases ni contenido.

## 3. Anti "contenido inauténtico" (riesgo real para entrar al Programa de Socios)
YouTube revisa el **canal completo** y rechaza lo que parece plantilla repetida a escala. Para no caer:
- **Variar formatos** entre videos: Top 5, POV/historia corta, "respondiendo un comentario", mito vs. realidad, reacción a situación.
- **Humor y opinión propia** en cada guion (no se puede replicar a escala).
- **Revisión humana** de cada guion y cada video antes de publicar. Cambiar la estructura del gancho de un video al siguiente.
- Nada de contenido reciclado de otros creadores.
- En el formulario de subida: marcar "no hecho para niños" y **revisar si hay que declarar contenido alterado/sintético** (estilo dibujo animado normalmente no, pero se confirma en el formulario).

## 4. Imágenes (Google Flow, a mano)
- 9:16 vertical, **sin texto ni números dentro de la imagen** (los pone Remotion). Zona segura: 15% superior y 20% inferior vacíos.
- **Cada prompt es completo y autosuficiente** (descripción larga y fija de Kai dentro). Bloques exactos en `prompts/kai-character.md`.
- El **celular encendido** aparece en todas las escenas (elemento visual recurrente).
- Fondo por sección (ver `prompts/kai-character.md`). Nada de fondos amarillos/mostaza.
- Kai **exagerado** solo en grillas de serie y momentos absurdos.
- Cantidad: **Top 5 insignia 45-47 imágenes**; videos de volumen (POV, mitos) **12-32**. 2-3 imágenes por oración cuando la frase tiene varios elementos; 1 si es transición. Mínimo **1,0 s** por imagen.
- Nombres: `kai-p<parte>-<NN>.png` (`kai-p1-01.png` … `kai-p1-47.png`). Se generan **todas el mismo día** para que el estilo no se corra. Si una sale con el hoodie de otro tono o la cara deformada, se regenera antes de montar.
- Organizador: `tools/organize_images.py` (ver README). La hoja de contacto se revisa **antes** de gastar voz y render.

## 5. Sonido
- Voz siempre al **100%** y por encima de todo.
- Música oscura y suave en loop a **-22 dB**, baja **-6 dB más** mientras habla la voz; se corta antes de la línea final.
- SFX a **-12 dB**, colocados **2-3 frames ANTES** del corte visual.
- **Whoosh** solo en cortes de ganchos y cambios de contador (no en todos los cortes). **Impacto** en cada cambio del contador. **Golpe grave (thud)** al inicio de cada gancho. **Riser** 1-2 s antes del zoom a la grilla y **impacto seco** al caer en el panel. **Notificación** en escenas donde el celular es protagonista.
- **0,5 s de silencio** antes de la última línea (CTA), sin música ni SFX.
- Solo sonidos libres para uso comercial (Pixabay, YouTube Audio Library, Freesound CC0). Registrar fuente y licencia de cada uno en `public/sfx/LICENCIAS.md`.
- Mostrar **preview** antes del render final.

## 6. Remotion (1080x1920, 30 fps)
- Duración de cada línea = duración de su audio. Imágenes de una línea repartidas en partes iguales (mín. 1,0 s).
- Cortes secos, sin fundidos. **Movimiento**: zoom lento en imágenes impares, paneo en las pares. Zoom acelerado a la grilla en la línea de presentación.
- Ganchos: corte seco + **0,15 s de aire** antes de la línea siguiente.
- **Contador** 5→1 en la zona superior: aparece en el 5, cambia con cada número, se oculta en apertura y cierre.
- **Subtítulos palabra por palabra** activos el 100% del tiempo, blanco con borde negro, **palabra activa en mostaza #E1A11B**, a ~67% de la altura (fuera del 20% inferior).
- Título y etiquetas de la grilla los pone Remotion (la IA deforma las letras).
- Última línea: corte seco al terminar el audio.

## 7. Dos canales
- Cada parte sale en **los dos idiomas**, mismo día, en horarios distintos (EN: tarde/noche de EE. UU.; ES: noche de Latinoamérica).
- Un **canal separado por idioma** (no mezclar idiomas en un mismo canal).
- Español **neutro**. Voz es-MX o es-US; probar 2-3 y elegir.
- Mismas 47 imágenes: solo cambian `episodes/<slug>/<lang>/script.json`, la voz y los textos en pantalla.
- TikTok: hashtags y texto en el idioma del canal. No se necesita VPN para empezar; se mira de dónde vienen los espectadores a las 24-48 h y se decide.

## 8. Publicación (checklist)
Título (con 🚩 opcional) · descripción de 2-3 líneas con pregunta · hashtags (`#lovebombing #toxicrelationships #manipulation #psychology #redflags #shorts`) · comentario fijado con la pregunta del número · "no hecho para niños" · responder los primeros comentarios en los primeros 30-60 min · **no borrar ni reemplazar** un video flojo en las primeras horas.

## 9. Medición (para no improvisar)
Completar `tracking/videos.csv` a las 24 h, 48 h y 7 días: vistas, % promedio visto, **segundo donde cae la gente**, país principal, suscriptores ganados, versión de gancho. Con eso se endurece lo que no retiene y se duplica lo que sí.

## 10. Metas de monetización (YouTube)
- Nivel chico: 500 suscriptores + 3 M vistas de Shorts en 90 días (o 3.000 h en 12 meses).
- Completo: 1.000 suscriptores + 10 M vistas de Shorts en 90 días (o 4.000 h en 12 meses).
- **Desde el 1/feb/2027 los requisitos se duplican** (8.000 h o 20 M vistas). Plazo de fondo: calificar antes de esa fecha. Meta ambiciosa: octubre.
