# The khensu.nu Android OS (name pending)

Proposed 11 Oct 2026. A hardened Android for the khensu.nu phone, aiming past GrapheneOS: the same hardening, plus stealth networking through the khensu.nu mixnet, hardware privacy controls and the full Android app catalogue without giving Google a privileged place on the phone. Open decisions are in `OPEN-QUESTIONS.md`, section K. The phone is specified in `hardware/phone/SPEC.md`.

## 1. Starting point

- **Base:** the Android Open Source Project (AOSP), tracking each new release within weeks, the way GrapheneOS does.
- **What GrapheneOS already does well** and we keep as the baseline: hardened memory allocator (hardened_malloc), stricter SELinux and seccomp policies, per-app network and sensor permissions, storage and contact scopes, verified boot with the owner's keys, auto-reboot after a set time locked, USB-C data blocked while locked, PIN scrambling, duress PIN that wipes the phone, sandboxed Google Play (below), and fast security patches.
- **Why GrapheneOS stays on Pixels:** it needs hardware the OS can trust: a secure element with insider-attack resistance (Pixel's Titan M2), verified boot that accepts the owner's keys, an IOMMU that isolates the cellular modem and other radios, and at least 7 years of firmware updates from the chip maker. Our phone has to meet all of these, or the OS is weaker than GrapheneOS on a Pixel no matter what software we add. `hardware/phone/SPEC.md` section 4 sets them as hard requirements.
- **Licence:** AGPL-3.0 for our code, per the repo rules; AOSP parts stay Apache-2.0. We contribute general hardening fixes upstream to AOSP and offer them to GrapheneOS, credited.

## 2. What goes beyond GrapheneOS

1. **Stealth networking by default.** All app traffic can route through the khensu.nu mixnet per app (messages, browsing, app-store downloads), not just through a VPN. Cover traffic comes from the nodes, as in `PLAN.md`, so the phone doesn't burn battery on dummies. Apps that need low latency (calls, games) use the two-relay path from `design/stealth-relay.md`.
2. **Cellular privacy.** Rotating eSIM profiles, no permanent phone number needed, IMSI-catcher and fake base station detection with an alert, 2G off by default, and the modem isolated behind the IOMMU with no access to main memory.
3. **suñůlink built in.** The phone carries the suñůlink.shield transceiver inside (mesh, satellite and node mode), so there's no separate shield.
4. **Hardware privacy controls.** Physical switches cut power to the microphones, cameras and radios; the OS shows their state and can't override them (`hardware/phone/SPEC.md` section 6).
5. **Privacy display.** Pixel-level viewing-angle control on the panel, switched per app or automatically when a notification or password field shows (`hardware/phone/SPEC.md` section 3). Software adds a dimming mask and blurs previews; the angle control itself has to be in the panel.
6. **Private AI on the device only.** The same rule as the app: no server processing. Models run on the phone's neural processor.
7. **Encrypted everything, nothing on servers.** File-based encryption keyed by the secure element, encrypted backups only to the owner's own devices or nodes, and no cloud account needed to set up the phone.
8. **Personas.** Separate profiles with their own keys, network identities and apps, switched from the lock screen, with a hidden profile that a duress PIN never reveals.

## 3. Apps: the whole Android catalogue, Google unprivileged

- **Sandboxed Google Play**, as GrapheneOS ships it: the Play Store and Play services run as ordinary apps with no special permissions, so the full Play catalogue installs and works, including Spotify. Users who don't want it never install it.
- **Limits to state honestly:** Google certifies Android phones that ship Google apps by default (GMS licensing). A phone that puts Google in a sandbox isn't certified, so a few apps that require Google's Play Integrity "strong" verdict (some banking, payment and streaming apps) may refuse to run. GrapheneOS lists the affected apps; we'd publish the same list and push app makers to accept hardware attestation from our secure element instead.
- **Our own store:** webË apps and Android apps from developers who publish to us directly, signed and reproducibly built where possible, downloaded through the mixnet.
- **Music and video:** a Spotify equivalent means licensing catalogues from the major labels and publishers, which is a multi-year, nine-figure undertaking with minimum guarantees. Until then: Spotify, Apple Music, YouTube Music and others run as normal apps through sandboxed Play, and khensu.nu carries creators' own music, video and livestreams with subscriptions and per-purchase paywalls, paid through the shielded pool. A licensed catalogue is open question K5.

## 4. Updates and trust

- Monthly security releases and same-week fixes for critical bugs, signed with the founder threshold key, with build hashes in a binary transparency log and reproducible builds.
- At least 7 years of OS and firmware updates per phone, which depends on the chip maker's support contract (`hardware/phone/SPEC.md` section 4).
- Owners can lock the bootloader to their own keys or to ours, and can verify the running build with hardware attestation from another device.

## 5. Not decided

Name, chip vendor, and the questions in `OPEN-QUESTIONS.md` section K.
