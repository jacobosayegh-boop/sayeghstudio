#!/usr/bin/env node
/*
 * Genera los 6 pines de conversión para Pinterest (1000 x 1500 px, 2:3).
 *
 * Uso (desde la raíz del repo):
 *   node tools/pines_conversion/generar_pines.js
 *
 * Variables opcionales:
 *   RENDERS_DIR  carpeta con los renders de zonas (por omisión, la bóveda:
 *                /mnt/project-files/05_Portafolio_Web/renders_zonas_2026-11-06/)
 *   SALIDA_DIR   carpeta de salida (por omisión assets/pinterest/conversion/)
 *
 * Flujo: plantilla.html + datos de cada pin -> html/pin-0N-<tema>.html ->
 * captura con Playwright (Chromium) -> JPG calidad 88.
 *
 * Regla de marca: todo render lleva la leyenda "Render conceptual";
 * las fotos reales de obra no la llevan.
 */
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const RAIZ = path.resolve(__dirname, '..', '..');
const AQUI = __dirname;
const HTML_DIR = path.join(AQUI, 'html');
const RENDERS_DIR = process.env.RENDERS_DIR || '/mnt/project-files/05_Portafolio_Web/renders_zonas_2026-11-06/';
const SALIDA_DIR = process.env.SALIDA_DIR || path.join(RAIZ, 'assets', 'pinterest', 'conversion');

const repo = (p) => path.join(RAIZ, p);
const render = (f) => path.join(RENDERS_DIR, f);

// pos = background-position de cada imagen dentro de su recuadro.
const PINES = [
  {
    id: 'pin-01-presupuesto',
    modo: 'full', tono: 'oscuro', mediaH: 1500, textoTop: 900, h1: 84,
    fotos: [{ src: repo('assets/images/projects/nuvana.jpg'), pos: 'center 30%' }],
    esRender: false,
    credito: 'Nuvana, Interlomas',
    kicker: 'Ingeniería financiera',
    titular: 'El precio se firma antes de excavar',
    apoyo: 'Precios unitarios inquebrantables, auditados antes de mover la primera piedra.',
  },
  {
    id: 'pin-02-patrimonial',
    modo: 'split', tono: 'claro', mediaH: 860, textoTop: 924, h1: 78,
    fotos: [{ src: render('lomas_vestibulo.jpg'), pos: '45% center' }],
    esRender: true,
    kicker: 'Remodelación patrimonial',
    titular: 'Usted no coordina contratistas',
    apoyo: 'Dirección de obra pericial: un solo responsable de la demolición a la entrega.',
  },
  {
    id: 'pin-03-inversion',
    modo: 'split', tono: 'oscuro', mediaH: 860, textoTop: 924, h1: 74,
    fotos: [{ src: render('bosques_exterior.jpg'), pos: '52% center' }],
    esRender: true,
    kicker: 'Brokers y family offices',
    titular: 'Viabilidad antes de comprar el terreno',
    apoyo: 'Normativa, costo de obra y plusvalía, analizados antes de firmar la compra.',
  },
  {
    id: 'pin-04-materiales',
    modo: 'split', tono: 'claro', mediaH: 860, textoTop: 924, h1: 74,
    fotos: [
      { src: repo('assets/images/materials/travertino.jpg'), pos: 'center', etiqueta: 'Travertino' }
    ],
    esRender: false,
    kicker: 'Materialidad atemporal',
    titular: 'Materiales que no envejecen',
    apoyo: 'Travertino a la veta, elegido para durar décadas y no temporadas.',
  },
  {
    id: 'pin-05-bano',
    modo: 'split', tono: 'claro', mediaH: 860, textoTop: 924, h1: 78,
    fotos: [{ src: render('polanco_bano.jpg'), pos: '58% center' }],
    esRender: true,
    kicker: 'Baño y walk-in closet de autor',
    titular: 'Un baño pensado como santuario',
    apoyo: 'Piedra natural, luz cálida y cada pieza cotizada antes de construir.',
  },
  {
    id: 'pin-06-zona',
    modo: 'split', tono: 'oscuro', mediaH: 860, textoTop: 924, h1: 78,
    fotos: [{ src: render('interlomas_exterior.jpg'), pos: '50% center' }],
    esRender: true,
    kicker: 'Interlomas · Bosques · Lomas',
    titular: 'Arquitectura de autor en Interlomas',
    apoyo: 'Obra nueva y remodelación con rigor constructivo y dirección de obra pericial.',
  },
];

function rel(desde, archivo) {
  return path.relative(desde, archivo).split(path.sep).join('/');
}

function construirHtml(pin, plantilla) {
  const fotos = pin.fotos.map((f) => {
    // Archivos del repo: ruta relativa. Archivos fuera del repo (renders de la bóveda): file:// absoluto.
    const dentro = !path.relative(RAIZ, f.src).startsWith('..');
    const url = dentro ? rel(HTML_DIR, f.src) : 'file://' + path.resolve(f.src);
    const etiqueta = f.etiqueta ? `<span class="etiqueta">${f.etiqueta}</span>` : '';
    return `<div class="foto" style="background-image:url('${url}');background-position:${f.pos}">${etiqueta}</div>`;
  }).join('');

  let marca = '';
  if (pin.esRender) {
    // La leyenda va en la esquina inferior derecha de la imagen.
    marca = '<span class="render">Render conceptual</span>';
  } else if (pin.credito) {
    marca = `<span class="credito">${pin.credito}</span>`;
  }
  const renderBottom = 1500 - pin.mediaH + 28;

  const datos = {
    ID: pin.id,
    TONO: pin.tono,
    MODO: pin.modo,
    MEDIA_H: pin.mediaH,
    TEXTO_TOP: pin.textoTop,
    H1_SIZE: pin.h1,
    RENDER_BOTTOM: renderBottom,
    FOTOS: fotos,
    LOGO: rel(HTML_DIR, path.join(AQUI, 'logos', 'sayegh-principal-negativo.svg')),
    MARCA_IMAGEN: marca,
    KICKER: pin.kicker,
    TITULAR: pin.titular,
    APOYO: pin.apoyo,
  };
  return plantilla.replace(/\{\{(\w+)\}\}/g, (m, k) => (k in datos ? String(datos[k]) : m));
}

(async () => {
  const plantilla = fs.readFileSync(path.join(AQUI, 'plantilla.html'), 'utf8');
  fs.mkdirSync(HTML_DIR, { recursive: true });
  fs.mkdirSync(SALIDA_DIR, { recursive: true });

  for (const pin of PINES) {
    for (const f of pin.fotos) {
      if (!fs.existsSync(f.src)) throw new Error(`No existe la imagen ${f.src}`);
    }
    fs.writeFileSync(path.join(HTML_DIR, `${pin.id}.html`), construirHtml(pin, plantilla));
  }

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1000, height: 1500 }, deviceScaleFactor: 1 });
  for (const pin of PINES) {
    await page.goto('file://' + path.join(HTML_DIR, `${pin.id}.html`), { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    // Verifica que el texto no se salga de su zona (no debe tocar la cinta).
    const choque = await page.evaluate(() => {
      const t = document.querySelector('.texto').getBoundingClientRect();
      const c = document.querySelector('.cinta').getBoundingClientRect();
      return t.bottom > c.top - 24 ? Math.round(t.bottom - c.top) : null;
    });
    if (choque !== null) console.warn(`AVISO ${pin.id}: el texto queda a ${choque}px de la cinta`);
    const salida = path.join(SALIDA_DIR, `${pin.id}.jpg`);
    await page.screenshot({ path: salida, type: 'jpeg', quality: 88 });
    const kb = Math.round(fs.statSync(salida).size / 1024);
    console.log(`${pin.id}.jpg  ${kb} KB`);
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
