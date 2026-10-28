#!/usr/bin/env python3
"""
Ronda 3, paso 3: puntaje final por idea.

  matriz de viralidad (10 puntos, 1 a 10)  OPINIÓN apoyada en los datos  -> 40 %
  demanda      MEDIDO: vistas del mejor video del tema (ES o EN)         -> 15 %
  competencia  MEDIDO: cuántos videos en español del tema (menos = mejor) -> 15 %
  prueba chica MEDIDO: ganadores en canales de menos de 20.000 subs       -> 15 %
  encaje con Pijama  OPINIÓN                                              -> 15 %

Escribe research/data/ideas-2026-10/puntajes.json y puntajes.csv
"""
import csv
import json
import math
from pathlib import Path

OUT = Path(__file__).parent / "data" / "ideas-2026-10"
CRIT = ["gancho", "alcance", "curiosidad", "identificacion", "emocion", "compartir", "rewatch", "visual", "serie", "largo"]

# idea: (10 notas de la matriz, encaje con Pijama, frase de justificación)
MATRIZ = {
    1: ([8, 6, 7, 6, 7, 6, 5, 9, 8, 8], 8, "Pijama descalzo a -30 °C es una imagen fuerte y graciosa; el tema ya rinde en canales chicos en español."),
    2: ([6, 5, 7, 5, 6, 5, 4, 7, 6, 7], 6, "Interesa, pero en YouTube rinde poco solo: el mejor video en español del tema exacto no pasa de 21.000 vistas."),
    3: ([8, 8, 8, 9, 6, 8, 5, 8, 8, 8], 9, "Compararse con un cazador ('¿y si vivías mejor sin trabajo?') genera miles de comentarios; Pijama con su lunes de oficina encaja perfecto."),
    4: ([9, 9, 8, 9, 7, 8, 7, 9, 9, 9], 10, "Es literalmente la premisa del canal: un tipo de hoy tirado en cada época. En inglés hay un video de 11,7 millones; en español casi nada."),
    5: ([8, 7, 7, 7, 7, 7, 5, 8, 7, 8], 8, "Funciona, pero hay mucha competencia en español y repetiría la plantilla de '7 formas de morir'."),
    6: ([7, 7, 7, 6, 6, 6, 5, 8, 8, 8], 7, "Egipto atrae; lo que mejor rinde no es 'cuánto durarías' sino 'cómo aguantaban 50 °C sin aire acondicionado'."),
    7: ([7, 7, 7, 7, 6, 6, 5, 8, 8, 8], 7, "Roma tiene demanda grande en inglés; en español los ganadores son canales medianos y el tema está muy tratado."),
    8: ([7, 6, 6, 5, 7, 6, 5, 8, 7, 7], 7, "Vikingos rinden en canales grandes; en español solo 1 ganador en canal chico."),
    9: ([8, 8, 8, 8, 6, 7, 5, 8, 7, 6], 9, "Gancho fuerte y muy Pijama, pero casi no hay videos medibles: no se puede saber si la gente lo busca."),
    10: ([7, 7, 7, 9, 5, 8, 5, 7, 7, 6], 8, "La versión que gana es 'qué hacían todo el día antes de que existiera el trabajo' (se junta con la idea 3)."),
    11: ([7, 7, 7, 7, 6, 7, 5, 8, 8, 7], 8, "Comida asquerosa del pasado + Pijama probándola = humor; 6 ganadores en canales chicos en español."),
    12: ([8, 8, 8, 8, 6, 8, 5, 8, 9, 8], 9, "Baño, higiene y dormir: 12 ganadores en canales chicos en español; asco + risa; da para serie."),
    13: ([8, 7, 7, 6, 8, 7, 5, 8, 6, 8], 7, "La peste rinde mucho, pero los ganadores son documentales de reconstrucción; 'cuánto durarías' casi no existe en español."),
    14: ([7, 6, 6, 5, 7, 6, 5, 8, 6, 7], 6, "Piratas: demanda en canales grandes; poca prueba en canales chicos."),
    15: ([8, 7, 7, 7, 7, 7, 5, 8, 7, 8], 7, "Azteca/Inca: 14 ganadores en canales chicos en español (público latino), pero los comentarios castigan errores históricos."),
    16: ([7, 6, 6, 5, 7, 6, 5, 8, 7, 7], 6, "Soldados antiguos: poca prueba en canales chicos y mucho contenido de guerra que no es de Pijama."),
    17: ([7, 7, 8, 6, 5, 7, 5, 7, 7, 7], 7, "El mito 'vivían 30 años' tiene un ganador de 383.000 vistas en canal de 7.000; buen video, poca serie."),
    18: ([6, 6, 7, 7, 6, 6, 4, 6, 5, 6], 6, "Poca demanda medida (máximo 63.000 vistas) y riesgo con anunciantes por el tema sexual."),
    19: ([7, 7, 7, 8, 6, 7, 5, 8, 8, 7], 7, "En inglés rinde mucho (2,9 millones) pero en canales grandes; en español solo 1 ganador chico."),
    20: ([8, 7, 8, 8, 7, 7, 6, 9, 8, 8], 10, "Es más una estructura (hora por hora) que un tema; los videos 'despertaste en la prehistoria' casi no tienen vistas."),
    21: ([9, 8, 8, 6, 8, 8, 6, 8, 9, 9], 8, "Idea nueva de los datos: 9,7 millones en inglés y 1,1 millones en español (536 d.C.) en canal de 5.900 subs."),
    22: ([8, 8, 8, 8, 6, 7, 5, 8, 10, 8], 9, "Idea nueva de los datos: 'cómo aguantaban X sin nada moderno' (calor, frío, mosquitos) gana una y otra vez en canales chicos."),
}
NOMBRE_EXTRA = {21: "Los peores años para estar vivo (idea nueva)", 22: "Cómo aguantaban calor, frío o bichos sin nada moderno (idea nueva)"}


def nota_demanda(top):
    return round(max(1, min(10, 2 * (math.log10(max(top, 10)) - 3) + 2)), 1)


def nota_competencia(n_es):
    return round(max(1, 10 - min(9, n_es / 15)), 1)


def nota_prueba(g_es, g_en):
    return round(min(10, 1 + g_es + 0.5 * g_en), 1)


def main():
    mercado = {m["idea"]: m for m in json.loads((OUT / "mercado_ideas.json").read_text())}
    filas = []
    for n, (notas, encaje, por_que) in MATRIZ.items():
        m = mercado[n]
        top = max((m["es"]["top5_vistas"] or [0])[0], (m["en"]["top5_vistas"] or [0])[0])
        d = nota_demanda(top)
        c = nota_competencia(m["es"]["videos"])
        p = nota_prueba(m["es"]["ganadores_canal_chico"], m["en"]["ganadores_canal_chico"])
        mat = sum(notas) / len(notas)
        final = round(0.40 * mat + 0.15 * d + 0.15 * c + 0.15 * p + 0.15 * encaje, 2)
        filas.append({"idea": n, "nombre": NOMBRE_EXTRA.get(n, m["nombre"]), **dict(zip(CRIT, notas)),
                      "matriz_promedio": round(mat, 1), "demanda": d, "competencia": c, "prueba_canal_chico": p,
                      "encaje_pijama": encaje, "final": final, "por_que": por_que,
                      "top_vistas": top, "videos_es": m["es"]["videos"], "canales_es": m["es"]["canales"],
                      "ganadores_chicos_es": m["es"]["ganadores_canal_chico"], "ganadores_chicos_en": m["en"]["ganadores_canal_chico"],
                      "posibles_traducciones_es": m["es"]["posibles_traducciones"]})
    filas.sort(key=lambda f: -f["final"])
    for k, f in enumerate(filas):
        f["puesto"] = k + 1
        f["veredicto"] = "hacer" if f["final"] >= 7.5 else "probar" if f["final"] >= 6.8 else "descartar"
    (OUT / "puntajes.json").write_text(json.dumps(filas, ensure_ascii=False, indent=1))
    with (OUT / "puntajes.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    for f in filas:
        print(f"{f['puesto']:>2} #{f['idea']:>2} {f['final']:5} {f['veredicto']:9} mat{f['matriz_promedio']} d{f['demanda']} "
              f"c{f['competencia']} p{f['prueba_canal_chico']} e{f['encaje_pijama']}  {f['nombre'][:50]}")


if __name__ == "__main__":
    main()
