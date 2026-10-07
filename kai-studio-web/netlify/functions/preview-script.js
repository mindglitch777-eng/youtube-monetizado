// Convierte el guion en texto plano al script.json SIN escribir nada en
// GitHub — para que la página lo muestre antes de mandarlo de verdad.
const { parseGuion } = require("./_parse-guion");

exports.handler = async (event) => {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method not allowed" };
  }
  try {
    const { slug, voice, rate, texto } = JSON.parse(event.body);
    if (!slug || !/^[a-z0-9-]+$/.test(slug)) {
      return { statusCode: 400, body: JSON.stringify({ error: "Falta un slug válido (minúsculas, números, guiones)" }) };
    }
    const script = parseGuion({ slug, lang: "es", voice, rate, texto });
    return { statusCode: 200, body: JSON.stringify({ script }) };
  } catch (err) {
    return { statusCode: 400, body: JSON.stringify({ error: String(err.message || err) }) };
  }
};
