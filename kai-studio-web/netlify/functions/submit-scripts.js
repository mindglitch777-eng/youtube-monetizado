// Convierte el guion en texto plano a script.json (conversión por reglas
// fijas, sin IA — ver _parse-guion.js) y lo escribe en
// episodes/<slug>/es/script.json. Foco en español por ahora (ver RULES.md).
const { putFile } = require("./_github");
const { parseGuion } = require("./_parse-guion");

exports.handler = async (event) => {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method not allowed" };
  }
  try {
    const { slug, voice, rate, prefix, texto } = JSON.parse(event.body);
    if (!slug || !/^[a-z0-9-]+$/.test(slug)) {
      return { statusCode: 400, body: JSON.stringify({ error: "Falta un slug válido (minúsculas, números, guiones)" }) };
    }

    let script;
    try {
      script = parseGuion({ slug, lang: "es", voice, rate, prefix, texto });
    } catch (err) {
      return { statusCode: 400, body: JSON.stringify({ error: `Guion inválido: ${err.message}` }) };
    }

    await putFile(
      `kai-studio/episodes/${slug}/es/script.json`,
      Buffer.from(JSON.stringify(script, null, 1), "utf-8").toString("base64"),
      `Kai studio web: guion ES de ${slug}`,
    );

    return { statusCode: 200, body: JSON.stringify({ ok: true, script }) };
  } catch (err) {
    return { statusCode: 500, body: JSON.stringify({ error: String(err.message || err) }) };
  }
};
