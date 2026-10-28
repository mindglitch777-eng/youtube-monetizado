#!/usr/bin/env python3
"""
Ronda 3: ideas de video para "Explicado en Pijamas" (Pijama en el pasado).

  search    4 búsquedas por idea (2 en español por vistas, 1 en español por
            relevancia, 1 en inglés por vistas), videos de 4 a 20 minutos,
            últimos 24 meses, 50 resultados (cuesta lo mismo que 25).
  extra     búsquedas extra (ideas nuevas o videos de más de 20 minutos).
  details   detalle de todos los videos y canales (lotes de 50, 1 unidad).
  comments  comentarios más relevantes de los ids que se pasen (1 unidad c/u).

Clave en YOUTUBE_API_KEY (nunca se guarda). Todo queda en
research/data/ideas-2026-10/ y cada llamada se anota en cuota.log.
Una consulta ya guardada nunca se repite.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

API = "https://www.googleapis.com/youtube/v3"
KEY = os.environ.get("YOUTUBE_API_KEY")
OUT = Path(__file__).parent / "data" / "ideas-2026-10"
OUT.mkdir(parents=True, exist_ok=True)
LOG = OUT / "cuota.log"
TOPE_DIA = 9700  # unidades; la cuota gratis es 10.000 por día

# (n, idea, [(consulta, idioma, orden)])  — orden: v = viewCount, r = relevance
IDEAS = [
    (1, "Una noche a −30 °C en la Edad de Hielo", [
        ("cómo sobrevivían los humanos en la edad de hielo", "es", "v"),
        ("una noche en la edad de hielo", "es", "v"),
        ("cómo dormían en la edad de hielo con tanto frío", "es", "r"),
        ("how did humans survive the ice age", "en", "v")]),
    (2, "Qué hacían cuando se enfermaban (medicina prehistórica)", [
        ("medicina prehistórica cómo se curaban", "es", "v"),
        ("cómo eran los médicos en la antigüedad", "es", "v"),
        ("qué hacían los hombres prehistóricos cuando se enfermaban", "es", "r"),
        ("prehistoric medicine how did ancient people heal", "en", "v")]),
    (3, "Un día completo en una aldea de hace 10.000 años", [
        ("un día en la vida de un humano del neolítico", "es", "v"),
        ("cómo vivían hace 10000 años", "es", "v"),
        ("cómo era la vida en una aldea prehistórica", "es", "r"),
        ("a day in the life of a neolithic human", "en", "v")]),
    (4, "Cuánto durarías en cada época de la humanidad", [
        ("cuánto durarías en cada época de la historia", "es", "v"),
        ("sobrevivirías en otra época de la historia", "es", "v"),
        ("podrías sobrevivir en el pasado", "es", "r"),
        ("how long would you survive in every era of history", "en", "v")]),
    (5, "Así morirías en la Edad Media", [
        ("así morirías en la edad media", "es", "v"),
        ("cuánto durarías en la edad media", "es", "v"),
        ("cómo morían las personas en la edad media", "es", "r"),
        ("how you would die in the middle ages", "en", "v")]),
    (6, "Cuánto durarías en el Antiguo Egipto", [
        ("cuánto durarías en el antiguo egipto", "es", "v"),
        ("un día en el antiguo egipto", "es", "v"),
        ("cómo era la vida en el antiguo egipto", "es", "r"),
        ("could you survive in ancient egypt", "en", "v")]),
    (7, "Un día en la Antigua Roma (esclavo, ciudadano, gladiador)", [
        ("un día en la antigua roma", "es", "v"),
        ("cuánto durarías como gladiador", "es", "v"),
        ("cómo era la vida de un esclavo en roma", "es", "r"),
        ("a day in the life of an ancient roman", "en", "v")]),
    (8, "Cuánto durarías siendo un vikingo", [
        ("cuánto durarías como vikingo", "es", "v"),
        ("un día en la vida de un vikingo", "es", "v"),
        ("cómo era la vida de un vikingo", "es", "r"),
        ("could you survive as a viking", "en", "v")]),
    (9, "Qué pasaría si viajaras al pasado con tu celular", [
        ("qué pasaría si viajaras al pasado con tu celular", "es", "v"),
        ("qué pasaría si viajas en el tiempo a la edad media", "es", "v"),
        ("viajar al pasado con un celular", "es", "r"),
        ("what if you time traveled to the past with your phone", "en", "v")]),
    (10, "Qué trabajo tendrías en una tribu prehistórica", [
        ("qué trabajo tendrías en la prehistoria", "es", "v"),
        ("trabajos más antiguos de la humanidad", "es", "v"),
        ("trabajos en una tribu prehistórica", "es", "r"),
        ("what job would you have in the stone age", "en", "v")]),
    (11, "Qué comerías en la Edad de Piedra / Edad Media", [
        ("qué comían en la edad de piedra", "es", "v"),
        ("comer como en la edad media", "es", "v"),
        ("qué comían en la edad media", "es", "r"),
        ("what did people eat in the middle ages", "en", "v")]),
    (12, "Ir al baño, bañarse y dormir en el pasado", [
        ("cómo iban al baño en la antigüedad", "es", "v"),
        ("cómo dormían en la edad media", "es", "v"),
        ("cómo se bañaban en la edad media", "es", "r"),
        ("how did people go to the bathroom in medieval times", "en", "v")]),
    (13, "Cuánto durarías en la peste negra", [
        ("cuánto durarías en la peste negra", "es", "v"),
        ("la peste negra explicada", "es", "v"),
        ("cómo era vivir durante la peste negra", "es", "r"),
        ("could you survive the black death", "en", "v")]),
    (14, "Cuánto durarías de pirata", [
        ("cuánto durarías como pirata", "es", "v"),
        ("un día en la vida de un pirata", "es", "v"),
        ("cómo era la vida real de un pirata", "es", "r"),
        ("could you survive as a pirate", "en", "v")]),
    (15, "Cuánto durarías en el Imperio Azteca / Inca", [
        ("cuánto durarías en el imperio azteca", "es", "v"),
        ("cómo vivían los aztecas", "es", "v"),
        ("cómo era la vida en el imperio inca", "es", "r"),
        ("could you survive in the aztec empire", "en", "v")]),
    (16, "Cuánto durarías como soldado antiguo", [
        ("cuánto durarías como soldado romano", "es", "v"),
        ("cuánto durarías en esparta", "es", "v"),
        ("cómo era la vida de un soldado en la antigüedad", "es", "r"),
        ("could you survive as a roman legionary", "en", "v")]),
    (17, "Mitos de la prehistoria que son mentira", [
        ("mitos de la prehistoria que son mentira", "es", "v"),
        ("lo que te enseñaron mal sobre los cavernícolas", "es", "v"),
        ("los humanos prehistóricos vivían 30 años", "es", "r"),
        ("prehistoric myths debunked", "en", "v")]),
    (18, "Cómo se ligaba o se vivía en pareja en el pasado", [
        ("cómo se enamoraban en la prehistoria", "es", "v"),
        ("cómo se ligaba en la antigüedad", "es", "v"),
        ("cómo era el matrimonio en la edad media", "es", "r"),
        ("how did people find love in the past", "en", "v")]),
    (19, "La peor profesión de la historia", [
        ("los peores trabajos de la historia", "es", "v"),
        ("trabajos más asquerosos de la historia", "es", "v"),
        ("el peor trabajo de la edad media", "es", "r"),
        ("worst jobs in history", "en", "v")]),
    (20, "Tu primer día en el pasado hora por hora", [
        ("qué pasaría si despertaras en la prehistoria", "es", "v"),
        ("sobrevivir 24 horas en la prehistoria", "es", "v"),
        ("despertar en el pasado sobrevivir", "es", "r"),
        ("what if you woke up in the stone age", "en", "v")]),
]


def gastado_hoy():
    # la cuota se reinicia a medianoche hora del Pacífico (UTC-7 en octubre)
    hoy = (datetime.now(timezone.utc) - timedelta(hours=7)).strftime("%Y-%m-%d")
    tot = 0
    if LOG.exists():
        for line in LOG.read_text().splitlines():
            p = line.split("\t")
            if len(p) >= 4 and p[1] == hoy:
                tot += int(p[3])
    return hoy, tot


def get(ep, params, units, nota=""):
    hoy, tot = gastado_hoy()
    if tot + units > TOPE_DIA:
        raise SystemExit(f"tope diario: {tot} unidades gastadas hoy ({hoy}); seguir mañana")
    r = requests.get(f"{API}/{ep}", params={**params, "key": KEY}, timeout=30)
    with LOG.open("a") as f:
        f.write(f"{datetime.now(timezone.utc).isoformat(timespec='seconds')}\t{hoy}\t{ep}\t{units}\t"
                f"{tot + units}\t{r.status_code}\t{nota}\n")
    if r.status_code != 200:
        msg = r.json().get("error", {}).get("message", "")[:200]
        if "quota" in msg.lower():
            raise SystemExit(f"sin cuota: {msg}")
        raise RuntimeError(f"{ep} HTTP {r.status_code}: {msg}")
    return r.json()


def buscar(lista, idea, q, lang, orden, dur="medium"):
    path = OUT / "busquedas.json"
    done = json.loads(path.read_text()) if path.exists() else []
    o = {"v": "viewCount", "r": "relevance"}[orden]
    if any(d["consulta"] == q and d["orden"] == o and d["duracion"] == dur for d in done):
        return
    after = (datetime.now(timezone.utc) - timedelta(days=730)).strftime("%Y-%m-%dT%H:%M:%SZ")
    res = get("search", {"part": "snippet", "type": "video", "q": q, "maxResults": 50, "order": o,
                         "publishedAfter": after, "relevanceLanguage": lang, "videoDuration": dur}, 100, q)
    done.append({"idea": idea, "lista": lista, "consulta": q, "idioma": lang, "orden": o, "duracion": dur,
                 "publicado_despues_de": after, "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                 "items": res.get("items", [])})
    path.write_text(json.dumps(done, ensure_ascii=False, indent=1))
    print(f"#{idea} [{lang} {o} {dur}] {q}: {len(res.get('items', []))}", file=sys.stderr)


def cmd_search():
    for n, _, qs in IDEAS:
        for q, lang, orden in qs:
            buscar("semilla", n, q, lang, orden)


def cmd_extra(spec_file):
    # cada línea: idea<TAB>consulta<TAB>idioma<TAB>orden(v/r)<TAB>duracion(medium/long)
    for line in Path(spec_file).read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        idea, q, lang, orden, dur = line.split("\t")
        buscar("extra", idea, q, lang, orden, dur)


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
                                         "textFormat": "plainText"}, 1, vid)
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
    {"search": lambda: cmd_search(), "extra": lambda: cmd_extra(sys.argv[2]), "details": lambda: cmd_details(),
     "comments": lambda: cmd_comments(sys.argv[2:]), "hoy": lambda: print(gastado_hoy())}[cmd]()
