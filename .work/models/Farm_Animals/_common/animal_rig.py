# animal_rig.py - skeleton templates for the Farm Animals pack, armature builder, rigid/smooth binding, rig checks.
# Bone names + hierarchy are fixed per class (Q, ...) so Generic clips retarget between species of one class.
# Roll rule: every bone in the sagittal plane gets local X = world +X, so rotation_euler.x is the pitch in the side
# view for all of them (+x: forward-pointing bone tips go down, down-pointing bone tips go back (+Y)).
# Lateral bones (ears) get local Z = world up.
import bpy, math
from mathutils import Vector

Q_BONES = [
    ('Root', None), ('Pelvis', 'Root'), ('Spine1', 'Pelvis'), ('Spine2', 'Spine1'),
    ('Neck1', 'Spine2'), ('Neck2', 'Neck1'), ('Head', 'Neck2'), ('Jaw', 'Head'),
    ('Ear.L', 'Head'), ('Ear.R', 'Head'), ('Horn.L', 'Head'), ('Horn.R', 'Head'),
    ('FrontUpper.L', 'Spine2'), ('FrontLower.L', 'FrontUpper.L'), ('FrontFoot.L', 'FrontLower.L'),
    ('FrontUpper.R', 'Spine2'), ('FrontLower.R', 'FrontUpper.R'), ('FrontFoot.R', 'FrontLower.R'),
    ('HindUpper.L', 'Pelvis'), ('HindLower.L', 'HindUpper.L'), ('HindFoot.L', 'HindLower.L'),
    ('HindUpper.R', 'Pelvis'), ('HindLower.R', 'HindUpper.R'), ('HindFoot.R', 'HindLower.R'),
    ('Tail1', 'Pelvis'), ('Tail2', 'Tail1'), ('Tail3', 'Tail2'),
]
SKELETONS = {'Q': Q_BONES}
RIG_OBJECT = 'Rig'          # armature object name: the same for every species, so clip paths are "Rig/Root/Pelvis/..."

LEGS = {  # leg key -> (upper, lower, foot, knee points forward?)
    'FrontL': ('FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', True),
    'FrontR': ('FrontUpper.R', 'FrontLower.R', 'FrontFoot.R', True),
    'HindL': ('HindUpper.L', 'HindLower.L', 'HindFoot.L', False),
    'HindR': ('HindUpper.R', 'HindLower.R', 'HindFoot.R', False),
}


def mirror_name(n):
    return n[:-2] + '.R' if n.endswith('.L') else n


def bone_table(species):
    """full head/tail table incl. mirrored .R bones"""
    out = {}
    for n, (h, t) in species['bones'].items():
        out[n] = (Vector(h), Vector(t))
        if n.endswith('.L'):
            out[mirror_name(n)] = (Vector((-h[0], h[1], h[2])), Vector((-t[0], t[1], t[2])))
    return out


def build_armature(species, coll, skeleton='Q'):
    tab = bone_table(species)
    arm = bpy.data.armatures.get(RIG_OBJECT) or bpy.data.armatures.new(RIG_OBJECT)
    rig = bpy.data.objects.new(RIG_OBJECT, arm); coll.objects.link(rig)
    vl = bpy.context.view_layer
    for o in bpy.context.scene.objects: o.select_set(False)
    vl.objects.active = rig; rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for eb in list(arm.edit_bones): arm.edit_bones.remove(eb)
    for name, par in SKELETONS[skeleton]:
        h, t = tab[name]
        eb = arm.edit_bones.new(name); eb.head = h; eb.tail = t; eb.use_deform = True
        d = (t - h).normalized()
        if abs(d.x) > 0.7:
            eb.align_roll(Vector((0, 0, 1)))
        else:
            eb.align_roll(Vector((1, 0, 0)).cross(d))
        if par: eb.parent = arm.edit_bones[par]; eb.use_connect = False
    bpy.ops.object.mode_set(mode='OBJECT')
    for pb in rig.pose.bones: pb.rotation_mode = 'XYZ'
    arm.display_type = 'STICK'
    return rig


def check_rig(rig, skeleton='Q'):
    want = SKELETONS[skeleton]; bones = rig.data.bones
    names_ok = [b.name for b in bones] and set(b.name for b in bones) == set(n for n, _ in want)
    par_ok = all((bones[n].parent.name if bones[n].parent else None) == p for n, p in want if n in bones)
    roll_bad = []
    for b in bones:
        x = b.matrix_local.to_3x3().col[0]
        d = (b.tail_local - b.head_local).normalized()
        if abs(d.x) < 0.01 and x.dot(Vector((1, 0, 0))) < 0.999: roll_bad.append(b.name)
    print(f'RIG bones {len(bones)} (template {len(want)}) names_ok {names_ok} hierarchy_ok {par_ok} roll_bad {roll_bad}')
    return dict(bones=len(bones), names_ok=bool(names_ok), hierarchy_ok=par_ok, roll_bad=roll_bad)


def bind(mesh, rig, weights):
    """weights: list (per vertex index) of {bone: w}; normalised; armature modifier + parent"""
    for g in list(mesh.vertex_groups): mesh.vertex_groups.remove(g)
    groups = {b.name: mesh.vertex_groups.new(name=b.name) for b in rig.data.bones}
    for i, wd in enumerate(weights):
        s = sum(wd.values())
        for b, w in wd.items():
            if w > 0: groups[b].add([i], w / s, 'REPLACE')
    mod = mesh.modifiers.new('Armature', 'ARMATURE'); mod.object = rig
    mesh.parent = rig; mesh.matrix_parent_inverse.identity()
    nmax = max(len(w) for w in weights)
    print(f'BIND verts {len(weights)} max influences {nmax} groups {len(groups)}')
