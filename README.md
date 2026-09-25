# Knotwise — pipeline de producción automatizada

Canal de YouTube faceless en inglés (psicología de relaciones y dinámicas 
sociales): videos largos + shorts reciclados, producidos con Claude Code + 
Cloudflare Workers AI (flux-1-schnell) + Edge-TTS + Remotion.

Ver RULES.md antes de generar o publicar cualquier contenido — todas las 
reglas ahí son obligatorias.

## Calendario
- 2 videos largos por semana.
- 6 shorts reciclados por video (1 por bloque), vertical 9:16, hasta 180 s.

## Pipeline
1. El guion se escribe en el chat con Claude Code a partir de un tema, siguiendo RULES.md: 6 bloques (Hook, Gancho2, Cuerpo, Pago), sin intro, con solo el sonido de transición (whoosh) entre bloques, y un único CTA al final del último bloque. Se guarda en content/<nombre-video>/guion.md y se valida con `python scripts/validar_guion.py content/<nombre-video>/guion.md` — solo se sigue al paso 2 si termina en "LISTO PARA GENERAR IMÁGENES"
2. scripts/generar_audio.py → genera la narración con Edge-TTS y timeline.json.
3. scripts/generar_imagenes.py → genera las escenas con Cloudflare Workers AI (flux-1-schnell) y vuelve a correr generar_audio.py para actualizar timeline.json con las imágenes.
4. remotion/ → ensambla el video largo (`Video`) y los shorts (`Short`, uno por bloque) con imágenes + audio + subtítulos + sonido de marca + ícono de Knot.

## Qué corre dónde
| Paso | Dónde | Cómo se dispara |
|---|---|---|
| Voz (generar_audio.py) | GitHub Actions — `generar-voz.yml` | Automático al cambiar un `content/*/guion.md` |
| Imágenes (generar_imagenes.py) | GitHub Actions — `generar-imagenes.yml` | Al cambiar `content/<video>/imagenes/pedido.txt` (`--solo N` o vacío para el lote) |
| Sonidos de marca | GitHub Actions — `descargar-sonidos.yml` | Al cambiar `assets/sonido/fuentes.tsv` |
| Video largo y shorts (Remotion) | A mano | Ver remotion/README.md |

Los workflows commitean sus resultados en la misma rama. Las credenciales de 
Cloudflare van como secretos del repositorio (`CLOUDFLARE_ACCOUNT_ID`, 
`CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_R2_ACCESS_KEY_ID`, 
`CLOUDFLARE_R2_SECRET_ACCESS_KEY`) y, para correr local, en `.env` (ver 
`.env.example`).

**Nunca se pierde lo ya generado.** `generar_imagenes.py` y `generar_short.py` 
commitean y pushean cada imagen (y la voz) apenas termina, no solo al final 
(`scripts/segmentos.py`, función `checkpoint`; solo actúa dentro de GitHub 
Actions). Si el workflow se corta a mitad de camino — se agota el tiempo, se 
cae la red, un modelo falla — lo generado hasta ese momento ya quedó en la 
rama, y correrlo de nuevo retoma justo donde quedó: las imágenes que ya 
existen no se vuelven a pagar ni regenerar. El paso final "Commitear" de cada 
workflow es solo un respaldo por si algo quedó sin subir.

Los proveedores de imágenes descartados (Gemini, Pollinations, Hugging Face) 
están documentados en scripts/respaldo/, fuera del flujo principal.
