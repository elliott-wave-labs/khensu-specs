# Provisional patent application (draft for filing): NuLink transceiver shell

Draft 1, 10 October 2026. **Confidential until filed.** Prepared for filing as a US provisional application through USPTO Patent Center. Patent counsel should review before the non-provisional or PCT filing, which must follow within 12 months of the provisional filing date.

## Filing notes (not part of the application)

- **File tonight.** Parts of this design were shown on khensu.nu and elliottwave.studio on 10 October 2026 (exploded view naming the layers, a side view showing the back level with the lens tops, an antenna band in the edge, a node board with a network guard, named components). In the US that starts a 12-month grace period from 10 October 2026. Most other countries require absolute novelty at filing, so foreign rights in what the site already showed may be lost; anything filed here that the site did not show (the guard's enforcement rules, the camera plate geometry and verification, the profile continuity, the parameter-signature scheme) is still new. File before publishing any more detail.
- **Applicant:** Elliott Wave LLC. **Inventor:** Elliott (full legal name on the cover sheet). Sign an assignment from the inventor to Elliott Wave LLC and record it.
- **Entity status:** check micro or small entity eligibility on the current USPTO fee schedule; the cover sheet (form PTO/SB/16 or the Patent Center web form) and the provisional filing fee are all that is required. Claims are optional in a provisional but are included to help the later non-provisional.
- **Drawings to attach (PDF):** `hardware/shell/drawings/iphone-18-pro/KS-IPHONE-18-PRO-WRAP-100.png` (FIG. 1) and `-101.png` (FIG. 2), the exploded layer renders from `render_layers.py` (FIG. 3), the side views from khensu-site `SideView.astro` exported as images (FIG. 4A, 4B), the guard architecture diagram from `design/guard.md` section 3 (FIG. 5), and the guard egress flow (FIG. 6, to draw from section 5 below). The full `khensu-shell-drawings.pdf` may be attached as an appendix.
- **After filing:** send the application number and filing date so the sites can show "Patent pending" with a link, and add the entry to `PATENTS.md`.

---

## Title

Phone-mounted network node accessory with a lens-level back, a continuous edge profile and a hardware traffic guard

## Field

The disclosure relates to accessories that attach to the back of a mobile phone, and in particular to an accessory that adds a self-powered network node, radios and a battery to the phone without increasing the phone's maximum thickness, and to hardware that enforces a fixed traffic pattern on every radio of such a device.

## Background

Modern phones have a raised camera module (a camera plateau with lens rings standing above it). Cases and battery accessories either cover the module with a raised lip or sit around it, adding to the phone's maximum thickness and leaving an uneven back. Battery packs that attach magnetically add several millimetres everywhere.

Privacy networks such as mixnets hide who communicates with whom by sending fixed-size packets on a fixed schedule with cover traffic. In current devices that pattern is produced by software on the main processor. If that software or the operating system is compromised, or an update changes the schedule (for example slowing it on low battery), the traffic pattern changes and reveals activity. Radio chips with direct memory access to the main processor can also read keys and data.

Metal housings give strength and finish but block radio signals, so metal phone accessories either avoid radios or use large plastic windows that break the outer surface.

## Summary

An accessory ("shell") attaches to the back of a phone. Its outer face is level with the tops of the phone's lens rings, so the phone with the shell is no thicker at its thickest point than the phone alone, and the back becomes one flat surface with only the lenses, flash, depth sensor and microphone showing through sized openings in a camera plate. The shell's housing is machined from metal (for example titanium alloy or brass) and its side profile continues the phone's own edge curve, so the phone and shell read as one shape with no step or lip. Inside are a battery, a node computer, radios and a guard processor. The guard is the only path from the node computer to any radio; it sends only frames of allowed fixed sizes on a fixed schedule to allowed destinations, fills empty slots, never changes the schedule with battery level or temperature, and accepts new schedule parameters only when they carry a threshold of signatures from a network committee. The radios radiate through a narrow dielectric band set into the housing's edge wall, so the outer face stays one unbroken metal surface.

## Detailed description

### 1. Overview (FIG. 1, FIG. 3)

The shell 100 is a thin body that covers substantially the whole back of a phone 10. From the phone side outward it comprises: an attachment layer 110 (a micro-suction film, for example nano-suction polyurethane about 0.3 mm thick); a base plate 120 (for example glass-filled polycarbonate about 0.6 mm thick) that closes the cavity; a cavity holding a magnet array 130 compatible with the phone's magnetic charging alignment (for example a segmented NdFeB ring of 56 mm outer and 46 mm inner diameter, 0.5 mm thick), a circuit board 140 carrying the node computer, the guard and the radios (for example 34 × 14 × 1.6 mm), and a battery 150 (for example a single-cell lithium-ion pouch shaped to the remaining cavity); a heat-spreading sheet (for example graphite about 0.025 mm); and a housing 160 with an outer skin (for example 0.7 mm) and side walls (for example 1.0 mm).

In one example for a phone 71.9 × 150.0 mm with a body 8.75 mm thick, a camera plateau 3.0 mm high and lens rings 4.2 mm above the back, the shell is 71.1 × 149.2 mm and 4.2 mm thick, holds about 6.2 Wh, and weighs about 87 g in titanium alloy or about 126 g in brass. The figures are examples; the arrangement applies to any phone with a raised camera module.

### 2. Lens-level outer face and camera plate (FIG. 2, FIG. 4A, FIG. 4B)

The shell's thickness equals the height of the lens rings above the phone's back, so the outer face 162 is coplanar with the lens ring tops within a tolerance (for example +0/−0.05 mm, never below the rings). The phone's maximum thickness, measured at the lenses, is unchanged (12.95 mm in the example both without and with the shell).

Over the camera plateau the housing forms a camera plate 164 (for example 1.1 mm thick, 0.1 mm clear above the plateau) with one opening per sensor: a round opening around each lens ring with a clearance (for example 0.6 mm per side), and openings for the flash, the depth sensor and the microphone. Openings for emitters and sensors with a wide field of view widen with height (a draft) so the opening wall stays outside each sensor's light cone. The design is verified computationally: each sensor's column and field-of-view cone (with a margin, for example 0.3 mm) is intersected with the housing solid, and the design fails if any intersection exceeds a threshold (for example 0.2 mm³). The metal within a margin of the camera opening (for example 1.6 mm) is solid, with no cavity, for stiffness.

In an alternative, the outer face rises a fixed height above the lens rings (for example 3 mm) to hold a larger battery; the camera then sits in one drafted opening that clears every field of view (for example 120° for an ultra-wide lens). In another alternative, a smaller body sits within the magnet area below the camera module and clears it entirely.

### 3. Continuous edge profile (FIG. 4B)

The housing's outline follows the phone's plan outline inset by a small margin (for example 0.4 mm) so the shell never overhangs the phone, with corner radii equal to the phone's corner radii less the inset. In side profile, the housing's lower edge meets the phone's back edge where the phone's own edge round ends, and the housing's upper edge is rounded (for example with a 2.2 mm radius), so the phone's edge curve continues into the shell's edge without a step or lip. The housing is machined (for example by five-axis CNC) from the phone interface data, so the fit and the profile continuity are held to the phone's tolerances (for example ±0.05 mm on the outline).

Finishes: titanium alloy (for example Ti-6Al-4V) bead-blasted and powder-coated in a matte colour matched to the phone's finish, with the face machined low by the coating thickness so the coated face is level with the lens rings; or bare brass (for example C26000, lead-free) bead-blasted to satin and left uncoated so its copper content stays exposed.

### 4. Edge antenna band in an unbroken metal face

The radios' antennas (for example a sub-GHz flex antenna and a 2.4/5 GHz chip antenna) sit behind a dielectric band 166 (for example colour-matched UL94 V-0 polycarbonate, about 42 mm long) set flush (for example within 0.02 mm) into one edge wall of the housing, like the antenna bands in a phone frame. The outer face carries no window, so it remains one unbroken metal surface. A non-metal keep-out (for example 40 mm) is kept along that edge inside the cavity. In alternatives, a second band is set into a side wall, or a window over a wireless charging coil is provided in the skin.

### 5. Power path

A USB-C receptacle in the bottom edge charges the battery and passes power to the phone through a short right-angle jumper or a plug integrated into a case lip, with a single-cell charger with power path, a USB Power Delivery dual-role controller and a fuel gauge. When the battery is empty, the board runs from the phone's power. In alternatives, a wireless charging receiver coil sits under a dielectric window in the skin.

### 6. Node computer and guard (FIG. 5)

The board carries a node computer 142 (for example an application-class system-on-module such as a Cortex-A55-class processor with 2 GB of memory and 32 GB of storage, running node software) and a guard 144 (for example a Cortex-M33-class microcontroller with a hardware random number generator, AES and SHA acceleration, and SPI and SDIO host ports). The radios 146 (for example a Wi-Fi HaLow 802.11ah radio for a neighbourhood mesh and a Wi-Fi 6 with Bluetooth LE radio for the phone and nearby devices) connect only to the guard's host ports.

- The node computer has no radio and no network interface of its own. Its only link out is a serial bus (for example SPI) to the guard, which has no direct memory access into the node computer's memory.
- The guard is the radios' host and controls their power rails and reset lines; the node computer has no bus, reset line or power control to any radio.
- The guard holds the radios in reset until its own firmware passes a post-quantum signature check (for example ML-DSA-87) at every boot. Debug ports are disabled in production.
- Keys stay in the node computer's secure storage and the guard's own secure storage; radios never hold keys.

### 7. Egress rules enforced by the guard (FIG. 6)

The rules live in guard firmware and a signed parameter set; the node computer cannot change them.

1. **Fixed frame sizes.** Each link has a small set of allowed datagram sizes. Short frames are padded with random bytes; oversized frames are dropped and counted.
2. **Fixed schedule.** Each link sends exactly a configured number of frames per tick (for example four frames per 2 s tick on the internet link and one per tick on the mesh), at times jittered by the guard's random number generator (for example ±100 ms). Frames cannot leave early, late, or in greater or smaller number.
3. **Filled slots.** The node computer keeps a pool of valid cover packets in the guard. If the pool is empty when a slot comes due, the guard sends random bytes of the allowed size to the same peer, so the external pattern never changes.
4. **Bounded queues.** Extra frames wait for the next free slot up to a limit, then are dropped; real traffic only takes slots that cover would have used.
5. **Allowed destinations.** Internet-bound frames go only to the entry nodes listed in the current signed network epoch header, and optionally to the owner's own registered node; anything else is dropped.
6. **Constant streams.** Larger-frame streams (for example to the owner's own node or for calls) run at a constant rate set by the parameter set, padded when idle, and start and stop only on epoch boundaries.
7. **Battery and temperature independence.** The schedule takes no input from the power system or temperature. If the device cannot sustain the schedule, the guard stops all links together and restarts on a tick boundary instead of thinning traffic.
8. **Ingress filtering.** Inbound frames of disallowed size are dropped before reaching the node computer, and inbound rate is capped.
9. **Signed parameters with hard bounds.** Tick length, burst size, frame sizes and stream rates change only when a new parameter set arrives inside an epoch header carrying a valid threshold of committee signatures (for example ML-DSA-87), verified by the guard. Firmware bounds that no parameter set can cross include: tick between 1 and 2 s, no battery or temperature dependence, no destination outside the epoch's entry-node list, and no unpadded frames.
10. **Owner verification.** The guard keeps per-link counters (sent, padded, filled from the pool, filled with random bytes, dropped by reason) and signs an attestation of its firmware hash, parameter epoch and counters, which the paired phone app checks against a public transparency log.

In alternatives the guard is a field-programmable gate array placed between a node's processor and its Ethernet PHY and radios, for home nodes at gigabit rates.

### 7a. Shock-isolating attachment layer

The housing never contacts the phone directly. Its only load path to the phone's back is a compliant attachment layer, for example 0.5 mm of rate-dependent microcellular urethane with a micro-suction face, that both holds the accessory on and isolates it. The side walls stop inside the phone's plan outline (for example 0.4 mm), so in a back or edge impact the housing decelerates first and the phone is brought to rest over the layer's usable stroke (for example about 0.3 mm) rather than through a rigid metal contact (about 0.1 mm). Average deceleration scales as v²/2d, so from a 1.5 m drop (v ≈ 5.42 m/s) the phone sees about 5,000 g through the layer against about 15,000 g for a rigid contact. The layer's thickness is taken from the base plate (for example 0.6 mm reduced to 0.4 mm), so the stack height, and with it the lens-level outer face and the battery volume, are unchanged.

### 7b. Pairing to the phone's secure element

At setup the companion app creates a post-quantum signature key (for example ML-DSA-87) inside the phone's hardware secure element, usable only after biometric authentication, and signs the accessory's identity key and a pairing record with it. The accessory generates its own keys inside its processor's secure enclave and accepts configuration, firmware-update approval and owner traffic only when signed by the paired key. Revocation is a signed record from the phone, on which the accessory erases its keys. The accessory handles only sealed fixed-size packets and holds no readable message content.

### 7c. Independent ports

The accessory has its own USB-C receptacle in its bottom wall above the phone's port and never covers or occupies the phone's port, so both can be charged at once and the phone's port remains available for other devices.

### 8. Use

With the shell attached, the phone's maximum thickness is unchanged and its back is flat. The shell runs as a node on its own battery (for example about 4–5 hours at about 1 W), relays sealed packets to nearby shells and home nodes over the mesh, reaches the internet through the phone or Wi-Fi, wakes the phone over Bluetooth, and then runs from the phone's power over USB-C. Because the guard enforces the pattern, the device's traffic looks the same whether the owner is active, idle or low on battery, even if the node computer is compromised.

## Claims (optional in a provisional; included to support the later application)

1. An accessory for a mobile phone having a back and a camera module raised above the back to a lens height, the accessory comprising: a housing having a phone-facing side and an outer face; an attachment element on the phone-facing side; a battery and at least one radio within the housing; wherein the distance from the phone-facing side to the outer face equals the lens height within a tolerance, such that with the accessory attached the outer face is substantially coplanar with the top of the camera module and the maximum thickness of the phone is not increased; and a camera plate portion of the housing over the camera module having an opening for each lens.
2. The accessory of claim 1, wherein at least one opening widens with distance from the phone so that its wall lies outside a field-of-view cone of the corresponding sensor or emitter.
3. The accessory of claim 1, wherein the housing is metal, the outer face is an unbroken metal surface, and the at least one radio radiates through a dielectric band set flush into an edge wall of the housing.
4. The accessory of claim 1, wherein the housing outline follows the phone's plan outline inset by a margin, and the housing's side profile begins where the phone's back edge round ends and is rounded at the outer face, so the phone's edge profile continues into the housing without a step.
5. The accessory of claim 1, further comprising a node computer and a guard processor, wherein the node computer has no radio or network interface of its own and communicates only with the guard processor, and the at least one radio is connected only to the guard processor.
6. The accessory of claim 5, wherein the guard processor transmits on each radio link only frames of a predetermined set of sizes, a predetermined number per fixed time interval, padding short frames and filling empty slots with cover or random data, such that the external transmission pattern is independent of the node computer's activity.
7. The accessory of claim 6, wherein the guard processor's transmission schedule is independent of battery level and temperature, and the guard stops all links together, rather than reducing the rate, when the schedule cannot be sustained.
8. The accessory of claim 6, wherein the guard processor accepts a change to the frame sizes or the time interval only in a parameter set carrying a threshold of signatures from a plurality of network committee keys, and enforces fixed bounds that no parameter set can exceed.
9. The accessory of claim 5, wherein the guard processor controls the power and reset of each radio and holds the radios in reset until it has verified its own firmware with a post-quantum signature.
10. A network device comprising a host processor without any network interface of its own, a guard processor connected to the host processor only by a bus without direct memory access into the host processor's memory, and one or more radios connected only to the guard processor, wherein the guard processor enforces fixed frame sizes, a fixed schedule, filled empty slots, an allowed-destination list taken from a signed network epoch header, and schedule independence from battery level and temperature.
11. A method of adding a network node to a mobile phone without increasing its maximum thickness, comprising: measuring the height of the phone's camera module above its back; forming a metal housing whose thickness equals that height, whose outline follows the phone's outline inset by a margin, and whose camera plate has an opening for each sensor clear of each sensor's field-of-view cone; verifying by intersecting each sensor's field-of-view cone with the housing solid; placing a battery, a node computer, a guard processor and radios in the housing; and attaching the housing to the phone's back so that its outer face is level with the top of the camera module.
12. The accessory of claim 1, wherein the housing is coupled to the phone's back only through a compliant attachment layer, the housing's side walls lie inside the phone's plan outline, and the layer's usable compression stroke reduces the phone's average deceleration in a back or edge impact relative to a rigid contact.
13. The accessory of claim 12, wherein the attachment layer is a rate-dependent microcellular polymer with a micro-suction face that both retains the accessory on the phone and provides the compliant coupling, and the sum of the attachment layer and base plate thicknesses is constant such that the outer face remains level with the top of the camera module.
14. The accessory of claim 5, wherein the accessory stores its keys in a secure enclave of the node computer and accepts configuration and owner traffic only when signed by a post-quantum signature key held in a hardware secure element of the paired phone and released by biometric authentication.
15. The accessory of claim 1, further comprising its own charging port in an edge wall of the housing, wherein the housing leaves the phone's own charging port uncovered and unoccupied.
