# Work completed — 14–15 October 2026 (AM launch push)

Session close-out for agents and humans. Elliott commits after review. **Publish / SSL / device install done here; no further code push unless asked.**

## What “Ptah” is in Xcode Organizer

| What you see | Meaning |
| --- | --- |
| Scheme / archive name **Ptah** | Internal Xcode target name for the messenger |
| Display name **khensu.nu** | What people see on the Home Screen |
| Bundle ID **`nu.khensu.ptah`** | Current App Store / signing identifier |
| Version **0.1.0 (3)** | Build ready to Distribute |

Product apps people know as **`nu.*`**:

| Product | Host / page | App / surface today |
| --- | --- | --- |
| nu.waves | waves.khensu.nu | Standalone `nu.khensu.waves`, App Group `group.nu.khensu.ptah` |
| nu.create | create.khensu.nu | Site (+ Indra cards, **#numbers-section**); no separate IPA yet |
| nu.moments | moments.khensu.nu | Design + site; IPA not built — Templify-class editor |
| ñü.ævätåřş | avatars.khensu.nu | Site studio + **in-call styles** inside messenger; not a separate store app |
| nu.indra.og | indra.og.khensu.nu | Site product (îňðřæ.ōġ); mute-loop OG cards |
| Messenger / feed | khensu.nu | Ptah / `nu.khensu.ptah` — chats, calls, feed |

## Device install (Wi‑Fi)

| Device | Apps | Version |
| --- | --- | --- |
| Elliott’s 15 Pro (`A2A9915C-…`, UDID `00008130-00017561118B803A`) | `nu.khensu.ptah` (khensu.nu), `nu.khensu.waves` | 0.1.0 (3) |

Installed over localNetwork via `xcrun devicectl` from:

- `~/Desktop/khensu-ptah-submit/Ptah.xcarchive/Products/Applications/khensu.nu.app`
- `~/Desktop/khensu-waves-submit/Waves.xcarchive/Products/Applications/nu.waves.app`

Both launched successfully after install.

## Live sites

| URL | Notes |
| --- | --- |
| https://khensu.nu/avatars | Apex always-live fallback |
| https://avatars.khensu.nu | **LIVE** — `CN=avatars.khensu.nu`, HTTP/2 200 (cert `moqom-avatars-khensu-nu-2dcc63e6`) |
| https://khensu.nu/indra | Apex fallback |
| https://indra.og.khensu.nu | **LIVE** — `CN=indra.og.khensu.nu`, HTTP/2 200 (cert `moqom-indra-og-khensu-nu-1297f1f3`) |
| https://create.khensu.nu/#numbers-section | Keep |
| https://khensu.nu/app | GitHub install hub |
| https://bi.khensu.nu | Must stay `CN=bi.khensu.nu` during own-cert attach |

## GitHub install

| Asset | URL |
| --- | --- |
| Release | https://github.com/elliott-wave-labs/khensu-apple/releases/tag/0.1.0-build3 |
| Messenger IPA | https://github.com/elliott-wave-labs/khensu-apple/releases/download/0.1.0-build3/khensu.nu.ipa |
| nu.waves IPA | https://github.com/elliott-wave-labs/khensu-apple/releases/download/0.1.0-build3/nu.waves.ipa |
| Install docs | https://github.com/elliott-wave-labs/khensu-apple/blob/main/docs/INSTALL.md |

Local archives (Organizer → **Distribute App** — ASC API key for team `LHS49D8RYY` still missing Issuer ID):

- `~/Desktop/khensu-ptah-submit/Ptah.xcarchive` + `khensu.nu.ipa`
- `~/Desktop/khensu-waves-submit/Waves.xcarchive` + `nu.waves.ipa`

## SSL lesson (fixed in nu.harness)

Google-managed **own_certificate** hosts need: dig A → LB → **attach to proxy** → wait ACTIVE. Waiting for ACTIVE before attach deadlocks as `FAILED_NOT_VISIBLE`. NXDOMAIN certs on the proxy break bi SNI; correctly DNSed own certs attached while PROVISIONING do not (bi stayed `CN=bi.khensu.nu`). Project SSL cert quota = **10**. Skills + `nu.harness.md` + sites module updated.

## Commits pushed earlier this session

### khensu-specs

- https://github.com/elliott-wave-labs/khensu-specs/commit/60f1f5b8a3f95e747ed3127ea2e7fafef9103ff0 — ñü.ævätåřş + îňðřæ.ōġ
- https://github.com/elliott-wave-labs/khensu-specs/commit/875fdfd91b191fb09469b05301a49267d661d081 — nu.indra.og, Tech Talk 205, IETF hold
- https://github.com/elliott-wave-labs/khensu-specs/commit/96e62e9216ebda263357069c8ad46771419ed9b8 — alphabetical product nav

### khensu-site / khensu-apple / moqom

See prior `work-completed` rows; AM republish of khensu-nu + khensu-dev after sync-specs. Infra module fix in `moqom-pq` (attach-then-wait for own certs) — Elliott commits after review.

## Shipped behaviour

- Browser avatar studio + messenger call styles (ñü.ævätåřş)
- On-device captions + translate; Call PiP + Live Activity
- Indra mute-loop OG + chakra page; alpha nav
- 15 Pro Wi‑Fi install of messenger + nu.waves 0.1.0 (3)

## Hold / open (before 7am)

1. **You:** Xcode Organizer → **Distribute App** for Ptah + Waves (CLI has no team `LHS49D8RYY` Issuer ID; keychain has Development identities only)
2. IETF draft — still **do not submit**
3. nu.moments / nu.create IPAs — after push hold lifted
4. Review + commit: `work-*.md`, `nu.harness.md`, skills, moqom-pq module/pin
