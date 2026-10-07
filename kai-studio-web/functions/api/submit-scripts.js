// Convierte el guion en texto plano a script.json (conversión por reglas
// fijas, sin IA — ver _shared/parse-guion.js) y lo escribe en
// episodes/<slug>/es/script.json. Foco en español por ahora (ver RULES.md).
import { makeGithubClient, utf8ToBase64 } from "../_shared/github.js";
import { parseGuion } from "../_shared/parse-guion.js";
import { json } from "../_shared/json.js";

export async function onRequestPost({ request, env }) {
  try {
    const { slug, voice, rate, texto } = await request.json();
    if (!slug || !/^[a-z0-9-]+$/.test(slug)) {
      return json(400, { error: "Falta un slug válido (minúsculas, números, guiones)" });
    }

    let script;
    try {
      script = parseGuion({ slug, lang: "es", voice, rate, texto });
    } catch (err) {
      return json(400, { error: `Guion inválido: ${err.message}` });
    }

    const { putFile } = makeGithubClient(env);
    await putFile(
      `kai-studio/episodes/${slug}/es/script.json`,
      utf8ToBase64(JSON.stringify(script, null, 1)),
      `Kai studio web: guion ES de ${slug}`,
    );

    return json(200, { ok: true, script });
  } catch (err) {
    return json(500, { error: String(err.message || err) });
  }
}
