"""Paso 2/3 del PACK de video largo: genera las imágenes IA de shots.json con
Cloudflare Workers AI (flux-1-schnell).

Uso:
    python scripts/pack_imagenes.py content/<carpeta-pack> --solo-test
    python scripts/pack_imagenes.py content/<carpeta-pack>            (lote completo)

--solo-test genera únicamente las tomas marcadas "test_batch": true (Paso 2
del PACK) — no toca el resto. Sin esa bandera, genera todas las tomas
type=="ai" que todavía no tengan archivo, más las 2 miniaturas de
assets.json → thumbnails, con guarda de cuota (N5 del PACK: idempotente, no
regenera lo que ya existe, y si Cloudflare devuelve cuota agotada, para y
deja constancia de cuántas faltan).

Corre en GitHub Actions: Cloudflare Workers AI no es accesible desde el
entorno de Claude Code.
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MODELO = "@cf/black-forest-labs/flux-1-schnell"
PASOS = 8
TIMEOUT = 120
MAX_REGENERACIONES = 24  # N5: reserva de regeneraciones sobre las 80 del manifiesto


class CuotaAgotada(Exception):
    pass


def generar(cuenta, token, prompt):
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
                    "neurons/día)."
                ) from error
            if error.code not in (429, 500, 502, 503, 504) or intento == 2:
                raise RuntimeError(f"HTTP {error.code}: {detalle}") from error
            print(f"    HTTP {error.code}, reintentando en 15s", flush=True)
        except (urllib.error.URLError, TimeoutError) as error:
            if intento == 2:
                raise
            print(f"    {error}, reintentando en 15s", flush=True)
        time.sleep(15)


def checkpoint(carpeta_raiz, mensaje):
    if os.environ.get("GITHUB_ACTIONS") != "true":
        return
    import subprocess
    rama = os.environ.get("GITHUB_REF_NAME")
    try:
        subprocess.run(["git", "add", "-A", "--", "content"], cwd=carpeta_raiz, check=True)
        si_hay = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=carpeta_raiz)
        if si_hay.returncode == 0:
            return
        subprocess.run(["git", "commit", "-q", "-m", mensaje], cwd=carpeta_raiz, check=True)
        for _ in range(3):
            ok = subprocess.run(["git", "pull", "-q", "--rebase", "--autostash", "origin", rama],
                                cwd=carpeta_raiz).returncode == 0
            if ok and subprocess.run(["git", "push", "-q", "origin", f"HEAD:{rama}"],
                                     cwd=carpeta_raiz).returncode == 0:
                print(f"  ✓ checkpoint: {mensaje}", flush=True)
                return
            time.sleep(5)
        print(f"  ! no se pudo pushear el checkpoint ({mensaje})", flush=True)
    except Exception as error:  # noqa: BLE001
        print(f"  ! checkpoint falló ({error})", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("carpeta")
    parser.add_argument("--solo-test", action="store_true")
    parser.add_argument("--forzar", action="store_true")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    carpeta = Path(args.carpeta).resolve()
    shots = json.loads((carpeta / "shots.json").read_text(encoding="utf-8"))["shots"]
    assets = json.loads((carpeta / "assets.json").read_text(encoding="utf-8"))

    sys.path.insert(0, str(RAIZ / "scripts"))
    from segmentos import cargar_env
    cargar_env()
    cuenta = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not cuenta or not token:
        sys.exit("Faltan CLOUDFLARE_ACCOUNT_ID / CLOUDFLARE_API_TOKEN")

    # Pedidos: (nombre_base, archivo_relativo, prompt)
    pedidos = []
    ai_shots = [s for s in shots if s["type"] == "ai"]
    if args.solo_test:
        pedidos = [(s["id"], s["ai"]["file"], s["ai"]["prompt"]) for s in ai_shots if s["ai"].get("test_batch")]
    else:
        pedidos = [(s["id"], s["ai"]["file"], s["ai"]["prompt"]) for s in ai_shots]
        for clave, miniatura in assets["thumbnails"].items():
            pedidos.append((f"THUMB_{clave}", miniatura["file"], miniatura["prompt"]))

    pendientes = [p for p in pedidos if args.forzar or not (carpeta / p[1]).exists()]
    print(f"{len(pedidos)} pedidas, {len(pendientes)} por generar.")
    if not pendientes:
        print("Nada por generar (todo existe ya) — idempotente, no se regenera nada.")
        return

    generadas, fallidas = 0, []
    for nombre, archivo_rel, prompt in pendientes:
        destino = carpeta / archivo_rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        print(f"  {nombre} -> {archivo_rel} ...", flush=True)
        try:
            imagen = generar(cuenta, token, prompt)
        except CuotaAgotada as error:
            faltan = len(pendientes) - pendientes.index((nombre, archivo_rel, prompt))
            print(f"::warning::{error}")
            print(f"PARADO: cuota agotada. Faltan {faltan} imágenes de {len(pendientes)} pendientes "
                  f"(generadas {generadas} en esta corrida). Reanudar corriendo este mismo comando "
                  f"cuando se reponga la cuota (00:00 UTC) — no regenera lo que ya existe.")
            (carpeta / "CUOTA_AGOTADA.txt").write_text(
                f"Cuota agotada. Faltan {faltan} de {len(pendientes)} pendientes en esta corrida.\n"
                f"Generadas antes de parar: {generadas}.\n", encoding="utf-8")
            checkpoint(RAIZ, f"Checkpoint: cuota agotada, {generadas} imágenes generadas antes de parar")
            sys.exit(2)
        except Exception as error:  # noqa: BLE001
            print(f"    ! falló, sigo con la siguiente: {error}")
            fallidas.append(nombre)
            continue
        destino.write_bytes(imagen)
        generadas += 1
        print(f"    guardada: {destino} ({len(imagen) // 1024} KB)")
        checkpoint(RAIZ, f"Checkpoint: {nombre} generada (Cloudflare)")

    (carpeta / "CUOTA_AGOTADA.txt").unlink(missing_ok=True)
    print(f"\nListo: {generadas} generadas, {len(fallidas)} fallidas.")
    if fallidas:
        print(f"Fallidas (no por cuota, revisar a mano): {', '.join(fallidas)}")


if __name__ == "__main__":
    main()
