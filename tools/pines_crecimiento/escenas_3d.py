"""
Escenas 3D conceptuales para pines de Pinterest (Sayegh Studio).

Genera renders conceptuales de cocina y vestidor con Blender (Cycles, CPU),
usando como texturas las muestras de material del propio sitio
(assets/images/materials/). No son obras entregadas: cada imagen que salga de
aquí se marca como "Render conceptual" en el pin y en su descripción.

Uso (requiere el módulo bpy, p. ej. `pip install bpy==5.1.2` en un venv):
    python tools/pines_crecimiento/escenas_3d.py <salida_dir> [vista ...]

Vistas disponibles: ver VISTAS al final del archivo.
"""
import math
import os
import random
import sys

import bpy
from mathutils import Vector

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MAT_DIR = os.path.join(RAIZ, 'assets', 'images', 'materials')


# ---------------------------------------------------------------- utilidades
def limpiar():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def material_imagen(nombre, archivo, escala=1.0, rough=0.5, tinte=None, bump=0.15, especular=0.5):
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes['Principled BSDF']
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.image = bpy.data.images.load(os.path.join(MAT_DIR, archivo))
    tex.projection = 'BOX'
    tex.projection_blend = 0.25
    coord = nt.nodes.new('ShaderNodeTexCoord')
    mapping = nt.nodes.new('ShaderNodeMapping')
    mapping.inputs['Scale'].default_value = (1 / escala, 1 / escala, 1 / escala)
    nt.links.new(coord.outputs['Object'], mapping.inputs['Vector'])
    nt.links.new(mapping.outputs['Vector'], tex.inputs['Vector'])
    color = tex.outputs['Color']
    if tinte:
        mix = nt.nodes.new('ShaderNodeMix')
        mix.data_type = 'RGBA'
        mix.blend_type = 'MULTIPLY'
        mix.inputs['Factor'].default_value = 1.0
        nt.links.new(color, mix.inputs[6])
        mix.inputs[7].default_value = (*tinte, 1)
        color = mix.outputs[2]
    nt.links.new(color, bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = rough
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = especular
    if bump:
        bw = nt.nodes.new('ShaderNodeRGBToBW')
        b = nt.nodes.new('ShaderNodeBump')
        b.inputs['Strength'].default_value = bump
        b.inputs['Distance'].default_value = 0.002
        nt.links.new(tex.outputs['Color'], bw.inputs['Color'])
        nt.links.new(bw.outputs['Val'], b.inputs['Height'])
        nt.links.new(b.outputs['Normal'], bsdf.inputs['Normal'])
    return m


def material_tadelakt():
    """Aplanado de cal pulido (tadelakt): color arena cálido, brillo satinado y nubes de tono."""
    m = bpy.data.materials.new('tadelakt')
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes['Principled BSDF']
    ruido = nt.nodes.new('ShaderNodeTexNoise')
    ruido.inputs['Scale'].default_value = 4.5
    ruido.inputs['Detail'].default_value = 6
    rampa = nt.nodes.new('ShaderNodeValToRGB')
    rampa.color_ramp.elements[0].color = (0.36, 0.24, 0.16, 1)
    rampa.color_ramp.elements[1].color = (0.52, 0.38, 0.27, 1)
    nt.links.new(ruido.outputs['Fac'], rampa.inputs['Fac'])
    nt.links.new(rampa.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.22
    b = nt.nodes.new('ShaderNodeBump')
    b.inputs['Strength'].default_value = 0.06
    nt.links.new(ruido.outputs['Fac'], b.inputs['Height'])
    nt.links.new(b.outputs['Normal'], bsdf.inputs['Normal'])
    return m


def material_liso(nombre, color, rough=0.5, metal=0.0, emision=None, fuerza=0.0, transmision=0.0):
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    bsdf = m.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    if transmision:
        bsdf.inputs['Transmission Weight'].default_value = transmision
        bsdf.inputs['IOR'].default_value = 1.45
    if emision:
        bsdf.inputs['Emission Color'].default_value = (*emision, 1)
        bsdf.inputs['Emission Strength'].default_value = fuerza
    return m


def caja(nombre, centro, tam, mat, bisel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=centro)
    o = bpy.context.active_object
    o.name = nombre
    o.scale = tam
    bpy.ops.object.transform_apply(scale=True)
    if bisel:
        mod = o.modifiers.new('bisel', 'BEVEL')
        mod.width = bisel
        mod.segments = 2
    o.data.materials.append(mat)
    return o


def cilindro(nombre, centro, radio, alto, mat, rot=(0, 0, 0), verts=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radio, depth=alto, location=centro, rotation=rot)
    o = bpy.context.active_object
    o.name = nombre
    bpy.ops.object.shade_smooth()
    o.data.materials.append(mat)
    return o


def esfera(nombre, centro, radio, mat, escala=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radio, location=centro, segments=48, ring_count=24)
    o = bpy.context.active_object
    o.name = nombre
    o.scale = escala
    bpy.ops.object.shade_smooth()
    o.data.materials.append(mat)
    return o


def mundo(color, fuerza):
    w = bpy.data.worlds.new('mundo')
    bpy.context.scene.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = (*color, 1)
    bg.inputs['Strength'].default_value = fuerza


def sol(rot, fuerza, color=(1.0, 0.92, 0.80), angulo=1.5):
    bpy.ops.object.light_add(type='SUN', rotation=rot)
    s = bpy.context.active_object
    s.data.energy = fuerza
    s.data.color = color
    s.data.angle = math.radians(angulo)
    return s


def luz_area(loc, rot, tam, fuerza, color=(1, 0.95, 0.88), forma='RECTANGLE', tam_y=None):
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot)
    a = bpy.context.active_object
    a.data.shape = forma
    a.data.size = tam
    if tam_y:
        a.data.size_y = tam_y
    a.data.energy = fuerza
    a.data.color = color
    return a


def camara(loc, mira, lente=28, foco=None, f_stop=4.0, shift_y=0.0, nivel=True):
    """Cámara de arquitectura: eje horizontal (verticales rectas) y desplazamiento vertical."""
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.active_object
    if nivel:
        mira = (mira[0], mira[1], loc[2])
    c.data.shift_y = shift_y
    d = Vector(mira) - Vector(loc)
    c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    c.data.lens = lente
    c.data.sensor_width = 36
    if foco:
        c.data.dof.use_dof = True
        c.data.dof.focus_distance = foco
        c.data.dof.aperture_fstop = f_stop
    bpy.context.scene.camera = c
    return c


def follaje(x0, x1, y0, y1, n=120, semilla=7):
    random.seed(semilla)
    verdes = [(0.10, 0.20, 0.07), (0.16, 0.27, 0.10), (0.08, 0.15, 0.06), (0.22, 0.30, 0.12)]
    mats = [material_liso(f'hoja{i}', c, rough=0.8) for i, c in enumerate(verdes)]
    for i in range(n):
        x = random.uniform(x0, x1)
        y = random.uniform(y0, y1)
        z = random.uniform(0.6, 5.5)
        r = random.uniform(0.5, 1.3)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r, location=(x, y, z))
        o = bpy.context.active_object
        o.data.materials.append(random.choice(mats))
    tronco = material_liso('tronco', (0.12, 0.09, 0.07), rough=0.9)
    for i in range(9):
        cilindro(f'tronco{i}', (random.uniform(x0, x1), random.uniform(y0, y1), 2.5), 0.09, 5, tronco, verts=12)


def fondo_jardin(centro, ancho, alto, fuerza):
    """Plano emisivo con la vista a jardín de un render propio (estancia de Bosques de las Lomas)."""
    img = os.path.join(RAIZ, 'assets', 'images', 'zonas', 'bosques-de-las-lomas-estancia-travertino-jardin-1600.jpg')
    m = bpy.data.materials.new('jardin')
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    em = nt.nodes.new('ShaderNodeEmission')
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.image = bpy.data.images.load(img)
    tex.extension = 'EXTEND'
    uv = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    # Recorta la franja central de árboles del render (sin muebles).
    mp.inputs['Location'].default_value = (0.36, 0.30, 0)
    mp.inputs['Scale'].default_value = (0.30, 0.45, 1)
    nt.links.new(uv.outputs['UV'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], tex.inputs['Vector'])
    nt.links.new(tex.outputs['Color'], em.inputs['Color'])
    em.inputs['Strength'].default_value = fuerza
    nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
    bpy.ops.mesh.primitive_plane_add(size=1, location=centro, rotation=(math.radians(90), 0, math.radians(90)))
    o = bpy.context.active_object
    o.scale = (ancho, alto, 1)
    o.data.materials.append(m)
    o.visible_shadow = False
    return o


def ajustes(muestras=128, ancho=1000, alto=1500):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = muestras
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.03
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.render.resolution_x = ancho
    sc.render.resolution_y = alto
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'JPEG'
    sc.render.image_settings.quality = 94
    try:
        sc.view_settings.view_transform = 'AgX'
        sc.view_settings.look = 'AgX - Medium High Contrast'
    except TypeError:
        sc.view_settings.view_transform = 'Filmic'
    sc.view_settings.exposure = float(os.environ.get('EXPOSICION', '-0.2'))


# ---------------------------------------------------------------- materiales
def materiales():
    return {
        'travertino': material_imagen('travertino', 'travertino.jpg', escala=1.1, rough=0.32, bump=0.25),
        'travertino_piso': material_imagen('travertino_piso', 'travertino.jpg', escala=1.6, rough=0.45, bump=0.1),
        'nogal': material_imagen('nogal', 'nogal.jpg', escala=0.9, rough=0.45, bump=0.08),
        'encino': material_imagen('encino', 'encino.jpg', escala=0.28, rough=0.5, tinte=(0.86, 0.80, 0.72), bump=0.05),
        'concreto': material_imagen('concreto', 'microcemento.jpg', escala=2.2, rough=0.85, tinte=(1.25, 1.18, 1.08), bump=0.3),
        'marmol': material_imagen('marmol', 'marmol.jpg', escala=1.0, rough=0.15, bump=0.02),
        'piso_claro': material_imagen('piso_claro', 'microcemento.jpg', escala=3.0, rough=0.35, tinte=(1.9, 1.75, 1.55), bump=0.05),
        'tadelakt': material_tadelakt(),
        'yeso': material_liso('yeso', (0.83, 0.80, 0.75), rough=0.9),
        'bronce': material_liso('bronce', (0.62, 0.43, 0.25), rough=0.28, metal=1.0),
        'negro': material_liso('negro', (0.03, 0.03, 0.03), rough=0.25),
        'ceramica': material_liso('ceramica', (0.16, 0.14, 0.12), rough=0.6),
        'ceramica_clara': material_liso('ceramica_clara', (0.78, 0.74, 0.68), rough=0.55),
        'vidrio': material_liso('vidrio', (0.95, 0.97, 0.97), rough=0.0, transmision=1.0),
        'vidrio_humo': material_liso('vidrio_humo', (0.80, 0.76, 0.70), rough=0.02, transmision=1.0),
        'cuero': material_liso('cuero', (0.32, 0.18, 0.10), rough=0.55),
        'tela': material_liso('tela', (0.36, 0.31, 0.26), rough=0.95),
        'tela_osc': material_liso('tela_osc', (0.18, 0.17, 0.16), rough=0.95),
        'pasto': material_liso('pasto', (0.05, 0.08, 0.03), rough=0.95),
        'led': material_liso('led', (1, 1, 1), emision=(1.0, 0.78, 0.52), fuerza=12),
        'pantalla': material_liso('pantalla', (1, 1, 1), emision=(1.0, 0.80, 0.58), fuerza=6),
    }


# ---------------------------------------------------------------- cocina
def cocina(noche=False):
    M = materiales()
    W, D, H = 7.0, 6.0, 3.3
    # Envolvente
    caja('piso', (W / 2, D / 2, -0.05), (W + 6, D + 2, 0.1), M['piso_claro'])
    caja('techo', (W / 2, D / 2, H + 0.05), (W, D, 0.1), M['yeso'])
    caja('muro_fondo', (W / 2, D + 0.1, H / 2), (W, 0.2, H), M['concreto'])
    caja('muro_izq', (-0.1, D / 2, H / 2), (0.2, D, H), M['concreto'])
    # Muro derecho con ventanal de piso a techo (x = W)
    caja('muro_der_a', (W + 0.1, 0.4, H / 2), (0.2, 0.8, H), M['concreto'])
    caja('muro_der_b', (W + 0.1, D - 0.3, H / 2), (0.2, 0.6, H), M['concreto'])
    for i, y in enumerate([0.8, 2.3, 3.8, 5.4]):
        caja(f'mainel{i}', (W + 0.05, y, H / 2), (0.06, 0.05, H), M['negro'])
    caja('dintel', (W + 0.05, D / 2, H - 0.03), (0.06, D, 0.06), M['negro'])
    # Exterior: pasto y fondo de jardín (render propio del estudio, desenfocado por la cámara)
    caja('pasto', (W + 7, D / 2, -0.04), (12, 30, 0.1), M['pasto'])
    fondo_jardin((W + 5.5, D / 2, 2.6), 16, 9, 1.6 if not noche else 0.12)
    # Ranura de luz en el techo
    caja('ranura', (W / 2, 0.9, H - 0.005), (W - 1.0, 0.04, 0.01), M['led'])

    # Muro de guardado de nogal (fondo, izquierda) a altura completa
    caja('alacena', (1.35, D - 0.33, 1.5), (2.6, 0.62, 3.0), M['nogal'], bisel=0.004)
    for i, x in enumerate([0.70, 1.35, 2.0]):
        caja(f'junta{i}', (x, D - 0.635, 1.5), (0.006, 0.01, 2.9), M['negro'])
    # Barra de trabajo al fondo, derecha
    caja('mueble_bajo', (4.55, D - 0.33, 0.44), (3.7, 0.62, 0.88), M['nogal'], bisel=0.003)
    caja('cubierta', (4.55, D - 0.33, 0.905), (3.74, 0.66, 0.05), M['travertino'])
    caja('salpicadero', (4.55, D - 0.015, 1.55), (3.74, 0.03, 1.25), M['travertino'])
    caja('repisa', (4.55, D - 0.14, 2.28), (3.74, 0.26, 0.05), M['travertino'])
    caja('led_repisa', (4.55, D - 0.15, 2.25), (3.6, 0.02, 0.01), M['led'])
    caja('parrilla', (5.4, D - 0.33, 0.932), (0.80, 0.52, 0.006), M['negro'])
    # Tarja integrada y grifo de bronce
    caja('tarja', (3.6, D - 0.33, 0.925), (0.7, 0.42, 0.006), M['ceramica'])
    cilindro('grifo_v', (3.6, D - 0.08, 1.15), 0.014, 0.46, M['bronce'], verts=24)
    cilindro('grifo_h', (3.6, D - 0.19, 1.37), 0.014, 0.24, M['bronce'], rot=(math.radians(90), 0, 0), verts=24)
    # Objetos de repisa
    cilindro('jarra', (3.0, D - 0.14, 2.42), 0.07, 0.24, M['ceramica_clara'])
    esfera('cuenco_r', (5.7, D - 0.14, 2.34), 0.09, M['ceramica'], escala=(1, 1, 0.45))
    cilindro('libro', (6.1, D - 0.14, 2.36), 0.11, 0.06, M['tela_osc'], verts=4)

    # Isla monolítica de travertino con caídas laterales
    ix, iy = 3.6, 2.9
    caja('isla_bloque', (ix, iy, 0.53), (3.3, 1.15, 0.84), M['travertino'])
    caja('isla_zoclo', (ix, iy, 0.055), (3.1, 0.95, 0.11), M['negro'])
    # Objetos sobre la isla
    esfera('cuenco', (ix + 0.6, iy - 0.1, 0.99), 0.17, M['ceramica'], escala=(1, 1, 0.38))
    cilindro('florero', (ix - 0.9, iy + 0.15, 1.12), 0.085, 0.34, M['ceramica_clara'])
    cilindro('florero2', (ix - 0.72, iy + 0.05, 1.05), 0.06, 0.2, M['ceramica'])
    esfera('fruta', (ix + 0.6, iy - 0.1, 1.03), 0.05, material_liso('fruta', (0.75, 0.45, 0.12), rough=0.5))
    caja('tabla', (ix + 1.1, iy + 0.2, 0.97), (0.5, 0.32, 0.025), M['nogal'], bisel=0.004)
    # Bancos
    for k, x in enumerate([ix - 0.9, ix, ix + 0.9]):
        cilindro(f'asiento{k}', (x, iy - 0.95, 0.66), 0.2, 0.06, M['cuero'])
        for a in range(4):
            t = a * math.pi / 2 + math.pi / 4
            cilindro(f'pata{k}{a}', (x + 0.13 * math.cos(t), iy - 0.95 + 0.13 * math.sin(t), 0.32), 0.012, 0.64,
                     M['bronce'], verts=12)
        caja(f'aro{k}', (x, iy - 0.95, 0.24), (0.3, 0.3, 0.01), M['bronce'])
    # Lámparas colgantes
    for k, x in enumerate([ix - 0.95, ix, ix + 0.95]):
        cilindro(f'cable{k}', (x, iy, H - 0.5), 0.003, 1.0, M['negro'], verts=8)
        cilindro(f'pantalla{k}', (x, iy, H - 1.08), 0.11, 0.2, M['bronce'])
        cilindro(f'bombilla{k}', (x, iy, H - 1.185), 0.09, 0.012, M['pantalla'])
    # Luz
    if noche:
        mundo((0.02, 0.03, 0.06), 0.4)
        for k, x in enumerate([ix - 0.95, ix, ix + 0.95]):
            bpy.ops.object.light_add(type='SPOT', location=(x, iy, H - 1.2), rotation=(0, 0, 0))
            s = bpy.context.active_object
            s.data.energy = 140
            s.data.spot_size = math.radians(80)
            s.data.spot_blend = 0.6
            s.data.color = (1.0, 0.78, 0.55)
            s.data.shadow_soft_size = 0.08
        luz_area((4.55, D - 0.25, 2.24), (0, 0, 0), 3.5, 70, color=(1, 0.78, 0.5), tam_y=0.06)
        luz_area((W / 2, 0.9, H - 0.02), (0, 0, 0), W - 1, 120, color=(1, 0.8, 0.6), tam_y=0.08)
        luz_area((W + 4, 2, 4), (0, math.radians(-90), 0), 6, 30, color=(0.4, 0.5, 0.8))
    else:
        mundo((0.55, 0.65, 0.80), 0.9)
        sol((math.radians(58), 0, math.radians(102)), 4.2)
        luz_area((W - 0.3, 3.1, 1.7), (0, math.radians(-90), 0), 4.0, 260, color=(0.95, 0.97, 1.0), tam_y=3.0)
        luz_area((W / 2, D / 2, H - 0.05), (0, 0, 0), 3.0, 120, color=(1, 0.94, 0.86))
    return W, D, H, ix, iy


# ---------------------------------------------------------------- vestidor
def vestidor(noche=True):
    M = materiales()
    W, D, H = 4.4, 5.6, 3.0
    caja('piso', (W / 2, D / 2, -0.05), (W + 2, D + 2, 0.1), M['travertino_piso'])
    caja('techo', (W / 2, D / 2, H + 0.05), (W, D, 0.1), M['yeso'])
    caja('muro_fondo', (W / 2, D + 0.1, H / 2), (W, 0.2, H), M['travertino'])
    caja('muro_izq', (-0.1, D / 2, H / 2), (0.2, D, H), M['yeso'])
    caja('muro_der', (W + 0.1, D / 2, H / 2), (0.2, D, H), M['yeso'])
    caja('ranura', (W / 2, D / 2, H - 0.005), (0.04, D - 0.6, 0.01), M['led'])
    # Nicho de nogal con luz rasante en el muro de fondo
    caja('nicho', (W / 2, D - 0.02, 1.45), (1.3, 0.04, 2.1), M['nogal'])
    caja('nicho_led', (W / 2, D - 0.05, 2.49), (1.24, 0.02, 0.01), M['led'])
    caja('repisa_nicho', (W / 2, D - 0.15, 1.1), (1.3, 0.26, 0.04), M['travertino'])
    cilindro('pieza1', (W / 2 - 0.3, D - 0.15, 1.25), 0.07, 0.26, M['ceramica'])
    esfera('pieza2', (W / 2 + 0.25, D - 0.15, 1.18), 0.08, M['ceramica_clara'], escala=(1, 1, 0.7))
    # Guardado de nogal a ambos lados con frentes de vidrio humo
    for lado, x in (('i', 0.32), ('d', W - 0.32)):
        xb = 0.03 if lado == 'i' else W - 0.03
        caja(f'casco_{lado}', (xb, D / 2 + 0.2, 1.3), (0.06, D - 1.4, 2.6), M['nogal'])
        caja(f'base_{lado}', (x, D / 2 + 0.2, 0.06), (0.6, D - 1.4, 0.12), M['negro'])
        caja(f'remate_{lado}', (x, D / 2 + 0.2, 2.8), (0.6, D - 1.4, 0.4), M['nogal'])
        sgn = 1 if lado == 'i' else -1
        for k in range(5):
            y = 1.2 + k * 0.84
            caja(f'vidrio_{lado}{k}', (x + sgn * 0.305, y + 0.42, 1.55), (0.012, 0.8, 2.0), M['vidrio_humo'])
            caja(f'interior_{lado}{k}', (xb + sgn * 0.04, y + 0.42, 1.55), (0.02, 0.78, 1.96),
                 material_liso(f'fondo{lado}{k}', (0.30, 0.22, 0.15), rough=0.7))
            caja(f'led_{lado}{k}', (x + sgn * 0.27, y + 0.42, 2.52), (0.03, 0.74, 0.01), M['led'])
            random.seed(k * 11 + (0 if lado == 'i' else 5))
            for p in range(7):
                yy = y + 0.1 + p * 0.1
                tono = random.choice([(0.85, 0.82, 0.76), (0.18, 0.18, 0.2), (0.45, 0.38, 0.3), (0.9, 0.9, 0.88)])
                caja(f'prenda_{lado}{k}{p}', (x + sgn * 0.05, yy, 1.85), (0.36, 0.03, 0.7),
                     material_liso(f'tela{lado}{k}{p}', tono, rough=0.95))
            caja(f'tubo_{lado}{k}', (x + sgn * 0.05, y + 0.42, 2.22), (0.015, 0.78, 0.015), M['bronce'])
            caja(f'cajon_{lado}{k}', (x + sgn * 0.05, y + 0.42, 0.55), (0.5, 0.78, 0.6), M['nogal'])
    # Isla central de travertino con cajones de nogal
    caja('isla', (W / 2, D / 2, 0.45), (1.0, 1.8, 0.86), M['nogal'], bisel=0.003)
    caja('isla_cub', (W / 2, D / 2, 0.905), (1.06, 1.86, 0.05), M['travertino'])
    for k in range(3):
        caja(f'tirador{k}', (W / 2 - 0.505, D / 2, 0.25 + k * 0.25), (0.006, 1.6, 0.004), M['negro'])
    cilindro('bandeja', (W / 2, D / 2 - 0.4, 0.94), 0.16, 0.015, M['bronce'])
    esfera('frasco', (W / 2 - 0.06, D / 2 - 0.4, 1.0), 0.04, M['vidrio_humo'], escala=(1, 1, 1.5))
    caja('libro', (W / 2 + 0.1, D / 2 + 0.4, 0.95), (0.25, 0.32, 0.04), M['tela_osc'])
    # Banca y tapete
    caja('banca', (W / 2, 0.9, 0.22), (1.2, 0.42, 0.06), M['cuero'], bisel=0.01)
    caja('banca_base', (W / 2, 0.9, 0.1), (1.1, 0.36, 0.2), M['negro'])
    caja('tapete', (W / 2, D / 2, 0.003), (2.0, 3.0, 0.006), M['tela'])
    if noche:
        mundo((0.02, 0.02, 0.03), 0.2)
        luz_area((W / 2, D / 2, H - 0.02), (0, 0, 0), 0.08, 160, color=(1, 0.8, 0.6), tam_y=D - 0.6)
        luz_area((W / 2, D / 2, H - 0.1), (0, 0, 0), 2.0, 70, color=(1, 0.86, 0.7))
        bpy.ops.object.light_add(type='SPOT', location=(W / 2, D / 2, H - 0.05))
        s = bpy.context.active_object
        s.data.energy = 220
        s.data.spot_size = math.radians(55)
        s.data.spot_blend = 0.7
        s.data.color = (1, 0.82, 0.6)
    return W, D, H


# ---------------------------------------------------------------- baño de tadelakt
def bano():
    M = materiales()
    W, D, H = 3.4, 4.2, 3.0
    caja('piso', (W / 2, D / 2, -0.05), (W + 1, D + 1, 0.1), M['travertino_piso'])
    caja('techo', (W / 2, D / 2, H + 0.05), (W, D, 0.1), M['yeso'])
    caja('muro_fondo', (W / 2, D + 0.1, H / 2), (W, 0.2, H), M['tadelakt'])
    caja('muro_izq', (-0.1, D / 2, H / 2), (0.2, D, H), M['tadelakt'])
    caja('muro_der', (W + 0.1, D / 2, H / 2), (0.2, D, H), M['tadelakt'])
    caja('muro_frente', (W / 2, -0.6, H / 2), (W, 0.2, H), M['tadelakt'])
    # Tina exenta de piedra
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.5, depth=0.55, location=(1.15, D - 1.0, 0.275))
    t = bpy.context.active_object
    t.scale = (1.0, 1.7, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    mod = t.modifiers.new('bisel', 'BEVEL')
    mod.width = 0.06
    mod.segments = 6
    bpy.ops.object.shade_smooth()
    t.data.materials.append(M['travertino'])
    # Vaciado interior de la tina
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.42, depth=0.6, location=(1.15, D - 1.0, 0.6))
    hueco = bpy.context.active_object
    hueco.scale = (1.0, 1.75, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    boo = t.modifiers.new('vaciado', 'BOOLEAN')
    boo.object = hueco
    boo.operation = 'DIFFERENCE'
    t.modifiers.move(len(t.modifiers) - 1, 0)
    hueco.hide_render = True
    agua = material_liso('agua', (0.75, 0.8, 0.78), rough=0.02, transmision=0.9)
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.41, depth=0.02, location=(1.15, D - 1.0, 0.44))
    a = bpy.context.active_object
    a.scale = (1.0, 1.75, 1.0)
    a.data.materials.append(agua)
    cilindro('llave_tina', (0.35, D - 1.0, 0.5), 0.016, 1.0, M['bronce'], verts=24)
    cilindro('caño_tina', (0.45, D - 1.0, 0.98), 0.014, 0.22, M['bronce'], rot=(0, math.radians(90), 0), verts=24)
    # Nicho con luz
    caja('nicho', (1.15, D - 0.02, 1.25), (1.6, 0.06, 0.32), M['travertino'])
    caja('nicho_led', (1.15, D - 0.06, 1.40), (1.5, 0.02, 0.01), M['led'])
    cilindro('vela', (0.75, D - 0.08, 1.16), 0.04, 0.12, M['ceramica_clara'])
    esfera('piedra', (1.5, D - 0.08, 1.13), 0.06, M['ceramica'], escala=(1.4, 1, 0.6))
    # Lavabo volado de nogal con cubierta de travertino
    caja('mueble', (W - 0.28, 1.4, 0.72), (0.52, 1.5, 0.36), M['nogal'], bisel=0.004)
    caja('cubierta', (W - 0.28, 1.4, 0.92), (0.56, 1.54, 0.05), M['travertino'])
    esfera('ovalin', (W - 0.3, 1.4, 1.0), 0.2, M['ceramica_clara'], escala=(1, 1.2, 0.4))
    cilindro('grifo', (W - 0.03, 1.4, 1.25), 0.013, 0.22, M['bronce'], rot=(0, math.radians(90), 0), verts=24)
    caja('led_mueble', (W - 0.28, 1.4, 0.535), (0.45, 1.4, 0.01), M['led'])
    # Espejo redondo con marco de bronce
    cilindro('marco', (W - 0.012, 1.4, 1.75), 0.42, 0.02, M['bronce'], rot=(0, math.radians(90), 0))
    cilindro('espejo', (W - 0.025, 1.4, 1.75), 0.40, 0.02, material_liso('espejo', (0.92, 0.92, 0.92), rough=0.02, metal=1), rot=(0, math.radians(90), 0))
    # Toalla y banco
    caja('banco', (0.45, 1.0, 0.22), (0.4, 0.6, 0.44), M['nogal'], bisel=0.01)
    caja('toalla', (0.45, 1.0, 0.47), (0.32, 0.4, 0.06), M['tela'], bisel=0.02)
    # Luz natural cenital (tragaluz) y cálida
    caja('tragaluz', (1.15, D - 1.0, H - 0.001), (1.2, 0.8, 0.01), material_liso('cielo', (1, 1, 1), emision=(1, 0.97, 0.92), fuerza=1.5))
    luz_area((1.15, D - 1.0, H - 0.03), (0, 0, 0), 1.2, 110, color=(1, 0.95, 0.88), tam_y=0.8)
    luz_area((W / 2, 1.0, H - 0.05), (0, 0, 0), 1.0, 15, color=(1, 0.85, 0.65))
    mundo((0.05, 0.05, 0.06), 0.3)
    return W, D, H


# ---------------------------------------------------------------- vistas
def v_cocina_general(noche=False):
    W, D, H, ix, iy = cocina(noche)
    camara((0.5, 0.3, 1.35), (4.6, 4.4, 1.35), lente=19, foco=4.0, f_stop=8, shift_y=-0.12)


def v_cocina_isla():
    W, D, H, ix, iy = cocina(False)
    camara((ix + 2.5, iy - 2.0, 1.3), (ix + 0.4, iy + 0.3, 0.8), lente=30, foco=2.7, f_stop=4, nivel=False)


def v_cocina_frontal():
    W, D, H, ix, iy = cocina(False)
    camara((3.4, 0.2, 1.3), (3.4, D, 1.3), lente=20, foco=5.0, f_stop=8, shift_y=-0.05)


def v_cocina_ventana():
    W, D, H, ix, iy = cocina(False)
    camara((0.9, 5.1, 1.35), (W, 1.7, 1.35), lente=20, foco=3.2, f_stop=6, shift_y=-0.08)


def v_cocina_detalle():
    W, D, H, ix, iy = cocina(False)
    camara((2.75, D - 1.75, 1.55), (3.7, D - 0.1, 1.0), lente=34, foco=1.8, f_stop=3.2, nivel=False)


def v_cocina_noche():
    v_cocina_general(noche=True)


def v_cocina_noche_isla():
    W, D, H, ix, iy = cocina(True)
    camara((ix - 2.4, iy - 2.3, 1.3), (ix, iy + 0.3, 1.3), lente=24, foco=3.2, f_stop=4, shift_y=-0.1)


def v_vestidor_general():
    W, D, H = vestidor(True)
    camara((W / 2, 0.2, 1.4), (W / 2, D, 1.4), lente=19, foco=2.8, f_stop=6, shift_y=-0.06)


def v_vestidor_lateral():
    W, D, H = vestidor(True)
    camara((W / 2 - 0.6, 0.9, 1.4), (W - 0.3, 3.8, 1.4), lente=24, foco=2.4, f_stop=4)


def v_vestidor_isla():
    W, D, H = vestidor(True)
    camara((W / 2 + 0.9, D / 2 - 1.4, 1.5), (W / 2, D / 2 - 0.1, 0.9), lente=32, foco=1.7, f_stop=3.5, nivel=False)


def v_bano_tadelakt():
    W, D, H = bano()
    camara((2.05, -0.3, 1.3), (1.0, D, 1.3), lente=22, foco=3.6, f_stop=6, shift_y=-0.1)


def v_bano_tina():
    W, D, H = bano()
    camara((2.3, D - 2.6, 1.15), (1.15, D - 0.8, 0.7), lente=30, foco=2.1, f_stop=3.5, nivel=False)


def v_cocina_repisa():
    W, D, H, ix, iy = cocina(False)
    camara((6.0, D - 2.9, 1.5), (4.3, D, 1.45), lente=30, foco=3.0, f_stop=4, shift_y=-0.04)


def v_bano_lavabo():
    W, D, H = bano()
    camara((1.2, 1.0, 1.45), (W, 1.4, 1.2), lente=30, foco=2.0, f_stop=3.5, nivel=False)


def v_bano_nicho():
    W, D, H = bano()
    camara((1.9, 0.6, 1.25), (1.0, D, 1.25), lente=34, foco=3.3, f_stop=4, shift_y=-0.05)


VISTAS = {
    'bano-lavabo': v_bano_lavabo,
    'bano-nicho': v_bano_nicho,
    'bano-tadelakt': v_bano_tadelakt,
    'bano-tina': v_bano_tina,
    'cocina-repisa': v_cocina_repisa,
    'cocina-general': v_cocina_general,
    'cocina-isla': v_cocina_isla,
    'cocina-frontal': v_cocina_frontal,
    'cocina-ventana': v_cocina_ventana,
    'cocina-detalle': v_cocina_detalle,
    'cocina-noche': v_cocina_noche,
    'cocina-noche-isla': v_cocina_noche_isla,
    'vestidor-general': v_vestidor_general,
    'vestidor-lateral': v_vestidor_lateral,
    'vestidor-isla': v_vestidor_isla,
}


def main():
    args = sys.argv[1:]
    if '--' in args:
        args = args[args.index('--') + 1:]
    salida = args[0]
    vistas = args[1:] or list(VISTAS)
    muestras = int(os.environ.get('MUESTRAS', '128'))
    os.makedirs(salida, exist_ok=True)
    for v in vistas:
        limpiar()
        VISTAS[v]()
        ajustes(muestras)
        bpy.context.scene.render.filepath = os.path.join(salida, f'render-{v}.jpg')
        bpy.ops.render.render(write_still=True)
        print('OK', v, flush=True)


if __name__ == '__main__':
    main()
