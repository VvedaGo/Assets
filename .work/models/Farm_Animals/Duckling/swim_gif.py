# swim_gif.py - Duckling copy of ../Duck/swim_gif.py (read-only): wrapper around the shared _common/anim_gif.py (NOT edited),
# renders Duckling_Swim with a flat translucent water plane instead of the meadow, so the paddling legs show through it.
#   PYTHONUTF8=1 blender --background --factory-startup --python swim_gif.py -- Duckling Swim
# Duckling numbers: WATER_Z 0.050 m (~55 % up the body: belly 0.016 .. back ~0.08 m), pond floor 0.06 m below the root.
# anim_gif.py ends with a module-level main(); its source is executed here WITHOUT that last call, then meadow() is swapped
# for water(): light-blue disc at WATER_Z (55 % up the body: belly 0.077 .. back 0.265 m), alpha-blended, plus a darker
# pond floor below. Same camera, lights, sky, GIF settings and output path as every other clip.
import os, sys, math
import bpy

REPO = r'D:\GitProjects\Assets_Farm'
SRC = os.path.join(REPO, '.work', 'models', 'Farm_Animals', '_common', 'anim_gif.py')
WATER_Z = 0.050
FLOOR_Z = -0.06

code = open(SRC, encoding='utf-8').read().rstrip()
assert code.endswith('main()'), 'anim_gif.py layout changed'
ns = {'__file__': SRC, '__name__': 'anim_gif_lib'}
exec(compile(code[:-len('main()')], SRC, 'exec'), ns)
rn = ns['rn']


def _disc(name, z, R, hexcol, alpha=None):
    old = bpy.data.objects.get(name)
    if old: bpy.data.objects.remove(old, do_unlink=True)
    n = 48; me = bpy.data.meshes.new(name)
    me.from_pydata([(0, 0, z)] + [(R * math.cos(2 * math.pi * k / n), R * math.sin(2 * math.pi * k / n), z) for k in range(n)], [],
                   [(0, k + 1, (k + 1) % n + 1) for k in range(n)])
    m = rn._solid_mat(name + '_M', hexcol)
    if alpha is not None:
        b = next(x for x in m.node_tree.nodes if x.type == 'BSDF_PRINCIPLED')
        b.inputs['Alpha'].default_value = alpha; b.inputs['Roughness'].default_value = 0.35
        try: m.surface_render_method = 'BLENDED'
        except (AttributeError, TypeError): m.blend_method = 'BLEND'
        m.use_backface_culling = False
    me.materials.append(m)
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    return ob


def water(sc, size):
    R = max(60.0, size * 40)
    _disc('TMP_Meadow', FLOOR_Z, R, '#5E8E95')                 # pond floor (named like the meadow so it gets replaced)
    _disc('TMP_Water', WATER_Z, R, '#8EC8E2', alpha=0.55)


ns['meadow'] = water
sys.argv = [sys.argv[0], '--'] + (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['Duckling', 'Swim'])
ns['main']()
