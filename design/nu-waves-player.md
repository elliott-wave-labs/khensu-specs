# nu.waves player

**Status: built, 14 October 2026.** The player on [waves.khensu.nu](https://waves.khensu.nu) and in the nu.waves iOS app (`nu.khensu.waves`). Music, live channels, your files on this device, healing sounds generated here, spacetime bubble mid-listen, and head tracking — nothing processed on servers.

Related: `design/nu-audio.md`, `design/nu-spatial.md`, `design/nu-sounds-studio.md`, `PLAN.md` (Sounds tab).

## 1. What it is

nu.waves is a full listening app, not a demo widget:

- **Catalogue** — khėnsu.ñü’s First Attempt (five movable instruments), Musopen Chopin (CC0), healing generators (chakra tones, bowls, binaural beats, noise, rain, ocean, forest, creek), Wilhelm Scream (CC0).
- **Your library** — files you add (sealed AES-256-GCM chunks in IndexedDB), a folder handle on Chromium, and on-device music through the iOS app (`nu-local:`).
- **Live channels** — programmes pinned to a fixed epoch so every listener hears the same moment, with no server choosing.
- **Spacetime bubble™** — every sound is an HRTF object you can drag, clone, remove, widen or swing while it plays; venues and ñü.ÊQ (gain, reverb, echo duration, delay, bounces) apply mid-listen.
- **Head tracking** — phone motion, on-device camera face pose, or AirPods via the native app. Pose never leaves the device.

## 2. Hosts and packaging

| Surface | Role |
| --- | --- |
| `waves.khensu.nu` | Installable app shell (PWA: `waves.webmanifest`, `waves-sw.js` registered only on this host) |
| `khensu.nu/waves` | Same page; no service worker |
| `/waves/catalogue.json` | Machine-readable catalogue from `src/data/waves.ts` |
| iOS `Waves` target (`nu.khensu.waves`) | WKWebView over the live site; `webkit.messageHandlers.waves` for AirPods pose (`CMHeadphoneMotionManager` → `__wavesNative.head`) and Music library (`__wavesNative.library` + `nu-local://media/<id>`); background audio; `WKAppBoundDomains` = `waves.khensu.nu` |

Hash routes (`#/`, `#/search`, `#/library/…`, `#/channels`, `#/artist/…`, …) keep the app on one page so product-host rewrites stay unchanged.

## 3. Audio graph

Per track (a **deck**), objects feed HRTF panners → bus → dry / pre-delay→convolver / echo taps → loudness match → user gain (ñü.ÊQ) → limiter → output. Untouched originals and fixed beds skip the room; binaural beats are stereo-direct. Modes: **original**, **opus 5.1** (when present), **nu.waves**. Crossfade between decks; live channels retune from `onAir()`.

Listener orientation: yaw right-positive; Web Audio forward/up from head pose (`src/scripts/waves/head.ts`, `engine.ts`).

## 4. Privacy and rights

- No third-party scripts. Media is same-origin or `blob:` / `nu-local:`.
- Head pose and face frames stay on device (`nu-audio.md` A6).
- Kept tracks and added files are sealed under a non-extractable AES-GCM device key; AAD binds set and chunk index.
- Catalogue entries name their licence. Third-party music in the user’s library is never uploaded.

## 5. New listening IP (14 Oct 2026)

These ship in the web player and stay on the device. Code names are ASCII; people see the ñü forms in the UI.

| Shown | Code | What it is |
| --- | --- | --- |
| ñü.scene | `scene` | A named snapshot of every sound’s position, optional orbits, venue and ñü.ÊQ for a track. Recall mid-listen without re-encoding. Share a listen link (`#/t/{track}?scene=`) that opens the catalogue song already cued, with those settings applied — nothing is uploaded. |
| ñü.orbit | `orbit` | A sound walks a horizontal path around a centre at a chosen rate. Only the place numbers move; the samples stay put. |
| ñü.tide | `tide` | Home surfaces collections, albums and channels that fit the local hour (dawn / day / dusk / night), with no server and no profile. |
| ñü.ink | `ink` | While you drag and turn, a private path is drawn; you can keep it as a small glyph of how you listened, not of the music. |
| ñü.dim | `dim` | Sleep’s last 45 seconds collapse positions and reverb toward you, then fade volume, so the room goes quiet before the sound does. |

Also: “made for you” from likes and history on the device, queue reorder, PWA install prompt, wake lock while playing, swipe the mini bar to skip, richer keyboard shortcuts, offline banner.

## 6. Patent assessment

See `PATENTS.md` (nu.waves player entry, 14 Oct 2026, and the ñü.scene / ñü.orbit / ñü.ink / ñü.tide / ñü.dim row): mid-listen movable HRTF objects with venue/ñü.ÊQ, clock-pinned live programmes without a playlist server, sealed on-device library with head-tracked listener, plus saved spatial scenes, path-following objects, listening handwriting glyphs, clock-personalised home and room-collapsing sleep — assess before any public patent claim language beyond this design doc.
