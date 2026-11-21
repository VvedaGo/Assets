# rig_goat.py - LIV-08 Goat: skeleton Q (Cow's 27 bones incl. Horn.L/R, Tail1-3) + Beard (child of Jaw) = 28 bones,
# binding of the final mesh parts (each part = its bone, weight 1.0; Eye.L/R and Nose -> Head; two-bone 50/50 blend only on
# the knee/hock line where Lower is tucked into Upper), bend test, clips Goat_Idle / Goat_Walk / Goat_Browse, metrics,
# FBX + .blend. Pattern: ../Pig/rig_pig.py and ../Calf/rig_calf.py (read-only).
#   PYTHONUTF8=1 blender --background --factory-startup --python rig_goat.py -- LIV-08 bend|anim|export
# bend  : rig + extreme poses -> strips (TEMP)
# anim  : rig + clips + metrics (metrics_report.json) + clip strips (TEMP)
# export: anim + FBX (skinned parts + armature + 3 takes, NLA, bake_space_transform) + re-import check + events json + .blend
# The mesh comes unchanged from build_goat.build() (geometry, part names and pivots untouched).
import sys, os, math, json, importlib
REPO = r'D:\GitProjects\Assets_Farm'
WORK = REPO + r'\.work\models\Farm_Animals\Goat'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common', WORK):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
import numpy as np
from mathutils import Vector
import pack_common as pc
import animal_render as rn, animal_rig as ar, animal_species as asp, animal_anim as an, animal_export as ax
import build_goat as bg
import goat_clips as gcl
for m in (bg, gcl): importlib.reload(m)

ASSET = bg.ASSET; ART = bg.ART
CHECK = bg.CHECK
os.makedirs(CHECK, exist_ok=True)

ar.SKELETONS['QG'] = list(ar.Q_BONES) + [('Beard', 'Jaw')]
BIND = {'Eye.L': 'Head', 'Eye.R': 'Head', 'Nose': 'Head'}
LIMITS = dict(asp.Q_LIMITS, Beard=dict(x=(-30, 75), z=(-20, 20)),
              HindLower=dict(x=(-170, 24)))     # goat hock rests 24 deg flexed (lower rest -24.1): +24 = straight leg


def bone_of(part):
    return BIND.get(part, part)


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['LIV-08', 'bend'])[:2]


def far_vertex(o, piv):
    M = o.matrix_world
    return max((M @ v.co for v in o.data.vertices), key=lambda p: (p - piv).length)


def species(obs):
    """goat table in the animal_species format; bone heads = part pivots (joints), tails = next joint / far vertex"""
    P = {k: o.matrix_world.translation.copy() for k, o in obs.items()}
    t = lambda v: tuple(round(c, 4) for c in v)
    U = bg.U.normalized()
    B = {'Root': ((0, 0, 0), (0, -0.25, 0)),
         'Pelvis': (t(P['Pelvis']), t(P['Spine1'])), 'Spine1': (t(P['Spine1']), t(P['Spine2'])),
         'Spine2': (t(P['Spine2']), t(P['Neck1'])), 'Neck1': (t(P['Neck1']), t(P['Neck2'])),
         'Neck2': (t(P['Neck2']), t(P['Head'])), 'Head': (t(P['Head']), t(P['Nose'])),
         'Jaw': (t(P['Jaw']), t(P['Jaw'] + U * 0.15 * bg.HEAD_SCALE)),
         'Beard': (t(P['Beard']), t(far_vertex(obs['Beard'], P['Beard']))),
         'Ear.L': (t(P['Ear.L']), t(far_vertex(obs['Ear.L'], P['Ear.L']))),
         'Horn.L': (t(P['Horn.L']), t(far_vertex(obs['Horn.L'], P['Horn.L']))),
         'Tail1': (t(P['Tail1']), t(P['Tail2'])), 'Tail2': (t(P['Tail2']), t(P['Tail3'])),
         'Tail3': (t(P['Tail3']), t(far_vertex(obs['Tail3'], P['Tail3'])))}
    for kind in ('Front', 'Hind'):
        u, l, f = P[kind + 'Upper.L'], P[kind + 'Lower.L'], P[kind + 'Foot.L']
        B[kind + 'Upper.L'] = (t(u), t(l)); B[kind + 'Lower.L'] = (t(l), t(f)); B[kind + 'Foot.L'] = (t(f), t(Vector((f.x, f.y, 0.0))))
    return dict(id='LIV-08', species='Goat', asset=ASSET, tag=bg.TAG, skeleton='QG', bones=B,
                size=dict(length=1.10, withers=0.80),
                gait={'Walk': dict(T=0.9, duty=0.60, speed=0.40, lift=0.060, flick=(22, 16), crouch=0.002, roll=1.5,
                                   phases={'HindL': 0.0, 'FrontL': 0.25, 'HindR': 0.5, 'FrontR': 0.75},
                                   nod=3.0, ear=4.0, beard=6.0)},
                clips=[('Idle', 3.5, True), ('Walk', 0.9, True), ('Browse', 4.0, True)], limits=LIMITS, poses={},
                browse=dict(body_pitch=-3.0, nose_z=1.15, head_ang=(0.0, 20.0), reach_extra=0.015, tug_back=0.022,
                            tug_deg=7.0, ear_fwd=14.0))


def part_weights(nm, co, P):
    """per-vertex weights of a part (world co): its bone with 1.0, except the knee/hock line (Upper bottom ring + Lower top
    edge ring) 50/50 Upper/Lower, the Lower tuck ring hidden in Upper -> Upper, the Lower bottom ring hidden in the hoof -> Foot"""
    b = bone_of(nm)
    if nm in ('Neck1', 'Neck2'):
        return neck_weights(co, P)
    for s in ('.L', '.R'):
        for k in ('Front', 'Hind'):
            up, lo, ft = k + 'Upper' + s, k + 'Lower' + s, k + 'Foot' + s
            if nm not in (up, lo): continue
            zk = P[lo].z; zf = P[ft].z
            if nm == up:
                return {up: 0.5, lo: 0.5} if abs(co.z - zk) < 0.004 else {up: 1.0}
            if co.z < zf: return {ft: 1.0}
            if co.z > zk + 0.004: return {up: 1.0}
            return {up: 0.5, lo: 0.5}
    return {b: 1.0}


def neck_weights(co, P):
    """continuous weights along the neck path s (0 = Neck1 head, 1 = Neck2 head, 2 = Head head), identical for both neck
    parts so their coincident tuck rings move together: Spine2|Neck1 50/50 at the root, Neck1|Neck2 50/50 at the joint,
    Neck2|Head 20/80 at the skull (the head's small back ring stays covered when the head pitches up for Browse)"""
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


def joined(obs, rig, P):
    """TMP world-space copy of all parts with the same weights (for animal_anim.Skel and the metrics); never exported.
    Also returns the boolean mask of the Nose part vertices (muzzle) for the Browse search."""
    names = [b.name for b in rig.data.bones]; gi = {n: i for i, n in enumerate(names)}
    me = bpy.data.meshes.new('TMP_GoatAll'); ob = bpy.data.objects.new('TMP_GoatAll', me)
    bpy.context.scene.collection.objects.link(ob)
    for n in names: ob.vertex_groups.new(name=n)
    bm = bmesh.new(); dl = bm.verts.layers.deform.verify(); nose = []
    for nm, o in obs.items():
        M = o.matrix_world; vm = {}
        for v in o.data.vertices:
            co = M @ v.co; nv = bm.verts.new(co)
            for bn, w in part_weights(nm, co, P).items(): nv[dl][gi[bn]] = w
            vm[v.index] = nv; nose.append(nm == 'Nose')
        for p in o.data.polygons: bm.faces.new([vm[i] for i in p.vertices])
    bm.to_mesh(me); bm.free()
    ob.modifiers.new('Armature', 'ARMATURE').object = rig; ob.hide_render = True
    return ob, np.array(nose)


def rig_model(tex_dir):
    B = bg.build(tex_dir)
    sc = B['sc']; sc.render.fps = 30; sc.render.fps_base = 1.0
    SP = species(B['obs'])
    P = {k: o.matrix_world.translation.copy() for k, o in B['obs'].items()}
    rig = ar.build_armature(SP, B['coll'], 'QG')
    rchk = ar.check_rig(rig, 'QG')
    nblend = 0
    for nm, ob in B['obs'].items():
        mw = ob.matrix_world.copy(); ob.parent = rig; ob.matrix_parent_inverse.identity(); ob.matrix_world = mw
        for g in list(ob.vertex_groups): ob.vertex_groups.remove(g)
        groups = {}
        for v in ob.data.vertices:
            wd = part_weights(nm, mw @ v.co, P)
            if len(wd) > 1: nblend += 1
            for bn, w in wd.items():
                if bn not in groups: groups[bn] = ob.vertex_groups.new(name=bn)
                groups[bn].add([v.index], w, 'REPLACE')
        ob.modifiers.new('Armature', 'ARMATURE').object = rig
    bpy.data.objects.remove(B['root'], do_unlink=True)
    bpy.context.view_layer.update()
    tmp, nose = joined(B['obs'], rig, P)
    sk = an.Skel(rig, tmp)
    gcl.NOSE_MASK[0] = nose
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
    mk(lambda p: [an.rot(p, 'FrontLower.L', x=110), an.rot(p, 'FrontFoot.L', x=60), an.rot(p, 'HindLower.L', x=-100), an.rot(p, 'HindFoot.L', x=-60),
                  an.rot(p, 'FrontUpper.R', z=-20), an.rot(p, 'HindUpper.R', z=20)])
    mk(lambda p: [an.rot(p, 'Neck1', x=45), an.rot(p, 'Neck2', x=30), an.rot(p, 'Head', x=20)])        # head down
    mk(lambda p: [an.rot(p, 'Neck1', x=-30), an.rot(p, 'Neck2', x=-25), an.rot(p, 'Head', x=-35), an.rot(p, 'Jaw', x=22),
                  an.rot(p, 'Beard', x=-15)])                                                              # browse-like reach up
    mk(lambda p: [an.rot(p, 'Neck1', z=30), an.rot(p, 'Neck2', z=30), an.rot(p, 'Head', z=25)])
    mk(lambda p: [an.ear(p, up=40, back=-35), an.rot(p, 'Tail1', x=-30, z=30), an.rot(p, 'Tail2', z=35), an.rot(p, 'Tail3', z=40),
                  an.rot(p, 'Beard', z=20)])
    mk(lambda p: [an.ear(p, up=-35, back=35), an.rot(p, 'Tail1', x=30), an.rot(p, 'Tail2', x=25), an.rot(p, 'Tail3', x=25)])
    mk(lambda p: [an.body(sk, p, (0, 0, 0), pitch=12, roll=8), an.rot(p, 'Spine1', x=6, z=6), an.rot(p, 'Spine2', x=6, z=-6)])
    return P


# ---------------- clips ----------------
def anim(B):
    sk = B['sk']; SP = B['SP']
    clips = gcl.build_clips(sk, SP)
    acts = {}
    for c, _, _ in SP['clips']:
        C = clips[c]
        acts[c] = gcl.write_action_loc(B['rig'], f"{SP['species']}_{c}", C['frames'], C['loop'], C['bones'])
    ex = clips['Walk']['extra']
    print('WALK step', round(ex['step'], 3), 'drop front max/min', max(ex['drops']['Front']), min(ex['drops']['Front']),
          'hind', max(ex['drops']['Hind']), min(ex['drops']['Hind']))
    st = ex['stance']
    for k in an.LEGS:
        ft = ar.LEGS[k][2]; zs = []
        for f in st[k]:
            M = sk.fk(clips['Walk']['frames'][f]); zs.append((M[ft] @ Vector((0, sk.length[ft], 0))).z)
        print('WALK stance', k, 'frames', len(st[k]), 'foot tail z max', round(max(zs), 4), 'at', st[k][zs.index(max(zs))])
    rep = an.metrics(B['sc'], B['rig'], B['tmp'], {c: clips[c] for c, _, _ in SP['clips']}, acts, SP['limits'])
    # muzzle height over the Browse clip (Blender evaluation of the Nose part) vs the rest pose poll
    sc = B['sc']; an.assign(B['rig'], acts['Browse']); nose = B['obs']['Nose']; zs = []
    for f in range(int(acts['Browse'].frame_end) + 1):
        sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get(); me = nose.evaluated_get(dg).to_mesh()
        zs.append(sum((nose.matrix_world @ v.co).z for v in me.vertices) / len(me.vertices)); nose.evaluated_get(dg).to_mesh_clear()
    an.assign(B['rig'], None); sc.frame_set(0)
    rep['Browse']['nose_centre_z_m'] = [round(min(zs), 4), round(max(zs), 4)]
    rep['Browse'].update({k: (round(v, 4) if isinstance(v, float) else v) for k, v in clips['Browse']['extra'].items()})
    print('BROWSE nose centre z over the clip min/max', round(min(zs), 4), round(max(zs), 4), '| rest nose', round(nose.matrix_world.translation.z, 3))
    return clips, acts, rep


def clip_strips(B, clips, acts):
    sc = B['sc']; rig = B['rig']
    for c, _, _ in B['SP']['clips']:
        act = acts[c]; N = int(act.frame_end)
        fr = [round(i * N / 8) for i in range(8)]
        an.assign(rig, act)
        setters = [(lambda f=f: (sc.frame_set(f), bpy.context.view_layer.update())) for f in fr]
        view = (1.0, -0.05, 0.12) if c in ('Walk', 'Browse') else (0.85, -1.0, 0.25)
        strip(B, setters, os.path.join(CHECK, f'Goat_strip_{c}.png'), view)
    an.assign(rig, None); sc.frame_set(0)


# ---------------- export (copies of the Sheep/Pig steps for a multi-part skinned mesh) ----------------
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
    print('=== LIV-08 Goat rig', CMD)
    if CMD == 'bend':
        B = rig_model(os.path.join(CHECK, 'tex')); poses = bend_poses(B['sk'])
        setters = [(lambda p=p: apply_pose(B['rig'], p)) for p in poses]
        strip(B, setters, os.path.join(CHECK, 'Goat_bend_side.png'), (1.0, -0.15, 0.2))
        strip(B, setters, os.path.join(CHECK, 'Goat_bend_front.png'), (-0.6, -1.0, 0.35))
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
