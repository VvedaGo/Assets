# Preview render template (proven on the MarketFarm tractor). Copy next to the build script, edit the CONFIG block,
# run with execute_blender_code: exec(open(path).read()). Temp camera/lights/world are removed afterwards.
# Output: 1280x800 PNG, EEVEE, Standard view transform, light-grey backdrop (visible only to camera rays,
# lighting comes from sun + fill + soft ambient), model auto-fitted to FILL_W of the frame width and centred.
import bpy, math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

# ---------------- CONFIG ----------------
SCENE_NAME = 'FMS_Workshop_STA_08_Build'   # build scene (only this asset; the user's scene/Cube untouched)
COLLECTION = 'FMS_Workshop_STA_08'
OUT = globals().get('OUT', r"C:\Users\Sergv\orca\workspaces\VFX\master-2\art\Farm_Processing\Previews\FMS_Workshop_STA_08_Preview.png")
FILL_W = 0.68                       # model width as a share of frame width (0.65-0.70)
LOOK_AT = (0.0, 0.0, 0.80)          # target point ~ model centre (x, y, z) in metres
VIEW_DIR = globals().get('VIEW_DIR', (-0.36, -1.0, 0.42))   # like the reference: front, camera on the -X side, slightly above
BG_HEX = (0xc7, 0xcc, 0xd3)         # backdrop colour, same as the other pack previews
SKIP_SUFFIX = ('_LOD1', '_LOD2', '_Col')
# ----------------------------------------

sc = bpy.data.scenes[SCENE_NAME]
r = sc.render
saved = dict(engine=r.engine, rx=r.resolution_x, ry=r.resolution_y, pct=r.resolution_percentage, fp=r.filepath,
             vt=sc.view_settings.view_transform, cam=sc.camera, world=sc.world, ft=r.film_transparent)
try:
    r.engine = 'BLENDER_EEVEE'
except TypeError:
    r.engine = 'BLENDER_EEVEE_NEXT'          # the error message lists valid engines; Blender 4.2-4.x name
rx,ry=globals().get('RES',(1280,800))
r.resolution_x, r.resolution_y, r.resolution_percentage = rx, ry, 100
r.film_transparent = False
sc.view_settings.view_transform = 'Standard'

lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
w = bpy.data.worlds.new('TMP_World'); w.use_nodes = True
nt = w.node_tree
out = next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD')
bg = next(n for n in nt.nodes if n.type == 'BACKGROUND')
bg.inputs['Color'].default_value = (lin(BG_HEX[0]), lin(BG_HEX[1]), lin(BG_HEX[2]), 1)
amb = nt.nodes.new('ShaderNodeBackground')
amb.inputs['Color'].default_value = (0.82, 0.86, 0.95, 1); amb.inputs['Strength'].default_value = 0.45
lp = nt.nodes.new('ShaderNodeLightPath'); mix = nt.nodes.new('ShaderNodeMixShader')
nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs[0])       # camera sees BG, lighting uses ambient
nt.links.new(amb.outputs[0], mix.inputs[1]); nt.links.new(bg.outputs[0], mix.inputs[2])
nt.links.new(mix.outputs[0], out.inputs['Surface'])
sc.world = w

def sun(name, rot, e, shadow=True, ang=10):
    ld = bpy.data.lights.new(name, 'SUN'); ld.energy = e; ld.angle = math.radians(ang); ld.use_shadow = shadow
    ob = bpy.data.objects.new(name, ld); ob.rotation_euler = [math.radians(a) for a in rot]
    sc.collection.objects.link(ob); return ob
s1 = sun('TMP_Sun', (45, 0, -30), 3.4)
s2 = sun('TMP_Fill', (70, 0, 160), 0.9, shadow=False)

cd = bpy.data.cameras.new('TMP_Cam'); cd.lens = 70
cam = bpy.data.objects.new('TMP_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam
target = Vector(LOOK_AT); dirv = Vector(VIEW_DIR).normalized()
objs = [o for o in bpy.data.collections[COLLECTION].all_objects if o.type == 'MESH' and not o.name.endswith(SKIP_SUFFIX)]
pts = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]

def place(d):
    cam.location = target + dirv * d
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    xs = [world_to_camera_view(sc, cam, p) for p in pts]
    return min(p.x for p in xs), max(p.x for p in xs), min(p.y for p in xs), max(p.y for p in xs)

cd.shift_x = cd.shift_y = 0.0
d = 6.0
for _ in range(25):                              # converge distance: width = FILL_W, height <= 0.92
    x0, x1, y0, y1 = place(d); d *= max((x1 - x0) / FILL_W, (y1 - y0) / 0.88)
x0, x1, y0, y1 = place(d)
cd.shift_x = ((x0 + x1) / 2 - 0.5); cd.shift_y = ((y0 + y1) / 2 - 0.5) * (ry / rx)   # centre in frame
x0, x1, y0, y1 = place(d)
print('dist', round(d, 2), 'frame x', round(x0, 3), round(x1, 3), 'y', round(y0, 3), round(y1, 3))
r.filepath = OUT
r.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True, scene=sc.name)

for ob in (s1, s2):                              # cleanup: leave the scene exactly as found
    dat = ob.data; bpy.data.objects.remove(ob, do_unlink=True); bpy.data.lights.remove(dat)
dat = cam.data; bpy.data.objects.remove(cam, do_unlink=True); bpy.data.cameras.remove(dat)
sc.world = saved['world']; bpy.data.worlds.remove(w)
r.engine = saved['engine']; r.resolution_x, r.resolution_y, r.resolution_percentage = saved['rx'], saved['ry'], saved['pct']
r.filepath = saved['fp']; sc.view_settings.view_transform = saved['vt']; sc.camera = saved['cam']; r.film_transparent = saved['ft']
print('left over TMP:', [o.name for o in bpy.data.objects if o.name.startswith('TMP_')])

