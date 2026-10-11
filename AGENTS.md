# khensu.nu

Post-quantum private messenger on a decentralized operator network. `PLAN.md` is the source of truth; where it describes a single `moqom-messenger` repo, the repo split below replaces that layout.

## Repos (all under `elliott-wave-labs`, cloned side by side in `~/Documents/GitHub/khensu/`)

| Repo | Contents |
| --- | --- |
| `khensu-specs` | Plan, threat model, protocol specs, App ID guide, design canvas, this file, the multi-root workspace |
| `khensu-core` | Apache-2.0. Rust: OpenMLS fork with the ML-KEM-1024 + ML-DSA-87 suite, credentials, Outfox mixnet packets, consensus wire format, shielded-note formats, KhensuMemory index engine, vectors. Exposed to Swift with UniFFI as an XCFramework |
| `khensu-apple` | SwiftUI app `nu.khensu.ptah` for iPhone, iPad and Mac, Notification Service Extension, Share Extension |
| `khensu-tatenan` | Node `nu.khensu.tatenan` for Mac and Raspberry Pi 5: mixnet, mailbox, call relay, work receipts |
| `khensu-chain` | Post-quantum chain, token, shielded pool |
| `khensu-services` | Go: key transparency log, credential issuer, push gateway, MOTOM integration |
| `khensu-devnet` | Runs node, mixnet, chain and push gateway on one machine for development |
| `khensu-site` | `khensu.nu` and `tatenan.khensu.nu` |

## Fixed decisions

- MLS suite `MLS_256_MLKEM1024_AES256GCM_SHA512_MLDSA87` (pure post-quantum, same as MOQOM Cloud); ML-DSA-87 for every signature.
- Message signatures live inside the ciphertext only; every message gets its own key; signature and device keys rotate at least every 5 minutes or 1,000 messages and are revealed to the group after 7 days.
- All messages go through the mixnet; only calls use two relays run by different operators.
- Nothing is processed on servers: no Siri, no Private Cloud Compute, no Writing Tools in the composer, no iCloud.
- Minimum iOS, iPadOS and macOS 26. Stock Liquid Glass chrome only (see the App design section of `PLAN.md`).
- The hardware transceiver is shown as suñůlink.shield; code, commands, packages and identifiers use `sunu` (`hardware/sunu`, `nu.khensu.sunu`).
- The open web layer is shown as webË (E with a diaeresis, U+00CB); schemes, files and identifiers use `webe` (`webe://`, `WEBE.md`).
- "nu" is shown as ñü wherever people see it (khensu.ñü, ñü.media, ñüFi, ñüCode); code, URLs, domains, files and data keys keep `nu`.
- Site work is published as soon as it's built, to every site including the studio; it is never held for a patent filing.
- The network is a gift to humanity and all beings: freedom and privacy, plus a universal basic income, so people everywhere can create, build and live securely. Never phrase it as "can't be stopped". A founder dead-man's switch (weekly check-ins, fires after 42 days of silence or on handover) passes every founder power to consensus for good. Every code change, release and upgrade is archived on the network automatically; when the switch fires, the trusted committee nodes open the sealed escrow of all private code, patented code included, and release everything to every node, the founder's list of friends, the press (WSJ, Forbes), Wikimedia Commons and the Internet Archive (`PROTOCOL.md` 12.5–12.7).
- App commerce: a flat 10% of in-app purchases and subscriptions, never scaled up or down; tips stay 100% to the person.
- Commands for the private AI agents and the node terminal start with `~` (`~summarize`, `~node status`), never `/`.
- Permanent handles are `name.khensu.nu`, resolved from the key transparency log over the mixnet.
- Apple Team ID `LHS49D8RYY`. Licences: `khensu-core` Apache-2.0, `khensu-specs` CC BY 4.0, all other repos AGPL-3.0, CLA for outside contributors.
- Every component gets a full design doc and a patent assessment (`PATENTS.md`) once built, before any repo goes public.
