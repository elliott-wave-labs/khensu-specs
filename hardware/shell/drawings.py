# SPDX-License-Identifier: CC-BY-4.0
"""Production drawings for the khensu shell.

Builds A3 sheets as AutoCAD DXF (R2018, millimetres, native DIMENSION and HATCH
entities) from the parametric model in shell.py, plus one combined PDF:

  drawings/<phone>/KS-<phone>-<style>-100.dxf   assembly with parts list
  drawings/<phone>/KS-<phone>-<style>-101.dxf   machined housing
  drawings/<phone>/KS-<phone>-CASE-201.dxf      silicone shock case
  drawings/khensu-shell-drawings.pdf            every sheet

Views are true hidden-line projections of the solids, third-angle projection.
"""

from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

import cadquery as cq
import ezdxf
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from ezdxf.addons.drawing import Frontend, RenderContext  # noqa: E402
from ezdxf.addons.drawing.config import (  # noqa: E402
    BackgroundPolicy,
    ColorPolicy,
    Configuration,
    LineweightPolicy,
)
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend  # noqa: E402
from ezdxf.enums import TextEntityAlignment  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from OCP.BRepLib import BRepLib  # noqa: E402
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt  # noqa: E402
from OCP.HLRAlgo import HLRAlgo_Projector  # noqa: E402
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape  # noqa: E402

import shell as S  # noqa: E402

OUT = Path(__file__).parent / "drawings"
SHEET_W, SHEET_H = 420.0, 297.0
FRAME = (20.0, 10.0, 410.0, 287.0)
REV = "A"
DATE = dt.date(2026, 10, 10).isoformat()

V2 = tuple[float, float]
Map = Callable[[cq.Vector], V2]

FRONT = ((0, 0, 1), (1, 0, 0))  # looking at the outer face; X = x, Y = y
RIGHT = ((1, 0, 0), (0, 0, -1))  # from +X; X = -z, Y = y
BOTTOM = ((0, -1, 0), (1, 0, 0))  # from -Y; X = x, Y = z
ISO = ((1, -1, 1), (1, 1, 0))


# ---------- DXF document ----------

def new_doc() -> ezdxf.document.Drawing:
    doc = ezdxf.new("R2018", setup=True, units=4)
    doc.header["$MEASUREMENT"] = 1
    doc.header["$LTSCALE"] = 0.4
    doc.header["$INSUNITS"] = 4
    doc.styles.new("KHENSU", dxfattribs={"font": "isocpeur.ttf"})
    layers = [
        ("OUTLINE", 7, "CONTINUOUS", 50),
        ("HIDDEN", 8, "DASHED", 25),
        ("CENTER", 1, "CENTER", 18),
        ("SECTION", 7, "CONTINUOUS", 50),
        ("HATCH", 8, "CONTINUOUS", 13),
        ("DIM", 4, "CONTINUOUS", 18),
        ("TEXT", 7, "CONTINUOUS", 25),
        ("PHANTOM", 6, "PHANTOM", 18),
        ("BORDER", 7, "CONTINUOUS", 70),
        ("TITLE", 7, "CONTINUOUS", 35),
    ]
    for name, color, lt, lw in layers:
        doc.layers.add(name, color=color, linetype=lt, lineweight=lw)
    ds = doc.dimstyles.new("KHENSU")
    for k, v in dict(
        dimtxt=2.5, dimasz=2.0, dimexe=1.0, dimexo=0.8, dimgap=0.6, dimdec=2, dimtad=1,
        dimtih=0, dimtoh=0, dimzin=8, dimdsep=ord("."), dimtxsty="KHENSU", dimlunit=2,
        dimclrd=4, dimclre=4, dimclrt=7, dimcen=-1.5, dimtmove=2, dimatfit=3,
    ).items():
        ds.dxf.set(k, v)
    return doc


def text(msp, s: str, at: V2, h: float = 2.5, align=TextEntityAlignment.BOTTOM_LEFT, layer="TEXT", rot=0.0):
    msp.add_text(s, height=h, rotation=rot, dxfattribs={"layer": layer, "style": "KHENSU"}).set_placement(at, align=align)


def line(msp, a: V2, b: V2, layer="OUTLINE"):
    msp.add_line(a, b, dxfattribs={"layer": layer})


def rect(msp, x0, y0, x1, y1, layer="TITLE"):
    msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True, dxfattribs={"layer": layer})


# ---------- geometry to DXF ----------

def project(shape: cq.Shape, view) -> tuple[list[cq.Edge], list[cq.Edge]]:
    n, x = view
    algo = HLRBRep_Algo()
    algo.Add(shape.wrapped)
    algo.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*n), gp_Dir(*x))))
    algo.Update()
    algo.Hide()
    hlr = HLRBRep_HLRToShape(algo)

    def collect(comps) -> list[cq.Edge]:
        out = []
        for c in comps:
            if c is None or c.IsNull():
                continue
            for e in cq.Shape.cast(c).Edges():
                BRepLib.BuildCurves3d_s(e.wrapped, 1e-6)
                out.append(e)
        return out

    return (
        collect([hlr.VCompound(), hlr.OutLineVCompound()]),
        collect([hlr.HCompound(), hlr.OutLineHCompound()]),
    )


def bbox2d(edges: Iterable[cq.Edge]) -> tuple[float, float, float, float]:
    bb = cq.Compound.makeCompound(list(edges)).BoundingBox()
    return bb.xmin, bb.ymin, bb.xmax, bb.ymax


def add_edges(msp, edges: Iterable[cq.Edge], m: Map, scale: float, layer: str):
    for e in edges:
        gt = e.geomType()
        if gt == "LINE":
            a, b = m(e.startPoint()), m(e.endPoint())
            if math.dist(a, b) > 1e-4:
                msp.add_line(a, b, dxfattribs={"layer": layer})
        elif gt == "CIRCLE":
            c = m(e.arcCenter())
            r = e.radius() * scale
            if e.IsClosed():
                msp.add_circle(c, r, dxfattribs={"layer": layer})
                continue
            a, mid, b = m(e.startPoint()), m(e.positionAt(0.5)), m(e.endPoint())
            ang = [math.degrees(math.atan2(p[1] - c[1], p[0] - c[0])) for p in (a, mid, b)]
            ccw = (ang[1] - ang[0]) % 360 < (ang[2] - ang[0]) % 360
            s, t = (ang[0], ang[2]) if ccw else (ang[2], ang[0])
            msp.add_arc(c, r, s, t, dxfattribs={"layer": layer})
        else:
            pts = [m(p) for p in e.positions(np.linspace(0, 1, 32).tolist())]
            msp.add_lwpolyline(pts, dxfattribs={"layer": layer})


def view_map(origin: V2, center: V2, scale: float) -> Callable[[float, float], V2]:
    return lambda u, v: (origin[0] + scale * (u - center[0]), origin[1] + scale * (v - center[1]))


def draw_view(msp, shape: cq.Shape, view, origin: V2, scale: float = 1.0, hidden=True, center: V2 | None = None):
    """Draw a projected view centred at origin; returns (map from 2D view coords, sheet bbox)."""
    vis, hid = project(shape, view)
    x0, y0, x1, y1 = bbox2d(vis)
    c = center or ((x0 + x1) / 2, (y0 + y1) / 2)
    f = view_map(origin, c, scale)
    m: Map = lambda p: f(p.x, p.y)
    add_edges(msp, vis, m, scale, "OUTLINE")
    if hidden:
        add_edges(msp, hid, m, scale, "HIDDEN")
    a, b = f(x0, y0), f(x1, y1)
    return f, (a[0], a[1], b[0], b[1])


def section_faces(shape: cq.Shape, y_max: float | None = None, x: float = 0.0) -> list[cq.Face]:
    """Faces of the cut at plane x (section A-A at x = 0)."""
    slab = cq.Solid.makeBox(0.01, 2000, 2000, cq.Vector(x, -1000, -1000))
    if y_max is not None:
        slab = slab.intersect(cq.Solid.makeBox(1, y_max + 1000, 2000, cq.Vector(x - 0.5, -1000, -1000)))
    try:
        cut = shape.intersect(slab)
    except Exception:
        return []
    return [f for f in cut.Faces() if abs(f.Center().x - x) < 1e-6 and abs(abs(f.normalAt().x) - 1) < 1e-6]


def add_hatched(msp, faces: list[cq.Face], m: Map, scale: float, pattern="ANSI31", pscale=0.35, angle=0.0, solid=False):
    for face in faces:
        h = msp.add_hatch(color=8, dxfattribs={"layer": "HATCH"})
        if solid:
            h.set_solid_fill(color=8)
        else:
            h.set_pattern_fill(pattern, scale=pscale, angle=angle, color=8)
        for i, w in enumerate([face.outerWire(), *face.innerWires()]):
            n = max(48, int(w.Length() * 6))
            pts = [m(p) for p in w.positions(np.linspace(0, 1, n).tolist())]
            h.paths.add_polyline_path(pts, is_closed=True, flags=1 if i == 0 else 16)
        add_edges(msp, face.Edges(), m, scale, "SECTION")


# ---------- dimensions ----------

def dim(msp, p1: V2, p2: V2, base: V2, angle=0.0, text_="<>", lfac=1.0):
    msp.add_linear_dim(
        base=base, p1=p1, p2=p2, angle=angle, dimstyle="KHENSU", text=text_,
        override={"dimlfac": lfac}, dxfattribs={"layer": "DIM"},
    ).render()


def dim_r(msp, center: V2, r_sheet: float, angle: float, lfac=1.0, text_="<>"):
    msp.add_radius_dim(center=center, radius=r_sheet, angle=angle, dimstyle="KHENSU", text=text_,
                       override={"dimlfac": lfac}, dxfattribs={"layer": "DIM"}).render()


def dim_d(msp, center: V2, r_sheet: float, angle: float, lfac=1.0, text_="<>"):
    msp.add_diameter_dim(center=center, radius=r_sheet, angle=angle, dimstyle="KHENSU", text=text_,
                         override={"dimlfac": lfac}, dxfattribs={"layer": "DIM"}).render()


def center_mark(msp, c: V2, size: float):
    line(msp, (c[0] - size, c[1]), (c[0] + size, c[1]), "CENTER")
    line(msp, (c[0], c[1] - size), (c[0], c[1] + size), "CENTER")


def section_line(msp, x: float, y0: float, y1: float, label="A"):
    line(msp, (x, y0 - 3), (x, y1 + 3), "CENTER")
    for y in (y0 - 3, y1 + 3):
        msp.add_lwpolyline([(x, y), (x - 6, y)], dxfattribs={"layer": "SECTION", "const_width": 0.5})
        msp.add_solid([(x - 6, y + 1.2), (x - 9, y), (x - 6, y - 1.2)], dxfattribs={"layer": "SECTION"})
        text(msp, label, (x - 10.5, y), 3.5, TextEntityAlignment.MIDDLE_RIGHT)


def view_label(msp, s: str, at: V2, sub: str = ""):
    text(msp, s, at, 3.5, TextEntityAlignment.TOP_CENTER)
    if sub:
        text(msp, sub, (at[0], at[1] - 5), 2.5, TextEntityAlignment.TOP_CENTER)


def balloon(msp, n: int, target: V2, at: V2):
    line(msp, target, at, "DIM")
    msp.add_circle(target, 0.4, dxfattribs={"layer": "DIM"})
    msp.add_circle(at, 3.0, dxfattribs={"layer": "TEXT"})
    text(msp, str(n), at, 2.5, TextEntityAlignment.MIDDLE_CENTER)


# ---------- sheet furniture ----------

@dataclass
class TitleInfo:
    title: str
    subtitle: str
    dwg_no: str
    material: str
    finish: str
    scale: str
    mass: str
    sheet: str


def projection_symbol(msp, x: float, y: float):
    """Third-angle symbol: frustum, then end view on the side of the small end."""
    msp.add_lwpolyline([(x, y - 2.4), (x + 7, y - 1.4), (x + 7, y + 1.4), (x, y + 2.4)], close=True, dxfattribs={"layer": "TITLE"})
    line(msp, (x - 1, y), (x + 8, y), "CENTER")
    msp.add_circle((x + 12, y), 2.4, dxfattribs={"layer": "TITLE"})
    msp.add_circle((x + 12, y), 1.4, dxfattribs={"layer": "TITLE"})


def sheet_frame(msp, info: TitleInfo, notes: list[str]):
    rect(msp, 0, 0, SHEET_W, SHEET_H, "TITLE")
    x0, y0, x1, y1 = FRAME
    rect(msp, x0, y0, x1, y1, "BORDER")
    for i in range(1, 8):  # zone ticks
        x = x0 + (x1 - x0) * i / 8
        line(msp, (x, y1), (x, y1 + 5), "TITLE")
        line(msp, (x, y0), (x, y0 - 5), "TITLE")
    tx0, ty0 = 240.0, y0
    rows = [ty0, ty0 + 9, ty0 + 20, ty0 + 30, ty0 + 40, ty0 + 50, ty0 + 60]
    rect(msp, tx0, ty0, x1, rows[-1], "TITLE")
    for y in rows[1:-1]:
        line(msp, (tx0, y), (x1, y), "TITLE")
    cols = [tx0 + 40, tx0 + 85, tx0 + 125]
    line(msp, (cols[0], rows[0]), (cols[0], rows[1]), "TITLE")
    line(msp, (cols[1], rows[0]), (cols[1], rows[1]), "TITLE")
    line(msp, (cols[2], rows[0]), (cols[2], rows[2]), "TITLE")
    line(msp, (tx0 + 85, rows[4]), (tx0 + 85, rows[5]), "TITLE")
    line(msp, (tx0 + 68, rows[5]), (tx0 + 68, rows[6]), "TITLE")
    line(msp, (tx0 + 125, rows[5]), (tx0 + 125, rows[6]), "TITLE")

    def cell(label: str, value: str, x: float, y: float, h: float = 2.5):
        text(msp, label, (x + 1.2, y + 6.5 if h <= 3 else y + 7.5), 1.6, layer="TITLE")
        text(msp, value, (x + 1.2, y + 1.3), h)

    cell("SCALE", info.scale, tx0, rows[0])
    cell("MASS (EST.)", info.mass, cols[0], rows[0])
    cell("SHEET", info.sheet, cols[1], rows[0])
    cell("REV", REV, cols[2], rows[0])
    cell("DRAWING NUMBER", info.dwg_no, tx0, rows[1], 4.0)
    cell("SIZE", "A3", cols[2], rows[1])
    cell("PART", info.subtitle, tx0, rows[2])
    cell("", info.title, tx0, rows[3], 3.5)
    cell("MATERIAL", info.material, tx0, rows[4], 2.0)
    cell("FINISH", info.finish, tx0 + 85, rows[4], 2.0)
    cell("ELLIOTT WAVE LABS", "khensu.nu", tx0, rows[5], 3.0)
    cell("DRAWN / DATE", f"EW  {DATE}", tx0 + 70, rows[5], 2.2)
    projection_symbol(msp, tx0 + 133, rows[5] + 6.2)
    text(msp, "THIRD ANGLE", (tx0 + 145, rows[5] + 0.8), 1.4, TextEntityAlignment.BOTTOM_CENTER, "TITLE")
    text(msp, "PRELIMINARY: PHONE INTERFACE DIMENSIONS TO BE VERIFIED AGAINST APPLE ACCESSORY DESIGN GUIDELINES",
         (tx0, rows[-1] + 2), 1.8, layer="TITLE")

    nx, ny = x0 + 3, y0 + 3
    text(msp, "NOTES", (nx, ny + 6 + 4.2 * len(notes)), 3.0)
    for i, s in enumerate(notes):
        text(msp, f"{i + 1}. {s}", (nx, ny + 4.2 * (len(notes) - 1 - i) + 3), 2.0)


# ---------- sheets ----------

HOUSING_NOTES = [
    "DIMENSIONS IN MM. DO NOT SCALE DRAWING. STEP MODEL GOVERNS UNDIMENSIONED GEOMETRY.",
    "GENERAL TOLERANCES ISO 2768-mK UNLESS NOTED. PHONE INTERFACE FEATURES %%p0.05.",
    "BREAK SHARP EDGES 0.1-0.2. INTERNAL CORNER RADII 0.5 MIN.",
    "WINDOWS FILLED WITH ITEM 2 (PC), FLUSH TO SKIN WITHIN 0.02.",
    "MASK INTERNAL SKIN FOR GRAPHITE SHEET BOND (ITEM 9). NO BURRS AT USB-C OPENING.",
    "KEEP 40 MM NON-METAL ALONG BOTTOM EDGE (HALOW ANTENNA). NO METAL OVER COIL WINDOW.",
]

ASSEMBLY_NOTES = [
    "DIMENSIONS IN MM. SEE -101 FOR HOUSING DETAIL. STEP ASSEMBLY GOVERNS.",
    "BOND ITEM 3 TO HOUSING WITH 0.1 PSA PERIMETER BEAD; ITEM 4 LAMINATED TO ITEM 3.",
    "CELLS (ITEM 8) TO UN38.3 AND IEC 62133-2; PCM ON BOARD; NO CELL TOUCHES METAL.",
    "ITEM 9 GRAPHITE 25 UM ACROSS INNER SKIN, CLEAR OF COIL AND ANTENNA WINDOWS.",
    "MAGNET RING POLARITY AND ALIGNMENT PER MAGSAFE-COMPATIBLE ARRAY; VERIFY WITH TARGET PHONE.",
    "ATTACHMENT, DROP AND THERMAL TESTS PER SPEC.md SECTION 8 BEFORE RELEASE.",
]

CASE_NOTES = [
    "DIMENSIONS IN MM. LIQUID SILICONE RUBBER, SHORE 55A %%p5. STEP MODEL GOVERNS.",
    "ADD 0.5-1%%d DRAFT TO ALL WALLS BEFORE TOOLING; PARTING LINE AT MAX OUTLINE.",
    "BUTTON COVERS, SPEAKER, MIC AND USB-C OPENINGS PER APPLE DRAWINGS FOR TARGET MODEL.",
    "GENERAL TOLERANCES %%p0.15; CAMERA OPENING %%p0.10.",
    "HOLDS PHONE WITH WRAP MODULE (KS-*-WRAP-100). DROP TEST 1.2 M TO CONCRETE, 26 DROPS.",
]

BOM = [
    # item, part key, description, material / spec, process
    (1, "housing", "HOUSING", "TI-6AL-4V GR5", "CNC, SEE -101"),
    (2, "window_inserts", "RADIO / COIL WINDOWS", "PC, UL94 V-0, COLOUR MATCHED", "INSERT MOULD OR BOND"),
    (3, "base", "BASE PLATE 0.6", "PC-GF30", "MOULD OR CNC"),
    (4, "suction_film", "MICRO-SUCTION FILM 0.3", "NANO-SUCTION PU", "DIE CUT"),
    (5, "magnet_ring", "MAGNET RING", "NDFEB N52, NI-CU-NI", "BOUGHT IN"),
    (6, "coil", "QI2 RECEIVER COIL + FERRITE", "QI2 CERTIFIED MODULE", "BOUGHT IN"),
    (7, "pcb", "MAIN BOARD (SOM, GUARD, HALOW, WI-FI, BLE)", "PCBA, SEE SPEC.md", "SMT"),
    (8, "battery", "CELL PACK", "LI-ION POUCH 3.85 V, CUSTOM SHAPE", "BOUGHT IN"),
    (9, None, "GRAPHITE SHEET 25 UM", "PYROLYTIC GRAPHITE + PSA", "DIE CUT"),
    (10, None, "USB-C RECEPTACLE (SLIM STYLES)", "USB-C 2.0, MID-MOUNT, 16 PIN", "BOUGHT IN"),
]


def mass_str(parts: dict, density: float) -> str:
    return f"{S.mass_g(parts, density):.0f} G (AL)"


def housing_sheet(p: S.Phone, s: S.Style, parts: dict, dwg: str, sheet: str) -> ezdxf.document.Drawing:
    doc = new_doc()
    msp = doc.modelspace()
    housing = parts["housing"].val() if len(parts["housing"].solids().vals()) == 1 else cq.Compound.makeCompound(parts["housing"].solids().vals())
    ob = s.outline.val().BoundingBox()
    t = s.thickness

    fx, fy = 75.0, 178.0
    f, fb = draw_view(msp, housing, FRONT, (fx, fy), 1.0, hidden=True)
    to = lambda x, y: f(x, y)
    view_label(msp, "FRONT (OUTER FACE)", (fx, fb[1] - 13))

    # Overall size, corner radius
    dim(msp, to(ob.xmin, ob.ymax), to(ob.xmax, ob.ymax), (fx, fb[3] + 14), 0, "<> %%p0.05")
    dim(msp, to(ob.xmin, ob.ymin), to(ob.xmin, ob.ymax), (fb[0] - 9, fy), 90, "<> %%p0.05")
    r_corner = {"card": 8.0, "fill": p.corner_r - 3.0}.get(s.name, p.corner_r - S.B.edge_inset)
    dim_r(msp, to(ob.xmin + r_corner, ob.ymin + r_corner), r_corner, 225, text_="R<>")
    # MagSafe axis
    cx, cy = s.magsafe_center
    mc = to(cx, cy)
    center_mark(msp, mc, 30)
    text(msp, "MAGSAFE AXIS", (mc[0] + 2, mc[1] + 1.2), 2.0)
    dim(msp, to(ob.xmax, ob.ymin), to(cx, cy), (fb[2] + 8, fy), 90, "<> %%p0.05")
    if "coil" in parts:
        dim_d(msp, mc, S.B.coil_window_d / 2, 35, text_="<> WINDOW")
    # Antenna window
    ant = parts["window_inserts"].solids().vals()
    ant_bb = min(ant, key=lambda v: v.BoundingBox().ymin).BoundingBox()
    dim(msp, to(ant_bb.xmin, ant_bb.ymax), to(ant_bb.xmax, ant_bb.ymax), (fx, to(0, ant_bb.ymax)[1] + 5), 0, "<> WINDOW")
    dim(msp, to(ant_bb.xmax, ob.ymin), to(ant_bb.xmax, ant_bb.ymax), (to(ant_bb.xmax, 0)[0] + 6, 0), 90)
    # Camera bump cutout, if the outline has a hole
    holes = s.outline.faces("<Z").val().innerWires()
    if holes:
        hb = holes[0].BoundingBox()
        dim(msp, to(hb.xmin, hb.ymin), to(hb.xmax, hb.ymin), (0, to(0, hb.ymin)[1] - 5), 0, "<> %%p0.05")
        dim(msp, to(hb.xmax, hb.ymin), to(hb.xmax, hb.ymax), (to(hb.xmax, 0)[0] + 6, 0), 90, "<> %%p0.05")
        dim(msp, to(ob.xmin, hb.ymax), to(hb.xmin, hb.ymax), (0, fb[3] + 7), 0)
        text(msp, "CAMERA CUTOUT: 0.6 CLEARANCE ALL ROUND", (fb[0], fb[3] + 20), 2.0)
    else:
        clr = S.Phone.bump_bottom(p) - ob.ymax
        text(msp, f"TOP EDGE: {clr:.1f} CLEARANCE TO CAMERA BUMP", (fb[0], fb[3] + 20), 2.0)
    section_line(msp, mc[0], fb[1], fb[3])

    # Right view
    rx = fb[2] + 28
    _, rb = draw_view(msp, housing, RIGHT, (rx, fy), 1.0, hidden=True)
    view_label(msp, "RIGHT", (rx, rb[1] - 13))
    dim(msp, (rb[0], rb[3]), (rb[2], rb[3]), ((rb[0] + rb[2]) / 2, rb[3] + 8), 0, f"{t - S.B.suction:.2f}")

    # Bottom view
    by = fb[1] - 26
    _, bbv = draw_view(msp, housing, BOTTOM, (fx, by), 1.0, hidden=False)
    view_label(msp, "BOTTOM", (fx, bbv[1] - 6))
    if s.usb_c:
        uh = min(S.B.usb_h, t - 1.2)
        text(msp, f"USB-C OPENING {S.B.usb_w:.1f} x {uh:.1f}, CENTRED, R0.5 CORNERS", (bbv[2] + 4, by - 1), 2.0)

    # Section A-A, full length
    sx = rx + 34
    faces = section_faces(housing)
    if faces:
        allb = cq.Compound.makeCompound(faces).BoundingBox()
        sc = (-(allb.zmin + allb.zmax) / 2, (allb.ymin + allb.ymax) / 2)
        sf = view_map((sx, fy), sc, 1.0)
        add_hatched(msp, faces, lambda q: sf(-q.z, q.y), 1.0, solid=True)
        view_label(msp, "SECTION A-A", (sx, fy - (allb.ymax - allb.ymin) / 2 - 13))

    # Detail B: section near the bottom edge, 5:1
    k = 5.0
    L = 24.0
    xb = (min(S.B.antenna_l, ob.xlen - 2 * S.B.wall - 2) / 2 + S.B.window_margin + ob.xmax) / 2
    section_line(msp, to(xb, 0)[0], to(0, ob.ymin)[1], to(0, ob.ymin + L)[1], "B")
    dfaces = section_faces(housing, ob.ymin + L, xb)
    dx, dy = 305.0, 232.0
    if dfaces:
        db = cq.Compound.makeCompound(dfaces).BoundingBox()
        dc = ((db.ymin + db.ymax) / 2, (db.zmin + db.zmax) / 2)
        g = view_map((dx, dy), dc, k)
        dm: Map = lambda q: g(q.y, q.z)
        add_hatched(msp, dfaces, dm, k, pscale=0.5)
        view_label(msp, "SECTION B-B (BOTTOM EDGE)", (dx, g(0, db.zmin)[1] - 12), "SCALE 5:1")
        z0, z1 = S.B.suction, t
        ytop = db.ymax
        dim(msp, g(ytop, z0), g(ytop, z1), (g(ytop, 0)[0] + 10, 0), 90, lfac=1 / k)
        dim(msp, g(ytop, z1 - S.B.skin), g(ytop, z1), (g(ytop, 0)[0] + 20, 0), 90, f"{S.B.skin:.2f} SKIN", lfac=1 / k)
        dim(msp, g(db.ymin, z1), g(db.ymin + S.B.wall, z1), (0, g(0, z1)[1] + 8), 0, f"{S.B.wall:.2f} WALL", lfac=1 / k)
        text(msp, "PHONE SIDE (BASE PLATE ITEM 3 BONDS HERE)", (g(ob.ymin, 0)[0], g(0, z0)[1] - 6), 2.0)
    # Isometric
    iso_scale = 0.6
    _, ib = draw_view(msp, housing, ISO, (330.0, 130.0), iso_scale, hidden=False)
    view_label(msp, "ISOMETRIC", (330.0, ib[1] - 4), "SCALE 3:5")

    sheet_frame(msp, TitleInfo(
        title=f"{S.STYLE_TITLES[s.name].upper()} - {p.name.upper()}",
        subtitle="KHENSU SHELL - HOUSING",
        dwg_no=dwg, material="TI-6AL-4V GR5",
        finish="BEAD BLAST, SPACE GRAY PVD",
        scale="1:1", mass=f"{S.volume_cm3(parts['housing']) * S.DENSITY['ti_gr5']:.1f} G", sheet=sheet,
    ), HOUSING_NOTES)
    return doc


def assembly_sheet(p: S.Phone, s: S.Style, parts: dict, dwg: str, sheet: str) -> ezdxf.document.Drawing:
    doc = new_doc()
    msp = doc.modelspace()
    solids = [v for k, w in parts.items() if k != "antenna_keepout" for v in w.solids().vals()]
    asm = cq.Compound.makeCompound(solids)
    ob = s.outline.val().BoundingBox()

    fx, fy = 75.0, 178.0
    f, fb = draw_view(msp, asm, FRONT, (fx, fy), 1.0, hidden=True)
    view_label(msp, "FRONT, INTERNALS HIDDEN", (fx, fb[1] - 13))
    dim(msp, f(ob.xmin, ob.ymax), f(ob.xmax, ob.ymax), (fx, fb[3] + 12))
    dim(msp, f(ob.xmin, ob.ymin), f(ob.xmin, ob.ymax), (fb[0] - 9, fy), 90)
    cx, cy = s.magsafe_center
    center_mark(msp, f(cx, cy), 30)
    ring_od = parts["magnet_ring"].val().BoundingBox().xlen
    dim_d(msp, f(cx, cy), ring_od / 2, 140, text_="<> MAGNET RING")
    section_line(msp, f(cx, cy)[0], fb[1], fb[3])

    rx = fb[2] + 28
    _, rb = draw_view(msp, asm, RIGHT, (rx, fy), 1.0, hidden=False)
    view_label(msp, "RIGHT", (rx, rb[1] - 13))
    dim(msp, (rb[0], rb[3]), (rb[2], rb[3]), ((rb[0] + rb[2]) / 2, rb[3] + 8), 0, f"{s.thickness:.2f}")
    if s.usb_c:
        text(msp, "USB-C", (rx + 4, rb[1] + 2), 2.0)

    # Detail C: section A-A through the bottom 60 mm, 3:1, every part hatched
    k = 3.0
    L = 60.0
    dx, dy = 300.0, 112.0
    patterns = [("ANSI31", 0), ("ANSI31", 90), ("ANSI37", 0), ("ANSI31", 45), ("ANSI31", 0),
                ("ANSI32", 0), ("ANSI31", 90), ("ANSI33", 0), ("ANSI31", 0), ("ANSI31", 0)]
    allfaces: list[tuple[int, list[cq.Face]]] = []
    for item, key, *_ in BOM:
        if key and key in parts:
            fs = [fc for sol in parts[key].solids().vals() for fc in section_faces(sol, ob.ymin + L)]
            if fs:
                allfaces.append((item, fs))
    if allfaces:
        db = cq.Compound.makeCompound([fc for _, fs in allfaces for fc in fs]).BoundingBox()
        dc = ((db.ymin + db.ymax) / 2, (db.zmin + db.zmax) / 2)
        g = view_map((dx, dy), dc, k)
        dm: Map = lambda q: g(q.y, q.z)
        top = g(0, db.zmax)[1]
        bot = g(0, db.zmin)[1]
        placed = []
        for item, fs in allfaces:
            pat, ang = patterns[(item - 1) % len(patterns)]
            thin = max(fc.BoundingBox().zlen for fc in fs) < 0.65
            add_hatched(msp, fs, dm, k, pattern=pat, pscale=0.3, angle=ang, solid=thin)
            big = max(fs, key=lambda fc: fc.Area())
            c = big.Center()
            placed.append((item, dm(c)))
        placed.sort(key=lambda v: v[1][0])
        n = len(placed)
        x_lo, x_hi = g(db.ymin, 0)[0], g(db.ymax, 0)[0]
        for i, (item, tgt) in enumerate(placed):
            bx = x_lo + (x_hi - x_lo) * (i + 0.5) / n
            up = i % 2 == 0
            balloon(msp, item, tgt, (bx, top + 12 if up else bot - 12))
        dim(msp, g(db.ymax, db.zmin), g(db.ymax, db.zmax), (x_hi + 10, 0), 90, lfac=1 / k)
        view_label(msp, "DETAIL C (SECTION A-A, BOTTOM 60 MM)", (dx, bot - 20), "SCALE 3:1")

    # Parts list
    bx0, by0 = 240.0, 200.0
    widths = [10, 58, 58, 44]
    heads = ["ITEM", "DESCRIPTION", "MATERIAL / SPEC", "PROCESS"]
    rowh = 6.0
    rows = [r for r in BOM if r[1] is None or r[1] in parts]
    if not s.usb_c:
        rows = [r for r in rows if r[0] != 10]
    y = by0 + rowh * (len(rows) + 1)
    x1 = bx0 + sum(widths)
    rect(msp, bx0, by0, x1, y, "TITLE")
    xs = [bx0]
    for w in widths:
        xs.append(xs[-1] + w)
    for xv in xs[1:-1]:
        line(msp, (xv, by0), (xv, y), "TITLE")
    for i, h in enumerate(heads):
        text(msp, h, (xs[i] + 1.2, y - rowh + 1.8), 2.0)
    for r_i, (item, _, desc, mat, proc) in enumerate(rows):
        yy = y - rowh * (r_i + 2)
        line(msp, (bx0, yy + rowh), (x1, yy + rowh), "TITLE")
        for i, v in enumerate([str(item), desc, mat, proc]):
            text(msp, v, (xs[i] + 1.2, yy + 1.8), 1.8)
    text(msp, "PARTS LIST", (bx0, y + 2), 3.0)

    res = {
        "battery": f"{S.volume_cm3(parts['battery']) * S.B.wh_per_cm3:.1f} WH ({S.volume_cm3(parts['battery']):.1f} CM3)",
    }
    text(msp, f"CELL VOLUME {res['battery']} AT 0.45 WH/CM3.  THICKNESS {s.thickness:.2f} ON THE PHONE BACK.",
         (bx0, by0 - 6), 2.0)

    sheet_frame(msp, TitleInfo(
        title=f"{S.STYLE_TITLES[s.name].upper()} - {p.name.upper()}",
        subtitle="KHENSU SHELL - ASSEMBLY",
        dwg_no=dwg, material="SEE PARTS LIST", finish="SEE -101",
        scale="1:1", mass=mass_str(parts, S.DENSITY["ti_gr5"]), sheet=sheet,
    ), ASSEMBLY_NOTES)
    return doc


def case_sheet(p: S.Phone, module_t: float, dwg: str, sheet: str) -> ezdxf.document.Drawing:
    doc = new_doc()
    msp = doc.modelspace()
    case_w = S.build_case(p, module_t)
    case = case_w.val()
    bb = case.BoundingBox()

    fx, fy = 80.0, 178.0
    f, fb = draw_view(msp, case, FRONT, (fx, fy), 1.0, hidden=False)
    view_label(msp, "BACK", (fx, fb[1] - 13))
    dim(msp, (fb[0], fb[3]), (fb[2], fb[3]), (fx, fb[3] + 8))
    dim(msp, (fb[0], fb[1]), (fb[0], fb[3]), (fb[0] - 9, fy), 90)
    bx, by, bw, bh = p.bump_rect()
    ow, oh = bw + 1.6, bh + 1.6
    c0 = f(bx, by)
    dim(msp, (c0[0] - ow / 2, c0[1] - oh / 2), (c0[0] + ow / 2, c0[1] - oh / 2), (c0[0], c0[1] - oh / 2 - 5), 0, "<> %%p0.10")
    dim(msp, (c0[0] + ow / 2, c0[1] - oh / 2), (c0[0] + ow / 2, c0[1] + oh / 2), (c0[0] + ow / 2 + 6, c0[1]), 90, "<> %%p0.10")
    text(msp, "CAMERA OPENING, R%.1f CORNERS" % (p.bump_r + 0.8), (c0[0] - ow / 2, c0[1] - oh / 2 - 13), 2.0)
    section_line(msp, f(0, 0)[0], fb[1], fb[3])

    rx = fb[2] + 30
    _, rb = draw_view(msp, case, RIGHT, (rx, fy), 1.0, hidden=True)
    view_label(msp, "RIGHT", (rx, rb[1] - 13))
    dim(msp, (rb[0], rb[3]), (rb[2], rb[3]), ((rb[0] + rb[2]) / 2, rb[3] + 8))

    k = 4.0
    dfaces = section_faces(case, bb.ymin + 14)
    dx, dy = 320.0, 225.0
    if dfaces:
        db = cq.Compound.makeCompound(dfaces).BoundingBox()
        g = view_map((dx, dy), ((db.ymin + db.ymax) / 2, (db.zmin + db.zmax) / 2), k)
        add_hatched(msp, dfaces, lambda q: g(q.y, q.z), k, pattern="ANSI37", pscale=0.5)
        view_label(msp, "DETAIL B (SECTION A-A AT BOTTOM)", (dx, g(0, db.zmin)[1] - 10), "SCALE 4:1")
        text(msp, "WALL 1.60  /  FRONT LIP 1.00  /  BACK SKIN 0.80", (g(db.ymin, 0)[0], g(0, db.zmax)[1] + 6), 2.2)
    _, ib = draw_view(msp, case, ISO, (320.0, 120.0), 0.6, hidden=False)
    view_label(msp, "ISOMETRIC", (320.0, ib[1] - 4), "SCALE 3:5")

    sheet_frame(msp, TitleInfo(
        title=f"SILICONE SHOCK CASE - {p.name.upper()}",
        subtitle="KHENSU SHELL - CASE",
        dwg_no=dwg, material="LSR, SHORE 55A", finish="MATTE TEXTURE (VDI 27)",
        scale="1:1", mass=f"{S.volume_cm3(case_w) * 1.12:.0f} G", sheet=sheet,
    ), CASE_NOTES)
    return doc


# ---------- output ----------

def render(doc, pdf: PdfPages, png: Path | None = None):
    fig = plt.figure(figsize=(SHEET_W / 25.4, SHEET_H / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    cfg = Configuration(
        background_policy=BackgroundPolicy.WHITE,
        color_policy=ColorPolicy.BLACK,
        lineweight_policy=LineweightPolicy.ABSOLUTE,
        lineweight_scaling=0.8,
    )
    Frontend(RenderContext(doc), MatplotlibBackend(ax), config=cfg).draw_layout(doc.modelspace(), finalize=True)
    ax.set_xlim(0, SHEET_W)
    ax.set_ylim(0, SHEET_H)
    ax.set_aspect("equal")
    ax.axis("off")
    pdf.savefig(fig)
    if png:
        fig.savefig(png, dpi=160)
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    jobs = []
    for p in S.PHONES:
        styles = [s for s in S.styles_for(p)]
        for s in styles:
            jobs.append(("asm", p, s))
            jobs.append(("housing", p, s))
        jobs.append(("case", p, next(s for s in styles if s.name == "wrap")))
    total = len(jobs)
    with PdfPages(OUT / "khensu-shell-drawings.pdf") as pdf:
        for i, (kind, p, s) in enumerate(jobs, 1):
            sheet = f"{i} OF {total}"
            if kind == "case":
                dwg = f"KS-{p.name.upper()}-CASE-201"
                doc = case_sheet(p, s.thickness, dwg, sheet)
            else:
                parts = S.build_shell(p, s)
                dwg = f"KS-{p.name.upper()}-{s.name.upper()}-{100 if kind == 'asm' else 101}"
                doc = (assembly_sheet if kind == "asm" else housing_sheet)(p, s, parts, dwg, sheet)
            path = OUT / p.name / f"{dwg}.dxf"
            path.parent.mkdir(parents=True, exist_ok=True)
            doc.saveas(path)
            render(doc, pdf, OUT / p.name / f"{dwg}.png")
            print(f"{sheet}: {path.relative_to(OUT.parent)}")


if __name__ == "__main__":
    main()
