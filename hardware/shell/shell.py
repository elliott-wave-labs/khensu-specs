# SPDX-License-Identifier: CC-BY-4.0
"""Parametric CAD for the khensu shell.

Builds every attachment style for each reference phone and writes STEP and STL
files to out/<phone>/<style>/, plus a layout summary (out/summary.json).

Phone dimensions below are placeholders. Before machining or tooling, replace
them with the exact values from Apple's Accessory Design Guidelines drawings
for the target model.

Coordinates: the phone's back is the XY plane at z = 0 and faces +Z; the phone
body occupies z < 0. Origin at the centre of the back. +Y is the top of the
phone. Units are millimetres.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path

import cadquery as cq

OUT = Path(__file__).parent / "out"


@dataclass
class Phone:
    name: str
    width: float
    height: float
    depth: float
    corner_r: float
    bump_x0: float  # camera bump rectangle, from the phone's top-left corner
    bump_y0: float
    bump_w: float
    bump_h: float
    bump_r: float
    bump_z: float  # bump height above the back
    magsafe_y: float  # MagSafe centre, from the centre of the back

    def bump_rect(self) -> tuple[float, float, float, float]:
        """Bump as (cx, cy, w, h) in back coordinates."""
        cx = -self.width / 2 + self.bump_x0 + self.bump_w / 2
        cy = self.height / 2 - self.bump_y0 - self.bump_h / 2
        return cx, cy, self.bump_w, self.bump_h

    def bump_bottom(self) -> float:
        return self.height / 2 - self.bump_y0 - self.bump_h


PHONES = [
    # Pro-size phone with a full-width camera plateau across the top.
    Phone("pro-plateau", 71.9, 150.0, 8.75, 10.0, 0.0, 0.0, 71.9, 44.0, 10.0, 3.5, -5.0),
    # Standard-size phone with a square camera island at the top left.
    Phone("island", 71.5, 147.6, 7.8, 10.0, 4.5, 4.5, 38.0, 38.0, 8.0, 2.6, 0.0),
]


@dataclass
class Build:
    wall: float = 1.0  # side walls (CNC titanium)
    skin: float = 0.7  # outer face
    base: float = 0.6  # phone-side plate (glass-filled PC), closes the cavity
    suction: float = 0.3  # micro-suction film on the phone side
    gap: float = 0.6  # clearance to the camera bump
    edge_inset: float = 0.4  # inset from the phone's outline so the shell never overhangs
    magnet_od: float = 56.0  # MagSafe-compatible magnet ring
    magnet_id: float = 46.0
    magnet_t: float = 0.5
    coil_d: float = 44.0  # outer-face Qi2 receiver coil with ferrite
    coil_t: float = 0.8
    pcb_l: float = 34.0
    pcb_w: float = 14.0
    pcb_t: float = 1.6  # board plus tallest component
    antenna_l: float = 40.0  # sub-GHz HaLow antenna keep-out (non-metal window)
    antenna_w: float = 8.0
    usb_w: float = 9.2  # USB-C receptacle opening
    usb_h: float = 3.4
    coil_window_d: float = 46.0  # PC window in a metal skin over the coil
    window_margin: float = 1.0  # PC window around the antenna keep-out
    wh_per_cm3: float = 0.45  # thin pouch cells, conservative


B = Build()


STYLE_TITLES = {"card": "Card", "fill": "Fill", "wrap": "Wrap", "wrap-xl": "Wrap XL"}


@dataclass
class Style:
    name: str
    description: str
    thickness: float
    outline: cq.Workplane = field(repr=False)
    usb_c: bool
    magsafe_center: tuple[float, float]


def rounded_rect(w: float, h: float, r: float, cx: float = 0, cy: float = 0) -> cq.Workplane:
    r = min(r, w / 2 - 0.01, h / 2 - 0.01)
    return cq.Workplane("XY").center(cx, cy).rect(w, h).extrude(1).edges("|Z").fillet(r)


def outline_solid(outline: cq.Workplane, z0: float, t: float) -> cq.Workplane:
    """Re-extrude a 1 mm outline solid to thickness t starting at z0."""
    face = outline.faces("<Z").val()
    return cq.Workplane("XY").add(cq.Solid.extrudeLinear(face, cq.Vector(0, 0, t))).translate((0, 0, z0))


def offset_outline(outline: cq.Workplane, d: float) -> cq.Workplane:
    """Offset the outer edge by d and grow any holes (the camera cut-out) by -d, keeping the holes."""
    face = outline.faces("<Z").val()

    def slab(wire: cq.Wire, t: float = 1.0) -> cq.Workplane:
        return cq.Workplane("XY").add(cq.Solid.extrudeLinear(cq.Face.makeFromWires(wire), cq.Vector(0, 0, t)))

    result = slab(face.outerWire().offset2D(d, "arc")[0])
    for hole in face.innerWires():
        # offset2D's sign follows wire orientation, so pick the candidate by area.
        candidates = hole.offset2D(d, "arc") + hole.offset2D(-d, "arc")
        pick = max if d < 0 else min
        new_hole = pick(candidates, key=lambda w: cq.Face.makeFromWires(w).Area())
        result = result.cut(slab(new_hole, 3.0).translate((0, 0, -1.0)))
    return result


def styles_for(p: Phone) -> list[Style]:
    bx, by, bw, bh = p.bump_rect()
    bottom_of_bump = p.bump_bottom() - B.gap
    body = rounded_rect(p.width - 2 * B.edge_inset, p.height - 2 * B.edge_inset, p.corner_r - B.edge_inset)
    bump_cut = rounded_rect(bw + 2 * B.gap, bh + 2 * B.gap, p.bump_r + B.gap, bx, by)

    # Card: Pocket-sized, 86 x 56 x 5.2 mm, centred on MagSafe but kept clear of the bump.
    card_w, card_h, card_t = 56.0, 86.0, 5.2
    card_cy = min(p.magsafe_y, bottom_of_bump - card_h / 2 - 1.0)
    card = rounded_rect(card_w, card_h, 8.0, 0, card_cy)

    # Fill: the empty space below the bump, flush with the bump height.
    margin_side, margin_bottom = 3.0, 4.0
    fill_top = bottom_of_bump
    fill_bot = -p.height / 2 + margin_bottom
    fill_h = fill_top - fill_bot
    fill = rounded_rect(p.width - 2 * margin_side, fill_h, p.corner_r - margin_side, 0, fill_bot + fill_h / 2)
    fill = fill.cut(bump_cut)

    # Wrap: the whole back around the bump, flush with the bump height.
    if bw >= p.width - 2 * p.corner_r:
        # Full-width plateau: everything below it, with square top corners against the straight phone sides.
        bot = -p.height / 2 + B.edge_inset
        h = bottom_of_bump - bot
        wrap = rounded_rect(p.width - 2 * B.edge_inset, h, 1.0, 0, bot + h / 2).intersect(body)
    else:
        wrap = body.cut(bump_cut)

    slim_t = max(p.bump_z, min_slim_thickness())
    return [
        Style("card", "Pocket-style card on MagSafe, own battery only", card_t, card, False, (0, p.magsafe_y)),
        Style("fill", "Fills the space below the camera bump, flush with it", slim_t, fill, True, (0, p.magsafe_y)),
        Style("wrap", "Whole back around the camera bump, flush with it", slim_t, wrap, True, (0, p.magsafe_y)),
        Style("wrap-xl", "Large-capacity wrap, 3 mm proud of the bump", slim_t + 3.0, wrap, True, (0, p.magsafe_y)),
    ]


def min_slim_thickness() -> float:
    """Thinnest shell that still fits the board: film, base, PCB, clearance, skin."""
    return B.suction + B.base + B.pcb_t + 0.2 + B.skin


def build_shell(p: Phone, s: Style) -> dict[str, cq.Workplane]:
    t = s.thickness
    stack_bottom = B.suction + B.base  # phone side of the cavity
    envelope = outline_solid(s.outline, B.suction, t - B.suction)
    edge_fillet = min(1.2, (t - B.suction) * 0.45)
    try:
        envelope = envelope.faces(">Z").edges().fillet(edge_fillet)
    except Exception:
        pass

    inner = offset_outline(s.outline, -B.wall)
    cavity = outline_solid(inner, B.suction, t - B.skin - B.suction)
    housing = envelope.cut(cavity)

    base = outline_solid(offset_outline(inner, -0.05), B.suction, B.base)
    film = outline_solid(s.outline, 0, B.suction)

    cx, cy = s.magsafe_center
    inner_w = inner.val().BoundingBox().xlen
    ring_od = min(B.magnet_od, inner_w - 1.0)
    ring_id = ring_od - (B.magnet_od - B.magnet_id)
    magnets = (
        cq.Workplane("XY").center(cx, cy).circle(ring_od / 2).circle(ring_id / 2).extrude(B.magnet_t)
        .translate((0, 0, stack_bottom))
    )
    coil_z = t - B.skin - B.coil_t
    has_coil = coil_z >= stack_bottom + B.magnet_t + 0.1
    if not has_coil:
        coil_z = t - B.skin  # too thin for an outer Qi2 coil; the shell charges over USB-C only
    coil = (
        cq.Workplane("XY").center(cx, cy).circle(B.coil_d / 2).extrude(B.coil_t).translate((0, 0, coil_z))
        if has_coil else None
    )

    # Antenna along the bottom inside edge; PCB above it on the left; battery fills what's left.
    inner_bb = inner.val().BoundingBox()
    ant = (
        cq.Workplane("XY").center(0, inner_bb.ymin + B.antenna_w / 2 + 0.5)
        .rect(min(B.antenna_l, inner_bb.xlen - 2), B.antenna_w).extrude(t - B.skin - stack_bottom)
        .translate((0, 0, stack_bottom))
    )
    pcb_y = inner_bb.ymin + B.antenna_w + 1.5 + B.pcb_w / 2
    pcb_l = min(B.pcb_l, inner_bb.xlen - 2)
    pcb = (
        cq.Workplane("XY").center(inner_bb.xmin + pcb_l / 2 + 1, pcb_y).rect(pcb_l, B.pcb_w)
        .extrude(B.pcb_t).translate((0, 0, stack_bottom))
    )
    # Magnets and coil occupy only the MagSafe circle; the battery fills the rest of the cavity at full height.
    battery_t = t - B.skin - stack_bottom - 0.1
    if battery_t < 0.8:
        raise ValueError(f"{p.name}/{s.name}: {battery_t:.2f} mm left for cells; too thin")
    battery = outline_solid(offset_outline(inner, -0.5), stack_bottom + 0.05, battery_t)
    magsafe_zone = cq.Workplane("XY").center(cx, cy).circle(ring_od / 2 + 1.0).extrude(t + 2).translate((0, 0, -1))
    battery = battery.cut(magsafe_zone)
    stacked_t = coil_z - (stack_bottom + B.magnet_t) - 0.2
    if stacked_t >= 0.8:
        battery = battery.union(
            cq.Workplane("XY").center(cx, cy).circle(ring_od / 2 + 1.0).extrude(stacked_t)
            .translate((0, 0, stack_bottom + B.magnet_t + 0.1))
            .intersect(outline_solid(offset_outline(inner, -0.5), 0, t))
        )
    battery = battery.cut(ant.translate((0, 0, -1))).cut(
        cq.Workplane("XY").center(inner_bb.xmin + pcb_l / 2 + 1, pcb_y).rect(pcb_l + 2, B.pcb_w + 2).extrude(t + 2)
        .translate((0, 0, -1))
    )
    if s.usb_c:
        battery = battery.cut(
            cq.Workplane("XY").center(0, inner_bb.ymin + 6).rect(B.usb_w + 4, 14).extrude(t + 2).translate((0, 0, -1))
        )

    # Metal blocks radio and wireless charging: PC windows over the coil (skin only) and the antenna (skin and bottom wall).
    bb = s.outline.val().BoundingBox()
    win_top = inner_bb.ymin + B.antenna_w + 0.5 + B.window_margin
    ant_window = (
        cq.Workplane("XY")
        .center(0, (bb.ymin - 1 + win_top) / 2)
        .rect(min(B.antenna_l, inner_bb.xlen - 2) + 2 * B.window_margin, win_top - (bb.ymin - 1))
        .extrude(t + 1 - stack_bottom).translate((0, 0, stack_bottom))
    )
    cutter = ant_window
    if has_coil:
        cutter = cutter.union(
            cq.Workplane("XY").center(cx, cy).circle(B.coil_window_d / 2).extrude(B.skin + 1)
            .translate((0, 0, t - B.skin - 0.01))
        )
    inserts = housing.intersect(cutter)
    housing = housing.cut(cutter)

    if s.usb_c:
        port = (
            cq.Workplane("XZ").center(0, B.suction + (t - B.suction) / 2).rect(B.usb_w, min(B.usb_h, t - 1.2))
            .extrude(-6).translate((0, bb.ymin - 1, 0))
        )
        housing = housing.cut(port)
        inserts = inserts.cut(port)

    parts = {
        "housing": housing,
        "window_inserts": inserts,
        "base": base,
        "suction_film": film,
        "magnet_ring": magnets,
        "coil": coil,
        "pcb": pcb,
        "antenna_keepout": ant,
        "battery": battery,
    }
    return {k: v for k, v in parts.items() if v is not None}


def build_case(p: Phone, module_t: float) -> cq.Workplane:
    """Silicone shock case that holds the phone and a wrap module."""
    wall, lip, skin = 1.6, 1.0, 0.8
    outer = rounded_rect(p.width + 2 * wall, p.height + 2 * wall, p.corner_r + wall)
    z0, z1 = -p.depth - 0.8, module_t + skin
    case = outline_solid(outer, z0, z1 - z0)
    try:
        case = case.edges().fillet(1.5)
    except Exception:
        pass
    phone_body = outline_solid(rounded_rect(p.width, p.height, p.corner_r), -p.depth, p.depth + module_t)
    front_opening = outline_solid(rounded_rect(p.width - 2 * lip, p.height - 2 * lip, p.corner_r - lip), z0 - 1, 2.0)
    bx, by, bw, bh = p.bump_rect()
    camera = outline_solid(rounded_rect(bw + 1.6, bh + 1.6, p.bump_r + 0.8, bx, by), 0, z1 + 1)
    return case.cut(phone_body).cut(front_opening).cut(camera)


def phone_reference(p: Phone) -> cq.Workplane:
    body = outline_solid(rounded_rect(p.width, p.height, p.corner_r), -p.depth, p.depth)
    bx, by, bw, bh = p.bump_rect()
    bump = outline_solid(rounded_rect(bw, bh, p.bump_r, bx, by), 0, p.bump_z)
    return body.union(bump)


DENSITY = {  # g/cm3
    "ti_gr5": 4.43,
    "base": 1.45,  # 30% glass-filled PC
    "window_inserts": 1.2,  # PC
    "battery": 2.3,  # pouch cell
    "magnet_ring": 7.5,  # NdFeB
    "coil": 4.0,  # copper and ferrite
    "pcb": 2.5,  # populated board
    "suction_film": 1.1,
}


def mass_g(parts: dict[str, cq.Workplane], housing_density: float) -> float:
    total = volume_cm3(parts["housing"]) * housing_density
    for name, part in parts.items():
        if name in DENSITY:
            total += volume_cm3(part) * DENSITY[name]
    return total


def volume_cm3(w: cq.Workplane) -> float:
    return sum(s.Volume() for s in w.solids().vals()) / 1000.0


def export(w: cq.Workplane, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(w, str(path.with_suffix(".step")))
    cq.exporters.export(w, str(path.with_suffix(".stl")), tolerance=0.02, angularTolerance=0.1)


def main() -> None:
    summary: dict[str, object] = {"build": asdict(B), "phones": []}
    for p in PHONES:
        export(phone_reference(p), OUT / p.name / "phone-reference")
        entry: dict[str, object] = {"phone": asdict(p), "styles": []}
        for s in styles_for(p):
            parts = build_shell(p, s)
            for name, part in parts.items():
                export(part, OUT / p.name / s.name / name)
            bat = volume_cm3(parts["battery"])
            bb = s.outline.val().BoundingBox()
            solid_parts = [k for k in parts if k not in ("suction_film", "antenna_keepout")]
            clash = 0.0
            for i, a in enumerate(solid_parts):
                for b in solid_parts[i + 1:]:
                    try:
                        clash += volume_cm3(parts[a].intersect(parts[b])) * 1000.0
                    except ValueError:
                        pass  # disjoint parts give a null shape
            for name, part in parts.items():
                if not all(sol.isValid() for sol in part.solids().vals()):
                    raise ValueError(f"{p.name}/{s.name}/{name}: invalid solid")
            if clash > 0.5:
                raise ValueError(f"{p.name}/{s.name}: parts overlap by {clash:.1f} mm3")
            entry["styles"].append({
                "style": s.name,
                "description": s.description,
                "footprint_mm": [round(bb.xlen, 1), round(bb.ylen, 1)],
                "thickness_mm": round(s.thickness, 2),
                "battery_cm3": round(bat, 2),
                "battery_wh": round(bat * B.wh_per_cm3, 1),
                "housing_cm3": round(volume_cm3(parts["housing"]), 2),
                "usb_c_to_phone": s.usb_c,
                "magnet_ring_od_mm": round(volume_cm3(parts["magnet_ring"]) and parts["magnet_ring"].val().BoundingBox().xlen, 1),
                "interference_mm3": round(clash, 2),
                "outer_qi2_coil": "coil" in parts,
                "proud_of_bump_mm": round(max(0.0, s.thickness - p.bump_z), 2),
                "mass_g_titanium": round(mass_g(parts, DENSITY["ti_gr5"]), 0),
            })
            if s.name == "wrap":
                export(build_case(p, s.thickness), OUT / p.name / "case-silicone" / "case")
        summary["phones"].append(entry)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    for e in summary["phones"]:
        print(e["phone"]["name"])
        for s in e["styles"]:
            print(f"  {s['style']:8} {s['footprint_mm']} x {s['thickness_mm']} mm  battery {s['battery_cm3']} cm3 = {s['battery_wh']} Wh")


if __name__ == "__main__":
    main()
