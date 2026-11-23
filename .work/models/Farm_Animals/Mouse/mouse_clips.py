# mouse_clips.py - SML-03 Mouse clips (ANIMATIONS.md: Idle "sniffs", Scurry "fast tiny steps", Nibble "gnaws food").
# Copy/adaptation of ../Rabbit/rabbit_clips.py (flick, ears, foot_flat, plant_flat, nibble_arms) + the shared gait of
# _common/animal_anim.py (copied as gait_flat: feet keep their world orientation, the abduction would roll the paws).
# Shared helpers from _common/animal_anim.py are imported read-only. The long tail lies on the ground in the rest mesh:
# tail_clear() lifts each tail segment just enough that no tail vertex goes below the ground.
import math, os
import numpy as np
from mathutils import Vector, Matrix
from animal_anim import *
from animal_anim import R, LEGS
import animal_rig as ar

TW = 2 * math.pi
GROUND_TOL = -0.0005         # lowest vertex limit: pack -1 cm (Cow, 2.3 m) scaled to the 0.10 m mouse (-0.43 mm)
TAILS = ('Tail1', 'Tail2', 'Tail3')


def flick(t, c, w):
    """0..1 envelope on the loop phase: fast rise (first 25% of w), slow relax; zero outside [c, c+w)"""
    x = ((t - c) % 1.0) / w
    if x >= 1.0: return 0.0
    return math.sin(0.5 * math.pi * x / 0.25) if x < 0.25 else 0.5 * (1 + math.cos(math.pi * (x - 0.25) / 0.75))


def ears(p, fl=0.0, ol=0.0, sl=0.0, fr=0.0, or_=0.0, sr=0.0):
    """disc ears: f = tilt forward (+) / back (-), o = splay outwards, s = swivel about the ear bone; L and R independent"""
    rot(p, 'Ear.L', x=fl, y=sl, z=-ol); rot(p, 'Ear.R', x=fr, y=-sr, z=or_)


def foot_flat(sk, pose, k, pitch_deg=0.0):
    """foot local rotation so its WORLD orientation = rest orientation pitched by pitch_deg (+ = toe down)"""
    up, lo, ft, _ = ar.LEGS[k]
    M = sk.fk(pose)
    Pm = (M[lo] @ sk.rel[ft]).to_3x3()
    want = Matrix.Rotation(R(pitch_deg), 3, 'X') @ sk.rest[ft].to_3x3()
    pose[ft][1] = list((Pm.inverted() @ want).to_euler('XYZ'))


def plant_flat(sk, pose, legs=None):
    legs = LEGS if legs is None else legs
    plant(sk, pose, legs)
    for k in legs: foot_flat(sk, pose, k)


class TailClear:
    """lift Tail1..3 (pitch, smallest angle) so every tail vertex stays >= floor; sign found once from the rest pose"""
    def __init__(self, sk, floor=0.0002):
        self.sk = sk; self.floor = floor
        # each bone clears its own vertices distal of its head PLUS the child's hidden apex cone that reaches back behind
        # the child's head (it would sink if only the child lifted). Not the whole distal tail: the tip must not lift the
        # root. Tail1's root cap behind its pivot is buried in the rump; the body floor lift covers it in Nibble.
        V = sk.V[:, :3]
        def side(b):
            h = np.array(sk.rest[b].translation); d = np.array(sk.rest[b].to_3x3().col[1]); return (V - h) @ d
        self.masks = []
        for i, b in enumerate(TAILS):
            m = sk.mask([b]) & (side(b) > 0.0)
            if i + 1 < len(TAILS): m = m | (sk.mask([TAILS[i + 1]]) & (side(TAILS[i + 1]) < 0.0))
            self.masks.append(m)
        own = [sk.mask([b]) for b in TAILS]
        meanz = lambda q, m: float(sk.skin(sk.fk(q), m)[:, 2].mean())
        p = new_pose(sk); self.sign = {}
        for i, b in enumerate(TAILS):
            q = new_pose(sk); rot(q, b, x=10.0)
            self.sign[b] = 1.0 if meanz(q, own[i]) > meanz(p, own[i]) else -1.0
        print('TAIL lift signs', self.sign)

    def __call__(self, pose):
        sk = self.sk
        for i, b in enumerate(TAILS):
            m = self.masks[i]
            if sk.minz(pose, m) >= self.floor: continue
            base = pose[b][1][0]; lo, hi = 0.0, 70.0
            for _ in range(14):
                mid = 0.5 * (lo + hi); pose[b][1][0] = base + self.sign[b] * R(mid)
                if sk.minz(pose, m) >= self.floor: hi = mid
                else: lo = mid
            pose[b][1][0] = base + self.sign[b] * R(hi)


def gait_flat(sk, g, tail_fix, overlay=None):
    """copy of animal_anim.gait (trot/walk in place: stance feet move back at speed, swing arcs, body drop per girdle
    from the reach, FFT-smoothed) with flat feet (foot_flat, world pitch = flick) and the tail clearance"""
    T = g['T']; N = frames_of(T); duty = g['duty']; v = g['speed']; S = duty * v * T
    targ = []; need = {'Front': np.zeros(N), 'Hind': np.zeros(N)}
    stance = {k: [] for k in LEGS}
    piv = {k: sk.rest[ar.LEGS[k][0]].translation.copy() for k in LEGS}
    for f in range(N):
        ph = f / N; row = {}
        for k in LEGS:
            p = (ph - g['phases'][k]) % 1.0; G = sk.feet[k]; L3 = sk.length[ar.LEGS[k][2]]
            fl = g['flick'][0 if k.startswith('Front') else 1]
            if p < duty:
                y = G.y - S / 2 + S * p / duty; z = 0.0; hp = 0.0; stance[k].append(f)
            else:
                s = (p - duty) / (1 - duty)
                y = G.y + S / 2 - S * (s - math.sin(2 * math.pi * s) / (2 * math.pi))
                z = g['lift'] * math.sin(math.pi * s) ** 1.3; hp = fl * math.sin(math.pi * s) ** 2
            row[k] = (Vector((G.x, y, z + L3)), hp)
            if p < duty:
                up, lo, ft, front = ar.LEGS[k]; Lm = g.get('reach', 0.97) * (sk.length[up] + sk.length[lo])
                dy = y - piv[k].y; vert = math.sqrt(max(Lm * Lm - dy * dy, 0.0))
                gk = 'Front' if front else 'Hind'
                need[gk][f] = max(need[gk][f], (piv[k].z - (z + L3)) - vert)
        targ.append(row)
    drops = {}
    for gk, a in need.items():
        Fc = np.fft.rfft(a); Fc[3:] = 0; sm = np.fft.irfft(Fc, N)
        sm += max(0.0, float((a - sm).max())); drops[gk] = sm + g['crouch']
    span = piv['HindL'].y - piv['FrontL'].y
    frames = []
    for f in range(N):
        ph = f / N; pose = new_pose(sk)
        df, dh = drops['Front'][f], drops['Hind'][f]
        body(sk, pose, (0, 0, -dh - g['bob'] * (0.5 - 0.5 * math.cos(2 * TW * ph))),
             pitch=math.degrees(math.asin((df - dh) / span)), roll=g.get('roll', 0.0) * math.sin(TW * ph))
        if overlay: overlay(pose, ph)
        for k in LEGS:
            fet, hp = targ[f][k]
            leg_ik(sk, pose, k, fet, R(hp)); foot_flat(sk, pose, k, hp)
        tail_fix(pose)
        frames.append(pose)
    frames.append(copy_pose(frames[0]))
    events = sorted([(round(g['phases'][k] * N) % N, 'Footstep', k) for k in LEGS])
    return frames, events, dict(stance=stance, speed=v, step=S, N=N)


def arms_to(sk, pose, target, a_rng=(-125, 60), b_rng=(-2.5, 170)):
    """front legs by FK (grid search of shoulder/elbow pitch) so the FrontFoot head comes to target (side plane y, z);
    same angles on the right; returns (a, b, dist)"""
    best = None; base = copy_pose(pose)
    for a in np.arange(a_rng[0], a_rng[1] + 0.01, 2.5):
        for b in np.arange(b_rng[0], b_rng[1] + 0.01, 2.5):
            q = copy_pose(base)
            for s in ('L', 'R'):
                q['FrontUpper.' + s][1] = [R(a), 0.0, 0.0]; q['FrontLower.' + s][1] = [R(b), 0.0, 0.0]
            F = sk.fk(q)['FrontFoot.L'].translation
            d = math.hypot(F.y - target[0], F.z - target[1])
            if best is None or d < best[2]: best = (float(a), float(b), d)
    return best


def settle(sk, pose, legs, mask, floor=0.0):
    """move the body vertically so the lowest vertex of mask sits at floor (sitting on the rump), replant legs"""
    for _ in range(6):
        z = sk.minz(pose, mask)
        if abs(z - floor) < 2e-5: break
        raise_body(sk, pose, floor - z); plant_flat(sk, pose, legs)


# ---------------- clip parameters ----------------
SCURRY = dict(T=10.0 / 30.0, duty=0.50, speed=0.13, lift=0.0075,     # review 2026-11-21: step 1 cm -> ~2.2 cm (was invisible)
              flick=(-24.0, 12.0), crouch=0.0, bob=0.0005, roll=1.5, reach=1.0,
              phases={'HindL': 0.0, 'FrontR': 0.0, 'HindR': 0.5, 'FrontL': 0.5})
NIB_BODY = dict(pitch=-42.0, spine1=0.0, spine2=4.0, neck1=20.0, neck2=15.0, head=18.0, tail_lift=24.0, tail_droop=-34.0)
NIB_PAW = (0.0060, -0.0100)         # FrontFoot head target relative to the Nose pivot (y: + = behind it, z: below), m
NIB_IN = 9.0                        # front legs turned inwards (deg) so the paws meet under the chin
NIB_PAW_PITCH = -70.0               # paws turned palms-in/toes-up (deg, - = toe up)


def sit_mask(sk, reach=0.004):
    """what the sitting mouse rests on: body parts + the tail root (Tail1 cap and its first 4 mm past the pivot)"""
    V = sk.V[:, :3]; h = np.array(sk.rest['Tail1'].translation); d = np.array(sk.rest['Tail1'].to_3x3().col[1])
    return sk.mask(['Pelvis', 'Spine1', 'Spine2']) | (sk.mask(['Tail1']) & (((V - h) @ d) < reach))


def nib_pose(sk, t, B0, tail_fix, body_mask, arms=None):
    """Nibble pose at loop phase t: sit on the haunches, hunched back, head bowed, paws at the mouth (FK grid search
    once -> arms), chewing/nose/ears/tail overlays, then tail clearance and a whole-model floor lift"""
    s16 = math.sin(16 * TW * t); s2 = math.sin(2 * TW * t); s4 = math.sin(4 * TW * t)
    pose = new_pose(sk)
    body(sk, pose, (0, 0.002, 0), pitch=B0['pitch'] + 0.8 * s4)
    rot(pose, 'Spine1', x=B0['spine1']); rot(pose, 'Spine2', x=B0['spine2'] + 0.6 * s4)
    rot(pose, 'Neck1', x=B0['neck1'] + 1.0 * math.sin(TW * t)); rot(pose, 'Neck2', x=B0['neck2'])
    rot(pose, 'Head', x=B0['head'] + 1.6 * s16, z=3 * math.sin(TW * t))
    chew(pose, t, 16, open_deg=9.0, side_deg=2.0)
    rot(pose, 'Nose', x=6 * math.sin(8 * TW * t), z=2 * math.sin(8 * TW * t + 1.0))
    ears(pose, fl=-8 + 2 * math.sin(TW * t), ol=10, sl=-6, fr=-7 + 2 * math.sin(TW * t + 1.0), or_=10, sr=-6)
    # tail: Tail1 cancels the pelvis pitch (tail leaves the rump level), Tail2 droops to the ground, Tail2/3 curl to the side
    rot(pose, 'Tail1', x=-(B0['pitch'] + 0.8 * s4) + B0.get('tail_lift', 0.0))
    rot(pose, 'Tail2', x=B0.get('tail_droop', -12.0), z=B0.get('tail_curl', -14.0) + 3 * math.sin(TW * t))
    rot(pose, 'Tail3', x=-8.0, z=B0.get('tail_curl', -14.0) * 1.2 + 5 * math.sin(TW * t - 0.8))
    plant_flat(sk, pose, ['HindL', 'HindR'])
    settle(sk, pose, ['HindL', 'HindR'], body_mask, 0.0002)
    if arms is None:
        M = sk.fk(pose); Nz = M['Nose'].translation
        arms = arms_to(sk, pose, (Nz.y + B0.get('paw', NIB_PAW)[0], Nz.z + B0.get('paw', NIB_PAW)[1]))
    for sx, s in ((1, 'L'), (-1, 'R')):
        pose['FrontUpper.' + s][1] = [R(arms[0] - 2.5 * s2), 0.0, R(NIB_IN * sx)]
        pose['FrontLower.' + s][1] = [R(arms[1] + 5.5 + 4.0 * s2 + 1.5 * s16), R(4 * s2 * sx), 0.0]
        foot_flat(sk, pose, 'Front' + s, NIB_PAW_PITCH + 6 * s2)
    if os.environ.get('MOUSE_DBG'):
        for tag in ('before tail_fix', 'after tail_fix'):
            V = sk.skin(sk.fk(pose)); i = int(np.argmin(V[:, 2]))
            print('DBG', tag, 'minz', round(float(V[i, 2]), 5), 'bone', sk.order[int(np.argmax(sk.W[i]))], 'at', V[i].round(4),
                  'tail x', [round(math.degrees(pose[b][1][0]), 1) for b in TAILS])
            if tag == 'before tail_fix': tail_fix(pose)
    else:
        tail_fix(pose)
    for _ in range(4):                  # whole-model floor: the sitting rump/tail root may not go below the ground
        z = sk.minz(pose)
        if z >= 0.0: break
        raise_body(sk, pose, -z + 1e-5); plant_flat(sk, pose, ['HindL', 'HindR'])
        for s in ('L', 'R'): foot_flat(sk, pose, 'Front' + s, NIB_PAW_PITCH + 6 * s2)
    return pose, arms


def build_clips(sk, sp):
    out = {}; dur = {c: (T, loop) for c, T, loop in sp['clips']}
    tail_fix = TailClear(sk)
    body_mask = sit_mask(sk)

    # ---- Idle (3 s): crouched stand, fast shallow breathing (6x), 3 sniff bursts: head lifts/stretches forward, nose
    # twitches at ~7.5 Hz, jaw quivers; ears swivel independently; small look left/right; tail slow S sway on the ground
    STAND = new_pose(sk); body(sk, STAND, (0, 0, -0.0008)); plant_flat(sk, STAND)
    SNIFF = [(0.05, 0.22), (0.40, 0.18), (0.70, 0.22)]

    def ov_idle(p, t):
        breathe(sk, p, t, 0.00035, 6, 0.8)
        sn = sum(flick(t, c, w) for c, w in SNIFF)
        look = math.sin(TW * t)
        rot(p, 'Neck1', x=-7 * sn + 1.0 * math.sin(TW * t + 0.4), z=5.0 * look)
        rot(p, 'Neck2', x=-4 * sn, z=3.0 * look)
        rot(p, 'Head', x=-5 * sn - 1.5 * math.sin(2 * TW * t + 1.0), z=5.0 * math.sin(TW * t - 0.6), y=3 * sn * math.sin(TW * t))
        raise_body(sk, p, 0.0010 * sn)
        tw = 0.25 + sn
        rot(p, 'Nose', x=8 * tw * math.sin(22 * TW * t), z=3 * tw * math.sin(22 * TW * t + 1.2))
        rot(p, 'Jaw', x=2.5 * sn * (0.5 - 0.5 * math.cos(22 * TW * t)))
        ears(p, fl=4 * sn + 2 * math.sin(TW * t) - 10 * flick(t, 0.30, 0.14),
             ol=2 + 3 * math.sin(TW * t + 0.5), sl=-14 * flick(t, 0.55, 0.18) + 6 * sn,
             fr=4 * sn + 2 * math.sin(TW * t + 1.7) - 12 * flick(t, 0.86, 0.12),
             or_=2 + 3 * math.sin(TW * t + 2.2), sr=-16 * flick(t, 0.62, 0.20) + 6 * sn)
        rot(p, 'Tail1', z=6 * math.sin(TW * t)); rot(p, 'Tail2', z=8 * math.sin(TW * t - 0.6))
        rot(p, 'Tail3', z=12 * math.sin(TW * t - 1.2) + 6 * flick(t, 0.5, 0.2) * math.sin(4 * TW * t))
    N = frames_of(dur['Idle'][0]); fr = []
    for f in range(N):
        p = copy_pose(STAND); ov_idle(p, f / N); plant_flat(sk, p); tail_fix(p); fr.append(p)
    fr.append(copy_pose(fr[0]))
    out['Idle'] = dict(frames=fr, events=[(round(c * N) % N, 'Sniff', '') for c, _ in SNIFF])

    # ---- Scurry (1/3 s = 10 frames, trot pairs, in place; Animator root speed 0.11 m/s): low body, head forward and
    # level, quick nods, ears back, tail held just off the ground and swaying
    def ov_scurry(p, ph):
        rot(p, 'Spine1', x=1.5 * math.sin(2 * TW * ph)); rot(p, 'Spine2', x=-1.0 * math.sin(2 * TW * ph + 0.6))
        rot(p, 'Neck1', x=4 + 3 * math.sin(2 * TW * ph - 1.2)); rot(p, 'Head', x=-6 - 1.5 * math.sin(2 * TW * ph - 1.2))
        rot(p, 'Nose', x=5 * math.sin(2 * TW * ph))
        ears(p, fl=-16 + 3 * math.sin(2 * TW * ph - 2.0), ol=6, fr=-16 + 3 * math.sin(2 * TW * ph - 2.3), or_=6)
        rot(p, 'Tail1', x=6, z=7 * math.sin(TW * ph)); rot(p, 'Tail2', z=10 * math.sin(TW * ph - 0.9))
        rot(p, 'Tail3', z=14 * math.sin(TW * ph - 1.8))
    fr, ev, extra = gait_flat(sk, SCURRY, tail_fix, ov_scurry)
    out['Scurry'] = dict(frames=fr, events=ev, extra=extra)

    # ---- Nibble (2 s): sits up on the haunches (body 30 + 19 deg chest up, rump on the ground), head bowed to the paws,
    # front paws held together in front of the mouth (FK grid search), jaw gnaws 16x (8 Hz), nose twitches, paws turn the
    # (imaginary) seed: small rotation/bob 2x per loop, ears relaxed out, tail curled forward on the ground
    N = frames_of(dur['Nibble'][0]); fr = []; gap = []; arms = None
    for f in range(N):
        pose, arms = nib_pose(sk, f / N, NIB_BODY, tail_fix, body_mask, arms)
        M = sk.fk(pose)
        gap.append(round((M['FrontFoot.L'].translation - M['Nose'].translation).length, 4))
        fr.append(pose)
    fr.append(copy_pose(fr[0]))
    out['Nibble'] = dict(frames=fr, events=[(0, 'Nibble', 'Start')],
                         extra=dict(paw_to_nose_m=[min(gap), max(gap)], arm_search=[round(x, 4) for x in arms]))
    for c, (T, loop) in dur.items():
        out[c]['loop'] = loop; out[c].setdefault('bones', None); out[c].setdefault('extra', {})
    return out


# Nibble pose candidates for `rig_mouse.py -- SML-03 pose` (overrides of NIB_BODY; dict() = the chosen one)
NIB_CANDIDATES = [dict(pitch=-36.0, spine1=-14.0, spine2=-14.0, neck1=30.0, neck2=25.0, head=30.0),
                  dict(),
                  dict(pitch=-45.0, spine1=4.0, spine2=8.0, neck1=18.0, neck2=14.0, head=16.0),
                  dict(pitch=-40.0, spine1=-4.0, spine2=0.0, neck1=24.0, neck2=18.0, head=22.0, paw=(0.004, -0.012))]
