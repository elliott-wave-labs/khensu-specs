# khensu guard: hardware-enforced cover

Draft 0.1, 10 October 2026. **Decided** (`OPEN-QUESTIONS.md` 77): every khensu hardware device has a guard. It's a core feature, not an option.

## 1. What it is

The guard is a small, separate chip that owns every network path out of a khensu device. The main computer has no radio and no network interface of its own; it can only hand packets to the guard. The guard sends exactly the fixed-size packets on the fixed schedule that the protocol requires, and nothing else.

Stealth today rests on software doing the right thing. The guard makes it rest on hardware: even if the main computer is fully compromised (a kernel exploit, a malicious update, a supply-chain implant), it can't leak anything through packet sizes, timing, bursts or extra connections, because it can't reach a radio except through the guard.

## 2. What it protects against

| Threat | Without a guard | With a guard |
| --- | --- | --- |
| Compromised main computer sends extra traffic, bursts or odd sizes that reveal activity or encode data | Possible | Blocked: only fixed sizes on the fixed tick leave the device |
| Compromised main computer opens a direct connection to an attacker | Possible | Blocked: no network path except through the guard, which only sends to the current entry nodes |
| Compromised radio firmware reads keys or messages from memory | Possible over buses with direct memory access | Blocked: radios sit behind the guard on buses with no access to the main computer's memory |
| Compromised radio firmware learns content or activity | Sees what software gives it | Sees only sealed fixed-size packets on a constant schedule |
| Malicious firmware or parameter update slows the tick on low battery, or adds a "debug" channel | Possible | Blocked: the guard enforces fixed bounds and accepts schedule changes only with committee signatures |
| Physical attacker probes debug ports | Possible | Production devices have debug fused off on both chips |

**What it doesn't stop:**
- **Radio-level presence.** Wi-Fi, Bluetooth and HaLow management frames (beacons, probes, acknowledgements) come from the radio chips themselves, so someone nearby with a scanner can tell a device is there. MAC addresses rotate.
- **Content leaks by a compromised main computer through the protocol itself**, for example by sending real messages to an attacker inside correctly formed sealed packets. The guard enforces the pattern, not the meaning; end-to-end protections and the threat model cover the rest.
- **A compromised guard.** That's why its firmware is small, open source, reproducibly built and verified at every boot (section 6).

## 3. Architecture

```text
            ┌───────────── khensu device ─────────────┐
            │                                          │
 main       │  SoM (Linux, tatenan)                     │
 computer   │     │  SPI, guard protocol only           │
            │     ▼                                    │
 guard      │  Guard (MCU or FPGA, open firmware)      │──── radio power rails, resets
            │     │ SPI / SDIO host        │           │
            │     ▼                        ▼           │
 radios     │  HaLow radio        Wi-Fi 6 + BLE radio  │
            │                                          │
            └──────────────────────────────────────────┘
```

- **One way in and out.** The SoM connects only to the guard, over SPI. SPI has no direct memory access from the far side, so neither the guard nor anything behind it can read SoM memory.
- **The guard is the radios' host.** Radios hang off the guard's SPI or SDIO host ports. The SoM has no bus to them, no reset line and no power control.
- **Power control.** The guard switches the radio power rails and holds them in reset until its own boot checks pass.
- **USB-C** carries power only at launch. If USB data is added later, it goes through the guard like every other link.
- **Keys** live in the SoM's secure enclave (tatenan's node keys) and the guard's own secure storage (the guard's identity and update keys). Radios never see a key.

## 4. Two guard classes

| Class | Used in | Part (candidates, to be verified) | Throughput | Power |
| --- | --- | --- | --- | --- |
| **Guard-M** (microcontroller) | Shell, portable devices | Cortex-M33 with TrustZone, TRNG, AES and SHA acceleration, SPI and SDIO host (e.g. STM32U5 class) | Up to about 40 Mbit/s over SPI, enough for a shell's mesh and Wi-Fi share | About 20–50 mW |
| **Guard-F** (FPGA) | Home node, portals | Lattice ECP5 class, sitting between the SoC and the Ethernet PHY and radios; fully open toolchain (Yosys, nextpnr) so the bitstream can be audited and rebuilt | Gigabit line rate | About 0.3–1 W |

Phones and Macs can't carry a guard. There, tatenan and the app enforce the same rules in software, and `THREAT-MODEL.md` states the difference.

**Radio fit for Guard-M:** the HaLow and Wi-Fi/Bluetooth radios must run with a microcontroller host (their drivers on the guard, not on Linux). Morse Micro HaLow chips and some Wi-Fi 6/Bluetooth chips offer microcontroller host drivers; picking parts that do is a board requirement (open item).

## 5. Rules the guard enforces

The rules live in guard firmware and a signed parameter set. The SoM can't change them.

**5.1 Egress shape**
- **Fixed frame sizes.** Each link has a small set of allowed datagram sizes from the parameter set (for the shell's internet link: the small-packet size; bulk size only on approved constant streams). Undersized frames are padded with random bytes after the sealed packet; oversized frames are dropped and counted.
- **Fixed schedule.** Each link sends exactly the configured number of frames per tick (internet link: 4 small packets per 2 s tick; HaLow mesh: 1 per tick), at times jittered by the guard's own random number generator (±100 ms). The SoM can't send early, late, more or less.
- **Empty slots are filled.** The SoM keeps a pool of valid cover packets topped up in the guard. If the pool runs dry, the guard sends random bytes of the right size to the same peer, so the outside pattern never changes (the first hop can tell; nobody else can).
- **Queues are bounded.** Extra frames wait for the next free slot up to a small limit, then are dropped. Real traffic never changes the pattern; it only takes slots that cover would have used.
- **Destinations.** Internet frames go only to the entry nodes listed in the current signed epoch header (plus the user's own node, if registered). Anything addressed elsewhere is dropped.
- **Constant streams.** Bulk-packet streams (own node, the Wi-Fi-and-charging window, call trunks) run at the constant rate the parameter set allows for each stream type, padded when idle, and start and stop only on epoch-aligned boundaries.

**5.2 Battery and heat never change the pattern**
- The schedule doesn't depend on battery level, temperature or power source. The guard has no input from the power system that could slow the tick.
- If the device can't sustain the schedule (cells empty and no phone power), the guard stops all links together and restarts on a tick boundary, rather than thinning traffic.

**5.3 Ingress**
- Inbound frames must match the allowed sizes; others are dropped before reaching the SoM. This shrinks the SoM's attack surface.
- Inbound rate is capped to protect the SoM from floods.

**5.4 Parameter changes**
- Tick length, burst size, frame sizes and stream rates come from the network's consensus parameters. The guard accepts a new parameter set only inside an epoch header carrying a valid threshold of committee ML-DSA-87 signatures, checked by the guard itself.
- Hard bounds in firmware that no parameter set can cross: tick between 1 and 2 s, no battery or temperature dependence, no destination outside the epoch's entry-node list, no unpadded frames.

## 6. Guard firmware

- **Open source, small and auditable.** Target under 20,000 lines of Rust (embedded, `no_std`), published in `khensu-tatenan` (or a dedicated repo) with reproducible builds. Guard-F gateware is published with its open toolchain build.
- **Secure boot.** The guard verifies its own firmware with ML-DSA-87 at every boot before powering any radio. Production parts have debug ports fused off.
- **Updates** need two signatures: the khensu release key and the device owner's approval from the paired app. A failed update rolls back to the previous image (A/B slots).
- **Transparency.** Every guard firmware hash is published in the key transparency log; the app compares the guard's reported hash against the log.

## 7. Verification by the owner

- The guard keeps counters per link: frames sent, padded, filled from the pool, filled with random bytes, dropped (oversize, wrong destination, queue full). The paired app shows them.
- A radio capture of a device, idle or busy, must show the same pattern. This is part of the hardware test plan (`hardware/sunu/SPEC.md` section 8) and of certification for any third-party khensu hardware.
- The guard signs a short attestation (firmware hash, parameter-set epoch, counters) that the app checks against the transparency log.

## 8. Cost

| Item | Shell (Guard-M) | Home node (Guard-F) |
| --- | --- | --- |
| Parts | About $3–6 | About $15–30 |
| Board area | About 5 × 5 mm package plus passives | About 10 × 10 mm BGA plus memory |
| Power | About 20–50 mW | About 0.3–1 W |

## 9. Open items

1. **77a, physical radio switch:** a slide switch that cuts the radio power rails in hardware, independent of both chips. Open.
2. Radio parts with microcontroller host drivers for Guard-M (HaLow and Wi-Fi 6/Bluetooth), and their real throughput behind SPI or SDIO.
3. ML-DSA-87 verification time on the chosen Guard-M part for a committee threshold (estimated well under a second, once per parameter change).
4. Guard-F board design on the home node carrier (Ethernet PHY behind the FPGA).
5. Whether third-party khensu hardware must include a guard to earn as a node (rec: required for the "khensu hardware" mark, not for running tatenan on your own computer).
