# SPDX-License-Identifier: CC-BY-4.0
"""Path-traced renders of each shell layer from one fixed camera, for exploded-view animation.

Every layer is rendered at its true position into an identically sized transparent PNG, so stacking
the images reproduces the assembly and translating them vertically explodes it (the camera is
orthographic and its up vector has a positive Z component, so a Z offset is a pure screen-space Y offset).

    uv run python render_layers.py <out_dir> [--samples N] [--size PX]

The CAD (shell.py) is exported to STL here, rendered with Blender's Cycles (this same file runs inside
Blender for that step), then the colour variants and assemblies are composited with Pillow.
"""

from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

SIZE = 1600
AZ, EL = math.radians(32), math.radians(36)

# iPhone 18 Pro finishes, as listed on apple.com/shop/buy-iphone/iphone-18-pro (approximate colours).
PHONE_COLOURS = {
    "burgundy": (112, 34, 46),
    "glacier": (196, 212, 223),
    "silver": (212, 213, 216),
    "black": (46, 47, 51),
}
DEFAULT_COLOUR = "burgundy"
# The titanium shell is matte powder coat matched to each phone, a touch deeper than the phone's
# aluminium so the seam reads. Brass is bare C26000 with a satin bead-blast.
SHELL_COLOURS = {c: tuple(int(ch * 0.9) for ch in rgb) for c, rgb in PHONE_COLOURS.items()}
FINISHES = [*PHONE_COLOURS, "brass"]

LAYERS = ["phone", "suction_film", "base", "magnet_ring", "pcb", "battery", "coil", "window_inserts", "housing"]
BLENDER = os.environ.get("BLENDER", "/Applications/Blender.app/Contents/MacOS/Blender")


def camera_basis():
    import numpy as np

    eye = np.array([math.sin(AZ) * math.cos(EL), -math.cos(AZ) * math.cos(EL), math.sin(EL)])
    right = np.cross(-eye, [0, 0, 1.0])
    right /= np.linalg.norm(right)
    up = np.cross(right, -eye)
    return eye, right, up


# ---------------------------------------------------------------- CAD export (uv environment)


def phone_body(p):
    """iPhone 18 Pro, from apple.com: aluminium unibody with a full-width camera plateau, a colour-matched
    Ceramic Shield panel in the lower back, USB-C with speaker and microphone holes on the bottom edge, and
    the Action button and volume buttons on the left side. Returns (aluminium, back glass, dark interiors)."""
    import cadquery as cq

    import shell as S

    half = p.height / 2
    body = (
        cq.Workplane("XY").workplane(offset=-p.depth).rect(p.width, p.height).extrude(p.depth)
        .edges("|Z").fillet(p.corner_r).faces("<Z").edges().fillet(1.6).faces(">Z").edges().fillet(0.4)
    )
    # Back glass: a flush panel below the plateau.
    top, bottom, inset = p.bump_bottom() - 1.4, -half + 2.6, 2.6
    panel = S.rounded_rect(p.width - 2 * inset, top - bottom, p.corner_r - inset, 0, (top + bottom) / 2)
    body = body.cut(S.outline_solid(panel, -0.3, 1.0))
    glass = S.outline_solid(S.offset_outline(panel, -0.04), -0.3, 0.3)

    def bottom_edge(sketch, depth, at=-half - 0.5):
        return sketch.extrude(-depth).translate((0, at, 0))

    zc = -p.depth / 2
    dark = bottom_edge(cq.Workplane("XZ").center(0, zc).slot2D(8.6, 2.9), 6.0, -half + 1.0)
    dark = dark.union(bottom_edge(cq.Workplane("XZ").center(0, zc).rect(6.6, 0.66), 0.75, -half + 0.3))
    body = body.cut(bottom_edge(cq.Workplane("XZ").center(0, zc).slot2D(8.9, 3.2), 1.5))
    for side in (-1, 1):
        for k in range(6):
            x = side * (10.5 + 1.75 * k)
            body = body.cut(bottom_edge(cq.Workplane("XZ").center(x, zc).circle(0.55), 1.7))
            dark = dark.union(bottom_edge(cq.Workplane("XZ").center(x, zc).circle(0.6), 3.0, -half + 0.8))
    # Action button and volume buttons, on the side the camera looks at (+x on the back).
    for from_top, length in ((33.0, 6.5), (47.0, 10.0), (60.0, 10.0)):
        btn = (cq.Workplane("XY").box(1.4, length, 2.3).edges("|X").fillet(1.1)
               .translate((p.width / 2 - 0.25, half - from_top - length / 2, zc)))
        body = body.union(btn)
    plateau = S.outline_solid(S.plateau_outline(p), -1.0, p.bump_z + 1.0).faces(">Z").edges().fillet(0.8)
    return body.union(plateau), glass, dark


def shell_port(s):
    """The shell's own USB-C receptacle behind the opening in its bottom wall."""
    import cadquery as cq

    import shell as S

    ymin = s.outline.val().BoundingBox().ymin
    zc = S.B.suction + (s.thickness - S.B.suction) / 2
    block = cq.Workplane("XZ").center(0, zc).slot2D(8.6, 2.6).extrude(-5.0).translate((0, ymin + 0.9, 0))
    tongue = cq.Workplane("XZ").center(0, zc).rect(6.6, 0.66).extrude(-0.7).translate((0, ymin + 0.35, 0))
    return block.union(tongue)


def ortho_view(eye, corners, width_px, height_px, margin):
    """Orthographic camera framing `corners`: basis, centre, mm across the frame."""
    import numpy as np

    eye = np.array(eye, float)
    eye /= np.linalg.norm(eye)
    right = np.cross(-eye, [0, 0, 1.0])
    right /= np.linalg.norm(right)
    up = np.cross(right, -eye)
    sx, sy = corners @ right, corners @ up
    center = np.array([(sx.min() + sx.max()) / 2, (sy.min() + sy.max()) / 2])
    scale = max((sx.max() - sx.min()) / (width_px * margin), (sy.max() - sy.min()) / (height_px * margin))  # mm per px
    return eye, right, up, center, scale


def export_meshes(work: Path) -> dict:
    import cadquery as cq
    import numpy as np

    import shell as S

    work.mkdir(parents=True, exist_ok=True)
    p = next(ph for ph in S.PHONES if ph.name == "iphone-18-pro")
    s = next(st for st in S.styles_for(p) if st.name == "wrap")
    parts = S.build_shell(p, s)

    def save(w, name):
        cq.exporters.export(w, str(work / f"{name}.stl"), tolerance=0.01, angularTolerance=0.08)

    body, glass, dark = phone_body(p)
    save(body, "phone")
    save(glass, "phone_glass")
    save(dark, "phone_dark")
    save(shell_port(s), "shell_port")
    for name in LAYERS[1:]:
        if name in parts:
            save(parts[name], name)

    # Side view: the long edge from just above the back, camera end to the right.
    yaw, el = math.radians(7), math.radians(10)
    side_corners = np.array([[x, y, z] for x in (-p.width / 2, p.width / 2) for y in (-p.height / 2, p.height / 2)
                             for z in (-p.depth, p.lens_z)])
    se, sr, su, sc_, sscale = ortho_view([math.cos(el) * math.cos(yaw), math.cos(el) * math.sin(yaw), math.sin(el)],
                                         side_corners, 2400, 750, 0.86)

    def side_px(v):
        v = np.array(v, float)
        return [round(float((v @ sr - sc_[0]) / sscale + 1200), 1), round(float(375 - (v @ su - sc_[1]) / sscale), 1)]

    side = {
        "eye": se.tolist(), "right": sr.tolist(), "up": su.tolist(), "center": sc_.tolist(),
        "ortho_scale": 2400 * sscale, "res": [2400, 750], "px_per_mm_z": float(su[2] / sscale),
        "guide": [side_px([p.width / 2 + 0.6, -p.height / 2 - 18, p.lens_z]), side_px([p.width / 2 + 0.6, p.height / 2 + 10, p.lens_z])],
        "top_mm": p.depth + p.lens_z,
    }

    eye, right, up = camera_basis()
    corners = np.array([[x, y, z] for x in (-p.width / 2, p.width / 2) for y in (-p.height / 2, p.height / 2)
                        for z in (-p.depth, s.thickness)])
    sx, sy = corners @ right, corners @ up
    center = [(sx.min() + sx.max()) / 2, (sy.min() + sy.max()) / 2]
    px_per_mm = SIZE * 0.86 / max(sx.max() - sx.min(), sy.max() - sy.min())
    info = {
        "eye": eye.tolist(), "right": right.tolist(), "up": up.tolist(), "center": center,
        "ortho_scale": SIZE / px_per_mm, "px_per_mm_z": float(px_per_mm * up[2]),
        "bump_z": p.bump_z, "lens_z": p.lens_z, "shell_t": s.thickness,
        "sensors": [list(x) for x in p.sensor_list()],
        "parts": [n for n in LAYERS if (work / f"{n}.stl").exists()],
        "side": side,
    }
    (work / "scene.json").write_text(json.dumps(info, indent=2))
    return info


# ---------------------------------------------------------------- Cycles (inside Blender)


def srgb_to_linear(rgb):
    return tuple(((c / 255 + 0.055) / 1.055) ** 2.4 if c / 255 > 0.04045 else c / 255 / 12.92 for c in rgb) + (1.0,)


def blender_main(work: Path, out: Path, samples: int, size: int):
    import bmesh
    import bpy
    from mathutils import Matrix, Vector

    info = json.loads((work / "scene.json").read_text())
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        sc.cycles.device = "GPU"
    except Exception as e:  # CPU still works, just slower
        print("GPU unavailable:", e)
    sc.cycles.samples = samples
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.01
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 12
    sc.cycles.transmission_bounces = 12
    sc.render.resolution_x = sc.render.resolution_y = size
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    try:
        sc.view_settings.view_transform = "AgX"
        sc.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass

    # Studio lighting: Blender's bundled studio HDRI for reflections, a big overhead softbox and a rim light.
    world = bpy.data.worlds.new("studio")
    sc.world = world
    world.use_nodes = True
    wn = world.node_tree.nodes
    bg = next(n for n in wn if n.type == "BACKGROUND")
    env = wn.new("ShaderNodeTexEnvironment")
    hdri = Path(bpy.utils.system_resource("DATAFILES")) / "studiolights" / "world" / "studio.exr"
    env.image = bpy.data.images.load(str(hdri))
    world.node_tree.links.new(env.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 1.1

    def area(name, direction, size_mm, power, dist=520.0):
        d = Vector(direction).normalized()
        data = bpy.data.lights.new(name, "AREA")
        data.shape = "DISK"
        data.size = size_mm
        data.energy = power
        ob = bpy.data.objects.new(name, data)
        ob.location = d * dist
        ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
        sc.collection.objects.link(ob)

    area("key", (-0.35, -0.55, 1.0), 320, 2.6e6)
    area("rim", (0.85, 0.55, 0.35), 160, 1.1e6)
    area("fill", (0.6, -0.9, 0.25), 260, 0.5e6)

    def ortho_camera(name, v):
        eye, right, up = Vector(v["eye"]), Vector(v["right"]), Vector(v["up"])
        data = bpy.data.cameras.new(name)
        data.type = "ORTHO"
        data.ortho_scale = v["ortho_scale"]
        data.clip_start, data.clip_end = 1, 4000
        ob = bpy.data.objects.new(name, data)
        ob.matrix_world = Matrix((
            (right.x, up.x, eye.x, 0), (right.y, up.y, eye.y, 0), (right.z, up.z, eye.z, 0), (0, 0, 0, 1)))
        ob.location = right * v["center"][0] + up * v["center"][1] + eye * 1500
        sc.collection.objects.link(ob)
        return ob

    cam = ortho_camera("cam", info)
    side_cam = ortho_camera("side", info["side"])
    sc.camera = cam

    def material(name, colour=(0.5, 0.5, 0.5, 1), metallic=0.0, roughness=0.5, **extra):
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        bsdf.inputs["Base Color"].default_value = colour
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        for k, v in extra.items():
            try:
                bsdf.inputs[k].default_value = v
            except KeyError:
                print("no input", k)
        return m

    def grain(m, scale, strength):
        """Fine bump: the texture of powder coat or bead blast."""
        nt = m.node_tree
        bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
        tc = nt.nodes.new("ShaderNodeTexCoord")
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = scale
        noise.inputs["Detail"].default_value = 4
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = strength
        bump.inputs["Distance"].default_value = 0.02
        nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
        nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        return m

    def set_colour(m, rgb):
        next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Base Color"].default_value = srgb_to_linear(rgb)

    def smooth(ob, angle=32):
        bpy.context.view_layer.objects.active = ob
        for o in bpy.context.selected_objects:
            o.select_set(False)
        ob.select_set(True)
        try:
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle))
        except Exception:
            bpy.ops.object.shade_auto_smooth(angle=math.radians(angle))

    def import_stl(name):
        bpy.ops.wm.stl_import(filepath=str(work / f"{name}.stl"))
        ob = bpy.context.selected_objects[0]
        ob.name = name
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
        bm.to_mesh(ob.data)
        bm.free()
        smooth(ob)
        return ob

    def lathe(name, profile, cx, cy, z0=0.0, n=160, mat=None):
        """Closed solid of revolution from an (r, z) loop; r = 0 points collapse to the axis."""
        bm = bmesh.new()
        rings = []
        for r, z in profile:
            if r < 1e-6:
                rings.append([bm.verts.new((cx, cy, z0 + z))])
            else:
                rings.append([bm.verts.new((cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n), z0 + z))
                              for i in range(n)])
        for a, b in zip(rings, rings[1:] + rings[:1]):
            if len(a) == 1 and len(b) == 1:
                continue
            for i in range(n):
                if len(a) == 1:
                    bm.faces.new((a[0], b[i], b[(i + 1) % n]))
                elif len(b) == 1:
                    bm.faces.new((a[i], a[(i + 1) % n], b[0]))
                else:
                    bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new(name, me)
        sc.collection.objects.link(ob)
        if mat:
            ob.data.materials.append(mat)
        smooth(ob, 40)
        return ob

    def arc(cr, cz, rad, a0, a1, steps=6):
        return [(cr + rad * math.cos(math.radians(a0 + (a1 - a0) * k / steps)),
                 cz + rad * math.sin(math.radians(a0 + (a1 - a0) * k / steps))) for k in range(steps + 1)]

    # Materials
    phone_mat = material("phone", metallic=0.8, roughness=0.36, **{"Coat Weight": 0.1, "Coat Roughness": 0.25})
    bezel_mat = material("bezel", (0.045, 0.045, 0.05, 1), 1.0, 0.1)
    barrel_mat = material("barrel", (0.008, 0.008, 0.009, 1), 0.0, 0.55)
    element_mat = material("element", (0.004, 0.004, 0.006, 1), 0.0, 0.025, **{
        "IOR": 1.8, "Thin Film Thickness": 430.0, "Thin Film IOR": 1.38})
    sapphire_mat = material("sapphire", (1, 1, 1, 1), 0.0, 0.0, **{
        "IOR": 1.77, "Transmission Weight": 1.0, "Thin Film Thickness": 140.0, "Thin Film IOR": 1.38})
    flash_mat = material("flash", (0.78, 0.72, 0.52, 1), 0.0, 0.38, **{"Coat Weight": 1.0, "Coat Roughness": 0.05})
    lidar_mat = material("lidar", (0.006, 0.006, 0.008, 1), 0.0, 0.04, **{"Thin Film Thickness": 300.0, "Thin Film IOR": 1.45})
    hole_mat = material("hole", (0.002, 0.002, 0.002, 1), 0.0, 0.9)
    # Ceramic coat over Grade 5 titanium: a hard, satin, colour-matched ceramic layer (micro-arc oxide base,
    # ceramic topcoat), with the fine grain of a sprayed finish.
    powder_mat = grain(material("ceramic", metallic=0.0, roughness=0.42, **{"Coat Weight": 0.25, "Coat Roughness": 0.3}), 300, 0.1)
    brass_mat = grain(material("brass", srgb_to_linear((222, 182, 110)), 1.0, 0.34), 320, 0.12)
    windows_mat = material("windows", metallic=0.0, roughness=0.48)
    mats = {
        "suction_film": material("film", (0.66, 0.68, 0.72, 1), 0.0, 0.45, Alpha=0.5),
        "base": material("base", (0.03, 0.033, 0.04, 1), 0.0, 0.42),
        "magnet_ring": material("magnet", (0.62, 0.62, 0.64, 1), 1.0, 0.22),
        "pcb": material("pcb", (0.006, 0.05, 0.022, 1), 0.0, 0.22, **{"Coat Weight": 0.6, "Coat Roughness": 0.08}),
        "battery": material("battery", (0.23, 0.23, 0.24, 1), 0.8, 0.38),
        "coil": material("coil", srgb_to_linear((184, 115, 58)), 1.0, 0.25),
    }
    chip_mat = material("chip", (0.012, 0.012, 0.013, 1), 0.0, 0.4)
    glass_back_mat = material("back glass", metallic=0.0, roughness=0.42, **{"Coat Weight": 0.6, "Coat Roughness": 0.35})
    dark_mat = material("port", (0.01, 0.01, 0.011, 1), 0.6, 0.45)

    groups: dict[str, list] = {}
    for name in info["parts"]:
        ob = import_stl(name)
        ob.data.materials.append({"phone": phone_mat, "housing": powder_mat, "window_inserts": windows_mat}.get(name) or mats[name])
        groups[name] = [ob]
    for name, mat, group in (("phone_glass", glass_back_mat, "phone"), ("phone_dark", dark_mat, "phone"), ("shell_port", dark_mat, "housing")):
        ob = import_stl(name)
        ob.data.materials.append(mat)
        groups[group].append(ob)

    # Chips on the node board: NXP i.MX 93 (14 x 14 mm FCBGA) and the STM32U5 guard (7 x 7 mm).
    pcb = groups["pcb"][0]
    xs = [v.co.x for v in pcb.data.vertices]
    ys = [v.co.y for v in pcb.data.vertices]
    ztop = max(v.co.z for v in pcb.data.vertices)
    cy = (min(ys) + max(ys)) / 2
    for i, (cx, w, t) in enumerate(((min(xs) + 10.0, 14.0, 1.0), (min(xs) + 25.0, 7.0, 0.8))):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, ztop + t / 2))
        chip = bpy.context.active_object
        chip.name = f"chip{i}"
        chip.scale = (w, min(w, max(ys) - min(ys) - 1.0), t)
        chip.data.materials.append(chip_mat)
        bev = chip.modifiers.new("bevel", "BEVEL")
        bev.width, bev.segments = 0.15, 2
        groups["pcb"].append(chip)

    # Lenses: polished bezel, sapphire cover with an anti-reflective film, a stepped black barrel and a
    # coated front element. Small sensors: frosted flash, LiDAR glass, microphone port.
    base_z, top = info["bump_z"], info["lens_z"]
    lens_parts = []
    for name, x, y, r, z, _ in info["sensors"]:
        if z > base_z:
            rin = 0.79 * r
            h = z - base_z
            bez = [(rin, 0.0), (rin, h - 0.12), (rin + 0.12, h), (r - 0.35, h), *arc(r - 0.35, h - 0.35, 0.35, 90, 0)[1:], (r, 0.0)]
            lens_parts.append(lathe(f"{name}-bezel", bez, x, y, base_z, mat=bezel_mat))
            barrel = [(0.55 * r, h - 1.1), (0.79 * r - 0.02, h - 1.1), (0.79 * r - 0.02, h - 0.55), (0.68 * r, h - 0.55),
                      (0.68 * r, h - 0.75), (0.55 * r, h - 0.75)]
            lens_parts.append(lathe(f"{name}-barrel", barrel, x, y, base_z, mat=barrel_mat))
            re = 0.55 * r - 0.02
            dome = [(re * math.sin(math.radians(a)), h - 0.95 + 0.33 * math.cos(math.radians(a)) ** 1.5) for a in range(0, 91, 6)]
            lens_parts.append(lathe(f"{name}-element", [*dome, (re, h - 1.1), (0.0, h - 1.1)], x, y, base_z, mat=element_mat))
            glass = [(0.0, h - 0.06), (rin - 0.03, h - 0.06), (rin - 0.03, h - 0.32), (0.0, h - 0.32)]
            lens_parts.append(lathe(f"{name}-sapphire", glass, x, y, base_z, mat=sapphire_mat))
        elif name == "flash":
            lens_parts.append(lathe("flash-ring", [(0.0, 0.0), (r, 0.0), (r, 0.03), (0.0, 0.03)], x, y, base_z, mat=bezel_mat))
            lens_parts.append(lathe("flash", [(0.0, 0.0), (0.88 * r, 0.0), (0.88 * r, 0.06), (0.0, 0.07)], x, y, base_z, mat=flash_mat))
        elif name == "lidar":
            lens_parts.append(lathe("lidar", [(0.0, 0.0), (r, 0.0), (r, 0.04), (0.6 * r, 0.09), (0.0, 0.11)], x, y, base_z, mat=lidar_mat))
        else:
            lens_parts.append(lathe(name, [(0.0, 0.0), (r, 0.0), (r, 0.02), (0.0, 0.02)], x, y, base_z, mat=hole_mat))
    groups["phone"] += lens_parts

    everything = [o for o in sc.objects if o.type == "MESH"]

    def render(name, visible, holdout=(), side=False):
        for o in everything:
            o.hide_render = o not in visible and o not in holdout
            o.is_holdout = o in holdout
        sc.camera = side_cam if side else cam
        sc.render.resolution_x, sc.render.resolution_y = (
            [round(r * size / SIZE) for r in info["side"]["res"]] if side else (size, size))
        sc.render.filepath = str(out / f"{name}.png")
        bpy.ops.render.render(write_still=True)
        print("rendered", name, flush=True)

    out.mkdir(parents=True, exist_ok=True)
    for colour, rgb in PHONE_COLOURS.items():
        set_colour(phone_mat, rgb)
        set_colour(glass_back_mat, tuple(int(c * 0.78) for c in rgb))
        render(f"phone_{colour}", groups["phone"])
        render(f"side_phone_{colour}", groups["phone"], side=True)
    housing = groups["housing"][0]
    windows = groups["window_inserts"][0]
    for finish in FINISHES:
        if finish == "brass":
            housing.data.materials[0] = brass_mat
            set_colour(windows_mat, (150, 120, 72))
        else:
            housing.data.materials[0] = powder_mat
            set_colour(powder_mat, SHELL_COLOURS[finish])
            # Radio windows are PC moulded in a matching colour, so the back reads as one surface.
            set_colour(windows_mat, tuple(int(c * 0.94) for c in SHELL_COLOURS[finish]))
        render(f"housing_{finish}", groups["housing"])
        render(f"window_inserts_{finish}", groups["window_inserts"])
        render(f"side_shell_{finish}", groups["housing"] + groups["window_inserts"], side=True)
    for name in ("suction_film", "base", "magnet_ring", "pcb", "battery", "coil"):
        if name in groups:
            render(name, groups[name])
    # The lenses again, seen only through the shell's openings: the housing is a holdout, so the
    # assembled images (and the exploded view at rest) paint them over the housing's far wall.
    housing.data.materials[0] = powder_mat
    render("camera", lens_parts, holdout=[housing])
    render("side_camera", lens_parts, holdout=[housing], side=True)


# ---------------------------------------------------------------- compositing (uv environment)


def composite(out: Path, info: dict):
    from PIL import Image, ImageDraw, ImageFilter

    images = {p.stem: Image.open(p).convert("RGBA") for p in out.glob("*.png")}
    size = images["camera"].size[0]
    meta = {"size": size, "px_per_mm_z": info["px_per_mm_z"] * size / SIZE, "layers": []}
    for name in LAYERS:
        key = f"{name}_{DEFAULT_COLOUR}" if name in ("phone", "housing", "window_inserts") else name
        if key not in images:
            continue
        img = images[key]
        if key != name:
            img.save(out / f"{name}.png", optimize=True)
        images[name] = img
        meta["layers"].append({"name": name, "bbox": img.getbbox()})
    # Flattened assemblies, one per colour (shell matched to phone), for the colour picker.
    for colour in PHONE_COLOURS:
        for shell, suffix in ((colour, ""), ("brass", "_brass")):
            flat = images[f"phone_{colour}"].copy()
            for name in LAYERS[1:-2]:
                if name in images:
                    flat.alpha_composite(images[name])
            flat.alpha_composite(images[f"window_inserts_{shell}"])
            flat.alpha_composite(images[f"housing_{shell}"])
            flat.alpha_composite(images["camera"])
            flat.save(out / f"assembled_{colour}{suffix}.png", optimize=True)
    # Soft contact shadow under the phone.
    sh = Image.new("L", (size, size), 0)
    ImageDraw.Draw(sh).ellipse((size * 0.18, size * 0.80, size * 0.82, size * 0.93), fill=120)
    sh = sh.filter(ImageFilter.GaussianBlur(size / 40))
    shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    shadow.putalpha(sh)
    shadow.save(out / "shadow.png", optimize=True)
    for name, img in images.items():
        if name in ("camera",) or name.startswith(("phone_", "housing_", "window_inserts_", "side_")) or name in LAYERS:
            img.save(out / f"{name}.png", optimize=True)
    (out / "layers.json").write_text(json.dumps(meta, indent=2))
    side = info["side"]
    (out / "side.json").write_text(json.dumps({
        "res": side["res"], "guide": side["guide"], "px_per_mm_z": side["px_per_mm_z"], "top_mm": side["top_mm"]}, indent=2))


def main(argv: list[str]):
    out = Path(argv[0]) if argv and not argv[0].startswith("--") else Path("renders")
    samples = int(argv[argv.index("--samples") + 1]) if "--samples" in argv else 160
    size = int(argv[argv.index("--size") + 1]) if "--size" in argv else SIZE
    work = out / ".meshes"
    info = export_meshes(work)
    subprocess.run([BLENDER, "-b", "--factory-startup", "-P", __file__, "--", "blender", str(work), str(out),
                    str(samples), str(size)], check=True)
    composite(out, info)
    shutil.rmtree(work)


if __name__ == "__main__":
    if "--" in sys.argv and sys.argv[sys.argv.index("--") + 1:][:1] == ["blender"]:
        a = sys.argv[sys.argv.index("--") + 2:]
        blender_main(Path(a[0]), Path(a[1]), int(a[2]), int(a[3]))
    else:
        main(sys.argv[1:])
