// Agrega una nota nueva a la bitácora y regenera el sitio.
// Uso: node tools/blog-notas/nueva_nota.mjs <nota.json>
// nota.json = { "tema": "...", "slug": "...", "title": "...", "excerpt": "...", "html": "<p>...</p>",
//               "difusion": { "facebook": "...", "gbp": "..." } }
// Antes: python3 tools/blog-notas/redes.py <slug> <imagen_base> "<título>" (portada y piezas para redes).
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

// Difusión (desde 17-11-2026): textos para Facebook y Google Business y piezas para redes ya generadas.
const d = n.difusion || {};
const LEX = /(?<!\p{L})(lujos[oa]s?|lujo|bonit[oa]s?|barat[oa]s?|econ[oó]mic[oa]s?|decorar|decoraci[oó]n|dise[nñ]o gratis|presupuestos? r[aá]pidos?|garantizad[oa]s?|garant[ií]a|entrega a tiempo|IA|render|generad[oa] con)(?!\p{L})/u;
for (const [k, max] of [["facebook", 1200], ["gbp", 1400]]) {
  const t = String(d[k] || "").trim();
  if (t.length < 120 || t.length > max) { console.error(`difusion.${k}: largo ${t.length} fuera de 120-${max}`); process.exit(1); }
  const m = t.match(LEX); if (m) { console.error(`difusion.${k}: palabra vetada «${m[0]}»`); process.exit(1); }
  if (/[*#_`]|^\s*[-•]/m.test(t)) { console.error(`difusion.${k}: sin markdown, viñetas ni hashtags`); process.exit(1); }
}
if (/https?:\/\/|www\.|@|\d[\d\s().-]{8,}\d/.test(d.gbp)) { console.error("difusion.gbp: Google rechaza URL, correo o teléfono en el texto (el botón lleva el enlace)"); process.exit(1); }
if (!/sayeghstudio\.com\/blog\/notas\//.test(d.facebook)) { console.error("difusion.facebook: falta el enlace a la nota"); process.exit(1); }
const RED = (suf) => `/assets/images/blog-notas/redes/${n.slug}-${suf}.jpg`;
for (const suf of ["og", "historia", "gbp"]) {
  if (!fs.existsSync(path.join(RAIZ, RED(suf).slice(1)))) { console.error(`Falta ${RED(suf)}: corre antes tools/blog-notas/redes.py`); process.exit(1); }
}
if (!n.image && fs.existsSync(path.join(RAIZ, `assets/images/blog-notas/${n.slug}.webp`))) n.image = `/assets/images/blog-notas/${n.slug}.webp`;

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
  base_imagen: n.base_imagen || "",
  html: n.html.trim(),
  difusion: { facebook: d.facebook.trim(), gbp: d.gbp.trim(), og: RED("og"), historia: RED("historia"), gbp_imagen: RED("gbp") },
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
