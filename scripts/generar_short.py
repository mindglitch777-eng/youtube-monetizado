"""Produce un short standalone: voz (edge-tts), escenas (Cloudflare) y timeline.json.

Uso:
    python scripts/generar_short.py content/<nombre-short>/guion.md [opciones]

Opciones:
    --forzar        Regenera la voz y todas las imágenes aunque ya existan.
    --sin-imagenes  Solo voz y timeline (por ejemplo, si faltan las credenciales).

Formato del guion (empieza con "Formato: short"; no pasa por validar_guion.py):

    Formato: short
    Estilo: exagerado        (opcional: suma la variante exagerada de PROMPTS.md)
    Ritmo: 2                 (opcional: una imagen cada N segundos, ver abajo)

    # Escena N               una sección del short
    <!-- variante: media | fria | calida -->
    <!-- imagen NOMBRE: descripción -->   una o más imágenes (sin NOMBRE = escena-N)
    <!-- sonido: whoosh -->  whoosh en el corte de entrada
    <!-- parte: N -->        el short se divide y la parte N empieza acá
    Texto narrado, con la palabra resaltada en **negrita**.

    Comentarios de línea: "sonido: ding", "efecto: impacto", "contador: 1/5"
    (o "fin"), "overlay: like | follow" y "imagen: NOMBRE" (la línea queda
    fija sobre esa imagen).

Imágenes: sin "Ritmo", cada escena muestra sus imágenes repartidas en su
tiempo (una sola, en los shorts anteriores). Con "Ritmo: N" el total es
duración / N (redondeado hacia arriba), repartido entre las escenas según
cuántos segundos dura cada una en el audio real; si a una escena le faltan
imágenes, se generan variantes (otro ángulo o momento de la misma escena).
Las imágenes que ya existen no se regeneran.

La narración se genera en una sola llamada a edge-tts y los tiempos de cada
línea salen de los tiempos de sus palabras. Resultado: audio/narracion.mp3,
imagenes/*.jpg, timeline.json y, si hay "parte: N", timeline-parte-N.json
(mismo audio recortado con audioDesde, mismas imágenes).
"""

import argparse
import asyncio
import json
import math
import os
import re
import sys
from pathlib import Path

from generar_audio import KNOT_ICONO, SONIDOS, normalizar_palabra, sintetizar
from generar_imagenes import ESTILO, ESTILO_EXAGERADO, VARIANTE_POR_TIPO, CuotaAgotada, generar
from segmentos import RAIZ, cargar_env, checkpoint

VARIANTES = {
    "media": "",
    "fria": VARIANTE_POR_TIPO["ejemplo"],   # Cuerpo: frío y cerrado
    "calida": VARIANTE_POR_TIPO["pago"],    # Pago: cálido y abierto
}
# Para completar los cupos de una escena: la misma escena desde otro ángulo o momento.
ANGULOS = [
    "Close-up, tight framing on the figure's posture and hands.",
    "Wide shot from far away, small figures in a big empty space.",
    "Low angle, dramatic perspective looking up.",
    "Seen from behind, over-the-shoulder view.",
    "The same moment a few seconds later, dramatic side lighting and strong shadows.",
    "High angle looking down on the scene.",
]
COLA_FINAL = 1.5        # segundos después de la última palabra para el sting
VOLUMEN_CLICK = 0.3     # click suave en cada palabra resaltada (sin ding)
ADELANTO_WHOOSH = 0.25  # el whoosh arranca un poco antes del corte de escena
ADELANTO_PARTE = 0.15   # margen antes de la primera palabra de cada parte
AJUSTE_CORTE = 0.6      # un corte de imagen se corre hasta a la palabra más cercana
MAX_SEGUNDOS = 60       # RULES.md, sección Shorts

COMENTARIO = re.compile(r"<!--(.*?)-->", re.DOTALL)
ESCENA = re.compile(r"^#\s+escena\s+(\d+)\s*$", re.IGNORECASE)


# --- Lectura del guion -------------------------------------------------------

def leer_short(ruta):
    texto = Path(ruta).read_text(encoding="utf-8")
    if not re.match(r"\s*formato\s*:\s*short\b", texto, re.IGNORECASE):
        sys.exit(f"{ruta} no empieza con 'Formato: short'.")
    # Los comentarios de varias líneas (documentación) no forman parte del guion.
    texto = re.sub(r"<!--(?:(?!-->)[^\n])*\n.*?-->", "", texto, flags=re.DOTALL)
    exagerado = bool(re.search(r"^estilo\s*:\s*exagerado\s*$", texto, re.IGNORECASE | re.MULTILINE))
    ritmo = re.search(r"^ritmo\s*:\s*([\d.]+)\s*$", texto, re.IGNORECASE | re.MULTILINE)

    escenas, lineas = [], []
    contador = None
    for crudo in texto.splitlines():
        crudo = crudo.strip()
        if m := ESCENA.match(crudo):
            escenas.append({"numero": int(m.group(1)), "pool": [], "variante": "media",
                            "whoosh": False, "parte": None, "exagerado": exagerado})
            continue
        if not escenas or not crudo:
            continue
        comentarios = [c.strip() for c in COMENTARIO.findall(crudo)]
        narrado = COMENTARIO.sub("", crudo).strip()
        escena = escenas[-1]
        if not narrado:  # línea que es solo un comentario de la escena
            for c in comentarios:
                clave, _, valor = c.partition(":")
                palabras_clave = clave.strip().split()
                clave = palabras_clave[0].lower() if palabras_clave else ""
                if clave == "imagen":
                    nombre = palabras_clave[1] if len(palabras_clave) > 1 else None
                    escena["pool"].append({"nombre": nombre, "prompt": valor.strip()})
                elif clave == "variante":
                    escena["variante"] = valor.strip().lower()
                elif clave == "sonido" and valor.strip().lower() == "whoosh":
                    escena["whoosh"] = True
                elif clave == "parte":
                    escena["parte"] = int(valor)
            continue
        claves = {c.partition(":")[0].strip().lower(): c.partition(":")[2].strip() for c in comentarios}
        if "contador" in claves:
            contador = None if claves["contador"].lower() == "fin" else claves["contador"]
        negritas = re.findall(r"\*\*(.+?)\*\*", narrado)
        lineas.append({
            "numero": len(lineas) + 1,
            "escena": escena["numero"],
            "texto": narrado.replace("**", ""),
            "destacada": negritas[0] if negritas else None,
            "ding": claves.get("sonido", "").lower() == "ding",
            "impacto": claves.get("efecto", "").lower() == "impacto",
            "contador": contador,
            "overlay": claves.get("overlay", "").lower() or None,
            "imagen_fija": claves.get("imagen") or None,
        })

    for e in escenas:
        if not e["pool"]:
            sys.exit(f"La escena {e['numero']} no tiene ninguna imagen.")
        if e["variante"] not in VARIANTES:
            sys.exit(f"Escena {e['numero']}: variante '{e['variante']}' desconocida.")
        for k, img in enumerate(e["pool"]):
            if not img["nombre"]:  # formato anterior: una imagen sin nombre por escena
                img["nombre"] = f"escena-{e['numero']}" + (f"-{k + 1}" if k else "")
    return escenas, lineas, float(ritmo.group(1)) if ritmo else None


def armar_prompt(escena, descripcion):
    variante = VARIANTES[escena["variante"]]
    variante = f" {variante}." if variante else ""
    estilo = f"{ESTILO} {ESTILO_EXAGERADO}" if escena["exagerado"] else ESTILO
    # Sin "Avoid: ...": flux-1-schnell no entiende negaciones y termina dibujando
    # lo que se nombra (búhos, firmas). Ver generar_imagenes.py.
    return f"{estilo}{variante} {descripcion}"


# --- Voz ---------------------------------------------------------------------

def repartir_palabras(lineas, palabras):
    """Asigna cada palabra del audio a su línea, recorriendo las palabras del texto."""
    tokens = [(linea["numero"], t) for linea in lineas for t in linea["texto"].split()]
    i = 0
    resultado = []
    for palabra in palabras:
        # Signos sueltos del texto ("—") no llegan como palabra del audio: se
        # pegan a la palabra anterior para que el subtítulo los muestre y corte ahí.
        while i < len(tokens) and not re.search(r"\w", tokens[i][1]):
            if resultado and resultado[-1]["linea"] == tokens[i][0]:
                resultado[-1]["texto"] += " " + tokens[i][1]
            i += 1
        buscada = normalizar_palabra(palabra["texto"])
        # Palabras con guion ("guilt-tripping") llegan partidas del audio: la
        # segunda mitad se suma a la palabra anterior en vez de repetirse.
        if resultado and i and buscada and buscada in normalizar_palabra(tokens[i - 1][1]) \
                and not (i < len(tokens) and buscada in normalizar_palabra(tokens[i][1])):
            resultado[-1]["fin"] = palabra["fin"]
            continue
        for j in range(i, min(i + 5, len(tokens))):
            if buscada and buscada in normalizar_palabra(tokens[j][1]):
                palabra["linea"], palabra["texto"] = tokens[j][0], tokens[j][1]
                i = j + 1
                break
        else:
            palabra["linea"] = tokens[i - 1][0] if i else 1
        resultado.append(palabra)
    return resultado


# --- Cortes de imagen --------------------------------------------------------

def repartir(total, pesos, minimo=1):
    """Reparte `total` enteros según `pesos` (mayor resto), con un mínimo por ítem."""
    cantidades = [minimo] * len(pesos)
    resto = total - minimo * len(pesos)
    if resto <= 0 or not sum(pesos):
        return cantidades
    exactos = [resto * p / sum(pesos) for p in pesos]
    cantidades = [c + int(x) for c, x in zip(cantidades, exactos)]
    faltan = total - sum(cantidades)
    for k in sorted(range(len(pesos)), key=lambda k: exactos[k] - int(exactos[k]), reverse=True)[:faltan]:
        cantidades[k] += 1
    return cantidades


def ajustar(t, inicios_palabras, desde, hasta):
    """Corre un corte a la palabra más cercana (si hay una a menos de AJUSTE_CORTE)."""
    cercanas = [p for p in inicios_palabras if desde < p < hasta and abs(p - t) <= AJUSTE_CORTE]
    return min(cercanas, key=lambda p: abs(p - t)) if cercanas else t


def planificar_cortes(escenas, lineas, inicios, fin_narracion, ritmo, inicios_palabras):
    """Devuelve los cortes de imagen [{desde, hasta, escena, nombre}], en orden."""
    rangos = {}
    for n, e in enumerate(escenas):
        propias = [l for l in lineas if l["escena"] == e["numero"]]
        desde = inicios[propias[0]["numero"]] if n else 0.0
        siguiente = escenas[n + 1] if n + 1 < len(escenas) else None
        if siguiente:
            primera = next(l for l in lineas if l["escena"] == siguiente["numero"])
            hasta = inicios[primera["numero"]]
        else:
            hasta = fin_narracion + COLA_FINAL
        rangos[e["numero"]] = (desde, hasta)

    # Líneas fijas a una imagen: su tiempo queda afuera del reparto.
    fijas = {}
    for linea in lineas:
        if linea["imagen_fija"]:
            ini = inicios[linea["numero"]]
            sig = inicios.get(linea["numero"] + 1, fin_narracion + COLA_FINAL)
            fijas.setdefault(linea["escena"], []).append((ini, sig, linea["imagen_fija"]))

    def intervalos_libres(e):
        desde, hasta = rangos[e["numero"]]
        libres, cursor = [], desde
        for ini, fin, _ in sorted(fijas.get(e["numero"], [])):
            if ini > cursor:
                libres.append((cursor, ini))
            cursor = max(cursor, fin)
        if hasta > cursor:
            libres.append((cursor, hasta))
        return libres

    libres = {e["numero"]: intervalos_libres(e) for e in escenas}
    if ritmo:
        total = math.ceil(fin_narracion / ritmo)
        # Las líneas fijas cuentan como cambio visual (el overlay rompe la estática).
        ocupados = sum(max(1, round((fin - ini) / ritmo)) for fs in fijas.values() for ini, fin, _ in fs)
        duraciones = [sum(b - a for a, b in libres[e["numero"]]) for e in escenas]
        cupos = repartir(max(total - ocupados, len(escenas)), duraciones)
    else:
        cupos = [len(e["pool"]) for e in escenas]

    cortes = []
    for e, cupo in zip(escenas, cupos):
        # Lista de imágenes: primero las del guion, después variantes de cada una.
        nombres = [img["nombre"] for img in e["pool"]]
        k = 0
        while len(nombres) < cupo:
            base = e["pool"][k % len(e["pool"])]["nombre"]
            nombres.append(f"{base}-v{k // len(e['pool']) + 1}")
            k += 1
        nombres = nombres[:cupo]

        intervalos = libres[e["numero"]]
        por_intervalo = repartir(cupo, [b - a for a, b in intervalos])
        usados = 0
        for (a, b), cantidad in zip(intervalos, por_intervalo):
            limites = [a + (b - a) * j / cantidad for j in range(cantidad + 1)]
            limites = [limites[0]] + [ajustar(t, inicios_palabras, a, b) for t in limites[1:-1]] + [limites[-1]]
            for j in range(cantidad):
                cortes.append({"desde": limites[j], "hasta": limites[j + 1], "escena": e["numero"],
                               "nombre": nombres[(usados + j) % len(nombres)]})
            usados += cantidad
        for ini, fin, nombre in fijas.get(e["numero"], []):
            cortes.append({"desde": ini, "hasta": fin, "escena": e["numero"], "nombre": nombre})
    cortes.sort(key=lambda c: c["desde"])
    return cortes


def prompts_de(escenas, cortes):
    """Prompt de cada imagen usada (las variantes toman la descripción base + un ángulo)."""
    por_nombre = {}
    for e in escenas:
        for img in e["pool"]:
            por_nombre[img["nombre"]] = (e, img["prompt"])
    prompts = {}
    for nombre in dict.fromkeys(c["nombre"] for c in cortes):
        m = re.match(r"(.+)-v(\d+)$", nombre)
        if nombre in por_nombre:
            e, descripcion = por_nombre[nombre]
            prompts[nombre] = armar_prompt(e, descripcion)
        elif m and m.group(1) in por_nombre:
            e, descripcion = por_nombre[m.group(1)]
            k = int(m.group(2)) - 1 + list(por_nombre).index(m.group(1))
            prompts[nombre] = armar_prompt(e, f"{descripcion} {ANGULOS[k % len(ANGULOS)]}")
        else:
            print(f"  ! la imagen '{nombre}' no está definida en ninguna escena")
    return prompts


# --- Programa principal ------------------------------------------------------

async def main_async(args):
    ruta = Path(args.guion).resolve()
    carpeta = ruta.parent
    escenas, lineas, ritmo = leer_short(ruta)
    cargar_env()
    voz = os.environ.get("EDGE_TTS_VOICE", "en-US-JennyNeural")

    # --- Voz: una sola narración ---
    (carpeta / "audio").mkdir(exist_ok=True)
    mp3, meta = carpeta / "audio" / "narracion.mp3", carpeta / "audio" / "narracion.json"
    texto = " ".join(linea["texto"] for linea in lineas)
    datos = json.loads(meta.read_text(encoding="utf-8")) if meta.exists() else None
    if args.forzar or not mp3.exists() or not datos or datos.get("texto") != texto \
            or datos.get("voz") != voz:
        print("Generando la narración con edge-tts ...", flush=True)
        datos = await sintetizar(texto, voz, mp3)
        datos.update(texto=texto, voz=voz)
    # Se re-reparte siempre desde el texto, así los arreglos de alineación aplican
    # también a audios ya generados.
    datos["palabras"] = repartir_palabras(lineas, [dict(p) for p in datos["palabras"]])
    meta.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    checkpoint("Checkpoint: narración generada (edge-tts)")

    palabras = datos["palabras"]
    inicios = {}
    for p in palabras:
        inicios.setdefault(p["linea"], p["inicio"])
    fin_narracion = palabras[-1]["fin"]
    duracion_total = round(fin_narracion + COLA_FINAL, 3)

    # --- Cortes de imagen ---
    cortes = planificar_cortes(escenas, lineas, inicios, fin_narracion, ritmo,
                               [p["inicio"] for p in palabras])
    prompts = prompts_de(escenas, cortes)

    carpeta_img = carpeta / "imagenes"
    carpeta_img.mkdir(exist_ok=True)
    (carpeta_img / "prompts.json").write_text(
        json.dumps(prompts, ensure_ascii=False, indent=2), encoding="utf-8")
    cuenta, token = os.environ.get("CLOUDFLARE_ACCOUNT_ID"), os.environ.get("CLOUDFLARE_API_TOKEN")
    if not args.sin_imagenes and not (cuenta and token):
        print("! Faltan CLOUDFLARE_ACCOUNT_ID / CLOUDFLARE_API_TOKEN: no se generan imágenes.")
    pendientes = [n for n in prompts if args.forzar or not list(carpeta_img.glob(n + ".*"))]
    if pendientes and cuenta and token and not args.sin_imagenes:
        print(f"Generando {len(pendientes)} imágenes ...", flush=True)
        for k, nombre in enumerate(pendientes):
            try:
                imagen = generar(cuenta, token, prompts[nombre])
            except CuotaAgotada as error:
                # El límite es diario: insistir con las que faltan solo quema CI.
                # Se corta acá; lo ya generado queda guardado por los checkpoints.
                print(f"::warning::{error}")
                print(f"! Quedan {len(pendientes) - k} imágenes sin generar; "
                      f"correr de nuevo este mismo comando cuando se reponga la cuota.")
                break
            except Exception as error:  # noqa: BLE001 - una imagen que falla no frena el resto
                print(f"  ! {nombre}: {error}")
                continue
            for viejo in carpeta_img.glob(nombre + ".*"):
                viejo.unlink()
            extension = ".png" if imagen[:8] == b"\x89PNG\r\n\x1a\n" else ".jpg"
            (carpeta_img / (nombre + extension)).write_bytes(imagen)
            print(f"  {nombre}{extension}", flush=True)
            checkpoint(f"Checkpoint: {nombre} generada (Cloudflare)")

    # Imagen de cada corte; si falta, se usa otra de la misma escena.
    def archivo(nombre):
        encontradas = sorted(carpeta_img.glob(nombre + ".*"))
        return encontradas[0].relative_to(RAIZ).as_posix() if encontradas else None

    faltantes = set()
    for c in cortes:
        c["imagen"] = archivo(c["nombre"])
        if not c["imagen"]:
            faltantes.add(c["nombre"])
            alternativas = [archivo(x["nombre"]) for x in cortes if x["escena"] == c["escena"]]
            c["imagen"] = next((a for a in alternativas if a), None)
    if faltantes:
        print(f"  ! faltan {len(faltantes)} imágenes (se reemplazan por otras de su escena): "
              f"{', '.join(sorted(faltantes))}")

    escena_de = {e["numero"]: e for e in escenas}
    primeros = {}
    for c in cortes:
        primeros.setdefault(c["escena"], id(c))
    tramos = [{"desde": round(c["desde"], 3), "hasta": round(c["hasta"], 3), "imagen": c["imagen"],
               "escena": c["escena"],
               "whoosh": primeros[c["escena"]] == id(c) and escena_de[c["escena"]]["whoosh"]}
              for c in cortes]

    # --- Timeline: un segmento por línea ---
    segmentos, escena_anterior = [], None
    for n, linea in enumerate(lineas):
        inicio = inicios.get(linea["numero"], 0.0)
        siguiente = inicios.get(linea["numero"] + 1, duracion_total) if n + 1 < len(lineas) else duracion_total
        propias = [dict(p, inicio=round(p["inicio"] - inicio, 3), fin=round(p["fin"] - inicio, 3))
                   for p in palabras if p["linea"] == linea["numero"]]
        destacada = None
        if linea["destacada"]:
            buscada = normalizar_palabra(linea["destacada"].split()[0])
            destacada = next((k for k, p in enumerate(propias)
                              if normalizar_palabra(p["texto"].split()[0]) == buscada), None)
        sonidos = []
        if linea["escena"] != escena_anterior and escena_de[linea["escena"]]["whoosh"]:
            sonidos.append({"archivo": SONIDOS["whoosh"], "en": -ADELANTO_WHOOSH})
        if destacada is not None:
            if linea["ding"]:
                sonidos.append({"archivo": SONIDOS["ding"], "en": propias[destacada]["inicio"]})
            else:
                sonidos.append({"archivo": SONIDOS["click"], "en": propias[destacada]["inicio"],
                                "volumen": VOLUMEN_CLICK})
        if n == len(lineas) - 1:
            sonidos.append({"archivo": SONIDOS["sting"], "en": round(fin_narracion - inicio, 3)})
        tramo = next((t for t in reversed(tramos) if t["desde"] <= inicio + 0.01), tramos[0])
        segmentos.append({
            "id": f"l{linea['numero']:02d}",
            "tipo": "linea",
            "bloque": None,
            "escena": linea["escena"],
            "inicio": round(inicio, 3),
            "duracion": round(siguiente - inicio, 3),
            "audio": None,
            "imagen": tramo["imagen"],
            "palabras": propias,
            "destacada": destacada,
            "sonidos": sonidos,
            "impacto": linea["impacto"],
            "contador": linea["contador"],
            "overlay": linea["overlay"],
        })
        escena_anterior = linea["escena"]

    salida = {
        "titulo": "",
        "video": carpeta.relative_to(RAIZ).as_posix(),
        "voz": voz,
        "icono": KNOT_ICONO,
        "formato": "short",
        "audio": mp3.relative_to(RAIZ).as_posix(),
        "duracionTotal": duracion_total,
        "segmentos": segmentos,
        "tramos": tramos,
    }
    (carpeta / "timeline.json").write_text(
        json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{'línea':>5} {'escena':>6} {'inicio':>7}  texto")
    for s, linea in zip(segmentos, lineas):
        print(f"{linea['numero']:>5} {linea['escena']:>6} {s['inicio']:>6.2f}s  {linea['texto']}")
    print(f"\nNarración: {fin_narracion:.2f} s. Duración total del short: {duracion_total:.2f} s.")
    print(f"Cortes de imagen: {len(tramos)} ({len({t['imagen'] for t in tramos if t['imagen']})} imágenes distintas).")
    for e in escenas:
        propios = [t for t in tramos if t["escena"] == e["numero"]]
        segundos = sum(t["hasta"] - t["desde"] for t in propios)
        print(f"  escena {e['numero']}: {len(propios)} cortes en {segundos:.1f} s")
    escribir_partes(carpeta, salida, escenas, palabras)
    checkpoint("Checkpoint: timeline.json actualizado")
    if duracion_total >= MAX_SEGUNDOS and not any(e["parte"] for e in escenas):
        print(f"! El short dura {MAX_SEGUNDOS} s o más: Remotion va a frenar el render (RULES.md).")


def escribir_partes(carpeta, salida, escenas, palabras):
    """Si hay escenas con "parte: N", escribe timeline-parte-N.json para cada parte."""
    for viejo in carpeta.glob("timeline-parte-*.json"):
        viejo.unlink()
    if not any(e["parte"] for e in escenas):
        return
    parte_de, actual = {}, 1
    for e in escenas:
        actual = e["parte"] or actual
        parte_de[e["numero"]] = actual
    for parte in sorted(set(parte_de.values())):
        segs = [s for s in salida["segmentos"] if parte_de[s["escena"]] == parte]
        lineas_parte = {int(s["id"][1:]) for s in segs}
        fin = max(p["fin"] for p in palabras if p["linea"] in lineas_parte)
        desde = max(0.0, segs[0]["inicio"] - ADELANTO_PARTE)
        hasta = fin + COLA_FINAL
        nuevos = []
        for k, s in enumerate(segs):
            s = json.loads(json.dumps(s))
            inicio_abs = s["inicio"]
            s["inicio"] = round(inicio_abs - desde, 3)
            # Sin el whoosh de entrada (sonaría antes del segundo 0) ni el sting del total.
            s["sonidos"] = [x for x in s["sonidos"] if inicio_abs - desde + x["en"] >= 0
                            and x["archivo"] != SONIDOS["sting"]]
            if k == len(segs) - 1:
                s["sonidos"].append({"archivo": SONIDOS["sting"], "en": round(fin - inicio_abs, 3)})
                s["duracion"] = round(hasta - inicio_abs, 3)
            nuevos.append(s)
        tramos = []
        for t in salida["tramos"]:
            a, b = max(t["desde"], desde), min(t["hasta"], hasta)
            if b - a > 0.05:
                tramos.append(dict(t, desde=round(a - desde, 3), hasta=round(b - desde, 3),
                                   whoosh=t["whoosh"] and a == t["desde"] and a > desde))
        dur = round(hasta - desde, 3)
        destino = carpeta / f"timeline-parte-{parte}.json"
        destino.write_text(json.dumps(dict(salida, segmentos=nuevos, tramos=tramos, duracionTotal=dur,
                                           audioDesde=round(desde, 3), parte=parte),
                                      ensure_ascii=False, indent=2), encoding="utf-8")
        aviso = "  ! 60 s o más" if dur >= MAX_SEGUNDOS else ""
        print(f"Parte {parte}: escenas {sorted(e for e, p in parte_de.items() if p == parte)}, "
              f"{dur:.2f} s, {len(tramos)} cortes → {destino.name}{aviso}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("guion")
    parser.add_argument("--forzar", action="store_true")
    parser.add_argument("--sin-imagenes", action="store_true")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
