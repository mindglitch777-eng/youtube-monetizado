#!/usr/bin/env python3
"""
Video 3: barrido amplio de videos que explotaron en canales chicos o nuevos.

  search   una búsqueda por consulta (últimos 6 meses, por vistas, 50
           resultados, videos de 4 a 20 min o de más de 20 min según la consulta)
  details  detalle de todos los videos y canales encontrados (lotes de 50)
  tabla    arma research/data/video3-2026-10/tabla.json con los indicadores

Clave en YOUTUBE_API_KEY (nunca se guarda). Cada llamada se anota en
cuota.log y una consulta ya guardada nunca se repite.
"""
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

API = "https://www.googleapis.com/youtube/v3"
KEY = os.environ.get("YOUTUBE_API_KEY")
OUT = Path(__file__).parent / "data" / "video3-2026-10"
OUT.mkdir(parents=True, exist_ok=True)
LOG = OUT / "cuota.log"
TOPE_DIA = 9500
HOY = datetime(2026, 10, 26, tzinfo=timezone.utc)
DESDE = (HOY - timedelta(days=183)).strftime("%Y-%m-%dT00:00:00Z")

# (consulta, idioma, duración)  duración: medium = 4–20 min, long = >20 min
CONSULTAS = [
    # supervivencia / "qué pasaría si" en el pasado (nuestro terreno)
    ("cuánto durarías", "es", "medium"),
    ("qué pasaría si viajaras al pasado", "es", "medium"),
    ("sobrevivir en la edad media", "es", "medium"),
    ("cómo era la vida hace 1000 años", "es", "medium"),
    ("un día en la vida de", "es", "medium"),
    ("how long would you survive", "en", "medium"),
    ("what if you woke up in", "en", "medium"),
    ("a day in the life of a medieval", "en", "medium"),
    ("survive history", "en", "medium"),
    # historia oscura / rara
    ("los peores trabajos de la historia", "es", "medium"),
    ("castigos más crueles de la historia", "es", "medium"),
    ("cosas asquerosas que hacían en el pasado", "es", "medium"),
    ("historia que no te contaron en la escuela", "es", "medium"),
    ("worst jobs in history", "en", "medium"),
    ("disgusting things people did in the past", "en", "medium"),
    ("dark history", "en", "medium"),
    # formatos: escala, niveles, iceberg, comparaciones, cronologías
    ("niveles de", "es", "medium"),
    ("iceberg de la historia", "es", "medium"),
    ("cada año de la historia", "es", "medium"),
    ("evolución de", "es", "medium"),
    ("every level of", "en", "medium"),
    ("iceberg explained", "en", "long"),
    ("timeline of", "en", "medium"),
    ("every year until", "en", "medium"),
    ("tier list historia", "es", "medium"),
    ("history tier list", "en", "medium"),
    # dormir / largos (formato que paga bien y casi no existe en español)
    ("historia para dormir", "es", "long"),
    ("history for sleep", "en", "long"),
    ("datos aburridos para dormir", "es", "long"),
    ("boring history to fall asleep", "en", "long"),
    # ciencia / cuerpo humano / qué pasaría
    ("qué le pasa a tu cuerpo si", "es", "medium"),
    ("qué pasaría si", "es", "medium"),
    ("what happens to your body if", "en", "medium"),
    ("what would happen if", "en", "medium"),
    # misterio / civilizaciones
    ("civilizaciones perdidas", "es", "medium"),
    ("misterios sin resolver de la historia", "es", "medium"),
    ("lost civilizations", "en", "medium"),
    # animación / personaje (lo nuestro: personaje que viaja)
    ("animación historia", "es", "medium"),
    ("historia animada", "es", "medium"),
    ("animated history", "en", "medium"),
    ("2d animation explained", "en", "medium"),
    # comparaciones de precio / dinero en la historia
    ("cuánto costaba en la antigüedad", "es", "medium"),
    ("how much did it cost in medieval times", "en", "medium"),
    # "pov" y segunda persona
    ("pov eres", "es", "medium"),
    ("pov you are", "en", "medium"),
    # curiosidades generales / documentales en español
    ("curiosidades de la historia", "es", "medium"),
    ("documental historia", "es", "long"),
    ("datos que no sabías", "es", "medium"),
    # profesiones / vida cotidiana
    ("cómo se bañaban en la edad media", "es", "medium"),
    ("cómo era ser niño en", "es", "medium"),
    ("what it was like to be", "en", "medium"),
    # extremos
    ("el lugar más peligroso del mundo", "es", "medium"),
    ("most dangerous", "en", "medium"),
    ("sobrevivir 24 horas", "es", "medium"),
    # futuro / inverso
    ("qué pasará en el futuro", "es", "medium"),
    ("what will happen in 1000 years", "en", "medium"),
]


def gastado_hoy():
    if not LOG.exists():
        return 0
    hoy = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return sum(int(l.split()[1]) for l in LOG.read_text().splitlines() if l.startswith(hoy))


def get(recurso, costo, **p):
    if gastado_hoy() + costo > TOPE_DIA:
        raise SystemExit("tope de cuota del día")
    p["key"] = KEY
    r = requests.get(f"{API}/{recurso}", params=p, timeout=60)
    with LOG.open("a") as f:
        f.write(f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')} {costo} {recurso} {p.get('q', '')}\n")
    r.raise_for_status()
    return r.json()


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower())[:60]


def search():
    d = OUT / "search"
    d.mkdir(exist_ok=True)
    for q, lang, dur in CONSULTAS:
        f = d / f"{lang}_{dur}_{slug(q)}.json"
        if f.exists():
            continue
        r = get("search", 100, part="snippet", q=q, type="video", order="viewCount", maxResults=50,
                publishedAfter=DESDE, videoDuration=dur, relevanceLanguage=lang)
        f.write_text(json.dumps({"q": q, "lang": lang, "dur": dur, "items": r.get("items", [])}, ensure_ascii=False))
        print(f"{q}: {len(r.get('items', []))}")


def lotes(ids, n=50):
    ids = list(ids)
    for i in range(0, len(ids), n):
        yield ids[i:i + n]


def details():
    vids, chans = set(), set()
    for f in (OUT / "search").glob("*.json"):
        for it in json.loads(f.read_text())["items"]:
            vids.add(it["id"]["videoId"])
            chans.add(it["snippet"]["channelId"])
    vf, cf = OUT / "videos.json", OUT / "canales.json"
    V = json.loads(vf.read_text()) if vf.exists() else {}
    C = json.loads(cf.read_text()) if cf.exists() else {}
    for l in lotes(sorted(vids - set(V))):
        for it in get("videos", 1, part="snippet,statistics,contentDetails", id=",".join(l))["items"]:
            V[it["id"]] = it
    for l in lotes(sorted(chans - set(C))):
        for it in get("channels", 1, part="snippet,statistics", id=",".join(l))["items"]:
            C[it["id"]] = it
    vf.write_text(json.dumps(V, ensure_ascii=False))
    cf.write_text(json.dumps(C, ensure_ascii=False))
    print(f"{len(V)} videos, {len(C)} canales")


def dur_s(iso):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    return sum(int(x or 0) * k for x, k in zip(m.groups(), (3600, 60, 1))) if m else 0


def fecha(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def tabla():
    V = json.loads((OUT / "videos.json").read_text())
    C = json.loads((OUT / "canales.json").read_text())
    origen = {}
    for f in (OUT / "search").glob("*.json"):
        d = json.loads(f.read_text())
        for it in d["items"]:
            origen.setdefault(it["id"]["videoId"], []).append(f"{d['lang']}:{d['q']}")
    filas = []
    for vid, v in V.items():
        c = C.get(v["snippet"]["channelId"])
        if not c:
            continue
        st, cs = v.get("statistics", {}), c.get("statistics", {})
        vistas = int(st.get("viewCount", 0))
        subs = int(cs.get("subscriberCount", 0)) if not cs.get("hiddenSubscriberCount") else None
        dias = max(1, (HOY - fecha(v["snippet"]["publishedAt"])).days)
        edad_canal = max(1, (HOY - fecha(c["snippet"]["publishedAt"])).days)
        vids_canal = int(cs.get("videoCount", 0)) or 1
        vistas_canal = int(cs.get("viewCount", 0))
        filas.append({
            "id": vid, "titulo": v["snippet"]["title"], "canal": c["snippet"]["title"], "canal_id": c["id"],
            "idioma": v["snippet"].get("defaultAudioLanguage") or v["snippet"].get("defaultLanguage") or "",
            "pais": c["snippet"].get("country", ""),
            "publicado": v["snippet"]["publishedAt"][:10], "dias": dias,
            "dur": dur_s(v["contentDetails"].get("duration")),
            "vistas": vistas, "vistas_dia": round(vistas / dias),
            "likes": int(st.get("likes", st.get("likeCount", 0))), "coment": int(st.get("commentCount", 0)),
            "subs": subs, "ratio_vs_subs": round(vistas / subs, 1) if subs else None,
            "canal_creado": c["snippet"]["publishedAt"][:10], "edad_canal_dias": edad_canal,
            "videos_canal": vids_canal, "vistas_canal": vistas_canal,
            "prom_canal": round(vistas_canal / vids_canal),
            "outlier_vs_prom": round(vistas / max(1, vistas_canal / vids_canal), 1),
            "vistas_canal_mes": round(vistas_canal / edad_canal * 30),
            "consultas": origen.get(vid, []),
        })
    filas.sort(key=lambda r: -r["vistas_dia"])
    (OUT / "tabla.json").write_text(json.dumps(filas, ensure_ascii=False, indent=0))
    print(f"{len(filas)} filas")


if __name__ == "__main__":
    if not KEY and sys.argv[1] != "tabla":
        raise SystemExit("Falta YOUTUBE_API_KEY")
    {"search": search, "details": details, "tabla": tabla}[sys.argv[1]]()
