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
    "phone": ((48, 51, 57), 0.4, 40, 255),
    "bezel": ((150, 154, 162), 0.8, 50, 255),
    "lens": ((8, 9, 12), 0.9, 90, 255),
    "suction_film": ((205, 208, 214), 0.1, 10, 150),
    "base": ((52, 55, 61), 0.15, 20, 255),
    "magnet_ring": ((196, 200, 207), 0.8, 60, 255),
    "pcb": ((24, 56, 42), 0.3, 30, 255),
    "battery": ((34, 36, 41), 0.25, 20, 255),
    "coil": ((184, 115, 58), 0.7, 50, 255),
    "window_inserts": ((30, 31, 35), 0.6, 70, 255),
    "housing": ((136, 132, 125), 0.75, 45, 255),
}

LAYERS = ["phone", "suction_film", "base", "magnet_ring", "pcb", "battery", "coil", "window_inserts", "housing"]


def tess(shape: cq.Shape, tol=0.05) -> tuple[np.ndarray, np.ndarray]:
    verts, tris = shape.tessellate(tol, 0.2)
    v = np.array([(p.x, p.y, p.z) for p in verts])
    return v, np.array(tris)


def phone_with_lenses(p: S.Phone) -> tuple[cq.Shape, cq.Shape]:
    body = S.phone_reference(p).val()
    bx, by, bw, bh = p.bump_rect()
    r = min(bw * 0.19, bh * 0.34)
    pts = [(bx - bw * 0.24, by), (bx + bw * 0.24, by)]
    lenses = cq.Workplane("XY").pushPoints(pts).circle(r).extrude(1.0).translate((0, 0, p.bump_z)).val()
    glass = cq.Workplane("XY").pushPoints(pts).circle(r * 0.62).extrude(1.3).translate((0, 0, p.bump_z)).val()
    return body, lenses, glass


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


def render(shapes: list[tuple[cq.Shape, str]], scale: float, center: np.ndarray) -> Image.Image:
    """Shapes are painted in list order; triangles are depth-sorted within each shape."""
    img = Image.new("RGBA", (SIZE * SS, SIZE * SS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for shape, mat_name in shapes:
        polys = []
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
            polys.append((depth[t[i]].mean(), [tuple(p2[j]) for j in t[i]], shade(n[i], mat)))
        for _, pts, col in sorted(polys, key=lambda q: -q[0]):
            draw.polygon(pts, fill=col)
    return img.resize((SIZE, SIZE), Image.LANCZOS)


def main(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    p = next(ph for ph in S.PHONES if ph.name == "island")
    s = next(st for st in S.styles_for(p) if st.name == "wrap")
    parts = S.build_shell(p, s)
    body, lenses, glass = phone_with_lenses(p)

    corners = np.array([[x, y, z] for x in (-p.width / 2, p.width / 2) for y in (-p.height / 2, p.height / 2)
                        for z in (-p.depth, s.thickness)])
    sx, sy = corners @ RIGHT, corners @ UP
    center = np.array([(sx.min() + sx.max()) / 2, (sy.min() + sy.max()) / 2])
    scale = SIZE * SS * 0.86 / max(sx.max() - sx.min(), sy.max() - sy.min())

    meta = {"size": SIZE, "px_per_mm_z": float(scale / SS * UP[2]), "layers": []}
    for name in LAYERS:
        if name == "phone":
            shapes = [(body, "phone"), (lenses, "bezel"), (glass, "lens")]
        elif name in parts:
            shapes = [(sol, name) for sol in parts[name].solids().vals()]
        else:
            continue
        img = render(shapes, scale, center)
        img.save(out / f"{name}.png", optimize=True)
        bb = img.getbbox()
        meta["layers"].append({"name": name, "bbox": bb})
        print(name, bb)
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
