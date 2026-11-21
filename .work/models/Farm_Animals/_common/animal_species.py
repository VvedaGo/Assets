# animal_species.py - species tables for the Farm Animals pack (Blender axes: front = -Y, left = +X, up = +Z, metres).
# One dict per species: ids/names, palette, rest bone layout (heads/tails; .L given, .R mirrored by animal_rig),
# gait parameters, clip list, joint limits. Calf/Sheep/Pig/Horse add an entry here (or derive with scaled()).
import copy

FPS = 30

# Q-core clip set (FARM_ANIMALS_PACK.md 7.3): (clip, seconds, loop)
Q_CORE = [('Idle', 2.5, True), ('Idle_Look', 4.0, True), ('Eat', 2.0, True), ('Drink', 2.0, True), ('Walk', 1.0, True),
          ('Run', 0.6, True), ('Lie_Down', 1.5, False), ('Lie_Idle', 3.0, True), ('Sleep', 4.0, True),
          ('Stand_Up', 1.5, False), ('Hit_React', 0.6, False)]

# joint limits in degrees on the local euler channels (x = pitch in the sagittal plane for all sagittal bones)
Q_LIMITS = {
    'FrontUpper': dict(x=(-75, 60), z=(-25, 25)), 'FrontLower': dict(x=(-3, 170)), 'FrontFoot': dict(x=(-60, 120)),
    'HindUpper': dict(x=(-60, 75), z=(-25, 25)), 'HindLower': dict(x=(-170, 3)), 'HindFoot': dict(x=(-120, 110)),
    'Neck1': dict(x=(-45, 90), z=(-60, 60)), 'Neck2': dict(x=(-45, 90), z=(-60, 60)), 'Head': dict(x=(-50, 80), z=(-60, 60)),
    'Jaw': dict(x=(-2, 30), z=(-8, 8)), 'Tail1': dict(x=(-60, 80), z=(-60, 60)), 'Tail2': dict(x=(-60, 80), z=(-60, 60)),
    'Tail3': dict(x=(-60, 80), z=(-60, 60)), 'Ear': dict(x=(-70, 70), z=(-70, 70)),
    'Pelvis': dict(x=(-25, 25), y=(-15, 15), z=(-15, 15)), 'Spine1': dict(x=(-15, 15), z=(-15, 15)),
    'Spine2': dict(x=(-15, 15), z=(-15, 15)), 'NECK_YAW_TOTAL': 120,
}

COW = dict(
    id='LIV-01', species='Cow', asset='FMS_Cow', tag='FarmAnimals_Cow', skeleton='Q',
    size=dict(length=2.30, withers=1.45),
    palette=['#F3F0EB', '#DCD6CF', '#2D2A2A', '#1E1B1B',
             '#EC9E97', '#D7847F', '#F0A7A1', '#7A3B3B',
             '#2A1D17', '#3A2E28', '#EADAB4', '#CDB98E',
             '#B5835A', '#6E9F4A', '#8E959B', '#C8473B'],
    bones={
        'Root': ((0, 0, 0), (0, -0.25, 0)),
        'Pelvis': ((0, 0.52, 1.12), (0, 0.18, 1.14)),
        'Spine1': ((0, 0.18, 1.14), (0, -0.26, 1.16)),
        'Spine2': ((0, -0.26, 1.16), (0, -0.66, 1.20)),
        'Neck1': ((0, -0.66, 1.20), (0, -0.80, 1.36)),
        'Neck2': ((0, -0.80, 1.36), (0, -0.90, 1.50)),
        'Head': ((0, -0.90, 1.50), (0, -1.380, 1.164)),
        'Jaw': ((0, -0.983, 1.314), (0, -1.257, 1.111)),
        'Ear.L': ((0.16, -1.058, 1.590), (0.49, -0.94, 1.53)),
        'Horn.L': ((0.095, -1.075, 1.66), (0.16, -1.09, 1.79)),
        'FrontUpper.L': ((0.20, -0.58, 1.00), (0.20, -0.58, 0.44)),
        'FrontLower.L': ((0.20, -0.58, 0.44), (0.20, -0.58, 0.10)),
        'FrontFoot.L': ((0.20, -0.58, 0.10), (0.20, -0.58, 0.0)),
        'HindUpper.L': ((0.21, 0.64, 1.06), (0.21, 0.64, 0.48)),
        'HindLower.L': ((0.21, 0.64, 0.48), (0.21, 0.64, 0.10)),
        'HindFoot.L': ((0.21, 0.64, 0.10), (0.21, 0.64, 0.0)),
        'Tail1': ((0, 0.90, 1.36), (0, 0.97, 1.14)),
        'Tail2': ((0, 0.97, 1.14), (0, 0.99, 0.92)),
        'Tail3': ((0, 0.99, 0.92), (0, 1.00, 0.70)),
    },
    # gaits: T cycle s, duty = stance share, speed m/s (stored for the Animator), lift m, hoof flick deg (front, hind),
    # phases = touchdown phase per leg (walk: lateral sequence, run: diagonal trot pairs)
    gait={
        'Walk': dict(T=1.0, duty=0.64, speed=0.90, lift=0.11, flick=(40, 28), crouch=0.008, bob=0.010,
                     phases={'HindL': 0.0, 'FrontL': 0.25, 'HindR': 0.5, 'FrontR': 0.75},
                     nod=4.0, tail=(5, 8, 11), ear=4.0),
        'Run': dict(T=0.6, duty=0.42, speed=2.0, lift=0.17, flick=(60, 40), crouch=0.015, bob=0.0,
                    phases={'HindL': 0.0, 'FrontR': 0.0, 'HindR': 0.5, 'FrontL': 0.5},
                    nod=6.0, tail=(8, 12, 16), ear=7.0),
    },
    clips=Q_CORE + [('Moo', 2.0, False), ('Tail_Swish', 1.2, True)],
    limits=Q_LIMITS,
    poses=dict(  # targets used by the clip generators (m / deg)
        eat_muzzle_z=0.10, drink_muzzle_z=0.45, lie_roll=3.0, sleep_muzzle_z=0.03,
    ),
)

SPECIES = {'Cow': COW}


def scaled(base, name, s, **over):
    """derive a species table by uniform scaling of the rest layout (calf/lamb starting point)"""
    d = copy.deepcopy(base); d['species'] = name
    d['bones'] = {k: (tuple(c * s for c in h), tuple(c * s for c in t)) for k, (h, t) in base['bones'].items()}
    for g in d['gait'].values():
        g['speed'] *= s; g['lift'] *= s
    d.update(over)
    return d
