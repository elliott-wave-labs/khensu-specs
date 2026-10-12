---
title: "nu-media: Constant-Bitrate Media with Receiver-Side Neural Enhancement and Private Bulk Transfer"
abbrev: "nu-media"
docname: draft-staffer-nu-media-00
category: std
submissiontype: IETF
ipr: trust200902
area: WIT
keyword:
  - media format
  - constant bitrate
  - super resolution
  - traffic analysis
  - file transfer
  - post-quantum
  - MOQ
  - SFrame
v: 3
stand_alone: yes
pi: [toc, sortrefs, symrefs]

author:
  -
    fullname: Justin Elliott Staffer
    organization: Elliott Wave LLC
    email: hello@elliottwave.studio

normative:
  RFC8446:
  RFC9000:
  RFC9420:
  RFC9605:
  RFC5869:
  RFC6838:
  RFC6716:
  RFC8126:
  I-D.ietf-moq-transport:
  HEVC:
    title: "High efficiency video coding"
    author:
      - org: ITU-T
    date: 2024
    seriesinfo:
      ITU-T Recommendation: H.265
  H273:
    title: "Coding-independent code points for video signal type identification"
    author:
      - org: ITU-T
    date: 2024
    seriesinfo:
      ITU-T Recommendation: H.273
  BT2020:
    title: "Parameter values for ultra-high definition television systems for production and international programme exchange"
    author:
      - org: ITU-R
    date: 2015
    seriesinfo:
      ITU-R Recommendation: BT.2020-2
  BT2100:
    title: "Image parameter values for high dynamic range television for use in production and international programme exchange"
    author:
      - org: ITU-R
    date: 2018
    seriesinfo:
      ITU-R Recommendation: BT.2100-2
  ST2084:
    title: "High Dynamic Range Electro-Optical Transfer Function of Mastering Reference Displays"
    author:
      - org: SMPTE
    date: 2014
    seriesinfo:
      SMPTE: ST 2084:2014
  ST2086:
    title: "Mastering Display Color Volume Metadata Supporting High Luminance and Wide Color Gamut Images"
    author:
      - org: SMPTE
    date: 2018
    seriesinfo:
      SMPTE: ST 2086:2018
  FIPS180-4:
    title: "Secure Hash Standard (SHS)"
    author:
      - org: NIST
    date: 2015
    seriesinfo:
      FIPS: PUB 180-4
  FIPS203:
    title: "Module-Lattice-Based Key-Encapsulation Mechanism Standard"
    author:
      - org: NIST
    date: 2024
    seriesinfo:
      FIPS: "203"
  FIPS204:
    title: "Module-Lattice-Based Digital Signature Standard"
    author:
      - org: NIST
    date: 2024
    seriesinfo:
      FIPS: "204"
  SP800-38D:
    title: "Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC"
    author:
      - org: NIST
    date: 2007
    seriesinfo:
      NIST: SP 800-38D

informative:
  RFC3550:
  RFC4855:
  RFC7798:
  RFC8216:
  RFC9180:
  RFC9297:
  I-D.ietf-webtrans-http3:
  ISO14496-15:
    title: "Information technology - Coding of audio-visual objects - Part 15: Carriage of network abstraction layer (NAL) unit structured video in the ISO base media file format"
    author:
      - org: ISO/IEC
    date: 2022
    seriesinfo:
      ISO/IEC: 14496-15
  LCEVC:
    title: "Information technology - Low Complexity Enhancement Video Coding"
    author:
      - org: ISO/IEC
    date: 2021
    seriesinfo:
      ISO/IEC: 23094-2
  PADME:
    title: "Reducing Metadata Leakage from Encrypted Files and Communication with PURBs"
    author:
      - name: Kirill Nikitin
      - name: Ludovic Barman
      - name: Wouter Lueks
      - name: Matthew Underwood
      - name: Jean-Pierre Hubaux
      - name: Bryan Ford
    date: 2019
    seriesinfo:
      Proceedings on Privacy Enhancing Technologies: "2019(4)"
  LOOPIX:
    title: "The Loopix Anonymity System"
    author:
      - name: Ania M. Piotrowska
      - name: Jamie Hayes
      - name: Tariq Elahi
      - name: Sebastian Meiser
      - name: George Danezis
    date: 2017
    seriesinfo:
      USENIX Security Symposium: "2017"
  VBRLEAK:
    title: "Spot Me if You Can: Uncovering Spoken Phrases in Encrypted VoIP Conversations"
    author:
      - name: Charles V. Wright
      - name: Lucas Ballard
      - name: Scott E. Coull
      - name: Fabian Monrose
      - name: Gerald M. Masson
    date: 2008
    seriesinfo:
      IEEE Symposium on Security and Privacy: "2008"
  HIFIC:
    title: "High-Fidelity Generative Image Compression"
    author:
      - name: Fabian Mentzer
      - name: George Toderici
      - name: Michael Tschannen
      - name: Eirikur Agustsson
    date: 2020
    seriesinfo:
      NeurIPS: "2020"
  ELIC:
    title: "ELIC: Efficient Learned Image Compression with Unevenly Grouped Space-Channel Contextual Adaptive Coding"
    author:
      - name: Dailan He
      - name: Ziming Yang
      - name: Weikun Peng
      - name: Rui Ma
      - name: Hongwei Qin
      - name: Yan Wang
    date: 2022
    seriesinfo:
      CVPR: "2022"
  DCVC:
    title: "Deep Contextual Video Compression"
    author:
      - name: Jiahao Li
      - name: Bin Li
      - name: Yan Lu
    date: 2021
    seriesinfo:
      NeurIPS: "2021"
  NAS:
    title: "Neural Adaptive Content-aware Internet Video Delivery"
    author:
      - name: Hyunho Yeo
      - name: Youngmok Jung
      - name: Jaehong Kim
      - name: Jinwoo Shin
      - name: Dongsu Han
    date: 2018
    seriesinfo:
      USENIX OSDI: "2018"
  ASPERA:
    title: "IBM Aspera FASP high-speed transport"
    author:
      - org: IBM
    date: false
    target: https://www.ibm.com/products/aspera

--- abstract

This document specifies nu-media, a media container and bitstream for images and video, and nu-transfer, a protocol for private bulk transfer of files. nu-media carries a constant-bitrate base layer in HEVC Main 10, an optional bit-exact learned residual layer inside the prediction loop, and receiver-side neural enhancement (super resolution, artefact removal and frame interpolation) outside the loop that costs no bits and cannot drift. It uses 1 MHz timestamps with variable frame rate up to 2,000 frames per second, independent tiles for frames up to 43,008 x 21,504 pixels, BT.2020 colour with PQ and HLG, and strips capture metadata. Senders never downscale. nu-transfer moves content-addressed, fixed-size, end-to-end sealed chunks with erasure coding and receiver pull, using ML-KEM-1024, AES-256-GCM and ML-DSA-87. The document gives mappings onto constant-rate transports, including Media over QUIC, and registers media types.

--- note_Discussion_Venues

This is an individual submission. The author seeks a home for it in the AVTCORE working group (media format and RTP considerations) or the MOQ working group (constant-rate mapping and transfer over Media over QUIC), and will bring it to the relevant area dispatch first. The intended status is Standards Track.

--- note_Intellectual_Property

The author has filed or intends to file patent applications covering parts of this document; an IPR disclosure will be made under BCP 79 (RFC 8179).

--- middle

# Introduction

Encrypted real-time media leaks content through its sizes and timing: variable-bitrate encoders produce packet sizes that correlate with speech and motion {{VBRLEAK}}. Constant-rate padded transports such as mixnets {{LOOPIX}} remove that leak, but give each sender a fixed and often small number of bits. At the same time, receiving devices now carry neural accelerators that can upscale, clean and interpolate video in real time, and published learned image codecs ({{HIFIC}}, {{ELIC}}) and video codecs ({{DCVC}}) show large gains over conventional coding. Receiver-side super resolution for streaming has been studied before, for example with per-video models sent alongside the stream {{NAS}}.

nu-media is designed for that setting. It fixes the bits on the wire and moves the improvement to the receiver:

* A **base layer** in HEVC {{HEVC}} Main 10 at constant bitrate, which every current hardware encoder and decoder supports, and which is always decodable alone.
* An **enhancement layer outside the prediction loop**: super resolution, artefact removal and frame interpolation run on the receiver. It has no coded bits, is not bit-exact, never enters a reference picture and so cannot drift. Each receiver chooses what its hardware can run.
* An optional **residual layer inside the loop**: a learned residual decoded with integer-only arithmetic, so it is bit-exact on every conforming decoder.
* **Learned progressive images** whose layers are sized to fit fixed transport slots, so a preview arrives in the first slot and each later slot refines the whole picture.

nu-transfer moves stored media and files over constant-rate carriers. Chunks are content-addressed, padded to one size, sealed end to end, erasure coded and pulled by the receiver by hash. A sender can transcode video to nu-media at native resolution before sending, which is where any time saving over conventional transfer comes from, or send the original bytes bit-exact.

The design rules that distinguish nu-media from existing scalable or enhancement codecs such as SHVC in {{HEVC}} and {{LCEVC}} are: the enhancement layer has no bitstream at all; senders never downscale stored media; capture metadata has no place in the format; and every layer is sized for constant-rate transport.

# Conventions and Definitions

{::boilerplate bcp14-tagged}

Structures use the presentation language of {{Section 3 of RFC8446}}. `opaque x<V>` denotes a vector with a variable-length integer length prefix as in {{Section 16 of RFC9000}}; `varint` is such an integer. Integers are big-endian.

Base layer:
: The HEVC Main 10 (or fallback H.264) layer, decodable alone.

Enhancement:
: Receiver-side processing of decoded pictures for display only, with no coded data.

Residual layer:
: A coded, integer-decoded learned layer that predicts from its own previous output.

Native resolution:
: The resolution, frame rate and bit depth of the source as captured.

Constant-rate carrier:
: A transport that sends fixed-size units at a fixed schedule whether or not there is data, filling idle slots with padding indistinguishable from data.

Chunk store:
: A set of nodes that store and return sealed chunks by content address.

Cryptographic notation:

* `H(x)` is SHA-512 and `H256(x)` is SHA-512/256 {{FIPS180-4}}.
* `KDF(k, info, L)` is `HKDF-Expand(HKDF-Extract("", k), info, L)` with SHA-512 {{RFC5869}}.
* `AEAD(k, n, p, a)` is AES-256-GCM {{SP800-38D}} with key `k`, nonce `n`, plaintext `p`, associated data `a`.
* `KEM` is ML-KEM-1024 {{FIPS203}}; `SIG` is ML-DSA-87 {{FIPS204}} in pure mode with an empty context string.
* `Label(x)` is the ASCII string "nu-media v1 " followed by `x`.

# Design Rules {#rules}

R1 (native resolution):
: A sender MUST NOT scale stored media or a transfer payload down from its native resolution, frame rate or bit depth. Lower resolutions are obtained by the receiver fetching fewer tiles or an additional overview track. The only exception is the live base layer of a constant-rate call ({{rtp}}, {{moq}}), which MAY be coded at a reduced size that is signalled in the track descriptor.

R2 (no raw):
: The format has no uncompressed sample format and does not carry camera sensor raw data. Highest-quality use is native resolution in the `visually_lossless` mode, or the `lossless` mode. Raw camera files are sent as opaque files by a bit-exact transfer ({{transfer}}).

R3 (constant-bitrate base):
: The base layer is coded at constant bitrate.

R4 (enhancement outside the loop):
: Enhanced pixels MUST NOT be written into any reference picture.

R5 (residual inside the loop):
: Residual decoding MUST use only the integer arithmetic specified in {{residual}}.

R6 (fidelity):
: Enhancement, residual and image networks MUST NOT use generative adversarial or diffusion synthesis.

R7 (metadata):
: Capture metadata MUST NOT be carried ({{metadata}}).

R8 (no frame loss):
: A decoder MUST present every coded frame it decodes; interpolated frames are only inserted between coded frames.

# Media Format {#media-format}

## Stream Header

A nu-media object is a stream header followed by segments.

~~~
enum { call(1), stored(2), image(3), lossless(4), (65535) } Profile;

struct {
  opaque  magic[4];             /* 0x6E 0x75 0x4D 0x65, "nuMe" */
  uint16  version;              /* 1 */
  Profile profile;
  uint32  flags;                /* bit0 live, bit1 tiled,
                                   bit2 has_overview */
  TrackDescriptor tracks<V>;    /* 1 to 16 */
  Extension extensions<V>;
} StreamHeader;
~~~

A decoder MUST reject an object whose magic differs or whose version it does not implement. Unknown flag bits MUST be sent as zero and ignored on receipt.

## Track Descriptor

~~~
enum { video(1), image(2), audio(3), alpha(4), depth(5),
       second_eye(6), overview(7), data(8), (255) } TrackKind;

enum { hevc_main10(1), h264_high(2), nu_residual_v1(3),
       nu_image_v1(4), nu_lossless_v1(5), opus(6), (65535) } CodecId;

enum { rectilinear(0), equirectangular(1), cubemap(2),
       fisheye_pair(3), (255) } Projection;

enum { cbr(1), lossless(2), (255) } RateControl;
enum { standard(1), visually_lossless(2), lossless(3), (255) }
     QualityMode;

struct {
  uint8       track_id;
  TrackKind   kind;
  CodecId     codec;
  uint8       depends_on;       /* 0xFF if none */
  uint32      native_width;
  uint32      native_height;
  uint32      coded_width;      /* = native except R1 exception */
  uint32      coded_height;
  TileGrid    grid;
  ColourDescription colour;
  Projection  projection;
  RateControl rate_control;
  QualityMode quality;
  uint32      nominal_bitrate;  /* bit/s; 0 for images */
  uint8       reorder;          /* 1 if coded out of order */
  opaque      codec_config<V>;
  Extension   extensions<V>;
} TrackDescriptor;
~~~

Widths MUST be 16 to 43,008 and heights 16 to 21,504. A decoder MUST reject a track exceeding these limits before allocating frame memory. Audio tracks use Opus {{RFC6716}}.

## Tiling {#tiling}

~~~
struct {
  uint16 tile_width;            /* 0 = untiled */
  uint16 tile_height;           /* 0 = untiled */
  uint16 columns;
  uint16 rows;
} TileGrid;
~~~

A video track MAY be untiled only if `coded_width * coded_height` is at most 8,912,896 and each dimension is at most 8,444 (the HEVC level 5.1 luma limits). Otherwise it MUST be tiled. Tile width and height MUST each be a multiple of 128 from 512 to 2,048. The grid is uniform from the top-left; the last column and row carry the remainder, which MUST be at least 64 pixels. Tiles are numbered in raster order.

Each tile is an independent elementary stream with its own parameter sets and reference pictures and no prediction across tile edges, so a decoder can decode any subset of tiles. A sender MAY add an `overview` track: the whole frame at reduced size, as an additional representation that does not replace the native track.

## Frame Header

~~~
enum { base_intra(1), base_inter(2), residual(3), image_layer(4),
       lossless_frame(5), audio_frame(6), data_frame(7), (255) }
     FrameType;

struct { uint16 tile_index; uint32 length; } TileEntry;

struct {
  FrameType type;
  uint8     track_id;
  uint16    flags;              /* bit0 random_access,
                                   bit1 droppable,
                                   bit2 discontinuity,
                                   bit3 end_of_stream */
  uint64    pts_us;             /* 1 MHz clock */
  int32     dts_offset_us;
  uint32    duration_us;
  uint32    frame_seq;
  TileEntry tiles<V>;
  Extension extensions<V>;
} FrameHeader;
~~~

Tile payloads follow the header in `tiles` order. For HEVC and H.264 a tile payload is a sequence of NAL units, each with a 4-byte length prefix, as in {{ISO14496-15}}. Random-access frames carry parameter sets in-band.

## Timestamps and Frame Rate

`pts_us` counts microseconds from the start of the stream; the first frame of each track has `pts_us` 0, and no wall-clock time is carried. There is no frame rate field. Within a track `pts_us` MUST strictly increase in presentation order and consecutive coded frames MUST be at least 500 microseconds apart, which bounds the coded rate at 2,000 frames per second. The rate MAY change at any frame.

## Extensions

~~~
struct {
  uint16 ext_type;              /* IANA registry, see IANA
                                   Considerations */
  uint8  critical;
  opaque data<V>;
} Extension;
~~~

A decoder that does not recognise a critical extension MUST reject the header that contains it, and MUST skip an unrecognised non-critical extension. Each type appears at most once per header.

## Layers

### Base Layer

The base layer is HEVC Main 10 {{HEVC}}, 4:2:0, 10-bit, at constant bitrate with a conformant hypothetical reference decoder. Devices without a Main 10 encoder MAY use H.264 High profile at 8 bits for SDR. In the `call` profile the encoder MUST NOT reorder frames and SHOULD use periodic intra refresh instead of intra pictures, so that coded sizes have no periodic peaks. A conforming decoder MUST be able to present the base layer alone.

### Enhancement Outside the Loop

Enhancement has no coded data. A sender MAY include an `enhancement_hint` extension:

~~~
struct {
  uint8  allowed;        /* bit0 super resolution, bit1 artefact
                            removal, bit2 frame interpolation,
                            bit3 chroma restoration,
                            bit4 tile seam smoothing */
  uint16 max_display_fps;
} EnhancementHint;
~~~

A receiver MUST NOT apply an operation whose bit is clear. It MUST NOT write enhanced pixels into a reference picture. Interpolated frames MUST NOT be counted, stored or exported as coded frames, and a player that captures or exports a frame MUST indicate whether it was interpolated. A receiver MUST NOT fetch an enhancement model over the network in response to a stream.

### Residual Layer {#residual}

~~~
struct {
  opaque model_id[32];   /* H256(Label("residual model") ||
                            descriptor || weights) */
  uint16 refresh_period; /* 1 to 600 frames */
  uint8  base_scale;     /* 1 or 2 */
} ResidualConfig;
~~~

The residual reconstruction is `R_t = clip(U(B_t) + D(r_t, R_(t-1)))` where `B_t` is the decoded base, `U` an integer upsampler, `r_t` the entropy-decoded residual symbols and `D` the synthesis network. `D` and the entropy model MUST use INT8 weights, INT32 accumulation, requantisation by arithmetic right shift with round-half-up, and saturation to INT16 activations, and MUST NOT use floating point. At a residual refresh point, `R_(t-1)` is replaced by `U(B_t)`. The base layer never references the residual layer; a decoder that lacks the model or cannot decode the residual in time MUST drop the residual track and continue with the base.

## Images

Images use codec `nu_image_v1`, a learned transform codec. Analysis and synthesis transforms MAY run in 16-bit floating point. The hyperprior and context models that produce the entropy coder's probability tables MUST use the integer rules of {{residual}}, and the entropy coder is a range coder with 16-bit integer cumulative distributions, so every decoder recovers identical symbols. Decoded samples MUST be within 2 code values (12-bit) of the reference decoder.

Images are 12-bit, 4:4:4, in BT.2020 primaries. Layer 0 is a preview of the whole picture and each later layer refines the whole picture. An image track carries one `image_layer` frame per layer. When a transport has fixed slots, the encoder SHOULD size layer 0 to one slot payload and pad each later layer to end on a slot boundary.

## Colour and HDR

~~~
struct {
  uint8 colour_primaries;          /* H.273; 9 required */
  uint8 transfer_characteristics;  /* H.273; 16 PQ, 18 HLG,
                                      13 sRGB, 1 BT.709 */
  uint8 matrix_coefficients;       /* H.273; 9 video, 0 or 14
                                      images */
  uint8 full_range;
  uint8 bit_depth;                 /* 10 video, 12 images */
  uint8 chroma_format;             /* 1 = 4:2:0, 3 = 4:4:4 */
} ColourDescription;
~~~

Code points are those of {{H273}}. Primaries are always BT.2020 {{BT2020}}; HDR uses PQ {{ST2084}} or HLG {{BT2100}}. Mastering display metadata {{ST2086}}, content light level and per-scene tone-mapping curves are carried in extensions.

## Metadata Stripping {#metadata}

An encoder MUST NOT carry, in any field, extension, supplemental enhancement information message or user data: EXIF, XMP, IPTC or maker notes; location, altitude, heading or motion data; device make, model, serial number or software; capture or modification time; original file names; embedded thumbnails or face regions. Orientation MUST be applied to the pixels. HEVC tile streams MUST contain only these SEI payloads: mastering display colour volume, content light level, alternative transfer characteristics, decoded picture hash and recovery point.

## Quality Modes

`standard` is a constant-bitrate ladder chosen per pixel rate. `visually_lossless` is native resolution at a bitrate where the decoded result is not distinguishable from the source in a flicker test at native size. `lossless` (codec `nu_lossless_v1`) MUST decode to the exact source samples, and each lossless frame MUST carry a `sample_hash` extension containing `H` of the decoded samples, which the decoder MUST check.

# Constant-Rate Operation

For live media over a constant-rate carrier, the sender:

1. Chooses a tier: a fixed object size and a fixed object rate.
2. Runs the base encoder at no more than 0.95 of the tier's payload capacity after encryption and object headers.
3. Splits each coded frame into fixed-size objects. A frame that does not fill its share is padded; an empty slot carries a padding object.
4. Encrypts every object, padding included, so that padding is inside the ciphertext, and computes the padding length after encryption overhead so every ciphertext has the same length.
5. Sends objects at exact intervals with no bursts, and changes tier only rarely, between adjacent tiers, at a random-access point.

The object plaintext is:

~~~
enum { padding(0), media(1), (255) } CallObjectKind;

struct {
  CallObjectKind kind;
  uint8  flags;          /* bit0 frame_start, bit1 frame_end,
                            bit2 random_access */
  uint16 data_len;
  uint32 frame_seq;
  uint64 pts_us;
  uint16 tile_index;
  opaque data[data_len];
  opaque zero_pad[...];
} CallObjectPlain;
~~~

The sender SHOULD code at most 60 frames per second in this mode; receivers MAY interpolate higher display rates (R8 still applies to coded frames).

## Mapping to Media over QUIC {#moq}

When carried over MOQT {{I-D.ietf-moq-transport}}, typically inside WebTransport {{I-D.ietf-webtrans-http3}} (which uses HTTP Datagrams and the Capsule Protocol {{RFC9297}}):

* Each media track (audio, base video per tile, and a data track for frame manifests and tone-map updates) is an MOQT track with constant-rate objects.
* A group is one intra-refresh period; an object is one encrypted `CallObjectPlain`.
* Objects are protected with SFrame {{RFC9605}}. Keys MAY be derived from an MLS {{RFC9420}} exporter.
* The sender MUST pad QUIC packets carrying objects to a fixed size per session, so that variable-length MOQT and QUIC framing does not show through packet sizes.
* Viewers of tiled sources subscribe to tile tracks by viewport. To limit what a relay learns, a viewer SHOULD hold a fixed number of tile subscriptions and move them rather than add and remove them.
* For group sessions, each sender SHOULD publish a signed manifest over the authentication tags of all its objects in each interval, padding included, so relays cannot drop objects selectively without detection.

## RTP Considerations {#rtp}

This document does not define an RTP payload format. Implementers mapping nu-media to RTP {{RFC3550}} should note:

* The base layer can be carried with the HEVC payload format {{RFC7798}}, but constant-rate operation requires fixed-size packets at a fixed rate with padding inside the end-to-end encryption. The RTP padding bit and the marker bit are visible to the network and reveal padding and frame boundaries; a constant-rate mapping needs both to be constant.
* RTP timestamps of media frames reveal frame timing. A constant-rate mapping should timestamp packets by transmission slot and carry `pts_us` inside the encrypted payload.
* Enhancement has no data, so it needs no payload format. A residual layer would need its own payload format or a multiplexed one.

A payload format is a candidate for future work in AVTCORE.

# Transfer Protocol {#transfer}

## Overview

nu-transfer moves a payload (a file, or a nu-media object made from it) as fixed-size sealed chunks in a chunk store. The sender stores chunks; the receiver, after receiving an offer, pulls them by address in any order. No node learns plaintext, file names, types or exact sizes.

## Keys

~~~
transfer_secret = random(32)
transfer_id     = random(16)
k_root      = KDF(transfer_secret, Label("root"), 32)
k_man_j     = KDF(transfer_secret, Label("manifest") || uint32(j),
                  32)
k_chunk_i   = KDF(transfer_secret, Label("chunk") || uint32(i), 32)
del_i       = KDF(transfer_secret, Label("delete") || uint8(role)
                                   || uint32(i), 32)
sealed      = AEAD(k, zero_nonce, ChunkPlain,
                   transfer_id || uint8(role) || uint32(i))
chunk_addr  = H256(Label("chunk addr") || sealed)
~~~

Each key encrypts exactly one plaintext, so a zero nonce is safe. Chunk addresses depend on a random per-transfer key; senders MUST NOT use convergent encryption.

## Chunks

~~~
enum { root(1), manifest(2), data(3), parity(4), (255) } ChunkRole;

struct {
  uint32 used;
  opaque data[61420];
} ChunkPlain;                 /* sealed: 61,440 bytes */
~~~

All sealed chunks are exactly 61,440 bytes. The payload is cut into 61,420-byte pieces; padding chunks have `used` 0.

## Erasure Coding and Padding

The sender groups data chunks into stripes of `k` data and `m` parity chunks (default 16 and 4), using systematic Reed-Solomon coding over GF(2^8) with a Cauchy generator matrix applied to `ChunkPlain` before sealing. The receiver needs any `k` chunks of a stripe.

If the payload needs `n` data chunks, the sender stores `max(4, Padme(n))` data chunks, where Padme is the padding function of {{PADME}} applied to the chunk count. The receiver MUST fetch padding chunks like any other.

## Manifest

~~~
enum { bit_exact(1), nu_media(2), (255) } TransferMode;

struct {
  uint8  k;
  uint8  m;
  uint32 stripe_count;
} CodingParams;

struct {
  uint16       version;           /* 1 */
  opaque       transfer_id[16];
  TransferMode mode;
  opaque       name<V>;           /* inside encryption only */
  opaque       media_type<V>;
  uint64       payload_size;
  opaque       payload_hash[64];  /* H(payload) */
  uint64       source_size;
  opaque       source_hash<V>;    /* nu_media mode, optional */
  CodingParams coding;
  uint32       chunk_count;
  opaque       chunk_addrs<V>;    /* 32 bytes each */
  uint64       expires;           /* coarse, transport-defined */
  Extension    extensions<V>;
} TransferManifest;

struct {
  TransferManifest manifest;
  opaque signer_ref[32];          /* H256(signer public key) */
  opaque signature<V>;            /* SIG.Sign(sk, Label("manifest")
                                     || manifest) */
} SignedManifest;

struct {
  opaque manifest_addrs<V>;
  uint32 manifest_bytes;
} RootChunk;
~~~

The serialized `SignedManifest` is stored in manifest chunks, whose addresses are listed in one root chunk. A receiver MUST verify the signature and the consistency of `chunk_count`, `coding` and sizes before fetching data chunks, and MUST verify `payload_hash` before presenting or saving the payload. In `nu_media` mode the payload is a nu-media object transcoded from the source at native resolution (R1); in `bit_exact` mode it is the source bytes.

## Offer

~~~
struct {
  opaque transfer_secret[32];
  opaque transfer_id[16];
  opaque root_addr[32];
  uint64 padded_bytes;
  opaque preview<V>;
} TransferOffer;

struct {
  opaque kem_ct[1568];            /* KEM.Encaps(recipient key) */
  opaque ct<V>;                   /* AEAD(KDF(ss, Label("offer"),
                                     32), zero_nonce,
                                     TransferOffer, "") */
} SealedOffer;
~~~

The offer is delivered inside an authenticated end-to-end channel, for example an MLS {{RFC9420}} group whose cipher suite uses ML-KEM-1024 and ML-DSA-87, or as a `SealedOffer` to the recipient's ML-KEM-1024 key. HPKE {{RFC9180}} with an ML-KEM-1024 KEM is an alternative construction for the sealed offer.

## Chunk Store Operations

~~~
enum { chunk_put(7), chunk_get(8), chunk_stat(9),
       chunk_delete(10), (255) } ChunkOp;

PUT:    chunk_addr[32], delete_check[32]
        (= H256(Label("delete check") || del_i)),
        retain, sealed_chunk[61440]
GET:    up to 7 x (chunk_addr[32], return path)
STAT:   up to 1,024 x chunk_addr[32], return path
DELETE: chunk_addr[32], delete_secret[32]
~~~

A node MUST verify on PUT that `H256(Label("chunk addr") || sealed_chunk)` equals `chunk_addr` and that the length is exact, and MUST discard the request otherwise. PUT of an address already held is a no-op. DELETE succeeds only if the hash of `delete_secret` matches the stored `delete_check`. GET returns the chunk or `not_found`. STAT returns a signed bitmap of the addresses held. Nodes SHOULD NOT keep records of which return paths fetched which addresses.

## State Machines

Sender: PREPARING (transcode if chosen, hash, cut, pad, code, seal, persist) to UPLOADING (PUT) to CONFIRMING (STAT until each chunk is held by a quorum of replicas) to OFFERED (send offer; MAY happen as soon as root and manifest chunks are held) to COMPLETE on a done message from every recipient, after which the sender SHOULD DELETE all chunks. The sender persists every state before the network action it records, so all steps resume after interruption.

Receiver: OFFERED to FETCH_MANIFEST to VERIFY_MANIFEST to FETCHING (GET in any order; decode each stripe as soon as `k` chunks are held) to VERIFYING (`payload_hash`) to DONE (send a done message). Failures: `manifest_invalid`, `insufficient_chunks`, `hash_mismatch`. The have-bitmap is persisted so fetching resumes.

## Carriage

nu-transfer is transport-independent. Chunk store operations MAY be carried by a mix network with single-use reply blocks, by MOQT (one track per chunk address, fetched with FETCH, which lets relays cache content-addressed objects), or by a direct session. To keep sizes and timing from leaking, they SHOULD be carried in constant-rate carriers: a carrier that runs whenever its conditions hold, whether or not a transfer is queued.

# Security Considerations

**Confidentiality and integrity.** Chunks are sealed with AES-256-GCM under single-use keys; addresses are ciphertext hashes verified by nodes and receivers, and every address is bound by an ML-DSA-87 signature. Key delivery uses ML-KEM-1024. These choices aim at NIST security category 5 against quantum adversaries, including recording now and decrypting later.

**Hostile media.** Media parsers are a common target for remote, zero-interaction exploits. Decoders MUST enforce the limits in {{media-format}} before allocation, MUST reject rather than repair malformed headers, SHOULD parse containers in memory-safe code in a sandbox without network access, and SHOULD NOT decode a transfer before its manifest signature verifies.

**Models.** Networks for images, residual and enhancement are identified by hash and shipped with the implementation. A stream cannot load code or weights.

**Enhancement and evidence.** Enhancement changes displayed pixels and interpolation creates frames. R6 forbids generative synthesis, R4 keeps enhanced pixels out of the prediction loop, and players must label interpolated frames. Content intended as evidence should use `lossless` or a `bit_exact` transfer.

**Denial of service.** Chunk stores should require an anonymous credential or similar per PUT and bound retention. Erasure coding and replication absorb dropped chunks; nodes that return chunks whose hash does not match can be identified by the receiver.

**Deniability.** If manifests are signed with rotating keys whose private halves are later revealed to the group (as some messaging systems do for message signatures), manifests are as deniable as messages; a standalone signature with a long-term key is not.

# Privacy Considerations

**Content.** No node sees plaintext, names, media types, real sizes or hashes.

**Size.** Padme padding of the chunk count leaks O(log log n) bits; all payloads below about 245 kilobytes appear identical. Variable-bitrate media leaks content through sizes {{VBRLEAK}}; constant-rate operation removes this only if every object, packet and interval is constant, including padding inside encryption.

**Timing and existence.** Carriers that start only when there is something to send reveal that something is being sent. Carriers SHOULD run on a schedule independent of use.

**Linking.** Random per-transfer keys make chunk addresses unlinkable across transfers. A chunk shared by several recipients is fetched several times; a node can count fetches of an address. Per-recipient encryption removes this at the cost of more uploads, and is RECOMMENDED for small objects.

**Metadata.** {{metadata}} removes capture metadata but not what is in the picture, nor the sensor noise pattern that forensic tools can match to a camera.

**Viewport.** Tile requests reveal where a viewer is looking to whoever sees them; over relays, viewers should keep subscription counts fixed.

**Model downloads** at playback would reveal what is being watched and are forbidden.

# IANA Considerations

IANA is asked to register two media types using the templates of {{RFC6838}}, and to create three registries.

## Media Type application/nu-media

Type name:
: application

Subtype name:
: nu-media

Required parameters:
: N/A

Optional parameters:
: profile: one of "call", "stored", "image", "lossless". codecs: a comma-separated list of codec names from the registry in {{codec-registry}}.

Encoding considerations:
: binary

Security considerations:
: See the Security Considerations section of RFC XXXX. The format contains no executable content. Decoders must enforce the size limits before allocating memory.

Interoperability considerations:
: Version is signalled in the stream header; decoders reject unknown major versions.

Published specification:
: RFC XXXX

Applications that use this media type:
: Messaging and media applications exchanging images, video and mixed media.

Fragment identifier considerations:
: N/A

Additional information:
: Deprecated alias names for this type: N/A. Magic number(s): 0x6E 0x75 0x4D 0x65 at offset 0. File extension(s): .numedia. Macintosh file type code(s): N/A.

Person & email address to contact for further information:
: Justin Elliott Staffer, hello@elliottwave.studio

Intended usage:
: COMMON

Restrictions on usage:
: None

Author:
: Justin Elliott Staffer

Change controller:
: IETF

## Media Type video/nu-media

Type name:
: video

Subtype name:
: nu-media

Required parameters:
: N/A

Optional parameters:
: profile and codecs, as for application/nu-media.

Encoding considerations:
: binary

Security considerations:
: As for application/nu-media.

Interoperability considerations:
: As for application/nu-media. Objects of this type contain at least one video track.

Published specification:
: RFC XXXX

Applications that use this media type:
: Video calling, stored video and live streaming applications.

Fragment identifier considerations:
: N/A

Additional information:
: Magic number(s): 0x6E 0x75 0x4D 0x65 at offset 0. File extension(s): .numedia. Macintosh file type code(s): N/A.

Person & email address to contact for further information:
: Justin Elliott Staffer, hello@elliottwave.studio

Intended usage:
: COMMON

Restrictions on usage:
: This registration is for files and framed streams. It does not define an RTP payload format; use with RTP requires a payload format specification under {{RFC4855}}.

Author:
: Justin Elliott Staffer

Change controller:
: IETF

## nu-media Frame Header Extensions Registry {#ext-registry}

IANA is asked to create the "nu-media Frame Header Extensions" registry in a new "nu-media" registry group. Each entry has a Value (16-bit), Name, May Be Critical (Y/N), Location (stream, track, frame) and Reference. Registration policies {{RFC8126}}: 0x0001-0x7FFF Specification Required; 0x8000-0xEFFF Expert Review; 0xF000-0xFFFF Private Use. Value 0 is reserved. Initial entries:

| Value | Name | Critical | Location | Reference |
| --- | --- | --- | --- | --- |
| 1 | mastering_display | N | track | RFC XXXX |
| 2 | content_light_level | N | track | RFC XXXX |
| 3 | tone_map_curve | N | frame | RFC XXXX |
| 4 | enhancement_hint | N | track, frame | RFC XXXX |
| 5 | residual_model | Y | track | RFC XXXX |
| 6 | sample_hash | N | frame | RFC XXXX |
| 7 | roi_map | N | frame | RFC XXXX |
| 8 | live_photo_pair | N | stream | RFC XXXX |
| 9 | spatial_layout | N | stream | RFC XXXX |
| 10 | segment_duration_hint | N | stream | RFC XXXX |

Designated experts should check that a new extension carries no capture metadata ({{metadata}}) and that critical extensions are essential to decoding.

## nu-media Codec Identifiers Registry {#codec-registry}

A registry of 16-bit codec identifiers. Policies: 1-49151 Specification Required; 49152-65279 First Come First Served; 65280-65535 Private Use. Initial entries: 1 hevc_main10, 2 h264_high, 3 nu_residual_v1, 4 nu_image_v1, 5 nu_lossless_v1, 6 opus, each referencing RFC XXXX.

## nu-transfer Error Codes Registry

A registry of 16-bit codes. Policies: 0-1023 Specification Required; 1024-65535 First Come First Served. Initial entries: 0 ok, 1 not_found, 2 bad_size, 3 addr_mismatch, 4 token_invalid, 5 rate_limited, 6 expired, 7 storage_full, 8 bad_delete_secret, 32 unsupported_version, 33 unsupported_critical_extension, 34 limits_exceeded, 35 manifest_invalid, 36 insufficient_chunks, 37 hash_mismatch, 38 model_unavailable, 39 decode_error.

--- back

# Comparison with Conventional Transfer {#comparison}

This appendix is informative. Commercial transfer services such as IBM Aspera {{ASPERA}} move the original bytes at close to line rate and are well suited to long, lossy paths; cloud storage services hold copies on their servers. HLS {{RFC8216}} and similar segment-based streaming deliver variable-bitrate ladders in which segment sizes vary with content.

nu-transfer over a constant-rate privacy carrier is slower per byte than a direct link, because of padding, parity, fixed rates and mix network headers. A bit-exact transfer is not faster than a line-rate transfer tool. It saves time only when the sender transcodes to nu-media at native resolution: for example a ProRes 422 HQ 4K master is roughly 660 Mbit/s (estimate), while the nu-media design point for 4K HDR at streaming quality is 9.6 Mbit/s (unmeasured design value). The saving comes from the codec, and the same transcoded file would move faster still over a line-rate tool; the difference nu-transfer adds is that no server sees the content, its name or its recipients.

# Status of Figures

No nu-media bitrate in this document has been measured with the full layer stack. Figures are design values and estimates; measured results will be added in later revisions.

# Acknowledgments
{:numbered="false"}

TBD.
