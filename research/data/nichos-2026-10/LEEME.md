# Datos crudos — investigación de nichos faceless (14/10/2026)

Generados con `research/nichos_faceless.py` (API de YouTube Data v3). Cuota gastada: ver `cuota.json`.

| Archivo | Qué tiene |
|---|---|
| `busquedas.json.gz` | las 52 búsquedas (tema, idioma, consulta) con sus resultados crudos |
| `videos_busqueda.json.gz` | detalle (snippet, stats, duración) de cada video encontrado |
| `canales.json.gz` | detalle de los 1.564 canales encontrados |
| `uploads.json` | IDs de los últimos 50 videos de cada canal < 200k subs |
| `videos_canales_resumen.json.gz` | título, fecha, duración, vistas, likes, comentarios y tags de esos ~50.000 videos |
| `canales_metricas.csv/json` | métricas por canal (creación, subs, vistas, mediana de los últimos 10, % Shorts, video más visto) |
| `outliers.csv/json` | videos con ≥3x la mediana de su canal y ≥50k vistas |
| `videos_top_completos.json` | respuesta completa de la API (descripción, tags) de los 16 videos analizados |

Para volver a correr `enrich` hay que descomprimir los `.gz` (el script lee los `.json` sin comprimir).
El informe se arma con `python3 research/informe/build_informe.py` → `research/informe/nichos-faceless.html`.
