// Sube UNA imagen a kai-studio/inbox/<slug>/<filename>. El frontend llama
// esto una vez por imagen (no todas juntas) porque Cloudflare Pages
// Functions rechaza pedidos de más de 100MB, pero el límite real útil
// sigue siendo el de la Contents API de GitHub (~ unos pocos MB cómodos
// en base64 antes de que convenga partir el archivo).
import { makeGithubClient } from "../_shared/github.js";
import { json } from "../_shared/json.js";

export async function onRequestPost({ request, env }) {
  try {
    const { slug, filename, dataBase64 } = await request.json();
    if (!slug || !filename || !dataBase64) {
      return json(400, { error: "Faltan slug, filename o dataBase64" });
    }
    if (!/^[a-z0-9-]+$/.test(slug)) {
      return json(400, { error: "El slug solo puede tener minúsculas, números y guiones" });
    }
    if (!/^[\w.-]+\.(png|jpg|jpeg)$/i.test(filename)) {
      return json(400, { error: "Nombre de archivo inválido" });
    }

    const { putFile } = makeGithubClient(env);
    await putFile(
      `kai-studio/inbox/${slug}/${filename}`,
      dataBase64,
      `Kai studio web: subir ${filename} (${slug})`,
    );
    return json(200, { ok: true });
  } catch (err) {
    return json(500, { error: String(err.message || err) });
  }
}
