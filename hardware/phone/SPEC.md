# The khensu.nu phone (name pending): product specification

Proposed 11 Oct 2026. Our own phone for the khensu.nu Android OS (`design/os.md`): a titanium or brass body with the khensu.nu stone inlay on every phone, the best sensors of the current Samsung Galaxy S Ultra, iPhone Pro and Pixel Pro, a privacy display, hardware kill switches and suñůlink built in. Open decisions are in `OPEN-QUESTIONS.md`, section K. Every figure here is a target until it is measured on a prototype.

## 1. Body and materials

| Option | Finish | Notes |
| --- | --- | --- |
| **Solid brass** (kept, decided) | Bare, uncoated, brushed | Brass that is at least 60% copper is inherently antimicrobial when bare: copper alloys are registered with the US EPA (for example CuVerro) as killing 99.9% of certain bacteria within 2 hours, and the effect is permanent because it comes from the metal. Any coating or lacquer stops it, so brass must stay uncoated. It darkens to a patina and shows fingerprints, which a quick polish removes; the patina doesn't stop the antimicrobial effect. Reads as a gold phone. Heavier (density about 8.5 g/cm³ against titanium's 4.5). |
| **Titanium, ceramic coat** | Maroon, gold, black | Grade 5 titanium with a hard ceramic coating; the coating hides fingerprints and resists scratches. Not antimicrobial by itself. |
| **Titanium, antimicrobial coat** (proposed option) | As above | A ceramic coat with an EPA-registered antimicrobial agent bound in, the kind used on public touch surfaces since 2020: silver-ion or copper-infused coatings, or a photocatalytic titanium dioxide layer that works under light. These wear over years, unlike bare brass, and any public health claim needs the coating's own EPA registration (and EU Biocidal Products Regulation approval in Europe), so we only use already-registered coatings and repeat their exact approved wording. Likely cheaper than brass. |

- **Inlay on every phone:** the khensu.nu mark in stone with the platinum line, set flush into the back as on suñůlink.shield (lapis, black and white labradorite, bloodstone, onyx, kyanite, tourmaline; moldavite and Paraíba as a tier).
- **Durability, not "indestructible":** no phone is indestructible, so we never say it. Targets: IP68 and IP69, MIL-STD-810H drop and shock procedures, a 2 m drop onto concrete without a cracked screen (the best phones today manage about 1–2 m), Corning Gorilla Armor-class or sapphire cover glass, and a titanium frame. The stone inlay is softer than the metal; it is sealed and may show fine wear, as the shield page says.

## 2. Sensors: the best of Samsung, Apple and Google, then more

Matched against the Galaxy S Ultra, iPhone Pro and Pixel Pro current at design freeze, taking the best of each:

- **Main camera:** a 1-inch-type sensor (Sony LYT-900 class or newer), larger than any of the three uses today.
- **Telephoto:** a periscope at 5× or more with a large sensor, plus a 3× (Samsung keeps two telephotos; Apple and Google one).
- **Ultra-wide:** 50 MP with autofocus for macro.
- **Front:** autofocus, 4K60.
- **Depth:** a LiDAR or time-of-flight scanner (Apple has LiDAR), used for AR, focus and secure face unlock.
- **Face unlock:** structured-light 3D face unlock with a secure pipeline into the secure element, which Android flagships lack today (Pixel and Galaxy face unlock are camera-only, apart from the Pixel 4).
- **Fingerprint:** Qualcomm 3D Sonic ultrasonic under the display (Samsung's), which works with wet fingers.
- **Radios:** 5G with satellite messaging (NTN), Wi-Fi 7, Bluetooth 6, UWB, NFC, Thread, plus suñůlink's mesh and satellite radio built in.
- **Also:** barometer, thermometer, magnetometer, high-rate IMU for stabilisation, and a hardware true random number generator in the secure element.

## 3. Display

- **Panel:** the same Samsung Display flagship OLED family as the top Galaxy S Ultra: LTPO 1–120 Hz, about 2,600 nits peak or more, anti-reflective cover.
- **Privacy display:** Samsung has built viewing-angle control into the panel's pixels ("Flex Magic Pixel", in the Galaxy S Ultra line), so the screen can turn private for people beside you. A software filter alone can only dim or blur the screen; it can't narrow the viewing angle. So we need that panel feature, which means buying it from Samsung Display (open question K3), with the OS switching it per app and automatically for passwords and notifications.
- **Holograms:** true holograms aren't possible on a phone screen today. What is possible is a glasses-free 3D light-field mode, where a lens layer over the panel shows depth (Leia's displays, as in RED's Hydrogen One, and Looking Glass at larger sizes). Earlier attempts traded away 2D sharpness and battery, and the Hydrogen One sold poorly, so we treat it as a research track: a switchable layer that doesn't cost 2D sharpness, for 3D messages, video calls and the LiDAR captures. Decision in K4.

## 4. Security hardware (required for the OS to beat GrapheneOS)

These are hard requirements. Without them the OS is weaker than GrapheneOS on a Pixel, whatever the software does.

- **Secure element** with insider-attack resistance (firmware can't be updated without the owner's PIN), our own or a certified part (Common Criteria EAL5+ or higher), holding disk keys, attestation keys and throttling PIN guesses.
- **Verified boot** that accepts the owner's own keys and shows them at boot.
- **IOMMU isolation** for the cellular modem, Wi-Fi, Bluetooth, GPU and every other component with direct memory access.
- **Memory tagging** (Arm MTE) on by default, which GrapheneOS uses on recent Pixels.
- **At least 7 years of firmware and driver updates** from the chip maker, in the contract.
- **Chip:** the flagship Qualcomm Snapdragon (as in the Galaxy S Ultra) or MediaTek Dimensity; Google's Tensor isn't sold to others. Choice in K1, judged on these requirements first.

## 5. suñůlink inside

The suñůlink.shield electronics (mesh radio, satellite link, node mode, extra battery) move inside the phone, so the phone is a khensu.nu node by itself and earns like one when it's charging, under the same rules as `PLAN.md`.

## 6. Privacy switches

Three hardware switches on the frame: microphones, cameras and radios. Each cuts power in hardware; the OS reads their position but can't change it. The radio switch leaves the suñůlink mesh on only if the owner chooses that in setup.

## 7. Price

Priced close to cost, as on the shield: a published expected cost per phone and a few percent above it. Expected cost needs quotes for the panel, chip, cameras and machining (K6).

## 8. Open items

Name, chip, panel supply, hologram track, music licensing, cost quotes, the antimicrobial titanium option, and certification (FCC, CE, carrier approvals). See `OPEN-QUESTIONS.md` section K.
