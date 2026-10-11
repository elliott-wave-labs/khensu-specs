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
    bump_z: float  # camera plateau height above the back
    magsafe_y: float  # MagSafe centre, from the centre of the back
    lens_z: float = 0.0  # top of the lens rings above the back; the slim styles finish level with it
    # (name, x, y, radius, top z, half field of view in degrees) relative to the plateau's top-left
    # corner (+x right, +y down). A half angle of 0 marks a port that must stay open but has no cone.
    sensors: tuple[tuple[str, float, float, float, float, float], ...] = ()

    def bump_rect(self) -> tuple[float, float, float, float]:
        """Bump as (cx, cy, w, h) in back coordinates."""
        cx = -self.width / 2 + self.bump_x0 + self.bump_w / 2
        cy = self.height / 2 - self.bump_y0 - self.bump_h / 2
        return cx, cy, self.bump_w, self.bump_h

    def bump_bottom(self) -> float:
        return self.height / 2 - self.bump_y0 - self.bump_h

    def full_width_bump(self) -> bool:
        return self.bump_w >= self.width - 0.01

    def sensor_list(self) -> list[tuple[str, float, float, float, float, float]]:
        """Sensors in back coordinates: (name, x, y, radius, top z, half field of view)."""
        bx, by, bw, bh = self.bump_rect()
        left, top = bx - bw / 2, by + bh / 2
        return [(n, left + x, top - y, r, z, fov) for n, x, y, r, z, fov in self.sensors]


PHONES = [
    # iPhone 18 Pro: an aluminium camera plateau across the full width of the top, as on apple.com.
    # Placeholder geometry until Apple's accessory drawings replace it.
    Phone(
        "iphone-18-pro", 71.9, 150.0, 8.75, 10.0, 0.0, 0.0, 71.9, 43.0, 10.0, 2.0, -5.0, lens_z=4.2,
        sensors=(
            ("wide", 14.7, 14.7, 7.6, 4.2, 42.0),
            ("ultra wide", 14.7, 32.3, 7.6, 4.2, 60.0),
            ("telephoto", 29.9, 23.5, 7.6, 4.2, 20.0),
            ("flash", 58.0, 15.5, 2.8, 2.0, 60.0),
            ("lidar", 58.0, 31.5, 3.6, 2.0, 40.0),
            ("microphone", 63.9, 23.5, 0.6, 2.0, 0.0),
        ),
    ),
    # Standard-size phone with a square camera island at the top left.
    Phone(
        "island", 71.5, 147.6, 7.8, 10.0, 4.5, 4.5, 38.0, 38.0, 8.0, 2.6, 0.0, lens_z=3.6,
        sensors=(
            ("wide", 10.5, 10.5, 7.0, 3.6, 42.0),
            ("ultra wide", 10.5, 27.5, 7.0, 3.6, 60.0),
            ("flash", 28.5, 10.5, 2.5, 2.6, 60.0),
            ("microphone", 28.5, 19.0, 0.6, 2.6, 0.0),
            ("lidar", 28.5, 27.5, 3.0, 2.6, 40.0),
        ),
    ),
]


@dataclass
class Build:
    wall: float = 1.0  # side walls (CNC titanium)
    skin: float = 0.7  # outer face
    base: float = 0.4  # phone-side plate (glass-filled PC), closes the cavity
    # Phone side: microcellular urethane (PORON XRD class) with a micro-suction face. It holds the
    # shell on and is the shock isolator: in a back or edge impact it lets the shell's mass decelerate
    # over the layer's stroke instead of hammering the phone's glass through a rigid contact.
    suction: float = 0.5
    gap: float = 0.6  # clearance to the camera bump
    fov_margin: float = 0.3  # extra clearance past each sensor's field-of-view cone
    plate_clear: float = 0.1  # between the plateau top and the underside of the camera plate
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
    plate: bool = False  # covers the camera plateau, with an opening per sensor, for a flat back


def rounded_rect(w: float, h: float, r: float, cx: float = 0, cy: float = 0) -> cq.Workplane:
    r = min(r, w / 2 - 0.01, h / 2 - 0.01)
    return cq.Workplane("XY").center(cx, cy).rect(w, h).extrude(1).edges("|Z").fillet(r)


def plateau_outline(p: Phone, grow: float = 0.0) -> cq.Workplane:
    """The camera plateau's outline grown by `grow`. A full-width plateau follows the phone's own top
    corners and meets its sides square at the bottom."""
    if not p.full_width_bump():
        bx, by, bw, bh = p.bump_rect()
        return rounded_rect(bw + 2 * grow, bh + 2 * grow, p.bump_r + grow, bx, by)
    top = p.height / 2 + grow
    bottom = p.bump_bottom() - grow
    band = cq.Workplane("XY").center(0, (top + bottom) / 2).rect(p.width + 2 * grow + 2, top - bottom).extrude(1)
    return rounded_rect(p.width + 2 * grow, p.height + 2 * grow, p.corner_r + grow).intersect(band)


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
    bump_cut = plateau_outline(p, B.gap)

    # Card: Pocket-sized, 86 x 56 x 5.2 mm, centred on MagSafe but kept clear of the bump.
    card_w, card_h, card_t = 56.0, 86.0, 5.2
    card_cy = min(p.magsafe_y, bottom_of_bump - card_h / 2 - 1.5)
    card = rounded_rect(card_w, card_h, 8.0, 0, card_cy)

    # Fill: inset from the phone's edges, over the camera plateau too, so the back is flat.
    margin_side, margin_bottom = 3.0, 4.0
    fill_top = p.height / 2 - margin_side
    fill_bot = -p.height / 2 + margin_bottom
    fill_h = fill_top - fill_bot
    fill = rounded_rect(p.width - 2 * margin_side, fill_h, p.corner_r - margin_side, 0, fill_bot + fill_h / 2)

    # Wrap XL: the whole back around the bump (the camera sits in a drafted well).
    if bw + 2 * B.gap >= p.width - 2 * B.edge_inset - 2 * B.wall:
        # Full-width plateau: everything below it, with square top corners against the straight phone sides.
        bot = -p.height / 2 + B.edge_inset
        h = bottom_of_bump - bot
        wrap = rounded_rect(p.width - 2 * B.edge_inset, h, 1.0, 0, bot + h / 2).intersect(body)
    else:
        wrap = body.cut(bump_cut)

    # Level with the lens rings, so the back reads as one flat surface with no camera bump.
    slim_t = max(p.lens_z, p.bump_z, min_slim_thickness())
    return [
        Style("card", "Pocket-style card on MagSafe, own battery only", card_t, card, False, (0, p.magsafe_y)),
        Style("fill", "Inset from the edges, over the camera: a flat back level with the lenses", slim_t, fill, True, (0, p.magsafe_y), plate=True),
        Style("wrap", "The whole back, over the camera: a flat back level with the lenses", slim_t, body, True, (0, p.magsafe_y), plate=True),
        Style("wrap-xl", "Large-capacity wrap, flat back 3 mm above the lenses in a drafted well", slim_t + 3.0, wrap, True, (0, p.magsafe_y)),
    ]


def camera_draft(p: Phone, t: float, gap: float = B.gap) -> float:
    """How far the camera opening must widen from the plateau top to the shell's top face so no
    sensor's field of view touches the wall. Zero when the shell finishes level with the lenses."""
    bx, by, bw, bh = p.bump_rect()
    x0, x1, y0, y1 = bx - bw / 2 - gap, bx + bw / 2 + gap, by - bh / 2 - gap, by + bh / 2 + gap
    need = 0.0
    for _, x, y, r, z, fov in p.sensor_list():
        h = t - z
        if fov <= 0 or h <= 0:
            continue
        d = min(x - r - x0, x1 - x - r, y - r - y0, y1 - y - r)
        need = max(need, h * math.tan(math.radians(fov)) + B.fov_margin - d)
    return max(0.0, need)


def check_sensors(p: Phone, s: Style, housing: cq.Workplane) -> None:
    """Raise if the housing touches any sensor, or enters a field-of-view cone, with 0.2 mm to spare."""
    t = s.thickness
    for name, x, y, r, z, fov in p.sensor_list():
        rr = r + 0.2
        column = cq.Solid.makeCylinder(rr, max(z - p.bump_z, 0.01), cq.Vector(x, y, p.bump_z))
        h = t + 1.0 - z
        cone = (cq.Solid.makeCone(rr, rr + h * math.tan(math.radians(fov)), h, cq.Vector(x, y, z))
                if fov > 0 else cq.Solid.makeCylinder(rr, h, cq.Vector(x, y, z)))
        keepout = cq.Workplane("XY").add(column).union(cq.Workplane("XY").add(cone))
        try:
            hit = volume_cm3(housing.intersect(keepout)) * 1000.0
        except ValueError:
            hit = 0.0
        if hit > 1e-3:
            raise ValueError(f"{p.name}/{s.name}: shell blocks the {name} ({hit:.3f} mm3)")


def sensor_opening(p: Phone, t: float, x: float, y: float, r: float, z: float, fov: float) -> cq.Workplane:
    """Opening through the camera plate: 0.6 mm round the sensor, widening with height so the wall
    stays outside its field of view."""
    rb = r + B.gap
    h = t - z
    rise = t - p.bump_z
    slope = (h * math.tan(math.radians(fov)) + B.fov_margin) / rise if fov > 0 and h > 0 else 0.0
    z0, z1 = p.bump_z - 0.5, t + 0.5
    rt = rb + slope * (z1 - p.bump_z)
    r0 = rb - slope * 0.5
    solid = (cq.Solid.makeCone(r0, rt, z1 - z0, cq.Vector(x, y, z0)) if slope > 0
             else cq.Solid.makeCylinder(rb, z1 - z0, cq.Vector(x, y, z0)))
    return cq.Workplane("XY").add(solid)


def min_slim_thickness() -> float:
    """Thinnest shell that still fits the board: film, base, PCB, clearance, skin."""
    return B.suction + B.base + B.pcb_t + 0.2 + B.skin


def build_shell(p: Phone, s: Style) -> dict[str, cq.Workplane]:
    t = s.thickness
    stack_bottom = B.suction + B.base  # phone side of the cavity
    envelope = outline_solid(s.outline, B.suction, t - B.suction)
    # A crisp edge, like the phone's own, so the flat back reads flat.
    edge_fillet = min(0.8 if s.plate else 1.2, (t - B.suction) * 0.45)
    try:
        envelope = envelope.faces(">Z").edges().fillet(edge_fillet)
    except Exception:
        pass

    inner = offset_outline(s.outline, -B.wall)
    bx, by, bw, bh = p.bump_rect()
    draft = camera_draft(p, t) if s.name != "card" else 0.0
    # Solid titanium around the camera opening: no cells in the thin rails, and room for the draft.
    ring = B.gap + draft + B.wall
    keepout = plateau_outline(p, ring)
    if s.name != "card":
        inner = inner.cut(keepout)
        inner = cq.Workplane("XY").add(max(inner.solids().vals(), key=lambda v: v.Volume()))
        inner = offset_outline(offset_outline(inner, -0.5), 0.5)  # drop slivers under 1 mm wide
    cavity = outline_solid(inner, B.suction, t - B.skin - B.suction)
    housing = envelope.cut(cavity)
    pocket = None
    if s.plate:
        # The plateau sits in a pocket under a plate level with the lens rings; each sensor gets its own opening.
        g = B.gap
        pocket = outline_solid(plateau_outline(p, g), -1.0, p.bump_z + B.plate_clear + 1.0)
        housing = housing.cut(pocket)
        for _, x, y, r, z, fov in p.sensor_list():
            housing = housing.cut(sensor_opening(p, t, x, y, r, z, fov))
    if draft > 0:
        # Widen the opening above the plateau so the wall stays outside every field-of-view cone.
        def wire(grow: float, z: float) -> cq.Wire:
            g = B.gap + grow
            return plateau_outline(p, g).faces("<Z").wires().val().translate((0, 0, z))
        slope = draft / (t - p.bump_z)
        well = cq.Solid.makeLoft([wire(0.0, p.bump_z), wire(slope * (t + 1 - p.bump_z), t + 1)])
        housing = housing.cut(cq.Workplane("XY").add(well))

    base = outline_solid(offset_outline(inner, -0.05), B.suction, B.base)
    film = outline_solid(s.outline, 0, B.suction)
    if pocket is not None:
        film = film.cut(pocket)

    cx, cy = s.magsafe_center
    inner_w = inner.val().BoundingBox().xlen
    ring_od = min(B.magnet_od, inner_w - 1.0)
    ring_id = ring_od - (B.magnet_od - B.magnet_id)
    magnets = (
        cq.Workplane("XY").center(cx, cy).circle(ring_od / 2).circle(ring_id / 2).extrude(B.magnet_t)
        .translate((0, 0, stack_bottom))
    )
    coil_z = t - B.skin - B.coil_t
    # The flat-back styles are one unbroken metal face, which a Qi2 coil can't see through; they charge
    # over USB-C. Only the card, which has no plug, keeps a coil behind a window.
    has_coil = coil_z >= stack_bottom + B.magnet_t + 0.1 and not s.plate
    if not has_coil:
        coil_z = t - B.skin
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

    # Metal blocks radio and wireless charging. Flat-back styles: a PC antenna band in the bottom wall only,
    # like the bands on a phone's frame, so the outer face stays unbroken metal. Others: PC windows through
    # the skin and bottom wall over the antenna, and through the skin over the coil.
    bb = s.outline.val().BoundingBox()
    ant_w = min(B.antenna_l, inner_bb.xlen - 2) + 2 * B.window_margin
    if s.plate:
        ant_window = (
            cq.Workplane("XY").center(0, (bb.ymin - 1 + inner_bb.ymin + 0.3) / 2)
            .rect(ant_w, inner_bb.ymin + 0.3 - (bb.ymin - 1))
            .extrude(t - B.skin - stack_bottom).translate((0, 0, stack_bottom))
        )
    else:
        win_top = inner_bb.ymin + B.antenna_w + 0.5 + B.window_margin
        ant_window = (
            cq.Workplane("XY")
            .center(0, (bb.ymin - 1 + win_top) / 2)
            .rect(ant_w, win_top - (bb.ymin - 1))
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
            cq.Workplane("XZ").center(0, B.suction + (t - B.suction) / 2).slot2D(B.usb_w, min(B.usb_h, t - 1.2))
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
    camera = outline_solid(plateau_outline(p, 0.8), 0, z1 + 1)
    return case.cut(phone_body).cut(front_opening).cut(camera)


@dataclass
class Armor:
    liner: float = 0.6  # PORON XRD class urethane between the phone's sides and the frame
    frame: float = 1.2  # titanium or brass side rails
    lip: float = 0.8  # raised rim in front of the screen glass, so a face-down drop lands on the rim
    overlap: float = 0.8  # how far the rim reaches over the screen's black border
    corner: float = 13.0  # composite corner bumpers: impact zones, and RF-clear over the phone's antenna lines
    rail: float = 1.2  # metal kept above and below each side opening
    button_margin: float = 1.5  # open clearance round each button, no caps
    bottom_open: float = 52.0  # speaker, microphone and USB-C opening in the bottom edge
    earpiece_open: float = 26.0  # rim notch over the earpiece speaker and front microphone


A = Armor()

# Side controls, placeholder positions until Apple's accessory drawings: (side, centre from the top, length).
# Back coordinates: +x is the phone's left edge seen from the front.
CONTROLS = {
    "iphone-18-pro": (
        ("+x", 33.0, 6.5),  # Action button
        ("+x", 47.0, 10.0),  # volume up
        ("+x", 60.0, 10.0),  # volume down
        ("-x", 43.0, 17.0),  # side button
        ("-x", 103.0, 19.0),  # Camera Control: pressed and slid, so its opening stays fully open
    ),
}


def build_armor(p: Phone, t: float) -> dict[str, cq.Workplane]:
    """Edge frame that, with the wrap on the back, encloses the whole phone: metal side rails, composite
    corner bumpers over a urethane liner, a rim proud of the screen, and open cut-outs for every control,
    speaker, microphone and port."""
    grow = A.liner + A.frame
    outer = rounded_rect(p.width + 2 * grow, p.height + 2 * grow, p.corner_r + grow)
    z_front = -p.depth - A.lip
    shell = outline_solid(outer, z_front, t - z_front)
    try:
        shell = shell.edges("|Z").fillet(0.01).faces(">Z or <Z").edges().fillet(0.8)
    except Exception:
        pass
    phone_side = rounded_rect(p.width + 2 * A.liner, p.height + 2 * A.liner, p.corner_r + A.liner)
    phone = rounded_rect(p.width, p.height, p.corner_r)
    wrap_clear = rounded_rect(p.width - 2 * B.edge_inset + 0.2, p.height - 2 * B.edge_inset + 0.2, p.corner_r - B.edge_inset + 0.1)
    window = rounded_rect(p.width - 2 * A.overlap, p.height - 2 * A.overlap, p.corner_r - A.overlap)
    shell = (
        shell.cut(outline_solid(phone_side, -p.depth - 0.3, p.depth + 0.3))
        .cut(outline_solid(wrap_clear, -0.01, t + 1))
        .cut(outline_solid(plateau_outline(p, A.liner), -0.01, p.bump_z + 0.31))
        .cut(outline_solid(window, z_front - 1, A.lip + 1.0))
    )
    liner = (
        outline_solid(phone_side, -p.depth - 0.3, p.depth + 0.3)
        .cut(outline_solid(phone, -p.depth, p.depth + 1))
        .cut(outline_solid(window, -p.depth - 1, 1.0))
    )

    # Open cut-outs through the frame and liner.
    w2, h2 = p.width / 2 + grow + 1, p.height / 2
    zc, zh = -p.depth / 2, p.depth - 2 * A.rail
    for side, from_top, length in CONTROLS.get(p.name, ()):
        x = w2 - (grow + 1) / 2 if side == "+x" else -w2 + (grow + 1) / 2
        cut = cq.Workplane("XY").box(grow + 1.2, length + 2 * A.button_margin, zh).translate((x, h2 - from_top, zc))
        shell, liner = shell.cut(cut), liner.cut(cut)
    bottom = cq.Workplane("XY").box(A.bottom_open, grow + 1.2, zh).translate((0, -h2 - (grow + 1) / 2 + 0.5, zc))
    shell, liner = shell.cut(bottom), liner.cut(bottom)
    # The earpiece speaker and front microphone sit in the slot along the top of the glass: no rim over
    # them, so the rim forms no cavity in front of either and Spatial Audio and voice pickup are unchanged.
    earpiece = cq.Workplane("XY").box(A.earpiece_open, A.overlap + grow + 4.0, A.lip + 0.31).translate(
        (0, h2 + (grow + 4.0 - A.overlap) / 2, z_front + (A.lip + 0.31) / 2 - 0.01))
    shell, liner = shell.cut(earpiece), liner.cut(earpiece)

    corners = None
    for sx in (-1, 1):
        for sy in (-1, 1):
            box = cq.Workplane("XY").box(A.corner + grow, A.corner + grow, 40).translate(
                (sx * (p.width / 2 + grow - (A.corner + grow) / 2), sy * (p.height / 2 + grow - (A.corner + grow) / 2), 0))
            corners = box if corners is None else corners.union(box)
    bumpers = shell.intersect(corners)
    rails = shell.cut(corners)
    return {"frame": rails, "corner_bumpers": bumpers, "liner": liner}


def phone_reference(p: Phone) -> cq.Workplane:
    body = outline_solid(rounded_rect(p.width, p.height, p.corner_r), -p.depth, p.depth)
    bump = outline_solid(plateau_outline(p), 0, p.bump_z)
    body = body.union(bump)
    for name, x, y, r, z, _ in p.sensor_list():
        if z > p.bump_z:
            body = body.union(cq.Workplane("XY").center(x, y).circle(r).extrude(z - p.bump_z).translate((0, 0, p.bump_z)))
    return body


DENSITY = {  # g/cm3
    "ti_gr5": 4.43,
    "brass": 8.53,  # C26000 cartridge brass, 70/30, lead-free
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
            check_sensors(p, s, parts["housing"])
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
                "above_lenses_mm": round(max(0.0, s.thickness - p.lens_z), 2),
                "camera_draft_mm": round(camera_draft(p, s.thickness) if s.name != "card" else 0.0, 2),
                "camera": "plate with sensor openings" if s.plate else ("drafted well" if s.name != "card" else "clear of the camera"),
                "mass_g_titanium": round(mass_g(parts, DENSITY["ti_gr5"]), 0),
                "mass_g_brass": round(mass_g(parts, DENSITY["brass"]), 0),
            })
            if s.name == "wrap":
                export(build_case(p, s.thickness), OUT / p.name / "case-silicone" / "case")
                armor = build_armor(p, s.thickness)
                for name, part in armor.items():
                    export(part, OUT / p.name / "armor" / name)
                ref = phone_reference(p)
                hits = {k: volume_cm3(v.intersect(ref)) * 1000.0 for k, v in armor.items()}
                hits.update({f"wrap {k}": volume_cm3(armor["frame"].intersect(v)) * 1000.0
                             for k, v in parts.items() if k in ("housing", "suction_film", "base")})
                if max(hits.values()) > 0.5:
                    raise ValueError(f"{p.name}/armor: clash {hits}")
                fb = armor["frame"].union(armor["corner_bumpers"]).val().BoundingBox()
                entry["armor"] = {
                    "footprint_mm": [round(fb.xlen, 1), round(fb.ylen, 1)],
                    "thickness_mm": round(fb.zlen, 2),
                    "rim_above_screen_mm": A.lip,
                    "edge_mm": A.liner + A.frame,
                    "frame_g_titanium": round(volume_cm3(armor["frame"]) * DENSITY["ti_gr5"], 0),
                    "frame_g_brass": round(volume_cm3(armor["frame"]) * DENSITY["brass"], 0),
                    "corners_and_liner_g": round(volume_cm3(armor["corner_bumpers"]) * 1.2 + volume_cm3(armor["liner"]) * 0.5, 0),
                }
        summary["phones"].append(entry)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    for e in summary["phones"]:
        print(e["phone"]["name"])
        for s in e["styles"]:
            print(f"  {s['style']:8} {s['footprint_mm']} x {s['thickness_mm']} mm  battery {s['battery_wh']} Wh  "
                  f"{s['mass_g_titanium']:.0f} g Ti / {s['mass_g_brass']:.0f} g brass  draft {s['camera_draft_mm']} mm  {s['camera']}")


if __name__ == "__main__":
    main()
