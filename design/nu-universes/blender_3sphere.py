"""
The 3-sphere S^3 in Blender — Hopf fibres, stereographically projected to 3D.

S^3 = {(x, y, z, w) in R^4 : x^2 + y^2 + z^2 + w^2 = 1} cannot be built in 3D
directly, so this builds what a 3D render *can* show: its stereographic
projection (x, y, z) / (d - w), as glowing fibre curves, rotating in the
XW / YW 4D planes over the animation range.

Run headless (renders PNG frames + a still):
    blender -b -P design/nu-universes/blender_3sphere.py -- --out ~/Desktop/3-sphere

Run interactively: paste into Blender's Scripting workspace and Run Script,
then press Play — the fibres rotate in 4D in the viewport.

Interactive web version (drag / sliders / modes): 3-sphere.html beside this file.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

# ---------------------------------------------------------------- parameters
FIBRES = 48            # Hopf fibres
SEGMENTS = 110         # points per fibre circle
FRAMES = 120           # one full-ish 4D turn at 24 fps = 5 s loop-ish
PROJ_D = 2.4           # stereographic pole distance (matches the web viewer)
SCALE = 1.35
BEVEL = 0.006          # fibre tube thickness


def fibre_point(eta, delta, t):
    """One point of a Hopf fibre: z1 = cos(eta) e^{it}, z2 = sin(eta) e^{i(delta+t)}."""
    c, s = math.cos(eta), math.sin(eta)
    return (c * math.cos(t), c * math.sin(t),
            s * math.cos(delta + t), s * math.sin(delta + t))


def rotate_4d(p, axw, ayw):
    x, y, z, w = p
    c, s = math.cos(axw), math.sin(axw)
    x, w = x * c - w * s, x * s + w * c
    c, s = math.cos(ayw), math.sin(ayw)
    y, w = y * c - w * s, y * s + w * c
    return (x, y, z, w)


def project(p):
    x, y, z, w = p
    k = PROJ_D / max(0.18, PROJ_D - w)
    return Vector((x * k * SCALE, z * k * SCALE, y * k * SCALE))  # Blender: Z up


def hsv(h, s, v):
    import colorsys
    return (*colorsys.hsv_to_rgb(h % 1.0, s, v), 1.0)


# ---------------------------------------------------------------- scene setup
def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = os.path.expanduser(argv[argv.index("--out") + 1]) if "--out" in argv else None

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    scene = bpy.context.scene
    scene.frame_start, scene.frame_end = 1, FRAMES

    # materials are cached per colour band so 48 fibres share ~12 materials
    mats = {}
    def material(hue):
        key = round(hue, 2)
        if key not in mats:
            m = bpy.data.materials.new(f"S3_{key:.2f}")
            m.use_nodes = True
            bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
            bsdf.inputs["Base Color"].default_value = hsv(hue, 0.55, 1.0)
            bsdf.inputs["Emission Color"].default_value = hsv(hue, 0.85, 1.0)
            bsdf.inputs["Emission Strength"].default_value = 2.4
            bsdf.inputs["Roughness"].default_value = 0.35
            mats[key] = m
        return mats[key]

    curves = []
    for i in range(FIBRES):
        eta = 0.18 + (math.pi / 2 - 0.36) * ((i * 0.6180339887) % 1)
        delta = i * 2.399963  # golden angle
        cu = bpy.data.curves.new(f"Hopf_{i:02d}", "CURVE")
        cu.dimensions = "3D"
        cu.bevel_depth = BEVEL
        cu.bevel_resolution = 3
        spline = cu.splines.new("POLY")
        spline.points.add(SEGMENTS)  # SEGMENTS+1 points, last closes the loop
        ob = bpy.data.objects.new(cu.name, cu)
        ob.data.materials.append(material(eta / (math.pi / 2) * 0.75 + delta / 6.28 * 0.2))
        bpy.context.collection.objects.link(ob)
        curves.append((ob, eta, delta))

    # keyframe the projected shape: shape lives in the curve points themselves,
    # so bake every 4th frame as a keyframed point location.
    for frame in range(1, FRAMES + 1, 4):
        scene.frame_set(frame)
        phase = (frame - 1) / FRAMES * math.pi * 2
        axw, ayw = phase, phase * 0.6
        for ob, eta, delta in curves:
            pts = ob.data.splines[0].points
            for j in range(SEGMENTS + 1):
                t = j / SEGMENTS * math.pi * 2
                co = project(rotate_4d(fibre_point(eta, delta, t), axw, ayw))
                pts[j].co = (*co, 1.0)
                pts[j].keyframe_insert("co", frame=frame)
        if frame == 1:
            scene.frame_set(1)

    # camera + light + dark world, Cycles-or-Eevee agnostic (read valid engines)
    cam_data = bpy.data.cameras.new("Cam")
    cam = bpy.data.objects.new("Cam", cam_data)
    cam.location, cam.rotation_euler = (4.2, -5.2, 3.0), (math.radians(62), 0, math.radians(38))
    bpy.context.collection.objects.link(cam)
    scene.camera = cam

    sun = bpy.data.objects.new("Key", bpy.data.lights.new("Key", "SUN"))
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))
    bpy.context.collection.objects.link(sun)

    world = bpy.data.worlds.new("S3World") if not bpy.data.worlds else bpy.data.worlds[0]
    scene.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = (0.004, 0.005, 0.012, 1.0)
    bg.inputs[1].default_value = 1.0

    scene.render.resolution_x = scene.render.resolution_y = 1080
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except TypeError:
        pass  # keep whatever engine this Blender build reports

    if out:  # headless: still at frame 1 + all frames as PNGs (ffmpeg them to mp4)
        os.makedirs(out, exist_ok=True)
        scene.render.filepath = os.path.join(out, "3-sphere_")
        scene.frame_set(1)
        bpy.ops.render.render(write_still=True)
        for frame in range(1, FRAMES + 1):
            scene.frame_set(frame)
            scene.render.filepath = os.path.join(out, f"frame_{frame:03d}.png")
            bpy.ops.render.render(write_still=True)
        print(f"S3: wrote still + {FRAMES} frames to {out} "
              f"(mp4: ffmpeg -framerate 24 -i {out}/frame_%03d.png -pix_fmt yuv420p 3-sphere.mp4)")
    else:
        scene.frame_set(1)
        print(f"S3: {FIBRES} Hopf fibres built — press Play to rotate through w.")


if __name__ == "__main__":
    main()
