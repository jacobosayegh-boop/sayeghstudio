// Pruebas del blog propio. Uso: node tools/blog-notas/test_generar.mjs (sin dependencias)
import fs from "node:fs";
import path from "node:path";
import assert from "node:assert/strict";
import { validar, generar } from "./generar.mjs";

const raiz = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../..");
const leer = (p) => fs.readFileSync(path.join(raiz, p), "utf8");
const base = { id: "x", slug: "nota-prueba", title: "Título", excerpt: "Extracto", isoDate: "2026-11-16T00:00:00Z", image: "/a.webp", html: "<p>Texto</p>" };
let n = 0;
const caso = (nombre, fn) => { fn(); n++; console.log("ok", nombre); };

caso("acepta nota limpia", () => validar([base]));
caso("rechaza frase vetada", () => assert.throws(() => validar([{ ...base, html: "<p>Obra sin sorpresas</p>" }]), /vetada/));
caso("rechaza promesa en título", () => assert.throws(() => validar([{ ...base, title: "Remodela sin sobrecostos" }]), /vetada/));
caso("rechaza marcador de render", () => assert.throws(() => validar([{ ...base, html: "<p>[Insertar render 4K]</p>" }]), /vetada/));
caso("rechaza script", () => assert.throws(() => validar([{ ...base, html: "<p onclick=x>a</p>" }]), /no permitido/));
caso("rechaza slug repetido", () => assert.throws(() => validar([base, { ...base }]), /repetido/));

const antes = leer("blog/index.html");
generar();
caso("generar es idempotente", () => assert.equal(leer("blog/index.html"), antes));

const notas = JSON.parse(leer("data/blog-notas.json"));
caso("una página por nota con canonical, h1 y JSON-LD", () => {
  for (const x of notas) {
    const h = leer(`blog/notas/${x.slug}/index.html`);
    assert.ok(h.includes(`<link rel="canonical" href="https://sayeghstudio.com/blog/notas/${x.slug}/">`), x.slug);
    assert.ok(h.includes("<h1>") && h.includes('"@type": "BlogPosting"'), x.slug);
    assert.ok(fs.existsSync(path.join(raiz, x.image.slice(1))), "falta portada " + x.slug);
    JSON.parse(h.split('<script type="application/ld+json">')[1].split("</script>")[0]);
  }
});
caso("feed propio con la forma que lee la edge function", () => {
  const f = JSON.parse(leer("blog/notas/feed.json"));
  assert.equal(f.articles.length, notas.length);
  for (const a of f.articles) assert.ok(a.title && /^[a-z0-9-]+$/.test(a.slug) && /^https:\/\//.test(a.image) && !Number.isNaN(Date.parse(a.isoDate)));
});
caso("notas con difusion: piezas en el sitio y URL absolutas en el feed (las lee el pod)", () => {
  const f = JSON.parse(leer("blog/notas/feed.json"));
  for (const x of notas.filter((y) => y.difusion)) {
    const a = f.articles.find((y) => y.slug === x.slug);
    for (const k of ["og", "historia", "gbp_imagen"]) {
      assert.ok(fs.existsSync(path.join(raiz, x.difusion[k].slice(1))), `falta ${k} de ${x.slug}`);
      assert.match(a.difusion[k], /^https:\/\/sayeghstudio\.com\/assets\/images\/blog-notas\/redes\/.+\.jpg$/);
    }
    assert.ok(a.difusion.facebook.includes(`/blog/notas/${x.slug}/`) && a.difusion.gbp.length >= 120);
    assert.ok(!/https?:|@/.test(a.difusion.gbp), "GBP sin URL ni correo");
  }
});
caso("URL viejas de Soro redirigen", () => {
  const r = leer("_redirects");
  assert.match(r, /^\/blog\/\s+post=:slug\s+\/blog\/notas\/:slug\/\s+301!$/m);
  assert.match(r, /due-diligence-inmobiliario-sin-sobrecostos\/\s+\/blog\/notas\/due-diligence-inmobiliario\//);
});
caso("ya no queda Soro en el sitio", () => {
  for (const p of ["index.html", "blog/index.html", "netlify/edge-functions/recien-publicado.ts"]) assert.ok(!/trysoro|soro-blog|\?post=/.test(leer(p)), p);
});
caso("sitemap incluye todas las notas", () => {
  const s = leer("sitemap.xml");
  for (const x of notas) assert.ok(s.includes(`/blog/notas/${x.slug}/</loc>`), x.slug);
});
console.log(`${n} pruebas en verde`);
