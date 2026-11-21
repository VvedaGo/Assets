# pigeon_clips.py - FLIGHT-CAPABLE bird clip toolkit (skeleton B) + clips Idle / Peck / Fly / Hop for BRD-08 Pigeon,
# reused read-only by ../Sparrow/rig_sparrow.py and ../Crow/rig_crow.py (all numbers come from the species tables).
# Copied from ../Hen/hen_clips.py (read-only there) and extended:
#  - BirdSkel.fk takes a per-bone euler order (sk.eorder) or a 3x3 Matrix as the rotation of a bone (wing bones are
#    generated as matrices and converted at the end by finalize(): one euler order per wing bone, chosen so the middle
#    angle stays away from the +-90 deg gimbal lock over ALL clips, compat-continuous eulers).
#  - wing_set(): spread / flap / sweep / twist of WingUpper about the shoulder + lag (up/down) and sweep of WingLower and
#    WingTip about their seam hinges. The spread maps the folded wing frame (a = length back, n = outer normal,
#    c = n x a) onto the flight frame (a' = out, n' = up): the outer (patterned) face of the folded wing becomes the top.
#  - clips: idle (looks around in jerks, breathing, tail, ruffle), peck (hen peck with a long virtual neck), fly (flapping
#    flight in place, body lifted, feet tucked, head stabilised), hop (both feet together, ballistic body, in place).
import math
import numpy as np
import bpy
from mathutils import Matrix, Vector, Euler, Quaternion
from bpy_extras import anim_utils
from animal_anim import FPS, R, smooth, new_pose, frames_of, assign

TW = 2 * math.pi
ORDERS = ('XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX')
WING_BONES = ('WingUpper', 'WingLower', 'WingTip')


def copy_pose(p):
    return {n: [list(a), (b.copy() if isinstance(b, Matrix) else list(b))] for n, (a, b) in p.items()}


def rot(pose, bone, x=0.0, y=0.0, z=0.0):
    r = pose[bone][1]
    if isinstance(r, Matrix):
        pose[bone][1] = r @ Euler((R(x), R(y), R(z)), 'XYZ').to_matrix(); return
    r[0] += R(x); r[1] += R(y); r[2] += R(z)


# ---------------- skeleton ----------------
class BirdSkel:
    """FK + linear-blend skinning on a joined mesh (copy of hen_clips.BirdSkel); per-bone euler order; legs table"""
    def __init__(self, rig, mesh, legs, mover='Body'):
        self.rig = rig; self.legs = legs; self.mover = mover; bones = rig.data.bones; order = []

        def visit(b):
            order.append(b.name)
            for c in b.children: visit(c)
        for b in bones:
            if b.parent is None: visit(b)
        self.order = order
        self.eorder = {n: 'XYZ' for n in order}
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

    def rmat(self, n, rr):
        return rr.to_4x4() if isinstance(rr, Matrix) else Euler(rr, self.eorder[n]).to_matrix().to_4x4()

    def fk(self, pose):
        M = {}
        for n in self.order:
            loc, rr = pose[n]
            B = Matrix.Translation(loc) @ self.rmat(n, rr)
            p = self.parent[n]
            M[n] = (M[p] @ self.rel[n] if p else self.rel[n]) @ B
        return M

    def skin(self, M, mask=None):
        S = np.array([np.array(M[n]) for n in self.order]) @ self.rest_inv
        V = self.V if mask is None else self.V[mask]; W = self.W if mask is None else self.W[mask]
        return (np.einsum('bij,vj->vbi', S, V) * W[:, :, None]).sum(1)[:, :3]

    def tip(self, M, bone):
        return M[bone] @ Vector((0, self.length[bone], 0))


# ---------------- pose helpers (copies of hen_clips) ----------------
def body(sk, pose, off=(0, 0, 0), pitch=0.0, roll=0.0, yaw=0.0):
    """mover bone (Body: local X = world X, Y = forward, Z = down): world offset (m), pitch + = nose down, roll, yaw (deg)"""
    Rm = sk.rest[sk.mover].to_3x3()
    pose[sk.mover][0] = list(Rm.transposed() @ Vector(off)); pose[sk.mover][1] = [R(pitch), R(roll), R(yaw)]


def lower_body(sk, pose, dz):
    Rm = sk.rest[sk.mover].to_3x3(); o = Rm @ Vector(pose[sk.mover][0]); o.z -= dz
    pose[sk.mover][0] = list(Rm.transposed() @ o)


def leg_ik(sk, pose, leg, ankle, toe_pitch=0.0):
    """analytic 2-bone IK (copy of hen_clips.leg_ik); foot bone kept vertical + toe_pitch (rad, + = toes down)"""
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
    for _ in range(6):
        ex = plant(sk, pose, feet)
        if ex < -margin + 1e-5: return
        lower_body(sk, pose, ex + margin)
    plant(sk, pose, feet)


def head_down_deg(sk, M):
    d = M['Head'].to_3x3() @ Vector((0, 1, 0))
    return math.degrees(math.atan2(-d.z, -d.y))


def set_head_down(sk, pose, deg):
    for _ in range(2):
        e = (deg - head_down_deg(sk, sk.fk(pose)) + 180.0) % 360.0 - 180.0
        pose['Head'][1][0] += R(e)


def neck_ik2(sk, pose, target, bend=-1, b1='Neck1', b2='Neck2'):
    """analytic planar 2-bone neck IK (copy of hen_clips.neck_ik2): Neck2's tail (= Head pivot) to target"""
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
    n = len(keys); i = max(j for j in range(n) if keys[j][0] <= t) if t >= keys[0][0] else n - 1
    t0, v1 = keys[i]; v0 = keys[i - 1][1]
    u = smooth(((t - t0) % 1.0) / d)
    return [a + (b - a) * u for a, b in zip(v0, v1)]


def env(t, t0, t1, t2, t3):
    if t < t0 or t >= t3: return 0.0
    if t < t1: return smooth((t - t0) / (t1 - t0))
    if t < t2: return 1.0
    return 1.0 - smooth((t - t2) / (t3 - t2))


def look(sk, p, yaw, tilt=0.0, nod=0.0, share=0.3):
    """head yaw split Neck2 (twist) / Head (about its down axis), tilt = roll about the beak axis"""
    rot(p, 'Neck2', y=share * yaw); rot(p, 'Head', z=-(1 - share) * yaw, y=tilt, x=nod)


def burst(t, t0, w, cycles):
    x = ((t - t0) % 1.0) / w
    return math.sin(cycles * TW * x) * math.sin(math.pi * x) if x < 1.0 else 0.0


# ---------------- wings ----------------
def wing_frame(sk, sp, s):
    """folded-wing frame (a, c, n) of side s in rest (armature) space; .R mirrored from .L"""
    a, c, n = (Vector(v) for v in sp['wing_frame'])
    if s == 'R':
        a = Vector((-a.x, a.y, a.z)); n = Vector((-n.x, n.y, n.z)); c = n.cross(a)
    return a, c, n


def _local(sk, bone, Rw):
    """rotation Rw (rest space, about the bone head) -> bone-local rotation"""
    Rr = sk.rest[bone].to_3x3()
    return Rr.inverted() @ Rw @ Rr


def wing_set(sk, sp, pose, s, spread=1.0, flap=0.0, sweep=0.0, twist=0.0, lag=(0.0, 0.0), lsweep=(0.0, 0.0), fold=0.0):
    """s 'L'/'R'. spread 0..1 (folded -> flight frame), flap deg (+ = up), sweep deg (+ = tip back), twist deg (+ = leading
    edge down), lag (WingLower, WingTip) deg (+ = tip up relative to the parent part), lsweep deg (+ = tip back),
    fold deg: WingUpper out-swing about the body side (folded wing only, + = out) for ruffles."""
    a, c, n = wing_frame(sk, sp, s); sg = 1.0 if s == 'L' else -1.0
    F = Matrix((a, c, n)).transposed()
    a2 = Vector((sg, 0, 0)); n2 = Vector((0, 0, 1)); c2 = n2.cross(a2)
    F2 = Matrix((a2, c2, n2)).transposed()
    q = (F2 @ F.transposed()).to_quaternion()
    Rs = Quaternion().slerp(q, spread).to_matrix() if spread < 1.0 else q.to_matrix()
    Rf = Matrix.Rotation(-sg * R(flap), 3, 'Y') @ Matrix.Rotation(sg * R(sweep), 3, 'Z') @ Matrix.Rotation(R(twist), 3, 'X')
    Rfold = Matrix.Rotation(R(fold), 3, c)          # about the folded chord axis: tip out (left: a x? sign checked below)
    if fold:
        test = Rfold @ a
        if test.dot(n) < 0: Rfold = Matrix.Rotation(-R(fold), 3, c)
    Rw = Rf @ Rs @ Rfold if spread > 0 else Rfold
    pose['WingUpper.' + s][1] = _local(sk, 'WingUpper.' + s, Rw)
    for b, lg, sw in (('WingLower.' + s, lag[0], lsweep[0]), ('WingTip.' + s, lag[1], lsweep[1])):
        if b not in pose: continue
        Rl = Matrix.Rotation(R(lg), 3, a.cross(n)) @ Matrix.Rotation(sg * R(sw), 3, n)     # mirror: sweep sign flips
        pose[b][1] = _local(sk, b, Rl)


def wing_bones(sk):
    return [n for n in sk.order if n.split('.')[0] in WING_BONES]


def finalize(sk, clips):
    """wing bones: choose one euler order per bone (min of the max |middle angle| over all frames of all clips), convert
    matrices / XYZ lists to compat-continuous eulers in that order. Sets sk.eorder."""
    for n in wing_bones(sk):
        mats = []
        for C in clips.values():
            mats.append([(fr[n][1].copy() if isinstance(fr[n][1], Matrix) else Euler(fr[n][1], sk.eorder[n]).to_matrix())
                         for fr in C['frames']])
        best = None
        for o in ORDERS:
            mid = 0.0
            for seq in mats:
                for m in seq: mid = max(mid, abs(math.degrees(m.to_euler(o)[ 'XYZ'.index(o[1]) ])))
            if best is None or mid < best[1] - 1e-6: best = (o, mid)
        o = best[0]; sk.eorder[n] = o
        for C, seq in zip(clips.values(), mats):
            prev = None
            for fr, m in zip(C['frames'], seq):
                e = m.to_euler(o) if prev is None else m.to_euler(o, prev)
                fr[n][1] = [e.x, e.y, e.z]; prev = e
            if C['loop']: C['frames'][-1][n][1] = list(C['frames'][0][n][1])
        print(f'EULER {n}: order {o} max middle angle {best[1]:.1f} deg')


# ---------------- clips ----------------
def stand(sk, sp):
    P = sp['poses']; S = new_pose(sk); settle(sk, S, margin=P['stand_bend']); return S


def clip_idle(sk, sp, T):
    """looks around in quick jerks with pauses, breathing, tail wag + flick, wing ruffle"""
    P = sp['poses']; STAND = stand(sk, sp); LOOK = P['idle_look']; N = frames_of(T); fr = []
    br = P.get('breaths', 2); snap = P.get('snap_frames', 3.0) / N
    for f in range(N):
        t = f / N; p = copy_pose(STAND)
        rot(p, sk.mover, x=P.get('breath_pitch', 0.8) * math.sin(br * TW * t))
        lower_body(sk, p, P.get('breath_dz', 0.0015) * (1 - math.cos(br * TW * t)) / 2)
        yaw, tilt, nod = jerk(t, LOOK, snap)
        look(sk, p, yaw, tilt, nod, P.get('look_share', 0.3))
        rot(p, 'Neck1', x=P.get('neck_sway', 1.5) * math.sin(TW * t + 0.3))
        tb = 0.0
        for t0, w, cyc, amp in P.get('tail_flicks', [(0.58, 0.14, 3, 12.0)]): tb += amp * burst(t, t0, w, cyc)
        rot(p, 'TailFan1', x=P.get('tail_idle', 2.0) * math.sin(2 * TW * t) + P.get('tail_flick_up', 0.0) * abs(tb) / 12.0,
            z=4 * math.sin(TW * t) + tb)
        if 'TailFan2' in p: rot(p, 'TailFan2', z=0.5 * tb, x=1.5 * math.sin(2 * TW * t - 0.6))
        ru = 0.0
        for t0, w, cyc in P.get('ruffles', [(0.86, 0.10, 2)]): ru = max(ru, abs(burst(t, t0, w, cyc)))
        for s in ('L', 'R'): wing_set(sk, sp, p, s, spread=0.0, fold=P['wing_out'] * (0.15 + 0.85 * ru))
        plant(sk, p); fr.append(p)
    fr.append(copy_pose(fr[0]))
    return dict(frames=fr, events=[])


def clip_peck(sk, sp, T):
    """hen peck (copy of hen_clips): lean, quick pecks to the ground with pauses (one cocked look), rise"""
    P = sp['poses']; STAND = stand(sk, sp); M0 = sk.fk(STAND); down_rest = head_down_deg(sk, M0); Lh = sk.length['Head']
    feet = {k: sk.feet[k] + Vector(P['peck_foot'].get(k, (0, 0, 0))) for k in sk.legs}
    tip_rest = sk.tip(M0, 'Head')
    ready = Vector((0, P['peck_y'], P['peck_ready_z'])); hit = Vector((0, P['peck_y'], P['peck_hit_z']))
    N = frames_of(T); fr = []; hits = []
    for f in range(N):
        t = f / N; p = new_pose(sk)
        lean = env(t, *P['peck_lean'])
        st = 0.0
        for c in P['peck_hits']:
            st = max(st, env(t, c - 2.0 / N, c, c + 1.0 / N, c + 5.0 / N))
        body(sk, p, (0, -P.get('peck_fwd', 0.0) * lean, -P['peck_drop'] * lean), pitch=P['peck_pitch'] * lean + P.get('peck_jab', 3.0) * st)
        settle(sk, p, feet, margin=P['stand_bend'])
        yaw, tilt, nod = jerk(t, P['peck_look'], 3.0 / N)
        tip = tip_rest.lerp(ready, lean).lerp(hit, st)
        down = down_rest + (P['peck_ready_down'] - down_rest) * lean + (P['peck_hit_down'] - P['peck_ready_down']) * st
        a = math.radians(down); d = Vector((0, -math.cos(a), -math.sin(a)))
        err = neck_ik2(sk, p, tip - d * Lh); set_head_down(sk, p, down)
        if err > 0.003:
            print(f'PECK f{f} err {err:.4f}')
        rot(p, 'Head', z=-yaw, y=tilt)
        rot(p, 'TailFan1', x=P['peck_tail'] * lean + 8 * st)
        if 'TailFan2' in p: rot(p, 'TailFan2', x=0.4 * P['peck_tail'] * lean)
        for s in ('L', 'R'): wing_set(sk, sp, p, s, spread=0.0, fold=P['wing_out'] * 0.4 * lean)
        if st > 0.99: hits.append(f)
        fr.append(p)
    fr.append(copy_pose(fr[0]))
    return dict(frames=fr, events=[(h, 'Peck', '') for h in sorted(set(hits)) if h - 1 not in hits], extra=dict(feet=feet))


def warp(ph, d):
    """flap phase 0..1 -> u: downstroke ph 0..d -> u 0..0.5, upstroke d..1 -> 0.5..1"""
    return 0.5 * ph / d if ph < d else 0.5 + 0.5 * (ph - d) / (1 - d)


def clip_fly(sk, sp, T):
    """flapping flight in place: body lifted (lowest vertex at F['clear'] above the ground), pitched to near level, feet
    tucked back, head kept level in space, wings: flap (+ = up) about the shoulder with lagging WingLower/WingTip, sweep
    back and twist on the upstroke, body bobs up on the downstroke, tail tilts with the beat"""
    F = sp['fly']; N = frames_of(T); nfl = F['flaps']; fr = []
    M0 = sk.fk(new_pose(sk)); down_rest = head_down_deg(sk, M0)
    for f in range(N):
        t = f / N; ph = (t * nfl) % 1.0; u = warp(ph, F['down']); cu, su = math.cos(TW * u), math.sin(TW * u)
        p = new_pose(sk)
        body(sk, p, (0, 0, F['lift'] - F['bob'] * cu), pitch=F['pitch'] + F['pitch_beat'] * su)
        for k, (up, lo, ft, _) in sk.legs.items():
            p[up][1] = [R(F['leg'][0]), 0.0, 0.0]; p[lo][1] = [R(F['leg'][1]), 0.0, 0.0]; p[ft][1] = [R(F['leg'][2]), 0.0, 0.0]
        for b, x in F['neck'].items(): rot(p, b, x=x)
        set_head_down(sk, p, down_rest + F.get('head_down', 0.0) + F.get('head_nod', 0.0) * su)
        rot(p, 'TailFan1', x=F['tail'] + F['tail_beat'] * cu)
        if 'TailFan2' in p: rot(p, 'TailFan2', x=0.5 * F['tail_beat'] * cu)
        flap = F['mid'] + F['amp'] * cu
        for s in ('L', 'R'):
            wing_set(sk, sp, p, s, spread=1.0, flap=flap, sweep=F['sweep'] - F['sweep_up'] * su, twist=F['twist'] * su,
                     lag=tuple(F.get('lag0', (0.0, 0.0))[i] + F['lag'][i] * math.sin(TW * u - F['lag_ph'][i]) for i in (0, 1)),
                     lsweep=(F['lsweep'][0] - F['lsweep_up'][0] * su, F['lsweep'][1] - F['lsweep_up'][1] * su))
        fr.append(p)
    # lift so the lowest vertex over the clip sits at F['clear'] above the ground
    lo = min(float(sk.skin(sk.fk(p))[:, 2].min()) for p in fr)
    for p in fr: lower_body(sk, p, lo - F['clear'])
    fr.append(copy_pose(fr[0]))
    ev = [(round(N * k / nfl), 'Flap', '') for k in range(nfl)]
    return dict(frames=fr, events=ev, extra=dict(flaps=nfl))


def clip_hop(sk, sp, T):
    """two-footed hop in place (root moves at the hop speed v): contact = feet planted and moving back at v, landing dip +
    push; air = ballistic body arc, feet tucked a little and carried forward. The body follows the feet in y (it stays over
    them in contact and travels with them in the air, like a real hop, not a constant glide). Body nose-down at the landing,
    nose-up at the push; tail flicks up after the landing; small wing flick in the air; head lags the hop."""
    H = sp['hop']; N = frames_of(T); c = H['contact']; S = H['length']; v = S / T; Sc = v * c * T
    P = sp['poses']; STAND = stand(sk, sp); fr = []; stance = {k: [] for k in sk.legs}
    drop = STAND_drop(sk, STAND); down_rest = head_down_deg(sk, sk.fk(STAND)); nc = round(c * N)
    for f in range(N):
        t = f / N; p = copy_pose(STAND)
        if f < nc:
            s = f / nc; dz = -H['crouch'] * math.sin(math.pi * s)
            pitch = H['pitch_land'] * (1 - smooth(s)) - H['pitch_push'] * smooth(s)
            yoff = -Sc / 2 + Sc * s; zf = 0.0; air = 0.0
            for k in sk.legs: stance[k].append(f)
        else:
            s = (f - nc) / (N - nc); dz = 4 * H['height'] * s * (1 - s)
            pitch = -H['pitch_push'] * (1 - smooth(s)) + H['pitch_land'] * smooth(s)
            yoff = Sc / 2 - Sc * (s - math.sin(TW * s) / TW); air = math.sin(math.pi * s)
            zf = dz + H['tuck'] * air
        body(sk, p, (0, H['body_follow'] * yoff, dz), pitch=pitch)
        lower_body(sk, p, drop)
        for k in sk.legs:
            G = sk.feet[k]; a = Vector((G.x, G.y + yoff, zf + sk.length[sk.legs[k][2]]))
            leg_ik(sk, p, k, a, R(H['toe_air']) * air)
        set_head_down(sk, p, down_rest + H['head_lag'] * math.sin(TW * t - 0.8))
        rot(p, 'TailFan1', x=H['tail_flick'] * max(0.0, burst(t, 0.02, 0.30, 1)))
        for s_ in ('L', 'R'): wing_set(sk, sp, p, s_, spread=0.0, fold=P['wing_out'] * 0.2 + H['wing_flick'] * air)
        fr.append(p)
    fr.append(copy_pose(fr[0]))
    return dict(frames=fr, events=[(0, 'Land', 'Both'), (nc, 'Takeoff', 'Both')], extra=dict(stance=stance, speed=v, step=S, N=N))


def STAND_drop(sk, STAND):
    """vertical drop of the standing pose (settle) as a world dz (>0 = lowered)"""
    Rm = sk.rest[sk.mover].to_3x3(); return -(Rm @ Vector(STAND[sk.mover][0])).z


CLIP_FUNCS = {'Idle': clip_idle, 'Peck': clip_peck, 'Fly': clip_fly, 'Hop': clip_hop}


def build_clips(sk, sp):
    out = {}
    for c, T, loop in sp['clips']:
        out[c] = CLIP_FUNCS[sp.get('clip_funcs', {}).get(c, c)](sk, sp, T)
        out[c]['loop'] = loop; out[c].setdefault('extra', {})
    finalize(sk, out)
    return out


# ---------------- actions + metrics (copies of hen_clips.write_action / metrics) ----------------
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
    """measured on Blender's evaluation of the written actions: loop closure, lowest vertex, foot slip in stance (hop),
    beak tip height (peck), fly clearance + wing tip span, joint ranges vs limits"""
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
        minz = 1e9; minf = 0; feet = {k: [] for k in sk.legs}; beak = []; span = []; minco = None
        for f in range(N + 1):
            sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get()
            me = mesh.evaluated_get(dg).to_mesh(); xs = [v.co.x for v in me.vertices]
            lowv = min(me.vertices, key=lambda v: v.co.z); z = lowv.co.z; lco = lowv.co.copy()
            span.append(max(xs) - min(xs))
            mesh.evaluated_get(dg).to_mesh_clear()
            if z < minz: minz, minf, minco = z, f, lco
            for k, (up, lo, ft, _) in sk.legs.items(): feet[k].append(rig.pose.bones[ft].tail.copy())
            beak.append(rig.pose.bones['Head'].tail.copy())
        r['lowest_vertex_m'] = round(minz, 4); r['lowest_frame'] = minf; r['lowest_at'] = [round(c, 3) for c in minco]
        r['span_x_m'] = [round(min(span), 3), round(max(span), 3)]
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
        if name == 'Peck':
            r['beak_tip_min_z_m'] = round(min(b.z for b in beak), 4); r['beak_tip_max_z_m'] = round(max(b.z for b in beak), 4)
        ranges = {}; viol = []; nyaw = 0.0
        for fr_ in C['frames']:
            nyaw = max(nyaw, abs(math.degrees(fr_['Neck1'][1][1] + fr_['Neck2'][1][1] - fr_['Head'][1][2])))
            for b, (loc, rr) in fr_.items():
                for i, ax in enumerate('xyz'):
                    d = math.degrees(rr[i]); lo, hi = ranges.get((b, ax), (d, d)); ranges[(b, ax)] = (min(lo, d), max(hi, d))
        for (b, ax), (lo, hi) in ranges.items():
            lim = (limits.get(b) or limits.get(b.split('.')[0], {})).get(ax)
            if lim and (lo < lim[0] - 0.01 or hi > lim[1] + 0.01): viol.append(f'{b}.{ax} {lo:.1f}..{hi:.1f} (limit {lim})')
        if nyaw > limits['NECK_YAW_TOTAL']: viol.append(f'neck yaw total {nyaw:.1f}')
        r['neck_yaw_total_deg'] = round(nyaw, 1)
        r['joint_ranges_deg'] = {f'{b}.{ax}': [round(lo, 1), round(hi, 1)] for (b, ax), (lo, hi) in sorted(ranges.items())
                                 if hi - lo > 0.05 or abs(hi) > 0.05}
        r['limit_violations'] = viol
        rep[name] = r
        print(f"METRIC {name:6s} N={N:3d} closure={r['loop_closure_deg']}deg/{r['loop_closure_loc_m']}m lowest={r['lowest_vertex_m']}@{minf}{r['lowest_at']} "
              f"span={r['span_x_m']} slip={r.get('foot_slip_pct_of_step', '-')}% stanceZ={r.get('stance_foot_max_height_m', '-')} "
              f"beak={r.get('beak_tip_min_z_m', '-')} neckyaw={r['neck_yaw_total_deg']} viol={viol}")
    assign(rig, None)
    return rep
