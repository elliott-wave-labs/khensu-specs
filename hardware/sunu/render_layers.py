# SPDX-License-Identifier: CC-BY-4.0
"""Path-traced renders of each shell layer from one fixed camera, for exploded-view animation.

Every layer is rendered at its true position into an identically sized transparent PNG, so stacking
the images reproduces the assembly and translating them vertically explodes it (the camera is
orthographic and its up vector has a positive Z component, so a Z offset is a pure screen-space Y offset).

    uv run python render_layers.py <out_dir> [--samples N] [--size PX]

The CAD (sunu.py, the wrap-xl style: suñůlink.shield) is exported to STL here, rendered with Blender's Cycles
(this same file runs inside Blender for that step) on the procedural iPhone 18 Pro and Apple-style studio
lights from photoreal.py, then the colour variants and assemblies are composited with Pillow.
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

# iPhone 18 Pro finishes (photoreal.COLOURS has the materials). The composites and the site's pickers use these names.
PHONE_COLOURS = ["burgundy", "glacier", "silver", "black"]
DEFAULT_COLOUR = "burgundy"
# The titanium shell's ceramic finish is the phone's colour and sheen. Brass is bare C26000 with a satin bead-blast.
FINISHES = [*PHONE_COLOURS, "brass"]
STYLE = "wrap-xl"

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

    import sunu as S

    work.mkdir(parents=True, exist_ok=True)
    p = next(ph for ph in S.PHONES if ph.name == "iphone-18-pro")
    s = next(st for st in S.styles_for(p) if st.name == STYLE)
    parts = S.build_shell(p, s)

    def save(w, name):
        cq.exporters.export(w, str(work / f"{name}.stl"), tolerance=0.01, angularTolerance=0.08)

    for name in LAYERS[1:]:
        if name in parts:
            save(parts[name], name)

    # Side view: the long edge from just above the back, camera end to the right.
    yaw, el = math.radians(7), math.radians(10)
    side_corners = np.array([[x, y, z] for x in (-p.width / 2, p.width / 2) for y in (-p.height / 2, p.height / 2)
                             for z in (-p.depth, s.thickness)])
    se, sr, su, sc_, sscale = ortho_view([math.cos(el) * math.cos(yaw), math.cos(el) * math.sin(yaw), math.sin(el)],
                                         side_corners, 2400, 750, 0.86)

    def side_px(v):
        v = np.array(v, float)
        return [round(float((v @ sr - sc_[0]) / sscale + 1200), 1), round(float(375 - (v @ su - sc_[1]) / sscale), 1)]

    side = {
        "eye": se.tolist(), "right": sr.tolist(), "up": su.tolist(), "center": sc_.tolist(),
        "ortho_scale": 2400 * sscale, "res": [2400, 750], "px_per_mm_z": float(su[2] / sscale),
        "guide": [side_px([p.width / 2 + 0.6, -p.height / 2 - 18, s.thickness]), side_px([p.width / 2 + 0.6, p.height / 2 + 10, s.thickness])],
        "lens_guide": [side_px([p.width / 2 + 0.6, -p.height / 2 - 18, p.lens_z]), side_px([p.width / 2 + 0.6, p.height / 2 + 10, p.lens_z])],
        "top_mm": p.depth + s.thickness,
        "lens_mm": p.depth + p.lens_z,
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
        "bump_z": p.bump_z, "lens_z": p.lens_z, "shell_t": s.thickness, "suction": S.B.suction,
        "outline_ymin": s.outline.val().BoundingBox().ymin,
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

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import photoreal as P

    info = json.loads((work / "scene.json").read_text())
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    P._cycles(sc, samples)
    sc.cycles.adaptive_threshold = 0.01
    sc.cycles.max_bounces = 12
    sc.cycles.transmission_bounces = 12
    sc.cycles.transparent_max_bounces = 16
    sc.render.resolution_x = sc.render.resolution_y = size
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    # Apple-style studio on black, the rig turned to face this camera.
    # Looking down at the back, the overhead key and the world's top box sit right in the mirror direction,
    # so both run lower here than in the upright product shots.
    # The side view gets its own rig and world, turned to its camera; at that grazing angle the glass mirrors
    # the overhead key, so it runs lower still.
    rigs = {}
    for view, eye, light in ((False, info["eye"], dict(key=0.18, front=0.3, sheen=0.3, side=0.8, world_strength=0.05)),
                             (True, info["side"]["eye"], dict(key=0.12, front=0.3, sheen=0.25, world_strength=0.06))):
        lights = P.studio(sc, 1.0, camera=eye, **light)
        rigs[view] = (lights, sc.world)

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
        return P.material(name, colour[:3], metallic, roughness, **extra)

    def grain(m, scale, strength):
        """Fine bump: the texture of a bead blast."""
        nt = m.node_tree
        bsdf = P.bsdf_of(m)
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

    def set_linear(m, rgb):
        P.bsdf_of(m).inputs["Base Color"].default_value = (*rgb[:3], 1.0)

    def import_stl(name):
        bpy.ops.wm.stl_import(filepath=str(work / f"{name}.stl"))
        ob = bpy.context.selected_objects[0]
        ob.name = name
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
        bm.to_mesh(ob.data)
        bm.free()
        for f in ob.data.polygons:
            f.use_smooth = True
        ob.data.set_sharp_from_angle(angle=math.radians(32))
        return ob

    # Ceramic coat over Grade 5 titanium in the phone's own colour and sheen; bare brass with a satin bead-blast.
    powder_mat = material("ceramic", metallic=0.8, roughness=0.36, **{"Coat Weight": 0.12, "Coat Roughness": 0.3})
    brass_mat = grain(material("brass", srgb_to_linear((222, 182, 110)), 1.0, 0.34), 320, 0.06)
    windows_mat = material("windows", metallic=0.0, roughness=0.48, **{"Coat Weight": 0.15, "Coat Roughness": 0.3})
    mats = {
        "suction_film": material("film", (0.66, 0.68, 0.72, 1), 0.0, 0.45, Alpha=0.5),
        "base": material("base", (0.03, 0.033, 0.04, 1), 0.0, 0.42),
        "magnet_ring": material("magnet", (0.62, 0.62, 0.64, 1), 1.0, 0.22),
        "pcb": material("pcb", (0.006, 0.05, 0.022, 1), 0.0, 0.22, **{"Coat Weight": 0.6, "Coat Roughness": 0.08}),
        "battery": material("battery", (0.23, 0.23, 0.24, 1), 0.8, 0.38),
        "coil": material("coil", srgb_to_linear((184, 115, 58)), 1.0, 0.25),
    }
    chip_mat = material("chip", (0.012, 0.012, 0.013, 1), 0.0, 0.4)

    groups: dict[str, list] = {}
    for name in info["parts"]:
        ob = import_stl(name)
        ob.data.materials.append({"housing": powder_mat, "window_inserts": windows_mat}.get(name) or mats[name])
        groups[name] = [ob]
    # The plug-through sits inside the antenna band, so it renders with the band, which occludes it from above.
    groups["window_inserts"].append(P.shield_port(None, info["outline_ymin"], info["shell_t"], info["suction"]))

    # The procedural iPhone 18 Pro: every mesh under its root; the lens modules are one object.
    phone = P.build_phone(DEFAULT_COLOUR)
    phone_meshes = [o for o in sc.objects if o.type == "MESH" and o.parent == phone]
    groups["phone"] = phone_meshes
    lens_parts = [o for o in phone_meshes if o.name == "iPhone camera"]

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

    everything = [o for o in sc.objects if o.type == "MESH"]

    def render(name, visible, holdout=(), side=False):
        for o in everything:
            o.hide_render = o not in visible and o not in holdout
            o.is_holdout = o in holdout
        sc.camera = side_cam if side else cam
        for view, (lights, world) in rigs.items():
            for l in lights:
                l.hide_render = view != side
            if view == side:
                sc.world = world
        sc.render.resolution_x, sc.render.resolution_y = (
            [round(r * size / SIZE) for r in info["side"]["res"]] if side else (size, size))
        sc.render.filepath = str(out / f"{name}.png")
        bpy.ops.render.render(write_still=True)
        print("rendered", name, flush=True)

    out.mkdir(parents=True, exist_ok=True)
    only = os.environ.get("SUNU_ONLY", "")
    for colour in PHONE_COLOURS:
        P.recolour(colour)
        if not only or "phone" in only:
            render(f"phone_{colour}", groups["phone"])
            render(f"side_phone_{colour}", groups["phone"], side=True)
    housing = groups["housing"][0]
    for finish in FINISHES:
        wb = P.bsdf_of(windows_mat)
        if finish == "brass":
            housing.data.materials[0] = brass_mat
            # Against bare brass the windows are gloss black: an accent ring round the inlay and a band at the bottom.
            set_linear(windows_mat, (0.004, 0.004, 0.0045))
            wb.inputs["Metallic"].default_value, wb.inputs["Roughness"].default_value = 0.0, 0.18
        else:
            housing.data.materials[0] = powder_mat
            set_linear(powder_mat, P.COLOURS[finish]["alu"])
            # Radio windows are PC moulded and coated to match, so the back reads as one surface.
            set_linear(windows_mat, P.COLOURS[finish]["alu"])
            wb.inputs["Metallic"].default_value, wb.inputs["Roughness"].default_value = 0.6, 0.42
        if not only or "housing" in only:
            render(f"housing_{finish}", groups["housing"])
            render(f"window_inserts_{finish}", groups["window_inserts"])
            render(f"side_shell_{finish}", groups["housing"] + groups["window_inserts"], side=True)
    if not only or "parts" in only:
        for name in ("suction_film", "base", "magnet_ring", "pcb", "battery", "coil"):
            if name in groups:
                render(name, groups[name])
    # The lenses again, seen only past the shell: the housing is a holdout, so the assembled images (and the
    # exploded view at rest) paint them over anything of the shell's that the renders stacked on top.
    housing.data.materials[0] = powder_mat
    for colour in PHONE_COLOURS:
        P.recolour(colour)
        render(f"camera_{colour}", lens_parts, holdout=[housing])
    P.recolour(DEFAULT_COLOUR)
    render("side_camera", lens_parts, holdout=[housing], side=True)


# ---------------------------------------------------------------- compositing (uv environment)


def composite(out: Path, info: dict):
    from PIL import Image, ImageDraw, ImageFilter

    images = {p.stem: Image.open(p).convert("RGBA") for p in out.glob("*.png")}
    images["camera"] = images[f"camera_{DEFAULT_COLOUR}"]
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
            flat.alpha_composite(images[f"camera_{colour}"])
            flat.save(out / f"assembled_{colour}{suffix}.png", optimize=True)
    # Soft contact shadow under the phone.
    sh = Image.new("L", (size, size), 0)
    ImageDraw.Draw(sh).ellipse((size * 0.18, size * 0.80, size * 0.82, size * 0.93), fill=120)
    sh = sh.filter(ImageFilter.GaussianBlur(size / 40))
    shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    shadow.putalpha(sh)
    shadow.save(out / "shadow.png", optimize=True)
    for name, img in images.items():
        if name.startswith("camera_"):
            continue
        if name in ("camera",) or name.startswith(("phone_", "housing_", "window_inserts_", "side_")) or name in LAYERS:
            img.save(out / f"{name}.png", optimize=True)
    (out / "layers.json").write_text(json.dumps(meta, indent=2))
    side = info["side"]
    (out / "side.json").write_text(json.dumps({
        "res": side["res"], "guide": side["guide"], "lens_guide": side["lens_guide"], "px_per_mm_z": side["px_per_mm_z"],
        "top_mm": side["top_mm"], "lens_mm": side["lens_mm"]}, indent=2))


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
