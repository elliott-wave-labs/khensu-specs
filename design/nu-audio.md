# nu-audio: speech, music, lossless and spatial sound

How khensu.nu carries sound beyond the 32 kbit/s Opus of calls: very low-bitrate speech for poor links and voice notes, music at streaming-service quality, bit-exact lossless masters up to 192 kHz, and spatial audio with head tracking, all inside the same nu-media container (`design/nu-media-protocol.md`) and all at constant rate wherever audio travels live.

Status: design, 11 October 2026. **Nothing here is built or measured.** Every bitrate, size and quality figure for nu-audio is a **design target**; every figure for AAC, Opus, FLAC, ALAC, Dolby Atmos, APAC and the neural codecs is an **estimate** from public material unless a measurement is cited. Section 11 is the benchmark that replaces them. Registry values proposed here are listed in `nu-media-protocol.md` 16.10. Open questions are in section 12 and `OPEN-QUESTIONS.md` section H (97–101). Per-frame provenance for audio is in `design/nu-provenance.md`.

## 1. Profiles

| Profile | Codec | Rate | Where it's used | Status |
| --- | --- | --- | --- | --- |
| Call | Opus CBR, mono, 48 kHz, 20 ms, DTX off | 32,000 bit/s | Every call, room and Push to Talk session (`PROTOCOL.md` 7.1) | Existing |
| Low-bandwidth speech | `nu_speech_v1` (neural), 16 kHz output extended to 48 kHz on the receiver | 6,000 bit/s design target (3,200 and 9,200 as alternatives) | Voice notes in the ticks, calls on poor links, mesh radio, satellite | New |
| Music | Opus CBR or constrained VBR, stereo, 48 kHz | 128,000–256,000 bit/s design target | Shared songs, live performances in Places, music in video | New |
| Lossless | FLAC (RFC 9639), integer PCM | Source rate, typically 50–70% of PCM (estimate) | Masters, archives, anything that must be bit-exact | New |
| Spatial | Opus with ambisonic channel mapping (RFC 8486), first to third order; channel beds up to 7.1.4 | 192,000–448,000 bit/s design target | Spatial video, Places, immersive music, spatial voice in group calls (later) | New |

Exports to other apps use AAC, ALAC, FLAC, Opus or APAC through the platform encoders (section 9).

## 2. Rules

These extend R1–R8 in `nu-media-protocol.md` section 3.

| Rule | Statement |
| --- | --- |
| A1 Constant rate when live | Audio that travels in real time (calls, rooms, broadcasts, Push to Talk) is constant bitrate in fixed-size objects at a fixed rate, with no discontinuous transmission. Silence costs exactly what speech or music costs, so packet sizes and timing reveal nothing about who is speaking or what is playing (the VBR leaks described by Wright et al. are why) |
| A2 Native for lossless | Lossless tracks keep the source's sample rate, bit depth and channel count. Lossy tracks are coded at 48 kHz (Opus's only internal rate); the source rate is recorded so exports can return to it. Content above 20 kHz survives only in lossless |
| A3 Enhancement outside the bitstream | Receiver-side bandwidth extension, packet-loss concealment, noise suppression and dereverberation are display-only, like the video enhancement layer (R4): never fed back into decoding, never exported as if received, and switched off for lossless tracks and in evidence mode |
| A4 Fidelity | Nothing is added that the speaker or performer didn't produce (R6). Neural speech coding at very low rates resynthesises the waveform; it is allowed only in the low-bandwidth profile, labelled "low-bandwidth voice", and must pass the fidelity gates in 11.3. Evidence mode never uses it |
| A5 Metadata stripping | Section 8 of `nu-media-protocol.md` applies. In addition: ID3 tags, Vorbis comments, iTunes atoms, Broadcast WAV `bext` (originator, origination date and time), iXML, recorder serial numbers, GPS in recorder metadata and embedded cover art are dropped. Title, artist and cover art are kept only if the user keeps them, inside the encryption |
| A6 Head pose stays local | Head-tracking data is used only by the receiving device's renderer and never leaves it. Nothing in the format or the call framing carries listener orientation |

## 3. Constant-rate carriage

### 3.1 Calls and live audio

Call audio objects are SFrame ciphertexts of a fixed size per tier (`nu-media-protocol.md` 10.2). Each object holds one coded frame plus the 18-byte `CallObjectPlain` header, a typical 17-byte SFrame header and the 16-byte tag (51 bytes of overhead), padded to the tier's object size. Design targets:

| Tier | Codec and rate | Frame | Coded bytes per frame | Object size | Objects per second | On the wire (objects only) |
| --- | --- | --- | --- | --- | --- | --- |
| A-low (new) | `nu_speech_v1`, 6,000 bit/s | 40 ms | 30 | 96 B | 25 | 19,200 bit/s |
| A (existing) | Opus CBR 32,000 bit/s | 20 ms | 80 | 160 B | 50 | 64,000 bit/s |
| A-music (new) | Opus CBR 128,000 bit/s stereo | 20 ms | 320 | 384 B | 50 | 153,600 bit/s |
| A-hifi (new) | Opus CBR 256,000 bit/s stereo | 20 ms | 640 | 704 B | 50 | 281,600 bit/s |
| A-spatial-1 (new) | Opus, first-order ambisonics (4 channels), 256,000 bit/s | 20 ms | 640 | 704 B | 50 | 281,600 bit/s |
| A-spatial-3 (new) | Opus, third-order ambisonics (16 channels), 448,000 bit/s | 20 ms | 1,120 | 1,200 B | 50 | 480,000 bit/s |

- **Spare bytes carry redundancy, not nothing.** The existing 160-byte object has about 29 bytes of padding after an 80-byte Opus frame. Version 1 fills them with Opus deep redundancy (DRED, Opus 1.5) or a low-rate copy of earlier frames, so a lost object can be rebuilt from its successor. The object size and rate don't change, so this costs no wire bits and reveals nothing.
- **Same-tier fallback.** On a poor link the sender can switch the A tier's content from Opus 32 kbit/s to `nu_speech_v1` at 6 kbit/s plus redundancy for the previous four frames (5 × 15 bytes at 20 ms framing), inside the same 160-byte objects. Nothing changes on the wire; speech survives bursts of up to 80 ms of loss. A tier change to A-low saves wire bits but is visible to the local network, like video tier changes (`PROTOCOL.md` 7.1).
- **Tier changes** follow the video rules: at most every 30 s, adjacent tiers only, with hysteresis.
- **Packing into QUIC packets.** `nu-media-protocol.md` 10.2 pads every QUIC packet carrying call objects to one fixed size per session (about 1,350 bytes). In an audio-only call that would put each 160-byte object in a 1,350-byte packet, about 540 kbit/s on the wire. Audio-only sessions need a smaller fixed packet size, or several 20 ms objects per packet at the cost of latency (TBD-spike; open question 98).
- **Live lossless** (a studio session over the user's own node) can't save wire bits: the constant rate must cover the largest possible FLAC frame, which is about the PCM rate. Lossless saves space only in stored files.

### 3.2 Voice notes and music in the ticks and the bulk lane

Stored audio is a nu-media object like an image: on the tick lane up to `TICK_MEDIA_MAX` (256 chunks of 1,990 bytes), otherwise a nu-transfer on the bulk lane. Within a stored file, Opus may use constrained VBR, because the object's size is padded by the transport and visible only to the recipients.

| Content | Codec | Size | Lane and time |
| --- | --- | --- | --- |
| 60 s voice note | Opus 32,000 bit/s | 240,000 B, 121 chunks | Ticks: about 41 ticks, about 82 s |
| 60 s voice note | `nu_speech_v1` 6,000 bit/s (design target) | 45,000 B, 23 chunks | Ticks: about 8 ticks, about 16 s |
| 4 min song | Opus 160,000 bit/s (design target) | 4.8 MB | Bulk lane |
| 4 min song, 16-bit 44.1 kHz | FLAC, about 900,000 bit/s (estimate) | about 27 MB | Bulk lane |
| 4 min song, 24-bit 96 kHz | FLAC, about 3,000,000 bit/s (estimate) | about 90 MB | Bulk lane |

Voice notes play progressively: the first chunks hold the first seconds, so playback starts before the rest arrives.

## 4. Low-bandwidth speech (`nu_speech_v1`)

**Why.** At 6 kbit/s a minute of speech fits in eight ticks instead of 41, calls survive links that can't carry 64 kbit/s, and the mesh radio and satellite paths (`PLAN.md`, Portal project) can carry voice. Opus at 6 kbit/s is narrowband SILK and sounds muffled; neural codecs at the same rate are much closer to wideband speech (published claims, to verify in 11).

**Candidates** (all must run on the device; nothing is processed on servers):

| Candidate | Rates | Latency | Licence | Notes |
| --- | --- | --- | --- | --- |
| Lyra v2 (Google, SoundStream-based) | 3.2, 6, 9.2 kbit/s | 20 ms frames | Apache-2.0 (code and weights, to confirm) | Fixed-size frames, so naturally constant rate; adversarially trained decoder (A4) |
| Opus 1.5 at 6–9 kbit/s with NoLACE | 6–12 kbit/s | Opus's | BSD | NoLACE is a receiver-side neural post-filter on a standard Opus bitstream, so it sits outside the bitstream (A3); lowest risk |
| EnCodec (Meta) | 1.5–24 kbit/s | Streaming mode available | Code MIT; weights' licence to check | General audio at 24 kHz; heavier |
| Descript Audio Codec (DAC) | about 8 kbit/s at 44.1 kHz | Not low-latency | MIT (to confirm) | Music and speech; for stored notes, not calls |
| Mimi (Kyutai) | about 1.1 kbit/s | 80 ms frames | To check | Very low rate; strong resynthesis, highest fidelity risk |

**Recommendation for the spike:** Opus 1.5 at 6–9 kbit/s with NoLACE as the baseline, Lyra v2 at 6 kbit/s as the neural codec, both measured against the A4 gates. `nu_speech_v1` becomes whichever passes with fewer bits, retrained on our own data if the licence or fidelity requires it.

**Format.** `codec_config` holds the model ID (`H256(Label("na speech model") || descriptor || weights)`, as image models), the frame length (20 or 40 ms), the rate and the output sample rate. Frames are fixed-size quantiser indices with no entropy coding, so every frame is the same size and the bitstream is identical on every device. The decoder runs in FP16 on the Neural Engine or CPU; decoded samples may differ slightly between devices, but nothing predicts from them.

**Fidelity risk.** Very low-rate neural codecs can change phonemes, smooth out accents, or make one voice sound like another, because the decoder resynthesises speech from a compact code. That matters for a messenger: a mis-heard "not" changes meaning, and a voice that doesn't sound like its speaker undermines trust. The gates in 11.3 (word error rate and speaker similarity against Opus at 32 kbit/s) are pass/fail for shipping, and the UI labels the mode.

## 5. Music

- **Codec.** Opus at 48 kHz stereo, 128,000–256,000 bit/s (design target; Opus is generally reported transparent for most listeners at about 128–160 kbit/s stereo, an estimate to verify in 11). CBR in live tiers, constrained VBR in stored files.
- **Why not AAC inside nu-media.** AAC needs a patent licence for encoders outside the platform's own, and Opus is at least as good at these rates (estimate). AAC stays as an export format through AudioToolbox, where the platform encoder is used (licensing position to confirm with counsel, question 99).
- **Passthrough.** A song the user already has as AAC, ALAC or MP3 can be sent untouched as a bit-exact nu-transfer instead of being re-encoded; re-encoding lossy to lossy costs quality, and the app says so.
- **Loudness.** Tracks may carry integrated loudness, loudness range and true peak (ITU-R BS.1770, EBU R128) in a `loudness` extension (proposed), so players can level songs without analysing them.

## 6. Lossless and high resolution

- **Codec.** FLAC (RFC 9639, December 2024), integer PCM, 1 to 8 channels (FLAC's limit per stream; more channels are open question 6 in section 12), 8 to 32 bits per sample, sample rates up to 192 kHz in version 1. Each FLAC frame is one `audio_frame`.
- **Bit-exact.** Every frame carries `sample_hash` (ext 6, SHA-512 of the decoded samples), as `nu_lossless_v1` does for pictures, and a decoder MUST report failure if a hash differs. The provenance tree (`nu-provenance.md`) covers the coded frames as well.
- **32-bit float.** FLAC and ALAC are integer-only. Float masters (32-bit float WAV or CAF from a DAW) travel as a nu-transfer in a new **sample-exact** variant of `bit_exact`: the app rewrites the file's container without its metadata (A5) and keeps every sample bit for bit, recording the SHA-512 of the samples. A float lossless codec in nu-media is question 100.
- **Why not ALAC inside nu-media.** ALAC is open (Apache-2.0) and native on Apple platforms, but FLAC compresses slightly better on typical music (estimate), has an IETF specification and is supported on Android and the web. ALAC remains an export format.
- **Enhancement** is off for lossless tracks (A3).

## 7. Spatial audio

### 7.1 What's carried

| Layout | How | Notes |
| --- | --- | --- |
| Binaural stereo | Opus stereo with a `binaural` flag | Already rendered for headphones; the receiver doesn't spatialise again |
| Channel beds | Opus channel mapping family 1 (mono to 7.1); 7.1.4 and other layouts with family 255 plus a channel-layout extension | 7.1.4 is the usual Atmos bed |
| Ambisonics, first to third order | Opus channel mapping families 2 and 3 (RFC 8486): 4, 9 or 16 channels, ACN order, SN3D normalisation (AmbiX), optional head-locked stereo pair | Matches iPhone spatial recordings (first order) and Apple's APAC ambisonic support (up to third order) |
| Objects (sound sources with positions) | Later: positions on a metadata track | ASAF and Atmos are object-based; version 1 carries objects only in 3D scenes (`design/nu-3d.md` 3.9) |

The `ambisonics_layout` extension (proposed) records order, normalisation, channel order and whether a head-locked pair is present.

### 7.2 Rendering on the receiver

- The receiver decodes the ambisonic or channel bed and renders it binaurally with head tracking (AirPods motion through `CMHeadphoneMotionManager`) using Apple's spatial audio renderer (AVAudioEngine, PHASE or the platform APAC renderer; to choose in the spike), or to the device's speakers.
- Head pose never leaves the device (A6). In group calls with spatial voice (later), each participant is placed locally by the receiver from the room layout, not by sending positions.

### 7.3 Apple Spatial Audio, ASAF and APAC

- **What Apple ships (iOS 26).** Apple Spatial Audio Format (ASAF) is Apple's production format: linear PCM plus spatial metadata in Broadcast WAV files, with objects and higher-order ambisonics. The Apple Positional Audio Codec (APAC) is its delivery codec. The APAC encoder is available from iOS, iPadOS and macOS 26 and supports ambisonics up to third order; the decoder from iOS 17 and macOS 14. On iOS 26, apps can record first-order ambisonics with `AVAssetWriter` into a spatial audio asset: an APAC track, an AAC stereo compatibility track and a metadata track (Apple WWDC25 sessions 251, 297 and 403; Apple's APAC document).
- **Import.** iPhone spatial recordings (APAC first order) are decoded through AVFoundation and re-encoded as Opus first-order ambisonics. APAC isn't used inside nu-media: it is proprietary, its encoder exists only on Apple platforms, and Android and the web can't decode it.
- **Export.** "Save to Photos" and "Share outside khensu" write APAC through `AVAssetWriter` with the AAC stereo compatibility track, so Photos and other Apple apps play it as spatial audio. Android and the web get Opus ambisonics in WebM or Ogg, or a binaural AAC render.
- **Dolby Atmos.** Played through Apple's decoders where it arrives (E-AC-3 JOC), never authored by khensu; authoring needs Dolby's licence. Imported Atmos decodes to channels, so it is carried as a 7.1.4 bed (objects are lost) or sent bit-exact.

### 7.4 Auto spatial for Akashic members (`nu_upmix_v1`)

Proposed 11 Oct 2026, design only; nothing here is built or measured, and every figure is a design target. When an Akashic member plays a track that has no spatial mix (mono or plain stereo, with no `binaural` flag, channel bed or ambisonics), their own device separates the mix into its parts and places them around the listener, live, on the Neural Engine. Apple's chips have no "TPU"; the Neural Engine is the equivalent, and `nu_upmix_v1` is written for it. It isn't Apple's "Spatialize Stereo", which widens the whole stereo image; this places each part of the song.

**Who gets it.** Akashic members only (`PLAN.md`, subscriptions), alongside Akashic's upscaling. The app checks the Akashic entitlement on the device with StoreKit 2's signed transactions; no server is asked, and the network never learns which tracks were upmixed (A6).

**Pipeline, all on the listener's device.**

| Stage | What it does | Runs on |
| --- | --- | --- |
| 1. Separate | `nu_sep_v1`, our own separation network, splits the stereo mix into vocals, drums, bass, other instruments and ambience, 44.1 or 48 kHz, in 2-second windows with 0.5 s overlap | Neural Engine (Core ML, 16-bit, convolution only so every layer stays on the Neural Engine) |
| 2. Keep it whole | Mixture-consistency projection: the five stems are corrected so they sum back to the original stereo, sample for sample to within 16-bit rounding (−90 dBFS) | CPU (Accelerate) |
| 3. Place | Vocals front centre; bass centre and the low-frequency channel; drums front, 60° wide; other instruments spread to ±70° following their stereo position; ambience to the surrounds and height, decorrelated. The placement table is fixed and published, so the same track always sounds the same | CPU |
| 4. Encode the scene | Third-order ambisonics (16 channels) or a 7.1.4 bed, held in memory only | CPU |
| 5. Render | Binaural with head tracking through the spatial renderer in 7.2, using the listener's Personalized Spatial Audio profile; to speakers on a Mac or HomePod | Platform renderer |

**Rules.**

- **Display only (A3).** The upmix is an enhancement outside the bitstream: it is never stored, exported, published, forwarded or fed back into encoding, and nobody receives it but the listener's ears.
- **The artist decides.** A track's `spatial_policy` extension (proposed) can say `no_auto` and the upmix never runs. Artists own their work (`PLAN.md`, creators); a mix they chose to release in stereo stays stereo if they say so.
- **Labelled and reversible.** The now-playing screen shows "Auto spatial", and one tap plays the original stereo. Tracks with a real spatial mix always play that mix instead.
- **Nothing lost.** Because of stage 2, folding the upmix back to stereo gives the original; if the stems fail that check for a window, that window plays as plain stereo.
- **Offline and private.** The models ship inside the app; no audio, stem, position or head pose leaves the device.

**Akashic artists.** When an Akashic member publishes a stereo track, they can run the same pipeline on their own devices before release, adjust the placement, and publish the result as a real spatial mix (a 7.1.4 bed or third-order ambisonics, 7.1) labelled "auto-mixed". That is Akashic's "one rung above the source" applied to sound. The stereo master is published with it.

**What we must write.** `nu_sep_v1` (the separation network, its training code and its Core ML conversion), the mixture-consistency and placement stages, the scene encoder, and the test harness below. Open separation models such as HTDemucs (MIT) are the comparison point, not the product: their attention layers fall back from the Neural Engine to the GPU, and we need weights trained only on data we hold rights to (11.2).

**Budgets (design targets).** At least 20× real time on an iPhone 17 or M-series Mac, so a 4-minute song is ready in 12 s and playback can start after the first window; added latency under 2.5 s before sound, or immediate stereo that crossfades to spatial once the first windows are ready; under 150 mW extra while playing; model under 40 MB.

**Gates before it ships.**

- Separation quality at least 7 dB SDR (signal-to-distortion ratio) averaged over vocals, drums, bass and other on the MUSDB18-HQ test set (an estimate of what a Neural Engine-sized model can reach; HTDemucs is reported near 9 dB).
- Stereo fold-down within −90 dBFS of the original on every test track (stage 2).
- A MUSHRA listening test with at least 20 listeners on AirPods Pro and AirPods Max: auto spatial preferred over the original stereo and over "Spatialize Stereo" on most of a 40-track set across genres, with no track rated worse than stereo by most listeners.
- Real-time factor, latency, power and size measured on the oldest supported iPhone, against the budgets above.

The ñü.sounds demo on khensu.nu currently uses a plain matrix upmix made with FFmpeg's `surround` filter, not `nu_upmix_v1`; it is replaced once `nu_upmix_v1` passes these gates.

## 8. Receiver-side enhancement (outside the bitstream)

| Operation | Use | Rule |
| --- | --- | --- |
| Bandwidth extension | `nu_speech_v1` at 16 kHz to 48 kHz output; old narrowband sources | A3; labelled |
| Packet-loss concealment | Neural concealment for lost call frames (Opus 1.5 deep PLC class) | A3; concealed spans counted, never presented as received |
| Noise suppression and dereverberation | When the far end sends noisy audio | A3; off for music, lossless and evidence mode |

Sender-side processing (echo cancellation, which calls need, and the user's own choice of Apple's on-device voice isolation) happens before encoding, on the sender's device, and is part of what is sent. No audio is processed on a server.

## 9. Export

| Target | Format | Encoder | Notes |
| --- | --- | --- | --- |
| Photos, Music, other Apple apps | AAC-LC 256 kbit/s in `.m4a`, or ALAC | AudioToolbox | ALAC for lossless sources |
| Spatial, Apple | APAC with AAC stereo compatibility track in `.mov` or `.mp4` | `AVAssetWriter` (iOS 26 and later) | 7.3 |
| Lossless, everywhere | FLAC | libFLAC (BSD) | Bit-exact from nu-media lossless |
| Open formats | Opus in Ogg (`.opus`) or WebM | libopus | Passthrough from nu-media Opus tracks, no re-encode |
| DAW masters | WAV or CAF, integer or float PCM | Our own writer | Metadata-free (A5) |

## 10. Comparison

### 10.1 Music and general audio

| Codec | Typical rate for stereo music (estimate) | Algorithmic latency (estimate) | Lossless | Spatial | Licence | Apple platform support |
| --- | --- | --- | --- | --- | --- | --- |
| AAC-LC | 192–256 kbit/s (Apple Music's standard tier is 256 kbit/s) | about 50 ms and up | No | Channel beds | Patent pool for encoders | Hardware and system encoder and decoder |
| HE-AAC v2 | 32–64 kbit/s, not transparent | higher than AAC-LC | No | Stereo | Patent pool | System |
| Opus | 128–160 kbit/s generally transparent | 26.5 ms default (5–66.5 ms) | No | Ambisonics (RFC 8486), channel beds | BSD, royalty-free (RFC 6716) | Bundled libopus |
| FLAC | 50–70% of PCM: about 700–1,000 kbit/s at 16-bit 44.1 kHz | One block, typically about 90 ms | Yes | Channels | BSD (RFC 9639) | System decoder |
| ALAC | Slightly larger than FLAC | One packet | Yes | Channels | Apache-2.0 | Native |
| Dolby Atmos (E-AC-3 JOC) | about 768 kbit/s on Apple Music | — | No | Objects and beds | Proprietary, licensed | Decoder |
| APAC | from about 64 kbit/s; 384–768 kbit/s for first- to third-order ambisonics (Apple's recommendation for projected media) | — | No | Objects, beds, ambisonics to third order | Proprietary | Encoder iOS 26+, decoder iOS 17+; not on Android or the web |
| **nu-audio**, design targets | Opus 128–256 kbit/s; FLAC lossless; ambisonics 256–448 kbit/s | 26.5 ms (Opus), 40–60 ms (speech) | FLAC, with SHA-512 per frame | Ambisonics to third order, beds to 7.1.4; objects later | Open codecs only inside nu-media | Bundled; platform encoders for export |

### 10.2 Low-rate speech

| Codec | Rate | Bandwidth | Licence | Quality relative to Opus 32 kbit/s |
| --- | --- | --- | --- | --- |
| Opus (SILK) | 6 kbit/s | Narrowband | BSD | Much lower (estimate) |
| AMR-WB | 12.65 kbit/s | Wideband | Patent pool | Lower (estimate) |
| EVS | 7.2–9.6 kbit/s | Wideband to super-wideband | Patent pool | Close at 9.6 (estimate) |
| Lyra v2 | 3.2–9.2 kbit/s | Wideband | Apache-2.0 | Google reports 3.2 kbit/s comparable to Opus at about 10 kbit/s (to verify) |
| **`nu_speech_v1`**, design target | 6 kbit/s | Wideband coded, full band after extension | Ours | Same word error rate and speaker similarity as Opus 32 kbit/s (11.3) |

## 11. Benchmark plan

A planned script, `bench/audio.py`, and an audio page in the `bench/ios` NuBench app (encode and decode on the phone, scored on the Mac like the video runs). Data in `bench/out/audio/`.

### 11.1 Metrics

| Metric | What | Notes |
| --- | --- | --- |
| ViSQOL v3 | Full-reference quality, audio mode (48 kHz) for music, speech mode (16 kHz) for speech | Apache-2.0 |
| PESQ (ITU-T P.862) and POLQA (P.863) class | Full-reference speech quality | PESQ reference code has licence restrictions and POLQA is a commercial licence; used only if licensed, ViSQOL otherwise |
| WARP-Q | Full-reference quality designed for generative speech codecs | Neural codecs fool older metrics |
| NISQA, DNSMOS | No-reference speech quality | Licences to check |
| Word error rate | On-device `SpeechAnalyzer` transcription of decoded speech against the source transcript | Fidelity gate (11.3) |
| Speaker similarity | Cosine similarity of speaker embeddings (ECAPA-TDNN, SpeechBrain, Apache-2.0) between source and decoded | Fidelity gate (11.3) |
| AMBIQUAL | Ambisonic quality (localisation accuracy and listening quality, a ViSQOL extension) | Spatial tiers |
| Listening tests | MUSHRA (ITU-R BS.1534) for music and spatial; ABX for transparency claims | Replace metric-only claims before anything is quoted |
| Device | Encode and decode time per frame (CPU, Neural Engine), energy (MetricKit), mouth-to-ear latency on a loopback rig, robustness at 1–20% random and burst loss | iPhone 18 Pro and the oldest iOS 26 device |

### 11.2 Content and licences

| Set | Licence | Use |
| --- | --- | --- |
| LibriSpeech test-clean | CC BY 4.0 | Speech, word error rate |
| VCTK | CC BY 4.0 | Many speakers and accents, speaker similarity |
| ITU-T P.501 test signals | ITU terms | Standard speech test material |
| EBU SQAM | EBU terms (to check) | Critical music excerpts |
| MUSDB18-HQ | Non-commercial research | Private development only |
| Ambisonic recordings (EigenScape or similar) | To check | Spatial tiers |
| Our own iPhone recordings, including spatial audio | Ours | Real phone content |

### 11.3 Pass criteria (design targets)

- **Music:** Opus at 160 kbit/s indistinguishable from the source in ABX for most listeners on the test set; ViSQOL within 0.1 of AAC-LC at 256 kbit/s.
- **Lossless:** every frame hash matches on every supported device; FLAC size within 2% of `flac -8`.
- **Low-bandwidth speech:** at 6 kbit/s, word error rate no more than 1 percentage point above Opus at 32 kbit/s, speaker similarity at least 0.85 against the source (threshold to calibrate on Opus 32 kbit/s), and no new phoneme substitutions in a targeted minimal-pair test. Failing any of these blocks shipping the mode (A4).
- **Calls:** no audible gaps at 5% random loss with redundancy in the spare bytes; mouth-to-ear latency within the 150 ms call budget (`PROTOCOL.md` 7.1).
- **Spatial:** AMBIQUAL localisation accuracy at third order no worse than APAC at Apple's recommended rate, measured on the same content.

Measured results go here, with the device, OS build and commit of each run.

## 12. Open questions

1. **Neural speech and R6** (question 97): accept a labelled exception for adversarially trained speech decoders at very low rates, or require decoders trained without adversarial loss and accept lower quality.
2. **Audio-only packet size** (question 98): the fixed QUIC packet size for audio-only calls, or several 20 ms objects per packet, against the latency budget.
3. **AAC export licensing** (question 99): confirm that exporting AAC through Apple's AudioToolbox encoder needs no separate licence from us.
4. **Float lossless** (question 100): add a float lossless codec (WavPack-class) to nu-media, or keep float masters as sample-exact transfers.
5. **Objects** (question 101): object-based spatial audio (ASAF and Atmos style) in nu-media, and how to carry positions without new leaks in calls.
6. **More than 8 lossless channels**: several FLAC streams per track, or one track per FLAC stream.
