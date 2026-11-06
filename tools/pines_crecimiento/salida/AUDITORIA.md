# Auditoría del hilo B2 (pines de zona y de material, CSV de carga y calendario)

Revisión del 6 de noviembre de 2026, 06:10 UTC, hecha con `tools/pines_crecimiento/auditar.py` sobre la carpeta de la bóveda. El script sale con código 1 ante cualquier error.

## Resultado

```
OK    Combinaciones previas cargadas para el cruce: 53
OK    Filas de carga revisadas: 32
OK    Imágenes revisadas (1000 x 1500, <300 KB): 32
OK    Calendario: 55 filas, máximo 4 por día
OK    Entregables de texto revisados contra 41 términos vetados: 7

Resultado: 0 errores, 0 avisos
```

## Qué se revisó

1. Columnas exactas del CSV de Pinterest (Title, Media URL, Pinterest board, Thumbnail, Description, Link, Publish date, Keywords), título de 100 caracteres o menos y descripción de 500 o menos.
2. Palabra clave dentro de los primeros 40 caracteres del título.
3. Fechas en formato ISO, en UTC, entre el 8 de noviembre y el 7 de diciembre a las 06:00.
4. Ninguna hora repetida dentro del calendario. Ninguna hora choca con los 15 pines ya programados ni con las 8 casillas de video y carrusel.
5. Enlaces solo a sayeghstudio.com, a rutas que están en el sitemap o a /auditoria.
6. UTM en cada fila: utm_source=pinterest, utm_medium=organic_pin, una de las cuatro campañas permitidas y utm_content igual al slug.
7. /auditoria aparece si y solo si la campaña es conversion_auditoria. Hay un pin de Auditoría por semana.
8. Slug e imagen únicos. Ninguna combinación de imagen y enlace repite el CSV descartado de 47 pines, los 6 de conversión ni los feeds RSS.
9. Tableros con el nombre exacto del contrato.
10. Ninguna fuente de terceros: ni AVIVIA, ni Piedras Chinas, ni Temixco, ni Taller 18.
11. Cada pin con render lleva la leyenda "Render conceptual de Sayegh Studio. No corresponde a una obra entregada." en la imagen y en la descripción.
12. Imágenes de 1000 x 1500 y menos de 300 KB. La copia de la bóveda es idéntica píxel por píxel.
13. Calendario con las columnas del contrato, más segmento, día, hora_cdmx y bloque. 7 pines frescos por semana en las 4 semanas.
14. Lista de exclusión del §6.5 y palabras vetadas del encargo en los 7 entregables de texto. "0 %" solo cuenta como cifra suelta, no dentro de "30 %".

## Cambios de la última vuelta

- Las 8 casillas de video y carrusel quedaron con la fecha, la hora, el tablero y el enlace de VIDEO_pines.md y CARRUSEL_pines.md. Este hilo no escribe esos dos archivos.
- Cuatro pines propios cambiaron de casilla para no chocar con los carruseles:
  - zona-polanco-01 pasa al jueves 19-nov a las 20:30.
  - obra-nuvana-01 pasa al jueves 26-nov a las 20:30 y cambia al público A.
  - material-tadelakt-01 pasa al jueves 3-dic a las 20:30.
  - zona-coyoacan-01 pasa al domingo 6-dic a las 19:30.
- Ajuste de tableros para llegar a 20:
  - zona-bosque-real-01 pasa a Obra Gris, porque su texto trata del corte y el movimiento de tierras.
  - conv-07-cocina pasa a Travertino, y su texto ahora nombra la piedra. No cambió ni su fecha ni su hora.
- La bóveda agrega un manifiesto C2PA (segmento APP11, unos 5.7 KB) a cada JPG al guardarlo. Por eso la auditoría compara píxeles y no bytes. [Certeza, revisado en zona-bosques-01.jpg] Pinterest toma la imagen del sitio, no de la bóveda.

## Conteo de tableros al 6 de diciembre

Este conteo suma la base, los pines de este hilo, las series de los otros agentes y los pines de conversión ya programados. No incluye los otros 9 programados, cuyo tablero no se conoce.

| Tablero | Total | Desglose |
|---|---|---|
| Travertino | 20 | 12 + 5 + 2 + 1 |
| Obra Gris | 20 | 17 + 3 |
| Presupuesto | 25 | 16 + 5 + 3 + 1 |
| Acabados | 23 | 19 + 4 |

[Certeza, contado]

## Lo que queda abierto

- [Probable fuerte] Pinterest lee la columna Publish date en UTC. Si la leyera en hora de la cuenta, todos los pines se publicarían 6 horas tarde.
- [Certeza] El CSV solo se puede subir después de que se fusione el PR. Antes de eso, las Media URL de /assets/pinterest/crecimiento/ no existen en el sitio.
- [Suposición] Los tableros de cocinas y de baños se abren solo si la búsqueda los valida. Sus 12 semillas van en PINES_tableros_nuevos_carga.csv, con estado condicionado.
- [Certeza] material-tadelakt-01 enlaza a un artículo de baños tipo spa que no menciona el tadelakt. Por eso la descripción no promete que lo haga.
