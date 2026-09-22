# Respaldo — proveedores de imágenes descartados

Nada de esta carpeta forma parte del pipeline. El proveedor en uso es
**Cloudflare Workers AI** (`scripts/generar_imagenes.py`).

| Proveedor | Estado | Motivo |
|---|---|---|
| Gemini API | Descartado, sin código | Requiere facturación (cuota gratuita 0 para modelos de imagen). |
| Pollinations.ai | `generar_imagenes_pollinations.py` | El acceso anónimo ignora modelo, tamaño y `nologo` (marca de agua). |
| Hugging Face (FLUX.1-schnell) | Descartado, sin código | Se reemplazó por Cloudflare antes de implementarlo. |
