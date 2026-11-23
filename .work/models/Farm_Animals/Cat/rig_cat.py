# rig_cat.py - PET-02 Cat: skeleton Q without Horn.L/R (Cow names, Tail1-3, Ear.L/R) = 25 bones, binding of the final
# mesh parts (each part = its bone, weight 1.0; Eye.L/R and Nose -> Head), two-bone blends where the bend test needs them:
# the spine path Pelvis|Spine1|Spine2 (50/50 at the joints: the back undulates in Walk), the neck path
# Spine2|Neck1|Neck2|Head (Dog/Goat copy), the tail path Tail1|Tail2|Tail3 (50/50 at the joints: S-curves), the knee
# line (upper/lower 50/50 within 6 mm of the knee). Bend test, clips Cat_Idle / Cat_Walk / Cat_Lie_Idle, metrics,
# FBX + .blend. Pattern: ../Dog/rig_dog.py (read-only). The mesh comes unchanged from build_cat.build().
#   PYTHONUTF8=1 blender --background --factory-startup --python rig_cat.py -- PET-02 bend|anim|export
import sys, os, math, json, importlib
REPO = r'D:\GitProjects\Assets_Farm'
WORK = REPO + r'\.work\models\Farm_Animals\Cat'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common', WORK):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
import animal_render as rn, animal_rig as ar, animal_species as asp, animal_anim as an, animal_export as ax
import build_cat as bc
import cat_clips as ccl
for m in (bc, ccl): importlib.reload(m)

ASSET = bc.ASSET; ART = bc.ART
CHECK = bc.CHECK
os.makedirs(CHECK, exist_ok=True)

ar.SKELETONS['QC'] = [b for b in ar.Q_BONES if not b[0].startswith('Horn')]
BIND = {'Eye.L': 'Head', 'Eye.R': 'Head', 'Nose': 'Head'}
LIMITS = dict(asp.Q_LIMITS, Tail1=dict(x=(-105, 80), z=(-60, 60)), FrontFoot=dict(x=(-70, 120)))   # paw flat at push-off   # cat: the tail can lie flat on the ground
KNEE_TOL = 0.006
# hind thigh -> Pelvis weights (top ring inside the body, ring at z 0.14) and Spine2 weight at the neck root; env override
# for testing (CAT_THIGH="0.7,0.0" CAT_NECK_ROOT=0.5 = the round-1 binding)
THIGH_W = tuple(float(v) for v in os.environ.get('CAT_THIGH', '1.0,0.0').split(','))
THIGH_MID_Z = 0.13
NECK_ROOT_W = float(os.environ.get('CAT_NECK_ROOT', '0.5'))


def bone_of(part):
    return BIND.get(part, part)


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['PET-02', 'bend'])[:2]


def far_vertex(o, piv):
    M = o.matrix_world
    return max((M @ v.co for v in o.data.vertices), key=lambda p: (p - piv).length)


def species(obs):
    """cat table in the animal_species format; bone heads = part pivots (joints), tails = next joint / far vertex"""
    P = {k: o.matrix_world.translation.copy() for k, o in obs.items()}
    t = lambda v: tuple(round(c, 4) for c in v)
    B = {'Root': ((0, 0, 0), (0, -0.10, 0)),
         'Pelvis': (t(P['Pelvis']), t(P['Spine1'])), 'Spine1': (t(P['Spine1']), t(P['Spine2'])),
         'Spine2': (t(P['Spine2']), t(P['Neck1'])), 'Neck1': (t(P['Neck1']), t(P['Neck2'])),
         'Neck2': (t(P['Neck2']), t(P['Head'])), 'Head': (t(P['Head']), t(P['Nose'])),
         'Jaw': (t(P['Jaw']), t(far_vertex(obs['Jaw'], P['Jaw']))),
         'Ear.L': (t(P['Ear.L']), t(far_vertex(obs['Ear.L'], P['Ear.L']))),
         'Tail1': (t(P['Tail1']), t(P['Tail2'])), 'Tail2': (t(P['Tail2']), t(P['Tail3'])),
         'Tail3': (t(P['Tail3']), t(far_vertex(obs['Tail3'], P['Tail3'])))}
    for kind in ('Front', 'Hind'):
        u, l, f = P[kind + 'Upper.L'], P[kind + 'Lower.L'], P[kind + 'Foot.L']
        B[kind + 'Upper.L'] = (t(u), t(l)); B[kind + 'Lower.L'] = (t(l), t(f)); B[kind + 'Foot.L'] = (t(f), t(Vector((f.x, f.y, 0.0))))
    return dict(id='PET-02', species='Cat', asset=ASSET, tag=bc.TAG, skeleton='QC', bones=B,
                size=dict(length=0.518, withers=0.300),
                gait={'Walk': dict(T=0.8, duty=0.62, speed=0.36, lift=0.034, flick=(10, 20), crouch=0.006, roll=1.2, bob=0.002,
                                   reach=0.99, narrow=0.80, spine=3.0, ear=3.0, tail=(4.0, 6.0, 8.0),
                                   phases={'HindL': 0.0, 'FrontL': 0.25, 'HindR': 0.5, 'FrontR': 0.75})},
                idle=dict(tail=(10.0, 16.0, 22.0), lag=0.22, hip=0.8, ear=22.0),
                clips=[('Idle', 3.5, True), ('Walk', 0.8, True), ('Lie_Idle', 4.0, True)], limits=LIMITS, poses={})


def path_weights(co, pts, bones, root=None):
    """continuous weights along a joint chain pts[0..n] (copy of ../Dog/rig_dog.path_weights)"""
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


def neck_weights(co, P):
    """copy of the Dog/Goat neck path: Spine2|Neck1 50/50 at the root, Neck1|Neck2 50/50, Neck2|Head 20/80 at the skull"""
    A, Bp, C = P['Neck1'], P['Neck2'], P['Head']
    t1 = (co - A).dot(Bp - A) / (Bp - A).length_squared
    s = t1 if t1 < 1.0 else 1.0 + max(0.0, (co - Bp).dot(C - Bp) / (C - Bp).length_squared)
    knots = [(0.0, {'Spine2': NECK_ROOT_W, 'Neck1': 1.0 - NECK_ROOT_W}), (0.5, {'Neck1': 1.0}), (1.0, {'Neck1': 0.5, 'Neck2': 0.5}),
             (1.5, {'Neck2': 1.0}), (2.0, {'Neck2': 0.2, 'Head': 0.8})]
    if s <= knots[0][0]: return dict(knots[0][1])
    if s >= knots[-1][0]: return dict(knots[-1][1])
    for (s0, w0), (s1, w1) in zip(knots, knots[1:]):
        if s0 <= s <= s1:
            u = (s - s0) / (s1 - s0); out = {}
            for k, w in w0.items(): out[k] = out.get(k, 0.0) + w * (1 - u)
            for k, w in w1.items(): out[k] = out.get(k, 0.0) + w * u
            return {k: w for k, w in out.items() if w > 1e-4}


def part_weights(nm, co, P, tail_pts, spine_pts):
    b = bone_of(nm)
    if nm in ('Pelvis', 'Spine1', 'Spine2'):
        return path_weights(co, spine_pts, ['Pelvis', 'Spine1', 'Spine2'])
    if nm in ('Neck1', 'Neck2'):
        return neck_weights(co, P)
    if nm in ('Tail1', 'Tail2', 'Tail3'):
        return path_weights(co, tail_pts, ['Tail1', 'Tail2', 'Tail3'])
    for s in ('.L', '.R'):
        for k in ('Front', 'Hind'):
            up, lo, ft = k + 'Upper' + s, k + 'Lower' + s, k + 'Foot' + s
            if nm not in (up, lo): continue
            zk = P[lo].z; zf = P[ft].z
            if nm == up:
                bb = 'Spine2' if k == 'Front' else 'Pelvis'
                if co.z > P[up].z - 0.005:            # thigh/shoulder top inside the body stays with the body when folded
                    return {bb: THIGH_W[0], up: 1.0 - THIGH_W[0]} if k == 'Hind' else {bb: 0.7, up: 0.3}
                # round 2 (ANIMATION_FIXES 2): the hind thigh's upper ring (z 0.14) is shared with the pelvis too, so the
                # long thigh faces between it and the body-bound top ring bend into a haunch instead of standing out of the
                # hip as a flat light slab in Lie_Idle
                if k == 'Hind' and co.z > THIGH_MID_Z:
                    return {bb: THIGH_W[1], up: 1.0 - THIGH_W[1]}
                return {up: 0.5, lo: 0.5} if abs(co.z - zk) < KNEE_TOL else {up: 1.0}
            if co.z < zf: return {ft: 1.0}
            if co.z > zk + KNEE_TOL: return {up: 1.0}
            if co.z > zk - KNEE_TOL: return {up: 0.5, lo: 0.5}
            return {lo: 1.0}
    return {b: 1.0}


def joined(obs, rig, P, tail_pts, spine_pts):
    """TMP world-space copy of all parts with the same weights (for animal_anim.Skel and the metrics); never exported"""
    names = [b.name for b in rig.data.bones]; gi = {n: i for i, n in enumerate(names)}
    me = bpy.data.meshes.new('TMP_CatAll'); ob = bpy.data.objects.new('TMP_CatAll', me)
    bpy.context.scene.collection.objects.link(ob)
    for n in names: ob.vertex_groups.new(name=n)
    bm = bmesh.new(); dl = bm.verts.layers.deform.verify()
    for nm, o in obs.items():
        M = o.matrix_world; vm = {}
        for v in o.data.vertices:
            co = M @ v.co; nv = bm.verts.new(co)
            for bn, w in part_weights(nm, co, P, tail_pts, spine_pts).items(): nv[dl][gi[bn]] = w
            vm[v.index] = nv
        for p in o.data.polygons: bm.faces.new([vm[i] for i in p.vertices])
    bm.to_mesh(me); bm.free()
    ob.modifiers.new('Armature', 'ARMATURE').object = rig; ob.hide_render = True
    return ob


def rig_model(tex_dir):
    B = bc.build(tex_dir)
    sc = B['sc']; sc.render.fps = 30; sc.render.fps_base = 1.0
    SP = species(B['obs'])
    P = {k: o.matrix_world.translation.copy() for k, o in B['obs'].items()}
    bn = SP['bones']
    tail_pts = [Vector(bn['Tail1'][0]), Vector(bn['Tail2'][0]), Vector(bn['Tail3'][0]), Vector(bn['Tail3'][1])]
    spine_pts = [Vector(bn['Pelvis'][0]), Vector(bn['Spine1'][0]), Vector(bn['Spine2'][0]), Vector(bn['Spine2'][1])]
    rig = ar.build_armature(SP, B['coll'], 'QC')
    rchk = ar.check_rig(rig, 'QC')
    nblend = 0
    for nm, ob in B['obs'].items():
        mw = ob.matrix_world.copy(); ob.parent = rig; ob.matrix_parent_inverse.identity(); ob.matrix_world = mw
        for g in list(ob.vertex_groups): ob.vertex_groups.remove(g)
        groups = {}
        for v in ob.data.vertices:
            wd = part_weights(nm, mw @ v.co, P, tail_pts, spine_pts)
            if len(wd) > 1: nblend += 1
            for b_, w in wd.items():
                if b_ not in groups: groups[b_] = ob.vertex_groups.new(name=b_)
                groups[b_].add([v.index], w, 'REPLACE')
        ob.modifiers.new('Armature', 'ARMATURE').object = rig
    bpy.data.objects.remove(B['root'], do_unlink=True)
    bpy.context.view_layer.update()
    tmp = joined(B['obs'], rig, P, tail_pts, spine_pts)
    sk = an.Skel(rig, tmp)
    print(f'RIG bones {len(rig.data.bones)} | parts bound {len(B["obs"])} | 2-bone blended vertices {nblend}')
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
    mk(lambda p: [an.rot(p, 'FrontLower.L', x=110), an.rot(p, 'FrontFoot.L', x=50), an.rot(p, 'HindLower.L', x=-100), an.rot(p, 'HindFoot.L', x=-50),
                  an.rot(p, 'FrontUpper.R', z=-20), an.rot(p, 'HindUpper.R', z=20)])
    mk(lambda p: [an.rot(p, 'Neck1', x=35), an.rot(p, 'Neck2', x=25), an.rot(p, 'Head', x=20)])                   # head down
    mk(lambda p: [an.rot(p, 'Neck1', x=-20), an.rot(p, 'Neck2', x=-20), an.rot(p, 'Head', x=-25), an.rot(p, 'Jaw', x=20)])
    mk(lambda p: [an.rot(p, 'Neck1', z=25), an.rot(p, 'Neck2', z=25), an.rot(p, 'Head', z=25)])
    mk(lambda p: [an.ear(p, up=30, back=-30), an.rot(p, 'Tail1', z=30), an.rot(p, 'Tail2', z=-35), an.rot(p, 'Tail3', z=40)])
    mk(lambda p: [an.rot(p, 'Spine1', z=10), an.rot(p, 'Spine2', z=-10), an.rot(p, 'Pelvis', z=-6)])           # undulation 10 deg
    mk(lambda p: [an.rot(p, 'Spine1', x=10), an.rot(p, 'Spine2', x=-10), an.rot(p, 'Tail1', x=-60), an.rot(p, 'Tail2', z=40)])
    return P


# ---------------- clips ----------------
def anim(B):
    sk = B['sk']; SP = B['SP']
    clips = ccl.build_clips(sk, SP)
    acts = {}
    for c, _, _ in SP['clips']:
        C = clips[c]
        acts[c] = an.write_action(B['rig'], f"{SP['species']}_{c}", C['frames'], C['loop'], C['bones'])
    ex = clips['Walk']['extra']
    print('WALK step', round(ex['step'], 3), 'drops', ex['drops'])
    rep = an.metrics(B['sc'], B['rig'], B['tmp'], {c: clips[c] for c, _, _ in SP['clips']}, acts, SP['limits'])
    sc = B['sc']; rig = B['rig']
    # Idle tail: lateral travel of the tail tip; Lie_Idle: lowest vertex of body / each leg / tail (resting, not floating)
    an.assign(rig, acts['Idle']); xs = []
    for f in range(int(acts['Idle'].frame_end) + 1):
        sc.frame_set(f); xs.append(rig.pose.bones['Tail3'].tail.x)
    rep['Idle']['tail_tip_lateral_m'] = [round(min(xs), 3), round(max(xs), 3)]
    an.assign(rig, acts['Lie_Idle']); dg = bpy.context.evaluated_depsgraph_get(); groups = {}
    sc.frame_set(0); dg = bpy.context.evaluated_depsgraph_get()
    for nm, o in B['obs'].items():
        me = o.evaluated_get(dg).to_mesh(); z = min((o.matrix_world @ v.co).z for v in me.vertices); o.evaluated_get(dg).to_mesh_clear()
        k = ('body' if nm in ('Pelvis', 'Spine1', 'Spine2') else 'tail' if nm.startswith('Tail') else
             nm.split('Upper')[0].split('Lower')[0].split('Foot')[0] + nm[-2:] if ('Front' in nm or 'Hind' in nm) else None)
        if k: groups[k] = min(groups.get(k, 9.0), z)
    rep['Lie_Idle']['rest_lowest_z_m'] = {k: round(v, 4) for k, v in sorted(groups.items())}
    rep['Lie_Idle']['pose'] = clips['Lie_Idle']['extra'].get('lie')
    print('IDLE tail tip x', rep['Idle']['tail_tip_lateral_m'], '| LIE lowest z per group', rep['Lie_Idle']['rest_lowest_z_m'])
    an.assign(rig, None); sc.frame_set(0)
    return clips, acts, rep


def clip_strips(B, clips, acts, only=None):
    sc = B['sc']; rig = B['rig']
    for c, _, _ in B['SP']['clips']:
        if only and c not in only: continue
        act = acts[c]; N = int(act.frame_end)
        fr = [round(i * N / 8) for i in range(8)]
        view = {'Idle': (-0.35, 1.0, 0.6), 'Walk': (1.0, -0.05, 0.12), 'Lie_Idle': (1.0, -0.6, 0.12)}[c]
        an.assign(rig, act)
        setters = [(lambda f=f: (sc.frame_set(f), bpy.context.view_layer.update())) for f in fr]
        strip(B, setters, os.path.join(CHECK, f'Cat_strip_{c}.png'), view)
        print('strip', c, 'frames', fr)
    an.assign(rig, None); sc.frame_set(0)


# ---------------- export (copies of the Dog steps) ----------------
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
        if c in SP['gait']: e['speed_mps'] = SP['gait'][c]['speed']
        d['clips'][c] = e
    json.dump(d, open(path, 'w'), indent=1); print('events', path)


if __name__ == '__main__':
    ID, CMD = args()
    print('=== PET-02 Cat rig', CMD)
    if CMD == 'bend':
        B = rig_model(os.path.join(CHECK, 'tex')); poses = bend_poses(B['sk'])
        setters = [(lambda p=p: apply_pose(B['rig'], p)) for p in poses]
        strip(B, setters, os.path.join(CHECK, 'Cat_bend_side.png'), (1.0, -0.15, 0.2))
        strip(B, setters, os.path.join(CHECK, 'Cat_bend_back.png'), (-0.6, 1.0, 0.6))
    elif CMD == 'lieviews':
        B = rig_model(os.path.join(CHECK, 'tex')); clips, acts, rep = anim(B)
        an.assign(B['rig'], acts['Lie_Idle']); B['sc'].frame_set(0)
        sc = B['sc']; rn.setup_workbench(sc, 400, 300); g = rn.ground(sc); cam = rn.camera(sc); obs = list(B['obs'].values())
        pts = rn.mesh_points(obs); tiles = []
        for v in ((1.0, -0.6, 0.12), (1, 0, 0.02), (0.3, 0.2, 1.0), (-0.7, 1.0, 0.3)):
            rn.fit(sc, cam, pts, v, (0.9, 0.9)); pth = rn.render_to(sc, os.path.join(CHECK, 'tile.png')); tiles.append(rn.load_px(pth))
        rn.compose(tiles, 2, os.path.join(CHECK, 'Cat_lie_views.png'))
    elif CMD == 'anim':
        B = rig_model(os.path.join(CHECK, 'tex')); clips, acts, rep = anim(B)
        json.dump(rep, open(os.path.join(WORK, 'metrics_report.json'), 'w'), indent=1, default=str)
        only = sys.argv[sys.argv.index('--') + 3:] or None
        clip_strips(B, clips, acts, only)
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
