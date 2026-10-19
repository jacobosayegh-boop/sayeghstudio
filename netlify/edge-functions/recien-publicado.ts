// "Recién publicado" siempre con la nota más nueva de la bitácora.
// Corre en "/" y "/blog/": reescribe lo que hay entre <!-- RECENT_ARTICLES_START --> y
// <!-- RECENT_ARTICLES_END --> con la última nota. Si la fuente falla, tarda o cambia de formato,
// se entrega el HTML estático ya desplegado (mismo marcado), sin error visible.

const EMBED = "https://app.trysoro.com/api/embed/cdb974da-4251-40d2-9ad6-3778e1063a87";
const FEED_ALT = "https://via.sayeghstudio.com/api/soro";
const START = "<!-- RECENT_ARTICLES_START -->";
const END = "<!-- RECENT_ARTICLES_END -->";
const TIMEOUT_MS = 1500;
const TTL_MS = 5 * 60 * 1000;
const TZ = "America/Mexico_City";

type Article = { title: string; slug: string; excerpt: string; isoDate: string; image?: string };

// Caché por isolate: evita pegarle a la fuente en cada visita y sirve de respaldo si falla.
let cached: { at: number; article: Article } | null = null;

const esc = (s = "") =>
  String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

const valid = (a: Article | undefined): a is Article =>
  !!a && typeof a.title === "string" && a.title.length > 0 &&
  /^[a-z0-9][a-z0-9-]*$/i.test(a.slug || "") && !Number.isNaN(Date.parse(a.isoDate));

// Extrae el arreglo JSON de "var SORO_ARTICLES = [ ... ];" contando corchetes (respeta cadenas).
function parseEmbed(js: string): Article[] {
  const m = js.match(/var\s+SORO_ARTICLES\s*=\s*\[/);
  if (!m || m.index === undefined) return [];
  const open = m.index + m[0].length - 1;
  let depth = 0, inStr = false, esc_ = false;
  for (let i = open; i < js.length; i++) {
    const c = js[i];
    if (inStr) {
      if (esc_) esc_ = false;
      else if (c === "\\") esc_ = true;
      else if (c === '"') inStr = false;
    } else if (c === '"') inStr = true;
    else if (c === "[") depth++;
    else if (c === "]" && --depth === 0) {
      try { return JSON.parse(js.slice(open, i + 1)); } catch { return []; }
    }
  }
  return [];
}

async function newest(): Promise<Article | null> {
  if (cached && Date.now() - cached.at < TTL_MS) return cached.article;
  const pick = (list: Article[]) =>
    list.filter(valid).sort((a, b) => Date.parse(b.isoDate) - Date.parse(a.isoDate))[0];
  try {
    const r = await fetch(EMBED, { signal: AbortSignal.timeout(TIMEOUT_MS) });
    if (r.ok) {
      const a = pick(parseEmbed(await r.text()));
      if (a) return (cached = { at: Date.now(), article: a }).article;
    }
  } catch { /* se intenta la fuente alterna */ }
  try {
    const r = await fetch(FEED_ALT, { signal: AbortSignal.timeout(TIMEOUT_MS) });
    if (r.ok) {
      const a = pick(((await r.json()) as { articles?: Article[] }).articles || []);
      if (a) return (cached = { at: Date.now(), article: a }).article;
    }
  } catch { /* sin fuente: respaldo */ }
  return cached ? cached.article : null;
}

function card(a: Article, heading: string): string {
  const date = new Intl.DateTimeFormat("es-MX", {
    day: "numeric", month: "long", year: "numeric", timeZone: TZ,
  }).format(new Date(a.isoDate));
  // La URL viene de un tercero y va dentro de url('...') en un atributo style: se codifican a mano
  // comillas, paréntesis, barra invertida, espacios y control (encodeURIComponent NO codifica ' ( ) ).
  const safeUrl = (u: string) =>
    u.replace(/['"()\\\s<>`\u0000-\u001f]/g, (c) => "%" + c.charCodeAt(0).toString(16).toUpperCase().padStart(2, "0"));
  const img = /^https:\/\/[^\s]+$/.test(a.image || "") && String(a.image).length < 2000
    ? `style="background: url('${esc(safeUrl(String(a.image)))}') center/cover no-repeat;"`
    : "";
  return `<a href="/blog/?post=${encodeURIComponent(a.slug)}" class="blog-featured-card" role="listitem">
            <div class="blog-card-image" ${img}></div>
            <div class="blog-card-body">
              <p class="blog-card-meta">Bitácora de obra · ${esc(date)}</p>
              <${heading} class="blog-card-title">${esc(a.title)}</${heading}>
              <p class="blog-card-excerpt">${esc(a.excerpt)}</p>
            </div>
          </a>`;
}

export default async (_request: Request, context: { next: () => Promise<Response> }) => {
  const response = await context.next();
  try {
    if (response.status !== 200 || !(response.headers.get("content-type") || "").includes("text/html")) {
      return response;
    }
    const article = await newest();
    if (!article) return response;

    const html = await response.text();
    const s = html.indexOf(START), e = html.indexOf(END);
    if (s === -1 || e === -1 || e < s) return new Response(html, response);

    // Conserva el nivel de encabezado que ya usa cada página (h3 en inicio, h2 en blog).
    const old = html.slice(s, e);
    const heading = (old.match(/<(h[2-4]) class="blog-card-title"/) || [])[1] || "h3";

    const headers = new Headers(response.headers);
    // El cuerpo cambia en cada visita: sin validadores, un 304 contra el ETag del HTML estático
    // dejaría al navegador mostrando una tarjeta vieja.
    headers.delete("content-length");
    headers.delete("etag");
    headers.delete("last-modified");
    return new Response(
      html.slice(0, s + START.length) + "\n          " + card(article, heading) + "\n          " + html.slice(e),
      { status: response.status, headers },
    );
  } catch {
    return response;
  }
};

export const config = { path: ["/", "/blog", "/blog/"] };
