// Pruebas del bloque "ATRIBUCIÓN HACIA LA AUDITORÍA" de js/main.js.
// Uso: node tools/test_atribucion.mjs  (sin dependencias)
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const raiz = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const src = fs.readFileSync(path.join(raiz, 'js/main.js'), 'utf8');
const ini = src.indexOf('── ATRIBUCIÓN HACIA LA AUDITORÍA ──');
const fin = src.lastIndexOf('/*', src.indexOf('── FIN ATRIBUCIÓN HACIA LA AUDITORÍA ──'));
assert.ok(ini > 0 && fin > ini, 'no se encontró el bloque de atribución');
const bloque = src.slice(src.lastIndexOf('/*', ini), fin);

// Escenario: ejecuta el bloque con DOM/almacenamiento simulados.
function escenario({ url, referrer = '', hrefs = [], storage = {}, storageFalla = false }) {
  const u = new URL(url);
  const links = hrefs.map((h) => {
    const a = { _h: h, getAttribute() { return this._h; }, setAttribute(_, v) { this._h = v; } };
    a.closest = () => a;
    return a;
  });
  const almacen = { ...storage };
  const sessionStorage = {
    getItem(k) { if (storageFalla) throw new Error('bloqueado'); return k in almacen ? almacen[k] : null; },
    setItem(k, v) { if (storageFalla) throw new Error('bloqueado'); almacen[k] = String(v); },
  };
  const oyentes = {};
  const document = {
    referrer, readyState: 'complete',
    querySelectorAll: () => links,
    addEventListener(ev, fn, cap) { (oyentes[ev] ||= []).push({ fn, cap }); },
  };
  const location = { href: u.href, search: u.search, pathname: u.pathname, hostname: u.hostname, origin: u.origin };
  vm.runInNewContext(bloque, { URL, URLSearchParams, document, location, sessionStorage });
  const lanzar = (ev, a) => (oyentes[ev] || []).forEach((o) => o.fn({ target: a }));
  return { links, almacen, oyentes, lanzar, hrefs: () => links.map((l) => l._h) };
}
const params = (h) => new URL(h, 'https://sayeghstudio.com').searchParams;

let ok = 0;
const prueba = (n, f) => { f(); ok++; console.log('ok  - ' + n); };

prueba('aterrizaje con UTM de Pinterest decora enlace a via', () => {
  const e = escenario({ url: 'https://sayeghstudio.com/blog/x/?utm_source=pinterest&utm_medium=pin&utm_campaign=c1&utm_content=pin9', hrefs: ['https://via.sayeghstudio.com'] });
  const p = params(e.hrefs()[0]);
  assert.equal(p.get('utm_source'), 'pinterest');
  assert.equal(p.get('utm_medium'), 'pin');
  assert.equal(p.get('utm_campaign'), 'c1');
  assert.equal(p.get('utm_content'), 'pin9');
  assert.ok(e.almacen.sayegh_utm);
});

prueba('referrer pin.it como respaldo', () => {
  const e = escenario({ url: 'https://sayeghstudio.com/zonas/polanco/', referrer: 'https://pin.it/abc', hrefs: ['https://via.sayeghstudio.com/'] });
  const p = params(e.hrefs()[0]);
  assert.equal(p.get('utm_source'), 'pinterest');
  assert.equal(p.get('utm_medium'), 'organic_pin');
  assert.equal(p.get('utm_campaign'), 'conversion_auditoria');
  assert.equal(p.get('utm_content'), 'ref-zonas_polanco');
});

prueba('referrer mx.pinterest.com y pinterest.com.mx', () => {
  for (const r of ['https://mx.pinterest.com/pin/1', 'https://www.pinterest.com.mx/']) {
    const e = escenario({ url: 'https://sayeghstudio.com/', referrer: r, hrefs: ['https://via.sayeghstudio.com'] });
    assert.equal(params(e.hrefs()[0]).get('utm_source'), 'pinterest');
    assert.equal(params(e.hrefs()[0]).get('utm_content'), 'ref-inicio');
  }
});

prueba('referrer Google = organic/seo', () => {
  const e = escenario({ url: 'https://sayeghstudio.com/blog/', referrer: 'https://www.google.com.mx/', hrefs: ['https://via.sayeghstudio.com'] });
  const p = params(e.hrefs()[0]);
  assert.equal(p.get('utm_source'), 'google');
  assert.equal(p.get('utm_medium'), 'organic');
  assert.equal(p.get('utm_campaign'), 'seo');
});

prueba('referrer red social y otro dominio', () => {
  let e = escenario({ url: 'https://sayeghstudio.com/', referrer: 'https://l.facebook.com/l.php', hrefs: ['https://via.sayeghstudio.com'] });
  assert.equal(params(e.hrefs()[0]).get('utm_source'), 'facebook');
  assert.equal(params(e.hrefs()[0]).get('utm_medium'), 'social');
  e = escenario({ url: 'https://sayeghstudio.com/', referrer: 'https://www.ejemplo-blog.mx/nota', hrefs: ['https://via.sayeghstudio.com'] });
  assert.equal(params(e.hrefs()[0]).get('utm_source'), 'ejemplo-blog.mx');
  assert.equal(params(e.hrefs()[0]).get('utm_medium'), 'referral');
});

prueba('referrer interno conserva lo guardado', () => {
  const guardado = JSON.stringify({ utm_source: 'pinterest', utm_medium: 'organic_pin', utm_campaign: 'conversion_auditoria', utm_content: 'ref-inicio' });
  const e = escenario({ url: 'https://sayeghstudio.com/blog/', referrer: 'https://sayeghstudio.com/', storage: { sayegh_utm: guardado }, hrefs: ['https://via.sayeghstudio.com'] });
  assert.equal(params(e.hrefs()[0]).get('utm_source'), 'pinterest');
  assert.equal(e.almacen.sayegh_utm, guardado);
});

prueba('referrer interno sin nada guardado: etiqueta de sitio', () => {
  const e = escenario({ url: 'https://sayeghstudio.com/blog/', referrer: 'https://www.sayeghstudio.com/', hrefs: ['https://via.sayeghstudio.com'] });
  const p = params(e.hrefs()[0]);
  assert.equal(p.get('utm_source'), 'sayeghstudio');
  assert.equal(p.get('utm_medium'), 'sitio');
  assert.equal(p.get('utm_campaign'), 'cta');
  assert.equal(p.get('utm_content'), 'blog');
  assert.equal(e.almacen.sayegh_utm, undefined);
});

prueba('un UTM nuevo sobrescribe lo guardado', () => {
  const e = escenario({ url: 'https://sayeghstudio.com/?utm_source=ig', storage: { sayegh_utm: '{"utm_source":"pinterest"}' }, hrefs: ['https://via.sayeghstudio.com'] });
  assert.equal(JSON.parse(e.almacen.sayegh_utm).utm_source, 'ig');
});

prueba('utm_campaign propio del enlace se respeta', () => {
  const e = escenario({ url: 'https://sayeghstudio.com/?utm_source=pinterest&utm_campaign=otra', hrefs: ['https://via.sayeghstudio.com/?utm_campaign=propia'] });
  const p = params(e.hrefs()[0]);
  assert.equal(p.get('utm_campaign'), 'propia');
  assert.equal(p.get('utm_source'), 'pinterest');
});

prueba('enlaces relativos /auditoria y /viabilidad/ se decoran', () => {
  const e = escenario({ url: 'https://sayeghstudio.com/?utm_source=pinterest', hrefs: ['/auditoria', '/viabilidad/', '/auditoria/'] });
  e.hrefs().forEach((h) => { assert.ok(h.startsWith('https://sayeghstudio.com/') || h.startsWith('/')); assert.equal(params(h).get('utm_source'), 'pinterest'); });
});

prueba('enlaces ajenos no se tocan', () => {
  const hs = ['https://www.instagram.com/x', '/blog/', '/auditoria-de-obra/', 'mailto:a@b.com', 'tel:+5255', '#top', 'https://otra.com/auditoria', 'https://via.sayeghstudio.com.falso.com/'];
  const e = escenario({ url: 'https://sayeghstudio.com/?utm_source=pinterest', hrefs: hs });
  assert.deepEqual(e.hrefs(), hs);
});

prueba('el hash se conserva', () => {
  const e = escenario({ url: 'https://sayeghstudio.com/?utm_source=pinterest', hrefs: ['https://via.sayeghstudio.com/?a=1#form'] });
  const u = new URL(e.hrefs()[0]);
  assert.equal(u.hash, '#form');
  assert.equal(u.searchParams.get('a'), '1');
  assert.equal(u.searchParams.get('utm_source'), 'pinterest');
});

prueba('sanitiza <script> y limita a 60', () => {
  const e = escenario({ url: 'https://sayeghstudio.com/?utm_source=' + encodeURIComponent('<script>alert(1)</script>') + '&utm_term=' + 'a'.repeat(100), hrefs: ['https://via.sayeghstudio.com'] });
  const o = JSON.parse(e.almacen.sayegh_utm);
  assert.equal(o.utm_source, 'scriptalert1script');
  assert.equal(o.utm_term.length, 60);
  assert.ok(!/[<>()\/]/.test(e.hrefs()[0].split('?')[1]));
});

prueba('sessionStorage lanza error: sigue funcionando con memoria', () => {
  const e = escenario({ url: 'https://sayeghstudio.com/?utm_source=pinterest', storageFalla: true, hrefs: ['https://via.sayeghstudio.com'] });
  assert.equal(params(e.hrefs()[0]).get('utm_source'), 'pinterest');
});

prueba('href inválido no rompe', () => {
  const e = escenario({ url: 'https://sayeghstudio.com/?utm_source=pinterest', hrefs: ['http://[::malo', '', null, 'https://via.sayeghstudio.com'] });
  assert.equal(params(e.hrefs()[3]).get('utm_source'), 'pinterest');
});

prueba('enlaces tardíos: click/auxclick/contextmenu en captura', () => {
  const e = escenario({ url: 'https://sayeghstudio.com/?utm_source=pinterest', hrefs: [] });
  for (const ev of ['click', 'auxclick', 'contextmenu']) {
    assert.ok(e.oyentes[ev].some((o) => o.cap === true), ev);
    const a = { _h: 'https://via.sayeghstudio.com', getAttribute() { return this._h; }, setAttribute(_, v) { this._h = v; } };
    a.closest = () => a;
    e.lanzar(ev, a);
    assert.equal(params(a._h).get('utm_source'), 'pinterest');
  }
});

prueba('android-app:// mapea apps conocidas', () => {
  const casos = { 'android-app://com.pinterest': ['pinterest', 'organic_pin'], 'android-app://com.google.android.googlequicksearchbox/': ['google', 'organic'], 'android-app://com.instagram.android': ['instagram', 'social'], 'android-app://com.facebook.katana': ['facebook', 'social'], 'android-app://com.otra.app': ['com.otra.app', 'referral'], 'android-app://com.google.android.gm': ['com.google.android.gm', 'referral'] };
  for (const [r, [src, med]] of Object.entries(casos)) {
    const e = escenario({ url: 'https://sayeghstudio.com/', referrer: r, hrefs: ['https://via.sayeghstudio.com'] });
    assert.equal(params(e.hrefs()[0]).get('utm_source'), src, r);
    assert.equal(params(e.hrefs()[0]).get('utm_medium'), med, r);
  }
});

prueba('subdominios de buscadores que no son búsqueda cuentan como referral', () => {
  for (const r of ['https://mail.google.com/', 'https://docs.google.com/x', 'https://drive.google.com/', 'https://mail.yahoo.com/']) {
    const e = escenario({ url: 'https://sayeghstudio.com/', referrer: r, hrefs: ['https://via.sayeghstudio.com'] });
    assert.equal(params(e.hrefs()[0]).get('utm_medium'), 'referral', r);
  }
  for (const [r, src] of [['https://www.google.com/', 'google'], ['https://google.com.mx/', 'google'], ['https://www.bing.com/', 'bing'], ['https://search.yahoo.com/', 'yahoo'], ['https://duckduckgo.com/', 'duckduckgo'], ['https://www.ecosia.org/', 'ecosia']]) {
    const e = escenario({ url: 'https://sayeghstudio.com/', referrer: r, hrefs: ['https://via.sayeghstudio.com'] });
    assert.equal(params(e.hrefs()[0]).get('utm_source'), src, r);
    assert.equal(params(e.hrefs()[0]).get('utm_medium'), 'organic', r);
  }
});

prueba('selector de lead de Pinterest sigue coincidiendo', () => {
  const e = escenario({ url: 'https://sayeghstudio.com/?utm_source=pinterest', hrefs: ['https://via.sayeghstudio.com'] });
  assert.ok(e.hrefs()[0].includes('via.sayeghstudio.com'));
});

console.log(`\n${ok} pruebas pasaron`);
