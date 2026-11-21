# rig_calf.py - LIV-02 Calf rig + clips + skinned export (skeleton Q, 25 bones: Cow names/hierarchy without Horn.L/R).
#   PYTHONUTF8=1 blender --background --factory-startup --python rig_calf.py -- LIV-02 rig|bend|anim|export
# rig   : final mesh from build_calf.py (geometry, part names, pivots unchanged) joined into ONE skinned mesh FMS_Calf,
#         armature 'Rig' with bone heads on the part pivots, each part bound rigidly (weight 1.0) to its bone
# bend  : rig + extreme joint poses -> strips (TEMP)
# anim  : rig + Calf_Idle / Calf_Walk / Calf_Lie_Idle + stage-5 metrics (metrics_report.json) + frame strips (TEMP)
# export: anim + FBX (mesh + armature + 3 takes, NLA, bake_space_transform) + verify + events json + .blend (rig + actions)
# Shared modules in _common are imported read-only; calf-specific copies live here.
import sys, os, math, json, importlib
REPO = r'C:\Users\Sergv\orca\workspaces\VFX\master-3'
HERE = REPO + r'\.work\models\Farm_Animals\Calf'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common', HERE):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
import pack_common as pc
import animal_species as asp, animal_rig as ar, animal_render as rn, animal_anim as an, animal_export as ax
import build_calf as bc
import calf_clips

ASSET = bc.ASSET
ART = bc.ART
CHECK = bc.CHECK
RIG_OBJECT = ar.RIG_OBJECT
CALF_BONES = [(n, p) for n, p in ar.Q_BONES if not n.startswith('Horn')]      # 25 bones
PART_BONE = {'Eye.L': 'Head', 'Eye.R': 'Head', 'Nose': 'Head'}                # every other part -> bone of the same name

SP = dict(
    id='LIV-02', species='Calf', asset=ASSET, tag=bc.TAG, skeleton='Q', palette=bc.PALETTE,
    gait={'Walk': dict(T=0.8, duty=0.62, speed=0.62, lift=0.07, flick=(35, 25), crouch=0.0, bob=0.008,
                       phases={'HindL': 0.0, 'FrontR': 0.25, 'HindR': 0.5, 'FrontL': 0.75},      # diagonal-sequence walk
                       nod=3.5, tail=(5, 8, 11), ear=4.0)},
    clips=[('Idle', 3.0, True), ('Walk', 0.8, True), ('Lie_Idle', 3.5, True)],
    # calf limits: Q + hind hip abduction to 60 deg (Lie_Idle: the fat hind leg lies beside the belly, ANIMATION_FIXES 1)
    limits=dict(asp.Q_LIMITS, HindUpper=dict(x=(-60, 75), y=(-25, 25), z=(-60, 60))), poses=dict(lie_roll=2.0))


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['LIV-02', 'rig'])[:2]


# ---------------- skeleton from the part pivots ----------------
def bone_table(obs):
    P = {n: o.matrix_world.translation.copy() for n, o in obs.items()}
    far = lambda n: max((obs[n].matrix_world @ v.co for v in obs[n].data.vertices), key=lambda q: (q - P[n]).length)
    u_ear = Vector((1.0, 0.12, 0.22)).normalized()
    t = {
        'Root': (Vector((0, 0, 0)), Vector((0, -0.25, 0))),
        'Pelvis': (P['Pelvis'], P['Spine1']), 'Spine1': (P['Spine1'], P['Spine2']), 'Spine2': (P['Spine2'], P['Neck1']),
        'Neck1': (P['Neck1'], P['Neck2']), 'Neck2': (P['Neck2'], P['Head']), 'Head': (P['Head'], P['Nose']),
        'Jaw': (P['Jaw'], P['Jaw'] + bc.U * 0.20),
        'Tail1': (P['Tail1'], P['Tail2']), 'Tail2': (P['Tail2'], P['Tail3']), 'Tail3': (P['Tail3'], far('Tail3')),
    }
    for s, sg in (('.L', 1), ('.R', -1)):
        t['Ear' + s] = (P['Ear' + s], P['Ear' + s] + Vector((sg * u_ear.x, u_ear.y, u_ear.z)) * 0.30)
        for k in ('Front', 'Hind'):
            up, lo, ft = P[k + 'Upper' + s], P[k + 'Lower' + s], P[k + 'Foot' + s]
            t[k + 'Upper' + s] = (up, lo); t[k + 'Lower' + s] = (lo, ft); t[k + 'Foot' + s] = (ft, Vector((ft.x, ft.y, 0.0)))
    return t


def build_armature(tab, coll):
    """copy of animal_rig.build_armature for the calf bone list (no horns); same roll rule"""
    arm = bpy.data.armatures.new(RIG_OBJECT)
    rig = bpy.data.objects.new(RIG_OBJECT, arm); coll.objects.link(rig)
    vl = bpy.context.view_layer
    for o in bpy.context.scene.objects: o.select_set(False)
    vl.objects.active = rig; rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for name, par in CALF_BONES:
        h, tl = tab[name]
        eb = arm.edit_bones.new(name); eb.head = h; eb.tail = tl; eb.use_deform = True
        d = (tl - h).normalized()
        if abs(d.x) > 0.7: eb.align_roll(Vector((0, 0, 1)))
        else: eb.align_roll(Vector((1, 0, 0)).cross(d))
        if par: eb.parent = arm.edit_bones[par]; eb.use_connect = False
    bpy.ops.object.mode_set(mode='OBJECT')
    for pb in rig.pose.bones: pb.rotation_mode = 'XYZ'
    arm.display_type = 'STICK'
    return rig


def check_rig(rig):
    bones = rig.data.bones
    names_ok = set(b.name for b in bones) == set(n for n, _ in CALF_BONES)
    par_ok = all((bones[n].parent.name if bones[n].parent else None) == p for n, p in CALF_BONES if n in bones)
    print(f'RIG bones {len(bones)} (Q without horns {len(CALF_BONES)}) names_ok {names_ok} hierarchy_ok {par_ok}')
    return dict(bones=len(bones), names_ok=names_ok, hierarchy_ok=par_ok)


def join_parts(B):
    """all part objects -> one mesh FMS_Calf (world space, pivot = origin = ground under the centre of mass);
    per-vertex bone = the part's bone, weight 1.0"""
    bm = bmesh.new(); W = []; parts = {}
    for nm in bc.PART_ORDER:
        o = B['obs'][nm]; me = o.data.copy(); me.transform(o.matrix_world)
        n0 = len(bm.verts); bm.from_mesh(me); bpy.data.meshes.remove(me)
        n1 = len(bm.verts); W += [{PART_BONE.get(nm, nm): 1.0}] * (n1 - n0); parts[nm] = (n0, n1)
    coll = B['coll']
    for o in list(coll.objects):
        d = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if d is not None and d.users == 0: bpy.data.meshes.remove(d)
    me = bpy.data.meshes.new(ASSET); bm.to_mesh(me); bm.free()
    me.materials.append(B['mat'])
    ob = bpy.data.objects.new(ASSET, me); coll.objects.link(ob)
    return ob, W, parts


def lerp_w(y, knots):
    """knots [(y, bone)] ascending -> piecewise linear 2-bone blend (Cow weights pattern)"""
    if y <= knots[0][0]: return {knots[0][1]: 1.0}
    if y >= knots[-1][0]: return {knots[-1][1]: 1.0}
    for (y0, b0), (y1, b1) in zip(knots, knots[1:]):
        if y0 <= y <= y1:
            t = (y - y0) / (y1 - y0); return {b0: 1 - t, b1: t} if b0 != b1 else {b0: 1.0}


KNEE_MODE = os.environ.get('CALF_KNEE', 'rigid_sock')


def smooth_joints(ob, W, parts, tab):
    """rigid part binding everywhere except (as on the Cow): body blended across the Spine2|Spine1|Pelvis joints
    (+-8 cm) so the barrel bends without opening the tuck seams, Neck1 eases into Spine2 at its root, Neck2 into Head"""
    vs = ob.data.vertices; BW = 0.08
    y21 = tab['Spine1'][1].y; y1p = tab['Pelvis'][1].y            # Spine2 head / Spine1 head (the part boundaries)
    knots = [(y21 - BW, 'Spine2'), (y21 + BW, 'Spine1'), (y1p - BW, 'Spine1'), (y1p + BW, 'Pelvis')]
    n = 0
    for nm in ('Pelvis', 'Spine1', 'Spine2'):
        for i in range(*parts[nm]): W[i] = lerp_w(vs[i].co.y, knots); n += 1
    z1, z2, zh = tab['Neck1'][0].z, tab['Neck2'][0].z, tab['Head'][0].z
    for i in range(*parts['Neck1']):
        t = min(max((vs[i].co.z - z1) / (z2 - z1), 0.0), 1.0); W[i] = {'Spine2': 0.5 * (1 - t), 'Neck1': 0.5 + 0.5 * t}; n += 1
    for i in range(*parts['Neck2']):
        t = min(max((vs[i].co.z - z2) / (zh - z2), 0.0), 1.0); W[i] = {'Neck2': 1 - 0.8 * t, 'Head': 0.8 * t}; n += 1
    # legs (Cow knee pattern): the knee line (Upper bottom ring + sock top edge ring) 50/50 Upper/Lower -> no gap when the
    # knee bends; the sock's hidden tuck ring follows Upper; the sock's bottom ring (inside the hoof) follows Foot, so the
    # thick sock never swings out below the hoof when the short Lower bone tilts
    # knee line, rework (ANIMATION_FIXES 1): weights by side instead of a flat 50/50. The ring vertex on the OUTER side of the
    # fold (front of the front knee, back of the hind hock) stays with Upper, the inner one goes with Lower (it swings into the
    # upper and hides), the sides (on the hinge axis) are 50/50. A flat 50/50 collapsed the outer knee ring to a point when the
    # knee folds 140-170 deg (lying pose): the brown upper became a pyramid and the sock a flat sheet.
    for s in ('.L', '.R'):
        for k in ('Front', 'Hind'):
            up, lo, ft = k + 'Upper' + s, k + 'Lower' + s, k + 'Foot' + s
            kp = tab[lo][0]; zk = kp.z; zf = tab[ft][0].z; outer = -1.0 if k == 'Front' else 1.0

            def knee_w(co):
                if KNEE_MODE == 'orig': return {up: 0.5, lo: 0.5}
                d = co - kp; u = outer * d.y / max(math.hypot(d.x, d.y), 1e-6)
                w = min(max(0.5 + 0.5 * u, 0.0), 1.0)
                return {up: w, lo: 1.0 - w} if 0.0 < w < 1.0 else {(up if w >= 1.0 else lo): 1.0}
            for i in range(*parts[up]):
                if abs(vs[i].co.z - zk) < 0.004: W[i] = knee_w(vs[i].co); n += 1
            for i in range(*parts[lo]):
                z = vs[i].co.z
                if z < zf: W[i] = {ft: 1.0}
                elif z > zk + 0.004: W[i] = {up: 1.0}
                else: W[i] = {lo: 1.0} if KNEE_MODE == 'rigid_sock' else knee_w(vs[i].co)
                n += 1
    print(f'SMOOTH joint weights on {n} vertices (body + neck); all other parts rigid 1.0')


def rig(tex_dir):
    B = bc.build(tex_dir)
    sc = B['sc']; sc.render.fps = 30; sc.render.fps_base = 1.0
    tab = bone_table(B['obs'])
    ob, W, parts = join_parts(B)
    smooth_joints(ob, W, parts, tab)
    r = build_armature(tab, B['coll'])
    rchk = check_rig(r)
    ar.bind(ob, r, W)
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    print(f'SKINNED mesh {ob.name}: verts {len(ob.data.vertices)} tris {tris} parts {len(parts)}')
    B.update(ob=ob, rig=r, rig_checks=rchk, tris=tris, bones=tab)
    return B


# ---------------- bend test / strips ----------------
def apply_pose(rig_, pose):
    for n, (l, rr) in pose.items():
        pb = rig_.pose.bones[n]; pb.location = l; pb.rotation_euler = rr
    bpy.context.view_layer.update()


def strip(B, setters, out, view=bc.REF_VIEW, cols=4, size=(320, 240)):
    sc = B['sc']; rn.setup_workbench(sc, *size); g = rn.ground(sc); cam = rn.camera(sc)
    pts = []
    for st in setters:
        st(); pts += rn.mesh_points([B['ob']])[::5]
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
    mk(lambda p: [an.rot(p, 'FrontUpper.L', x=-75), an.rot(p, 'FrontUpper.R', x=60), an.rot(p, 'HindUpper.L', x=75), an.rot(p, 'HindUpper.R', x=-60)])
    mk(lambda p: [an.rot(p, 'FrontLower.L', x=150), an.rot(p, 'FrontFoot.L', x=90), an.rot(p, 'HindLower.L', x=-150), an.rot(p, 'HindFoot.L', x=-90),
                  an.rot(p, 'FrontUpper.R', z=-25), an.rot(p, 'HindUpper.R', z=25)])
    mk(lambda p: [an.rot(p, 'Neck1', x=60), an.rot(p, 'Neck2', x=40), an.rot(p, 'Head', x=40)])
    mk(lambda p: [an.rot(p, 'Neck1', x=-35), an.rot(p, 'Neck2', x=-30), an.rot(p, 'Head', x=-40), an.rot(p, 'Jaw', x=25)])
    mk(lambda p: [an.rot(p, 'Neck1', z=40), an.rot(p, 'Neck2', z=40), an.rot(p, 'Head', z=30)])
    mk(lambda p: [an.ear(p, up=60, back=-60), an.rot(p, 'Tail1', x=70, z=45), an.rot(p, 'Tail2', z=50), an.rot(p, 'Tail3', z=50)])
    mk(lambda p: [an.body(sk, p, (0, 0, 0), pitch=20, roll=12), an.rot(p, 'Spine1', x=12, z=12), an.rot(p, 'Spine2', x=12, z=-12)])
    P.append(calf_clips.best_lie(sk, SP)[0])
    return P


def anim(B):
    sk = an.Skel(B['rig'], B['ob'])
    clips = calf_clips.build_clips(sk, SP)
    acts = {}
    for c, _, _ in SP['clips']:
        C = clips[c]; acts[c] = an.write_action(B['rig'], f"{SP['species']}_{c}", C['frames'], C['loop'], C['bones'])
    rep = an.metrics(B['sc'], B['rig'], B['ob'], {c: clips[c] for c, _, _ in SP['clips']}, acts, SP['limits'])
    # lying pose: legs must stay under / beside the body (nothing above 60% of the lying back height)
    import numpy as np
    M = sk.fk(clips['Lie_Idle']['frames'][0]); legs = sk.mask(calf_clips.FRONT_LEGS + calf_clips.HIND_LEGS)
    LP = sk.skin(M, legs); BP = sk.skin(M, sk.mask(calf_clips.BODY))
    rep['Lie_Idle'].update(clips['Lie_Idle']['extra'].get('lie', {}), leg_top_z=round(float(LP[:, 2].max()), 3),
                           body_top_z=round(float(BP[:, 2].max()), 3), body_lowest_z=round(float(BP[:, 2].min()), 3))
    print('LIE legs top z', rep['Lie_Idle']['leg_top_z'], 'body top z', rep['Lie_Idle']['body_top_z'], 'belly z', rep['Lie_Idle']['body_lowest_z'])
    return sk, clips, acts, rep


def clip_strips(B, clips, acts):
    sc = B['sc']; r = B['rig']
    for c, _, _ in SP['clips']:
        act = acts[c]; N = int(act.frame_end)
        fr = [round(i * N / 8) for i in range(8)]
        an.assign(r, act)
        setters = [(lambda f=f: (sc.frame_set(f), bpy.context.view_layer.update())) for f in fr]
        view = (1.0, -0.25, 0.22) if c == 'Walk' else bc.REF_VIEW
        strip(B, setters, os.path.join(CHECK, f'Calf_strip_{c}.png'), view)
        if c == 'Lie_Idle':
            strip(B, setters[:4], os.path.join(CHECK, f'Calf_strip_{c}_front.png'), (0.25, -1.0, 0.15))
            strip(B, setters[:4], os.path.join(CHECK, f'Calf_strip_{c}_back.png'), (-0.7, 1.0, 0.4))
    an.assign(r, None); sc.frame_set(0)


# ---------------- export ----------------
def events_json(clips, path):
    d = dict(species=SP['species'], asset=ASSET, fps=an.FPS, note='Unity AnimationEvents to add on import (FBX does not carry them)',
             clips={})
    for c, T, loop in SP['clips']:
        C = clips[c]; N = len(C['frames']) - 1
        e = dict(take=f"{SP['species']}_{c}", seconds=round(N / an.FPS, 3), last_frame=N, loop=loop,
                 events=[dict(name=n, frame=f, time=round(f / an.FPS, 4), stringParameter=p) for f, n, p in C['events']])
        if c in SP['gait']: e['speed_mps'] = SP['gait'][c]['speed']
        d['clips'][c] = e
    json.dump(d, open(path, 'w'), indent=1); print('events', path)


def export_nla(rig_, mesh, actions, fbx):
    """Cow export_nla pattern (one NLA track per action, bake_space_transform); all bones baked so the static folded
    legs of Lie_Idle keep their curves"""
    ad = rig_.animation_data or rig_.animation_data_create(); sc = bpy.context.scene
    assert sc.render.fps == 30 and sc.render.fps_base == 1.0
    for pb in rig_.pose.bones: pb.location = (0, 0, 0); pb.rotation_euler = (0, 0, 0)
    for o in sc.objects: o.select_set(False)
    rig_.select_set(True); mesh.select_set(True); bpy.context.view_layer.objects.active = rig_
    for t in list(ad.nla_tracks): ad.nla_tracks.remove(t)
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
    for t in list(ad.nla_tracks): ad.nla_tracks.remove(t)
    return fbx


if __name__ == '__main__':
    ID, CMD = args()
    print('=== LIV-02 Calf', CMD)
    if CMD == 'rig':
        B = rig(os.path.join(CHECK, 'tex'))
    elif CMD == 'bend':
        B = rig(os.path.join(CHECK, 'tex')); sk = an.Skel(B['rig'], B['ob'])
        poses = bend_poses(sk)
        st = [(lambda p=p: apply_pose(B['rig'], p)) for p in poses]
        strip(B, st, os.path.join(CHECK, 'Calf_bend_side.png'))
        strip(B, st, os.path.join(CHECK, 'Calf_bend_front.png'), view=(-0.6, -1.0, 0.25))
    elif CMD == 'anim':
        B = rig(os.path.join(CHECK, 'tex'))
        sk, clips, acts, rep = anim(B)
        json.dump(rep, open(os.path.join(HERE, 'metrics_report.json'), 'w'), indent=1)
        clip_strips(B, clips, acts)
    elif CMD == 'export':
        B = rig(os.path.join(ART, 'Textures')); sk, clips, acts, rep = anim(B)
        fbx = export_nla(B['rig'], B['ob'], [acts[c] for c, _, _ in SP['clips']], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        summ = ax.fbx_summary(fbx)
        cmp_ = ax.reimport_compare(fbx, B['rig'], B['ob'], [acts[c] for c, _, _ in SP['clips']])
        events_json(clips, os.path.join(ART, 'Meshes', ASSET + '.events.json'))
        an.assign(B['rig'], None)
        for pb in B['rig'].pose.bones: pb.location = (0, 0, 0); pb.rotation_euler = (0, 0, 0)
        bpy.context.view_layer.update()
        data = {B['coll'], B['ob'], B['rig'], B['ob'].data, B['rig'].data, B['mat'], B['img']} | set(acts.values())
        bpy.data.libraries.write(os.path.join(ART, 'Blend', ASSET + '.blend'), data, fake_user=True, path_remap='ABSOLUTE')
        print('blend', os.path.join(ART, 'Blend', ASSET + '.blend'))
        full = dict(asset=ASSET, tris=B['tris'], rig=B['rig_checks'], clips=rep,
                    export=dict(fbx=fbx, summary=summ, reimport=cmp_))
        json.dump(full, open(os.path.join(HERE, 'metrics_report.json'), 'w'), indent=1, default=str)
        print('report', os.path.join(HERE, 'metrics_report.json'))
