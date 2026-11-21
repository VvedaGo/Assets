# rig_frog.py - SML-05 Frog: new skeleton F (22 bones) designed from the mesh parts, rigid binding of the final parts
# (each part = one vertex group, weight 1.0; Jaw underside blended onto a scaled Throat bone), bend test, clips Frog_Idle /
# Frog_Jump, metrics, FBX + .blend.
#   PYTHONUTF8=1 blender --background --factory-startup --python rig_frog.py -- SML-05 bend|anim|export
# bend  : rig + extreme poses -> strips (TEMP)
# anim  : rig + clips + metrics (metrics_report.json) + clip strips (TEMP)
# export: anim + FBX (skinned parts + armature + 2 takes, NLA, bake_space_transform) + re-import check + events json + .blend
# The mesh comes unchanged from build_frog.build() (geometry, part names and pivots untouched).
# Structure copied from ../Mouse/rig_mouse.py (itself a copy of ../Rabbit/rig_rabbit.py); shared modules read-only.
import sys, os, math, json, importlib, copy
REPO = r'D:\GitProjects\Assets_Farm'
WORK = REPO + r'\.work\models\Farm_Animals\Frog'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common', WORK):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from bpy_extras import anim_utils
import pack_common as pc
import animal_render as rn, animal_rig as ar, animal_anim as an, animal_export as ax
import build_frog as bs
import frog_clips as rcl
for m in (bs, rcl): importlib.reload(m)

ASSET = bs.ASSET; ART = bs.ART
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_frog_rig')
os.makedirs(CHECK, exist_ok=True)

# skeleton F: Q-S names (Pelvis/Spine1/Spine2/Neck1/Head/Jaw, Front/Hind Upper/Lower/Foot) so generic tools still apply;
# no tail, no ears; + Throat (buccal pouch, scaled) and Eye.L/R (blink = eyes pulled in) under Head
SKEL = 'F_Frog'
ar.SKELETONS[SKEL] = [('Root', None), ('Pelvis', 'Root'), ('Spine1', 'Pelvis'), ('Spine2', 'Spine1'), ('Neck1', 'Spine2'),
                      ('Head', 'Neck1'), ('Jaw', 'Head'), ('Throat', 'Head'), ('Eye.L', 'Head'), ('Eye.R', 'Head'),
                      ('FrontUpper.L', 'Spine2'), ('FrontLower.L', 'FrontUpper.L'), ('FrontFoot.L', 'FrontLower.L'),
                      ('FrontUpper.R', 'Spine2'), ('FrontLower.R', 'FrontUpper.R'), ('FrontFoot.R', 'FrontLower.R'),
                      ('HindUpper.L', 'Pelvis'), ('HindLower.L', 'HindUpper.L'), ('HindFoot.L', 'HindLower.L'),
                      ('HindUpper.R', 'Pelvis'), ('HindLower.R', 'HindUpper.R'), ('HindFoot.R', 'HindLower.R')]
LOC_BONES = ('Pelvis', 'Eye.L', 'Eye.R')
SCALE_BONES = ('Throat',)
THROAT_Z = (0.0365, 0.0230)        # Jaw vertices: weight 0 on the Throat at/above the mouth line, 1 at the jaw floor

# frog joint limits (deg, local euler); legs fold/extend far (jump), feet flex both ways
LIMITS = {'Pelvis': dict(x=(-40, 25), y=(-10, 10), z=(-10, 10)), 'Spine1': dict(x=(-15, 15), z=(-15, 15)),
          'Spine2': dict(x=(-15, 15), z=(-15, 15)), 'Neck1': dict(x=(-20, 20), z=(-20, 20)), 'Head': dict(x=(-25, 25), z=(-25, 25)),
          'Jaw': dict(x=(-15, 5), z=(-3, 3)), 'Eye': dict(x=(-5, 5), y=(-5, 5), z=(-5, 5)),
          'FrontUpper': dict(x=(-90, 90), y=(-60, 60), z=(-80, 80)), 'FrontLower': dict(x=(-90, 90), y=(-45, 45), z=(-90, 90)),
          'FrontFoot': dict(x=(-60, 90), y=(-60, 60), z=(-60, 60)),
          'HindUpper': dict(x=(-90, 90), y=(-90, 90), z=(-135, 135)), 'HindLower': dict(x=(-90, 90), y=(-60, 60), z=(-110, 110)),
          'HindFoot': dict(x=(-30, 130), y=(-60, 60), z=(-70, 70)), 'NECK_YAW_TOTAL': 45}


def bone_of(part):
    return part


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['SML-05', 'bend'])[:2]


def species(obs):
    """frog table in the animal_species format; bone heads = part pivots (joints)"""
    P = {k: o.matrix_world.translation.copy() for k, o in obs.items()}
    t = lambda v: tuple(round(c, 5) for c in v)
    sh = Vector((0, 0.0133, 0))           # build_frog centre-of-mass shift (heads come from the pivots, which include it)
    jaw_y = P['Jaw'].y
    B = {'Root': ((0, 0, 0), (0, -0.03, 0)),
         'Pelvis': (t(P['Pelvis']), t(P['Spine1'])), 'Spine1': (t(P['Spine1']), t(P['Spine2'])),
         'Spine2': (t(P['Spine2']), t(P['Spine2'] + Vector((0, -0.010, 0.002)))),
         'Neck1': (t(P['Neck1']), t(P['Head'])),
         'Head': (t(P['Head']), t(P['Head'] + Vector((0, -0.024, 0.004)))),
         'Jaw': (t(P['Jaw']), t(P['Jaw'] + Vector((0, -0.034, -0.004)))),
         'Throat': (t(Vector((0, jaw_y - 0.012, 0.031))), t(Vector((0, jaw_y - 0.012, 0.021)))),
         'Eye.L': (t(P['Eye.L']), t(P['Eye.L'] + bs.EYE_AX.normalized() * 0.016))}
    for kind, fdir, flen in (('Front', bs.FF_DIR, 0.012), ('Hind', bs.HF_DIR, 0.022)):
        u, l, f = P[kind + 'Upper.L'], P[kind + 'Lower.L'], P[kind + 'Foot.L']
        if kind == 'Hind':
            # the shin mesh starts 11 mm below/outside the knee POINT (thigh tip) and reaches into the thigh with a hidden
            # cone to HIP.lerp(KNEE, 0.8) (build_frog): the knee HINGE is put there, so the shin stays rooted in the thigh
            # when the leg unfolds (hinge at the thigh tip opened a 1-2 cm gap). Mesh/pivots unchanged.
            l = u.lerp(l, 0.8)
        B[kind + 'Upper.L'] = (t(u), t(l)); B[kind + 'Lower.L'] = (t(l), t(f))
        B[kind + 'Foot.L'] = (t(f), t(f + Vector((fdir.x, fdir.y, 0.0)).normalized() * flen))
    return dict(id='SML-05', species='Frog', asset=ASSET, tag=bs.TAG, skeleton=SKEL, bones=B,
                size=dict(length=0.09, withers=0.05), gait={},
                clips=[('Idle', 3.0, True), ('Jump', 1.5, True)], limits=LIMITS, poses={})


def part_weights(nm, ob):
    """per vertex {bone: w}: rigid (part -> own bone), Jaw underside blended onto Throat by height"""
    if nm != 'Jaw': return None
    M = ob.matrix_world; out = []
    for v in ob.data.vertices:
        z = (M @ v.co).z; u = min(1.0, max(0.0, (THROAT_Z[0] - z) / (THROAT_Z[0] - THROAT_Z[1])))
        w = u * u * (3 - 2 * u); out.append({'Jaw': 1.0 - w, 'Throat': w})
    return out


def joined(obs, rig):
    """TMP world-space copy of all parts with the same vertex groups (for animal_anim.Skel and the metrics); never exported"""
    names = [b.name for b in rig.data.bones]; gi = {n: i for i, n in enumerate(names)}
    me = bpy.data.meshes.new('TMP_FrogAll'); ob = bpy.data.objects.new('TMP_FrogAll', me)
    bpy.context.scene.collection.objects.link(ob)
    for n in names: ob.vertex_groups.new(name=n)
    bm = bmesh.new(); dl = bm.verts.layers.deform.verify()
    for nm, o in obs.items():
        M = o.matrix_world; vm = {}; pw = part_weights(nm, o)
        for v in o.data.vertices:
            nv = bm.verts.new(M @ v.co); vm[v.index] = nv
            for b, w in (pw[v.index] if pw else {bone_of(nm): 1.0}).items():
                if w > 0: nv[dl][gi[b]] = w
        for p in o.data.polygons: bm.faces.new([vm[i] for i in p.vertices])
    bm.to_mesh(me); bm.free()
    ob.modifiers.new('Armature', 'ARMATURE').object = rig; ob.hide_render = True
    return ob


def rig_model(tex_dir):
    B = bs.build(tex_dir)
    sc = B['sc']; sc.render.fps = 30; sc.render.fps_base = 1.0
    SP = species(B['obs'])
    rig = ar.build_armature(SP, B['coll'], SKEL)
    rchk = ar.check_rig(rig, SKEL)
    for nm, ob in B['obs'].items():
        pw = part_weights(nm, ob)
        mw = ob.matrix_world.copy(); ob.parent = rig; ob.matrix_parent_inverse.identity(); ob.matrix_world = mw
        for g in list(ob.vertex_groups): ob.vertex_groups.remove(g)
        if pw is None:
            vg = ob.vertex_groups.new(name=bone_of(nm)); vg.add(list(range(len(ob.data.vertices))), 1.0, 'REPLACE')
        else:
            G = {b: ob.vertex_groups.new(name=b) for b in pw[0]}
            for i, wd in enumerate(pw):
                for b, w in wd.items():
                    if w > 0: G[b].add([i], w, 'REPLACE')
        ob.modifiers.new('Armature', 'ARMATURE').object = rig
    bpy.data.objects.remove(B['root'], do_unlink=True)
    bpy.context.view_layer.update()
    tmp = joined(B['obs'], rig)
    sk = an.Skel(rig, tmp)
    nt = sum(1 for w in part_weights('Jaw', B['obs']['Jaw']) if w['Throat'] > 0)
    print(f'RIG bones {len(rig.data.bones)} | parts bound {len(B["obs"])} | Jaw verts on Throat {nt}/{len(B["obs"]["Jaw"].data.vertices)}')
    B.update(rig=rig, rig_checks=rchk, tmp=tmp, sk=sk, SP=SP)
    return B


def write_action(rig, name, C):
    """animal_anim.write_action + location keys for LOC_BONES and scale keys for SCALE_BONES (clip['scale'])"""
    frames = C['frames']; scl = C.get('scale')
    old = bpy.data.actions.get(name)
    if old: bpy.data.actions.remove(old)
    act = bpy.data.actions.new(name); act.use_fake_user = True
    slot = act.slots.new(id_type='OBJECT', name=rig.name)
    cb = anim_utils.action_ensure_channelbag_for_slot(act, slot)
    N = len(frames) - 1
    for b in frames[0]:
        chans = [('rotation_euler', lambda f, i: frames[f][b][1][i])]
        if b in LOC_BONES: chans.append(('location', lambda f, i: frames[f][b][0][i]))
        if b in SCALE_BONES and scl: chans.append(('scale', lambda f, i: scl[f].get(b, (1, 1, 1))[i]))
        for path, get in chans:
            for i in range(3):
                fc = cb.fcurves.new(f'pose.bones["{b}"].{path}', index=i, group_name=b)
                fc.keyframe_points.add(N + 1)
                co = []
                for f in range(N + 1): co += [float(f), float(get(f, i))]
                fc.keyframe_points.foreach_set('co', co)
                fc.keyframe_points.foreach_set('interpolation', [1] * (N + 1))
                fc.update()
    act.use_frame_range = True; act.frame_start = 0; act.frame_end = N; act.use_cyclic = C['loop']
    return act


def apply_pose(rig, pose, scale=None):
    for n, (l, r) in pose.items():
        pb = rig.pose.bones[n]; pb.location = l; pb.rotation_euler = r; pb.scale = (scale or {}).get(n, (1, 1, 1))
    bpy.context.view_layer.update()


def strip(B, setters, out, view, cols=4, size=(320, 240)):
    sc = B['sc']; rn.setup_workbench(sc, *size); g = rn.ground(sc); cam = rn.camera(sc); cam.data.clip_start = 0.002
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
    r = an.rot
    mk(lambda p: [r(p, 'HindUpper.L', x=-60), r(p, 'HindLower.L', x=90), r(p, 'HindUpper.R', x=40, z=30), r(p, 'HindLower.R', x=-40)])
    mk(lambda p: [r(p, 'HindFoot.L', x=100), r(p, 'HindFoot.R', x=-40, z=30), r(p, 'FrontFoot.L', x=60), r(p, 'FrontFoot.R', x=-40)])
    mk(lambda p: [r(p, 'FrontUpper.L', x=-60), r(p, 'FrontLower.L', x=60), r(p, 'FrontUpper.R', x=50, z=-30), r(p, 'FrontLower.R', x=-50)])
    mk(lambda p: [r(p, 'Neck1', x=-20), r(p, 'Head', x=-25), r(p, 'Jaw', x=-15)])
    mk(lambda p: [r(p, 'Neck1', x=20, z=20), r(p, 'Head', x=25, z=25)])
    mk(lambda p: [an.body(sk, p, (0, 0, 0), pitch=-35), r(p, 'Spine1', x=-15), r(p, 'Spine2', x=-15)])
    mk(lambda p: [an.body(sk, p, (0, 0, 0), pitch=20, roll=10), r(p, 'Spine1', x=15, z=15), r(p, 'Spine2', x=15, z=-15)])
    mk(lambda p: [r(p, 'HindUpper.L', x=120), r(p, 'HindLower.L', x=-120), r(p, 'HindUpper.R', x=120), r(p, 'HindLower.R', x=-120)])
    return P


# ---------------- clips ----------------
def foot_slip(B, clips, acts):
    """planted feet (Blender evaluation): max distance of the foot bone head/tail from its rest spot, per clip"""
    rig = B['rig']; sc = B['sc']; out = {}
    for c, C in clips.items():
        an.assign(rig, acts[c]); worst = 0.0
        for k in rcl.LEGS:
            ft = ar.LEGS[k][2]; bn = rig.data.bones[ft]; h0, t0 = bn.head_local.copy(), bn.tail_local.copy()
            for f in C['planted'][k]:
                sc.frame_set(f); pb = rig.pose.bones[ft]
                worst = max(worst, (rig.matrix_world @ pb.head - h0).length, (rig.matrix_world @ pb.tail - t0).length)
        L = rig.data.bones['HindFoot.L'].length
        out[c] = dict(planted_foot_slip_m=round(worst, 6), planted_foot_slip_pct_of_foot=round(100 * worst / L, 3))
        print(f'SLIP {c}: planted feet max {worst * 1000:.3f} mm ({100 * worst / L:.2f}% of the {L * 1000:.0f} mm hind foot)')
    an.assign(rig, None)
    return out


def anim(B):
    sk = B['sk']; SP = B['SP']
    clips = rcl.build_clips(sk, SP)
    acts = {}
    for c, _, _ in SP['clips']:
        acts[c] = write_action(B['rig'], f"{SP['species']}_{c}", clips[c])
    import numpy as np
    for c, _, _ in SP['clips']:      # generator-side diagnosis (no bone scale): which bone owns the lowest vertex
        worst = (1.0, None, None)
        for f, pose in enumerate(clips[c]['frames']):
            V = sk.skin(sk.fk(pose)); i = int(np.argmin(V[:, 2]))
            if V[i, 2] < worst[0]: worst = (float(V[i, 2]), f, sk.order[int(np.argmax(sk.W[i]))])
        print(f'LOWEST {c}: z {worst[0]:.4f} frame {worst[1]} bone {worst[2]}')
    print('JUMP', clips['Jump']['extra'])
    # animal_anim.metrics sums Neck1 + Neck2 + Head yaw: the frog has no Neck2 -> a zero dummy only for that sum
    mc = {c: dict(clips[c], frames=[dict(fr_, Neck2=[[0.0] * 3, [0.0] * 3]) for fr_ in clips[c]['frames']]) for c, _, _ in SP['clips']}
    rep = an.metrics(B['sc'], B['rig'], B['tmp'], mc, acts, SP['limits'])
    slip = foot_slip(B, {c: clips[c] for c, _, _ in SP['clips']}, acts)
    for c, r in rep.items():
        r['lowest_vertex_limit_m'] = rcl.GROUND_TOL
        r.update(clips[c].get('extra', {})); r.update(slip[c])
        sc0, scN = clips[c]['scale'][0], clips[c]['scale'][-1]
        r['scale_loop_closure'] = max(abs(a - b) for k in sc0 for a, b in zip(sc0[k], scN[k]))
    return clips, acts, rep


def clip_strips(B, clips, acts, views=None):
    sc = B['sc']; rig = B['rig']
    for c, _, _ in B['SP']['clips']:
        act = acts[c]; N = int(act.frame_end)
        fr = [round(i * N / 8) for i in range(8)]
        if c == 'Jump': fr = [0, 12, 15, 17, 20, 23, 27, 30]
        an.assign(rig, act)
        setters = [(lambda f=f: (sc.frame_set(f), bpy.context.view_layer.update())) for f in fr]
        view = (views or {}).get(c) or (0.85, -1.0, 0.25)
        strip(B, setters, os.path.join(CHECK, f'Frog_strip_{c}.png'), view)
    an.assign(rig, None); sc.frame_set(0)


# ---------------- export (copies of the Lamb/Sheep steps for a multi-part skinned mesh) ----------------
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
        d['clips'][c] = e
    json.dump(d, open(path, 'w'), indent=1); print('events', path)


if __name__ == '__main__':
    ID, CMD = args()
    print('=== SML-05 Frog rig', CMD)
    if CMD == 'bend':
        B = rig_model(os.path.join(CHECK, 'tex')); poses = bend_poses(B['sk'])
        setters = [(lambda p=p: apply_pose(B['rig'], p)) for p in poses]
        strip(B, setters, os.path.join(CHECK, 'Frog_bend_side.png'), (1.0, -0.15, 0.2))
        strip(B, setters, os.path.join(CHECK, 'Frog_bend_front.png'), (-0.6, -1.0, 0.35))
    elif CMD == 'anim':
        B = rig_model(os.path.join(CHECK, 'tex')); clips, acts, rep = anim(B)
        json.dump(rep, open(os.path.join(WORK, 'metrics_report.json'), 'w'), indent=1, default=str)
        clip_strips(B, clips, acts, {'Jump': (1.0, -0.25, 0.10)})
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
        full = dict(asset=ASSET, tris=B['total'], bones=len(B['rig'].data.bones), rig=B['rig_checks'], clips=rep,
                    export=dict(fbx=fbx, takes=[(s['name'], s['frames30']) for s in summ['stacks']], limbs=summ['limb_nodes'],
                                roots=summ['roots'], reimport=X))
        json.dump(full, open(os.path.join(WORK, 'metrics_report.json'), 'w'), indent=1, default=str)
        print('report', os.path.join(WORK, 'metrics_report.json'))
