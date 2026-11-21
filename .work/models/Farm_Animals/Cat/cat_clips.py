# cat_clips.py - PET-02 Cat clips (planning/FarmAnimals/ANIMATIONS.md: Idle "moves its tail", Walk "walks",
# Lie_Idle "lies, breathes"). Shared helpers from _common/animal_anim.py are imported read-only (nothing modified there).
# The cat legs rest straight (vertical bone chains), so the shared analytic leg_ik is used as on the Cow.
import math
import numpy as np
from mathutils import Vector
from animal_anim import *
from animal_anim import R, LEGS
import animal_rig as ar

TW = 2 * math.pi
TAIL_WAVES = 2              # Idle: 2 slow S-waves in 3.5 s (integer -> closed loop)
FRONT_LEGS = ['FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', 'FrontUpper.R', 'FrontLower.R', 'FrontFoot.R']
HIND_LEGS = ['HindUpper.L', 'HindLower.L', 'HindFoot.L', 'HindUpper.R', 'HindLower.R', 'HindFoot.R']
BODY = ['Pelvis', 'Spine1', 'Spine2']
TAIL = ['Tail1', 'Tail2', 'Tail3']


def flick(t, c, w):
    """0..1 envelope on the loop phase: fast rise (first 25% of w), slow relax; zero outside [c, c+w)"""
    x = ((t - c) % 1.0) / w
    if x >= 1.0: return 0.0
    return math.sin(0.5 * math.pi * x / 0.25) if x < 0.25 else 0.5 * (1 + math.cos(math.pi * (x - 0.25) / 0.75))


def s_wave(p, ph, amps, lag, pitch=(0.0, 0.0, 0.0)):
    """travelling lateral wave up Tail1-3 (each bone `lag` of a cycle later) -> the held-up tail draws slow S-curves"""
    for i, (b, a) in enumerate(zip(TAIL, amps)):
        rot(p, b, x=pitch[i], z=a * math.sin(TW * (ph - lag * i)))


def ears(p, t, events, amp=22.0):
    """ear twitches: events [(side, centre, width, strength)] -> quick flick back/out, slow relax"""
    for side, c, w, k in events:
        e = k * flick(t, c, w); sg = 1 if side == 'L' else -1
        rot(p, 'Ear.' + side, x=amp * 0.6 * e, z=sg * amp * e)


def gait_cat(sk, sp, name, overlay):
    """copy of animal_anim.gait (via ../Dog/dog_clips.gait_dog): overlay applied BEFORE the leg IK, feet placed closer to
    the midline (cats put their paws nearly in a line), stance reach as a parameter"""
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
        sm += max(0.0, float((a - sm).max())); drops[gk] = sm + g['crouch']
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


# ---------------- lying pose (loaf: front paws tucked under the chest, hind legs folded beside the belly) ----------------
def lie_pose_cat(sk, fa, fl, ha, hl, splay, pitch, ff=0.0, hf=0.0):
    p = new_pose(sk)
    body(sk, p, (0, 0.0, -0.12), pitch=pitch)
    for s, sg in (('L', 1), ('R', -1)):
        rot(p, 'FrontUpper.' + s, x=-fa, z=-2 * sg); rot(p, 'FrontLower.' + s, x=fl); rot(p, 'FrontFoot.' + s, x=ff)
        rot(p, 'HindUpper.' + s, x=ha, z=-splay * sg); rot(p, 'HindLower.' + s, x=-hl); rot(p, 'HindFoot.' + s, x=hf)
    rot(p, 'Neck1', x=-pitch - 4); rot(p, 'Head', x=2)
    no_penetration(sk, p, exact=True)
    return p


def best_lie(sk):
    """grid search. The belly must rest ON the ground (lowest body vertex <= 2 mm after the whole pose is set down on its
    lowest vertex), the folded legs tuck under / lie along the body: leg vertices below the belly or sticking out in
    front of the chest / behind the rump are penalised, and the visible leg ends (paws) must not hover."""
    # Rework (ANIMATION_FIXES 2): the old grid only tried the hind upper FORWARD (-50..10); the winner (-35, hock -150)
    # folded the metatarsus + paw straight UP, so the cream paw stuck out of the flank at the hip as a light rectangle with
    # a dark sole line. Now the hind upper goes BACK (hip -> hock behind, low), the metatarsus folds forward along the
    # ground beside the belly (real loaf), and paws above 40% of the lying body height are penalised. Pose values judged
    # on rendered side / 3/4 / front close-ups.
    bm = sk.mask(BODY); fm = sk.mask(FRONT_LEGS); hm = sk.mask(HIND_LEGS); best = None
    pm = sk.mask(['HindFoot.L', 'HindFoot.R', 'FrontFoot.L', 'FrontFoot.R'])
    # paws: front foot -60 (paw lies flat, sole down; with +20 it stood upright and its dark sole showed as a dark line at
    # the chest), hind foot +60..90 (paw flat on the ground in front of the hock, sole down)
    for fa in (60, 75):
        for fl in (150, 165):
            for ha in (35, 45, 55):
                for hl in (130, 140, 150):
                    for splay in (20, 25):
                        for ff, hf in ((-60.0, 90.0), (-60.0, 60.0), (-45.0, 90.0)):
                            p = lie_pose_cat(sk, fa, fl, ha, hl, splay, 0.0, ff, hf)
                            M = sk.fk(p); BP = sk.skin(M, bm); FP = sk.skin(M, fm); HP = sk.skin(M, hm); PP = sk.skin(M, pm)
                            zb = float(BP[:, 2].min()); zf = float(FP[:, 2].min()); zh = float(HP[:, 2].min())
                            y0 = float(BP[:, 1].min()) + 0.01; y1 = float(BP[:, 1].max()) - 0.02
                            out = float((FP[:, 1] < y0).mean()) + float((HP[:, 1] > y1).mean())
                            hb = float(BP[:, 2].max()) - zb
                            paw_up = max(0.0, float(PP[:, 2].max()) - zb - 0.4 * hb)
                            score = 3.0 * zb + 0.3 * zf + 0.3 * zh + 0.25 * out + 3.0 * paw_up
                            if best is None or score < best[0]: best = (score, zb, zf, zh, out, fa, fl, ha, hl, splay, ff, hf, p)
    _, zb, zf, zh, out, fa, fl, ha, hl, splay, ff, hf, p = best
    sink = min(zb, 0.008)                    # set the belly down; folded legs may sink <= 8 mm into the ground (grass)
    if sink > 0: raise_body(sk, p, -sink); zb -= sink; zf -= sink; zh -= sink
    info = dict(front_upper=fa, front_knee=fl, hind_upper=ha, hind_knee=hl, splay=splay, front_foot=ff, hind_foot=hf,
                sink_m=round(sink, 4), belly_z=round(zb, 4), front_leg_z=round(zf, 4), hind_leg_z=round(zh, 4), legs_outside=round(out, 3))
    print('LIE', info)
    return p, info


def curl_tail(sk, p, side=1):
    """tail laid down and curled round the left flank: Tail1 pitch solved so the tail rests on the ground (lowest ~3 mm)"""
    tm = sk.mask(TAIL); base = copy_pose(p)

    def at(a):
        q = copy_pose(base); rot(q, 'Tail1', x=-a, z=side * 55); rot(q, 'Tail2', z=side * 55); rot(q, 'Tail3', z=side * 45)
        return q, float(sk.skin(sk.fk(q), tm)[:, 2].min())
    lo, hi = 0.0, 105.0
    for _ in range(30):
        m = (lo + hi) / 2; q, z = at(m)
        if z > 0.003: lo = m
        else: hi = m
    q, z = at(lo); print(f'TAIL lying pitch {lo:.1f} deg, tail lowest {z:.4f}')
    return q, lo


def build_clips(sk, sp):
    out = {}; dur = {c: (T, loop) for c, T, loop in sp['clips']}
    STAND = stand_pose(sk)

    def loop_static(name, base, overlay, planted=LEGS):
        N = frames_of(dur[name][0]); fr = []
        for f in range(N):
            p = copy_pose(base); overlay(p, f / N); plant(sk, p, planted); fr.append(p)
        fr.append(copy_pose(fr[0])); return fr

    # Idle (3.5 s): standing; the raised tail draws 2 slow S-curves (a wave travels up Tail1-3 with a lag, the tip also
    # curls forward/back a little) - the main feature; 2 breaths; the head turns a little left and back; ear twitches
    # L 0.16, R 0.47, L small 0.78; the rump answers the tail with a tiny sway. All periodic over the loop.
    idl = sp['idle']

    def ov_idle(p, t):
        breathe(sk, p, t, 0.0025, 2, 0.8)
        w = TAIL_WAVES * t
        s_wave(p, w, idl['tail'], idl['lag'], pitch=(2.0 * math.sin(TW * w + 0.5), 3.0 * math.sin(TW * w - 0.3),
                                                      6.0 * math.sin(TW * w - 1.1)))
        rot(p, 'Pelvis', z=-idl['hip'] * math.sin(TW * w))
        rot(p, 'Neck1', x=1.0 * math.sin(TW * t + 0.4), z=3.0 * math.sin(TW * t - 0.3))
        rot(p, 'Head', x=-1.5 * math.sin(2 * TW * t + 1.0), z=7.0 * math.sin(TW * t))
        ears(p, t, [('L', 0.16, 0.08, 1.0), ('R', 0.47, 0.08, 1.0), ('L', 0.78, 0.06, 0.6)], idl['ear'])
    out['Idle'] = dict(frames=loop_static('Idle', STAND, ov_idle), events=[])

    # Walk (0.8 s): soft lateral-sequence walk (HindL, FrontL, HindR, FrontR), paws placed close to the midline, the back
    # undulates (Spine1/Spine2 yaw in opposition + light roll), the head held level (neck counters the body pitch), the
    # tail held up with a gentle lagged sway, ears bob lightly.
    g = sp['gait']['Walk']

    def ov_walk(p, ph, pitch):
        u = g['spine']
        rot(p, 'Spine1', z=u * math.sin(TW * ph), x=0.6 * math.sin(2 * TW * ph))
        rot(p, 'Spine2', z=-u * math.sin(TW * ph - 0.4))
        rot(p, 'Neck1', x=-0.6 * pitch + 0.5 * math.sin(2 * TW * ph - 1.0), z=0.8 * u * math.sin(TW * ph - 0.9))
        rot(p, 'Head', x=-0.4 * pitch - 0.6 * math.sin(2 * TW * ph - 1.3), z=-0.6 * u * math.sin(TW * ph - 1.2))
        s_wave(p, ph, g['tail'], 0.12, pitch=(2.0 * math.sin(2 * TW * ph - 1.5), 0.0, 3.0 * math.sin(2 * TW * ph - 2.2)))
        rot(p, 'Ear.L', x=g['ear'] * math.sin(2 * TW * ph - 2.0)); rot(p, 'Ear.R', x=g['ear'] * math.sin(2 * TW * ph - 2.3))
    fr, ev, extra = gait_cat(sk, sp, 'Walk', ov_walk)
    out['Walk'] = dict(frames=fr, events=ev, extra=extra)

    # Lie_Idle (4.0 s): ready loaf pose (belly on the ground, front paws tucked under the chest, hind legs folded beside the
    # belly), head up, tail laid round the left flank; 2 slow breaths (spine only, the belly stays on the ground), the head
    # drifts a little, ear twitches, the tail tip flicks twice.
    LIE, info = best_lie(sk)
    LIE, tail_a = curl_tail(sk, LIE, -1)
    info['tail1_pitch'] = round(tail_a, 1)

    def ov_lie(p, t):
        breathe(sk, p, t, 0.0, 2, 1.2)
        rot(p, 'Neck1', x=1.2 * math.sin(TW * t)); rot(p, 'Head', x=-1.0 * math.sin(TW * t + 0.8), z=5.0 * math.sin(TW * t + 0.3))
        ears(p, t, [('R', 0.22, 0.08, 1.0), ('L', 0.58, 0.08, 0.8)], sp['idle']['ear'])
        rot(p, 'Tail3', z=-12.0 * (flick(t, 0.40, 0.12) + flick(t, 0.86, 0.10)))
    out['Lie_Idle'] = dict(frames=loop_static('Lie_Idle', LIE, ov_lie, planted=[]), events=[], extra=dict(lie=info))
    for c, (T, loop) in dur.items():
        out[c]['loop'] = loop; out[c].setdefault('bones', None); out[c].setdefault('extra', {})
    return out
