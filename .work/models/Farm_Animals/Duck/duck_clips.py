# duck_clips.py - bird clip toolkit (skeleton B) + the Duck clips Idle / Walk / Swim (planning/FarmAnimals/ANIMATIONS.md).
# Copied from ../Hen/hen_clips.py (read-only): toolkit, gait(), write_action(), metrics() unchanged; build_clips() replaced
# (Idle with a bill dip + tail wag bursts, Walk = waddle with a small head bob instead of the hen head-hold, Swim = in-place
# paddle). All numbers in rig_duck.DUCK.
import math
import numpy as np
import bpy
from mathutils import Matrix, Vector, Euler
from bpy_extras import anim_utils
from animal_anim import FPS, R, smooth, new_pose, copy_pose, rot, frames_of, assign

TW = 2 * math.pi


# ---------------- skeleton ----------------
class BirdSkel:
    """FK + linear-blend skinning on a joined mesh (copy of animal_anim.Skel); legs = {key: (upper, lower, foot, knee_fwd)}"""
    def __init__(self, rig, mesh, legs, mover='Body'):
        self.rig = rig; self.legs = legs; self.mover = mover; bones = rig.data.bones; order = []

        def visit(b):
            order.append(b.name)
            for c in b.children: visit(c)
        for b in bones:
            if b.parent is None: visit(b)
        self.order = order
        self.parent = {b.name: (b.parent.name if b.parent else None) for b in bones}
        self.rest = {b.name: b.matrix_local.copy() for b in bones}
        self.rel = {n: (self.rest[p].inverted() @ self.rest[n]) if p else self.rest[n].copy() for n, p in self.parent.items()}
        self.length = {b.name: b.length for b in bones}
        self.idx = {n: i for i, n in enumerate(order)}
        me = mesh.data
        self.V = np.array([tuple(v.co) + (1.0,) for v in me.vertices])
        W = np.zeros((len(me.vertices), len(order))); gname = {g.index: g.name for g in mesh.vertex_groups}
        for v in me.vertices:
            for g in v.groups: W[v.index, self.idx[gname[g.group]]] = g.weight
        self.W = W / W.sum(1, keepdims=True)
        self.rest_inv = np.array([np.array(self.rest[n].inverted()) for n in order])
        self.feet = {}
        for k, (up, lo, ft, _) in legs.items():
            v = self.rest[ft] @ Vector((0, self.length[ft], 0)); self.feet[k] = Vector((v.x, v.y, 0.0))

    def fk(self, pose):
        M = {}
        for n in self.order:
            loc, rr = pose[n]
            B = Matrix.Translation(loc) @ Euler(rr, 'XYZ').to_matrix().to_4x4()
            p = self.parent[n]
            M[n] = (M[p] @ self.rel[n] if p else self.rel[n]) @ B
        return M

    def skin(self, M, mask=None):
        S = np.array([np.array(M[n]) for n in self.order]) @ self.rest_inv
        V = self.V if mask is None else self.V[mask]; W = self.W if mask is None else self.W[mask]
        return (np.einsum('bij,vj->vbi', S, V) * W[:, :, None]).sum(1)[:, :3]

    def tip(self, M, bone):
        return M[bone] @ Vector((0, self.length[bone], 0))


# ---------------- pose helpers ----------------
def body(sk, pose, off=(0, 0, 0), pitch=0.0, roll=0.0, yaw=0.0):
    """mover bone (Body: local X = world X, Y = forward, Z = down): world offset (m), pitch + = nose down, roll, yaw (deg)"""
    Rm = sk.rest[sk.mover].to_3x3()
    pose[sk.mover][0] = list(Rm.transposed() @ Vector(off)); pose[sk.mover][1] = [R(pitch), R(roll), R(yaw)]


def lower_body(sk, pose, dz):
    Rm = sk.rest[sk.mover].to_3x3(); o = Rm @ Vector(pose[sk.mover][0]); o.z -= dz
    pose[sk.mover][0] = list(Rm.transposed() @ o)


def leg_ik(sk, pose, leg, ankle, toe_pitch=0.0):
    """analytic 2-bone IK (copy of animal_anim.leg_ik for a legs table); foot bone kept vertical + toe_pitch (rad, + = toes
    down). Returns the reach excess in metres (> 0: target out of reach)."""
    up, lo, ft, front = sk.legs[leg]
    M = sk.fk(pose); M0 = M[sk.parent[up]] @ sk.rel[up]
    t = M0.inverted() @ Vector(ankle)
    beta = math.atan2(-t.x, t.y); r = math.hypot(t.x, t.y); tz = t.z
    L1, L2 = sk.length[up], sk.length[lo]
    d0 = math.hypot(r, tz); d = min(max(d0, abs(L1 - L2) + 1e-4), L1 + L2 - 1e-6)
    base = math.atan2(tz, r)
    al = math.acos(max(-1.0, min(1.0, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))))
    a1 = base - al if front else base + al
    ky, kz = L1 * math.cos(a1), L1 * math.sin(a1)
    ty, tz2 = d * math.cos(base), d * math.sin(base)
    phi2 = math.atan2(tz2 - kz, ty - ky)
    dd = Matrix.Rotation(-beta, 3, 'Z') @ (M0.to_3x3().inverted() @ Vector((0, 0, -1)))
    phid = math.atan2(dd.z, dd.y)
    pose[up][1] = [a1, 0.0, beta]; pose[lo][1] = [phi2 - a1, 0.0, 0.0]; pose[ft][1] = [phid + toe_pitch - phi2, 0.0, 0.0]
    return d0 - (L1 + L2)


def plant(sk, pose, feet=None):
    feet = feet or {}; ex = -1.0
    for k, (up, lo, ft, _) in sk.legs.items():
        G = Vector(feet.get(k, sk.feet[k])); ex = max(ex, leg_ik(sk, pose, k, G + Vector((0, 0, sk.length[ft])) ))
    return ex


def settle(sk, pose, feet=None, margin=0.006):
    """plant both feet; lower the body until both legs reach with a small knee bend (margin m)"""
    for _ in range(6):
        ex = plant(sk, pose, feet)
        if ex < -margin + 1e-5: return
        lower_body(sk, pose, ex + margin)
    plant(sk, pose, feet)


def head_down_deg(sk, M):
    """signed head pitch below the forward horizontal in the sagittal plane (forward = -Y), -180..180"""
    d = M['Head'].to_3x3() @ Vector((0, 1, 0))
    return math.degrees(math.atan2(-d.z, -d.y))


def set_head_down(sk, pose, deg):
    for _ in range(2):
        e = (deg - head_down_deg(sk, sk.fk(pose)) + 180.0) % 360.0 - 180.0
        pose['Head'][1][0] += R(e)


def neck_ik(sk, pose, target, bones=('Neck1', 'Neck2'), end='Head', iters=12, share=(0.5, 0.5)):
    """move the end bone head (Head pivot) to target (world) by adding pitch to the neck bones (Newton, numeric Jacobian,
    damped least squares, a small preference for an even split between the bones)"""
    target = Vector(target); x = np.zeros(len(bones)); base = [pose[b][1][0] for b in bones]

    def head(xv):
        for b, b0, a in zip(bones, base, xv): pose[b][1][0] = b0 + a
        return np.array(sk.fk(pose)[end].translation)
    for _ in range(iters):
        h = head(x); e = np.array(target) - h
        if np.linalg.norm(e) < 2e-4: break
        J = np.zeros((3, len(bones)))
        for i in range(len(bones)):
            dx = x.copy(); dx[i] += 1e-3; J[:, i] = (head(dx) - h) / 1e-3
        lam = 1e-4
        step = np.linalg.solve(J.T @ J + lam * np.eye(len(bones)), J.T @ e)
        x = x + np.clip(step, -0.35, 0.35)
    head(x)
    return float(np.linalg.norm(np.array(target) - np.array(sk.fk(pose)[end].translation)))


def neck_ik2(sk, pose, target, bend=-1, b1='Neck1', b2='Neck2'):
    """analytic planar 2-bone neck IK in the sagittal (YZ) plane: Neck2's tail (= Head pivot) to target; the elbow
    (Neck1/Neck2 joint) on a fixed side of the line N0->H: bend -1 = u rotated -90 deg in (y, z) (pecking neck arches up;
    no side flip while the line turns). Rotations about the bones' local X (= world X by
    the roll rule). Returns the remaining distance (m)."""
    M = sk.fk(pose); N0 = M[b1].translation; L1, L2 = sk.length[b1], sk.length[b2]
    v = Vector((0, target[1] - N0.y, target[2] - N0.z)); d0 = v.length; u = v / max(d0, 1e-9)
    d = min(max(d0, abs(L1 - L2) + 1e-4), L1 + L2 - 1e-5)
    a = (L1 * L1 - L2 * L2 + d * d) / (2 * d); h = math.sqrt(max(L1 * L1 - a * a, 0.0))
    n = Vector((0, -u.z, u.y)) * (-bend)
    J = Vector((0, N0.y, N0.z)) + u * a + n * h; H = Vector((0, N0.y, N0.z)) + u * d
    for b, p0, p1 in ((b1, Vector((0, N0.y, N0.z)), J), (b2, J, H)):
        M = sk.fk(pose); c = M[b].to_3x3() @ Vector((0, 1, 0)); w = (p1 - p0).normalized()
        pose[b][1][0] += math.atan2(c.y * w.z - c.z * w.y, c.y * w.y + c.z * w.z)
    return float((sk.fk(pose)['Head'].translation - Vector(target)).length)


def jerk(t, keys, d=0.03):
    """bird-like holds: keys [(t_i, (values...))] sorted on 0..1, periodic; snap from the previous value over d (smoothstep)"""
    n = len(keys); i = max(j for j in range(n) if keys[j][0] <= t) if t >= keys[0][0] else n - 1
    t0, v1 = keys[i]; v0 = keys[i - 1][1]
    u = smooth(((t - t0) % 1.0) / d)
    return [a + (b - a) * u for a, b in zip(v0, v1)]


def env(t, t0, t1, t2, t3):
    """0 before t0, smooth rise to 1 at t1, hold, smooth fall to 0 at t3 (start of the fall t2)"""
    if t < t0 or t >= t3: return 0.0
    if t < t1: return smooth((t - t0) / (t1 - t0))
    if t < t2: return 1.0
    return 1.0 - smooth((t - t2) / (t3 - t2))


def look(sk, p, yaw, tilt=0.0, nod=0.0, sp=None):
    """head yaw split Neck2 (twist about its up axis) / Head (about its down axis), tilt = roll about the beak axis"""
    rot(p, 'Neck2', y=0.3 * yaw); rot(p, 'Head', z=-0.7 * yaw, y=tilt, x=nod)


# ---------------- clips ----------------
def gait(sk, sp, name, overlay):
    """biped walk in place: stance feet move back at speed, swing arcs with toe curl, body height from leg reach (smoothed,
    periodic); overlay(pose, phase) runs before the leg IK"""
    g = sp['gait'][name]; T = g['T']; N = frames_of(T); duty = g['duty']; v = g['speed']; S = duty * v * T
    targ = []; need = np.zeros(N); stance = {k: [] for k in sk.legs}
    piv = {k: sk.rest[sk.legs[k][0]].translation.copy() for k in sk.legs}
    for f in range(N):
        ph = f / N; row = {}
        for k, (up, lo, ft, _) in sk.legs.items():
            p = (ph - g['phases'][k]) % 1.0; G = sk.feet[k]; L3 = sk.length[ft]
            if p < duty:
                y = G.y - S / 2 + S * p / duty; z = 0.0; tp = 0.0; stance[k].append(f)
                Lm = 0.97 * (sk.length[up] + sk.length[lo]); dy = y - piv[k].y
                need[f] = max(need[f], (piv[k].z - L3) - math.sqrt(max(Lm * Lm - dy * dy, 0.0)))
            else:
                s = (p - duty) / (1 - duty)
                y = G.y + S / 2 - S * (s - math.sin(TW * s) / TW)
                z = g['lift'] * math.sin(math.pi * s) ** 1.3; tp = R(g['toe_curl']) * math.sin(math.pi * s) ** 2
            row[k] = (Vector((G.x, y, z + L3)), tp)
        targ.append(row)
    Fc = np.fft.rfft(need); Fc[4:] = 0; drop = np.fft.irfft(Fc, N); drop += max(0.0, float((need - drop).max())) + g['crouch']
    frames = []
    for f in range(N):
        ph = f / N; pose = new_pose(sk)
        w = math.sin(TW * (ph - 0.05))                                   # weight over the left leg at ph ~0.3
        body(sk, pose, (g['sway'] * w, 0, -drop[f]), pitch=g['pitch'], roll=-g['roll'] * w, yaw=g['yaw'] * math.sin(TW * ph))
        overlay(pose, ph)
        for k in sk.legs:
            a, tp = targ[f][k]; leg_ik(sk, pose, k, a, tp)
        frames.append(pose)
    frames.append(copy_pose(frames[0]))
    events = sorted([(round(g['phases'][k] * N) % N, 'Footstep', k) for k in sk.legs])
    return frames, events, dict(stance=stance, speed=v, step=S, N=N, drop=[round(float(x), 4) for x in drop])


def build_clips(sk, sp):
    """Duck: Idle (stand, breathe, smooth head turns, tail wag bursts, one bill dip), Walk (waddle: strong roll + sway,
    small head bob, webbed feet lift and place, tail wag), Swim (in place: float bob + rock, alternate leg paddle under
    the body, head held up with a slight bob, tail wag). Parameters in rig_duck.DUCK."""
    out = {}; dur = {c: (T, loop) for c, T, loop in sp['clips']}
    P = sp['poses']
    STAND = new_pose(sk); settle(sk, STAND, margin=P['stand_bend'])
    M0 = sk.fk(STAND); down_rest = head_down_deg(sk, M0)
    side = {'L': 1, 'R': -1}

    def burst(t, t0, w, cycles):
        x = ((t - t0) % 1.0) / w
        return math.sin(cycles * TW * x) * math.sin(math.pi * x) if x < 1.0 else 0.0

    # ---- Idle
    LOOK = P['idle_look']; Ti = dur['Idle'][0]

    def ov_idle(p, t):
        br = P['breaths']
        rot(p, sk.mover, x=P['breath_pitch'] * math.sin(br * TW * t))
        lower_body(sk, p, P['breath_dz'] * (1 - math.cos(br * TW * t)) / 2)
        yaw, tilt, nod = jerk(t, LOOK, P['snap_frames'] / (Ti * FPS))
        dip = env(t, *P['dip'])
        look(sk, p, yaw, tilt, nod + P['dip_deg'] * dip)
        rot(p, 'Neck1', x=1.5 * math.sin(TW * t + 0.3) + 0.35 * P['dip_deg'] * dip)
        rot(p, 'Beak_Lower', x=P['dip_open'] * env(t, P['dip'][1], P['dip'][1] + 0.02, P['dip'][2] - 0.02, P['dip'][2]))
        wag = sum(burst(t, t0, w, c) for t0, w, c in P['tail_bursts'])
        rot(p, 'TailFan1', x=1.5 * math.sin(2 * TW * t), z=P['tail_wag'] * wag)
        rot(p, 'TailFan2', z=0.5 * P['tail_wag'] * sum(burst(t - 0.015, t0, w, c) for t0, w, c in P['tail_bursts']))
        for s, sg in side.items(): rot(p, 'WingUpper.' + s, z=-sg * P['wing_out'] * 0.2)
    N = frames_of(Ti); fr = []
    for f in range(N):
        p = copy_pose(STAND); ov_idle(p, f / N); plant(sk, p); fr.append(p)
    fr.append(copy_pose(fr[0])); out['Idle'] = dict(frames=fr, events=[])

    # ---- Walk: waddle (strong roll + sway from gait()), small head bob twice per cycle, tail wag against the roll
    g = sp['gait']['Walk']

    def ov_walk(p, ph):
        q = (2 * ph) % 1.0
        b = g['head_bob'] * math.sin(TW * q - 0.8)
        rot(p, 'Neck1', x=b); rot(p, 'Neck2', x=-0.5 * b)
        set_head_down(sk, p, down_rest + g['head_nod'] * math.sin(TW * q - 0.4))
        rot(p, 'Neck2', y=g['head_counter'] * math.sin(TW * (ph - 0.05)))       # head stays level against the roll
        rot(p, 'TailFan1', z=g['tail'] * math.sin(TW * ph - 1.2), x=0.3 * g['tail'] * math.sin(2 * TW * ph))
        rot(p, 'TailFan2', z=0.6 * g['tail'] * math.sin(TW * ph - 1.9))
        for s, sg in side.items(): rot(p, 'WingUpper.' + s, z=-sg * P['wing_out'] * 0.3 * (1 + math.sin(2 * TW * ph)))
    fr, ev, extra = gait(sk, sp, 'Walk', ov_walk)
    out['Walk'] = dict(frames=fr, events=ev, extra=extra)

    # ---- Swim: in place, floating; legs paddle alternately (power stroke back with the web spread, recovery forward
    # with the toes trailing); the body bobs and rocks a little; head up with a slight bob; tail wag
    S = P['swim']; Ts = dur['Swim'][0]; N = frames_of(Ts); fr = []; ev = []
    hipz = {k: sk.rest[sk.legs[k][0]].translation.z for k in sk.legs}
    for f in range(N):
        t = f / N; p = new_pose(sk)
        body(sk, p, (0, 0, S['bob'] * math.sin(2 * TW * t)), pitch=S['pitch'] * math.sin(2 * TW * t + 0.8),
             roll=S['roll'] * math.sin(S['strokes'] * TW * t + 0.3))
        for k, ph0 in (('LegL', 0.0), ('LegR', 0.5)):
            G = sk.feet[k]; L3 = sk.length[sk.legs[k][2]]
            s = (S['strokes'] * t - ph0) % 1.0                  # stroke phase 0..1 (S['strokes'] cycles per loop per leg)
            if s < S['power']:                                  # power stroke: front -> back, low
                u = smooth(s / S['power'])
                y = G.y + S['y_front'] + (S['y_back'] - S['y_front']) * u
                z = S['z_low'] + S['z_dip'] * math.sin(math.pi * u); tp = R(S['toe_power'])
            else:                                               # recovery: back -> front, raised, toes trailing
                u = smooth((s - S['power']) / (1 - S['power']))
                y = G.y + S['y_back'] + (S['y_front'] - S['y_back']) * u
                z = S['z_low'] + S['z_lift'] * math.sin(math.pi * u); tp = R(S['toe_power'] + (S['toe_recover'] - S['toe_power']) * math.sin(math.pi * u))
            leg_ik(sk, p, k, Vector((G.x, y, z + L3)), tp)
        b = S['head_bob'] * math.sin(2 * TW * t + 0.5)
        rot(p, 'Neck1', x=S['neck_up'] + b); rot(p, 'Neck2', x=-0.5 * S['neck_up'] - 0.4 * b)
        set_head_down(sk, p, down_rest + S['head_nod'] * math.sin(2 * TW * t + 1.0))
        rot(p, 'TailFan1', z=S['tail'] * math.sin(2 * TW * t), x=2.0 * math.sin(2 * TW * t + 1.2))
        rot(p, 'TailFan2', z=0.6 * S['tail'] * math.sin(2 * TW * t - 0.7))
        for s_, sg in side.items(): rot(p, 'WingUpper.' + s_, z=-sg * P['wing_out'] * 0.2)
        fr.append(p)
    fr.append(copy_pose(fr[0]))
    per = N / S['strokes']                                       # frames per stroke cycle
    for k, ph0 in (('LegL', 0.0), ('LegR', 0.5)):
        for i in range(int(S['strokes'])):
            ev.append((int(round((i + ph0) * per)) % N, 'Paddle', k))
    out['Swim'] = dict(frames=fr, events=sorted(ev), extra=dict(water_z=S['water_z']))
    for c, (T, loop) in dur.items():
        out[c]['loop'] = loop; out[c].setdefault('bones', None); out[c].setdefault('extra', {})
    return out


# ---------------- actions + metrics (copies of animal_anim.write_action / metrics for the bird skeleton) ----------------
def write_action(rig, name, frames, loop, mover='Body'):
    old = bpy.data.actions.get(name)
    if old: bpy.data.actions.remove(old)
    act = bpy.data.actions.new(name); act.use_fake_user = True
    slot = act.slots.new(id_type='OBJECT', name=rig.name)
    cb = anim_utils.action_ensure_channelbag_for_slot(act, slot)
    N = len(frames) - 1
    for b in frames[0]:
        for path, ix in [('rotation_euler', 1)] + ([('location', 0)] if b == mover else []):
            for i in range(3):
                fc = cb.fcurves.new(f'pose.bones["{b}"].{path}', index=i, group_name=b)
                fc.keyframe_points.add(N + 1); co = []
                for f, p in enumerate(frames): co += [float(f), p[b][ix][i]]
                fc.keyframe_points.foreach_set('co', co)
                fc.keyframe_points.foreach_set('interpolation', [1] * (N + 1))
                fc.update()
    act.use_frame_range = True; act.frame_start = 0; act.frame_end = N; act.use_cyclic = loop
    return act


def metrics(sc, rig, mesh, sk, clips, acts, limits):
    """measured on Blender's evaluation of the written actions: loop closure, lowest vertex, foot slip in stance (walk),
    head stillness in the walk hold phase, beak tip height at the pecks, joint ranges vs limits"""
    rep = {}
    for name, C in clips.items():
        act = acts[name]; assign(rig, act); N = int(act.frame_end)
        r = dict(frames=N + 1, seconds=round(N / FPS, 3), loop=C['loop'])
        cb = anim_utils.action_get_channelbag_for_slot(act, act.slots[0]); worst = 0.0; lw = 0.0
        for fc in cb.fcurves:
            dv = abs(fc.evaluate(0) - fc.evaluate(N))
            if fc.data_path.endswith('rotation_euler'): worst = max(worst, math.degrees(dv))
            else: lw = max(lw, dv)
        r['loop_closure_deg'] = round(worst, 6); r['loop_closure_loc_m'] = round(lw, 6)
        minz = 1e9; minf = 0; feet = {k: [] for k in sk.legs}; head = []; beak = []
        for f in range(N + 1):
            sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get()
            me = mesh.evaluated_get(dg).to_mesh(); lowv = min(me.vertices, key=lambda v: v.co.z); z = lowv.co.z; lco = lowv.co.copy()
            mesh.evaluated_get(dg).to_mesh_clear()
            if z < minz: minz, minf, minco = z, f, lco
            for k, (up, lo, ft, _) in sk.legs.items(): feet[k].append(rig.pose.bones[ft].tail.copy())
            head.append(rig.pose.bones['Head'].head.copy()); beak.append(rig.pose.bones['Head'].tail.copy())
        r['lowest_vertex_m'] = round(minz, 4); r['lowest_frame'] = minf; r['lowest_at'] = [round(c, 3) for c in minco]
        ex = C.get('extra') or {}
        if 'stance' in ex:
            v = ex['speed']; S = ex['step']; slip = 0.0; lift = 0.0
            for k in sk.legs:
                fs = ex['stance'][k]; runs = []; cur = [fs[0]]
                for a, b in zip(fs, fs[1:]):
                    if b == a + 1: cur.append(b)
                    else: runs.append(cur); cur = [b]
                runs.append(cur)
                if len(runs) > 1 and runs[-1][-1] == ex['N'] - 1 and runs[0][0] == 0:
                    runs[0] = runs[-1] + [x + ex['N'] for x in runs[0]]; runs.pop()
                for run in runs:
                    p0 = feet[k][run[0] % ex['N']]
                    for fr_ in run:
                        p = feet[k][fr_ % ex['N']]; dt = (fr_ - run[0]) / FPS
                        slip = max(slip, (p - p0 - Vector((0, v * dt, 0))).length); lift = max(lift, abs(p.z))
            r['foot_slip_m'] = round(slip, 4); r['foot_slip_pct_of_step'] = round(100 * slip / S, 2)
            r['step_m'] = round(S, 3); r['stance_foot_max_height_m'] = round(lift, 4); r['speed_mps'] = v
            # head in world space (ground frame = root frame moving back at v): range of y over the clip
            ys = [h.y - v * f / FPS for f, h in enumerate(head[:ex['N']])]
            hy = [h.y for h in head]
            r['head_y_range_rel_body_m'] = round(max(hy) - min(hy), 4)
            r['head_world_drift_in_hold_mps'] = None
        if name == 'Peck':
            r['beak_tip_min_z_m'] = round(min(b.z for b in beak), 4); r['beak_tip_max_z_m'] = round(max(b.z for b in beak), 4)
        ranges = {}; viol = []; nyaw = 0.0
        for fr_ in C['frames']:
            nyaw = max(nyaw, abs(math.degrees(fr_['Neck1'][1][1] + fr_['Neck2'][1][1] - fr_['Head'][1][2])))
            for b, (loc, rr) in fr_.items():
                for i, ax in enumerate('xyz'):
                    d = math.degrees(rr[i]); lo, hi = ranges.get((b, ax), (d, d)); ranges[(b, ax)] = (min(lo, d), max(hi, d))
        for (b, ax), (lo, hi) in ranges.items():
            lim = limits.get(b.split('.')[0], {}).get(ax)
            if lim and (lo < lim[0] - 0.01 or hi > lim[1] + 0.01): viol.append(f'{b}.{ax} {lo:.1f}..{hi:.1f} (limit {lim})')
        if nyaw > limits['NECK_YAW_TOTAL']: viol.append(f'neck yaw total {nyaw:.1f}')
        r['neck_yaw_total_deg'] = round(nyaw, 1)
        r['joint_ranges_deg'] = {f'{b}.{ax}': [round(lo, 1), round(hi, 1)] for (b, ax), (lo, hi) in sorted(ranges.items())
                                 if hi - lo > 0.05 or abs(hi) > 0.05}
        r['limit_violations'] = viol
        rep[name] = r
        print(f"METRIC {name:6s} N={N:3d} closure={r['loop_closure_deg']}deg/{r['loop_closure_loc_m']}m lowest={r['lowest_vertex_m']}@{minf}{r['lowest_at']} "
              f"slip={r.get('foot_slip_pct_of_step', '-')}% stanceZ={r.get('stance_foot_max_height_m', '-')} "
              f"headY={r.get('head_y_range_rel_body_m', '-')} beak={r.get('beak_tip_min_z_m', '-')} neckyaw={r['neck_yaw_total_deg']} viol={viol}")
    assign(rig, None)
    return rep
