# nu.waves player

**Status: built, 14 October 2026; stem adding and ñü.mobility added 19 October 2026.** The player on [waves.khensu.nu](https://waves.khensu.nu) and in the nu.waves iOS app (`nu.khensu.waves`). Music, live channels, your files on this device, healing sounds generated here, spacetime bubble mid-listen, stems added from other songs and other bubbles, and Immersive Mobility — nothing processed on servers.

Related: `design/nu-audio.md`, `design/nu-spatial.md`, `design/nu-sounds-studio.md`, `PLAN.md` (Sounds tab).

## 1. What it is

nu.waves is a full listening app, not a demo widget:

- **Catalogue** — khėnsu.ñü’s First Attempt (five movable instruments), Musopen Chopin (CC0), healing generators (chakra tones, bowls, binaural beats, noise, rain, ocean, forest, creek), Wilhelm Scream (CC0).
- **Your library** — files you add (sealed AES-256-GCM chunks in IndexedDB), a folder handle on Chromium, and on-device music through the iOS app (`nu-local:`).
- **Live channels** — programmes pinned to a fixed epoch so every listener hears the same moment, with no server choosing.
- **Spacetime bubble™** — every sound is an HRTF object you can drag, clone, remove, widen or swing while it plays; venues and ñü.ÊQ (gain, reverb, echo duration, delay, bounces) apply mid-listen.
- **Add a stem** — not just clone: any stem of any other song, a whole other song as one node, a generated tone, or one of your own files can be added into the bubble that is playing (3.2). A ñü.scene carries the borrowed stems with it, so a stem can move from one bubble to another.
- **ñü.mobility (Immersive Mobility), on by default** — you are locked inside the bubble: the sounds stay where they are and you move through them, by head turn and in xyz (3.1). Off, every sensor is ignored and the sounds stay fixed in your ears, as the player worked before. Head pose comes from phone motion, the on-device camera face pose, or AirPods via the native app, and never leaves the device.

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

### 3.1 ñü.mobility — Immersive Mobility (the lock mode, default on)

Shown as ñü.mobility in headings, buttons and labels; code `mobility`; running text nu.mobility.

| | On (default) | Off |
| --- | --- | --- |
| Where the sounds are | Fixed at their places in the spacetime bubble (world-locked to the bubble) | Fixed in your ears (head-locked), exactly as the player worked before this mode existed |
| Turning your head | The bubble stays put and you turn inside it: a sound ahead moves to your left ear as you turn right | Nothing changes in your ears |
| Moving in xyz | You travel through the bubble: sounds you walk toward get nearer and louder, sounds behind you fall behind | Nothing changes in your ears |
| Sensors | Gyro, accelerometer, camera and AirPods motion all steer the listener | **All ignored** — gyro, accelerometer, camera and headphone motion never reach the listener; the Web Audio listener sits at the centre, facing ahead |

- **State.** `Engine.mobility` (default `true`, persisted per device as the `mobility` setting; only an explicit off survives a reload) and `Engine.listenerPos`, the listener's place in bubble axes (x right, y ahead, z up, metres), clamped to 0.8 × the bubble radius so you stay inside it. `setMobility(false)` eases the listener back to the centre facing ahead and gates `setPose`, so a sensor reading taken while it is off cannot leak into the sound. Panner positions never change for mobility: only the Web Audio listener's orientation (`listenerVectors`) and position (`positionX/Y/Z`, same axis map as `place`: bubble (x, y, z) → (x, z, −y)) move.
- **Where xyz comes from.** Rotation is the head pose (phone, camera or AirPods, `head.ts`). Translation is, in order of honesty: the camera's face place and size (lean → x, duck/rise → z, face growing or shrinking against its recentre size → y, bounded, web); a bounded, heavily damped lean estimate from `CMHeadphoneMotionManager.userAcceleration` in the native bridge (`WavesBridge.swift`, ±1.2 m, leaks back to centre — a lean, never claimed as a walked position); and the keys everywhere — W A S D walk relative to where you face, R/F rise and sink (0.25 m per press, 0.6 m with Shift), combined with the sensor place in `Engine.syncListener`. True walked position (ARKit world tracking in the app, as in nu.universes L0) is the native follow-on; nothing here claims it.
- **Recentre** makes the current facing "ahead" and returns the listener to the centre. The orb draws the head dot, the facing arrow and every sound's thread from `listenerPos`, so where you stand is visible. ñü.ink records head turns only while mobility is on.
- **Privacy.** Unchanged (A6): pose and place are computed and used on the device, never sent anywhere; turning mobility off also stops them reaching the listener at all.

### 3.2 Adding stems from other songs and other bubbles

Clone duplicates a sound already in the bubble. Adding brings a new one in:

- **Sources.** The stem picker in the player (`Add a stem — any song, any bubble`) lists every catalogue stem by song, whole songs without stems as one node, generated tones and sounds, and your own files (your library and, in the app, the phone's music). `Engine.addStemFromTrack(source, stem?)` and `addGenToBubble` do the work.
- **The node.** An added stem is a first-class bubble object (`Obj.srcTrack` / `Obj.srcStem` record where it came from; `mix` = a whole song as one node): its own element or voice, looping and re-synced to the deck clock (`currentTime % duration` on load, then the deck's drift pass), HRTF panner at the venue's place for that stem (offset if the place is taken), and it drags, orbits, clones (clones keep the provenance), restores and removes exactly like a native stem. It never touches the playing track's own objects, its untouched original, or its loudness match. Caps: 28 objects in a bubble (16 for generated layers), shown honestly as "the bubble is full" rather than a silent no-op.
- **Between bubbles.** ñü.scene capture records each added node's source next to its place; the share encoding carries it (`x` list in `scene.ts`, old codes without it still decode). Recalling a scene — from your library, a pasted listen, a share link or SharePlay — first re-adds the missing borrowed stems into the bubble that is playing (`materialiseScene`), then places them. Audio is never carried by the scene: catalogue stems come from the catalogue, your files from your own library on that device, and a source that is not on the device is skipped, not fetched from anyone else.
- **Rights.** Unchanged: a borrowed stem is a local playback layer on your device. Nothing is uploaded, exported, published or sent to anyone; a shared scene shares places and source ids, never samples (5).
- **One tap.** Every list row whose track can lend its stems shows `+ stems`, which drops all of them into the bubble of the song that is playing (First Attempt, every hosted mobygratis track). Generated tones keep `+ 3D`.

### 3.3 mobygratis

The full mobygratis catalogue (499 instrumentals, 22 Oct 2026) is an artist on nu.waves, so any of its stems can go into any song.

- **Data.** `src/data/mobygratis.json` holds title, tags, BPM, length and the mobygratis id for every track, plus the stem list once a track is hosted. `tools/mobygratis.py sync` refreshes it from mobygratis.com's public catalogue; `tools/mobygratis.py import` signs in with our mobygratis account (downloads need one), takes each track's multitrack WAVs, encodes every stem to 48 kbps mono Opus in MP4, uploads to `gs://khensu-waves-media/mobygratis/<slug>/` and records the stems. One track at a time, WAVs deleted before the next, resumable.
- **Hosting.** `khensu-waves-media` is its own public bucket with CORS for the khensu hosts, outside `moqom-sites`, because a site publish deletes anything under the site prefix that is not in `dist/`. The site CSP allows it in `media-src` and `connect-src`.
- **Before audio arrives.** A track without stems is listed with "stems arriving"; it is skipped in queues and can't lend stems.
- **Licence terms the player keeps.** Free and non-commercial: mobygratis tracks are never sold, never paid per play and never behind a paywall (`Track.nonCommercial`). Credit is "Music by mobygratis", never Moby by name. Not for promoting right-wing politics, meat, dairy or other animal products (stated on the artist page). Restricted Tracks play but never lend stems (`lendsStems`). A track removed from mobygratis.com drops out on the next `sync`.

## 4. Privacy and rights

- No third-party scripts. Media is same-origin, `blob:` / `nu-local:`, or the `khensu-waves-media` bucket.
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
| ñü.mobility | `mobility` | Immersive Mobility (3.1): the lock mode, on by default. You are inside the bubble and the sounds stay where they are while you turn and move in xyz; off, all sensors are ignored and the sounds stay in your ears. |
| — (stem adding) | `addStemFromTrack`, `Obj.srcTrack/srcStem` | Adding a stem, a whole song or a tone from any other song or bubble into the playing bubble (3.2) — distinct from clone, which only copies what is already there. Borrowed stems travel between bubbles inside ñü.scene. |

Also: “made for you” from likes and history on the device, queue reorder, PWA install prompt, wake lock while playing, swipe the mini bar to skip, richer keyboard shortcuts, offline banner.

## 6. Patent assessment

See `PATENTS.md` (nu.waves player entry, 14 Oct 2026, and the ñü.scene / ñü.orbit / ñü.ink / ñü.tide / ñü.dim row): mid-listen movable HRTF objects with venue/ñü.ÊQ, clock-pinned live programmes without a playlist server, sealed on-device library with head-tracked listener, plus saved spatial scenes, path-following objects, listening handwriting glyphs, clock-personalised home and room-collapsing sleep — assess before any public patent claim language beyond this design doc.

19 Oct 2026 additions, same treatment (published now, never held for a filing): cross-song / cross-bubble stem adding with per-node source provenance carried inside a saved spatial scene so the borrowed node is rebuilt in a different bubble without carrying samples, and the default-on bubble-locked mobility mode (sensor rotation plus bounded xyz translation of the listener against fixed in-bubble sources, with a hard sensor-ignore off state). Prior art to search: DAW stem import and DJ stem decks (which do not place borrowed stems as movable HRTF objects in a playing bubble, nor carry them in a shareable scene), Apple / Dolby head-tracked spatial audio (rotation of a fixed mix, not listener translation through independently movable objects), and 6DoF game audio (listener movement in a authored world, not a music bubble built mid-listen). See the new `PATENTS.md` row.
