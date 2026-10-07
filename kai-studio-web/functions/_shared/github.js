// Helper compartido para hablar con la API de GitHub (Contents API + Actions
// API). Corre en el runtime de Cloudflare Workers — solo Web APIs nativas
// (fetch, atob/btoa, TextEncoder/TextDecoder), sin nada de Node. El token
// vive SOLO en las variables de entorno del lado del servidor — nunca se
// manda al navegador.

export function makeGithubClient(env) {
  const OWNER = env.GITHUB_OWNER || "mindglitch777-eng";
  const REPO = env.GITHUB_REPO || "youtube-monetizado";
  const BRANCH = env.GITHUB_BRANCH || "claude/knot-youtube-automation-17ild6";
  const TOKEN = env.GITHUB_TOKEN;

  function requireToken() {
    if (!TOKEN) {
      throw new Error("Falta la variable de entorno GITHUB_TOKEN en la configuración de Cloudflare Pages.");
    }
  }

  async function gh(path, opts = {}) {
    requireToken();
    return fetch(`https://api.github.com${path}`, {
      ...opts,
      headers: {
        Authorization: `Bearer ${TOKEN}`,
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "kai-studio-web",
        ...(opts.body ? { "Content-Type": "application/json" } : {}),
        ...opts.headers,
      },
    });
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
    return base64ToUtf8(data.content);
  }

  async function latestWorkflowRun(workflowFile) {
    const res = await gh(
      `/repos/${OWNER}/${REPO}/actions/workflows/${workflowFile}/runs?branch=${BRANCH}&per_page=1`,
    );
    if (!res.ok) throw new Error(`No pude leer el workflow: ${res.status} ${await res.text()}`);
    const data = await res.json();
    return data.workflow_runs?.[0] ?? null;
  }

  return { OWNER, REPO, BRANCH, putFile, listDir, readFile, latestWorkflowRun };
}

// GitHub's Contents API devuelve base64 con saltos de línea cada 60 chars,
// y puede contener texto UTF-8 multibyte (acentos, ñ) — atob() sola los
// rompe, hay que pasar por TextDecoder.
function base64ToUtf8(b64) {
  const binary = atob(b64.replace(/\n/g, ""));
  const bytes = Uint8Array.from(binary, (c) => c.charCodeAt(0));
  return new TextDecoder("utf-8").decode(bytes);
}

export function utf8ToBase64(str) {
  const bytes = new TextEncoder().encode(str);
  let binary = "";
  bytes.forEach((b) => { binary += String.fromCharCode(b); });
  return btoa(binary);
}
