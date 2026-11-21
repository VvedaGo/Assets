# rig_lamb.py - LIV-05 Lamb: skeleton Q-S (Q without Horn.L/R and Tail3 = 24 bones), rigid binding of the final mesh
# parts (each part = one vertex group, weight 1.0), bend test, clips Lamb_Idle / Lamb_Walk / Lamb_Play_Hop, metrics, FBX + .blend.
#   PYTHONUTF8=1 blender --background --factory-startup --python rig_lamb.py -- LIV-05 bend|anim|export
# bend  : rig + extreme poses -> strips (TEMP)
# anim  : rig + clips + metrics (metrics_report.json) + clip strips (TEMP)
# export: anim + FBX (skinned parts + armature + 3 takes, NLA, bake_space_transform) + re-import check + events json + .blend
# The mesh comes unchanged from build_lamb.build() (geometry, part names, Wool_* groups and pivots untouched).
# Shared modules (_common/animal_*.py) are used read-only; the skeleton variant is registered at runtime in this process.
import sys, os, math, json, importlib
REPO = r'D:\GitProjects\Assets_Farm'
WORK = REPO + r'\.work\models\Farm_Animals\Lamb'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common', WORK):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
import pack_common as pc
import animal_render as rn, animal_rig as ar, animal_species as asp, animal_anim as an, animal_export as ax
import build_lamb as bs
import lamb_clips as scl
for m in (bs, scl): importlib.reload(m)

ASSET = bs.ASSET; ART = bs.ART
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_lamb')
os.makedirs(CHECK, exist_ok=True)

ar.SKELETONS['QS'] = [(n, p) for n, p in ar.Q_BONES if n not in ('Horn.L', 'Horn.R', 'Tail3')]
BIND = {'Eye.L': 'Head', 'Eye.R': 'Head', 'Nose': 'Head', 'Wool_Pelvis': 'Pelvis', 'Wool_Spine1': 'Spine1',
        'Wool_Spine2': 'Spine2', 'Wool_Neck': 'Neck1', 'Wool_Head': 'Head'}


def bone_of(part):
    return BIND.get(part, part)


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['LIV-05', 'bend'])[:2]


EAR_D = Vector((1.0, -0.27, -0.24)).normalized()     # = build_lamb ear leaf direction (sideways, 15 fwd, 13 down)
EAR_LEN = 0.20                                         # visible ear leaf length (m, after the head scale)


def species(obs):
    """lamb table in the animal_species format; bone heads = part pivots (joints), tails = next joint"""
    P = {k: o.matrix_world.translation.copy() for k, o in obs.items()}
    t = lambda v: tuple(round(c, 4) for c in v)
    U = bs.U.normalized()
    B = {'Root': ((0, 0, 0), (0, -0.20, 0)),
         'Pelvis': (t(P['Pelvis']), t(P['Spine1'])), 'Spine1': (t(P['Spine1']), t(P['Spine2'])),
         'Spine2': (t(P['Spine2']), t(P['Neck1'])), 'Neck1': (t(P['Neck1']), t(P['Neck2'])),
         'Neck2': (t(P['Neck2']), t(P['Head'])), 'Head': (t(P['Head']), t(P['Nose'])),
         'Jaw': (t(P['Jaw']), t(P['Jaw'] + U * 0.12 * bs.HEAD_SCALE)),
         'Ear.L': (t(P['Ear.L']), t(P['Ear.L'] + EAR_D * EAR_LEN)),
         'Tail1': (t(P['Tail1']), t(P['Tail2'])),
         'Tail2': (t(P['Tail2']), t(P['Tail2'] + (P['Tail2'] - P['Tail1']).normalized() * 0.08))}
    for kind in ('Front', 'Hind'):
        u, l, f = P[kind + 'Upper.L'], P[kind + 'Lower.L'], P[kind + 'Foot.L']
        B[kind + 'Upper.L'] = (t(u), t(l)); B[kind + 'Lower.L'] = (t(l), t(f)); B[kind + 'Foot.L'] = (t(f), t(Vector((f.x, f.y, 0.0))))
    return dict(id='LIV-05', species='Lamb', asset=ASSET, tag=bs.TAG, skeleton='QS', bones=B,
                size=dict(length=0.86, withers=0.56),
                gait={'Walk': dict(T=0.7, duty=0.58, speed=0.22, lift=0.032, flick=(16, 12), crouch=0.002, roll=2.0,
                                   phases={'HindL': 0.0, 'FrontL': 0.25, 'HindR': 0.5, 'FrontR': 0.75},
                                   nod=5.0, wool=1.5, tail=(10.0, 14.0), ear=6.0)},
                hop=dict(T=1.0, takeoff=0.25, land=0.68, height=0.10, squash=0.030, tuck=0.05, pitch=6.0),
                clips=[('Idle', 3.0, True), ('Walk', 0.7, True), ('Play_Hop', 1.0, True)], limits=asp.Q_LIMITS, poses={})


def joined(obs, rig):
    """TMP world-space copy of all parts with one vertex group per bone (for animal_anim.Skel and the metrics); never exported"""
    names = [b.name for b in rig.data.bones]; gi = {n: i for i, n in enumerate(names)}
    me = bpy.data.meshes.new('TMP_LambAll'); ob = bpy.data.objects.new('TMP_LambAll', me)
    bpy.context.scene.collection.objects.link(ob)
    for n in names: ob.vertex_groups.new(name=n)
    bm = bmesh.new(); dl = bm.verts.layers.deform.verify()
    for nm, o in obs.items():
        M = o.matrix_world; g = gi[bone_of(nm)]; vm = {}
        for v in o.data.vertices:
            nv = bm.verts.new(M @ v.co); nv[dl][g] = 1.0; vm[v.index] = nv
        for p in o.data.polygons: bm.faces.new([vm[i] for i in p.vertices])
    bm.to_mesh(me); bm.free()
    ob.modifiers.new('Armature', 'ARMATURE').object = rig; ob.hide_render = True
    return ob


def rig_model(tex_dir):
    B = bs.build(tex_dir)
    sc = B['sc']; sc.render.fps = 30; sc.render.fps_base = 1.0
    SP = species(B['obs'])
    rig = ar.build_armature(SP, B['coll'], 'QS')
    rchk = ar.check_rig(rig, 'QS')
    for nm, ob in B['obs'].items():
        mw = ob.matrix_world.copy(); ob.parent = rig; ob.matrix_parent_inverse.identity(); ob.matrix_world = mw
        for g in list(ob.vertex_groups): ob.vertex_groups.remove(g)
        vg = ob.vertex_groups.new(name=bone_of(nm)); vg.add(list(range(len(ob.data.vertices))), 1.0, 'REPLACE')
        ob.modifiers.new('Armature', 'ARMATURE').object = rig
    bpy.data.objects.remove(B['root'], do_unlink=True)
    bpy.context.view_layer.update()
    tmp = joined(B['obs'], rig)
    sk = an.Skel(rig, tmp)
    print(f'RIG bones {len(rig.data.bones)} | parts bound {len(B["obs"])} | groups', sorted({bone_of(n) for n in B['obs']}))
    B.update(rig=rig, rig_checks=rchk, tmp=tmp, sk=sk, SP=SP)
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
    mk(lambda p: [an.rot(p, 'FrontUpper.L', x=-60), an.rot(p, 'FrontUpper.R', x=45), an.rot(p, 'HindUpper.L', x=60), an.rot(p, 'HindUpper.R', x=-45)])
    mk(lambda p: [an.rot(p, 'FrontLower.L', x=150), an.rot(p, 'FrontFoot.L', x=90), an.rot(p, 'HindLower.L', x=-150), an.rot(p, 'HindFoot.L', x=-90),
                  an.rot(p, 'FrontUpper.R', z=-25), an.rot(p, 'HindUpper.R', z=25)])
    mk(lambda p: [an.rot(p, 'Neck1', x=55), an.rot(p, 'Neck2', x=35), an.rot(p, 'Head', x=25)])        # graze-like reach down
    mk(lambda p: [an.rot(p, 'Neck1', x=-35), an.rot(p, 'Neck2', x=-30), an.rot(p, 'Head', x=-35), an.rot(p, 'Jaw', x=25)])
    mk(lambda p: [an.rot(p, 'Neck1', z=40), an.rot(p, 'Neck2', z=40), an.rot(p, 'Head', z=30)])
    mk(lambda p: [an.ear(p, up=60, back=-60), an.rot(p, 'Tail1', x=70, z=45), an.rot(p, 'Tail2', z=55)])
    mk(lambda p: [an.ear(p, up=-50, back=50), an.rot(p, 'Tail1', x=-50), an.rot(p, 'Tail2', x=-40)])
    mk(lambda p: [an.body(sk, p, (0, 0, 0), pitch=20, roll=12), an.rot(p, 'Spine1', x=12, z=12), an.rot(p, 'Spine2', x=12, z=-12)])
    return P


# ---------------- clips ----------------
def anim(B):
    sk = B['sk']; SP = B['SP']
    clips = scl.build_clips(sk, SP)
    acts = {}
    for c, _, _ in SP['clips']:
        C = clips[c]
        acts[c] = an.write_action(B['rig'], f"{SP['species']}_{c}", C['frames'], C['loop'], C['bones'])
    print('HOP', clips['Play_Hop']['extra'])
    ex = clips['Walk']['extra']; print('WALK step', round(ex['step'], 3), 'drop front max/min', max(ex['drops']['Front']), min(ex['drops']['Front']), 'hind', max(ex['drops']['Hind']), min(ex['drops']['Hind']))
    rep = an.metrics(B['sc'], B['rig'], B['tmp'], {c: clips[c] for c, _, _ in SP['clips']}, acts, SP['limits'])
    # wool gaps: how far each wool group's lobe centres move away from the core parts across the clip (rigid binding check)
    return clips, acts, rep


def clip_strips(B, clips, acts):
    sc = B['sc']; rig = B['rig']
    for c, _, _ in B['SP']['clips']:
        act = acts[c]; N = int(act.frame_end)
        fr = [round(i * N / 8) for i in range(8)]
        an.assign(rig, act)
        setters = [(lambda f=f: (sc.frame_set(f), bpy.context.view_layer.update())) for f in fr]
        view = (1.0, -0.05, 0.12) if c in ('Walk', 'Play_Hop') else (0.85, -1.0, 0.25)
        strip(B, setters, os.path.join(CHECK, f'Lamb_strip_{c}.png'), view)
    an.assign(rig, None); sc.frame_set(0)


# ---------------- export (lamb-local copies, from the Sheep, of the Cow/animal_export steps for a multi-part skinned mesh) ----------------
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
    print('=== LIV-05 Lamb rig', CMD)
    if CMD == 'bend':
        B = rig_model(os.path.join(CHECK, 'tex')); poses = bend_poses(B['sk'])
        setters = [(lambda p=p: apply_pose(B['rig'], p)) for p in poses]
        strip(B, setters, os.path.join(CHECK, 'Lamb_bend_side.png'), (1.0, -0.15, 0.2))
        strip(B, setters, os.path.join(CHECK, 'Lamb_bend_front.png'), (-0.6, -1.0, 0.35))
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
        full = dict(asset=ASSET, tris=B['total'], bones=len(B['rig'].data.bones), rig=B['rig_checks'], clips=rep,
                    export=dict(fbx=fbx, takes=[(s['name'], s['frames30']) for s in summ['stacks']], limbs=summ['limb_nodes'],
                                roots=summ['roots'], reimport=X))
        json.dump(full, open(os.path.join(WORK, 'metrics_report.json'), 'w'), indent=1, default=str)
        print('report', os.path.join(WORK, 'metrics_report.json'))
