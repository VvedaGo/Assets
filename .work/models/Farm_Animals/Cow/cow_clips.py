# cow_clips.py - LIV-01 Cow clip set: copy of _common/animal_anim.build_clips with cow-specific fixes
# (Eat reaches the ground, Lie_Down kneels one front leg after the other, Stand_Up pushes up on one front leg,
# Sleep lays the head on the ground beside the left front leg). Shared helpers are imported read-only.
import math
from mathutils import Vector
from animal_anim import *
from animal_anim import R, LEGS
from bpy_extras import anim_utils

NECK_REACH = 0.11      # m, Neck1 translation used by Eat only (keyed location channel)
LOC_BONES = ('Pelvis', 'Neck1')
GRAZE_REACH = 0.28     # m, Neck1 reach in Eat/Graze (was 0.11): the neck, not the front legs, brings the muzzle down
GRAZE_PITCH = 4.0      # deg, body nose-down in Eat/Graze (+ front feet 0.24/0.14 m forward); the neck takes the rest


def write_action(rig, name, frames, loop, bones=None):
    """copy of animal_anim.write_action that also keys Neck1 location (Eat neck reach)"""
    import bpy
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


def build_clips(sk, sp):  # cow-local copy of animal_anim.build_clips (polish pass)
    """all clips of a Q species -> {clip: dict(frames, loop, events, bones, extra)}"""
    out = {}; dur = {c: (T, loop) for c, T, loop in sp['clips']}; ps = sp['poses']
    STAND = stand_pose(sk)

    def loop_static(name, base, overlay, planted=LEGS):
        N = frames_of(dur[name][0]); fr = []
        for f in range(N):
            p = copy_pose(base); overlay(p, f / N); plant(sk, p, planted); fr.append(p)
        fr.append(copy_pose(fr[0])); return fr

    # Idle (ANIMATIONS.md: "moves ears and tail"): subtle breathing, tiny head drift, ears flick alternately
    # (quick flick then relax), tail sways with lag + one short swish per loop. Every term is periodic in t -> closed loop.
    def flick(t, c, w):
        """0..1 envelope on the loop phase: fast rise (first 25% of w), slow relax; zero outside [c, c+w)"""
        x = ((t - c) % 1.0) / w
        if x >= 1.0: return 0.0
        return math.sin(0.5 * math.pi * x / 0.25) if x < 0.25 else 0.5 * (1 + math.cos(math.pi * (x - 0.25) / 0.75))

    def ov_idle(p, t):
        TW = 2 * math.pi
        breathe(sk, p, t, 0.006, 2, 0.8)                                       # 2 slow breaths per loop
        rot(p, 'Neck1', x=1.2 * math.sin(TW * t + 0.4)); rot(p, 'Head', x=-0.8 * math.sin(2 * TW * t + 1.0), z=2.5 * math.sin(TW * t))
        # ears: gentle baseline drift, left flick at 0.14, right flick at 0.46, small left twitch at 0.80
        fl = flick(t, 0.14, 0.11) + 0.55 * flick(t, 0.80, 0.08); fr_ = flick(t, 0.46, 0.11)
        rot(p, 'Ear.L', x=-3 + 2 * math.sin(TW * t) + 16 * fl, z=-(4 * math.sin(TW * t + 0.5)) + 32 * fl)
        rot(p, 'Ear.R', x=-3 + 2 * math.sin(TW * t + 1.7) + 16 * fr_, z=-(-4 * math.sin(TW * t + 2.2) + 32 * fr_))
        # tail: lagged sway (2 cycles/loop) + one swish (S-shaped side flick) around t = 0.60
        for i, (b, a) in enumerate((('Tail1', 5.0), ('Tail2', 7.0), ('Tail3', 9.0))):
            sw = 0.0; x = ((t - 0.58 - 0.025 * i) % 1.0) / 0.20
            if x < 1.0: sw = math.sin(TW * x) * math.sin(math.pi * x)
            rot(p, b, x=6.0 * math.sin(math.pi * min(x, 1.0)) * (1 - 0.4 * i) if x < 1.0 else 0.0,
                z=a * math.sin(TW * (2 * t) - 0.7 * (i + 1)) + (24 + 8 * i) * sw)
    out['Idle'] = dict(frames=loop_static('Idle', STAND, ov_idle), events=[])

    # Idle_Look: head left/right with hold, ears follow
    def ov_look(p, t):
        breathe(sk, p, t, 0.010, 2)
        s = math.tanh(2.2 * math.sin(2 * math.pi * t)) / math.tanh(2.2); A = 50.0 * s
        rot(p, 'Neck1', z=-0.3 * A); rot(p, 'Neck2', z=-0.3 * A); rot(p, 'Head', z=-0.4 * A, x=-5 * abs(s))
        s2 = math.tanh(2.2 * math.sin(2 * math.pi * (t - 0.04))) / math.tanh(2.2)
        rot(p, 'Ear.L', z=-18 * s2, x=4); rot(p, 'Ear.R', z=-18 * s2, x=4)
        tail_sway(p, t, (3, 5, 7), cycles=2)
    out['Idle_Look'] = dict(frames=loop_static('Idle_Look', STAND, ov_look), events=[])

    # Eat: head down to the grass, one front foot forward, chewing
    # Rework (ANIMATION_FIXES 3): the old pose pitched the body 7 deg + spine 9 deg with the front feet planted, so the
    # shoulders dropped ~0.3 m and the front legs folded into a zigzag (FrontLower ~88 deg, knees crossing in view). Now the
    # body tilts only a little (front lower by ~6 cm), both front feet step forward so the front legs slant forward-down
    # nearly straight (knee a few deg, strictly forward: no yaw/abduction), and the NECK does the reach.
    eat = copy_pose(STAND); body(sk, eat, (0, -0.03, 0.0), pitch=GRAZE_PITCH); rot(eat, 'Spine2', x=1.0)
    eat_feet = {'FrontL': sk.feet['FrontL'] + Vector((0, -0.24, 0)), 'FrontR': sk.feet['FrontR'] + Vector((0, -0.14, 0))}
    plant(sk, eat, None, eat_feet); rot(eat, 'Neck1', z=4)
    print('GRAZE front knees', [round(math.degrees(eat[b][1][0]), 1) for b in ('FrontLower.L', 'FrontLower.R')],
          'upper', [round(math.degrees(eat[b][1][0]), 1) for b in ('FrontUpper.L', 'FrontUpper.R')])
    eat['Neck1'][0] = [0.0, 0.0, GRAZE_REACH]          # neck extension forward-down (Neck1 local +Z) (stretches the thick neck loft)
    # 2D search (neck pitch n split 0.6/0.4 on Neck1/Neck2, head pitch h): lowest muzzle that stays in front of the
    # front hooves; among those reaching the target pick the least neck bend
    hm = sk.mask(['Head', 'Jaw']); base = {bn: eat[bn][1][0] for bn in ('Neck1', 'Neck2', 'Head')}
    yfront = min(eat_feet['FrontL'].y, eat_feet['FrontR'].y) - 0.06; cand = []   # muzzle in front of the leading hoof
    for n in range(0, 176, 5):
        for h in range(-45, 61, 5):          # head within its joint limit (-50..80); Neck1/Neck2 <= 90 each
            if 0.5 * n > 90: continue
            eat['Neck1'][1][0] = base['Neck1'] + R(0.5 * n); eat['Neck2'][1][0] = base['Neck2'] + R(0.5 * n)
            eat['Head'][1][0] = base['Head'] + R(h)
            P_ = sk.skin(sk.fk(eat), hm); z = float(P_[:, 2].min()); low = P_[P_[:, 2] < 0.30]; yb = float(low[:, 1].max()) if len(low) else -9.0   # head part near the grass
            if yb < yfront: cand.append((z, n, h))
    ok = [c for c in cand if c[0] >= ps['eat_muzzle_z']]
    z_, n_, h_ = min(ok, key=lambda c: (round(abs(c[0] - ps['eat_muzzle_z']), 2), c[1])) if ok else min(cand)
    eat['Neck1'][1][0] = base['Neck1'] + R(0.5 * n_); eat['Neck2'][1][0] = base['Neck2'] + R(0.5 * n_)
    eat['Head'][1][0] = base['Head'] + R(h_); A_eat = n_
    print('EAT reachable min z (head in front of hooves)', round(min(cand)[0], 3), 'chosen neck/head', n_, h_)
    hp_ = sk.skin(sk.fk(eat), hm)
    print('EAT neck pitch', round(A_eat, 1), 'muzzle min z', round(float(hp_[:, 2].min()), 3), 'muzzle front y', round(float(hp_[:, 1].min()), 3),
          'front feet y', round(sk.feet['FrontL'].y - 0.14, 3), round(sk.feet['FrontR'].y, 3))

    def ov_eat(p, t):
        chew(p, t, 4, 8, 3); rot(p, 'Head', x=3 * math.sin(2 * math.pi * t)); breathe(sk, p, t, 0.006)
        ear(p, up=-6 + 8 * bump(t, 0.3, 0.08), back=6); tail_sway(p, t, (4, 6, 9))
    N = frames_of(dur['Eat'][0]); fr = []
    for f in range(N):
        p = copy_pose(eat); ov_eat(p, f / N); plant(sk, p, None, eat_feet); fr.append(p)
    fr.append(copy_pose(fr[0])); out['Eat'] = dict(frames=fr, events=[])

    # Graze (ANIMATIONS.md "пасётся", 4 s loop): Eat pose (head down in front of the hooves, 0.11 m neck reach),
    # bite-tug + chewing, the head lifts slightly once per loop while chewing, ears flick, tail sways with lag
    if 'Graze' in dur:
        def gflick(t, c, w):
            x = ((t - c) % 1.0) / w
            if x >= 1.0: return 0.0
            return math.sin(0.5 * math.pi * x / 0.25) if x < 0.25 else 0.5 * (1 + math.cos(math.pi * (x - 0.25) / 0.75))

        def ov_graze(p, t):
            TW = 2 * math.pi
            lift = 0.5 * (1 - math.cos(TW * ((t - 0.50) % 1.0) / 0.30)) if (t - 0.50) % 1.0 < 0.30 else 0.0   # 1.2 s head lift
            rot(p, 'Neck1', x=-11 * lift); rot(p, 'Neck2', x=-5 * lift); rot(p, 'Head', x=-4 * lift)
            tug = (1 - lift) * math.sin(TW * 4 * t)                                  # 4 bite tugs per loop while down
            rot(p, 'Head', x=2.0 * tug, z=1.5 * math.sin(TW * t))
            chew(p, t, 8, 7, 3)                                                      # 8 chews / 4 s
            breathe(sk, p, t, 0.004, 2, 0.6)
            fl = gflick(t, 0.20, 0.10); fr2 = gflick(t, 0.72, 0.10)
            rot(p, 'Ear.L', x=-6 + 14 * fl, z=6 + 26 * fl); rot(p, 'Ear.R', x=-6 + 14 * fr2, z=-(6 + 26 * fr2))
            for i, (bn, a) in enumerate((('Tail1', 5.0), ('Tail2', 7.0), ('Tail3', 9.0))):
                rot(p, bn, z=a * math.sin(TW * 2 * t - 0.7 * (i + 1)))
        Ng = frames_of(dur['Graze'][0]); fr = []
        for f in range(Ng):
            p = copy_pose(eat); ov_graze(p, f / Ng); plant(sk, p, None, eat_feet); fr.append(p)
        fr.append(copy_pose(fr[0])); out['Graze'] = dict(frames=fr, events=[])

    # Drink: head down to trough height, swallow pulses
    dr = copy_pose(STAND); body(sk, dr, (0, -0.02, -0.01), pitch=2.0); plant(sk, dr)
    aim_head(sk, dr, ps['drink_muzzle_z'])

    def ov_drink(p, t):
        rot(p, 'Neck1', x=2.5 * math.sin(2 * math.pi * 3 * t)); rot(p, 'Neck2', x=-1.5 * math.sin(2 * math.pi * 3 * t - 0.8))
        chew(p, t, 3, 3, 0); breathe(sk, p, t, 0.005); ear(p, up=-4, back=8 + 6 * bump(t, 0.5, 0.1)); tail_sway(p, t, (3, 5, 7))
    out['Drink'] = dict(frames=loop_static('Drink', dr, ov_drink), events=[])

    # Walk / Run
    for nm in ('Walk', 'Run'):
        fr, ev, extra = gait(sk, sp, nm); out[nm] = dict(frames=fr, events=ev, extra=extra)

    LIE = lie_pose(sk, sp); KNEEL = kneel_pose(sk)
    # Lie_Down (once): head lowers, front kneels, hind drops, settle
    k1 = copy_pose(STAND); rot(k1, 'Neck1', x=16); body(sk, k1, (0, 0.04, -0.01)); plant(sk, k1)
    k3 = copy_pose(LIE); body(sk, k3, tuple(body_off(sk, LIE) + Vector((0, 0, 0.06))), pitch=7.0, roll=1.0)
    FL = ('FrontUpper.L', 'FrontLower.L', 'FrontFoot.L'); FR = ('FrontUpper.R', 'FrontLower.R', 'FrontFoot.R')
    # one front knee goes down first, the other leg still carries the chest
    k1b = copy_pose(STAND); body(sk, k1b, (0, 0.03, -0.07), pitch=8.0); rot(k1b, 'Neck1', x=10)
    for bn in FL: k1b[bn][1] = list(KNEEL[bn][1])
    plant(sk, k1b, ['FrontR', 'HindL', 'HindR']); no_penetration(sk, k1b, ['FrontR', 'HindL', 'HindR'])
    out['Lie_Down'] = dict(frames=keyed(sk, frames_of(dur['Lie_Down'][0]),
                                        [(0.0, STAND, LEGS), (0.16, k1, LEGS), (0.34, k1b, ['FrontR', 'HindL', 'HindR']),
                                         (0.52, KNEEL, ['HindL', 'HindR']), (0.80, k3, []), (1.0, LIE, [])]), events=[])
    # Lie_Idle: breathing + chewing cud + ear flick
    def ov_lie(p, t):
        breathe(sk, p, t, 0.0, 1, 1.6); chew(p, t, 4, 6, 4); ear(p, up=-5 + 12 * bump(t, 0.4, 0.06), back=4)
        rot(p, 'Neck1', x=1.5 * math.sin(2 * math.pi * t)); tail_sway(p, t, (0, 3, 5))
    out['Lie_Idle'] = dict(frames=loop_static('Lie_Idle', LIE, ov_lie, planted=[]), events=[])
    # Sleep: classic resting pose - head turned back to the left and laid on the ground beside the left shoulder
    sl = copy_pose(LIE); sl['Neck1'][0] = [0.0, 0.0, NECK_REACH]
    hm = sk.mask(['Head', 'Jaw']); base = {bn: list(sl[bn][1]) for bn in ('Neck1', 'Neck2', 'Head')}; best = None
    for Y in range(70, 116, 5):
        for n in range(0, 91, 3):
            for h in range(-48, 41, 4):
                sl['Neck1'][1] = [base['Neck1'][0] + R(0.55 * n), 0.0, base['Neck1'][2] - R(0.45 * Y)]
                sl['Neck2'][1] = [base['Neck2'][0] + R(0.45 * n), 0.0, base['Neck2'][2] - R(0.35 * Y)]
                sl['Head'][1] = [base['Head'][0] + R(h), 0.0, base['Head'][2] - R(0.20 * Y)]
                M = sk.fk(sl); HP = sk.skin(M, hm); z = float(HP[:, 2].min())
                inside = int(((HP[:, 0] < 0.40) & (HP[:, 2] > 0.12) & (HP[:, 1] > -0.95)).sum())   # head verts inside the chest
                yax = M['Head'].to_3x3().col[1]; down = math.degrees(math.asin(max(-1.0, min(1.0, -yax.z))))
                score = abs(z - ps['sleep_muzzle_z']) * 100 + inside * 0.5 + abs(down - 15.0) * 0.05 + Y * 0.01
                if best is None or score < best[0]: best = (score, Y, n, h, z, down, inside)
    _, Y_, n_, h_, z_, dn_, in_ = best
    sl['Neck1'][1] = [base['Neck1'][0] + R(0.55 * n_), 0.0, base['Neck1'][2] - R(0.45 * Y_)]
    sl['Neck2'][1] = [base['Neck2'][0] + R(0.45 * n_), 0.0, base['Neck2'][2] - R(0.35 * Y_)]
    sl['Head'][1] = [base['Head'][0] + R(h_), 0.0, base['Head'][2] - R(0.20 * Y_)]
    raise_body(sk, sl, 0.012)       # breathing margin
    print('SLEEP yaw', Y_, 'neck/head pitch', n_, h_, 'head lowest z', round(z_, 3), 'head axis down', round(dn_, 1), 'head verts in chest', in_)
    ear(sl, up=-22, back=12)

    def ov_sleep(p, t):
        breathe(sk, p, t, 0.0, 1, 2.2); rot(p, 'Head', x=-1.0 * math.sin(2 * math.pi * t))
    out['Sleep'] = dict(frames=loop_static('Sleep', sl, ov_sleep, planted=[]), events=[])
    # Stand_Up (once): lunge, hind rises first (kneeling front), then front, settle
    s1 = copy_pose(LIE); rot(s1, 'Neck1', x=22); body(sk, s1, tuple(body_off(sk, LIE) + Vector((0, -0.03, 0.0))), pitch=3.0)
    s3 = copy_pose(STAND); rot(s3, 'Neck1', x=-6); rot(s3, 'Head', x=-4); plant(sk, s3)
    # hind end up first (front kneeling), then the left front leg pushes up while the right still kneels
    s2b = copy_pose(KNEEL); body(sk, s2b, tuple(body_off(sk, KNEEL) + Vector((0, 0, 0.10))), pitch=8.0); rot(s2b, 'Neck1', x=-8)
    plant(sk, s2b, ['FrontL', 'HindL', 'HindR']); no_penetration(sk, s2b, ['FrontL', 'HindL', 'HindR'])
    out['Stand_Up'] = dict(frames=keyed(sk, frames_of(dur['Stand_Up'][0]),
                                        [(0.0, LIE, []), (0.16, s1, []), (0.46, KNEEL, ['HindL', 'HindR']),
                                         (0.66, s2b, ['FrontL', 'HindL', 'HindR']), (0.86, s3, LEGS), (1.0, STAND, LEGS)]), events=[])
    # Hit_React (once): flinch sideways/back, head thrown up, ears back, tail up, recover
    h1 = copy_pose(STAND); body(sk, h1, (0.05, 0.05, -0.03), pitch=-3.0, roll=4.0, yaw=5.0)
    rot(h1, 'Spine2', x=-3); rot(h1, 'Neck1', x=-12); rot(h1, 'Neck2', x=-8); rot(h1, 'Head', x=-12, z=6); ear(h1, up=15, back=40)
    rot(h1, 'Tail1', x=40); rot(h1, 'Tail2', x=15); plant(sk, h1)
    h2 = blend(STAND, h1, -0.25); plant(sk, h2)
    out['Hit_React'] = dict(frames=keyed(sk, frames_of(dur['Hit_React'][0]),
                                         [(0.0, STAND, LEGS), (0.17, h1, LEGS), (0.45, h2, LEGS), (1.0, STAND, LEGS)]), events=[])
    # Moo (once): head up and forward, jaw opens, vocal event
    m1 = copy_pose(STAND); rot(m1, 'Neck1', x=6); rot(m1, 'Neck2', x=-14); rot(m1, 'Head', x=-24); ear(m1, up=-8, back=18)
    body(sk, m1, (0, 0.02, -0.01), pitch=1.5); plant(sk, m1)
    m2 = copy_pose(m1); rot(m2, 'Jaw', x=22); m3 = copy_pose(m1); rot(m3, 'Jaw', x=19); rot(m3, 'Head', x=-3)
    Nm = frames_of(dur['Moo'][0])

    def ov_moo(p, t):
        if 0.32 < t < 0.72: rot(p, 'Jaw', x=1.5 * math.sin(2 * math.pi * 14 * t))
    out['Moo'] = dict(frames=keyed(sk, Nm, [(0.0, STAND, LEGS), (0.22, m1, LEGS), (0.32, m2, LEGS), (0.72, m3, LEGS), (0.82, m1, LEGS),
                                            (1.0, STAND, LEGS)], ov_moo), events=[(round(0.27 * Nm), 'Vocal', 'Moo')])
    # Tail_Swish (loop, tail bones only -> for an AvatarMask layer)
    N = frames_of(dur['Tail_Swish'][0]); fr = []
    for f in range(N):
        p = copy_pose(STAND); t = f / N
        rot(p, 'Tail1', x=8 + 5 * math.sin(4 * math.pi * t), z=20 * math.sin(2 * math.pi * t))
        rot(p, 'Tail2', z=24 * math.sin(2 * math.pi * (t - 0.08))); rot(p, 'Tail3', z=28 * math.sin(2 * math.pi * (t - 0.16)))
        fr.append(p)
    fr.append(copy_pose(fr[0])); out['Tail_Swish'] = dict(frames=fr, events=[], bones=['Tail1', 'Tail2', 'Tail3'])
    for c, (T, loop) in dur.items():
        out[c]['loop'] = loop; out[c].setdefault('bones', None); out[c].setdefault('extra', {})
    return out


