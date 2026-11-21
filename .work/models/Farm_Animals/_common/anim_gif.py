# anim_gif.py - render animation clips of a Farm Animals model to looping GIFs (headless Blender 5.2 + ffmpeg).
# Owner: Cow pilot (model-artist). Other agents RUN it, do not edit it; keep this CLI stable:
#   PYTHONUTF8=1 blender --background --factory-startup --python anim_gif.py -- <Name> <Clip> [<Clip> ...]
#        [--size 640 400] [--gif-fps 20] [--view 1.0 -0.55 0.17] [--fill 0.66] [--mp4] [--keep-frames]
# Output: art/Farm_Animals/Previews/Anim/<Name>_<Clip>.gif  (palettegen/paletteuse, no dithering, loops forever,
#         kept under ~4 MB: width then fps reduced if needed, printed). --mp4 also writes <Name>_<Clip>.mp4 (H.264 yuv420p 30 fps).
# Model: armature + meshes appended from art/Farm_Animals/Blend/FMS_<Name>.blend (collection FMS_<Name>, or any collection
#        holding an armature) with actions <Name>_<Clip>; if the .blend has no rig, art/Farm_Animals/Meshes/FMS_<Name>.fbx is
#        imported instead (takes "<obj>|<Name>_<Clip>" are matched by suffix).
# Look:  pack preview setup (EEVEE, low 3/4 front-left view, sun + fill, sky gradient + meadow horizon), ONE fixed camera
#        per clip fitted to the animal over ALL frames (any size/aspect), animal ~66% of the width.
# Loops: action.use_cyclic or first pose == last pose -> frames f0..f1-1 rendered, GIF shows 2 passes; one-shot clips once.
# Frames: %TEMP%/FarmAnimals_gif/<Name>_<Clip>/ (deleted afterwards); a 4-frame contact sheet (0, 1/4, 1/2, 3/4) stays in
#        %TEMP%/FarmAnimals_gif/<Name>_<Clip>_sheet.png for checking.
import bpy, sys, os, math, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
if HERE not in sys.path: sys.path.insert(0, HERE)
import animal_render as rn          # read-only use: fit, camera, mesh_points, compose, load_px, _lin, _solid_mat

ART = os.path.join(REPO, 'art', 'Farm_Animals')
OUT_DIR = os.path.join(ART, 'Previews', 'Anim')
TMP = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_gif')
GIF_LIMIT = 4.0 * 1024 * 1024


def parse():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    o = dict(name=None, clips=[], size=(640, 400), gif_fps=20, view=(1.0, -0.55, 0.17), fill=0.66, mp4=False, keep=False)
    i = 0
    while i < len(a):
        x = a[i]
        if x == '--size': o['size'] = (int(a[i + 1]), int(a[i + 2])); i += 3
        elif x == '--gif-fps': o['gif_fps'] = int(a[i + 1]); i += 2
        elif x == '--view': o['view'] = tuple(float(v) for v in a[i + 1:i + 4]); i += 4
        elif x == '--fill': o['fill'] = float(a[i + 1]); i += 2
        elif x == '--mp4': o['mp4'] = True; i += 1
        elif x == '--keep-frames': o['keep'] = True; i += 1
        elif x.startswith('--'): raise SystemExit('unknown option ' + x)
        elif o['name'] is None: o['name'] = x; i += 1
        else: o['clips'].append(x); i += 1
    if not o['name'] or not o['clips']:
        raise SystemExit('usage: anim_gif.py -- <Name> <Clip> [<Clip> ...] [--size W H] [--gif-fps F] [--view x y z] [--fill f] [--mp4]')
    return o


# ---------------- model ----------------
def _clear_scene(sc):
    for o in list(sc.objects): bpy.data.objects.remove(o, do_unlink=True)


def load_blend(name, sc):
    path = os.path.join(ART, 'Blend', f'FMS_{name}.blend')
    if not os.path.isfile(path): return None
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.collections = list(src.collections); dst.actions = list(src.actions)
    colls = [c for c in dst.collections if c is not None]
    rigged = [c for c in colls if any(o.type == 'ARMATURE' for o in c.all_objects)]
    if not rigged: return None
    coll = next((c for c in rigged if c.name == f'FMS_{name}'), rigged[0])
    sc.collection.children.link(coll)
    rig = next(o for o in coll.all_objects if o.type == 'ARMATURE')
    meshes = [o for o in coll.all_objects if o.type == 'MESH' and not o.name.endswith(('_LOD1', '_LOD2', '_Col'))]
    print('MODEL from blend', path, 'collection', coll.name, 'rig', rig.name, 'meshes', len(meshes))
    return rig, meshes


def load_fbx(name, sc):
    path = os.path.join(ART, 'Meshes', f'FMS_{name}.fbx')
    if not os.path.isfile(path): raise SystemExit(f'no rigged FMS_{name}.blend and no {path}')
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path, use_anim=True)
    new = [o for o in bpy.data.objects if o not in before]
    rig = next((o for o in new if o.type == 'ARMATURE'), None)
    if rig is None: raise SystemExit(f'{path} has no armature')
    meshes = [o for o in new if o.type == 'MESH' and not o.name.endswith(('_LOD1', '_LOD2', '_Col'))]
    print('MODEL from fbx', path, 'rig', rig.name, 'meshes', len(meshes))
    return rig, meshes


def find_action(name, clip):
    want = f'{name}_{clip}'
    return bpy.data.actions.get(want) or next((a for a in bpy.data.actions if a.name.endswith('|' + want)), None)


def assign(rig, act):
    ad = rig.animation_data or rig.animation_data_create(); ad.action = act
    if getattr(act, 'slots', None) and len(act.slots): ad.action_slot = act.slots[0]


def is_loop(sc, rig, act, f0, f1):
    if act.use_cyclic: return True
    def pose(f):
        sc.frame_set(f); return [pb.matrix_basis.copy() for pb in rig.pose.bones]
    a, b = pose(f0), pose(f1)
    return max(max(abs(x - y) for ra, rb in zip(ma, mb) for x, y in zip(ra, rb)) for ma, mb in zip(a, b)) < 1e-3


# ---------------- look ----------------
def environment(sc):
    """pack preview look (animal_render.preview): EEVEE, sky gradient for camera rays, ambient + sun + fill, meadow"""
    r = sc.render
    try: r.engine = 'BLENDER_EEVEE'
    except TypeError: r.engine = 'BLENDER_EEVEE_NEXT'
    try: sc.eevee.taa_render_samples = 32
    except AttributeError: pass
    r.film_transparent = False; sc.view_settings.view_transform = 'Standard'
    lin = rn._lin
    w = bpy.data.worlds.new('TMP_GifWorld'); w.use_nodes = True; nt = w.node_tree
    out_n = next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD'); bg = next(n for n in nt.nodes if n.type == 'BACKGROUND')
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[0].color = (lin('e3'), lin('ec'), lin('f2'), 1)
    ramp.color_ramp.elements[1].position = 0.45; ramp.color_ramp.elements[1].color = (lin('86'), lin('b4'), lin('de'), 1)
    nt.links.new(tc.outputs['Generated'], sep.inputs[0]); nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
    amb = nt.nodes.new('ShaderNodeBackground'); amb.inputs['Color'].default_value = (0.80, 0.86, 0.96, 1); amb.inputs['Strength'].default_value = 0.55
    lp = nt.nodes.new('ShaderNodeLightPath'); mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs[0]); nt.links.new(amb.outputs[0], mix.inputs[1])
    nt.links.new(bg.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], out_n.inputs['Surface']); sc.world = w
    for nm, rot, e, sh in (('TMP_Sun', (48, 0, -35), 3.6, True), ('TMP_Fill', (70, 0, 160), 0.9, False)):
        ld = bpy.data.lights.new(nm, 'SUN'); ld.energy = e; ld.angle = math.radians(8); ld.use_shadow = sh
        ob = bpy.data.objects.new(nm, ld); ob.rotation_euler = [math.radians(a) for a in rot]; sc.collection.objects.link(ob)


def meadow(sc, size):
    """ground disc scaled to the animal (horizon stays visible for a mouse or a horse)"""
    old = bpy.data.objects.get('TMP_Meadow')
    if old: bpy.data.objects.remove(old, do_unlink=True)
    me = bpy.data.meshes.new('TMP_Meadow'); n = 48; R = max(60.0, size * 40)
    me.from_pydata([(0, 0, 0)] + [(R * math.cos(2 * math.pi * k / n), R * math.sin(2 * math.pi * k / n), 0) for k in range(n)], [],
                   [(0, k + 1, (k + 1) % n + 1) for k in range(n)])
    me.materials.append(rn._solid_mat('TMP_Meadow_M', '#93AE6E'))
    sc.collection.objects.link(bpy.data.objects.new('TMP_Meadow', me))


# ---------------- output ----------------
def ffmpeg(args):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y'] + args, check=True)


def probe(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration,size', '-of', 'default=nw=1', path],
                       capture_output=True, text=True)
    return r.stdout.strip().replace('\n', ' ')


def render_clip(o, sc, rig, meshes, clip):
    name = o['name']; act = find_action(name, clip)
    if act is None:
        print(f'SKIP {name}_{clip}: action not found; have {sorted(a.name for a in bpy.data.actions)}'); return
    assign(rig, act)
    f0, f1 = int(round(act.frame_range[0])), int(round(act.frame_range[1]))
    loop = is_loop(sc, rig, act, f0, f1); last = f1 - 1 if loop else f1
    sc.frame_start, sc.frame_end = f0, last
    W, H = o['size']; sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = W, H, 100
    pts = []
    step = max(1, (last - f0) // 40)
    for f in list(range(f0, last + 1, step)) + [last]:
        sc.frame_set(f); pts += rn.mesh_points(meshes)[::2]
    size = max(max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3))
    meadow(sc, size)
    cam = rn.camera(sc, 'TMP_GifCam', 50)
    d = rn.fit(sc, cam, pts, o['view'], (o['fill'], 0.84))
    cam.data.clip_start = max(0.0005, d * 0.01); cam.data.clip_end = max(500.0, d * 200)
    fdir = os.path.join(TMP, f'{name}_{clip}')
    shutil.rmtree(fdir, ignore_errors=True); os.makedirs(fdir)
    sc.render.image_settings.file_format = 'PNG'; sc.render.filepath = os.path.join(fdir, 'f_')
    bpy.ops.render.render(animation=True, scene=sc.name)
    frames = sorted(x for x in os.listdir(fdir) if x.startswith('f_') and x.endswith('.png')); N = len(frames)
    sheet = os.path.join(TMP, f'{name}_{clip}_sheet.png')
    rn.compose([rn.load_px(os.path.join(fdir, frames[int(N * k / 4)])) for k in range(4)], 2, sheet)
    passes = 2 if loop else 1
    seq = os.path.join(fdir, 'seq'); os.makedirs(seq)
    for p_ in range(passes):
        for i, fn in enumerate(frames): shutil.copyfile(os.path.join(fdir, fn), os.path.join(seq, f'{p_ * N + i:05d}.png'))
    os.makedirs(OUT_DIR, exist_ok=True)
    src = os.path.join(seq, '%05d.png'); gif = os.path.join(OUT_DIR, f'{name}_{clip}.gif')
    gfps, gw = o['gif_fps'], W
    for attempt in range(5):
        vf = (f'fps={gfps},scale={gw}:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=full[p];'
              f'[b][p]paletteuse=dither=none')
        ffmpeg(['-framerate', '30', '-i', src, '-vf', vf, '-loop', '0', gif])
        if os.path.getsize(gif) <= GIF_LIMIT: break
        print(f'NOTE {name}_{clip}: GIF {os.path.getsize(gif) / 1e6:.2f} MB > 4 MB -> reducing')
        if attempt % 2 == 0: gw = int(gw * 0.8) // 2 * 2
        else: gfps = max(10, gfps - 5)
    print(f'CLIP {name}_{clip} frames {N} ({f0}..{last}) loop {loop} passes {passes} gif {gw}px {gfps} fps')
    print('GIF', gif, probe(gif))
    if o['mp4']:
        mp4 = os.path.join(OUT_DIR, f'{name}_{clip}.mp4')
        ffmpeg(['-framerate', '30', '-i', src, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-movflags', '+faststart', mp4])
        print('MP4', mp4, probe(mp4))
    print('SHEET', sheet)
    if not o['keep']: shutil.rmtree(fdir, ignore_errors=True)


def main():
    o = parse(); sc = bpy.context.scene; _clear_scene(sc)
    sc.render.fps, sc.render.fps_base = 30, 1.0
    m = load_blend(o['name'], sc) or load_fbx(o['name'], sc)
    environment(sc)
    for clip in o['clips']:
        render_clip(o, sc, m[0], m[1], clip)


main()
