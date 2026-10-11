# nu-media: images, video and HDR in minimal wire bits

How khensu.nu sends photos and video at the fewest bits on the wire while keeping resolution, colour and HDR, using the A20 Pro's Neural Engine and media engines. Status: design. **No nu-media measurements exist yet.** Every baseline figure below is an estimate from typical results for Apple's encoders and the published literature; every nu-media figure is a target. Section 8 is the benchmark that replaces them. Open questions in `OPEN-QUESTIONS.md` section H (52 and 55). Summary in `PLAN.md`, nu-media.

## 1. Hardware it is built for

iPhone 18 Pro and Pro Max (Apple's specifications page):

| Part | What it gives nu-media |
| --- | --- |
| A20 Pro: dual 16-core Neural Engine | Learned image encode and decode, receiver-side video enhancement (Core ML, FP16 and INT8) |
| 7-core GPU with Neural Accelerators | Second place to run networks; colour conversion and tone mapping in Metal |
| Media engine: hardware encode | HEVC (Main, Main 10, HDR), H.264, ProRes. **No AV1 encoder** |
| Media engine: hardware decode | HEVC, H.264, AV1, ProRes; HDR as Dolby Vision, HDR10+/HDR10 and HLG |
| Display | 2622 × 1206 (Pro, 3,162,132 px) or 2868 × 1320 (Pro Max, 3,785,760 px) at 460 ppi; P3; 1,000 nits typical, 1,600 nits HDR peak; ProMotion up to 120 Hz |
| Cameras | 48 MP Fusion cameras; 4K Dolby Vision up to 120 fps; spatial video 1080p30; ProRes RAW, Apple Log 2, ACES |

The A20 Pro has no "TPU"; Apple's term is the Neural Engine. The iPhone has no AV1 encoder, but the measured run in section 8.1 shows real-time software AV1 at 960 × 540 beats the hardware HEVC encoder at full 1080p by about 21 VMAF points at 500 kbit/s, at a quarter of the pixels to encode. So the video base layer is AV1 Main 10 encoded on the CPU at reduced resolution, with hardware HEVC Main 10 as the low-power fallback (Low Power Mode, thermal pressure, or a CPU too slow for the tier). AV1 decodes in hardware on A17 Pro and later and in software (dav1d) on earlier chips. nu-media works on every iOS 26 device and is tuned for iPhone 18 Pro on iOS 27.

## 2. The wire budget

Everything is sized against the stealth tick (`PROTOCOL.md`): with the app open, a burst every 2 s with 3 payload slots of 2,048 bytes.

| Unit | Bits |
| --- | --- |
| One slot (2,048 B payload) | 16,384 |
| One tick (3 slots) | 49,152 |
| Per second, foreground | 24,576 bit/s |
| Bulk packet payload (own node, charging window) | 524,288 (64 KB) |
| Call tiers (constant rate) | L 500,000 bit/s, M 1,500,000 bit/s, H 3,800,000 bit/s, plus Opus 32,000 bit/s |

Bits are the primary unit below. KB means 1,024 bytes; MB means 1,000,000 bytes.

## 3. Images: ImageIO against nu-media

One full-screen photo on iPhone 18 Pro (3,162,132 px). Bits = bits per pixel (bpp) × pixels. Time is how long it takes to arrive inside the ticks.

| Format | Setting | bpp | Bits | Size | Slots | Time in ticks |
| --- | --- | --- | --- | --- | --- | --- |
| JPEG (ImageIO) | quality 0.8 | 1.60 | 5,059,411 | 618 KB | 309 | 206 s |
| JPEG (ImageIO) | quality 0.5 | 0.90 | 2,845,919 | 347 KB | 174 | 116 s |
| HEIC (ImageIO, hardware HEVC) | quality 0.8 | 0.80 | 2,529,706 | 309 KB | 155 | 104 s |
| HEIC (ImageIO, hardware HEVC) | quality 0.4 | 0.25 | 790,533 | 96.5 KB | 49 | 34 s |
| **nu-media**, target upper | fidelity mode | 0.104 | 327,680 | 40 KB | 20 | 14 s |
| **nu-media**, target lower | fidelity mode | 0.039 | 122,880 | 15 KB | 8 | 6 s |
| **nu-media** preview | first slot | 0.0052 | 16,384 | 2 KB | 1 | first tick |

What to expect honestly:

- **At equal quality, nu-media targets about half the bits of ImageIO HEIC.** That figure is an estimate: the best learned image codecs measure roughly 10–20% fewer bits than VVC intra, VVC intra roughly 25% fewer than HEVC intra (HM reference), and a real-time hardware HEIC encoder needs more bits than HM. Combined, that is about 45–55% below ImageIO HEIC.
- **15–40 KB is a size cap, not "the same picture for free".** It is about what HEIC would need at 30–80 KB: softer than the camera's original, but clean. Learned codecs degrade by smoothing, not by blocks and ringing, which is why they look better than HEIC at these sizes.
- **Fidelity first:** no generated texture (no GAN or diffusion decoders), so nothing appears that wasn't in the photo.
- **Originals** (full 48 MP, ProRAW, Live Photos) don't go through the ticks. They go through your own node, the charging window or the trickle (`PLAN.md`, Stealth).

## 4. Video: hardware H.264 and H.265 against nu-media

### 4.1 Stored video at equal quality

The baselines are VideoToolbox hardware encoders at typical good streaming quality, around VMAF 93, on natural content. nu-media's target is the same VMAF with about 40% fewer bits than hardware HEVC; the realistic range from the literature is 30–50%. 60-second clip.

| Codec | Resolution and frame rate | Pixel rate (px/s) | Bitrate (bit/s) | bpp | Bits per minute | Size per minute |
| --- | --- | --- | --- | --- | --- | --- |
| H.264 hardware, 8-bit SDR | 1920 × 1080, 30 fps | 62,208,000 | 6,000,000 | 0.096 | 360,000,000 | 45.0 MB |
| HEVC hardware, 8-bit SDR | 1920 × 1080, 30 fps | 62,208,000 | 3,600,000 | 0.058 | 216,000,000 | 27.0 MB |
| HEVC hardware, Main 10 HDR | 1920 × 1080, 30 fps | 62,208,000 | 4,500,000 | 0.072 | 270,000,000 | 33.8 MB |
| HEVC hardware, Main 10 HDR | 3840 × 2160, 30 fps | 248,832,000 | 16,000,000 | 0.064 | 960,000,000 | 120.0 MB |
| AV1 (playback only on iPhone, for reference) | 1920 × 1080, 30 fps | 62,208,000 | 2,600,000 | 0.042 | 156,000,000 | 19.5 MB |
| **nu-media**, SDR target | 1920 × 1080, 30 fps | 62,208,000 | 2,200,000 | 0.035 | 132,000,000 | 16.5 MB |
| **nu-media**, HDR target | 1920 × 1080, 30 fps | 62,208,000 | 2,700,000 | 0.043 | 162,000,000 | 20.3 MB |
| **nu-media**, HDR target | 3840 × 2160, 30 fps | 248,832,000 | 9,600,000 | 0.039 | 576,000,000 | 72.0 MB |

Video doesn't fit the foreground ticks: one nu-media HDR minute at 1080p (162,000,000 bits) takes about 110 minutes at 24,576 bit/s. It goes through your own node or the charging window.

### 4.2 Calls at equal bits

Calls run at a fixed bitrate (stealth), so the comparison is what resolution and frame rate each codec delivers for the same bits. nu-media sends a reduced-resolution base layer and the receiver's Neural Engine adds super-resolution, artefact removal and frame interpolation (section 5). The table below is the design target; section 8.1 has the first measurements, which replace the HEVC base layer with AV1.

| Tier | Codec | Sent | Shown | bpp sent | bpp shown | Bits per minute |
| --- | --- | --- | --- | --- | --- | --- |
| L, 500,000 bit/s | H.264 hardware | 640 × 360, 30 fps | same | 0.072 | 0.072 | 30,000,000 |
| | HEVC hardware | 960 × 540, 30 fps | same | 0.032 | 0.032 | 30,000,000 |
| | **nu-media** | 960 × 540, 30 fps HEVC base | 1920 × 1080, 30 fps | 0.032 | 0.008 | 30,000,000 |
| M, 1,500,000 bit/s | H.264 hardware | 960 × 540, 30 fps | same | 0.096 | 0.096 | 90,000,000 |
| | HEVC hardware | 1280 × 720, 30 fps | same | 0.054 | 0.054 | 90,000,000 |
| | **nu-media** | 1280 × 720, 30 fps HEVC base | 1920 × 1080, 60 fps | 0.054 | 0.012 | 90,000,000 |
| H, 3,800,000 bit/s | H.264 hardware | 1280 × 720, 60 fps | same | 0.069 | 0.069 | 228,000,000 |
| | HEVC hardware | 1920 × 1080, 30 fps | same | 0.061 | 0.061 | 228,000,000 |
| | **nu-media** | 1080 × 1920, 30 fps, 10-bit HDR base | full panel 1206 × 2622, 60 fps (120 on ProMotion) | 0.061 | 0.020 | 228,000,000 |

Audio adds 1,920,000 bits per minute (Opus at 32,000 bit/s, constant).

## 5. How nu-media works

- **Images:** a learned transform codec. The analysis and synthesis networks run on the Neural Engine in FP16; the entropy model (hyperprior and context model) runs in integer arithmetic on the CPU, so every device decodes the exact same symbols. Learned codecs that run their entropy model in floating point break when encoder and decoder hardware differ; integer entropy models avoid that. Progressive: the first slot carries a preview, and each later slot refines the whole picture.
- **Video, three layers:**
  - **Base:** AV1 Main 10 at reduced resolution, encoded on the CPU at constant bitrate with low-delay prediction (no lookahead), so it can be used live. Hardware HEVC Main 10 at the same resolution is the low-power fallback. The base layer is always decodable on its own. CPU time and energy per frame on each supported chip are open until measured on device.
  - **Enhancement, outside the loop:** super-resolution, artefact removal and frame interpolation on the receiver's Neural Engine. It can't drift and needn't be bit-exact. Target budget on iPhone 18 Pro: 8 ms per frame at 60 fps and 300 mW, to be measured.
  - **Residual, inside the loop:** a learned integer residual layer adds detail on devices that can run it in real time. Stored video only at first.
- **Metadata:** all EXIF, GPS, device and time data is dropped; only colour and HDR metadata is kept.

## 6. HDR and colour: wider than the phone

nu-media carries more colour than the iPhone's screen shows, so the same file looks right on later displays.

| Property | nu-media | ImageIO HEIC / JPEG | Hardware H.264 / HEVC on iPhone |
| --- | --- | --- | --- |
| Primaries | **BT.2020** (about 76% of CIE 1931 xy; P3 is about 54%, sRGB about 36%) | P3 or sRGB | BT.709, P3, BT.2020 (HEVC Main 10) |
| Transfer | **PQ (SMPTE ST 2084, up to 10,000 nits) and HLG (BT.2100)**; sRGB and P3 gamma for SDR | sRGB gamma; HDR through a gain map | PQ, HLG (HEVC Main 10); SDR only on H.264 |
| Bit depth | **12-bit images, 10-bit video** (12-bit via the residual layer) | 8-bit JPEG; 8- or 10-bit HEIC | 8-bit H.264; 10-bit HEVC |
| Chroma | **4:4:4 images**; 4:2:0 video base with chroma restored by the enhancement layer | 4:2:0 typical | 4:2:0 |
| Working space | Linear-light FP16 in BT.2020, native to the Neural Engine | Display-referred | Display-referred |
| HDR metadata | Mastering display, MaxCLL/MaxFALL, and our own per-scene tone-mapping curves | ISO 21496-1 gain map | HDR10 static; Dolby Vision 8.4 from the camera |

- **Display:** the receiver tone-maps from PQ or HLG to the screen's current headroom with Apple's EDR APIs, so HDR stays HDR at 1,600 nits and degrades cleanly on SDR screens.
- **Export:** when you save to Photos or share outside khensu.nu, nu-media writes HEIC with an ISO 21496-1 gain map through ImageIO (images), or HEVC Main 10 HLG through VideoToolbox (video), so other apps show it correctly.
- **Dolby Vision and HDR10+:** received camera clips in Dolby Vision profile 8.4 are carried as their HLG base plus our own tone-mapping metadata. We play Dolby Vision and HDR10+ through Apple's decoders but don't author either; both need licences from their owners.
- **Cost of HDR:** about 10–25% more bits than SDR at the same quality (estimate), included in the tables above.

## 7. More than the usual formats

| Feature | What nu-media does |
| --- | --- |
| Up to 48 MP | Full-resolution originals, coded in tiles so any region can be fetched first |
| Alpha | Transparency channel for stickers and cut-outs |
| Depth | Portrait and LiDAR depth maps at a quarter resolution, for refocusing and AR |
| Spatial photos and video | The second eye coded as a residual from the first (Apple's spatial video is MV-HEVC 1080p30) |
| Live Photos | Still plus up to 3 s of motion, the motion as a video residual from the still |
| Screen content | A mode for screenshots and documents: sharp text, palettes, optional lossless |
| Lossless | Bit-exact mode for documents and originals |
| Region of interest | Extra bits on faces and text in the same file size |
| Later | 360° video in viewport tiles (Places), Gaussian splats and 3D capture |

## 8. Benchmark: replacing the estimates

A Swift test app, `nu-media/bench`, runs on iPhone 18 Pro and an iOS 26 device from the oldest supported generation and writes the tables above with measured numbers.

- **Codecs:**
  - ImageIO JPEG and HEIC at quality 0.3–0.95, with ImageIO AVIF and JPEG XL as decode-only references;
  - VideoToolbox hardware H.264 and HEVC Main and Main 10, both variable and constant bitrate, with low-latency rate control for the call tiers;
  - nu-media images and video.
- **Content:**
  - images: Kodak (24 images), the CLIC professional validation set, and our own iPhone captures in SDR and HDR;
  - video: the UVG sequences at 1080p and 4K, HDR test sequences, and recorded video-call content.
- **Quality metrics:**
  - all content: PSNR on Y′CbCr (6:1:1 weighting), MS-SSIM and VMAF;
  - HDR: PU21-encoded PSNR and VMAF, and colour error as ΔE_ITP (ITU-R BT.2124).
- **Results:** BD-rate against each baseline, bits per image and per minute, encode and decode time per image and per frame, and energy per image and per minute (MetricKit and power logs).
- **Pass criteria for shipping:**
  - images use at least 35% fewer bits than ImageIO HEIC at equal MS-SSIM;
  - calls score higher VMAF at the displayed resolution than hardware HEVC at the same tier;
  - decode is bit-exact across all supported devices;
  - no frame drops at 60 fps on iPhone 18 Pro.

Measured results go here, with the device, OS build and commit of each run.

| Run | Device | OS | Result |
| --- | --- | --- | --- |
| 8.1 | Apple M1 Pro (Mac, not iPhone) | macOS 26.4.1 | Video baselines and base layer only; no Neural Engine enhancement |

### 8.1 Desktop baseline run

`bench/codecs.py` with ffmpeg, data in `bench/results.json`. Source: *Tears of Steel* 1080p (Blender Foundation, CC BY 3.0), 6 s from 28 s, 24 fps, 8-bit 4:2:0. Quality is VMAF (libvmaf, default model) against the 1080p source. H.264 and HEVC use VideoToolbox with software fallback disabled, so these are Apple's hardware encoders; VideoToolbox undershoots its target by about 30%, so the table uses actual bitrates. nu-media rows are the base layer only, upscaled with Lanczos: a floor for the enhancement layer to build on.

| Codec | Real time live | ~350 kbit/s | ~700 kbit/s | ~1,400 kbit/s | ~2,800 kbit/s | kbit/s for VMAF 80 |
| --- | --- | --- | --- | --- | --- | --- |
| H.264, Apple hardware | Yes | 29.6 | 56.3 | 77.2 | 88.5 | 1,638 |
| HEVC, Apple hardware | Yes | 37.0 | 62.4 | 82.4 | 90.9 | 1,277 |
| nu-media base, HEVC hardware at 960 × 540 | Yes | 47.5 | 68.2 | 81.7 | 89.3 | 1,270 |
| nu-media base, SVT-AV1 real time at 960 × 540 | Yes, CPU | 63.5 (299) | 73.5 (560) | 82.0 (1,056) | 87.6 (2,062) | 912 |
| AV1, SVT-AV1 real time (CBR, low delay, preset 10) at 1080p | CPU heavy | 65.0 (334) | 75.0 (581) | 83.3 (1,114) | 89.7 (2,133) | 861 |
| AV1, SVT-AV1 preset 8, lookahead (not usable live) | No | 72.8 (248) | 83.1 (495) | 89.1 (956) | 92.8 (1,899) | 403 |

Bracketed figures are the actual kbit/s where an encoder didn't land near the column. Equal-bitrate check at 500 kbit/s (each encoder steered to within 3%): H.264 42.6, HEVC 50.9, nu-media HEVC base 59.2, nu-media AV1 base 72.0, real-time AV1 at 1080p 72.9.

What this changes and what it doesn't:

- **The base layer becomes AV1** (section 5). At low bitrates, encoding fewer pixels well beats encoding all of them badly; above about VMAF 85 full-resolution AV1 pulls ahead, which is where the enhancement layer has to earn its place.
- **Offline AV1 is the bar for the enhancement layer:** nu-media's target is that quality (about 400 kbit/s for VMAF 80 on this clip) in real time on iPhone. Unmeasured until the enhancement network exists.
- **AV2 and learned codecs are not measured here.** Published figures: AV2 about 30% fewer bits than AV1 (AOMedia); DCVC-RT 21% fewer than H.266 VTM and real time at 1080p only on an NVIDIA A100 (Jia et al., CVPR 2025). Neither has a phone encoder. The site plots them as estimates scaled from the offline AV1 curve (0.70 and 0.65).
- **One clip, one machine, 8-bit SDR.** The section 8 pass criteria still need the iPhone app, the full content set, HDR and energy.
