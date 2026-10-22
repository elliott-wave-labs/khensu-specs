# Work completed — 22 October 2026 (nu.universes flight)

## Commits pushed

| Repo | Commit |
| --- | --- |
| khensu-specs | https://github.com/elliott-wave-labs/khensu-specs/commit/eade591a0b94e4ebaa8d7c6c64f87e9b68b1d9be |
| khensu-apple | https://github.com/elliott-wave-labs/khensu-apple/commit/d3f86107f8abbdbbc797f681f702ce068b937fd8 |
| khensu-site | https://github.com/elliott-wave-labs/khensu-site/commit/de93f5f4255839508e10e89edc02979271f991e1 |

## Live

| Surface | URL | Status |
| --- | --- | --- |
| nu.universes (i.verse) | https://iverse.khensu.nu | HTTP 200, CN on `moqom-aura-iverse-khensu-nu` (SAN: aura, iverse, universes, rabbithole, portal) |
| aliases | https://universes.khensu.nu · https://rabbithole.khensu.nu · https://portal.khensu.nu · https://khensu.nu/universes | HTTP 200, same page |
| nu.eyes | https://khensu.nu/eyes | HTTP 200, try-on |
| moments | https://moments.khensu.nu | HTTP 200, studio + templates |
| bi (always-live check) | https://bi.khensu.nu | HTTP 200, `CN=bi.khensu.nu` |

- **Spec:** `design/nu-universes.md` — iverse hosts, flight map, directions/rabbitholes. Patent rows in `PATENTS.md`. pycache ignored.
- **App:** Waves Universes is a 3D flight (RealityKit `CustomMaterial` sprites, bundled HYG/UNGC/2MRS + Hubble M33, AR table, directions). `xcodebuild` Waves iOS Release **BUILD SUCCEEDED**.
- **Site:** 3D flight in three.js, MediaPipe eyes try-on, moments studio frames. Published 22 Oct with `gcloud storage` from a frozen dist (live `dist/` was being rebuilt mid-rsync).

# Work completed — 18 October 2026 (nu.moments build 4)

## nu.moments full editor 0.1.0 (6) + moments site — 19 Oct

| Asset | URL |
| --- | --- |
| Release | https://github.com/elliott-wave-labs/khensu-apple/releases/tag/0.1.0-build6 |
| Apple commit | https://github.com/elliott-wave-labs/khensu-apple/commit/0cd26bb |
| Site commit | khensu-site `df7d044` (local; publish blocked, see below) |

- **App:** template looks/transitions/formats render in preview + export, captions burned in, split/duplicate/speed/in-point/mute, generated beat + beat sync + Auto-fit, auto captions on device, subject lift (photos), carousel slides, save to Photos. All three 0.1.0 (6) installed + launched on 15 Pro; Air still unreachable.
- **Site:** moments page rebuilt — working in-browser studio (upload, looks, burned captions, canvas export), real frames with the actual looks applied, real app screenshot in the hero phone, honest copy for what build 6 does, `/app` hub now links build-6 IPAs for all three apps. `pnpm build` passes (229 pages).
- **Published 19 Oct:** https://khensu.nu/moments/ (studio + real frames) and https://khensu.nu/app (build-6 IPAs). ADC login as `elliott@moqom.cloud` can write; `publish-sites.sh` still calls `gsutil`, which uses the CLI account `iam.elliott.io@gmail.com` and 403s. Uploaded with `gcloud storage` + the ADC token, then purged `/moments/*`, `/app/*`, `/khensu/moments/*`.

## Status-bar chrome 0.1.0 (5) — 18 Oct PM

Blurred header below the status bar in all apps (visible `ultraThinMaterial` nav bar, inline titles; Waves web view no longer ignores the safe area; onboarding/lock scrim). Verified in simulator screenshots (Chats, nu.waves Listen, ñü.mømëntš home).

| Asset | URL |
| --- | --- |
| Release | https://github.com/elliott-wave-labs/khensu-apple/releases/tag/0.1.0-build5 |
| Commit | https://github.com/elliott-wave-labs/khensu-apple/commit/d5e8bda |
| IPAs | `nu.moments.ipa` · `nu.waves.ipa` · `khensu.nu.ipa` on that release |

15 Pro: all three build-5 apps installed + launched 18 Oct PM. iPhone Air still unreachable from this Mac (offline in `xctrace`) — build-5 apps are in `/tmp/build5/*/DD/Build/Products/Release-iphoneos/` + GitHub for when it connects.

## nu.moments + all apps 0.1.0 (4) — GitHub

| Asset | URL |
| --- | --- |
| Release | https://github.com/elliott-wave-labs/khensu-apple/releases/tag/0.1.0-build4 |
| nu.moments IPA (new) | https://github.com/elliott-wave-labs/khensu-apple/releases/download/0.1.0-build4/nu.moments.ipa |
| Messenger IPA | https://github.com/elliott-wave-labs/khensu-apple/releases/download/0.1.0-build4/khensu.nu.ipa |
| nu.waves IPA (+ Universes) | https://github.com/elliott-wave-labs/khensu-apple/releases/download/0.1.0-build4/nu.waves.ipa |
| Commit | https://github.com/elliott-wave-labs/khensu-apple/commit/4487be7 |

- **nu.moments built:** templates, persistent on-device projects/media, beat sync, caption styles, trim/reorder, preview, 1080×1920 export. Simulator + Release device builds pass; IPA signed (wildcard team profile, minimal sideload entitlements — App ID registration still open, see work-ip).
- **Waves fixed + shipped:** Universes tab; `RealityViewCameraContent` fix for iOS 26 SDK.
- **Ptah/Waves archives (4)** on Desktop (`khensu-ptah-submit`, `khensu-waves-submit`); IPAs beside them + `khensu-moments-submit/nu.moments.ipa`.
- **Device install — 15 Pro DONE 18 Oct 9:21pm:** all three 0.1.0 (4) installed + launched on Elliott's 15 Pro (`nu.khensu.moments`, `nu.khensu.waves`, `nu.khensu.ptah` verified in device app list).
- **iPhone Air PENDING:** Mac cannot see the Air at all (`xctrace` lists it offline, no USB/Wi-Fi tunnel) despite unlock/cable attempt. When the Air is data-cabled to this Mac or on the same Wi-Fi awake: `xcrun devicectl device install app --device 6EA81217-82D6-588D-A2F1-7F74651142A7 <app>` ×3 from `/tmp/build4/*/DD/Build/Products/Release-iphoneos/` (apps persist there + IPAs on GitHub).

---

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
| nu.moments | moments.khensu.nu · /moments | Native Moments target (`nu.khensu.moments`) builds; Templify-beating site in dist (publish blocked on GCS IAM) |
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
| https://khensu.nu/aura | **ñü.åůřâ** first show — live 15 Oct PM (apex until Hover A + own cert) |
| https://dev.khensu.nu/specs/nu-aura/ | Fashion + quiet sensing spec |
| https://sla.khensu.nu · https://network.khensu.nu | 100% uptime pulse verified with aura publish |

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

## nu.universes (nu.u) — 18 Oct 2026

- Spec + model: `design/nu-universes.md` + `design/nu-universes/blender_m33.py` (M33 constants from ESA/Hubble heic1901, NASA M33, ESO, EarthSky; 19-channel spectral cube; FLRW cosmic timeline; three-twinkle physics; mantis observer).
- App: `khensu-apple/Waves/Universes/` (5 Swift files) inside `nu.khensu.waves`; Waves is now Listen + Universes tabs. RealityKit + AR toggle, wavelength bands gamma→radio + mantis + sonify, Big Bang timeline. **BUILD SUCCEEDED** macOS + iOS (generic) via xcodegen + xcodebuild, Xcode 26.2.
- Site: live at https://iverse.khensu.nu and https://khensu.nu/universes (published 22 Oct).
- Blender: MCP was offline (addon not running); procedural M33 script ships as source of truth, syntax-validated, exports USD/glTF for RealityKit/web.
- Elliott reviews + commits (specs, apple, site) — not pushed here.
