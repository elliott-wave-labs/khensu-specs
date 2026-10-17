# nu.eyes (part of nu.devices)

Wearable sight + quiet sensing for khėnsu.ñü. Shown as **ñü.êýêš**; code/host `eyes` (`eyes.khensu.nu`). Family page: **nu.devices** (`devices.khensu.nu`). Sister: [nu.ears](../ears/SPEC.md). Fashion: [nu.aura](../../design/nu-aura.md). AI: [nu.ral](https://memory.khensu.nu).

**Status: design 15 October 2026.** Not built. Figures are design targets until measured. Page must not say patent pending.

> Agent rule (Elliott, 15 Oct 2026): do **not** commit or push this MD. Code may ship without review.

## 1. Wear as a set

One outfit of hardware — same Guard / HaLow / BLE / EdgeLock chip family as [suñůlink.shield](../sunu/SPEC.md). Mix and match; buy together on nu.devices at **cost + labour + 10%** (not 10×). Recycle preferred over repair.

| Piece | Default | Optional omit |
| --- | --- | --- |
| **Glasses (Club)** | Clear / sun-reactive glass, side **autodim** button, **4K** world cams, dry **EEG**, jawbone (bone-conduction) audio | No mic SKU (cam + EEG only) |
| **nu.ears** | Spatial audio, jawbone path, calls | **No camera** (never) |
| **Ring** | Sensing (EEG/pulse) **or** tiny 4K cam in stone | No-cam sensing-only |
| **Brooch** | Real crystal (not Swarovski-class fake) with optional cam | Sensing-only |
| **Necklace** | Moldavite in **silver**, stones + metal **touch skin**; EKG / Class 1 near-IR monitor in the **case** | — |
| **Bracelet** | Wrist pulse + motion, metal on skin | — |
| **suñůlink.shield** | Pocket mesh + battery | Phone-only mode |

Phone in pocket. Talk to glasses / ears. Heavy LLM = **nu.ral** on phone/shield — not in the frame.

## 2. Glasses — clear, autodim, 4K, jawbone, EEG

- **Lens:** clear / transparent by default; photochromic sun response; **side button** forces autodim for bright sun (electrochromic or LC film, mineral glass — no plastic stack if avoidable).
- **Cameras:** **4K** outward (stereo when the SKU carries two). Encrypted stream to phone/shield.
- **Audio:** **jawbone** bone conduction on the temple — private to the wearer.
- **EEG:** dry contacts in temples / nose pads; metal touches skin.
- **Mic:** optional. SKU without mic still has cam + EEG.
- **Chips:** same family as sunu — Guard (STM32U5 / i.MX 93 EdgeLock class), MM6108 HaLow, BLE (IW612 / nRF54), SE, ML-KEM-1024 sessions.
- **No LLM SoC in the glasses.**

Silhouette: Dior Club M1U class panoramic mask; **ÑÜ** mark. Optional Prada-class runway.

## 3. Materials — natural, vegan, skin contact

| Rule | Detail |
| --- | --- |
| Touch skin | Stones and metals contact skin. No plastic barrier, **no glue** in the skin path (mechanical set / friction / rivet / solder). |
| Vegan | No leather, bone, horn, shell, animal glue. Plant / mineral / metal only. |
| Zero carbon (design aim) | Recycled metals where possible; renewable process power; local CNC; ship density over air when we can. Measured footprint replaces the aim later. |
| Metals | Ti-6Al-4V ceramic powder coat, bare C26000 brass, pure Au / Pt / Ag. |
| Stones | Real moldavite, emerald, diamond, ñü.isheru set — not costume crystal. |
| Acetate | Prefer mineral glass + metal; if a front needs polymer, plant-based acetate disclosed — not default. |

## 4. Economics (nu.devices)

| Rule | Number |
| --- | --- |
| Device markup | **10%** on cost + labour |
| Not | Luxury 10× |
| Repair | Not recommended at this margin |
| Recycle | Yes — return nu.devices; compost organics in life generally :-) |
| Aura fashion fixed prices | $444 / $44k / $4.4m / $44m×3 still apply to show jewelry lines |
| Tips | 100% to the person; app IAP flat 10% |

## 5. Buy-now BOM (bench)

See earlier list: Muse / OpenBCI dry EEG, MAX86141 PPG, Class 1 850–940 nm VCSEL, micro-OLED or dim film eval, MM6108, nRF54/IW612, STM32U5 or i.MX 93, donor Club frame, Ti/brass/Au/Pt/Ag, real moldavite + silver for necklace prototype. Galea reference ~$43k or Discovery Program if useful.

## 6. Hosts

| Host | Until dig A → LB |
| --- | --- |
| `devices.khensu.nu` | apex `/devices` |
| `eyes.khensu.nu` | apex `/eyes` |
| `vegan.khensu.nu` | apex `/vegan` |
| `aura.khensu.nu` | dig OK; own cert PROVISIONING |

Never add NXDOMAIN hosts to the shared products SSL pack.
