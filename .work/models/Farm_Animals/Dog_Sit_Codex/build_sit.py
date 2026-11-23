import math
import os
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Matrix, Vector

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
TEMP = Path(os.environ["TEMP"]) / "FarmAnimalsCodex"
TEMP.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(OUT.parent / "Dog"))
import build_dog as dog

pc, rn = dog.pc, dog.rn
W, W2, R, TAN, K, W3, NOSE, SOLE, EYE = range(9)
dog.ASSET = "Dog_Sit_Codex"
m = dog.Model()
rotation = {}


def axis_rotation(a, b):
    return Vector(a).normalized().rotation_difference(Vector(b).normalized()).to_matrix()


def loft(name, spec, colors, pivot, aim=None, rest=(0, 0, -1), n=8, ground=False):
    # Horizontal elliptical sections: center XYZ, radii XY; angle zero faces forward.
    rings = [[Vector((x + rx * math.sin(2 * math.pi * k / n),
                      y - ry * math.cos(2 * math.pi * k / n), z))
              for k in range(n)] for x, y, z, rx, ry in spec]
    m.loft(name, rings, colors, colors if isinstance(colors, int) else colors(0, 0),
           colors if isinstance(colors, int) else colors(len(spec) - 2, 0), ground=ground)
    m.pivot[name] = Vector(pivot)
    if aim is not None:
        rotation[name] = axis_rotation(rest, Vector(aim) - Vector(pivot))


pelvis = (0, .116, .168)
spine1 = (0, .047, .305)
spine2 = (0, -.048, .459)
neck1 = (0, -.12, .576)
neck2 = (0, -.151, .657)
head = Vector((0, -.169, .729))
forward = (0, -1, 0)


def body_coat(j, k):
    return W2 if k in (0, 7) else R if k in (1, 6) else K


def lower_coat(j, k):
    return R if k in (0, 1, 6, 7) else K


loft("Pelvis", [(0,.125,0,.090,.070),(0,.125,.038,.144,.111),(0,.105,.141,.161,.145),
                (0,.076,.247,.153,.130),(0,.046,.325,.125,.102)],
     lower_coat, pelvis, spine1, forward, n=8, ground=True)
loft("Spine1", [(0,.083,.197,.129,.105),(0,.068,.252,.150,.133),(0,.035,.320,.155,.135),
                (0,-.012,.400,.149,.128),(0,-.052,.474,.126,.102)],
     lower_coat, spine1, spine2, forward, n=8)
loft("Spine2", [(0,.001,.344,.120,.110),(0,-.025,.398,.142,.129),
                (0,-.065,.475,.151,.133),(0,-.103,.536,.139,.129),(0,-.126,.592,.097,.093)],
     body_coat, spine2, neck1, forward, n=8)
loft("Neck1", [(0,-.091,.476,.101,.099),
               (0,-.130,.581,.123,.107),(0,-.144,.637,.099,.091),(0,-.151,.673,.079,.069)],
     body_coat, neck1, neck2, (0,-.45,1), n=8)
loft("Neck2", [(0,-.144,.596,.088,.077),(0,-.151,.640,.101,.091),
               (0,-.160,.688,.114,.101),(0,-.169,.751,.086,.081)],
     body_coat, neck2, head, (0,-.45,1), n=8)

ruff = (0,-.212,.66)
# Chest fringe follows the breast, with a pointed lower edge and recessed back.
loft("Ruff", [(0,-.170,.694,.101,.085),(0,-.185,.647,.133,.103),
              (0,-.181,.578,.143,.105),(0,-.160,.497,.121,.130),
              (0,-.177,.421,.093,.110),(0,-.200,.359,.014,.077)],
     lambda j,k: W if k in (0,1,6,7) else W2, ruff, (0,-.225,.359), (0,-.18,-1), n=8)
ruff_low = [v for v in {v for f in m.P.comp[-1][1] for v in f.verts} if v.co.z < .36]
for v in ruff_low:
    # Higher at the edges; central front points hang over the breast.
    v.co.z += (v.co.y + .277) * .39 + abs(v.co.x) * 1.1

for suffix, sign in ((".L", 1), (".R", -1)):
    def leg(name, spec, colors, joint, aim=None, ground=False, rest=(0,0,-1)):
        mirrored = [(sign * x, y, z, rx, ry) for x,y,z,rx,ry in spec]
        mirror = lambda p: (sign*p[0],p[1],p[2])
        loft(name+suffix, mirrored, colors, mirror(joint), mirror(aim) if aim else None,
             rest, ground=ground)

    shoulder, elbow, wrist = (.075,-.183,.488), (.073,-.214,.275), (.072,-.242,.066)
    leg("FrontUpper", [(.076,-.161,.532,.054,.057),(.077,-.182,.464,.055,.058),
                       (.073,-.210,.310,.042,.044),
                       (.073,-.218,.249,.035,.037)],
        lambda j,k: R if j == 0 and k in (2,3,4,5) else W, shoulder, elbow)
    leg("FrontLower", [(.073,-.212,.295,.036,.039),(.073,-.218,.250,.039,.041),
                       (.073,-.231,.156,.034,.035),(.072,-.242,.069,.030,.031),
                       (.072,-.244,.045,.028,.027)],
        W, elbow, wrist)
    leg("FrontFoot", [(.073,-.263,0,.042,.059),(.073,-.265,.010,.046,.062),
                      (.073,-.263,.032,.044,.059),(.072,-.249,.054,.033,.043),
                      (.072,-.242,.095,.027,.027)],
        lambda j,k: SOLE if j == 0 else W, wrist, ground=True)

    hip, stifle, hind_wrist = (.099,.100,.153), (.174,-.063,.156), (.179,-.152,.047)
    leg("HindUpper", [(.134,.081,.013,.054,.084),(.146,.056,.054,.091,.128),
                      (.153,.031,.114,.103,.150),(.154,.021,.181,.104,.143),
                      (.147,.041,.241,.092,.115),(.130,.066,.295,.065,.076),
                      (.105,.076,.337,.033,.041)],
        lambda j,k: K if j >= 3 and k in (3,4,5) else R, hip, stifle,
        rest=(0,.15,-1))
    leg("HindLower", [(.174,-.121,.011,.032,.047),(.176,-.114,.035,.044,.068),
                      (.172,-.091,.079,.052,.064),(.167,-.074,.120,.051,.060),
                      (.153,-.041,.160,.045,.051)],
        R, stifle, hind_wrist)
    leg("HindFoot", [(.181,-.185,0,.046,.064),(.181,-.187,.008,.050,.067),
                     (.180,-.181,.026,.046,.062),(.177,-.161,.047,.034,.043),
                     (.173,-.134,.069,.025,.025)],
        lambda j,k: SOLE if j == 0 else W2 if j == 3 else W, hind_wrist, ground=True)

# Brush curves sideways as it reaches the ground. Each section has a buried cap.
tail = [
    ((0,.216,.180),.042,.050), ((.010,.271,.119),.060,.064),
    ((.054,.313,.063),.070,.062), ((.133,.335,.066),.078,.066),
    ((.228,.333,.066),.082,.066), ((.312,.303,.058),.071,.058),
    ((.377,.251,.046),.058,.046), ((.425,.195,.034),.041,.034),
    ((.449,.142,.024),.019,.024), ((.450,.123,.017),.006,.012),
]
tail = [(Vector(c),w,h) for c,w,h in tail]


def tail_ring(i):
    center, width, height = tail[i]
    tangent = tail[min(i+1,len(tail)-1)][0] - tail[max(i-1,0)][0]
    tangent.z = 0
    side = Vector((-tangent.y, tangent.x, 0)).normalized()
    return [center + side*(width*math.cos(k*math.tau/8)) + Vector((0,0,height*math.sin(k*math.tau/8)))
            for k in range(8)]


for name, a, b in (("Tail1",0,2),("Tail2",2,5),("Tail3",5,9)):
    rings = [tail_ring(i) for i in range(a,b+1)]
    if a:
        center = tail[a][0]
        tucked = center.lerp(tail[a-1][0], .24)
        rings.insert(0,[tucked+(v-center)*.87 for v in rings[0]])
    if b < 9:
        center = tail[b][0]
        tucked = center.lerp(tail[b+1][0], .24)
        rings.append([tucked+(v-center)*.86 for v in rings[-1]])
    colors = lambda j,k: W if a==5 and j>=2 else K if k<4 else R
    m.loft(name,rings,colors,K,W if a==5 else K)
    m.pivot[name] = tail[a][0]
    rotation[name] = axis_rotation((0,1,-.4),tail[b][0]-tail[a][0])

# Reuse the collie's blaze, stop, muzzle, eyes and folded ear construction.
# Trim the mane so only short fur points meet the bib.
dog.MANE = [(b,d,L*.70,w*.88,t,slot) for i,(b,d,L,w,t,slot) in enumerate(dog.MANE) if i not in (3,5,7)]
dog.EAR_D1 = (.82,.05,1)
dog.EAR_FOLD = (-.96,.82,.24)
dog.EAR_UP = .105
head_parts = len(m.P.comp)
dog.build_face(m, dog.build_head(m))
head_rotation = Matrix.Rotation(math.radians(2),3,"X") @ Matrix.Rotation(math.radians(9),3,"Z")
for name, faces, _ in m.P.comp[head_parts:]:
    for v in {v for f in faces for v in f.verts}:
        v.co = head + head_rotation @ ((v.co-dog.HP)*.79)
for name in dog.HEAD_GROUP:
    m.pivot[name] = head + head_rotation @ ((m.pivot[name]-dog.HP)*.79)
    rotation[name] = head_rotation

# Put the origin beneath the seated center of mass without moving ground contacts.
bm = m.P.bm
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
com, _ = dog.com_of(bm)
delta = Vector((-com.x,-com.y,0))
for v in bm.verts:
    v.co += delta
for key in m.pivot:
    m.pivot[key] += delta

bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts)>3])
# BMesh triangulation replaces caps. Refresh component face lists from surviving faces
# and triangulated caps, grouped by connectivity and original part layer.
components = []
remaining = set(bm.faces)
while remaining:
    f = remaining.pop()
    shell = [f]
    for face in shell:
        for edge in face.edges:
            for neighbor in edge.link_faces:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    shell.append(neighbor)
    name = dog.PART_ORDER[f[m.pl]]
    components.append((name,shell,name=="Pelvis" or "Foot." in name))
m.P.comp = components

sc = bpy.context.scene
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
coll = bpy.data.collections.new(dog.ASSET)
sc.collection.children.link(coll)
img = pc.atlas_image("T_Dog_Sit_Codex",str(OUT/"T_Dog_Sit_Codex.png"),dog.PALETTE)
mat = pc.material("M_Dog_Sit_Codex",img)
root, parts = dog.objects(m,coll,mat)
for name, obj in parts.items():
    transform = rotation.get(name, Matrix.Identity(3))
    obj.data.transform(transform.inverted().to_4x4())
    obj.rotation_euler = transform.to_euler("XYZ")
bpy.context.view_layer.update()
checks = pc.comp_checks(m.P, mirror_skip=tuple(dog.HEAD_GROUP)+("Tail1","Tail2","Tail3"))
triangles = sum(len(o.data.polygons) for o in parts.values())
assert triangles <= 2100, triangles
assert not any(checks[k] for k in ("nonmanifold","loose","degenerate")), checks
pts = rn.mesh_points(parts.values())
bounds = [max(v[i] for v in pts)-min(v[i] for v in pts) for i in range(3)]
assert abs(min(v.z for v in pts))<1e-6
print("FINAL", triangles, bounds)

views = {"q":(.70,-1,.21),"side":(1,0,.085),"front":(0,-1,.09),"back":(0,1,.10)}
for key, view in views.items():
    rn.preview(sc,list(parts.values()),str(TEMP/f"sit_{key}.png"),view=view,fill=(.81,.84))

fbx = pc.export(dog.ASSET,coll,root,str(OUT/"Dog_Sit_Codex.fbx"))
pc.verify(fbx)
# Compare actual positions after re-import, allowing for FBX vertex reordering.
from mathutils.kdtree import KDTree
original = {o.name: [o.matrix_world @ v.co for v in o.data.vertices] for o in parts.values()}
def verify_world_vertices():
    window = bpy.context.window
    imported_scene = bpy.data.scenes.new("FBX_Roundtrip")
    window.scene = imported_scene
    bpy.ops.import_scene.fbx(filepath=fbx)
    bpy.context.view_layer.update()
    imported = {o.name.removesuffix(".001"): o for o in imported_scene.objects if o.type=="MESH"}
    assert set(imported)==set(original)
    error = 0
    for name, points in original.items():
        tree = KDTree(len(points))
        for i,p in enumerate(points):
            tree.insert(p,i)
        tree.balance()
        o = imported[name]
        assert len(o.data.vertices)==len(points)
        error = max(error, max(tree.find(o.matrix_world @ v.co)[2] for v in o.data.vertices))
    print("FBX world vertex max error (m):", error)
    assert error < 1e-5, error
    for o in list(imported_scene.objects):
        bpy.data.objects.remove(o,do_unlink=True)
    window.scene = sc
    bpy.data.scenes.remove(imported_scene)
    return error


error = verify_world_vertices()
img.pack()
sc.unit_settings.system = "METRIC"
sc.unit_settings.scale_length = 1
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == "VIEW_3D":
            space = area.spaces.active
            space.region_3d.view_rotation = Vector(views["q"]).to_track_quat("Z","Y")
            space.region_3d.view_location = (0,0,.48)
            space.region_3d.view_distance = 1.82
            space.shading.type = "MATERIAL"
            space.overlay.show_overlays = False
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"Dog_Sit_Codex.blend"))

fmt = lambda v: ", ".join(f"{x:.4f}" for x in v)
with (TEMP/"parts.md").open("w", encoding="utf-8") as table:
    table.write(f"{triangles} tris. Width × length × height {fmt(bounds)} m. FBX re-import maximum world vertex error {error:.2g} m.\n\n")
    table.write("| Part | Location XYZ (m) | Rotation XYZ (°) | Tris |\n|---|---:|---:|---:|\n")
    table.write("| Root | 0, 0, 0 | 0, 0, 0 | 0 |\n")
    for name,obj in parts.items():
        table.write(f"| {name} | {fmt(obj.location)} | {fmt(map(math.degrees,obj.rotation_euler))} | {len(obj.data.polygons)} |\n")

blend_path = OUT/"Dog_Sit_Codex.blend"
bpy.ops.wm.open_mainfile(filepath=str(blend_path))
reopened = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
assert len(reopened) == 28 and all(obj.parent and obj.parent.name == dog.ASSET for obj in reopened)
assert sum(len(obj.data.polygons) for obj in reopened) == triangles
assert bpy.data.images["T_Dog_Sit_Codex"].packed_file
for obj in reopened:
    uv = obj.data.uv_layers.active.data
    for face in obj.data.polygons:
        face_uvs = {tuple(uv[i].uv) for i in face.loop_indices}
        assert len(face_uvs) == 1
        u, v = face_uvs.pop()
        assert all(value in (.125, .375, .625, .875) for value in (u, v))
print("Reopened blend: 28 meshes, packed atlas and per-face palette UVs verified.")

