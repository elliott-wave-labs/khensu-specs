#!/usr/bin/env python3
# SPDX-License-Identifier: CC-BY-4.0
"""nu.universes — procedural Triangulum Galaxy (M33) for RealityKit / AR.

Builds M33 from the catalogue constants in design/nu-universes.md §3:
face-on spiral, NO bright bulge, NO bar, ~60 kly across, NGC 604/595 knots,
Pisces Dwarf satellite. This is a labelled reconstruction; the Hubble tiles
are the data (they cross-fade in the app by zoom).

Run headless:
  blender -b -P blender_m33.py -- --out ~/Desktop/nu-u-m33
Interactive (Blender MCP): paste the build_m33() body via execute_blender_code,
then `look` at it. Exports USDZ (RealityKit) + glTF (web) when --out is given.
"""
import math, random, sys, os

try:
    import bpy
except ImportError:
    bpy = None

SEED = 33
STARS = 40000
R_MAX_LY = 30000.0

def _clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
        pass

def _mat(name, color, emission_strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    if emission_strength:
        try:
            bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
            bsdf.inputs["Emission Strength"].default_value = emission_strength
        except Exception:
            pass
    return m

def build_m33(stars=STARS):
    if bpy is None:
        raise SystemExit("Run inside Blender: blender -b -P blender_m33.py -- --out DIR")
    _clear()
    rng = random.Random(SEED)
    # --- star points: log-spiral, two arms, disc thickness falls with radius ---
    verts, cols = [], []
    for i in range(stars):
        arm = 0.0 if i % 2 == 0 else math.pi
        r = 2000 + 26000 * (rng.random() ** 1.6)
        theta = arm + math.log(max(r / 2000, 1.0)) * 1.1 + rng.gauss(0, 0.18)
        x, y = r * math.cos(theta) / 1000.0, r * math.sin(theta) / 1000.0  # scene units: 1 = 1 kly
        z = rng.gauss(0, max(0.35 * math.exp(-r / 12000.0), 0.04))
        verts.append((x, y, z))
        young = rng.random() < 0.28  # blue arm population vs old disc
        cols.append((0.55, 0.70, 1.0) if young else (1.0, 0.82, 0.60))
    mesh = bpy.data.meshes.new("M33_stars")
    mesh.from_pydata(verts, [], [])
    mesh.update()
    # vertex colours
    color_layer = mesh.color_attributes.new(name="Col", type="FLOAT_COLOR", domain="POINT")
    for i, c in enumerate(cols):
        color_layer.data[i].color = (*c, 1.0)
    obj = bpy.data.objects.new("M33_Stars", mesh)
    bpy.context.collection.objects.link(obj)
    mat = _mat("M33_star_points", (0.8, 0.85, 1.0), 0.4)
    # point-cloud look: material on object; rendering as points is set in Eevee via geometry nodes fallback
    obj.data.materials.append(mat)

    # --- NGC 604 / 595 emission knots (icospheres, emissive pink H-alpha) ---
    for name, (lx, ly), size, col in [
        ("NGC604", (9000, 5500), 750, (1.0, 0.35, 0.55)),
        ("NGC595", (-6500, 3800), 400, (1.0, 0.45, 0.60)),
    ]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=size / 1000.0,
                                              location=(lx / 1000.0, ly / 1000.0, 0))
        o = bpy.context.active_object
        o.name = name
        o.data.materials.append(_mat(name + "_mat", col, 2.0))

    # --- Pisces Dwarf satellite ---
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.5, location=(28.0, -18.0, 2.0))
    dwarf = bpy.context.active_object
    dwarf.name = "PiscesDwarf"
    dwarf.data.materials.append(_mat("PiscesDwarf_mat", (0.9, 0.8, 0.65), 0.3))

    # --- camera + light for look/render ---
    bpy.ops.object.camera_add(location=(0, -55, 38), rotation=(math.radians(55), 0, 0))
    bpy.context.scene.camera = bpy.context.active_object
    bpy.ops.object.light_add(type="SUN", location=(10, -20, 30))
    bpy.context.active_object.data.energy = 2.0
    world = bpy.data.worlds["World"]
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = (0.005, 0.006, 0.012, 1.0)
    bg.inputs[1].default_value = 1.0
    return obj

def export_all(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    # glTF for web / model-viewer
    bpy.ops.export_scene.gltf(filepath=os.path.join(out_dir, "m33.glb"),
                              export_format="GLB", export_vertex_color="MATERIAL")
    # USD for RealityKit (usdchecker --arkit must pass on the .usdz packaging step in the app pipeline)
    try:
        bpy.ops.wm.usd_export(filepath=os.path.join(out_dir, "m33.usdc"), selected_objects_only=False)
    except Exception as e:
        print(f"USD export skipped: {e}")
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, "m33.blend"))
    print(f"nu.u M33 exported to {out_dir}")

if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    build_m33()
    if "--out" in argv:
        export_all(argv[argv.index("--out") + 1])
    else:
        print("Built M33 in scene. Pass -- --out DIR to export USD/glTF.")
