#!/usr/bin/env python3
"""
Genera los documentos legibles a partir de contenido.py:
  CALENDARIO_30_dias.md y .csv (7-nov a 6-dic de 2026, día por día)
Uso: python3 tools/pines_crecimiento/documentos.py <carpeta_salida>
"""
import csv
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contenido as C  # noqa: E402
from construir import utc, enlace, MEDIA_BASE  # noqa: E402

DIAS = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
MESES = {11: 'nov', 12: 'dic'}
INICIO, FIN = dt.date(2026, 11, 7), dt.date(2026, 12, 6)


def objetivo(p, tipo):
    if p['bloque'] == 'conversion':
        return 'lead'
    if tipo in ('carrusel', 'video'):
        return 'guardado y seguidor'
    if p['seg'] == 'B':
        return 'clic'
    return 'guardado'


def eventos():
    ev = []
    for f, slug, tab, tit in C.YA_PROGRAMADOS_CONVERSION:
        ev.append(dict(fecha=f, hora='10:30', utc=f'{f}T16:30', tipo='conversión (ya programado)', slug=slug,
                       tablero=tab, seg='A+B', bloque='conversion', obj='lead', quien='automático',
                       nota=tit + '. Enlace a via.sayeghstudio.com con UTM.'))
    for u in C.YA_PROGRAMADOS_OTROS_UTC:
        d = dt.datetime.strptime(u, '%Y-%m-%dT%H:%M') - dt.timedelta(hours=6)
        ev.append(dict(fecha=d.strftime('%Y-%m-%d'), hora=d.strftime('%H:%M'), utc=u, tipo='ya programado (otro hilo)',
                       slug='', tablero='', seg='', bloque='', obj='', quien='automático',
                       nota='Pin ya programado en la cuenta; contenido no informado a este hilo.'))
    for p in C.PINES:
        ev.append(dict(fecha=p['fecha'], hora=p['hora'], utc=utc(p['fecha'], p['hora'])[:16],
                       tipo='conversión (CSV nuevo)' if p['bloque'] == 'conversion' else 'imagen (CSV nuevo)',
                       slug=p['slug'], tablero=C.TAB[p['tab']], seg=p['seg'], bloque=p['bloque'],
                       obj=objetivo(p, 'imagen'), quien='automático (CSV)', nota=p['t40']))
    for p in C.SEMILLAS:
        ev.append(dict(fecha=p['fecha'], hora=p['hora'], utc=utc(p['fecha'], p['hora'])[:16],
                       tipo='semilla tablero nuevo (CSV aparte, condicionado)', slug=p['slug'], tablero=C.TAB[p['tab']],
                       seg=p['seg'], bloque=p['bloque'], obj='guardado y seguidor', quien='automático tras crear tablero',
                       nota=p['t40'] + '. Solo si el tablero ya existe; si no, se recorre la fecha.'))
    for r in C.RESERVAS:
        ev.append(dict(fecha=r['fecha'], hora=r['hora'], utc=utc(r['fecha'], r['hora'])[:16],
                       tipo=('video' if r['tipo'] == 'video' else 'carrusel') + ' (serie de otro agente)', slug=r['slug'],
                       tablero=C.TAB[r['tab']], seg=r['seg'], bloque=r['bloque'], obj='guardado y seguidor',
                       quien='Jacobo o sesión en la Mac (lo produce otro agente)',
                       nota='Ver ' + ('VIDEO_pines.md' if r['tipo'] == 'video' else 'CARRUSEL_pines.md') + '; fecha, hora y tablero fijados ahí.'))
    def manual(f, h, nota, quien='Jacobo', obj=''):
        ev.append(dict(fecha=f, hora=h, utc='', tipo='acción manual', slug='', tablero='', seg='', bloque='',
                       obj=obj, quien=quien, nota=nota))

    manual('2026-11-07', '09:00', 'Revisar en Pinterest > Programados que los 6 de conversión salgan a las 10:30 CDMX.', 'sesión en la Mac')
    manual('2026-11-07', '11:00', 'Fusionar el PR de imágenes de crecimiento y comprobar que una Media URL abre (p. ej. zona-bosques-01.jpg).', 'coordinador')
    manual('2026-11-07', '12:00', 'Cargar PINES_crecimiento_carga.csv (20 pines) en Pinterest > Crear > Importar contenido. No subir el CSV de 47.', 'sesión en la Mac')
    manual('2026-11-08', '12:00', 'Validar en el buscador de Pinterest las palabras de los dos tableros nuevos (TABLEROS_nuevos.md, sección 3). Si pasan, crear los tableros y cargar PINES_tableros_nuevos_carga.csv.', 'Jacobo')
    for f in ('2026-11-09', '2026-11-16', '2026-11-23', '2026-11-30'):
        manual(f, '09:00', 'Reporte semanal: llenar impresiones_7d, guardados_7d y clics_7d en CALENDARIO_pines.csv y una fila en METRICAS_semanales.csv.', 'hilo B', 'medición')
        manual(f, '18:00', 'Responder comentarios de la semana y mover a su tablero correcto los pines que Instagram dejó en Remodelación (máx. 4 ediciones por hora).', 'Jacobo', 'seguidor')
        manual(f, '18:30', 'Guardar 1 o 2 pines propios en el tablero que más lo necesite (repines; tope 30 % de lo publicado en la semana).', 'Jacobo', 'seguidor')
        manual(f, '19:00', 'Revisar si los feeds RSS pinearon páginas nuevas del sitio; si una página nueva no aparece en 48 h, avisar al hilo A (vigilante).', 'hilo B')
    manual('2026-11-21', '09:00', 'Revisión del día 21: si los clics salientes de 30 días son menos de 8, rediseñar los pines de conversión (titular y foto) antes de subir frecuencia. Si son 8 o más, mantener 7 por semana.', 'hilo B con Fable 5.1', 'clic')
    manual('2026-12-06', '20:00', 'Cierre de 30 días: comparar contra metas del 7-dic (20 clics, 25 guardados, 15 seguidores) y proponer el ritmo de enero.', 'hilo B', 'medición')
    for r in C.RESERVAS:
        h = (dt.datetime.strptime(r['hora'], '%H:%M') - dt.timedelta(minutes=30)).strftime('%H:%M')
        manual(r['fecha'], h, f'Programar a mano {r["slug"]} (sale {r["hora"]}).', 'Jacobo o sesión en la Mac')
    ev.sort(key=lambda e: (e['fecha'], e['hora']))
    return ev


def fecha_larga(f):
    d = dt.date.fromisoformat(f)
    return f'{DIAS[d.weekday()]} {d.day} {MESES[d.month]}'


def calendario(carpeta):
    ev = eventos()
    publicaciones = {}
    for e in ev:
        if e['tipo'] != 'acción manual':
            publicaciones[e['fecha']] = publicaciones.get(e['fecha'], 0) + 1
    assert max(publicaciones.values()) <= 25

    cols = ['fecha', 'dia', 'hora_cdmx', 'hora_utc', 'tipo', 'slug', 'tablero', 'segmento', 'bloque', 'objetivo',
            'responsable', 'nota']
    with open(os.path.join(carpeta, 'CALENDARIO_30_dias.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for e in ev:
            d = dt.date.fromisoformat(e['fecha'])
            w.writerow([e['fecha'], DIAS[d.weekday()], e['hora'], e['utc'], e['tipo'], e['slug'], e['tablero'],
                        e['seg'], e['bloque'], e['obj'], e['quien'], e['nota']])

    L = []
    L.append('# Calendario de 30 días en Pinterest (7 de noviembre al 6 de diciembre de 2026)\n')
    L.append('Sayegh Studio. Versión legible de `CALENDARIO_30_dias.csv` y de `06_Growth_SEO_Copy/pinterest/CALENDARIO_pines.csv` '
             '(la hoja del contrato, con las columnas de §6.3 más segmento, día, hora y bloque). Horas en CDMX (UTC−6 todo el año); '
             'en el CSV de carga van en UTC.\n')
    L.append('Etiquetas: [Certeza] dato de la cuenta, del contrato o contado con código. [Probable] inferencia fuerte. [Suposición] criterio nuestro.\n')
    L.append('## Reglas que respeta\n')
    L.append('- Días y horas de §6.2 bis del contrato (versión 22:45): mujeres de 30 a 55 años (A) martes y jueves 20:30, sábado 10:00 y domingo 19:30; '
             'empresarios e inversionistas (B) martes 9:30 y jueves 13:30; conversión el miércoles 10:30. [Certeza]')
    L.append('- 7 pines frescos por semana en 4 semanas (8 al 15, 16 al 22, 23 al 29 de noviembre y 30 de noviembre al 6 de diciembre): 20 de imagen por CSV y 8 casillas fijas para 4 carruseles y 4 videos que ya produjeron y auditaron otros agentes (VIDEO_pines.md y CARRUSEL_pines.md). [Certeza, contado]')
    L.append('- Uno por semana a la Auditoría de Viabilidad: semana del 8 al 15 con los 6 de conversión (7 al 12) ya cargados; después conv-07 (18-nov), conv-08 (25-nov) y conv-09 (2-dic). [Certeza]')
    L.append(f'- Máximo de publicaciones en un día: {max(publicaciones.values())} (tope 25). [Certeza, contado]')
    L.append('- Repines: 1 o 2 por semana, nunca más del 30 % de lo publicado. [Certeza del tope; Probable del efecto]')
    L.append('- Ninguno de los 15 horarios ya ocupados se repite. Los 6 de conversión salen a las 16:30 UTC (10:30 CDMX) y los otros 9 a las 20:00 o 20:30 CDMX del día anterior. [Certeza, datos del coordinador]')
    L.append('- Los 12 pines semilla de los tableros nuevos están condicionados a que Jacobo valide la búsqueda y cree los tableros (contrato §6.4). Si no se crean, esas filas no se suben y el ritmo queda en 7 por semana. [Certeza]\n')

    semanas = [('2026-11-08', '2026-11-15'), ('2026-11-16', '2026-11-22'), ('2026-11-23', '2026-11-29'), ('2026-11-30', '2026-12-06')]
    frescos = [e for e in ev if e['tipo'].startswith(('imagen (CSV', 'conversión (CSV', 'carrusel', 'video'))]
    L.append('## Conteo por semana (pines frescos nuestros)\n')
    L.append('| Semana | Frescos | A | B | Conversión | Semillas condicionadas |')
    L.append('|---|---|---|---|---|---|')
    for a, b in semanas:
        sel = [e for e in frescos if a <= e['fecha'] <= b]
        sem = [e for e in ev if e['tipo'].startswith('semilla') and a <= e['fecha'] <= b]
        L.append(f'| {fecha_larga(a)} a {fecha_larga(b)} | {len(sel)} | {sum(e["seg"] == "A" for e in sel)} | '
                 f'{sum(e["seg"] == "B" for e in sel)} | {sum(e["bloque"] == "conversion" for e in sel)} | {len(sem)} |')
    L.append('\nLa semana 1 abarca dos domingos (8 y 15 de noviembre) porque el lunes 9 no tiene franja del contrato; las otras tres van de lunes a domingo. [Certeza, contado]\n')
    L.append('## Día por día\n')
    L.append('Objetivo: seguidor, guardado, clic o lead (prospecto). Responsable "automático" quiere decir que Pinterest lo publica solo una vez cargado.\n')
    d = INICIO
    while d <= FIN:
        f = d.isoformat()
        del_dia = [e for e in ev if e['fecha'] == f]
        L.append(f'### {fecha_larga(f).capitalize()}\n')
        if not del_dia:
            L.append('Sin publicación programada. Los feeds RSS publican solos si hay página nueva en el sitio.\n')
        else:
            L.append('| Hora | Qué sale | Tablero | Público | Objetivo | Quién |')
            L.append('|---|---|---|---|---|---|')
            for e in del_dia:
                que = e['tipo'] + (f': `{e["slug"]}`' if e['slug'] else '') + (f'. {e["nota"]}' if e['nota'] else '')
                L.append(f'| {e["hora"]} | {que} | {e["tablero"]} | {e["seg"]} | {e["obj"]} | {e["quien"]} |')
            L.append('')
        d += dt.timedelta(days=1)
    L.append('## Feeds automáticos\n')
    L.append('Los cuatro feeds RSS (feed.xml, feed-remodelacion.xml, feed-piedra.xml, feed-concreto-minimalismo.xml) ya pinearon 41 páginas el 6-nov y '
             'no se tocan: Pinterest crea un pin por cada enlace nuevo, así que publican solos solo cuando el sitio suma una página. '
             'Ningún pin de este calendario repite imagen y enlace de un feed: todas las imágenes son archivos nuevos en '
             '`/assets/pinterest/crecimiento/`. [Certeza, verificado con el script de auditoría]\n')
    with open(os.path.join(carpeta, 'CALENDARIO_30_dias.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L) + '\n')


def copy(carpeta):
    L = ['# Copy de los pines de crecimiento (zona, material, conversión y semillas)\n',
         'Sayegh Studio. Fuente única: `tools/pines_crecimiento/contenido.py` en el repo. '
         'Carga: `PINES_crecimiento_carga.csv` (20 pines, tableros existentes) y `PINES_tableros_nuevos_carga.csv` '
         '(12 semillas, solo después de crear los tableros). Horas en CDMX; en el CSV van en UTC.\n',
         'Público: A = mujeres de 30 a 55 años; B = empresarios e inversionistas de alto valor; A+B = conversión.\n',
         'Leyenda en imagen y descripción de todo render: "' + C.LEYENDA + '" Las muestras de tzalam y chukum son fotos '
         'reales de material del sitio y la foto de Nuvana es de obra; esas no llevan la leyenda y lo dicen en la descripción.\n']
    for titulo, grupo in (('Pines del CSV principal', C.PINES), ('Semillas de los tableros nuevos', C.SEMILLAS)):
        L.append(f'## {titulo}\n')
        for p in sorted(grupo, key=lambda x: (x['fecha'], x['hora'])):
            fuente = os.path.relpath(p['img']['src'], C.RAIZ)
            if fuente.startswith('..'):
                fuente = 'bóveda: ' + os.path.basename(p['img']['src'])
            L.append(f'### {p["slug"]}\n')
            L.append(f'- {fecha_larga(p["fecha"]).capitalize()}, {p["hora"]} CDMX ({utc(p["fecha"], p["hora"])} UTC) · público {p["seg"]} · bloque {p["bloque"]} · tablero {C.TAB[p["tab"]]}')
            L.append(f'- Título ({len(p["titulo"])} car.): {p["titulo"]}')
            L.append(f'- Título corto ({len(p["t40"])} car.): {p["t40"]}')
            L.append(f'- Texto en la imagen: {p["kicker"]} / {p["titular"]} / {p["apoyo"]}')
            L.append(f'- Imagen: `{MEDIA_BASE}{p["slug"]}.jpg` (base: {fuente})')
            L.append(f'- Enlace: {enlace(p["destino"], p["camp"], p["slug"])}')
            L.append(f'- Palabras clave: {p["kw"]}')
            L.append(f'- Descripción ({len(p["desc"])} car.): {p["desc"]}\n')
    with open(os.path.join(carpeta, 'PINES_crecimiento_copy.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L) + '\n')


if __name__ == '__main__':
    destino = sys.argv[1]
    os.makedirs(destino, exist_ok=True)
    calendario(destino)
    copy(destino)
    print('Documentos listos en', destino)
