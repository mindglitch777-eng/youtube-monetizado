#!/usr/bin/env python3
"""
Ronda 3, paso 2: métricas por video y notas de mercado por idea.

No usa la API: lee lo guardado en research/data/ideas-2026-10/ (y los videos
de la ronda 2 que entren en la ventana de 24 meses) y escribe:

  videos_metricas.json / .csv   cada video con sus métricas y las ideas a las que pertenece
  mercado_ideas.json            demanda, competencia y prueba para canales chicos por idea
"""
import csv
import json
import re
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE = Path(__file__).parent / "data"
OUT = BASE / "ideas-2026-10"
AHORA = datetime.now(timezone.utc)
VENTANA = AHORA - timedelta(days=730)
HISPANOS = {"AR", "BO", "CL", "CO", "CR", "CU", "DO", "EC", "ES", "GT", "HN", "MX", "NI", "PA", "PE", "PR", "PY", "SV",
            "UY", "VE", "US"}  # US: muchos creadores hispanos viven allá, no se marca como traducción solo por eso


def plano(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


ANTIGUO = (r"prehist|antig|ancient|stone age|edad de piedra|primeros humanos|early humans|first humans|cavern|caveman|"
           r"cavemen|paleolit|neolit|medieval|edad media|middle ages|pasado|the past|histor|viking|vikin|roman|egipt|"
           r"egypt|aztec|tribu|tribe|hunter.?gather|cazador|neander|sapiens|siglo|century|ice age|edad de hielo")

PREHIST = (r"prehist|stone age|edad de piedra|cavern|caveman|cavemen|paleolit|neolit|tribu|tribe|ancient humans|humanos antiguos|"
           r"primeros humanos|early humans|first humans|hunter.?gather|cazador|neander|ice age|edad de hielo|10.?000|antepasados|ancestors")
# títulos que caen por palabra suelta pero no son del tema (juegos, anime, ficción, deportes, paranormal)
RUIDO = re.compile(r"goku|resident evil|roblox|minecraft|\bnba\b|warhammer|banquet challenge|beardmeats|fortnite|\beu5\b|"
                   r"\bguide\b|venezuela|anime|manhwa|manga|gameplay|\bsims\b|backrooms|windrose|skeleton army|miglorn|"
                   r"resumen|recap|pelicula|movie|monja|paradox|paradoja|viajeros en el tiempo|mike marcum|b-2|marine platoon|"
                   r"cretacico|carbonifero|orcas|serial killer|apex predator|depredador|rap\b|song|cancion|somali|salazar|mr increible")

# (n, patrón obligatorio, patrón de contexto o None)
REGLAS = {
    1: (r"edad de hielo|era de hielo|ice age|glacia|era glaciar|\bfrio\b|\bcold\b|winter|invierno|-3\d|congel|freez", PREHIST),
    2: (r"medicin|medico|enferm|curab|se curaban|heal|surgery|surgeon|cirug|trepan|doctor|sick|disease|dentist|dentis", ANTIGUO),
    3: (r"neolit|aldea|village|10.?000 (anos|years)|10k years|primeros agricult|first farmers|catal|gobekli|"
        r"todo el dia|all day|un dia (completo )?en la vida|a day in the life|daily life|vida diaria|vida cotidiana", PREHIST),
    4: (r"(cada|todas las|every|each) .*(epoca|era|period|periodo|siglo|century)", r"sobreviv|surviv|durar|how long|cuanto|last"),
    5: (r"edad media|medieval|middle ages|medievo", None),
    6: (r"egipt|egypt|faraon|pharaoh", None),
    7: (r"\broma\b|romano|romana|\broman|gladiad|gladiator|pompey|pompeya|pompeii", None),
    8: (r"vikin", None),
    9: (r"(celular|telefono|phone|smartphone|iphone|movil).*(pasado|past|tiempo|time|medieval|edad media|prehist|stone age)|"
        r"(pasado|past|tiempo|time|medieval|edad media|prehist|stone age).*(celular|telefono|phone|smartphone|iphone|movil)|"
        r"viaj\w* (en el tiempo|al pasado)|time travel", PREHIST + "|" + ANTIGUO),
    10: (r"trabajo|empleo|\bjobs?\b|profesion|oficio|\bwork(ed|ers?)?\b|occupation|rol\b|role", PREHIST),
    11: (r"comian|comer|comida|\bfood|\beat\b|\bate\b|eating|diet|dieta|cocina|cook|recet|recipe|\bmeal", ANTIGUO),
    12: (r"\bbano|banaban|banarse|toilet|bathroom|\bpoop|higiene|hygiene|dormian|dormir|\bsleep|\bbath|wash|lavaban|"
         r"limpiaban|\bwc\b|letrina|latrine|caca", ANTIGUO),
    13: (r"peste|plague|black death", None),
    14: (r"pirat", None),
    15: (r"azteca|aztec|\binca|mexica|tenochtitl|\bmaya", None),
    16: (r"soldad|soldier|legion|esparta|spart|samur|hoplit|guerrer|warrior|gladiad|gladiator|caballero|knight|batalla|battle",
         r"roman|esparta|spart|samur|hoplit|griego|greek|medieval|edad media|vikin|legion|gladiad|azteca|aztec|antig|ancient|persa|persian"),
    17: (r"\bmitos?\b|myths?|mentira|\blies\b|wrong|equivoc|falso|false|misconcep|debunk|te ensenaron|you were taught|(vivian|lived|vivir\w*) .*(30|treinta) (anos|years)|30 (anos|years)", ANTIGUO),
    18: (r"\bamor\b|\blove\b|pareja|matrimon|marri|\bsexo?\b|dating|\bligar|ligaban|enamor|romance|\bcita", ANTIGUO),
    19: (r"(peor|worst|asqueros|disgusting|horrible|terrible|deadliest|mas peligros).*(trabajo|\bjobs?\b|profesion|oficio|empleo)|"
         r"(trabajo|\bjobs?\b|profesion|oficio|empleo).*(peor|worst|asqueros|disgusting|horrible)", None),
    20: (r"despert|woke up|wake up|transport|viaj\w* (en el tiempo|al pasado)|time travel|sent back|24 horas|24 hours|"
         r"primer dia|first day|survive.*day|sobrevivir.*dia|\d+ (days|dias) in|spends? \d+|pasa \d+", r"egypt|egipt|roma|roman|medieval|edad media|prehist|stone age|edad de piedra|caveman|cavern|paleolit|"
                                                                  r"ice age|edad de hielo|pasado|the past|1.000.000|million years|"
                                                                  r"neander|primeros humanos|early humans|10.?000"),
    # ideas nuevas que aparecieron en los datos
    21: (r"(worst|peor\w*) .*(years?|periods?|times?|anos?|epocas?|momentos?|siglos?|centur\w*) .*(alive|vivo|vivir|to live|nacer|born)", None),
    22: (r"(\bsin\b|without) (aire acondicionado|air condition\w*|calefaccion|heating|refrigera\w*|fridge|nevera|"
         r"papel higienico|toilet paper|jabon|soap|antibiotic\w*|electric\w*|firewood|lena|congelarse|freezing|morir)|"
         r"(how did|como|que hacian|what did).*(sleep|dorm|surviv|sobreviv|hac\w*).*(heat|calor|cold|frio|mosquit|desert|"
         r"desierto|winter|invierno|blizzard|-3\d|50)", ANTIGUO),
    23: (r"(modern\w*|de hoy|actual\w*|gym bro|iphone|celular|telefono|phone|smartphone).*(\bpast\b|pasado|ancient|antig|"
         r"medieval|edad media|prehist|stone age|\brome\b|\broma\b|egypt|egipt|century|siglo)", None),
}
NOMBRES = {21: "Los peores años (o épocas) para estar vivo", 22: "Cómo sobrevivían al calor, frío o bichos sin nada moderno",
           23: "Una persona de hoy (o su celular) en el pasado"}


def dur_seg(iso):
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return None
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


ES_PAL = re.compile(r"\b(el|la|los|las|que|como|cómo|qué|por|para|una|del|era|vida|años|durarías|sobrevivir|historia)\b")
EN_PAL = re.compile(r"\b(the|how|what|you|would|life|in|of|and|was|were|did|why|years|survive|history)\b")


def idioma(v):
    sn = v["snippet"]
    lang = (sn.get("defaultAudioLanguage") or sn.get("defaultLanguage") or "").lower()
    if lang.startswith("es"):
        return "es"
    if lang.startswith("en"):
        return "en"
    if lang:
        return "otro"
    t = sn["title"].lower()
    es, en = len(ES_PAL.findall(t)), len(EN_PAL.findall(t))
    if re.search(r"[áéíóúñ¿¡]", t):
        es += 2
    return "es" if es > en else "en" if en > es else "?"


def main():
    busq = json.loads((OUT / "busquedas.json").read_text())
    vids = json.loads((OUT / "videos.json").read_text())
    cans = json.loads((OUT / "canales.json").read_text())
    for n, nombre, _ in __import__("ideas").IDEAS:  # 1 a 20
        NOMBRES[n] = nombre
    # de qué búsqueda salió cada video
    origen = {}
    for b in busq:
        for it in b["items"]:
            vid = it["id"].get("videoId")
            if vid:
                origen.setdefault(vid, set()).add(str(b["idea"]))
    # ronda 2 (mismo nicho, 12 meses): se suma si tiene los datos del canal
    r2v = BASE / "huecos-2026-10" / "videos.json"
    r2c = BASE / "huecos-2026-10" / "canales.json"
    if r2v.exists() and r2c.exists():
        for k, v in json.loads(r2v.read_text()).items():
            vids.setdefault(k, v)
            origen.setdefault(k, set()).add("ronda2")
        for k, c in json.loads(r2c.read_text()).items():
            cans.setdefault(k, c)

    filas = []
    for vid, v in vids.items():
        sn, st = v["snippet"], v.get("statistics", {})
        pub = datetime.fromisoformat(sn["publishedAt"].replace("Z", "+00:00"))
        if pub < VENTANA:
            continue
        seg = dur_seg(v.get("contentDetails", {}).get("duration"))
        if seg is None or seg < 240:  # solo videos de 4 minutos o más
            continue
        c = cans.get(sn["channelId"], {})
        cs, csn = c.get("statistics", {}), c.get("snippet", {})
        subs = None if cs.get("hiddenSubscriberCount") else int(cs.get("subscriberCount", 0) or 0)
        vistas = int(st.get("viewCount", 0) or 0)
        likes = int(st["likeCount"]) if "likeCount" in st else None
        dias = max(1, (AHORA - pub).days)
        cpub = csn.get("publishedAt")
        edad_canal = (pub - datetime.fromisoformat(cpub.replace("Z", "+00:00"))).days if cpub else None
        t = plano(sn["title"])
        ideas = []
        for n, (pat, ctx) in REGLAS.items():
            if not RUIDO.search(t) and re.search(pat, t) and (ctx is None or re.search(ctx, t)):
                ideas.append(n)
        salto = round(vistas / subs, 2) if subs else None
        ganador = vistas >= 10000 and ((subs is not None and subs > 0 and vistas >= 10 * subs) or
                                       (vistas > 100000 and subs is not None and subs < 20000))
        fracaso = vistas < 1000 and dias >= 60
        pais = csn.get("country", "")
        ct = plano(csn.get("title", ""))
        lang = idioma(v)
        trad = lang == "es" and (bool(pais) and pais not in HISPANOS or bool(re.search(r"espanol|\bes\b|spanish", ct)))
        filas.append({
            "id": vid, "url": f"https://www.youtube.com/watch?v={vid}", "titulo": sn["title"], "idioma": lang,
            "canal": csn.get("title", sn.get("channelTitle")), "canal_id": sn["channelId"], "pais_canal": pais,
            "subs": subs, "videos_canal": int(cs.get("videoCount", 0) or 0), "publicado": sn["publishedAt"][:10],
            "dias": dias, "duracion_min": round(seg / 60, 1), "vistas": vistas, "vistas_dia": round(vistas / dias, 1),
            "salto": salto, "likes_vistas": round(likes / vistas, 4) if likes is not None and vistas else None,
            "comentarios": int(st.get("commentCount", 0) or 0) if "commentCount" in st else None,
            "edad_canal_al_publicar_dias": edad_canal, "ganador": ganador, "fracaso": fracaso,
            "posible_traduccion": trad, "ideas": ideas, "salio_de": sorted(origen.get(vid, [])),
            "miniatura": (sn.get("thumbnails", {}).get("high") or sn.get("thumbnails", {}).get("default") or {}).get("url"),
        })
    filas.sort(key=lambda f: -f["vistas"])
    (OUT / "videos_metricas.json").write_text(json.dumps(filas, ensure_ascii=False, indent=1))
    campos = [k for k in filas[0] if k != "ideas"] + ["ideas"]
    with (OUT / "videos_metricas.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for r in filas:
            w.writerow({**r, "ideas": " ".join(map(str, r["ideas"])), "salio_de": " ".join(r["salio_de"])})

    seis = (AHORA - timedelta(days=183)).strftime("%Y-%m-%d")
    mercado = []
    for n in REGLAS:
        rel = [f for f in filas if n in f["ideas"]]
        out = {"idea": n, "nombre": NOMBRES[n]}
        for lg in ("es", "en"):
            r = [f for f in rel if f["idioma"] == lg]
            g = [f for f in r if f["ganador"]]
            out[lg] = {
                "videos": len(r),
                "canales": len({f["canal_id"] for f in r}),
                "videos_ultimos_6_meses": sum(f["publicado"] >= seis for f in r),
                "top5_vistas": [f["vistas"] for f in r[:5]],
                "mediana_vistas": sorted(f["vistas"] for f in r)[len(r) // 2] if r else None,
                "videos_100k": sum(f["vistas"] >= 100000 for f in r),
                "videos_1M": sum(f["vistas"] >= 1000000 for f in r),
                "ganadores": len(g),
                "ganadores_canal_chico": sum(1 for f in g if f["subs"] is not None and f["subs"] < 20000),
                "fracasos": sum(f["fracaso"] for f in r),
                "posibles_traducciones": sum(f["posible_traduccion"] for f in r),
                "mejores": [{k: f[k] for k in ("id", "titulo", "canal", "subs", "vistas", "publicado", "salto",
                                               "duracion_min", "ganador", "posible_traduccion")} for f in r[:8]],
                "mejores_ganadores": [{k: f[k] for k in ("id", "titulo", "canal", "subs", "vistas", "publicado", "salto",
                                                         "duracion_min")} for f in sorted(g, key=lambda f: -(f["salto"] or 0))[:8]],
                "fracasos_ejemplo": [{k: f[k] for k in ("id", "titulo", "canal", "subs", "vistas", "publicado")}
                                     for f in r if f["fracaso"]][:3],
            }
        mercado.append(out)
    (OUT / "mercado_ideas.json").write_text(json.dumps(mercado, ensure_ascii=False, indent=1))
    print(f"{len(filas)} videos de 4+ min en 24 meses; ganadores {sum(f['ganador'] for f in filas)}")
    for m in mercado:
        e, i = m["es"], m["en"]
        print(f"#{m['idea']:>2} {m['nombre'][:42]:42} ES v{e['videos']:>3} c{e['canales']:>3} top{(e['top5_vistas'] or [0])[0]:>9,} "
              f"100k{e['videos_100k']:>3} G{e['ganadores']:>3} Gch{e['ganadores_canal_chico']:>3} F{e['fracasos']:>3} tr{e['posibles_traducciones']:>2} | "
              f"EN v{i['videos']:>3} top{(i['top5_vistas'] or [0])[0]:>10,} 1M{i['videos_1M']:>3} G{i['ganadores']:>3} Gch{i['ganadores_canal_chico']:>3}")


if __name__ == "__main__":
    main()
