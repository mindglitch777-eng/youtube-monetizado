"""Corredor para GitHub Actions: busca content-kai/*/audio/preview_request.json
y llama kai_voces_preview.py con lo que diga cada uno. Separado del workflow
YAML para no meter Python multilínea dentro de un bloque `run:`."""

import glob
import json
import subprocess

for ruta in glob.glob("content-kai/*/audio/preview_request.json"):
    req = json.load(open(ruta, encoding="utf-8"))
    print(f"::group::{ruta}")
    subprocess.run(
        ["python", "scripts/kai_voces_preview.py", req["texto"], req["carpeta"], *req["voces"]],
        check=True,
    )
    print("::endgroup::")
