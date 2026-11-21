# ladybug_clips.py - INS-03 Ladybug clips (ANIMATIONS.md: Idle "moves antennae", Crawl "crawls", Fly "flies with opened
# elytra"). Insect toolkit copied from ../Bee/bee_clips.py (assign, World, write_action, overlap helpers, metrics adapted):
# poses are rotations about ARMATURE-space axes through the bone head (World.rot_axis) converted to the local euler.
# Legs are ONE rigid part each (hip -> knee -> foot): Crawl swings them about the vertical axis through the hip (yaw)
# + a lift rotation in the swing; the small radial error of a pure yaw (the sole would run on an arc) is cancelled by a
# sub-millimetre bone translation (hip ball stays inside the body), so stance soles run on a straight line at speed.
# Fly: elytra open as hard shells about their hinge (outer edge up, rear up, rear out), the folded hind wings unfold
# sideways from under them and flap about the body axis; legs tucked, body nose-up, hovering.
import math
import bpy
from mathutils import Matrix, Vector, Euler
from mathutils.bvhtree import BVHTree
from bpy_extras import anim_utils

FPS = 30
TW = 2 * math.pi
R = math.radians
X_, Y_, Z_ = (1, 0, 0), (0, 1, 0), (0, 0, 1)
LEGS = ['Leg_1.L', 'Leg_2.L', 'Leg_3.L', 'Leg_1.R', 'Leg_2.R', 'Leg_3.R']
TRIPOD_A = ('Leg_1.L', 'Leg_2.R', 'Leg_3.L')      # tripod gait: A swings while B stands, then the other way round


def assign(rig, act):
    ad = rig.animation_data or rig.animation_data_create(); ad.action = act
    if act is not None and getattr(act, 'slots', None) and len(act.slots): ad.action_slot = act.slots[0]
    if act is None:
        for pb in rig.pose.bones: pb.location = (0, 0, 0); pb.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()


class World:
    """armature-space pose helper (copy of bee_clips.World): pose({bone: R | (loc, R)}) -> {bone: [loc_local, euler_local]}"""
    def __init__(self, rig):
        self.rig = rig; self.names = [b.name for b in rig.data.bones]
        self.rest = {b.name: b.matrix_local.to_3x3() for b in rig.data.bones}
        self.head = {b.name: b.head_local.copy() for b in rig.data.bones}

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


def smooth(x):
    x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)


# ---------------- legs ----------------
def leg_solve(W, n, F0, target):
    """rigid leg n: the smallest rotation about the hip that points the hip->sole line at the target, plus a translation
    along that line for the length difference (hip ball slides in/out of the body by < 2 mm), so the sole contact point
    F0 (rest, body space) lands exactly on target (body space). Returns (loc, R, shift)."""
    H = W.head[n]; v0 = F0 - H; vt = target - H
    Rm = v0.rotation_difference(vt).to_matrix()
    d = vt - Rm @ v0
    return d, Rm, d.length


def body_delta(W, loc, Rm):
    H = W.head['Body']
    return lambda p: H + Rm @ (p - H) + loc, lambda p: H + Rm.transposed() @ (p - loc - H)


# ---------------- clips ----------------
def idle_frame(W, S, F0, t, T):
    """standing still, feet planted (legs untouched); antennae sweep and flick independently, head turns/nods a little,
    body breathes (tiny pitch), elytra tighten once"""
    I = S['idle']; u = t / T; d = {}
    d['Body'] = W.rot_axis('Body', X_, I['breath'] * math.sin(TW * 2 * u))
    hl = W.axis('Head', 0)
    d['Head'] = W.rot_axis('Head', Z_, I['head_yaw'] * math.sin(TW * u)) @ Matrix.Rotation(R(I['head_nod'] * math.sin(TW * 2 * u + 0.7)), 3, hl)
    for n in ('Antenna.L', 'Antenna.R'):
        s = side(n); o = 0.0 if s > 0 else 1.9
        flick = math.exp(-((((u - (0.30 if s > 0 else 0.68)) + 0.5) % 1.0 - 0.5) / 0.035) ** 2)
        pitch = I['ant_pitch'] * math.sin(TW * 2 * u + o) - I['ant_flick'] * flick
        yaw = s * (I['ant_yaw'] * math.sin(TW * u + o) + 0.5 * I['ant_yaw'] * math.sin(TW * 3 * u + 2 * o))
        d[n] = Matrix.Rotation(R(pitch), 3, hl) @ W.rot_axis(n, Z_, yaw)
    # body breathing moves the hips: re-plant every foot exactly (body space target = inverse body delta of the rest spot)
    fw, inv = body_delta(W, Vector(), d['Body'])
    for n in LEGS:
        loc, Rm, _ = leg_solve(W, n, F0[n], inv(F0[n]))
        d[n] = (loc, Rm)
    return W.pose(d)


def crawl_frame(W, S, F0, t, T):
    C = S['crawl']; u = (t / T) % 1.0; d = {}; v = C['step'] / (C['duty'] * T)
    bob = C['bob'] * math.cos(2 * TW * u); roll = C['roll'] * math.sin(TW * u); yaw = C['yaw'] * math.sin(TW * u)
    Rb = W.rot_axis('Body', Z_, yaw) @ W.rot_axis('Body', Y_, roll) @ W.rot_axis('Body', X_, C['pitch'])
    lb = Vector((0, 0, bob))
    d['Body'] = (lb, Rb)
    fw, inv = body_delta(W, lb, Rb)
    info = {}
    for n in LEGS:
        ph = (u - (0.0 if n in TRIPOD_A else 0.5)) % 1.0
        G = F0[n]; S_ = C['step']
        if ph < C['duty']:                                   # stance: sole on the ground, moving back at speed
            y = G.y - S_ / 2 + S_ * ph / C['duty']; tgt = Vector((G.x, y, G.z)); lift = 0.0; st = True
            loc, Rm, sh = leg_solve(W, n, G, inv(tgt))
        else:                                                # swing: forward arc, lift by rotation
            s = (ph - C['duty']) / (1 - C['duty'])
            y = G.y + S_ / 2 - S_ * (s - math.sin(TW * s) / TW)
            st = False
            tgt = Vector((G.x, y, G.z + C['lift'] * math.sin(math.pi * s) ** 1.2))
            loc, Rm, sh = leg_solve(W, n, G, inv(tgt))
        d[n] = (loc, Rm); info[n] = dict(stance=st, shift=sh)
    hl = W.axis('Head', 0)
    d['Head'] = W.rot_axis('Head', Z_, -0.6 * C['yaw'] * math.sin(TW * u)) @ Matrix.Rotation(R(C['head_nod'] * math.sin(2 * TW * u + 0.5)), 3, hl)
    for n in ('Antenna.L', 'Antenna.R'):
        s = side(n); o = 0.0 if s > 0 else 0.9
        d[n] = Matrix.Rotation(R(-C['ant_fwd'] + C['ant_amp'] * math.sin(2 * TW * u + o)), 3, hl) @ \
            W.rot_axis(n, Z_, s * 0.6 * C['ant_amp'] * math.sin(TW * u + o))
    return W.pose(d), info, v


def fly_frame(W, S, t, T):
    F = S['fly']; u = t / T; ph = TW * F['flaps'] * u; d = {}
    d['Root'] = ((0, 0, F['hover'] + F['bob'] * math.sin(ph) + F['bob_slow'] * math.sin(TW * u)), Matrix.Identity(3))
    d['Body'] = W.rot_axis('Body', Y_, F['roll'] * math.sin(TW * u)) @ W.rot_axis('Body', X_, F['pitch'] + F['pitch_amp'] * math.sin(TW * u))
    for n in ('Elytra.L', 'Elytra.R'):
        s = side(n); tr = F['ely_tremble'] * math.sin(ph + 0.6)
        Rm = W.rot_axis(n, Z_, -s * F['ely_yaw']) @ W.rot_axis(n, X_, F['ely_rear_up']) @ W.rot_axis(n, Y_, -s * (F['ely_open'] + tr))
        d[n] = ((s * F['ely_shift'], 0.0, F['ely_shift'] * 0.5), Rm)          # hinges part a little: split edges stay apart
    for n in ('Wing.L', 'Wing.R'):
        s = side(n)
        up = F['flap_mid'] + F['flap_amp'] * math.cos(ph)              # + = wing tip up
        feather = F['feather'] * math.sin(ph)
        Ru = W.rot_axis(n, Z_, -s * F['unfold'])                       # folded (tip back) -> spread sideways, swept back
        span = (Ru @ Vector((0, 1, 0))).normalized()                    # spread wing direction (from the folded +Y)
        d[n] = W.rot_axis(n, Y_, -s * up) @ Matrix.Rotation(R(feather), 3, span) @ Ru
    for n in LEGS:
        s = side(n); k = int(n[4])
        # sideways legs: fold back about Z, hang down about Y (clear of the flapping wings)
        d[n] = W.rot_axis(n, Z_, s * (F['leg_back'][k - 1] + F['leg_swing'] * math.sin(TW * u + 0.8 * k))) @ \
            W.rot_axis(n, Y_, s * F['leg_hang'])
    hl = W.axis('Head', 0)
    d['Head'] = Matrix.Rotation(R(F['head_nod'] * math.sin(TW * u + 0.4)), 3, hl)
    for n in ('Antenna.L', 'Antenna.R'):
        a = -(F['ant_trail'] + F['ant_amp'] * math.sin(TW * 2 * u - (0.5 if n.endswith('.R') else 0.0)))
        d[n] = Matrix.Rotation(R(a), 3, hl)
    return W.pose(d)


def contact_points(rig, obs):
    """rest contact point of every leg = centre of its sole vertices (z < 0.1 mm), armature space"""
    F0 = {}
    for n in LEGS:
        o = obs[n]; V = [o.matrix_world @ v.co for v in o.data.vertices]
        sole = [p for p in V if p.z < 1e-4]
        F0[n] = sum(sole, Vector()) / len(sole)
    return F0


def build_clips(rig, S, obs):
    W = World(rig); out = {}; F0 = contact_points(rig, obs)
    for name, T, loop in S['clips']:
        N = int(round(T * FPS)); fr = []; ex = {}
        if name == 'Idle':
            fr = [idle_frame(W, S, F0, f / FPS, T) for f in range(N)]
        elif name == 'Crawl':
            infos = []
            for f in range(N):
                p, info, v = crawl_frame(W, S, F0, f / FPS, T); fr.append(p); infos.append(info)
            ex = dict(stance={n: [f for f in range(N) if infos[f][n]['stance']] for n in LEGS}, speed=v, step=S['crawl']['step'], N=N,
                      max_hip_shift_m=round(max(i[n]['shift'] for i in infos for n in LEGS), 5))
        elif name == 'Fly':
            fr = [fly_frame(W, S, f / FPS, T) for f in range(N)]
        fr.append([None])
        fr[-1] = {b: [list(a), list(c)] for b, (a, c) in fr[0].items()}       # exact loop: last = first
        out[name] = dict(frames=fr, loop=loop, T=T, extra=ex, F0=F0)
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


def leg_point(rig, n, F0):
    pb = rig.pose.bones[n]; bn = rig.data.bones[n]
    return rig.matrix_world @ (pb.matrix @ (bn.matrix_local.inverted() @ F0))


def metrics(sc, rig, obs, clips, acts, S):
    pairs = [(l, 'Elytra' + l[-2:]) for l in LEGS] + [(w, e) for w in ('Wing.L', 'Wing.R') for e in ('Elytra.L', 'Elytra.R')] + \
            [('Wing.L', 'Wing.R'), ('Elytra.L', 'Elytra.R')] + [(f'Leg_{i}{s}', f'Leg_{i + 1}{s}') for i in (1, 2) for s in ('.L', '.R')] + \
            [(w, l) for w in ('Wing.L', 'Wing.R') for l in LEGS if l[-2:] == w[-2:]] + [('Wing.L', 'Head'), ('Wing.R', 'Head')]
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
        ang = {}; shift = {}
        for fr in C['frames']:
            for b, (l, e) in fr.items():
                ang[b] = max(ang.get(b, 0.0), math.degrees(Euler(e, 'XYZ').to_quaternion().angle))
                if b.startswith('Leg'): shift[b] = max(shift.get(b, 0.0), Vector(l).length)
        viol = []
        for b, a in ang.items():
            key = next((k for k in S['limits'] if b.startswith(k)), None)
            if key and a > S['limits'][key] + 0.01: viol.append(f'{b} {a:.1f} > {S["limits"][key]}')
        r['max_rotation_deg'] = {b: round(a, 1) for b, a in sorted(ang.items()) if a > 0.05}
        r['max_leg_translation_m'] = round(max(shift.values()), 5) if shift else 0.0
        r['limit_violations'] = viol
        minz = 1e9; worst_new = {}; feet = {n: [] for n in LEGS}
        for f in range(N + 1):
            sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get()
            for n, o in obs.items():
                V, _ = _world_mesh(o, dg); minz = min(minz, min(v.z for v in V))
            for n in LEGS: feet[n].append(leg_point(rig, n, C['F0'][n]))
            if f % 2 == 0:
                ov = _overlaps(obs, pairs)
                for k, v in ov.items():
                    if v > base[k]: worst_new[k] = max(worst_new.get(k, 0), v - base[k])
        r['lowest_vertex_m'] = round(minz, 5)
        r['new_overlap_face_pairs_vs_rest'] = worst_new
        if name == 'Idle':
            r['foot_slip_m'] = round(max((p - C['F0'][n]).length for n in LEGS for p in feet[n]), 6)
        elif name == 'Crawl':
            ex = C['extra']; v = ex['speed']; Sg = ex['step']; slip = 0.0; lift = 0.0
            for n in LEGS:
                fs = ex['stance'][n]; runs = []; cur = [fs[0]]
                for a, b in zip(fs, fs[1:]):
                    if b == a + 1: cur.append(b)
                    else: runs.append(cur); cur = [b]
                runs.append(cur)
                if len(runs) > 1 and runs[-1][-1] == ex['N'] - 1 and runs[0][0] == 0:
                    runs[0] = runs[-1] + [x + ex['N'] for x in runs[0]]; runs.pop()
                for run in runs:
                    p0 = feet[n][run[0] % ex['N']]
                    for fr_ in run:
                        p = feet[n][fr_ % ex['N']]; dt = (fr_ - run[0]) / FPS
                        slip = max(slip, (p - p0 - Vector((0, v * dt, 0))).length); lift = max(lift, abs(p.z))
            r['foot_slip_m'] = round(slip, 6); r['foot_slip_pct_of_step'] = round(100 * slip / Sg, 2)
            r['step_m'] = Sg; r['speed_mps'] = round(v, 4); r['stance_sole_max_height_m'] = round(lift, 5)
            r['max_hip_shift_m'] = ex['max_hip_shift_m']
        else:
            r['feet_min_height_m'] = round(min(p.z for n in LEGS for p in feet[n]), 4)
        rep[name] = r
        print(f"METRIC {name:6s} N={N:3d} closure={r['loop_closure_deg']}deg/{r['loop_closure_loc_m']}m lowest={r['lowest_vertex_m']} "
              f"slip={r.get('foot_slip_m', '-')} ({r.get('foot_slip_pct_of_step', '-')}%) feet={r.get('feet_min_height_m', '-')} "
              f"legshift={r['max_leg_translation_m']} viol={viol} newoverlap={worst_new}")
        print('   max rot', r['max_rotation_deg'])
    assign(rig, None); sc.frame_set(0)
    print('   rest overlaps', rep['rest_overlap_face_pairs'])
    return rep
