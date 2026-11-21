# fly_gif.py - bird Fly wrapper around the shared _common/anim_gif.py (read-only, NOT edited; pattern of Bee/bee_gif.py).
#   PYTHONUTF8=1 blender --background --factory-startup --python fly_gif.py -- <Name> Fly [anim_gif options]
# anim_gif.py ends with a module-level main(); its source is executed here WITHOUT that last call, then for the Fly clip:
#  - the camera fit also gets the sun-shadow footprint of the bird on z = 0, so the flying bird (body lifted in the clip)
#    and its shadow are both in frame; the sun is steeper (22 deg from vertical, pack: 48) so the shadow stays near the bird.
# Same lights, sky, meadow, GIF settings and output path (art/Farm_Animals/Previews/Anim/<Name>_Fly.gif) as every clip.
# Used by Pigeon, Sparrow (and later Crow).
import os, sys, math
import bpy
from mathutils import Vector

REPO = r'C:\Users\Sergv\orca\workspaces\VFX\master-3'
SRC = os.path.join(REPO, '.work', 'models', 'Farm_Animals', '_common', 'anim_gif.py')
SUN_FLY = (22, 0, -35)

code = open(SRC, encoding='utf-8').read().rstrip()
assert code.endswith('main()'), 'anim_gif.py layout changed'
ns = {'__file__': SRC, '__name__': 'anim_gif_lib'}
exec(compile(code[:-len('main()')], SRC, 'exec'), ns)
rn = ns['rn']


class RnProxy:
    """animal_render with mesh_points extended by the sun-shadow footprint on the ground; everything else delegated"""
    def __getattr__(self, k):
        return getattr(rn, k)

    def mesh_points(self, objs):
        pts = rn.mesh_points(objs)
        sun = bpy.data.objects.get('TMP_Sun')
        sd = (sun.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()
        return pts + [p - sd * (p.z / sd.z) for p in pts[::4]]


ns['rn'] = RnProxy()
sys.argv = [sys.argv[0], '--'] + (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['Pigeon', 'Fly'])
o = ns['parse'](); sc = bpy.context.scene; ns['_clear_scene'](sc)
sc.render.fps, sc.render.fps_base = 30, 1.0
m = ns['load_blend'](o['name'], sc) or ns['load_fbx'](o['name'], sc)
ns['environment'](sc)
bpy.data.objects['TMP_Sun'].rotation_euler = [math.radians(a) for a in SUN_FLY]
for clip in o['clips']:
    ns['render_clip'](o, sc, m[0], m[1], clip)
