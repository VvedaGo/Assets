# MOD-03 Workshop wall 2 m (kind 'plain' -> FMS_Workshop_MOD_03) and MOD-05 Wall with doorway 2 m (kind 'door' ->
# FMS_Workshop_MOD_05). ONE shared script for both (MOD05_WallDoor\build_wall_door.py only forwards to it).
# It REUSES the accepted MOD-04 script ..\MOD04_WallWindow\build_wall_window.py WITHOUT editing it: the MOD-04 source is
# exec'd up to its module-level `build()` call (helpers, palette, contract constants, snap_check, ymirror_check, build,
# render, verify_headless), then build_wall / KINDS / paths are overridden here for 'plain' and 'door' only.
# MOD-04 ('window') is never built or exported by this script, so its files stay byte-identical.
# Headless:
#   blender --background --factory-startup --python build_wall_modules.py -- <mode> <plain|door> [round] [--pair]
#   mode: dry    = build + checks only (numbers)
#         check  = + check render + 128 px thumb to %TEMP%\FarmProcessing_check\MOD-03|MOD-05
#                  --pair: MOD-03 + MOD-04 + MOD-05 side by side (snap proof render)
#         export = + FBX, .fbm, texture, .blend, preview, FBX re-import verify
import bpy, os, sys, shutil, math
from mathutils import Vector

_ROOT = r"C:\Users\Sergv\orca\workspaces\VFX\master-2"
_FP = os.path.join(_ROOT, '.work', 'models', 'Farm_Processing')
_MOD04 = os.path.join(_FP, 'MOD04_WallWindow', 'build_wall_window.py')
_src = open(_MOD04, encoding='utf-8').read()
_src = _src[:_src.index('ROOTOB, COLL, IMG, MAT, BODY = build()')]
exec(compile(_src, _MOD04, 'exec'), globals())          # defines PAL, contract constants, ybox, xb, snap_check, build, ...
_mod04_tmp = os.path.join(os.environ.get('TEMP', ''), 'FarmProcessing_check', 'MOD-04')
try: os.rmdir(_mod04_tmp)                                # MOD-04 source makes this dir on load; drop it if empty
except OSError: pass

assert KIND in ('plain', 'door'), 'this script builds MOD-03 (plain) and MOD-05 (door) only'
FOLDER = {'plain': 'MOD03_Wall', 'door': 'MOD05_WallDoor'}[KIND]
HERE = os.path.join(_FP, FOLDER)                         # render() uses HERE\render_preview.py (own copy per item)
CHECK_DIR = os.path.join(os.environ.get('TEMP', HERE), 'FarmProcessing_check', {'plain': 'MOD-03', 'door': 'MOD-05'}[KIND])
os.makedirs(CHECK_DIR, exist_ok=True)

# ---------------- per-kind parameters (contract numbers above are untouched) ----------------
KINDS['plain'] = dict(open=None, brace=(1.52, 0.24),
                      stones=(0.60, 0.60, 0.60),                 # 3 long plinth stones like the ref
                      stud=0.07,                                  # centre stud half-width (dark wood)
                      midrail=(1.30, 1.46))                       # dark mid rail crossing the stud
# arched doorway (segmental arch: springs at z 1.78 at x +-0.48, apex 2.02) -> shared with MOD-09 (door frame outer = this opening)
KINDS['door'] = dict(open=(0.48, 0.0, 2.02), arch=(1.78, 2.02), jamb=0.10, head=(0.61, 0.10), sill=None, brace=(1.45, 0.62),
                     bricks=((0.0, 0.21, (0.5,)), (0.21, 0.42, ())),   # rows (z0, z1, split fractions post->jamb)
                     brick_bev=(0.030, 0.024))
Y_STUD, Y_MID = Y_FRAME - 0.006, Y_FRAME - 0.004
if KIND == 'door': BUDGET = (300, 800)      # arched casing + arched plaster cost ~150 tris more (user asked for the arched door)

def arch_circle(hx, zs, za):
    """circle through (+-hx, zs) and (0, za): returns centre z and radius"""
    zc = (za * za - zs * zs - hx * hx) / (2 * (za - zs)); return zc, za - zc

def arch_pts(zc, r, x_from, x_to, n):
    """n-1 interior points on the arch circle between x_from and x_to (in that order)"""
    a0 = math.atan2(math.sqrt(max(r * r - x_from * x_from, 0)), x_from); a1 = math.atan2(math.sqrt(max(r * r - x_to * x_to, 0)), x_to)
    return [(r * math.cos(a0 + (a1 - a0) * k / n), zc + r * math.sin(a0 + (a1 - a0) * k / n)) for k in range(1, n)]

def door_arch_z(x, grow=0.0):
    hx, _, _ = KINDS['door']['open']; zs, za = KINDS['door']['arch']; zc, r = arch_circle(hx, zs, za)
    return zc + math.sqrt(max((r + grow) ** 2 - x * x, 0.0))

_plaster04 = plaster
def plaster(P, K):
    """door: two side panels + a top panel whose lower edge follows the middle of the arched casing (no hole in the opening)"""
    if not (K['open'] and K.get('arch')): return _plaster04(P, K)
    x1, z0, z1 = PX0 + SINK, PLASTER_Z[0], PLASTER_Z[1]; rings = yr(Y_PLASTER, 0.0)
    hx, _, _ = K['open']; jw = K['jamb']; hx_in = hx + jw / 2
    mirror_x(lambda s: xb(P, 'plaster', s, hx_in, x1, z0, z1, rings, PLASTER, PLASTER, PLASTER))
    zs, za = K['arch']; zc, r = arch_circle(hx, zs, za); rm = r + jw / 2
    poly = [(-hx_in, zc + math.sqrt(rm * rm - hx_in * hx_in))] + arch_pts(zc, rm, -hx_in, hx_in, 10) + \
           [(hx_in, zc + math.sqrt(rm * rm - hx_in * hx_in)), (hx_in, z1), (-hx_in, z1)]
    P.loft('plaster', [[Vector((x, y, z)) for x, z in poly] for y in (-Y_PLASTER, Y_PLASTER)], PLASTER, PLASTER, PLASTER)

_brace_ext_mod04 = brace_ext
def brace_ext(u):
    """MOD-04 rule, but a steep brace (door: it must clear the head) must not run out of the 0.10 half-post at x = +-1:
    clamp the post-side extension so both square end corners stay inside x 0.90..0.998 (asserted by build())."""
    e0, e1 = _brace_ext_mod04(u)
    return min(e0, (HX - 0.002 - PX0 - BR_W * abs(u.z)) / abs(u.x)), e1

def stone_rings(bev):
    return [(-Y_STONE, bev[0]), (-Y_STONE + bev[1], 0.0), (Y_STONE - bev[1], 0.0), (Y_STONE, bev[0])]

def build_wall(kind):
    K = KINDS[kind]; P = Part('Body'); op = K['open']
    # --- contract frame: half-posts, plate, low rail, joint blocks + red caps (identical to MOD-04) ---
    mirror_x(lambda s: xb(P, 'post', s, PX0, HX, 0.0, PLATE_Z[0] + SINK, yr(Y_FRAME, 0.010), WOOD, WOOD, WOOD, snap_outer=True))
    ybox(P, 'plate', -HX, HX, PLATE_Z[0], PLATE_Z[1], yr(Y_FRAME, 0.012), WOOD, WOOD, WOOD, snap0=True, snap1=True)
    if op:
        xj = op[0] + K['jamb']
        mirror_x(lambda s: xb(P, 'rail', s, xj, PX0 + SINK, RAIL_Z[0], RAIL_Z[1], yr(Y_FRAME - 0.003, 0.010), WOOD, WOOD, WOOD))
    else:
        ybox(P, 'rail', -PX0 - SINK, PX0 + SINK, RAIL_Z[0], RAIL_Z[1], yr(Y_FRAME - 0.003, 0.010), WOOD, WOOD, WOOD)
    for z0, z1 in BLOCK_ZS:
        mirror_x(lambda s: xb(P, 'block', s, BLOCK_X0, HX, z0, z1, yr(Y_BLOCK, 0.008), WOOD, WOOD, WOOD, snap_outer=True))
        cx, cz, h = (BLOCK_X0 + HX) / 2, (z0 + z1) / 2, CAP_S / 2
        for s in (1, -1):
            for rings in ([(-Y_CAP, CAP_IN), (-CAP_Y0, 0.0)], [(CAP_Y0, 0.0), (Y_CAP, CAP_IN)]):
                ybox(P, 'cap', s * cx - h, s * cx + h, cz - h, cz + h, rings, RED, RED, RED)
    # --- plinth ---
    if op:          # door: two staggered brick rows between each post and jamb; nothing in the opening (walk-through)
        for z0, z1, cuts in K['bricks']:
            xs = [xj] + [xj + (PX0 - xj) * (1 - c) for c in cuts] + [PX0]
            xs = sorted(xs)
            for s in (1, -1):
                for a, b in zip(xs[:-1], xs[1:]):
                    ybox(P, 'stone', *((a, b) if s > 0 else (-b, -a)), z0, z1, stone_rings(K['brick_bev']), STONE, STONE_D, STONE)
    else:
        xs = [-PX0]
        for w in K['stones']: xs.append(xs[-1] + w)
        for a, b in zip(xs[:-1], xs[1:]):
            ybox(P, 'stone', a, b, 0.0, STONE_Z1, stone_rings(tuple(v * 1.5 for v in STONE_BEV)), STONE, STONE_D, STONE)
    plaster(P, K)
    # --- plain: dark centre stud + dark mid rail crossing it (rail in front) ---
    if K.get('stud'):
        sw = K['stud']
        ybox(P, 'stud', -sw, sw, RAIL_Z[1] - SINK, PLATE_Z[0] + SINK, yr(Y_STUD, 0.010), WOOD_M, WOOD_M, WOOD_M)
        z0, z1 = K['midrail']
        ybox(P, 'midrail', -PX0 - SINK, PX0 + SINK, z0, z1, yr(Y_MID, 0.010), WOOD_M, WOOD_M, WOOD_M)
    # --- braces (dark), ends sunk into the post and the plate ---
    bz0, bx1 = K['brace']
    for s in (1, -1):
        A, B = Vector((s * PX0, 0, bz0)), Vector((s * bx1, 0, PLATE_Z[0]))
        u = (B - A).normalized(); e0, e1 = brace_ext(u)
        sweep(P, 'brace', A - u * e0, B + u * e1, [(-Y_BRACE, -BR_W), (Y_BRACE, -BR_W), (Y_BRACE, BR_W), (-Y_BRACE, BR_W)],
              [(0, 1, 0), (1, 1, 0)], WOOD_M, WOOD_M, WOOD_M, ref=(0, 1, 0))
    # --- door: ONE inverted-U dark casing (jambs to the ground + head, full-depth reveal). A single loft costs 60 tris
    #     instead of 84 for three boxes; the saving pays for the two-row brick plinth (budget 650). No head overhang.
    if op:
        hx, oz0, oz1 = op; xo = hx + K['jamb']; zs, za = K['arch']; zc, r = arch_circle(hx, zs, za); ro = r + K['jamb']
        zso = zc + math.sqrt(ro * ro - xo * xo)
        U = [(-xo, 0.0), (-hx, 0.0), (-hx, zs)] + arch_pts(zc, r, -hx, hx, 8) + [(hx, zs), (hx, 0.0), (xo, 0.0), (xo, zso)] + \
            arch_pts(zc, ro, xo, -xo, 8) + [(-xo, zso)]
        P.loft('casing', [[Vector((x, y, z)) for x, z in offset_rect_poly(U, d)] for y, d in yr(Y_CASE, 0.008)],
               WOOD_D, WOOD_D, WOOD_D, ground=True)
    return P

def offset_rect_poly(pts, d):
    """inward offset of a polygon (XZ), true miter (exact for axis-aligned corners, also correct on the arch)"""
    if not d: return pts
    n = len(pts); area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    sgn = 1 if area > 0 else -1                          # CCW -> inward normal of edge (dx, dz) is (-dz, dx)
    def nrm(a, b):
        dx, dz = b[0] - a[0], b[1] - a[1]; L = (dx * dx + dz * dz) ** 0.5
        return (-dz / L * sgn, dx / L * sgn)
    out = []
    for i in range(n):
        n1 = nrm(pts[i - 1], pts[i]); n2 = nrm(pts[i], pts[(i + 1) % n])
        k = d / max(1e-6, 1 + n1[0] * n2[0] + n1[1] * n2[1])
        out.append((pts[i][0] + k * (n1[0] + n2[0]), pts[i][1] + k * (n1[1] + n2[1])))
    return out

def door_check(ob):
    """walk-through: clear opening >= 0.9 x 2.0 m, no geometry inside the opening box (through the full depth)"""
    hx, oz0, oz1 = KINDS['door']['open']
    clear_w, clear_h = 2 * hx, oz1 - oz0
    inside = [v.co for v in ob.data.vertices if abs(v.co.x) < hx - 1e-6 and v.co.z < door_arch_z(v.co.x) - 0.006]
    # a face could still span the hole without a vertex in it: ray-cast through the opening on a grid
    from mathutils.bvhtree import BVHTree
    bvh = BVHTree.FromObject(ob, bpy.context.evaluated_depsgraph_get())
    hits = 0
    for i in range(1, 20):
        for j in range(0, 41):
            x = -hx + 2 * hx * i / 20; z = 0.001 + (door_arch_z(x) - 0.010) * j / 40     # 10 mm below the true circle (chord sagitta ~4 mm)
            if bvh.ray_cast(Vector((x, -1.0, z)), Vector((0, 1, 0)), 2.0)[0] is not None: hits += 1
    print(f'  DOOR arched opening {clear_w:.3f} wide, apex {clear_h:.3f} m, springs at {KINDS["door"]["arch"][0]:.2f} (need >= 0.90 x 2.00 at the centre), threshold z {oz0:.3f}, '
          f'verts inside {len(inside)}, ray hits through opening {hits}')
    assert clear_w >= 0.9 and clear_h >= 2.0 and oz0 == 0.0 and not inside and hits == 0

ROOTOB, COLL, IMG, MAT, BODY = build()
if KIND == 'door': door_check(BODY)

if MODE == 'check':
    tag = f'{KIND}_r{ROUND}'
    front = os.path.join(CHECK_DIR, tag + '_front.png'); render(front)
    thumb(front, os.path.join(CHECK_DIR, tag + '_thumb128.png'))
    if '--back' in ARGV: render(os.path.join(CHECK_DIR, tag + '_back.png'), view=(0.42, 1.0, 0.36))
    if '--pair' in ARGV:     # MOD-03 | MOD-04 (exported FBX) | MOD-05 in a row, every 2.0 m
        other = 'door' if KIND == 'plain' else 'plain'
        b2 = pc.to_object(build_wall(other), NAME + '_Other', COLL, MAT, (0, 0, 0), ROOTOB)
        b2.location.x = W if other == 'door' else -W           # MOD-03 at x -2, MOD-04 at 0, MOD-05 at +2
        BODY.location.x = -W if KIND == 'plain' else W
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=os.path.join(ART, 'Meshes', 'FMS_Workshop_MOD_04.fbx'))   # read only, at x 0
        for o in set(bpy.data.objects) - before:
            for c in list(o.users_collection): c.objects.unlink(o)
            COLL.objects.link(o)
        bpy.context.view_layer.update()
        g = dict(OUT=os.path.join(CHECK_DIR, 'snap_row.png'), PCT=60, SCENE_NAME=bpy.context.scene.name, COLLECTION=NAME,
                 VIEW_DIR=(0.30, -1.0, 0.30), FILL_W=0.86)
        src = open(os.path.join(HERE, 'render_preview.py')).read().replace('FILL_H = 0.88', 'FILL_H = 0.6').replace('FILL_W = 0.80', 'FILL_W = 0.86')
        exec(src, g)
elif MODE == 'export':
    fbx = os.path.join(ART, 'Meshes', NAME + '.fbx')
    pc.export(NAME, COLL, ROOTOB, fbx)
    fbm = os.path.join(ART, 'Meshes', NAME + '.fbm'); os.makedirs(fbm, exist_ok=True)
    shutil.copy2(os.path.join(ART, 'Textures', TEX_NAME), os.path.join(fbm, TEX_NAME))
    pc.save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), COLL, MAT, IMG)
    render(os.path.join(ART, 'Previews', NAME + '_Preview.png'), pct=100)
    verify_headless(fbx)
