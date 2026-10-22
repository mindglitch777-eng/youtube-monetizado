#!/usr/bin/env python3
"""
Investigación de nichos faceless con la API de YouTube Data v3.

Lee la clave de la variable de entorno YOUTUBE_API_KEY (nunca se guarda en
el repo). Guarda TODO lo crudo en research/data/nichos-<fecha>/ y lleva la
cuenta de unidades de cuota gastadas (search = 100, el resto = 1).

Pasos:
  search    corre las búsquedas de QUERIES (videos de los últimos 90 días,
            ordenados por vistas) y guarda los resultados crudos.
  enrich    pide detalles de todos los videos y canales encontrados (lotes
            de 50 IDs), filtra canales < 200k subs, baja sus últimos 50
            uploads y calcula métricas por canal y outliers por video.
"""
import json
import os
import statistics
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

API = "https://www.googleapis.com/youtube/v3"
KEY = os.environ.get("YOUTUBE_API_KEY")
OUT = Path(__file__).parent / "data" / os.environ.get("RUN_DIR", "nichos-2026-10")
OUT.mkdir(parents=True, exist_ok=True)
QUOTA_FILE = OUT / "cuota.json"

MAX_SUBS = 200_000

# (tema, idioma, consulta, duración)  duración: any | long | medium | short
QUERIES = [
    # humanos antiguos / historia cotidiana
    ("historia_cotidiana", "en", "what life was like in ancient times", "any"),
    ("historia_cotidiana", "en", "prehistoric humans how they lived", "any"),
    ("historia_cotidiana", "en", "history for sleep", "long"),
    ("historia_cotidiana", "es", "cómo era la vida en la antigüedad", "any"),
    ("historia_cotidiana", "es", "humanos prehistóricos", "any"),
    ("historia_cotidiana", "pt", "como era a vida na antiguidade", "any"),
    ("historia_cotidiana", "de", "Leben im Mittelalter Doku", "any"),
    ("historia_cotidiana", "fr", "vie quotidienne au moyen âge", "any"),
    # psicología / comportamiento
    ("psicologia", "en", "psychology explained human behavior", "any"),
    ("psicologia", "en", "dark psychology", "any"),
    ("psicologia", "es", "psicología explicada comportamiento humano", "any"),
    ("psicologia", "es", "psicología oscura", "any"),
    ("psicologia", "pt", "psicologia explicada", "any"),
    ("psicologia", "de", "Psychologie erklärt", "any"),
    # animales prehistóricos / vida salvaje
    ("animales_prehistoricos", "en", "prehistoric animals documentary", "any"),
    ("animales_prehistoricos", "en", "prehistoric creatures size comparison", "any"),
    ("animales_prehistoricos", "es", "animales prehistóricos", "any"),
    ("animales_prehistoricos", "pt", "animais pré-históricos", "any"),
    ("vida_salvaje", "en", "wildlife documentary animals facts", "any"),
    ("vida_salvaje", "es", "documental animales salvajes", "any"),
    # ingeniería / megaobras
    ("ingenieria", "en", "megaprojects engineering", "any"),
    ("ingenieria", "en", "how it was built engineering explained", "any"),
    ("ingenieria", "es", "megaconstrucciones ingeniería", "any"),
    ("ingenieria", "pt", "megaconstruções engenharia", "any"),
    # ciencia explicada
    ("ciencia", "en", "science explained animation", "any"),
    ("ciencia", "en", "what if science scenario", "any"),
    ("ciencia", "es", "ciencia explicada", "any"),
    ("ciencia", "pt", "ciência explicada", "any"),
    ("ciencia", "hi", "विज्ञान रहस्य", "any"),
    # otros nichos faceless habituales (para comparar)
    ("espacio", "en", "space documentary universe", "any"),
    ("espacio", "es", "documental universo espacio", "any"),
    ("misterios", "en", "unsolved mysteries documentary", "any"),
    ("misterios", "es", "misterios sin resolver", "any"),
    ("estoicismo", "en", "stoicism", "any"),
    ("estoicismo", "es", "estoicismo", "any"),
    ("historias_biblicas", "en", "bible stories animated", "any"),
    ("historias_biblicas", "es", "historias de la biblia", "any"),
    ("geografia", "en", "geography explained why countries", "any"),
    ("finanzas", "en", "money explained economics", "any"),
    ("finanzas", "es", "economía explicada", "any"),
    # segunda ronda: profundizar en el subnicho que más fuerte salió
    # (vida cotidiana de humanos antiguos / supervivencia prehistórica)
    ("prof_vida_antigua", "en", "what did ancient humans actually do all day", "long"),
    ("prof_vida_antigua", "en", "how long would you survive in prehistoric times", "long"),
    ("prof_vida_antigua", "en", "your life as a medieval peasant", "long"),
    ("prof_vida_antigua", "es", "cómo vivían los humanos prehistóricos", "long"),
    ("prof_vida_antigua", "es", "cuánto sobrevivirías en la prehistoria", "any"),
    ("prof_vida_antigua", "es", "así era un día en la vida de un romano", "any"),
    ("prof_vida_antigua", "es", "documental prehistoria origen del ser humano", "long"),
    ("prof_vida_antigua", "pt", "como viviam os humanos pré-históricos", "any"),
    ("prof_vida_antigua", "pt", "documentário pré-história", "long"),
    ("prof_animales_prehist", "es", "megafauna extinta documental", "long"),
    ("prof_animales_prehist", "en", "ice age megafauna documentary", "long"),
    ("prof_psicologia", "es", "por qué el cerebro hace esto psicología", "long"),
]


def quota_add(units, what):
    q = json.loads(QUOTA_FILE.read_text()) if QUOTA_FILE.exists() else {"total": 0, "search_calls": 0, "other_calls": 0}
    q["total"] += units
    if units == 100:
        q["search_calls"] += 1
    else:
        q["other_calls"] += 1
    QUOTA_FILE.write_text(json.dumps(q, indent=1))


def get(endpoint, params, units):
    params = {**params, "key": KEY}
    for attempt in range(3):
        r = requests.get(f"{API}/{endpoint}", params=params, timeout=30)
        if r.status_code == 200:
            quota_add(units, endpoint)
            return r.json()
        if r.status_code >= 500:
            time.sleep(2 ** attempt)
            continue
        quota_add(units, endpoint)  # los errores 4xx también descuentan cuota
        raise SystemExit(f"{endpoint} HTTP {r.status_code}: {r.json().get('error', {}).get('message')}")
    raise SystemExit(f"{endpoint}: falló 3 veces")


def chunks(xs, n=50):
    for i in range(0, len(xs), n):
        yield xs[i:i + n]


def iso_dur(s):
    """PT1H2M3S -> segundos"""
    import re
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s or "")
    if not m:
        return None
    d, h, mi, se = (int(x) if x else 0 for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + se


def cmd_search(only=None):
    after = (datetime.now(timezone.utc) - timedelta(days=90)).strftime("%Y-%m-%dT%H:%M:%SZ")
    path = OUT / "busquedas.json"
    done = json.loads(path.read_text()) if path.exists() else []
    done_keys = {(d["tema"], d["idioma"], d["consulta"]) for d in done}
    for tema, lang, q, dur in QUERIES:
        if (tema, lang, q) in done_keys or (only and tema not in only):
            continue
        params = {"part": "snippet", "type": "video", "q": q, "maxResults": 50,
                  "order": "viewCount", "publishedAfter": after, "relevanceLanguage": lang}
        if dur != "any":
            params["videoDuration"] = dur
        res = get("search", params, 100)
        done.append({"tema": tema, "idioma": lang, "consulta": q, "duracion": dur,
                     "publicado_despues_de": after, "fecha_busqueda": datetime.now(timezone.utc).isoformat(),
                     "items": res.get("items", [])})
        path.write_text(json.dumps(done, ensure_ascii=False, indent=1))
        print(f"{tema}/{lang}: {len(res.get('items', []))} videos", file=sys.stderr)


def videos_details(ids):
    out = {}
    for c in chunks(list(ids)):
        res = get("videos", {"part": "snippet,statistics,contentDetails", "id": ",".join(c), "maxResults": 50}, 1)
        for it in res.get("items", []):
            out[it["id"]] = it
    return out


def cmd_enrich():
    busq = json.loads((OUT / "busquedas.json").read_text())
    found = {}  # video_id -> (tema, idioma)
    for b in busq:
        for it in b["items"]:
            vid = it["id"].get("videoId")
            if vid:
                found.setdefault(vid, []).append((b["tema"], b["idioma"], b["consulta"]))

    vpath = OUT / "videos_busqueda.json"
    vids = json.loads(vpath.read_text()) if vpath.exists() else {}
    vids.update(videos_details([v for v in found if v not in vids]))
    vpath.write_text(json.dumps(vids, ensure_ascii=False, indent=1))

    chan_ids = sorted({v["snippet"]["channelId"] for v in vids.values()})
    cpath = OUT / "canales.json"
    chans = json.loads(cpath.read_text()) if cpath.exists() else {}
    if True:
        for c in chunks([x for x in chan_ids if x not in chans]):
            res = get("channels", {"part": "snippet,statistics,contentDetails,topicDetails,brandingSettings",
                                   "id": ",".join(c), "maxResults": 50}, 1)
            for it in res.get("items", []):
                chans[it["id"]] = it
        cpath.write_text(json.dumps(chans, ensure_ascii=False, indent=1))

    # candidatos: < 200k subs (y subs visibles)
    cand = [cid for cid, ch in chans.items()
            if not ch["statistics"].get("hiddenSubscriberCount")
            and int(ch["statistics"].get("subscriberCount", 0)) < MAX_SUBS]

    upath = OUT / "uploads.json"
    uploads = json.loads(upath.read_text()) if upath.exists() else {}
    for cid in cand:
        if cid in uploads:
            continue
        pl = chans[cid]["contentDetails"]["relatedPlaylists"]["uploads"]
        try:
            res = get("playlistItems", {"part": "contentDetails", "playlistId": pl, "maxResults": 50}, 1)
            uploads[cid] = [it["contentDetails"]["videoId"] for it in res.get("items", [])]
        except SystemExit as e:
            uploads[cid] = {"error": str(e)}
        upath.write_text(json.dumps(uploads, ensure_ascii=False, indent=1))

    updet_path = OUT / "videos_canales.json"
    updet = json.loads(updet_path.read_text()) if updet_path.exists() else {}
    need = [v for lst in uploads.values() if isinstance(lst, list) for v in lst if v not in updet]
    updet.update(videos_details(need))
    updet_path.write_text(json.dumps(updet, ensure_ascii=False, indent=1))

    now = datetime.now(timezone.utc)
    rows, outliers = [], []
    for cid in cand:
        ch = chans[cid]
        st = ch["statistics"]
        lst = uploads.get(cid)
        if not isinstance(lst, list):
            continue
        vs = [updet[v] for v in lst if v in updet]
        vs.sort(key=lambda v: v["snippet"]["publishedAt"], reverse=True)
        views = [int(v["statistics"].get("viewCount", 0)) for v in vs]
        last10 = views[:10]
        med = statistics.median(last10) if last10 else 0
        created = datetime.fromisoformat(ch["snippet"]["publishedAt"].replace("Z", "+00:00"))
        durs = [iso_dur(v["contentDetails"].get("duration")) or 0 for v in vs[:10]]
        shorts = sum(1 for d in durs if d <= 180)
        temas = sorted({t for v in found if vids.get(v, {}).get("snippet", {}).get("channelId") == cid for t, _, _ in found[v]})
        idiomas = sorted({l for v in found if vids.get(v, {}).get("snippet", {}).get("channelId") == cid for _, l, _ in found[v]})
        top = max(vs, key=lambda v: int(v["statistics"].get("viewCount", 0))) if vs else None
        subs = int(st.get("subscriberCount", 0))
        total = int(st.get("viewCount", 0))
        rows.append({
            "channel_id": cid,
            "canal": ch["snippet"]["title"],
            "url": f"https://www.youtube.com/channel/{cid}",
            "handle": ch["snippet"].get("customUrl"),
            "pais": ch["snippet"].get("country"),
            "temas": ",".join(temas),
            "idiomas_busqueda": ",".join(idiomas),
            "creado": ch["snippet"]["publishedAt"][:10],
            "meses_de_vida": round((now - created).days / 30.4, 1),
            "subs": subs,
            "vistas_totales": total,
            "videos": int(st.get("videoCount", 0)),
            "vistas_por_sub": round(total / subs, 1) if subs else None,
            "mediana_ult10": int(med),
            "pct_shorts_ult10": round(100 * shorts / len(durs)) if durs else None,
            "duracion_mediana_ult10_s": int(statistics.median(durs)) if durs else None,
            "top_video_id": top["id"] if top else None,
            "top_video_titulo": top["snippet"]["title"] if top else None,
            "top_video_vistas": int(top["statistics"].get("viewCount", 0)) if top else None,
            "uploads_revisados": len(vs),
        })
        for v in vs:
            vv = int(v["statistics"].get("viewCount", 0))
            if med and vv >= 3 * med and vv >= 50_000:
                outliers.append({
                    "channel_id": cid, "canal": ch["snippet"]["title"], "subs": subs,
                    "video_id": v["id"], "titulo": v["snippet"]["title"],
                    "publicado": v["snippet"]["publishedAt"][:10],
                    "vistas": vv, "likes": int(v["statistics"].get("likeCount", 0) or 0),
                    "comentarios": int(v["statistics"].get("commentCount", 0) or 0),
                    "duracion_s": iso_dur(v["contentDetails"].get("duration")),
                    "mediana_canal": int(med), "factor_outlier": round(vv / med, 1),
                    "vistas_por_sub": round(vv / subs, 1) if subs else None,
                })
    (OUT / "canales_metricas.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1))
    (OUT / "outliers.json").write_text(json.dumps(outliers, ensure_ascii=False, indent=1))
    import csv
    for name, data in (("canales_metricas.csv", rows), ("outliers.csv", outliers)):
        if data:
            with open(OUT / name, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(data[0].keys()))
                w.writeheader()
                w.writerows(data)
    print(f"canales totales: {len(chans)}  candidatos <200k: {len(cand)}  outliers: {len(outliers)}", file=sys.stderr)
    print(QUOTA_FILE.read_text(), file=sys.stderr)


if __name__ == "__main__":
    if not KEY:
        raise SystemExit("Falta YOUTUBE_API_KEY")
    step = sys.argv[1]
    if step == "search":
        cmd_search(sys.argv[2:] or None)
    elif step == "enrich":
        cmd_enrich()
