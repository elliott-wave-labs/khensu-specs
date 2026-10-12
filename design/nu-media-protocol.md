# nu-media protocol: container, bitstream, transport mapping and nu-transfer

Status: draft 0.1, 11 October 2026. Design only; nothing here is implemented or measured. It turns `design/nu-media.md` (what nu-media is and why) into wire formats, state machines and rules that code and test vectors can follow. Where this document and `nu-media.md` differ, `nu-media.md` describes intent and this document describes the wire. Open questions stay in `OPEN-QUESTIONS.md` section H (52 and 55); new ones found while writing this are in section 18.

**Figures.** No nu-media figure in this document has been measured. Every bitrate, size and time for nu-media is a **design target**; every figure for other products is an **estimate** from public material unless a measurement is cited (`nu-media.md` section 8). Values marked **TBD-spike** are fixed by measurement, then frozen.

## 1. Scope

This document specifies:

1. **The nu-media container and bitstream** (sections 3–9): stream and track headers, frame headers with 1 MHz timestamps, tiling, the three video layers, learned progressive images, colour and HDR, metadata stripping, and the quality modes.
2. **The transport mapping onto khensu** (section 10): images and small media inside the 2-second ticks, video calls on the constant-rate call tiers through two relays, and stored video and files on the bulk lane inside constant streams only.
3. **nu-transfer** (sections 11–12): free private file transfer with content-addressed, padded, fixed-size chunks sealed end to end, erasure coding, resumption and receiver pull by chunk hash, with an optional transcode to nu-media before sending or a bit-exact lossless send.

It relies on `PROTOCOL.md` for primitives (section 1), labels, MLS (section 4), content types (5.1), fragments (5.3), mailboxes (6.2), reliable delivery (6.7), calls (7, 7.1), mix packets and lane sizes (8.2, 8.3), SURBs (8.7) and ticks (8.8).

Out of scope: the training of the enhancement, residual and image networks; the DCI cinema package; Dolby Vision and HDR10+ authoring (`nu-media.md` section 6). 3D and Gaussian splats (`nu-3d.md`), audio beyond call Opus (`nu-audio.md`) and per-unit provenance (`nu-provenance.md`) are specified in their own documents, with registry entries proposed in 16.10.

## 2. Conventions

- Structures use the TLS presentation language (RFC 8446 section 3) exactly as `PROTOCOL.md` does: integers are big-endian, `opaque x<V>` is a vector with a QUIC-style varint length prefix (RFC 9000 section 16), `opaque x[N]` is fixed length, `varint` is a QUIC variable-length integer.
- `Label(x)`, `KDF`, `H`, `H256`, `AEAD`, `KEM`, `SIG`, `Sign` and `Verify` are as in `PROTOCOL.md` section 1: ML-KEM-1024, ML-DSA-87, AES-256-GCM, SHA-512, SHA-512/256, HKDF-SHA-512.
- The key words MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are used as in BCP 14 (RFC 2119, RFC 8174) when, and only when, in capitals.
- Pixel sizes are width × height. Bit rates are bits per second of the coded stream, excluding transport framing, unless a row says "on the wire". KiB = 1,024 bytes; MB = 1,000,000 bytes.
- Colour code points are those of ITU-T H.273.

## 3. Design rules

These rules bind every encoder, decoder and sender. They are the reason the format exists.

| Rule | Statement |
| --- | --- |
| R1 Native resolution | A sender MUST NOT scale a source down to fit the codec, the link or the bit budget. Stored media and transfers carry the source's native resolution, frame rate and bit depth; only the bitrate changes. Viewers choose lower resolution by fetching fewer tiles or an additional overview track (4.4), never by the sender replacing the native track. The one exception is the live call base layer (10.2), where the tier fixes the bits and a reduced coded size is signalled in the track header. |
| R2 No raw | nu-media has no uncompressed sample format and does not carry sensor raw (ProRes RAW, Apple ProRAW DNG, Blackmagic RAW). "Raw" in khensu means native resolution at a visually lossless bitrate (`visually_lossless`, 9.1), plus a mathematically lossless mode (`lossless`, 9.2). Raw camera files travel as opaque files in a bit-exact nu-transfer (11.12). |
| R3 Constant-bitrate base | The video base layer is hardware HEVC Main 10 at constant bitrate, always decodable on its own. |
| R4 Enhancement outside the loop | Receiver-side super resolution, artefact removal and frame interpolation never feed back into any reference picture, are never bit-exact and so cannot drift. |
| R5 Residual inside the loop | The learned residual layer is integer-only and bit-exact on every conforming decoder, because later residual frames predict from it. |
| R6 Fidelity | No generative texture: enhancement, residual and image networks MUST NOT use GAN or diffusion synthesis. Nothing appears that was not in the source. |
| R7 Metadata stripping | The container has no field for capture metadata. Only colour, HDR and timing relative to the stream start are carried (section 8). |
| R8 No frame loss | A decoder MUST present every coded frame it decodes. Interpolated frames are only added between coded frames, never substituted for them. |

## 4. Container

A nu-media object is a `StreamHeader` followed by zero or more `Segment`s. A file, a tick-lane object, a bulk transfer payload and a stored stream all use this layout. Calls use a compact framing of the same fields (10.2).

### 4.1 Stream header

```
opaque NuMagic[4] = { 0x6E, 0x75, 0x4D, 0x65 };   // "nuMe"

enum { call(1), stored(2), image(3), lossless(4), (65535) } Profile;

struct {
  opaque  magic[4];             // NuMagic
  uint16  version;              // 1 for this document
  Profile profile;
  uint32  flags;                // bit0 live (no index), bit1 tiled, bit2 has_overview; others 0
  TrackDescriptor tracks<V>;    // 1 to 16 tracks
  Extension extensions<V>;      // 4.7
} StreamHeader;
```

- A decoder MUST reject a `StreamHeader` whose `magic` differs, and MUST reject `version` values it does not implement (section 13).
- Unknown `flags` bits MUST be zero on send and ignored on receive.

### 4.2 Track descriptor

```
enum { video(1), image(2), audio(3), alpha(4), depth(5), second_eye(6), overview(7), data(8), (255) } TrackKind;

enum {
  hevc_main10(1),        // base layer, ITU-T H.265 Main 10 profile
  h264_high(2),          // fallback base for devices without HEVC Main 10 encode
  nu_residual_v1(3),     // learned integer residual (5.3)
  nu_image_v1(4),        // learned progressive image (6)
  nu_lossless_v1(5),     // mathematically lossless (9.2)
  opus(6),               // audio, RFC 6716
  (65535)
} CodecId;

enum { rectilinear(0), equirectangular(1), cubemap(2), fisheye_pair(3), (255) } Projection;

enum { cbr(1), lossless(2), (255) } RateControl;
enum { standard(1), visually_lossless(2), lossless(3), (255) } QualityMode;

struct {
  uint8       track_id;           // unique in the stream
  TrackKind   kind;
  CodecId     codec;
  uint8       depends_on;         // track_id of the base for residual, alpha, depth,
                                  // second_eye; 0xFF if none
  uint32      native_width;       // source size, R1
  uint32      native_height;
  uint32      coded_width;        // equals native except the call base exception (10.2)
  uint32      coded_height;
  TileGrid    grid;               // 4.4
  ColourDescription colour;       // 7.1; absent fields zero for audio and data
  Projection  projection;
  RateControl rate_control;
  QualityMode quality;
  uint32      nominal_bitrate;    // bit/s of the coded track; 0 for images and lossless
  uint8       reorder;            // 1 if frames may be coded out of presentation order
  opaque      codec_config<V>;    // codec-specific, below
  Extension   extensions<V>;
} TrackDescriptor;
```

`codec_config`:

| Codec | Contents |
| --- | --- |
| `hevc_main10`, `h264_high` | Empty. Each tile stream carries its own parameter sets in-band (4.5) |
| `nu_residual_v1` | `ResidualConfig` (5.3) |
| `nu_image_v1` | `ImageConfig` (6.1) |
| `nu_lossless_v1` | `LosslessConfig` (9.2) |
| `opus` | Opus identification header fields: channel count, pre-skip, input sample rate, channel mapping family and table (RFC 7845; families 2 and 3 for ambisonics, RFC 8486; `nu-audio.md` 7) |

Limits for version 1:

| Limit | Value |
| --- | --- |
| `native_width`, `coded_width` | 16 to 43,008 |
| `native_height`, `coded_height` | 16 to 21,504 |
| Frame area | at most 924,844,032 samples (43,008 × 21,504, a 42K equirectangular frame) |
| Tracks per stream | 16 |
| Coded frame rate per track | at most 2,000 fps (4.6) |

A decoder MUST reject a track exceeding these limits before allocating any frame buffer.

### 4.3 Segments

```
struct {
  uint64 first_pts_us;          // pts of the first frame in the segment
  uint32 frame_count;
  uint32 segment_bytes;         // bytes of all FrameRecords that follow
  SegmentIndex index;           // empty when StreamHeader.flags.live
} SegmentHeader;

struct {
  uint32 frame_offset;          // from the end of SegmentHeader
  uint16 tile_index;
  uint32 tile_offset;           // from the start of the frame's tile payload area
  uint32 tile_length;
} TileIndexEntry;

struct { TileIndexEntry entries<V>; } SegmentIndex;

struct { FrameHeader header; opaque tile_payloads[...]; } FrameRecord;   // lengths from header.tiles
```

- A segment starts at a random-access frame (`FrameHeader.flags.random_access`) for every video track in it. Default segment length: 1 s for `stored`, 2 s for 360° and VR content (TBD-spike).
- The `SegmentIndex` lets a receiver fetch only the tiles in its viewport (10.3.4). It is optional for `live` streams.

### 4.4 Tiling

```
struct {
  uint16 tile_width;            // 0 = untiled
  uint16 tile_height;           // 0 = untiled
  uint16 columns;               // ceil(coded_width / tile_width), 1 if untiled
  uint16 rows;                  // ceil(coded_height / tile_height), 1 if untiled
} TileGrid;
```

- **Untiled.** A video track MAY be untiled (one tile equal to the frame) only if `coded_width × coded_height ≤ 8,912,896` and each dimension is at most 8,444: the HEVC level 5.1 luma limits, so every hardware decoder can hold the frame. A 3840 × 2160 or 1206 × 2622 frame is untiled; 4096 × 2304 and anything larger is tiled.
- **Tiled.** `tile_width` and `tile_height` MUST each be a multiple of 128 from 512 to 2,048. The grid is uniform from the top-left; the last column and row carry the remainder, which MUST be at least 64 px, so senders pick a tile size that leaves it so. Tiles are numbered row-major from 0; `tile_index < columns × rows ≤ 3,528` (84 × 42 at 512 px on a 42K frame).
- **Independence.** Each tile is an independent elementary stream: its own parameter sets, its own reference pictures, no prediction across tile edges. Any tile decodes on its own, so a decoder holds only the tiles it was asked for. Edge tiles narrower than the HEVC minimum coding block are padded inside the tile stream and cropped with the conformance window.
- **Seams.** Version 1 has no tile overlap. The enhancement layer MAY smooth tile seams (5.2).
- **Overview track.** In addition to the native track, a sender MAY include a `kind = overview` track: the whole frame at a reduced size (for example a 4,096 × 2,048 full sphere under a 42K equirectangular track) so a viewer can turn its head before the native tiles arrive. This is an extra representation, so it does not break R1.
- **Images** use the same grid. A 48 MP original (8,064 × 6,048, `nu-media.md` section 7) is tiled at 1,024 or 2,048 px so any region can be fetched first.

### 4.5 Frame header

```
enum {
  base_intra(1),         // base layer random access or intra-refresh start
  base_inter(2),
  residual(3),
  image_layer(4),        // one progressive layer of an image (6.2)
  lossless_frame(5),
  audio_frame(6),
  data_frame(7),
  (255)
} FrameType;

struct {
  uint16 tile_index;
  uint32 length;                // bytes of this tile's payload in this frame
} TileEntry;

struct {
  FrameType type;
  uint8     track_id;
  uint16    flags;              // bit0 random_access, bit1 droppable,
                                // bit2 discontinuity, bit3 end_of_stream; others 0
  uint64    pts_us;             // presentation time, 1 MHz clock, 4.6
  int32     dts_offset_us;      // decode time = pts_us - dts_offset_us; 0 unless track.reorder
  uint32    duration_us;        // 0 = until the next frame of the track
  uint32    frame_seq;          // per track, +1 per coded frame, wraps
  TileEntry tiles<V>;           // tiles present, ascending tile_index; a subset when fetched by viewport
  Extension extensions<V>;
} FrameHeader;
```

- Tile payloads follow the header in `tiles` order. For `hevc_main10` and `h264_high`, a tile payload is a sequence of NAL units, each prefixed by a 4-byte big-endian length (the ISO/IEC 14496-15 layout with `lengthSizeMinusOne = 3`). Random-access frames carry VPS, SPS and PPS (or SPS and PPS for H.264) in-band in every tile.
- `droppable` marks frames no other frame references (residual frames always are droppable from the base's point of view; base frames never are in the `call` profile).
- `frame_seq` gaps tell the decoder a coded frame was lost; it conceals (section 12) and counts the loss.

### 4.6 Timestamps and frame rate

- `pts_us` counts microseconds from the stream start. The first frame of each track has `pts_us = 0`; there is no wall-clock or capture-time field anywhere in the format (R7).
- Frame rate is variable: there is no rate field. Within a track, `pts_us` strictly increases in presentation order, and consecutive coded frames MUST be at least 500 µs apart, which caps a track at 2,000 fps. A track can change rate at any frame.
- Rates in use: 30 and 60 fps on every device, 120 fps on ProMotion devices, 240 fps for camera slow motion, up to 2,000 fps for game capture to high-refresh displays (`nu-media.md` 7.1). Stored high-rate sources are coded at their native rate (R1). In calls the sender codes at most 60 fps and the receiver interpolates higher rates (5.2, 10.2).
- NTSC rates are carried exactly as microsecond timestamps (29.97 fps alternates 33,366 and 33,367 µs); no rounding of the source's own timing is allowed when the source has exact timestamps.
- Audio frames use the same clock. Lip sync is by `pts_us` only.

### 4.7 Extensions

```
struct {
  uint16 ext_type;              // registry 16.4
  uint8  critical;              // 1 = a decoder that doesn't know ext_type MUST reject the
                                //     containing header (stream, track or frame)
  opaque data<V>;
} Extension;
```

- An extension type appears at most once per header. Unknown non-critical extensions are skipped.
- Version 1 senders MUST NOT mark any extension in registry 16.4 critical except `residual_model` (it changes how the residual decodes).

## 5. Video layers

| Layer | Track codec | Inside the prediction loop | Bit-exact | Bits on the wire | Drift |
| --- | --- | --- | --- | --- | --- |
| Base | `hevc_main10` (or `h264_high`) | Yes, HEVC's own | Yes, per ITU-T H.265 | All of the rate | None (standard codec) |
| Enhancement | none | **No** | **No** | Zero (only an optional hint, 5.2) | Cannot drift |
| Residual | `nu_residual_v1` | Yes, its own loop | Yes (integer) | Part of the rate when present | Reset at every refresh |

### 5.1 Base layer

- **Codec.** HEVC Main 10 (ITU-T H.265, general_profile_idc 2), 4:2:0, 10-bit, primaries BT.2020, transfer PQ, HLG or SDR (7.1). Devices without HEVC Main 10 encode use `h264_high` (8-bit, SDR only) and signal it in the track.
- **Rate control.** Constant bitrate at `nominal_bitrate`, HRD-conformant, with low-latency settings in the `call` profile: no frame reordering, periodic intra refresh instead of keyframes (`PROTOCOL.md` 7.1), coded picture buffer at most 100 ms of the tier's payload capacity (design target). In the `stored` profile reordering is allowed (`reorder = 1`) and random-access frames start each segment.
- **Bitrate ladder.** The sender picks `nominal_bitrate` from the source's pixel rate and dynamic range. Design targets at VMAF 93 (`standard`), from `nu-media.md` 4.1:

  | Source | `standard` design target | `visually_lossless` estimate |
  | --- | --- | --- |
  | 1920 × 1080, 30 fps, SDR | 2.2 Mbit/s | about 2–3× `standard` |
  | 1920 × 1080, 30 fps, HDR | 2.7 Mbit/s | about 2–3× `standard` |
  | 3840 × 2160, 30 fps, HDR | 9.6 Mbit/s | about 2–3× `standard` |
  | Other sizes and rates | scale by pixel rate at about 0.035–0.045 bit per pixel, lower above 4K (estimate) | — |

  These figures include the residual layer and receiver enhancement that don't exist yet; the base alone at these rates scores lower (`nu-media.md` 8.2). The ladder is replaced by measured values from the benchmark.
- **Tiles.** For tiled tracks the rate is split over tiles by the encoder (more to tiles with more detail) and the sum stays constant per segment.
- **Conformance.** A conforming decoder MUST be able to present the base layer alone. Everything else is an improvement on top.

### 5.2 Enhancement layer (outside the loop)

The enhancement layer has no coded data. It is what the receiver's Neural Engine does to the decoded base (or base plus residual) before display:

| Operation | Bit in `EnhancementHint.allowed` |
| --- | --- |
| Super resolution from `coded` to `native` or display size | 0 |
| Artefact removal (blocking, ringing, banding) | 1 |
| Frame interpolation between coded frames | 2 |
| Chroma restoration from 4:2:0 toward 4:4:4 | 3 |
| Tile seam smoothing | 4 |

```
struct {
  uint8  allowed;               // bitmask above; default 0x1F for lossy video
  uint16 max_display_fps;       // ceiling for interpolation; 0 = display rate
} EnhancementHint;              // ext_type enhancement_hint, never critical
```

Rules:

- The decoder MUST NOT write enhanced pixels into any reference picture of the base or residual layer (R4). Enhanced output is display-only.
- Enhancement is never bit-exact. Two receivers may show slightly different pixels; neither affects later frames.
- The receiver chooses the enhancement per device and per moment (thermal state, battery, display), within `allowed`. Design target on iPhone 18 Pro: 8 ms per frame at 60 fps and 300 mW (`nu-media.md` 5), to be measured.
- Interpolated frames are inserted between two coded frames and timed on the 1 MHz clock. They are never stored, exported as coded frames, or counted as received frames (R8). A player that exports or screenshots MUST say whether the frame shown was interpolated.
- A sender sets `allowed = 0` for `lossless` tracks and for screen content where interpolation would mislead (text scrolling, slides); receivers MUST honour a cleared bit.
- Models are part of the app and identified by hash. A receiver MUST NOT download an enhancement model in response to a stream, because the download would reveal what is being watched.

### 5.3 Residual layer (inside the loop)

```
struct {
  opaque model_id[32];          // H256(Label("nm residual model") || model descriptor || weights)
  uint16 refresh_period;        // frames between residual refresh points, 1 to 600
  uint8  base_scale;            // 1 = same size as base; 2 = residual at 2x base (call L exception)
} ResidualConfig;
```

- A residual track (`kind = video`, `codec = nu_residual_v1`, `depends_on` = base track) carries a learned residual per frame. The residual reconstruction is `R_t = clip(U(B_t) + D(r_t, R_{t-1}))`, where `B_t` is the decoded base, `U` a specified integer upsampler (identity when `base_scale = 1`), `r_t` the entropy-decoded residual symbols and `D` the integer synthesis network, which also takes the previous residual reconstruction.
- **Integer only.** `D` and the entropy model use INT8 weights, INT32 accumulators, requantisation by arithmetic right shift with round-half-up, and saturation to INT16 activations. No floating point is allowed anywhere in residual decoding. Every conforming decoder produces identical `R_t`.
- **Refresh.** At every residual refresh point (`random_access` on the residual frame) `R_{t-1}` is replaced by `U(B_t)`, so a lost residual frame affects at most `refresh_period` frames.
- **Droppable.** The base never references the residual. A decoder that lacks the model named by `model_id`, can't run it in real time, or loses residual data drops the residual track and continues with base plus enhancement.
- **Scope.** Version 1 uses the residual layer for `stored` tracks only (`nu-media.md` 5). Calls may adopt it once real-time decode on the oldest supported device is measured.
- **12-bit, 4:4:4 stored video.** On a stored track the residual carries 12-bit 4:4:4 (`ColourDescription.bit_depth = 12`, `chroma_format = 3`) over the 10-bit 4:2:0 base, so the decoded picture has 4,096 steps per channel and a chroma sample on every pixel. That is four times the steps and four times the chroma samples of a Main 10 stream. Calls stay on the 10-bit base until residual decode is measured in real time on the oldest supported device.

## 6. Images

### 6.1 Learned image codec (`nu_image_v1`)

```
struct {
  opaque model_id[32];          // H256(Label("nm image model") || descriptor || weights)
  uint8  layer_count;           // progressive layers, 1 to 16
  uint8  flags;                 // bit0 screen_content mode, bit1 has_alpha_track, bit2 has_depth_track
} ImageConfig;
```

- Analysis and synthesis transforms run on the Neural Engine in FP16. The hyperprior and context models that produce the entropy coder's probability tables run in integer arithmetic on the CPU (same integer rules as 5.3), and the entropy coder is a range coder with 16-bit integer CDFs. Every device therefore decodes **exactly the same symbols**. Learned codecs that compute their entropy model in floating point fail when encoder and decoder hardware differ; this design avoids that.
- Synthesis is FP16, so decoded pixels may differ slightly between devices. Conformance: decoded pixels MUST be within 2 code values (12-bit) of the reference decoder at every sample (TBD-spike: confirm this tolerance holds on A13 to A20 Pro and M-series). No reference picture depends on them, so the difference never grows.
- Colour: 12-bit, 4:4:4, BT.2020 primaries, PQ, HLG or SDR transfer; RGB (`matrix_coefficients = 0`) or ICtCp (14).
- `screen_content` mode, for screenshots and documents, uses a model trained for sharp text and flat colour, and MAY switch to `nu_lossless_v1` per tile.

### 6.2 Progressive layers

- Layer 0 is a **preview** of the whole picture. Each later layer refines the **whole** picture (more latent channels, then finer quantisation), so every arrival makes all of it sharper rather than revealing it row by row.
- An image track carries one `image_layer` frame per layer, all with `pts_us = 0`, in layer order. A layer frame holds that layer for every tile present.
- **Sizing for ticks.** When an image is sent on the tick lane (10.1), the encoder sizes layer 0 to at most one tick chunk payload (1,990 bytes, 15,920 bits) and pads every layer to end on a tick chunk boundary, so the receiver can render after each complete chunk group without waiting for the rest.
- Design targets for a 3,162,132-pixel full-screen photo (`nu-media.md` 3): preview 1 chunk; full image 15–40 KB in `standard` quality, which is 8–21 chunks.

### 6.3 Other image content

| Content | Encoding |
| --- | --- |
| Alpha | `kind = alpha` track, 12-bit single channel, same tile grid, `depends_on` the colour track |
| Depth | `kind = depth` track at a quarter of the colour resolution |
| Spatial photo or video | `kind = second_eye`, coded as a residual from the first eye |
| Live Photo | One image track (the still) plus one video track of up to 3 s whose first frame predicts from the still, plus an Opus track. Design target about 200 KB in total. The receiver builds a `PHLivePhoto` with a fresh asset identifier generated on the receiving device |
| 48 MP originals | Tiled image track in `standard` or `visually_lossless`; never on the tick lane (10.4) |

## 7. Colour and HDR

### 7.1 Colour description

```
struct {
  uint8 colour_primaries;          // H.273: 9 = BT.2020 (required for video and images)
  uint8 transfer_characteristics;  // H.273: 16 = PQ (ST 2084), 18 = HLG (BT.2100),
                                   //        13 = sRGB / Display P3, 1 = BT.709
  uint8 matrix_coefficients;       // H.273: 9 = BT.2020 non-constant luminance (video base),
                                   //        0 = identity / RGB, 14 = ICtCp (images)
  uint8 full_range;                // 0 = narrow (video base), 1 = full (images)
  uint8 bit_depth;                 // 10 video base, 10 or 12 residual, 12 images
  uint8 chroma_format;             // 0 = 4:0:0, 1 = 4:2:0 (video base), 3 = 4:4:4 (images)
} ColourDescription;
```

- The primaries are always BT.2020. P3 and BT.709 sources are placed inside the BT.2020 gamut without clipping; SDR sources keep an SDR transfer. This lets the same file look right on later wide-gamut displays.
- Encoders work internally in linear-light FP16 BT.2020, the Neural Engine's native precision.

### 7.2 HDR metadata

| Extension | Contents |
| --- | --- |
| `mastering_display` | SMPTE ST 2086 primaries and white point (x, y in units of 0.00002), max and min luminance (units of 0.0001 cd/m²) |
| `content_light_level` | MaxCLL and MaxFALL in cd/m² |
| `tone_map_curve` | Per-scene curves: `struct { uint64 scene_start_us; uint16 target_peak_nits; uint8 knot_count; Knot knots[knot_count]; }` with `Knot { uint16 in_pq; uint16 out_pq; }`, up to 33 knots, piecewise linear in PQ code values |

- The receiver tone-maps from PQ or HLG to the display's current headroom (Apple EDR on Apple devices), using `tone_map_curve` when present.
- Export outside khensu writes HEIC with an ISO 21496-1 gain map (images) or HEVC Main 10 HLG (video) through the platform encoders (`nu-media.md` 6). Received Dolby Vision profile 8.4 clips are carried as their HLG base plus `tone_map_curve`; nu-media does not author Dolby Vision or HDR10+.

## 8. Metadata stripping

The encoder takes pixels, samples and colour metadata from the source and nothing else. The container has no field for, and an encoder MUST NOT carry in any extension, codec SEI or user data:

- EXIF, XMP, IPTC, maker notes, GPS, altitude, heading, motion sensor data;
- device make, model, serial number, lens identifiers, software version;
- capture, modification or upload date and time, time zone;
- original file name (a nu-transfer carries a file name only inside the end-to-end encrypted manifest, 11.6, and only if the user keeps it);
- embedded thumbnails, face regions, Photos asset identifiers, depth calibration data beyond what depth decoding needs.

Further rules:

- **Orientation** is applied to the pixels before encoding; there is no orientation flag.
- **HEVC SEI.** Base-layer tile streams MUST contain only these SEI payload types: mastering display colour volume, content light level, alternative transfer characteristics, decoded picture hash, and recovery point. Encoders strip everything else (including user data unregistered SEI, which some hardware encoders insert).
- **Not removed.** Sensor noise patterns (PRNU) and scene content can still identify a camera or place. That is a property of the picture, not of the format (section 15).

## 9. Quality modes

### 9.1 `standard` and `visually_lossless`

- `standard` is the ladder in 5.1 (design target VMAF 93 on natural content).
- `visually_lossless` is native resolution at a bitrate where trained viewers can't tell the decoded result from the source in a flicker test at the native display size (TBD-spike; design target VMAF at least 97 with no visible banding in HDR). It is the mode for masters, review copies and anything a user calls "raw" (R2).

### 9.2 `lossless`

```
struct {
  uint8 transform;              // 1 = reversible YCoCg-R, 0 = none (source RGB or Y'CbCr kept)
  uint8 predictor;              // 1 = learned integer context model, 2 = MED (LOCO-I) fallback
} LosslessConfig;
```

- Decoded samples MUST equal the source samples exactly, at the source bit depth and chroma format. Every `lossless_frame` carries the SHA-512 of its decoded samples in a `sample_hash` extension, and a decoder MUST report failure if the hash differs.
- Version 1 codes each frame intra-only per tile; inter-frame lossless is future work. Lossless video is very large (for 4K30 10-bit, estimated at several hundred Mbit/s) and is for local networks, own nodes and dedicated links.
- Enhancement is disabled (`allowed = 0`).
- A bit-exact copy of the **original file** is a different thing: that is a nu-transfer in `bit_exact` mode (11.12), which sends the source bytes untouched.

## 10. Transport mapping onto khensu

| Content | Lane | Carrier | Section |
| --- | --- | --- | --- |
| Photos, screenshots, stickers, Live Photos at screen size, voice notes, short clips up to `TICK_MEDIA_MAX` | Small (2,048 B payload) | The 2-second foreground ticks, in place of cover | 10.1 |
| Live video and audio in calls, rooms, Places | Call tiers | WebTransport sessions to two relays run by different operators, joined by padded trunks | 10.2 |
| Stored video, originals, 360° and VR, files | Bulk (65,536 B payload) | Constant streams only: the user's own node, the Wi-Fi-and-charging window, call trunks | 10.3 |

### 10.1 Images and small media in the ticks

Each foreground tick is one `fetch` plus 3 outgoing small packets (`PROTOCOL.md` 8.8). Media chunks take outgoing slots that would otherwise carry cover, so the external pattern never changes.

**Tick chunk.**

```
struct {
  opaque chunk_ref[16];         // H256(Label("nm tick ref") || k_obj || uint32(leaf) || uint32(i))[0..16]
  opaque ct[2008];              // AEAD(k_i, zero_nonce, TickChunkPlain), includes the 16-byte tag
} TickChunk;                    // 2,024 bytes: the Fragment data size (PROTOCOL 5.3)

struct {
  uint16 used;                  // bytes of data that are real; the rest is zero
  opaque data[1990];
} TickChunkPlain;               // 1,992 bytes

k_obj = random 32 per media object
k_i   = KDF(k_obj, Label("nm tick chunk") || uint32(leaf) || uint32(i), 32)
```

- `leaf` is the recipient's MLS leaf index. Chunks are encrypted per recipient leaf, so the same image sent to several members produces unrelated ciphertexts and refs, and mailbox nodes can't link the members' mailboxes by matching items. The sender pays one encryption per recipient leaf; the bits per recipient are unchanged.
- `chunk_ref` is different for every chunk, so a mailbox node can't group chunks of one object. The receiver computes the refs it expects from `k_obj` and matches them.
- A `TickChunk` is stored with `store` (`PROTOCOL.md` 6.2) as the `sealed` item to the recipient leaf's mailbox, framed exactly like a `Fragment`, so its encoded length equals a Fragment's and a mailbox node can't tell media from messages.
- Chunk data is the nu-media object (header plus frames) cut into 1,990-byte pieces in order.

**Offer.** The sender first sends an MLS message:

```
struct {
  opaque k_obj[32];
  uint16 chunk_count;           // at most TICK_MEDIA_MAX
  uint16 layer_ends<V>;         // chunk index after which each progressive layer is complete
  uint32 native_width;
  uint32 native_height;
  opaque media_type<V>;         // "application/nu-media" or "video/nu-media"
  opaque inline_chunk<V>;       // optional: TickChunkPlain for chunk 0 (the preview), so it
                                // arrives with the offer
} TickMediaOffer;               // body of content type media_offer (16.9)
```

- With `inline_chunk`, the offer needs a larger fragment bucket (4 instead of 3) and the preview shows as soon as the offer is reassembled.
- `TICK_MEDIA_MAX` = 256 chunks (509,440 bytes of data) by default, a consensus-tunable client parameter. Larger objects go to the bulk lane (10.3). Design target sizes: a full-screen photo 8–21 chunks (about 3–7 ticks), a Live Photo about 101 chunks (about 34 ticks, about 70 s).

**Scheduling** of the 3 outgoing slots, highest first: store receipts and acks; message fragments (oldest first); typing events; PIR queries; tick media chunks in layer order, round-robin between objects so one large object doesn't block a second photo's preview.

**Receiving.** The receiver's normal fetch returns tick chunks with other items. After each complete layer (all chunks up to `layer_ends[n]`), it decodes and redraws. Missing chunks are retried by the sender under the normal reliable-delivery rules (`PROTOCOL.md` 6.7): same bytes, backoff, inside cover slots only.

**Throughput.** 3 chunks per tick is 5,970 data bytes every 2 s, about 23,880 bit/s of nu-media data while the app is in the foreground and the slots are otherwise free. There are no tick media in the background (there are no background ticks).

### 10.2 Video calls on the constant-rate tiers

Calls follow the stealth call profile (`PROTOCOL.md` 7.1) in full: setup over the mixnet, two entry relays from different operators, autonomous systems and jurisdictions, constant-rate padded trunks between relays, WebTransport over HTTP/3 inside khensu camouflage, SFrame with per-sender keys from the MLS exporter, edge blurring, relay rotation.

**Objects.** Every media object is exactly 1,200 bytes of SFrame ciphertext (header, encrypted payload, 16-byte tag) at the tier's fixed rate:

| Tier | Objects per second | Interval | On the wire (objects only) | Video payload capacity | Encoder rate (design target, 0.95 × capacity) |
| --- | --- | --- | --- | --- | --- |
| Audio | 50 | 20 ms | 160 B objects, 64,000 bit/s | — | Opus CBR 32,000 bit/s, DTX off |
| L | 60 | 16.67 ms | 576,000 bit/s | about 551,000 bit/s | about 524,000 bit/s |
| M | 160 | 6.25 ms | 1,536,000 bit/s | about 1,470,000 bit/s | about 1,397,000 bit/s |
| H | 400 | 2.5 ms | 3,840,000 bit/s | about 3,677,000 bit/s | about 3,493,000 bit/s |

Capacity assumes a typical 17-byte SFrame header and the 18-byte object header below, leaving 1,149 bytes of video per object. The tier names "about 500 kbit/s, 1.5 Mbit/s, 3.8 Mbit/s" in `PROTOCOL.md` are on-the-wire rates; the encoder runs at the lower figures here (see 18).

**Object plaintext (inside SFrame).**

```
enum { padding(0), media(1), (255) } CallObjectKind;

struct {
  CallObjectKind kind;
  uint8  flags;                 // bit0 frame_start, bit1 frame_end, bit2 random_access
                                // (intra-refresh start), bit3 tone_map follows in data
  uint16 data_len;              // 0 for padding
  uint32 frame_seq;
  uint64 pts_us;                // 1 MHz, from call start
  uint16 tile_index;            // 0 when untiled
  opaque data[data_len];        // part of the frame's tile payload (length-prefixed NAL units)
  opaque zero_pad[...];         // fills the object to exactly 1,200 bytes after SFrame
} CallObjectPlain;              // 18-byte header
```

- The sender computes `zero_pad` from the actual SFrame header length, so the ciphertext is always 1,200 bytes even when the SFrame KID or counter grow. Padding sits inside the SFrame ciphertext, so relays can't tell padding from media.
- Objects go out at exact tier intervals with no burst. A frame bigger than its share waits for later slots; the CBR buffer limit (5.1) bounds the wait. Empty slots carry `padding` objects.
- Every QUIC packet carrying call objects MUST be padded with QUIC PADDING frames to one fixed size per session (TBD-spike, about 1,350 bytes), so variable MOQT object headers don't show through packet sizes.
- **Base-size exception (R1).** At tier L the sender MAY code the base at a reduced size (for example 960 × 540 for a 1920 × 1080 camera), signalled in `coded_width` and `coded_height`, and the receiver's enhancement restores the native or display size. Measurements so far (`nu-media.md` 8.2) show a reduced base loses to a full-size base on current Apple hardware at 720p and 4K, so senders SHOULD use full size at M and H and decide at L per chip (TBD-spike).
- **Frame rate.** The sender codes at most 60 fps. The receiver interpolates to 120 fps on ProMotion and 240 fps where enabled, at no extra bits (5.2). Interpolated frames are never counted as received.
- **Tier changes** happen at most every 30 s, between adjacent tiers, with hysteresis, at a random-access point (`PROTOCOL.md` 7.1).
- **Group calls** add `FrameManifest` on the data track (`PROTOCOL.md` 7). `tags_hash` covers the SFrame tags of every object in the interval, padding included, so a relay can't drop objects selectively without detection.

**MOQ mapping.** One MOQT session per relay connection; the track namespace is a per-call random 16-byte value (hex) agreed in call setup. Tracks:

| Track name | Content | Group | Object | Priority |
| --- | --- | --- | --- | --- |
| `a` | Opus | 1 s | one 160 B object | highest |
| `v0` | Base video, tile 0 or untiled | one intra-refresh period | one 1,200 B object | high |
| `v0.t<n>` | Base video tile *n* (tiled live sources, Places) | one intra-refresh period | one 1,200 B object | high |
| `m` | `FrameManifest`, tone-map updates | 1 s | one 1,200 B object | medium |

Places and other live 360° sources subscribe to tile tracks by viewport and to an overview track. Each subscribed track is constant-rate, so the set of tracks a viewer subscribes to, and when it changes, is visible to its entry relay but not their content; viewers SHOULD keep a fixed number of tile subscriptions and move them, rather than adding and removing (TBD-spike).

### 10.3 Stored video and files on the bulk lane

Bulk packets travel only inside constant streams (`PROTOCOL.md` 8.8). A constant stream sends a fixed number of fixed-size bulk packets per interval for its whole life, whether or not there is anything to send; real chunks replace cover.

| Carrier | Who sends | When it runs | Rate | Path |
| --- | --- | --- | --- | --- |
| Own node | The user's own node (`khensu-tatenan` on a Mac or Pi 5, or a suñůlink.shield) | Always, at the node's capacity class | Node cover rate from the epoch header | Phone to own node over the local network at a constant rate; own node into the mixnet, 5 hops |
| Wi-Fi-and-charging window | The phone | While on Wi-Fi and charging, opened whether or not anything is queued | Window rate from the epoch header | Phone into the mixnet, 5 hops |
| Call trunk | The phone, in a transfer session (call profile with a data track and no media) | While both sides are online | A call tier rate | Two relays, as a call (10.2); not the mixnet |

- **Window rule.** The Wi-Fi-and-charging window MUST open whenever its conditions hold, after a random delay (TBD-spike, uniformly 0–10 min), and run for a random length (TBD-spike), whether or not any transfer is queued. Otherwise the window itself would reveal that the user is sending something.
- **Trunk sessions** are faster (two relays, no mix delays) but give the weaker anonymity of a call (relays see each endpoint's IP and that a session exists, as for any call). The app offers them only when both sides are online and the user chooses speed.
- Bulk content is always a nu-transfer (section 11), including stored nu-media video, originals and attachments larger than `TICK_MEDIA_MAX`.

#### 10.3.4 Viewport fetch for 360° and VR

A stored 360° or VR stream is transferred as a nu-transfer whose payload is the nu-media object. The receiver fetches the stream header, the segment indexes and the overview track first, then fetches the chunks that hold the tiles in and near its viewport, then the rest in the background. Because nu-transfer chunks are pulled by hash (11.8), fetch order is the receiver's choice and nodes see only uniform chunk requests.

## 11. nu-transfer: private file transfer

### 11.1 Properties

| Property | How |
| --- | --- |
| Free | No per-transfer charge. Uses the sender's and receiver's anonymous access tokens (`PROTOCOL.md` 11.1) and their rate limits; retention follows the token tier |
| End to end | Chunks and manifest are sealed with keys only sender and recipients hold (11.2); key delivery is MLS (ML-KEM-1024) or a standalone ML-KEM-1024 seal (11.7); manifests are signed with ML-DSA-87 |
| No server sees plaintext or names | File names, types, sizes and hashes are inside the encrypted manifest. Nodes see fixed-size ciphertext chunks addressed by hash |
| Content-addressed | Every chunk is stored and fetched under the hash of its ciphertext; nodes verify it on store |
| Padded, fixed size | Every chunk is 61,440 bytes sealed; the chunk count is padded (11.5) |
| Erasure coded | Systematic Reed–Solomon stripes; any *k* of *k + m* chunks per stripe rebuild it (11.4) |
| Resumable | Both sides keep per-chunk state durably; any chunk can be resent or refetched in any order |
| Receiver pulls | The receiver fetches chunks by hash through SURBs, in its own order and at its own constant rate |

### 11.2 Keys and labels

```
transfer_secret = random 32                                   // per transfer, sender
transfer_id     = random 16
k_root          = KDF(transfer_secret, Label("nt root"), 32)
k_man_j         = KDF(transfer_secret, Label("nt manifest") || uint32(j), 32)
k_chunk_i       = KDF(transfer_secret, Label("nt chunk") || uint32(i), 32)
del_i           = KDF(transfer_secret, Label("nt delete") || uint32(i), 32)   // also for root and manifest chunks, domain-separated by role
sealed          = AEAD(k, zero_nonce, ChunkPlain, aad = transfer_id || uint8(role) || uint32(index))
chunk_addr      = H256(Label("nt chunk addr") || sealed)
```

- Every key encrypts exactly one plaintext, so the zero nonce is safe.
- Chunk addresses are hashes of ciphertext under a random per-transfer key. There is **no convergent encryption**: the same file sent twice, or by two people, produces unrelated chunks. This gives up cross-transfer deduplication to prevent confirmation-of-file attacks.

### 11.3 Chunk format

```
enum { root(1), manifest(2), data(3), parity(4), (255) } ChunkRole;   // inside the ciphertext only

struct {
  uint32 used;                  // real bytes in data; 0 for padding chunks
  opaque data[61420];
} ChunkPlain;                   // 61,424 bytes

SealedChunk = opaque[61440];    // AEAD output: 61,424 + 16-byte tag
```

- `SealedChunk` is fixed at 61,440 bytes so a `chunk_put` with its framing and access token fits the 65,536-byte bulk payload (`PROTOCOL.md` 8.3), with 4,096 bytes left for framing (TBD-spike once the access token size is fixed).
- The payload (the file, or the nu-media object after transcode) is cut into 61,420-byte pieces in order. The last piece's `used` is less than 61,420; padding chunks have `used = 0` and zero data.

### 11.4 Erasure coding

```
struct {
  uint8  k;                     // data chunks per stripe, 1 to 64
  uint8  m;                     // parity chunks per stripe, 0 to 32
  uint32 stripe_count;
} CodingParams;
```

- Defaults: `k = 16, m = 4` (25% overhead). For fewer than 16 data chunks, one stripe with `k` = the data chunk count and `m = max(1, ceil(k / 4))`.
- Code: systematic Reed–Solomon over GF(2^8) with a Cauchy generator matrix (exact matrix and test vectors in `khensu-core/vectors/nt-rs/`, TBD), applied to the `ChunkPlain` bytes of each stripe **before** encryption. Each data and parity chunk is then sealed separately, so nodes can't tell parity from data.
- Chunk indices are stripe-major: stripe *s* holds data chunks `s·(k+m)` to `s·(k+m)+k−1`, then its parity.
- The receiver needs any `k` chunks of each stripe. Erasure coding covers replicas that expired, failed or were rotated out, without the sender re-uploading.

### 11.5 Size padding

- Let `n` be the number of data chunks the payload needs. The sender stores `n' = max(4, Padmé(n))` data chunks, the extra ones being padding chunks, then adds parity. Padmé (Nikitin et al., PETS 2019): with `E = floor(log2 n)`, `S = floor(log2 E) + 1`, `z = E − S`, `n' = (n + 2^z − 1) & ~(2^z − 1)`; for `n ≤ 2`, `n' = n`.
- Padmé overhead is at most about 12% and leaks O(log log n) bits of size. The minimum of 4 data chunks (about 245 KB) makes all small files look alike.
- The receiver MUST fetch padding chunks like any other, so nodes and observers see only the padded count.

### 11.6 Manifest

```
enum { bit_exact(1), nu_media(2), (255) } TransferMode;

struct {
  uint16       version;         // 1
  opaque       transfer_id[16];
  TransferMode mode;
  opaque       name<V>;         // UTF-8 file name, inside encryption only; empty if the user strips it
  opaque       media_type<V>;   // e.g. "video/nu-media", "application/pdf", "application/octet-stream"
  uint64       payload_size;    // bytes of the payload sent
  opaque       payload_hash[64];// H(payload)
  uint64       source_size;     // nu_media mode: size of the original before transcode; else = payload_size
  opaque       source_hash<V>;  // nu_media mode: H(original), 64 bytes, optional; else empty
  CodingParams coding;
  uint32       chunk_count;     // all data, padding and parity chunks
  opaque       chunk_addrs<V>;  // 32 bytes per chunk, index order
  uint64       expires_epoch;   // network epoch after which nodes may drop the chunks
  Extension    extensions<V>;
} TransferManifest;

struct {
  TransferManifest manifest;
  opaque       signer_ref[32];  // H256 of the signer's ML-DSA-87 public key
  opaque       signature<V>;    // Sign(signer_sk, "nt manifest", manifest)
} SignedManifest;

struct {
  opaque       manifest_addrs<V>;  // chunk_addr of each manifest chunk, in order
  uint32       manifest_bytes;
} RootChunk;                       // ChunkPlain.data of the single root chunk
```

- The `SignedManifest` is serialized, cut into manifest chunks (role `manifest`, keys `k_man_j`) and listed by address in one root chunk (role `root`, key `k_root`). One root chunk holds up to 1,918 manifest addresses, each manifest chunk up to 1,919 chunk addresses, so version 1 handles about 3.68 million chunks per transfer, about 180 GB of payload at default coding. Larger payloads are split into several transfers.
- **Signer.** In group mode the signer key is the sender's current MLS leaf signature key (ML-DSA-87), which rotates and is revealed to the group after 7 days (`PROTOCOL.md` 4.1), so a manifest has the same deniability as a message. In standalone mode (11.7) the signer is the sender's device signature key, which is not deniable; the UI says so.
- `source_hash` lets a recipient who later receives the original confirm it is the file the transcode came from. A sender who doesn't want to commit to the original leaves it empty.
- `created` times are deliberately absent (R7); `expires_epoch` is coarse (one hour).

### 11.7 Offer delivery

**Group mode (default).** The sender sends a `TransferOffer` as an MLS application message in the conversation:

```
struct {
  opaque transfer_secret[32];
  opaque transfer_id[16];
  opaque root_addr[32];
  uint64 padded_bytes;          // chunk_count × 61,420, for the UI and the fetch plan
  opaque preview<V>;            // optional nu-media preview layer, at most 1,990 bytes
} TransferOffer;                // body of content type transfer_offer (16.9)
```

The offer reveals only to the group what the manifest reveals; nodes see a normal fragmented MLS message.

**Standalone mode** (to one's own other devices or own node, or to a recipient's published KeyPackage before a group exists):

```
struct {
  opaque kem_ct[1568];          // KEM.Encaps(recipient_ek): ML-KEM-1024
  opaque ct<V>;                 // AEAD(KDF(ss, Label("nt offer"), 32), zero_nonce, TransferOffer)
} SealedOffer;
```

`SealedOffer` is stored like a fragment to the recipient's intro mailbox (`PROTOCOL.md` 6.1) or handed to the own node over the local link.

**Early offer.** The sender MAY send the offer as soon as the root and manifest chunks are stored, so the receiver starts pulling while upload continues; chunks not yet stored return `not_found` and are retried.

### 11.8 Mailbox operations

nu-transfer adds four operations to `MailboxOp` (`PROTOCOL.md` 6.2). For these the `mailbox_id` field carries the chunk address (put, delete) or zero bytes (get, stat).

```
enum { ..., chunk_put(7), chunk_get(8), chunk_stat(9), chunk_delete(10), (255) } MailboxOp;

struct { opaque chunk_addr[32]; opaque surb<V>; } ChunkPull;

    case chunk_put:    opaque delete_check[32];     // H256(Label("nt delete check") || del_i)
                       uint32 retain_epochs;        // capped by token tier
                       opaque sealed_chunk[61440];
    case chunk_get:    ChunkPull pulls<V>;          // 1 to 7
    case chunk_stat:   opaque chunk_addrs<V>;       // 1 to 1,024 addresses
                       opaque surb<V>;
    case chunk_delete: opaque delete_secret[32];    // del_i
```

Replies (through the SURB, each padded to the bulk payload size):

```
enum { ok(0), not_found(1), (255) } ChunkStatus;

struct {
  ChunkStatus status;
  opaque      chunk_addr[32];
  opaque      sealed_chunk[61440];          // zero bytes if not_found
} ChunkReply;

struct {
  uint64 network_epoch;
  opaque replica_node_id[32];
  opaque present_bitmap<V>;                 // bit j = chunk_addrs[j] held
  opaque signature<V>;                      // Sign(node_key, "chunk stat", fields above)
} ChunkStatReply;
```

Node behaviour:

- **Placement.** A chunk lives on three replicas chosen by rendezvous hashing of `chunk_addr` over the epoch's mailbox nodes, distinct operators and networks, as for mailbox items (`PROTOCOL.md` 6.2). The first replica copies to the other two.
- **Verification on put.** The node MUST check `H256(Label("nt chunk addr") || sealed_chunk) = chunk_addr` and the exact length, and drop the request otherwise (`addr_mismatch`, `bad_size`). A put of an address already held is a no-op (idempotent).
- **Retention.** Until `retain_epochs` after the put, capped by the token tier (30 days Free, 90 days Plus, `PROTOCOL.md` 6.2), or until a valid `chunk_delete`, whichever is first.
- **Delete.** `chunk_delete` succeeds only if `H256(Label("nt delete check") || delete_secret)` equals the stored `delete_check`. Only the sender holds `del_i`; recipients can't delete unless the sender gives them the secrets.
- **Get.** A node answers each `ChunkPull` through its SURB with a `ChunkReply`, on the bulk lane. Seven SURBs (8,248 bytes each) fit one bulk request, so a receiver's uplink is about one request per seven chunks it downloads.
- Nodes keep no record of who fetched what beyond the replay filter.

### 11.9 Sender state machine

```
IDLE --start(file, mode)--> PREPARING
PREPARING: [nu_media] transcode (11.12); hash; cut; pad (11.5); erasure code (11.4);
           seal every chunk; write all SealedChunks and the manifest to the durable outbox
PREPARING --ok--> UPLOADING            --error--> FAILED(prepare_error)
UPLOADING: chunk_put each chunk inside constant-stream slots (root and manifest first)
UPLOADING --manifest stored and early offer chosen--> UPLOADING + OFFERED
UPLOADING --all puts sent--> CONFIRMING
CONFIRMING: chunk_stat in batches; a chunk is Stored when 2 of 3 replicas report it;
            re-put chunks that aren't, with backoff
CONFIRMING --every chunk Stored--> OFFERED (send TransferOffer if not yet sent)
OFFERED --TransferDone from every recipient device--> COMPLETE
OFFERED --expires_epoch passed--> EXPIRED
any --user cancels--> CANCELLING: chunk_delete every chunk --> CANCELLED
COMPLETE --sender option "delete after delivery" (default on)--> chunk_delete all
```

- Every state and per-chunk status (`pending`, `put_sent`, `stored`) is written durably before the network action it records, so a crash resumes where it stopped. Resent puts carry identical bytes.
- No constant stream available: the machine waits in its state; nothing is ever sent outside a constant stream.

### 11.10 Receiver state machine

```
OFFERED: show sender, padded size, preview; auto-accept below a user-set size
OFFERED --accept--> FETCH_ROOT --> FETCH_MANIFEST
FETCH_MANIFEST --all manifest chunks--> VERIFY_MANIFEST
VERIFY_MANIFEST: version; Verify(signature) with the sender's leaf key from the group
                 (or device key in standalone); chunk_count and coding consistent;
                 sizes within limits
VERIFY_MANIFEST --ok--> FETCHING       --fail--> FAILED(manifest_invalid)
FETCHING: chunk_get in the receiver's chosen order (viewport first for 360°); for each
          reply, check H256(sealed) = addr, decrypt, mark have; per stripe, decode as soon as
          k chunks are held and stop fetching that stripe
FETCHING --a stripe has < k reachable chunks after retries--> FAILED(insufficient_chunks)
FETCHING --all stripes decoded--> VERIFYING
VERIFYING: H(payload) = payload_hash; for lossless nu-media, per-frame sample hashes
VERIFYING --ok--> DONE: send TransferDone (MLS message: transfer_id) --> sender
VERIFYING --fail--> FAILED(hash_mismatch)
any --user declines or deletes--> DISCARDED (no message to the sender beyond the normal receipt)
```

- The have-bitmap and decoded stripes are durable, so a transfer resumes after app kill, reboot or weeks offline, within retention.
- Even after a stripe decodes with `k` chunks, the receiver SHOULD keep requesting chunks up to the stripe's padded total at the same constant rate, choosing among its remaining chunks, unless the carrier is the user's own node; this keeps its fetch volume tied to the padded size, not to which replicas happened to answer (TBD-spike: cost versus leak).

### 11.11 Resumption and duplicates

- Sender and receiver can each stop at any time and continue later; neither depends on the other being online in mixnet carriers.
- Puts and gets are idempotent by address; deletes by secret. A `TransferOffer` received twice is processed once by `transfer_id`.
- If the receiver finds a chunk expired, it reports the missing indices in a `TransferNeed` MLS message (`transfer_id`, stripe list); the sender re-puts from its outbox if it still holds the chunks.

### 11.12 Pre-send transcode and bit-exact sends

The sender chooses one mode per file:

| Mode | What is sent | When to use | Size |
| --- | --- | --- | --- |
| `nu_media` | The source transcoded on the sender's own device to nu-media at **native resolution and frame rate** (R1), `standard` or `visually_lossless` | Video and images where a visually equal copy is enough: review copies, sharing, personal media | Much smaller: this is where the time saving comes from (section 17) |
| `bit_exact` | The original file bytes untouched, `payload_hash = H(file)` | Masters, raw camera files (R2), documents, archives, anything that must match byte for byte | Same as the source plus padding and parity |

- Transcode runs only on the sender's devices (phone, Mac or own node); nothing is transcoded on operator servers.
- The UI shows both choices with their sizes and estimated times before sending, and never transcodes without the user choosing it. Files that aren't media are always `bit_exact`.
- A `nu_media` transcode of HDR keeps HDR (section 7); of high frame rate keeps the rate; of 360° keeps the projection and tiles.

### 11.13 Overheads

| Overhead | Factor on the bulk lane | Note |
| --- | --- | --- |
| Mix header | 65,536 / 73,736 = 0.889 | `PROTOCOL.md` 8.3 |
| Chunk framing | 61,420 / 65,536 = 0.937 | 11.3 |
| Parity (default) | 16 / 20 = 0.800 | 11.4 |
| Size padding | 0.89 to 1.00 | 11.5 |
| **Goodput / constant-stream rate** | **about 0.59 to 0.67** | Excluding the receiver's request uplink |

## 12. Error handling

### 12.1 Codes

| Code | Name | Where | Action |
| --- | --- | --- | --- |
| 0 | `ok` | wire | — |
| 1 | `not_found` | wire, get | Retry another replica; then `TransferNeed` |
| 2 | `bad_size` | wire, put | Sender bug; FAILED |
| 3 | `addr_mismatch` | wire, put; local, get | Put: sender bug. Get: drop the reply, try another replica, count the node |
| 4 | `token_invalid` | wire | Refresh tokens; retry |
| 5 | `rate_limited` | wire | Back off; retry later inside the stream |
| 6 | `expired` | wire | As `not_found` |
| 7 | `storage_full` | wire | Try the next replica in rendezvous order |
| 8 | `bad_delete_secret` | wire | Ignore (not the sender) |
| 32 | `unsupported_version` | local | Reject the object or manifest; tell the user to update |
| 33 | `unsupported_critical_extension` | local | Reject the containing header |
| 34 | `limits_exceeded` | local | Reject before allocation (4.2) |
| 35 | `manifest_invalid` | local | FAILED; warn that the sender's signature didn't verify |
| 36 | `insufficient_chunks` | local | FAILED after `TransferNeed` gets no answer |
| 37 | `hash_mismatch` | local | FAILED; never show or save the payload |
| 38 | `model_unavailable` | local | Drop the residual layer; continue |
| 39 | `decode_error` | local | Conceal (12.2) |

Wire codes are not sent to unauthenticated parties beyond what a node returns through the requester's own SURB. Mailbox nodes return errors only for `chunk_stat` and `chunk_get`; `chunk_put` and `chunk_delete` are fire-and-forget, confirmed by `chunk_stat`.

### 12.2 Media decoding errors

- A corrupt or missing base tile: conceal by repeating the co-located tile from the last good frame, mark the tile as concealed until its next intra refresh or random-access frame, and count it.
- A missing residual frame: continue with base plus enhancement until the next residual refresh.
- A `frame_seq` gap: as above; never drop later good frames to "catch up" (R8).
- A malformed header or a field outside limits: reject the whole object; decoders MUST NOT attempt partial recovery from headers.

## 13. Versioning and extensibility

- **Container.** `StreamHeader.version` is the major version; a decoder MUST reject versions it doesn't implement. Compatible additions use non-critical extensions (registry 16.4) and new enum values in registries 16.1–16.3; decoders ignore unknown non-critical extensions and reject unknown codec IDs per track (the track is skipped; if the base track is unknown, the object is rejected).
- **Tick and call framing** are versioned with the khensu protocol (`PROTOCOL.md` changelog); a change in `TickChunk` or `CallObjectPlain` layout is a protocol version change, negotiated in call setup or the content registry.
- **nu-transfer.** `TransferManifest.version` (1); unknown versions are rejected with `unsupported_version`. Labels carry the protocol's `"khensu v1 "` prefix, so a version 2 key schedule can't collide.
- **Models.** Image, residual and enhancement models are identified by hash, not version number. A new image or residual model is a new `model_id`; encoders send a model only after the app versions that carry it are spread widely enough (TBD), and keep the old one as the default until then.

## 14. Security considerations

- **Confidentiality and integrity.** Tick chunks and nu-transfer chunks are AEAD-sealed (AES-256-GCM) under keys delivered inside MLS with the ML-KEM-1024 suite, or by a standalone ML-KEM-1024 seal. Each key seals one plaintext. Content addresses are hashes of ciphertext, so nodes verify what they store and receivers verify what they fetch; the signed manifest binds every address, so a node can't substitute a chunk.
- **Authentication.** Manifests are signed with ML-DSA-87. In group mode the signature key is the sender's rotating MLS leaf key, preserving the deniability of `PROTOCOL.md` 4.1; standalone offers are not deniable.
- **Quantum adversaries.** ML-KEM-1024 and ML-DSA-87 at NIST category 5; AES-256 and SHA-512 keep large margins under Grover. A harvest-now-decrypt-later adversary recording constant streams gains nothing without the keys.
- **Hostile media.** Image and video parsers are a classic remote attack surface (malformed images in other messengers have been used for zero-click exploits). Decoders MUST: parse containers and extensions in memory-safe code (Rust in `khensu-core`) inside a sandboxed process with no network access; enforce section 4.2 limits before allocating; reject, not repair, malformed headers; pass only validated, size-checked NAL units to platform decoders; and decode nothing until the manifest signature (bulk) or MLS authentication (ticks) has verified.
- **Decompression bombs.** Frame area, tile count, layers, frames per segment and total payload are bounded; a receiver checks `padded_bytes` in the offer against free storage before fetching.
- **Models.** Networks ship inside the signed app and are pinned by `model_id`. Streams can't load code or weights. An unknown model ID disables only the optional layer.
- **Enhancement and evidence.** Enhancement and interpolation change displayed pixels. They are fidelity-trained (R6), never written to reference pictures, and the player labels interpolated frames and offers "show decoded only". Content that may serve as evidence should be sent `bit_exact` or `lossless`, and users should be told why.
- **Denial of service.** Storage abuse is bounded by anonymous token spends per put and by retention. Nodes verify addresses before storing. A malicious replica can drop chunks; erasure coding and three replicas absorb it, and `addr_mismatch` replies are attributed to the node for reputation.
- **Replay.** Puts, gets and offers are idempotent; mix packets have per-epoch replay protection (`PROTOCOL.md` 8.5).

## 15. Privacy considerations

- **No server sees plaintext, names or types.** File names, media types, real sizes and hashes are only inside the encrypted manifest.
- **Size.** Nodes see the padded chunk count: Padmé leaks about O(log log n) bits, and every transfer under about 245 KB looks the same. Tick media sizes are visible to nobody outside the conversation, because chunks replace cover and refs are per chunk.
- **Timing.** Mixnet carriers run at constant rates regardless of use, and the charging window opens whether or not anything is queued (10.3). Call-trunk transfer sessions are visible as sessions, like calls, which is why they are opt-in.
- **Linking.** Chunk addresses are unlinkable across transfers (random keys, no convergent encryption). Tick chunks are per recipient leaf. Bulk chunks are shared by recipients, so a replica can count how many fetches an address receives (roughly the number of recipient devices, plus retries); fetches arrive through SURBs and don't reveal who fetched.
- **Metadata stripping** removes capture metadata (section 8). It can't remove what is in the picture: faces, places, screens, and the sensor's noise fingerprint (PRNU), which forensic tools use to match a photo to a camera. Re-encoding at `standard` weakens PRNU but doesn't reliably remove it; users who need that should be told.
- **Viewport fetch** reveals nothing to nodes in mixnet carriers (all chunk requests look alike). In live Places over relays, tile subscriptions are visible to the viewer's own entry relay, which knows the viewer's IP; 10.2 asks viewers to keep subscription counts fixed.
- **Tier changes** in calls are visible to the local network and reveal network conditions, not content (`PROTOCOL.md` 7.1).
- **Model downloads** would leak; they don't happen at playback (5.2).

## 16. Registries

Policies: **Spec** = a stable published specification reviewed by the khensu protocol editors; **FCFS** = first come first served with a short description; **Private** = experiments, never sent to other people's devices. Each registry is kept in `PROTOCOL.md` section 15 once frozen. Proposed values for 3D, audio and provenance are in 16.10; they take the next unassigned values and change no existing entry.

### 16.1 nu-media codec IDs (`uint16`)

| Value | Name | Policy |
| --- | --- | --- |
| 0 | reserved | — |
| 1 | `hevc_main10` | Spec |
| 2 | `h264_high` | Spec |
| 3 | `nu_residual_v1` | Spec |
| 4 | `nu_image_v1` | Spec |
| 5 | `nu_lossless_v1` | Spec |
| 6 | `opus` | Spec |
| 7–49,151 | unassigned | Spec |
| 49,152–65,279 | unassigned | FCFS |
| 65,280–65,535 | private use | Private |

### 16.2 Track kinds and profiles (`uint8`, `uint16`)

Track kinds 1–8 as in 4.2, 9–239 Spec, 240–255 Private. Profiles 1–4 as in 4.1, 5–65,279 Spec, 65,280–65,535 Private.

### 16.3 Frame types (`uint8`)

1–7 as in 4.5; 8–239 Spec; 240–255 Private.

### 16.4 Frame header extensions (`uint16`)

| Value | Name | May be critical | Where | Section |
| --- | --- | --- | --- | --- |
| 0 | reserved | — | — | — |
| 1 | `mastering_display` | No | track | 7.2 |
| 2 | `content_light_level` | No | track | 7.2 |
| 3 | `tone_map_curve` | No | frame, call data track | 7.2 |
| 4 | `enhancement_hint` | No | track, frame | 5.2 |
| 5 | `residual_model` | Yes | track | 5.3 |
| 6 | `sample_hash` | No | frame | 9.2 |
| 7 | `roi_map` | No | frame | regions with extra bits (faces, text) |
| 8 | `live_photo_pair` | No | stream | 6.3 |
| 9 | `spatial_layout` | No | stream | stereo baseline and eye order |
| 10 | `segment_duration_hint` | No | stream | 4.3 |
| 11–32,767 | unassigned | | | Spec |
| 32,768–61,439 | unassigned | | | FCFS |
| 61,440–65,535 | private use | | | Private |

### 16.5 Projections (`uint8`)

0–3 as in 4.2; 4–239 Spec; 240–255 Private.

### 16.6 Quality modes and rate control (`uint8`)

As in 4.2; new values Spec.

### 16.7 Transfer modes (`uint8`)

1 `bit_exact`, 2 `nu_media`; 3–239 Spec; 240–255 Private.

### 16.8 nu-transfer error codes (`uint16`)

0–8 wire and 32–39 local as in 12.1; 9–31 Spec (wire); 40–1,023 Spec (local); 1,024–65,535 FCFS.

### 16.9 Additions to khensu registries

| Registry (`PROTOCOL.md` 15) | Value | Name |
| --- | --- | --- |
| Content types | 18 | `media_offer` (`TickMediaOffer`, 10.1) |
| Content types | 19 | `transfer_offer` (`TransferOffer`, 11.7) |
| Content types | 20 | `transfer_done` (`transfer_id`) |
| Content types | 21 | `transfer_need` (`transfer_id`, missing stripes) |
| Mailbox ops (6.2) | 7–10 | `chunk_put`, `chunk_get`, `chunk_stat`, `chunk_delete` |
| Signature labels | — | `"nt manifest"`, `"chunk stat"` |
| KDF and hash labels | — | `"nm tick ref"`, `"nm tick chunk"`, `"nm residual model"`, `"nm image model"`, `"nt root"`, `"nt manifest"`, `"nt chunk"`, `"nt delete"`, `"nt delete check"`, `"nt chunk addr"`, `"nt offer"` |

Media types for use outside khensu (`application/nu-media`, `video/nu-media`) are requested in `proposals/draft-staffer-nu-media-00.md`.

### 16.10 Proposed entries for 3D, audio and provenance

Status: proposed, 11 October 2026; design only. Each entry is specified in the document named and becomes **Spec** when that document is frozen.

| Registry | Value | Name | Specified in |
| --- | --- | --- | --- |
| Profile (4.1) | 5 | `scene` | `nu-3d.md` 3 |
| Track kind (4.2) | 9 | `scene` | `nu-3d.md` 3.1 |
| Track kind | 10 | `mesh` | `nu-3d.md` 3.3 |
| Track kind | 11 | `texture` | `nu-3d.md` 3.5 |
| Track kind | 12 | `animation` | `nu-3d.md` 3.7 |
| Track kind | 13 | `splat` | `nu-3d.md` 3.8 |
| Codec ID (16.1) | 7 | `nu_scene_v1` | `nu-3d.md` 3.2 |
| Codec ID | 8 | `nu_mesh_v1` | `nu-3d.md` 3.3 |
| Codec ID | 9 | `nu_anim_v1` | `nu-3d.md` 3.7 |
| Codec ID | 10 | `nu_splat_v1` | `nu-3d.md` 3.8 |
| Codec ID | 11 | `ktx2` (KTX 2.0 with Basis Universal or ASTC) | `nu-3d.md` 3.5 |
| Codec ID | 12 | `nu_speech_v1` | `nu-audio.md` 4 |
| Codec ID | 13 | `flac` (RFC 9639) | `nu-audio.md` 6 |
| Codec ID | 14 | `nu_provenance_v1` (provenance data track) | `nu-provenance.md` 4 |
| Frame type (4.5) | 8 | `scene_layer` | `nu-3d.md` 3.1 |
| Frame type | 9 | `provenance` | `nu-provenance.md` 4 |
| Extension (16.4) | 11 | `provenance_key` (stream, never critical) | `nu-provenance.md` 8.1 |
| Extension | 12 | `edit_manifest` (stream) | `nu-provenance.md` 6.1 |
| Extension | 13 | `perceptual_fingerprint` (stream; only when the user publishes it) | `nu-provenance.md` 7 |
| Extension | 14 | `fallback_binding` (stream; wrapped USDZ and GLB) | `nu-3d.md` 7.3 |
| Extension | 15 | `scene_bounds` (track; bounding box, units and axis conversion) | `nu-3d.md` 2 (D8) |
| Extension | 16 | `loudness` (track; ITU-R BS.1770 integrated loudness, range, true peak) | `nu-audio.md` 5 |
| Extension | 17 | `ambisonics_layout` (track; order, normalisation, channel order, head-locked pair) | `nu-audio.md` 7.1 |
| nu-transfer manifest extension (11.6) | — | `provenance` (piece-tree root and signer) | `nu-provenance.md` 4.1 |
| Transfer mode (16.7) | 3 | `sample_exact` (container rewritten without metadata, samples bit-exact) | `nu-audio.md` 6 |
| Signature labels | — | `"np trailer"`, `"np checkpoint"` | `nu-provenance.md` 8 |
| KDF and hash labels | — | `"np leaf"`, `"np chunk"`, `"np node"`, `"np checkpoint"`, `"np capture key"`, `"na speech model"` | `nu-provenance.md` 3.2, `nu-audio.md` 4 |

None of the new extensions may be marked critical by version 1 senders. Media type `model/nu-media` for `profile = scene` and the file extension `.nu` are proposed in `nu-3d.md` 8 for the next revision of the IETF draft.

## 17. Comparison with Dropbox and IBM Aspera

What each one is, honestly:

| | Dropbox | IBM Aspera (FASP) | khensu nu-transfer |
| --- | --- | --- | --- |
| Model | Upload to Dropbox's servers; recipients download from them | Point to point (or via an Aspera server) over FASP, a UDP protocol with its own rate control built to fill the link | Chunks stored on mailbox nodes run by independent operators, reached through a 5-hop mixnet inside constant streams; or a two-relay session |
| Who can read the file | Dropbox holds the keys by default (encrypted at rest and in transit, but not end to end); end-to-end encrypted folders exist on some business plans (to check) | Encrypted in transit; client-side encryption at rest is an option, not the default; the server operator sees file names, sizes and both endpoints | Only sender and recipients; no node sees plaintext, names or real sizes |
| Who knows who sent what to whom | Dropbox | The Aspera server operator and the network | No single party (mixnet carriers); the two relays see endpoints in trunk sessions |
| Speed per byte | Limited by the upload and download links and Dropbox's servers | Near line rate on long, lossy links, where TCP struggles; this is Aspera's strength | **Slower per byte than a direct link**: bounded by the constant-stream rate, with goodput about 0.59–0.67 of it (11.13), plus mix delays (latency, not throughput) |
| Bytes moved | The file | The file | The file (`bit_exact`), or a nu-media transcode (`nu_media`) |

**Where khensu is faster, and where it isn't.** khensu saves time only when nu-media makes the file smaller. A ProRes 422 HQ 4K master is about 660 Mbit/s (estimate; Apple's ProRes white paper lists higher rates at 29.97 fps, to check per frame rate). nu-media's 4K HDR design target is 9.6 Mbit/s at `standard` quality, about 69 times smaller; `visually_lossless` is estimated at 2–3 times that. The transport is never faster than Aspera.

Worked example, a 10-minute 4K ProRes 422 HQ master (about 396 Gbit, 49.5 GB). Every row is an estimate. The constant-stream rate of 20 Mbit/s is an **assumed** figure for illustration, not a protocol value (the real rates are consensus parameters not yet set).

| Method | Bytes sent | Link or stream | Estimated time |
| --- | --- | --- | --- |
| Aspera, bit-exact | 396 Gbit | 1 Gbit/s at about 90% use | about 7.3 min |
| Aspera, bit-exact | 396 Gbit | 100 Mbit/s at about 90% use | about 73 min |
| Dropbox, bit-exact | 396 Gbit | 100 Mbit/s up, then 100 Mbit/s down | about 66–75 min upload, then the download (can overlap partly) |
| khensu `bit_exact` | 396 Gbit + parity and padding | 20 Mbit/s constant stream (assumed), goodput about 13 Mbit/s | **about 8.3 h** |
| khensu `nu_media`, `standard` (9.6 Mbit/s design target) | 5.76 Gbit | 20 Mbit/s constant stream (assumed) | about 7.2 min, plus transcode (about 6 min on an iPhone Air if 4K HEVC encode runs at the measured ~48 fps; can overlap with sending) |
| khensu `nu_media`, `visually_lossless` (estimate 24 Mbit/s) | 14.4 Gbit | same | about 18 min, plus transcode |
| Aspera sending the same nu-media file | 5.76 Gbit | 1 Gbit/s | about 6 s |

What this means:

- **Bit-exact sends are not faster than Aspera** and are much slower than a direct gigabit link. Over the mixnet, khensu pays for privacy with throughput: header overhead, parity, padding and a rate fixed in advance.
- **The transcode, not the transport, is the win.** Anyone can transcode before using Aspera or Dropbox, and would then be faster still. khensu's difference is that the smaller file then moves with no server seeing it, its name or who received it, and the transcode is built in at native resolution.
- **A transcode is not the master.** `nu_media` is for review, approvals, dailies and sharing; a finishing house that needs the ProRes bytes needs `bit_exact`, and should expect hours, not minutes, unless both sides use a fast own-node stream or a trunk session.
- **Free and private** are khensu's other differences: no per-gigabyte charge and no account tied to an identity. Aspera is a paid enterprise product; Dropbox's free tier has a small storage cap (figures to check before quoting).

## 18. Open issues found while writing

1. `PROTOCOL.md` 6.4 pads attachment chunks to 64 KiB and seals them, which with the tag and request framing exceeds the 65,536-byte bulk payload. This document uses 61,440-byte sealed chunks; 6.4 should be replaced by section 11 when frozen.
2. `PROTOCOL.md` 6.2 puts a SURB (8,248 bytes) inside `store` and `fetch`, but a small-lane payload is 2,048 bytes. Small-lane receipts and fetch replies need a smaller return-path construction or a different design; tick media inherits whatever is chosen.
3. Whether `Fragment` headers (`msg_ref`, `index`, `count`) are visible to mailbox nodes isn't stated. If they are, they leak message sizes to mailbox nodes; tick chunks avoid this with per-chunk refs, and fragments could do the same.
4. The call tier names in `PROTOCOL.md` 7.1 ("about 500 kbit/s, 1.5 Mbit/s, 3.8 Mbit/s") are close to the on-the-wire rates; the encoder can only use about 0.91 of them after SFrame and object headers (10.2). `nu-media.md` 4.2 tables use the nominal rates.
5. R1 (never downscale) and the reduced-size call base at tier L conflict in spirit; this document keeps the exception for calls only, signalled, and asks for measurements to decide whether to drop it.
6. The constant-stream rates for the own node, the charging window and trunk transfer sessions aren't set anywhere; section 17 uses an assumed 20 Mbit/s.
7. The SFrame header length varies with KID and counter; 10.2 absorbs it in padding. Check whether RFC 9605 allows fixed-length encoding instead.
8. Media types and registries for use outside khensu go through the IETF draft; khensu's own registries stay in `PROTOCOL.md` 15.
9. `TickMediaOffer` (10.1) doesn't commit to the content. Every recipient learns `k_obj` and can derive other recipients' chunk keys and references, so a malicious group member could store substitute chunks in another member's mailbox. `nu-provenance.md` 5.1 proposes adding `object_root` and `layer_roots` to the offer.
10. The fixed QUIC packet size in 10.2 (about 1,350 bytes) would make audio-only calls cost about 540 kbit/s on the wire for a 64 kbit/s audio track; audio-only sessions need their own packet size (`nu-audio.md` 3.1).

## Changelog

- 0.1 (11 Oct 2026): first draft.
- 0.1, addendum (11 Oct 2026): registry entries proposed for 3D, audio and provenance (16.10); open issues 9 and 10.
