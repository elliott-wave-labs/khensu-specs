# Provisional patent application (draft): suñůlink.shield phone-mounted node accessory

**DRAFT for the inventor and patent counsel. Not filed. Confidential.** Draft 2, 11 October 2026 (draft 1, 10 October 2026). Prepared as a US provisional application for filing through USPTO Patent Center. A non-provisional or PCT application claiming its priority must follow within 12 months of the provisional filing date.

## Filing notes (not part of the application)

- **Everything above the line below is a note to the inventor and counsel and is not filed.** The filing package (`patents/filing/shield/`, never committed) is built from the text below the line: `specification.pdf` and `drawings.pdf` (FIG. 1 to FIG. 9, 9 sheets, generated from the CAD in `hardware/sunu/sunu.py` by `patents/filing/_build/figs_shield.py`), plus `cover-sheet.md`. This draft has not been reviewed by a registered patent practitioner; the claims are the inventor's drafting aid and counsel should rewrite them for the non-provisional.
- **What changed in draft 2.** The only product is now the large-capacity wrap ("wrap-xl"): on iPhone 18 Pro a 71.0 × 105.9 mm body below the full-width camera plateau, 7.68 mm thick (3 mm above the lens tops), with a camera-facing top edge drafted 3.69 mm so that no field of view up to the 120° ultra wide touches it. Draft 2 adds the wrap-xl description and claims (draft derived from each sensor's field of view, body ending below a full-width plateau, battery volume against proud height, the build-time interference check, the node with a hardware guard) and keeps the lens-level face of draft 1 as a further embodiment. Draft 1's example figures (4.2 mm, 6.2 Wh) were for an earlier phone model; on iPhone 18 Pro the lens-level wrap is 4.68 mm and about 7.5 Wh. `hardware/sunu/SPEC.md` still shows the old figures.
- **All numbers are design values computed from the CAD model**, not measurements of built hardware: cell capacity is cell volume × 0.45 Wh/cm³, and masses are housing volume × density. No unit has been made. The phone interface data for iPhone 18 Pro (outline, plateau, lens positions and heights, fields of view) are the inventor's model values and should be checked against Apple's accessory design guidelines before a non-provisional.
- **Inventor:** Justin Elliott Staffer. **Applicant and assignee:** Elliott Wave LLC. Sign an assignment from the inventor to Elliott Wave LLC and record it. Counsel should confirm inventorship (only natural persons who contributed to the conception of a claim; AI tools used in CAD or drafting are not inventors).
- **Public disclosure already made** (from the `khensu-site` git history; times are Pacific, commit times rather than deployment times, so confirm against the hosting provider's deployment log):
  - 10 October 2026, 21:07 to 23:19 (`e7c3504` site created, `9d334ae` titanium shell labels, `0539da7` shell clips onto iPhone with a "+0 mm" side view, `34fbc43` seamless CNC shell, `8d4120c` shell spec page, `eb5c945` named shell hardware, `68d83b1` path-traced renders, shell spec with parts, physics and pairing). Draft 1 also records parts shown on elliottwave.studio on 10 October. This disclosed the **lens-level face**, the exploded layers, the edge antenna band, a node board with a network guard, the shock-isolating layer and phone pairing in general terms.
  - 11 October 2026, 04:23 (`78f1934`, on GitHub `origin/main`): the `/shield` page with a "Wrap XL", "a Wrap 3 mm above the lenses with twice the battery, its camera well angled clear of every field of view" (whole back, 71.1 × 149.2 × 7.2 mm, 13.2 Wh, draft 1.3 mm). This disclosed **the concept of a raised wrap with a camera well drafted clear of the fields of view**.
  - 11 October 2026, 08:54 and later (`fd404ee`, `b32b251`, `a5f8f2e`; **local only, not on GitHub when checked**): the single product, 14 Wh, 71.0 × 105.9 × 7.68 mm, draft 3.69 mm, "top edge angled clear of every field of view… even the ultra wide at 120°", the graphite heat spreader in the section, USB-C and Qi2 charging text. If these were deployed, they disclosed the plateau-terminated body and its numbers.
  - **Apparently not disclosed:** the draft formula (claims 2 and 3), the build-time keep-out check as a method (claims 21 to 25), the solid-metal margin sized from the draft, the battery-against-height relation (claim 8), and the guard's enforcement rules, attestation and signed-parameter bounds (claims 26 to 30). The US one-year grace period (35 U.S.C. 102(b)(1)(A)) covers the inventor's own disclosures; foreign rights in what was shown are probably lost. File before publishing any more detail.
- `khensu-specs` and `khensu-site` are private GitHub repositories (checked 11 October 2026).
- **Entity status and fee:** see `patents/filing/shield/cover-sheet.md`. Claims are optional in a provisional; they are included to support the later application.
- **After filing:** record the application number and date in `PATENTS.md`, and send them back so the sites can show "Patent pending".

---

## Title

Phone-mounted network node accessory with a field-of-view-derived drafted edge, a body terminating below the camera plateau, and a hardware traffic guard

## Cross-reference to related applications

None.

## Field

The disclosure relates to accessories that attach to the back of a mobile phone, and in particular to an accessory that adds a battery, radios and a self-powered network node to a phone next to a raised camera module without obstructing any camera or sensor, to a method of verifying such an accessory's geometry against the fields of view of the phone's sensors, and to hardware that enforces a fixed traffic pattern on every radio of such a device.

## Background

Modern phones have a raised camera module: a camera plateau standing above the phone's back, with lens rings standing above the plateau. On some phones the plateau spans the full width of the phone; on others it is an island in one corner. The lenses include ultra-wide cameras with fields of view of about 120°, and the module also carries a flash, a depth sensor and a microphone.

Battery cases and magnetic battery packs add thickness behind the phone. A pack that is thicker than the camera module rises beside it, and an edge of the pack next to the module can enter the field of view of a wide lens or of the flash, causing vignetting, flare or a shadow in photos. Cases usually avoid this with a generous cut-out or a raised lip that stops below the lenses, which wastes volume that could hold battery cells. The cut-out is typically sized by eye or from a fixed clearance and is not derived from the sensors' actual fields of view.

Privacy networks such as mix networks hide who communicates with whom by sending fixed-size packets on a fixed schedule with cover traffic. In current devices that pattern is produced by software on the main processor. If that software or the operating system is compromised, or an update changes the schedule (for example slowing it on low battery), the traffic pattern changes and reveals activity. Radio chips with direct memory access to the main processor can also read keys and data.

Metal housings give strength and finish but block radio signals and wireless charging, so metal phone accessories either avoid radios or use large plastic windows that break the outer surface.

## Summary

An accessory ("shield") attaches to the back of a phone next to its raised camera module. Its body is thicker than the camera module so that it can hold a large battery. The edge of the body that faces the camera module is drafted: it is inclined away from the module between the height of the camera plateau and the body's outer face, by a draft distance derived from the fields of view of the phone's sensors. For each sensor, the draft needed is the height of the outer face above the sensor, times the tangent of the sensor's half field of view, plus a margin, less the distance already available between the sensor's ring and the body's edge; the draft used is the largest of these. No sensor's field of view therefore touches the accessory, even for a 120° ultra-wide lens, and the body keeps the most battery volume that any given height allows.

On a phone whose camera plateau spans the phone's full width, the body ends just below the plateau and covers the rest of the back. On a phone with a camera island, the body covers the whole back around the island, and the camera sits in a well whose walls are drafted the same way. In an example on a current phone the body is 71.0 × 105.9 mm and 7.68 mm thick, 3 mm above the lens tops, with a 3.69 mm draft and about 14 Wh of cells. Each extra millimetre of height adds about 5 cm³ (about 2.3 Wh) of cells and about 1.73 mm of draft.

The geometry is generated from the phone's interface data and checked automatically at build time: a keep-out solid (a column over each sensor and its field-of-view cone, enlarged by a margin) is intersected with the housing solid, and the build fails if any intersection has more than a threshold volume.

The housing is machined from metal. A Qi2 charging coil sits under a dielectric window in the outer face; the radios radiate through a dielectric band in the bottom edge; a graphite sheet spreads heat into the metal skin; a magnet ring and a micro-suction shock-absorbing layer hold the body on the phone. The accessory has its own USB-C port and can also take power from the phone. Inside, a node computer without any radio reaches the radios only through a guard processor that sends only fixed-size frames on a fixed schedule to allowed destinations, fills empty slots, never changes the schedule with battery level or temperature, and accepts new schedule parameters only with a threshold of committee signatures.

In a further embodiment the outer face is level with the lens tops and a camera plate with one opening per sensor covers the plateau, so the phone's maximum thickness is unchanged.

## Brief description of the drawings

FIG. 1 is a perspective view of an accessory according to a first embodiment attached to a phone with a full-width camera plateau.

FIG. 2A is a back view of the phone and accessory of FIG. 1, with internal parts shown in hidden lines.

FIG. 2B is a bottom end view of the phone and accessory of FIG. 1.

FIG. 3A is a section through the phone and accessory of FIG. 1 on a plane through the ultra-wide lens, parallel to the phone's long side.

FIG. 3B is an enlarged detail of FIG. 3A showing the drafted edge and the field-of-view cones of two lenses.

FIG. 4 is an exploded perspective view of the accessory of FIG. 1.

FIG. 5A is a perspective view of an accessory according to a second embodiment attached to a phone with a camera island.

FIG. 5B is a back view of the phone and accessory of FIG. 5A.

FIG. 5C is a section through the camera well of the accessory of FIG. 5A.

FIG. 6 is a flowchart of a method of generating and verifying the accessory geometry.

FIG. 7A is a perspective view of an accessory according to a third embodiment, whose outer face is level with the lens tops.

FIG. 7B is a section through the accessory of FIG. 7A.

FIG. 8 is a block diagram of the electronics of the accessory.

FIG. 9 is a flowchart of the guard processor's handling of one transmission slot.

## Detailed description

Dimensions are examples for one phone model and are design values computed from a three-dimensional model; the embodiments apply to other phones, sizes and materials.

### 1. Phone interface (FIG. 1, FIG. 3B)

Referring to FIG. 1, a phone 10 has a back 11 (FIG. 3B) and a camera module comprising a camera plateau 12 raised above the back and lens rings 14a, 14b and 14c (wide, ultra-wide and telephoto cameras) raised above the plateau, together with a flash, a depth sensor and a microphone on the plateau. In one example the phone is 71.78 × 149.96 × 8.62 mm; the plateau 12 spans the full width of the phone, is 43.1 mm long from the top end of the phone and stands 2.78 mm above the back 11; and the lens ring tops are 4.68 mm above the back.

Each sensor i is described by its position (x_i, y_i) on the back, the radius r_i of its ring or window, the height z_i of its top above the back, and its half field of view θ_i. In the example, with positions measured from the top left of the plateau:

- wide camera: (14.35, 14.36) mm, r = 8.29 mm, z = 4.68 mm, θ = 42°;
- ultra-wide camera: (14.35, 33.60) mm, r = 8.29 mm, z = 4.68 mm, θ = 60° (a 120° field of view);
- telephoto camera: (32.45, 23.98) mm, r = 8.29 mm, z = 4.68 mm, θ = 20°;
- flash: (57.97, 13.82) mm, r = 3.37 mm, z = 2.78 mm, θ = 60°;
- depth sensor: (57.97, 34.15) mm, r = 3.35 mm, z = 2.78 mm, θ = 40°;
- microphone: (57.97, 23.98) mm, r = 0.38 mm, z = 2.78 mm, no cone (a column only).

### 2. First embodiment: body below a full-width plateau (FIG. 1 to FIG. 4)

**2.1 Outline.** The accessory 100 has a body that covers the back 11 of the phone below the plateau 12. Its outline follows the phone's plan outline inset by a margin (for example 0.4 mm) at the sides and bottom, with corner radii equal to the phone's corner radii less the inset, so the accessory never overhangs the phone. When the plateau spans the phone's width less the accessory's walls, the body's top end is a straight edge one clearance (for example 0.6 mm) below the plateau, with small radii (for example 1 mm) at its corners against the straight phone sides. In the example the body is 71.0 × 105.9 mm (FIG. 2A).

**2.2 Thickness.** The body's thickness T, measured from the phone's back 11 to its outer face 162, is the lens height plus a chosen height Δ above the lens tops; in the example Δ = 3.0 mm and T = 7.68 mm. The outer face 162 is flat, and its edge is rounded (for example with a 1.2 mm radius).

**2.3 Drafted edge.** The body's camera-facing edge 168 (FIG. 1, FIG. 3B) is drafted. Below the height of the plateau 12 the edge is a vertical wall one clearance from the plateau; from the plateau height to the outer face 162 the edge is inclined away from the camera module, reaching the outer face a draft distance d further from the plateau than at its foot. The draft d is computed as

d = max(0, max over sensors i of [(T − z_i) · tan θ_i + m − s_i]),

where (T − z_i) is the height h of the outer face above the sensor top, m is a margin (for example 0.3 mm), and s_i is the distance from the edge of the sensor's ring to the foot of the drafted edge, measured toward the nearest edge of the plateau opening. Sensors whose top is at or above the outer face, or that have no field of view, are skipped. The term in brackets is how far the sensor's field-of-view cone 180 spreads beyond the foot of the edge at the height of the outer face; the draft takes the worst case of all sensors.

In the example (FIG. 3B), the ultra-wide camera, whose ring edge lies s = 1.81 mm from the foot of the edge, needs (7.68 − 4.68) · tan 60° + 0.3 − 1.81 = 3.69 mm, which governs; the wide camera and the flash need less. The drafted edge 168 therefore runs from the foot of the edge at the plateau height (2.78 mm) to a line 3.69 mm further down the phone at the outer face. The cone 180 of the ultra-wide lens 14b passes the edge 168 with the margin m to spare, and the cone of the wide lens 14a points away from it.

The draft is the smallest that clears every field of view, so the body keeps the greatest volume, and therefore battery, for its height. Where the draft is zero (for example when T does not exceed the sensor heights by enough for any cone to reach the edge), the edge is vertical.

**2.4 Solid margin.** Around the drafted edge the housing is solid metal over a band whose width is the clearance plus the draft plus the wall thickness (in the example 0.6 + 3.69 + 1.0 mm), with no cells or cavity, which stiffens the edge that the draft makes thin.

**2.5 Battery volume against height.** Raising the outer face adds cell volume over the whole body but also widens the draft, which removes volume along the camera-facing edge. In the example, computed from the three-dimensional model:

| Height above lens tops (mm) | Thickness T (mm) | Draft d (mm) | Cell volume (cm³) | Cell energy at 0.45 Wh/cm³ (Wh) | Mass in titanium alloy (g) |
| --- | --- | --- | --- | --- | --- |
| 0.5 | 5.18 | 0.00 | 17.50 | 7.9 | 82 |
| 1.0 | 5.68 | 0.22 | 20.46 | 9.2 | 89 |
| 2.0 | 6.68 | 1.95 | 25.89 | 11.7 | 105 |
| 3.0 | 7.68 | 3.69 | 31.09 | 14.0 | 121 |
| 4.0 | 8.68 | 5.42 | 36.05 | 16.2 | 136 |
| 5.0 | 9.68 | 7.15 | 40.80 | 18.4 | 152 |

Each millimetre adds about 5 cm³ (about 2.3 Wh), while the draft grows by tan 60° ≈ 1.73 mm per millimetre because the ultra-wide camera governs. At 5 mm the depth sensor nearly governs. The height is chosen from this relation, for example 3 mm for about twice the cells of the lens-level embodiment (section 4).

**2.6 Layers (FIG. 3B, FIG. 4).** From the phone side outward, the accessory 100 comprises: an attachment layer 110 (for example 0.5 mm of rate-dependent microcellular urethane with a micro-suction face); a base plate 120 (for example glass-filled polycarbonate, 0.4 mm) closing a cavity; in the cavity, a magnet ring 130 aligned with the phone's magnetic charging alignment (for example segmented NdFeB, 56 mm outer and 46 mm inner diameter, 0.5 mm), a circuit board 140 (for example 34 × 14 × 1.6 mm) carrying the node computer, the guard and the radios, a battery 150 (for example lithium-ion pouch cells shaped to the remaining cavity, stacked over the magnet ring where height allows), and a Qi2 receiver coil 155 with ferrite (for example 44 mm diameter, 0.8 mm) under the outer skin; a heat-spreading sheet 158 (for example 25 µm graphite) under the whole skin with an opening over the coil 155; and a housing 160 with an outer skin 161 (for example 0.7 mm) and side walls 163 (for example 1.0 mm). The housing 160 is machined (for example by five-axis CNC) from titanium alloy (for example Ti-6Al-4V) or brass. In the example the housing is about 6.63 cm³ and the accessory weighs about 121 g in titanium alloy or 148 g in brass.

**2.7 Windows and ports (FIG. 2A, FIG. 2B, FIG. 4).** A dielectric coil window 170 (for example 46 mm diameter, polycarbonate) is set flush into the skin 161 over the coil 155 so the accessory can be charged by a Qi2 charger placed on its outer face. A dielectric antenna band 166 (for example colour-matched UL94 V-0 polycarbonate, about 42 mm long) is set flush into the bottom wall and the adjoining part of the skin, in front of the antennas (for example a sub-GHz Wi-Fi HaLow flex antenna and a 2.4/5 GHz chip antenna), with a non-metal keep-out (for example 40 × 8 mm) behind it. A USB-C receptacle 172 in the bottom wall, through the band 166, charges the battery. The accessory does not cover or occupy the phone's own port.

**2.8 Attachment and shock isolation.** The housing never contacts the phone directly: its only load path to the back 11 is the attachment layer 110, which both holds the accessory on (with the magnet ring 130) and isolates it. The side walls 163 stop inside the phone's plan outline, so in a back or edge impact the housing decelerates first and the phone is brought to rest over the layer's usable stroke (for example about 0.3 mm) rather than through a rigid metal contact (about 0.1 mm). Average deceleration scales as v²/2d, so from a 1.5 m drop (v ≈ 5.42 m/s) the phone sees about 5,000 g through the layer against about 15,000 g for a rigid contact.

### 3. Second embodiment: camera island in a drafted well (FIG. 5A to FIG. 5C)

When the phone's camera module is an island that does not span the phone's width, the accessory 100 covers the whole back of the phone 10 around the island 12, and the island sits in a camera well 176 through the body. The walls of the well 176 are drafted by the same rule as the edge 168, taking s_i toward each side of the island, so every field-of-view cone 180 clears every wall of the well (FIG. 5C). In an example on a phone with an island, the accessory is 70.7 × 146.8 mm and 6.6 mm thick, 3 mm above the lens tops, with a draft of 1.4 mm and about 13.7 Wh of cells, weighing about 128 g in titanium alloy.

### 4. Third embodiment: lens-level outer face (FIG. 7A, FIG. 7B)

In this embodiment the thickness T equals the lens height, so the outer face 162 is coplanar with the lens ring tops within a tolerance (for example +0/−0.05 mm, never below the rings), and the phone's maximum thickness, measured at the lenses, is unchanged. The accessory covers the whole back including the plateau 12: over the plateau the housing forms a camera plate 164 (for example 1.1 mm thick, 0.1 mm clear above the plateau) with sensor openings 178, one per sensor, each a clearance (for example 0.6 mm) around the sensor's ring, widening with height so that its wall stays outside the sensor's field-of-view cone by the margin m. In the example the accessory is 71.0 × 149.2 mm and 4.68 mm thick, with about 7.5 Wh of cells and about 95 g in titanium alloy; the battery 150 lies beside the plateau (FIG. 7B). The housing's lower edge meets the phone's back where the phone's own edge round ends and its upper edge is rounded, so the phone's edge curve continues into the accessory without a step. Because the outer face is one unbroken metal surface, this embodiment charges over USB-C and radiates only through the band in the bottom wall.

### 5. Build-time field-of-view check (FIG. 6)

The geometry of every embodiment is generated and verified by a program from the phone's interface data. Referring to FIG. 6:

- In step 300 the program reads the interface data: the phone outline and corner radii, the plateau outline and height, and for each sensor its position, radius, height and field of view.
- In step 302 it chooses the thickness T as the lens height plus a height Δ.
- In step 304 it computes, for each sensor, the draft needed, h tan θ + m − s.
- In step 306 it takes the draft d as the largest of these, or zero.
- In step 308 it generates the housing solid with the outline of section 2.1 or section 3 and an edge or well drafted by d (a loft between the plateau opening, offset by the clearance at the plateau height, and the same opening offset by the clearance plus d at the outer face), or, for the third embodiment, the camera plate with sensor openings.
- In step 310 it builds, for each sensor, a keep-out solid. The solid is the union of a column of radius r + 0.2 mm from the plateau to the sensor top and a cone with apex half-angle θ, starting at radius r + 0.2 mm at the sensor top and extending above the outer face. A sensor with no field of view gets a column only.
- In step 312 it intersects each keep-out solid with the housing solid and computes the volume of the intersection.
- In step 314 it compares each volume with a threshold (for example 0.001 cm³). If any volume exceeds the threshold, step 316 fails the build, naming the sensor, and the design is adjusted (for example by a smaller Δ, a larger margin or a corrected interface datum) and returns to step 302.
- Otherwise, in step 318 the program reports zero interference, the cell volume and energy, and the mass in each material.
- In step 320 it exports manufacturing files (for example STEP and STL for each part, and drawings).

The check is independent of the draft formula, so it also catches errors in the formula, in the interface data or in other features (for example fillets or windows) that might reach into a cone. The sweep of section 2.5 is produced by running the method for several values of Δ.

### 6. Electronics and hardware traffic guard (FIG. 8, FIG. 9)

**6.1 Architecture.** Referring to FIG. 8, the accessory 100 contains a node computer 142 (for example an application-class system-on-module with a Cortex-A55-class processor, 2 GB of memory and 32 GB of storage, running node software for a mix network), a guard processor 144 (for example a Cortex-M33-class microcontroller with a hardware random number generator, AES and SHA acceleration, and SPI and SDIO host ports), a Wi-Fi HaLow (802.11ah) radio 146a for a neighbourhood mesh and a Wi-Fi 6 with Bluetooth LE radio 146b for the phone and nearby devices, both radiating through the band 166.

- The node computer 142 has no radio and no network interface of its own. Its only link out is a serial bus 147 (for example SPI) to the guard 144, without direct memory access into the node computer's memory.
- The radios 146a and 146b connect only to the guard's host ports. The guard is the radios' host and controls their power rails and reset lines 148; the node computer has no bus, reset line or power control to any radio.
- The guard holds the radios in reset until its own firmware passes a post-quantum signature check (for example ML-DSA-87) at every boot. Debug ports are disabled in production.
- Keys stay in the node computer's secure storage and the guard's own secure storage; radios never hold keys.

**6.2 Power.** A power path 149 (a single-cell charger with power path, a USB Power Delivery dual-role controller and a fuel gauge) connects the battery 150, the USB-C receptacle 172, the Qi2 coil 155, and a USB-C link 174 to the phone 10, over which the accessory can take power from the phone when its cells are empty. The guard 144 receives power only. The schedule takes no input from the power path.

**6.3 Egress rules (FIG. 9).** The rules live in guard firmware and a signed parameter set; the node computer cannot change them. Referring to FIG. 9:

- In step 400 a slot falls due, at a time jittered by the guard's random number generator (for example ±100 ms).
- In step 402 the guard checks whether a frame is queued. If one is, step 404 checks that its size is one of the link's allowed sizes and its destination is allowed, namely an entry node listed in the current signed network epoch header or the owner's registered node. A frame that fails the check is dropped and counted (step 406); a frame that passes is padded with random bytes to the allowed size (step 408).
- If no frame is queued, step 410 checks a pool of valid cover packets that the node computer keeps in the guard. If the pool holds one, it is sent (step 412); otherwise the guard sends random bytes of the allowed size to the same peer (step 414).
- In step 416 exactly one frame leaves at the slot time.
- In step 418 the guard updates per-link counters (sent, padded, filled from the pool, filled with random bytes, dropped by reason) and periodically signs an attestation of its firmware hash, parameter epoch and counters, which the paired phone app checks against a public transparency log.
- If the device cannot sustain the schedule, step 420 stops all links together and restarts them on a tick boundary instead of thinning traffic.

Further rules:

1. **Fixed schedule.** Each link sends exactly a configured number of frames per tick (for example four frames per 2 s tick on the internet link and one per tick on the mesh); frames cannot leave early, late, or in greater or smaller number. Extra frames wait for the next free slot up to a limit, then are dropped.
2. **Constant streams.** Larger-frame streams (for example to the owner's node or for calls) run at a constant rate set by the parameter set, padded when idle, and start and stop only on epoch boundaries.
3. **Battery and temperature independence.** The schedule takes no input from the power system or temperature.
4. **Ingress filtering.** Inbound frames of disallowed size are dropped before reaching the node computer, and inbound rate is capped.
5. **Signed parameters with hard bounds.** Tick length, burst size, frame sizes and stream rates change only when a new parameter set arrives inside an epoch header carrying a valid threshold of committee signatures (for example ML-DSA-87), verified by the guard. Firmware bounds that no parameter set can cross include a tick between 1 and 2 s, no battery or temperature dependence, no destination outside the epoch's entry-node list, and no unpadded frames.

In an alternative the guard is a field-programmable gate array placed between a node's processor and its Ethernet PHY and radios, for home nodes at gigabit rates.

**6.4 Pairing.** At setup the companion app creates a post-quantum signature key (for example ML-DSA-87) inside the phone's hardware secure element, usable only after biometric authentication, and signs the accessory's identity key and a pairing record with it. The accessory generates its own keys inside its node computer's secure enclave and accepts configuration, firmware-update approval and owner traffic only when signed by the paired key. Revocation is a signed record from the phone, on which the accessory erases its keys. The accessory handles only sealed fixed-size packets and holds no readable message content.

**6.5 Use.** The accessory runs as a node on its own battery, relays sealed packets to nearby accessories and home nodes over the mesh, reaches the internet through the phone or Wi-Fi, wakes the phone over Bluetooth, and then runs from the phone's power. Because the guard enforces the pattern, the device's traffic looks the same whether the owner is active, idle or low on battery, even if the node computer is compromised.

## Claims

1. An accessory for a mobile phone, the phone having a back and a camera module comprising a camera plateau raised above the back and a plurality of optical sensors on the plateau, each sensor having a ring or window, a top at a sensor height above the back, and a field of view, the accessory comprising: a housing having a phone-facing side and an outer face at a thickness from the back greater than the sensor height of at least one of the sensors; an attachment element on the phone-facing side; and a battery within the housing; wherein the housing has an edge facing the camera module, the edge being inclined away from the camera module between the height of the plateau and the outer face by a draft distance, the draft distance being at least the largest, over the sensors, of the height of the outer face above the sensor top multiplied by the tangent of the sensor's half field of view, plus a margin, less the distance from the sensor's ring or window to the foot of the edge, such that no portion of the housing lies within the field of view of any of the sensors.
2. The accessory of claim 1, wherein the draft distance equals said largest value, such that the edge is inclined no further than needed to clear every field of view.
3. The accessory of claim 1, wherein the sensors include an ultra-wide camera having a field of view of at least 110°, and the draft distance is set by the ultra-wide camera.
4. The accessory of claim 1, wherein the camera plateau spans substantially the full width of the phone, and the housing terminates at a straight edge adjacent to and below the plateau and covers substantially all of the back below the plateau.
5. The accessory of claim 4, wherein the outline of the housing follows the phone's outline inset by a margin at the sides and bottom, and the straight edge has corners of a radius smaller than the phone's corner radius.
6. The accessory of claim 1, wherein the camera module is an island not spanning the width of the phone, the housing covers the back around the island and defines a well receiving the island, and each wall of the well is inclined according to claim 1.
7. The accessory of claim 1, wherein below the height of the plateau the edge is a substantially vertical wall spaced from the plateau by a clearance, and the housing is solid, without cavity, over a band along the edge of a width at least the clearance plus the draft distance plus a wall thickness.
8. The accessory of claim 1, wherein the outer face lies a height between 1 mm and 5 mm above the tops of the sensors, the draft distance increases with said height at the tangent of the governing sensor's half field of view, and the battery occupies substantially all of the housing's internal volume not occupied by the draft and by other components, such that each millimetre of said height adds battery volume over the whole housing.
9. The accessory of claim 8, wherein said height is about 3 mm, the draft distance is between 3 mm and 4.5 mm, and the battery stores at least 12 Wh.
10. The accessory of claim 1, wherein the housing is metal and comprises a dielectric window flush with the outer face over a wireless charging receiver coil within the housing.
11. The accessory of claim 1, wherein the housing is metal and at least one radio within the housing radiates through a dielectric band set flush into a bottom wall of the housing.
12. The accessory of claim 1, further comprising a graphite heat-spreading sheet between the battery and a metal outer skin of the housing.
13. The accessory of claim 1, wherein the attachment element comprises a magnet ring aligned with the phone's magnetic charging alignment and a compliant micro-suction layer that is the housing's only load path to the phone's back, and the housing's side walls lie inside the phone's plan outline.
14. The accessory of claim 1, further comprising its own USB-C receptacle in a wall of the housing that leaves the phone's charging port uncovered, and a power path that charges the battery from the receptacle and can take power from the phone.
15. The accessory of claim 1, further comprising a node computer, a guard processor and at least one radio, wherein the node computer has no radio or network interface of its own and communicates only with the guard processor, and the at least one radio is connected only to the guard processor.
16. The accessory of claim 15, wherein the guard processor transmits on each radio link only frames of a predetermined set of sizes, a predetermined number per fixed time interval, padding short frames and filling empty slots with cover packets or random data, such that the external transmission pattern is independent of the node computer's activity.
17. The accessory of claim 16, wherein the guard processor's schedule is independent of battery level and temperature, and the guard stops all links together, rather than reducing the rate, when the schedule cannot be sustained.
18. The accessory of claim 16, wherein the guard processor accepts a change to the frame sizes or the time interval only in a parameter set carrying a threshold of signatures from a plurality of network committee keys, and enforces fixed bounds that no parameter set can exceed.
19. The accessory of claim 15, wherein the guard processor controls the power and reset of each radio and holds the radios in reset until it has verified its own firmware with a post-quantum signature.
20. An accessory for a mobile phone having a back and a camera module raised above the back to a lens height, the accessory comprising: a housing having a phone-facing side and an outer face; an attachment element on the phone-facing side; a battery and at least one radio within the housing; wherein the distance from the phone-facing side to the outer face equals the lens height within a tolerance, such that with the accessory attached the outer face is substantially coplanar with the top of the camera module and the maximum thickness of the phone is not increased; and a camera plate portion of the housing over the camera module having an opening for each sensor, at least one opening widening with distance from the phone so that its wall lies outside a field-of-view cone of the corresponding sensor.
21. A method of making an accessory for a mobile phone having a camera module with a plurality of sensors, comprising: obtaining interface data comprising, for each sensor, a position, a radius, a height and a field of view; selecting a thickness of the accessory; computing for each sensor a draft from its height below the outer face, its field of view and its distance from an edge of an opening for the camera module, and taking the largest; generating, by a computer, a housing solid having an edge or opening adjacent to the camera module inclined by the largest draft; generating, for each sensor, a keep-out solid comprising a column over the sensor and a cone of the sensor's field of view from the sensor's top, enlarged by a margin; computing the volume of the intersection of each keep-out solid with the housing solid; rejecting the design if any volume exceeds a threshold; and otherwise producing manufacturing files for the housing.
22. The method of claim 21, wherein rejecting the design comprises failing an automated build and identifying the sensor whose keep-out solid is intersected, and the method repeats with an adjusted thickness or margin.
23. The method of claim 21, further comprising computing a battery volume within the housing solid for each of a plurality of thicknesses and selecting the thickness from the relation between battery volume and draft.
24. The method of claim 21, wherein the keep-out solid for a sensor without a field of view is a column only.
25. The method of claim 21, further comprising machining the housing from metal according to the manufacturing files.
26. A network device comprising a host processor without any network interface of its own, a guard processor connected to the host processor only by a bus without direct memory access into the host processor's memory, and one or more radios connected only to the guard processor, wherein the guard processor enforces fixed frame sizes, a fixed schedule, filled empty slots, an allowed-destination list taken from a signed network epoch header, and schedule independence from battery level and temperature.
27. The network device of claim 26, wherein the guard processor keeps per-link counters of frames sent, padded, filled from a cover pool, filled with random data and dropped, and signs an attestation of its firmware hash, parameter epoch and counters for verification by a paired phone.
28. The network device of claim 26, wherein the guard processor controls the power and reset of each radio, and the host processor has no power, reset or bus connection to any radio.
29. The network device of claim 26, housed in an accessory according to claim 1.
30. The network device of claim 26, wherein the guard processor accepts configuration and owner traffic only when signed by a post-quantum signature key held in a hardware secure element of a paired phone and released by biometric authentication.

## Abstract

An accessory on a phone's back beside its raised camera module holds a battery, radios and a network node. Its body is thicker than the camera module, and its camera-facing edge is inclined by a draft equal to the largest, over the phone's sensors, of the outer face's height above the sensor times the tangent of its half field of view, plus a margin, less the available clearance, so no field of view, even a 120° ultra wide, touches it. On a phone with a full-width camera plateau the body ends just below the plateau; on a camera-island phone the camera sits in a drafted well. The geometry is generated from the phone's interface data and fails its build if any sensor's column or field-of-view cone intersects the housing. A guard processor, the only path to the radios, sends fixed-size frames on a fixed schedule regardless of battery or temperature.
