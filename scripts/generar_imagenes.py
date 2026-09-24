"""Genera las escenas de un video con Cloudflare Workers AI (flux-1-schnell).

Uso:
    python scripts/generar_imagenes.py content/<nombre-video>/guion.md [opciones]

Opciones:
    --dry-run       Solo arma los prompts (imagenes/prompts.json), sin llamar a la API.
    --solo N        Genera únicamente la imagen número N (para probar antes del lote).
    --forzar        Regenera también las imágenes que ya existen.
    --sin-timeline  No vuelve a correr generar_audio.py al terminar.

Una imagen por escena: Hook, Gancho 2, cada ejemplo del Cuerpo y Pago de cada
bloque (36 en un video de 6 bloques). Las escenas muestran siluetas humanas
simples, nunca a Knot (RULES.md). Las imágenes que ya existen se saltean.

flux-1-schnell en Workers AI ignora el tamaño pedido y siempre devuelve
1024x1024, y no acepta prompt negativo. Tampoco sirve ponerlo dentro del
prompt ("Avoid: ..."): el modelo no entiende negaciones y termina dibujando lo
que se nombra (búhos, firmas). Por eso NEGATIVO queda definido pero no se
envía. Remotion recorta centrado a 16:9 (video) o 9:16 (shorts).

Al terminar corre generar_audio.py para que timeline.json incluya las
imágenes nuevas (los audios existentes no se regeneran).

Credenciales en .env (o secretos del repositorio en GitHub Actions):
CLOUDFLARE_ACCOUNT_ID y CLOUDFLARE_API_TOKEN.
"""

import argparse
import base64
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from segmentos import RAIZ, cargar_env, checkpoint, leer_guion, nombre_base, validar_o_salir

MODELO = "@cf/black-forest-labs/flux-1-schnell"
PASOS = 8  # máximo que admite flux-1-schnell; más pasos, más calidad
MAX_PROMPT = 2048  # límite de caracteres del prompt en Workers AI
TIMEOUT = 120

# RULES.md, sección "Estilo visual de las escenas humanas" (mismo texto que
# assets/personaje/PROMPTS.md).
ESTILO = (
    "Flat vector-style illustration, minimalist character design, soft painterly "
    "digital art, muted desaturated color palette, gentle color gradients, clean "
    "simple linework. Human figures shown as simple silhouettes with featureless or "
    "barely suggested faces — no detailed facial features. Editorial illustration "
    "style, like a modern animated explainer video or picture book, never "
    "photorealistic, never photographic."
)
# Variante "exagerada" (PROMPTS.md): se suma al bloque de estilo, no lo reemplaza.
# En prueba; los shorts la activan con "Estilo: exagerado" en el guion.
ESTILO_EXAGERADO = (
    "Bold high-contrast accents, sharper shadow edges. Human figures shown as simple "
    "silhouettes with exaggerated, dramatic body language — bigger gestures, tenser "
    "posture, more dynamic poses than a neutral illustration."
)
NEGATIVO = (
    "photorealistic, photograph, realistic skin texture, detailed facial features, "
    "detailed eyes, extra limbs, extra fingers, deformed hands, blurry, text, "
    "watermark, logo, signature, low quality, distorted anatomy, 3d render, CGI, "
    "grainy, film grain, realistic lighting"
)
VARIANTE_POR_TIPO = {
    "hook": "balanced medium tones, neither cool nor warm, medium framing",
    "gancho2": "balanced medium tones, neither cool nor warm, medium framing",
    "ejemplo": "cool blue-gray tones, desaturated, tight and slightly claustrophobic "
               "framing, low ambient light, soft shadows",
    "pago": "warm amber and soft golden tones, gentle warm light, wide open framing "
            "with breathing space around the figures, calm and reassuring",
}


def armar_prompt(segmento):
    inicio = f"{ESTILO} {VARIANTE_POR_TIPO[segmento['tipo']]}. "
    fin = ""  # sin bloque negativo: ver la explicación arriba
    escena = ("Scene in an everyday, recognizable setting, one or two simple human "
              "silhouettes whose posture and body language show this moment: ")
    lugar = MAX_PROMPT - len(inicio) - len(escena) - len(fin) - 2
    texto = segmento["texto"]
    if len(texto) > lugar:
        texto = texto[:lugar - 1].rsplit(" ", 1)[0] + "…"
    return f"{inicio}{escena}\"{texto}\"{fin}"


def existente(carpeta, base):
    return next(iter(sorted(carpeta.glob(base + ".*"))), None)


class CuotaAgotada(Exception):
    """Se acabó la cuota diaria gratis de Workers AI. Reintentar no sirve de nada
    (el límite es por día, no por minuto): hay que parar en el acto, no seguir
    insistiendo imagen por imagen y quemar minutos de CI para nada."""


def generar(cuenta, token, prompt):
    """POST a Workers AI. Devuelve los bytes de la imagen (la API la manda en base64)."""
    url = f"https://api.cloudflare.com/client/v4/accounts/{cuenta}/ai/run/{MODELO}"
    cuerpo = json.dumps({"prompt": prompt, "steps": PASOS}).encode()
    pedido = urllib.request.Request(url, data=cuerpo, method="POST", headers={
        "Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    for intento in range(3):
        try:
            with urllib.request.urlopen(pedido, timeout=TIMEOUT) as respuesta:
                datos = json.loads(respuesta.read())
            imagen = (datos.get("result") or {}).get("image")
            if not datos.get("success", True) or not imagen:
                raise RuntimeError(f"respuesta sin imagen: {datos.get('errors')}")
            return base64.b64decode(imagen)
        except urllib.error.HTTPError as error:
            detalle = error.read().decode(errors="replace")[:300]
            if error.code == 429 and "daily free allocation" in detalle.lower():
                raise CuotaAgotada(
                    "Se agotó la cuota diaria gratis de Cloudflare Workers AI (10.000 "
                    "neurons/día). No se soluciona reintentando: hay que esperar al "
                    "reseteo diario (00:00 UTC) o pasar a un plan pago de Workers AI."
                ) from error
            if error.code not in (429, 500, 502, 503, 504) or intento == 2:
                raise RuntimeError(f"HTTP {error.code}: {detalle}") from error
            print(f"    HTTP {error.code}, reintentando en 15s", flush=True)
        except (urllib.error.URLError, TimeoutError) as error:
            if intento == 2:
                raise
            print(f"    {error}, reintentando en 15s", flush=True)
        time.sleep(15)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("guion")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--solo", type=int)
    parser.add_argument("--forzar", action="store_true")
    parser.add_argument("--sin-timeline", action="store_true")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    ruta_guion = Path(args.guion)
    validar_o_salir(ruta_guion)
    _, segmentos = leer_guion(ruta_guion)
    escenas = [s for s in segmentos if s["ilustrar"]]

    carpeta = ruta_guion.parent / "imagenes"
    carpeta.mkdir(parents=True, exist_ok=True)
    prompts = {nombre_base(s): armar_prompt(s) for s in escenas}
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
    cuenta = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not cuenta or not token:
        sys.exit("Faltan CLOUDFLARE_ACCOUNT_ID y/o CLOUDFLARE_API_TOKEN en .env")

    fallidas = []
    for s in pendientes:
        base = nombre_base(s)
        print(f"  {base} ...", flush=True)
        try:
            datos = generar(cuenta, token, prompts[base])
        except CuotaAgotada as error:
            # Reintentar imagen por imagen no sirve: el límite es diario. Cortar acá
            # y dejar lo ya generado guardado, en vez de quemar CI insistiendo con
            # las que faltan (cada una tarda ~45s en fallar 3 veces).
            print(f"::warning::{error}")
            print(f"! Quedan {len(pendientes) - pendientes.index(s)} imágenes sin generar; "
                  f"correr de nuevo este mismo comando cuando se reponga la cuota.")
            break
        except Exception as error:  # noqa: BLE001 - una imagen que falla no frena el resto del lote
            print(f"    ! falló, sigo con la siguiente: {error}")
            fallidas.append(base)
            continue
        viejo = existente(carpeta, base)
        if viejo:
            viejo.unlink()
        extension = ".png" if datos[:8] == b"\x89PNG\r\n\x1a\n" else ".jpg"
        destino = carpeta / (base + extension)
        destino.write_bytes(datos)
        print(f"    guardada: {destino} ({len(datos) // 1024} KB)")
        checkpoint(f"Checkpoint: {base} generada (Cloudflare)")
    if fallidas:
        print(f"! {len(fallidas)} imágenes no se pudieron generar, volver a correr para reintentarlas: "
              f"{', '.join(fallidas)}")

    if not args.sin_timeline:
        print("Actualizando timeline.json con generar_audio.py ...", flush=True)
        subprocess.run([sys.executable, str(RAIZ / "scripts" / "generar_audio.py"),
                        str(ruta_guion)], check=True)
        checkpoint("Checkpoint: timeline.json actualizado")
    print("Listo.")


if __name__ == "__main__":
    main()
