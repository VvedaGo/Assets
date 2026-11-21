# rig_dog.py - PET-01 Dog: skeleton Q without Horn.L/R (Cow names, Tail1-3) + Ruff (child of Spine2) = 26 bones,
# binding of the final mesh parts (each part = its bone, weight 1.0; Eye.L/R and Nose -> Head; the black cheek fins are part
# of Head), two-bone blends: knee/hock line (Goat), the neck path Spine2|Neck1|Neck2|Head (Goat), the tail path
# Tail1|Tail2|Tail3 (50/50 at each joint: the bushy tail wags wide), the Ruff fading from its own bone (chest) to Neck1
# (under the cheeks). Bend test, clips Dog_Idle / Dog_Walk, metrics, FBX + .blend.
# Pattern: ../Goat/rig_goat.py (read-only).
#   PYTHONUTF8=1 blender --background --factory-startup --python rig_dog.py -- PET-01 bend|anim|export
# bend  : rig + extreme poses -> strips (TEMP)
# anim  : rig + clips + metrics (metrics_report.json) + clip strips (TEMP)
# export: anim + FBX (skinned parts + armature + 2 takes, NLA, bake_space_transform) + re-import check + events json + .blend
# The mesh comes unchanged from build_dog.build() (geometry, part names and pivots untouched).
import sys, os, math, json, importlib
REPO = r'C:\Users\Sergv\orca\workspaces\VFX\master-3'
WORK = REPO + r'\.work\models\Farm_Animals\Dog'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common', WORK):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
import numpy as np
from mathutils import Vector
import pack_common as pc
import animal_render as rn, animal_rig as ar, animal_species as asp, animal_anim as an, animal_export as ax
import build_dog as bd
import dog_clips as dcl
for m in (bd, dcl): importlib.reload(m)

ASSET = bd.ASSET; ART = bd.ART
CHECK = bd.CHECK
os.makedirs(CHECK, exist_ok=True)

ar.SKELETONS['QD'] = [b for b in ar.Q_BONES if not b[0].startswith('Horn')] + [('Ruff', 'Spine2')]
BIND = {'Eye.L': 'Head', 'Eye.R': 'Head', 'Nose': 'Head'}
LIMITS = dict(asp.Q_LIMITS, Ruff=dict(x=(-15, 50), y=(-10, 10), z=(-15, 15)),   # sit: ruff hangs on the chest
             
              Pelvis=dict(x=(-65, 25), y=(-15, 15), z=(-15, 15)),    # Sit_Idle: pelvis pitched nose-up (sitting)
              FrontUpper=dict(x=(-75, 70), z=(-25, 25)), HindUpper=dict(x=(-60, 130), z=(-80, 80)))   # sit: shoulder, hip flexion; hip z: thighs splayed 50 deg with the pelvis pitched -54 (euler z -76)   # HindLower set from the rest bend below


def bone_of(part):
    return BIND.get(part, part)


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['PET-01', 'bend'])[:2]


def far_vertex(o, piv):
    M = o.matrix_world
    return max((M @ v.co for v in o.data.vertices), key=lambda p: (p - piv).length)


def species(obs):
    """dog table in the animal_species format; bone heads = part pivots (joints), tails = next joint / far vertex"""
    P = {k: o.matrix_world.translation.copy() for k, o in obs.items()}
    t = lambda v: tuple(round(c, 4) for c in v)
    rz = min((o.matrix_world @ v.co for o in (obs['Ruff'],) for v in o.data.vertices), key=lambda p: p.z)
    B = {'Root': ((0, 0, 0), (0, -0.25, 0)),
         'Pelvis': (t(P['Pelvis']), t(P['Spine1'])), 'Spine1': (t(P['Spine1']), t(P['Spine2'])),
         'Spine2': (t(P['Spine2']), t(P['Neck1'])), 'Neck1': (t(P['Neck1']), t(P['Neck2'])),
         'Neck2': (t(P['Neck2']), t(P['Head'])), 'Head': (t(P['Head']), t(P['Nose'])),
         'Jaw': (t(P['Jaw']), t(far_vertex(obs['Jaw'], P['Jaw']))),
         'Ruff': (t(P['Ruff']), t(Vector((0.0, rz.y, rz.z)))),
         'Ear.L': (t(P['Ear.L']), t(far_vertex(obs['Ear.L'], P['Ear.L']))),
         'Tail1': (t(P['Tail1']), t(P['Tail2'])), 'Tail2': (t(P['Tail2']), t(P['Tail3'])),
         'Tail3': (t(P['Tail3']), t(far_vertex(obs['Tail3'], P['Tail3'])))}
    for kind in ('Front', 'Hind'):
        u, l, f = P[kind + 'Upper.L'], P[kind + 'Lower.L'], P[kind + 'Foot.L']
        B[kind + 'Upper.L'] = (t(u), t(l)); B[kind + 'Lower.L'] = (t(l), t(f)); B[kind + 'Foot.L'] = (t(f), t(Vector((f.x, f.y, 0.0))))
    return dict(id='PET-01', species='Dog', asset=ASSET, tag=bd.TAG, skeleton='QD', bones=B,
                size=dict(length=1.355, withers=0.757),
                # Walk round 2: 34 fr (1.133 s), stride 0.60 m (0.44x nose->tail), stance travel 0.372 m, diagonal couplets
                # (front 0.18 cycle after its diagonal hind: same-side paws >= 0.2 m apart, paws are 0.18 m long);
                # stance centred under shoulder/hip; front legs 0.995 straight in stance, hind 0.97 (hock bent back)
                gait={'Walk': dict(T=34 / 30, duty=0.60, stride=0.60, harm=18, harm_hind=5, lift=(0.065, 0.065), lift_skew=(0.85, 1.0), flick=(32, 24),
                                   straight=(0.9995, 0.985), centre=(0.0, 0.0), out=(0.0, 0.005), crouch=0.0, roll=1.5, sway=0.006,
                                   phases={'HindL': 0.0, 'FrontR': 0.18, 'HindR': 0.5, 'FrontL': 0.68},
                                   ear=4.0, tail=(8.0, 12.0, 16.0), tail_bounce=3.0, ruff=2.5)},
                idle=dict(wag=(24.0, 32.0, 40.0), lag=0.10, hip=1.5, ear=14.0, tail_lift=(14.0, 6.0, 2.0),
                          hind_drop=0.03, front_drop=0.004, hind_back=0.02, shift=0.012, shift_roll=0.0, breath=0.005, breath_spine=1.6),
                sit=dict(tilt=57.0, spine=(-6.0, -8.0), rump_z=0.01, front_ext=0.995, front_out=0.04, head_level=1.0, ruff=26.0,
                         paw_fwd=0.03, hock_z=0.095, hock_splay=50.0, cannon_in=15.0, cannon_slope=8.0, tail_z=0.11,
                         tail_curve=(-18.0, -38.0), tail_tip_up=4.0, breaths=2, tip_lift=16.0, tip_wag=12.0),
                clips=[('Idle', 3.0, True), ('Walk', 34 / 30, True), ('Sit_Idle', 3.5, True)], limits=LIMITS, poses={})


def path_weights(co, pts, bones, root=None):
    """continuous weights along a joint chain pts[0..n] (s = segment index + fraction): 50/50 at the inner joints,
    each bone alone in the middle of its segment; `root` = {bone: w} at s = 0 (else the first bone alone)"""
    s = 0.0
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        u = (co - a).dot(b - a) / (b - a).length_squared
        if u < 1.0 or i == len(pts) - 2: s = i + max(0.0, u); break
    knots = [(0.0, root or {bones[0]: 1.0})]
    for i, bn in enumerate(bones):
        knots.append((i + 0.5, {bn: 1.0}))
        if i < len(bones) - 1: knots.append((i + 1.0, {bn: 0.5, bones[i + 1]: 0.5}))
    if s >= knots[-1][0]: return dict(knots[-1][1])
    for (s0, w0), (s1, w1) in zip(knots, knots[1:]):
        if s0 <= s <= s1:
            u = (s - s0) / (s1 - s0); out = {}
            for k, w in w0.items(): out[k] = out.get(k, 0.0) + w * (1 - u)
            for k, w in w1.items(): out[k] = out.get(k, 0.0) + w * u
            return {k: w for k, w in out.items() if w > 1e-4}
    return dict(knots[0][1])


def part_weights(nm, co, P, tail_pts):
    b = bone_of(nm)
    if nm in ('Neck1', 'Neck2'):
        return neck_weights(co, P)
    if nm in ('Tail1', 'Tail2', 'Tail3'):
        return path_weights(co, tail_pts, ['Tail1', 'Tail2', 'Tail3'])
    if nm == 'Ruff':                                   # chest -> own bone, under the cheeks -> follows the neck
        z0, z1 = P['Neck1'].z, P['Neck2'].z + 0.06
        u = an.smooth((co.z - z0) / (z1 - z0))
        return {k: w for k, w in (('Ruff', 1.0 - u), ('Neck1', u)) if w > 1e-4}
    for s in ('.L', '.R'):
        for k in ('Front', 'Hind'):
            up, lo, ft = k + 'Upper' + s, k + 'Lower' + s, k + 'Foot' + s
            if nm not in (up, lo): continue
            zk = P[lo].z; zf = P[ft].z
            if nm == up:
                return {up: 0.5, lo: 0.5} if abs(co.z - zk) < 0.008 else {up: 1.0}
            if co.z < zf: return {ft: 1.0}
            if co.z > zk + 0.008: return {up: 1.0}
            return {up: 0.5, lo: 0.5}
    return {b: 1.0}


def neck_weights(co, P):
    """copy of the Goat neck path: Spine2|Neck1 50/50 at the root, Neck1|Neck2 50/50, Neck2|Head 20/80 at the skull"""
    A, Bp, C = P['Neck1'], P['Neck2'], P['Head']
    t1 = (co - A).dot(Bp - A) / (Bp - A).length_squared
    s = t1 if t1 < 1.0 else 1.0 + max(0.0, (co - Bp).dot(C - Bp) / (C - Bp).length_squared)
    knots = [(0.0, {'Spine2': 0.5, 'Neck1': 0.5}), (0.5, {'Neck1': 1.0}), (1.0, {'Neck1': 0.5, 'Neck2': 0.5}),
             (1.5, {'Neck2': 1.0}), (2.0, {'Neck2': 0.2, 'Head': 0.8})]
    if s <= knots[0][0]: return dict(knots[0][1])
    if s >= knots[-1][0]: return dict(knots[-1][1])
    for (s0, w0), (s1, w1) in zip(knots, knots[1:]):
        if s0 <= s <= s1:
            u = (s - s0) / (s1 - s0); out = {}
            for k, w in w0.items(): out[k] = out.get(k, 0.0) + w * (1 - u)
            for k, w in w1.items(): out[k] = out.get(k, 0.0) + w * u
            return {k: w for k, w in out.items() if w > 1e-4}


def joined(obs, rig, P, tail_pts):
    """TMP world-space copy of all parts with the same weights (for animal_anim.Skel and the metrics); never exported"""
    names = [b.name for b in rig.data.bones]; gi = {n: i for i, n in enumerate(names)}
    me = bpy.data.meshes.new('TMP_DogAll'); ob = bpy.data.objects.new('TMP_DogAll', me)
    bpy.context.scene.collection.objects.link(ob)
    for n in names: ob.vertex_groups.new(name=n)
    bm = bmesh.new(); dl = bm.verts.layers.deform.verify()
    for nm, o in obs.items():
        M = o.matrix_world; vm = {}
        for v in o.data.vertices:
            co = M @ v.co; nv = bm.verts.new(co)
            for bn, w in part_weights(nm, co, P, tail_pts).items(): nv[dl][gi[bn]] = w
            vm[v.index] = nv
        for p in o.data.polygons: bm.faces.new([vm[i] for i in p.vertices])
    bm.to_mesh(me); bm.free()
    ob.modifiers.new('Armature', 'ARMATURE').object = rig; ob.hide_render = True
    return ob


def rig_model(tex_dir):
    B = bd.build(tex_dir)
    sc = B['sc']; sc.render.fps = 30; sc.render.fps_base = 1.0
    SP = species(B['obs'])
    P = {k: o.matrix_world.translation.copy() for k, o in B['obs'].items()}
    tail_pts = [Vector(SP['bones']['Tail1'][0]), Vector(SP['bones']['Tail2'][0]), Vector(SP['bones']['Tail3'][0]),
                Vector(SP['bones']['Tail3'][1])]
    rig = ar.build_armature(SP, B['coll'], 'QD')
    rchk = ar.check_rig(rig, 'QD')
    nblend = 0
    for nm, ob in B['obs'].items():
        mw = ob.matrix_world.copy(); ob.parent = rig; ob.matrix_parent_inverse.identity(); ob.matrix_world = mw
        for g in list(ob.vertex_groups): ob.vertex_groups.remove(g)
        groups = {}
        for v in ob.data.vertices:
            wd = part_weights(nm, mw @ v.co, P, tail_pts)
            if len(wd) > 1: nblend += 1
            for bn, w in wd.items():
                if bn not in groups: groups[bn] = ob.vertex_groups.new(name=bn)
                groups[bn].add([v.index], w, 'REPLACE')
        ob.modifiers.new('Armature', 'ARMATURE').object = rig
    bpy.data.objects.remove(B['root'], do_unlink=True)
    bpy.context.view_layer.update()
    tmp = joined(B['obs'], rig, P, tail_pts)
    sk = an.Skel(rig, tmp)
    print(f'RIG bones {len(rig.data.bones)} | parts bound {len(B["obs"])} | 2-bone blended vertices {nblend} | groups',
          sorted({bone_of(n) for n in B['obs']}))
    B.update(rig=rig, rig_checks=rchk, tmp=tmp, sk=sk, SP=SP, nblend=nblend)
    return B


# ---------------- strips ----------------
def apply_pose(rig, pose):
    for n, (l, r) in pose.items():
        pb = rig.pose.bones[n]; pb.location = l; pb.rotation_euler = r
    bpy.context.view_layer.update()


def strip(B, setters, out, view, cols=4, size=(320, 240)):
    sc = B['sc']; rn.setup_workbench(sc, *size); g = rn.ground(sc); cam = rn.camera(sc)
    obs = list(B['obs'].values()); pts = []
    for st in setters:
        st(); pts += rn.mesh_points(obs)[::5]
    rn.fit(sc, cam, pts, view, (0.94, 0.92))
    tiles = []
    for i, st in enumerate(setters):
        st(); p = rn.render_to(sc, os.path.join(CHECK, f'tile_{i}.png')); tiles.append(rn.load_px(p)); os.remove(p)
    rn.compose(tiles, cols, out)
    bpy.data.objects.remove(g, do_unlink=True)


def bend_poses(sk):
    P = []

    def mk(fn):
        p = an.new_pose(sk); fn(p); P.append(p)
    mk(lambda p: [an.rot(p, 'FrontUpper.L', x=-45), an.rot(p, 'FrontUpper.R', x=35), an.rot(p, 'HindUpper.L', x=45), an.rot(p, 'HindUpper.R', x=-35)])
    mk(lambda p: [an.rot(p, 'FrontLower.L', x=100), an.rot(p, 'FrontFoot.L', x=50), an.rot(p, 'HindLower.L', x=-90), an.rot(p, 'HindFoot.L', x=-50),
                  an.rot(p, 'FrontUpper.R', z=-20), an.rot(p, 'HindUpper.R', z=20)])
    mk(lambda p: [an.rot(p, 'Neck1', x=40), an.rot(p, 'Neck2', x=25), an.rot(p, 'Head', x=20), an.rot(p, 'Ruff', x=8)])   # head down
    mk(lambda p: [an.rot(p, 'Neck1', x=-25), an.rot(p, 'Neck2', x=-20), an.rot(p, 'Head', x=-25), an.rot(p, 'Jaw', x=20),
                  an.rot(p, 'Ruff', x=-8)])                                                                        # head up
    mk(lambda p: [an.rot(p, 'Neck1', z=25), an.rot(p, 'Neck2', z=25), an.rot(p, 'Head', z=20)])
    mk(lambda p: [an.ear(p, up=30, back=-25), an.rot(p, 'Tail1', z=25), an.rot(p, 'Tail2', z=30), an.rot(p, 'Tail3', z=35)])
    mk(lambda p: [an.ear(p, up=-25, back=25), an.rot(p, 'Tail1', x=25, z=-25), an.rot(p, 'Tail2', x=15, z=-30), an.rot(p, 'Tail3', z=-35)])
    mk(lambda p: [an.body(sk, p, (0, 0, 0), pitch=10, roll=8), an.rot(p, 'Spine1', x=6, z=6), an.rot(p, 'Spine2', x=6, z=-6),
                  an.rot(p, 'Ruff', z=10)])
    return P


# ---------------- clips ----------------
def leg_checks(sk, clips):
    """per clip: joint bend direction in bone-local terms (lower x relative to the straight value; front carpus may only
    flex forward (+), hind hock only backward (-), tolerance 1 deg), the largest stance bow of the front legs (joint
    offset from the shoulder->paw line, walk), the smallest same-side paw gap (paw centres along the body) and the
    smallest left/right paw gap (x) - paws are 0.18 m long, 0.13 m wide"""
    out = {}
    st_ = {k: -math.degrees(dcl._IK[k][0]) for k in an.LEGS}          # lower x of a straight leg
    for c, C in clips.items():
        wrong = []; flex = {k: [1e9, -1e9] for k in an.LEGS}; bow = 0.0; gap_s = 1e9; gap_x = 1e9
        stance = (C.get('extra') or {}).get('stance', {})
        for f, p in enumerate(C['frames'][:-1]):
            M = sk.fk(p); paw = {}
            for k in an.LEGS:
                up, lo, ft, front = ar.LEGS[k]
                b = math.degrees(p[lo][1][0]) - st_[k]; flex[k][0] = min(flex[k][0], b); flex[k][1] = max(flex[k][1], b)
                if (front and b < -1.0) or (not front and b > 1.0): wrong.append((f, k, round(b, 1)))
                paw[k] = M[ft].translation
                if front and f in stance.get(k, []):
                    H = M[up].translation; K = M[lo].translation; F = M[ft].translation
                    d = (F - H).normalized(); bow = max(bow, (K - H - d * (K - H).dot(d)).length)
            for s in ('L', 'R'): gap_s = min(gap_s, paw['Hind' + s].y - paw['Front' + s].y)
            for g in ('Front', 'Hind'): gap_x = min(gap_x, abs(paw[g + 'L'].x - paw[g + 'R'].x))
        out[c] = dict(wrong_way_frames=len(wrong), wrong_examples=wrong[:6],
                      flex_deg={k: [round(a, 1), round(b, 1)] for k, (a, b) in flex.items()},
                      front_stance_bow_m=round(bow, 4) if stance else None, min_same_side_paw_gap_m=round(gap_s, 3),
                      min_left_right_paw_gap_m=round(gap_x, 3))
        print('LEGS', c, out[c])
    return out


def anim(B):
    sk = B['sk']; SP = B['SP']
    clips = dcl.build_clips(sk, SP)
    de = math.degrees(dcl._IK['HindL'][0])            # hock rest flex: straight leg = HindLower x of +|rest|
    SP['limits']['HindLower'] = dict(x=(-170, max(3.0, abs(de) + 3.0)))
    acts = {}
    for c, _, _ in SP['clips']:
        C = clips[c]
        acts[c] = an.write_action(B['rig'], f"{SP['species']}_{c}", C['frames'], C['loop'], C['bones'])
    ex = clips['Walk']['extra']
    print('WALK step', round(ex['step'], 3), 'drop front max/min', max(ex['drops']['Front']), min(ex['drops']['Front']),
          'hind', max(ex['drops']['Hind']), min(ex['drops']['Hind']))
    rep = an.metrics(B['sc'], B['rig'], B['tmp'], {c: clips[c] for c, _, _ in SP['clips']}, acts, SP['limits'])
    for c, v in leg_checks(sk, clips).items(): rep[c]['legs'] = v
    if 'sit' in clips.get('Sit_Idle', {}).get('extra', {}): rep['Sit_Idle']['sit_pose'] = clips['Sit_Idle']['extra']['sit']
    # tail wag amplitude (Blender evaluation): lateral travel of the tail tip over the Idle clip
    sc = B['sc']; rig = B['rig']; an.assign(rig, acts['Idle']); xs = []
    for f in range(int(acts['Idle'].frame_end) + 1):
        sc.frame_set(f); xs.append(rig.pose.bones['Tail3'].tail.x)
    an.assign(rig, None); sc.frame_set(0)
    rep['Idle']['tail_tip_lateral_m'] = [round(min(xs), 3), round(max(xs), 3)]
    rep['Idle']['wag_hz'] = round(dcl.WAGS / 3.0, 3)
    print('IDLE tail tip x min/max', round(min(xs), 3), round(max(xs), 3))
    return clips, acts, rep


def clip_strips(B, clips, acts):
    sc = B['sc']; rig = B['rig']
    only = os.environ.get('DOG_STRIPS')
    for c, _, _ in B['SP']['clips']:
        if only and c not in only.split(','): continue
        act = acts[c]; N = int(act.frame_end)
        fr = [round(i * N / 12) for i in range(12)]
        views = {'Idle': [('side', (1.0, 0.0, 0.06)), ('back', (-0.35, 1.0, 0.6)), ('q', (1.0, -0.55, 0.17))],
                 'Walk': [('side', (1.0, 0.0, 0.04)), ('q', (1.0, -0.55, 0.17))],
                 'Sit_Idle': [('side', (1.0, 0.0, 0.06)), ('q', (1.0, -0.55, 0.17)), ('front', (0.25, -1.0, 0.15))]}[c]
        if c != 'Walk': fr = fr[:4]
        an.assign(rig, act)
        setters = [(lambda f=f: (sc.frame_set(f), bpy.context.view_layer.update())) for f in fr]
        for vn, view in views:
            strip(B, setters, os.path.join(CHECK, f'Dog_strip_{c}_{vn}.png'), view, cols=4 if c != 'Walk' else 6, size=(300, 230))
        print('strip', c, 'frames', fr)
    an.assign(rig, None); sc.frame_set(0)


# ---------------- export (copies of the Goat steps) ----------------
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
        for f in sorted({0, N // 3, (2 * N) // 3, N}):
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


def events_json(SP, clips, path):
    d = dict(species=SP['species'], asset=ASSET, fps=an.FPS, note='Unity AnimationEvents to add on import (FBX does not carry them)',
             clips={})
    for c, T, loop in SP['clips']:
        C = clips[c]; N = len(C['frames']) - 1
        e = dict(take=f"{SP['species']}_{c}", seconds=round(N / an.FPS, 3), last_frame=N, loop=loop,
                 events=[dict(name=n, frame=f, time=round(f / an.FPS, 4), stringParameter=p) for f, n, p in C['events']])
        if c in SP['gait']: e['speed_mps'] = round(C['extra']['speed'], 4)
        d['clips'][c] = e
    json.dump(d, open(path, 'w'), indent=1); print('events', path)


if __name__ == '__main__':
    ID, CMD = args()
    print('=== PET-01 Dog rig', CMD)
    if CMD == 'bend':
        B = rig_model(os.path.join(CHECK, 'tex')); poses = bend_poses(B['sk'])
        setters = [(lambda p=p: apply_pose(B['rig'], p)) for p in poses]
        strip(B, setters, os.path.join(CHECK, 'Dog_bend_side.png'), (1.0, -0.15, 0.2))
        strip(B, setters, os.path.join(CHECK, 'Dog_bend_back.png'), (-0.6, 1.0, 0.45))
    elif CMD == 'sitlook':        # close views of one Sit_Idle frame (penetration check: ruff vs front legs, hind legs vs belly)
        B = rig_model(os.path.join(CHECK, 'tex')); clips, acts, rep = anim(B)
        an.assign(B['rig'], acts['Sit_Idle']); B['sc'].frame_set(26); bpy.context.view_layer.update()
        sc = B['sc']; rn.setup_workbench(sc, 480, 400); g = rn.ground(sc); cam = rn.camera(sc)
        pts = rn.mesh_points(list(B['obs'].values())); tiles = []
        for v in ((1.0, 0.0, 0.08), (0.0, -1.0, 0.1), (0.7, -1.0, 0.25), (-0.6, 1.0, 0.3), (1.0, 0.3, -0.25)):
            rn.fit(sc, cam, pts, v, (0.9, 0.9)); pth = rn.render_to(sc, os.path.join(CHECK, 't.png')); tiles.append(rn.load_px(pth)); os.remove(pth)
        rn.compose(tiles, 3, os.path.join(CHECK, 'Dog_sit_views.png'))
    elif CMD == 'anim':
        B = rig_model(os.path.join(CHECK, 'tex')); clips, acts, rep = anim(B)
        json.dump(rep, open(os.path.join(WORK, 'metrics_report.json'), 'w'), indent=1)
        clip_strips(B, clips, acts)
    elif CMD == 'export':
        B = rig_model(os.path.join(ART, 'Textures')); clips, acts, rep = anim(B)
        SP = B['SP']; parts = list(B['obs'].values()); al = [acts[c] for c, _, _ in SP['clips']]
        bpy.data.objects.remove(B['tmp'], do_unlink=True)
        fbx = os.path.join(ART, 'Meshes', ASSET + '.fbx')
        export_nla(B['rig'], parts, al, fbx)
        summ = ax.fbx_summary(fbx)
        X = reimport_check(fbx, B['rig'], parts, al)
        events_json(SP, clips, os.path.join(ART, 'Meshes', ASSET + '.events.json'))
        coll = B['coll']
        data = {coll} | set(coll.objects) | {o.data for o in coll.objects if o.data} | {B['mat'], B['img']} | set(al)
        bpy.data.libraries.write(os.path.join(ART, 'Blend', ASSET + '.blend'), data, fake_user=True, path_remap='ABSOLUTE')
        print('blend', os.path.join(ART, 'Blend', ASSET + '.blend'), 'objects', len(coll.objects), 'actions', [a.name for a in al])
        full = dict(asset=ASSET, tris=B['total'], bones=len(B['rig'].data.bones), rig=B['rig_checks'], blended_vertices=B['nblend'],
                    clips=rep, export=dict(fbx=fbx, takes=[(s['name'], s['frames30']) for s in summ['stacks']], limbs=summ['limb_nodes'],
                                           roots=summ['roots'], reimport=X))
        json.dump(full, open(os.path.join(WORK, 'metrics_report.json'), 'w'), indent=1, default=str)
        print('report', os.path.join(WORK, 'metrics_report.json'))
