# rig_puppy.py - PET-03 Puppy: copy of ../Dog/rig_dog.py (read-only there): skeleton QD = Q without Horn.L/R + Ruff
# (child of Spine2) = 26 bones, binding of the final mesh parts (each part = its bone, weight 1.0; Eye.L/R and Nose ->
# Head), two-bone blends: knee/hock line, neck path Spine2|Neck1|Neck2|Head, tail path Tail1|Tail2|Tail3, Ruff (chest
# bib) fading from its own bone to Neck1 under the cheeks. Bend test, clips Puppy_Idle / Puppy_Trot / Puppy_Play_Bow
# (puppy_clips.py), metrics, FBX + re-import check + events json + .blend; meshcheck vs the mesh-only FBX backup.
#   PYTHONUTF8=1 blender --background --factory-startup --python rig_puppy.py -- PET-03 bend|anim|export|meshcheck
# The mesh comes unchanged from build_puppy.build() (geometry, part names and pivots untouched).
import sys, os, math, json, importlib
REPO = r'C:\Users\Sergv\orca\workspaces\VFX\master-3'
WORK = REPO + r'\.work\models\Farm_Animals\Puppy'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common', WORK):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
import numpy as np
from mathutils import Vector
import pack_common as pc
import animal_render as rn, animal_rig as ar, animal_species as asp, animal_anim as an, animal_export as ax
import build_puppy as bd
import puppy_clips as dcl
for m in (bd, dcl): importlib.reload(m)

ASSET = bd.ASSET; ART = bd.ART
CHECK = bd.CHECK
os.makedirs(CHECK, exist_ok=True)

ar.SKELETONS['QD'] = [b for b in ar.Q_BONES if not b[0].startswith('Horn')] + [('Ruff', 'Spine2')]
BIND = {'Eye.L': 'Head', 'Eye.R': 'Head', 'Nose': 'Head'}
LIMITS = dict(asp.Q_LIMITS, Ruff=dict(x=(-15, 50), y=(-10, 10), z=(-15, 15)),   # HindLower set from the rest bend in anim()
              FrontUpper=dict(x=(-100, 60), z=(-25, 25)))   # Play_Bow: shoulder reaches forward (forearms along the ground)


THIGH_TOP = -0.005


def bone_of(part):
    return BIND.get(part, part)


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['PET-03', 'bend'])[:2]


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
    return dict(id='PET-03', species='Puppy', asset=ASSET, tag=bd.TAG, skeleton='QD', bones=B,
                size=dict(length=0.645, withers=0.298),
                gait={'Trot': dict(T=0.5, duty=0.45, speed=0.55, lift=0.040, flick=(30, 24), crouch=0.004, roll=1.5, bob=0.006,
                                   phases={'HindL': 0.0, 'FrontR': 0.0, 'HindR': 0.5, 'FrontL': 0.5},
                                   ear=7.0, tail=(6.0, 9.0, 12.0), tail_bounce=5.0, ruff=4.0)},
                idle=dict(wag=(18.0, 24.0, 30.0), lag=0.10, hip=2.5, ear=14.0),
                bow=dict(paw_fwd=0.060, chest_clear=0.010, hop=0.025, head_up=1.0, wag=(20.0, 26.0, 32.0), wags=8, bounce_share=0.18,
                         times=(0.10, 0.24, 0.66, 0.80), rises=(0.0, -0.005, -0.010),
                         tail_up=18.0, bounce=0.008, tilt=10.0),
                clips=[('Idle', 3.0, True), ('Trot', 0.5, True), ('Play_Bow', 2.5, True)], limits=LIMITS, poses={})


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
                if co.z > P[up].z + THIGH_TOP:     # thigh/shoulder top inside the body follows the body (Cat rule)
                    return {('Spine2' if k == 'Front' else 'Pelvis'): 0.7, up: 0.3}
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
    me = bpy.data.meshes.new('TMP_PuppyAll'); ob = bpy.data.objects.new('TMP_PuppyAll', me)
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
def anim(B):
    sk = B['sk']; SP = B['SP']
    clips = dcl.build_clips(sk, SP)
    de = math.degrees(dcl._IK['HindL'][0])            # hock rest flex: straight leg = HindLower x of +|rest|
    SP['limits']['HindLower'] = dict(x=(-170, max(3.0, abs(de) + 3.0)))
    acts = {}
    for c, _, _ in SP['clips']:
        C = clips[c]
        acts[c] = an.write_action(B['rig'], f"{SP['species']}_{c}", C['frames'], C['loop'], C['bones'])
    ex = clips['Trot']['extra']
    print('TROT step', round(ex['step'], 3), 'drop front max/min', max(ex['drops']['Front']), min(ex['drops']['Front']),
          'hind', max(ex['drops']['Hind']), min(ex['drops']['Hind']))
    rep = an.metrics(B['sc'], B['rig'], B['tmp'], {c: clips[c] for c, _, _ in SP['clips']}, acts, SP['limits'])
    # tail wag amplitude (Blender evaluation): lateral travel of the tail tip over the Idle clip
    sc = B['sc']; rig = B['rig']; an.assign(rig, acts['Idle']); xs = []
    for f in range(int(acts['Idle'].frame_end) + 1):
        sc.frame_set(f); xs.append(rig.pose.bones['Tail3'].tail.x)
    an.assign(rig, None); sc.frame_set(0)
    rep['Idle']['tail_tip_lateral_m'] = [round(min(xs), 3), round(max(xs), 3)]
    rep['Idle']['wag_hz'] = round(dcl.WAGS / 3.0, 3)
    rep['Play_Bow']['bow'] = clips['Play_Bow']['extra'].get('bow')
    print('IDLE tail tip x min/max', round(min(xs), 3), round(max(xs), 3))
    return clips, acts, rep


def clip_strips(B, clips, acts):
    sc = B['sc']; rig = B['rig']
    for c, _, _ in B['SP']['clips']:
        act = acts[c]; N = int(act.frame_end)
        if c == 'Idle':     # 8 frames ~1/8 of a wag period apart (period 90/7 = 12.9 frames) + 1 seen from behind-above
            per = N / dcl.WAGS; fr = [round(i * per / 8 * 1.0) for i in range(8)]
            view = (-0.25, 1.0, 0.85)
        else:
            fr = [round(i * N / 8) for i in range(8)]
            view = (1.0, -0.05, 0.12) if c in ('Trot', 'Play_Bow') else (0.85, -0.75, 0.25)
        an.assign(rig, act)
        setters = [(lambda f=f: (sc.frame_set(f), bpy.context.view_layer.update())) for f in fr]
        strip(B, setters, os.path.join(CHECK, f'Puppy_strip_{c}.png'), view)
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
        if c in SP['gait']: e['speed_mps'] = SP['gait'][c]['speed']
        d['clips'][c] = e
    json.dump(d, open(path, 'w'), indent=1); print('events', path)


def meshcheck(B):
    """built (rest) mesh vs the ORIGINAL mesh-only FBX backup in TEMP/FarmAnimals_pets_bak: per part vertex sets"""
    fbx = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_pets_bak', ASSET + '.fbx')
    win = bpy.context.window; prev = win.scene; sc = bpy.data.scenes.new('TMP_MeshCheck'); win.scene = sc
    before = set(bpy.data.objects); bpy.ops.import_scene.fbx(filepath=fbx)
    new = [o for o in bpy.data.objects if o not in before]; im = {_base(o.name).replace(ASSET + '_', '', 1): o for o in new if o.type == 'MESH'}
    pts = lambda o: sorted(tuple(round(c, 4) for c in (o.matrix_world @ v.co)) for v in o.data.vertices)
    worst = 0.0; missing = []
    for nm, o in B['obs'].items():
        if nm not in im: missing.append(nm); continue
        A, Bv = pts(o), pts(im[nm])
        if len(A) != len(Bv): worst = float('inf'); continue
        worst = max(worst, max(max(abs(x - y) for x, y in zip(a, b)) for a, b in zip(A, Bv)))
    win.scene = prev
    for o in new: bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.scenes.remove(sc)
    print(f'MESHCHECK vs {fbx}: parts {len(B["obs"])} missing {missing} max vertex diff {worst:.5f} m')
    return worst, missing


if __name__ == '__main__':
    ID, CMD = args()
    print('=== PET-03 Puppy rig', CMD)
    if CMD == 'bend':
        B = rig_model(os.path.join(CHECK, 'tex')); poses = bend_poses(B['sk'])
        setters = [(lambda p=p: apply_pose(B['rig'], p)) for p in poses]
        strip(B, setters, os.path.join(CHECK, 'Puppy_bend_side.png'), (1.0, -0.15, 0.2))
        strip(B, setters, os.path.join(CHECK, 'Puppy_bend_back.png'), (-0.6, 1.0, 0.45))
    elif CMD == 'meshcheck':
        B = bd.build(os.path.join(CHECK, 'tex')); meshcheck(B)
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
