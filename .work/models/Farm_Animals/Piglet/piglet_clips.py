# pig_clips.py - LIV-07 Piglet clips (ANIMATIONS.md: Idle "stands", Walk "walks", Root "roots the ground with the snout").
# Shared helpers from _common/animal_anim.py are imported read-only. gait_piglet() is the Sheep gait copy (overlay applied
# BEFORE the leg IK, so the feet stay planted); write_action_loc keys Neck1 location in every take (Root reach) as the Sheep.
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


def burst(t, c, w, n=2):
    """n fast oscillations inside a window [c, c+w) of the loop phase, zero elsewhere"""
    x = ((t - c) % 1.0) / w
    return math.sin(n * TW * x) * math.sin(math.pi * x) if x < 1.0 else 0.0


def gait_piglet(sk, sp, name, overlay):
    """copy of the Sheep gait (animal_anim.gait + overlay hook before the leg IK)"""
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


def tail_curl(p, x1=0.0, z1=0.0, x2=0.0, z2=0.0, x3=0.0, z3=0.0):
    rot(p, 'Tail1', x=x1, z=z1); rot(p, 'Tail2', x=x2, z=z2); rot(p, 'Tail3', x=x3, z=z3)


def build_clips(sk, sp):
    out = {}; dur = {c: (T, loop) for c, T, loop in sp['clips']}
    STAND = stand_pose(sk)

    def loop_static(name, base, overlay, planted=LEGS, feet=None):
        N = frames_of(dur[name][0]); fr = []
        for f in range(N):
            p = copy_pose(base); overlay(p, f / N); plant(sk, p, planted, feet); fr.append(p)
        fr.append(copy_pose(fr[0])); return fr

    # Idle (3.0 s): 2 breaths, small head drift, 2 sniff bursts (quick small head nods = the snout sniffs), ears flick UP
    # in turn (L 0.18, R 0.52, small L twitch 0.84), curly tail twitches (bursts 0.35 and 0.75). All terms periodic.
    def ov_idle(p, t):
        breathe(sk, p, t, 0.004, 2, 1.0)
        rot(p, 'Neck1', x=1.2 * math.sin(TW * t + 0.4)); rot(p, 'Head', x=-1.5 * math.sin(TW * t + 1.0), z=3.0 * math.sin(TW * t))
        sn = burst(t, 0.06, 0.10, 4) + burst(t, 0.60, 0.09, 3)
        rot(p, 'Head', x=2.2 * sn, y=0.0)
        fl = flick(t, 0.18, 0.12) + 0.5 * flick(t, 0.84, 0.08); fr_ = flick(t, 0.52, 0.12)
        rot(p, 'Ear.L', x=-12 * fl + 2 * math.sin(TW * t), z=10 * fl)
        rot(p, 'Ear.R', x=-12 * fr_ + 2 * math.sin(TW * t + 1.7), z=-10 * fr_)
        tw = burst(t, 0.35, 0.10, 2) + 0.7 * burst(t, 0.75, 0.08, 2)
        tail_curl(p, x1=2 * math.sin(TW * t), z1=4 * math.sin(TW * 2 * t) + 16 * tw, z2=8 * tw, x3=6 * tw)
    out['Idle'] = dict(frames=loop_static('Idle', STAND, ov_idle), events=[])

    # Walk (0.6 s): tiny quick lateral-sequence steps ("семенит"); body roll (waddle) + small yaw sway with Spine counter-sway,
    # head bob twice per cycle, ears bounce with a lag, the tail curl bobs
    g = sp['gait']['Walk']

    def ov_walk(p, ph):
        rot(p, 'Pelvis', z=g['sway'] * math.sin(TW * ph - 0.6))
        pass                                                      # no Spine2 counter-sway: rigid body segments would open seams
        nod = g['nod'] * math.sin(TW * 2 * ph - 1.2)
        rot(p, 'Neck1', x=0.5 * nod, z=-1.0 * math.sin(TW * ph - 0.6)); rot(p, 'Head', x=-0.2 * nod)
        # ear bounce: tips only lift (negative pitch) and fall back to rest, so the drooping flaps never swing into the face
        eL = -0.5 * g['ear'] * (1 - math.cos(TW * 2 * ph - 2.0)); eR = -0.5 * g['ear'] * (1 - math.cos(TW * 2 * ph - 2.3))
        rot(p, 'Ear.L', x=eL, z=-0.3 * eL); rot(p, 'Ear.R', x=eR, z=0.3 * eR)
        tail_curl(p, x1=g['tail'][0] * math.sin(TW * 2 * ph - 1.5), z1=g['tail'][1] * math.sin(TW * ph - 0.4),
                  x2=0.5 * g['tail'][0] * math.sin(TW * 2 * ph - 2.0), z2=0.6 * g['tail'][1] * math.sin(TW * ph - 0.9))
    fr, ev, extra = gait_piglet(sk, sp, 'Walk', ov_walk)
    out['Walk'] = dict(frames=fr, events=ev, extra=extra)

    # Root (3 s loop): front legs braced (both front feet forward), body a little lower and nose-down, neck pitched down +
    # Neck1 reach (keyed location) so the snout disc touches the ground in front of the hooves; 5 plough thrusts
    # (quick push forward along the ground, lift and pull back), head digs on each push, ears hang forward, tail wiggles.
    rt = sp['root']
    dig = copy_pose(STAND); body(sk, dig, (0, 0.0, -rt['drop']), pitch=rt['pitch'])
    feet = {k: sk.feet[k] + Vector((0, -rt['foot_fwd'], 0)) for k in ('FrontL', 'FrontR')}
    plant(sk, dig, None, feet)
    nm = sk.mask(['Head']) & SNOUT_MASK[0] if SNOUT_MASK[0] is not None else sk.mask(['Head'])
    hm = sk.mask(['Head', 'Jaw', 'Ear.L', 'Ear.R']) & ~nm
    base = {bn: dig[bn][1][0] for bn in ('Neck1', 'Neck2', 'Head')}
    yfront = min(feet['FrontL'].y, feet['FrontR'].y) - 0.06
    cand = []
    for ry in range(0, 9, 2):
        for rz in range(0, 15, 2):
            dig['Neck1'][0] = [0.0, ry / 100.0, rz / 100.0]
            for n in range(0, 121, 5):
                for h in range(-30, 71, 5):
                    dig['Neck1'][1][0] = base['Neck1'] + R(0.6 * n); dig['Neck2'][1][0] = base['Neck2'] + R(0.4 * n)
                    dig['Head'][1][0] = base['Head'] + R(h)
                    M_ = sk.fk(dig); Pn = sk.skin(M_, nm); Ph = sk.skin(M_, hm)
                    zn = float(Pn[:, 2].min()); zh = float(Ph[:, 2].min()); yb = float(Pn[:, 1].max())
                    if yb < yfront and zh >= rt['head_clear'] and abs(zn - rt['snout_z']) < 0.012 and n + h >= rt.get('min_pitch', 0):
                        cand.append((abs(zn - rt['snout_z']) + 0.002 * (abs(n) + abs(h)) / 10 + 0.05 * (ry + rz) / 100, ry, rz, n, h, zn, zh))
    if not cand: raise RuntimeError('ROOT: no neck/head solution reaches the ground')
    _, ry_, rz_, n_, h_, zn_, zh_ = min(cand)
    dig['Neck1'][0] = [0.0, ry_ / 100.0, rz_ / 100.0]
    dig['Neck1'][1][0] = base['Neck1'] + R(0.6 * n_); dig['Neck2'][1][0] = base['Neck2'] + R(0.4 * n_); dig['Head'][1][0] = base['Head'] + R(h_)
    print('ROOT reach', ry_ / 100.0, rz_ / 100.0, 'neck pitch', n_, 'head pitch', h_, 'snout min z', round(zn_, 3),
          'rest of head min z', round(zh_, 3), 'candidates', len(cand))
    Rn = sk.rest['Neck1'].to_3x3().transposed()
    THR = rt['thrusts']

    def ov_root(p, t):
        u = (t * THR) % 1.0
        if u < 0.4: s = smooth(u / 0.4); lift = 0.0                   # push forward along the ground
        else: s = 1 - smooth((u - 0.4) / 0.6); lift = math.sin(math.pi * (u - 0.4) / 0.6)   # lift and pull back
        d = Rn @ Vector((0, -rt['thrust_len'] * s, rt['thrust_lift'] * lift))
        loc = p['Neck1'][0]; p['Neck1'][0] = [loc[0] + d.x, loc[1] + d.y, loc[2] + d.z]
        rot(p, 'Head', x=rt['dig_deg'] * s * (1 - lift), z=2.0 * math.sin(TW * 2 * t))
        rot(p, 'Neck2', x=1.5 * math.sin(TW * THR * t - 0.8))
        breathe(sk, p, t, 0.003, 3, 0.6)
        ear(p, up=rt['ear_fwd'] + 4 * math.sin(TW * THR * t - 1.2), back=0.0)
        tail_curl(p, x1=3 * math.sin(TW * 3 * t), z1=10 * math.sin(TW * 6 * t), z2=8 * math.sin(TW * 6 * t - 0.9),
                  x3=5 * math.sin(TW * 6 * t - 1.6))
    out['Root'] = dict(frames=loop_static('Root', dig, ov_root, None, feet), events=[],
                       extra=dict(reach=(ry_ / 100.0, rz_ / 100.0), neck=n_, head=h_, snout_z=zn_))
    for c, (T, loop) in dur.items():
        out[c]['loop'] = loop; out[c].setdefault('bones', None); out[c].setdefault('extra', {})
    return out


SNOUT_MASK = [None]          # set by rig_piglet: boolean mask of the Nose part vertices in the TMP joined mesh
LOC_BONES = ('Pelvis', 'Neck1')


def write_action_loc(rig, name, frames, loop, bones=None):
    """copy of animal_anim.write_action that also keys Neck1 location (Root reach) in every take"""
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
