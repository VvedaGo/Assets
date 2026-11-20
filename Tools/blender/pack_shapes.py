# pack_shapes.py - shared bmesh shape helpers for procedural low-poly pack props (extracted from Farm Processing
# TOL_Tools/build_tools.py, 2026-11-20). All builders add faces to a pack_common.Part with a palette slot per face.
# Default slot constants follow the standard 16-cell flat palette below (override PAL per item; keep cells 0-9 stable).
# Usage in a build script (inside Blender):
#   sys.path.insert(0, <repo>/Tools/blender); import pack_common as pc; from pack_shapes import *
import bmesh, math
from mathutils import Vector, Matrix
import pack_common as pc
from pack_common import Part, ngon, chamf_rect, sweep, rect_prism

# ---------------- standard flat palette (4x4 atlas cells) ----------------
PAL = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
       '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
       '#6E757B', '#A9AFB4', '#B39C74', '#5A3C26',      # cell 10 darker than STA-05 (#C7B288) so perforations read
       '#EADAB4', '#C99263', '#A26A43', '#857B6E']
WOOD, WOOD_D, WOOD_M, CREAM, CREAM_D, RED, RED_D, METAL, METAL_D, METAL_L, CREAM_IN, WOOD_DD, CREAM_B, HWOOD, BLADE, FOOT = range(16)
WOOD, WOOD_D, WOOD_M, CREAM, CREAM_D, RED, RED_D, METAL, METAL_D, METAL_L, CREAM_IN, WOOD_DD, CREAM_B, HWOOD, BLADE, FOOT = range(16)

# ---------------- primitives: rings, planar fills with holes, tubes ----------------
def ringco(z, apo, n, phase=0.5):
    rc = apo / math.cos(math.pi / n)
    return [Vector((rc * math.cos(-math.pi / 2 + (k + phase) * 2 * math.pi / n), rc * math.sin(-math.pi / 2 + (k + phase) * 2 * math.pi / n), z)) for k in range(n)]

def edge(bm, a, b):
    return bm.edges.get((a, b)) or bm.edges.new((a, b))

def fill(P, loops, slot, normal):
    """planar region bounded by loops[0] with holes loops[1:] (scanfill)"""
    es = [edge(P.bm, L[i], L[(i + 1) % len(L)]) for L in loops for i in range(len(L))]
    r = bmesh.ops.triangle_fill(P.bm, use_beauty=True, use_dissolve=False, edges=es, normal=Vector(normal))
    fs = [g for g in r['geom'] if isinstance(g, bmesh.types.BMFace)]
    for f in fs: f[P.slot] = slot
    return fs

def hole_loop(P, c, u, w, r, hn, a0=0.0):
    return [P.bm.verts.new(c + u * r * math.cos(a0 + 2 * math.pi * i / hn) + w * r * math.sin(a0 + 2 * math.pi * i / hn)) for i in range(hn)]

def tube(P, a, b, slot):
    n = len(a); return [P.face([a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]], slot) for i in range(n)]

def blind(P, hl, n_out, depth, wall_slot, bottom_slot):
    """recess behind a hole loop: tube inward by depth along -n_out, closed by a flat bottom"""
    inner = [P.bm.verts.new(v.co - n_out * depth) for v in hl]
    fs = tube(P, hl, inner, wall_slot); fs.append(P.face(list(reversed(inner)), bottom_slot))
    return fs

def shell(P, cname, prof, n, side_slot, cap0, cap1, holes=None, pairs=(), hole_slot=CREAM_IN, cap_holes=None, hn=6, ground=True,
          phase=0.5, a0=0.0):
    """n-gon solid of revolution. prof: [(z, apothem)] closed section path (outer bottom -> up -> rim -> down inside -> floor).
    holes: {band j: (radius, skip_facets)} a hole through every facet of band j; pairs: [(outer band, inner band)] -> tubes.
    A 4-tuple (radius, skip, depth, bottom_slot) makes a blind recess instead (no pair needed).
    cap_holes: [(x, y, r)] holes through both caps (prof[0] and prof[-1]), joined by vertical tubes."""
    holes = holes or {}
    R = [[P.bm.verts.new(v) for v in ringco(z, a, n, phase)] for z, a in prof]; faces = []; H = {}
    for j in range(len(R) - 1):
        for k in range(n):
            A, B, C, D = R[j][k], R[j][(k + 1) % n], R[j + 1][(k + 1) % n], R[j + 1][k]
            s = side_slot(j, k) if callable(side_slot) else side_slot
            if j in holes and k not in holes[j][1]:
                c = (A.co + B.co + C.co + D.co) / 4; u = (B.co - A.co).normalized()
                w = (C.co + D.co) / 2 - (A.co + B.co) / 2; w = (w - u * w.dot(u)).normalized()
                if w.z < 0: w = -w
                hl = hole_loop(P, c, u, w, holes[j][0], hn, a0); H[(j, k)] = hl
                faces += fill(P, [[A, B, C, D], hl], s, u.cross(w))
                if len(holes[j]) == 4: faces += blind(P, hl, u.cross(w).normalized(), holes[j][2], hole_slot, holes[j][3])
            else:
                faces.append(P.face([A, B, C, D], s))
    def cap(ring, z, slot):
        if not cap_holes: return [P.face(list(ring), slot)], []
        hls = [hole_loop(P, Vector((x, y, z)), Vector((1, 0, 0)), Vector((0, 1, 0)), r, hn) for x, y, r in cap_holes]
        return fill(P, [ring] + hls, slot, (0, 0, 1)), hls
    f0, h0 = cap(R[0], prof[0][0], cap0); f1, h1 = cap(R[-1], prof[-1][0], cap1); faces += f0 + f1
    for a, b in zip(h0, h1): faces += tube(P, a, b, hole_slot)
    for jo, ji in pairs:
        for k in range(n):
            if (jo, k) in H: faces += tube(P, H[(jo, k)], H[(ji, k)], hole_slot)
    P.comp.append((cname, faces, ground))


# ---------------- sweeps and plates ----------------
def path_sweep(P, cname, pts, up, sec, slot, slot_cap, closed=False):
    """sweep a 2D section [(side, up)] along a polyline with mitred joints (thickness kept in the bends); closed=True -> ring"""
    up = Vector(up); rings = []; n = len(pts)
    for i, c in enumerate(pts):
        d1 = (c - pts[i - 1]).normalized() if (i > 0 or closed) else None
        d2 = (pts[(i + 1) % n] - c).normalized() if (i < n - 1 or closed) else None
        t = (d1 + d2).normalized() if d1 and d2 else (d1 or d2)
        k = 1.0 / t.dot(d1) if d1 and d2 else 1.0
        sd = t.cross(up).normalized(); uu = sd.cross(t).normalized()
        rings.append([c + sd * x * k + uu * y for x, y in sec])
    if closed: return P.torus_loft(cname, rings, slot)
    return P.loft(cname, rings, slot, slot_cap, slot_cap)

def flat_plate(P, cname, outline, z0, z1, holes, slot_top, slot_bot, slot_side, slot_hole, ground=True):
    """flat plate from a CCW outline [(x, y)] with through-holes (list of [(x, y)] loops), top/bottom via scanfill"""
    bm = P.bm
    ob = [bm.verts.new((x, y, z0)) for x, y in outline]; ot = [bm.verts.new((x, y, z1)) for x, y in outline]
    hb = [[bm.verts.new((x, y, z0)) for x, y in h] for h in holes]; ht = [[bm.verts.new((x, y, z1)) for x, y in h] for h in holes]
    faces = fill(P, [ot] + ht, slot_top, (0, 0, 1)) + fill(P, [ob] + hb, slot_bot, (0, 0, 1)) + tube(P, ob, ot, slot_side)
    for a, b in zip(hb, ht): faces += tube(P, a, b, slot_hole)
    P.comp.append((cname, faces, ground))


# ---------------- hardware ----------------
def bolt(P, p0, axis, r=0.008, h=0.010, sunk=0.003):
    a = Vector(axis).normalized(); p0 = Vector(p0)
    ref = (0, 0, 1) if abs(a.z) < 0.9 else (1, 0, 0)
    sweep(P, 'bolt', p0 - a * sunk, p0 + a * h, ngon(r, 6, math.pi / 2), [(0, 1, 0), (1, 0.75, 0)], METAL, METAL, METAL_L, ref=ref)

def oct_rod(P, cname, p0, p1, radii, slot, slot_cap, n=8, ref=(0, 0, 1)):
    """octagonal rod along p0->p1, radii = [(t, r)]"""
    r0 = max(r for _, r in radii)
    sweep(P, cname, p0, p1, ngon(r0, n, math.pi / n), [(t, r / r0, 0) for t, r in radii], slot, slot_cap, slot_cap, ref=ref)


# ---------------- boards, basins, outlines ----------------
def plank4(P, cn, x0, x1, y0, y1, z0, z1, ch, side, top):
    """4-sided board with a top chamfer (20 tris); its side faces stay vertical up to z1-ch"""
    def ring(z, d): return [Vector(v) for v in ((x0 + d, y0 + d, z), (x1 - d, y0 + d, z), (x1 - d, y1 - d, z), (x0 + d, y1 - d, z))]
    P.loft(cn, [ring(z0, 0), ring(z1 - ch, 0), ring(z1, ch)], lambda j, k: side if j == 0 else top, side, top)

def basin_loft(P, cn, cx, cy, z_bot, z_top, z_flange, bot_wh, top_wh, fl_wh, in_wh, z_floor, c, out_slot, rim_slot, in_slot, floor_slot):
    """open rectangular basin: outer wall bottom->top, flange (outer lip), inner wall down to a floor (closed manifold)"""
    def R(z, wh, cc): return [Vector((cx + x, cy + y, z)) for x, y in chamf_rect(wh[0], wh[1], cc)]
    rings = [R(z_bot, bot_wh, c * 0.8), R(z_top, top_wh, c), R(z_top, fl_wh, c * 1.1), R(z_flange, fl_wh, c * 1.1),
             R(z_flange, in_wh, c * 0.9), R(z_floor, (in_wh[0] - 0.06, in_wh[1] - 0.06), c * 0.7)]
    P.loft(cn, rings, lambda j, k: (out_slot, rim_slot, rim_slot, rim_slot, in_slot)[j], out_slot, floor_slot)

def poly_offset(pts, d):
    """true-miter inward offset of a closed polygon (any orientation)"""
    n = len(pts); area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n)); sg = 1 if area > 0 else -1
    def nrm(a, b):
        dx, dz = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dz); return (-dz / L * sg, dx / L * sg)
    out = []
    for i in range(n):
        n1, n2 = nrm(pts[i - 1], pts[i]), nrm(pts[i], pts[(i + 1) % n]); k = d / max(1e-6, 1 + n1[0] * n2[0] + n1[1] * n2[1])
        out.append((pts[i][0] + k * (n1[0] + n2[0]), pts[i][1] + k * (n1[1] + n2[1])))
    return out

def arc(zc, r, x_from, x_to, n):
    a0 = math.atan2(math.sqrt(max(r * r - x_from * x_from, 0)), x_from); a1 = math.atan2(math.sqrt(max(r * r - x_to * x_to, 0)), x_to)
    return [(r * math.cos(a0 + (a1 - a0) * k / n), zc + r * math.sin(a0 + (a1 - a0) * k / n)) for k in range(1, n)]


# ---------------- placement ----------------
def rest_on_ground(P):
    """tilt about X so the lowest point of the front half and of the back half both touch z=0 (a tool lying on a table)"""
    # rigid body on a plane: it rests on the edge of the lower convex hull (YZ projection) that lies under the centre
    vs = list(P.bm.verts); yc = (min(v.co.y for v in vs) + max(v.co.y for v in vs)) / 2
    pts = sorted({(round(v.co.y, 6), round(v.co.z, 6)) for v in vs})
    hull = []
    for p in pts:                                               # monotone chain, lower hull
        while len(hull) >= 2 and (hull[-1][0] - hull[-2][0]) * (p[1] - hull[-2][1]) - (hull[-1][1] - hull[-2][1]) * (p[0] - hull[-2][0]) <= 0:
            hull.pop()
        hull.append(p)
    p, q = next((a_, b_) for a_, b_ in zip(hull, hull[1:]) if a_[0] <= yc <= b_[0])
    a = math.atan2(-(q[1] - p[1]), q[0] - p[0])                 # rotate so p and q get the same height
    M = Matrix.Rotation(a, 4, 'X')                              # z' = y sin a + z cos a
    for v in vs: v.co = M @ v.co
    print(f'  rest tilt {math.degrees(a):.2f} deg')

def center_on_ground(P):
    vs = list(P.bm.verts)
    lo = [min(v.co[i] for v in vs) for i in range(3)]; hi = [max(v.co[i] for v in vs) for i in range(3)]
    off = Vector(((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]))
    for v in vs: v.co -= off


# ---------------- furniture members ----------------
def box(P, cn, x0, x1, y0, y1, z0, z1, side, top, c=0.006, ground=False):
    rect_prism(P, cn, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, c, [(z0, 0), (z1, 0)], side, top, top, ground=ground)

def plain_box(P, cn, x0, x1, y0, y1, z0, z1, side, top):
    """4-sided box (12 tris) for slats/caps"""
    sweep(P, cn, ((x0 + x1) / 2, (y0 + y1) / 2, z0), ((x0 + x1) / 2, (y0 + y1) / 2, z1),
          [((x1 - x0) / 2, (y1 - y0) / 2), (-(x1 - x0) / 2, (y1 - y0) / 2), (-(x1 - x0) / 2, -(y1 - y0) / 2), ((x1 - x0) / 2, -(y1 - y0) / 2)],
          [(0, 1, 0), (1, 1, 0)], side, top, top, ref=(1, 0, 0))

def splay_leg(P, foot, top, s=0.10, c=0.012):
    sweep(P, 'leg', foot, top, chamf_rect(s, s, c), [(0, 1, 0), (1, 1, 0)], WOOD, WOOD_M, WOOD_M, ref=(0, 1, 0), flat0=True, ground=True)

def red_cap(P, x, y_face, z, size=0.050, t=0.012):
    plain_box(P, 'cap', x - size / 2, x + size / 2, y_face - t, y_face + 0.002, z - size / 2, z + size / 2, RED, RED_D)
