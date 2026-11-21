# rig_hedgehog.py - SML-04 Hedgehog: new small skeleton "QS" (22 bones) designed from the mesh parts of build_hedgehog.py:
#   Root > Pelvis > Spine1 > Spine2 > Neck1 > Neck2 > Head > Nose (snout), Ear.L/R (Head);
#   Front/Hind Upper > Lower > Foot .L/.R (Upper = hidden hip connector inside the shell; parent Spine2 / Pelvis).
# Q names are kept (so the shared animal_anim helpers, leg IK and metrics work); no Jaw, no Tail, no Horns.
# Binding (rigid parts, weight 1.0 unless noted): shell Pelvis/Spine1/Spine2 = path blend Pelvis|Spine1|Spine2 (50/50 at the
# joints, the shell arches smoothly in Curl_Up); Spikes_Pelvis/Spine1/Spine2 -> their bone (rigid shards); Spikes_Neck:
# the head-top spike -> Head, the 4 shell spikes -> Spine2 (they sit on the shell front: following Neck1 would lift them off
# the shell when the head tucks); Head/Jaw/Eye.L/R -> Head; Nose -> Nose; Ear -> Ear; Neck1/Neck2 hidden connectors -> own
# bone; legs: Lower part top ring -> Upper, bottom ring (inside the paw) -> Foot, knee bone joint at z 0.028; Foot -> Foot.
# Clips Hedgehog_Idle (sniffs) / Hedgehog_Walk / Hedgehog_Curl_Up (curl into a ball, hold, uncurl), metrics, FBX + .blend.
# Pattern: ../Fox/rig_fox.py (itself ../Cat/rig_cat.py + ../Dog). The mesh comes unchanged from build_hedgehog.build().
#   PYTHONUTF8=1 blender --background --factory-startup --python rig_hedgehog.py -- SML-04 bend|anim|curlviews|export
import sys, os, math, json, importlib
REPO = r'D:\GitProjects\Assets_Farm'
WORK = REPO + r'\.work\models\Farm_Animals\Hedgehog'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common', WORK):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import animal_render as rn, animal_rig as ar, animal_species as asp, animal_anim as an, animal_export as ax
import build_hedgehog as bh
import hedgehog_clips as hcl
for m in (bh, hcl): importlib.reload(m)

ASSET = bh.ASSET; ART = bh.ART
CHECK = bh.CHECK
os.makedirs(CHECK, exist_ok=True)

ar.SKELETONS['QS'] = [('Root', None), ('Pelvis', 'Root'), ('Spine1', 'Pelvis'), ('Spine2', 'Spine1'),
                      ('Neck1', 'Spine2'), ('Neck2', 'Neck1'), ('Head', 'Neck2'), ('Nose', 'Head'),
                      ('Ear.L', 'Head'), ('Ear.R', 'Head'),
                      ('FrontUpper.L', 'Spine2'), ('FrontLower.L', 'FrontUpper.L'), ('FrontFoot.L', 'FrontLower.L'),
                      ('FrontUpper.R', 'Spine2'), ('FrontLower.R', 'FrontUpper.R'), ('FrontFoot.R', 'FrontLower.R'),
                      ('HindUpper.L', 'Pelvis'), ('HindLower.L', 'HindUpper.L'), ('HindFoot.L', 'HindLower.L'),
                      ('HindUpper.R', 'Pelvis'), ('HindLower.R', 'HindUpper.R'), ('HindFoot.R', 'HindLower.R')]
BIND = {'Eye.L': 'Head', 'Eye.R': 'Head', 'Jaw': 'Head', 'Spikes_Pelvis': 'Pelvis', 'Spikes_Spine1': 'Spine1',
        'Spikes_Spine2': 'Spine2'}
# curl: the back arches (pelvis tips the rump down, spine segments bend), the head tucks far down under the shell front
LIMITS = dict(asp.Q_LIMITS, Pelvis=dict(x=(-130, 25), y=(-15, 15), z=(-15, 15)), Spine1=dict(x=(-15, 130), z=(-15, 15)),
              Spine2=dict(x=(-15, 130), z=(-15, 15)), Head=dict(x=(-50, 80), z=(-60, 60)), Nose=dict(x=(-20, 20), z=(-20, 20)),
              FrontFoot=dict(x=(-70, 120)), FrontUpper=dict(x=(-75, 75), z=(-25, 25)), HindUpper=dict(x=(-75, 75), z=(-25, 25)))
KNEE_TOL = 0.004
KNEE_Z = 0.028
SHELL = ('Pelvis', 'Spine1', 'Spine2')
HIDE = ('Head', 'Jaw', 'Eye.L', 'Eye.R', 'Nose', 'Ear.L', 'Ear.R', 'FrontLower.L', 'FrontFoot.L', 'FrontLower.R', 'FrontFoot.R',
        'HindLower.L', 'HindFoot.L', 'HindLower.R', 'HindFoot.R')


def bone_of(part):
    return BIND.get(part, part)


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['SML-04', 'bend'])[:2]


def far_vertex(o, piv):
    M = o.matrix_world
    return max((M @ v.co for v in o.data.vertices), key=lambda p: (p - piv).length)


def species(obs):
    """hedgehog table in the animal_species format; bone heads = part pivots (joints), tails = next joint / far vertex"""
    P = {k: o.matrix_world.translation.copy() for k, o in obs.items()}
    t = lambda v: tuple(round(c, 5) for c in v)
    nose_tip = min((obs['Nose'].matrix_world @ v.co for v in obs['Nose'].data.vertices), key=lambda p: p.y)
    B = {'Root': ((0, 0, 0), (0, -0.05, 0)),
         'Pelvis': (t(P['Pelvis']), t(P['Spine1'])), 'Spine1': (t(P['Spine1']), t(P['Spine2'])),
         'Spine2': (t(P['Spine2']), t(P['Neck1'])), 'Neck1': (t(P['Neck1']), t(P['Neck2'])),
         'Neck2': (t(P['Neck2']), t(P['Head'])), 'Head': (t(P['Head']), t(P['Nose'])),
         'Nose': (t(P['Nose']), t(Vector((0.0, nose_tip.y, P['Nose'].z)))),
         'Ear.L': (t(P['Ear.L']), t(far_vertex(obs['Ear.L'], P['Ear.L'])))}
    for kind in ('Front', 'Hind'):
        u, f = P[kind + 'Upper.L'], P[kind + 'Foot.L']
        l = Vector((u.x, u.y, KNEE_Z))       # knee bone joint mid-way down the visible leg (the part pivot 0.040 would
        #                                       leave a 12 mm upper bone: IK angles blow up for a 3 mm leg shortening)
        B[kind + 'Upper.L'] = (t(u), t(l)); B[kind + 'Lower.L'] = (t(l), t(f)); B[kind + 'Foot.L'] = (t(f), t(Vector((f.x, f.y, 0.0))))
    return dict(id='SML-04', species='Hedgehog', asset=ASSET, tag=bh.TAG, skeleton='QS', bones=B,
                size=dict(length=0.220, withers=0.153),
                gait={'Walk': dict(T=0.5, duty=0.62, speed=0.11, lift=0.009, flick=(0, 0), crouch=0.002, roll=2.0, bob=0.0008,
                                   reach=0.99, narrow=1.0, sway=2.5, nose=6.0,
                                   phases={'HindL': 0.0, 'FrontL': 0.25, 'HindR': 0.5, 'FrontR': 0.75})},
                idle=dict(sniffs=3, nose=(9.0, 6.0), head_up=7.0, turn=10.0, ear=14.0),
                curl=dict(pelvis=-115.0, spine=(115.0, 115.0),   # rework 2026-11-21: shell closes into a loop (round ball)
                          lead_head=(0.0, 0.0), to_centre=dict(head=(0.0, -0.005, 0.005), front=(0.015, -0.012, -0.01), hind=(0.015, 0.012, -0.01)),
                          shrink={'Head': (0.55, (-0.01, 0.02)), 'FrontUpper.L': (0.5, (-0.02, 0.03)), 'FrontUpper.R': (0.5, (-0.02, 0.03)),
                                  'HindUpper.L': (0.5, (-0.02, 0.03)), 'HindUpper.R': (0.5, (-0.02, 0.03))},
                          neck=(15.0, 10.0), head=(10.0, 0.0), head_back=0.052, head_down=-0.008,
                          leg_front=(0.0, 0.018, 0.042), leg_hind=(0.0, -0.012, 0.040), leg_fold=30.0, ear=(-60.0, 0.0), ear_in=0.016, ear_down=0.010,
                          t_in=(0.04, 0.30), t_out=(0.66, 0.94)),
                clips=[('Idle', 3.0, True), ('Walk', 0.5, True), ('Curl_Up', 3.0, True)], limits=LIMITS, poses={},
                loc_bones=['Pelvis', 'Head', 'Ear.L', 'Ear.R', 'FrontUpper.L', 'FrontUpper.R', 'HindUpper.L', 'HindUpper.R'])


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


def neck_islands(ob):
    """Spikes_Neck: connected vertex islands; the island centred on x = 0 is the head-top spike -> Head, others -> Spine2"""
    me = ob.data; par = list(range(len(me.vertices)))

    def find(i):
        while par[i] != i: par[i] = par[par[i]]; i = par[i]
        return i
    for e in me.edges:
        a, b = find(e.vertices[0]), find(e.vertices[1])
        if a != b: par[a] = b
    isl = {}
    for v in me.vertices: isl.setdefault(find(v.index), []).append(v.index)
    out = {}
    for vs in isl.values():
        cx = sum((ob.matrix_world @ me.vertices[i].co).x for i in vs) / len(vs)
        for i in vs: out[i] = 'Head' if abs(cx) < 0.004 else 'Spine2'
    return out


def part_weights(nm, co, P, spine_pts, vi=None, isl=None):
    if nm in SHELL:
        return path_weights(co, spine_pts, list(SHELL))
    if nm == 'Spikes_Neck':
        return {isl[vi]: 1.0}
    for s in ('.L', '.R'):
        for k in ('Front', 'Hind'):
            up, lo, ft = k + 'Upper' + s, k + 'Lower' + s, k + 'Foot' + s
            if nm != lo: continue
            zk = KNEE_Z
            if co.z < P[ft].z: return {ft: 1.0}          # shin bottom ring sits inside the paw: moves with the paw
            if co.z > zk + KNEE_TOL: return {up: 1.0}
            if co.z > zk - KNEE_TOL: return {up: 0.5, lo: 0.5}
            return {lo: 1.0}
    return {bone_of(nm): 1.0}


def joined(obs, rig, P, spine_pts, isl):
    """TMP world-space copy of all parts with the same weights (for animal_anim.Skel and the metrics); never exported"""
    names = [b.name for b in rig.data.bones]; gi = {n: i for i, n in enumerate(names)}
    me = bpy.data.meshes.new('TMP_HedgehogAll'); ob = bpy.data.objects.new('TMP_HedgehogAll', me)
    bpy.context.scene.collection.objects.link(ob)
    for n in names: ob.vertex_groups.new(name=n)
    bm = bmesh.new(); dl = bm.verts.layers.deform.verify(); pl = bm.faces.layers.int.new('part')
    order = list(obs)
    for nm, o in obs.items():
        M = o.matrix_world; vm = {}
        for v in o.data.vertices:
            co = M @ v.co; nv = bm.verts.new(co)
            for bn, w in part_weights(nm, co, P, spine_pts, v.index, isl).items(): nv[dl][gi[bn]] = w
            vm[v.index] = nv
        for p in o.data.polygons:
            f = bm.faces.new([vm[i] for i in p.vertices]); f[pl] = order.index(nm)
    bm.to_mesh(me); bm.free()
    ob.modifiers.new('Armature', 'ARMATURE').object = rig; ob.hide_render = True
    ob['parts'] = order
    return ob


def rig_model(tex_dir):
    B = bh.build(tex_dir)
    sc = B['sc']; sc.render.fps = 30; sc.render.fps_base = 1.0
    SP = species(B['obs'])
    P = {k: o.matrix_world.translation.copy() for k, o in B['obs'].items()}
    bn = SP['bones']
    spine_pts = [Vector(bn['Pelvis'][0]), Vector(bn['Spine1'][0]), Vector(bn['Spine2'][0]), Vector(bn['Spine2'][1])]
    isl = neck_islands(B['obs']['Spikes_Neck'])
    print('SPIKES_NECK islands -> Head', sum(1 for b in isl.values() if b == 'Head'), 'verts, -> Spine2',
          sum(1 for b in isl.values() if b == 'Spine2'), 'verts')
    rig = ar.build_armature(SP, B['coll'], 'QS')
    rchk = ar.check_rig(rig, 'QS')
    nblend = 0
    for nm, ob in B['obs'].items():
        mw = ob.matrix_world.copy(); ob.parent = rig; ob.matrix_parent_inverse.identity(); ob.matrix_world = mw
        for g in list(ob.vertex_groups): ob.vertex_groups.remove(g)
        groups = {}
        for v in ob.data.vertices:
            wd = part_weights(nm, mw @ v.co, P, spine_pts, v.index, isl)
            if len(wd) > 1: nblend += 1
            for b_, w in wd.items():
                if b_ not in groups: groups[b_] = ob.vertex_groups.new(name=b_)
                groups[b_].add([v.index], w, 'REPLACE')
        ob.modifiers.new('Armature', 'ARMATURE').object = rig
    bpy.data.objects.remove(B['root'], do_unlink=True)
    bpy.context.view_layer.update()
    tmp = joined(B['obs'], rig, P, spine_pts, isl)
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
    mk(lambda p: [an.rot(p, 'FrontUpper.L', x=-35), an.rot(p, 'FrontUpper.R', x=30), an.rot(p, 'HindUpper.L', x=35), an.rot(p, 'HindUpper.R', x=-30)])
    mk(lambda p: [an.rot(p, 'FrontLower.L', x=60), an.rot(p, 'FrontFoot.L', x=40), an.rot(p, 'HindLower.L', x=-60), an.rot(p, 'HindFoot.L', x=-40),
                  an.rot(p, 'FrontUpper.R', z=-20), an.rot(p, 'HindUpper.R', z=20)])
    mk(lambda p: [an.rot(p, 'Neck1', x=30), an.rot(p, 'Neck2', x=15), an.rot(p, 'Head', x=20)])                   # head down
    mk(lambda p: [an.rot(p, 'Neck1', x=-15), an.rot(p, 'Head', x=-20), an.rot(p, 'Nose', x=-15)])               # head up, sniff
    mk(lambda p: [an.rot(p, 'Neck1', z=15), an.rot(p, 'Neck2', z=10), an.rot(p, 'Head', z=15), an.rot(p, 'Nose', z=15)])
    mk(lambda p: [an.ear(p, up=30, back=-30), an.rot(p, 'Spine1', z=10), an.rot(p, 'Spine2', z=-10)])
    mk(lambda p: [an.rot(p, 'Pelvis', x=-25), an.rot(p, 'Spine1', x=20), an.rot(p, 'Spine2', x=25)])           # arch (curl)
    mk(lambda p: [an.body(sk, p, (0, 0, 0), pitch=0, roll=10), an.rot(p, 'Spine1', x=-10), an.rot(p, 'Spine2', x=-10)])
    return P


# ---------------- clips ----------------
def hidden_report(B, frame_poses):
    """parts that must hide in the ball (head, face, ears, legs). outside = vertices outside the posed shell (nearest-surface
    test) and above 3 mm; visible = vertices from which a ray in any of 26 directions escapes without hitting the shell, the
    spikes or the ground (z = 0), i.e. a camera there would see them"""
    dirs = [Vector((x, y, z)).normalized() for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1) if (x, y, z) != (0, 0, 0)]
    occl = [n for n in B['obs'] if n not in HIDE]
    out = {}
    for lab, st in frame_poses:
        st(); dg = bpy.context.evaluated_depsgraph_get()

        def bvh_of(names):
            verts = []; polys = []
            for nm in names:
                o = B['obs'][nm]; me = o.evaluated_get(dg).to_mesh(); base = len(verts)
                verts += [o.matrix_world @ v.co for v in me.vertices]; polys += [[base + i for i in p.vertices] for p in me.polygons]
                o.evaluated_get(dg).to_mesh_clear()
            return BVHTree.FromPolygons(verts, polys)
        shell = bvh_of(SHELL); occ = bvh_of(occl)
        n_out = 0; n_vis = 0; n_all = 0; worst = 0.0; who = {}; vis = {}
        for nm in HIDE:
            o = B['obs'][nm]; me = o.evaluated_get(dg).to_mesh()
            for v in me.vertices:
                p = o.matrix_world @ v.co; n_all += 1
                loc, nrm, _, _ = shell.find_nearest(p)
                d = (p - loc).dot(nrm)
                if d > 0.0005 and p.z > 0.003:
                    n_out += 1; worst = max(worst, d); who[nm] = who.get(nm, 0) + 1
                seen = False
                for dv in dirs:
                    if dv.z < -0.01: continue                        # rays going down end on the ground
                    if occ.ray_cast(p + dv * 1e-4, dv)[0] is None: seen = True; break
                if seen: n_vis += 1; vis[nm] = vis.get(nm, 0) + 1
            o.evaluated_get(dg).to_mesh_clear()
        out[lab] = dict(outside_shell=n_out, visible=n_vis, of=n_all, worst_out_m=round(worst, 4), outside_parts=who, visible_parts=vis)
    return out


def anim(B):
    sk = B['sk']; SP = B['SP']
    clips = hcl.build_clips(sk, SP)
    acts = {}
    shr = list(clips['Curl_Up'].get('scale', {}))
    for c, _, _ in SP['clips']:
        C = clips[c]
        if not C.get('scale') and shr: C['scale'] = {b: [1.0] * len(C['frames']) for b in shr}   # same channels in every take
        acts[c] = hcl.write_action(B['rig'], f"{SP['species']}_{c}", C['frames'], C['loop'], SP['loc_bones'], C.get('scale'))
    ex = clips['Walk']['extra']
    print('WALK step', round(ex['step'], 3), 'drops', ex['drops'])
    rep = an.metrics(B['sc'], B['rig'], B['tmp'], {c: clips[c] for c, _, _ in SP['clips']}, acts, SP['limits'])
    sc = B['sc']; rig = B['rig']
    for c, _, _ in SP['clips']:
        rep[c]['loop_closure_loc_m'] = hcl.loc_closure(acts[c])
    C = clips['Curl_Up']; ext = C['extra']
    an.assign(rig, acts['Curl_Up'])
    fh = ext['hold_frames']
    hr = hidden_report(B, [(f'f{f}', (lambda f=f: (sc.frame_set(f), bpy.context.view_layer.update()))) for f in fh])
    rep['Curl_Up']['ball'] = dict(ext['ball'], hidden_check=hr)
    print('CURL hidden check (hold frames)', hr)
    print('LOOP loc closure', {c: rep[c]['loop_closure_loc_m'] for c, _, _ in SP['clips']})
    an.assign(rig, None); sc.frame_set(0)
    return clips, acts, rep


def clip_strips(B, clips, acts, only=None):
    sc = B['sc']; rig = B['rig']
    for c, _, _ in B['SP']['clips']:
        if only and c not in only: continue
        act = acts[c]; N = int(act.frame_end)
        fr = [round(i * N / 8) for i in range(8)]
        view = {'Idle': (0.85, -1.0, 0.25), 'Walk': (1.0, -0.05, 0.12), 'Curl_Up': (1.0, -0.55, 0.3)}[c]
        an.assign(rig, act)
        setters = [(lambda f=f: (sc.frame_set(f), bpy.context.view_layer.update())) for f in fr]
        strip(B, setters, os.path.join(CHECK, f'Hedgehog_strip_{c}.png'), view)
        print('strip', c, 'frames', fr)
    an.assign(rig, None); sc.frame_set(0)


# ---------------- export (copies of the Dog steps) ----------------
def export_nla(rig, parts, actions, fbx):
    ad = rig.animation_data or rig.animation_data_create(); sc = bpy.context.scene
    assert sc.render.fps == 30 and sc.render.fps_base == 1.0
    for pb in rig.pose.bones: pb.location = (0, 0, 0); pb.rotation_euler = (0, 0, 0); pb.scale = (1, 1, 1)
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
    print('=== SML-04 Hedgehog rig', CMD)
    if CMD == 'bend':
        B = rig_model(os.path.join(CHECK, 'tex')); poses = bend_poses(B['sk'])
        setters = [(lambda p=p: apply_pose(B['rig'], p)) for p in poses]
        strip(B, setters, os.path.join(CHECK, 'Hedgehog_bend_side.png'), (1.0, -0.15, 0.2))
        strip(B, setters, os.path.join(CHECK, 'Hedgehog_bend_back.png'), (-0.6, 1.0, 0.6))
    elif CMD == 'curlviews':      # the held ball from 6 sides (holes / parts poking out)
        B = rig_model(os.path.join(CHECK, 'tex')); clips, acts, rep = anim(B)
        an.assign(B['rig'], acts['Curl_Up']); B['sc'].frame_set(clips['Curl_Up']['extra']['hold_frames'][1])
        sc = B['sc']; rn.setup_workbench(sc, 400, 300); g = rn.ground(sc); cam = rn.camera(sc); obs = list(B['obs'].values())
        pts = rn.mesh_points(obs); tiles = []
        for v in ((1.0, -0.55, 0.17), (0.0, -1.0, 0.05), (1.0, 0.0, 0.05), (-0.6, 1.0, 0.3), (0.01, 0.0, 1.0), (0.7, -0.7, -0.08)):
            rn.fit(sc, cam, pts, v, (0.9, 0.9)); pth = rn.render_to(sc, os.path.join(CHECK, 'tile.png')); tiles.append(rn.load_px(pth))
        rn.compose(tiles, 3, os.path.join(CHECK, 'Hedgehog_curl_views.png'))
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
