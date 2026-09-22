"""Lectura compartida de guion.md para generar_imagenes.py y generar_audio.py.

Divide el guion en segmentos narrados, en orden:
    intro, y por cada bloque: hook, gancho2, ej1, ej2, ej3, pago, transicion
    (el bloque 6 termina con pago y cta).

Cada segmento sabe si lleva imagen (Hook, Gancho 2, cada ejemplo y Pago),
si tiene una marca <!-- sonido: ding --> y qué palabra se resalta en los
subtítulos (la que esté en **negrita** dentro de ese segmento).
"""

import os
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

ENCABEZADO = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
VINETA = re.compile(r"^ ?(?:[-*+]|\d+[.)])\s+(.*)$")
COMENTARIO = re.compile(r"<!--(.*?)-->", re.DOTALL)
NEGRITA = re.compile(r"\*\*(.+?)\*\*")
TITULO = re.compile(r"^\s*t[ií]tulo\s*:\s*(.+)$", re.IGNORECASE)

TIPOS_CON_IMAGEN = ("hook", "gancho2", "ejemplo", "pago")


def cargar_env():
    """Carga RAIZ/.env en os.environ sin pisar variables ya definidas."""
    ruta = RAIZ / ".env"
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, _, valor = linea.partition("=")
        os.environ.setdefault(clave.strip(), valor.strip().strip("\"'"))


def validar_o_salir(ruta_guion):
    """RULES.md: si el guion no cumple las reglas, el pipeline se detiene."""
    validador = RAIZ / "scripts" / "validar_guion.py"
    resultado = subprocess.run([sys.executable, str(validador), str(ruta_guion)],
                               capture_output=True, text=True, encoding="utf-8")
    if resultado.returncode != 0:
        print(resultado.stdout or resultado.stderr)
        print("Pipeline detenido: el guion no pasa validar_guion.py.")
        sys.exit(1)


def _tipo(titulo):
    # Misma normalización que validar_guion.py.
    from validar_guion import normalizar, tipo_encabezado
    tipo, valor = tipo_encabezado(titulo)
    if tipo:
        return tipo, valor
    t = normalizar(titulo)
    if t.startswith("intro"):
        return "intro", None
    if t.startswith("transicion"):
        return "transicion", None
    return None, None


def _limpiar(texto):
    """Texto a narrar: sin comentarios, sin marcas de markdown, en una línea."""
    texto = COMENTARIO.sub("", texto)
    texto = texto.replace("**", "").replace("__", "")
    return re.sub(r"\s+", " ", texto).strip()


def leer_guion(ruta_guion):
    """Devuelve (titulo, segmentos). Cada segmento es un dict."""
    sys.path.insert(0, str(RAIZ / "scripts"))
    lineas = Path(ruta_guion).read_text(encoding="utf-8").splitlines()

    titulo = ""
    crudos = []          # (bloque, tipo, lineas)
    bloque = None
    actual = None
    en_comentario = False
    for linea in lineas:
        if not titulo and (m := TITULO.match(linea)):
            titulo = m.group(1).strip()
        if en_comentario:
            if actual is not None:
                actual[2].append(linea)
            en_comentario = "-->" not in linea
            continue
        if "<!--" in linea and "-->" not in linea.split("<!--")[-1]:
            en_comentario = True
            if actual is not None:
                actual[2].append(linea)
            continue
        m = ENCABEZADO.match(linea)
        if m:
            tipo, valor = _tipo(m.group(2))
            if tipo == "bloque":
                bloque, actual = valor, None
            elif tipo in ("intro", "hook", "gancho 2", "pago", "transicion", "cta"):
                actual = [bloque, tipo.replace(" ", ""), []]
                crudos.append(actual)
            elif tipo == "cuerpo":
                actual = [bloque, "cuerpo", []]
                crudos.append(actual)
            elif tipo != "ejemplo":
                actual = None
            continue
        if actual is not None:
            actual[2].append(linea)

    segmentos = []
    for bloque, tipo, contenido in crudos:
        if tipo == "cuerpo":
            ejemplos = []
            for linea in contenido:
                m = VINETA.match(linea)
                if m:
                    ejemplos.append([m.group(1)])
                elif ejemplos and linea.strip():
                    ejemplos[-1].append(linea)
            for n, partes in enumerate(ejemplos, 1):
                segmentos.append(_segmento(bloque, "ejemplo", "\n".join(partes), n))
        else:
            segmento = _segmento(bloque, tipo, "\n".join(contenido))
            if segmento["texto"]:
                segmentos.append(segmento)

    imagen = 0
    for orden, s in enumerate(segmentos, 1):
        s["orden"] = orden
        if s["ilustrar"]:
            imagen += 1
            s["numero_imagen"] = imagen
    return titulo, segmentos


def _segmento(bloque, tipo, crudo, ejemplo=None):
    comentarios = [c.strip() for c in COMENTARIO.findall(crudo)]
    hilo = next((c.split(":", 1)[1].strip() for c in comentarios
                 if c.lower().startswith("hilo:")), None)
    ding = any(re.match(r"sonido\s*:\s*ding\b", c, re.IGNORECASE) for c in comentarios)
    negritas = NEGRITA.findall(COMENTARIO.sub("", crudo))
    if tipo == "ejemplo":
        ident = f"b{bloque}-ej{ejemplo}"
    elif bloque is None:
        ident = tipo
    else:
        ident = f"b{bloque}-{tipo}"
    return {
        "id": ident,
        "bloque": bloque,
        "tipo": tipo,
        "ejemplo": ejemplo,
        "texto": _limpiar(crudo),
        "ilustrar": tipo in TIPOS_CON_IMAGEN,
        "ding": ding,
        "destacada": negritas[0].strip() if negritas else None,
        "hilo": hilo,
    }


def nombre_base(segmento):
    """Nombre de archivo de imagen, numerado en orden: 01-b1-hook."""
    return f"{segmento['numero_imagen']:02d}-{segmento['id']}"


def nombre_audio(segmento):
    return f"{segmento['orden']:02d}-{segmento['id']}"
