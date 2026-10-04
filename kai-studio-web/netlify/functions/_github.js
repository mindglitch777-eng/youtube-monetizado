// Helper compartido para hablar con la API de GitHub (Contents API + Actions
// API). Usa fetch nativo (Node 18+, que es lo que corre Netlify Functions).
// El token vive SOLO acá (variable de entorno del lado del servidor) — nunca
// se manda al navegador.

const OWNER = process.env.GITHUB_OWNER || "mindglitch777-eng";
const REPO = process.env.GITHUB_REPO || "youtube-monetizado";
const BRANCH = process.env.GITHUB_BRANCH || "claude/knot-youtube-automation-17ild6";
const TOKEN = process.env.GITHUB_TOKEN;

function requireToken() {
  if (!TOKEN) {
    throw new Error("Falta la variable de entorno GITHUB_TOKEN en la configuración de Netlify.");
  }
}

async function gh(path, opts = {}) {
  requireToken();
  const res = await fetch(`https://api.github.com${path}`, {
    ...opts,
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      ...(opts.body ? { "Content-Type": "application/json" } : {}),
      ...opts.headers,
    },
  });
  return res;
}

// Sube o actualiza UN archivo (Contents API). Si ya existe, lo actualiza
// (necesita su sha actual); si no, lo crea.
async function putFile(repoPath, contentBase64, message) {
  const getRes = await gh(`/repos/${OWNER}/${REPO}/contents/${encodeURI(repoPath)}?ref=${BRANCH}`);
  let sha;
  if (getRes.status === 200) {
    const data = await getRes.json();
    sha = data.sha;
  } else if (getRes.status !== 404) {
    throw new Error(`No pude leer ${repoPath}: ${getRes.status} ${await getRes.text()}`);
  }

  const putRes = await gh(`/repos/${OWNER}/${REPO}/contents/${encodeURI(repoPath)}`, {
    method: "PUT",
    body: JSON.stringify({
      message,
      content: contentBase64,
      branch: BRANCH,
      ...(sha ? { sha } : {}),
    }),
  });
  if (!putRes.ok) {
    throw new Error(`No pude escribir ${repoPath}: ${putRes.status} ${await putRes.text()}`);
  }
  return putRes.json();
}

// Lista los nombres de archivo dentro de una carpeta del repo (o [] si no existe).
async function listDir(repoPath) {
  const res = await gh(`/repos/${OWNER}/${REPO}/contents/${encodeURI(repoPath)}?ref=${BRANCH}`);
  if (res.status === 404) return [];
  if (!res.ok) throw new Error(`No pude listar ${repoPath}: ${res.status} ${await res.text()}`);
  const data = await res.json();
  return Array.isArray(data) ? data.map((f) => f.name) : [];
}

// Lee el contenido (texto) de un archivo, o null si no existe.
async function readFile(repoPath) {
  const res = await gh(`/repos/${OWNER}/${REPO}/contents/${encodeURI(repoPath)}?ref=${BRANCH}`);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`No pude leer ${repoPath}: ${res.status} ${await res.text()}`);
  const data = await res.json();
  return Buffer.from(data.content, "base64").toString("utf-8");
}

async function latestWorkflowRun(workflowFile) {
  const res = await gh(
    `/repos/${OWNER}/${REPO}/actions/workflows/${workflowFile}/runs?branch=${BRANCH}&per_page=1`,
  );
  if (!res.ok) throw new Error(`No pude leer el workflow: ${res.status} ${await res.text()}`);
  const data = await res.json();
  return data.workflow_runs?.[0] ?? null;
}

module.exports = { OWNER, REPO, BRANCH, putFile, listDir, readFile, latestWorkflowRun };
