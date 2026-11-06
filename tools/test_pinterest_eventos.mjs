// Pruebas del bloque "PINTEREST TAG" de js/main.js.
// Uso: node tools/test_pinterest_eventos.mjs  (sin dependencias)
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const raiz = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const src = fs.readFileSync(path.join(raiz, 'js/main.js'), 'utf8');
const ini = src.indexOf('const PinterestTag');
const fin = src.indexOf('/* ── MANIFIESTO VIDEO SOUND TOGGLE');
assert.ok(ini > 0 && fin > ini, 'no se encontró el bloque de Pinterest');
const bloque = src.slice(ini, fin);

function escenario({ ruta, consentimiento }) {
  const llamadas = [];
  const oyentes = {};
  const almacen = consentimiento ? { ga_consent_status: 'accepted' } : {};
  const window = {};
  const document = {
    createElement: () => ({}),
    getElementsByTagName: () => [{ parentNode: { insertBefore() {} } }],
    addEventListener(ev, fn) { (oyentes[ev] ||= []).push(fn); },
  };
  // El código base de Pinterest define window.pintrk si no existe: se sustituye por un registrador.
  Object.defineProperty(window, 'pintrk', {
    configurable: true,
    set() { Object.defineProperty(window, 'pintrk', { value: (...a) => llamadas.push(a), writable: true, configurable: true }); },
    get() { return undefined; },
  });
  const ctx = {
    window, document, location: { pathname: ruta },
    localStorage: { getItem: (k) => (k in almacen ? almacen[k] : null) },
  };
  vm.runInNewContext(bloque, ctx);
  const clic = (coincide) => {
    const t = { closest: (sel) => (coincide(sel) ? {} : null) };
    (oyentes.click || []).forEach((fn) => fn({ target: t }));
  };
  return { llamadas, almacen, clic };
}
const esCta = (s) => s.includes('via.sayeghstudio.com');
const esAceptar = (s) => s === '#consent-accept';
const eventos = (l) => JSON.parse(JSON.stringify(l)).filter((a) => a[0] === 'track').map((a) => a.slice(1));

let ok = 0;
const prueba = (n, f) => { f(); ok++; console.log('ok  - ' + n); };

prueba('sin consentimiento no hay llamadas', () => {
  const e = escenario({ ruta: '/zonas-landing/polanco/', consentimiento: false });
  e.clic(esCta);
  assert.equal(e.llamadas.length, 0);
});

prueba('con consentimiento en zona: pagevisit y viewcategory zona-<slug>', () => {
  const e = escenario({ ruta: '/zonas-landing/polanco/', consentimiento: true });
  assert.deepEqual(eventos(e.llamadas), [['pagevisit'], ['viewcategory', { category: 'zona-polanco' }]]);
});

prueba('clic a via envía custom clic_auditoria y NO lead', () => {
  const e = escenario({ ruta: '/zonas-landing/polanco/', consentimiento: true });
  e.clic(esCta);
  const ev = eventos(e.llamadas);
  assert.deepEqual(ev.at(-1), ['custom', { event_name: 'clic_auditoria' }]);
  assert.ok(!ev.some((x) => x[0] === 'lead'));
});

prueba('blog y materiales', () => {
  const ult = (r) => eventos(escenario({ ruta: r, consentimiento: true }).llamadas).at(-1);
  assert.deepEqual(ult('/blog/estrategia/'), ['viewcategory', { category: 'blog' }]);
  assert.deepEqual(ult('/blog/'), ['viewcategory', { category: 'blog' }]);
  assert.deepEqual(ult('/blog/materiales/'), ['viewcategory', { category: 'blog' }]);
  assert.deepEqual(ult('/blog/materiales/concreto-aparente-lujo/'), ['viewcategory', { category: 'material-concreto-aparente-lujo' }]);
});

prueba('otras páginas no envían viewcategory', () => {
  for (const r of ['/', '/guia/', '/privacidad/', '/aliados/', '/blogger/']) {
    assert.deepEqual(eventos(escenario({ ruta: r, consentimiento: true }).llamadas), [['pagevisit']]);
  }
});

prueba('slug saneado a [a-z0-9-] y máximo 60', () => {
  const a = escenario({ ruta: '/zonas-landing/Pol_anco%20X/', consentimiento: true });
  assert.equal(eventos(a.llamadas).at(-1)[1].category, 'zona-polanco20x');
  const b = escenario({ ruta: '/zonas-landing/' + 'a'.repeat(100) + '/', consentimiento: true });
  assert.equal(eventos(b.llamadas).at(-1)[1].category, 'zona-' + 'a'.repeat(60));
});

prueba('aceptar después: viewcategory una sola vez', () => {
  const e = escenario({ ruta: '/blog/estrategia/', consentimiento: false });
  e.clic(esAceptar);
  assert.equal(e.llamadas.length, 0);
  e.almacen.ga_consent_status = 'accepted';
  e.clic(esAceptar);
  e.clic(esAceptar);
  assert.deepEqual(eventos(e.llamadas), [['pagevisit'], ['viewcategory', { category: 'blog' }]]);
});

console.log(`\n${ok} pruebas pasaron`);
