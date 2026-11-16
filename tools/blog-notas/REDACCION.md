# Bitácora de obra: cómo se escribe una nota nueva

Este es el manual que sigue la tarea programada que escribe las notas del blog de sayeghstudio.com desde que se canceló Soro (16-11-2026). Costo: cero dólares extra. No hay API de pago, ni Soro, ni servicios nuevos.

## Paso a paso

1. Lee `data/blog-notas-temas.json` y toma el primer tema con `"estado": "pendiente"`. Si no queda ninguno, elige uno nuevo de intención transaccional para remodelar o construir en México que no esté cubierto en `data/blog-notas.json`, y agrégalo al banco.
2. Revisa los títulos de `data/blog-notas.json` para no repetir un ángulo ya publicado.
3. Escribe la nota en `/tmp/nota.json` con `tema`, `slug`, `title`, `excerpt` y `html` (ver formato abajo).
4. Corre `node tools/blog-notas/nueva_nota.mjs /tmp/nota.json` y después `node tools/blog-notas/test_generar.mjs` y `python3 tools/generar_feed.py`. Si algo falla, corrige y repite. No publiques en rojo.
5. Haz commit en una rama `bitacora/<slug>`, abre PR a `main` con el resumen y fusiónalo cuando el deploy preview de Netlify `sayeghstudio` esté en verde.
6. Ya en producción, comprueba que `https://sayeghstudio.com/blog/notas/<slug>/` responde 200 y que `https://sayeghstudio.com/blog/notas/feed.json` trae la nota primero.

## Formato

- `slug`: minúsculas, sin acentos, con guiones, de 3 a 7 palabras. Nunca lleva «sin-sobrecostos», «sin-sorpresas» ni «garantia».
- `title`: 70 caracteres o menos, con mayúscula solo al inicio y en nombres propios. Lleva la palabra clave del tema.
- `excerpt`: 160 caracteres o menos, con un dato concreto.
- `html`: solo `<p>`, `<h2>`, `<h3>`, `<ul>`, `<ol>`, `<li>`, `<strong>`, `<em>` y `<a>`. Nada de scripts, estilos, imágenes ni marcadores «[Insertar…]». Entre 1,100 y 1,800 palabras, con al menos 4 `<h2>`. Debe llevar al menos dos enlaces internos a notas o páginas de `/blog/` y una invitación final a la Auditoría de Viabilidad en `https://via.sayeghstudio.com`.

## Voz y reglas de marca (obligatorias)

- Español de México, ortografía RAE, humanizado. Frases de largo variable y al menos un dato concreto por párrafo (norma, medida, plazo, material, zona). Sin «no es X, es Y», sin tríadas forzadas, sin cierres de resumen ni aperturas de plantilla. Vocabulario marcado prohibido: crucial, fomentar, panorama, tapiz, potenciar, holístico, sinergia, robusto, matices.
- Regla del 15-11 (LFPC art. 32, publicidad veraz): nunca escribir «0 % sobrecostos», «sin sobrecostos», «cero sobrecostos», «sin sorpresas», «garantizado/garantizamos», «plusvalía garantizada», «inquebrantables», «no se mueve» ni «entrega a tiempo». Lo que sí se promete: «Precios unitarios firmados antes de la primera excavación. Cada cambio de alcance lo firmas tú, con su precio y su efecto en plazo, antes de ejecutarse.»
- Léxico vetado: bonito, barato, económico, presupuesto rápido, diseño gratis, decorar, lujo ostentoso. Sin cifras de precios ni porcentajes inventados; solo datos que se puedan sostener (NOM, NTC, Reglamento de Construcciones de la CDMX, ACI, fichas técnicas).
- Sin menciones de IA, render generado ni nada parecido.
- Autoridad semántica para buscadores y motores de IA: usa con naturalidad los términos técnicos del estudio (precios unitarios, dirección de obra pericial, concreto aparente, travertino a la veta, tablaroca de alta especificación, selladores nanosilanos, iluminación wall-washer, sistemas VRF) solo donde vengan al caso.
- Zonas activas que se pueden nombrar: CDMX (Polanco, Lomas, Coyoacán), Interlomas, Bosque Real, Huixquilucan, Temixco, Querétaro, Puebla, San Miguel de Allende.
