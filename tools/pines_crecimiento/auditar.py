#!/usr/bin/env python3
"""
Auditoría de cero errores para los pines de crecimiento (agente auditor).

Uso: python3 tools/pines_crecimiento/auditar.py <carpeta_de_salida_en_boveda>
Revisa los CSV y .md entregados, las imágenes del worktree y los cruces contra los CSV previos
y los feeds RSS. Sale con código 1 si hay al menos un error.
"""
import csv
import datetime as dt
import glob
import os
import re
import sys
from urllib.parse import urlparse, parse_qs

from PIL import Image, ImageChops

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contenido as C  # noqa: E402
from construir import VETADAS, COLS_CARGA, HTML_DIR, vetadas_en  # noqa: E402

RAIZ = C.RAIZ
BOVEDA_PIN = '/mnt/project-files/06_Growth_SEO_Copy/pinterest/'
CAMPANAS = {'conversion_auditoria', 'zonas', 'materiales', 'blog'}
COLS_CAL = ['fecha', 'slug', 'tablero', 'tipo', 'titulo_40', 'descripcion', 'url_imagen', 'url_destino_con_utm',
            'estado', 'impresiones_7d', 'guardados_7d', 'clics_7d']
PROHIBIDAS_FUENTE = ['avivia', 'piedras_chinas', 'temixco', 'taller']

errores, avisos, ok = [], [], []


def err(m):
    errores.append(m)


def leer_csv(ruta):
    with open(ruta, encoding='utf-8-sig') as fh:
        return list(csv.DictReader(fh))


def main(salida):
    sitemap = set(re.findall(r'<loc>([^<]+)</loc>', open(os.path.join(RAIZ, 'sitemap.xml')).read()))
    redirects = open(os.path.join(RAIZ, '_redirects')).read()
    destinos_validos = {urlparse(u).path for u in sitemap}
    if re.search(r'^/auditoria\s', redirects, re.M):
        destinos_validos.add('/auditoria')

    # Combinaciones previas imagen+enlace (CSV de 47, conversión y feeds)
    previas = set()
    for ruta in [BOVEDA_PIN + '2026-11-06_PINES_carga_masiva.csv',
                 BOVEDA_PIN + 'pines_conversion/2026-11-06_PINES_conversion_carga.csv']:
        for r in leer_csv(ruta):
            previas.add((r['Media URL'], urlparse(r['Link']).path))
    imagenes_previas = {m for m, _ in previas}
    for feed in glob.glob(os.path.join(RAIZ, 'feed*.xml')):
        t = open(feed, encoding='utf-8').read()
        for it in re.findall(r'<item>(.*?)</item>', t, re.S):
            link = re.search(r'<link>(.*?)</link>', it).group(1)
            for img in set(re.findall(r'url="([^"]+)"', it)):
                previas.add((img, urlparse(link).path))
                imagenes_previas.add(img)
    ok.append(f'Combinaciones previas cargadas para el cruce: {len(previas)}')

    ocupados = {u + ':00' for u in C.YA_PROGRAMADOS_OTROS_UTC} | {f'{f}T16:30:00' for f, *_ in C.YA_PROGRAMADOS_CONVERSION}

    # ---------------------------------------------------------- CSV de carga
    datos = {p['slug']: p for p in C.PINES + C.SEMILLAS}
    vistos_media, vistos_slug, vistos_fecha = set(), set(), set()
    filas_total = 0
    for nombre in ('PINES_crecimiento_carga.csv', 'PINES_tableros_nuevos_carga.csv'):
        ruta = os.path.join(salida, nombre)
        if not os.path.exists(ruta):
            err(f'Falta {nombre}')
            continue
        with open(ruta, encoding='utf-8') as fh:
            cab = next(csv.reader(fh))
        if cab != COLS_CARGA:
            err(f'{nombre}: columnas {cab} distintas al formato oficial')
        filas = leer_csv(ruta)
        filas_total += len(filas)
        for i, r in enumerate(filas, 2):
            ref = f'{nombre}:{i}'
            if len(r['Title']) > 100:
                err(f'{ref} título de {len(r["Title"])} caracteres')
            if len(r['Description']) > 500:
                err(f'{ref} descripción de {len(r["Description"])} caracteres')
            if not r['Title'] or not r['Description'] or not r['Keywords']:
                err(f'{ref} campo vacío')
            try:
                d = dt.datetime.strptime(r['Publish date'], '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                err(f'{ref} fecha no ISO: {r["Publish date"]}')
                continue
            if not (dt.datetime(2026, 11, 8) <= d <= dt.datetime(2026, 12, 7, 6)):
                err(f'{ref} fecha fuera de rango: {r["Publish date"]}')
            if r['Publish date'] in ocupados:
                err(f'{ref} choca con un horario ya ocupado: {r["Publish date"]}')
            if r['Publish date'] in vistos_fecha:
                err(f'{ref} hora repetida dentro de nuestros CSV: {r["Publish date"]}')
            vistos_fecha.add(r['Publish date'])
            u = urlparse(r['Link'])
            q = {k: v[0] for k, v in parse_qs(u.query).items()}
            if u.scheme != 'https' or u.netloc != 'sayeghstudio.com':
                err(f'{ref} enlace fuera del sitio: {r["Link"]}')
            if u.path not in destinos_validos:
                err(f'{ref} destino no está en sitemap ni en _redirects: {u.path}')
            if q.get('utm_source') != 'pinterest' or q.get('utm_medium') != 'organic_pin':
                err(f'{ref} UTM source/medium incorrectos')
            if q.get('utm_campaign') not in CAMPANAS:
                err(f'{ref} utm_campaign fuera del contrato: {q.get("utm_campaign")}')
            if (u.path == '/auditoria') != (q.get('utm_campaign') == 'conversion_auditoria'):
                err(f'{ref} campaña y destino de auditoría no coinciden')
            slug = q.get('utm_content', '')
            if slug in vistos_slug:
                err(f'{ref} utm_content repetido: {slug}')
            vistos_slug.add(slug)
            if not r['Media URL'].endswith(f'/{slug}.jpg'):
                err(f'{ref} el archivo no coincide con el slug')
            if r['Media URL'] in vistos_media:
                err(f'{ref} imagen repetida: {r["Media URL"]}')
            vistos_media.add(r['Media URL'])
            if (r['Media URL'], u.path) in previas or r['Media URL'] in imagenes_previas:
                err(f'{ref} duplica una combinación o imagen previa (CSV de 47, conversión o feed)')
            if not r['Media URL'].startswith('https://sayeghstudio.com/assets/pinterest/crecimiento/'):
                err(f'{ref} Media URL fuera de assets/pinterest/crecimiento')
            local = os.path.join(RAIZ, urlparse(r['Media URL']).path.lstrip('/'))
            if not os.path.exists(local):
                err(f'{ref} falta el archivo en el worktree: {local}')
            p = datos.get(slug)
            if not p:
                err(f'{ref} slug sin ficha en contenido.py: {slug}')
                continue
            if r['Pinterest board'] != C.TAB[p['tab']]:
                err(f'{ref} tablero distinto al de la ficha')
            if len(p['t40']) > 40:
                err(f'{ref} titulo_40 de {len(p["t40"])} caracteres')
            if p['t40'].lower() not in r['Title'][:41].lower():
                err(f'{ref} la palabra clave corta no está en los primeros 40 caracteres del título')
            fuente = p['img']['src'].lower()
            if any(x in fuente for x in PROHIBIDAS_FUENTE):
                err(f'{ref} usa una imagen vetada: {fuente}')
            if p['marca'] == 'render':
                if C.LEYENDA not in r['Description']:
                    err(f'{ref} imagen render sin la leyenda de render conceptual en la descripción')
                html = os.path.join(HTML_DIR, f'{slug}.html')
                if not os.path.exists(html) or C.LEYENDA not in open(html, encoding='utf-8').read():
                    err(f'{ref} la imagen no lleva la leyenda de render conceptual')
            if 'conceptual' not in r['Description'].lower() and p['marca'] == 'render':
                err(f'{ref} falta la palabra "conceptual"')
            if not re.search(r'guarde|auditoría de viabilidad', r['Description'], re.I):
                err(f'{ref} la descripción no llama a guardar ni a la Auditoría')
    ok.append(f'Filas de carga revisadas: {filas_total}')

    # Uno por semana a la Auditoría
    conv = sorted(p['fecha'] for p in C.PINES if p['camp'] == 'conversion_auditoria')
    for a, b in [('2026-11-16', '2026-11-22'), ('2026-11-23', '2026-11-29'), ('2026-11-30', '2026-12-06')]:
        if not any(a <= f <= b for f in conv):
            err(f'Semana {a} sin pin a la Auditoría')

    # ---------------------------------------------------------- imágenes
    n_img = 0
    for p in C.PINES + C.SEMILLAS:
        ruta = os.path.join(RAIZ, 'assets', 'pinterest', 'crecimiento', p['slug'] + '.jpg')
        if not os.path.exists(ruta):
            continue
        n_img += 1
        im = Image.open(ruta)
        if im.size != (1000, 1500):
            err(f'{p["slug"]}.jpg mide {im.size}')
        kb = os.path.getsize(ruta) / 1024
        if kb >= 300:
            err(f'{p["slug"]}.jpg pesa {kb:.0f} KB')
        copia = os.path.join(salida, 'imagenes', p['slug'] + '.jpg')
        # La bóveda agrega un manifiesto C2PA (segmento APP11) al guardar; se comparan los píxeles, no los bytes.
        if not os.path.exists(copia):
            err(f'{p["slug"]}.jpg falta en la bóveda')
        else:
            with Image.open(copia) as cb, Image.open(ruta) as cr:
                if cb.size != cr.size or ImageChops.difference(cb.convert('RGB'), cr.convert('RGB')).getbbox():
                    err(f'{p["slug"]}.jpg no está copiada igual en la bóveda')
    ok.append(f'Imágenes revisadas (1000 x 1500, <300 KB): {n_img}')

    # ---------------------------------------------------------- calendario
    cal_ruta = os.path.join(os.path.dirname(os.path.normpath(salida)), 'CALENDARIO_pines.csv')
    if not os.path.exists(cal_ruta):
        err('Falta CALENDARIO_pines.csv en 06_Growth_SEO_Copy/pinterest/')
    else:
        with open(cal_ruta, encoding='utf-8') as fh:
            cab = next(csv.reader(fh))
        if cab[:12] != COLS_CAL or not {'segmento', 'dia', 'hora_cdmx', 'bloque'} <= set(cab):
            err(f'CALENDARIO_pines.csv: columnas no cumplen §6.3 + extras: {cab}')
        filas = leer_csv(cal_ruta)
        por_dia = {}
        for r in filas:
            if len(r['titulo_40']) > 40:
                err(f'calendario {r["slug"]}: titulo_40 largo')
            if len(r['descripcion']) > 500:
                err(f'calendario {r["slug"]}: descripción larga')
            por_dia[r['fecha']] = por_dia.get(r['fecha'], 0) + 1
        horas = {}
        for r in filas:
            horas.setdefault(r['publish_date_utc'], []).append(r['slug'])
        for h, ss in horas.items():
            if len(ss) > 1:
                err(f'calendario: choque de hora {h}: {", ".join(ss)}')
        if max(por_dia.values()) > 25:
            err('Más de 25 pines en un día')
        semanas = [('2026-11-08', '2026-11-15'), ('2026-11-16', '2026-11-22'), ('2026-11-23', '2026-11-29'),
                   ('2026-11-30', '2026-12-06')]
        for a, b in semanas:
            n = sum(1 for r in filas if a <= r['fecha'] <= b and r['estado'] in ('borrador', 'producido_otro_agente'))
            if n != 7:
                err(f'Semana {a}: {n} pines frescos (contrato: 7)')
        ok.append(f'Calendario: {len(filas)} filas, máximo {max(por_dia.values())} por día')

    # ---------------------------------------------------------- texto de todos los entregables
    entregables = [os.path.join(salida, f) for f in ('PINES_crecimiento_carga.csv', 'PINES_tableros_nuevos_carga.csv',
                                                     'PINES_crecimiento_detalle.csv', 'CALENDARIO_30_dias.md',
                                                     'CALENDARIO_30_dias.csv', 'NOTA_B2_tableros_nuevos_semillas.md')]
    entregables.append(cal_ruta)
    for ruta in entregables:
        if not os.path.exists(ruta):
            err(f'Falta {os.path.basename(ruta)}')
            continue
        texto = open(ruta, encoding='utf-8').read().lower()
        texto = texto.replace('¿cómo garantizan', '')  # no aplica a nuestros archivos
        for v in vetadas_en(texto):
            err(f'{os.path.basename(ruta)}: contiene "{v}"')
        for marca in ('—', '–'):
            if texto.count(marca) > 1:
                avisos.append(f'{os.path.basename(ruta)}: {texto.count(marca)} rayas o semirrayas')
    ok.append(f'Entregables de texto revisados contra {len(VETADAS)} términos vetados: {len(entregables)}')


if __name__ == '__main__':
    main(sys.argv[1])
    for m in ok:
        print('OK   ', m)
    for m in avisos:
        print('AVISO', m)
    for m in errores:
        print('ERROR', m)
    print(f'\nResultado: {len(errores)} errores, {len(avisos)} avisos')
    sys.exit(1 if errores else 0)
