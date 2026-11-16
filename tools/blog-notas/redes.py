#!/usr/bin/env python3
"""Portada y piezas para redes de una nota de la bitácora (costo 0, solo Pillow).

Uso:
  python3 tools/blog-notas/redes.py <slug> <imagen_base> "<título de la nota>"

<imagen_base> puede ser la imagen que devolvió el flujo «[v2] Bitácora · Portada» del pod
(fal.ai o Nano Banana Pro), una foto real de obra o una portada vieja de la bitácora.
Genera, sin metadatos (ni EXIF ni C2PA) y sin rótulos:
  assets/images/blog-notas/<slug>.webp                1440x960  portada del sitio
  assets/images/blog-notas/redes/<slug>-og.jpg        1200x630  vista previa de Facebook
  assets/images/blog-notas/redes/<slug>-historia.jpg  1080x1920 historia de Instagram con título
  assets/images/blog-notas/redes/<slug>-gbp.jpg       1200x900  Google Business, sin texto
"""
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FUENTES = os.path.join(os.path.dirname(__file__), "fuentes")
CARBON, BLANCO, ORO, GRIS, ARENA = "#1A1A1A", "#FAFAFA", "#E5B962", "#8A8D8F", "#D1C7B3"
VETADAS = re.compile(r"\b(ia|render|generad[oa]|inteligencia artificial)\b", re.I)


def fuente(peso, tam):
    return ImageFont.truetype(os.path.join(FUENTES, f"inter-tight-latin-{peso}-normal.ttf"), tam)


def recorte(img, w, h):
    return ImageOps.fit(img, (w, h), Image.LANCZOS, centering=(0.5, 0.5))


def espaciado(draw, xy, texto, fnt, color, track):
    x, y = xy
    for ch in texto:
        draw.text((x, y), ch, font=fnt, fill=color)
        x += draw.textlength(ch, font=fnt) + track
    return x


def lineas(draw, texto, fnt, ancho):
    out, cur = [], ""
    for p in texto.split():
        prueba = (cur + " " + p).strip()
        if draw.textlength(prueba, font=fnt) <= ancho:
            cur = prueba
        else:
            if cur:
                out.append(cur)
            cur = p
    if cur:
        out.append(cur)
    return out


def historia(base, titulo):
    W, H = 1080, 1920
    lienzo = Image.new("RGB", (W, H), CARBON)
    foto = recorte(base, W, 1180)
    lienzo.paste(foto, (0, 0))
    # Degradado de la foto al carbón (sin rebote ni brillo).
    grad = Image.new("L", (1, 460))
    for y in range(460):
        grad.putpixel((0, y), int(255 * (y / 459) ** 1.4))
    grad = grad.resize((W, 460))
    lienzo.paste(Image.new("RGB", (W, 460), CARBON), (0, 1180 - 460), grad)
    d = ImageDraw.Draw(lienzo)
    x0, ancho = 84, W - 168
    # Zona segura de Instagram: 250 px arriba y abajo libres de texto.
    tam = 78
    while True:
        ft = fuente(700, tam)
        ls = lineas(d, titulo, ft, ancho)
        if len(ls) <= 4 or tam <= 54:
            break
        tam -= 4
    alto_t = len(ls) * int(tam * 1.12)
    y = 1600 - alto_t - 120
    espaciado(d, (x0, y - 70), "BITÁCORA DE OBRA", fuente(500, 30), ORO, 30 * 0.08)
    for l in ls:
        d.text((x0, y), l, font=ft, fill=BLANCO)
        y += int(tam * 1.12)
    d.line((x0, y + 28, x0 + 96, y + 28), fill=ORO, width=3)
    d.text((x0, y + 56), "Nota completa en sayeghstudio.com/blog", font=fuente(500, 36), fill=ARENA)
    espaciado(d, (x0, 1625), "SAYEGH  ·  S T U D I O", fuente(500, 26), GRIS, 26 * 0.08)
    return lienzo


def guardar(img, ruta, fmt, **kw):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    limpia = Image.new("RGB", img.size)
    limpia.paste(img.convert("RGB"))  # copia sin metadatos
    limpia.save(ruta, fmt, **kw)
    return ruta


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    slug, base_p, titulo = sys.argv[1], sys.argv[2], " ".join(sys.argv[3].split())
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        sys.exit(f"slug inválido: {slug}")
    if VETADAS.search(titulo):
        sys.exit("El título lleva una palabra vetada en piezas públicas (IA, render, generado).")
    base = ImageOps.exif_transpose(Image.open(base_p)).convert("RGB")
    if min(base.size) < 600:
        sys.exit(f"Imagen base muy chica: {base.size}")
    img_dir = os.path.join(RAIZ, "assets/images/blog-notas")
    salidas = [
        guardar(recorte(base, 1440, 960), os.path.join(img_dir, f"{slug}.webp"), "WEBP", quality=82, method=6),
        guardar(recorte(base, 1200, 630), os.path.join(img_dir, "redes", f"{slug}-og.jpg"), "JPEG", quality=86, optimize=True, progressive=True),
        guardar(historia(base, titulo), os.path.join(img_dir, "redes", f"{slug}-historia.jpg"), "JPEG", quality=88, optimize=True),
        guardar(recorte(base, 1200, 900), os.path.join(img_dir, "redes", f"{slug}-gbp.jpg"), "JPEG", quality=86, optimize=True),
    ]
    for s in salidas:
        print(os.path.relpath(s, RAIZ), f"{os.path.getsize(s) // 1024} KB")


if __name__ == "__main__":
    main()
