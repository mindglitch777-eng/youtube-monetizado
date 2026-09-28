"""Paso 4 del PACK de video largo: descarga los 8 clips reales de Pexels
listados en assets.json (principal, con respaldo si falla), corre ffprobe
sobre cada uno y arma credits.txt.

Uso:
    python scripts/pack_clips.py content/<carpeta-pack>

Corre en GitHub Actions: videos.pexels.com no es accesible desde el entorno
de Claude Code. ffprobe sí corre acá (ubuntu-latest lo trae).
"""

import json
import subprocess
import sys
import urllib.request
from pathlib import Path


def descargar(url, destino):
    pedido = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(pedido, timeout=60) as respuesta, open(destino, "wb") as archivo:
        archivo.write(respuesta.read())


def es_video(ruta):
    try:
        salida = subprocess.run(["file", "-b", "--mime-type", str(ruta)], capture_output=True, text=True, check=True)
        return salida.stdout.strip().startswith("video/")
    except Exception:  # noqa: BLE001
        return False


def ffprobe_info(ruta):
    salida = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height,r_frame_rate,duration", "-of", "json", str(ruta)],
        capture_output=True, text=True,
    )
    if salida.returncode != 0:
        return None
    datos = json.loads(salida.stdout)
    return (datos.get("streams") or [None])[0]


def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: python scripts/pack_clips.py content/<carpeta-pack>")
    carpeta = Path(sys.argv[1]).resolve()
    assets = json.loads((carpeta / "assets.json").read_text(encoding="utf-8"))
    carpeta_clips = carpeta / "clips"
    carpeta_clips.mkdir(parents=True, exist_ok=True)

    creditos = ["# Créditos de clips reales (Pexels)\n"]
    fallidos = []
    for clave, info in assets["clips"].items():
        destino = carpeta_clips / f"{clave}.mp4"
        marcador = carpeta_clips / f"{clave}.fuente.json"
        if destino.exists() and marcador.exists():
            print(f"✓ {clave}.mp4 ya existe")
            fuente_creditos = json.loads(marcador.read_text(encoding="utf-8"))
        else:
            usado = None
            for etiqueta, fuente in (("principal", info), ("respaldo", info.get("backup"))):
                if not fuente:
                    continue
                try:
                    descargar(fuente["url"], destino)
                    if es_video(destino):
                        usado = (etiqueta, fuente)
                        break
                    destino.unlink(missing_ok=True)
                except Exception as error:  # noqa: BLE001
                    print(f"  {etiqueta} falló para {clave}: {error}")
                    destino.unlink(missing_ok=True)
            if not usado:
                print(f"::warning::No se pudo descargar el clip {clave} (ni principal ni respaldo)")
                fallidos.append(clave)
                continue
            etiqueta, fuente_creditos = usado
            marcador.write_text(json.dumps(fuente_creditos, ensure_ascii=False), encoding="utf-8")
            print(f"✓ {clave}.mp4 ← {etiqueta} ({fuente_creditos['url']})")

        info_stream = ffprobe_info(destino) if destino.exists() else None
        if info_stream:
            print(f"    {info_stream.get('width')}x{info_stream.get('height')} "
                  f"{info_stream.get('r_frame_rate')} {float(info_stream.get('duration', 0)):.2f}s")
        creditos.append(f"- **{clave}.mp4** ({info['use']}): {fuente_creditos['author']} — {fuente_creditos['page']}")

    (carpeta / "credits.txt").write_text("\n".join(creditos) + "\n", encoding="utf-8")
    print(f"\ncredits.txt escrito. Clips fallidos: {fallidos or 'ninguno'}")
    if fallidos:
        print("::warning::Declarar en AUDIT.md los clips fallidos (regla de sección 9 del PACK).")


if __name__ == "__main__":
    main()
