# rig_donkey.py - LIV-11 Donkey: skeleton Q-H (copy of Horse/rig_horse.py), rigid binding, bend test, clips (Idle/Walk/Graze),
# metrics, FBX + events + .blend.
#   PYTHONUTF8=1 blender --background --factory-startup --python rig_donkey.py -- LIV-11 rig|bend|anim|strips|export
# The mesh comes unchanged from build_donkey.build() (31 parts); the parts are joined into ONE skinned mesh FMS_Donkey
# (one SkinnedMeshRenderer, like the Horse) and every part is bound with weight 1.0 to the bone of the same name
# (Eye.L/R and Nostrils -> Head). Shared _common modules are imported read-only.
import sys, os, math, json, importlib
REPO = r'D:\GitProjects\Assets_Farm'
HERE = REPO + r'\.work\models\Farm_Animals\Donkey'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common', HERE):
    if p not in sys.path: sys.path.insert(0, p)
import bpy
from mathutils import Vector, Matrix
import pack_common as pc
import animal_species as asp, animal_rig as ar, animal_anim as an, animal_render as rn, animal_export as ax
import build_donkey as bh
import donkey_clips as hc
importlib.reload(hc)

ASSET = bh.ASSET; ART = bh.ART; CHECK = bh.CHECK
RIG = ar.RIG_OBJECT

# ---------------- species table (donkey-local; shared animal_species.py untouched) ----------------
LIMITS = dict(asp.Q_LIMITS)
LIMITS.update({'Mane1': dict(x=(-30, 30), y=(-25, 25), z=(-30, 30)), 'Mane2': dict(x=(-30, 30), y=(-25, 25), z=(-30, 30)),
               'Mane3': dict(x=(-30, 30), y=(-25, 25), z=(-30, 30)), 'Forelock': dict(x=(-30, 30), y=(-20, 20), z=(-30, 30)),
               'Ear': dict(x=(-70, 70), y=(-80, 80), z=(-70, 70)),
               # the horse hock rests at ~30 deg flexion (cannon not collinear with the gaskin): +30 = straight leg
               'HindLower': dict(x=(-140, 30)), 'FrontFoot': dict(x=(-75, 120))})
HORSE = dict(
    id='LIV-11', species='Donkey', asset=ASSET, tag=bh.TAG, skeleton='Q-H', palette=bh.PALETTE,
    clips=[('Idle', 4.0, True), ('Walk', 1.0, True), ('Graze', 5.0, True)],
    gait={'Walk': dict(T=1.0, duty=0.62, speed=0.85, lift=0.09, flick=(26, 18), crouch=0.006, bob=0.010,
                       phases={'HindL': 0.0, 'FrontL': 0.25, 'HindR': 0.5, 'FrontR': 0.75},     # four-beat LH-LF-RH-RF
                       nod=5.0, tail=(4, 6, 8), ear=3.0)},
    limits=LIMITS, poses=dict(graze_muzzle_z=0.03),
)

QH_BONES = [
    ('Root', None), ('Pelvis', 'Root'), ('Spine1', 'Pelvis'), ('Spine2', 'Spine1'),
    ('Neck1', 'Spine2'), ('Neck2', 'Neck1'), ('Head', 'Neck2'), ('Jaw', 'Head'),
    ('Ear.L', 'Head'), ('Ear.R', 'Head'), ('Forelock', 'Head'),
    ('Mane1', 'Neck2'), ('Mane2', 'Mane1'), ('Mane3', 'Neck1'),
    ('FrontUpper.L', 'Spine2'), ('FrontLower.L', 'FrontUpper.L'), ('FrontFoot.L', 'FrontLower.L'),
    ('FrontUpper.R', 'Spine2'), ('FrontLower.R', 'FrontUpper.R'), ('FrontFoot.R', 'FrontLower.R'),
    ('HindUpper.L', 'Pelvis'), ('HindLower.L', 'HindUpper.L'), ('HindFoot.L', 'HindLower.L'),
    ('HindUpper.R', 'Pelvis'), ('HindLower.R', 'HindUpper.R'), ('HindFoot.R', 'HindLower.R'),
    ('Tail1', 'Pelvis'), ('Tail2', 'Tail1'), ('Tail3', 'Tail2'),
]
PART_BONE = {n: n for n in bh.PART_ORDER}
PART_BONE.update({'Eye.L': 'Head', 'Eye.R': 'Head', 'Nostrils': 'Head'})


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['LIV-11', 'rig'])[:2]


def bone_table(P):
    """bone heads on the joints = the part pivots of build_horse (body bones on the part boundaries: the Pelvis part
    pivot is the Pelvis|Spine1 boundary, the Spine1 pivot the Spine1|Spine2 boundary)"""
    V = Vector; t = {}
    b1, b2 = P['Pelvis'], P['Spine1']
    ks = b2.z / 1.30                  # horse numbers below scaled by the body height (Horse Spine1 pivot z 1.30)
    t['Root'] = (V((0, 0, 0)), V((0, -0.25 * ks, 0)))
    t['Pelvis'] = (V((0, b1.y + 0.32 * ks, b1.z + 0.02 * ks)), V((0, b1.y, b1.z)))
    t['Spine1'] = (V((0, b1.y, b1.z)), V((0, b2.y, b2.z)))
    t['Spine2'] = (V((0, b2.y, b2.z)), V((0, b2.y - 0.48 * ks, b2.z + 0.02 * ks)))
    t['Neck1'] = (P['Neck1'], P['Neck2'])
    t['Neck2'] = (P['Neck2'], P['Head'])
    t['Head'] = (P['Head'], P['Nostrils'])
    jd = (P['Nostrils'] - P['Head']).normalized()
    t['Jaw'] = (P['Jaw'], P['Jaw'] + jd * 0.20 * ks)
    u = Vector((0.16, 0.06, 1.0)).normalized()
    t['Ear.L'] = (P['Ear.L'], P['Ear.L'] + u * 0.28 * ks)
    t['Forelock'] = (P['Forelock'], P['Forelock'] + jd * 0.30 * ks)
    t['Mane1'] = (P['Mane1'], P['Mane2']); t['Mane2'] = (P['Mane2'], P['Mane3'])
    t['Mane3'] = (P['Mane3'], P['Mane3'] + (P['Mane3'] - P['Mane2']).normalized() * 0.25 * ks)
    for k in ('Front', 'Hind'):
        up, lo, ft = P[k + 'Upper.L'], P[k + 'Lower.L'], P[k + 'Foot.L']
        t[k + 'Upper.L'] = (up, lo); t[k + 'Lower.L'] = (lo, ft); t[k + 'Foot.L'] = (ft, V((ft.x, ft.y, 0.0)))
    t['Tail1'] = (P['Tail1'], P['Tail2']); t['Tail2'] = (P['Tail2'], P['Tail3'])
    t['Tail3'] = (P['Tail3'], V((0, P["Tail3"].y + 0.04 * ks, P["Tail3"].z - 0.30 * ks)))
    full = {}
    for n, (h, tl) in t.items():
        full[n] = (h.copy(), tl.copy())
        if n.endswith('.L'):
            full[n[:-2] + '.R'] = (V((-h.x, h.y, h.z)), V((-tl.x, tl.y, tl.z)))
    return full


def build_armature(tab, coll):
    """copy of animal_rig.build_armature with the Q-H bone list (same roll rule: sagittal bones local X = world +X)"""
    arm = bpy.data.armatures.new(RIG)
    rig = bpy.data.objects.new(RIG, arm); coll.objects.link(rig)
    vl = bpy.context.view_layer
    for o in bpy.context.scene.objects: o.select_set(False)
    vl.objects.active = rig; rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for name, par in QH_BONES:
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
    names_ok = set(b.name for b in bones) == set(n for n, _ in QH_BONES)
    par_ok = all((bones[n].parent.name if bones[n].parent else None) == p for n, p in QH_BONES)
    roll_bad = [b.name for b in bones if abs((b.tail_local - b.head_local).normalized().x) < 0.01
                and b.matrix_local.to_3x3().col[0].dot(Vector((1, 0, 0))) < 0.999]
    print(f'RIG bones {len(bones)} names_ok {names_ok} hierarchy_ok {par_ok} roll_bad {roll_bad}')
    return dict(bones=len(bones), names_ok=names_ok, hierarchy_ok=par_ok, roll_bad=roll_bad)


def join_parts(B):
    """31 part objects -> one mesh FMS_Donkey in world space, a vertex group (bone name) per part, weight 1.0"""
    obs = B['obs']; root = B['root']
    tris0 = sum(len(o.data.polygons) for o in obs.values())
    for nm, o in obs.items():
        mw = o.matrix_world.copy(); o.parent = None
        o.data.transform(mw); o.matrix_world = Matrix.Identity(4)
        vg = o.vertex_groups.get(PART_BONE[nm]) or o.vertex_groups.new(name=PART_BONE[nm])
        vg.add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')
    bpy.data.objects.remove(root, do_unlink=True)
    vl = bpy.context.view_layer
    for o in bpy.context.scene.objects: o.select_set(False)
    for o in obs.values(): o.select_set(True)
    vl.objects.active = obs['Pelvis']
    bpy.ops.object.join()
    ob = vl.objects.active; ob.name = ASSET; ob.data.name = ASSET
    W = []
    gname = {g.index: g.name for g in ob.vertex_groups}
    for v in ob.data.vertices:
        gs = [(gname[g.group], g.weight) for g in v.groups if g.weight > 0]
        if len(gs) != 1: raise RuntimeError(f'vertex {v.index} groups {gs}')
        W.append({gs[0][0]: 1.0})
    tris1 = len(ob.data.polygons)
    print(f'JOIN parts {len(obs)} -> {ob.name}: tris {tris0} -> {tris1}, verts {len(ob.data.vertices)}')
    return ob, W


def rig_stage(tex_dir):
    B = bh.build(tex_dir)
    sc = B['sc']; sc.render.fps = 30; sc.render.fps_base = 1.0
    P = {n: o.location.copy() for n, o in B['obs'].items()}
    ob, W = join_parts(B)
    tab = bone_table(P)
    rig = build_armature(tab, B['coll'])
    rchk = check_rig(rig)
    ar.bind(ob, rig, W)
    B.update(ob=ob, rig=rig, rig_checks=rchk, tris=len(ob.data.polygons), pivots=P)
    return B


# ---------------- strips (Workbench, fixed camera) ----------------
def apply_pose(rig, pose):
    for n, (l, r) in pose.items():
        pb = rig.pose.bones[n]; pb.location = l; pb.rotation_euler = r
    bpy.context.view_layer.update()


def strip(B, setters, out, view=(1.0, -0.85, 0.30), cols=4, size=(320, 240)):
    sc = B['sc']; rn.setup_workbench(sc, *size); g = rn.ground(sc); cam = rn.camera(sc)
    pts = []
    for st in setters:
        st(); pts += rn.mesh_points([B['ob']])[::7]
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
    mk(lambda p: [an.rot(p, 'FrontLower.L', x=150), an.rot(p, 'FrontFoot.L', x=100), an.rot(p, 'HindLower.L', x=-150), an.rot(p, 'HindFoot.L', x=-100),
                  an.rot(p, 'FrontUpper.R', z=-25), an.rot(p, 'HindUpper.R', z=25)])
    mk(lambda p: [an.rot(p, 'Neck1', x=70), an.rot(p, 'Neck2', x=60), an.rot(p, 'Head', x=45)])
    mk(lambda p: [an.rot(p, 'Neck1', x=-40), an.rot(p, 'Neck2', x=-35), an.rot(p, 'Head', x=-45), an.rot(p, 'Jaw', x=28)])
    mk(lambda p: [an.rot(p, 'Neck1', z=45), an.rot(p, 'Neck2', z=45), an.rot(p, 'Head', z=30)])
    mk(lambda p: [hc.ears(p, l_swivel=80, r_swivel=80, l_tilt=-60, r_tilt=40), an.rot(p, 'Tail1', x=70, z=50),
                  an.rot(p, 'Tail2', z=60), an.rot(p, 'Tail3', z=60)])
    mk(lambda p: [an.rot(p, 'Mane1', z=30, y=25), an.rot(p, 'Mane2', z=30, y=25), an.rot(p, 'Mane3', z=-30, x=30),
                  an.rot(p, 'Forelock', z=30, x=-30)])
    mk(lambda p: [an.body(sk, p, (0, 0, 0), pitch=25, roll=15), an.rot(p, 'Spine1', x=15, z=15), an.rot(p, 'Spine2', x=15, z=-15)])
    return P


# ---------------- clips / actions / metrics ----------------
def anim(B):
    sk = an.Skel(B['rig'], B['ob'])
    clips = hc.build_clips(sk, HORSE)
    acts = {}
    for c, _, _ in HORSE['clips']:
        C = clips[c]; acts[c] = an.write_action(B['rig'], f"{HORSE['species']}_{c}", C['frames'], C['loop'], C['bones'])
    rep = an.metrics(B['sc'], B['rig'], B['ob'], {c: clips[c] for c, _, _ in HORSE['clips']}, acts, HORSE['limits'])
    rep['_graze'] = clips.get('_graze_info')
    # self-intersection probe: leg vertices of the far/near pairs crossing each other or the opposite leg plane, and
    # head vertices behind the front hooves while low (Graze)
    import numpy as np
    for c in ('Walk', 'Graze', 'Idle'):
        worst_x = 0.0
        L = sk.mask([b for b in sk.order if b.endswith('.L') and ('Front' in b or 'Hind' in b)])
        Rm = sk.mask([b for b in sk.order if b.endswith('.R') and ('Front' in b or 'Hind' in b)])
        for fr in clips[c]['frames']:
            M = sk.fk(fr)
            worst_x = max(worst_x, -float(sk.skin(M, L)[:, 0].min()), float(sk.skin(M, Rm)[:, 0].max()))
        rep[c]['legs_cross_midline_m'] = round(worst_x, 4)
        print(f'LEGS {c}: deepest leg vertex across the midline {worst_x:.4f} m (<0 = never crosses)')
    return sk, clips, acts, rep


def clip_strips(B, clips, acts):
    sc = B['sc']; rig = B['rig']
    for c, _, _ in HORSE['clips']:
        act = acts[c]; N = int(act.frame_end)
        fr = [round(i * N / 8) for i in range(8)]
        an.assign(rig, act)
        setters = [(lambda f=f: (sc.frame_set(f), bpy.context.view_layer.update())) for f in fr]
        view = (1.0, -0.15, 0.15) if c == 'Walk' else (1.0, -0.85, 0.30)
        strip(B, setters, os.path.join(CHECK, f"{HORSE['species']}_strip_{c}.png"), view)
        if c == 'Graze':
            strip(B, setters[:4], os.path.join(CHECK, f"{HORSE['species']}_strip_{c}_front.png"), (0.25, -1.0, 0.15), cols=4)
    an.assign(rig, None); sc.frame_set(0)


def events_json(clips, path):
    d = dict(species=HORSE['species'], asset=ASSET, fps=an.FPS, note='Unity AnimationEvents to add on import (FBX does not carry them)', clips={})
    for c, T, loop in HORSE['clips']:
        C = clips[c]; N = len(C['frames']) - 1
        e = dict(take=f"{HORSE['species']}_{c}", seconds=round(N / an.FPS, 3), last_frame=N, loop=loop,
                 events=[dict(name=n, frame=f, time=round(f / an.FPS, 4), stringParameter=p) for f, n, p in C['events']])
        if c in HORSE['gait']: e['speed_mps'] = HORSE['gait'][c]['speed']
        d['clips'][c] = e
    json.dump(d, open(path, 'w'), indent=1); print('events', path)


def export_nla(rig, mesh, actions, fbx):
    """Cow pattern: NLA track per action, bake_space_transform, all bones keyed in every take"""
    ad = rig.animation_data or rig.animation_data_create(); sc = bpy.context.scene
    assert sc.render.fps == 30 and sc.render.fps_base == 1.0
    for pb in rig.pose.bones: pb.location = (0, 0, 0); pb.rotation_euler = (0, 0, 0)
    for o in sc.objects: o.select_set(False)
    rig.select_set(True); mesh.select_set(True); bpy.context.view_layer.objects.active = rig
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
    print('=== LIV-11 Donkey rig', CMD)
    if CMD == 'rig':
        B = rig_stage(os.path.join(CHECK, 'tex'))
    elif CMD == 'bend':
        B = rig_stage(os.path.join(CHECK, 'tex')); sk = an.Skel(B['rig'], B['ob'])
        poses = bend_poses(sk)
        strip(B, [(lambda p=p: apply_pose(B['rig'], p)) for p in poses], os.path.join(CHECK, 'Donkey_bend_side.png'), (1.0, -0.2, 0.25))
        strip(B, [(lambda p=p: apply_pose(B['rig'], p)) for p in poses], os.path.join(CHECK, 'Donkey_bend_front.png'), (-0.6, -1.0, 0.3))
    elif CMD in ('anim', 'strips'):
        B = rig_stage(os.path.join(CHECK, 'tex'))
        sk, clips, acts, rep = anim(B)
        json.dump(rep, open(os.path.join(HERE, 'metrics_report.json'), 'w'), indent=1, default=str)
        if CMD == 'strips': clip_strips(B, clips, acts)
    elif CMD == 'export':
        B = rig_stage(os.path.join(ART, 'Textures'))
        sk, clips, acts, rep = anim(B)
        al = [acts[c] for c, _, _ in HORSE['clips']]
        fbx = export_nla(B['rig'], B['ob'], al, os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        summ = ax.fbx_summary(fbx)
        cmp_ = ax.reimport_compare(fbx, B['rig'], B['ob'], al)
        names = sorted(s_['name'] for s_ in summ['stacks'])
        print('EXPORT takes', names, 'match', names == sorted(a.name for a in al), 'limbs', summ['limb_nodes'])
        events_json(clips, os.path.join(ART, 'Meshes', ASSET + '.events.json'))
        for pb in B['rig'].pose.bones: pb.location = (0, 0, 0); pb.rotation_euler = (0, 0, 0)
        an.assign(B['rig'], None); bpy.context.view_layer.update()
        data = {B['coll'], B['ob'], B['rig'], B['ob'].data, B['rig'].data, B['mat'], B['img']} | set(acts.values())
        bpy.data.libraries.write(os.path.join(ART, 'Blend', ASSET + '.blend'), data, fake_user=True, path_remap='ABSOLUTE')
        print('blend', os.path.join(ART, 'Blend', ASSET + '.blend'))
        full = dict(asset=ASSET, tris=B['tris'], rig=B['rig_checks'], clips=rep,
                    export=dict(fbx=fbx, takes=names, summary=summ, reimport=cmp_))
        json.dump(full, open(os.path.join(HERE, 'metrics_report.json'), 'w'), indent=1, default=str)
        print('report', os.path.join(HERE, 'metrics_report.json'))
