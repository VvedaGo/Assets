# crow_clips.py - BRD-10 Crow: Walk generator for the flight-capable bird toolkit ../Pigeon/pigeon_clips.py (read-only,
# NOT edited). Importing this module registers clip_walk in pigeon_clips.CLIP_FUNCS (in memory only), so
# rig_pigeon.main() builds Idle / Walk / Fly for the crow table in ../Crow/rig_crow.py.
# Walk = copy of ../Hen/hen_clips.gait (biped walk in place: stance feet move back at the walk speed, swing arcs with toe
# curl, body height from the leg reach, FFT-smoothed and periodic) + the hen head-bob overlay (head held still in space,
# then thrust forward before each touchdown), adapted to pigeon_clips (BirdSkel, wing_set for the folded wings).
import math
import numpy as np
from mathutils import Vector
import pigeon_clips as hc
from pigeon_clips import TW, R, smooth, new_pose, frames_of, copy_pose, rot, body, leg_ik, neck_ik2, set_head_down, \
    head_down_deg, wing_set, stand


def gait(sk, sp, overlay):
    """copy of hen_clips.gait (Walk table sp['gait']['Walk']); overlay(pose, phase) runs before the leg IK"""
    g = sp['gait']['Walk']; T = g['T']; N = frames_of(T); duty = g['duty']; v = g['speed']; S = duty * v * T
    targ = []; need = np.zeros(N); stance = {k: [] for k in sk.legs}
    piv = {k: sk.rest[sk.legs[k][0]].translation.copy() for k in sk.legs}
    for f in range(N):
        ph = f / N; row = {}
        for k, (up, lo, ft, _) in sk.legs.items():
            p = (ph - g['phases'][k]) % 1.0; G = sk.feet[k]; L3 = sk.length[ft]
            if p < duty:
                y = G.y - S / 2 + S * p / duty; z = 0.0; tp = 0.0; stance[k].append(f)
                Lm = g.get('reach', 0.97) * (sk.length[up] + sk.length[lo]); dy = y - piv[k].y
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
    events = sorted([(round(g['phases'][k] * N) % N, 'Footstep', 'L' if k.endswith('L') else 'R') for k in sk.legs])
    return frames, events, dict(stance=stance, speed=v, step=S, N=N, drop=[round(float(x), 4) for x in drop])


def clip_walk(sk, sp, T):
    """crow walk: deliberate strut, head held still in space (moves back with the ground) then thrust forward before
    each touchdown, slight waddle roll/sway, tail bobs, wings folded (tiny settle)"""
    g = sp['gait']['Walk']; P = sp['poses']; assert abs(g['T'] - T) < 1e-6
    M0 = sk.fk(new_pose(sk)); head_rest = M0['Head'].translation.copy(); down_rest = head_down_deg(sk, M0)
    hold = g['hold']; A = g['speed'] * hold * T / 2 * g.get('head_share', 1.0)   # head travel per step, body frame (m)
    hb = sk.rest[sk.mover].inverted() @ head_rest

    def ov(p, ph):
        q = (2 * ph + g.get('head_phase', 0.0)) % 1.0
        dy = (-A / 2 + A * q / hold) if q < hold else (A / 2 - A * smooth((q - hold) / (1 - hold)))
        M = sk.fk(p); Rb = M[sk.mover].to_3x3() @ sk.rest[sk.mover].to_3x3().inverted()
        tgt = M[sk.mover] @ hb + Rb @ Vector((0, dy, g['head_dz'] * math.cos(TW * q)))
        neck_ik2(sk, p, tgt); set_head_down(sk, p, down_rest + g['head_nod'] * math.sin(TW * q))
        rot(p, 'TailFan1', x=g['tail'] * math.sin(2 * TW * ph - 1.0), z=0.5 * g['tail'] * math.sin(TW * ph - 0.5))
        if 'TailFan2' in p: rot(p, 'TailFan2', x=0.6 * g['tail'] * math.sin(2 * TW * ph - 1.6))
        for s in ('L', 'R'): wing_set(sk, sp, p, s, spread=0.0, fold=P['wing_out'] * 0.3 * (1 + math.sin(2 * TW * ph)))
    fr, ev, extra = gait(sk, sp, ov)
    extra['head_travel'] = A
    return dict(frames=fr, events=ev, extra=extra)


hc.CLIP_FUNCS['Walk'] = clip_walk
