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

## 5. Patent assessment

See `PATENTS.md` (nu.waves player entry, 14 Oct 2026): mid-listen movable HRTF objects with venue/ñü.ÊQ, clock-pinned live programmes without a playlist server, and sealed on-device library with head-tracked listener — assess before any public patent claim language beyond this design doc.
