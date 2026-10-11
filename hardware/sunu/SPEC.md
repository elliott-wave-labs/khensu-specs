# suñůlink shield: product specification

Revision B, 10 October 2026. **Preliminary.** Phone interface dimensions are placeholders until they are replaced with Apple's Accessory Design Guidelines drawings for each target model. Electrical figures marked *estimate* are to be measured on the first boards.

suñůlink shield (formerly the khensu shell) is a post-quantum mesh transceiver and node that attaches to the back of an iPhone. **The product is the Wrap on iPhone 18 Pro and Pro Max** (iPhone 18 to follow); the other styles stay in the CAD as engineering references. It relays sealed khensu packets over Wi-Fi HaLow to nearby shells and home nodes, reaches the internet through the phone or Wi-Fi, wakes the phone over Bluetooth instead of Apple's push service, and earns from token burning like any node. Background in `design/mesh.md` section 6.

## 1. Deliverables

| File | Contents |
| --- | --- |
| `drawings/sunu-drawings.pdf` | All 18 sheets, A3, third-angle projection |
| `drawings/<phone>/KS-<phone>-<style>-100.dxf` | Assembly: views, section with balloons, parts list |
| `drawings/<phone>/KS-<phone>-<style>-101.dxf` | Housing detail for CNC: dimensions, windows, sections, isometric |
| `drawings/<phone>/KS-<phone>-CASE-201.dxf` | Silicone shock case for moulding |
| `out/<phone>/<style>/*.step`, `*.stl` | Every part as a separate solid (STEP governs undimensioned geometry) |
| `out/summary.json` | Computed volumes, battery, mass and interference check |
| `sunu.py`, `drawings.py` | Parametric source; rerun after changing any dimension |

DXF files are AutoCAD R2018, millimetres, with native DIMENSION and HATCH entities on standard layers (OUTLINE, HIDDEN, CENTER, SECTION, HATCH, DIM, TEXT, BORDER, TITLE). They open directly in AutoCAD, Fusion, SolidWorks, DraftSight and LibreCAD.

## 2. Variants

| Style | Phone | Footprint (mm) | Thickness (mm) | Cells | Mass (titanium) | Attachment | Drawings |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Card | iPhone 18 Pro | 56 × 86 | 5.2 | 4.1 Wh | 50 g | Magnets (53 mm ring) | KS-IPHONE-18-PRO-CARD-100/101 |
| Fill | iPhone 18 Pro | 65.9 × 143.0, camera plate | 4.2 (level) | 5.4 Wh | 73 g | Magnets and suction | KS-IPHONE-18-PRO-FILL-100/101 |
| **Wrap (the product)** | iPhone 18 Pro | 71.1 × 149.2, camera plate over the full-width plateau | 4.2 (level) | 6.2 Wh | 93 g (136 g brass) | Magnets and shock-isolating suction layer | KS-IPHONE-18-PRO-WRAP-100/101 |
| Wrap XL | iPhone 18 Pro | 71.1 × 149.2, long camera cut-out, 1.3 mm draft | 7.2 (+3.0) | 13.2 Wh | 124 g | Magnets and suction | KS-IPHONE-18-PRO-WRAP-XL-100/101 |
| Card | Standard | 56 × 86 | 5.2 | 4.1 Wh | 50 g | Magnets (53 mm ring) | KS-ISLAND-CARD-100/101 |
| Fill | Standard | 65.5 × 140.6, camera plate | 3.6 (level) | 4.6 Wh | 69 g | Magnets and suction | KS-ISLAND-FILL-100/101 |
| Wrap | Standard | 70.7 × 146.8, camera plate | 3.6 (level) | 5.4 Wh | 79 g | Magnets and suction | KS-ISLAND-WRAP-100/101 |
| Wrap XL | Standard | 70.7 × 146.8, 1.4 mm draft | 6.6 (+3.0) | 13.7 Wh | 129 g | Magnets and suction | KS-ISLAND-WRAP-XL-100/101 |
| Silicone case | Both | phone + 1.6 per side | phone + module + 0.8 | (holds a Wrap) | about 18 g | Grips the phone | KS-*-CASE-201 |

"Level" means the top face is level with the tops of the lens rings, so the back is one flat surface with no camera bump, like a phone with flush cameras; "+" is height above the lens rings. In the fill and wrap a camera plate covers the plateau (2.1 mm thick on iPhone 18 Pro's 2 mm plateau, 0.1 mm above it), with a round opening for each lens, the flash, the depth sensor and the microphone: 0.6 mm clear round each, and the flash and depth-sensor openings widen with height so the wall stays outside their light cones. The XL rises 3 mm above the lenses, where separate openings for the ultra wide would merge, so its camera sits in one opening that widens with height (the draft) to stay out of every field of view (120° for the ultra wide), with 0.3 mm to spare. `sunu.py` intersects each sensor's column and field-of-view cone with the housing and fails the build if anything touches, with 0.2 mm to spare. The slim styles also have a 3.4 mm floor (shock layer 0.5, base 0.4, board 1.6 with 0.2 clearance, skin 0.7). iPhone 18 Pro's camera plateau runs the full width of the phone (apple.com), so the wrap's camera plate spans edge to edge over it and its side walls stop at the plateau. The titanium within 1.6 mm of the opening is solid, with no cells. Cell energy assumes 0.45 Wh/cm³ for thin pouch cells.

## 3. Mechanical

**Construction stack (phone side outward):** shock layer with micro-suction face 0.5 → base plate 0.4 → cavity (magnet ring 0.5, board 1.6, cells; Qi2 coil 0.8 under the skin in the card and XL only) → graphite sheet 0.025 → skin 0.7. Side walls 1.0.

| Item | Material | Process and finish | Notes |
| --- | --- | --- | --- |
| Housing (titanium) | Ti-6Al-4V Grade 5 (ASTM B348 / F136), "titanium battleproof shell"; yield at least 828 MPa, about 1.6× 7075-T6 aluminium | 5-axis CNC; bead blast; plasma electrolytic oxidation (micro-arc) to grow a 10–15 µm TiO₂ ceramic layer from the titanium, then a colour-matched ceramic topcoat 20–25 µm on the outer faces (Burgundy, Glacier, Silver, Black for iPhone 18 Pro), satin so it doesn't show fingerprints. Mask the inside, the windows and the phone side; machine the face 0.035 mm low so the finished face is level with the lens rings | 0.7 mm skin needs a vacuum fixture; 0.8–1.0 mm is safer for first articles |
| Housing (brass) | C26000 cartridge brass (70% copper, 30% zinc, lead-free, no nickel) | 5-axis CNC; bead blast to satin and leave bare. No lacquer or coating, which would stop the copper working on germs. It darkens to a natural patina; it cannot rust (no iron) | About 1.9× the titanium housing mass (wrap 136 g against 93 g). Copper alloys of at least 60% copper are registered with the US EPA as antimicrobial; product claims need the registered alloy, approved wording, and regulatory review before launch |
| Windows | PC, UL94 V-0, colour matched | Insert-moulded or bonded, flush within 0.02 | Fill and wrap: a 42 mm antenna band in the bottom wall only, like the bands on a phone's frame; the outer face is one unbroken metal surface with no windows. Card and XL: Ø46 over the coil (skin only) and a 42 mm strip along the bottom edge (skin and wall) |
| Base plate | PC-GF30 | Moulded or CNC | Bonded with a 0.1 mm PSA perimeter bead |
| Shock layer | Microcellular urethane, PORON XRD class, 0.5 mm, with a micro-suction face | Die cut, laminated to base | Holds the shell on and isolates it: rate-dependent, soft at rest and firm at impact. Washable; replaceable part. See section 3a |
| Magnet ring | NdFeB N52, Ni-Cu-Ni plated, segmented | Bought in | MagSafe-compatible array; 56/46 mm (53/43 mm in the card) |
| Silicone case | LSR, Shore 55A ±5 | Injection moulded, VDI 27 texture | Add 0.5–1° draft; button covers per model |

**Tolerances:** ISO 2768-mK general; phone interface features (outline, camera cutout, MagSafe axis) ±0.05; camera clearance 0.6 per side, with the face level with the lens rings within +0/−0.05 (never below them); window flushness 0.02.

**Attachment targets (to validate):** normal pull-off at least 10 N on magnets alone and 25 N with suction; shear at least 15 N; no creep over 24 h at 40 °C; repeated attach/detach 5,000 cycles without film loss.

**USB-C (decided):** the shell has its own USB-C receptacle centred in its bottom wall, directly above the iPhone's. The iPhone's port is never covered or plugged: the shell sits on the back only, so the owner can charge both at once (two cables or one dual-head cable) and keep the iPhone's port for drives, displays, audio and CarPlay. There is no jumper to the phone.

### 3a. Drop physics and shock isolation

From a drop height h the impact speed is v = √(2gh): 5.42 m/s at 1.5 m. Stopping over distance d gives an average deceleration v²/2d. With a rigid metal-to-phone contact (d ≈ 0.1 mm) that is about 15,000 g; through the 0.5 mm shock layer with about 0.3 mm usable stroke it is about 5,000 g, a third of the rigid case. Energy at impact rises from 2.9 J (about 200 g phone) to 4.3 J with the 93 g shell, which is why the shell's mass must reach the phone through the layer, never through a hard contact.

- The housing never touches the phone directly: the shock layer is the only load path on the back, and the side walls stop 0.4 mm inside the phone's outline.
- The shell protects the back and frames the camera. It does not cover the screen; face-down drops are the phone's own Ceramic Shield 2.
- Verify on first articles: MIL-STD-810H Method 516.8 transit drops at 1.2 m and 1.5 m onto steel-backed plywood, 26 orientations, with accelerometers on the phone; publish peak g with and without the layer.

### 3b. Pairing to the iPhone's Secure Enclave

At setup the app creates a `SecureEnclave.MLDSA87` key (CryptoKit, iOS 26), gated by Face ID with `.biometryCurrentSet`, and signs the shell's identity key and a pairing record. The shell generates its keys inside the i.MX 93's EdgeLock Secure Enclave and accepts configuration, updates approval and owner traffic only when signed by the paired key. Revocation is a signed record from the phone; a revoked shell wipes its keys. The shell holds no readable message content: it handles only sealed fixed-size packets.

## 4. Electrical

**Architecture (decided):** one Linux system-on-module, always on while attached, and a guard chip that owns both radios (`design/guard.md`). The SoM has no radio or network interface of its own: it talks only to the guard over SPI, and the guard is the radios' host and controls their power. The 2 s tick never changes with battery level.

| Block | Choice (candidates) | Notes |
| --- | --- | --- |
| Application processor | NXP i.MX 93 SoM (2× Cortex-A55, Cortex-M33, EdgeLock Secure Enclave) | Runs tatenan in a reduced node profile; secure boot; node keys sealed in EdgeLock |
| Memory | 2 GB LPDDR4X, 32 GB eMMC | Encrypted outbox, inbox and content cache |
| Guard (Guard-M) | STMicroelectronics STM32U5 (Cortex-M33 with TrustZone, TRNG, AES/SHA acceleration, SPI and SDIO host) | Open Rust firmware; enforces frame sizes, the tick, destinations and signed parameters; ML-DSA-87 secure boot; holds radios in reset until its checks pass |
| Mesh radio | Wi-Fi HaLow (802.11ah) module based on the Morse Micro MM6108, hosted by the guard | Pre-certified module; must support a microcontroller host |
| Wi-Fi and Bluetooth | NXP IW612 (Wi-Fi 6, Bluetooth LE, 802.15.4), hosted by the guard | Link to the phone and nearby devices; Bluetooth wakes the app |
| Power path | TI TPS25750 USB-C PD controller, TI BQ25895 1S charger with power path, TI BQ27427 fuel gauge | Charges over its own USB-C (fill, wrap) or Qi2 (card, XL). The iPhone's port stays free |
| Wireless charging | Qi2-certified receiver module, coil under the skin window (card and XL only) | The flat-back fill and wrap have no coil, since metal over it would block charging; they charge over USB-C. The phone can't charge wirelessly through any metal shell |
| Cells | 1S Li-ion pouch, 3.85 V nominal, about 1,610 mAh (6.2 Wh) in the wrap, custom shape to the cavity | Protection circuit on board; NTC on the pack; 1.7–1.8 mm thick in slim styles; IEC 62133-2 and UN 38.3 |
| Cells, extended option | 1S silicon-carbon anode pouch (Group14 SCC55 class, as shipping in flagship phones), same envelope: about 7.5 Wh (about 1,950 mAh). Higher cost. Next step: 100% silicon anode (Enovix AI-1 class, 935 Wh/L independently tested, in smartphone qualification as of 2026) | Silicon swells more than graphite: keep the 0.1 mm swell allowance in the cell pocket, qualify cycle life at the node's duty cycle, same protection, NTC and IEC 62133-2 / UN 38.3 certification |

**Power budget (estimate, to be measured):**

| Load | Average |
| --- | --- |
| SoM running the node profile | 0.4–0.6 W |
| HaLow at a 2 s mesh tick plus relaying | 0.15–0.4 W |
| Wi-Fi and Bluetooth to the phone | 0.05–0.2 W |
| Guard | 0.02–0.05 W |
| **Total** | **about 1 W** |

At about 1 W and 85% conversion efficiency, a slim shell runs about 4–5 hours on its own cells, the card about 3.5 hours and the XL about 11 hours. After that it stops relaying until it is charged; it never draws from the phone, whose port stays open. The owner's own messages still arrive through the phone.

## 5. Radios and network

| Link | Band | Use |
| --- | --- | --- |
| Wi-Fi HaLow | Sub-GHz ISM by region (US 902–928 MHz, EU 863–868 MHz, others per market) | Neighbourhood mesh, about 1 km to home nodes (target, line of sight) |
| Wi-Fi 6 | 2.4 and 5 GHz | Internet backhaul when on Wi-Fi; link to the phone |
| Bluetooth LE 5.3 | 2.4 GHz | Wakes the khensu app without APNs; control channel |

- **Internet traffic** looks like ordinary HTTPS/3: WebTransport on UDP 443 with no SNI, sealed mixnet packets inside.
- **Mesh traffic** uses the same sealed fixed-size packets on a constant 2 s tick (1 small packet per tick on the mesh), so the radio pattern doesn't reveal activity.
- **Antennas:** HaLow flex antenna and the 2.4/5 GHz chip antenna sit behind the bottom-edge PC window; keep 40 mm non-metal along that edge. The titanium housing makes the window mandatory.

## 6. Thermal

- Skin temperature target 41 °C maximum in a 25 °C room (well inside IEC 62368-1 touch limits).
- 25 µm pyrolytic graphite across the inner skin, clear of both windows.
- Control order above 41 °C or when the phone reports thermal pressure: cut charging rate first, then pause optional work (cache serving, committee duty). The tick and cover never change.
- Never charges itself and the phone at full rate at the same time.

## 7. Environmental and durability

| Item | Target |
| --- | --- |
| Operating | 0–35 °C; charging 0–45 °C at the cells |
| Storage | −20 to 45 °C at 40–60% charge |
| Ingress | IP54 for slim styles; the dive case is a separate rigid housing with O-rings |
| Drop | 1.2 m to concrete, 26 drops on the phone with the shell attached (case version) |
| Magnets | Keep away from magnetic-stripe cards and pacemakers (labelling) |

## 8. Compliance and verification

- **Radio:** FCC Part 15 (HaLow under 15.247), ISED, CE RED, UKCA, MIC Japan, RCM; pre-certified modules reduce, but don't remove, end-product testing.
- **RF exposure:** the shell is worn against the phone and the head during calls, so SAR evaluation is required in each market.
- **Battery and safety:** UN38.3 (transport), IEC 62133-2, IEC 62368-1.
- **RF:** the flat-back styles radiate only through the edge band, with metal over the antennas; measure HaLow, Wi-Fi and Bluetooth efficiency on first articles and widen the band (or add a second on a side wall) if range falls short.
- **Charging and USB:** Qi2 certification (WPC) for the receiver; USB-IF compliance for the USB-C port.
- **Materials:** RoHS, REACH, WEEE, battery directive labelling.
- **Apple:** marketed as "MagSafe-compatible", not "Made for MagSafe" (an MFi programme term).
- **Test plan before release:**
  - attachment pull and shear;
  - drop;
  - thermal soak at 35 °C ambient with relaying and charging;
  - battery abuse;
  - HaLow range;
  - battery life against the power budget;
  - tick conformity: a radio capture shows the same pattern idle and busy, including with the SoM deliberately trying to send extra, oversized or misaddressed traffic (the guard must block all of it);
  - guard attestation: firmware hash matches the transparency log, counters match the capture.

## 9. Firmware

- **Names:** suñůlink shield is the display name only. Code, commands, packages and identifiers use the ASCII name `sunu`: the CAD package `hardware/sunu` (`uv run python sunu.py`), the firmware crates `sunu-*`, the `sunu` command on the device and on tatenan nodes, and the accessory identifier `nu.khensu.sunu`.

- **Guard firmware:** open Rust (`no_std`), under 20,000 lines, reproducible builds, ML-DSA-87 secure boot, updates need the release key and the owner's approval; debug fused off. Rules in `design/guard.md` section 5.

- tatenan in a reduced node profile: relay, mesh mailbox for the owner, public content cache, committee duty while charged and backhauled.
- Secure boot; A/B updates delivered over the khensu network, signed with ML-DSA-87; no vendor cloud.
- Node keys generated on the device and never exported.

## 10. Open items

1. Replace placeholder phone dimensions with Apple's accessory drawings for the first models (iPhone 18 Pro first, then standard iPhones) and regenerate.
2. Base plate retention: PSA perimeter bond now; decide whether to add a 0.3 mm ledge in the housing for location.
3. Cell supplier for 1.7–1.8 mm custom pouch cells in the slim cavity shape, with a minimum-thickness check.
4. Magnet array: MagSafe-compatible pole pattern and the 53 mm ring in the card; verify hold on target phones.
5. SAR and HaLow regulatory approval per launch market.
6. Model-specific button and port features for the silicone case.
7. Board layout to confirm the 34 × 14 × 1.6 mm envelope fits the SoM, the guard, both radios and the power path.
8. Radio parts with microcontroller host drivers for the guard (HaLow and Wi-Fi 6/Bluetooth) and their throughput behind SPI or SDIO.
9. Physical radio switch (`OPEN-QUESTIONS.md` 77a).
