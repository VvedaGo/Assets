# ram_clips.py - LIV-12 Ram clips (ANIMATIONS.md: Idle "stands", Walk "walks", Graze "grazes"). Copied from ../Sheep/sheep_clips.py;
# change: the Graze search also keeps the horn curls >= 3 cm above the ground (Horn.L/R bones follow the head).
# Shared helpers from _common/animal_anim.py are imported read-only; gait() is copied here with an overlay hook that runs
# BEFORE the leg IK (head bob, lagged wool bounce on Spine1/Spine2, ears, 2-bone tail), so the feet stay planted.
import math
import numpy as np
from mathutils import Vector
from animal_anim import *
from animal_anim import R, LEGS
import animal_rig as ar

TW = 2 * math.pi


def flick(t, c, w):
    """0..1 envelope on the loop phase: fast rise (first 25% of w), slow relax; zero outside [c, c+w)"""
    x = ((t - c) % 1.0) / w
    if x >= 1.0: return 0.0
    return math.sin(0.5 * math.pi * x / 0.25) if x < 0.25 else 0.5 * (1 + math.cos(math.pi * (x - 0.25) / 0.75))


def gait_sheep(sk, sp, name, overlay):
    """copy of animal_anim.gait (feet move back at speed in stance, swing arcs, body height per girdle from reach)
    with overlay(pose, phase) applied before the leg IK and a 2-bone tail"""
    g = sp['gait'][name]; T = g['T']; N = frames_of(T); duty = g['duty']; v = g['speed']; S = duty * v * T
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
                z = g['lift'] * math.sin(math.pi * s) ** 1.3; hp = R(fl) * math.sin(math.pi * s) ** 2
            row[k] = (Vector((G.x, y, z + L3)), hp, p < duty)
            if p < duty:
                up, lo, ft, front = ar.LEGS[k]; Lm = 0.985 * (sk.length[up] + sk.length[lo])
                dy = y - piv[k].y; vert = math.sqrt(max(Lm * Lm - dy * dy, 0.0))
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
        body(sk, pose, (0, 0, -dh), pitch=math.degrees(math.asin((df - dh) / span)), roll=g['roll'] * math.sin(TW * ph))
        overlay(pose, ph)
        for k in LEGS:
            fet, hp, st = targ[f][k]
            leg_ik(sk, pose, k, fet, hp)
        frames.append(pose)
    frames.append(copy_pose(frames[0]))
    events = sorted([(round(g['phases'][k] * N) % N, 'Footstep', k) for k in LEGS])
    return frames, events, dict(stance=stance, speed=v, step=S, N=N, drops={k: [round(float(x), 4) for x in d] for k, d in drops.items()})


def build_clips(sk, sp):
    out = {}; dur = {c: (T, loop) for c, T, loop in sp['clips']}
    STAND = stand_pose(sk)

    def loop_static(name, base, overlay, planted=LEGS):
        N = frames_of(dur[name][0]); fr = []
        for f in range(N):
            p = copy_pose(base); overlay(p, f / N); plant(sk, p, planted); fr.append(p)
        fr.append(copy_pose(fr[0])); return fr

    # Idle (3 s): 2 slow breaths lifting the body and the wool (Pelvis + Spine1/2 pitch), small head drift, ears flick in
    # turn (left 0.15, right 0.48, small left twitch 0.80), short tail wiggle with a quick burst at 0.62. All terms periodic.
    def ov_idle(p, t):
        breathe(sk, p, t, 0.005, 2, 1.3)
        rot(p, 'Neck1', x=1.5 * math.sin(TW * t + 0.4)); rot(p, 'Head', x=-1.0 * math.sin(2 * TW * t + 1.0), z=3.0 * math.sin(TW * t))
        fl = flick(t, 0.15, 0.10) + 0.5 * flick(t, 0.80, 0.08); fr_ = flick(t, 0.48, 0.10)
        rot(p, 'Ear.L', x=-2 + 2 * math.sin(TW * t) + 14 * fl, z=-(3 * math.sin(TW * t + 0.5)) + 28 * fl)
        rot(p, 'Ear.R', x=-2 + 2 * math.sin(TW * t + 1.7) + 14 * fr_, z=-(-3 * math.sin(TW * t + 2.2) + 28 * fr_))
        x = ((t - 0.62) % 1.0) / 0.16; burst = math.sin(2 * TW * x) * math.sin(math.pi * x) if x < 1.0 else 0.0
        rot(p, 'Tail1', x=3 * math.sin(TW * 2 * t), z=4 * math.sin(TW * 3 * t) + 14 * burst)
        rot(p, 'Tail2', z=6 * math.sin(TW * 3 * t - 0.8) + 20 * burst)
    out['Idle'] = dict(frames=loop_static('Idle', STAND, ov_idle), events=[])

    # Walk (0.9 s): quick lateral-sequence walk, short steps; head bob twice per cycle, wool (Spine1/Spine2) bounces with a
    # lag behind the body bob, ears and tail swing
    g = sp['gait']['Walk']

    def ov_walk(p, ph):
        nod = g['nod'] * math.sin(TW * 2 * ph - 1.2)
        rot(p, 'Neck1', x=0.6 * nod, z=1.5 * math.sin(TW * ph - 0.6)); rot(p, 'Head', x=-0.3 * nod)
        rot(p, 'Spine1', x=g['wool'] * math.sin(TW * 2 * ph - 2.0)); rot(p, 'Spine2', x=-0.8 * g['wool'] * math.sin(TW * 2 * ph - 2.6))
        rot(p, 'Tail1', x=2 * math.sin(TW * 2 * ph - 1.5), z=g['tail'][0] * math.sin(TW * ph - 0.4))
        rot(p, 'Tail2', z=g['tail'][1] * math.sin(TW * ph - 0.9))
        ear(p, up=g['ear'] * math.sin(TW * 2 * ph - 2.0), back=-3.0 + 0.5 * g['ear'] * math.sin(TW * 2 * ph - 2.6))
    fr, ev, extra = gait_sheep(sk, sp, 'Walk', ov_walk)
    out['Walk'] = dict(frames=fr, events=ev, extra=extra)

    # Graze (ANIMATIONS.md "pasyotsya", 4 s loop): FrontL 6 cm forward, body slightly lower and nose-down, neck pitched down
    # + small Neck1 reach (keyed location, Graze only) so the muzzle is ~2 cm above the ground in front of the hooves;
    # bite tugs, jaw chewing, one short head lift, ears flick, tail wiggle, breathing through the wool. All periodic.
    if 'Graze' in dur:
        gz = sp['graze']
        eat = copy_pose(STAND); body(sk, eat, (0, -0.01, -gz['drop']), pitch=gz['pitch'])
        feet = {'FrontL': sk.feet['FrontL'] + Vector((0, -gz['foot_fwd'], 0))}
        plant(sk, eat, None, feet)
        hm = sk.mask(['Head', 'Jaw']); hn = sk.mask(['Horn.L', 'Horn.R']); base = {bn: eat[bn][1][0] for bn in ('Neck1', 'Neck2', 'Head')}
        yfront = min(sk.feet['FrontL'].y - gz['foot_fwd'], sk.feet['FrontR'].y) - 0.02; cand = []
        for r10 in range(0, 23, 2):
            eat['Neck1'][0] = [0.0, 0.0, r10 / 100.0]
            for n in range(0, 151, 5):
                for h in range(-40, 61, 5):      # >= -40: the overlay adds up to -8 (head lift + tug), limit -50
                    eat['Neck1'][1][0] = base['Neck1'] + R(0.6 * n); eat['Neck2'][1][0] = base['Neck2'] + R(0.4 * n)
                    eat['Head'][1][0] = base['Head'] + R(h)
                    M_ = sk.fk(eat); P_ = sk.skin(M_, hm); z = float(P_[:, 2].min()); yb = float(P_[:, 1].max()); zh = float(sk.skin(M_, hn)[:, 2].min())
                    ya = M_['Head'].to_3x3().col[1]; down = math.degrees(math.atan2(-ya.z, -ya.y))   # head axis below the forward horizontal
                    if yb < yfront and z >= gz['muzzle_z'] and zh >= 0.03 and gz['head_down'][0] <= down <= gz['head_down'][1]:
                        cand.append((round(z - gz['muzzle_z'], 2), r10, n, abs(h), h, z, down))
        _, r_, n_, _, h_, z_, dn_ = min(cand)
        eat['Neck1'][0] = [0.0, 0.0, r_ / 100.0]
        eat['Neck1'][1][0] = base['Neck1'] + R(0.6 * n_); eat['Neck2'][1][0] = base['Neck2'] + R(0.4 * n_); eat['Head'][1][0] = base['Head'] + R(h_)
        print('GRAZE reach', r_ / 100.0, 'neck pitch', n_, 'head pitch', h_, 'muzzle min z', round(z_, 3), 'head axis down deg', round(dn_, 1), 'candidates', len(cand))

        def ov_graze(p, t):
            lift = 0.5 * (1 - math.cos(TW * ((t - 0.55) % 1.0) / 0.25)) if (t - 0.55) % 1.0 < 0.25 else 0.0   # 1 s head lift
            rot(p, 'Neck1', x=-12 * lift); rot(p, 'Neck2', x=-6 * lift); rot(p, 'Head', x=-5 * lift)
            tug = (1 - lift) * max(0.0, math.sin(TW * 5 * t)) ** 2                            # 5 bite tugs while down
            rot(p, 'Head', x=-3.0 * tug, z=1.5 * math.sin(TW * t))
            chew(p, t, 10, 9, 3)                                                             # 10 chews / 4 s
            breathe(sk, p, t, 0.004, 2, 1.0)
            fl = flick(t, 0.20, 0.10); fr2 = flick(t, 0.72, 0.10)
            rot(p, 'Ear.L', x=-6 + 14 * fl, z=6 + 26 * fl); rot(p, 'Ear.R', x=-6 + 14 * fr2, z=-(6 + 26 * fr2))
            x = ((t - 0.40) % 1.0) / 0.15; burst = math.sin(2 * TW * x) * math.sin(math.pi * x) if x < 1.0 else 0.0
            rot(p, 'Tail1', z=4 * math.sin(TW * 2 * t) + 12 * burst); rot(p, 'Tail2', z=6 * math.sin(TW * 2 * t - 0.8) + 18 * burst)
        Ng = frames_of(dur['Graze'][0]); fr = []
        for f in range(Ng):
            p = copy_pose(eat); ov_graze(p, f / Ng); plant(sk, p, None, feet); fr.append(p)
        fr.append(copy_pose(fr[0])); out['Graze'] = dict(frames=fr, events=[], extra=dict(reach=r_ / 100.0, neck=n_, head=h_, muzzle_z=z_))
    for c, (T, loop) in dur.items():
        out[c]['loop'] = loop; out[c].setdefault('bones', None); out[c].setdefault('extra', {})
    return out


LOC_BONES = ('Pelvis', 'Neck1')


def write_action_loc(rig, name, frames, loop, bones=None):
    """copy of animal_anim.write_action that also keys Neck1 location (Graze neck reach); used for Graze only"""
    import bpy
    from bpy_extras import anim_utils
    old = bpy.data.actions.get(name)
    if old: bpy.data.actions.remove(old)
    act = bpy.data.actions.new(name); act.use_fake_user = True
    slot = act.slots.new(id_type='OBJECT', name=rig.name)
    cb = anim_utils.action_ensure_channelbag_for_slot(act, slot)
    N = len(frames) - 1
    for bn in (bones or [n for n in frames[0]]):
        chans = [('rotation_euler', 1)] + ([('location', 0)] if bn in LOC_BONES else [])
        for path, ix in chans:
            for i in range(3):
                fc = cb.fcurves.new(f'pose.bones["{bn}"].{path}', index=i, group_name=bn)
                fc.keyframe_points.add(N + 1)
                co = []
                for f, p in enumerate(frames): co += [float(f), p[bn][ix][i]]
                fc.keyframe_points.foreach_set('co', co)
                fc.keyframe_points.foreach_set('interpolation', [1] * (N + 1))
                fc.update()
    act.use_frame_range = True; act.frame_start = 0; act.frame_end = N; act.use_cyclic = loop
    return act
