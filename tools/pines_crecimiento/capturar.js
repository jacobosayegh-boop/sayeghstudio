#!/usr/bin/env node
/*
 * Captura páginas HTML a JPG o PNG con Playwright (Chromium).
 * Uso: node tools/pines_crecimiento/capturar.js <trabajos.json>
 * trabajos.json = [{ "html": ruta, "salida": ruta, "ancho": 1000, "alto": 1500,
 *                    "png": false, "transparente": false, "calidad": 86 }]
 * Lo invoca construir.py; no hace falta llamarlo a mano.
 */
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const trabajos = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch();
  for (const t of trabajos) {
    const page = await browser.newPage({ viewport: { width: t.ancho, height: t.alto }, deviceScaleFactor: 1 });
    await page.goto('file://' + path.resolve(t.html), { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    const choque = await page.evaluate(() => {
      const t = document.querySelector('.texto');
      const c = document.querySelector('.cinta');
      if (!t || !c) return null;
      const a = t.getBoundingClientRect();
      const b = c.getBoundingClientRect();
      return a.bottom > b.top - 20 ? Math.round(a.bottom - b.top) : null;
    });
    if (choque !== null) console.warn(`AVISO ${path.basename(t.salida)}: el texto invade la cinta (${choque}px)`);
    const opts = { path: t.salida };
    if (t.png) { opts.type = 'png'; opts.omitBackground = !!t.transparente; }
    else { opts.type = 'jpeg'; opts.quality = t.calidad || 86; }
    for (let intento = 1; ; intento++) {
      try { await page.screenshot(opts); break; } catch (e) {
        if (intento >= 4) throw e;
        console.log(`reintento ${intento} ${path.basename(t.salida)}`);
        await page.waitForTimeout(1500 * intento);
      }
    }
    await page.close();
    console.log('OK', path.basename(t.salida), Math.round(fs.statSync(t.salida).size / 1024), 'KB');
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
