# rig_crow.py - BRD-10 Crow: skeleton B bird rig with flight-ready wing bones (20 bones), clip Crow_Idle (this round).
#   PYTHONUTF8=1 blender --background --factory-startup --python rig_crow.py -- BRD-10 bend|anim|export|meshcheck
# Uses ../Pigeon/rig_pigeon.py + ../Pigeon/pigeon_clips.py read-only (flight-capable copy of the Hen rig B toolkit):
# only the species table lives here. Geometry, part names and pivots come unchanged from build_crow.build().
# Round 2 (2026-11-21): + Walk (crow_clips.py: hen gait copy registered into pigeon_clips.CLIP_FUNCS in memory, pigeon
# files untouched) + Fly (pigeon_clips.clip_fly with the 'fly' table below). Idle table unchanged.
import sys, os
REPO = r'C:\Users\Sergv\orca\workspaces\VFX\master-3'
HERE = REPO + r'\.work\models\Farm_Animals\Crow'
for p in (REPO + r'\.work\models\Farm_Animals\Pigeon', HERE):
    if p not in sys.path: sys.path.insert(0, p)
import rig_pigeon as rb
import crow_clips  # registers Walk in pigeon_clips.CLIP_FUNCS
import build_crow

# Crow: 0.40 m tall (hen size), big head on hidden neck connectors, wing = 3 overlapping plates (coverts, secondaries,
# primaries) -> wing bones keep the build pivots (plates are layers, not a chain along the length); slow deliberate head
# turns with holds, a cocked look, one tail flick, one wing settle.
CROW = dict(
    id='BRD-10', species='Crow', skeleton='B', module='build_crow', work=HERE,
    bind={'Eye.L': 'Head', 'Eye.R': 'Head', 'Neck1': 'Body', 'Neck2': 'Head'},    # hidden neck connectors stay hidden
    ends={'Root': (0, -0.10, 0), 'Body': (0, -0.10, 0), 'Head': (0, -0.113, -0.022), 'Beak_Lower': (0, -0.047, -0.012),
          'WingTip.L': (-0.028, 0.206, -0.029), 'TailFan2': (0, 0.178, -0.084)},
    heads={}, blend={},
    wing_heads='pivots', wing_pivot=(0.040, 0.0, 0.0),
    clips=[('Idle', 4.0, True), ('Walk', 0.8, True), ('Fly', 1.0, True)],
    gait={'Walk': dict(T=0.8, duty=0.6, speed=0.22, lift=0.030, toe_curl=24, crouch=0.004, reach=0.97, pitch=3.0, roll=2.5,
                       sway=0.004, yaw=2.0, phases={'LegL': 0.0, 'LegR': 0.5}, hold=0.66, head_share=0.6, head_phase=0.0,
                       head_dz=0.003, head_nod=3.0, tail=4.0)},
    limits=dict(rb.B_LIMITS), lowest_ok=-0.010,
    strip_views={'Idle': [(0.6, -1.0, 0.35)], 'Walk': [(1.0, -0.05, 0.12), (0.6, -1.0, 0.35)],
                 'Fly': [(0.5, -1.0, 0.55), (0.05, 0.25, 1.0), (1.0, -0.05, 0.1)]},
    bend_views={'side': (1.0, -0.15, 0.2), 'front': (-0.6, -1.0, 0.45), 'top': (0.1, 0.3, 1.0)},
    poses=dict(stand_bend=0.008, wing_out=5.0, breaths=2, breath_pitch=0.8, breath_dz=0.0015, snap_frames=4.0,
               look_share=0.3, neck_sway=1.2, tail_idle=1.5,
               # (t, (yaw, tilt, nod)): turn right and hold, cocked look, back, slow turn left, glance down, centre
               idle_look=[(0.00, (0, 0, 0)), (0.08, (40, 4, -2)), (0.20, (62, 14, 0)), (0.33, (20, 0, 4)), (0.40, (0, 0, 0)),
                          (0.50, (-45, -6, -2)), (0.62, (-66, -16, 2)), (0.72, (-30, 0, 10)), (0.82, (0, 10, 6)),
                          (0.90, (0, 0, 0))],
               tail_flicks=[(0.45, 0.10, 1, 10.0)], tail_flick_up=8.0, ruffles=[(0.86, 0.10, 1)]),
    # flight: slow rowing beats (crow ~3 Hz), body pitched, feet tucked
    fly=dict(flaps=3, down=0.55, lift=0.15, clear=0.12, bob=0.012, pitch=24.0, pitch_beat=3.0,
             leg=(55.0, 85.0, 95.0), neck={}, head_down=0.0, head_nod=2.0, tail=-4.0, tail_beat=4.0,
             mid=10.0, amp=50.0, sweep=6.0, sweep_up=14.0, twist=8.0, lag=(12.0, 16.0), lag_ph=(0.7, 1.2),
             lsweep=(0.0, 0.0), lsweep_up=(4.0, 8.0)),
)

if __name__ == '__main__':
    rb.main(CROW, build_crow)
