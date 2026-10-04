// Devuelve el mismo estado que tools/status.py (imágenes/voz/video por
// episodio/idioma) más el último run del pipeline en GitHub Actions.
const { listDir, readFile, latestWorkflowRun } = require("./_github");

exports.handler = async (event) => {
  try {
    const slug = event.queryStringParameters?.slug;
    if (!slug) {
      return { statusCode: 400, body: JSON.stringify({ error: "Falta ?slug=" }) };
    }

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

    return {
      statusCode: 200,
      body: JSON.stringify({
        slug,
        idiomas: resultados,
        ultimaCorrida: run
          ? { estado: run.status, conclusion: run.conclusion, url: run.html_url, creado: run.created_at }
          : null,
      }),
    };
  } catch (err) {
    return { statusCode: 500, body: JSON.stringify({ error: String(err.message || err) }) };
  }
};
