# nu.moments: templates, beat sync and editing on your device

Product name: **ñü.mømëntš** (shown); code, host and identifiers: `moments`, `nu.moments`, `nu.khensu.moments`, host `moments.khensu.nu` (path `/moments` on the apex). Formerly the working name “editor” in `design/editor.md`.

Status: native app shipped in `khensu-apple` 0.1.0 build 6 (Moments target, `nu.khensu.moments`) — six templates whose looks, transitions and caption styles render in preview and export; formats 9:16/1:1/4:5/16:9; split/duplicate/trim/speed/mute; beat sync with your track or a generated beat; Auto-fit frame scoring; auto captions from on-device speech; subject lift for photos (Vision); carousel slides; save to Photos; projects + media persisted in Application Support. GitHub sideload IPA in release `0.1.0-build6`; App Store archive pending App ID registration (see `work-ip.md`). Moments site rebuilt (browser studio, real frames) on moments.khensu.nu and `/moments`. This doc is the engineering truth. Patent assessment once the editor is in wider use (`PATENTS.md`).

## 1. Rules

- **Everything on the device.** Upscaling, scene expansion, templates, beat sync, matting, stabilization and export run on the Neural Engine, GPU and CPU of the user’s own device. No server, no Private Cloud Compute, no cloud rendering. A Mac or the user’s own node can take long renders over the local network, inside the user’s own devices only.
- **Generated detail is a choice, never a default in transport.** nu.media sending stays fidelity-only (`design/nu-media.md` section 5). AI upscaling and scene expansion happen only when the user turns them on in nu.moments, and the result carries a “generated detail” flag inside the file so the receiver can show it. The flag holds no identity, device or time data.
- **Originals are kept.** Every edit is a non-destructive recipe over the original, so upscaling and expansion can be undone or redone with a better model later.
- **Native resolution.** The editor never downscales a source to edit it (section 7.2 of `design/nu-media.md`); proxies are generated for the timeline, and export renders from the originals.
- **Templates over the mixnet.** Template packages are signed and content-addressed, fetched over webË, so nobody learns which templates you use.

## 2. Product surface (Templify-class)

A creator-first editor for stories, carousels and posts, with the privacy posture of khėnsu.ñü:

| Feature | What it does |
| --- | --- |
| Video editor | Timeline, cuts, transitions, colour, export to nu.media or HEVC / ProRes / H.264 |
| Beat sync | On-device shot detection and beat matching; import clips and a track you have rights to; no timeline required for the simple path |
| Remove background | Subject lift and soft matting (section 5.1 of `design/editor.md`); stickers and collage slots |
| Overlays and stickers | Declarative effect-graph packs from webË; weekly drops from creators, no remote code |
| Photo editor | Filters, retouch, presets; same non-destructive recipe model |
| Designer templates | Signed packages: layout, timing, text styles, music cues, effect graph |
| Carousels | Multi-slide scrapbook layouts for the Feed and outside export |
| Captions | Customizable caption styles; text stays on device |
| Curated presets | Film, print, haze and editorial looks as effect graphs |

## 3. Detail specs

Sections 2–6 of `design/editor.md` (upscaling, scene expansion, templates, stabilization, matting, export) are normative for nu.moments until folded into this file.

## 4. App identity

- Bundle / target: `nu.khensu.moments` inside `khensu-apple` (iPhone, iPad and Mac; iOS, iPadOS and macOS 26).
- Stock Liquid Glass chrome only.
- Commerce: flat 10% on in-app purchases and subscriptions; tips 100% to the person (`design/app-commerce.md`).
- Creators publish templates as personas and earn through network payments; templates have no tracking.

## 5. Open questions

- Model sizes that fit on iPhone with good speed (creative upscaler and outpainting in Core ML within about 1–2 GB).
- Template package format and effect-graph spec (to write as `design/templates.md`).
- Patent assessment once built: playback-time stabilization from carried motion metadata, full-frame stabilization with scene expansion, and a matte carried as a nu.media layer.
