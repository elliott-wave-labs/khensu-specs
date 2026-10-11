# khensu shell: CAD

Parametric CadQuery model of the khensu shell, the mesh node that attaches to the back of a phone. See `design/mesh.md` section 6 for what it does.

```sh
uv run python shell.py      # solids: STEP and STL
uv run python drawings.py   # A3 production drawings: AutoCAD DXF and one PDF
```

The full product specification (variants, materials, electrical, radios, thermal, compliance, test plan, open items) is in `SPEC.md`. Drawings are in `drawings/`: an assembly sheet (-100) and a housing detail sheet (-101) per style and phone, and a case sheet (-201) per phone, all in `drawings/khensu-shell-drawings.pdf`.

This writes STEP (for CAM and tooling) and STL (for prints) to `out/<phone>/<style>/`, and `out/summary.json` with footprint, thickness, battery volume and Wh, mass in titanium, and an interference check. The script fails if any part overlaps another, any solid is invalid, or a style is too thin for its cells.

**Before cutting metal:** the phone dimensions in `PHONES` are placeholders. Replace them with Apple's Accessory Design Guidelines drawings for each target model (outline, corner radius, camera bump outline and height, MagSafe centre), then rerun.

## Styles

| Style | What it is | Attaches by |
| --- | --- | --- |
| `card` | Pocket-size card, 56 × 86 × 5.2 mm, below the bump | MagSafe-compatible magnets (53 mm ring to fit the width) |
| `fill` | Fills the flat area below the camera bump, flush with it | Magnets plus micro-suction |
| `wrap` | Covers the whole back around the bump, flush with it | Magnets plus micro-suction |
| `wrap-xl` | `wrap` 3 mm thicker, for all-day relaying | Magnets plus micro-suction |
| `case-silicone` | Shock case that holds the phone and a `wrap` module | Case grips the phone |

## Part files

| File | Part | Suggested process |
| --- | --- | --- |
| `housing` | Outer skin and side walls (1.0 mm walls, 0.7 mm skin), USB-C opening, window cut-outs | CNC titanium Ti-6Al-4V Grade 5 (the only material) |
| `window_inserts` | PC windows over the coil and along the bottom edge (antennas) | Insert-moulded or bonded PC, flush to the skin |
| `base` | Phone-side plate (0.6 mm) that closes the cavity | Injection-moulded or CNC 30% glass-filled PC |
| `suction_film` | 0.3 mm micro-suction layer | Die-cut nano-suction PU film |
| `magnet_ring` | MagSafe-compatible ring (56/46 mm, 0.5 mm) | Bought-in NdFeB segment ring |
| `coil` | Qi2 receiver coil and ferrite under the skin | Bought-in module |
| `pcb` | Board volume including the tallest part (1.6 mm) | Stand-in for the system-on-module and radios |
| `antenna_keepout` | HaLow antenna area, bottom edge | No metal here: see below |
| `battery` | Space available for cells | Custom pouch cells cut to this shape |
| `phone-reference` | Phone body and bump | For fit checks only |

## CNC notes

- Machine the housing from the outside first (5-axis, or two 3-axis setups), then pocket the cavity. 0.7 mm skin over 60 × 100 mm needs a vacuum fixture or a sacrificial support; 0.8–1.0 mm is safer for a first article.
- **Metal blocks radio and wireless charging.** Titanium blocks both, so cut the skin over `coil` and along `antenna_keepout` into windows filled with PC or glass-filled nylon (insert-moulded or bonded), like the bands on a phone frame. Keep at least 40 mm of non-metal length along the bottom edge for the sub-GHz antenna.
- Inside corner radii in the model are at least 0.5 mm; use a 1 mm end mill for the cavity and leave 0.2 mm radii only where the CAM can reach.
- Bead-blast and PVD the titanium. Mask the inside where the graphite sheet bonds.
- Tolerances for a first article: ±0.05 mm on the outline and bump cutout, ±0.1 mm elsewhere. Bump clearance is 0.6 mm per side.

## Mould notes (silicone shock case)

- Liquid silicone rubber, Shore 50–60A, 1.6 mm walls, 1.0 mm front lip, raised corners for drop protection.
- Add 0.5–1° draft on all walls before tooling; the model has none.
- The model has the camera opening only. Add model-specific button covers, Action button, Camera Control, speaker and microphone holes, and the USB-C opening from Apple's drawings.
- The case grips the phone with a `wrap` module inside, so the module can be ejected without tools.
- A dive version needs a rigid polycarbonate housing with O-ring seals, not silicone.

## Heat

About 1 W while relaying, spread over the back, is a few degrees of rise. Charging is the main heat source. A 25 µm graphite sheet under the skin spreads heat from the board and coil; above a 41 °C skin temperature firmware cuts the charging rate first, then pauses optional work (cache serving, committee duty), and never charges the phone and itself at full rate at the same time. The board is always on and the 2 s tick and cover never change, so heat is managed through charging and optional work only.
