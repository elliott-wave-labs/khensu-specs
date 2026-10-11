# SPDX-License-Identifier: CC-BY-4.0
"""Shaded renders of each shell layer from one fixed camera, for exploded-view animation.

Every layer is drawn at its true position into an identically sized transparent PNG, so stacking
the images reproduces the assembly and translating them vertically explodes it (the camera's up
vector has a positive Z component, so a Z offset is a pure screen-space Y offset).

    uv run python render_layers.py <out_dir>
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import cadquery as cq
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import shell as S

SIZE = 1600
SS = 2  # supersampling
AZ, EL = math.radians(32), math.radians(36)
EYE = np.array([math.sin(AZ) * math.cos(EL), -math.cos(AZ) * math.cos(EL), math.sin(EL)])
FWD = -EYE
RIGHT = np.cross(FWD, [0, 0, 1.0])
RIGHT /= np.linalg.norm(RIGHT)
UP = np.cross(RIGHT, FWD)
LIGHT = np.array([-0.35, -0.55, 1.0])
LIGHT /= np.linalg.norm(LIGHT)
FILL = np.array([0.8, 0.2, 0.4])
FILL /= np.linalg.norm(FILL)

MATERIALS = {  # base rgb, specular strength, shininess, alpha
    "bezel": ((58, 60, 65), 0.8, 50, 255),
    "flash": ((226, 222, 200), 0.5, 30, 255),
    "lens": ((8, 9, 12), 0.9, 90, 255),
    "suction_film": ((205, 208, 214), 0.1, 10, 150),
    "base": ((52, 55, 61), 0.15, 20, 255),
    "magnet_ring": ((196, 200, 207), 0.8, 60, 255),
    "pcb": ((24, 56, 42), 0.3, 30, 255),
    "battery": ((34, 36, 41), 0.25, 20, 255),
    "coil": ((184, 115, 58), 0.7, 50, 255),
    "window_inserts": ((30, 31, 35), 0.6, 70, 255),
}

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
MATTE = (0.05, 6)  # specular strength, shininess: powder coat has almost no highlight
BRASS = ((181, 146, 88), 0.32, 16, 255)

LAYERS = ["phone", "suction_film", "base", "magnet_ring", "pcb", "battery", "coil", "window_inserts", "housing"]


def tess(shape: cq.Shape, tol=0.05) -> tuple[np.ndarray, np.ndarray]:
    verts, tris = shape.tessellate(tol, 0.2)
    v = np.array([(p.x, p.y, p.z) for p in verts])
    return v, np.array(tris)


def phone_with_lenses(p: S.Phone) -> tuple[cq.Shape, cq.Shape, cq.Shape, cq.Shape]:
    """Phone body (plateau only), lens rings, lens glass and the small sensors, from the CAD sensor map."""
    bx, by, bw, bh = p.bump_rect()
    body = S.outline_solid(S.rounded_rect(p.width, p.height, p.corner_r), -p.depth, p.depth).union(
        S.outline_solid(S.rounded_rect(bw, bh, p.bump_r, bx, by), 0, p.bump_z)).val()
    lenses, glass, small = cq.Workplane("XY"), cq.Workplane("XY"), cq.Workplane("XY")
    for _, x, y, r, z, _ in p.sensor_list():
        if z > p.bump_z:
            lenses = lenses.union(cq.Workplane("XY").center(x, y).circle(r).extrude(z - p.bump_z).translate((0, 0, p.bump_z)))
            glass = glass.union(cq.Workplane("XY").center(x, y).circle(r * 0.62).extrude(z - p.bump_z - 0.15).translate((0, 0, p.bump_z + 0.1)))
        else:
            small = small.union(cq.Workplane("XY").center(x, y).circle(r).extrude(0.1).translate((0, 0, p.bump_z)))
    return body, lenses.val(), glass.val(), small.val()


def project(v: np.ndarray, scale: float, center: np.ndarray) -> np.ndarray:
    x = (v @ RIGHT - center[0]) * scale + SIZE * SS / 2
    y = SIZE * SS / 2 - (v @ UP - center[1]) * scale
    return np.stack([x, y], axis=1)


def shade(n: np.ndarray, mat) -> tuple[int, int, int, int]:
    rgb, ks, shin, alpha = mat
    diff = max(0.0, float(n @ LIGHT)) * 0.75 + max(0.0, float(n @ FILL)) * 0.2 + 0.22
    h = LIGHT + EYE
    h /= np.linalg.norm(h)
    spec = ks * max(0.0, float(n @ h)) ** shin
    c = [min(255, int(ch * diff + 255 * spec)) for ch in rgb]
    return (*c, alpha)


def grain(img: Image.Image, amount: float = 7.0, seed: int = 1) -> Image.Image:
    """Fine speckle on opaque pixels: the texture of powder coat or bead blast."""
    a = np.asarray(img).astype(np.float32)
    noise = np.random.default_rng(seed).normal(0, amount, a.shape[:2])[..., None]
    a[..., :3] = np.clip(a[..., :3] + noise * (a[..., 3:4] > 0), 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def render(shapes: list[tuple[cq.Shape, str]], scale: float, center: np.ndarray) -> Image.Image:
    """Z-buffered rasterisation of every shape in the call, so hidden faces never show through."""
    W = SIZE * SS
    zbuf = np.full((W, W), np.inf, np.float32)
    rgba = np.zeros((W, W, 4), np.uint8)
    for shape, mat_name in shapes:
        mat = MATERIALS[mat_name]
        v, t = tess(shape)
        if len(t) == 0:
            continue
        p2 = project(v, scale, center)
        depth = v @ FWD
        a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
        n = np.cross(b - a, c - a)
        ln = np.linalg.norm(n, axis=1)
        ok = ln > 1e-12
        n[ok] /= ln[ok, None]
        for i in np.nonzero(ok)[0]:
            if n[i] @ EYE <= 0:
                continue
            (xa, ya), (xb, yb), (xc, yc) = p2[t[i]]
            da, db, dc = depth[t[i]]
            x0, x1 = max(int(min(xa, xb, xc)), 0), min(int(max(xa, xb, xc)) + 1, W - 1)
            y0, y1 = max(int(min(ya, yb, yc)), 0), min(int(max(ya, yb, yc)) + 1, W - 1)
            den = (yb - yc) * (xa - xc) + (xc - xb) * (ya - yc)
            if x1 < x0 or y1 < y0 or abs(den) < 1e-9:
                continue
            X, Y = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            w0 = ((yb - yc) * (X - xc) + (xc - xb) * (Y - yc)) / den
            w1 = ((yc - ya) * (X - xc) + (xa - xc) * (Y - yc)) / den
            w2 = 1 - w0 - w1
            z = w0 * da + w1 * db + w2 * dc
            zs = zbuf[y0:y1 + 1, x0:x1 + 1]
            m = (w0 >= -1e-4) & (w1 >= -1e-4) & (w2 >= -1e-4) & (z < zs)
            zs[m] = z[m]
            rgba[y0:y1 + 1, x0:x1 + 1][m] = shade(n[i], mat)
    return Image.fromarray(rgba, "RGBA").resize((SIZE, SIZE), Image.LANCZOS)


def main(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    p = next(ph for ph in S.PHONES if ph.name == "iphone-18-pro")
    s = next(st for st in S.styles_for(p) if st.name == "wrap")
    parts = S.build_shell(p, s)
    body, lenses, glass, small = phone_with_lenses(p)

    corners = np.array([[x, y, z] for x in (-p.width / 2, p.width / 2) for y in (-p.height / 2, p.height / 2)
                        for z in (-p.depth, s.thickness)])
    sx, sy = corners @ RIGHT, corners @ UP
    center = np.array([(sx.min() + sx.max()) / 2, (sy.min() + sy.max()) / 2])
    scale = SIZE * SS * 0.86 / max(sx.max() - sx.min(), sy.max() - sy.min())

    meta = {"size": SIZE, "px_per_mm_z": float(scale / SS * UP[2]), "layers": []}
    images = {}
    for colour, rgb in PHONE_COLOURS.items():
        MATERIALS[f"phone_{colour}"] = (rgb, 0.4, 40, 255)
        MATERIALS[f"housing_{colour}"] = (SHELL_COLOURS[colour], *MATTE, 255)
        img = render([(body, f"phone_{colour}"), (lenses, "bezel"), (glass, "lens"), (small, "flash")], scale, center)
        img.save(out / f"phone_{colour}.png", optimize=True)
        images[f"phone_{colour}"] = img
    MATERIALS["housing_brass"] = BRASS
    for finish in [*PHONE_COLOURS, "brass"]:
        img = render([(sol, f"housing_{finish}") for sol in parts["housing"].solids().vals()], scale, center)
        img = grain(img, 7.0 if finish != "brass" else 4.0)
        img.save(out / f"housing_{finish}.png", optimize=True)
        images[f"housing_{finish}"] = img
        # Radio windows are PC moulded in a matching colour, so the back reads as one surface.
        base = MATERIALS[f"housing_{finish}"][0]
        MATERIALS[f"windows_{finish}"] = (tuple(int(ch * 0.94) for ch in base), 0.08, 10, 255)
        img = render([(sol, f"windows_{finish}") for sol in parts["window_inserts"].solids().vals()], scale, center)
        img.save(out / f"window_inserts_{finish}.png", optimize=True)
        images[f"window_inserts_{finish}"] = img
    for name in LAYERS:
        if name in ("phone", "housing", "window_inserts"):
            img = images[f"{name}_{DEFAULT_COLOUR}"]
        elif name in parts:
            img = render([(sol, name) for sol in parts[name].solids().vals()], scale, center)
        else:
            continue
        img.save(out / f"{name}.png", optimize=True)
        images[name] = img
        meta["layers"].append({"name": name, "bbox": img.getbbox()})
        print(name, img.getbbox())
    # The lenses again on their own: nothing on the shell hides them once it's on, so the assembled
    # images (and the exploded view at rest) paint them over the housing's far wall.
    # Only the faces that show through the plate's openings: lens-ring tops, glass and the small sensors.
    tops, glass_tops = cq.Workplane("XY"), cq.Workplane("XY")
    for _, x, y, r, z, _ in p.sensor_list():
        if z > p.bump_z:
            tops = tops.union(cq.Workplane("XY").center(x, y).circle(r).extrude(0.05).translate((0, 0, z - 0.05)))
            glass_tops = glass_tops.union(cq.Workplane("XY").center(x, y).circle(r * 0.62).extrude(0.05).translate((0, 0, z - 0.04)))
    camera = render([(tops.val(), "bezel"), (glass_tops.val(), "lens"), (small, "flash")], scale, center)
    camera.save(out / "camera.png", optimize=True)
    # Flattened assemblies, one per colour (shell matched to phone), for the colour picker.
    for colour in PHONE_COLOURS:
        for shell, suffix in ((colour, ""), ("brass", "_brass")):
            flat = images[f"phone_{colour}"].copy()
            for name in LAYERS[1:-2]:
                if name in images:
                    flat.alpha_composite(images[name])
            flat.alpha_composite(images[f"window_inserts_{shell}"])
            flat.alpha_composite(images[f"housing_{shell}"])
            flat.alpha_composite(camera)
            flat.save(out / f"assembled_{colour}{suffix}.png", optimize=True)
    # soft contact shadow under the phone
    sh = Image.new("L", (SIZE, SIZE), 0)
    d = ImageDraw.Draw(sh)
    d.ellipse((SIZE * 0.18, SIZE * 0.80, SIZE * 0.82, SIZE * 0.93), fill=120)
    sh = sh.filter(ImageFilter.GaussianBlur(40))
    shadow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    shadow.putalpha(sh)
    shadow.save(out / "shadow.png", optimize=True)
    (out / "layers.json").write_text(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("renders"))
