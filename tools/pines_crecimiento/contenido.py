"""
Contenido de los pines de crecimiento (4 semanas, 8-nov a 6-dic de 2026).

Fuente única para imágenes, CSV de carga y calendario. Lo usa construir.py.
Horas en CDMX (UTC-6 todo el año); construir.py las convierte a UTC para el CSV.

Segmentos: A = mujeres de 30 a 55 años; B = empresarios e inversionistas de alto valor.
Bloques (contrato §6.2 bis): A_noche (mar y jue 20:30), A_finde (sáb 10:00, dom 19:30),
B_laboral (mar 9:30, jue 13:30), conversion (mié 10:30).
"""
import os

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
BOVEDA = os.environ.get('RENDERS_DIR', '/mnt/project-files/05_Portafolio_Web/renders_zonas_2026-11-06/')
RENDERS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'renders')


def V(f):  # render de la bóveda
    return os.path.join(BOVEDA, f)


def Z(f):  # render de zona del sitio
    return os.path.join(RAIZ, 'assets', 'images', 'zonas', f)


def MAT(f):  # muestra de material del sitio
    return os.path.join(RAIZ, 'assets', 'images', 'materials', f)


def R(v):  # render 3D conceptual de este directorio (escenas_3d.py)
    return os.path.join(RENDERS, f'render-{v}.jpg')


def P(f):  # foto de proyecto del sitio
    return os.path.join(RAIZ, 'assets', 'images', 'projects', f)


LEYENDA = 'Render conceptual de Sayegh Studio. No corresponde a una obra entregada.'
CTA_AUDITORIA = 'Solicite su Auditoría de Viabilidad en sayeghstudio.com/auditoria.'

TAB = {
    'remodelacion': 'Remodelación de Casas de Lujo CDMX',
    'travertino': 'Travertino y Piedra Natural en Interiores',
    'presupuesto': 'Presupuesto de Remodelación: Guía para Clientes',
    'obra': 'Obra Gris y Proceso de Construcción',
    'acabados': 'Acabados de Lujo: Detalles e Instalación',
    'concreto': 'Concreto Aparente y Minimalismo Cálido',
    'cocinas': 'Cocinas de Lujo: Diseño y Remodelación',
    'banos': 'Baños de Lujo en Piedra Natural',
}

# Cada pin de imagen:
#  slug (= utm_content y nombre de archivo), fecha y hora CDMX, segmento, bloque, tablero,
#  campaña UTM, destino (ruta del sitio), t40 (título corto, máx. 40), titulo (máx. 100,
#  empieza con la palabra clave), desc (máx. 500), kw, img (fuente, posición, zoom),
#  marca ('render' | 'credito' | 'ninguna'), textos de imagen y cinta ('guardar' | 'auditoria').

PINES = [
    # ------------------------------------------------ semana 1 (8 al 15 de noviembre)
    dict(slug='zona-bosques-01', fecha='2026-11-10', hora='09:30', seg='B', bloque='B_laboral', tab='presupuesto',
         camp='zonas', destino='/zonas-landing/bosques-de-las-lomas/',
         t40='Viabilidad en Bosques de las Lomas',
         titulo='Viabilidad en Bosques de las Lomas: qué revisar antes de comprar o remodelar',
         desc=('Antes de comprar o remodelar una casa en Bosques de las Lomas conviene saber tres cosas: qué permite '
               'la normativa del lote, cómo se comporta la pendiente y qué estructura se puede conservar. Con eso se '
               'fija el alcance y un precio por partida antes de excavar. La página de la zona explica cómo trabajamos '
               'ahí. ' + LEYENDA + ' ' + CTA_AUDITORIA),
         kw='Bosques de las Lomas, casa en Bosques de las Lomas, viabilidad de terreno, remodelación de casas, arquitecto residencial CDMX',
         img=dict(src=V('bosques_exterior.jpg'), pos='68% 58%', zoom=230), marca='render', tono='oscuro', modo='split',
         kicker='Bosques de las Lomas', titular='Viabilidad antes de comprar', apoyo='Pendiente, arbolado y normativa: cuánta casa cabe y a qué precio, antes del primer plano.',
         cinta='auditoria'),
    dict(slug='material-travertino-01', fecha='2026-11-10', hora='20:30', seg='A', bloque='A_noche', tab='travertino',
         camp='materiales', destino='/blog/materiales/travertino-arquitectura-lujo/',
         t40='Escalera de travertino',
         titulo='Escalera de travertino: ideas para un vestíbulo de piedra natural',
         desc=('El travertino gana carácter con los años. Con los poros rellenos y sellados toma calidez, y la veta '
               'corrida hace que la escalera se lea como una sola pieza. Antes de elegirlo conviene revisar el acabado '
               '(pulido, apomazado o envejecido), el sellado y el mantenimiento. La guía de travertino en '
               'sayeghstudio.com lo explica con detalle. ' + LEYENDA + ' Guarde este pin para su próxima remodelación.'),
         kw='escalera de travertino, travertino, piedra natural, vestíbulo de lujo, interiores de casas de lujo',
         img=dict(src=V('lomas_vestibulo.jpg'), pos='42% center'), marca='render', tono='claro', modo='split',
         kicker='Travertino', titular='Una escalera que envejece bien', apoyo='Piedra a la veta, sellada y con luz cenital. Guárdela para su vestíbulo.',
         cinta='guardar'),
    dict(slug='zona-bosque-real-01', fecha='2026-11-12', hora='13:30', seg='B', bloque='B_laboral', tab='obra',
         camp='zonas', destino='/zonas-landing/bosque-real/',
         t40='Casa en Bosque Real con vista',
         titulo='Casa en Bosque Real con vista: terraza y proyecto pensados desde la pendiente',
         desc=('En Bosque Real la vista se gana o se pierde en el corte del terreno: cuántos niveles bajan, cuánta '
               'tierra se mueve y dónde queda la terraza. Para quien compra para vivir o para invertir, esas decisiones '
               'fijan el costo de obra mucho antes que los acabados. La página de Bosque Real explica cómo revisamos '
               'reglamento, suelo y precios unitarios. ' + LEYENDA + ' ' + CTA_AUDITORIA),
         kw='Bosque Real, casa en pendiente, movimiento de tierras, obra gris, Huixquilucan',
         img=dict(src=Z('bosque-real-terraza-vista-golf-1600.jpg'), pos='50% center'), marca='render', tono='oscuro', modo='split',
         kicker='Bosque Real · Huixquilucan', titular='La vista se decide en el corte', apoyo='Niveles, contención y orientación resueltos antes del primer plano.',
         cinta='auditoria'),
    dict(slug='material-nogal-01', fecha='2026-11-12', hora='20:30', seg='A', bloque='A_noche', tab='acabados',
         camp='materiales', destino='/blog/materiales/maderas-nobles-lujo/',
         t40='Nogal en cocina',
         titulo='Nogal en cocina: muro de guardado de piso a techo con veta continua',
         desc=('El nogal de veta oscura luce más en paños grandes: un muro de guardado de piso a techo, sin jaladeras, '
               'donde la veta corre de una puerta a la siguiente. Pide madera estable, buen secado y un acabado que '
               'aguante el uso diario de una cocina. La guía de maderas nobles en sayeghstudio.com compara nogal, encino '
               'y parota. ' + LEYENDA + ' Guarde esta idea para su cocina.'),
         kw='nogal, madera de nogal, cocina de nogal, muebles de cocina de lujo, maderas nobles',
         img=dict(src=R('cocina-frontal'), pos='center 40%'), marca='render', tono='claro', modo='split',
         kicker='Nogal', titular='Guardado de nogal de piso a techo', apoyo='Frentes sin jaladeras y veta continua: la cocina se ve ordenada todo el día.',
         cinta='guardar'),
    dict(slug='zona-polanco-01', fecha='2026-11-19', hora='20:30', seg='A', bloque='A_noche', tab='remodelacion',
         camp='zonas', destino='/zonas-landing/polanco/',
         t40='Departamento en Polanco',
         titulo='Departamento en Polanco: remodelación con sala cálida, nogal y chimenea',
         desc=('En Polanco casi todo proyecto es remodelación: la losa, las bajantes y la ventana ya están dadas. El '
               'trabajo está en la luz, la madera y en esconder instalaciones sin perder altura. Esta sala con chimenea '
               'lineal y muros de nogal muestra hacia dónde puede ir un departamento existente. Vea cómo trabajamos en '
               'la zona en sayeghstudio.com. ' + LEYENDA + ' Guarde este pin para su remodelación.'),
         kw='departamento en Polanco, remodelación de departamento, interiores de lujo, sala con chimenea, Polanco',
         img=dict(src=V('polanco_sala.jpg'), pos='40% center'), marca='render', tono='oscuro', modo='split',
         kicker='Polanco', titular='Un departamento que se siente casa', apoyo='Luz cálida, nogal y chimenea en un edificio existente.',
         cinta='guardar'),
    # ------------------------------------------------ semana 2 (16 al 22 de noviembre)
    dict(slug='zona-interlomas-01', fecha='2026-11-17', hora='09:30', seg='B', bloque='B_laboral', tab='presupuesto',
         camp='zonas', destino='/zonas-landing/interlomas/',
         t40='Remodelación en Interlomas',
         titulo='Remodelación en Interlomas: casa con identidad propia dentro de la privada',
         desc=('Muchas casas de Interlomas nacieron como producto de desarrollador. Convertirlas en una residencia con '
               'identidad propia toca fachada, distribución y jardín, siempre dentro del reglamento de la privada. Para '
               'un comprador o inversionista, revisar eso antes de firmar evita sorpresas de alcance. La página de '
               'Interlomas explica el método. ' + LEYENDA + ' ' + CTA_AUDITORIA),
         kw='remodelación en Interlomas, casa en Interlomas, remodelación de fachada, casa en privada, Huixquilucan',
         img=dict(src=V('interlomas_exterior.jpg'), pos='18% 78%', zoom=260), marca='render', tono='oscuro', modo='split',
         kicker='Interlomas', titular='Identidad propia dentro de la privada', apoyo='Fachada, distribución y jardín, con reglamento y precio revisados antes.',
         cinta='auditoria'),
    dict(slug='material-cantera-01', fecha='2026-11-17', hora='20:30', seg='A', bloque='A_noche', tab='travertino',
         camp='materiales', destino='/blog/zonas/coyoacan-remodelacion-lujo/',
         t40='Cantera en casonas de Coyoacán',
         titulo='Cantera en casonas de Coyoacán: restaurar la piedra original del patio',
         desc=('La cantera de una casona en Coyoacán ya trae décadas de pátina. Al remodelar conviene restaurarla con '
               'piedra de características parecidas y dejar que lo nuevo se lea como nuevo, sin imitar lo antiguo. '
               'Muchas de estas fachadas están sujetas a criterios de la alcaldía y del INAH. El artículo sobre '
               'remodelación en Coyoacán lo explica en sayeghstudio.com. ' + LEYENDA + ' Guarde este pin.'),
         kw='cantera, cantera para casas, patio de cantera, casona en Coyoacán, piedra natural',
         img=dict(src=Z('coyoacan-casona-patio-cantera-1600.jpg'), pos='38% center'), marca='render', tono='claro', modo='split',
         kicker='Cantera', titular='Cantera que ya tiene historia', apoyo='Restaurar la piedra del patio y dejar que lo nuevo se lea como nuevo.',
         cinta='guardar'),
    dict(slug='conv-07-cocina', fecha='2026-11-18', hora='10:30', seg='A+B', bloque='conversion', tab='travertino',
         camp='conversion_auditoria', destino='/auditoria',
         t40='Remodelación de cocina de lujo',
         titulo='Remodelación de cocina de lujo: alcance y precio definidos antes de demoler',
         desc=('Una cocina de autor se decide antes de demoler: dónde va la isla, qué pasa con las instalaciones, si la '
               'piedra será travertino o mármol, qué madera, y cuánto cuesta cada partida. La Auditoría de Viabilidad reúne normativa, estado '
               'del inmueble, especificación y precios unitarios por escrito, para que usted apruebe con números claros. '
               + LEYENDA + ' ' + CTA_AUDITORIA),
         kw='remodelación de cocina, cocina de lujo, cocina de travertino, isla de piedra, auditoría de viabilidad, precios unitarios',
         img=dict(src=R('cocina-noche'), pos='center 45%'), marca='render', tono='oscuro', modo='split',
         kicker='Cocina de autor', titular='Decida la cocina antes de demoler', apoyo='Isla, guardado e instalaciones con precio por partida desde el inicio.',
         cinta='auditoria'),
    dict(slug='material-tzalam-01', fecha='2026-11-24', hora='20:30', seg='A', bloque='A_noche', tab='acabados',
         camp='materiales', destino='/',
         t40='Tzalam en interiores',
         titulo='Tzalam en interiores: madera mexicana para pisos, lambrines y celosías',
         desc=('El tzalam es una madera tropical del sureste de México, de tono miel con vetas oscuras. En casas de autor '
               'se usa en pisos, lambrines, puertas y celosías, y combina bien con concreto aparente y travertino. Forma '
               'parte del muestrario de materiales de Sayegh Studio; véalo junto al resto en la sección de materiales '
               'de sayeghstudio.com. Imagen: muestra real de tzalam. Guarde este pin para su paleta de materiales.'),
         kw='tzalam, madera tzalam, pisos de madera, lambrín de madera, maderas mexicanas',
         img=dict(src=MAT('tzalam.jpg'), pos='center', etiqueta='Tzalam'), marca='ninguna', tono='claro', modo='split',
         kicker='Tzalam', titular='La madera que invita a descalzarse', apoyo='Madera tropical de México, tono miel y vetas oscuras.',
         cinta='guardar'),
    dict(slug='zona-coyoacan-01', fecha='2026-12-06', hora='19:30', seg='A', bloque='A_finde', tab='remodelacion',
         camp='zonas', destino='/zonas-landing/coyoacan/',
         t40='Casona en Coyoacán',
         titulo='Casona en Coyoacán: estancia con vigas de madera restauradas y ventanal',
         desc=('Las vigas de madera de una casona en Coyoacán se pueden conservar y reforzar en lugar de esconderlas bajo '
               'un plafón. Con un ventanal nuevo hacia el jardín, la estancia gana luz sin perder el carácter de la casa. '
               'Antes de tocar un muro revisamos INAH, alcaldía y estructura. Vea cómo trabajamos en Coyoacán en '
               'sayeghstudio.com. ' + LEYENDA + ' Guarde esta idea.'),
         kw='casona en Coyoacán, remodelación casa antigua, vigas de madera, restauración de casona, Coyoacán',
         img=dict(src=Z('coyoacan-estancia-vigas-madera-1600.jpg'), pos='45% center'), marca='render', tono='oscuro', modo='split',
         kicker='Coyoacán', titular='Vigas de madera, luz de tarde', apoyo='Una casona restaurada para vivirse hoy, sin borrar su historia.',
         cinta='guardar'),
    # ------------------------------------------------ semana 3 (23 al 29 de noviembre)
    dict(slug='zona-lomas-01', fecha='2026-11-24', hora='09:30', seg='B', bloque='B_laboral', tab='presupuesto',
         camp='zonas', destino='/zonas-landing/lomas-de-chapultepec/',
         t40='Residencia en Lomas de Chapultepec',
         titulo='Residencia en Lomas de Chapultepec: alberca, terraza y precio por partida',
         desc=('Las casas de Lomas de Chapultepec suelen cargar programas grandes: alberca, cava, gimnasio y áreas de '
               'servicio, a veces sobre varias ampliaciones con su propia estructura. Separar lo que conviene conservar '
               'de lo que conviene sustituir es lo primero que se revisa, junto con los precios unitarios de cada '
               'partida. La página de la zona lo explica. ' + LEYENDA + ' ' + CTA_AUDITORIA),
         kw='Lomas de Chapultepec, residencia de lujo CDMX, casa con alberca, remodelación de residencia, precios unitarios',
         img=dict(src=V('lomas_exterior.jpg'), pos='50% center'), marca='render', tono='oscuro', modo='split',
         kicker='Lomas de Chapultepec', titular='Programa grande, precio claro', apoyo='Alberca, cava y servicio: cada partida con precio antes de construir.',
         cinta='auditoria'),
    dict(slug='material-chukum-01', fecha='2026-12-01', hora='20:30', seg='A', bloque='A_noche', tab='acabados',
         camp='materiales', destino='/',
         t40='Chukum para muros y baños',
         titulo='Chukum para muros y baños: aplanado de origen maya en casas de autor',
         desc=('El chukum es un aplanado de origen maya que se prepara con la resina del árbol del mismo nombre, cal y '
               'polvo de piedra. Da un acabado mate y cálido, sin juntas, para muros, baños y albercas. Forma parte del '
               'muestrario de materiales de Sayegh Studio junto con el travertino, el tzalam y el microcemento; véalos '
               'en sayeghstudio.com. Imagen: muestra real de chukum. Guarde este pin para su paleta de materiales.'),
         kw='chukum, acabado chukum, muros de chukum, baño de chukum, aplanados naturales',
         img=dict(src=MAT('chukum.jpg'), pos='center', etiqueta='Chukum'), marca='ninguna', tono='claro', modo='split',
         kicker='Chukum', titular='El tacto de la tierra, pulido', apoyo='Aplanado de origen maya para muros, baños y albercas.',
         cinta='guardar'),
    dict(slug='conv-08-bano', fecha='2026-11-25', hora='10:30', seg='A+B', bloque='conversion', tab='travertino',
         camp='conversion_auditoria', destino='/auditoria',
         t40='Baño de travertino y nogal',
         titulo='Baño de travertino y nogal: remodelación con precio definido antes de iniciar',
         desc=('Un baño principal de piedra natural se decide antes de abrir muros: pendientes, impermeabilización, '
               'ventilación, luz cálida y cada pieza de travertino especificada a la veta. La Auditoría de Viabilidad '
               'deja eso por escrito con precios unitarios, para que la obra arranque con alcance cerrado. '
               + LEYENDA + ' ' + CTA_AUDITORIA),
         kw='baño de travertino, remodelación de baño, baño de lujo, baño principal, auditoría de viabilidad',
         img=dict(src=V('polanco_bano.jpg'), pos='58% center'), marca='render', tono='claro', modo='split',
         kicker='Baño principal', titular='Un baño de piedra, decidido antes', apoyo='Piedra, ventilación y luz con precio por partida antes de la obra.',
         cinta='auditoria'),
    dict(slug='obra-nuvana-01', fecha='2026-11-26', hora='20:30', seg='A', bloque='A_noche', tab='obra',
         camp='blog', destino='/blog/proceso/supervision-obra-lujo/',
         t40='Supervisión de obra residencial',
         titulo='Supervisión de obra residencial: qué revisar antes de cerrar cada etapa',
         desc=('En una obra residencial lo que no se revisa a tiempo queda escondido detrás de un acabado. La supervisión '
               'revisa plomos, niveles, juntas de piedra e instalaciones antes de cerrar cada etapa, y deja registro '
               'para el cliente. Foto de obra del proyecto Nuvana, en Interlomas. El artículo sobre supervisión de obra '
               'en sayeghstudio.com explica qué debe recibir usted en cada visita. Guarde esta lista para su obra.'),
         kw='supervisión de obra, obra gris, construcción residencial, dirección de obra, proceso de construcción',
         img=dict(src=P('nuvana.jpg'), pos='center 35%'), marca='credito', credito='Nuvana, Interlomas', tono='oscuro', modo='split',
         kicker='Supervisión de obra', titular='Lo que se revisa antes de cerrar', apoyo='Plomos, juntas e instalaciones auditados en sitio, etapa por etapa.',
         cinta='auditoria'),
    dict(slug='zona-san-miguel-01', fecha='2026-11-28', hora='10:00', seg='A', bloque='A_finde', tab='travertino',
         camp='zonas', destino='/zonas-landing/san-miguel-de-allende/',
         t40='Casa en San Miguel de Allende',
         titulo='Casa en San Miguel de Allende: escalera de cantera y herrería forjada',
         desc=('En San Miguel de Allende la cantera, la herrería forjada y el mezquite son el vocabulario de la casa. Una '
               'escalera con luz cenital puede ordenar todo el interior. Antes de diseñar en el centro se revisan los '
               'criterios de protección de la zona y del municipio. Vea cómo trabajamos en San Miguel en '
               'sayeghstudio.com. ' + LEYENDA + ' Guarde esta idea para su casa.'),
         kw='casa en San Miguel de Allende, escalera de cantera, herrería forjada, casa colonial, cantera',
         img=dict(src=Z('san-miguel-de-allende-escalera-cantera-forja-1600.jpg'), pos='55% center'), marca='render', tono='claro', modo='split',
         kicker='San Miguel de Allende', titular='Cantera, forja y luz cenital', apoyo='Una escalera que se vuelve el centro de la casa.',
         cinta='guardar'),
    # ------------------------------------------------ semana 4 (30 de noviembre al 6 de diciembre)
    dict(slug='material-concreto-01', fecha='2026-12-01', hora='09:30', seg='B', bloque='B_laboral', tab='obra',
         camp='materiales', destino='/blog/materiales/concreto-aparente-lujo/',
         t40='Concreto aparente',
         titulo='Concreto aparente: cómo se cuela un muro que queda a la vista por décadas',
         desc=('El concreto aparente no admite correcciones con pintura: el acabado sale de la cimbra, del vibrado y del '
               'curado. Por eso se planea desde la obra gris, con muestras previas y juntas definidas. Bien hecho, el '
               'muro no se repinta y envejece bien, algo que pesa en el mantenimiento de una casa de inversión. La guía '
               'de concreto aparente lo explica en sayeghstudio.com. ' + LEYENDA + ' Guarde esta guía.'),
         kw='concreto aparente, muro de concreto aparente, cimbra, obra gris, casa de concreto',
         img=dict(src=Z('interlomas-residencia-concreto-celosia-1600.jpg'), pos='78% 40%', zoom=300), marca='render', tono='oscuro', modo='split',
         kicker='Concreto aparente', titular='Un muro que no se vuelve a pintar', apoyo='Cimbra, vibrado y curado deciden el acabado por décadas.',
         cinta='guardar'),
    dict(slug='material-tadelakt-01', fecha='2026-12-03', hora='20:30', seg='A', bloque='A_noche', tab='acabados',
         camp='materiales', destino='/blog/tendencias/banos-spa-lujo/',
         t40='Tadelakt en el baño',
         titulo='Tadelakt en el baño: aplanado de cal pulida sin juntas para muros y regadera',
         desc=('El tadelakt es un aplanado de cal de origen marroquí que se compacta y se pule con piedra hasta lograr un '
               'brillo satinado. Bien aplicado y tratado con jabón negro resiste la humedad, por eso se usa en regaderas '
               'y muros de baño sin juntas. El artículo de baños tipo spa en sayeghstudio.com explica cómo se piensa un '
               'baño principal. ' + LEYENDA + ' Guarde este pin.'),
         kw='tadelakt, baño de tadelakt, muros sin juntas, aplanado de cal, baño tipo spa',
         img=dict(src=R('bano-tadelakt'), pos='center 40%'), marca='render', tono='claro', modo='split',
         kicker='Tadelakt', titular='Muros de cal pulida para el baño', apoyo='Sin juntas, con brillo satinado y hecho para la humedad.',
         cinta='guardar'),
    dict(slug='conv-09-vestidor', fecha='2026-12-02', hora='10:30', seg='A+B', bloque='conversion', tab='remodelacion',
         camp='conversion_auditoria', destino='/auditoria',
         t40='Walk-in closet de nogal',
         titulo='Walk-in closet de nogal: diseño y precio definidos antes de fabricar',
         desc=('Un walk-in closet bien resuelto se mide antes de dibujar: cuánto cuelga, cuánto se dobla, qué se ve detrás '
               'del vidrio y dónde va la luz. Con eso se especifica la carpintería de nogal y se cotiza pieza por pieza. '
               'La Auditoría de Viabilidad deja alcance y precios unitarios por escrito antes de fabricar. '
               + LEYENDA + ' ' + CTA_AUDITORIA),
         kw='walk in closet, vestidor de lujo, closet de nogal, vestidores modernos, auditoría de viabilidad',
         img=dict(src=R('vestidor-lateral'), pos='center'), marca='render', tono='oscuro', modo='split',
         kicker='Walk-in closet', titular='Un vestidor que ordena el día', apoyo='Nogal, vidrio y luz cálida, con cada pieza cotizada antes de fabricar.',
         cinta='auditoria'),
    dict(slug='inversion-reventa-01', fecha='2026-11-19', hora='13:30', seg='B', bloque='B_laboral', tab='presupuesto',
         camp='blog', destino='/blog/inversion/arquitectura-como-activo-reventa/',
         t40='Valor de reventa de una casa de autor',
         titulo='Valor de reventa de una casa de autor: decisiones de proyecto que sostienen el precio',
         desc=('Dos casas con los mismos metros y la misma ubicación pueden seguir trayectorias de valor distintas. '
               'Pesan un diseño hecho para ese terreno, materiales que no se reponen a los diez años y una ejecución sin '
               'defectos ocultos. El artículo en sayeghstudio.com explica qué revisan un valuador y un comprador. '
               + LEYENDA + ' ' + CTA_AUDITORIA),
         kw='valor de reventa, plusvalía de una casa, inversión inmobiliaria, casa de autor, arquitectura residencial',
         img=dict(src=Z('bosques-de-las-lomas-estancia-travertino-jardin-1600.jpg'), pos='22% 70%', zoom=160), marca='render', tono='oscuro', modo='split',
         kicker='Inversión', titular='Valor que se sostiene al vender', apoyo='Diseño para el terreno, materiales que duran y obra sin defectos ocultos.',
         cinta='auditoria'),
    dict(slug='presupuesto-precio-01', fecha='2026-12-03', hora='13:30', seg='B', bloque='B_laboral', tab='presupuesto',
         camp='blog', destino='/blog/estrategia/presupuesto-vs-precio/',
         t40='Presupuesto o precio firmado',
         titulo='Presupuesto o precio firmado: qué cambia antes de construir una casa de lujo',
         desc=('Un presupuesto es una estimación que se mueve con la obra; un precio firmado es un compromiso por '
               'partida, con alcance, especificación y plazo. La diferencia se nota a mitad de la obra, cuando aparecen '
               'los cambios. El artículo en sayeghstudio.com explica cómo pasar de uno al otro antes de excavar. '
               + LEYENDA + ' ' + CTA_AUDITORIA),
         kw='presupuesto de obra, precio de construcción, precios unitarios, construir casa de lujo, contrato de obra',
         img=dict(src=Z('bosque-real-residencia-travertino-bosque-1600.jpg'), pos='40% 62%', zoom=230), marca='render', tono='oscuro', modo='split',
         kicker='Ingeniería financiera', titular='Presupuesto o precio firmado', apoyo='Alcance, especificación y plazo por partida, antes de excavar.',
         cinta='auditoria'),]

# Pines de arranque de los dos tableros nuevos. Se cargan solo después de crear el tablero
# (contrato §6.4: abrir tras validar la búsqueda). CSV aparte.
SEMILLAS = [
    dict(slug='cocina-isla-01', fecha='2026-11-16', hora='21:00', seg='A', bloque='A_noche', tab='cocinas',
         camp='materiales', destino='/blog/materiales/marmol-travertino-piedra-natural/',
         t40='Isla de cocina en travertino',
         titulo='Isla de cocina en travertino: cómo elegir la piedra para la cubierta',
         desc=('Una isla de travertino pide piedra con poros bien rellenos y sellado de fábrica, porque la cubierta de '
               'una cocina recibe aceite, cítricos y vino todos los días. El mármol se marca antes; el travertino sellado '
               'tolera mejor el uso si se mantiene. La guía que compara mármol, travertino y piedra natural está en '
               'sayeghstudio.com. ' + LEYENDA + ' Guarde este pin para su cocina.'),
         kw='isla de cocina, cubierta de travertino, cocina de travertino, mármol o travertino, cocinas de lujo',
         img=dict(src=R('cocina-isla'), pos='center'), marca='render', tono='claro', modo='split',
         kicker='Cocina de autor', titular='La isla, en una sola piedra', apoyo='Travertino sellado para el uso diario de una cocina.',
         cinta='guardar'),
    dict(slug='cocina-ventanal-01', fecha='2026-11-17', hora='21:00', seg='A', bloque='A_noche', tab='cocinas',
         camp='blog', destino='/blog/tendencias/minimalismo-calido-2026/',
         t40='Cocina minimalista cálida',
         titulo='Cocina minimalista cálida con ventanal de piso a techo hacia el jardín',
         desc=('El minimalismo cálido cambia el blanco frío por piedra, madera y luz natural. En la cocina se traduce en '
               'pocos materiales, guardado oculto y un ventanal que trae el jardín a la mesa. El artículo de minimalismo '
               'cálido en sayeghstudio.com explica cómo se combina con concreto y travertino. ' + LEYENDA +
               ' Guarde esta idea para su cocina.'),
         kw='cocina minimalista, minimalismo cálido, cocina con ventanal, cocinas modernas, cocina con vista al jardín',
         img=dict(src=R('cocina-ventana'), pos='center'), marca='render', tono='claro', modo='split',
         kicker='Minimalismo cálido', titular='La cocina mira al jardín', apoyo='Pocos materiales, guardado oculto y luz natural.',
         cinta='guardar'),
    dict(slug='cocina-bronce-01', fecha='2026-11-18', hora='21:00', seg='A', bloque='A_noche', tab='cocinas',
         camp='materiales', destino='/blog/materiales/acabados-metalicos-lujo/',
         t40='Grifería de bronce en cocina',
         titulo='Grifería de bronce en cocina: herrajes que toman pátina con los años',
         desc=('El bronce y el latón sólidos toman pátina con el uso en lugar de pelarse, por eso funcionan en la grifería '
               'y los herrajes de una cocina que se usa todos los días. Junto al travertino dan una lectura cálida, '
               'lejos del cromo. La guía de acabados metálicos en sayeghstudio.com explica dónde aplicarlos. '
               + LEYENDA + ' Guarde este pin.'),
         kw='grifería de bronce, latón en cocina, acabados metálicos, herrajes de cocina, cocina de lujo',
         img=dict(src=R('cocina-detalle'), pos='center'), marca='render', tono='oscuro', modo='split',
         kicker='Detalle', titular='Bronce que envejece bien', apoyo='Grifería y herrajes elegidos antes de la piedra.',
         cinta='guardar'),
    dict(slug='cocina-luz-01', fecha='2026-11-19', hora='21:30', seg='A', bloque='A_noche', tab='cocinas',
         camp='blog', destino='/blog/tendencias/cocinas-de-autor-lujo/',
         t40='Iluminación de cocina sobre la isla',
         titulo='Iluminación de cocina sobre la isla: colgantes cálidos y luz rasante',
         desc=('La luz de una cocina se diseña en capas: colgantes cálidos sobre la isla para trabajar, una línea rasante '
               'bajo la repisa y luz general que no deslumbre. Se decide con el proyecto eléctrico, antes de colocar la '
               'piedra. El artículo de cocinas de autor en sayeghstudio.com cuenta qué se resuelve primero. '
               + LEYENDA + ' Guarde esta idea.'),
         kw='iluminación de cocina, lámparas para isla, cocina de noche, luz cálida, cocinas de autor',
         img=dict(src=R('cocina-noche-isla'), pos='center'), marca='render', tono='oscuro', modo='split',
         kicker='Iluminación', titular='Luz cálida sobre la isla', apoyo='Colgantes, luz rasante y luz general, en capas.',
         cinta='guardar'),
    dict(slug='cocina-salpicadero-01', fecha='2026-11-20', hora='21:00', seg='A', bloque='A_noche', tab='cocinas',
         camp='materiales', destino='/blog/materiales/nanosilano-ciencia/',
         t40='Salpicadero de travertino',
         titulo='Salpicadero de travertino: sellado para que la piedra no se manche',
         desc=('Un salpicadero de travertino recibe vapor, grasa y agua. Con un sellador de nanosilano la piedra sigue '
               'respirando pero tarda mucho más en mancharse, sin película que se raye o amarillee. El artículo sobre '
               'nanosilano en sayeghstudio.com explica cómo funciona y cada cuánto conviene resellar. ' + LEYENDA +
               ' Guarde este pin para su cocina.'),
         kw='salpicadero de piedra, travertino en cocina, sellador para travertino, nanosilano, cocinas de lujo',
         img=dict(src=R('cocina-repisa'), pos='center'), marca='render', tono='claro', modo='split',
         kicker='Travertino en cocina', titular='Un salpicadero que no se mancha', apoyo='Piedra sellada con nanosilano y repisa con luz.',
         cinta='guardar'),
    dict(slug='bano-sellado-01', fecha='2026-11-23', hora='21:00', seg='A', bloque='A_noche', tab='banos',
         camp='materiales', destino='/blog/materiales/nanosilano-ciencia/',
         t40='Baño de travertino sin manchas',
         titulo='Baño de travertino sin manchas: cómo se sella la piedra del lavabo',
         desc=('En el baño el travertino convive con agua, jabón y cosméticos. Sellarlo con nanosilano hace que la piedra '
               'repela el agua sin cambiar su aspecto ni cerrarle los poros. El artículo sobre nanosilano en '
               'sayeghstudio.com explica por qué el travertino lo necesita y cada cuánto conviene resellar. ' + LEYENDA +
               ' Guarde este pin para su baño.'),
         kw='baño de travertino, sellador para travertino, lavabo de piedra, baños de lujo, mantenimiento de piedra',
         img=dict(src=V('polanco_bano.jpg'), pos='88% 62%', zoom=290), marca='render', tono='claro', modo='split',
         kicker='Baño de piedra', titular='Piedra sellada, sin manchas', apoyo='Travertino tratado para convivir con el agua.',
         cinta='guardar'),
    dict(slug='bano-lavabo-01', fecha='2026-11-24', hora='21:30', seg='A', bloque='A_noche', tab='banos',
         camp='materiales', destino='/blog/materiales/maderas-nobles-lujo/',
         t40='Lavabo volado de nogal y travertino',
         titulo='Lavabo volado de nogal y travertino con espejo de bronce',
         desc=('Un mueble de lavabo volado deja el piso libre, se limpia fácil y hace que el baño se vea más amplio. El '
               'nogal funciona lejos de la salpicadura directa y con buen sellado; la cubierta de travertino recibe el '
               'agua. La guía de maderas nobles en sayeghstudio.com explica cómo trabajar la madera en climas húmedos. '
               + LEYENDA + ' Guarde esta idea para su baño.'),
         kw='lavabo de nogal, mueble de baño, baño de travertino, baños modernos, espejo redondo',
         img=dict(src=R('bano-lavabo'), pos='center'), marca='render', tono='claro', modo='split',
         kicker='Lavabo', titular='Nogal volado, piedra encima', apoyo='Piso libre, luz bajo el mueble y bronce en el espejo.',
         cinta='guardar'),
    dict(slug='bano-nicho-01', fecha='2026-11-25', hora='21:00', seg='A', bloque='A_noche', tab='banos',
         camp='blog', destino='/blog/proceso/remodelacion-sin-mudarse/',
         t40='Remodelación de baño por etapas',
         titulo='Remodelación de baño por etapas: nicho de piedra y tina sin dejar la casa',
         desc=('El baño principal puede remodelarse por etapas mientras la familia sigue en casa: se sella la zona contra '
               'polvo, se programa el corte de agua y se deja otro baño en servicio. El artículo sobre remodelación sin '
               'mudarse en sayeghstudio.com explica qué espacios admiten fases y cuáles no. ' + LEYENDA +
               ' Guarde este pin.'),
         kw='remodelación de baño, remodelación por etapas, baño con tina, nicho en baño, baños de lujo',
         img=dict(src=R('bano-nicho'), pos='center'), marca='render', tono='claro', modo='split',
         kicker='Remodelación por etapas', titular='El baño nuevo, sin mudarse', apoyo='Obra sellada y otro baño en servicio mientras dura.',
         cinta='guardar'),
    dict(slug='bano-agua-01', fecha='2026-11-26', hora='21:30', seg='A', bloque='A_noche', tab='banos',
         camp='materiales', destino='/blog/materiales/marmol-travertino-piedra-natural/',
         t40='Travertino o mármol para el baño',
         titulo='Travertino o mármol para el baño: qué pasa con el agua en cada piedra',
         desc=('El mármol pulido sin sellar se marca con una gota de limón; el travertino tiene poros visibles que, bien '
               'rellenos y sellados, aguantan el agua del baño. La guía que compara mármol, travertino y piedra natural '
               'en sayeghstudio.com indica dónde conviene cada una en piso y muro. ' + LEYENDA +
               ' Guarde esta guía para su baño.'),
         kw='travertino o mármol, piedra para baño, piso de travertino, baño de mármol, piedra natural',
         img=dict(src=os.path.join(RAIZ, 'assets', 'images', 'blog-ai', 'nanosilano-ciencia', 'secundaria.jpg'), pos='center', zoom=120),
         marca='render', tono='oscuro', modo='split',
         kicker='Piedra y agua', titular='Travertino o mármol en el baño', apoyo='Porosidad, sellado y mantenimiento de cada piedra.',
         cinta='guardar'),
    dict(slug='bano-regadera-01', fecha='2026-11-27', hora='21:00', seg='A', bloque='A_noche', tab='banos',
         camp='blog', destino='/blog/tendencias/banos-spa-lujo/',
         t40='Regadera de piedra natural',
         titulo='Regadera de piedra natural: travertino continuo y toallero de herrería',
         desc=('Una regadera de piedra natural se ve mejor con pocas juntas: piezas grandes de travertino, veta corrida y '
               'pendiente resuelta desde la obra gris. La ventilación decide cuánto dura el acabado. El artículo de '
               'baños tipo spa en sayeghstudio.com enumera lo que no puede faltar en el baño principal. ' + LEYENDA +
               ' Guarde esta idea para su baño.'),
         kw='regadera de piedra, baño de travertino, baños de lujo, baño tipo spa, regadera moderna',
         img=dict(src=V('polanco_bano.jpg'), pos='14% 45%', zoom=260), marca='render', tono='claro', modo='split',
         kicker='Regadera', titular='Piedra continua, pocas juntas', apoyo='Travertino a la veta y ventilación pensada desde la obra.',
         cinta='guardar'),
    dict(slug='cocina-autor-01', fecha='2026-11-21', hora='21:00', seg='A', bloque='A_finde', tab='cocinas',
         camp='blog', destino='/blog/tendencias/cocinas-de-autor-lujo/',
         t40='Cocina de lujo con isla de travertino',
         titulo='Cocina de lujo con isla de travertino, nogal y ventanal al jardín',
         desc=('Isla monolítica de travertino, muro de guardado en nogal y un ventanal de piso a techo hacia el jardín. '
               'Una cocina de autor se arma con pocos materiales bien elegidos y con las instalaciones resueltas antes '
               'de la piedra. El artículo de cocinas de autor en sayeghstudio.com cuenta qué decisiones se toman '
               'primero. ' + LEYENDA + ' Guarde este pin para su cocina.'),
         kw='cocina de lujo, isla de cocina, cocina con isla, cocina de travertino, cocinas modernas',
         img=dict(src=R('cocina-general'), pos='center 40%'), marca='render', tono='claro', modo='split',
         kicker='Cocina de autor', titular='Una isla de piedra como centro', apoyo='Travertino, nogal y luz de jardín. Guárdela para su cocina.',
         cinta='guardar'),

    dict(slug='bano-spa-01', fecha='2026-11-28', hora='21:00', seg='A', bloque='A_finde', tab='banos',
         camp='blog', destino='/blog/tendencias/banos-spa-lujo/',
         t40='Baño tipo spa con tina de travertino',
         titulo='Baño tipo spa con tina de travertino y luz cenital para el baño principal',
         desc=('Una tina exenta de piedra bajo un tragaluz, piso de travertino y muros de cal pulida: un baño principal '
               'pensado para bajar el ritmo al final del día. Detrás hay decisiones técnicas que se toman antes: '
               'ventilación, pendientes, impermeabilización y sellado de la piedra. El artículo de baños tipo spa en '
               'sayeghstudio.com las explica. ' + LEYENDA + ' Guarde esta idea.'),
         kw='baño tipo spa, tina de piedra, baño de travertino, baños de lujo, baño principal',
         img=dict(src=R('bano-tina'), pos='center 45%'), marca='render', tono='claro', modo='split',
         kicker='Baño tipo spa', titular='Una tina de piedra bajo luz cenital', apoyo='Travertino, cal pulida y bronce para el baño principal.',
         cinta='guardar'),
]

# Casillas fijas de los pines de video y de varias páginas (los producen y auditan otros agentes;
# ellos escriben VIDEO_pines.md y CARRUSEL_pines.md con estos mismos slugs).
RESERVAS = [
    dict(slug='video-01', fecha='2026-11-08', hora='19:30', seg='A', bloque='A_finde', tipo='video', tab='travertino', url='https://sayeghstudio.com/blog/tendencias/banos-spa-lujo/?utm_source=pinterest&utm_medium=organic_pin&utm_campaign=blog&utm_content=video-01'),
    dict(slug='carrusel-01', fecha='2026-11-14', hora='10:00', seg='A', bloque='A_finde', tipo='varias_paginas', tab='travertino', url='https://sayeghstudio.com/blog/materiales/marmol-travertino-piedra-natural/?utm_source=pinterest&utm_medium=organic_pin&utm_campaign=materiales&utm_content=carrusel-01'),
    dict(slug='video-02', fecha='2026-11-15', hora='19:30', seg='A', bloque='A_finde', tipo='video', tab='remodelacion', url='https://sayeghstudio.com/zonas-landing/polanco/?utm_source=pinterest&utm_medium=organic_pin&utm_campaign=zonas&utm_content=video-02'),
    dict(slug='carrusel-02', fecha='2026-11-21', hora='10:00', seg='A', bloque='A_finde', tipo='varias_paginas', tab='presupuesto', url='https://sayeghstudio.com/auditoria?utm_source=pinterest&utm_medium=organic_pin&utm_campaign=conversion_auditoria&utm_content=carrusel-02'),
    dict(slug='video-03', fecha='2026-11-22', hora='19:30', seg='A', bloque='A_finde', tipo='video', tab='concreto', url='https://sayeghstudio.com/blog/materiales/concreto-aparente-lujo/?utm_source=pinterest&utm_medium=organic_pin&utm_campaign=materiales&utm_content=video-03'),
    dict(slug='carrusel-04', fecha='2026-11-26', hora='13:30', seg='B', bloque='B_laboral', tipo='varias_paginas', tab='presupuesto', url='https://sayeghstudio.com/auditoria?utm_source=pinterest&utm_medium=organic_pin&utm_campaign=conversion_auditoria&utm_content=carrusel-04'),
    dict(slug='video-04', fecha='2026-11-29', hora='19:30', seg='A', bloque='A_finde', tipo='video', tab='presupuesto', url='https://sayeghstudio.com/auditoria?utm_source=pinterest&utm_medium=organic_pin&utm_campaign=conversion_auditoria&utm_content=video-04'),
    dict(slug='carrusel-03', fecha='2026-12-05', hora='10:00', seg='A', bloque='A_finde', tipo='varias_paginas', tab='remodelacion', url='https://sayeghstudio.com/blog/tendencias/banos-spa-lujo/?utm_source=pinterest&utm_medium=organic_pin&utm_campaign=blog&utm_content=carrusel-03'),
]

# Pines ya programados en la cuenta (datos del coordinador, 6-nov 04:05Z y v22:45). Solo calendario.
YA_PROGRAMADOS_CONVERSION = [
    ('2026-11-07', 'pin-01-presupuesto', 'Remodelación de Casas de Lujo CDMX', 'Presupuesto de remodelación: el precio se firma'),
    ('2026-11-08', 'pin-02-patrimonial', 'Remodelación de Casas de Lujo CDMX', 'Remodelación patrimonial de lujo en CDMX'),
    ('2026-11-09', 'pin-03-inversion', 'Presupuesto de Remodelación: Guía para Clientes', 'Viabilidad antes de comprar el terreno'),
    ('2026-11-10', 'pin-04-materiales', 'Travertino y Piedra Natural en Interiores', 'Travertino en interiores'),
    ('2026-11-11', 'pin-05-bano', 'Remodelación de Casas de Lujo CDMX', 'Baño de autor en CDMX'),
    ('2026-11-12', 'pin-06-zona', 'Remodelación de Casas de Lujo CDMX', 'Arquitecto en Interlomas'),
]
# Horarios UTC de los otros 9 pines ya programados (contenido no informado al hilo B).
YA_PROGRAMADOS_OTROS_UTC = [
    '2026-11-07T02:30', '2026-11-08T02:00', '2026-11-09T02:00', '2026-11-10T02:30', '2026-11-11T02:00',
    '2026-11-12T02:30', '2026-11-13T02:00', '2026-11-14T02:30', '2026-11-15T02:00',
]
