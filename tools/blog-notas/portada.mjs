// Pide la imagen base de una portada al flujo «[v2] Bitácora · Portada» del pod (fal.ai flux/dev,
// respaldo Nano Banana Pro; tope 20 al mes). Costo aproximado: 0.03 USD por imagen.
// Uso: node tools/blog-notas/portada.mjs <slug> "<prompt en inglés: material o detalle, sin personas ni texto>" <salida.jpg>
// Requiere N8N_API_KEY en el entorno (la clave del webhook se lee del pod; nunca se imprime ni se guarda).
// Sale con código 2 si no hay imagen: entonces usa una foto real de assets/images/ o una portada vieja.
import fs from "node:fs";

const [slug, prompt, salida] = process.argv.slice(2);
if (!slug || !prompt || !salida) { console.error("Uso: portada.mjs <slug> <prompt> <salida.jpg>"); process.exit(1); }
const POD = "https://masterful-nightingale.pikapod.net";
const KEY = process.env.N8N_API_KEY;
if (!KEY) { console.error("Sin N8N_API_KEY: usa una foto real o una portada vieja."); process.exit(2); }

const h = { "X-N8N-API-KEY": KEY };
const lista = await (await fetch(`${POD}/api/v1/workflows?limit=250`, { headers: h })).json();
const wf = (lista.data || []).find((w) => w.name === "[v2] Bitácora · Portada" && w.active);
if (!wf) { console.error("El flujo de portada no está activo en el pod."); process.exit(2); }
const det = await (await fetch(`${POD}/api/v1/workflows/${wf.id}`, { headers: h })).json();
const cfg = det.nodes.find((n) => n.name === "Config").parameters.jsCode;
const clave = (cfg.match(/"CLAVE":"([0-9a-f]{20,})"/) || [])[1];
if (!clave) { console.error("El flujo no tiene clave configurada."); process.exit(2); }

const r = await fetch(`${POD}/webhook/bitacora-portada`, {
  method: "POST",
  headers: { "Content-Type": "application/json", "X-Bitacora-Clave": clave },
  body: JSON.stringify({ slug, prompt }),
  signal: AbortSignal.timeout(300000),
});
const j = await r.json().catch(() => ({}));
if (!j.ok) { console.error(`Sin portada (${r.status}): ${j.error || "respuesta vacía"}`); process.exit(2); }
let bytes;
if (j.url) bytes = Buffer.from(await (await fetch(j.url)).arrayBuffer());
else bytes = Buffer.from(j.b64, "base64");
fs.writeFileSync(salida, bytes);
console.log(`Portada lista (${j.fuente}, ${Math.round(bytes.length / 1024)} KB): ${salida}`);
