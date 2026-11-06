#!/usr/bin/env python3
"""
Construye los pines de crecimiento de Pinterest de Sayegh Studio (4 semanas, 8-nov a 6-dic de 2026): 20 pines de zona,
material y conversión, más 12 semillas para los dos tableros nuevos.

Uso (desde la raíz del repo):
    python3 tools/pines_crecimiento/construir.py [imagenes] [csv]
Sin argumentos hace las dos cosas. FILTRO=<regex> limita las imágenes a los slugs que coincidan.

Requisitos: Python 3 con Pillow y Node con Playwright (Chromium).
Los renders 3D conceptuales ya están en tools/pines_crecimiento/renders/ (los genera escenas_3d.py).

Salidas:
  assets/pinterest/crecimiento/*.jpg   pines 2:3 de 1000 x 1500 (<300 KB)
  tools/pines_crecimiento/salida/      CSV de carga, CSV de semillas, detalle y calendario
"""
import csv
import datetime as dt
import io
import json
import os
import re
import subprocess
import sys
import tempfile

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contenido as C  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = C.RAIZ
SALIDA_IMG = os.environ.get('SALIDA_DIR', os.path.join(RAIZ, 'assets', 'pinterest', 'crecimiento'))
SALIDA_CSV = os.path.join(AQUI, 'salida')
HTML_DIR = os.path.join(AQUI, 'html')
BASE = 'https://sayeghstudio.com'
MEDIA_BASE = BASE + '/assets/pinterest/crecimiento/'
MAX_KB = 295

# Lista de exclusión: 35 términos de TABLEROS_y_palabras_clave.md + ampliación del contrato §6.5
# + palabras vetadas del encargo. Se compara sin mayúsculas. Ninguna fila con estas palabras pasa.
VETADAS = [
    'gratis', 'gratuita', 'gratuito', 'sin sobrecostos', '0% sobrecostos', '0 %', '0%', 'cero sobrecostos',
    'sobrecosto', 'garantiz', 'barato', 'barata', 'económic', 'economic', 'bonito', 'bonita', 'el mejor',
    'los mejores', 'lujo ostentoso', 'descuento', 'promoción', 'promocion', 'oferta', 'precio especial',
    'millones de pesos', 'mxn', '#ad', '#publicidad', '#patrocinado', 'colaboración pagada', 'sorteo',
    'giveaway', '#repost', 'taller 18', 'cumpleaños', 'vacaciones', 'sin costo total', 'presupuesto rápido',
    'diseño gratis', 'te ayudamos a decorar', '$',
]

DIAS = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']


def vetadas_en(texto):
    """Términos vetados presentes en el texto. "0 %" solo cuenta como cifra suelta, no dentro de "30 %"."""
    t = texto.lower()
    hallados = []
    for v in VETADAS:
        if v in ('0 %', '0%'):
            if re.search(r'(?<![\d.,])0 ?%', t) and '0 %' not in hallados:
                hallados.append('0 %')
        elif v in t:
            hallados.append(v)
    return hallados


def revisar_texto(etiqueta, texto):
    for v in vetadas_en(texto):
        raise SystemExit(f'ERROR palabra vetada "{v}" en {etiqueta}: {texto[:80]}')


def utc(fecha, hora):
    d = dt.datetime.strptime(f'{fecha} {hora}', '%Y-%m-%d %H:%M') + dt.timedelta(hours=6)
    return d.strftime('%Y-%m-%dT%H:%M:%S')


def enlace(destino, camp, slug):
    q = f'utm_source=pinterest&utm_medium=organic_pin&utm_campaign={camp}&utm_content={slug}'
    return f'{BASE}{destino}?{q}'


# ------------------------------------------------------------------ imágenes
def foto_html(f, desde):
    src = f['src']
    if not os.path.exists(src) and not os.environ.get('FILTRO'):
        raise SystemExit(f'No existe la imagen {src}')
    dentro = not os.path.relpath(src, RAIZ).startswith('..')
    url = os.path.relpath(src, desde).replace(os.sep, '/') if dentro else 'file://' + os.path.abspath(src)
    tam = f"{f['zoom']}%" if f.get('zoom') else 'cover'
    et = f'<span class="etiqueta">{f["etiqueta"]}</span>' if f.get('etiqueta') else ''
    return f'<div class="foto" style="background-image:url(\'{url}\');background-position:{f.get("pos", "center")};background-size:{tam}">{et}</div>'


def html_pin(plantilla, d, foto, ancho=1000, alto=1500, capa=False, serie=''):
    media_h = 920 if not capa else alto
    marca = ''
    if d.get('marca') == 'render':
        marca = f'<span class="render">{C.LEYENDA}</span>'
    elif d.get('marca') == 'credito':
        marca = f'<span class="credito">{d.get("credito", "")}</span>'
    if d.get('cinta') == 'auditoria':
        accion, url = 'Auditoría de Viabilidad', 'sayeghstudio.com/auditoria'
    else:
        accion, url = 'Guarde esta idea', 'sayeghstudio.com'
    if capa:
        texto_top, render_bottom = alto - 124 - 430, 124 + 450
    else:
        texto_top, render_bottom = media_h + 58, alto - media_h + 20
    datos = {
        'ID': d['id'], 'ANCHO': ancho, 'ALTO': alto, 'TONO': 'capa' if capa else d.get('tono', 'claro'),
        'MODO': 'capa' if capa else 'split', 'MEDIA_H': media_h, 'TEXTO_TOP': texto_top,
        'H1_SIZE': d.get('h1', 70), 'RENDER_BOTTOM': render_bottom,
        'FOTOS': foto or '', 'MARCA_IMAGEN': marca, 'KICKER': d['kicker'], 'TITULAR': d['titular'],
        'APOYO': d['apoyo'], 'CINTA_ACCION': accion, 'CINTA_URL': url,
        'SERIE': f'<span class="serie">{serie}</span>' if serie else '',
        'FONDO_BODY': 'transparent' if capa else '#1A1A1A',
    }
    return re.sub(r'\{\{(\w+)\}\}', lambda m: str(datos.get(m.group(1), m.group(0))), plantilla)


def optimizar_jpg(ruta):
    im = Image.open(ruta).convert('RGB')
    for q in (88, 84, 80, 76, 72, 68):
        buf = io.BytesIO()
        im.save(buf, 'JPEG', quality=q, optimize=True, progressive=True)
        if buf.tell() <= MAX_KB * 1024:
            break
    with open(ruta, 'wb') as fh:
        fh.write(buf.getvalue())
    return q, buf.tell() // 1024


def trabajos_imagenes():
    """Devuelve la lista de (id, html) de todos los pines estáticos y láminas de carrusel."""
    plantilla = open(os.path.join(AQUI, 'plantilla.html'), encoding='utf-8').read()
    lista = []
    for p in C.PINES + C.SEMILLAS:
        d = dict(p, id=p['slug'])
        largo = len(d['titular'])
        d['h1'] = 86 if largo <= 26 else 78 if largo <= 32 else 72
        lista.append((d['slug'], html_pin(plantilla, d, foto_html(p['img'], HTML_DIR))))
    return lista


def capturar(trabajos, json_path):
    with open(json_path, 'w') as fh:
        json.dump(trabajos, fh)
    r = subprocess.run(['node', os.path.join(AQUI, 'capturar.js'), json_path], cwd=RAIZ, text=True,
                       capture_output=True)
    print(r.stdout.strip())
    if r.returncode != 0 or 'AVISO' in r.stdout + r.stderr:
        print(r.stderr)
        raise SystemExit('Fallo o aviso en la captura')


def construir_imagenes():
    os.makedirs(HTML_DIR, exist_ok=True)
    os.makedirs(SALIDA_IMG, exist_ok=True)
    trabajos = []
    filtro = os.environ.get('FILTRO', '')
    for ident, html in trabajos_imagenes():
        if filtro and not re.search(filtro, ident):
            continue
        ruta_html = os.path.join(HTML_DIR, f'{ident}.html')
        with open(ruta_html, 'w', encoding='utf-8') as fh:
            fh.write(html)
        trabajos.append(dict(html=ruta_html, salida=os.path.join(SALIDA_IMG, f'{ident}.jpg'),
                             ancho=1000, alto=1500, calidad=90))
    capturar(trabajos, os.path.join(tempfile.gettempdir(), 'pines_crecimiento_trabajos.json'))
    for t in trabajos:
        q, kb = optimizar_jpg(t['salida'])
        print(f'  {os.path.basename(t["salida"])}: calidad {q}, {kb} KB')


# ------------------------------------------------------------------ CSV
COLS_CARGA = ['Title', 'Media URL', 'Pinterest board', 'Thumbnail', 'Description', 'Link', 'Publish date', 'Keywords']


def fila_carga(p, tablero=None):
    for campo in ('titulo', 'desc', 'kw', 't40'):
        revisar_texto(f'{p["slug"]}.{campo}', p[campo])
    return {
        'Title': p['titulo'], 'Media URL': MEDIA_BASE + p['slug'] + '.jpg',
        'Pinterest board': tablero or C.TAB[p['tab']], 'Thumbnail': '', 'Description': p['desc'],
        'Link': enlace(p['destino'], p['camp'], p['slug']), 'Publish date': utc(p['fecha'], p['hora']),
        'Keywords': p['kw'],
    }


def escribir_csv(ruta, cols, filas):
    with open(ruta, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(filas)


def construir_csv():
    os.makedirs(SALIDA_CSV, exist_ok=True)
    escribir_csv(os.path.join(SALIDA_CSV, 'PINES_crecimiento_carga.csv'), COLS_CARGA,
                 [fila_carga(p) for p in C.PINES])
    escribir_csv(os.path.join(SALIDA_CSV, 'PINES_tableros_nuevos_carga.csv'), COLS_CARGA,
                 [fila_carga(p) for p in C.SEMILLAS])

    cols_cal = ['fecha', 'slug', 'tablero', 'tipo', 'titulo_40', 'descripcion', 'url_imagen', 'url_destino_con_utm',
                'estado', 'impresiones_7d', 'guardados_7d', 'clics_7d', 'segmento', 'dia', 'hora_cdmx', 'bloque',
                'publish_date_utc', 'origen', 'nota']
    filas = []

    def dia(f):
        return DIAS[dt.date.fromisoformat(f).weekday()]

    for f, slug, tab, tit in C.YA_PROGRAMADOS_CONVERSION:
        filas.append(dict(fecha=f, slug=slug, tablero=tab, tipo='imagen', titulo_40=tit[:40], descripcion='',
                          url_imagen=f'{BASE}/assets/pinterest/conversion/{slug}.jpg',
                          url_destino_con_utm=f'https://via.sayeghstudio.com/?utm_source=pinterest&utm_medium=organic_pin&utm_campaign=conversion_auditoria&utm_content={slug}',
                          estado='cargado', segmento='A+B', dia=dia(f), hora_cdmx='10:30', bloque='conversion',
                          publish_date_utc=f'{f}T16:30:00', origen='pines_conversion (ya programado)', nota=''))
    for u in C.YA_PROGRAMADOS_OTROS_UTC:
        d = dt.datetime.strptime(u, '%Y-%m-%dT%H:%M') - dt.timedelta(hours=6)
        f = d.strftime('%Y-%m-%d')
        filas.append(dict(fecha=f, slug='', tablero='', tipo='imagen', titulo_40='', descripcion='',
                          url_imagen='', url_destino_con_utm='', estado='cargado', segmento='', dia=dia(f),
                          hora_cdmx=d.strftime('%H:%M'), bloque='', publish_date_utc=u + ':00',
                          origen='ya programado en la cuenta (contenido no informado al hilo B)', nota=''))

    def agregar(p, tipo, url_img, origen, estado='borrador', tablero=None):
        for campo in ('titulo', 'desc', 't40'):
            revisar_texto(f'{p["slug"]}.{campo}', p[campo])
        filas.append(dict(fecha=p['fecha'], slug=p['slug'], tablero=tablero or C.TAB[p['tab']], tipo=tipo,
                          titulo_40=p['t40'], descripcion=p['desc'], url_imagen=url_img,
                          url_destino_con_utm=enlace(p['destino'], p['camp'], p['slug']), estado=estado,
                          segmento=p['seg'], dia=dia(p['fecha']), hora_cdmx=p['hora'], bloque=p['bloque'],
                          publish_date_utc=utc(p['fecha'], p['hora']), origen=origen, nota=p.get('nota', '')))

    for p in C.PINES:
        agregar(p, 'imagen', MEDIA_BASE + p['slug'] + '.jpg', 'PINES_crecimiento_carga.csv')
    for p in C.SEMILLAS:
        agregar(p, 'imagen', MEDIA_BASE + p['slug'] + '.jpg', 'PINES_tableros_nuevos_carga.csv',
                estado='condicionado')
    for r in C.RESERVAS:
        filas.append(dict(fecha=r['fecha'], slug=r['slug'], tablero=C.TAB[r['tab']], tipo=r['tipo'], titulo_40='',
                          descripcion='', url_imagen='', url_destino_con_utm=r['url'], estado='producido_otro_agente', segmento=r['seg'],
                          dia=dia(r['fecha']), hora_cdmx=r['hora'], bloque=r['bloque'],
                          publish_date_utc=utc(r['fecha'], r['hora']), origen='serie de otro agente',
                          nota='Lo llena el agente de ' + ('videos (VIDEO_pines.md)' if r['tipo'] == 'video' else 'carruseles (CARRUSEL_pines.md)') + '; fecha, hora y tablero fijados por ese archivo. No va en estos CSV de carga.'))
    filas.sort(key=lambda r: r['publish_date_utc'])
    for r in filas:
        for k in ('impresiones_7d', 'guardados_7d', 'clics_7d'):
            r.setdefault(k, '')
    escribir_csv(os.path.join(SALIDA_CSV, 'CALENDARIO_pines.csv'), cols_cal, filas)

    # Detalle por pin (audiencia y bloque), útil para el reporte semanal.
    det = []
    for grupo, tipo in ((C.PINES, 'imagen'), (C.SEMILLAS, 'imagen_semilla')):
        for p in grupo:
            det.append(dict(slug=p['slug'], tipo=tipo, segmento=p['seg'], bloque=p['bloque'], fecha=p['fecha'],
                            hora_cdmx=p['hora'], tablero=C.TAB[p['tab']], utm_campaign=p['camp'],
                            destino=BASE + p['destino'], titulo=p['titulo']))
    escribir_csv(os.path.join(SALIDA_CSV, 'PINES_crecimiento_detalle.csv'), list(det[0].keys()), det)
    print('CSV listos en', SALIDA_CSV)


if __name__ == '__main__':
    pasos = sys.argv[1:] or ['csv', 'imagenes']
    if 'csv' in pasos:
        construir_csv()
    if 'imagenes' in pasos:
        construir_imagenes()
