# rig_butterfly.py - INS-02 Butterfly: insect rig (skeleton I, copy of Bee/rig_bee.py), rigid binding of the final part mesh,
# bend test, clips Butterfly_Fly / Butterfly_Perch_Idle (butterfly_clips.py), metrics, FBX (skinned parts + armature + 2 takes)
# + events json + .blend.
#   PYTHONUTF8=1 blender --background --factory-startup --python rig_butterfly.py -- INS-02 probe|bend|anim|export
# probe : wing closing fraction sweep -> overlap counts (numbers only)
# bend  : rig + extreme poses -> strips (TEMP)          anim  : rig + clips + metrics + clip strips (TEMP)
# export: anim + FBX (NLA takes, bake_space_transform) + re-import check + events json + .blend (rig + actions)
# FINAL EXPORT = this script's export mode (build_butterfly.py export would overwrite the FBX with the static mesh).
# The mesh comes unchanged from build_butterfly.build() (16 parts); every part bound rigidly (weight 1.0) to one bone.
import sys, os, math, json, importlib
REPO = r'D:\GitProjects\Assets_Farm'
WORK = REPO + r'\.work\models\Farm_Animals\Butterfly'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common', REPO + r'\.work\models\Farm_Animals\Bee', WORK):
    if p not in sys.path: sys.path.insert(0, p)
import bpy
from mathutils import Vector, Matrix
import animal_render as rn, animal_export as ax
import build_butterfly as bm_
import butterfly_clips as bc
import rig_bee as rb                      # read-only reuse: export_nla, reimport_check (Bee helpers, bc swapped below)
for m in (bm_, bc): importlib.reload(m)
rb.bc = bc                                # reimport_check uses bc.assign -> same signature here

RIG_OBJECT = 'Rig'

# ---------------- species table (Butterfly) ----------------
_e_out, _e_up, _n = bm_.wing_frame(bm_.WING_TILT)
SPECIES = dict(
    id='INS-02', species='Butterfly', asset=bm_.ASSET, skeleton='I',
    bones=[('Root', None), ('Body', 'Root'), ('Head', 'Body'), ('Antenna.L', 'Head'), ('Antenna.R', 'Head'),
           ('WingFront.L', 'Body'), ('WingBack.L', 'Body'), ('WingFront.R', 'Body'), ('WingBack.R', 'Body'),
           ('Leg_1.L', 'Body'), ('Leg_2.L', 'Body'), ('Leg_3.L', 'Body'), ('Leg_1.R', 'Body'), ('Leg_2.R', 'Body'), ('Leg_3.R', 'Body')],
    bind={'Eye.L': 'Head', 'Eye.R': 'Head'},
    tails={'Root': (0, -0.030, 0), 'Body': (0, -0.015, 0), 'Head': 'face', 'Antenna': 'far', 'Wing': 'far', 'Leg': 'far'},
    limits={'Body': 25, 'Head': 30, 'Antenna': 35, 'WingFront': 125, 'WingBack': 125, 'Leg': 40},
    clips=[('Fly', 1.0, True), ('Perch_Idle', 4.0, True)],
    # wing closing rotation: forewing frame (out, up, normal) -> (close_dir, ., close_normal); see butterfly_clips.Wings
    wing=dict(frame=(tuple(_e_out), tuple(_e_up), tuple(_n)), close_dir=(0.0, 0.62, 0.78), close_normal=(1.0, 0.0, 0.0)),
    fly=dict(flaps=2, k_mid=0.37, k_amp=0.45, hover=0.06, drift=0.006, bob=0.007, pitch=-6.0, pitch_amp=3.0, roll=2.0,
             leg_back=(25.0, 30.0, 34.0), leg_tuck=(8.0, 8.0, 6.0), leg_swing=3.0, head_nod=3.0, ant_trail=8.0, ant_amp=5.0),
    perch=dict(k_open=0.0, k_closed=0.82, close_window=(0.10, 0.40, 0.62, 0.92), tremble=0.025, tremble_cycles=6,
               head_yaw=6.0, head_nod=3.0, ant_pitch=9.0, ant_yaw=7.0),
)
SP = SPECIES
ASSET = SP['asset']; ART = bm_.ART
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_butterfly_rig')
os.makedirs(CHECK, exist_ok=True)


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['INS-02', 'bend'])[:2]


def bone_of(part):
    return SP['bind'].get(part, part)


def bone_heads_tails(obs):
    out = {}
    for n, par in SP['bones']:
        key = n if n in SP['tails'] else n.split('.')[0].split('_')[0]
        if key.startswith('Wing'): key = 'Wing'
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
    """copy of rig_bee.build_armature (roll rule: sagittal bones local X = world X, lateral bones local Z = world up)"""
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
    print(f'RIG bones {len(names)} hierarchy_ok {par_ok} parts bound {len(B["obs"])} (rigid 1.0) tris {B["total"]}')
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


def wing_pose(W, WG, k):
    d = {}
    for s in (1.0, -1.0): WG.pair(d, s, k)
    return W.pose(d)


def bend_poses(W, WG):
    P = [wing_pose(W, WG, k) for k in (-0.15, 0.3, 0.6, 1.0)]
    legs = {}
    for n in ('Leg_1', 'Leg_2', 'Leg_3'):
        legs[n + '.L'] = W.rot_axis(n + '.L', (1, 0, 0), 40); legs[n + '.R'] = W.rot_axis(n + '.R', (1, 0, 0), -40)
    P.append(W.pose(legs))
    P.append(W.pose({'Head': W.rot_axis('Head', (0, 0, 1), 30), 'Antenna.L': W.rot_axis('Antenna.L', (1, 0, 0), -35),
                     'Antenna.R': W.rot_axis('Antenna.R', (1, 0, 0), 35)}))
    P.append(W.pose({'Head': W.rot_axis('Head', (1, 0, 0), 30)}))
    P.append(W.pose({'Body': W.rot_axis('Body', (1, 0, 0), -25)}))
    return P


# ---------------- clips ----------------
def anim(B):
    rig = B['rig']; clips, W, WG = bc.build_clips(rig, SP)
    acts = {c: bc.write_action(rig, f"{SP['species']}_{c}", clips[c]['frames'], loop) for c, _, loop in SP['clips']}
    rep = bc.metrics(B['sc'], rig, B['obs'], clips, acts, SP)
    return clips, acts, rep


def clip_strips(B, acts):
    sc = B['sc']; rig = B['rig']
    for c, _, _ in SP['clips']:
        act = acts[c]; N = int(act.frame_end)
        fr = [round(i * N / 8) for i in range(8)] if c != 'Fly' else [round(i * 15 / 8) for i in range(8)]
        bc.assign(rig, act)
        setters = [(lambda f=f: (sc.frame_set(f), bpy.context.view_layer.update())) for f in fr]
        strip(B, setters, os.path.join(CHECK, f'Butterfly_strip_{c}.png'), (1.0, -0.55, 0.25))
        strip(B, setters, os.path.join(CHECK, f'Butterfly_strip_{c}_side.png'), (1.0, 0.0, 0.10))
    bc.assign(rig, None); sc.frame_set(0)


def events_json(path):
    F = SP['fly']; N = int(round(SP['clips'][0][1] * bc.FPS))
    ev = [dict(name='WingFlap', frame=int(round(i * N / F['flaps'])), time=round(i * N / F['flaps'] / bc.FPS, 4), stringParameter='Down')
          for i in range(F['flaps'])]
    d = dict(species='Butterfly', asset=ASSET, fps=bc.FPS, note='Unity AnimationEvents to add on import (FBX does not carry them)',
             clips={'Fly': dict(take='Butterfly_Fly', seconds=1.0, last_frame=N, loop=True, hover_m=F['hover'], events=ev),
                    'Perch_Idle': dict(take='Butterfly_Perch_Idle', seconds=4.0, last_frame=120, loop=True, events=[])})
    json.dump(d, open(path, 'w'), indent=1); print('events', path)


if __name__ == '__main__':
    ID, CMD = args()
    print('=== INS-02 Butterfly rig', CMD)
    if CMD == 'probe':
        B = rig_model(os.path.join(CHECK, 'tex')); W = bc.World(B['rig']); WG = bc.Wings(W, SP)
        pairs = bc.overlap_pairs(B['obs']); W.apply(wing_pose(W, WG, 0.0)); base = bc._overlaps(B['obs'], pairs)
        print('rest overlaps', {k: v for k, v in base.items() if v})
        for k in (-0.2, -0.1, 0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 1.0, 1.05):
            W.apply(wing_pose(W, WG, k)); ov = bc._overlaps(B['obs'], pairs)
            new = {a: v - base[a] for a, v in ov.items() if v > base[a]}
            minz = min((o.matrix_world @ v.co).z for o in [B['obs'][n] for n in B['obs'] if n.startswith('Wing')]
                       for v in o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh().vertices)
            print(f'k {k:5.2f} new overlaps {new}')
    elif CMD == 'bend':
        B = rig_model(os.path.join(CHECK, 'tex')); W = bc.World(B['rig']); WG = bc.Wings(W, SP); poses = bend_poses(W, WG)
        setters = [(lambda p=p: W.apply(p)) for p in poses]
        strip(B, setters, os.path.join(CHECK, 'Butterfly_bend_34.png'), (1.0, -0.55, 0.3))
        strip(B, setters, os.path.join(CHECK, 'Butterfly_bend_side.png'), (1.0, 0.0, 0.1))
    elif CMD == 'anim':
        B = rig_model(os.path.join(CHECK, 'tex')); clips, acts, rep = anim(B)
        json.dump(rep, open(os.path.join(WORK, 'metrics_report.json'), 'w'), indent=1)
        clip_strips(B, acts)
    elif CMD == 'export':
        B = rig_model(os.path.join(ART, 'Textures')); clips, acts, rep = anim(B)
        parts = list(B['obs'].values()); al = [acts[c] for c, _, _ in SP['clips']]
        fbx = os.path.join(ART, 'Meshes', ASSET + '.fbx')
        rb.export_nla(B['rig'], parts, al, fbx)
        summ = ax.fbx_summary(fbx)
        X = rb.reimport_check(fbx, B['rig'], parts, al)
        events_json(os.path.join(ART, 'Meshes', ASSET + '.events.json'))
        coll = B['coll']
        data = {coll} | set(coll.objects) | {o.data for o in coll.objects if o.data} | {B['mat'], B['img']} | set(al)
        bpy.data.libraries.write(os.path.join(ART, 'Blend', ASSET + '.blend'), data, fake_user=True, path_remap='ABSOLUTE')
        print('blend', os.path.join(ART, 'Blend', ASSET + '.blend'), 'objects', len(coll.objects), 'actions', [a.name for a in al])
        full = dict(asset=ASSET, tris=B['total'], bones=len(B['rig'].data.bones), rig=B['rig_checks'], clips=rep,
                    export=dict(fbx=fbx, takes=[(s['name'], s['frames30']) for s in summ['stacks']], limbs=summ['limb_nodes'],
                                roots=summ['roots'], reimport=X))
        json.dump(full, open(os.path.join(WORK, 'metrics_report.json'), 'w'), indent=1, default=str)
        print('report', os.path.join(WORK, 'metrics_report.json'))
