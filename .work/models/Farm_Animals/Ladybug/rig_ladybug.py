# rig_ladybug.py - INS-03 Ladybug: insect rig (skeleton I, copy of ../Bee/rig_bee.py), rigid binding of the final part mesh,
# bend test, clips Ladybug_Idle / Ladybug_Crawl / Ladybug_Fly (ladybug_clips.py), metrics, FBX (skinned parts + armature +
# 3 takes) + events json + .blend.
#   PYTHONUTF8=1 blender --background --factory-startup --python rig_ladybug.py -- INS-03 bend|anim|export
# FINAL EXPORT = this script's export mode (build_ladybug.py export would overwrite the FBX with the static mesh).
# The mesh comes unchanged from build_ladybug.build() (16 parts); every part bound rigidly (weight 1.0) to one bone.
import sys, os, math, json, importlib
REPO = r'C:\Users\Sergv\orca\workspaces\VFX\master-3'
WORK = REPO + r'\.work\models\Farm_Animals\Ladybug'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common', WORK):
    if p not in sys.path: sys.path.insert(0, p)
import bpy
from mathutils import Vector, Matrix
import animal_render as rn, animal_export as ax
import build_ladybug as bm_
import ladybug_clips as bc
for m in (bm_, bc): importlib.reload(m)

RIG_OBJECT = 'Rig'          # same armature object name as every species of the pack

# ---------------- species table (Bee) - the only block to change for another insect ----------------
SPECIES = dict(
    id='INS-03', species='Ladybug', asset=bm_.ASSET, skeleton='I',
    # skeleton I variant: Elytra (hard shells, hinge at the top-front of the split) + Wing (folded hind wings) per side
    bones=[('Root', None), ('Body', 'Root'), ('Head', 'Body'), ('Antenna.L', 'Head'), ('Antenna.R', 'Head'),
           ('Elytra.L', 'Body'), ('Elytra.R', 'Body'), ('Wing.L', 'Body'), ('Wing.R', 'Body'),
           ('Leg_1.L', 'Body'), ('Leg_2.L', 'Body'), ('Leg_3.L', 'Body'), ('Leg_1.R', 'Body'), ('Leg_2.R', 'Body'), ('Leg_3.R', 'Body')],
    bind={'Eye.L': 'Head', 'Eye.R': 'Head'},
    tails={'Root': (0, -0.020, 0), 'Body': (0, -0.012, 0), 'Head': (0, -0.010, 0), 'Antenna': 'far', 'Wing': 'far',
           'Elytra': (0, 0.030, 0), 'Leg': 'far'},
    limits={'Body': 30, 'Head': 25, 'Antenna': 40, 'Elytra': 75, 'Wing': 115, 'Leg': 45},
    clips=[('Idle', 3.0, True), ('Crawl', 16 / 30, True), ('Fly', 1.0, True)],
    idle=dict(breath=1.2, head_yaw=6.0, head_nod=3.0, ant_pitch=14.0, ant_yaw=16.0, ant_flick=22.0),
    crawl=dict(step=0.0050, duty=0.5, lift=0.0011, bob=0.00025, roll=1.5, yaw=2.0, pitch=0.0, head_nod=2.5, ant_fwd=8.0, ant_amp=8.0),
    fly=dict(hover=0.045, flaps=5, flap_mid=12.0, flap_amp=34.0, feather=12.0, bob=0.0008, bob_slow=0.0020, pitch=-22.0, pitch_amp=3.0,
             roll=2.0, ely_open=12.0, ely_rear_up=38.0, ely_yaw=28.0, ely_tremble=2.0, ely_shift=0.0008, unfold=78.0,
             leg_back=(-5.0, 20.0, 30.0), leg_swing=4.0, leg_hang=25.0, head_nod=3.0, ant_trail=10.0, ant_amp=6.0),
)
SP = SPECIES
ASSET = SP['asset']; ART = bm_.ART
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_ladybug_rig')
os.makedirs(CHECK, exist_ok=True)


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['INS-03', 'bend'])[:2]


def bone_of(part):
    return SP['bind'].get(part, part)


def bone_heads_tails(obs):
    """heads at part pivots; tails per SP['tails'] (by bone name or its prefix before '_' / '.')"""
    out = {}
    for n, par in SP['bones']:
        key = n if n in SP['tails'] else n.split('.')[0].split('_')[0]
        rule = SP['tails'][key]
        if n == 'Root':
            h = Vector((0, 0, 0)); out[n] = (h, h + Vector(rule)); continue
        o = obs[n]; h = o.matrix_world.translation.copy()
        if rule == 'far':
            t = max((o.matrix_world @ v.co for v in o.data.vertices), key=lambda p: (p - h).length)
        elif rule == 'face':
            em = (obs['Eye.L'].matrix_world.translation + obs['Eye.R'].matrix_world.translation) / 2
            d = Vector((em.x - h.x, em.y - h.y, 0)).normalized(); t = h + d * 0.014
        else:
            t = h + Vector(rule)
        out[n] = (h, t)
    return out


def build_armature(tab, coll):
    """copy of animal_rig.build_armature without .L->.R mirroring (roll rule identical: sagittal bones local X = world X,
    lateral bones local Z = world up)"""
    arm = bpy.data.armatures.get(RIG_OBJECT) or bpy.data.armatures.new(RIG_OBJECT)
    rig = bpy.data.objects.new(RIG_OBJECT, arm); coll.objects.link(rig)
    vl = bpy.context.view_layer
    for o in bpy.context.scene.objects: o.select_set(False)
    vl.objects.active = rig; rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for eb in list(arm.edit_bones): arm.edit_bones.remove(eb)
    for name, par in SP['bones']:
        h, t = tab[name]
        eb = arm.edit_bones.new(name); eb.head = h; eb.tail = t; eb.use_deform = True
        d = (t - h).normalized()
        if abs(d.x) > 0.7: eb.align_roll(Vector((0, 0, 1)))
        else: eb.align_roll(Vector((1, 0, 0)).cross(d))
        if par: eb.parent = arm.edit_bones[par]; eb.use_connect = False
    bpy.ops.object.mode_set(mode='OBJECT')
    for pb in rig.pose.bones: pb.rotation_mode = 'XYZ'
    arm.display_type = 'STICK'
    return rig


def rig_model(tex_dir):
    B = bm_.build(tex_dir)
    sc = B['sc']; sc.render.fps = 30; sc.render.fps_base = 1.0
    tab = bone_heads_tails(B['obs'])
    rig = build_armature(tab, B['coll'])
    names = [b.name for b in rig.data.bones]
    par_ok = all((rig.data.bones[n].parent.name if rig.data.bones[n].parent else None) == p for n, p in SP['bones'])
    for nm, ob in B['obs'].items():
        mw = ob.matrix_world.copy(); ob.parent = rig; ob.matrix_parent_inverse.identity(); ob.matrix_world = mw
        for g in list(ob.vertex_groups): ob.vertex_groups.remove(g)
        g = ob.vertex_groups.new(name=bone_of(nm)); g.add(list(range(len(ob.data.vertices))), 1.0, 'REPLACE')
        ob.modifiers.new('Armature', 'ARMATURE').object = rig
    bpy.data.objects.remove(B['root'], do_unlink=True)
    bpy.context.view_layer.update()
    print(f'RIG bones {len(names)} hierarchy_ok {par_ok} parts bound {len(B["obs"])} (rigid 1.0) | bones',
          {n: (tuple(round(c, 4) for c in rig.data.bones[n].head_local), round(rig.data.bones[n].length, 4)) for n in names})
    B.update(rig=rig, rig_checks=dict(bones=len(names), hierarchy_ok=par_ok, rigid=True), SP=SP)
    return B


# ---------------- strips ----------------
def strip(B, setters, out, view, cols=4, size=(320, 240)):
    sc = B['sc']; rn.setup_workbench(sc, *size); g = rn.ground(sc); cam = rn.camera(sc); cam.data.clip_start = 0.002
    obs = list(B['obs'].values()); pts = []
    for st in setters:
        st(); pts += rn.mesh_points(obs)[::3]
    rn.fit(sc, cam, pts, view, (0.94, 0.92))
    tiles = []
    for i, st in enumerate(setters):
        st(); p = rn.render_to(sc, os.path.join(CHECK, f'tile_{i}.png')); tiles.append(rn.load_px(p)); os.remove(p)
    rn.compose(tiles, cols, out)
    bpy.data.objects.remove(g, do_unlink=True)


def bend_poses(rig):
    W = bc.World(rig); P = []
    P.append(bc.fly_frame(W, SP, 0.0, 1.0))
    P.append(bc.fly_frame(W, SP, 0.1, 1.0))
    P.append(W.pose({n: W.rot_axis(n, (0, 0, 1), 25 * (1 if n[4] != '3' else -1) * bc.side(n)) for n in bc.LEGS}))
    P.append(W.pose({n: W.rot_axis(n, (0, 1, 0), -25 * bc.side(n)) for n in bc.LEGS}))
    P.append(W.pose({'Head': W.rot_axis('Head', (0, 0, 1), 25), 'Antenna.L': W.rot_axis('Antenna.L', (1, 0, 0), -40),
                     'Antenna.R': W.rot_axis('Antenna.R', (1, 0, 0), 40)}))
    P.append(W.pose({'Head': W.rot_axis('Head', (1, 0, 0), 25)}))
    P.append(W.pose({'Elytra.L': W.rot_axis('Elytra.L', (0, 1, 0), -75), 'Elytra.R': W.rot_axis('Elytra.R', (0, 1, 0), 75)}))
    P.append(W.pose({'Body': W.rot_axis('Body', (1, 0, 0), -30)}))
    return P


# ---------------- clips ----------------
def anim(B):
    rig = B['rig']; clips = bc.build_clips(rig, SP, B['obs'])
    print('CRAWL', {k: v for k, v in clips['Crawl']['extra'].items() if k != 'stance'})
    acts = {c: bc.write_action(rig, f"{SP['species']}_{c}", clips[c]['frames'], loop) for c, _, loop in SP['clips']}
    rep = bc.metrics(B['sc'], rig, B['obs'], clips, acts, SP)
    return clips, acts, rep


def clip_strips(B, acts):
    sc = B['sc']; rig = B['rig']
    for c, _, _ in SP['clips']:
        act = acts[c]; N = int(act.frame_end)
        fr = [round(i * N / 8) for i in range(8)] if c != 'Fly' else [0, 1, 2, 3, 4, 5, 15, 21]
        bc.assign(rig, act)
        setters = [(lambda f=f: (sc.frame_set(f), bpy.context.view_layer.update())) for f in fr]
        strip(B, setters, os.path.join(CHECK, f'Ladybug_strip_{c}.png'), (0.9, -0.8, 0.3))
    bc.assign(rig, None); sc.frame_set(0)


# ---------------- export (copied from rig_hen.py) ----------------
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
            win.scene = prev; bc.assign(rig, act); prev.frame_set(f); A = world([src[n] for n in names])
            win.scene = sc; iad = irig.animation_data or irig.animation_data_create(); iad.action = ia
            if ia.slots: iad.action_slot = ia.slots[0]
            sc.frame_set(f + int(round(ia.frame_range[0]))); Bv = world([imesh[n] for n in names])
            if len(A) != len(Bv): worst = float('inf'); break
            worst = max(worst, max((a - b).length for a, b in zip(A, Bv)))
        errs[act.name] = round(worst, 5)
    res['missing_parts'] = missing; res['max_vertex_error_m'] = errs
    win.scene = prev; bc.assign(rig, None)
    for o in new_obs:
        d = o.data; bpy.data.objects.remove(o, do_unlink=True)
        try:
            if d is not None and d.users == 0: (bpy.data.meshes if isinstance(d, bpy.types.Mesh) else bpy.data.armatures).remove(d)
        except Exception: pass
    for a in new_acts: bpy.data.actions.remove(a)
    bpy.data.scenes.remove(sc)
    print('REIMPORT', {k: v for k, v in res.items() if k != 'import_actions'}); print('REIMPORT actions', res['import_actions'])
    return res


def events_json(clips, path):
    F = SP['fly']
    d = dict(species='Ladybug', asset=ASSET, fps=bc.FPS, note='Unity AnimationEvents to add on import (FBX does not carry them)', clips={})
    for c, T, loop in SP['clips']:
        N = len(clips[c]['frames']) - 1; ev = []
        if c == 'Crawl':
            ev = [dict(name='Footstep', frame=f, time=round(f / bc.FPS, 4), stringParameter=p) for f, p in ((0, 'TripodA'), (N // 2, 'TripodB'))]
        if c == 'Fly':
            ev = [dict(name='WingFlap', frame=int(round(i * N / F['flaps'])), time=round(i * N / F['flaps'] / bc.FPS, 4), stringParameter='Down')
                  for i in range(F['flaps'])]
        d['clips'][c] = dict(take=f'Ladybug_{c}', seconds=round(N / bc.FPS, 3), last_frame=N, loop=loop, events=ev)
        if c == 'Crawl': d['clips'][c]['speed_mps'] = round(clips[c]['extra']['speed'], 4)
        if c == 'Fly': d['clips'][c]['hover_m'] = F['hover']
    json.dump(d, open(path, 'w'), indent=1); print('events', path)


if __name__ == '__main__':
    ID, CMD = args()
    print('=== INS-03 Ladybug rig', CMD)
    if CMD == 'bend':
        B = rig_model(os.path.join(CHECK, 'tex')); W = bc.World(B['rig']); poses = bend_poses(B['rig'])
        setters = [(lambda p=p: W.apply(p)) for p in poses]
        strip(B, setters, os.path.join(CHECK, 'Ladybug_bend_34.png'), (0.9, -0.6, 0.3))
        strip(B, setters, os.path.join(CHECK, 'Ladybug_bend_front.png'), (0.0, -1.0, 0.25))
    elif CMD == 'anim':
        B = rig_model(os.path.join(CHECK, 'tex')); clips, acts, rep = anim(B)
        json.dump(rep, open(os.path.join(WORK, 'metrics_report.json'), 'w'), indent=1)
        clip_strips(B, acts)
    elif CMD == 'export':
        B = rig_model(os.path.join(ART, 'Textures')); clips, acts, rep = anim(B)
        parts = list(B['obs'].values()); al = [acts[c] for c, _, _ in SP['clips']]
        fbx = os.path.join(ART, 'Meshes', ASSET + '.fbx')
        export_nla(B['rig'], parts, al, fbx)
        summ = ax.fbx_summary(fbx)
        X = reimport_check(fbx, B['rig'], parts, al)
        events_json(clips, os.path.join(ART, 'Meshes', ASSET + '.events.json'))
        coll = B['coll']
        data = {coll} | set(coll.objects) | {o.data for o in coll.objects if o.data} | {B['mat'], B['img']} | set(al)
        bpy.data.libraries.write(os.path.join(ART, 'Blend', ASSET + '.blend'), data, fake_user=True, path_remap='ABSOLUTE')
        print('blend', os.path.join(ART, 'Blend', ASSET + '.blend'), 'objects', len(coll.objects), 'actions', [a.name for a in al])
        full = dict(asset=ASSET, tris=B['total'], bones=len(B['rig'].data.bones), rig=B['rig_checks'], clips=rep,
                    export=dict(fbx=fbx, takes=[(s['name'], s['frames30']) for s in summ['stacks']], limbs=summ['limb_nodes'],
                                roots=summ['roots'], reimport=X))
        json.dump(full, open(os.path.join(WORK, 'metrics_report.json'), 'w'), indent=1, default=str)
        print('report', os.path.join(WORK, 'metrics_report.json'))
