#!/usr/bin/env python3
"""Genera los feeds RSS 2.0 de Sayegh Studio para "Importar contenido > RSS" de Pinterest.

Solo librería estándar. Uso (desde la raíz del repo o desde cualquier lado):
    python3 tools/generar_feed.py

Lee sitemap.xml, abre el index.html local de cada URL y escribe:
    feed.xml                       (todo)
    feed-<grupo>.xml               (uno por tablero, ver FEEDS_POR_TABLERO)

Sale con código 1 si alguna entrada no tiene título, descripción, imagen o fecha,
si contiene una frase prohibida, o si algún XML generado no parsea.
"""

import email.utils
import html
import json
import os
import re
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from urllib.parse import urlparse

# --------------------------------------------------------------------------
# Configuración editable
# --------------------------------------------------------------------------

SITIO = "https://sayeghstudio.com"
TITULO_CANAL = "Sayegh Studio"
DESCRIPCION_CANAL = ("Arquitectura, remodelación y diseño de interiores de lujo en "
                     "Ciudad de México, Estado de México, Querétaro y Guanajuato.")
IDIOMA = "es-MX"
MAX_TITULO = 100

# Mapeo de feeds por tablero de Pinterest.
# Cada feed tiene una lista de reglas; una página entra si su ruta (p. ej.
# "/blog/materiales/travertino-arquitectura-lujo/") empieza con algún "prefijo"
# y, si la regla trae "slugs_con", el último segmento contiene alguna de esas
# palabras. "excepto_slugs_con" quita las páginas cuyo slug contenga esas palabras.
FEEDS_POR_TABLERO = {
    "feed-remodelacion.xml": {
        "titulo": "Sayegh Studio · Remodelación de lujo",
        "reglas": [
            {"prefijo": "/zonas-landing/"},
            {"prefijo": "/blog/zonas/"},
            {"prefijo": "/blog/proceso/"},
            {"prefijo": "/blog/inversion/"},
            {"prefijo": "/blog/estrategia/"},
        ],
    },
    "feed-piedra.xml": {
        "titulo": "Sayegh Studio · Piedra natural",
        "reglas": [
            {"prefijo": "/blog/materiales/",
             "slugs_con": ["travertino", "marmol", "piedra", "nanosilano"]},
        ],
    },
    "feed-concreto-minimalismo.xml": {
        "titulo": "Sayegh Studio · Concreto y minimalismo",
        "reglas": [
            # Resto de materiales: concreto, maderas, metales, vidrio...
            {"prefijo": "/blog/materiales/",
             "excepto_slugs_con": ["travertino", "marmol", "piedra", "nanosilano"]},
            {"prefijo": "/blog/tendencias/"},
        ],
    },
}

# Etiqueta <category> según la sección de la URL.
CATEGORIAS = {
    "/zonas-landing/": "Zonas",
    "/blog/zonas/": "Zonas",
    "/blog/materiales/": "Materiales",
    "/blog/tendencias/": "Tendencias",
    "/blog/proceso/": "Proceso",
    "/blog/inversion/": "Inversión",
    "/blog/estrategia/": "Estrategia",
    "/guia/": "Guías",
}

# Rutas excluidas siempre (portada, índices, legales, aliados).
EXCLUIR_EXACTAS = {"/", "/blog/", "/privacidad/", "/aliados/"}
EXCLUIR_PREFIJOS = ("/privacidad/", "/aliados/")
# Índices de categoría del blog: /blog/<cat>/ (dos segmentos exactos).
RE_INDICE_BLOG = re.compile(r"^/blog/[^/]+/$")
# Páginas que solo entran si tienen og:image.
EXCLUIR_SI_SIN_OG_IMAGE = {"/guia/"}

# Frases que Pinterest/la marca no permiten en título o descripción.
# Se comparan en minúsculas y sin acentos (así "económico" atrapa "economico").
FRASES_PROHIBIDAS = [
    "gratis", "gratuita", "gratuito", "0% sobrecostos", "sin sobrecostos",
    "garantizad", "barato", "económico",
]

# --------------------------------------------------------------------------

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NS_SITEMAP = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
NS_MEDIA = "http://search.yahoo.com/mrss/"
NS_ATOM = "http://www.w3.org/2005/Atom"
TIPOS_IMAGEN = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}

avisos = []
errores = []


def avisar(msg):
    avisos.append(msg)
    print("AVISO: " + msg, file=sys.stderr)


def error(msg):
    errores.append(msg)
    print("ERROR: " + msg, file=sys.stderr)


def sin_acentos(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto)
                   if unicodedata.category(c) != "Mn").lower()


class ExtractorHead(HTMLParser):
    """Extrae <title>, metas y bloques JSON-LD sin depender del orden de atributos."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.titulo = None
        self.metas = {}
        self.jsonld = []
        self._en_title = False
        self._en_jsonld = False
        self._buf = []

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "title" and self.titulo is None:
            self._en_title, self._buf = True, []
        elif tag == "meta":
            clave = (a.get("property") or a.get("name") or "").strip().lower()
            if clave and "content" in a and clave not in self.metas:
                self.metas[clave] = a["content"].strip()
        elif tag == "script" and a.get("type", "").strip().lower() == "application/ld+json":
            self._en_jsonld, self._buf = True, []

    def handle_endtag(self, tag):
        if tag == "title" and self._en_title:
            self.titulo = " ".join("".join(self._buf).split())
            self._en_title = False
        elif tag == "script" and self._en_jsonld:
            self.jsonld.append("".join(self._buf))
            self._en_jsonld = False

    def handle_data(self, data):
        if self._en_title or self._en_jsonld:
            self._buf.append(data)


def nodos_jsonld(bloques):
    """Aplana bloques JSON-LD (listas y @graph) en una lista de dicts."""
    pila, salida = [], []
    for b in bloques:
        try:
            pila.append(json.loads(b))
        except ValueError:
            continue
    while pila:
        n = pila.pop(0)
        if isinstance(n, list):
            pila.extend(n)
        elif isinstance(n, dict):
            salida.append(n)
            if "@graph" in n:
                pila.append(n["@graph"])
    return salida


def parsear_fecha(valor):
    if not valor:
        return None
    valor = valor.strip()
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", valor):
            d = datetime.strptime(valor, "%Y-%m-%d")
        else:
            d = datetime.fromisoformat(valor.replace("Z", "+00:00"))
    except ValueError:
        return None
    if d.tzinfo is None:
        # Fecha sin zona: se toma mediodía en Ciudad de México (UTC-6).
        if d.hour == 0 and d.minute == 0 and d.second == 0:
            d = d.replace(hour=12)
        d = d.replace(tzinfo=timezone(timedelta(hours=-6)))
    return d


def fecha_jsonld(nodos):
    """datePublished del nodo principal (Article/BlogPosting/WebPage...); si no, dateModified."""
    preferidos = ("BlogPosting", "Article", "NewsArticle", "TechArticle", "HowTo",
                  "WebPage", "CollectionPage")

    def tipos(n):
        t = n.get("@type", [])
        return t if isinstance(t, list) else [t]

    ordenados = sorted(nodos, key=lambda n: min(
        [preferidos.index(t) for t in tipos(n) if t in preferidos] or [99]))
    for campo in ("datePublished", "dateModified"):
        for n in ordenados:
            f = parsear_fecha(n.get(campo) if isinstance(n.get(campo), str) else None)
            if f:
                return f, "JSON-LD " + campo
    return None, None


def fecha_git(ruta_rel):
    try:
        r = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%aI", "--", ruta_rel],
            cwd=RAIZ, capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    lineas = [l for l in r.stdout.split("\n") if l.strip()]
    return parsear_fecha(lineas[-1]) if lineas else None


def recortar_titulo(t):
    if len(t) <= MAX_TITULO:
        return t
    corte = t[:MAX_TITULO - 1]
    if " " in corte:
        corte = corte[:corte.rfind(" ")]
    return corte.rstrip(" ,;:·|-–—") + "…"


def resolver_imagen(url_img, ruta_pag):
    """Devuelve (url_absoluta, ruta_local, mime) o None con aviso."""
    u = urlparse(url_img)
    if u.netloc and u.netloc.lower() not in ("sayeghstudio.com", "www.sayeghstudio.com"):
        avisar(f"{ruta_pag}: og:image fuera del dominio ({url_img}); se omite la página")
        return None
    ruta_url = u.path
    base, ext = os.path.splitext(ruta_url)
    ext = ext.lower()
    if ext == ".webp":
        hermano = None
        for e in (".jpg", ".jpeg", ".png"):
            if os.path.isfile(os.path.join(RAIZ, (base + e).lstrip("/"))):
                hermano = base + e
                break
        if not hermano:
            avisar(f"{ruta_pag}: og:image es .webp sin .jpg hermano ({ruta_url}); se omite la página")
            return None
        ruta_url, ext = hermano, os.path.splitext(hermano)[1].lower()
    if ext not in TIPOS_IMAGEN:
        avisar(f"{ruta_pag}: og:image con formato no aceptado por Pinterest ({ruta_url}); se omite la página")
        return None
    local = os.path.join(RAIZ, ruta_url.lstrip("/"))
    if not os.path.isfile(local):
        avisar(f"{ruta_pag}: la imagen {ruta_url} no existe en el repo; se omite la página")
        return None
    return SITIO + ruta_url, local, TIPOS_IMAGEN[ext]


def excluida(ruta):
    return (ruta in EXCLUIR_EXACTAS or ruta.startswith(EXCLUIR_PREFIJOS)
            or bool(RE_INDICE_BLOG.match(ruta)))


def categoria(ruta):
    for pref, nombre in CATEGORIAS.items():
        if ruta.startswith(pref):
            return nombre
    return "Arquitectura"


def en_feed(ruta, reglas):
    slug = ruta.rstrip("/").rsplit("/", 1)[-1]
    for r in reglas:
        if not ruta.startswith(r["prefijo"]):
            continue
        if "slugs_con" in r and not any(p in slug for p in r["slugs_con"]):
            continue
        if any(p in slug for p in r.get("excepto_slugs_con", [])):
            continue
        return True
    return False


def leer_sitemap():
    arbol = ET.parse(os.path.join(RAIZ, "sitemap.xml"))
    for url in arbol.getroot().findall("sm:url", NS_SITEMAP):
        loc = (url.findtext("sm:loc", default="", namespaces=NS_SITEMAP) or "").strip()
        lastmod = (url.findtext("sm:lastmod", default="", namespaces=NS_SITEMAP) or "").strip()
        if loc:
            yield loc, lastmod


def construir_entrada(loc, lastmod):
    ruta = urlparse(loc).path or "/"
    if not ruta.endswith("/"):
        ruta += "/"
    if excluida(ruta):
        return None
    rel = (ruta.lstrip("/") + "index.html")
    archivo = os.path.join(RAIZ, rel)
    if not os.path.isfile(archivo):
        avisar(f"{ruta}: no existe {rel}; se omite la página")
        return None
    with open(archivo, encoding="utf-8") as fh:
        p = ExtractorHead()
        p.feed(fh.read())

    og_img = p.metas.get("og:image", "")
    if ruta in EXCLUIR_SI_SIN_OG_IMAGE and not og_img:
        avisar(f"{ruta}: sin og:image; excluida por regla")
        return None

    titulo = html.unescape(p.metas.get("og:title") or p.titulo or "").strip()
    desc = html.unescape(p.metas.get("og:description") or p.metas.get("description") or "").strip()
    desc = " ".join(desc.split())
    titulo = " ".join(titulo.split())

    ok = True
    if not titulo:
        error(f"{ruta}: entrada sin título"); ok = False
    if not desc:
        error(f"{ruta}: entrada sin descripción"); ok = False
    # Se revisan todas las variantes (título, og:title, description, og:description),
    # no solo la que termina en el feed.
    candidatos = (("<title>", p.titulo), ("og:title", p.metas.get("og:title")),
                  ("meta description", p.metas.get("description")),
                  ("og:description", p.metas.get("og:description")))
    for campo, texto in candidatos:
        if not texto:
            continue
        texto = html.unescape(texto)
        norm = sin_acentos(texto)
        for frase in FRASES_PROHIBIDAS:
            if sin_acentos(frase) in norm:
                error(f"{ruta}: frase prohibida «{frase}» en {campo}: {texto!r}"); ok = False

    imagen = None
    if not og_img:
        error(f"{ruta}: entrada sin imagen (og:image)"); ok = False
    else:
        imagen = resolver_imagen(og_img, ruta)
        if imagen is None:
            return None  # omitida con aviso (webp sin jpg, externa, inexistente)

    fecha, origen = fecha_jsonld(nodos_jsonld(p.jsonld))
    if not fecha and lastmod:
        fecha, origen = parsear_fecha(lastmod), "sitemap lastmod"
    if not fecha:
        fecha, origen = fecha_git(rel), "git (primer commit)"
    if not fecha:
        avisar(f"{ruta}: sin fecha (JSON-LD, lastmod ni git); se omite la página")
        return None
    if not ok:
        return None

    if len(titulo) > MAX_TITULO:
        nuevo = recortar_titulo(titulo)
        avisar(f"{ruta}: título de {len(titulo)} caracteres recortado a {len(nuevo)}")
        titulo = nuevo

    return {
        "ruta": ruta,
        "link": SITIO + ruta,
        "titulo": titulo,
        "descripcion": desc,
        "categoria": categoria(ruta),
        "fecha": fecha,
        "origen_fecha": origen,
        "img_url": imagen[0],
        "img_len": os.path.getsize(imagen[1]),
        "img_tipo": imagen[2],
    }


def rss(nombre_archivo, titulo_canal, entradas):
    ET.register_namespace("media", NS_MEDIA)
    ET.register_namespace("atom", NS_ATOM)
    raiz = ET.Element("rss", {"version": "2.0"})
    canal = ET.SubElement(raiz, "channel")
    ET.SubElement(canal, "title").text = titulo_canal
    ET.SubElement(canal, "link").text = SITIO + "/"
    ET.SubElement(canal, "description").text = DESCRIPCION_CANAL
    ET.SubElement(canal, "language").text = IDIOMA
    ET.SubElement(canal, f"{{{NS_ATOM}}}link", {
        "href": f"{SITIO}/{nombre_archivo}", "rel": "self", "type": "application/rss+xml"})
    if entradas:
        # Determinista: la fecha del canal es la de la entrada más reciente.
        ET.SubElement(canal, "lastBuildDate").text = email.utils.format_datetime(entradas[0]["fecha"])
    for e in entradas:
        it = ET.SubElement(canal, "item")
        ET.SubElement(it, "title").text = e["titulo"]
        ET.SubElement(it, "link").text = e["link"]
        ET.SubElement(it, "guid", {"isPermaLink": "true"}).text = e["link"]
        ET.SubElement(it, "pubDate").text = email.utils.format_datetime(e["fecha"])
        ET.SubElement(it, "description").text = e["descripcion"]
        ET.SubElement(it, "category").text = e["categoria"]
        ET.SubElement(it, "enclosure", {
            "url": e["img_url"], "type": e["img_tipo"], "length": str(e["img_len"])})
        ET.SubElement(it, f"{{{NS_MEDIA}}}content", {
            "url": e["img_url"], "type": e["img_tipo"], "medium": "image",
            "fileSize": str(e["img_len"])})
    ET.indent(raiz, space="  ")
    datos = b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(raiz, encoding="utf-8") + b"\n"
    destino = os.path.join(RAIZ, nombre_archivo)
    with open(destino, "wb") as fh:
        fh.write(datos)
    try:
        ET.parse(destino)
    except ET.ParseError as ex:
        error(f"{nombre_archivo}: el XML generado no parsea: {ex}")
    return destino


def main():
    entradas = []
    for loc, lastmod in leer_sitemap():
        e = construir_entrada(loc, lastmod)
        if e:
            entradas.append(e)
    if errores:
        print(f"\nFALLÓ: {len(errores)} error(es); no se escriben feeds.", file=sys.stderr)
        return 1
    entradas.sort(key=lambda e: (e["fecha"], e["link"]), reverse=True)

    rss("feed.xml", TITULO_CANAL, entradas)
    print(f"feed.xml: {len(entradas)} entradas")
    asignadas = set()
    for nombre, conf in FEEDS_POR_TABLERO.items():
        sub = [e for e in entradas if en_feed(e["ruta"], conf["reglas"])]
        asignadas.update(e["ruta"] for e in sub)
        rss(nombre, conf["titulo"], sub)
        print(f"{nombre}: {len(sub)} entradas")
    for e in entradas:
        if e["ruta"] not in asignadas:
            avisar(f"{e['ruta']}: solo está en feed.xml (no coincide con ningún tablero)")
    if errores:
        return 1
    print(f"OK ({len(avisos)} aviso(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
