# Work in progress — AM launch (Product Hunt after Apple)

**Rule:** Elliott reviews + commits docs. Publish / SSL / device install OK without commit. Do not push app code unless asked.

## App naming (target)

People / App Store product names: **`nu.<product>`**.

| Store / product name | Bundle ID (target) | App Group | Role |
| --- | --- | --- | --- |
| khensu.nu (messenger + feed) | today `nu.khensu.ptah` | `group.nu.khensu.ptah` | Chats, calls, feed, Ask khensu |
| nu.waves | `nu.khensu.waves` | same App Group | Spatial music |
| nu.create | register `nu.khensu.create` | **same App Group** | Creators / pay / rights |
| nu.moments | register `nu.khensu.moments` | **same App Group** | Templify-class editor |
| ñü.ævätåřş | **not** a separate App Store app | — | Styles inside calls + moments/create |

## Submit checklist (this AM, before 7am PDT)

1. **Organizer → Distribute App** for Ptah (`nu.khensu.ptah` 0.1.0/3) and Waves (`nu.khensu.waves` 0.1.0/3). Archives on Desktop under `khensu-*-submit/`. CLI blocked until Elliott Wave ASC key + **Issuer ID** exist for team `LHS49D8RYY` (Downloads AuthKeys are other teams).
2. **Product HTTPS** — **done** (both ACTIVE, matching CN, bi still `CN=bi.khensu.nu`).
3. **GitHub install** — already live at release `0.1.0-build3`; hub https://khensu.nu/app
4. **15 Pro** — both apps installed over Wi‑Fi (done).
5. **Register App IDs** when ready: `nu.khensu.moments`, `nu.khensu.create` + App Group membership.
6. **IETF** — hold draft-staffer-link-preview-media-00.
7. **Terraform** — sites module now attach-then-wait for own certs; after certs ACTIVE, import manual cert names or bump `certificate_epoch` and reconcile (quota 10). Do not apply a plan that detaches working certs.

## Certs in flight (manual bootstrap)

| Host | Cert name | Notes |
| --- | --- | --- |
| avatars.khensu.nu | `moqom-avatars-khensu-nu-2dcc63e6` | Attached; was PROVISIONING (not FAILED) |
| indra.og.khensu.nu | `moqom-indra-og-khensu-nu-1297f1f3` | Attached; explicit Cloud DNS A + `*.og.khensu.nu` |

## IP / patent notes (do not say “patent pending” on pages)

| Topic | Doc | Status |
| --- | --- | --- |
| ñü.ævätåřş on-device styles + stealth packing | `design/nu-avatars.md`, `PATENTS.md` | Browser + call path shipped |
| nu.indra.og mute-loop cards | `design/indra.md` | Trade dress / copyright |
| nu.moments editor / templates | `design/nu-moments.md` | Design; assess before claim language |
| Captions / translate on device | apple commit 702bc5f | Shipped |

## Blockers

| Blocker | Action |
| --- | --- |
| No Elliott Wave ASC Issuer ID | Create key in App Store Connect → Users and Access → Keys; or Distribute from Organizer |
| moments / create IPAs | Build after push hold lifted |
| ~~Product host certs~~ | Cleared — avatars + indra.og ACTIVE |
| No Apple Distribution identity in keychain (only Development) | Organizer Distribute uses Apple’s cloud signing when signed into Xcode with team `LHS49D8RYY` |

## Related

See `work-completed.md`. Skills: `nu-harness`, `publishing-khensu-sites`, `khensu-work-log`.
