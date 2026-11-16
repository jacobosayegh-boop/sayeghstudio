# Bitácora de obra: cómo se escribe una nota nueva

Este es el manual que sigue la tarea programada que escribe las notas del blog de sayeghstudio.com desde que se canceló Soro (16-11-2026). Corre los días nones a las 06:23 (CDMX) desde el 17-11-2026. El único gasto es la imagen base de la portada (≈0.03 USD en fal.ai, tope 20 al mes en el pod). Spec 033 del repo sayegh-fase1-automatizacion.

La difusión ya no es tarea de esta sesión: el flujo del pod «[v2] Bitácora · Difusión de notas» lee `blog/notas/feed.json` y publica la nota más nueva que trae `difusion`: historia de Instagram a las 11:15, Facebook con enlace a las 12:45 y Google Business con botón a las 16:45. Por eso la nota debe quedar en vivo antes de las 11:00. Esta sesión nunca publica en redes por su cuenta.

## Paso a paso

1. Lee `data/blog-notas-temas.json` y toma el primer tema con `"estado": "pendiente"`. Si no queda ninguno, elige uno nuevo de intención transaccional para remodelar o construir en México que no esté cubierto en `data/blog-notas.json`, y agrégalo al banco.
2. Revisa los títulos de `data/blog-notas.json` para no repetir un ángulo ya publicado.
3. Escribe la nota en `/tmp/nota.json` con `tema`, `slug`, `title`, `excerpt`, `html` y `difusion` (ver formato abajo).
4. Portada. Redacta en inglés un prompt de 1 a 3 frases que muestre un material o un detalle constructivo del tema (travertino a la veta, concreto aparente, junta de tablaroca, armado, plano con escalímetro), sin personas, sin rostros, sin texto ni logos, sin fachadas que parezcan obra terminada. Corre `node tools/blog-notas/portada.mjs <slug> "<prompt>" /tmp/portada.jpg`. Revisa la imagen: si trae letras, personas, manos deformes o algo que parezca una obra ejecutada de Sayegh Studio, no la uses. Si sale con código 2 o la descartas, usa una foto real de `assets/images/materials/` o `assets/images/projects/` que no haya salido en las últimas 10 notas (campo `base_imagen`), o la portada de una nota vieja. Una imagen generada solo ilustra el tema; nunca se presenta como obra de Sayegh Studio.
5. Piezas para redes: `python3 tools/blog-notas/redes.py <slug> /tmp/portada.jpg "<title>"`. Crea la portada del sitio y la vista de Facebook, la historia 9:16 con el título y la foto de Google Business, todas sin metadatos. Abre la historia y revisa que el título se lea completo.
6. Corre `node tools/blog-notas/nueva_nota.mjs /tmp/nota.json` y después `node tools/blog-notas/test_generar.mjs` y `python3 tools/generar_feed.py`. Si algo falla, corrige y repite. No publiques en rojo.
7. Repaso de una nota vieja (lo que antes hacía Soro al actualizar): toma la nota con `isoDate` más antigua que no tenga `dateModified` en los últimos 30 días. Revisa frases vetadas y enlaces internos rotos, agrega como mucho un enlace interno a la nota nueva si el tema se relaciona, y pon `dateModified` con la fecha de hoy. No cambies su slug ni su título. Corre otra vez `node tools/blog-notas/generar.mjs` y la prueba. Esa nota no se vuelve a compartir en redes.
8. Haz commit en una rama `bitacora/<slug>`, abre PR a `main` con el resumen y fusiónalo cuando el deploy preview de Netlify `sayeghstudio` esté en verde.
9. Ya en producción, comprueba que `https://sayeghstudio.com/blog/notas/<slug>/` responde 200 y que `https://sayeghstudio.com/blog/notas/feed.json` trae la nota primero.

## Formato

- `slug`: minúsculas, sin acentos, con guiones, de 3 a 7 palabras. Nunca lleva «sin-sobrecostos», «sin-sorpresas» ni «garantia».
- `title`: 70 caracteres o menos, con mayúscula solo al inicio y en nombres propios. Lleva la palabra clave del tema.
- `excerpt`: 160 caracteres o menos, con un dato concreto.
- `difusion.facebook`: de 300 a 900 caracteres, texto plano en español de México, sin markdown, sin hashtags, sin viñetas. Abre con el dato o la pregunta más útil de la nota, resume en dos o tres frases qué aprende quien la lea y termina con el enlace completo `https://sayeghstudio.com/blog/notas/<slug>/`. Comillas inglesas, ¿ y ¡ de apertura.
- `difusion.gbp`: de 250 a 1,200 caracteres, texto plano, sin URL, correo ni teléfono (Google los rechaza; el botón «Más información» ya lleva a la nota). Nombra la zona o el tipo de obra cuando venga al caso y cierra invitando a leer la nota o a iniciar la Auditoría de Viabilidad.
- Las dos frases de difusión siguen las mismas reglas de voz y marca de abajo. Nunca «IA», «render» ni «generado».
- `html`: solo `<p>`, `<h2>`, `<h3>`, `<ul>`, `<ol>`, `<li>`, `<strong>`, `<em>` y `<a>`. Nada de scripts, estilos, imágenes ni marcadores «[Insertar…]». Entre 1,100 y 1,800 palabras, con al menos 4 `<h2>`. Debe llevar al menos dos enlaces internos a notas o páginas de `/blog/` y una invitación final a la Auditoría de Viabilidad en `https://via.sayeghstudio.com`.

## Voz y reglas de marca (obligatorias)

- Español de México, ortografía RAE, humanizado. Frases de largo variable y al menos un dato concreto por párrafo (norma, medida, plazo, material, zona). Sin «no es X, es Y», sin tríadas forzadas, sin cierres de resumen ni aperturas de plantilla. Vocabulario marcado prohibido: crucial, fomentar, panorama, tapiz, potenciar, holístico, sinergia, robusto, matices.
- Regla del 15-11 (LFPC art. 32, publicidad veraz): nunca escribir «0 % sobrecostos», «sin sobrecostos», «cero sobrecostos», «sin sorpresas», «garantizado/garantizamos», «plusvalía garantizada», «inquebrantables», «no se mueve» ni «entrega a tiempo». Lo que sí se promete: «Precios unitarios firmados antes de la primera excavación. Cada cambio de alcance lo firmas tú, con su precio y su efecto en plazo, antes de ejecutarse.»
- Léxico vetado: bonito, barato, económico, presupuesto rápido, diseño gratis, decorar, lujo ostentoso. Sin cifras de precios ni porcentajes inventados; solo datos que se puedan sostener (NOM, NTC, Reglamento de Construcciones de la CDMX, ACI, fichas técnicas).
- Sin menciones de IA, render generado ni nada parecido.
- Autoridad semántica para buscadores y motores de IA: usa con naturalidad los términos técnicos del estudio (precios unitarios, dirección de obra pericial, concreto aparente, travertino a la veta, tablaroca de alta especificación, selladores nanosilanos, iluminación wall-washer, sistemas VRF) solo donde vengan al caso.
- Zonas activas que se pueden nombrar: CDMX (Polanco, Lomas, Coyoacán), Interlomas, Bosque Real, Huixquilucan, Temixco, Querétaro, Puebla, San Miguel de Allende.
