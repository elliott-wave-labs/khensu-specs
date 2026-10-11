# khensu shell: product specification

Revision A, 10 October 2026. **Preliminary.** Phone interface dimensions are placeholders until they are replaced with Apple's Accessory Design Guidelines drawings for each target model. Electrical figures marked *estimate* are to be measured on the first boards.

The khensu shell is a mesh node that attaches to the back of an iPhone. It relays sealed khensu packets over Wi-Fi HaLow to nearby shells and home nodes, reaches the internet through the phone or Wi-Fi, wakes the phone over Bluetooth instead of Apple's push service, and earns from token burning like any node. Background in `design/mesh.md` section 6.

## 1. Deliverables

| File | Contents |
| --- | --- |
| `drawings/khensu-shell-drawings.pdf` | All 18 sheets, A3, third-angle projection |
| `drawings/<phone>/KS-<phone>-<style>-100.dxf` | Assembly: views, section with balloons, parts list |
| `drawings/<phone>/KS-<phone>-<style>-101.dxf` | Housing detail for CNC: dimensions, windows, sections, isometric |
| `drawings/<phone>/KS-<phone>-CASE-201.dxf` | Silicone shock case for moulding |
| `out/<phone>/<style>/*.step`, `*.stl` | Every part as a separate solid (STEP governs undimensioned geometry) |
| `out/summary.json` | Computed volumes, battery, mass and interference check |
| `shell.py`, `drawings.py` | Parametric source; rerun after changing any dimension |

DXF files are AutoCAD R2018, millimetres, with native DIMENSION and HATCH entities on standard layers (OUTLINE, HIDDEN, CENTER, SECTION, HATCH, DIM, TEXT, BORDER, TITLE). They open directly in AutoCAD, Fusion, SolidWorks, DraftSight and LibreCAD.

## 2. Variants

| Style | Phone | Footprint (mm) | Thickness (mm) | Cells | Mass (titanium) | Attachment | Drawings |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Card | iPhone 18 Pro | 56 × 86 | 5.2 | 4.1 Wh | 50 g | Magnets (53 mm ring) | KS-IPHONE-18-PRO-CARD-100/101 |
| Fill | iPhone 18 Pro | 65.9 × 101.9 | 3.4 (+0.4) | 2.1 Wh | 47 g | Magnets and suction | KS-IPHONE-18-PRO-FILL-100/101 |
| Wrap | iPhone 18 Pro | 71.1 × 149.2, long camera cut-out | 3.4 (+0.4) | 2.7 Wh | 58 g | Magnets and suction | KS-IPHONE-18-PRO-WRAP-100/101 |
| Wrap XL | iPhone 18 Pro | 71.1 × 149.2, long camera cut-out | 6.4 (+3.4) | 11.3 Wh | 109 g | Magnets and suction | KS-IPHONE-18-PRO-WRAP-XL-100/101 |
| Card | Standard | 56 × 86 | 5.2 | 4.1 Wh | 50 g | Magnets (53 mm ring) | KS-ISLAND-CARD-100/101 |
| Fill | Standard | 65.5 × 100.5 | 3.4 (+0.8) | 2.0 Wh | 46 g | Magnets and suction | KS-ISLAND-FILL-100/101 |
| Wrap | Standard | 70.7 × 146.8 | 3.4 (+0.8) | 3.5 Wh | 65 g | Magnets and suction | KS-ISLAND-WRAP-100/101 |
| Wrap XL | Standard | 70.7 × 146.8 | 6.4 (+3.8) | 13.4 Wh | 123 g | Magnets and suction | KS-ISLAND-WRAP-XL-100/101 |
| Silicone case | Both | phone + 1.6 per side | phone + module + 0.8 | (holds a Wrap) | about 18 g | Grips the phone | KS-*-CASE-201 |

"+" is height above the camera bump. The slim styles have a 3.4 mm floor (suction film 0.3, base 0.6, board 1.6 with 0.2 clearance, skin 0.7), so on phones with a lower bump they sit slightly proud. Cell energy assumes 0.45 Wh/cm³ for thin pouch cells.

## 3. Mechanical

**Construction stack (phone side outward):** micro-suction film 0.3 → base plate 0.6 → cavity (magnet ring 0.5, board 1.6, cells, Qi2 coil 0.8 under the skin) → graphite sheet 0.025 → skin 0.7. Side walls 1.0.

| Item | Material | Process and finish | Notes |
| --- | --- | --- | --- |
| Housing | Ti-6Al-4V Grade 5 titanium (only material), "titanium battleproof shell" | 5-axis CNC; bead blast and space gray PVD | 0.7 mm skin needs a vacuum fixture; 0.8–1.0 mm is safer for first articles |
| Windows | PC, UL94 V-0, colour matched | Insert-moulded or bonded, flush within 0.02 | Ø46 over the coil (skin only); 42 mm strip along the bottom edge (skin and wall) for the antennas |
| Base plate | PC-GF30 | Moulded or CNC | Bonded with a 0.1 mm PSA perimeter bead |
| Suction film | Nano-suction PU | Die cut, laminated to base | Washable; replaceable part |
| Magnet ring | NdFeB N52, Ni-Cu-Ni plated, segmented | Bought in | MagSafe-compatible array; 56/46 mm (53/43 mm in the card) |
| Silicone case | LSR, Shore 55A ±5 | Injection moulded, VDI 27 texture | Add 0.5–1° draft; button covers per model |

**Tolerances:** ISO 2768-mK general; phone interface features (outline, camera cutout, MagSafe axis) ±0.05; camera clearance 0.6 per side; window flushness 0.02.

**Attachment targets (to validate):** normal pull-off at least 10 N on magnets alone and 25 N with suction; shear at least 15 N; no creep over 24 h at 40 °C; repeated attach/detach 5,000 cycles without film loss.

**Phone connection:** the fill, wrap and XL have a USB-C receptacle on the bottom edge and connect to the phone's port with a short right-angle USB-C jumper (included). The silicone case can integrate the plug in its lip. The card has no connector.

## 4. Electrical

**Architecture (decided):** one Linux system-on-module, always on while attached, and a guard chip that owns both radios (`design/guard.md`). The SoM has no radio or network interface of its own: it talks only to the guard over SPI, and the guard is the radios' host and controls their power. The 2 s tick never changes with battery level.

| Block | Choice (candidates) | Notes |
| --- | --- | --- |
| Application processor | Low-power Cortex-A55 class SoM (e.g. NXP i.MX 93) | Runs tatenan in a reduced node profile; secure boot |
| Memory | 2 GB LPDDR4X, 32 GB eMMC | Encrypted outbox, inbox and content cache |
| Guard (Guard-M) | Cortex-M33 with TrustZone, TRNG, AES/SHA acceleration, SPI and SDIO host (e.g. STM32U5 class) | Open Rust firmware; enforces frame sizes, the tick, destinations and signed parameters; ML-DSA-87 secure boot; holds radios in reset until its checks pass |
| Mesh radio | Wi-Fi HaLow (802.11ah) module (e.g. Morse Micro MM6108 based), hosted by the guard | Pre-certified module; must support a microcontroller host |
| Wi-Fi and Bluetooth | Wi-Fi 6 and Bluetooth LE 5.3 combo with a microcontroller host driver, hosted by the guard | Link to the phone and nearby devices; Bluetooth wakes the app |
| Power path | 1S charger with power-path, USB-C PD dual-role controller, fuel gauge | Charges from USB-C or Qi2; powers the board from the phone when cells are empty |
| Wireless charging | Qi2-certified receiver module, coil under the skin window | The shell charges itself; it does not pass charge wirelessly to the phone |
| Cells | 1S Li-ion pouch, 3.85 V nominal, custom shape to the cavity | Protection circuit on board; NTC on the pack; 1.7–1.8 mm thick in slim styles |

**Power budget (estimate, to be measured):**

| Load | Average |
| --- | --- |
| SoM running the node profile | 0.4–0.6 W |
| HaLow at a 2 s mesh tick plus relaying | 0.15–0.4 W |
| Wi-Fi and Bluetooth to the phone | 0.05–0.2 W |
| Guard | 0.02–0.05 W |
| **Total** | **about 1 W** |

At about 1 W and 85% conversion efficiency, a slim shell runs about 1.7–3 hours on its own cells, the card about 3.5 hours, the iPhone 18 Pro XL about 10 hours and the standard XL about 11 hours. After that, the fill, wrap and XL draw about 1 W from the phone over USB-C (roughly 6–7% of a Pro iPhone's battery per hour), and the card stops.

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
