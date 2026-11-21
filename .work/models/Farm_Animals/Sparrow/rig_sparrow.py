# rig_sparrow.py - BRD-09 Sparrow: skeleton B bird rig with flight (20 bones), clips Sparrow_Idle / Sparrow_Hop / Sparrow_Fly.
#   PYTHONUTF8=1 blender --background --factory-startup --python rig_sparrow.py -- BRD-09 bend|anim|export|meshcheck
# Uses ../Pigeon/rig_pigeon.py + ../Pigeon/pigeon_clips.py read-only (flight-capable copy of the Hen rig B toolkit):
# only the species table lives here. Geometry, part names and pivots come unchanged from build_sparrow.build().
import sys, os
REPO = r'C:\Users\Sergv\orca\workspaces\VFX\master-3'
HERE = REPO + r'\.work\models\Farm_Animals\Sparrow'
for p in (REPO + r'\.work\models\Farm_Animals\Pigeon', HERE):
    if p not in sys.path: sys.path.insert(0, p)
import rig_pigeon as rb
import build_sparrow

# Sparrow: 0.122 m tall (0.30x the hen), ball head, wing = upper shield + lower band under it + tip plate on the tail base.
# Fast, jerky: 2-frame snaps, quick breathing, tail flicks; hop = both feet together; flight 8 frames per wing beat.
LIM = dict(rb.B_LIMITS)
SPARROW = dict(
    id='BRD-09', species='Sparrow', skeleton='B', module='build_sparrow', work=HERE,
    bind={'Eye.L': 'Head', 'Eye.R': 'Head', 'Neck1': 'Body', 'Neck2': 'Head'},    # hidden neck connectors stay hidden
    ends={'Root': (0, -0.04, 0), 'Body': (0, -0.03, 0), 'Head': (0, -0.044, -0.004), 'Beak_Lower': (0, -0.013, -0.003),
          'TailFan2': (0, 0.040, -0.012)},
    heads={}, blend={},
    wing_heads='seams', wing_pivot=(0.010, 0.0, 0.0),
    clips=[('Idle', 3.0, True), ('Hop', 0.5, True), ('Fly', 0.8, True)],
    limits=LIM, lowest_ok=-0.003,
    strip_views={'Fly': [(0.5, -1.0, 0.55), (0.05, 0.25, 1.0)], 'Hop': [(1.0, -0.02, 0.10)], 'Idle': [(0.6, -1.0, 0.35)]},
    bend_views={'side': (1.0, -0.15, 0.2), 'front': (-0.6, -1.0, 0.45), 'top': (0.1, 0.3, 1.0)},
    poses=dict(stand_bend=0.0015, wing_out=10.0, breaths=5, breath_pitch=1.2, breath_dz=0.0005, snap_frames=2.0,
               look_share=0.25, neck_sway=1.0, tail_idle=3.0, tail_flick_up=14.0,
               idle_look=[(0.00, (0, 0, 0)), (0.07, (35, 10, -4)), (0.16, (42, 18, 0)), (0.24, (12, 0, 6)), (0.33, (0, 0, 0)),
                          (0.42, (-34, -10, -3)), (0.50, (-46, -16, 2)), (0.58, (-20, 0, 6)), (0.67, (0, 8, -6)),
                          (0.78, (26, 0, 0)), (0.86, (8, -12, 4)), (0.93, (0, 0, 0))],
               tail_flicks=[(0.20, 0.08, 1, 14.0), (0.62, 0.08, 1, 14.0)], ruffles=[(0.40, 0.08, 2), (0.88, 0.06, 2)]),
    hop=dict(contact=0.4, length=0.06, height=0.030, crouch=0.006, pitch_land=10.0, pitch_push=8.0, tuck=0.006, toe_air=35.0,
             body_follow=0.8, head_lag=5.0, tail_flick=22.0, wing_flick=6.0),
    fly=dict(flaps=3, down=0.55, lift=0.05, clear=0.022, bob=0.004, pitch=22.0, pitch_beat=3.0,
             leg=(55.0, 85.0, 95.0), neck={}, head_down=0.0, head_nod=2.0, tail=-4.0, tail_beat=5.0,
             mid=10.0, amp=60.0, sweep=4.0, sweep_up=16.0, twist=8.0, lag=(0.0, 18.0), lag_ph=(0.7, 1.0), lag0=(0.0, 14.0),
             lsweep=(0.0, 0.0), lsweep_up=(0.0, 10.0)),
)

if __name__ == '__main__':
    rb.main(SPARROW, build_sparrow)
