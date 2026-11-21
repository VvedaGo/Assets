# ladybug_gif.py - Ladybug wrapper around the shared _common/anim_gif.py (read-only, NOT edited; copy of Butterfly/butterfly_gif.py
# without the flower prop).
#   PYTHONUTF8=1 blender --background --factory-startup --python ladybug_gif.py -- Ladybug Idle Crawl Fly
#  - Fly: the camera fit also gets the sun-shadow footprint on z = 0, so the hovering ladybug (Root +0.045 m) and its
#         shadow are both in frame; sun 8 deg from vertical keeps the shadow under the butterfly.
#  - other clips: unchanged pack look (sun 48 deg).
import os, sys, math
import bpy
from mathutils import Vector

REPO = r'D:\GitProjects\Assets_Farm'
SRC = os.path.join(REPO, '.work', 'models', 'Farm_Animals', '_common', 'anim_gif.py')

code = open(SRC, encoding='utf-8').read().rstrip()
assert code.endswith('main()'), 'anim_gif.py layout changed'
ns = {'__file__': SRC, '__name__': 'anim_gif_lib'}
exec(compile(code[:-len('main()')], SRC, 'exec'), ns)
rn = ns['rn']; CUR = {'clip': None}


class RnProxy:
    def __getattr__(self, k):
        return getattr(rn, k)

    def mesh_points(self, objs):
        pts = rn.mesh_points(objs)
        if CUR['clip'] == 'Fly':
            sun = bpy.data.objects.get('TMP_Sun')
            sd = (sun.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()
            pts = pts + [p - sd * (p.z / sd.z) for p in pts[::4]]
        return pts


ns['rn'] = RnProxy()
sys.argv = [sys.argv[0], '--'] + (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['Ladybug', 'Idle', 'Crawl', 'Fly'])
o = ns['parse'](); sc = bpy.context.scene; ns['_clear_scene'](sc)
sc.render.fps, sc.render.fps_base = 30, 1.0
m = ns['load_blend'](o['name'], sc) or ns['load_fbx'](o['name'], sc)
ns['environment'](sc)
for clip in o['clips']:
    CUR['clip'] = clip
    sun = bpy.data.objects['TMP_Sun']
    sun.rotation_euler = [math.radians(a) for a in ((8, 0, -35) if clip == 'Fly' else (48, 0, -35))]
    ns['render_clip'](o, sc, m[0], m[1], clip)
