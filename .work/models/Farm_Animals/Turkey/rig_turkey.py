# rig_turkey.py - BRD-07 Turkey rig: copy of ../Rooster/rig_rooster.py (skeleton B, 20 bones, read-only) + 3 bones the mesh
# dictates: Wattle (child of Head: the long dewlap, draped along the neck in the clips; the crown caruncles of the same part
# stay on Head), TailFan_Side.L/.R (children of TailFan2: the two outer fan plates per side fold behind/in front of the
# centre plates and spread for Display) = skeleton BT, 23 bones. Clips Turkey_Idle / Turkey_Walk / Turkey_Display.
#   PYTHONUTF8=1 blender --background --factory-startup --python rig_turkey.py -- BRD-07 bend|anim|export
# bend  : rig + extreme poses -> strips (TEMP)          anim  : rig + clips + metrics + clip strips (TEMP)
# export: anim + FBX (skinned parts + armature + 3 takes, NLA, bake_space_transform) + re-import check + events json + .blend
# Geometry, part names and pivots come unchanged from build_turkey.build(). Shared modules (_common) are used read-only;
# skeleton 'BT' is registered in animal_rig.SKELETONS at runtime in this process only.
import sys, os, math, json, importlib
REPO = r'C:\Users\Sergv\orca\workspaces\VFX\master-3'
WORK = REPO + r'\.work\models\Farm_Animals\Turkey'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common', WORK):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
import animal_render as rn, animal_rig as ar, animal_anim as an, animal_export as ax
import build_turkey as bm_
import turkey_clips as hc
for m in (bm_, hc): importlib.reload(m)

# ---------------- skeleton B (bird) template: bone, parent ----------------
B_BONES = [
    ('Root', None), ('Body', 'Root'), ('Neck1', 'Body'), ('Neck2', 'Neck1'), ('Head', 'Neck2'), ('Beak_Lower', 'Head'),
    ('WingUpper.L', 'Body'), ('WingLower.L', 'WingUpper.L'), ('WingTip.L', 'WingLower.L'),
    ('WingUpper.R', 'Body'), ('WingLower.R', 'WingUpper.R'), ('WingTip.R', 'WingLower.R'),
    ('TailFan1', 'Body'), ('TailFan2', 'TailFan1'),
    ('LegUpper.L', 'Body'), ('LegLower.L', 'LegUpper.L'), ('Foot.L', 'LegLower.L'),
    ('LegUpper.R', 'Body'), ('LegLower.R', 'LegUpper.R'), ('Foot.R', 'LegLower.R'),
    ('Wattle', 'Head'), ('TailFan_Side.L', 'TailFan2'), ('TailFan_Side.R', 'TailFan2'),
]
ar.SKELETONS['BT'] = B_BONES
B_LEGS = {'LegL': ('LegUpper.L', 'LegLower.L', 'Foot.L', True), 'LegR': ('LegUpper.R', 'LegLower.R', 'Foot.R', True)}
# bone heads = part pivots; tails = next joint in the chain; these chain ends get a tail offset (m) from their head:
CHAIN_TAIL = {'Neck1': 'Neck2', 'Neck2': 'Head', 'WingUpper.L': 'WingLower.L', 'WingLower.L': 'WingTip.L', 'TailFan1': 'TailFan2',
              'LegUpper.L': 'LegLower.L', 'LegLower.L': 'Foot.L'}
B_LIMITS = {  # local euler degrees (x = pitch for all sagittal bones; Neck y = twist, Head z = yaw, Head y = tilt)
    'Body': dict(x=(-45, 45), y=(-20, 20), z=(-25, 25)), 'Neck1': dict(x=(-60, 100), y=(-60, 60), z=(-30, 30)),
    'Neck2': dict(x=(-110, 75), y=(-60, 60), z=(-30, 30)), 'Head': dict(x=(-70, 90), y=(-40, 40), z=(-100, 100)),
    'Beak_Lower': dict(x=(-2, 35)), 'WingUpper': dict(x=(-30, 30), y=(-30, 30), z=(-90, 90)),
    'WingLower': dict(x=(-30, 30), y=(-60, 60), z=(-60, 60)), 'WingTip': dict(x=(-30, 30), y=(-60, 60), z=(-60, 60)),
    'TailFan1': dict(x=(-40, 60), z=(-40, 40)), 'TailFan2': dict(x=(-40, 60), z=(-40, 40)),
    'LegUpper': dict(x=(-100, 100), z=(-35, 35)), 'LegLower': dict(x=(-150, 150)), 'Foot': dict(x=(-120, 120)),
    'Wattle': dict(x=(-90, 90), y=(-45, 45), z=(-45, 45)), 'TailFan_Side': dict(x=(-90, 90), y=(-90, 90), z=(-90, 90)),
    'NECK_YAW_TOTAL': 200,
}
WATTLE_SPLIT_Z = 0.645      # Wattle part: crown caruncles above (-> Head), dewlap below (-> Wattle bone; separate loft)

# ---------------- species table (Turkey: 0.75 m to the fan top, big round body, upright red neck, long dewlap, big fan) ----
TURKEY = dict(
    id='BRD-07', species='Turkey', asset=bm_.ASSET, tag=bm_.TAG, skeleton='BT',
    bind={'Eye.L': 'Head', 'Eye.R': 'Head', 'BreastTuft': 'Body'},                     # Wattle: per vertex (see weights)
    ends={'Root': (0, -0.12, 0), 'Body': (0, -0.10, 0), 'Head': 'front', 'Beak_Lower': 'front', 'WingTip.L': 'far',
          'TailFan2': 'mid', 'TailFan_Side.L': 'far', 'Wattle': 'low'},               # Foot: straight down to the ground
    blend={'Neck1': [('Body', 'head', 0.020), ('Neck2', 'tail', 0.014)], 'Neck2': [('Neck1', 'head', 0.014), ('Head', 'tail', 0.012)]},
    gait={'Walk': dict(T=1.0, duty=0.6, speed=0.24, lift=0.050, toe_curl=22, crouch=0.005, pitch=0.0, roll=2.5, sway=0.006,
                       yaw=2.0, phases={'LegL': 0.0, 'LegR': 0.5}, hold=0.65, head_dz=0.006, head_nod=4.0, tail=3.0,
                       bob_max=0.050, bob_back=-0.45)},
    clips=[('Idle', 3.5, True), ('Walk', 1.0, True), ('Display', 4.0, True)],
    limits=B_LIMITS,
    poses=dict(stand_bend=0.008, wing_out=5.0, chest=-2.0,
               idle_look=[(0.00, (0, 0, 0)), (0.12, (26, 5, -3)), (0.24, (20, 9, 2)), (0.36, (0, 0, 0)), (0.47, (-24, -5, -3)),
                          (0.57, (-30, -9, 4)), (0.70, (-6, 0, 6)), (0.80, (14, 3, 0)), (0.90, (0, 0, 0))],
               # fan: relaxed (Idle/Walk) = fan pitched back + outer plates folded in; Display = fully spread (+ extra)
               fan_relax=(-35.0, 44.0), fan_display=(4.0, -6.0), drape=0.8,
               # display envelope (open start, open, close start, closed) as clip fractions; body, neck, wings, rattle
               disp_env=(0.05, 0.22, 0.76, 0.94), disp_chest=-9.0, disp_neck=(-16.0, 12.0), disp_head=10.0,
               disp_wing_out=7.0, disp_wing_droop=-14.0, disp_yaw=9.0, rattle=(0.42, 0.57), rattle_hz=14.0),
)
SP = TURKEY
ASSET = SP['asset']; ART = bm_.ART
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_turkey_rig')
os.makedirs(CHECK, exist_ok=True)


def bone_of(part):
    return SP['bind'].get(part, part)


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['BRD-07', 'bend'])[:2]


def species_bones(obs):
    """bone heads at the part pivots (.L given, .R mirrored by animal_rig.bone_table)"""
    P = {k: o.matrix_world.translation.copy() for k, o in obs.items()}
    t = lambda v: tuple(round(c, 4) for c in v)
    B = {'Root': ((0, 0, 0), t(Vector(SP['ends']['Root'])))}
    for n, par in B_BONES:
        if n == 'Root' or n.endswith('.R'): continue
        h = P[n]
        V = [obs[n].matrix_world @ v.co for v in obs[n].data.vertices] if n in obs else []
        if n == 'Wattle': V = [v for v in V if v.z < WATTLE_SPLIT_Z]
        if n in CHAIN_TAIL: tl = P[CHAIN_TAIL[n]]
        elif n.startswith('Foot'): tl = Vector((h.x, h.y, 0.0))
        elif SP['ends'].get(n) == 'front': tl = min(V, key=lambda v: v.y)                       # beak tip
        elif SP['ends'].get(n) == 'far': tl = max(V, key=lambda v: (v - h).length)
        elif SP['ends'].get(n) == 'mid':                                                         # centre plate tip (x = 0)
            m = max((v for v in V if abs(v.x) < 0.03), key=lambda v: (v - h).length); tl = Vector((0.0, m.y, m.z))
        elif SP['ends'].get(n) == 'low': tl = Vector((h.x, h.y, min(v.z for v in V)))           # dewlap: straight down
        else: tl = h + Vector(SP['ends'][n])
        B[n] = (t(h), t(tl))
    return B


def weights(obs, rig):
    """per part: {vertex index: {bone: w}} - rigid 1.0, linear blends at the joints listed in SP['blend']"""
    out = {}
    for nm, o in obs.items():
        b = bone_of(nm); bb = rig.data.bones[b]; h = bb.head_local; u = (bb.tail_local - bb.head_local); L = u.length; u = u / L
        M = o.matrix_world; W = []
        for v in o.data.vertices:
            t = (M @ v.co - h).dot(u); w = {b: 1.0}
            if nm == 'Wattle' and (M @ v.co).z >= WATTLE_SPLIT_Z: W.append({'Head': 1.0}); continue
            for other, end, wd in SP['blend'].get(nm, []):
                if end == 'head':
                    s = min(max(0.5 + 0.5 * t / wd, 0.0), 1.0); w = {k: x * s for k, x in w.items()}; w[other] = w.get(other, 0) + 1 - s
                else:
                    s = min(max(0.5 - 0.5 * (t - L) / wd, 0.0), 1.0); wb = w[b]; w[b] = wb * s; w[other] = w.get(other, 0) + wb * (1 - s)
            W.append({k: x for k, x in w.items() if x > 1e-4})
        out[nm] = W
    return out


def joined(obs, rig, W):
    """TMP world-space copy of all parts with the same weights (BirdSkel + metrics); never exported"""
    names = [b.name for b in rig.data.bones]; gi = {n: i for i, n in enumerate(names)}
    me = bpy.data.meshes.new('TMP_TurkeyAll'); ob = bpy.data.objects.new('TMP_TurkeyAll', me)
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
    B = bm_.build(tex_dir)
    sc = B['sc']; sc.render.fps = 30; sc.render.fps_base = 1.0
    sp = dict(SP); sp['bones'] = species_bones(B['obs'])
    rig = ar.build_armature(sp, B['coll'], 'BT')
    rchk = ar.check_rig(rig, 'BT')
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


# ---------------- strips ----------------
def apply_pose(rig, pose):
    for n, (l, r) in pose.items():
        pb = rig.pose.bones[n]; pb.location = l; pb.rotation_euler = r
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


def bend_poses(sk):
    P = []; rot = an.rot

    def mk(fn):
        p = an.new_pose(sk); fn(p); P.append(p)
    mk(lambda p: [rot(p, 'LegUpper.L', x=-70), rot(p, 'LegLower.L', x=110), rot(p, 'Foot.L', x=70),
                  rot(p, 'LegUpper.R', x=50, z=-30), rot(p, 'LegLower.R', x=-40)])
    mk(lambda p: [rot(p, 'Neck1', x=60), rot(p, 'Neck2', x=50), rot(p, 'Head', x=20), rot(p, 'Beak_Lower', x=30)])
    mk(lambda p: [rot(p, 'Neck1', x=-45), rot(p, 'Neck2', x=-40), rot(p, 'Head', x=-30)])
    mk(lambda p: [rot(p, 'Neck1', y=40, z=20), rot(p, 'Neck2', y=45, z=15), rot(p, 'Head', z=-80, y=30)])
    mk(lambda p: [rot(p, 'WingUpper.L', z=-60), rot(p, 'WingUpper.R', z=60), rot(p, 'WingLower.L', y=-20), rot(p, 'WingLower.R', y=20),
                  rot(p, 'TailFan1', x=40), rot(p, 'TailFan2', x=25)])
    mk(lambda p: [rot(p, 'WingUpper.L', z=-90), rot(p, 'WingUpper.R', z=90), rot(p, 'WingTip.L', z=30), rot(p, 'WingTip.R', z=-30),
                  rot(p, 'TailFan1', x=-30, z=35), rot(p, 'TailFan2', z=30)])
    mk(lambda p: [hc.body(sk, p, (0, 0, -0.03), pitch=20, roll=12), hc.settle(sk, p), rot(p, 'Wattle', x=40, z=25)])
    mk(lambda p: [hc.body(sk, p, (0, 0, 0), pitch=-15, yaw=20), hc.settle(sk, p), hc.fan(sk, p, -50, 45)])
    return P


# ---------------- clips ----------------
def anim(B):
    sk = B['sk']; sp = B['SP']
    clips = hc.build_clips(sk, sp)
    acts = {c: hc.write_action(B['rig'], f"{sp['species']}_{c}", clips[c]['frames'], clips[c]['loop'], sk.mover) for c, _, _ in sp['clips']}
    ex = clips['Walk']['extra']
    print('WALK step', round(ex['step'], 3), 'head travel', round(ex['head_travel'], 3), 'body drop min/max', min(ex['drop']), max(ex['drop']))
    print('DISPLAY events', clips['Display']['events'], clips['Display']['extra'])
    rep = hc.metrics(B['sc'], B['rig'], B['tmp'], sk, {c: clips[c] for c, _, _ in sp['clips']}, acts, sp['limits'])
    return clips, acts, rep


def clip_strips(B, clips, acts):
    sc = B['sc']; rig = B['rig']
    for c, _, _ in B['SP']['clips']:
        act = acts[c]; N = int(act.frame_end)
        fr = [round(i * N / 8) for i in range(8)]
        an.assign(rig, act)
        setters = [(lambda f=f: (sc.frame_set(f), bpy.context.view_layer.update())) for f in fr]
        view = (1.0, -0.02, 0.10) if c == 'Walk' else (0.6, -1.0, 0.35)
        strip(B, setters, os.path.join(CHECK, f'Turkey_strip_{c}.png'), view)
    an.assign(rig, None); sc.frame_set(0)


# ---------------- export (copies of the Sheep/Cow steps for a multi-part skinned mesh) ----------------
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


def events_json(sp, clips, path):
    d = dict(species=sp['species'], asset=ASSET, fps=an.FPS, note='Unity AnimationEvents to add on import (FBX does not carry them)',
             clips={})
    for c, T, loop in sp['clips']:
        C = clips[c]; N = len(C['frames']) - 1
        e = dict(take=f"{sp['species']}_{c}", seconds=round(N / an.FPS, 3), last_frame=N, loop=loop,
                 events=[dict(name=n, frame=f, time=round(f / an.FPS, 4), stringParameter=p) for f, n, p in C['events']])
        if c in sp['gait']: e['speed_mps'] = sp['gait'][c]['speed']
        d['clips'][c] = e
    json.dump(d, open(path, 'w'), indent=1); print('events', path)


if __name__ == '__main__':
    ID, CMD = args()
    print('=== BRD-07 Turkey rig', CMD)
    if CMD == 'bend':
        B = rig_model(os.path.join(CHECK, 'tex')); poses = bend_poses(B['sk'])
        setters = [(lambda p=p: apply_pose(B['rig'], p)) for p in poses]
        strip(B, setters, os.path.join(CHECK, 'Turkey_bend_side.png'), (1.0, -0.15, 0.2))
        strip(B, setters, os.path.join(CHECK, 'Turkey_bend_front.png'), (-0.6, -1.0, 0.45))
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
        full = dict(asset=ASSET, tris=B['total'], bones=len(B['rig'].data.bones), rig=B['rig_checks'], clips=rep,
                    export=dict(fbx=fbx, takes=[(s['name'], s['frames30']) for s in summ['stacks']], limbs=summ['limb_nodes'],
                                roots=summ['roots'], reimport=X))
        json.dump(full, open(os.path.join(WORK, 'metrics_report.json'), 'w'), indent=1, default=str)
        print('report', os.path.join(WORK, 'metrics_report.json'))
