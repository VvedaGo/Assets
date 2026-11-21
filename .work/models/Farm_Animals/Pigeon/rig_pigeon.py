# rig_pigeon.py - BRD-08 Pigeon: skeleton B bird rig WITH FLIGHT (20 bones), binding of the final part mesh (rigid parts +
# linear blends: the head's collar skirt stretches between Body and Head), bend test incl. flight poses, clips
# Pigeon_Idle / Pigeon_Peck / Pigeon_Fly, metrics, FBX (3 takes) + re-import check + events json + .blend.
#   PYTHONUTF8=1 blender --background --factory-startup --python rig_pigeon.py -- BRD-08 bend|anim|export|meshcheck
# Copied from ../Hen/rig_hen.py (read-only there) and made species-generic: main(SP, build_module, work_dir) is also used by
# ../Sparrow/rig_sparrow.py and ../Crow/rig_crow.py with their own tables. Changes vs the hen:
#  - wing bones for flight: WingUpper head = spread pivot on the wing root (sp['wing_pivot'] offsets in the folded wing
#    frame), WingLower / WingTip heads on the seams between the wing parts (sp['wing_heads'] = 'seams'), WingTip tail at
#    the wing tip; per-bone euler order for the wing bones (pigeon_clips.finalize), wide flight limits;
#  - 'heads' overrides (long virtual neck bones inside the body/head for the peck reach), 'plane' blends;
#  - bend test with flight extremes; meshcheck = built mesh vs the mesh-only FBX backup (mesh unchanged).
# Geometry, part names and pivots come unchanged from build_<species>.build(). Shared modules (_common) are read-only.
import sys, os, math, json, importlib
REPO = r'D:\GitProjects\Assets_Farm'
HERE = REPO + r'\.work\models\Farm_Animals\Pigeon'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common', HERE):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector, Matrix
import animal_render as rn, animal_rig as ar, animal_anim as an, animal_export as ax
import pigeon_clips as hc
importlib.reload(hc)

# ---------------- skeleton B (bird) template: bone, parent (same as the hen) ----------------
B_BONES = [
    ('Root', None), ('Body', 'Root'), ('Neck1', 'Body'), ('Neck2', 'Neck1'), ('Head', 'Neck2'), ('Beak_Lower', 'Head'),
    ('WingUpper.L', 'Body'), ('WingLower.L', 'WingUpper.L'), ('WingTip.L', 'WingLower.L'),
    ('WingUpper.R', 'Body'), ('WingLower.R', 'WingUpper.R'), ('WingTip.R', 'WingLower.R'),
    ('TailFan1', 'Body'), ('TailFan2', 'TailFan1'),
    ('LegUpper.L', 'Body'), ('LegLower.L', 'LegUpper.L'), ('Foot.L', 'LegLower.L'),
    ('LegUpper.R', 'Body'), ('LegLower.R', 'LegUpper.R'), ('Foot.R', 'LegLower.R'),
]
ar.SKELETONS['B'] = B_BONES
B_LEGS = {'LegL': ('LegUpper.L', 'LegLower.L', 'Foot.L', True), 'LegR': ('LegUpper.R', 'LegLower.R', 'Foot.R', True)}
CHAIN_TAIL = {'Neck1': 'Neck2', 'Neck2': 'Head', 'WingUpper.L': 'WingLower.L', 'WingLower.L': 'WingTip.L', 'TailFan1': 'TailFan2',
              'LegUpper.L': 'LegLower.L', 'LegLower.L': 'Foot.L'}
# hen limits + FLIGHT ranges for the wing bones (euler in the per-bone order chosen by pigeon_clips.finalize)
B_LIMITS = {
    'Body': dict(x=(-45, 60), y=(-20, 20), z=(-25, 25)), 'Neck1': dict(x=(-60, 100), y=(-60, 60), z=(-30, 30)),
    'Neck2': dict(x=(-110, 75), y=(-60, 60), z=(-30, 30)), 'Head': dict(x=(-90, 90), y=(-40, 40), z=(-100, 100)),
    'Beak_Lower': dict(x=(-2, 35)), 'WingUpper': dict(x=(-30, 30), y=(-30, 30), z=(-90, 90)),
    # flight: WingUpper euler order ZYX (finalize); z = spread yaw out + flap, x = flap/pitch of the spread wing, y = twist
    'WingUpper.L': dict(x=(-90, 30), y=(-45, 45), z=(-180, 10)), 'WingUpper.R': dict(x=(-90, 30), y=(-45, 45), z=(-10, 180)),
    'WingLower': dict(x=(-45, 45), y=(-45, 45), z=(-45, 45)), 'WingTip': dict(x=(-45, 45), y=(-45, 45), z=(-45, 45)),
    'TailFan1': dict(x=(-40, 60), z=(-40, 40)), 'TailFan2': dict(x=(-40, 60), z=(-40, 40)),
    'LegUpper': dict(x=(-100, 100), z=(-35, 35)), 'LegLower': dict(x=(-150, 150)), 'Foot': dict(x=(-120, 120)),
    'NECK_YAW_TOTAL': 200,
}

# ---------------- species table (Pigeon: 0.27 m tall, plump, head on a hidden neck; collar skirt stretches) ----------------
PIGEON = dict(
    id='BRD-08', species='Pigeon', skeleton='B', module='build_pigeon', work=HERE,
    bind={'Eye.L': 'Head', 'Eye.R': 'Head', 'Neck1': 'Body', 'Neck2': 'Head'},   # hidden neck connectors stay hidden
    ends={'Root': (0, -0.08, 0), 'Body': (0, -0.07, 0), 'Head': (0, -0.062, -0.016), 'Beak_Lower': (0, -0.021, -0.012),
          'TailFan2': (0, 0.10, -0.031)},
    # long virtual neck (bone heads inside the chest / head) so the peck reaches the ground; parts keep their pivots
    heads={'Neck1': (0, 0.012, 0.118), 'Neck2': (0, -0.030, 0.165)},
    # head collar skirt (ring H0 inside the chest) -> Body, ring H1 (collar line) -> Head: the blue band stretches
    blend={'Head': [('Body', 'plane', (0, -0.048, 0.188), (0, -0.454, 0.891), -0.016, 0.014)]},
    wing_heads='seams', wing_pivot=(0.030, 0.0, 0.0),
    clips=[('Idle', 4.0, True), ('Peck', 2.5, True), ('Fly', 1.0, True)],
    limits=B_LIMITS, lowest_ok=-0.007,
    strip_views={'Fly': [(0.5, -1.0, 0.55), (0.05, 0.25, 1.0)], 'Peck': [(1.0, -0.02, 0.10)], 'Idle': [(0.6, -1.0, 0.35)]},
    bend_views={'side': (1.0, -0.15, 0.2), 'front': (-0.6, -1.0, 0.45), 'top': (0.1, 0.3, 1.0)},
    poses=dict(stand_bend=0.004, wing_out=8.0, breaths=3, breath_pitch=1.0, breath_dz=0.0012, snap_frames=3.0,
               idle_look=[(0.00, (0, 0, 0)), (0.10, (30, 8, -3)), (0.20, (24, 14, 2)), (0.32, (0, 0, 0)), (0.44, (-30, -8, -3)),
                          (0.54, (-38, -12, 4)), (0.66, (-6, 0, 10)), (0.78, (18, 4, 0)), (0.90, (0, 0, 0))],
               tail_flicks=[(0.58, 0.12, 2, 8.0)], ruffles=[(0.84, 0.10, 2)],
               peck_lean=(0.08, 0.22, 0.64, 0.80), peck_hits=(0.30, 0.43, 0.55), peck_pitch=30.0, peck_drop=0.0, peck_fwd=0.015, peck_jab=3.0,
               peck_y=-0.120, peck_ready_z=0.040, peck_hit_z=0.003, peck_ready_down=62.0, peck_hit_down=72.0, peck_tail=22.0,
               peck_foot={'LegL': (0, -0.006, 0), 'LegR': (0, 0.006, 0)},
               peck_look=[(0.00, (0, 0, 0)), (0.34, (14, 16, 0)), (0.40, (0, 0, 0)), (0.86, (16, 6, 0)), (0.95, (0, 0, 0))]),
    fly=dict(flaps=3, down=0.55, lift=0.10, clear=0.045, bob=0.008, pitch=26.0, pitch_beat=3.0,
             leg=(55.0, 85.0, 95.0), neck={}, head_down=0.0, head_nod=2.0, tail=-6.0, tail_beat=4.0,
             mid=12.0, amp=55.0, sweep=6.0, sweep_up=14.0, twist=8.0, lag=(22.0, 18.0), lag_ph=(0.7, 1.3),
             lsweep=(0.0, 0.0), lsweep_up=(6.0, 10.0)),
)

SP = None; BM = None; ASSET = None; ART = None; CHECK = None; WORK = None


def configure(sp, bm_module):
    global SP, BM, ASSET, ART, CHECK, WORK
    SP = sp; BM = bm_module; ASSET = BM.ASSET; ART = BM.ART; WORK = sp['work']
    SP['asset'] = ASSET; SP['tag'] = BM.TAG
    CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_' + sp['species'].lower() + '_rig')
    os.makedirs(CHECK, exist_ok=True)


def bone_of(part):
    return SP['bind'].get(part, part)


def args(default_id):
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + [default_id, 'bend'])[:2]


def _pts(o):
    return [o.matrix_world @ v.co for v in o.data.vertices]


def _end_centroid(pts, which):
    y = min(p.y for p in pts) if which == 'front' else max(p.y for p in pts)
    sel = [p for p in pts if abs(p.y - y) < 0.002]; return sum(sel, Vector()) / len(sel)


def wing_geometry(obs):
    """folded wing frame + pivots of the left wing from its parts: a = front of WingUpper -> back of WingTip, n = +X
    orthogonalised, c = n x a; spread pivot P = front + pa*a + pc*c + pn*n; seam heads = front centroids of WingLower/Tip"""
    up, lo, tp = _pts(obs['WingUpper.L']), _pts(obs['WingLower.L']), _pts(obs['WingTip.L'])
    front = _end_centroid(up, 'front'); back = _end_centroid(tp, 'back')
    a = (back - front).normalized(); X = Vector((1, 0, 0)); n = (X - a * X.dot(a)).normalized(); c = n.cross(a)
    pa, pc, pn = SP['wing_pivot']
    piv = front + a * pa + c * pc + n * pn
    return dict(a=a, c=c, n=n, front=front, back=back, pivot=piv,
                seam_lower=_end_centroid(lo, 'front'), seam_tip=_end_centroid(tp, 'front'))


def species_bones(obs):
    """bone heads at the part pivots (or overrides / wing pivots); tails = next joint; .R mirrored by animal_rig"""
    P = {k: o.matrix_world.translation.copy() for k, o in obs.items()}
    for k, v in SP.get('heads', {}).items(): P[k] = Vector(v)
    WG = wing_geometry(obs); SP['wing_frame'] = (tuple(WG['a']), tuple(WG['c']), tuple(WG['n'])); SP['_wg'] = WG
    P['WingUpper.L'] = WG['pivot']
    if SP.get('wing_heads') == 'seams':
        P['WingLower.L'] = WG['seam_lower']; P['WingTip.L'] = WG['seam_tip']
    t = lambda v: tuple(round(c, 4) for c in v)
    B = {'Root': ((0, 0, 0), t(Vector(SP['ends']['Root'])))}
    for n, par in B_BONES:
        if n == 'Root' or n.endswith('.R'): continue
        h = P[n]
        if n in CHAIN_TAIL: tl = P[CHAIN_TAIL[n]]
        elif n.startswith('Foot'): tl = Vector((h.x, h.y, 0.0))
        elif n == 'WingTip.L': tl = WG['back'] if SP.get('wing_heads') == 'seams' else h + Vector(SP['ends'][n])
        else: tl = h + Vector(SP['ends'][n])
        B[n] = (t(h), t(tl))
    print('WING frame a', t(WG['a']), 'c', t(WG['c']), 'n', t(WG['n']), 'pivot', t(WG['pivot']), 'seams', t(P['WingLower.L']), t(P['WingTip.L']))
    return B


def weights(obs, rig):
    """per part: {vertex index: {bone: w}} - rigid 1.0, linear blends: (other, 'head'|'tail', half width) along the bone
    axis (hen) or (other, 'plane', point, normal, s_full, s_zero): full 'other' at signed distance <= s_full"""
    out = {}
    for nm, o in obs.items():
        b = bone_of(nm); bb = rig.data.bones[b]; h = bb.head_local; u = (bb.tail_local - bb.head_local); L = u.length; u = u / L
        M = o.matrix_world; W = []
        for v in o.data.vertices:
            p = M @ v.co; t = (p - h).dot(u); w = {b: 1.0}
            for spec in SP['blend'].get(nm, []):
                other, kind = spec[0], spec[1]
                if kind == 'head':
                    wd = spec[2]; s = min(max(0.5 + 0.5 * t / wd, 0.0), 1.0); w = {k: x * s for k, x in w.items()}; w[other] = w.get(other, 0) + 1 - s
                elif kind == 'tail':
                    wd = spec[2]; s = min(max(0.5 - 0.5 * (t - L) / wd, 0.0), 1.0); wb = w[b]; w[b] = wb * s; w[other] = w.get(other, 0) + wb * (1 - s)
                else:
                    P0, nrm, s0, s1 = Vector(spec[2]), Vector(spec[3]).normalized(), spec[4], spec[5]
                    d = (p - P0).dot(nrm); s = min(max((d - s0) / (s1 - s0), 0.0), 1.0)
                    wb = w[b]; w[b] = wb * s; w[other] = w.get(other, 0) + wb * (1 - s)
            W.append({k: x for k, x in w.items() if x > 1e-4})
        out[nm] = W
    return out


def joined(obs, rig, W):
    names = [b.name for b in rig.data.bones]; gi = {n: i for i, n in enumerate(names)}
    me = bpy.data.meshes.new('TMP_BirdAll'); ob = bpy.data.objects.new('TMP_BirdAll', me)
    bpy.context.scene.collection.objects.link(ob)
    for n in names: ob.vertex_groups.new(name=n)
    bm = bmesh.new(); dl = bm.verts.layers.deform.verify()
    for nm, o in obs.items():
        M = o.matrix_world; vm = {}
        for v in o.data.vertices:
            nv = bm.verts.new(M @ v.co); vm[v.index] = nv
            for b, w in W[nm][v.index].items(): nv[dl][gi[b]] = w
        for p in o.data.polygons: bm.faces.new([vm[i] for i in p.vertices])
    bm.to_mesh(me); bm.free()
    ob.modifiers.new('Armature', 'ARMATURE').object = rig; ob.hide_render = True
    return ob


def rig_model(tex_dir):
    B = BM.build(tex_dir)
    sc = B['sc']; sc.render.fps = 30; sc.render.fps_base = 1.0
    sp = SP; sp['bones'] = species_bones(B['obs'])
    rig = ar.build_armature(sp, B['coll'], 'B')
    rchk = ar.check_rig(rig, 'B')
    W = weights(B['obs'], rig); nblend = 0
    for nm, ob in B['obs'].items():
        mw = ob.matrix_world.copy(); ob.parent = rig; ob.matrix_parent_inverse.identity(); ob.matrix_world = mw
        for g in list(ob.vertex_groups): ob.vertex_groups.remove(g)
        groups = {}
        for i, wd in enumerate(W[nm]):
            nblend += len(wd) > 1
            for b, w in wd.items():
                if b not in groups: groups[b] = ob.vertex_groups.new(name=b)
                groups[b].add([i], w, 'REPLACE')
        ob.modifiers.new('Armature', 'ARMATURE').object = rig
    bpy.data.objects.remove(B['root'], do_unlink=True)
    bpy.context.view_layer.update()
    tmp = joined(B['obs'], rig, W)
    sk = hc.BirdSkel(rig, tmp, B_LEGS, 'Body')
    print(f'RIG bones {len(rig.data.bones)} | parts bound {len(B["obs"])} | blended verts {nblend} | bones',
          {n: (tuple(round(c, 3) for c in rig.data.bones[n].head_local), round(rig.data.bones[n].length, 3)) for n in sk.order})
    B.update(rig=rig, rig_checks=rchk, tmp=tmp, sk=sk, SP=sp)
    return B


def apply_orders(rig, sk):
    for n, o in sk.eorder.items(): rig.pose.bones[n].rotation_mode = o


# ---------------- strips ----------------
def apply_pose(rig, sk, pose):
    for n, (l, r) in pose.items():
        pb = rig.pose.bones[n]; pb.location = l
        if isinstance(r, Matrix):
            pb.rotation_mode = 'XYZ'; pb.rotation_euler = r.to_euler('XYZ')
        else:
            pb.rotation_mode = sk.eorder[n]; pb.rotation_euler = r
    bpy.context.view_layer.update()


def strip(B, setters, out, view, cols=4, size=(320, 240)):
    sc = B['sc']; rn.setup_workbench(sc, *size); g = rn.ground(sc); cam = rn.camera(sc)
    obs = list(B['obs'].values()); pts = []
    for st in setters:
        st(); pts += rn.mesh_points(obs)[::3]
    rn.fit(sc, cam, pts, view, (0.94, 0.92))
    tiles = []
    for i, st in enumerate(setters):
        st(); p = rn.render_to(sc, os.path.join(CHECK, f'tile_{i}.png')); tiles.append(rn.load_px(p)); os.remove(p)
    rn.compose(tiles, cols, out)
    bpy.data.objects.remove(g, do_unlink=True)


def bend_poses(sk, sp):
    """extremes: legs, neck down/back/twist, peck reach, head yaw, body pitch/roll, wings folded ruffle, flight up/down with
    max lag, flight with feet tucked (whole pose)"""
    P = []; rot = hc.rot; ws = lambda p, **kw: [hc.wing_set(sk, sp, p, s, **kw) for s in ('L', 'R')]

    def mk(fn):
        p = hc.new_pose(sk); fn(p); P.append(p)
    mk(lambda p: [rot(p, 'LegUpper.L', x=-70), rot(p, 'LegLower.L', x=110), rot(p, 'Foot.L', x=70),
                  rot(p, 'LegUpper.R', x=50, z=-30), rot(p, 'LegLower.R', x=-40)])
    mk(lambda p: [rot(p, 'Neck1', x=50), rot(p, 'Neck2', x=40), rot(p, 'Head', x=20), rot(p, 'Beak_Lower', x=30)])
    mk(lambda p: [rot(p, 'Neck1', x=-30), rot(p, 'Neck2', x=-30), rot(p, 'Head', x=-30)])
    mk(lambda p: [rot(p, 'Neck1', y=30), rot(p, 'Neck2', y=30), rot(p, 'Head', z=-80, y=30)])
    mk(lambda p: [ws(p, spread=0.0, fold=40), rot(p, 'TailFan1', x=40, z=30)])
    F = sp.get('fly', {})
    mk(lambda p: [ws(p, flap=F.get('mid', 10) + F.get('amp', 55), lag=(-F.get('lag', (20, 20))[0], -F.get('lag', (20, 20))[1]),
                     sweep=F.get('sweep', 0) - F.get('sweep_up', 0), lsweep=(10, 14))])
    mk(lambda p: [ws(p, flap=F.get('mid', 10) - F.get('amp', 55), lag=(F.get('lag', (20, 20))[0], F.get('lag', (20, 20))[1]),
                     twist=F.get('twist', 0))])
    mk(lambda p: [hc.body(sk, p, (0, 0, 0.0), pitch=F.get('pitch', 15)),
                  [rot(p, b, x=a) for b, a in zip(('LegUpper.L', 'LegLower.L', 'Foot.L', 'LegUpper.R', 'LegLower.R', 'Foot.R'),
                                                  F.get('leg', (60, 60, 60)) * 2)], ws(p, flap=F.get('mid', 10))])
    return P


# ---------------- clips ----------------
def anim(B):
    sk = B['sk']; sp = B['SP']
    clips = hc.build_clips(sk, sp)
    apply_orders(B['rig'], sk)
    acts = {c: hc.write_action(B['rig'], f"{sp['species']}_{c}", clips[c]['frames'], clips[c]['loop'], sk.mover) for c, _, _ in sp['clips']}
    for c in clips:
        if clips[c]['events']: print(c.upper(), 'events', clips[c]['events'])
    rep = hc.metrics(B['sc'], B['rig'], B['tmp'], sk, {c: clips[c] for c, _, _ in sp['clips']}, acts, sp['limits'])
    return clips, acts, rep


def clip_strips(B, clips, acts, n=8):
    sc = B['sc']; rig = B['rig']
    for c, _, _ in B['SP']['clips']:
        act = acts[c]; N = int(act.frame_end)
        fr = [round(i * N / n) for i in range(n)]
        an.assign(rig, act)
        setters = [(lambda f=f: (sc.frame_set(f), bpy.context.view_layer.update())) for f in fr]
        views = B['SP'].get('strip_views', {}).get(c, [(1.0, -0.02, 0.10) if c in ('Peck', 'Hop') else (0.6, -1.0, 0.35)])
        for k, view in enumerate(views):
            strip(B, setters, os.path.join(CHECK, f"{B['SP']['species']}_strip_{c}_{k}.png"), view)
    an.assign(rig, None); sc.frame_set(0)


# ---------------- export (copies of rig_hen.export_nla / reimport_check / events_json) ----------------
def export_nla(rig, parts, actions, fbx):
    ad = rig.animation_data or rig.animation_data_create(); sc = bpy.context.scene
    assert sc.render.fps == 30 and sc.render.fps_base == 1.0
    for pb in rig.pose.bones: pb.location = (0, 0, 0); pb.rotation_euler = (0, 0, 0)
    for o in sc.objects: o.select_set(False)
    rig.select_set(True)
    for o in parts: o.select_set(True)
    bpy.context.view_layer.objects.active = rig
    for tr in list(ad.nla_tracks): ad.nla_tracks.remove(tr)
    ad.action = None
    for act in actions:
        tr = ad.nla_tracks.new(); tr.name = act.name
        st = tr.strips.new(act.name, int(act.frame_start), act); st.name = act.name
    bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True, apply_scale_options='FBX_SCALE_ALL', axis_forward='-Z', axis_up='Y',
                             bake_space_transform=True, object_types={'ARMATURE', 'MESH'}, mesh_smooth_type='FACE',
                             use_mesh_modifiers=True, use_armature_deform_only=False, add_leaf_bones=False, primary_bone_axis='Y',
                             secondary_bone_axis='X', armature_nodetype='NULL', path_mode='COPY', embed_textures=False, bake_anim=True,
                             bake_anim_use_all_bones=True, bake_anim_force_startend_keying=True, bake_anim_step=1.0,
                             bake_anim_simplify_factor=0.0, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=False)
    for tr in list(ad.nla_tracks): ad.nla_tracks.remove(tr)
    print('exported', fbx)


def _base(n):
    return n.rsplit('.', 1)[0] if n[-4:-3] == '.' and n[-3:].isdigit() else n


def reimport_check(fbx, rig, parts, actions):
    win = bpy.context.window; prev = win.scene
    sc = bpy.data.scenes.new('TMP_FBXVerify'); win.scene = sc
    before_a = set(bpy.data.actions); before_o = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=fbx, use_anim=True)
    new_obs = [o for o in bpy.data.objects if o not in before_o]
    irig = next(o for o in new_obs if o.type == 'ARMATURE')
    imesh = {_base(o.name): o for o in new_obs if o.type == 'MESH'}
    new_acts = [a for a in bpy.data.actions if a not in before_a]
    res = dict(import_bones=len(irig.data.bones), import_meshes=len(imesh), import_actions=sorted(a.name for a in new_acts),
               import_tris=sum(len(p.vertices) - 2 for o in imesh.values() for p in o.data.polygons),
               import_frame_ranges={a.name: [round(x, 2) for x in a.frame_range] for a in new_acts},
               images=[(i.name, os.path.isfile(bpy.path.abspath(i.filepath))) for i in bpy.data.images if i.filepath])
    names = sorted(o.name for o in parts); src = {o.name: o for o in parts}
    missing = [n for n in names if n not in imesh]

    def world(objs):
        dg = bpy.context.evaluated_depsgraph_get(); out = []
        for o in objs:
            me = o.evaluated_get(dg).to_mesh(); out += [o.matrix_world @ v.co for v in me.vertices]; o.evaluated_get(dg).to_mesh_clear()
        return out
    errs = {}
    for act in actions:
        ia = next((a for a in new_acts if a.name == act.name or a.name.endswith('|' + act.name)), None)
        if ia is None or missing: errs[act.name] = None; continue
        N = int(act.frame_end); worst = 0.0
        for f in sorted({0, N // 4, N // 3, N // 2, (2 * N) // 3, N}):
            win.scene = prev; an.assign(rig, act); prev.frame_set(f); A = world([src[n] for n in names])
            win.scene = sc; iad = irig.animation_data or irig.animation_data_create(); iad.action = ia
            if ia.slots: iad.action_slot = ia.slots[0]
            sc.frame_set(f + int(round(ia.frame_range[0]))); Bv = world([imesh[n] for n in names])
            if len(A) != len(Bv): worst = float('inf'); break
            worst = max(worst, max((a - b).length for a, b in zip(A, Bv)))
        errs[act.name] = round(worst, 5)
    res['missing_parts'] = missing; res['max_vertex_error_m'] = errs
    win.scene = prev; an.assign(rig, None)
    for o in new_obs:
        d = o.data; bpy.data.objects.remove(o, do_unlink=True)
        try:
            if d is not None and d.users == 0: (bpy.data.meshes if isinstance(d, bpy.types.Mesh) else bpy.data.armatures).remove(d)
        except Exception: pass
    for a in new_acts: bpy.data.actions.remove(a)
    bpy.data.scenes.remove(sc)
    print('REIMPORT', {k: v for k, v in res.items() if k != 'import_actions'}); print('REIMPORT actions', res['import_actions'])
    return res


def events_json(sp, clips, path):
    d = dict(species=sp['species'], asset=ASSET, fps=an.FPS, note='Unity AnimationEvents to add on import (FBX does not carry them)',
             clips={})
    for c, T, loop in sp['clips']:
        C = clips[c]; N = len(C['frames']) - 1
        e = dict(take=f"{sp['species']}_{c}", seconds=round(N / an.FPS, 3), last_frame=N, loop=loop,
                 events=[dict(name=n, frame=f, time=round(f / an.FPS, 4), stringParameter=p) for f, n, p in C['events']])
        if 'speed' in C.get('extra', {}): e['speed_mps'] = round(C['extra']['speed'], 4)
        d['clips'][c] = e
    json.dump(d, open(path, 'w'), indent=1); print('events', path)


def meshcheck(B):
    """built (rest) mesh vs the ORIGINAL mesh-only FBX backup in TEMP/FarmAnimals_flight_bak: per part vertex sets"""
    fbx = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_flight_bak', ASSET + '.fbx')
    win = bpy.context.window; prev = win.scene; sc = bpy.data.scenes.new('TMP_MeshCheck'); win.scene = sc
    before = set(bpy.data.objects); bpy.ops.import_scene.fbx(filepath=fbx)
    new = [o for o in bpy.data.objects if o not in before]; im = {_base(o.name): o for o in new if o.type == 'MESH'}
    worst = 0.0; missing = []
    for nm, o in B['obs'].items():
        if nm not in im: missing.append(nm); continue
        A = sorted(tuple(round(c, 4) for c in p) for p in _pts(o)); Bv = sorted(tuple(round(c, 4) for c in p) for p in _pts(im[nm]))
        if len(A) != len(Bv): worst = float('inf'); continue
        worst = max(worst, max(max(abs(x - y) for x, y in zip(a, b)) for a, b in zip(A, Bv)))
    win.scene = prev
    for o in new: bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.scenes.remove(sc)
    print(f'MESHCHECK vs {fbx}: parts {len(B["obs"])} missing {missing} max vertex diff {worst:.5f} m')
    return worst, missing


def main(sp, bm_module):
    configure(sp, bm_module)
    ID, CMD = args(sp['id'])
    print('===', sp['id'], sp['species'], 'rig', CMD)
    if CMD == 'bend':
        B = rig_model(os.path.join(CHECK, 'tex')); poses = bend_poses(B['sk'], B['SP'])
        setters = [(lambda p=p: apply_pose(B['rig'], B['sk'], p)) for p in poses]
        for nm, view in B['SP'].get('bend_views', {'side': (1.0, -0.15, 0.2), 'front': (-0.6, -1.0, 0.45)}).items():
            strip(B, setters, os.path.join(CHECK, f"{sp['species']}_bend_{nm}.png"), view)
    elif CMD == 'meshcheck':
        B = BM.build(os.path.join(CHECK, 'tex')); meshcheck(B)
    elif CMD == 'anim':
        B = rig_model(os.path.join(CHECK, 'tex')); clips, acts, rep = anim(B)
        json.dump(rep, open(os.path.join(WORK, 'metrics_report.json'), 'w'), indent=1)
        clip_strips(B, clips, acts)
    elif CMD == 'export':
        B = rig_model(os.path.join(ART, 'Textures')); clips, acts, rep = anim(B)
        sp = B['SP']; parts = list(B['obs'].values()); al = [acts[c] for c, _, _ in sp['clips']]
        bpy.data.objects.remove(B['tmp'], do_unlink=True)
        fbx = os.path.join(ART, 'Meshes', ASSET + '.fbx')
        export_nla(B['rig'], parts, al, fbx)
        summ = ax.fbx_summary(fbx)
        X = reimport_check(fbx, B['rig'], parts, al)
        events_json(sp, clips, os.path.join(ART, 'Meshes', ASSET + '.events.json'))
        coll = B['coll']
        data = {coll} | set(coll.objects) | {o.data for o in coll.objects if o.data} | {B['mat'], B['img']} | set(al)
        bpy.data.libraries.write(os.path.join(ART, 'Blend', ASSET + '.blend'), data, fake_user=True, path_remap='ABSOLUTE')
        print('blend', os.path.join(ART, 'Blend', ASSET + '.blend'), 'objects', len(coll.objects), 'actions', [a.name for a in al])
        full = dict(asset=ASSET, tris=B['total'], bones=len(B['rig'].data.bones), rig=B['rig_checks'],
                    euler_orders={n: o for n, o in B['sk'].eorder.items() if o != 'XYZ'}, clips=rep,
                    export=dict(fbx=fbx, takes=[(s['name'], s['frames30']) for s in summ['stacks']], limbs=summ['limb_nodes'],
                                roots=summ['roots'], reimport=X))
        json.dump(full, open(os.path.join(WORK, 'metrics_report.json'), 'w'), indent=1, default=str)
        print('report', os.path.join(WORK, 'metrics_report.json'))


if __name__ == '__main__':
    import build_pigeon
    main(PIGEON, build_pigeon)
