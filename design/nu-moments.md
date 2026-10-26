# nu.moments: templates, beat sync and editing on your device

Product name: **ñü.mømëntš** (shown); code, host and identifiers: `moments`, `nu.moments`, `nu.khensu.moments`, host `moments.khensu.nu` (path `/moments` on the apex). Formerly the working name “editor” in `design/editor.md`.

Status (22 Oct 2026): build 10 adds the Prism effects and Paint styles (3.1, 3.2) after Datamosh in build 9 (3.3). Earlier: native app shipped in `khensu-apple` 0.1.0 build 6 (Moments target, `nu.khensu.moments`) — six templates whose looks, transitions and caption styles render in preview and export; formats 9:16/1:1/4:5/16:9; split/duplicate/trim/speed/mute; beat sync with your track or a generated beat; Auto-fit frame scoring; auto captions from on-device speech; subject lift for photos (Vision); carousel slides; save to Photos; projects + media persisted in Application Support. GitHub sideload IPA in release `0.1.0-build6`; App Store archive pending App ID registration (see `work-ip.md`). Moments site rebuilt (browser studio, real frames) on moments.khensu.nu and `/moments`. This doc is the engineering truth. Patent assessment once the editor is in wider use (`PATENTS.md`).

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

### 3.1 Prism effects (build 10)

Four timeline effects in a Prism group (`EffectKind.prism`, `.prismTunnel`, `.facets`, `.triangles`), drawn live by the same Core Image renderer as preview and export (`Moments/Services/Effects.swift`). Each blends back over the clip by Intensity, so the shot stays visible through the glass, and Speed sets the motion.

- **Prism glass.** A 30° wedge of the frame around an axis is masked by two half-plane gradients, then mirrored and turned twelve times for six-fold symmetry over the whole canvas. The axis points down the long side of the frame, because only that direction reaches the corners from the centre and the lower half of most shots has the detail, and it sways ±0.3 rad. Built-in `CIKaleidoscope` was rejected: it only fills a polygon set by the short side of the frame.
- **Prism tunnel.** Six nested copies of the clip, each half the size of the last and turned 0.14 rad more, darkened 0.18 EV per level, then mirrored four ways. The phase advances one level per loop, so the zoom never jumps.
- **Glass facets.** `CICrystallize` over moving noise gives flat cells. Each cell picks one of six copies of the clip, each slightly zoomed, turned, moved and hue-shifted, through nested `CIColorThreshold` masks, with the cell edges screened on as glints. `CIDisplacementDistortion` and `CIGlassDistortion` were rejected: both displace by the texture's gradient, so flat cells only move their edges.
- **Triangles.** `CITriangleKaleidoscope` over the clip.

All four end with a prism split: red scaled up and blue scaled down about the centre, recombined by per-channel maximum. Addition was used before and brightened the picture (mean luma 162 to 237 at zero intensity); the fix also corrected RGB split, glitch and VHS lines. Measured in the Mac harness at 1080×1920: 10–30 ms a frame.

### 3.2 Paint styles (build 10)

Five fast style-transfer networks (`Moments/Services/PaintStyle.swift`, models in `Moments/Resources/PaintStyles/`), trained by us with Create ML `MLStyleTransfer` (CNN, 1,000 iterations) on public-domain scans from Wikimedia Commons, with our own generated sample photos as content images:

| Style | Painting | Style strength, texel density | Training time (Mac CPU) |
| --- | --- | --- | --- |
| The Great Wave | Hokusai, The Great Wave off Kanagawa, about 1831 | 5, 256 | about 11 min |
| Starry Night | Van Gogh, The Starry Night, 1889 | 5, 256 | about 11 min |
| The Scream | Munch, The Scream, 1893, cropped to the sky and the figure | 6, 96 | about 2 min |
| Cubist | Juan Gris, Still Life before an Open Window, Place Ravignan, 1915 | 6, 96 | about 2 min |
| Kandinsky | Composition VII, 1913 | 5, 256 | about 11 min |

What we learned tuning them: at density 256, strength 5 only tinted the photo for The Scream, the Gris and Monet, while strength 7–10 collapsed the picture into texture or dark blobs. A coarse density (96) at strength 6 gave visible strokes and planes that still keep the subject. Monet's Impression, Sunrise is not shipped: every setting tried came out muddy, and with the sun in the crop it stamped pink blobs. Picasso's own paintings are still under copyright, so cubism learns from Gris, who died in 1927. Pretrained open-source weights were not used: the common ones (Rain Princess, Udnie, Candy) were trained on paintings that are still under copyright.

A photo is painted into a new JPEG; a clip is painted frame by frame into a new HEVC file with the same timestamps. Only frames inside the trimmed range are painted, and the rest pass through, so trims stay put. The clip's own sound is extracted first, as for datamosh. Strength dissolves the paint over the original; Brush sets the working size from 1,280 down to 512 pixels on the long side, so a bigger brush gives larger strokes. The result is resized back with Lanczos. `paintSourceName` keeps the original for Undo. Each model is 6.7 MB and runs with Core ML on the CPU and GPU. Measured on the Mac at 1080×1920: about 40 ms a frame.

### 3.3 Datamosh (build 9)

`Moments/Services/Datamosh.swift`. Vision optical flow at quarter resolution, averaged into 16-pixel macroblocks like codec motion vectors, drags old pixels with no fresh picture until the mosh ends. Three modes: from the clip before, bloom (one moment of motion repeated) and melt (the clip's own motion, with Leak). Amount multiplies the vectors. Baked into a new file, with `moshSourceName` kept for Undo. Measured on iPhone 15 Pro: 4.2 s for 3 s of 1080×1920.

### 3.4 Picture pulse (first template)

The first template is **Picture pulse**. Selected photos or a folder share one underlying colour for most of the screen; that wash shifts only as the pictures morph into each other. Three modes ship: the default path green → purple → blue → yellow → green, full spectrum, and monochrome. Not a beat-sync zoom. The site studio, the template cards and the moments Indra preview all show this wash, not a phone or a spinning node ring.

## 4. App identity

- Bundle / target: `nu.khensu.moments` inside `khensu-apple` (iPhone, iPad and Mac; iOS, iPadOS and macOS 26).
- Stock Liquid Glass chrome only.
- Commerce: flat 10% on in-app purchases and subscriptions; tips 100% to the person (`design/app-commerce.md`).
- Creators publish templates as personas and earn through network payments; templates have no tracking.

## 5. Open questions

- Model sizes that fit on iPhone with good speed (creative upscaler and outpainting in Core ML within about 1–2 GB).
- Template package format and effect-graph spec (to write as `design/templates.md`).
- Patent assessment once built: playback-time stabilization from carried motion metadata, full-frame stabilization with scene expansion, and a matte carried as a nu.media layer.
