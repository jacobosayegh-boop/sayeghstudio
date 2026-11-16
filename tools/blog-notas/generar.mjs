// Blog propio de Sayegh Studio (reemplaza el embed de Soro desde 16-11-2026).
// Fuente única: data/blog-notas.json. Genera páginas estáticas, índice, feed JSON,
// tarjetas del blog, «Recién publicado», sitemap y redirecciones de las URL viejas (?post=slug).
// Sin dependencias: node tools/blog-notas/generar.mjs
import fs from "node:fs";
import path from "node:path";

const RAIZ = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../..");
const SITIO = "https://sayeghstudio.com";
const TZ = "America/Mexico_City";
const leer = (p) => fs.readFileSync(path.join(RAIZ, p), "utf8");
const escribir = (p, s) => {
  fs.mkdirSync(path.dirname(path.join(RAIZ, p)), { recursive: true });
  fs.writeFileSync(path.join(RAIZ, p), s);
};
const esc = (s = "") => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const fecha = (iso) => new Intl.DateTimeFormat("es-MX", { day: "numeric", month: "long", year: "numeric", timeZone: TZ }).format(new Date(iso));
const SLUG = /^[a-z0-9][a-z0-9-]*$/;
const VETO = /sin sobrecostos|cero sobrecostos|0\s?% de sobrecostos|sin sorpresas|plusvalía garantizada|garantizamos|inquebrantable|\[Insertar/i;

export function validar(notas) {
  const vistos = new Set();
  for (const n of notas) {
    if (!SLUG.test(n.slug)) throw new Error(`slug inválido: ${n.slug}`);
    if (vistos.has(n.slug)) throw new Error(`slug repetido: ${n.slug}`);
    vistos.add(n.slug);
    if (!n.title || !n.excerpt || !n.html || Number.isNaN(Date.parse(n.isoDate))) throw new Error(`nota incompleta: ${n.slug}`);
    for (const c of [n.title, n.excerpt, n.html]) {
      const m = c.match(VETO);
      if (m) throw new Error(`frase vetada en ${n.slug}: ${m[0]}`);
    }
    if (/<script|on\w+=|javascript:/i.test(n.html)) throw new Error(`HTML no permitido en ${n.slug}`);
  }
}

function reemplazarEntre(texto, ini, fin, nuevo, archivo) {
  const s = texto.indexOf(ini), e = texto.indexOf(fin);
  if (s === -1 || e === -1 || e < s) throw new Error(`faltan marcadores ${ini} en ${archivo}`);
  return texto.slice(0, s + ini.length) + nuevo + texto.slice(e);
}

const tarjeta = (n, h = "h3", meta = "Bitácora de obra") => `<a href="/blog/notas/${n.slug}/" class="blog-featured-card" role="listitem">
            <div class="blog-card-image" style="background: url('${n.image}') center/cover no-repeat;"></div>
            <div class="blog-card-body">
              <p class="blog-card-meta">${meta} · ${esc(fecha(n.isoDate))}</p>
              <${h} class="blog-card-title">${esc(n.title)}</${h}>
              <p class="blog-card-excerpt">${esc(n.excerpt)}</p>
            </div>
          </a>`;

function partesPlantilla() {
  const t = leer("blog/materiales/concreto-aparente-lujo/index.html");
  const ga = t.slice(t.indexOf("<!-- Google Analytics"), t.indexOf("</head>"));
  const cabecera = t.slice(t.indexOf("<body"), t.indexOf("<main>"));
  const pie = t.slice(t.indexOf("</main>") + "</main>".length);
  if (!ga || !cabecera || !pie) throw new Error("plantilla base cambió");
  return { ga, cabecera, pie };
}

function head({ titulo, descripcion, url, imagen, ldjson, ga, tipo = "article" }) {
  return `<!DOCTYPE html>
<html lang="es" dir="ltr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${esc(titulo)} | Sayegh Studio</title>
  <meta name="description" content="${esc(descripcion)}">
  <meta name="author" content="Sayegh Studio">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="${url}">
  <link rel="alternate" type="application/rss+xml" title="Sayegh Studio" href="${SITIO}/feed.xml">
  <meta property="og:type" content="${tipo}">
  <meta property="og:site_name" content="Sayegh Studio">
  <meta property="og:locale" content="es_MX">
  <meta property="og:title" content="${esc(titulo)}">
  <meta property="og:description" content="${esc(descripcion)}">
  <meta property="og:url" content="${url}">
  <meta property="og:image" content="${SITIO}${imagen}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="preload" href="/fonts/archivo-400.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/fonts/spacegrotesk-500.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/css/main.css">
  <link rel="stylesheet" href="/css/subpages.css">
  <link rel="icon" href="/sayegh-logo-ink.png" type="image/png">
  <script type="application/ld+json">
${JSON.stringify(ldjson, null, 2).replace(/</g, "\\u003c")}
  </script>
${ga}</head>
`;
}

function paginaNota(n, i, notas, p) {
  const url = `${SITIO}/blog/notas/${n.slug}/`;
  const ld = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "BlogPosting",
        "@id": `${url}#article`,
        headline: n.title,
        description: n.excerpt,
        image: `${SITIO}${n.image}`,
        datePublished: n.isoDate,
        dateModified: n.dateModified || n.isoDate,
        inLanguage: "es-MX",
        mainEntityOfPage: url,
        author: { "@type": "Organization", "@id": `${SITIO}/#organization`, name: "Sayegh Studio" },
        publisher: { "@type": "Organization", "@id": `${SITIO}/#organization`, name: "Sayegh Studio", logo: { "@type": "ImageObject", url: `${SITIO}/sayegh-logo-ink.png` } },
        articleSection: "Bitácora de obra",
      },
      {
        "@type": "BreadcrumbList",
        "@id": `${url}#breadcrumb`,
        itemListElement: [
          { "@type": "ListItem", position: 1, name: "Inicio", item: `${SITIO}/` },
          { "@type": "ListItem", position: 2, name: "Blog", item: `${SITIO}/blog/` },
          { "@type": "ListItem", position: 3, name: "Bitácora de obra", item: `${SITIO}/blog/notas/` },
          { "@type": "ListItem", position: 4, name: n.title, item: url },
        ],
      },
    ],
  };
  const relacionadas = [1, 2, 3].map((k) => notas[(i + k) % notas.length]).filter((r) => r.slug !== n.slug);
  return head({ titulo: n.title, descripcion: n.excerpt, url, imagen: n.image, ldjson: ld, ga: p.ga }) + p.cabecera + `<main>
  <div class="blog-wrapper">
    <article class="blog-article">
      <h1>${esc(n.title)}</h1>
      <p class="article-meta">Por Sayegh Studio · ${esc(fecha(n.isoDate))}</p>
      <img src="${n.image}" alt="${esc(n.title)} — Sayegh Studio" width="1440" height="960" loading="eager">

      <section class="article-content">
${n.html}

        <div class="article-cta">
          <a href="https://via.sayeghstudio.com" class="btn btn-primary" data-event="cta_click" data-event-label="Auditoría (bitácora)">Inicia tu Auditoría de Viabilidad</a>
        </div>
      </section>

      <ul class="article-related">
${relacionadas.map((r) => `        <li><a href="/blog/notas/${r.slug}/">${esc(r.title)}</a></li>`).join("\n")}
        <li><a href="/blog/notas/">Toda la bitácora de obra</a></li>
      </ul>
    </article>
  </div>

  </main>` + p.pie;
}

function indice(notas, p) {
  const url = `${SITIO}/blog/notas/`;
  const ld = {
    "@context": "https://schema.org",
    "@type": "Blog",
    "@id": `${url}#blog`,
    name: "Bitácora de obra | Sayegh Studio",
    url,
    inLanguage: "es-MX",
    blogPost: notas.map((n) => ({ "@type": "BlogPosting", headline: n.title, url: `${SITIO}/blog/notas/${n.slug}/`, datePublished: n.isoDate })),
  };
  return head({ titulo: "Bitácora de obra", descripcion: "Notas técnicas de Sayegh Studio sobre precios unitarios, dirección de obra, materiales y viabilidad para remodelar o construir en México.", url, imagen: notas[0].image, ldjson: ld, ga: p.ga, tipo: "website" }) + p.cabecera + `<main>
  <div class="blog-wrapper">
    <p class="section-tag">Blog</p>
    <h1>Bitácora de obra</h1>
    <p>${notas.length} notas sobre precios unitarios, dirección de obra, materiales y viabilidad, de la más reciente a la más antigua.</p>
    <div class="blog-grid" role="list">
          ${notas.map((n) => tarjeta(n, "h2")).join("\n          ")}
    </div>
  </div>
  </main>` + p.pie;
}

export function generar() {
  const notas = JSON.parse(leer("data/blog-notas.json")).sort((a, b) => Date.parse(b.isoDate) - Date.parse(a.isoDate));
  validar(notas);
  const p = partesPlantilla();
  notas.forEach((n, i) => escribir(`blog/notas/${n.slug}/index.html`, paginaNota(n, i, notas, p)));
  escribir("blog/notas/index.html", indice(notas, p));
  escribir("blog/notas/feed.json", JSON.stringify({
    articles: notas.map((n) => ({ id: n.id, title: n.title, slug: n.slug, excerpt: n.excerpt, date: fecha(n.isoDate), isoDate: n.isoDate, image: `${SITIO}${n.image}`, url: `${SITIO}/blog/notas/${n.slug}/` })),
  }, null, 1));

  // Blog: «Recién publicado» estático (la edge function lo refresca) y las 12 notas más nuevas.
  let blog = leer("blog/index.html");
  blog = reemplazarEntre(blog, "<!-- RECENT_ARTICLES_START -->", "<!-- RECENT_ARTICLES_END -->", "\n        " + tarjeta(notas[0], "h2") + "\n        ", "blog/index.html");
  blog = reemplazarEntre(blog, "<!-- NOTAS_START -->", "<!-- NOTAS_END -->", `
      <div class="blog-grid" role="list">
          ${notas.slice(0, 12).map((n) => tarjeta(n, "h3")).join("\n          ")}
      </div>
      <p style="margin-top: 32px;"><a href="/blog/notas/" class="btn btn-ghost">Ver las ${notas.length} notas de la bitácora</a></p>
      `, "blog/index.html");
  escribir("blog/index.html", blog);

  let home = leer("index.html");
  home = reemplazarEntre(home, "<!-- RECENT_ARTICLES_START -->", "<!-- RECENT_ARTICLES_END -->", "\n          " + tarjeta(notas[0], "h3") + "\n          ", "index.html");
  home = reemplazarEntre(home, "<!-- NOTAS_START -->", "<!-- NOTAS_END -->", `
        <div class="blog-grid" role="list">
          ${notas.slice(0, 6).map((n) => tarjeta(n, "h3")).join("\n          ")}
        </div>
        <p style="margin-top: 32px;"><a href="/blog/notas/" class="btn btn-ghost">Ver las ${notas.length} notas de la bitácora</a></p>
        `, "index.html");
  escribir("index.html", home);

  // Sitemap.
  const urls = [{ loc: `${SITIO}/blog/notas/`, mod: notas[0].isoDate }, ...notas.map((n) => ({ loc: `${SITIO}/blog/notas/${n.slug}/`, mod: n.dateModified || n.isoDate }))];
  let mapa = leer("sitemap.xml");
  mapa = reemplazarEntre(mapa, "<!-- NOTAS_START -->", "<!-- NOTAS_END -->", "\n" + urls.map((u) => `  <url>
    <loc>${u.loc}</loc>
    <lastmod>${u.mod.slice(0, 10)}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>`).join("\n") + "\n  ", "sitemap.xml");
  escribir("sitemap.xml", mapa);

  // Redirecciones: URL viejas de Soro (/blog/?post=slug) y slugs renombrados.
  const renombres = notas.flatMap((n) => (n.slugs_previos || []).filter((s) => s !== n.slug && SLUG.test(s)).map((s) => [s, n.slug]));
  let red = leer("_redirects");
  red = reemplazarEntre(red, "# NOTAS_START", "# NOTAS_END", `
# Generado por tools/blog-notas/generar.mjs: no editar a mano.
${renombres.map(([a, b]) => `/blog/notas/${a}/   /blog/notas/${b}/   301!\n/blog/notas/${a}    /blog/notas/${b}/   301!`).join("\n")}
/blog/   post=:slug   /blog/notas/:slug/   301!
/blog    post=:slug   /blog/notas/:slug/   301!
`, "_redirects");
  escribir("_redirects", red);
  return notas.length;
}

if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(new URL(import.meta.url).pathname)) {
  console.log(`${generar()} notas generadas`);
}
