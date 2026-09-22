"""RESPALDO, fuera del flujo principal: versión con Pollinations.ai.

El proveedor en uso es Cloudflare Workers AI (scripts/generar_imagenes.py).
Para volver a usar este script, copiarlo a scripts/ (importa segmentos.py).

Uso:
    python scripts/respaldo/generar_imagenes_pollinations.py content/<nombre-video>/guion.md [opciones]

Opciones:
    --dry-run   Solo arma los prompts (imagenes/prompts.json), sin descargar nada.
    --solo N    Genera únicamente la imagen número N (para probar antes del lote).
    --forzar    Regenera también las imágenes que ya existen.

Una imagen por escena: Hook, Gancho 2, cada ejemplo del Cuerpo y Pago de cada
bloque (36 en un video de 6 bloques). Las escenas muestran siluetas humanas
simples, nunca a Knot: Knot aparece aparte, como ícono de marca en Remotion.
Las imágenes que ya existen se saltean. Entre pedido y pedido se esperan 16
segundos: el nivel gratis anónimo de Pollinations permite 1 cada 15 segundos.
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from segmentos import leer_guion, nombre_base, validar_o_salir

URL_BASE = "https://image.pollinations.ai/prompt/"
PARAMETROS = {"width": 1024, "height": 1024, "nologo": "true"}
ESPERA_ENTRE_PEDIDOS = 16
TIMEOUT = 180
EXTENSIONES = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}

# RULES.md, sección "Estilo visual de las escenas humanas".
ESTILO = (
    "Soft digital painting in a gentle storybook style with painterly textures, "
    "cinematic composition. People are shown as simple human silhouettes "
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
        f"{ESTILO} {ESTILO_POR_TIPO[segmento['tipo']]} "
        f"This image is one scene of a video titled \"{titulo}\", about relationship "
        f"psychology and social dynamics. "
        f"Illustrate the moment described by this narration, with one or two "
        f"simple human silhouettes whose posture and body language convey the "
        f"emotion: \"{segmento['texto']}\" "
        f"{PROHIBIDO}"
    )


def armar_url(prompt):
    return URL_BASE + urllib.parse.quote(prompt, safe="") + "?" + urllib.parse.urlencode(PARAMETROS)


def existente(carpeta, base):
    return next(iter(sorted(carpeta.glob(base + ".*"))), None)


def descargar(url):
    """GET a la URL de Pollinations. Reintenta ante límites (429) o errores del servidor."""
    pedido = urllib.request.Request(url, headers={"User-Agent": "knot-pipeline/1.0"})
    for intento in range(3):
        try:
            with urllib.request.urlopen(pedido, timeout=TIMEOUT) as respuesta:
                tipo = respuesta.headers.get_content_type()
                datos = respuesta.read()
            if not tipo.startswith("image/"):
                raise RuntimeError(f"la respuesta no es una imagen ({tipo})")
            return datos, tipo
        except (urllib.error.URLError, TimeoutError, RuntimeError) as error:
            codigo = getattr(error, "code", None)
            if isinstance(codigo, int) and 400 <= codigo < 500 and codigo != 429:
                raise
            if intento == 2:
                raise
            espera = ESPERA_ENTRE_PEDIDOS * (intento + 2)
            print(f"    reintentando en {espera}s ({error})", flush=True)
            time.sleep(espera)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("guion")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--solo", type=int)
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
    print(f"{len(escenas)} escenas, {len(pendientes)} por generar con Pollinations.ai.")
    print(f"Prompts guardados en {carpeta / 'prompts.json'}")
    if args.dry_run or not pendientes:
        return

    for n, s in enumerate(pendientes):
        if n:
            time.sleep(ESPERA_ENTRE_PEDIDOS)
        base = nombre_base(s)
        print(f"  {base} ...", flush=True)
        datos, tipo = descargar(armar_url(prompts[base]))
        viejo = existente(carpeta, base)
        if viejo:
            viejo.unlink()
        destino = carpeta / (base + EXTENSIONES.get(tipo, ".jpg"))
        destino.write_bytes(datos)
        print(f"    guardada: {destino} ({len(datos) // 1024} KB)")
    print("Listo.")


if __name__ == "__main__":
    main()
