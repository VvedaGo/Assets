# butterfly_clips.py - INS-02 Butterfly clips Fly / Perch_Idle (planning/FarmAnimals/ANIMATIONS.md). Copy of Bee/bee_clips.py
# (insect toolkit, skeleton I, rigid parts) with butterfly wing kinematics:
#  - the wing plates are FRONTAL (plane = out (X) x up-tilted-back), so a flap about the body axis would spin them in their
#    own plane. A wing "closes" by the rotation R_close that maps the forewing frame (out, up, normal) to
#    (up-back c1, forward-up c2, +-X): the plate ends in the sagittal plane, forewing up, hindwing back (resting butterfly).
#    Open <-> closed = the same axis, angle k * |R_close| (quaternion axis-angle), k = closing fraction.
#  - fore- and hindwing of one side move as ONE rigid pair (hindwing rotated about the forewing pivot: loc = (I-R)(Qf-Hh)),
#    so the 5.5 mm plate gap never closes.
# Poses are written as rotations about armature-space axes through the bone head (R_local = Rest^T R Rest), eulers kept
# continuous frame to frame (compat). All periodic terms have whole cycles per clip -> exact loops.
import math
import bpy
from mathutils import Matrix, Vector, Quaternion, Euler
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
        self.head = {b.name: b.head_local.copy() for b in rig.data.bones}

    def rot_axis(self, bone, axis, deg):
        return Matrix.Rotation(R(deg), 3, Vector(axis).normalized())

    def axis(self, bone, i):
        return self.rest[bone].col[i].copy()

    def pose(self, d, prev=None):
        out = {}
        for n in self.names:
            v = d.get(n); loc = Vector((0, 0, 0)); Rm = Matrix.Identity(3)
            if isinstance(v, tuple): loc, Rm = Vector(v[0]), v[1]
            elif v is not None: Rm = v
            Mb = self.rest[n]; Rl = Mb.transposed() @ Rm @ Mb
            e = Rl.to_euler('XYZ', Euler(prev[n][1], 'XYZ')) if prev else Rl.to_euler('XYZ')
            out[n] = [list(Mb.transposed() @ loc), list(e)]
        return out

    def apply(self, p):
        for n, (l, r) in p.items():
            pb = self.rig.pose.bones[n]; pb.location = l; pb.rotation_euler = r
        bpy.context.view_layer.update()


def side(n):
    return 1.0 if n.endswith('.L') else -1.0


MIRX = Matrix(((-1, 0, 0), (0, 1, 0), (0, 0, 1)))


class Wings:
    """closing rotation of the left wing pair (forewing frame -> sagittal resting frame) + mirrored right pair"""
    def __init__(self, W, S):
        F = S['wing']; e_out, e_up, n = [Vector(v) for v in F['frame']]
        A = Matrix((e_out, e_up, n)).transposed()                  # columns = rest frame
        c1 = Vector(F['close_dir']).normalized(); nx = Vector(F['close_normal']).normalized()
        c2 = nx.cross(c1).normalized(); c1 = c2.cross(nx).normalized()
        Bm = Matrix((c1, c2, nx)).transposed()
        Rc = Bm @ A.transposed()
        q = Rc.to_quaternion(); self.axis_L, self.ang = q.axis.copy(), q.angle
        self.W = W; self.S = S
        print(f'WINGS close rotation L: axis {tuple(round(c, 3) for c in self.axis_L)} angle {math.degrees(self.ang):.1f} deg')

    def rot(self, s, k, extra=None):
        Rl = Quaternion(self.axis_L, self.ang * k).to_matrix()
        if extra is not None: Rl = extra @ Rl
        return Rl if s > 0 else MIRX @ Rl @ MIRX

    def pair(self, d, s, k, extra=None):
        sfx = '.L' if s > 0 else '.R'; Rm = self.rot(s, k, extra)
        Qf = self.W.head['WingFront' + sfx]; Hh = self.W.head['WingBack' + sfx]
        d['WingFront' + sfx] = Rm
        d['WingBack' + sfx] = (tuple((Matrix.Identity(3) - Rm) @ (Qf - Hh)), Rm)


# ---------------- clips ----------------
def fly_frame(W, WG, S, t, T):
    F = S['fly']; u = t / T; ph = TW * F['flaps'] * u; slow = TW * u; X_, Y_, Z_ = (1, 0, 0), (0, 1, 0), (0, 0, 1)
    k = F['k_mid'] - F['k_amp'] * math.cos(ph)                  # ph = 0: wings closed above (top of the stroke)
    d = {'Root': ((0, 0, F['hover'] + F['drift'] * math.sin(slow)), Matrix.Identity(3))}
    d['Body'] = ((0, 0, -F['bob'] * math.cos(ph - 0.5)),
                 W.rot_axis('Body', X_, F['pitch'] + F['pitch_amp'] * math.sin(ph - 0.3)) @ W.rot_axis('Body', Y_, F['roll'] * math.sin(slow)))
    for s in (1.0, -1.0):
        WG.pair(d, s, k)
    for n in W.names:
        if not n.startswith('Leg'): continue
        s = side(n); i = int(n[4])
        sw = F['leg_swing'] * math.sin(slow + 0.8 * i + (0.4 if s < 0 else 0.0))
        d[n] = W.rot_axis(n, X_, F['leg_back'][i - 1] + sw) @ W.rot_axis(n, Y_, s * F['leg_tuck'][i - 1])
    hl = W.axis('Head', 0)
    d['Head'] = Matrix.Rotation(R(F['head_nod'] * math.sin(ph + 1.0)), 3, hl)
    for n in ('Antenna.L', 'Antenna.R'):
        a = -(F['ant_trail'] + F['ant_amp'] * math.sin(ph - 0.9 - (0.3 if n.endswith('.R') else 0.0)))
        d[n] = Matrix.Rotation(R(a), 3, hl)
    return d


def smooth(x):
    x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)


def perch_k(u, P):
    """closing fraction over the loop: open hold, slow close, closed hold, slow open (C1-continuous, periodic)"""
    a, b, c, e = P['close_window']
    if u < a: return 0.0
    if u < b: return smooth((u - a) / (b - a))
    if u < c: return 1.0
    if u < e: return 1.0 - smooth((u - c) / (e - c))
    return 0.0


def perch_frame(W, WG, S, t, T):
    P = S['perch']; u = t / T; X_, Z_ = (1, 0, 0), (0, 0, 1)
    k = perch_k(u, P) * P['k_closed'] + P['k_open']
    tr = P['tremble'] * math.sin(TW * P['tremble_cycles'] * u) * perch_k(u, P)
    d = {}
    for s in (1.0, -1.0):
        WG.pair(d, s, k + tr)
    hl = W.axis('Head', 0)
    d['Head'] = W.rot_axis('Head', Z_, P['head_yaw'] * math.sin(TW * u)) @ Matrix.Rotation(R(P['head_nod'] * math.sin(TW * 2 * u + 0.7)), 3, hl)
    for n in ('Antenna.L', 'Antenna.R'):
        o = 0.0 if n.endswith('.L') else 1.3
        d[n] = Matrix.Rotation(R(P['ant_pitch'] * math.sin(TW * 3 * u + o)), 3, hl) @ W.rot_axis(n, Z_, P['ant_yaw'] * math.sin(TW * 2 * u + o))
    return d


def build_clips(rig, S):
    W = World(rig); WG = Wings(W, S); out = {}
    for name, T, loop in S['clips']:
        N = int(round(T * FPS)); fr = []; prev = None
        for f in range(N + 1):
            d = fly_frame(W, WG, S, f / FPS, T) if name == 'Fly' else perch_frame(W, WG, S, f / FPS, T)
            p = W.pose(d, prev); fr.append(p); prev = p
        out[name] = dict(frames=fr, loop=loop, T=T)
    return out, W, WG


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


def overlap_pairs(obs):
    wings = sorted(n for n in obs if n.startswith('Wing')); legs = sorted(n for n in obs if n.startswith('Leg'))
    pairs = [(w, b) for w in wings for b in ('Body', 'Head', 'Antenna.L', 'Antenna.R')]
    pairs += [(a, b) for a in wings for b in wings if a < b]
    pairs += [(w, l) for w in wings for l in legs if w[-2:] == l[-2:]]
    return pairs


def metrics(sc, rig, obs, clips, acts, S):
    legs = sorted(n for n in obs if n.startswith('Leg'))
    pairs = overlap_pairs(obs)
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
        # euler continuity: largest per-frame jump of any rotation channel (a wrap would show as ~360)
        jump = 0.0
        for fc in cb.fcurves:
            if fc.data_path.endswith('rotation_euler'):
                vals = [fc.evaluate(f) for f in range(N + 1)]
                jump = max(jump, max(abs(a - b) for a, b in zip(vals, vals[1:])))
        r['max_euler_step_deg'] = round(math.degrees(jump), 2)
        ang = {}
        for fr in C['frames']:
            for b, (l, e) in fr.items():
                a = math.degrees(Euler(e, 'XYZ').to_quaternion().angle); ang[b] = max(ang.get(b, 0.0), a)
        viol = []
        for b, a in ang.items():
            key = next((k for k in S['limits'] if b.startswith(k)), None)
            if key and a > S['limits'][key] + 0.01: viol.append(f'{b} {a:.1f} > {S["limits"][key]}')
        r['max_rotation_deg'] = {b: round(a, 1) for b, a in sorted(ang.items()) if a > 0.05}
        r['limit_violations'] = viol
        minz = 1e9; legz = {l: [] for l in legs}; worst_new = {}; feet0 = None; slip = 0.0
        for f in range(N + 1):
            sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get()
            fz = {}
            for n, o in obs.items():
                V, _ = _world_mesh(o, dg); z = min(v.z for v in V); minz = min(minz, z)
                if n in legz:
                    legz[n].append(z); lo = min(V, key=lambda v: v.z); fz[n] = lo
            if name == 'Perch_Idle':
                if feet0 is None: feet0 = fz
                slip = max(slip, max((fz[l] - feet0[l]).length for l in legs))
            if f % 2 == 0:
                ov = _overlaps(obs, pairs)
                for k, v in ov.items():
                    if v > base[k]: worst_new[k] = max(worst_new.get(k, 0), v - base[k])
        r['lowest_vertex_m'] = round(minz, 4)
        r['new_overlap_face_pairs_vs_rest'] = worst_new
        if name == 'Perch_Idle':
            r['feet_on_ground_min'] = min(sum(1 for l in legs if legz[l][f] < 0.0005) for f in range(N + 1))
            r['foot_slip_m'] = round(slip, 6)
        else:
            r['feet_min_height_m'] = round(min(min(v) for v in legz.values()), 4)
        rep[name] = r
        print(f"METRIC {name:10s} N={N:3d} closure={r['loop_closure_deg']}deg/{r['loop_closure_loc_m']}m lowest={r['lowest_vertex_m']} "
              f"feet={r.get('feet_min_height_m', '-')} on_ground={r.get('feet_on_ground_min', '-')} slip={r.get('foot_slip_m', '-')} "
              f"eulerstep={r['max_euler_step_deg']} viol={viol} newoverlap={worst_new}")
        print('   max rot', r['max_rotation_deg'])
    assign(rig, None); sc.frame_set(0)
    print('   rest overlaps', rep['rest_overlap_face_pairs'])
    return rep
