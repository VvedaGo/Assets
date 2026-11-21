# fox_clips.py - SML-02 Fox clips (planning/FarmAnimals/ANIMATIONS.md: Idle "listens", Walk "sneaks", Lie_Idle "lies curled up").
# Shared helpers from _common/animal_anim.py are imported read-only. setup_ik/leg_ik_h = copy of ../Dog/dog_clips.py
# (rest-offset leg IK: the fox hind lower leg rests slanted, hock behind the paw); gait_fox = copy of
# ../Cat/cat_clips.gait_cat (overlay before the leg IK, paws near the midline); best_lie = copy of the Cat loaf search,
# then the fox curl: spine yawed, head laid on the ground at the flank, the bushy tail wrapped round the front.
import math
import numpy as np
from mathutils import Vector, Matrix, Euler
from animal_anim import *
from animal_anim import R, LEGS
import animal_anim as _an
import animal_rig as ar

TW = 2 * math.pi
FRONT_LEGS = ['FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', 'FrontUpper.R', 'FrontLower.R', 'FrontFoot.R']
HIND_LEGS = ['HindUpper.L', 'HindLower.L', 'HindFoot.L', 'HindUpper.R', 'HindLower.R', 'HindFoot.R']
BODY = ['Pelvis', 'Spine1', 'Spine2']
TAIL = ['Tail1', 'Tail2', 'Tail3']
HEADM = ['Head', 'Jaw', 'Ear.L', 'Ear.R']
_IK = {}


# ---------------- leg IK with rest offsets (copy of ../Dog/dog_clips.py) ----------------
def setup_ik(sk):
    global leg_ik
    for k in LEGS:
        up, lo, ft, front = ar.LEGS[k]
        cl = sk.rel[lo].to_3x3().col[1]; cf = sk.rel[ft].to_3x3().col[1]
        de = math.atan2(cl.z, cl.y); ep = math.atan2(cf.z, cf.y)
        t = sk.rest[up].inverted() @ sk.rest[ft].translation
        base = math.atan2(t.z, math.hypot(t.x, t.y))
        sgn = (1.0 if base > 0 else -1.0) if abs(base) > math.radians(1.0) else (1.0 if front else -1.0)
        if front: sgn = 1.0
        _IK[k] = (de, ep, sgn)
        print(f'IK {k}: lower rest {math.degrees(de):.1f} deg, foot rest {math.degrees(ep):.1f} deg, knee side {sgn:+.0f}')
    _an.leg_ik = leg_ik_h; leg_ik = leg_ik_h


def leg_ik_h(sk, pose, leg, fetlock, hoof_pitch=0.0):
    up, lo, ft, front = ar.LEGS[leg]; de, ep, sgn = _IK[leg]
    M = sk.fk(pose); M0 = M[sk.parent[up]] @ sk.rel[up]
    t = M0.inverted() @ Vector(fetlock)
    beta = math.atan2(-t.x, t.y); r = math.hypot(t.x, t.y); tz = t.z
    L1, L2 = sk.length[up], sk.length[lo]
    d0 = math.hypot(r, tz); d = min(max(d0, abs(L1 - L2) + 1e-4), L1 + L2 - 1e-6)
    base = math.atan2(tz, r)
    al = math.acos(max(-1.0, min(1.0, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))))
    a1 = base - sgn * al
    ky, kz = L1 * math.cos(a1), L1 * math.sin(a1)
    ty, tz2 = d * math.cos(base), d * math.sin(base)
    phi2 = math.atan2(tz2 - kz, ty - ky)
    dd = Matrix.Rotation(-beta, 3, 'Z') @ (M0.to_3x3().inverted() @ Vector((0, 0, -1)))
    phid = math.atan2(dd.z, dd.y)
    pose[up][1] = [a1, 0.0, beta]; pose[lo][1] = [phi2 - a1 - de, 0.0, 0.0]; pose[ft][1] = [phid + hoof_pitch - phi2 - ep, 0.0, 0.0]
    return d0 - (L1 + L2)


def flick(t, c, w):
    """0..1 envelope on the loop phase: fast rise (first 25% of w), slow relax; zero outside [c, c+w)"""
    x = ((t - c) % 1.0) / w
    if x >= 1.0: return 0.0
    return math.sin(0.5 * math.pi * x / 0.25) if x < 0.25 else 0.5 * (1 + math.cos(math.pi * (x - 0.25) / 0.75))


def hold(t, a, b, ramp):
    """periodic plateau: 0 before a, smooth rise over `ramp`, 1 until b, smooth fall over `ramp` (phase units)"""
    x = (t - a) % 1.0; L = (b - a) % 1.0
    if x < ramp: return smooth(x / ramp)
    if x < L: return 1.0
    if x < L + ramp: return 1.0 - smooth((x - L) / ramp)
    return 0.0


def s_wave(p, ph, amps, lag, pitch=(0.0, 0.0, 0.0)):
    for i, (b, a) in enumerate(zip(TAIL, amps)):
        rot(p, b, x=pitch[i], z=a * math.sin(TW * (ph - lag * i)))


def gait_fox(sk, sp, name, overlay):
    """copy of ../Cat/cat_clips.gait_cat (overlay applied BEFORE the leg IK, paws placed closer to the midline)"""
    g = sp['gait'][name]; T = g['T']; N = frames_of(T); duty = g['duty']; v = g['speed']; S = duty * v * T
    targ = []; need = {'Front': np.zeros(N), 'Hind': np.zeros(N)}
    stance = {k: [] for k in LEGS}
    piv = {k: sk.rest[ar.LEGS[k][0]].translation.copy() for k in LEGS}
    for f in range(N):
        ph = f / N; row = {}
        for k in LEGS:
            p = (ph - g['phases'][k]) % 1.0; G = sk.feet[k]; L3 = sk.length[ar.LEGS[k][2]]
            fl = g['flick'][0 if k.startswith('Front') else 1]; gx = G.x * g['narrow']
            if p < duty:
                y = G.y - S / 2 + S * p / duty; z = 0.0; hp = 0.0; stance[k].append(f)
            else:
                s = (p - duty) / (1 - duty)
                y = G.y + S / 2 - S * (s - math.sin(2 * math.pi * s) / (2 * math.pi))
                z = g['lift'] * math.sin(math.pi * s) ** 0.9; hp = R(fl) * math.sin(math.pi * s) ** 2
            row[k] = (Vector((gx, y, z + L3)), hp, p < duty)
            if p < duty:
                up, lo, ft, front = ar.LEGS[k]; Lm = g['reach'] * (sk.length[up] + sk.length[lo])
                dy = y - piv[k].y; dx = gx - piv[k].x; vert = math.sqrt(max(Lm * Lm - dy * dy - dx * dx, 0.0))
                gk = 'Front' if front else 'Hind'
                need[gk][f] = max(need[gk][f], (piv[k].z - (z + L3)) - vert)
        targ.append(row)
    drops = {}
    for gk, a in need.items():
        Fc = np.fft.rfft(a); Fc[4:] = 0; sm = np.fft.irfft(Fc, N)
        sm += max(0.0, float((a - sm).max())); drops[gk] = sm + g['crouch'] + (g.get('crouch_front', 0.0) if gk == 'Front' else 0.0)
    span = piv['HindL'].y - piv['FrontL'].y
    frames = []
    for f in range(N):
        ph = f / N; pose = new_pose(sk)
        df, dh = drops['Front'][f], drops['Hind'][f]
        pitch = math.degrees(math.asin((df - dh) / span))
        body(sk, pose, (0, 0, -dh + g['bob'] * math.cos(2 * TW * ph)), pitch=pitch, roll=g['roll'] * math.sin(TW * ph))
        overlay(pose, ph, pitch)
        for k in LEGS:
            fet, hp, st = targ[f][k]
            leg_ik(sk, pose, k, fet, hp)
        frames.append(pose)
    frames.append(copy_pose(frames[0]))
    events = sorted([(round(g['phases'][k] * N) % N, 'Footstep', k) for k in LEGS])
    return frames, events, dict(stance=stance, speed=v, step=S, N=N,
                                drops={k: [round(float(d.min()), 4), round(float(d.max()), 4)] for k, d in drops.items()})


# ---------------- curled lying pose ----------------
def lie_pose(sk, fa, fl, ha, hl, splay, ff=0.0, hf=0.0):
    """loaf base (copy of ../Cat/cat_clips.lie_pose_cat): front legs folded under the chest, hind legs beside the belly"""
    p = new_pose(sk)
    body(sk, p, (0, 0.0, -0.30))
    rot(p, 'Tail1', x=45)                      # tail out of the way during the search (curl() lays it down)
    for s, sg in (('L', 1), ('R', -1)):
        rot(p, 'FrontUpper.' + s, x=-fa, z=-2 * sg); rot(p, 'FrontLower.' + s, x=fl); rot(p, 'FrontFoot.' + s, x=ff)
        rot(p, 'HindUpper.' + s, x=ha, z=-splay * sg); rot(p, 'HindLower.' + s, x=-hl); rot(p, 'HindFoot.' + s, x=hf)
    no_penetration(sk, p, exact=True)
    return p


def best_lie(sk, front=None):
    """grid search (Cat): belly ON the ground, folded legs tucked under / along the body, no leg sticking out in front of
    the chest or behind the rump, legs not hovering. front = (fa, fl, ff) fixes the front legs (2026-11-21 rework: paws
    folded under the chest instead of stretched forward)"""
    bm = sk.mask(BODY); fm = sk.mask(FRONT_LEGS); hm = sk.mask(HIND_LEGS); best = None
    for fa in ((front[0],) if front else (45, 55, 65, 75)):     # front legs stretched forward on the ground (paws flat)
        for fl in ((front[1],) if front else (0, 15, 30)):
            for ha in (20, 35, 50, 65, 80):
                for hl in (110, 130, 150, 165):
                    for splay in (8, 14, 20):
                        for hf in (0.0, -20.0):
                            ff = front[2] if front else fa - fl
                            p = lie_pose(sk, fa, fl, ha, hl, splay, ff, hf)
                            M = sk.fk(p); BP = sk.skin(M, bm); FP = sk.skin(M, fm); HP = sk.skin(M, hm)
                            zb = float(BP[:, 2].min()); zf = float(FP[:, 2].min()); zh = float(HP[:, 2].min())
                            y1 = float(BP[:, 1].max()) - 0.02
                            out = float((HP[:, 1] > y1).mean()) + float((abs(HP[:, 0]) > 0.17).mean())
                            score = 3.0 * zb + 1.0 * zf + 0.3 * zh + 0.25 * out
                            if best is None or score < best[0]: best = (score, zb, zf, zh, out, fa, fl, ha, hl, splay, ff, hf, p)
    _, zb, zf, zh, out, fa, fl, ha, hl, splay, ff, hf, p = best
    info = dict(front_upper=fa, front_knee=fl, hind_upper=ha, hind_knee=hl, splay=splay, front_foot=ff, hind_foot=hf,
                belly_z=round(zb, 4), front_leg_z=round(zf, 4), hind_leg_z=round(zh, 4), legs_outside=round(out, 3))
    print('LIE loaf', info)
    return p, info


def yaw_world(sk, pose, bone, deg):
    """turn a bone about the world vertical through its head (rest frame): R' = Rrest^T Rz Rrest R; +deg = CCW from above
    (a forward-pointing chain turns to +X, the fox's left)"""
    Rr = sk.rest[bone].to_3x3()
    E = Euler(pose[bone][1], 'XYZ').to_matrix()
    pose[bone][1] = list((Rr.transposed() @ Matrix.Rotation(R(deg), 3, 'Z') @ Rr @ E).to_euler('XYZ'))


def curl(sk, base, lp):
    """curl to the fox's left (+X): head first lowered (pitch only, chin at chin_z), then pelvis/spine/neck/head turned
    about the vertical round to the left flank, the tail laid on the ground and wrapped forward along the same flank;
    the whole pose is set down on its lowest vertex (belly on the ground)"""
    p = copy_pose(base); sd = lp['side']
    rot(p, 'Pelvis', y=sd * lp['roll'])
    yaw_world(sk, p, 'Pelvis', sd * lp['pelvis_yaw'])
    yaw_world(sk, p, 'Spine1', sd * lp['spine'][0]); yaw_world(sk, p, 'Spine2', sd * lp['spine'][1])
    for b, a in zip(('Neck1', 'Neck2', 'Head'), lp['neck_yaw']): yaw_world(sk, p, b, sd * a)
    rot(p, 'Head', y=sd * lp['head_roll'])
    ear(p, up=lp['ear_up'], back=lp['ear_back'])
    no_penetration(sk, p, exact=True)            # belly on the ground (head still high)
    A = aim_head_fox(sk, p, lp['chin_z'], share=lp['head_share'], lo=-20.0, hi=100.0)   # pitch in the bone frames
    # tail: Tail1 pitch solved so the tail lies on the ground (lowest tail_z), then swept forward along the same flank
    tm = sk.mask(TAIL); q0 = copy_pose(p)

    def at(a):
        q = copy_pose(q0); rot(q, 'Tail1', x=-a)
        for b, y in zip(TAIL, lp['tail_yaw']): yaw_world(sk, q, b, -sd * y)
        return q, float(sk.skin(sk.fk(q), tm)[:, 2].min())
    lo, hi = -60.0, 100.0
    for _ in range(30):
        m = (lo + hi) / 2; q, z = at(m)
        if z > lp['tail_z']: lo = m
        else: hi = m
    q, z = at(lo)
    no_penetration(sk, q, exact=False)
    info = dict(head_pitch=round(A, 1), tail1_pitch=round(lo, 1), tail_lowest=round(z, 4))
    print('CURL', info)
    return q, info


def aim_head_fox(sk, pose, target_z, share, lo=-30.0, hi=120.0):
    """copy of animal_anim.aim_head with the fox head mask (no Horn bones)"""
    mask = sk.mask(HEADM)
    base = {b: pose[b][1][0] for b, _ in share}

    def f(A):
        for b, s in share: pose[b][1][0] = base[b] + R(A * s)
        return sk.minz(pose, mask)
    grid = [lo + (hi - lo) * i / 60 for i in range(61)]
    vals = [f(A) for A in grid]
    i_min = min(range(61), key=lambda i: vals[i])
    if vals[i_min] > target_z: A = grid[i_min]; f(A); return A
    a, b = lo, grid[i_min]
    for _ in range(40):
        m = (a + b) / 2
        if f(m) > target_z: a = m
        else: b = m
    f(b); return b


def build_clips(sk, sp):
    out = {}; dur = {c: (T, loop) for c, T, loop in sp['clips']}
    setup_ik(sk)
    STAND = stand_pose(sk)

    def loop_static(name, base, overlay, planted=LEGS):
        N = frames_of(dur[name][0]); fr = []
        for f in range(N):
            p = copy_pose(base); overlay(p, f / N); plant(sk, p, planted); fr.append(p)
        fr.append(copy_pose(fr[0])); return fr

    # Idle (4.0 s) "listens": the head turns to the left and holds with a curious tilt while both ears swivel to the
    # sound, comes back, turns a little to the right (ears follow, then one ear flicks), back to centre; small ear
    # twitches in between, 2 breaths, the low tail sways slowly once. All periodic over the loop.
    idl = sp['idle']

    def ov_idle(p, t):
        breathe(sk, p, t, 0.003, 2, 0.8)
        hl = hold(t, 0.06, 0.36, 0.08); hr = hold(t, 0.56, 0.78, 0.07)
        yaw = idl['turn'][0] * hl - idl['turn'][1] * hr
        tilt = idl['tilt'] * hold(t, 0.12, 0.32, 0.06) - 0.6 * idl['tilt'] * hold(t, 0.61, 0.74, 0.05)
        rot(p, 'Neck1', z=0.30 * yaw, x=-1.5 * hl); rot(p, 'Neck2', z=0.30 * yaw, x=-1.0 * hl); rot(p, 'Head', z=0.40 * yaw, y=tilt)
        rot(p, 'Head', x=-1.2 * math.sin(2 * TW * t + 0.7))
        # ears: swivel about their own axis (local y) towards the sound during the turns, + quick twitches (flick back)
        sw = idl['swivel']
        e = sw * (hl - hr)
        tl = flick(t, 0.44, 0.07) + 0.6 * flick(t, 0.90, 0.06); tr = flick(t, 0.82, 0.07)
        rot(p, 'Ear.L', y=e + idl['twitch'] * tl, x=-4.0 * hl + 0.5 * idl['twitch'] * tl, z=3.0 * tl)
        rot(p, 'Ear.R', y=e - idl['twitch'] * tr, x=-4.0 * hr + 0.5 * idl['twitch'] * tr, z=-3.0 * tr)
        s_wave(p, t, idl['tail'], 0.15, pitch=(1.5 * math.sin(TW * t), 0.0, 2.0 * math.sin(TW * t - 0.8)))
        rot(p, 'Pelvis', z=-0.6 * math.sin(TW * t))
    out['Idle'] = dict(frames=loop_static('Idle', STAND, ov_idle), events=[])

    # Walk (1.2 s) "sneaks, low": slow lateral-sequence stalk, body crouched (legs bent), the head stretched forward
    # and low at back height, ears pricked forward, the long tail held low and straight behind with a slow lagged sway,
    # high careful paw lifts with the paw curled back.
    g = sp['gait']['Walk']

    def ov_walk(p, ph, pitch):
        u = g['spine']
        rot(p, 'Spine1', z=u * math.sin(TW * ph), x=0.5 * math.sin(2 * TW * ph))
        rot(p, 'Spine2', z=-u * math.sin(TW * ph - 0.4))
        rot(p, 'Neck1', x=g['neck'][0] - 0.6 * pitch + 0.5 * math.sin(2 * TW * ph - 1.0), z=0.6 * u * math.sin(TW * ph - 0.9))
        rot(p, 'Neck2', x=g['neck'][1])
        rot(p, 'Head', x=g['neck'][2] - 0.4 * pitch - 0.6 * math.sin(2 * TW * ph - 1.3), z=-0.5 * u * math.sin(TW * ph - 1.2))
        s_wave(p, ph, g['tail'], 0.12, pitch=(g['tail_pitch'] + 1.5 * math.sin(2 * TW * ph - 1.5), 0.0, 2.0 * math.sin(2 * TW * ph - 2.2)))
        rot(p, 'Ear.L', x=g['ear_fwd'] + g['ear'] * math.sin(2 * TW * ph - 2.0))
        rot(p, 'Ear.R', x=g['ear_fwd'] + g['ear'] * math.sin(2 * TW * ph - 2.3))
    fr, ev, extra = gait_fox(sk, sp, 'Walk', ov_walk)
    out['Walk'] = dict(frames=fr, events=ev, extra=extra)

    # Lie_Idle (4.0 s): curled up - belly on the ground, legs folded under, spine bent to the left, the head laid on
    # the ground at the flank, the bushy tail wrapped round the front; 2 slow breaths (spine only), ear twitches,
    # the tail tip flicks once, the head lifts a hair once.
    base, info = best_lie(sk, sp['lie'].get('front'))
    LIE, ci = curl(sk, base, sp['lie'])
    info.update(ci)

    def ov_lie(p, t):
        breathe(sk, p, t, 0.0, 2, 1.0)
        rot(p, 'Head', x=-2.0 * hold(t, 0.30, 0.42, 0.06))
        rot(p, 'Ear.L', y=16.0 * flick(t, 0.20, 0.08), x=6.0 * flick(t, 0.20, 0.08))
        rot(p, 'Ear.R', y=-14.0 * flick(t, 0.62, 0.08), x=5.0 * flick(t, 0.62, 0.08))
        rot(p, 'Tail3', z=sp['lie']['side'] * 8.0 * flick(t, 0.75, 0.14))
    out['Lie_Idle'] = dict(frames=loop_static('Lie_Idle', LIE, ov_lie, planted=[]), events=[], extra=dict(lie=info))
    for c, (T, loop) in dur.items():
        out[c]['loop'] = loop; out[c].setdefault('bones', None); out[c].setdefault('extra', {})
    return out
