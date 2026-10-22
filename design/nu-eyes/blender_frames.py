#!/usr/bin/env python3
# SPDX-License-Identifier: CC-BY-4.0
"""nu.eyes — the five frames, built to size, for the web viewer, AR try-on and the catalogue renders.

  strap     goggle glasses: one wraparound shield lens, thin rim all round, short arms and a wide strap
  shade     the bold square sunglass: thick acetate, flat brow, soft corners
  print     the oversized cat-eye with the ÑÜ mirror print across the lenses
  wayfarer  the classic: wide flat brow, flared top corners, lens bottom rising to the outside, tilted forward
  round     thin metal panto: round below, flatter on top, keyhole bridge, nose pads

The acetate fronts are one solid plate cut from a single silhouette (two rims, bridge and end pieces
together), with rounded edges, a slight forward tilt and little wrap, the way current frames are made.

Units are metres. Blender axes: X across the face, -Y forward (out of the face), Z up. The origin is
midway between the two lens centres, on the lens plane, so the glTF (+Z out of the face, Y up) and
the USDZ (RealityKit, same) land with the origin between the pupils.

Every frame has the same part names, so code recolours by name:
  frame    front plate or wire rims     lens     the lenses (UV in 5 cm units, for the print)
  temples  the arms                     metal    hinges, rivets, logo, wire parts
  strap    strap band and slider        pads     nose pads

Run headless (Blender 5):
  blender -b -P blender_frames.py -- --out /tmp/nu-eyes [--print nu-print.png] [--render] [--only a,b]
Writes <id>.glb, <id>.usdz, frames.json, and with --render <id>.png catalogue stills.
"""
import json
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

N = 128  # outline samples per lens
RAYS = 200  # radial samples around each opening


# ----------------------------------------------------------------------------- outlines

def outline(spec):
    """Right lens outline (+X side, inner edge toward -x), counter-clockwise, lens-local metres."""
    a, b, n = spec["a"], spec["b"], spec["n"]
    n_top = spec.get("n_top", n)
    pts = []
    for i in range(N):
        t = 2 * math.pi * i / N
        c, s = math.cos(t), math.sin(t)
        e = n_top if s > 0 else n
        x = a * math.copysign(abs(c) ** (2 / e), c)
        y = b * math.copysign(abs(s) ** (2 / e), s)
        xn, yn = x / a, y / b
        # Trapezoid: the top is wider than the bottom, more on the outer side.
        x *= 1 + (spec.get("taper", 0) if xn > 0 else spec.get("taper_in", 0)) * yn
        # The bottom edge climbs toward the outer side (wayfarer).
        rise = spec.get("rise", 0)
        if rise and yn < 0:
            y += rise * (0.5 + 0.5 * xn) * (-yn)
        # Cat-eye lift at the outer top corner.
        lift = spec.get("lift", 0)
        if lift and xn > 0 and yn > 0:
            y += lift * (xn ** 3) * (yn ** 0.6)
        # Nose cut at the inner bottom.
        nose = spec.get("nose", 0)
        if nose and xn < 0 and yn < 0:
            y += nose * (max(0.0, -xn - 0.25) / 0.75) ** 2 * (-yn) ** 0.5
        pts.append((x, y))
    return pts


def offset(pts, width_fn):
    """Push each point of a counter-clockwise outline out along its normal by width_fn(nx, ny, x, y)."""
    out = []
    k = len(pts)
    for i in range(k):
        x0, y0 = pts[i - 1]
        x2, y2 = pts[(i + 1) % k]
        dx, dy = x2 - x0, y2 - y0
        ln = math.hypot(dx, dy) or 1
        nx, ny = dy / ln, -dx / ln
        w = width_fn(nx, ny, *pts[i])
        out.append((pts[i][0] + nx * w, pts[i][1] + ny * w))
    return out


def cast(c, ang, polys):
    """Farthest point where a ray from c at angle ang leaves the union of the polygons."""
    dx, dz = math.cos(ang), math.sin(ang)
    best = 0.0
    for poly in polys:
        k = len(poly)
        for i in range(k):
            px, pz = poly[i]
            qx, qz = poly[(i + 1) % k]
            ex, ez = qx - px, qz - pz
            den = dx * ez - dz * ex
            if abs(den) < 1e-15:
                continue
            wx, wz = px - c[0], pz - c[1]
            t = (wx * ez - wz * ex) / den
            s = (wx * dz - wz * dx) / den
            if t > 0 and -1e-9 <= s <= 1 + 1e-9:
                best = max(best, t)
    x, z = c[0] + dx * best, c[1] + dz * best
    return (0.0 if abs(x) < 1e-7 else x, z)


def inside(poly, p):
    x, z = p
    hit = False
    for i in range(len(poly)):
        (x0, z0), (x1, z1) = poly[i - 1], poly[i]
        if (z0 > z) != (z1 > z) and x < x0 + (z - z0) * (x1 - x0) / (z1 - z0):
            hit = not hit
    return hit


def nearest(poly, p):
    return min(range(len(poly)), key=lambda i: (poly[i][0] - p[0]) ** 2 + (poly[i][1] - p[1]) ** 2)


def arc(poly, i, j):
    """Points of a closed outline from index i to j inclusive, going forward."""
    out = [poly[i]]
    while i != j:
        i = (i + 1) % len(poly)
        out.append(poly[i])
    return out


def length(pts):
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def resample(pts, m):
    """m points evenly by arc length along an open polyline, from its start up to (not including) its end."""
    total = length(pts) or 1
    out, seg, run = [], 0, 0.0
    for s in range(m):
        target = total * s / m
        while seg < len(pts) - 2 and run + math.dist(pts[seg], pts[seg + 1]) < target:
            run += math.dist(pts[seg], pts[seg + 1])
            seg += 1
        d = math.dist(pts[seg], pts[seg + 1]) or 1
        f = min(1.0, (target - run) / d)
        out.append((pts[seg][0] + (pts[seg + 1][0] - pts[seg][0]) * f, pts[seg][1] + (pts[seg + 1][1] - pts[seg][1]) * f))
    return out


def angles(c, extra=()):
    """Uniform ray angles around c, plus rays aimed exactly at the given corner points."""
    out = [2 * math.pi * i / RAYS for i in range(RAYS)]
    out += [math.atan2(z - c[1], x - c[0]) % (2 * math.pi) for x, z in extra]
    return sorted(set(round(a, 9) for a in out))


# ----------------------------------------------------------------------------- mesh helpers

def new_obj(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return ob


def plate(name, halves, depth, bevel, rows=3):
    """Solid front from one or more (opening, silhouette) pairs with matching samples; seams at x = 0 weld shut."""
    bm = bmesh.new()
    for H, O, flip in halves:
        k = len(H)
        grid = [[bm.verts.new((h[0] + (o[0] - h[0]) * r / rows, 0, h[1] + (o[1] - h[1]) * r / rows))
                 for h, o in zip(H, O)] for r in range(rows + 1)]
        for r in range(rows):
            for i in range(k):
                j = (i + 1) % k
                q = (grid[r][i], grid[r][j], grid[r + 1][j], grid[r + 1][i])
                bm.faces.new(q[::-1] if flip else q)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-7)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = new_obj(name, bm)
    sol = ob.modifiers.new("solid", "SOLIDIFY")
    sol.thickness = depth
    sol.offset = 0
    bev = ob.modifiers.new("bevel", "BEVEL")
    bev.width = bevel
    bev.segments = 3
    bev.limit_method = "ANGLE"
    apply_mods(ob)
    return ob


def lens(name, pts, c, y0=0.0, rings=(0.2, 0.4, 0.6, 0.8, 1.0)):
    """Lens surface: a fan from c out to the outline, normals forward (-Y), planar UVs in 5 cm units."""
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    centre = bm.verts.new((c[0], y0, c[1]))
    loops = [[bm.verts.new((c[0] + (x - c[0]) * s, y0, c[1] + (z - c[1]) * s)) for x, z in pts] for s in rings]
    k = len(pts)
    for i in range(k):
        j = (i + 1) % k
        bm.faces.new((centre, loops[0][i], loops[0][j]))
        for r in range(len(rings) - 1):
            bm.faces.new((loops[r][i], loops[r + 1][i], loops[r + 1][j], loops[r][j]))
    for f in bm.faces:
        f.normal_update()
        if f.normal.y > 0:
            f.normal_flip()
        for loop in f.loops:
            co = loop.vert.co
            loop[uv].uv = (co.x / 0.05, co.z / 0.05)
    return new_obj(name, bm)


def sweep(name, path, w_fn, h_fn, round_=False, seg=8):
    """Tube along a polyline. Rectangular (w across, h up) or round (radius w)."""
    bm = bmesh.new()
    loops = []
    k = len(path)
    for i, p in enumerate(path):
        p = Vector(p)
        a = Vector(path[max(i - 1, 0)])
        b = Vector(path[min(i + 1, k - 1)])
        t = (b - a).normalized()
        up = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        side = t.cross(up).normalized()
        up = side.cross(t).normalized()
        u = i / max(k - 1, 1)
        w, h = w_fn(u), h_fn(u)
        if round_:
            ring_ = [p + side * (w * math.cos(2 * math.pi * s / seg)) + up * (w * math.sin(2 * math.pi * s / seg)) for s in range(seg)]
        else:
            ring_ = [p + side * w / 2 + up * h / 2, p - side * w / 2 + up * h / 2, p - side * w / 2 - up * h / 2, p + side * w / 2 - up * h / 2]
        loops.append([bm.verts.new(v) for v in ring_])
    m = len(loops[0])
    for i in range(k - 1):
        for s in range(m):
            s2 = (s + 1) % m
            bm.faces.new((loops[i][s], loops[i][s2], loops[i + 1][s2], loops[i + 1][s]))
    bm.faces.new(list(reversed(loops[0])))
    bm.faces.new(loops[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_obj(name, bm)


def rounded(ob, width, segments=2):
    bev = ob.modifiers.new("bevel", "BEVEL")
    bev.width = width
    bev.segments = segments
    bev.limit_method = "ANGLE"
    apply_mods(ob)
    return ob


def apply_mods(ob):
    bpy.context.view_layer.objects.active = ob
    for m in list(ob.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)


def mirror_x(ob, name):
    cp = ob.copy()
    cp.data = ob.data.copy()
    cp.name = name
    bpy.context.collection.objects.link(cp)
    for v in cp.data.vertices:
        v.co.x = -v.co.x
    cp.data.flip_normals()
    if cp.data.uv_layers:
        # Planar UVs from the mirrored positions, so the print reads the right way on both lenses.
        uv = cp.data.uv_layers.active.data
        for poly in cp.data.polygons:
            for li in poly.loop_indices:
                co = cp.data.vertices[cp.data.loops[li].vertex_index].co
                uv[li].uv = (co.x / 0.05, co.z / 0.05)
    return cp


def tilt_yz(y, z, deg):
    """Pantoscopic tilt: the top of the front comes forward (-Y)."""
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return y * c - z * s, y * s + z * c


def tilt(obs, deg):
    for ob in obs:
        for v in ob.data.vertices:
            v.co.y, v.co.z = tilt_yz(v.co.y, v.co.z, deg)


def wrap(ob, k):
    """Bend the whole frame back around the face: y += k·x²."""
    for v in ob.data.vertices:
        v.co.y += k * v.co.x * v.co.x


def join(name, obs):
    obs = [o for o in obs if o]
    if not obs:
        return None
    bpy.ops.object.select_all(action="DESELECT")
    for o in obs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    if len(obs) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = name
    ob.data.name = name
    return ob


def logo(name, x, y, z, side, size=0.0052):
    bpy.ops.object.text_add(location=(0, 0, 0))
    t = bpy.context.object
    t.data.body = "ÑÜ"
    font = os.environ.get("NU_EYES_FONT")
    if font and os.path.exists(font):
        t.data.font = bpy.data.fonts.load(font)
    t.data.size = size
    t.data.extrude = 0.00012
    t.data.align_x = "CENTER"
    t.data.align_y = "CENTER"
    bpy.ops.object.convert(target="MESH")
    t = bpy.context.object
    t.name = name
    # Text lies in XY facing +Z; stand it on the outer face of the temple, reading front to back.
    t.rotation_euler = (math.pi / 2, 0, math.pi / 2 if side > 0 else -math.pi / 2)
    t.location = (x, y, z)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return t


def edge_x(pts, z, band=0.0025):
    """Outermost x of an outline near height z."""
    near = [p[0] for p in pts if abs(p[1] - z) < band]
    return max(near) if near else max(p[0] for p in pts)


# ----------------------------------------------------------------------------- frames

FRAMES = {
    "strap": dict(name="strap", kind="shield", a=0.0305, b=0.0230, n=3.0, n_top=8.0, taper=0.06, nose=0.011,
                  bridge=0.014, rim=0.0024, brow=0.0012, depth=0.0040, band_top=1.0, band_bot=-0.0015,
                  tilt=6, wrap=4.2, hinge=0.010, temple_w=0.0030, temple_h=0.0075, strap=True),
    "shade": dict(name="shade", kind="plate", a=0.0262, b=0.0212, n=4.0, n_top=5.0, taper=0.04, nose=0.006,
                  bridge=0.020, rim=0.0050, brow=0.0010, wing=0.0010, depth=0.0070, bridge_h=0.0066, arch=0.004,
                  dip=0.0008, tilt=7, wrap=1.4, hinge=0.010, temple_w=0.0036, temple_h=0.0090),
    "print": dict(name="ñü print", kind="plate", a=0.0285, b=0.0212, n=3.0, n_top=3.6, taper=0.16, rise=0.004,
                  lift=0.011, nose=0.008, bridge=0.018, rim=0.0045, brow=0.0008, wing=0.0065, depth=0.0064,
                  bridge_h=0.0064, arch=0.004, dip=0.0015, tilt=7, wrap=1.6, hinge=0.012, temple_w=0.0034,
                  temple_h=0.0085),
    "wayfarer": dict(name="wayfarer", kind="plate", a=0.0250, b=0.0195, n=3.6, n_top=8.0, taper=0.22,
                     taper_in=0.04, rise=0.0045, lift=0.0025, nose=0.006, bridge=0.019, rim=0.0040, brow=0.0035,
                     wing=0.0035, depth=0.0072, bridge_h=0.0075, arch=0.003, dip=0.0004, tilt=9, wrap=1.2,
                     hinge=0.013, temple_w=0.0038, temple_h=0.0105),
    "round": dict(name="round", kind="wire", a=0.0236, b=0.0228, n=2.0, n_top=2.8, bridge=0.019, rim=0.0009,
                  tilt=6, wrap=0.9, pads=True),
}
TEMPLE_LENGTH = 0.145


def temple_path(x0, y0, z0, L=TEMPLE_LENGTH, splay=0.010, drop=0.034):
    """Straight back with a slight splay, then down behind the ear."""
    path = []
    for i in range(25):
        u = i / 24
        y = y0 + u * L
        z = z0
        if u * L > 0.104:
            z = z0 - drop * ((u * L - 0.104) / (L - 0.104)) ** 1.6
        path.append((x0 + splay * u, y, z))
    return path


def front_plate(spec, cx, pts):
    """Two rims, bridge and end pieces as one acetate silhouette, sampled from the right lens centre."""
    a, b = spec["a"], spec["b"]
    hole = [(cx + x, z) for x, z in pts]

    def rim_w(nx, ny, x, z):
        px, pz = (x - cx) / a, z / b
        # Thinner beside the nose, heavier along the brow, flared at the outer top corner.
        return (spec["rim"] * (1 - 0.3 * max(0.0, -px) ** 2) + spec["brow"] * max(0.0, ny) ** 1.5
                + spec.get("wing", 0) * max(0.0, px) ** 3 * max(0.0, pz) ** 0.5)

    sil = offset(hole, rim_w)
    xr = cx - 0.55 * a
    top = [i for i, (x, z) in enumerate(sil) if z > 0]
    T = min(top, key=lambda i: abs(sil[i][0] - xr))
    zt = sil[T][1] - spec.get("dip", 0)
    zb = zt - spec["bridge_h"]
    # The half silhouette, counter-clockwise from the top of the centre seam: down the seam, out along a
    # round arch under the bridge, round the rim, then a straight brow back to the seam.
    seam = [(0.0, zt + (zb - zt) * i / 8) for i in range(9)]
    arch = []
    for i in range(1, 400):
        x = xr * i / 400
        z = zb - spec["arch"] * (x / (spec["bridge"] / 2)) ** 2
        if inside(sil, (x, z)):
            break
        arch.append((x, z))
    J = nearest(sil, arch[-1] if arch else seam[-1])
    brow = [(sil[T][0] * (1 - i / 8), sil[T][1] + (zt - sil[T][1]) * i / 8) for i in range(1, 8)]
    S = seam + arch + arc(sil, J, T) + brow

    # Pair the opening with the silhouette by arc length between matching anchors.
    c = (cx, 0.0)
    anchors = [(nearest(hole, (cx - a, zt)), 0), (nearest(hole, (cx - a, zb)), len(seam) - 1),
               (nearest(hole, sil[J]), len(seam) + len(arch))]
    for t in (-math.pi / 2, 0.0, math.pi / 2):
        anchors.append((nearest(hole, cast(c, t, [hole])), nearest(S, cast(c, t, [S]))))
    k = len(hole)
    start = anchors[0][0]
    anchors.sort(key=lambda p: (p[0] - start) % k)
    H, O = [], []
    for (h0, s0), (h1, s1) in zip(anchors, anchors[1:] + anchors[:1]):
        hs, ss = arc(hole, h0, h1), arc(S, s0, s1)
        m = max(4, math.ceil(max(length(hs), length(ss)) / 0.0009))
        H += resample(hs, m)
        O += resample(ss, m)
    return c, H, O


def shield(spec, cx, pts):
    """One lens across both eyes: the two lens shapes joined by a band, cut for the nose."""
    b = spec["b"]
    right = [(cx + x, z) for x, z in pts]
    left = [(-x, z) for x, z in reversed(right)]
    band = [(-cx, spec["band_bot"]), (cx, spec["band_bot"]), (cx, spec["band_top"] * b), (-cx, spec["band_top"] * b)]
    c = (0.0, 0.006)
    H = [cast(c, t, [right, left, band]) for t in angles(c)]
    O = offset(H, lambda nx, ny, x, z: spec["rim"] + spec["brow"] * max(0.0, ny) ** 1.5)
    return c, H, O


def build(fid):
    spec = FRAMES[fid]
    kind = spec["kind"]
    a, bridge = spec["a"], spec["bridge"]
    cx = bridge / 2 + a
    pts = outline(spec)
    deg = spec.get("tilt", 0)

    rims, lenses, metal, temples, strap, pads = [], [], [], [], [], []

    if kind == "wire":
        lens_r = lens("lens_R", [(cx + x, z) for x, z in offset(pts, lambda *_: 0.0004)], (cx, 0.0), y0=-0.0002)
        lenses += [lens_r, mirror_x(lens_r, "lens_L")]
        rim_path = [(cx + x, 0, z) for x, z in pts] + [(cx + pts[0][0], 0, pts[0][1])]
        rim_r = sweep("rim_R", rim_path, lambda u: spec["rim"], lambda u: 0, round_=True)
        rims += [rim_r, mirror_x(rim_r, "rim_L")]
        br = [(-bridge / 2 - 0.0005 + bridge * 1.02 * i / 16, 0, 0.004 + 0.0055 * math.sin(math.pi * i / 16)) for i in range(17)]
        rims.append(sweep("bridge", br, lambda u: spec["rim"] * 1.05, lambda u: 0, round_=True))
        px, pz = bridge / 2 + 0.0035, -0.010
        pr = [sweep("padarm_R", [(bridge / 2 + 0.002, 0, 0.004), (px, 0.006, pz + 0.003), (px - 0.001, 0.009, pz)],
                    lambda u: 0.0005, lambda u: 0, round_=True)]
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.004, location=(px - 0.0015, 0.010, pz))
        pad = bpy.context.object
        pad.name = "pad_R"
        pad.scale = (0.35, 0.8, 1.25)
        pad.rotation_euler = (0, 0, math.radians(-30))
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        pads += [pad, mirror_x(pad, "pad_L")]
        metal += pr + [mirror_x(o, o.name.replace("_R", "_L")) for o in pr]
        hx, hz, back = cx + a + spec["rim"], 0.004, 0.0
        sil = [(cx + x, z) for x, z in pts]
    elif kind == "plate":
        c, H, O = front_plate(spec, cx, pts)
        rims.append(plate("front", [(H, O, False), ([(-x, z) for x, z in H], [(-x, z) for x, z in O], True)],
                          spec["depth"], 0.0011, rows=2))
        lens_r = lens("lens_R", offset(H, lambda *_: 0.0005), c, y0=-0.0003)
        lenses += [lens_r, mirror_x(lens_r, "lens_L")]
        hz = spec["hinge"]
        hx = edge_x(O, hz)
        # Two pins on the front of each end piece, between the lens and the outer edge.
        pin_x = (edge_x(H, hz) + hx) / 2 + 0.0008
        for k, dz in enumerate((0.0016, -0.0016)):
            pin = sweep(f"pin{k}_R", [(pin_x, -spec["depth"] / 2 - 0.00015, hz + dz), (pin_x, -spec["depth"] / 2 + 0.001, hz + dz)],
                        lambda u: 0.00062, lambda u: 0, round_=True, seg=12)
            metal += [pin, mirror_x(pin, f"pin{k}_L")]
        back = spec["depth"] / 2
        sil = O
    else:
        c, H, O = shield(spec, cx, pts)
        rims.append(plate("front", [(H, O, False)], spec["depth"], 0.0008, rows=2))
        lenses.append(lens("lens", offset(H, lambda *_: 0.0005), c, y0=-0.0002, rings=(0.12, 0.25, 0.4, 0.55, 0.7, 0.85, 1.0)))
        hz = spec["hinge"]
        hx = edge_x(O, hz)
        back = spec["depth"] / 2
        sil = O

    tilt(rims + lenses + pads + metal, deg)

    # Arms start at the back of the end piece, wherever the tilt put it.
    hy, hz2 = tilt_yz(back, hz, deg)
    if kind == "wire":
        tpath = temple_path(hx - 0.0015, hy + 0.003, hz2)
        temples.append(sweep("temple_R", tpath, lambda u: 0.0008, lambda u: 0, round_=True))
        # Acetate tip over the last third of the arm.
        tip = [p for i, p in enumerate(tpath) if i >= 15]
        temples.append(sweep("tip_R", tip, lambda u: 0.0016, lambda u: 0, round_=True, seg=10))
        metal.append(sweep("hinge_R", [(hx - 0.004, tilt_yz(0, hz, deg)[0], hz2), (hx - 0.0015, hy + 0.004, hz2)],
                           lambda u: 0.0012, lambda u: 0, round_=True))
    else:
        tw, th = spec["temple_w"], spec["temple_h"]
        x0 = hx - tw / 2 - 0.0002
        w_fn = lambda u: tw - 0.0008 * u
        h_fn = lambda u: th * (1 - 0.5 * u)
        tpath = temple_path(x0, hy + 0.0002, hz2, L=0.112 if kind == "shield" else TEMPLE_LENGTH,
                            drop=0.020 if kind == "shield" else 0.034)
        temples.append(rounded(sweep("temple_R", tpath, w_fn, h_fn), min(tw, th) * 0.3))
        metal.append(sweep("hinge_R", [(x0 - tw / 2 - 0.0006, hy + 0.0005, hz2), (x0 - tw / 2 - 0.0006, hy + 0.011, hz2)],
                           lambda u: 0.0014, lambda u: 0.0034))
        u_l = 0.030 / TEMPLE_LENGTH
        metal.append(logo("logo_R", x0 + 0.010 * u_l + w_fn(u_l) / 2 + 0.00006, hy + 0.030, hz2, +1,
                          size=min(0.0052, th * 0.6)))

    left = lambda obs: [mirror_x(o, o.name.replace("_R", "_L")) for o in obs if o.name.endswith("_R")]
    temples += left(temples)
    metal += left([m for m in metal if m.name.startswith(("hinge", "logo"))])

    if spec.get("strap"):
        # A wide band from end piece to end piece around the back of the head, with a slider at the back.
        sx = hx + 0.003
        z = hz2 - 0.001
        pts3 = [(sx, hy + 0.004, z), (sx + 0.004, 0.040, z)]
        for i in range(1, 40):
            ph = -math.radians(10) + math.radians(200) * i / 40
            pts3.append((0.083 * math.cos(ph), 0.112 + 0.100 * math.sin(ph), z - 0.003 * math.sin(ph)))
        pts3 += [(-sx - 0.004, 0.040, z), (-sx, hy + 0.004, z)]
        strap.append(sweep("band", pts3, lambda u: 0.0014, lambda u: 0.022))
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.2128, z))
        bk = bpy.context.object
        bk.name = "slider"
        bk.scale = (0.018, 0.0028, 0.025)
        bpy.ops.object.transform_apply(scale=True)
        strap.append(rounded(bk, 0.0009))
        # Loops at each end piece the band runs through.
        for side in (1, -1):
            loop = sweep(f"loop{side}", [(side * (hx + 0.0005), hy + 0.0005, z), (side * (hx + 0.0045), hy + 0.006, z)],
                         lambda u: 0.0035, lambda u: 0.024)
            rims.append(rounded(loop, 0.0008))

    parts = {
        "frame": join("frame", rims),
        "lens": join("lens", lenses),
        "temples": join("temples", temples),
        "metal": join("metal", metal),
        "strap": join("strap", strap),
        "pads": join("pads", pads),
    }
    for name, ob in parts.items():
        if ob is None:
            continue
        wrap(ob, spec["wrap"])
        ob.data.materials.clear()
        ob.data.materials.append(material(name, fid))
        for poly in ob.data.polygons:
            poly.use_smooth = name != "lens"
        if name != "lens":
            # Planar UVs in 5 cm units for acetate patterns: across the front, along the arms.
            uv = (ob.data.uv_layers.get("UVMap") or ob.data.uv_layers.new(name="UVMap")).data
            for poly in ob.data.polygons:
                for li in poly.loop_indices:
                    co = ob.data.vertices[ob.data.loops[li].vertex_index].co
                    uv[li].uv = ((co.y if name in ("temples", "strap") else co.x) / 0.05, co.z / 0.05)

    width = 2 * (max(p[0] for p in sil) + 0.002)
    meta = dict(id=fid, name=spec["name"], lensCenter=round(cx, 5), lensWidth=round(2 * a, 4),
                lensHeight=round(2 * spec["b"], 4), bridge=bridge, width=round(width, 4), templeLength=TEMPLE_LENGTH,
                wire=kind == "wire", strap=bool(spec.get("strap")))
    return parts, meta


# ----------------------------------------------------------------------------- materials (renders + export defaults)

DEFAULTS = {
    "strap": dict(frame=(0.02, 0.02, 0.022), rough=0.55, coat=0.0, lens=(0.95, 0.30, 0.08), mirror=True),
    "shade": dict(frame=(0.01, 0.01, 0.012), rough=0.28, coat=0.3, lens=(0.06, 0.06, 0.07)),
    "print": dict(frame=(0.012, 0.012, 0.014), rough=0.15, lens=(0.08, 0.08, 0.09), print=True),
    "wayfarer": dict(frame=(0.10, 0.045, 0.02), rough=0.2, lens=(0.12, 0.20, 0.10)),
    "round": dict(frame=(0.83, 0.62, 0.30), rough=0.25, metal=True, lens=(0.9, 0.9, 0.92), clear=True),
}
PRINT_PNG = None
# Tiles per 5 cm of lens: about two ÑÜ marks across each lens.
PRINT_REPEAT = 1.35


def principled(m):
    m.use_nodes = True
    return next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def material(role, fid):
    d = DEFAULTS[fid]
    m = bpy.data.materials.new(role)
    bsdf = principled(m)
    gold = (0.85, 0.66, 0.34, 1)
    if role in ("frame", "temples"):
        if d.get("metal"):
            bsdf.inputs["Base Color"].default_value = gold
            bsdf.inputs["Metallic"].default_value = 1.0
            bsdf.inputs["Roughness"].default_value = 0.22
        else:
            bsdf.inputs["Base Color"].default_value = (*d["frame"], 1)
            bsdf.inputs["Roughness"].default_value = d["rough"]
            try:
                bsdf.inputs["Coat Weight"].default_value = d.get("coat", 0.6)
            except KeyError:
                pass
    elif role == "metal":
        bsdf.inputs["Base Color"].default_value = gold if d.get("metal") else (0.85, 0.85, 0.87, 1)
        bsdf.inputs["Metallic"].default_value = 1.0
        bsdf.inputs["Roughness"].default_value = 0.2
    elif role in ("strap", "foam"):
        bsdf.inputs["Base Color"].default_value = (0.015, 0.015, 0.017, 1)
        bsdf.inputs["Roughness"].default_value = 0.85 if role == "foam" else 0.6
    elif role == "pads":
        bsdf.inputs["Base Color"].default_value = (0.9, 0.9, 0.9, 1)
        bsdf.inputs["Transmission Weight"].default_value = 0.9
        bsdf.inputs["Roughness"].default_value = 0.1
    elif role == "lens":
        lens_material(m, bsdf, d)
    return m


def lens_material(m, bsdf, d):
    nt = m.node_tree
    tint = d["lens"]
    bsdf.inputs["Base Color"].default_value = (*tint, 1)
    bsdf.inputs["Roughness"].default_value = 0.02
    bsdf.inputs["IOR"].default_value = 1.5
    alpha = 0.12 if d.get("clear") else 0.82
    bsdf.inputs["Alpha"].default_value = alpha
    if d.get("mirror"):
        bsdf.inputs["Metallic"].default_value = 0.85
        bsdf.inputs["Alpha"].default_value = 0.9
    if d.get("print") and PRINT_PNG:
        # The print: where the tile is white, a polished silver coating; elsewhere the tinted lens.
        img = bpy.data.images.load(PRINT_PNG)
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        tex.interpolation = "Cubic"
        uvn = nt.nodes.new("ShaderNodeTexCoord")
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (PRINT_REPEAT, PRINT_REPEAT, 1)
        nt.links.new(uvn.outputs["UV"], mp.inputs["Vector"])
        nt.links.new(mp.outputs["Vector"], tex.inputs["Vector"])
        mix_c = nt.nodes.new("ShaderNodeMix")
        mix_c.data_type = "RGBA"
        mix_c.inputs[6].default_value = (*tint, 1)
        mix_c.inputs[7].default_value = (0.92, 0.92, 0.95, 1)
        nt.links.new(tex.outputs["Alpha"], mix_c.inputs["Factor"])
        nt.links.new(mix_c.outputs[2], bsdf.inputs["Base Color"])
        nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Metallic"])
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["To Min"].default_value = alpha
        mr.inputs["To Max"].default_value = 1.0
        nt.links.new(tex.outputs["Alpha"], mr.inputs["Value"])
        nt.links.new(mr.outputs["Result"], bsdf.inputs["Alpha"])
    try:
        m.surface_render_method = "BLENDED"
    except (AttributeError, TypeError):
        pass


# ----------------------------------------------------------------------------- export + render

def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def export(fid, out):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, f"{fid}.glb"), export_format="GLB", use_selection=True,
                              export_apply=True, export_yup=True, export_materials="EXPORT")
    usd = os.path.join(out, f"{fid}.usdz")
    kw = dict(filepath=usd, selected_objects_only=True, export_materials=True)
    props = bpy.ops.wm.usd_export.get_rna_type().properties.keys()
    if "convert_orientation" in props:
        kw.update(convert_orientation=True, export_global_forward_selection="NEGATIVE_Z", export_global_up_selection="Y")
    bpy.ops.wm.usd_export(**kw)


def render(fid, out):
    sc = bpy.context.scene
    try:
        sc.render.engine = "CYCLES"
    except TypeError:
        pass
    prefs = bpy.context.preferences.addons.get("cycles")
    if prefs:
        cp = prefs.preferences
        for dev in ("METAL", "OPTIX", "CUDA"):
            try:
                cp.compute_device_type = dev
                cp.get_devices()
                for dv in cp.devices:
                    dv.use = True
                sc.cycles.device = "GPU"
                break
            except TypeError:
                continue
    sc.cycles.samples = 128
    sc.cycles.use_denoising = True
    sc.render.film_transparent = True
    sc.render.resolution_x, sc.render.resolution_y = 1200, 760
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"

    world = bpy.data.worlds.new("studio")
    sc.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    exr = os.path.join(os.path.dirname(bpy.app.binary_path), "..", "Resources",
                       f"{bpy.app.version[0]}.{bpy.app.version[1]}", "datafiles", "studiolights", "world", "studio.exr")
    if os.path.exists(exr):
        env = world.node_tree.nodes.new("ShaderNodeTexEnvironment")
        env.image = bpy.data.images.load(exr)
        world.node_tree.links.new(env.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 1.1

    def area(name, loc, power, size):
        ld = bpy.data.lights.new(name, "AREA")
        ld.energy = power
        ld.size = size
        lo = bpy.data.objects.new(name, ld)
        sc.collection.objects.link(lo)
        lo.location = loc
        d = Vector((0, 0, 0)) - Vector(loc)
        lo.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

    area("key", (-0.35, -0.45, 0.35), 9, 0.35)
    area("rim", (0.45, 0.35, 0.3), 12, 0.3)
    area("fill", (0.4, -0.5, -0.1), 2, 0.5)

    cam_d = bpy.data.cameras.new("cam")
    cam_d.lens = 85
    cam_d.dof.use_dof = True
    cam_d.dof.aperture_fstop = 11
    cam = bpy.data.objects.new("cam", cam_d)
    sc.collection.objects.link(cam)
    # Frame the model's bounds from the front three-quarter view.
    lo = Vector((1e9, 1e9, 1e9)); hi = -lo
    for ob in sc.objects:
        if ob.type == "MESH":
            for c in ob.bound_box:
                w = ob.matrix_world @ Vector(c)
                lo = Vector(map(min, lo, w)); hi = Vector(map(max, hi, w))
    target = (lo + hi) / 2
    radius = (hi - lo).length / 2
    view = Vector((-0.55, -0.78, 0.2)).normalized()
    dist = radius / math.tan(cam_d.angle / 2) * 1.12
    cam.location = target + view * dist
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam_d.dof.focus_distance = dist
    sc.camera = cam
    png = os.path.join(out, f"{fid}.png")
    sc.render.filepath = png
    bpy.ops.render.render(write_still=True)


def main():
    global PRINT_PNG
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = argv[argv.index("--out") + 1] if "--out" in argv else "/tmp/nu-eyes"
    if "--print" in argv:
        PRINT_PNG = os.path.abspath(argv[argv.index("--print") + 1])
    only = argv[argv.index("--only") + 1].split(",") if "--only" in argv else list(FRAMES)
    os.makedirs(out, exist_ok=True)
    metas = []
    for fid in only:
        clear()
        _, meta = build(fid)
        metas.append(meta)
        export(fid, out)
        if "--render" in argv:
            render(fid, out)
    with open(os.path.join(out, "frames.json"), "w") as f:
        json.dump(metas, f, indent=2, ensure_ascii=False)
    print("nu.eyes frames →", out)


if __name__ == "__main__":
    main()
