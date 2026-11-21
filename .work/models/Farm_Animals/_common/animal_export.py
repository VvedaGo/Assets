# animal_export.py - FBX export of a rigged animal with every clip as its own take, and verification:
#  * fbx_summary(): minimal binary-FBX reader -> root node transforms, LimbNode count, AnimationStack names + lengths
#    (what Unity's importer will see; no Blender importer involved)
#  * reimport_compare(): re-import into an empty scene and compare deformed vertex positions per clip/frame with the
#    source rig (catches axis / bake errors on armatures).
# Modes: 'nla' (one NLA track+strip per action -> take name = strip name = action name), 'actions'
# (bake_anim_use_all_actions -> take names "<object>|<action>"), 'perclip' (one FBX per clip).
import bpy, math, os, struct, zlib
from mathutils import Vector
from bpy_extras.io_utils import axis_conversion

KTIME = 46186158000      # FBX ticks per second


def _clear_nla(rig):
    ad = rig.animation_data
    if ad:
        for t in list(ad.nla_tracks): ad.nla_tracks.remove(t)


def export(rig, mesh, actions, fbx, mode='nla', bake_space=True, simplify=0.0):
    """actions: ordered list of bpy Actions. Returns path(s)."""
    ad = rig.animation_data or rig.animation_data_create()
    sc = bpy.context.scene
    assert sc.render.fps == 30 and sc.render.fps_base == 1.0, 'scene must run at 30 fps (FBX take length uses scene fps)'
    for pb in rig.pose.bones: pb.location = (0, 0, 0); pb.rotation_euler = (0, 0, 0)   # unkeyed bones bake at rest
    # Blender 5.2 nested-child fix (pack_common.export): pre-compensate objects two levels below the root (none here)
    G = axis_conversion(to_forward='-Z', to_up='Y').to_4x4()
    objs = [rig, mesh]
    nested = [(o, o.matrix_basis.copy()) for o in objs if o.parent is not None and o.parent.parent is not None]
    if bake_space:
        for o, _ in nested:
            Pm = o.parent.matrix_local.copy(); o.matrix_local = Pm.inverted() @ G @ Pm @ o.matrix_local
    for o in bpy.context.scene.objects: o.select_set(False)
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = rig
    common = dict(use_selection=True, apply_scale_options='FBX_SCALE_ALL', axis_forward='-Z', axis_up='Y',
                  bake_space_transform=bake_space, object_types={'ARMATURE', 'MESH'}, mesh_smooth_type='FACE',
                  use_mesh_modifiers=True, use_armature_deform_only=False, add_leaf_bones=False,
                  primary_bone_axis='Y', secondary_bone_axis='X', armature_nodetype='NULL', path_mode='COPY',
                  embed_textures=False, bake_anim=True, bake_anim_use_all_bones=True, bake_anim_force_startend_keying=True,
                  bake_anim_step=1.0, bake_anim_simplify_factor=simplify)
    out = []
    try:
        if mode == 'nla':
            _clear_nla(rig); ad.action = None
            for act in actions:
                tr = ad.nla_tracks.new(); tr.name = act.name
                st = tr.strips.new(act.name, int(act.frame_start), act)
                st.name = act.name; st.action_frame_start, st.action_frame_end = act.frame_start, act.frame_end
            bpy.ops.export_scene.fbx(filepath=fbx, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=False, **common)
            out.append(fbx)
            _clear_nla(rig)
        elif mode == 'actions':
            _clear_nla(rig)
            ad.action = actions[0]; ad.action_slot = actions[0].slots[0]
            bpy.ops.export_scene.fbx(filepath=fbx, bake_anim_use_nla_strips=False, bake_anim_use_all_actions=True, **common)
            out.append(fbx); ad.action = None
        elif mode == 'perclip':
            _clear_nla(rig)
            for act in actions:
                ad.action = act; ad.action_slot = act.slots[0]
                sc = bpy.context.scene; sc.frame_start, sc.frame_end = int(act.frame_start), int(act.frame_end)
                p = fbx[:-4] + '@' + act.name + '.fbx'
                bpy.ops.export_scene.fbx(filepath=p, bake_anim_use_nla_strips=False, bake_anim_use_all_actions=False, **common)
                out.append(p)
            ad.action = None
    finally:
        for o, m in nested: o.matrix_basis = m
        bpy.context.view_layer.update()
    print('exported', mode, out)
    return out


# ---------------- minimal binary FBX reader ----------------
def _read_fbx(path):
    data = open(path, 'rb').read()
    assert data[:20] == b'Kaydara FBX Binary  ', 'not a binary FBX'
    ver = struct.unpack('<I', data[23:27])[0]; wide = ver >= 7500

    def prop(o):
        t = chr(data[o]); o += 1
        if t in 'YCIFDL':
            fmt = {'Y': '<h', 'C': '<?', 'I': '<i', 'F': '<f', 'D': '<d', 'L': '<q'}[t]; n = struct.calcsize(fmt)
            return struct.unpack(fmt, data[o:o + n])[0], o + n
        if t in 'fdlib':
            ln, enc, cl = struct.unpack('<III', data[o:o + 12]); o += 12; raw = data[o:o + cl]; o += cl
            if enc: raw = zlib.decompress(raw)
            fmt = {'f': 'f', 'd': 'd', 'l': 'q', 'i': 'i', 'b': '?'}[t]
            return list(struct.unpack('<%d%s' % (ln, fmt), raw)), o
        if t in 'SR':
            ln = struct.unpack('<I', data[o:o + 4])[0]; o += 4; raw = data[o:o + ln]; o += ln
            return (raw.decode('utf-8', 'replace') if t == 'S' else raw), o
        raise ValueError('prop type ' + t)

    def node(o):
        if wide:
            end, nprop, plen = struct.unpack('<QQQ', data[o:o + 24]); o += 24
        else:
            end, nprop, plen = struct.unpack('<III', data[o:o + 12]); o += 12
        nl = data[o]; o += 1; name = data[o:o + nl].decode(); o += nl
        if end == 0: return None, o
        props = []
        for _ in range(nprop):
            v, o = prop(o); props.append(v)
        kids = []
        while o < end:
            k, o2 = node(o)
            if k is None: o = o2; break
            kids.append(k); o = o2
        return (name, props, kids), end
    top = []; o = 27
    while o < len(data) - 160:
        n, o = node(o)
        if n is None: break
        top.append(n)
    return ver, top


def _p70(n):
    out = {}
    for k in n[2]:
        if k[0] == 'Properties70':
            for p in k[2]:
                out[p[1][0]] = p[1][4:]
    return out


def fbx_summary(path):
    ver, top = _read_fbx(path)
    objs = next(n for n in top if n[0] == 'Objects'); conns = next(n for n in top if n[0] == 'Connections')
    models = {n[1][0]: n for n in objs[2] if n[0] == 'Model'}
    parent = {}
    for c in conns[2]:
        if c[1][0] == 'OO': parent[c[1][1]] = c[1][2]
    roots = []
    for mid, n in models.items():
        if parent.get(mid, 0) == 0:
            p = _p70(n)
            roots.append(dict(name=n[1][1].split('\x00')[0], type=n[1][2], rot=[round(x, 4) for x in p.get('Lcl Rotation', [0, 0, 0])],
                              scale=[round(x, 4) for x in p.get('Lcl Scaling', [1, 1, 1])],
                              pos=[round(x, 4) for x in p.get('Lcl Translation', [0, 0, 0])]))
    limbs = [n[1][1].split('\x00')[0] for n in models.values() if n[1][2] == 'LimbNode']
    stacks = []
    for n in objs[2]:
        if n[0] == 'AnimationStack':
            p = _p70(n); stop = p.get('LocalStop', [0])[0]; start = p.get('LocalStart', [0])[0]
            stacks.append(dict(name=n[1][1].split('\x00')[0], seconds=round((stop - start) / KTIME, 4),
                               frames30=round((stop - start) / KTIME * 30, 2)))
    gs = next((n for n in top if n[0] == 'GlobalSettings'), None); g = _p70(gs) if gs else {}
    s = dict(version=ver, roots=roots, limb_nodes=len(limbs), limb_names=sorted(limbs), stacks=stacks,
             up_axis=g.get('UpAxis'), front_axis=g.get('FrontAxis'), unit_scale=g.get('UnitScaleFactor'))
    print(f"FBX {os.path.basename(path)} v{ver} roots {roots} limbs {len(limbs)} stacks {len(stacks)}")
    for st in stacks: print('   take', st['name'], st['seconds'], 's', st['frames30'], 'frames')
    return s


# ---------------- re-import comparison ----------------
def reimport_compare(fbx, rig, mesh, actions, frames_per_clip=4):
    win = bpy.context.window; prev = win.scene
    sc = bpy.data.scenes.new('TMP_FBXVerify'); win.scene = sc
    before_a = set(bpy.data.actions); before_o = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=fbx, use_anim=True)
    new_obs = [o for o in bpy.data.objects if o not in before_o]
    irig = next(o for o in new_obs if o.type == 'ARMATURE'); imesh = next(o for o in new_obs if o.type == 'MESH')
    new_acts = [a for a in bpy.data.actions if a not in before_a]
    res = dict(import_bones=len(irig.data.bones), import_actions=sorted(a.name for a in new_acts),
               import_tris=sum(len(p.vertices) - 2 for p in imesh.data.polygons),
               import_dims=[round(x, 3) for x in imesh.dimensions], rig_rot=[round(math.degrees(a), 2) for a in irig.rotation_euler],
               rig_scale=[round(s, 4) for s in irig.scale], images=[(i.name, os.path.isfile(bpy.path.abspath(i.filepath))) for i in bpy.data.images if i.filepath])
    errs = {}; ranges = {}
    for act in actions:
        ia = next((a for a in new_acts if a.name == act.name or a.name.endswith('|' + act.name)), None)
        if ia is None: errs[act.name] = None; continue
        ranges[act.name] = [round(x, 2) for x in ia.frame_range]
        N = int(act.frame_end); fr = sorted({0, N, N // 3, (2 * N) // 3})
        worst = 0.0
        for f in fr:
            win.scene = prev; rig.animation_data.action = act; rig.animation_data.action_slot = act.slots[0]
            prev.frame_set(f); dg = bpy.context.evaluated_depsgraph_get()
            me = mesh.evaluated_get(dg).to_mesh(); A = [mesh.matrix_world @ v.co for v in me.vertices]; mesh.evaluated_get(dg).to_mesh_clear()
            win.scene = sc; iad = irig.animation_data; iad.action = ia
            if ia.slots: iad.action_slot = ia.slots[0]
            off = int(round(ia.frame_range[0]))
            sc.frame_set(f + off); dg = bpy.context.evaluated_depsgraph_get()
            me = imesh.evaluated_get(dg).to_mesh(); B = [imesh.matrix_world @ v.co for v in me.vertices]; imesh.evaluated_get(dg).to_mesh_clear()
            if len(A) != len(B): worst = float('inf'); break
            worst = max(worst, max((a - b).length for a, b in zip(A, B)))
        errs[act.name] = round(worst, 5)
    res['max_vertex_error_m'] = errs; res['import_frame_ranges'] = ranges
    win.scene = prev; rig.animation_data.action = None
    for o in new_obs:
        d = o.data; bpy.data.objects.remove(o, do_unlink=True)
        try:
            if d is not None and d.users == 0:
                (bpy.data.meshes if isinstance(d, bpy.types.Mesh) else bpy.data.armatures).remove(d)
        except Exception: pass
    for a in new_acts: bpy.data.actions.remove(a)
    bpy.data.scenes.remove(sc)
    print('REIMPORT', {k: v for k, v in res.items() if k not in ('import_actions',)})
    print('REIMPORT actions', res['import_actions'])
    return res
