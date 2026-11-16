// Agrega una nota nueva a la bitácora y regenera el sitio.
// Uso: node tools/blog-notas/nueva_nota.mjs <nota.json>
// nota.json = { "tema": "...", "slug": "...", "title": "...", "excerpt": "...", "html": "<p>...</p>" }
import fs from "node:fs";
import path from "node:path";
import { validar, generar } from "./generar.mjs";

const RAIZ = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../..");
const archivo = process.argv[2];
if (!archivo) { console.error("Falta el archivo de la nota"); process.exit(1); }
const n = JSON.parse(fs.readFileSync(archivo, "utf8"));
const datos = path.join(RAIZ, "data/blog-notas.json");
const notas = JSON.parse(fs.readFileSync(datos, "utf8"));
if (notas.some((x) => x.slug === n.slug)) { console.error(`Ya existe ${n.slug}`); process.exit(1); }

const palabras = n.html.replace(/<[^>]+>/g, " ").split(/\s+/).filter(Boolean).length;
if (palabras < 900 || palabras > 2200) { console.error(`Largo fuera de rango: ${palabras} palabras (900-2200)`); process.exit(1); }
if ((n.html.match(/<h2>/g) || []).length < 4) { console.error("Faltan subtítulos h2 (mínimo 4)"); process.exit(1); }
if (n.title.length > 70 || n.excerpt.length > 160) { console.error("Título > 70 o extracto > 160 caracteres"); process.exit(1); }
if (!/href="(https:\/\/via\.sayeghstudio\.com|\/blog\/)/.test(n.html)) { console.error("Falta al menos un enlace interno (/blog/... o via.sayeghstudio.com)"); process.exit(1); }

const nueva = {
  id: `propia-${new Date().toISOString().slice(0, 10)}-${n.slug}`,
  slug: n.slug,
  slugs_previos: [],
  title: n.title,
  excerpt: n.excerpt,
  isoDate: new Date().toISOString(),
  image: n.image || "",
  origen: "claude",
  tema: n.tema || "",
  html: n.html.trim(),
};
if (!nueva.image) {
  // Sin imagen nueva: se reusa la portada más antigua que no se haya usado en las últimas 10 notas.
  const recientes = new Set(notas.slice(0, 10).map((x) => x.image));
  nueva.image = [...notas].reverse().map((x) => x.image).find((im) => !recientes.has(im)) || notas[0].image;
}
validar([nueva, ...notas]);
notas.unshift(nueva);
fs.writeFileSync(datos, JSON.stringify(notas, null, 1));

const temasP = path.join(RAIZ, "data/blog-notas-temas.json");
if (n.tema && fs.existsSync(temasP)) {
  const temas = JSON.parse(fs.readFileSync(temasP, "utf8"));
  const t = temas.find((x) => x.tema === n.tema);
  if (t) { t.estado = "publicado"; t.slug = n.slug; t.fecha = nueva.isoDate.slice(0, 10); }
  fs.writeFileSync(temasP, JSON.stringify(temas, null, 1));
}
console.log(`Nota agregada: ${n.slug} (${palabras} palabras). ${generar()} notas generadas.`);
