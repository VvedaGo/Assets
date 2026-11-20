# build_registry_template.py - skeleton of a registry build script: many small props in one file (proven on Farm Processing
# TOL/PRD/FUR/MOD, 45 models). Copy it to .work/models/<Pack>/<Family>/build_<family>.py and fill CONFIG + builders.
# Headless:
#   PYTHONUTF8=1 blender.exe --background --factory-startup --python build_<family>.py -- <ID> build|export
#   build  = build + printed checks + check render to %TEMP%/<pack>_check/<ID>_check.png
#   export = build + FBX (+ .fbm via path_mode COPY) + collection-only .blend + ONE preview + FBX re-import verify
import bpy, math, os, sys
from mathutils import Vector

# ---------------- CONFIG ----------------
REPO = r"C:\path\to\repo"                                  # worktree root of the pack
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')   # env override for tests
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'My_Pack')   # Meshes / Textures / Previews / Blend
PREFIX, TEX_TAG = 'FMS_MyPack_', 'MyPack'                  # FMS_MyPack_TOL_01, T_MyPack_TOL01_BaseColor.png
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'mypack_check')
# ----------------------------------------
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_shapes import *          # Part, sweep, shell, fill, bolt, oct_rod, ... + palette slots WOOD, METAL, RED ...

ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
ID = ARGS[0] if ARGS else 'TOL01'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'


# ---------------- builders: return a Part, or [(Part, pivot), ...] for moving parts (direct root children) ----------------
def build_example_bowl():
    P = Part('Body'); n = 16
    prof = [(0.0, 0.08), (0.03, 0.10), (0.12, 0.16), (0.13, 0.16), (0.13, 0.15), (0.03, 0.09)]   # (z, apothem) closed section
    shell(P, 'bowl', prof, n, lambda j, k: (CREAM_D, CREAM, CREAM_B, CREAM_B, CREAM_B)[j], FOOT, CREAM_B)
    return P


# id -> name, builder, tris budget (ceiling; overruns are documented), preview view direction, fill (width, height share),
# optional per-item palette overrides {cell: '#RRGGBB'}, optional snapbox (x0, x1, y0, y1, z0, z1; None = not checked)
REG = {
    'TOL01': dict(name=PREFIX + 'TOL_01', build=build_example_bowl, budget=(150, 400), view=(0.0, -1.0, 0.5), fill=(0.72, 0.8)),
}


def build():
    cfg = REG[ID]; name = cfg['name']; tag = f'{TEX_TAG}_{ID}'
    sc = bpy.context.scene
    for o in list(sc.objects): bpy.data.objects.remove(o, do_unlink=True)
    coll = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if coll.name not in sc.collection.children: sc.collection.children.link(coll)
    pal = list(PAL)
    for k, v in cfg.get('pal', {}).items(): pal[k] = v
    tex = f'T_{tag}_BaseColor.png'
    img = pc.atlas_image(tex, os.path.join(ART, 'Textures', tex), pal); mat = pc.material(f'M_{tag}', img)
    root = bpy.data.objects.new(name, None); coll.objects.link(root)
    res = cfg['build']()
    parts = res if isinstance(res, list) else [(res, (0, 0, 0))]
    obs = {P.name: pc.to_object(P, name, coll, mat, piv, root) for P, piv in parts}
    bpy.context.view_layer.update()
    tot = pc.report(obs)
    for o in obs.values(): pc.coplanar_overlaps(o)
    lo, hi = cfg['budget']; print(f'  budget {lo}-{hi} ->', 'OK' if lo <= tot <= hi else f'x{tot / hi:.2f}')
    return name, coll, root, img, mat


name, coll, root, img, mat = build()
os.makedirs(CHECK_DIR, exist_ok=True)
if MODE == 'export':
    fbx = pc.export(name, coll, root, os.path.join(ART, 'Meshes', name + '.fbx'))
    pc.save_lib(os.path.join(ART, 'Blend', name + '.blend'), coll, mat, img)
    # preview: copy render() from an approved registry script (e.g. Farm Processing TOL_Tools/build_tools.py) or use
    # ~/.claude/skills/blender-unity-assets/render_preview_template.py; exactly ONE <name>_Preview.png into art/.../Previews
    pc.verify(fbx)
