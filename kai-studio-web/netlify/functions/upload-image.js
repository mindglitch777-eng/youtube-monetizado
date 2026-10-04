// Sube UNA imagen a kai-studio/inbox/<slug>/<filename>. El frontend llama
// esto una vez por imagen (no todas juntas) porque Netlify Functions
// rechaza pedidos de más de ~6MB.
const { putFile } = require("./_github");

exports.handler = async (event) => {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method not allowed" };
  }
  try {
    const { slug, filename, dataBase64 } = JSON.parse(event.body);
    if (!slug || !filename || !dataBase64) {
      return { statusCode: 400, body: JSON.stringify({ error: "Faltan slug, filename o dataBase64" }) };
    }
    if (!/^[a-z0-9-]+$/.test(slug)) {
      return { statusCode: 400, body: JSON.stringify({ error: "El slug solo puede tener minúsculas, números y guiones" }) };
    }
    if (!/^[\w.-]+\.(png|jpg|jpeg)$/i.test(filename)) {
      return { statusCode: 400, body: JSON.stringify({ error: "Nombre de archivo inválido" }) };
    }

    await putFile(
      `kai-studio/inbox/${slug}/${filename}`,
      dataBase64,
      `Kai studio web: subir ${filename} (${slug})`,
    );
    return { statusCode: 200, body: JSON.stringify({ ok: true }) };
  } catch (err) {
    return { statusCode: 500, body: JSON.stringify({ error: String(err.message || err) }) };
  }
};
