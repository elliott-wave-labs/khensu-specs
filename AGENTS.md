# khensu.nu

Post-quantum private messenger on a decentralized operator network. `PLAN.md` is the source of truth; where it describes a single `moqom-messenger` repo, the repo split below replaces that layout.

## Repos (all under `elliott-wave-labs`, cloned side by side in `~/Documents/GitHub/khensu/`)

| Repo | Contents |
| --- | --- |
| `khensu-specs` | Plan, threat model, protocol specs, App ID guide, design canvas, this file, the multi-root workspace |
| `khensu-core` | Rust: ML-KEM-1024 / ML-DSA-65 suite, MLS, Outfox mixnet packets, wallet and shielded notes, on-device memory index. Exposed to Swift with UniFFI as an XCFramework |
| `khensu-apple` | SwiftUI app `nu.khensu.ptah` for iPhone, iPad and Mac, Notification Service Extension, Share Extension |
| `khensu-tatenan` | Node `nu.khensu.tatenan` for Mac and Raspberry Pi 5: mixnet, mailbox, call relay, work receipts |
| `khensu-chain` | Post-quantum chain, token, shielded pool |
| `khensu-devnet` | Runs node, mixnet, chain and push gateway on one machine for development |
| `khensu-site` | `khensu.nu` and `tatenan.khensu.nu` |

## Fixed decisions

- Pure ML-KEM-1024 for key exchange (no classical hybrid), ML-DSA-65 signatures, AES-256-GCM.
- All messages go through the mixnet; only calls use two relays run by different operators.
- Nothing is processed on servers: no Siri, no Private Cloud Compute, no Writing Tools in the composer, no iCloud.
- Minimum iOS, iPadOS and macOS 26. Stock Liquid Glass chrome only (see the App design section of `PLAN.md`).
- Permanent handles are `name.khensu.nu`, resolved from the key transparency log over the mixnet.
- Apple Team ID `LHS49D8RYY`. License AGPL-3.0.
