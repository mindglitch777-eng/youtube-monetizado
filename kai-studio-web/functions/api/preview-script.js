// Convierte el guion en texto plano al script.json SIN escribir nada en
// GitHub — para que la página lo muestre antes de mandarlo de verdad.
import { parseGuion } from "../_shared/parse-guion.js";
import { json } from "../_shared/json.js";

export async function onRequestPost({ request }) {
  try {
    const { slug, voice, rate, texto } = await request.json();
    if (!slug || !/^[a-z0-9-]+$/.test(slug)) {
      return json(400, { error: "Falta un slug válido (minúsculas, números, guiones)" });
    }
    const script = parseGuion({ slug, lang: "es", voice, rate, texto });
    return json(200, { script });
  } catch (err) {
    return json(400, { error: String(err.message || err) });
  }
}
