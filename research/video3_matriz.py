#!/usr/bin/env python3
"""
Matriz de viralidad del video 3: 16 ideas candidatas puntuadas de 1 a 5 en
9 criterios con peso. Las notas salen de la evidencia anotada en cada idea
(barrido de la API en data/video3-2026-10 y consultas de vidIQ del 26/10/2026).
Es una comparación relativa entre ideas, no una predicción de vistas.

  python3 research/video3_matriz.py  ->  data/video3-2026-10/matriz.json
"""
import json
from pathlib import Path

OUT = Path(__file__).parent / "data" / "video3-2026-10" / "matriz.json"

CRITERIOS = [  # (clave, nombre, peso)
    ("dem", "Demanda probada", 20),
    ("vel", "Velocidad en canales chicos", 15),
    ("hue", "Hueco en español", 15),
    ("bus", "Búsquedas", 10),
    ("gan", "Fuerza del gancho", 10),
    ("enc", "Encaje con Pijama", 10),
    ("mon", "Monetización", 10),
    ("sho", "Shorts", 5),
    ("ser", "Serie", 5),
]

IDEAS = [
    ("E", "Pijama sobrevive del día 1 al día 30 en una época (peste negra 1348)",
     dict(dem=5, vel=5, hue=5, bus=2, gan=5, enc=5, mon=4, sho=5, ser=5)),
    ("I", "Qué te pasaría DE VERDAD si viajaras al pasado",
     dict(dem=4, vel=5, hue=5, bus=3, gan=5, enc=5, mon=4, sho=4, ser=3)),
    ("R", "¿Contra qué especie humana ganarías una pelea?",
     dict(dem=5, vel=4, hue=5, bus=3, gan=5, enc=4, mon=4, sho=5, ser=4)),
    ("B", "¿Qué hacía REALMENTE la gente en la Edad Media todo el día?",
     dict(dem=5, vel=5, hue=3, bus=5, gan=4, enc=5, mon=4, sho=4, ser=5)),
    ("A", "¿Cuánto durarías en cada continente en la Edad de Hielo?",
     dict(dem=5, vel=4, hue=4, bus=5, gan=4, enc=4, mon=4, sho=4, ser=4)),
    ("D", "¿Cómo dormían en la Edad de Hielo sin morir congelados?",
     dict(dem=5, vel=5, hue=4, bus=4, gan=4, enc=4, mon=5, sho=3, ser=4)),
    ("L", "Pijama come un día entero en cada época: qué le pasa a su cuerpo",
     dict(dem=4, vel=4, hue=4, bus=5, gan=4, enc=5, mon=4, sho=5, ser=4)),
    ("C", "Los peores años para estar vivo (536, 1348, 1816…)",
     dict(dem=5, vel=4, hue=5, bus=3, gan=5, enc=3, mon=3, sho=5, ser=3)),
    ("G", "Los peores trabajos de la historia: ¿cuánto durarías en cada uno?",
     dict(dem=4, vel=3, hue=4, bus=3, gan=4, enc=5, mon=4, sho=5, ser=4)),
    ("K", "Una noche de −40 °C dentro de un castillo medieval",
     dict(dem=4, vel=4, hue=3, bus=3, gan=4, enc=4, mon=4, sho=3, ser=3)),
    ("J", "¿Qué hacían los humanos antiguos cuando llovía una semana?",
     dict(dem=4, vel=3, hue=2, bus=5, gan=3, enc=4, mon=4, sho=3, ser=4)),
    ("Q", "El iceberg de la historia oscura",
     dict(dem=4, vel=3, hue=3, bus=4, gan=4, enc=3, mon=3, sho=4, ser=3)),
    ("P", "¿Sobrevivirías? Historia interactiva: elige y te digo si mueres",
     dict(dem=3, vel=3, hue=5, bus=2, gan=4, enc=4, mon=3, sho=3, ser=4)),
    ("F", "Qué se siente cada castigo medieval",
     dict(dem=4, vel=4, hue=3, bus=4, gan=5, enc=3, mon=2, sho=4, ser=3)),
    ("H", "Historia aburrida para dormir: 2 horas con Pijama",
     dict(dem=4, vel=2, hue=3, bus=5, gan=1, enc=3, mon=5, sho=1, ser=5)),
    ("M", "Cada desastre que cambió la historia",
     dict(dem=3, vel=3, hue=3, bus=3, gan=3, enc=3, mon=4, sho=3, ser=3)),
]


def main():
    filas = []
    for k, titulo, n in IDEAS:
        total = sum(n[c] * p for c, _, p in CRITERIOS) / 5  # 0–100
        filas.append({"id": k, "idea": titulo, "notas": n, "puntaje": round(total, 1)})
    filas.sort(key=lambda f: -f["puntaje"])
    OUT.write_text(json.dumps({"criterios": CRITERIOS, "ideas": filas}, ensure_ascii=False, indent=1))
    for i, f in enumerate(filas, 1):
        print(f"{i:2}. {f['puntaje']:5.1f}  {f['id']}  {f['idea']}")


if __name__ == "__main__":
    main()
