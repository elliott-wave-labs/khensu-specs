# SPDX-License-Identifier: CC-BY-4.0
"""Photoreal iPhone 18 Pro stand-in, khensu.nu wallpapers and an Apple-style studio rig, for Blender.

The phone is modelled here from measurements (no Apple mesh, texture or logo): an aluminium unibody with
rounded sides, a full-width camera plateau, three lens modules, flash, LiDAR and microphone, the side
buttons and Camera Control, USB-C with its speaker and microphone holes, antenna bands, a colour-matched
frosted glass back and the front glass with its display and Dynamic Island. Coordinates follow sunu.py:
millimetres, the back at z = 0 facing +Z, +Y the top, +X the Action-button side.

Used from render_layers.py and from khensu-site/tools/shield/{glb,render}.py:

    sys.path.insert(0, "<khensu-specs>/hardware/sunu"); import photoreal as P
    phone = P.build_phone("burgundy")          # root empty, millimetres
    P.studio(scene, unit=1.0)                  # lights for a millimetre scene (unit=0.001 for metres)

Run on its own it renders the wallpapers (one per colour) to out/iphone-18-pro/wallpaper/:

    /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P photoreal.py -- wallpaper
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
WALLPAPERS = HERE / "out/iphone-18-pro/wallpaper"

# iPhone 18 Pro, measured from Apple's AR model on apple.com (11 Oct 2026).
W, H, D = 71.78, 149.96, 8.62
R = 12.5  # continuous-curvature corner
PLATEAU_Z, PLATEAU_TO = 2.78, 43.1  # height above the back; from the top edge down
LENS_TOP, GLASS_TOP = 4.68, 4.9
LENS_OD = 16.57
MID = -D / 2  # mid-thickness, where the buttons and ports are centred


def Y(ztop: float) -> float:
    """Distance from the top edge to back-frame y."""
    return H / 2 - ztop


LENSES = [("wide", -21.54, 14.36), ("telephoto", -3.44, 23.98), ("ultra wide", -21.54, 33.6)]
FLASH, MIC, LIDAR = (22.08, 13.82, 6.73), (22.08, 23.98, 0.75), (22.08, 34.15, 6.69)
# (side, top of the button from the top edge, length, protrusion)
BUTTONS = [("+x", 30.81, 6.92, 0.46), ("+x", 42.81, 11.21, 0.46), ("+x", 57.0, 11.22, 0.46), ("-x", 46.66, 17.71, 0.46)]
CAMERA_CONTROL = ("-x", 89.81, 17.12)
GLASS_WINDOW = (64.18, 48.76, 146.16)  # width, top and bottom from the top edge
DISPLAY = (66.5, 144.68)
ISLAND = (15.67, 6.07, 8.0)  # width, height, centre from the top edge
ANTENNA_Y = (Y(19.5), Y(131.0))  # side antenna bands
TOP_WINDOW = (27.24, 4.5)

# Linear colours. alu: anodised aluminium; glass: frosted Ceramic Shield back; glow: the wallpaper light.
COLOURS = {
    "burgundy": dict(alu=(0.084, 0.045, 0.049), alu_r=0.30, glass=(0.056, 0.018, 0.021), glass_r=0.5,
                     glow=(1.0, 0.5, 0.56), deep=(0.16, 0.03, 0.045)),
    "black": dict(alu=(0.028, 0.028, 0.031), alu_r=0.30, glass=(0.012, 0.012, 0.014), glass_r=0.5,
                  glow=(0.62, 0.66, 0.75), deep=(0.035, 0.037, 0.045)),
    "silver": dict(alu=(0.60, 0.60, 0.61), alu_r=0.27, glass=(0.62, 0.62, 0.63), glass_r=0.5,
                   glow=(0.95, 0.93, 0.9), deep=(0.09, 0.09, 0.095)),
    "glacier": dict(alu=(0.44, 0.54, 0.62), alu_r=0.28, glass=(0.46, 0.56, 0.64), glass_r=0.5,
                    glow=(0.5, 0.78, 1.0), deep=(0.03, 0.06, 0.1)),
}

# ---------------------------------------------------------------- outlines and lofts


def rect_outline(x0, x1, y0, y1, corners, seg=24, breaks=(), step=4.0):
    """Counter-clockwise outline of a rectangle with superellipse corners (continuous curvature).
    corners: {"tr"|"tl"|"bl"|"br": (extent, exponent)}. Straight edges are split at `breaks`
    (x values on the top and bottom edges, y values on the sides) and at least every `step` mm."""
    pts = []

    def corner(X, Y_, dx, dy, e, n, forward):
        cx, cy = X - dx * e, Y_ - dy * e
        ts = [math.pi / 2 * k / seg for k in range(seg + 1)]
        if not forward:
            ts.reverse()
        return [(cx + dx * e * math.cos(t) ** (2 / n), cy + dy * e * math.sin(t) ** (2 / n)) for t in ts]

    def edge(a, b, axis):
        # Points strictly between a and b, along x (axis 0) or y (axis 1), at every break and every step.
        lo, hi = sorted((a[axis], b[axis]))
        vals = {v for v in breaks if lo + 0.05 < v < hi - 0.05}
        n = max(1, math.ceil((hi - lo) / step))
        vals |= {lo + (hi - lo) * k / n for k in range(1, n)}
        vals = sorted(vals, reverse=b[axis] < a[axis])
        out = []
        for v in vals:
            p = list(a)
            p[axis] = v
            out.append(tuple(p))
        return out

    tr = corner(x1, y1, 1, 1, *corners["tr"], True)
    tl = corner(x0, y1, -1, 1, *corners["tl"], False)
    bl = corner(x0, y0, -1, -1, *corners["bl"], True)
    br = corner(x1, y0, 1, -1, *corners["br"], False)
    for c, nxt, axis in ((tr, tl, 0), (tl, bl, 1), (bl, br, 0), (br, tr, 1)):
        pts += c + edge(c[-1], nxt[0], axis)
    # Drop duplicates where a corner meets a straight edge of zero length.
    clean = []
    for p in pts:
        if not clean or (abs(p[0] - clean[-1][0]) + abs(p[1] - clean[-1][1])) > 1e-4:
            clean.append(p)
    if abs(clean[0][0] - clean[-1][0]) + abs(clean[0][1] - clean[-1][1]) < 1e-4:
        clean.pop()
    return clean


def normals2d(pts):
    out = []
    n = len(pts)
    for i in range(n):
        ax, ay = pts[i - 1]
        bx, by = pts[(i + 1) % n]
        tx, ty = bx - ax, by - ay
        L = math.hypot(tx, ty) or 1
        out.append((ty / L, -tx / L))
    return out


def phone_outline(seg=24, inset=0.0, breaks=(), step=4.0):
    e = 1.5 * R
    c = {k: (e, 3.2) for k in ("tr", "tl", "bl", "br")}
    pts = rect_outline(-W / 2, W / 2, -H / 2, H / 2, c, seg, breaks, step)
    if inset:
        pts = [(x - nx * inset, y - ny * inset) for (x, y), (nx, ny) in zip(pts, normals2d(pts))]
    return pts


def loft(bm, pts, profile, cap0=True, cap1=True, frame=None):
    """Rings of `pts` offset inward by each profile (inset, z); quads between rings, n-gon caps.
    `frame` maps (x, y, z) to world coordinates. Returns (rings, side faces per ring gap, caps)."""
    nrm = normals2d(pts)
    frame = frame or (lambda x, y, z: (x, y, z))
    rings = [[bm.verts.new(frame(x - nx * i, y - ny * i, z)) for (x, y), (nx, ny) in zip(pts, nrm)] for i, z in profile]
    n = len(pts)
    bands = []
    for a, b in zip(rings, rings[1:]):
        bands.append([bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k])) for k in range(n)])
    caps = []
    if cap0:
        caps.append(bm.faces.new(list(reversed(rings[0]))))
    if cap1:
        caps.append(bm.faces.new(rings[-1]))
    return rings, bands, caps


def obj_from_bm(name, bm, mats, smooth_angle=30, parent=None):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    for p in me.polygons:
        p.use_smooth = True
    me.set_sharp_from_angle(angle=math.radians(smooth_angle))
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    if parent:
        ob.parent = parent
    return ob


def lathe(bm, profile, cx, cy, z0=0.0, n=96, mat=0):
    """Closed solid of revolution from an (r, z) loop; r = 0 points collapse to the axis."""
    rings = []
    for r, z in profile:
        if r < 1e-6:
            rings.append([bm.verts.new((cx, cy, z0 + z))])
        else:
            rings.append([bm.verts.new((cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n), z0 + z))
                          for i in range(n)])
    faces = []
    for a, b in zip(rings, rings[1:] + rings[:1]):
        if len(a) == 1 and len(b) == 1:
            continue
        for i in range(n):
            if len(a) == 1:
                f = bm.faces.new((a[0], b[i], b[(i + 1) % n]))
            elif len(b) == 1:
                f = bm.faces.new((a[i], a[(i + 1) % n], b[0]))
            else:
                f = bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
            f.material_index = mat
            faces.append(f)
    return faces


def arc(cr, cz, rad, a0, a1, steps=6):
    return [(cr + rad * math.cos(math.radians(a0 + (a1 - a0) * k / steps)),
             cz + rad * math.sin(math.radians(a0 + (a1 - a0) * k / steps))) for k in range(steps + 1)]


# ---------------------------------------------------------------- materials


def material(name, colour=(0.5, 0.5, 0.5), metallic=0.0, roughness=0.5, **extra):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*colour[:3], 1)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    for k, v in extra.items():
        if k == "Alpha" and v < 1:
            try:
                m.surface_render_method = "BLENDED"
            except AttributeError:
                pass
        try:
            bsdf.inputs[k].default_value = v
        except KeyError:
            print("no input", k)
    return m


def thin_glass(name, ior=1.5, tint=(1, 1, 1)):
    """A thin cover glass for Cycles: Fresnel-weighted mirror over a transparent pass-through, so light
    and shadow rays reach what is behind it (a refractive slab would leave the lens interior unlit).
    The faint tint is the anti-reflective coating's colour in the reflection."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    fres, mix = nt.nodes.new("ShaderNodeFresnel"), nt.nodes.new("ShaderNodeMixShader")
    tr, gl = nt.nodes.new("ShaderNodeBsdfTransparent"), nt.nodes.new("ShaderNodeBsdfGlossy")
    fres.inputs["IOR"].default_value = ior
    gl.inputs["Roughness"].default_value = 0.0
    gl.inputs["Color"].default_value = (*tint, 1)
    nt.links.new(fres.outputs["Fac"], mix.inputs["Fac"])
    nt.links.new(tr.outputs["BSDF"], mix.inputs[1])
    nt.links.new(gl.outputs["BSDF"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    return m


def bsdf_of(m):
    return next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def phone_materials(colour: str, web: bool = False) -> dict:
    """Materials named so the site's viewer can find them: "iPhone" is the aluminium."""
    c = COLOURS[colour]
    alu = c["alu"]
    m = {
        "alu": material("iPhone", alu, 1.0, c["alu_r"]),
        "ring": material("iPhone lens ring", tuple(v * 0.8 for v in alu), 1.0, 0.16),
        "glass": material("iPhone back glass", c["glass"], 0.0, c["glass_r"], **{"Coat Weight": 0.2, "Coat Roughness": 0.35}),
        "antenna": material("iPhone antenna band", tuple(v * 0.55 for v in alu), 0.0, 0.42),
        "port": material("iPhone port", (0.012, 0.012, 0.013), 0.0, 0.45),
        "steel": material("iPhone port shell", (0.42, 0.42, 0.43), 1.0, 0.28),
        "hole": material("iPhone hole", (0.002, 0.002, 0.002), 0.0, 0.9),
        "black": material("iPhone black", (0.006, 0.006, 0.007), 0.0, 0.32),
        "bezel": material("iPhone lens bezel", (0.03, 0.03, 0.032), 0.7, 0.3),
        "contacts": material("iPhone contacts", (0.9, 0.62, 0.3), 1.0, 0.2),
        "flash": material("iPhone flash", (0.78, 0.75, 0.66), 0.0, 0.32, **{"Coat Weight": 1.0, "Coat Roughness": 0.04}),
        "lidar": material("iPhone lidar", (0.006, 0.005, 0.009), 0.0, 0.05, **{"Coat Weight": 1.0, "Coat Roughness": 0.02}),
        "control": material("iPhone camera control", (0.01, 0.01, 0.012), 0.0, 0.06, **{"Coat Weight": 1.0, "Coat Roughness": 0.02}),
    }
    if web:
        m["sapphire"] = material("iPhone lens glass", (0.02, 0.02, 0.025), 0.0, 0.02, Alpha=0.18)
        m["element"] = material("iPhone lens element", (0.03, 0.02, 0.06), 0.6, 0.12)
        m["iris"] = material("iPhone iris", (0.05, 0.05, 0.055), 0.8, 0.35)
    else:
        m["sapphire"] = thin_glass("iPhone lens glass", 1.77, (0.28, 0.3, 0.45))
        m["element"] = material("iPhone lens element", (0.004, 0.004, 0.006), 0.0, 0.02, **{
            "IOR": 2.0, "Thin Film Thickness": 520.0, "Thin Film IOR": 1.38})
        m["iris"] = material("iPhone iris", (0.03, 0.03, 0.033), 0.9, 0.3)
        m["glint"] = material("iPhone lens glint", (0.01, 0.01, 0.015), 0.0, 0.0, **{
            "IOR": 2.2, "Thin Film Thickness": 380.0, "Thin Film IOR": 1.5})
        # The flash's Fresnel rings.
        nt = m["flash"].node_tree
        tc, wave, bump = nt.nodes.new("ShaderNodeTexCoord"), nt.nodes.new("ShaderNodeTexWave"), nt.nodes.new("ShaderNodeBump")
        wave.wave_type, wave.rings_direction = "RINGS", "SPHERICAL"
        wave.inputs["Scale"].default_value = 9.0
        bump.inputs["Strength"].default_value = 0.25
        nt.links.new(tc.outputs["Object"], wave.inputs["Vector"])
        nt.links.new(wave.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf_of(m["flash"]).inputs["Normal"])
    if "glint" not in m:
        m["glint"] = m["element"]
    m["screen"] = screen_material(colour, web)
    return m


def recolour(colour: str, web: bool = False):
    """Retint an existing phone's materials in place and swap its wallpaper."""
    c = COLOURS[colour]
    alu = c["alu"]
    for name, col, rough in (("iPhone", alu, c["alu_r"]), ("iPhone lens ring", tuple(v * 0.8 for v in alu), None),
                             ("iPhone back glass", c["glass"], c["glass_r"]),
                             ("iPhone antenna band", tuple(v * 0.55 for v in alu), None)):
        b = bsdf_of(bpy.data.materials[name])
        b.inputs["Base Color"].default_value = (*col, 1)
        if rough is not None:
            b.inputs["Roughness"].default_value = rough
    scr = bpy.data.materials["iPhone screen"]
    nt = scr.node_tree
    tex = next(n for n in nt.nodes if n.type == "TEX_IMAGE")
    tex.image = bpy.data.images.load(str(wallpaper_path(colour, web)), check_existing=True)
    nt.links.new(tex.outputs["Color"], bsdf_of(scr).inputs["Emission Color"])


def wallpaper_path(colour: str, web: bool = False) -> Path:
    return WALLPAPERS / (f"{colour}.jpg" if web else f"{colour}.png")


def screen_material(colour: str, web: bool, strength: float = 1.5):
    """Front glass: glossy black, with the wallpaper (display, black border and island baked in) as emission."""
    m = material("iPhone screen", (0.0, 0.0, 0.0), 0.0, 0.03, **{"Specular IOR Level": 0.35})
    nt = m.node_tree
    b = bsdf_of(m)
    tex = next((n for n in nt.nodes if n.type == "TEX_IMAGE"), None) or nt.nodes.new("ShaderNodeTexImage")
    path = wallpaper_path(colour, web)
    if path.exists():
        tex.image = bpy.data.images.load(str(path), check_existing=True)
        nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = strength
    return m


# ---------------------------------------------------------------- the phone


def _frame_side(sign):
    """Local (u along y, v along z, w outward) to world for a button on the +x or -x side."""
    def f(u, v, w):
        return (sign * (W / 2 + w), u, v)
    return f


def build_phone(colour: str = "burgundy", web: bool = False, name: str = "iPhone 18 Pro"):
    """Build the phone; returns its root empty (millimetres, back at z = 0)."""
    seg = 14 if web else 28
    lseg = 48 if web else 128
    M = phone_materials(colour, web)
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)

    # Unibody: rounded sides, front glass seated on top, a flat back with the glass window inset.
    top_x = TOP_WINDOW[0] / 2
    brk = [ANTENNA_Y[0] - 0.3, ANTENNA_Y[0] + 0.3, ANTENNA_Y[1] - 0.3, ANTENNA_Y[1] + 0.3, -top_x, top_x]
    pts = phone_outline(seg, breaks=brk, step=3.0 if not web else 6.0)
    zt = TOP_WINDOW[1] / 2
    side = [(0.55, -7.92), (0.33, -7.84), (0.16, -7.68), (0.06, -7.45), (0.012, -7.1), (0.0, -6.6),
            (0.0, MID - zt), (0.0, MID + zt), (0.0, -1.7), (0.02, -1.25), (0.09, -0.85), (0.24, -0.5),
            (0.48, -0.24), (0.8, -0.08), (1.15, -0.01), (1.3, 0.0)]
    if web:
        side = [side[i] for i in (0, 2, 4, 5, 6, 7, 8, 9, 11, 13, 15)]
    bm = bmesh.new()
    rings, bands, _ = loft(bm, pts, side, cap0=True, cap1=False)
    zi = {z: k for k, (_, z) in enumerate(side)}
    for k, band in enumerate(bands):
        zlo, zhi = side[k][1], side[k + 1][1]
        for f in band:
            c = f.calc_center_median()
            if abs(c.x) > W / 2 - 4 and any(abs(c.y - y) < 0.3 for y in ANTENNA_Y) and zhi < -0.3:
                f.material_index = 3
            elif c.y > H / 2 - 1 and abs(c.x) < top_x and zlo >= MID - zt - 1e-6 and zhi <= MID + zt + 1e-6:
                f.material_index = 3
    # Back face: the ring of aluminium round the glass window, then the window, recessed 0.03 mm.
    gw, gt, gb = GLASS_WINDOW
    rw = R - (W - gw) / 2
    win = rect_outline(-gw / 2, gw / 2, Y(gb), Y(gt), {k: (1.5 * rw, 3.2) for k in ("tr", "tl", "bl", "br")}, seg,
                       step=3.0 if not web else 6.0)
    wv = [bm.verts.new((x, y, 0.0)) for x, y in win]
    edges = [bm.edges.new((wv[i], wv[(i + 1) % len(wv)])) for i in range(len(wv))]
    back = rings[-1]
    edges += [bm.edges.get((back[i], back[(i + 1) % len(back)])) for i in range(len(back))]
    bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=edges, normal=(0, 0, 1))
    floor = [bm.verts.new((x, y, -0.03)) for x, y in win]
    n = len(win)
    for i in range(n):
        bm.faces.new((wv[i], floor[i], floor[(i + 1) % n], wv[(i + 1) % n]))
    bm.faces.new(floor).material_index = 1
    body = obj_from_bm("iPhone body", bm, [M["alu"], M["glass"], M["port"], M["antenna"]], parent=root)
    _cut_ports(body, M, web)

    # Camera plateau: full width, from the top down 43.1 mm, top corners following the phone's.
    pb = Y(PLATEAU_TO)
    e = 1.5 * R
    pc = {"tr": (e, 3.2), "tl": (e, 3.2), "bl": (1.6, 2.0), "br": (1.6, 2.0)}
    ppts = rect_outline(-W / 2, W / 2, pb, H / 2, pc, seg, step=3.0 if not web else 6.0)
    prof = [(0.012, -2.0), (0.0, -1.2), (0.0, PLATEAU_Z - 0.55), (0.04, PLATEAU_Z - 0.3), (0.16, PLATEAU_Z - 0.12),
            (0.36, PLATEAU_Z - 0.03), (0.5, PLATEAU_Z)]
    if web:
        prof = [prof[i] for i in (0, 1, 2, 4, 6)]
    bm = bmesh.new()
    loft(bm, ppts, prof)
    obj_from_bm("iPhone plateau", bm, [M["alu"]], parent=root)

    # Front glass: a rounded edge proud of the aluminium; the top face carries the display.
    gpts = phone_outline(seg, step=6.0)
    gprof = [(0.62, -7.86), (0.34, -7.93), (0.24, -8.1), (0.27, -8.3), (0.42, -8.48), (0.68, -8.58), (1.0, -8.62)]
    if web:
        gprof = [gprof[i] for i in (0, 2, 4, 6)]
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    loft(bm, gpts, gprof)
    for f in bm.faces:
        for lp in f.loops:
            lp[uv].uv = ((lp.vert.co.x + W / 2) / W, (lp.vert.co.y + H / 2) / H)
    obj_from_bm("iPhone screen", bm, [M["screen"]], parent=root)

    # Lens modules: colour-matched ring, black stepped bezel, sapphire cover, coated elements; an iris on the main camera.
    bm = bmesh.new()
    ro = LENS_OD / 2
    h = LENS_TOP - PLATEAU_Z
    gt_ = GLASS_TOP - PLATEAU_Z
    for lname, x, zt_ in LENSES:
        y = Y(zt_)
        ring = [(ro - 0.25, -0.2), (ro, 0.05), (ro, h - 0.4), *arc(ro - 0.4, h - 0.4, 0.4, 0, 90, 5)[1:],
                (7.35, h), (7.12, h - 0.18), (7.1, 0.0)]
        lathe(bm, ring, x, y, PLATEAU_Z, lseg, 0)
        steps = [(7.1, h - 0.18), (6.95, h - 0.18), (6.95, h - 0.32), (6.78, h - 0.32), (6.78, h - 0.44), (6.62, h - 0.44),
                 (6.62, h - 0.62), (6.3, h - 0.66), (5.0, 0.05), (7.1, 0.05)]
        lathe(bm, steps, x, y, PLATEAU_Z, lseg, 1)
        # Inside: a black floor, the iris or a stop, the front element dome and a small glint deep inside.
        lathe(bm, [(0.0, 0.04), (5.2, 0.04), (5.2, 0.08), (0.0, 0.08)], x, y, PLATEAU_Z, lseg, 1)
        dome = [(3.6 * math.sin(math.radians(a)), 0.2 + 0.3 * math.cos(math.radians(a)) ** 1.4) for a in range(0, 91, 10)]
        lathe(bm, [*dome, (3.6, 0.1), (0.0, 0.1)], x, y, PLATEAU_Z, lseg, 4)
        lathe(bm, [(0.0, 0.5), (0.9, 0.5), (0.0, 0.62)], x, y, PLATEAU_Z, lseg // 2, 5)
        if lname == "wide" and not web:
            _iris(bm, x, y, PLATEAU_Z + 0.82, 5.0, 2.5, 6)
        else:
            lathe(bm, [(2.6, 0.82), (5.0, 0.82), (5.0, 0.86), (2.6, 0.86)], x, y, PLATEAU_Z, lseg, 6)
        # Sapphire cover: slightly domed, its top 0.22 mm above the ring.
        cover = [(0.0, gt_), *[(6.6 * k / 6, gt_ - 0.2 * (k / 6) ** 2) for k in range(1, 7)], (6.6, h - 0.95), (0.0, h - 0.95)]
        lathe(bm, cover, x, y, PLATEAU_Z, lseg, 2)
    # Flash (milky diffuser in a thin bezel), LiDAR (dark glass), microphone, all flush with the plateau.
    z0 = PLATEAU_Z
    fx, fz, fd = FLASH
    lathe(bm, [(0.0, 0.0), (fd / 2, 0.0), (fd / 2, 0.035), (fd / 2 - 0.25, 0.04), (0.0, 0.04)], fx, Y(fz), z0, lseg, 1)
    lathe(bm, [(0.0, 0.03), (fd / 2 - 0.3, 0.03), (fd / 2 - 0.3, 0.05), (0.0, 0.055)], fx, Y(fz), z0, lseg, 7)
    lx, lz, ld = LIDAR
    lathe(bm, [(0.0, 0.0), (ld / 2, 0.0), (ld / 2, 0.035), (ld / 2 - 0.2, 0.04), (0.0, 0.04)], lx, Y(lz), z0, lseg, 1)
    lathe(bm, [(0.0, 0.03), (ld / 2 - 0.25, 0.03), (ld / 2 - 0.25, 0.05), (0.0, 0.06)], lx, Y(lz), z0, lseg, 8)
    mx, mz, md = MIC
    lathe(bm, [(0.0, 0.0), (md / 2, 0.0), (md / 2, 0.03), (0.0, 0.03)], mx, Y(mz), z0, 24, 9)
    obj_from_bm("iPhone camera", bm, [M["ring"], M["bezel"], M["sapphire"], M["black"], M["element"], M["glint"],
                                      M["iris"], M["flash"], M["lidar"], M["hole"]], smooth_angle=40, parent=root)

    # Side buttons (anodised to match) and Camera Control (sapphire crystal, nearly flush, in a thin aluminium rim).
    bm = bmesh.new()
    for sd, ztop, length, out in BUTTONS:
        _button(bm, sd, Y(ztop + length / 2), length, 2.66, out, 0, seg)
    sd, ztop, length = CAMERA_CONTROL
    _button(bm, sd, Y(ztop + length / 2), length + 0.5, 2.2, 0.06, 0, seg)
    _button(bm, sd, Y(ztop + length / 2), length, 1.9, 0.1, 1, seg)
    obj_from_bm("iPhone buttons", bm, [M["alu"], M["control"]], smooth_angle=35, parent=root)

    _port_interior(root, M, web)
    return root


def _button(bm, sd, yc, length, height, out, mat, seg):
    sign = 1 if sd == "+x" else -1
    r = height / 2 - 0.02
    c = {k: (r, 2.0) for k in ("tr", "tl", "bl", "br")}
    pts = rect_outline(yc - length / 2, yc + length / 2, MID - height / 2, MID + height / 2, c, max(6, seg // 3), step=50)
    prof = [(0.0, -0.8), (0.0, out - 0.18), (0.06, out - 0.05), (0.18, out)]
    if sign < 0:
        pts = list(reversed(pts))
    frame = lambda u, v, w: (sign * (W / 2 + w), u, v)
    _, bands, caps = loft(bm, pts, prof, frame=frame)
    for f in [f for b in bands for f in b] + caps:
        f.material_index = mat


def _iris(bm, x, y, z, r_out, r_in, blades):
    """Variable-aperture iris: `blades` thin plates whose inner edges form a polygon, each a hair higher."""
    for i in range(blades):
        a0 = 2 * math.pi * i / blades
        a1 = 2 * math.pi * (i + 1) / blades
        p0 = Vector((math.cos(a0) * r_in, math.sin(a0) * r_in))
        p1 = Vector((math.cos(a1) * r_in, math.sin(a1) * r_in))
        d = (p1 - p0).normalized()
        # Extend the inner edge past p1 to the outer circle.
        b = p1.dot(d)
        t = -b + math.sqrt(max(b * b - (p1.length_squared - r_out ** 2), 0))
        e1 = p1 + d * t
        ang0 = math.atan2(p0.y, p0.x)
        e0 = p0 + (p0 - p1).normalized() * 0  # the blade starts at p0
        a_e1 = math.atan2(e1.y, e1.x)
        a_o0 = ang0 - 0.5  # the previous blade covers the rest
        while a_e1 < a_o0:
            a_e1 += 2 * math.pi
        outer = [Vector((math.cos(a) * r_out, math.sin(a) * r_out)) for a in
                 [a_e1 - (a_e1 - a_o0) * k / 8 for k in range(9)]]
        poly = [p0, p1, e1] + outer[1:]
        zz = z + 0.012 * i
        top = [bm.verts.new((x + p.x, y + p.y, zz + 0.02)) for p in poly]
        bot = [bm.verts.new((x + p.x, y + p.y, zz)) for p in poly]
        try:
            bm.faces.new(top).material_index = 6
            bm.faces.new(list(reversed(bot))).material_index = 6
            m = len(poly)
            for k in range(m):
                bm.faces.new((bot[k], bot[(k + 1) % m], top[(k + 1) % m], top[k])).material_index = 6
        except ValueError:
            pass


def _stadium(w, h, n=12):
    """Stadium (slot) outline in the plane: width w, height h."""
    r = h / 2
    pts = []
    for k in range(n + 1):
        a = -math.pi / 2 + math.pi * k / n
        pts.append((w / 2 - r + r * math.cos(a), r * math.sin(a)))
    for k in range(n + 1):
        a = math.pi / 2 + math.pi * k / n
        pts.append((-w / 2 + r + r * math.cos(a), r * math.sin(a)))
    return pts


def _prism(bm, pts2d, y0, y1, zc, mat):
    """Extrude an (x, z) outline along y from y0 to y1."""
    a = [bm.verts.new((x, y0, zc + z)) for x, z in pts2d]
    b = [bm.verts.new((x, y1, zc + z)) for x, z in pts2d]
    n = len(pts2d)
    for k in range(n):
        bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k])).material_index = mat
    bm.faces.new(a).material_index = mat
    bm.faces.new(list(reversed(b))).material_index = mat


def _cut_ports(body, M, web):
    """USB-C opening and the speaker and microphone holes in the bottom edge, as one exact boolean."""
    yb = -H / 2
    bm = bmesh.new()
    _prism(bm, _stadium(9.02, 3.17, 10), yb - 2, yb + 0.55, MID, 0)
    _prism(bm, _stadium(6.68, 2.77, 10), yb - 1, yb + 4.6, MID, 1)
    n = 16 if not web else 10
    for s in (-1, 1):
        for k in range(7):
            x = s * (8.6 + k * 2.12)
            circ = [(x + 0.72 * math.cos(2 * math.pi * i / n), 0.72 * math.sin(2 * math.pi * i / n)) for i in range(n)]
            _prism(bm, circ, yb - 1, yb + 2.2, MID, 2)
    me = bpy.data.meshes.new("cutter")
    bm.to_mesh(me)
    bm.free()
    for m in (M["port"], M["steel"], M["hole"]):
        me.materials.append(m)
    cut = bpy.data.objects.new("cutter", me)
    bpy.context.scene.collection.objects.link(cut)
    mod = body.modifiers.new("ports", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = cut
    mod.solver = "EXACT"
    try:
        mod.material_mode = "TRANSFER"
    except AttributeError:
        pass
    dg = bpy.context.evaluated_depsgraph_get()
    new = bpy.data.meshes.new_from_object(body.evaluated_get(dg))
    old = body.data
    body.modifiers.clear()
    body.data = new
    bpy.data.meshes.remove(old)
    bpy.data.objects.remove(cut)
    for p in new.polygons:
        p.use_smooth = True
    new.set_sharp_from_angle(angle=math.radians(30))


def _port_interior(root, M, web):
    """USB-C: steel shell lining the opening, a dark back wall and the tongue with its contacts."""
    yb = -H / 2
    bm = bmesh.new()
    outer, inner = _stadium(6.66, 2.75, 10), _stadium(6.36, 2.45, 10)
    a = [bm.verts.new((x, yb + 0.56, MID + z)) for x, z in outer]
    b = [bm.verts.new((x, yb + 4.5, MID + z)) for x, z in outer]
    c = [bm.verts.new((x, yb + 4.5, MID + z)) for x, z in inner]
    d = [bm.verts.new((x, yb + 0.56, MID + z)) for x, z in inner]
    n = len(outer)
    for k in range(n):
        k1 = (k + 1) % n
        bm.faces.new((d[k], d[k1], c[k1], c[k])).material_index = 0  # inside of the shell
        bm.faces.new((a[k], d[k], d[k1], a[k1])).material_index = 0  # its front lip
    back = [bm.verts.new((x, yb + 4.45, MID + z)) for x, z in inner]
    bm.faces.new(back).material_index = 1
    # Tongue, set back from the opening.
    _prism(bm, [(-2.89, -0.35), (2.89, -0.35), (2.89, 0.35), (-2.89, 0.35)], yb + 1.3, yb + 4.46, MID, 1)
    if not web:
        for s in (-1, 1):
            for k in range(12):
                x = -2.5 + k * (5.0 / 11)
                _prism(bm, [(x - 0.12, 0), (x + 0.12, 0), (x + 0.12, 0.02), (x - 0.12, 0.02)],
                       yb + 1.6, yb + 2.6, MID + s * 0.35 - (0.02 if s < 0 else 0), 2)
    obj_from_bm("iPhone USB-C", bm, [M["steel"], M["port"], M["contacts"]], smooth_angle=35, parent=root)


# ---------------------------------------------------------------- suñůlink.shield USB-C receptacle


def shield_port(parent, outline_ymin, thickness, suction=0.5, usb_w=9.2, usb_h=3.4, web=False):
    """The shield's own USB-C receptacle behind the opening in its bottom wall: steel shell, tongue, contacts."""
    zc = suction + (thickness - suction) / 2
    # The cavity is black. A steel lining reads as a bright hole from the side the page shows.
    M = {"steel": material("shield port shell", (0.012, 0.012, 0.013), 0.0, 0.55),
         "port": material("shield port", (0.008, 0.008, 0.009), 0.0, 0.6),
         "contacts": material("shield contacts", (0.9, 0.62, 0.3), 1.0, 0.2)}
    y0 = outline_ymin + 0.95
    bm = bmesh.new()
    outer, inner = _stadium(usb_w - 0.5, usb_h - 0.5, 10), _stadium(usb_w - 1.4, usb_h - 1.05, 10)
    n = len(outer)
    a = [bm.verts.new((x, y0, zc + z)) for x, z in outer]
    d = [bm.verts.new((x, y0, zc + z)) for x, z in inner]
    c = [bm.verts.new((x, y0 + 4.2, zc + z)) for x, z in inner]
    for k in range(n):
        k1 = (k + 1) % n
        bm.faces.new((d[k], d[k1], c[k1], c[k])).material_index = 0
        bm.faces.new((a[k], d[k], d[k1], a[k1])).material_index = 0
    bm.faces.new([bm.verts.new((x, y0 + 4.15, zc + z)) for x, z in inner]).material_index = 1
    _prism(bm, [(-2.89, -0.35), (2.89, -0.35), (2.89, 0.35), (-2.89, 0.35)], y0 + 0.8, y0 + 4.16, zc, 1)
    if not web:
        for s in (-1, 1):
            for k in range(12):
                x = -2.5 + k * (5.0 / 11)
                _prism(bm, [(x - 0.12, 0), (x + 0.12, 0), (x + 0.12, 0.02), (x - 0.12, 0.02)],
                       y0 + 1.1, y0 + 2.1, zc + s * 0.35 - (0.02 if s < 0 else 0), 2)
    return obj_from_bm("shield USB-C", bm, [M["steel"], M["port"], M["contacts"]], smooth_angle=35, parent=parent)


# ---------------------------------------------------------------- lighting


def studio(scene, unit=1.0, world_strength=0.18, key=1.0, rim=1.0, fill=1.0, front=1.0, target=(0, 0, 0),
           camera=(0, -1, 0.08), sheen=1.0, side=0.0):
    """Apple-style product lighting on black: a large soft overhead key from slightly behind, a broad soft
    panel above the camera whose reflection lays a gradient over the faces, two long thin vertical strip
    lights behind the subject that draw specular lines down the edges, a low fill, and a dim world with a
    bright band overhead for reflections. The rig is placed relative to `camera`, the direction from the
    subject to the camera. `unit` is scene units per millimetre / 1000 (1.0 for millimetre scenes, 0.001
    for metres)."""
    k = 1000.0 * unit  # scene units per metre
    back = -Vector(camera).normalized()  # from the camera through the subject
    up = Vector((0, 0, 1))
    right = back.cross(up).normalized()
    up = right.cross(back).normalized()

    # A black studio whose only light is a few big soft boxes, painted into the world so their reflections
    # fall off smoothly across the faces (an HDRI of a real product studio, without the room).
    world = bpy.data.worlds.new("studio")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    bg = next(n for n in nt.nodes if n.type == "BACKGROUND")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    total = None
    boxes = [
        (up * 0.92 + back * 0.4, 38, 3.0),  # overhead, slightly behind
        (-back * 0.9 + up * 0.45 + right * 0.2, 45, 0.4 * sheen),  # behind and above the camera: the sheen on faces towards it
        (right * 0.95 - back * 0.15 + up * 0.15, 16, 0.9),  # tall panels either side
        (-right * 0.95 - back * 0.1 + up * 0.1, 16, 0.7),
    ]
    for d, radius, strength in boxes:
        dot = nt.nodes.new("ShaderNodeVectorMath")
        dot.operation = "DOT_PRODUCT"
        nt.links.new(tc.outputs["Generated"], dot.inputs[0])
        dot.inputs[1].default_value = d.normalized()
        c = math.cos(math.radians(radius))
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = c, 1.0
        mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = 0.0, strength
        nt.links.new(dot.outputs["Value"], mr.inputs["Value"])
        sq = nt.nodes.new("ShaderNodeMath")
        sq.operation = "POWER"
        sq.inputs[1].default_value = 0.7
        nt.links.new(mr.outputs["Result"], sq.inputs[0])
        if total is None:
            total = sq
        else:
            add = nt.nodes.new("ShaderNodeMath")
            nt.links.new(total.outputs[0], add.inputs[0])
            nt.links.new(sq.outputs[0], add.inputs[1])
            total = add
    nt.links.new(total.outputs[0], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = world_strength * 5

    def area(name, loc, energy, size, size_y=None, colour=(1, 1, 1)):
        l = bpy.data.lights.new(name, "AREA")
        l.shape = "RECTANGLE" if size_y else "DISK"
        l.size = size * k
        if size_y:
            l.size_y = size_y * k
        l.energy = energy * k * k  # watts at metre scale; irradiance falls with scene distance squared
        l.color = colour
        o = bpy.data.objects.new(name, l)
        scene.collection.objects.link(o)
        r_, f_, u_ = loc
        o.location = (right * r_ + back * f_ + up * u_) * k + Vector(target)
        o.rotation_euler = (Vector(target) - o.location).to_track_quat("-Z", "Y").to_euler()
        return o

    # Positions in metres as (right, behind the subject, up); energies in watts.
    return [
        area("key", (-0.1, 0.25, 0.8), 14.0 * key, 0.9),
        area("front", (0.25, -0.9, 0.6), 1.2 * front, 1.3),
        area("strip L", (-0.55, 0.3, 0.1), 10.0 * rim, 0.03, 1.4, (0.95, 0.97, 1.0)),
        area("strip R", (0.6, 0.2, 0.15), 12.0 * rim, 0.03, 1.4, (1.0, 0.98, 0.96)),
        area("fill", (0.35, -0.7, -0.25), 0.5 * fill, 1.0),
    ] + ([area("side", (-0.75, -0.35, 0.55), 6.0 * side, 0.8)] if side else [])


# ---------------------------------------------------------------- wallpapers


def _ribbon(bm, curve, width, tilt, mat=0, closed=False, taper=0.0):
    """A folded ribbon: a strip of width `width` swept along `curve` (list of (x, y, z)),
    its width direction tilted out of the screen plane by `tilt` radians about the curve tangent.
    A closed curve joins its ends; `taper` narrows an open one to nothing over that fraction at each end."""
    rows = []
    n = len(curve)
    for i, p in enumerate(curve):
        p = Vector(p)
        if closed:
            q = Vector(curve[(i + 1) % n]) - Vector(curve[i - 1])
        else:
            q = Vector(curve[min(i + 1, n - 1)]) - Vector(curve[max(i - 1, 0)])
        f = i / (n - 1)
        wk = width * (min(1.0, min(f, 1 - f) / taper) ** 0.5 if taper else 1.0)
        t = q.normalized()
        nrm = Vector((-t.y, t.x, 0)).normalized()  # in-plane normal, pointing outward for CCW curves
        w = (nrm * math.cos(tilt) + Vector((0, 0, 1)) * math.sin(tilt)).normalized()
        bulge = t.cross(w).normalized() * wk * 0.09  # a soft curl across the width
        rows.append([bm.verts.new(p + w * wk * (k / 12 - 0.5) + bulge * math.sin(math.pi * k / 12)) for k in range(13)])
    for a, b in zip(rows, rows[1:] + (rows[:1] if closed else [])):
        for k in range(12):
            bm.faces.new((a[k], b[k], b[k + 1], a[k + 1])).material_index = mat


def render_wallpaper(colour: str, out: Path, size=(1206, 2622), samples=96):
    """The khensu.nu mark as huge folded ribbons glowing in the phone's colour on near-black, rendered at
    display resolution and placed in a phone-sized frame with the black border and Dynamic Island."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    _cycles(sc, samples)
    sc.render.film_transparent = False
    sc.render.resolution_x, sc.render.resolution_y = size
    c = COLOURS[colour]
    world = bpy.data.worlds.new("w")
    sc.world = world
    world.use_nodes = True
    next(n for n in world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (*c["deep"], 1)
    next(n for n in world.node_tree.nodes if n.type == "BACKGROUND").inputs["Strength"].default_value = 0.04

    glow = c["glow"]
    satin = material("satin", tuple(0.04 + 0.3 * g for g in glow), 0.85, 0.3, **{
        "Coat Weight": 0.25, "Coat Roughness": 0.1})

    # The mark: a ring and the crescent's inner edge. The ring is repeated outward like the folds of a
    # pleated ribbon, each fold wider than the step so it tucks under the one inside it.
    bm = bmesh.new()
    folds = 6
    for k in range(folds):
        r = 47.5 + k * 17.0
        z = -k * 9.0
        pts = [(50 + r * math.cos(2 * math.pi * i / 360), 50 + r * math.sin(2 * math.pi * i / 360), z) for i in range(360)]
        _ribbon(bm, pts, 28.0, math.radians(52), 0, closed=True)
    # The crescent's inner edge: an arc of the circle centred 13.93 units right of the ring's centre,
    # from the ring's top to its bottom through the left.
    a0 = math.atan2(47.5, -13.93)
    span = [a0 + (2 * math.pi - 2 * a0) * i / 240 for i in range(241)]
    pts = [(63.93 + 49.52 * math.cos(a), 50 + 49.52 * math.sin(a), 3.0) for a in span]
    _ribbon(bm, pts, 18.0, math.radians(-58), 0, taper=0.12)
    ob = obj_from_bm("mark", bm, [satin], smooth_angle=80)
    sol = ob.modifiers.new("solid", "SOLIDIFY")
    sol.thickness, sol.offset = 0.9, 0
    bev = ob.modifiers.new("bevel", "BEVEL")
    bev.width, bev.segments = 0.4, 3
    sub = ob.modifiers.new("sub", "SUBSURF")
    sub.levels = sub.render_levels = 1

    # Camera: straight on, the mark large enough that only part of it fits on the narrow screen.
    cam = bpy.data.cameras.new("cam")
    cam.lens = 50
    cam.sensor_fit = "VERTICAL"
    cam.sensor_height = 36
    cam.dof.use_dof = True
    cam.dof.aperture_fstop = 2.2
    co = bpy.data.objects.new("cam", cam)
    sc.collection.objects.link(co)
    co.location = (40.0, 30.0, 330.0)
    co.rotation_euler = (Vector((44.0, 38.0, -10.0)) - co.location).to_track_quat("-Z", "Y").to_euler()
    cam.dof.focus_distance = (co.location - Vector((44, 38, 0))).length
    sc.camera = co

    def light(name, loc, energy, size, size_y=None, col=(1, 1, 1)):
        l = bpy.data.lights.new(name, "AREA")
        l.shape = "RECTANGLE" if size_y else "DISK"
        l.size = size
        if size_y:
            l.size_y = size_y
        l.energy, l.color = energy, col
        o = bpy.data.objects.new(name, l)
        sc.collection.objects.link(o)
        o.location = loc
        o.rotation_euler = (Vector((50, 50, -10)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()

    light("top", (40, 300, 60), 2.0e6, 70, None, glow)
    light("rim L", (-280, 80, 10), 3.0e6, 8, 500, tuple(0.5 + 0.5 * g for g in glow))
    light("rim R", (350, 40, 5), 2.4e6, 8, 500, tuple(0.6 + 0.4 * g for g in glow))
    light("low", (60, -280, 40), 0.6e5, 200, None, glow)

    raw = out.with_suffix(".raw.png")
    sc.render.filepath = str(raw)
    bpy.ops.render.render(write_still=True)
    _frame_wallpaper(raw, out, size)
    raw.unlink()


def _frame_wallpaper(raw: Path, out: Path, size):
    """Place the display render inside a phone-sized frame: black border, rounded display corners,
    the Dynamic Island. The frame spans the whole phone outline so the screen UVs are a planar map."""
    import numpy as np

    img = bpy.data.images.load(str(raw))
    dw, dh = size
    src = np.empty(dw * dh * 4, np.float32)
    img.pixels.foreach_get(src)
    src = src.reshape(dh, dw, 4)  # rows from the bottom
    px_mm = dw / DISPLAY[0]
    fw, fh = round(W * px_mm), round(H * px_mm)
    ox, oy = (fw - dw) // 2, (fh - dh) // 2
    rd = (R - (W - DISPLAY[0]) / 2) * 1.5 * px_mm
    iw, ih = ISLAND[0] * px_mm, ISLAND[1] * px_mm
    icx, icy = dw / 2, dh - (ISLAND[2] - (H - DISPLAY[1]) / 2) * px_mm
    ys, xs = np.mgrid[0:dh, 0:dw].astype(np.float32) + 0.5
    # Continuous-curvature display corners: a superellipse near each corner, antialiased by 4x4 supersampling.
    cover = np.zeros((dh, dw), np.float32)
    for sy in range(4):
        for sx in range(4):
            x = xs - 0.5 + (sx + 0.5) / 4
            y = ys - 0.5 + (sy + 0.5) / 4
            cx = np.minimum(x, dw - x)
            cy = np.minimum(y, dh - y)
            u = np.clip((rd - cx) / rd, 0, None)
            v = np.clip((rd - cy) / rd, 0, None)
            ok = u ** 3.2 + v ** 3.2 <= 1.0
            r = ih / 2
            dx = np.maximum(np.abs(x - icx) - (iw / 2 - r), 0)
            ok &= dx * dx + (y - icy) ** 2 > r * r
            cover += ok
    cover /= 16
    frame = np.zeros((fh, fw, 4), np.float32)
    frame[..., 3] = 1
    frame[oy:oy + dh, ox:ox + dw, :3] = src[..., :3] * cover[..., None]
    fr = bpy.data.images.new("frame", fw, fh, alpha=False)
    fr.pixels.foreach_set(frame.ravel())
    fr.filepath_raw = str(out)
    fr.file_format = "PNG"
    fr.save()
    # A light copy for the web GLBs.
    fr.scale(640, round(640 * fh / fw))
    sc = bpy.context.scene
    sc.view_settings.view_transform = "Standard"  # the pixels are already display-referred
    sc.view_settings.look = "None"
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 86
    fr.save_render(str(out.with_suffix(".jpg")), scene=sc)


def _cycles(sc, samples):
    sc.render.engine = "CYCLES"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        sc.cycles.device = "GPU"
    except Exception as e:
        print("GPU unavailable:", e)
    sc.cycles.samples = samples
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.use_denoising = True
    try:
        sc.view_settings.view_transform = "AgX"
        sc.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass


if __name__ == "__main__" and "--" in sys.argv:
    args = sys.argv[sys.argv.index("--") + 1:]
    if args[:1] == ["wallpaper"]:
        WALLPAPERS.mkdir(parents=True, exist_ok=True)
        size = (1206, 2622) if "--preview" not in args else (402, 874)
        for col in [a for a in args[1:] if a in COLOURS] or list(COLOURS):
            render_wallpaper(col, wallpaper_path(col), size, 96 if "--preview" not in args else 32)
            print("wrote", wallpaper_path(col), flush=True)
