"""Valida un guion.md contra las reglas de RULES.md antes de generar imágenes.

Uso:
    python scripts/validar_guion.py content/<nombre-video>/guion.md

Formato esperado del guion (el nivel de los encabezados #, ##, ### es libre;
una sección termina en el siguiente encabezado de igual o mayor nivel):

    Palabra clave SEO: <keyword>

    # Intro
    # Bloque 1
    ## Hook
    ## Gancho 2
    ## Cuerpo
    - ejemplo 1          (viñetas, líneas numeradas o subencabezados
    - ejemplo 2           "Ejemplo 1/2/3")
    - ejemplo 3
    ## Pago              (incluye una nota sobre el estado del hilo)
    ...
    # Bloque 6
    ## Hook / Gancho 2 / Cuerpo / Pago
    ## CTA               (único, solo en el bloque 6, después del Pago)

Sale con código 0 si todos los chequeos pasan, 1 si alguno falla y 2 si
no se pudo leer el archivo.
"""

import re
import sys
import unicodedata
from pathlib import Path

TOTAL_BLOQUES = 6
EJEMPLOS_POR_CUERPO = 3
SECCIONES = ("hook", "gancho 2", "cuerpo", "pago")
NOMBRES = {"hook": "Hook", "gancho 2": "Gancho 2", "cuerpo": "Cuerpo",
           "pago": "Pago", "cta": "CTA"}

ENCABEZADO = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
# Viñeta o línea numerada de primer nivel (las sub-viñetas indentadas no cuentan).
VINETA = re.compile(r"^ ?(?:[-*+]|\d+[.)])\s+\S")
KEYWORD = re.compile(
    r"^(?:palabra\s+clave(?:\s+seo)?(?:\s+objetivo)?|seo\s+keyword|target\s+keyword)"
    r"\s*(?::\s*(.*))?$",
    re.IGNORECASE,
)
COMENTARIO = re.compile(r"<!--.*?-->", re.DOTALL)


def normalizar(texto):
    """Minúsculas, sin tildes, sin markdown ni paréntesis: 'Cuerpo (3 ejemplos)' -> 'cuerpo'."""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"\(.*?\)", "", texto.replace("*", "").replace("_", " "))
    return re.sub(r"\s+", " ", texto).strip().lower()


def tipo_encabezado(titulo):
    t = normalizar(titulo)
    m = re.match(r"bloque\s*(\d+)\b", t)
    if m:
        return "bloque", int(m.group(1))
    if t == "hook":
        return "hook", None
    if re.fullmatch(r"gancho\s*2", t):
        return "gancho 2", None
    if t.startswith("cuerpo"):
        return "cuerpo", None
    if t.startswith("pago"):
        return "pago", None
    if re.match(r"cta\b", t):
        return "cta", None
    if re.match(r"ejemplo\s*\d+", t):
        return "ejemplo", None
    return None, None


def parsear(lineas):
    """Devuelve (bloques, secciones). Ignora encabezados dentro de comentarios HTML."""
    encabezados = []
    en_comentario = False
    for i, linea in enumerate(lineas):
        if en_comentario:
            en_comentario = "-->" not in linea
            continue
        if "<!--" in linea and "-->" not in linea.split("<!--")[-1]:
            en_comentario = True
            continue
        m = ENCABEZADO.match(linea)
        if m:
            tipo, valor = tipo_encabezado(m.group(2))
            encabezados.append({"linea": i, "nivel": len(m.group(1)),
                                "tipo": tipo, "valor": valor})

    bloques = [e for e in encabezados if e["tipo"] == "bloque"]
    secciones = []
    bloque_actual = None
    for n, e in enumerate(encabezados):
        if e["tipo"] == "bloque":
            bloque_actual = e["valor"]
            continue
        if e["tipo"] not in NOMBRES:
            continue
        fin = len(lineas)
        for siguiente in encabezados[n + 1:]:
            if siguiente["nivel"] <= e["nivel"] or siguiente["tipo"] == "bloque":
                fin = siguiente["linea"]
                break
        cuerpo = lineas[e["linea"] + 1:fin]
        subejemplos = [s for s in encabezados[n + 1:]
                       if s["tipo"] == "ejemplo" and s["linea"] < fin]
        secciones.append({"tipo": e["tipo"], "bloque": bloque_actual,
                          "linea": e["linea"] + 1, "lineas": cuerpo,
                          "subejemplos": len(subejemplos)})
    return bloques, secciones


def texto_visible(lineas):
    """Texto de la sección sin comentarios HTML ni encabezados."""
    texto = COMENTARIO.sub("", "\n".join(lineas))
    return "\n".join(l for l in texto.splitlines() if not ENCABEZADO.match(l)).strip()


def donde(seccion):
    b = seccion["bloque"]
    lugar = f"en el bloque {b}" if b is not None else "fuera de cualquier bloque"
    return f"{lugar} (línea {seccion['linea']})"


def secciones_de(secciones, bloque, tipo):
    return [s for s in secciones if s["bloque"] == bloque and s["tipo"] == tipo]


# --- Chequeos: cada uno devuelve (nombre, lista de motivos de falla) ---------

def chequear_estructura(bloques, secciones):
    motivos = []
    numeros = [b["valor"] for b in bloques]
    esperados = list(range(1, TOTAL_BLOQUES + 1))
    if numeros != esperados:
        encontrados = ", ".join(map(str, numeros)) or "ninguno"
        motivos.append(f"se encontraron {len(numeros)} bloques (numeración: {encontrados}); "
                       f"se esperaban exactamente {TOTAL_BLOQUES}, numerados del 1 al "
                       f"{TOTAL_BLOQUES} y en orden")
    for s in secciones:
        if s["bloque"] is None and s["tipo"] in SECCIONES:
            motivos.append(f"'{NOMBRES[s['tipo']]}' está {donde(s)}")
    for numero in sorted(set(numeros)):
        posiciones = []
        for tipo in SECCIONES:
            encontradas = secciones_de(secciones, numero, tipo)
            if not encontradas:
                motivos.append(f"bloque {numero}: falta la sección '{NOMBRES[tipo]}'")
                continue
            if len(encontradas) > 1:
                motivos.append(f"bloque {numero}: '{NOMBRES[tipo]}' aparece "
                               f"{len(encontradas)} veces")
            if not texto_visible(encontradas[0]["lineas"]):
                motivos.append(f"bloque {numero}: '{NOMBRES[tipo]}' está vacío "
                               f"(línea {encontradas[0]['linea']})")
            posiciones.append(encontradas[0]["linea"])
        if len(posiciones) == len(SECCIONES) and posiciones != sorted(posiciones):
            motivos.append(f"bloque {numero}: las secciones no están en el orden "
                           f"Hook → Gancho 2 → Cuerpo → Pago")
    return f"Estructura: {TOTAL_BLOQUES} bloques con Hook / Gancho 2 / Cuerpo / Pago", motivos


def chequear_cta(bloques, secciones):
    motivos = []
    ctas = [s for s in secciones if s["tipo"] == "cta"]
    if not ctas:
        motivos.append(f"no hay ninguna sección CTA; tiene que haber una al final "
                       f"del bloque {TOTAL_BLOQUES}")
    if len(ctas) > 1:
        motivos.append(f"el CTA aparece {len(ctas)} veces; tiene que aparecer una sola vez")
    for s in ctas:
        if s["bloque"] != TOTAL_BLOQUES:
            motivos.append(f"hay un CTA {donde(s)}; solo puede ir en el "
                           f"bloque {TOTAL_BLOQUES}")
    finales = [s for s in ctas if s["bloque"] == TOTAL_BLOQUES]
    if len(ctas) == 1 and finales:
        cta = finales[0]
        if not texto_visible(cta["lineas"]):
            motivos.append(f"el CTA está vacío (línea {cta['linea']})")
        pagos = secciones_de(secciones, TOTAL_BLOQUES, "pago")
        if pagos and pagos[0]["linea"] > cta["linea"]:
            motivos.append(f"el CTA (línea {cta['linea']}) tiene que ir después del "
                           f"Pago del bloque {TOTAL_BLOQUES} (línea {pagos[0]['linea']})")
    return f"CTA: una sola vez, al final del bloque {TOTAL_BLOQUES}", motivos


def chequear_ejemplos(bloques, secciones):
    motivos = []
    for numero in sorted({b["valor"] for b in bloques}):
        cuerpos = secciones_de(secciones, numero, "cuerpo")
        if not cuerpos:
            motivos.append(f"bloque {numero}: no tiene Cuerpo, no se pudieron contar ejemplos")
            continue
        cuerpo = cuerpos[0]
        if cuerpo["subejemplos"]:
            cantidad, forma = cuerpo["subejemplos"], "subencabezados 'Ejemplo N'"
        else:
            sin_comentarios = COMENTARIO.sub("", "\n".join(cuerpo["lineas"])).splitlines()
            cantidad = sum(1 for l in sin_comentarios if VINETA.match(l))
            forma = "viñetas/líneas numeradas"
        if cantidad != EJEMPLOS_POR_CUERPO:
            motivos.append(f"bloque {numero}: el Cuerpo tiene {cantidad} ejemplos ({forma}); "
                           f"tienen que ser exactamente {EJEMPLOS_POR_CUERPO}")
    if not bloques:
        motivos.append("no hay bloques, no se pudieron contar ejemplos")
    return f"Ejemplos: exactamente {EJEMPLOS_POR_CUERPO} en cada Cuerpo", motivos


def chequear_hilo(bloques, secciones):
    motivos = []
    for numero in sorted({b["valor"] for b in bloques}):
        pagos = secciones_de(secciones, numero, "pago")
        if not pagos:
            motivos.append(f"bloque {numero}: no tiene Pago, no se pudo buscar la nota del hilo")
        elif not re.search(r"\bhilo\b", "\n".join(pagos[0]["lineas"]), re.IGNORECASE):
            motivos.append(f"bloque {numero}: el Pago (línea {pagos[0]['linea']}) no "
                           f"menciona el 'hilo' (falta la nota de progresión)")
    if not bloques:
        motivos.append("no hay bloques, no se pudo buscar la nota del hilo")
    return "Hilo: nota de progresión en cada Pago", motivos


def buscar_keyword(lineas):
    for i, linea in enumerate(lineas):
        es_encabezado = bool(ENCABEZADO.match(linea))
        limpio = re.sub(r"^[\s#>*\-]+", "", linea).replace("**", "").replace("__", "").strip()
        m = KEYWORD.match(limpio)
        if not m:
            continue
        valor = (m.group(1) or "").strip()
        if not valor and es_encabezado:
            valor = next((l.strip() for l in lineas[i + 1:] if l.strip()), "")
            if ENCABEZADO.match(valor):
                valor = ""
        valor = valor.strip("`\"'“”*").strip()
        if valor:
            return valor
    return None


def chequear_seo(lineas):
    keyword = buscar_keyword(lineas)
    if not keyword:
        return "Palabra clave SEO", ["no se encontró la palabra clave SEO objetivo; "
                                     "agregá una línea 'Palabra clave SEO: <keyword>'"]
    return f"Palabra clave SEO: '{keyword}'", []


def chequear_seo_dicha(lineas, secciones):
    """RULES.md: la palabra clave se dice en voz alta dentro del guion."""
    keyword = buscar_keyword(lineas)
    nombre = "Palabra clave SEO dicha dentro del guion"
    if not keyword:
        return nombre, ["no hay palabra clave declarada, no se pudo verificar"]
    narracion = normalizar("\n".join(texto_visible(s["lineas"]) for s in secciones))
    if normalizar(keyword) not in narracion:
        return nombre, [f"'{keyword}' no aparece en el texto de ningún Hook / Gancho 2 / "
                        f"Cuerpo / Pago / CTA"]
    return nombre, []


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 2:
        print("Uso: python scripts/validar_guion.py <ruta/al/guion.md>")
        return 2
    ruta = Path(sys.argv[1])
    try:
        lineas = ruta.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        print(f"✗ No se pudo leer {ruta}: {error}")
        return 2

    bloques, secciones = parsear(lineas)
    resultados = [
        chequear_estructura(bloques, secciones),
        chequear_cta(bloques, secciones),
        chequear_ejemplos(bloques, secciones),
        chequear_hilo(bloques, secciones),
        chequear_seo(lineas),
        chequear_seo_dicha(lineas, secciones),
    ]

    print(f"Validando: {ruta}\n")
    for nombre, motivos in resultados:
        print(f"{'✗' if motivos else '✓'} {nombre}")
        for motivo in motivos:
            print(f"    - {motivo}")

    fallidos = sum(1 for _, motivos in resultados if motivos)
    print(f"\n{len(resultados) - fallidos}/{len(resultados)} chequeos pasaron.")
    if fallidos:
        print("✗ NO LISTO — corregí los puntos marcados con ✗ antes de seguir.")
        return 1
    print("✓ LISTO PARA GENERAR IMÁGENES")
    return 0


if __name__ == "__main__":
    sys.exit(main())
