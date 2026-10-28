#!/usr/bin/env python3
"""
Ronda 2: huecos en español dentro del nicho "humanos antiguos".

  search    1 búsqueda por tema en español (últimos 12 meses, orden por vistas)
  details   detalle de todos los videos encontrados (lotes de 50, 1 unidad)
  comments  comentarios más relevantes de los videos ganadores (1 unidad c/u)

Clave en YOUTUBE_API_KEY (nunca se guarda). Todo queda en
research/data/huecos-2026-10/ y la cuota en cuota.json.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

API = "https://www.googleapis.com/youtube/v3"
KEY = os.environ.get("YOUTUBE_API_KEY")
OUT = Path(__file__).parent / "data" / "huecos-2026-10"
OUT.mkdir(parents=True, exist_ok=True)
QF = OUT / "cuota.json"
MAX_BUSQUEDAS = 20

# (tema, consulta en español)
BUSQUEDAS = [
    ("sueño/noche", "cómo dormían los humanos antiguos"),
    ("frío", "cómo sobrevivían al frío los humanos prehistóricos"),
    ("calor/desierto", "cómo soportaban el calor en la antigüedad sin aire acondicionado"),
    ("comida", "qué comían realmente los humanos prehistóricos"),
    ("agua", "cómo conseguían agua potable los humanos antiguos"),
    ("higiene/baño", "cómo se bañaban y limpiaban en la antigüedad"),
    ("dientes", "cómo se limpiaban los dientes en la prehistoria"),
    ("enfermedad/medicina", "cómo curaban heridas y enfermedades en la prehistoria"),
    ("niños/parto", "cómo daban a luz las mujeres en la prehistoria"),
    ("muerte/violencia", "el primer asesinato de la historia prehistoria"),
    ("depredadores", "qué animales cazaban a los humanos prehistóricos"),
    ("placer/aburrimiento", "cómo se divertían los humanos prehistóricos"),
    ("poder/religión", "cómo nació la religión en la prehistoria"),
    ("ropa/cuerpo", "qué ropa usaban los humanos prehistóricos"),
    ("lenguaje", "cómo hablaban los primeros humanos"),
    ("fuego/inventos", "cómo encendían fuego los humanos prehistóricos"),
    ("vida medieval", "cómo era realmente la vida de un campesino medieval"),
    ("sexo/pareja", "cómo eran las relaciones de pareja en la prehistoria"),
    # verificación de dos ángulos latinoamericanos
    ("latam: vida mexica", "cómo era un día en la vida de un mexica azteca"),
    ("latam: megafauna sudamericana", "megafauna sudamericana humanos edad de hielo megaterio gliptodonte"),
]


def quota(units):
    q = json.loads(QF.read_text()) if QF.exists() else {"total": 0, "search": 0, "otras": 0}
    q["total"] += units
    q["search" if units == 100 else "otras"] += 1
    QF.write_text(json.dumps(q, indent=1))


def get(ep, params, units):
    r = requests.get(f"{API}/{ep}", params={**params, "key": KEY}, timeout=30)
    quota(units)
    if r.status_code != 200:
        raise RuntimeError(f"{ep} HTTP {r.status_code}: {r.json().get('error', {}).get('message', '')[:200]}")
    return r.json()


def cmd_search():
    path = OUT / "busquedas.json"
    done = json.loads(path.read_text()) if path.exists() else []
    after = (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")
    for tema, q in BUSQUEDAS:
        if any(d["consulta"] == q for d in done):
            continue
        if len(done) >= MAX_BUSQUEDAS:
            print("tope de búsquedas alcanzado", file=sys.stderr)
            break
        res = get("search", {"part": "snippet", "type": "video", "q": q, "maxResults": 50, "order": "viewCount",
                             "publishedAfter": after, "relevanceLanguage": "es"}, 100)
        done.append({"tema": tema, "consulta": q, "publicado_despues_de": after, "items": res.get("items", [])})
        path.write_text(json.dumps(done, ensure_ascii=False, indent=1))
        print(f"{tema}: {len(res.get('items', []))}", file=sys.stderr)


def cmd_details():
    b = json.loads((OUT / "busquedas.json").read_text())
    ids = sorted({it["id"]["videoId"] for s in b for it in s["items"] if it["id"].get("videoId")})
    path = OUT / "videos.json"
    vids = json.loads(path.read_text()) if path.exists() else {}
    need = [i for i in ids if i not in vids]
    for k in range(0, len(need), 50):
        res = get("videos", {"part": "snippet,statistics,contentDetails", "id": ",".join(need[k:k + 50])}, 1)
        for it in res.get("items", []):
            vids[it["id"]] = it
    path.write_text(json.dumps(vids, ensure_ascii=False, indent=1))
    chs = sorted({v["snippet"]["channelId"] for v in vids.values()})
    cpath = OUT / "canales.json"
    cans = json.loads(cpath.read_text()) if cpath.exists() else {}
    need = [c for c in chs if c not in cans]
    for k in range(0, len(need), 50):
        res = get("channels", {"part": "snippet,statistics", "id": ",".join(need[k:k + 50])}, 1)
        for it in res.get("items", []):
            cans[it["id"]] = it
    cpath.write_text(json.dumps(cans, ensure_ascii=False, indent=1))
    print(f"videos {len(vids)} canales {len(cans)}", file=sys.stderr)


def cmd_comments(ids):
    path = OUT / "comentarios.json"
    com = json.loads(path.read_text()) if path.exists() else {}
    for vid in ids:
        if vid in com:
            continue
        try:
            res = get("commentThreads", {"part": "snippet", "videoId": vid, "order": "relevance", "maxResults": 100,
                                         "textFormat": "plainText"}, 1)
            com[vid] = [{"texto": it["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
                         "likes": it["snippet"]["topLevelComment"]["snippet"]["likeCount"],
                         "respuestas": it["snippet"]["totalReplyCount"]} for it in res.get("items", [])]
        except RuntimeError as e:
            com[vid] = {"error": str(e)}
        path.write_text(json.dumps(com, ensure_ascii=False, indent=1))
        print(f"{vid}: {len(com[vid]) if isinstance(com[vid], list) else com[vid]}", file=sys.stderr)


if __name__ == "__main__":
    if not KEY:
        raise SystemExit("Falta YOUTUBE_API_KEY")
    cmd = sys.argv[1]
    {"search": lambda: cmd_search(), "details": lambda: cmd_details(),
     "comments": lambda: cmd_comments(sys.argv[2:])}[cmd]()
