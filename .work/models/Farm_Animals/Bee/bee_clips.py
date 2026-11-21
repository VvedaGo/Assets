# bee_clips.py - insect clip toolkit (skeleton I, rigid parts) + the Bee clips Fly / On_Flower (planning/FarmAnimals/ANIMATIONS.md).
# Reusable for every skeleton-I insect: all numbers come from the species table (rig_bee.SPECIES['fly'|'flower']).
# Poses are written as rotations about ARMATURE-space axes through the bone head (World.rot_axis) and converted to the
# bone's local euler (R_local = Rest^T R Rest), so wing flap = rotation about the body axis Y, leg lift = about Y, pitch =
# about X, whatever the bone roll. All periodic terms have an integer number of cycles per clip -> loops close exactly.
import math
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from bpy_extras import anim_utils

FPS = 30
TW = 2 * math.pi
R = math.radians


def assign(rig, act):
    ad = rig.animation_data or rig.animation_data_create(); ad.action = act
    if act is not None and getattr(act, 'slots', None) and len(act.slots): ad.action_slot = act.slots[0]
    if act is None:
        for pb in rig.pose.bones: pb.location = (0, 0, 0); pb.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()


class World:
    """armature-space pose helper: rest frames per bone; pose({bone: R | (loc, R)}) -> {bone: [loc_local, euler_local]}"""
    def __init__(self, rig):
        self.rig = rig; self.names = [b.name for b in rig.data.bones]
        self.rest = {b.name: b.matrix_local.to_3x3() for b in rig.data.bones}

    def rot_axis(self, bone, axis, deg):
        return Matrix.Rotation(R(deg), 3, Vector(axis).normalized())

    def axis(self, bone, i):
        return self.rest[bone].col[i].copy()

    def pose(self, d):
        out = {}
        for n in self.names:
            v = d.get(n); loc = Vector((0, 0, 0)); Rm = Matrix.Identity(3)
            if isinstance(v, tuple): loc, Rm = Vector(v[0]), v[1]
            elif v is not None: Rm = v
            Mb = self.rest[n]
            out[n] = [list(Mb.transposed() @ loc), list((Mb.transposed() @ Rm @ Mb).to_euler('XYZ'))]
        return out

    def apply(self, p):
        for n, (l, r) in p.items():
            pb = self.rig.pose.bones[n]; pb.location = l; pb.rotation_euler = r
        bpy.context.view_layer.update()


def side(n):
    return 1.0 if n.endswith('.L') else -1.0


# ---------------- clips ----------------
def fly_frame(W, S, t):
    F = S['fly']; ph = TW * F['flaps_per_s'] * t; slow = TW * t; Y_, X_, Z_ = (0, 1, 0), (1, 0, 0), (0, 0, 1)
    d = {'Root': ((0, 0, F['hover']), Matrix.Identity(3))}
    d['Body'] = ((0, 0, F['bob'] * math.sin(ph) + F['bob_slow'] * math.sin(slow)),
                 W.rot_axis('Body', X_, F['pitch'] + F['pitch_amp'] * math.sin(slow)))
    for n in W.names:
        if not n.startswith('Wing'): continue
        s = side(n); hind = n.startswith('WingBack')
        p = ph - (TW * F['hind_lag'] if hind else 0.0); k = F['hind_amp'] if hind else 1.0
        down = (F['hind_mid'] if hind else F['flap_mid']) + k * F['flap_amp'] * math.cos(p)                 # + = wing down (deg)
        feather = s * k * F['feather'] * math.sin(p)
        d[n] = W.rot_axis(n, Y_, s * down) @ Matrix.Rotation(R(feather), 3, W.axis(n, 1))
    for i, n in enumerate(sorted(x for x in W.names if x.startswith('Leg'))):
        s = side(n); k = int(n[4])
        sw = F['leg_swing'] * math.sin(slow + 0.8 * k + (0.4 if s < 0 else 0.0))
        d[n] = W.rot_axis(n, X_, F['leg_back'][k - 1] + sw) @ W.rot_axis(n, Y_, s * F['leg_hang'][k - 1])
    d['Abdomen'] = W.rot_axis('Abdomen', X_, F['abd_pitch'] * math.sin(slow - 0.6)) @ W.rot_axis('Abdomen', Z_, F['abd_yaw'] * math.sin(slow))
    hl = W.axis('Head', 0)
    d['Head'] = Matrix.Rotation(R(F['head_nod'] * math.sin(slow + 0.4)), 3, hl)
    for n in ('Antenna.L', 'Antenna.R'):
        a = -(F['ant_trail'] + F['ant_amp'] * math.sin(2 * slow - 0.9 - (0.5 if n.endswith('.R') else 0.0)))
        d[n] = Matrix.Rotation(R(a), 3, hl)
    return W.pose(d)


def flower_frame(W, S, t, T):
    F = S['flower']; u = t / T; Y_, X_, Z_ = (0, 1, 0), (1, 0, 0), (0, 0, 1)
    d = {}
    for n in W.names:
        if n.startswith('Wing'):
            s = side(n); fold = F['wing_fold'][0 if n.startswith('WingFront') else 1]     # fold back along the body (about X)
            d[n] = W.rot_axis(n, Z_, -s * F['wing_splay'][0 if n.startswith('WingFront') else 1]) @ W.rot_axis(n, X_, fold)
    order = F['order']; L = len(order)
    for i, n in enumerate(order):
        s = side(n); w = ((u - i / L) % 1.0) * L                              # 0..L, the lift window is w in [0, lift_frac)
        lift = reach = 0.0
        if w < F['lift_frac']:
            v = math.sin(math.pi * w / F['lift_frac']); lift = F['lift'] * v; reach = F['reach'] * v
        d[n] = W.rot_axis(n, Z_, -s * reach) @ W.rot_axis(n, Y_, -s * lift)   # reach forward, lift the foot (L: -Y)
    d['Abdomen'] = W.rot_axis('Abdomen', X_, F['abd_pump'] * math.sin(TW * F['pumps'] * u))
    hl = W.axis('Head', 0)
    d['Head'] = W.rot_axis('Head', Z_, F['head_yaw'] * math.sin(TW * u)) @ Matrix.Rotation(R(F['head_nod'] * math.sin(TW * 2 * u + 0.7)), 3, hl)
    for n in ('Antenna.L', 'Antenna.R'):
        o = 0.0 if n.endswith('.L') else 1.3
        d[n] = Matrix.Rotation(R(F['ant_pitch'] * math.sin(TW * 3 * u + o)), 3, hl) @ W.rot_axis(n, Z_, F['ant_yaw'] * math.sin(TW * 2 * u + o))
    return W.pose(d)


def build_clips(rig, S):
    W = World(rig); out = {}
    for name, T, loop in S['clips']:
        N = int(round(T * FPS))
        fn = (lambda t: fly_frame(W, S, t)) if name == 'Fly' else (lambda t, T=T: flower_frame(W, S, t, T))
        out[name] = dict(frames=[fn(f / FPS) for f in range(N + 1)], loop=loop, T=T)
    return out


def write_action(rig, name, frames, loop):
    old = bpy.data.actions.get(name)
    if old: bpy.data.actions.remove(old)
    act = bpy.data.actions.new(name); act.use_fake_user = True
    slot = act.slots.new(id_type='OBJECT', name=rig.name)
    cb = anim_utils.action_ensure_channelbag_for_slot(act, slot)
    N = len(frames) - 1
    for b in frames[0]:
        for path, ix in (('location', 0), ('rotation_euler', 1)):
            for i in range(3):
                fc = cb.fcurves.new(f'pose.bones["{b}"].{path}', index=i, group_name=b)
                fc.keyframe_points.add(N + 1); co = []
                for f, p in enumerate(frames): co += [float(f), p[b][ix][i]]
                fc.keyframe_points.foreach_set('co', co)
                fc.keyframe_points.foreach_set('interpolation', [1] * (N + 1))
                fc.update()
    act.use_frame_range = True; act.frame_start = 0; act.frame_end = N; act.use_cyclic = loop
    return act


# ---------------- metrics ----------------
def _world_mesh(o, dg):
    oe = o.evaluated_get(dg); me = oe.to_mesh()
    V = [o.matrix_world @ v.co for v in me.vertices]; P = [list(p.vertices) for p in me.polygons]
    oe.to_mesh_clear()
    return V, P


def _overlaps(obs, pairs):
    dg = bpy.context.evaluated_depsgraph_get(); T = {}
    for n in {x for p in pairs for x in p}:
        V, P = _world_mesh(obs[n], dg); T[n] = (BVHTree.FromPolygons(V, P), V)
    return {f'{a}/{b}': len(T[a][0].overlap(T[b][0])) for a, b in pairs}


def metrics(sc, rig, obs, clips, acts, S):
    legs = sorted(n for n in obs if n.startswith('Leg'))
    pairs = [(w, b) for w in obs if w.startswith('Wing') for b in ('Abdomen', 'Head')] + \
            [(w, v) for w in obs if w.startswith('WingFront') for v in obs if v.startswith('WingBack') and v[-2:] == w[-2:]] + \
            [(l, 'Abdomen') for l in legs] + [('WingFront.L', 'WingFront.R'), ('WingBack.L', 'WingBack.R')]
    assign(rig, None); base = _overlaps(obs, pairs)
    rep = {'rest_overlap_face_pairs': {k: v for k, v in base.items() if v}}
    for name, C in clips.items():
        act = acts[name]; assign(rig, act); N = int(act.frame_end)
        r = dict(frames=N + 1, seconds=round(N / FPS, 3), loop=C['loop'])
        cb = anim_utils.action_get_channelbag_for_slot(act, act.slots[0]); wr = wl = 0.0
        for fc in cb.fcurves:
            dv = abs(fc.evaluate(0) - fc.evaluate(N))
            if fc.data_path.endswith('rotation_euler'): wr = max(wr, math.degrees(dv))
            else: wl = max(wl, dv)
        r['loop_closure_deg'] = round(wr, 6); r['loop_closure_loc_m'] = round(wl, 6)
        # joint ranges: largest rotation angle of every bone away from rest vs limits
        ang = {}
        for fr in C['frames']:
            for b, (l, e) in fr.items():
                from mathutils import Euler
                a = math.degrees(Euler(e, 'XYZ').to_quaternion().angle); ang[b] = max(ang.get(b, 0.0), a)
        viol = []
        for b, a in ang.items():
            key = next((k for k in S['limits'] if b.startswith(k)), None)
            if key and a > S['limits'][key] + 0.01: viol.append(f'{b} {a:.1f} > {S["limits"][key]}')
        r['max_rotation_deg'] = {b: round(a, 1) for b, a in sorted(ang.items()) if a > 0.05}
        r['limit_violations'] = viol
        dg = None; minz = 1e9; legz = {l: [] for l in legs}; worst_new = {}
        for f in range(N + 1):
            sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get()
            for n, o in obs.items():
                V, _ = _world_mesh(o, dg); z = min(v.z for v in V); minz = min(minz, z)
                if n in legz: legz[n].append(z)
            if f % 2 == 0:
                ov = _overlaps(obs, pairs)
                for k, v in ov.items():
                    if v > base[k]: worst_new[k] = max(worst_new.get(k, 0), v - base[k])
        r['lowest_vertex_m'] = round(minz, 4)
        r['new_overlap_face_pairs_vs_rest'] = worst_new
        if name == 'On_Flower':
            contact = [sum(1 for l in legs if legz[l][f] < 0.0008) for f in range(N + 1)]
            r['legs_on_flower_min'] = min(contact); r['legs_on_flower_max'] = max(contact)
            r['leg_below_flower_m'] = round(min(min(v) for v in legz.values()), 5)
            r['max_foot_lift_m'] = round(max(max(v) for v in legz.values()), 4)
        else:
            r['feet_min_height_m'] = round(min(min(v) for v in legz.values()), 4)
        rep[name] = r
        print(f"METRIC {name:9s} N={N:3d} closure={r['loop_closure_deg']}deg/{r['loop_closure_loc_m']}m lowest={r['lowest_vertex_m']} "
              f"flower={r.get('legs_on_flower_min', '-')}..{r.get('legs_on_flower_max', '-')} below={r.get('leg_below_flower_m', '-')} "
              f"lift={r.get('max_foot_lift_m', '-')} feet={r.get('feet_min_height_m', '-')} viol={viol} newoverlap={worst_new}")
        print('   max rot', r['max_rotation_deg'])
    assign(rig, None); sc.frame_set(0)
    print('   rest overlaps', rep['rest_overlap_face_pairs'])
    return rep
