// Escribe episodes/<slug>/es/script.json (foco en español por ahora — ver
// RULES.md). Validamos que sea JSON parseable y tenga los campos mínimos
// antes de escribir, así un error de tipeo no rompe el pipeline en Actions.
const { putFile } = require("./_github");

function validar(script, idioma) {
  if (!script || typeof script !== "object") throw new Error(`El guion ${idioma} no es un JSON válido`);
  for (const campo of ["slug", "lang", "voice", "rate", "imagePrefix", "imageCount", "lines"]) {
    if (!(campo in script)) throw new Error(`Al guion ${idioma} le falta el campo "${campo}"`);
  }
  if (!Array.isArray(script.lines) || script.lines.length === 0) {
    throw new Error(`El guion ${idioma} no tiene líneas (lines)`);
  }
  for (const linea of script.lines) {
    if (typeof linea.id !== "number" || typeof linea.text !== "string" || !Array.isArray(linea.images)) {
      throw new Error(`Una línea del guion ${idioma} no tiene id/text/images válidos`);
    }
  }
}

exports.handler = async (event) => {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method not allowed" };
  }
  try {
    const { slug, scriptEs } = JSON.parse(event.body);
    if (!slug || !/^[a-z0-9-]+$/.test(slug)) {
      return { statusCode: 400, body: JSON.stringify({ error: "Falta un slug válido (minúsculas, números, guiones)" }) };
    }

    let es;
    try {
      es = JSON.parse(scriptEs);
      validar(es, "ES");
    } catch (err) {
      return { statusCode: 400, body: JSON.stringify({ error: `Guion inválido: ${err.message}` }) };
    }

    await putFile(
      `kai-studio/episodes/${slug}/es/script.json`,
      Buffer.from(JSON.stringify(es, null, 1), "utf-8").toString("base64"),
      `Kai studio web: guion ES de ${slug}`,
    );

    return { statusCode: 200, body: JSON.stringify({ ok: true }) };
  } catch (err) {
    return { statusCode: 500, body: JSON.stringify({ error: String(err.message || err) }) };
  }
};
