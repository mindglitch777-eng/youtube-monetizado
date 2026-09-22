# Canal Knot — pipeline de producción automatizada

Canal de YouTube faceless en inglés (psicología de relaciones y dinámicas 
sociales), producido con Claude Code + Gemini API + Edge-TTS + Remotion.

Ver RULES.md antes de generar o publicar cualquier contenido — todas las 
reglas ahí son obligatorias.

## Pipeline
1. scripts/generar_guion.py → genera guion.md encadenando 6 bloques (Hook, Gancho2, Cuerpo, Pago), con intro fija, transiciones fijas entre bloques, y un único CTA al final del último bloque
2. scripts/generar_imagenes.py → genera las escenas con Gemini API (Nano Banana)
3. scripts/generar_audio.py → genera narración con Edge-TTS
4. remotion/ → ensambla imagenes + audio + subtítulos + sonido de marca
