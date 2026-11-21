# bee_gif.py - Bee-only wrapper around the shared _common/anim_gif.py (read-only, NOT edited; pattern of Duck/swim_gif.py).
#   PYTHONUTF8=1 blender --background --factory-startup --python bee_gif.py -- Bee Fly On_Flower [anim_gif options]
# anim_gif.py ends with a module-level main(); its source is executed here WITHOUT that last call, then:
#  - Fly:       the camera fit also gets the sun-shadow footprint of the bee on z = 0, so the hovering bee (Root +0.10 m)
#               and its shadow are both in frame; sun 25 deg from vertical (pack: 48) keeps the shadow under the bee.
#  - On_Flower: the bee stands on a flower prop: flat centre disc (top 0.4 mm under the soles at z = 0), 10 white petals,
#               green stem down to the meadow, which is lowered to z = -FLOWER_H. The fit also gets the flower centre rim.
# Same lights, sky, GIF settings and output path (art/Farm_Animals/Previews/Anim/Bee_<Clip>.gif) as every other clip.
import os, sys, math
import bpy
from mathutils import Vector

REPO = r'C:\Users\Sergv\orca\workspaces\VFX\master-3'
SRC = os.path.join(REPO, '.work', 'models', 'Farm_Animals', '_common', 'anim_gif.py')
FLOWER_H, DISC_R, DISC_T, PETAL_R0, PETAL_R1, PETALS = 0.075, 0.036, 0.006, 0.030, 0.068, 10

code = open(SRC, encoding='utf-8').read().rstrip()
assert code.endswith('main()'), 'anim_gif.py layout changed'
ns = {'__file__': SRC, '__name__': 'anim_gif_lib'}
exec(compile(code[:-len('main()')], SRC, 'exec'), ns)
rn = ns['rn']; CUR = {'clip': None}


class RnProxy:
    """animal_render with mesh_points extended by clip-specific extra points (shadow / flower); everything else delegated"""
    def __getattr__(self, k):
        return getattr(rn, k)

    def mesh_points(self, objs):
        pts = rn.mesh_points(objs)
        if CUR['clip'] == 'Fly':
            sun = bpy.data.objects.get('TMP_Sun')
            sd = (sun.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()
            pts = pts + [p - sd * (p.z / sd.z) for p in pts[::4]]
        elif CUR['clip'] == 'On_Flower':
            pts = pts + [Vector((DISC_R * 1.15 * math.cos(a), DISC_R * 1.15 * math.sin(a), -DISC_T)) for a in
                         [2 * math.pi * k / 16 for k in range(16)]]
        return pts


ns['rn'] = RnProxy()
_meadow = ns['meadow']


def _obj(name, mat_hex, op, **kw):
    old = bpy.data.objects.get(name)
    if old: bpy.data.objects.remove(old, do_unlink=True)
    op(**kw); ob = bpy.context.active_object; ob.name = name
    ob.data.materials.clear(); ob.data.materials.append(rn._solid_mat(name + '_M', mat_hex))
    return ob


def flower_scene(sc, size):
    _meadow(sc, size)
    bpy.data.objects['TMP_Meadow'].location.z = -FLOWER_H
    cyl = bpy.ops.mesh.primitive_cylinder_add
    _obj('TMP_FlowerStem', '#5E8F3C', cyl, vertices=8, radius=0.0035, depth=FLOWER_H - DISC_T, location=(0, 0.004, -(FLOWER_H + DISC_T) / 2))
    _obj('TMP_FlowerDisc', '#C9742C', cyl, vertices=16, radius=DISC_R, depth=DISC_T, location=(0, 0, -0.0004 - DISC_T / 2))
    for k in range(PETALS):
        a = 2 * math.pi * (k + 0.5) / PETALS; r = (PETAL_R0 + PETAL_R1) / 2; L = (PETAL_R1 - PETAL_R0) / 2
        _obj(f'TMP_Petal{k}', '#F4F1EA', cyl, vertices=10, radius=1.0, depth=1.0,
             location=(r * math.cos(a), r * math.sin(a), -0.0035), rotation=(0, 0, a), scale=(L, 0.0115, 0.0018))
    print('FLOWER prop: disc r', DISC_R, 'top z', -0.0004, 'petals', PETALS, 'to r', PETAL_R1, 'meadow z', -FLOWER_H)


def meadow(sc, size):
    (flower_scene if CUR['clip'] == 'On_Flower' else _meadow)(sc, size)


ns['meadow'] = meadow
sys.argv = [sys.argv[0], '--'] + (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['Bee', 'Fly', 'On_Flower'])
o = ns['parse'](); sc = bpy.context.scene; ns['_clear_scene'](sc)
sc.render.fps, sc.render.fps_base = 30, 1.0
m = ns['load_blend'](o['name'], sc) or ns['load_fbx'](o['name'], sc)
ns['environment'](sc)
SUN_FLY = (25, 0, -35)               # Fly only: steeper sun than the pack's (48, 0, -35) so the shadow stays near the bee
for clip in o['clips']:
    CUR['clip'] = clip
    sun = bpy.data.objects['TMP_Sun']
    sun.rotation_euler = [math.radians(a) for a in (SUN_FLY if clip == 'Fly' else (48, 0, -35))]
    ns['render_clip'](o, sc, m[0], m[1], clip)
