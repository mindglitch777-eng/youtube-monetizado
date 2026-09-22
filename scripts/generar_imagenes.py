"""Genera las escenas de un video con la API de Gemini.

Uso:
    python scripts/generar_imagenes.py content/<nombre-video>/guion.md [opciones]

Opciones:
    --dry-run   Solo arma los prompts (imagenes/prompts.json), sin llamar a la API.
    --solo N    Genera únicamente la imagen número N (para probar antes del lote).
    --yes       No pide confirmación antes de gastar llamadas a la API.
    --forzar    Regenera también las imágenes que ya existen.

Una imagen por escena: Hook, Gancho 2, cada ejemplo del Cuerpo y Pago de cada
bloque (36 en un video de 6 bloques). Las escenas muestran siluetas humanas
simples, nunca a Knot: Knot aparece aparte, como ícono de marca en Remotion.
Las imágenes existentes se saltean para no pagar dos veces la misma escena.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

from segmentos import cargar_env, leer_guion, nombre_base, validar_o_salir

MODELO = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image")
EXTENSIONES = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}

# RULES.md, sección "Estilo visual de las escenas humanas".
ESTILO = (
    "Soft digital painting in a gentle storybook style with painterly textures, "
    "cinematic 16:9 composition. People are shown as simple human silhouettes "
    "without detailed facial features. The setting is an everyday, easily "
    "recognizable place (a living room, kitchen, bedroom, hallway, car or cafe)."
)
ESTILO_POR_TIPO = {
    # Cuerpo: paleta más fría y encuadre cerrado.
    "ejemplo": "Cooler palette (muted blues, grey-teal, soft cool shadows). Tight, close "
               "framing on one or two silhouettes (medium close-up), focused on posture "
               "and body language.",
    # Pago: paleta cálida y encuadre abierto.
    "pago": "Warm palette (soft amber, gold and warm browns, gentle warm light). Wide, "
            "open framing that shows the whole room with breathing space around the "
            "silhouettes, calm and reassuring.",
    # Hook y Gancho 2: RULES.md no los define; término medio entre los dos.
    "hook": "Balanced palette between cool and warm tones. Medium framing.",
    "gancho2": "Balanced palette between cool and warm tones. Medium framing.",
}
PROHIBIDO = (
    "Do not include any text, letters, captions, subtitles, logos or watermarks. "
    "Do not include owls, birds or any animal characters."
)


def armar_prompt(titulo, segmento):
    return (
        f"{ESTILO} {ESTILO_POR_TIPO[segmento['tipo']]}\n\n"
        f"This image is one scene of a video titled \"{titulo}\", about relationship "
        f"psychology and social dynamics.\n"
        f"Illustrate the moment described by this narration, with one or two "
        f"simple human silhouettes whose posture and body language convey the "
        f"emotion:\n\"{segmento['texto']}\"\n\n"
        f"{PROHIBIDO}"
    )


def existente(carpeta, base):
    return next(iter(sorted(carpeta.glob(base + ".*"))), None)


def generar(cliente, prompt):
    from google.genai import types

    config = types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(aspect_ratio="16:9"),
    )
    for intento in range(3):
        try:
            respuesta = cliente.models.generate_content(
                model=MODELO, contents=[prompt], config=config)
            for candidato in respuesta.candidates or []:
                for parte in (candidato.content.parts if candidato.content else []):
                    if parte.inline_data and parte.inline_data.data:
                        return parte.inline_data.data, parte.inline_data.mime_type
            raise RuntimeError("la respuesta no trajo ninguna imagen")
        except Exception as error:  # noqa: BLE001 - se reintenta cualquier fallo de la API
            codigo = getattr(error, "code", None)
            if codigo == 429 and "limit: 0" in str(error):
                sys.exit("La API key no tiene cuota para este modelo (plan gratuito con límite 0). "
                         "Hay que activar la facturación en el proyecto de Google AI Studio.")
            if isinstance(codigo, int) and 400 <= codigo < 500 and codigo != 429:
                raise
            if intento == 2:
                raise
            espera = 2 ** (intento + 1)
            print(f"    reintentando en {espera}s ({error})")
            time.sleep(espera)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("guion")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--solo", type=int)
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--forzar", action="store_true")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    ruta_guion = Path(args.guion)
    validar_o_salir(ruta_guion)
    titulo, segmentos = leer_guion(ruta_guion)
    escenas = [s for s in segmentos if s["ilustrar"]]

    carpeta = ruta_guion.parent / "imagenes"
    carpeta.mkdir(parents=True, exist_ok=True)
    prompts = {nombre_base(s): armar_prompt(titulo, s) for s in escenas}
    (carpeta / "prompts.json").write_text(
        json.dumps(prompts, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.solo:
        escenas = [s for s in escenas if s["numero_imagen"] == args.solo]
        if not escenas:
            sys.exit(f"No existe la escena número {args.solo}.")

    pendientes = [s for s in escenas
                  if args.forzar or not existente(carpeta, nombre_base(s))]
    print(f"{len(escenas)} escenas, {len(pendientes)} por generar con {MODELO}.")
    print(f"Prompts guardados en {carpeta / 'prompts.json'}")
    if args.dry_run or not pendientes:
        return

    cargar_env()
    clave = os.environ.get("GEMINI_API_KEY")
    if not clave:
        sys.exit("Falta GEMINI_API_KEY en .env")
    if not args.yes:
        respuesta = input(f"Esto hace {len(pendientes)} llamadas pagas a la API. ¿Seguir? (s/N) ")
        if respuesta.strip().lower() not in ("s", "si", "sí", "y", "yes"):
            sys.exit("Cancelado, no se llamó a la API.")

    from google import genai
    cliente = genai.Client(api_key=clave)
    for s in pendientes:
        base = nombre_base(s)
        print(f"  {base} ...", flush=True)
        datos, mime = generar(cliente, prompts[base])
        viejo = existente(carpeta, base)
        if viejo:
            viejo.unlink()
        destino = carpeta / (base + EXTENSIONES.get(mime, ".png"))
        destino.write_bytes(datos)
        print(f"    guardada: {destino}")
    print("Listo.")


if __name__ == "__main__":
    main()
