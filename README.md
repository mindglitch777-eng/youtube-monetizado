# Canal Knot — pipeline de producción automatizada

Canal de YouTube faceless en inglés (psicología de relaciones y dinámicas 
sociales), producido con Claude Code + Gemini API + Edge-TTS + Remotion.

Ver RULES.md antes de generar o publicar cualquier contenido — todas las 
reglas ahí son obligatorias.

## Pipeline
1. El guion se escribe en el chat con Claude Code a partir de un tema, siguiendo RULES.md: 6 bloques (Hook, Gancho2, Cuerpo, Pago), con intro fija, transiciones fijas entre bloques, y un único CTA al final del último bloque. Se guarda en content/<nombre-video>/guion.md y se valida con `python scripts/validar_guion.py content/<nombre-video>/guion.md` — solo se sigue al paso 2 si termina en "LISTO PARA GENERAR IMÁGENES"
2. scripts/generar_imagenes.py → genera las escenas con Gemini API (Nano Banana)
3. scripts/generar_audio.py → genera narración con Edge-TTS
4. remotion/ → ensambla imagenes + audio + subtítulos + sonido de marca
