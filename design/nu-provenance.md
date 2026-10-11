# nu-provenance: per-unit content provenance without device tracking

How every coded video frame and tile, every audio frame, every 3D unit and every file chunk in khensu.nu gets a hash bound into a signed tree, so a receiver can tell that nothing was changed, added, removed or reordered, and, if the sender chooses, that it came from one source, from a public persona, or straight from a camera in the khensu app, without anyone learning which device or person made it.

Status: design, 11 October 2026. **Nothing here is built or measured.** Byte costs are exact where they follow from the formats (`PROTOCOL.md` 1 sizes: ML-DSA-87 public key 2,592 bytes, signature 4,627 bytes, `H256` 32 bytes); rates and times are **estimates**, and figures for khensu formats that don't exist yet are **design targets**. Registry values proposed here are listed in `nu-media-protocol.md` 16.10. Open questions are in section 14 and `OPEN-QUESTIONS.md` section H (102–108).

## 1. The tension, and the decision

The owner asked for "source fingerprinting on each frame or raw audio frame, or each packet of bytes in a file". In most products, a source fingerprint identifies the device or the account that made something. khensu is a private, anonymous messenger: `nu-media-protocol.md` section 8 strips capture metadata precisely so a picture can't be traced to a phone, and `THREAT-MODEL.md` protects the social graph and identity binding against every node, us and Apple. A fingerprint that identified the device or the sender would undo that.

**Decision: nu-provenance is content provenance and integrity, not device tracking.** It answers "is this exactly what the source produced, and what can be said about that source?" and never "which phone made this?".

| It can prove | It never reveals |
| --- | --- |
| Every unit is exactly what the signer produced, in the order produced, with nothing inserted, removed or spliced from elsewhere | The device: no serial, hardware ID, App Attest key, identifier for vendor, model, OS build or lens |
| All units come from one source (one signing key) | The person, unless they sign with a public persona on purpose |
| Optionally: this came from a given public persona | Location, wall-clock time or time zone; only `pts_us` relative to the stream start (R7) |
| Optionally: this was captured by the camera or microphone in a genuine khensu app and not edited, with no way to tell which device or which other captures came from the same one | Who else received it, or that two private files came from the same sender (with the default modes) |
| Which edits were made, and from which signed parents | Anything to nodes: all provenance data is inside the end-to-end encryption |

## 2. Rules

| Rule | Statement |
| --- | --- |
| P1 No device identity | No field, extension or signature input may contain or be derived from a device identifier, a hardware-bound key that persists across streams, a serial number, capture time, location or the app instance's attestation key. Section 11 lists what is excluded |
| P2 The user chooses the signer | Four modes (section 5): `bound` and `one_time` reveal no identity and are the defaults; `persona` and `attested` are chosen per item or per persona |
| P3 Every unit | Every coded unit of every track and every data piece of a file is a leaf. There is no unprotected byte in a nu-media object except the provenance data itself |
| P4 Inside the encryption | Provenance travels inside tick chunks, nu-transfer chunks, MLS messages or SFrame ciphertexts. Nodes, relays and observers see nothing new, and object sizes stay as the transport fixes them |
| P5 Absence is neutral | Media without provenance shows as "no provenance", never as fake. Broken provenance shows exactly which time ranges, tiles or chunks failed |
| P6 Perceptual fingerprints stay local | Robust perceptual hashes (section 7) are computed and kept on the device. They leave it only when the user publishes them with a public post |
| P7 No new leaks in constant-rate traffic | Provenance in live media rides inside existing fixed-size objects and tracks at fixed intervals, so it changes no packet size or timing |

## 3. Units and leaves

### 3.1 What a unit is

| Content | Unit (one leaf) | Bytes hashed |
| --- | --- | --- |
| Video | One tile of one coded frame (base, residual) | The tile payload: length-prefixed NAL units or residual symbols |
| Image | One tile of one progressive layer | The tile's layer payload |
| Audio | One coded audio frame: 20 ms Opus, 20 or 40 ms `nu_speech_v1`, one FLAC block | The coded frame. For lossless tracks the decoded samples are also covered by `sample_hash` (ext 6, SHA-512); for lossy codecs only the coded bytes are hashed, because decoded samples are not bit-exact across decoders |
| 3D | One `scene_layer` frame: one level of one mesh, texture, animation clip or splat set (`design/nu-3d.md` 3.1) | The frame payload |
| Data and other tracks | One frame | The frame payload |
| File (nu-transfer) | One 61,420-byte data piece of the payload, before erasure coding and encryption (`nu-media-protocol.md` 11.3) | `data[0..used]` of the piece |

### 3.2 Leaf and tree

```
stream_salt = random 16 bytes per stream, in ProvenanceKey (8.1)

leaf = H256(Label("np leaf") || stream_salt || uint8(track_id) || uint8(frame_type) ||
            uint64(pts_us) || uint32(frame_seq) || uint16(tile_index) || uint32(unit_id) ||
            H256(unit_bytes))

chunk_leaf = H256(Label("np chunk") || stream_salt || uint32(piece_index) || H256(piece_bytes))

node = H256(Label("np node") || left || right)
```

- `unit_id` is the 3D unit (`nu-3d.md` 3.1) or zero; `tile_index` is zero when untiled.
- The tree over `n` leaves is the Merkle tree hash of RFC 9162 section 2.1 (split at the largest power of two below `n`), with the labels above in place of its 0x00 and 0x01 prefixes.
- Leaves bind track, frame type, timestamp, sequence and tile, so a verified unit can't be moved to another time, track or tile. The per-stream salt means identical bytes in two streams give different leaves, so verified segments can't be spliced from one stream into another.
- **Hash.** `H256` (SHA-512/256), the protocol's existing primitive, computed with the SHA-512 instructions of recent Apple chips (to confirm per chip). BLAKE3 is faster in software and is natively a tree, but would add a second hash primitive (question 103).
- Leaves are never sent. The receiver computes them from the units it decodes; only roots, checkpoints and signatures travel.

## 4. Roots and checkpoints

### 4.1 Stored objects and files

- **Segment roots.** For each segment (`nu-media-protocol.md` 4.3), `segment_root` is the tree over that segment's leaves in stored order (frame order, then ascending tile index). Images and 3D objects without segments use one tree per progressive layer (`layer_root`).
- **Stream root** is the tree over the segment or layer roots in order.
- **Trailer.** A `provenance` frame (frame type 9, proposed) on a `data` track (codec `nu_provenance_v1`, 14, proposed) at the end of the object carries every segment or layer root, the stream root and, in signing modes, the signature. A receiver that fetches only some tiles or segments (360° viewport fetch, 3D viewer-driven fetch) verifies them against the listed roots without fetching the rest; per-tile inclusion proofs for very large tiled frames (a 42K frame has up to 3,528 tiles) are an index option, about 32 bytes × log2(tiles) per tile per segment (TBD-spike).
- **nu-transfer.** The payload's pieces form their own tree; its root goes in a `provenance` extension of the `TransferManifest` (11.6), which the manifest signature already covers. When the payload is a nu-media object, the object's own trailer covers its units as well.

### 4.2 Live streams and calls

```
struct {
  uint32 checkpoint_seq;            // 0, 1, 2, ...
  uint64 first_pts_us;
  uint64 last_pts_us;
  uint32 leaf_count;
  opaque interval_root[32];         // tree over this interval's leaves
  opaque prev[32];                  // H256(Label("np checkpoint") || previous Checkpoint); zero for the first
  uint8  flags;                     // bit0 final (end of stream), bit1 has_leaf_tags
  opaque leaf_tags<V>;              // optional: 16-byte truncated leaves, for loss-tolerant checking
} Checkpoint;

struct {
  Checkpoint checkpoint;
  opaque     signature<V>;          // empty, or Sign(sk, "np checkpoint", checkpoint)
} ProvenanceCheckpoint;             // payload of a provenance frame (live)
```

- An unsigned checkpoint goes out every interval (default 1 s), chained by `prev`. A signed checkpoint goes out every `sign_every` intervals (default 10, so every 10 s); its signature covers every earlier checkpoint through the chain.
- **Loss.** A receiver that lost frames can't rebuild that interval's root. Without `leaf_tags` the interval shows "unverified (loss)", and later intervals still verify. With `leaf_tags` (default on for broadcasts), every frame that did arrive is checked individually against its 16-byte tag; the tags are covered by the signed chain.
- **Where they ride.** In calls and broadcasts, provenance frames go on the `m` data track (`nu-media-protocol.md` 10.2) inside its fixed-size 1,200-byte objects at its fixed rate (P7). A signed checkpoint needs about 4,700 bytes, so five objects; with the `m` track at one object per second (design target; its rate is not yet set), one signed checkpoint and ten unsigned ones fit in each 10 s.
- **Group calls** already sign a `FrameManifest` every 1 s with video and 5 s audio-only (`PROTOCOL.md` 7). Proposed protocol change: add the interval's `interval_root` (32 bytes) to `FrameManifest`, so group calls get content provenance for 32 bytes per manifest and no extra signature (question 104).
- **1:1 calls** are already authenticated end to end by SFrame keys from MLS. Provenance is off by default for them and on for broadcasts, Places and recorded sessions.

## 5. Signer modes

| Mode | Signer | What a verifier learns | Linkability | Deniability | Default for |
| --- | --- | --- | --- | --- | --- |
| `bound` | None of its own: the root rides inside the sender's MLS message | Inside the conversation: this is exactly what the sender sent | Same as the message | Same as the message (7-day reveal, `THREAT-MODEL.md` 4.1) | Tick-lane media (photos, voice notes, Live Photos, small 3D) |
| `one_time` | A fresh ML-DSA-87 key per stream, public key in the object | Every unit comes from the one source that held this key, unaltered; nothing about who | None across streams | The key proves nothing about identity; inside a conversation it is bound to the sender only through the MLS message, which becomes deniable after the reveal | Stored media, files on the bulk lane, broadcasts |
| `persona` | The persona's ML-DSA-87 key (`PLAN.md`, Public square) | This came from this public persona, unaltered | All items signed by the persona are linkable to it, by design | None: a persona signature is permanent proof | Public posts, chosen per persona |
| `attested` | A one-time key pre-certified by an anonymous capture credential (5.4) | Captured by the camera or microphone in a genuine khensu app, not edited, in credential month M; nothing about which device | None across captures | Proves capture by some genuine app, not by whom | Opt-in per capture ("Captured in khensu") |

### 5.1 `bound`

On the tick lane, a separate signature costs about 7.2 KB (public key plus signature): about 4 chunks, a quarter to a half of a 15–40 KB photo. The MLS message that carries the media key is already signed by the sender, so `bound` puts the object's roots in that message instead:

- **Proposed change to `TickMediaOffer`** (`nu-media-protocol.md` 10.1): add `opaque object_root[32]` and `opaque layer_roots<V>` (32 bytes per progressive layer, typically 3–6 layers). Each layer is checked against its root before it is drawn.
- **Why this is needed anyway.** Every recipient learns `k_obj`, and from it can derive the chunk keys and chunk references of every other recipient leaf (10.1). Today a malicious group member could therefore store substitute chunks in another member's mailbox, and the victim would decrypt and show them as the sender's media. Committing to the content in the sender-signed offer closes this (question 102; also added to `nu-media-protocol.md` section 18).
- If the user wants a self-contained signature on a tick-lane item ("Seal provenance"), the item uses `one_time` and the UI shows the extra chunks.

### 5.2 `one_time`

- The sender's device generates an ML-DSA-87 key pair for the stream, puts the public key in `ProvenanceKey`, signs the trailer or the signed checkpoints, and erases the secret key when the stream ends.
- Forwarding keeps the object byte for byte, so a forwarded file still verifies as "one source, unaltered", with no link to the original sender.
- On the bulk lane the cost (about 7.3 KB per stream) is small next to the minimum padded transfer of about 245 KB.

### 5.3 `persona`

- Public posts are already signed with the persona's key (`PLAN.md`, Public square); the post's signed body includes the media's stream root, so the media inherits the post's signature for 32 bytes.
- Media saved from a post and shared elsewhere carries `persona_ref` and the persona's public key (2,592 bytes) plus its own signature, so it verifies offline; the verifier checks the key against the transparency log when online.

### 5.4 `attested`: anonymous capture attestation

The goal is the strongest claim a phone can honestly make, "this came from a real camera in an unmodified khensu app and wasn't edited", without device identity.

- **Issuance.** When the app tops up its capture credentials, it proves an App Attest check to the credential issuer, as it already does for access tokens (`PROTOCOL.md` 11; `PLAN.md`, Anti-spam without identity). It generates a batch of one-time ML-DSA-87 key pairs on the device, blinds `H256(Label("np capture key") || public_key)` for each, and the issuer blind-signs them under its capture key for the current credential month. The issuer never sees the keys it certifies, so it can't link a later capture to the attestation.
- **Capture.** The app signs in `attested` mode only if every unit came straight from a built-in camera or microphone through `AVCaptureSession` into the nu-media encoder in the same process, with no edit, no screen recording and no external or virtual capture device. It uses one unused certified key per capture and erases the secret key afterwards.
- **Verification.** The verifier checks the issuer's blind signature on the hash of the public key, with the issuer's capture key for month M taken from the epoch header or the transparency log, then checks the stream signature.
- **Key consistency.** There is one issuer capture key per month for everyone, published in the log, so the issuer can't tag users by giving them different keys.
- **What it shows.** "Captured in khensu, [month]". The month is the credential epoch, the only time information in the system; a longer epoch hides more and limits revocation more (question 105).
- **Size.** Depends on the post-quantum blind signature or STARK credential chosen for access tokens (`OPEN-QUESTIONS.md` 17): estimated from a few kilobytes for a lattice blind signature to about 100 KB for a STARK proof (TBD-spike). That fits stored media and files, not the tick lane, so on the tick lane `attested` costs extra chunks and the UI says so.
- **Limits, stated plainly.**
  - App Attest judges the app instance at issuance, not at capture. A device compromised later, or a jailbroken device that injects frames into the capture pipeline, can sign false captures until its credentials run out.
  - It proves the camera saw it, not that the scene was real: filming a screen or a staged scene still verifies.
  - iPhones don't expose sensor-level signing (some cameras sign in the camera with C2PA), so the root of trust is the app, not the sensor.
  - Unlinkable credentials can't be revoked one by one; damage is bounded by the batch size and the credential month.

## 6. Edits, transcodes and export

### 6.1 Edit manifests

```
enum {
  trim(1), crop(2), rotate(3), colour(4), transcode(5), splice(6), overlay(7), redact(8),
  audio_mix(9), stabilise(10), generated_detail(11), matte(12), reframe(13), (255)
} EditOp;

struct {
  opaque         root[32];          // the parent's stream root
  ProvenanceMode mode;
  opaque         proof<V>;          // optional: the parent's ProvenanceKey and signed trailer
} ParentRef;

struct {
  ParentRef parents<V>;             // empty when the user unlinks the origin
  EditOp    ops<V>;
  opaque    op_params<V>;           // coarse parameters (trim points in pts_us, crop rectangle), no tool names
  opaque    output_root[32];
} EditManifest;                     // stream extension edit_manifest (12), covered by the output's signature
```

- The editor (`design/editor.md`) writes an `EditManifest` for every export. Generated content (outpainting, object removal, upscaling with invented texture) is always recorded as `generated_detail`, which matches the editor's "generated detail" flag.
- A pre-send transcode in nu-transfer (`nu_media` mode, 11.12) is a `transcode` edit whose parent is the original file's root, alongside the existing `source_hash`.
- With `proof`, a verifier can follow the chain: "Captured in khensu, then trimmed and colour-corrected". Without it, the parent is named by root only.
- **Unlinking.** A parent root lets anyone who holds the original confirm that this is derived from it. A user who doesn't want that (a redacted copy of a sensitive original, for example) removes the parents; the output then shows "edited, origin not linked".

### 6.2 C2PA export (opt-in)

C2PA Content Credentials are the industry format for provenance outside khensu. Export with C2PA is off by default and opt-in per export, because:

- a C2PA manifest names its claim generator (the app) and carries the signer's X.509 certificate, which can identify the signer or the app;
- C2PA signatures use classical algorithms in the versions we checked (whether a post-quantum algorithm has been added is to check), so they don't meet khensu's ML-DSA-87 rule;
- a certificate trusted by C2PA validators would need a signing service, which conflicts with "nothing is processed on servers" and would let that service see every export.

The proposed export maps `EditManifest` actions to C2PA action assertions and signs with a certificate tied to a persona (self-issued, so validators show an unknown signer), never to the device (question 106).

## 7. Perceptual fingerprints (local)

Cryptographic hashes break on any re-encode. To recognise "this is a re-encode or screenshot of something I have", the device also computes robust perceptual hashes:

| Content | Method | Size (estimate) |
| --- | --- | --- |
| Images, video frames | PDQ (Meta, BSD): 256-bit hash per image, and per video frame sampled once per second and at scene cuts | 32 bytes per sampled frame |
| Video clips | TMK+PDQF (Meta, BSD): one clip-level descriptor | about 1 KB per clip |
| Audio | Spectral landmark hashes (Wang, 2003 style), or a small learned embedding | about 10–30 hashes of 4 bytes per second |
| 3D | None in version 1 | — |

- **Use.** A local index on the device: when the user receives media without provenance, the app can say "similar to a verified original you have" (perceptual matches are always worded as similar, never as the same). A creator can publish fingerprints with a public post, so other people's apps can match re-uploads to the original post on their own devices.
- **P6.** Fingerprints are never sent, uploaded or matched against any list outside the device unless the user publishes them. They are deleted with the media they came from.
- **Weaknesses.** Perceptual hashes can be evaded by small changes and can be attacked with crafted collisions (demonstrated against Apple's NeuralHash in 2021). They are a convenience for the user, never evidence and never a moderation signal.
- **Not a scanning system.** This mechanism is not connected to the illegal-content hash list in `OPEN-QUESTIONS.md` 40, which concerns node operators refusing exact hashes. Whether the two should ever interact is question 107; the recommendation is no.

## 8. Wire formats

### 8.1 `ProvenanceKey` (stream extension 11, proposed)

```
enum { bound(1), one_time(2), persona(3), attested(4), (255) } ProvenanceMode;

struct {
  ProvenanceMode mode;
  opaque stream_salt[16];
  uint16 interval_ms;               // live only: checkpoint interval; 0 for stored objects
  uint8  sign_every;                // live only: signed checkpoint every n intervals
  select (mode) {
    case bound:    struct {};
    case one_time: opaque public_key[2592];
    case persona:  opaque persona_ref[32];      // H256 of the persona public key
                   opaque public_key<V>;        // empty, or the 2,592-byte key for offline checks
    case attested: opaque public_key[2592];
                   uint32 credential_month;
                   opaque issuer_key_ref[32];
                   opaque credential<V>;        // blind signature or STARK proof (5.4)
  };
} ProvenanceKey;
```

- Signature label `"np trailer"` for stored trailers and `"np checkpoint"` for live checkpoints; hash labels `"np leaf"`, `"np chunk"`, `"np node"`, `"np checkpoint"`, `"np capture key"` (registered in `nu-media-protocol.md` 16.10).
- The extension is never critical: a decoder that doesn't know it plays the media and shows "no provenance".

### 8.2 Trailer (stored)

```
struct {
  opaque roots<V>;                  // 32 bytes per segment or layer, in order
  opaque stream_root[32];
  uint32 leaf_count;
  opaque signature<V>;              // empty for bound; Sign(sk, "np trailer", fields above)
} ProvenanceTrailer;                // payload of the final provenance frame
```

### 8.3 Other extensions

| Extension (proposed) | Where | Contents |
| --- | --- | --- |
| `edit_manifest` (12) | stream | `EditManifest` (6.1) |
| `perceptual_fingerprint` (13) | stream | Only when the user publishes it with a public post (7) |
| `provenance` in `TransferManifest` | nu-transfer manifest | Mode, `stream_salt`, piece-tree root and, for `one_time` or `attested`, the `ProvenanceKey` fields; signed by the manifest signature or its own signature |

## 9. Cost

### 9.1 Per unit and per stream

| Item | Bytes | Sent |
| --- | --- | --- |
| Leaf per unit | 32 | Never; computed by the receiver |
| Segment or layer root | 32 per segment (1 s) or layer | Stored trailer |
| Unsigned live checkpoint | about 90, plus 16 per frame with `leaf_tags` | Every interval (1 s) |
| Signature | 4,627 | Once per stored stream; every 10 s live |
| `one_time` public key | 2,592 | Once per stream |
| `persona` reference | 32 (plus 2,592 for offline checks) | Once per stream |
| `attested` credential | TBD-spike: a few KB to about 100 KB (estimate) | Once per stream |
| `bound` roots in the offer | 32 plus 32 per layer | In the MLS message |
| Edit manifest | about 100 plus 40 per parent, plus optional parent proofs | Once per edit |

### 9.2 Worked examples

| Content | Mode | Provenance bytes | Share of the content |
| --- | --- | --- | --- |
| 30 KB photo on the tick lane (design target size) | `bound` | about 160 (object root and 4 layer roots) | about 0.5% |
| Same photo | `one_time` | about 7.4 KB (4 chunks) | about 25% |
| 60 s Opus voice note (240 KB) | `bound` | about 100 | under 0.1% |
| 1 min 1080p HDR nu-media video (20.3 MB design target) | `one_time` | about 9.2 KB (key, signature, 60 segment roots) | about 0.05% |
| 1 GB file on nu-transfer | `one_time` | about 7.3 KB in the manifest | under 0.001% |
| Live broadcast at tier M (about 1,397,000 bit/s encoder rate) | `one_time`, `leaf_tags` at 30 fps | about 90 B/s checkpoints, 480 B/s tags, 4,627 B every 10 s: about 8,300 bit/s | about 0.6% |
| Group call | Root in `FrameManifest` | 32 bytes per manifest (256 bit/s with video) | negligible |

Hashing cost: SHA-512 runs at gigabytes per second with hardware instructions (estimate), so hashing a 9.6 Mbit/s 4K stream (1.2 MB/s) is negligible; ML-DSA-87 signing and verification take well under a millisecond each on Apple silicon (estimate, to measure with libcrux).

## 10. Verification on the receiver

1. Parse `ProvenanceKey` and enforce limits before allocation, as for every header.
2. Compute each leaf as the unit is decoded.
3. At each layer end, segment end or checkpoint, build the root and compare it with the committed root: the `bound` roots in the MLS-signed offer, the trailer, or the checkpoint chain.
4. Check the signature for the mode: the included one-time key; the persona key (from the post, the log or the included key); for `attested`, the issuer's blind signature on the key hash with the issuer key for the credential month, then the stream signature.
5. Follow `EditManifest` parents where proofs are included.
6. Show the result:

| State | Shown as |
| --- | --- |
| `bound`, all roots match | Nothing extra (normal message media); "Verified" in details |
| `one_time`, valid | "One source, unaltered" |
| `persona`, valid | "From @persona, unaltered" |
| `attested`, valid | "Captured in khensu, [month], unedited" |
| Valid edit chain | "Edited from [parent state]: trim, crop…" ; "Edited, origin not linked" when parents are removed |
| Live, interval lost | "Unverified (loss)" for that span only |
| Mismatch | "Provenance broken" with the failing time ranges, tiles or chunks; for `bound` tick media, the failing layer is not drawn |
| None | "No provenance" (neutral, P5) |

Progressive previews are drawn as each layer verifies. Players that show receiver enhancement or interpolated frames (R4, A3, D5) say so in the same details view, since provenance covers the decoded data, not enhanced pixels.

## 11. What is never included

- Device identifiers of any kind: serial numbers, IMEI, hardware UUIDs, identifier for vendor, advertising identifier, App Attest key IDs or assertions, Secure Enclave key handles, MAC addresses.
- Device model, OS version, app version, camera module, lens or sensor identifiers.
- Location, altitude, heading, motion data, Wi-Fi or cell information.
- Wall-clock capture, edit or send times, and time zones. The only times are `pts_us` from the stream start and, in `attested` mode, the credential month.
- A long-lived key of the device or account (only one-time keys, the MLS leaf key through `bound`, or a persona key the user chose).
- Tool names or versions in edit manifests.
- Perceptual fingerprints, unless the user publishes them (P6).

What remains, as for all media (`nu-media-protocol.md` 15): faces, places and screens in the content, and the sensor noise pattern (PRNU), which provenance neither adds nor removes.

## 12. Threats

| Threat | Mitigation | What remains |
| --- | --- | --- |
| Tracking a device through its media | P1; one-time keys; App Attest only at issuance, behind blind signatures | PRNU and content (section 11) |
| Linking a user's private files to each other | New key and salt per stream; `bound` uses the conversation's own authentication | Two copies of the same file have the same roots: whoever holds both can tell they're the same file, as they could from the content |
| Altering, inserting or removing frames, tiles or chunks | Leaves in signed or MLS-committed trees | None while ML-DSA-87 and SHA-512/256 hold |
| Reordering or splicing between streams | Leaves bind position and the stream salt | — |
| Truncation | `final` flag and leaf counts in the signed trailer or last checkpoint | A live stream cut before its next signed checkpoint verifies only up to the last one |
| Insider substitution of tick media | `object_root` and `layer_roots` in the sender-signed offer (5.1) | Requires the proposed offer change |
| Presenting old media as new | No wall-clock time by design; the UI never infers "live" or "recent" from provenance | `attested` shows the month only |
| Fake "attested" captures | App Attest at issuance; one key per capture; monthly credentials; one issuer key for everyone in the log | Compromised or jailbroken devices until their credentials expire; filmed screens (5.4) |
| Issuer tagging users | Blind signing; one published capture key per month | Depends on the blind-signature scheme's unlinkability (TBD-spike) |
| Stripping provenance | Can't be prevented | Shown as "no provenance", not as fake (P5) |
| Perceptual hash abuse (scanning, false matches, crafted collisions) | Local only; worded as "similar"; not used as evidence or for moderation | User-published fingerprints can be attacked like any perceptual hash |
| Wrapped 3D file showing different content outside khensu | `fallback_binding` (`nu-3d.md` 7.3) | Other apps don't check it |
| Deniability loss | `bound` and `one_time` keep the conversation's 7-day deniability; `persona` and `attested` are chosen knowingly | A persona signature is permanent proof of authorship, which the UI states |
| Quantum adversary | ML-DSA-87 signatures, SHA-512/256 hashes | — |

## 13. Patent candidates

For `PATENTS.md` (design only, not built; assess before publishing). Prior art to compare against: C2PA and Content Credentials; ProofMode (Guardian Project), Truepic and its Qualcomm Snapdragon integration, Serelay, Starling Lab, Amber Authenticate; in-camera signing (Leica, Sony, Nikon); stream signing (Gennaro and Rohatgi, 1997; TESLA; EMSS); Merkle trees and RFC 9162; blind signatures (Chaum) and Privacy Pass (RFC 9576–9578); anonymous credentials (Idemix, U-Prove, BBS+); Apple App Attest and Google Play Integrity; PDQ, TMK and audio fingerprinting (Wang, 2003); khensu's own signed frame manifests (`PATENTS.md`). Candidate novelty for counsel:

1. Anonymous capture attestation: one-time media-signing keys pre-certified by blind signature after a single device attestation, so verifiers learn "genuine app, unedited, capture month" and nothing that links captures or devices.
2. Per-unit provenance trees committed inside fixed-size, fixed-rate media objects and existing signed frame manifests, adding provenance to live media without changing the traffic pattern.
3. User-selected provenance signers (conversation-bound, one-time, persona, attested) over leaves that bind position and a per-stream salt, with edit manifests whose parent links the user can remove.
4. Committing per-layer roots in a progressive media offer to stop insider substitution when chunks are encrypted per recipient from a shared object key.

## 14. Open questions

1. **Tick media substitution** (question 102): adopt `object_root` and `layer_roots` in `TickMediaOffer` now, independent of the rest of nu-provenance.
2. **Hash** (question 103): SHA-512/256 everywhere, or BLAKE3 for unit trees.
3. **Group-call manifests** (question 104): add `interval_root` to `FrameManifest` in `PROTOCOL.md` 7.
4. **Capture credential epoch and scheme** (question 105): month or longer; lattice blind signatures or STARK credentials (with 17); batch size.
5. **C2PA** (question 106): offer C2PA export at all, and with which signer.
6. **Perceptual fingerprints and the illegal-content list** (question 107): keep them strictly separate (recommended).
7. **Default on the tick lane** (question 108): `bound` for tick media and `one_time` for stored media and files (recommended), or one-time keys everywhere at about 4 extra chunks per item.
