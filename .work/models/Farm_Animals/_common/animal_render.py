# animal_render.py - check renders for the Farm Animals pack (Workbench tiles, contact sheets, frame strips) and the
# EEVEE preview (one frame, sky + meadow ground, no text). Check images go to %TEMP%/FarmAnimals_check only.
import bpy, math, os
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check')
REF_VIEW = (1.0, -0.42, 0.30)          # reference LIV-01: near (left, +X) side from the front-left, slightly above


def _lin(h):
    c = int(h, 16) / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _solid_mat(name, hexcol):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    rgb = tuple(_lin(hexcol[i:i + 2]) for i in (1, 3, 5))
    b.inputs['Base Color'].default_value = rgb + (1,); b.inputs['Roughness'].default_value = 1.0
    m.diffuse_color = rgb + (1,)
    return m


def ground(sc, size=12.0, hexcol='#9AA08F', name='TMP_Ground'):
    me = bpy.data.meshes.new(name)
    s = size / 2
    me.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
    me.materials.append(_solid_mat(name + '_M', hexcol))
    ob = bpy.data.objects.new(name, me); sc.collection.objects.link(ob)
    return ob


def setup_workbench(sc, w=640, h=400):
    try:
        sc.render.engine = 'BLENDER_WORKBENCH'
    except TypeError as e:
        print('engine', e)
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = w, h, 100
    sc.render.film_transparent = False
    sh = sc.display.shading
    sh.light = 'STUDIO'; sh.color_type = 'TEXTURE'; sh.show_shadows = True; sh.shadow_intensity = 0.35
    sh.show_cavity = False
    sc.display.light_direction = (0.45, -0.35, 0.82)
    if sc.world is None: sc.world = bpy.data.worlds.new('TMP_CheckWorld')
    sc.world.color = (0.62, 0.66, 0.72)
    sc.view_settings.view_transform = 'Standard'
    sc.render.image_settings.file_format = 'PNG'


def camera(sc, name='TMP_Cam', lens=50):
    cd = bpy.data.cameras.get(name) or bpy.data.cameras.new(name); cd.lens = lens
    cam = bpy.data.objects.get(name) or bpy.data.objects.new(name, cd)
    if cam.name not in sc.collection.objects: sc.collection.objects.link(cam)
    sc.camera = cam
    return cam


def fit(sc, cam, pts, view, fill=(0.86, 0.86), target=None):
    """place cam along view (target->eye) so pts fill the frame; returns distance"""
    lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
    tgt = Vector(target) if target else (lo + hi) / 2
    dirv = Vector(view).normalized(); cd = cam.data; cd.shift_x = cd.shift_y = 0.0
    asp = sc.render.resolution_y / sc.render.resolution_x

    def place(d):
        cam.location = tgt + dirv * d
        cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
        bpy.context.view_layer.update()
        xs = [world_to_camera_view(sc, cam, p) for p in pts]
        return min(p.x for p in xs), max(p.x for p in xs), min(p.y for p in xs), max(p.y for p in xs)
    d = 6.0
    for _ in range(20):
        x0, x1, y0, y1 = place(d); d *= max((x1 - x0) / fill[0], (y1 - y0) / fill[1])
    x0, x1, y0, y1 = place(d)
    cd.shift_x = (x0 + x1) / 2 - 0.5; cd.shift_y = ((y0 + y1) / 2 - 0.5) * asp
    place(d)
    return d


def mesh_points(objs):
    dg = bpy.context.evaluated_depsgraph_get(); pts = []
    for o in objs:
        oe = o.evaluated_get(dg); me = oe.to_mesh()
        pts += [o.matrix_world @ v.co for v in me.vertices]
        oe.to_mesh_clear()
    return pts


def render_to(sc, path):
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True, scene=sc.name)
    return path


def load_px(path):
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    a = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    bpy.data.images.remove(img)
    return a


def resize(a, h):
    """nearest-neighbour resize to height h (keeps aspect)"""
    H, W = a.shape[:2]; w = max(1, round(W * h / H))
    yi = (np.arange(h) * H / h).astype(int); xi = (np.arange(w) * W / w).astype(int)
    return a[yi][:, xi]


def compose(tiles, cols, out, pad=4):
    """tiles: list of arrays (bottom-up rows as from Blender); saved as one PNG"""
    h = max(t.shape[0] for t in tiles); w = max(t.shape[1] for t in tiles)
    rows = (len(tiles) + cols - 1) // cols
    canvas = np.ones(((h + pad) * rows + pad, (w + pad) * cols + pad, 4), dtype=np.float32)
    canvas[..., :3] = 0.25
    for i, t in enumerate(tiles):
        r, c = divmod(i, cols); rr = rows - 1 - r
        y0 = pad + rr * (h + pad); x0 = pad + c * (w + pad)
        canvas[y0:y0 + t.shape[0], x0:x0 + t.shape[1]] = t
    H, W = canvas.shape[:2]
    img = bpy.data.images.new('TMP_Sheet', W, H, alpha=True)
    img.pixels.foreach_set(canvas.ravel())
    img.filepath_raw = out; img.file_format = 'PNG'; img.save()
    bpy.data.images.remove(img)
    print('sheet', out)
    return out


def ref_tile(ref_path, h):
    a = load_px(ref_path)
    return resize(a, h)


def preview(sc, objs, out, view=(1.0, -0.62, 0.34), fill=(0.70, 0.80), lens=50):
    """EEVEE 1280x800, three-quarter front-left; camera-visible sky gradient + meadow ground disc, sun + fill."""
    r = sc.render
    try:
        r.engine = 'BLENDER_EEVEE'
    except TypeError:
        r.engine = 'BLENDER_EEVEE_NEXT'
    r.resolution_x, r.resolution_y, r.resolution_percentage = 1280, 800, 100
    r.film_transparent = False; sc.view_settings.view_transform = 'Standard'
    w = bpy.data.worlds.new('TMP_PreviewWorld'); w.use_nodes = True; nt = w.node_tree
    out_n = next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD'); bg = next(n for n in nt.nodes if n.type == 'BACKGROUND')
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[0].color = (_lin('e3'), _lin('ec'), _lin('f2'), 1)
    ramp.color_ramp.elements[1].position = 0.45; ramp.color_ramp.elements[1].color = (_lin('86'), _lin('b4'), _lin('de'), 1)
    nt.links.new(tc.outputs['Generated'], sep.inputs[0]); nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
    amb = nt.nodes.new('ShaderNodeBackground'); amb.inputs['Color'].default_value = (0.80, 0.86, 0.96, 1)
    amb.inputs['Strength'].default_value = 0.55
    lp = nt.nodes.new('ShaderNodeLightPath'); mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs[0]); nt.links.new(amb.outputs[0], mix.inputs[1])
    nt.links.new(bg.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], out_n.inputs['Surface'])
    old_world = sc.world; sc.world = w
    # meadow ground: big disc, soft green, fades into the horizon haze
    me = bpy.data.meshes.new('TMP_Meadow'); n = 48; R = 60.0
    me.from_pydata([(0, 0, 0)] + [(R * math.cos(2 * math.pi * k / n), R * math.sin(2 * math.pi * k / n), 0) for k in range(n)], [],
                   [(0, k + 1, (k + 1) % n + 1) for k in range(n)])
    me.materials.append(_solid_mat('TMP_Meadow_M', '#93AE6E'))
    gob = bpy.data.objects.new('TMP_Meadow', me); sc.collection.objects.link(gob)
    lights = []
    for nm, rot, e, sh in (('TMP_Sun', (48, 0, -35), 3.6, True), ('TMP_Fill', (70, 0, 160), 0.9, False)):
        ld = bpy.data.lights.new(nm, 'SUN'); ld.energy = e; ld.angle = math.radians(8); ld.use_shadow = sh
        ob = bpy.data.objects.new(nm, ld); ob.rotation_euler = [math.radians(a) for a in rot]
        sc.collection.objects.link(ob); lights.append(ob)
    cam = camera(sc, 'TMP_PrevCam', lens)
    pts = mesh_points(objs)
    fit(sc, cam, pts, view, fill)
    r.filepath = out; r.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True, scene=sc.name)
    for ob in lights + [gob, cam]:
        d = ob.data; bpy.data.objects.remove(ob, do_unlink=True)
        if isinstance(d, bpy.types.Light): bpy.data.lights.remove(d)
        elif isinstance(d, bpy.types.Camera): bpy.data.cameras.remove(d)
        elif isinstance(d, bpy.types.Mesh): bpy.data.meshes.remove(d)
    sc.world = old_world; bpy.data.worlds.remove(w)
    print('preview', out)
