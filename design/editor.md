# Editor: video and photo editing in khensu.nu

**Product name: nu.moments** (shown **ñü.mømëntš**). Code and host: `moments`, `nu.khensu.moments`, `moments.khensu.nu`. Canonical product brief: `design/nu-moments.md`. This file keeps the engineering sections (upscaling, expansion, templates, stabilization, matting, export).

## 1. Rules

- **Everything on the device.** Upscaling, scene expansion, templates, stabilization and export run on the Neural Engine, GPU and CPU of the user's own device. No server, no Private Cloud Compute, no cloud rendering. A Mac or the user's own node can take long renders over the local network, inside the user's own devices only.
- **Generated detail is a choice, never a default in transport.** nu-media sending stays fidelity-only (`design/nu-media.md` section 5). AI upscaling and scene expansion happen only when the user turns them on in the editor, and the result carries a "generated detail" flag inside the file so the receiver can show it. The flag holds no identity, device or time data.
- **Originals are kept.** Every edit is a non-destructive recipe over the original, so upscaling and expansion can be undone or redone with a better model later.
- **Native resolution.** The editor never downscales a source to edit it (section 7.2 of `design/nu-media.md`); proxies are generated for the timeline, and export renders from the originals.

## 2. AI upscaling ("up-res") of uploaded photos and video

- **When:** at import, or on any clip or photo later. Off by default for sending; on by default only inside the editor's export when the user asks for a larger size.
- **Two modes:**

  | Mode | What it does | Use |
  | --- | --- | --- |
  | Faithful | Restores detail that is really there: denoise, deblock, deblur, super-resolution trained with a fidelity loss | Archival, news, evidence, anything that must stay true |
  | Creative | Adds plausible detail with a diffusion-style model: textures, hair, foliage, text sharpening | Social posts, prints, wallpapers |

- **Targets:** photos up to 4× per side (48 MP to about 200 MP in tiles); video 2× per pass (1080p to 4K, 4K to 8K), with temporal consistency so detail doesn't flicker between frames.
- **Measured against:** Apple's low-latency super resolution (the nu-media prototype, `bench/ladder.py`), Topaz Video and Photo AI, Adobe Super Resolution. Faithful mode is scored with VMAF, PSNR and LPIPS against held-out originals; Creative mode with a viewer test (ITU-T P.910), because fidelity scores penalise invented detail by design.

## 3. Scene expansion (outpainting)

- **What:** extends a photo or video beyond its frame: turn a vertical clip into 16:9 or a 4:3 photo into a 21:9 wallpaper, fill the corners left by stabilization or rotation, remove objects and fill the hole.
- **Video:** expansion is propagated along optical flow and camera motion, so the invented edges move with the scene; a keyframe the user approves anchors each shot.
- **Limits:** expansion beyond 1.5× the original area is marked as low confidence in the editor. Faces and text are never invented in Faithful mode.

## 4. Templates (like Templify)

- **Templates** are signed, content-addressed packages (layout, timing, transitions, text styles, music cue points, effect graph) fetched over the mixnet from webË, so nobody learns which templates you use.
- **Auto-fit:** the editor picks the best clips and beats from your selection on the device: shot detection, faces, motion, audio beats and on-device aesthetic scoring.
- **Creators:** anyone can publish templates as a persona (`PLAN.md`, Public square) and earn through the network's payments; templates have no tracking and no remote code, only a declarative effect graph.
- **Music:** only tracks the user has the rights to, or the licensed catalogue once it exists (phone spec open question K5).

## 5. Stabilization

Existing systems each solve part of the problem: Apple's Action mode and Cinematic stabilization crop heavily; Google's fused video stabilization uses the gyro and optical image stabilization but bakes the result in; GoPro HyperSmooth and Insta360 FlowState are camera-only; Gyroflow (open source) uses gyro logs in post but needs lens profiles and crops.

The khensu.nu editor combines them and adds two things none of them do:

1. **Full-frame, no crop:** stabilization moves the frame freely and scene expansion (section 3) fills the exposed edges, so the output keeps the full field of view instead of cropping 10–30%. Research basis: full-frame video stabilization with neural fusion (FuSta, 2021) and later work.
2. **Stabilize at playback, not at encode:** the camera's motion (gyro at the sensor rate, per-row rolling-shutter timing, lens model, OIS position) is carried as compact metadata in the nu-media stream, and the receiver applies stabilization when it plays. The original stays unwarped, viewers can choose strength or horizon lock, and no bits are wasted encoding shake.

Plus:

- per-row rolling-shutter correction from the gyro, not frame-level;
- horizon lock in any orientation, including 360° (Insta360 Titan and other VR cameras);
- motion-blur reduction by the Neural Engine on frames where shake blurred the image;
- the same pipeline for live calls: stabilization metadata rides with the base layer and costs a few hundred bits per second (estimate).

**Measured against:** Apple Action mode, Pixel, GoPro HyperSmooth, Insta360 FlowState and Gyroflow on the same rigs, using the standard metrics from the stabilization literature (stability score, cropping ratio and distortion value), plus a viewer test. "Superior" is claimed only for the metrics where the measurements show it.

## 5.1 Matting: green screen and automatic rotoscoping

Cuts a subject out of a photo or video with a soft, feathered edge (hair, motion blur, smoke, glass), with or without a green screen. Everything runs on the device.

| Stage | What it does | Candidate models and methods |
| --- | --- | --- |
| Select | The user taps or brushes the subject once; the editor finds it in every frame | SAM 2 / EdgeTAM-class promptable video segmentation, with memory so it follows the subject through occlusion |
| Trimap | Turns the hard mask into "definitely in", "definitely out" and a thin unknown band at the edge | Erode and dilate scaled to the subject's size and motion blur |
| Matte | Solves a fractional alpha (0 to 1) for every pixel in the unknown band | ViTMatte-class trimap matting for stills; Robust Video Matting and MatAnyone-class recurrent matting for video |
| Foreground colour | Recovers the subject's true colour under semi-transparent edges, so no green or background fringe remains | Closed-form or fast multi-level foreground estimation; despill on green and blue screens |
| Temporal | Keeps the edge from shimmering between frames | Optical-flow-guided alpha propagation and smoothing |
| Green screen | Keys a screen colour directly when one is present, then hands the edges to the matting stage | Chroma key in YUV with similarity and blend, despill; the matte stage refines hair and blur |

- **Output:** the alpha is carried in nu-media as an extra layer (HEVC with alpha, the same encoder Apple uses for transparent video), so the receiver can composite the subject over any background at playback and the original stays untouched.
- **Uses:** background replacement in the editor and on calls, stickers from photos and video, template slots (section 4), and object removal with scene expansion (section 3).
- **Measured against:** the standard matting metrics (SAD, MSE, gradient and connectivity errors) on public matting benchmarks, and dtSSD for flicker in video; compared with Apple's subject lift and person segmentation, DaVinci Resolve Magic Mask, After Effects Roto Brush and Runway.
- **Demo:** the nu-media page shows a CC0 8K green-screen clip keyed in ffmpeg (`chromakey` plus `despill`), composited over another video. This is the green-screen path only; the AI matting stages above are not built yet.

## 6. Export and sharing

- Export to nu-media at native resolution (sending inside khensu.nu), or HEVC, ProRes, H.264 and HEIC for outside apps, through VideoToolbox and ImageIO.
- The "generated detail" flag is written as a nu-media metadata field; exports to outside formats add a C2PA-style content credential only if the user opts in (it can identify the editing app).

## 7. Open questions

- Model sizes that fit on iPhone with good speed: a creative upscaler and an outpainting model in Core ML within about 1–2 GB, to be measured on iPhone Air and iPhone 18 Pro.
- Template package format and effect-graph spec (to write as `design/templates.md`).
- Patent assessment once built: playback-time stabilization from carried motion metadata, full-frame stabilization with scene expansion inside a private messenger, and a matte carried as a nu-media layer for composition at playback (to add to `PATENTS.md`).
