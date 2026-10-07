// Devuelve el estado (imágenes/voz/video por episodio/idioma) más el
// último run del pipeline en GitHub Actions.
import { makeGithubClient } from "../_shared/github.js";
import { json } from "../_shared/json.js";

export async function onRequestGet({ request, env }) {
  try {
    const url = new URL(request.url);
    const slug = url.searchParams.get("slug");
    if (!slug) {
      return json(400, { error: "Falta ?slug=" });
    }

    const { listDir, readFile, latestWorkflowRun } = makeGithubClient(env);

    const resultados = {};
    for (const lang of ["en", "es"]) {
      const scriptTxt = await readFile(`kai-studio/episodes/${slug}/${lang}/script.json`);
      if (!scriptTxt) {
        resultados[lang] = { existe: false };
        continue;
      }
      const script = JSON.parse(scriptTxt);
      const imagenes = await listDir(`kai-studio/public/episodes/${slug}/images`);
      const timing = await readFile(`kai-studio/public/episodes/${slug}/${lang}/timing.json`);
      const videoDir = await listDir("kai-studio/out");
      resultados[lang] = {
        existe: true,
        imagenesListas: imagenes.filter((n) => n.endsWith(".png")).length,
        imagenesEsperadas: script.imageCount,
        vozLista: !!timing,
        videoListo: videoDir.includes(`${slug}-${lang}.mp4`),
      };
    }

    const run = await latestWorkflowRun("kai-studio-pipeline.yml");

    return json(200, {
      slug,
      idiomas: resultados,
      ultimaCorrida: run
        ? { estado: run.status, conclusion: run.conclusion, url: run.html_url, creado: run.created_at }
        : null,
    });
  } catch (err) {
    return json(500, { error: String(err.message || err) });
  }
}
