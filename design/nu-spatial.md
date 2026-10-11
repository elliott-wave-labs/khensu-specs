# ñü.spatial: automatic spatial mixing, the nu-audio Neural Engine codec and the ñü.fidelity marker

How khensu.nu turns stereo music into a spatial mix on the listener's or artist's own device, codes music and spatial beds on the Neural Engine at half the size of the best Opus for the same fidelity, and rates audio by what you hear instead of by kbit/s.

Status: design, 11 October 2026. **Nothing here is built or measured.** Every quality, size and efficiency figure for ñü.spatial, `nu_music_v1` and ñü.fidelity is a **design target**; figures for Opus, AAC, APAC, Dolby Atmos, ViSQOL and the neural codecs are **estimates** from public material unless a measurement is cited. Section 9 is the benchmark that replaces them. This extends `design/nu-audio.md` (profiles, rules A1–A6, constant-rate carriage, and 7.4, auto spatial with `nu_upmix_v1`) and `design/nu-media-protocol.md` (container, registries). Section 7.4 of `nu-audio.md` is the base pipeline (separate, keep it whole, place, encode, render); this document adds venue-aware placement on top of it as `nu_upmix_v2`, plus range, the codec and the marker. Open questions are in section 11 and `OPEN-QUESTIONS.md` 101.

## 1. What it does

| Feature | Who gets it | Where it runs |
| --- | --- | --- |
| Auto spatial mixing of stereo and mono music (`nu_upmix_v1` in `nu-audio.md` 7.4; venue-aware `nu_upmix_v2` here) | Akashic subscribers (`PLAN.md`, Pricing) | The listener's own iPhone, iPad or Mac, at play time; or the artist's own devices, at publish time |
| `nu_music_v1`, the nu-audio Neural Engine codec | Everyone, once it passes the gates in 9.4 | Encoder on the sender's device, decoder on every receiver |
| ñü.fidelity, the quality marker | Everyone | Measured in the benchmark; shown wherever a bitrate used to be |

- **Akashic only.** Auto spatial is an Akashic entitlement, alongside Akashic upscaling. The entitlement is checked on the device with StoreKit 2; the network never learns who subscribes (section 7).
- **Only when there's no spatial mix.** If a track already carries an ambisonic bed, a channel bed (5.1 and up) or a `binaural` flag (`nu-audio.md` 7.1), the artist's mix plays as it is. Auto spatial applies only to mono and stereo tracks.
- **Always labelled, always reversible.** An auto mix is shown as "Auto spatial · Akashic" with the venue it chose. The original stereo is one tap away, and the listener can pick a different venue or turn auto spatial off.
- **Artists decide.** A track's `spatial_policy` of `no_auto` (`nu-audio.md` 7.4) turns auto spatial off for that track. An Akashic artist can publish an auto spatial mix of their own track as an extra, labelled rendition next to the stereo original. Listener-side auto spatial is display-only (A3): never stored, published or shared.

## 2. Pipeline

Everything runs on the device's Neural Engine, GPU and CPU. Nothing is sent to a server: no Siri, no Private Cloud Compute, no cloud model (fixed decision in `AGENTS.md`).

```
stereo track ─► analysis ─► venue choice ─► separation + keep it whole ─► placement ─► room ─► 3rd-order ambisonics ─► Apple renderer + head tracking ─► AirPods
                (2.1)        (2.2)           (2.3, nu-audio 7.4 stages 1–2)  (2.4)        (2.5)   (2.6)
```

### 2.1 Analysis

- **Sound classification.** Apple's SoundAnalysis framework (`SNClassifySoundRequest` with the built-in classifier, about 300 sound labels) runs over the whole track in 3-second windows on the Neural Engine. Its labels (crowd, applause, cheering, electric guitar, drum kit, synthesizer, orchestra, choir, acoustic guitar, piano, reverberation and so on) are averaged into a track profile.
- **Room acoustics.** `nu_venue_v1`, our Core ML model, estimates the recording's reverberation time (RT60), direct-to-reverberant ratio, early-reflection density, stereo width, crest factor and the presence of an audience. It is trained on open impulse-response libraries (OpenAIR, licence per response) convolved with dry stems (MUSDB18-HQ, for research only, to confirm for shipping weights) and on recordings with known venues.
- **Music features.** Tempo, beat strength, loudness range (EBU R128), spectral balance and the bass share below 120 Hz, from Accelerate (vDSP).

### 2.2 Venue choice with Apple Intelligence

- **What Apple Intelligence does here.** The on-device Foundation Models framework (iOS, iPadOS and macOS 26) takes a short text summary of 2.1 (the top sound labels with confidences, the room estimates, tempo, loudness range and the track's genre tag if the artist set one) and returns a structured venue choice through guided generation (`@Generable`), with a confidence and a one-line reason shown to the listener ("Crowd noise, long reverb and orchestral strings: concert hall").
- **What it doesn't do.** The on-device Foundation Model takes text and images, not audio, so the listening itself is done by SoundAnalysis and `nu_venue_v1`; the language model only reasons over their results. It is never allowed to fall back to Private Cloud Compute. If Apple Intelligence is off or unavailable, a fixed decision tree over the same features picks the venue.

| Venue | Typical signals | Size and reverb |
| --- | --- | --- |
| Concert hall | Orchestra, choir, piano, long natural reverb, wide dynamics | 1,800–2,200 seats, RT60 about 2.0 s, strong late reverb from the sides, rear and above |
| Small room | Solo voice, acoustic guitar, piano, dry recording, little crowd | Studio or living room, RT60 about 0.3–0.5 s, close early reflections |
| Rock club | Distorted guitars, drum kit, bass, shouted vocals, crowd | 300–800 people, RT60 about 0.8–1.2 s, low ceiling, strong first reflections |
| EDM festival | Synthesizer, four-on-the-floor kick, sub-bass, crowd, risers | Open-air main stage, large PA, long diffuse tail, wide image |
| Cathedral (later) | Choir, organ, chant, very long reverb | RT60 3–6 s |
| Open air (later) | Field recordings, folk, birdsong | Little reverb, ground reflection only |

### 2.3 Separation into instruments

Stages 1 and 2 of `nu-audio.md` 7.4 unchanged: `nu_sep_v1`, our own convolution-only separation network on the Neural Engine, splits the mix into vocals, drums, bass, other instruments and ambience, and the mixture-consistency projection makes the stems sum back to the original stereo to within −90 dBFS. HT-Demucs is the comparison point, not the product. `nu_upmix_v2` keeps the same stems and adds a guitars and keys split inside "other" only if `nu_sep_v1` reaches the 7.4 quality gate for those stems too.

### 2.4 Placement by instrument and by frequency

Each stem is split into four bands with linear-phase crossovers, and each band is placed separately, because our ears locate sound differently at different wavelengths.

| Band | Range | Placement rule | Why |
| --- | --- | --- | --- |
| Low | Below 120 Hz | Centre and LFE, mono, never moved | Wavelengths over 2.8 m: ears can't locate them, and moving them only smears the kick and bass |
| Low-mid | 120 Hz–1.5 kHz | At the stem's position, normal width | Timing differences between the ears locate this band |
| High-mid | 1.5–6 kHz | At the stem's position, slightly narrower and closer | Level differences and the outer ear locate this band; keeps vocals and attacks sharp |
| Air | Above 6 kHz | Wider and raised 10–20° | Outer-ear cues for height; gives the room its sense of space |

| Venue | Vocals | Drums | Bass | Guitars (within other) | Keys and pads (within other) | Room and ambience stem |
| --- | --- | --- | --- | --- | --- | --- |
| Concert hall | Centre, 6 m | Rear of stage, ±20°, 9 m | Centre-left, 8 m | ±35°, 7 m | ±60°, 7 m, wide | Hall reverb from every direction, rear and height louder |
| Small room | Centre, 1.5 m | ±25°, 2.5 m | Centre, 2 m | ±30°, 2 m | ±40°, 2.5 m | Short room, early reflections only |
| Rock club | Centre, 3 m | ±30°, 4 m, overheads raised | Centre, 4 m | Left −45° and right +45°, 3.5 m | ±70°, 4 m | Low ceiling, strong first reflections, crowd behind |
| EDM festival | Centre, raised 10°, 8 m | Kick centre; hats and claps ±40° | Centre and LFE | ±50° | Wrap 360°, slow rotation on risers and breakdowns | Huge diffuse tail, PA delay towers behind |

The artist's own stereo panning is kept as an offset inside each stem's position, so a guitar panned hard left stays to the left.

### 2.5 Room

Each venue has a third-order ambisonic impulse response (measured where licences allow, otherwise generated with a geometric and diffuse model). Stems are convolved with it on the GPU with partitioned convolution; the wet level follows the venue table and is lowered if the recording already has long reverb (from 2.1), so the room isn't doubled.

### 2.6 Output and rendering

- The mix is built as third-order ambisonics (16 channels, AmbiX) with the LFE kept separate, then handed to Apple's spatial renderer (AVAudioEngine's environment node or PHASE; to choose in the spike) with the listener's Personalized Spatial Audio profile and head tracking from `CMHeadphoneMotionManager`. Head pose never leaves the device (`nu-audio.md` A6).
- Playback without AirPods: a binaural render for any headphones, or speaker virtualisation on iPhone, iPad and Mac speakers.
- A published auto mix (artist side, 1) is stored as a third-order ambisonic track coded with `nu_music_v1`, or with Opus family 3 until it passes the gates.

### 2.7 Fidelity rules

These extend `nu-audio.md` A1–A6.

| Rule | Statement |
| --- | --- |
| S1 Nothing invented | Auto spatial moves and places what's in the recording and adds a room. It never generates notes, voices or instruments. Before the room, folding back to stereo returns the original to within −90 dBFS (`nu-audio.md` 7.4, stage 2); any window that fails plays as plain stereo |
| S2 Labelled | Every auto mix carries `auto_spatial` metadata (venue, model versions, confidence) inside the encryption and is shown as "Auto spatial · Akashic" |
| S3 Artist's mix first | A native spatial mix is never replaced. Evidence mode and lossless playback never auto-mix |
| S4 Local | Listener-side auto mixes are display-only (A3): rendered on the device, never stored, exported, published or shared |
| S5 Deterministic | The venue decision is cached per track and made with greedy decoding, so the same track always gets the same venue and placement unless the listener changes it (`nu-audio.md` 7.4 publishes a fixed placement table; `nu_upmix_v2` publishes one table per venue) |

## 3. Range

- **What people hear.** Human hearing reaches about 20 Hz–20 kHz at best, and the top falls with age. Content above 20 kHz can't be heard; claims that it changes how music feels (the "hypersonic effect", Oohashi et al. 2000) haven't been reliably reproduced.
- **What AirPods receive.** AirPods over Bluetooth get 48 kHz audio (bandwidth up to 24 kHz). AirPods Max over USB-C get lossless 24-bit, 48 kHz. Nothing above 24 kHz reaches AirPods, so ñü.spatial never synthesises ultrasonic content: it would cost bytes and nobody could hear it.
- **What we extend.** Many sources are band-limited by old lossy encoding (the GarageBand demo on the ñü.sounds page is AAC at about 190 kbit/s and cuts off well below 20 kHz). `nu_bwe_music_v1`, a Neural Engine bandwidth extension, restores the band up to 24 kHz on the receiver. Under `nu-audio.md` A3 it's display-only and labelled, never fed back into decoding or exported as if received.
- **What we keep.** When the source has real content above 24 kHz (96 kHz and 192 kHz masters), the lossless tier keeps it bit-exact (`nu-audio.md` 6) for wired playback and archives. `nu_music_v1` codes up to 24 kHz.

## 4. `nu_music_v1`: the nu-audio Neural Engine codec

### 4.1 Goal

Same or better ñü.fidelity (section 5) than the best Opus at **half the bytes or fewer**, for stereo, 5.1, 7.1.4 and third-order ambisonics. "Best Opus" means the newest libopus release (1.5 at the time of writing) at the lowest rate that reaches the same ñü.fidelity, found by a rate sweep for each test item and layout. APAC and AAC are measured as well where an encoder is available.

### 4.2 Design

| Part | Choice | Why |
| --- | --- | --- |
| Transform | Learned analysis and synthesis transform on 20 ms frames (48 kHz), initialised from an MDCT | Gains over a fixed MDCT come mostly from adapting to the signal |
| Spatial redundancy | Joint coding of all channels with a learned inter-channel transform (ambisonic orders and channel beds) | Opus codes multichannel as coupled stereo and mono streams; the 16 channels of third-order ambisonics are highly correlated, so this is where the largest saving is expected |
| Perceptual model | Learned masking model trained against listening-test scores, not a fixed psychoacoustic model | Spends bits where people hear them |
| Entropy coding | Arithmetic coding with a neural context model (hyperprior plus autoregressive context over time, frequency and channel) | Typically the largest single gain in learned compression |
| Decoder | Deterministic and non-generative: no GAN, no diffusion, no sampling. Integer (fixed-point) inference, bit-exact on every device | Satisfies A4 (nothing invented) and lets provenance hashes (`design/nu-provenance.md`) match across devices |
| Hardware | Encoder and decoder on the Apple Neural Engine; a bit-exact integer reference decoder in Rust in `khensu-core` (CPU, WebAssembly) for Android, the web and verification | "TPU codec" in practice: the Neural Engine is the phone's tensor processor |
| Live carriage | Constant rate in fixed-size objects (A1) for every live tier; constrained VBR only in stored files | No leak through packet sizes |

### 4.3 Honest risk

- Neural codecs published so far (SoundStream, EnCodec, Descript Audio Codec) win clearly at low rates but are not reliably transparent for music at any rate, and their GAN-trained decoders break A4. Halving Opus at transparency with a deterministic decoder is an open research target, not an engineering certainty.
- Separation (2.3) doesn't make coding cheaper: six stems cost more bits than one mix. `nu_music_v1` codes the finished bed, not the stems.
- If `nu_music_v1` misses the 9.4 gates, ñü.sounds ships Opus (stereo and channel beds) and Opus family 3 (ambisonics), and this section is rewritten with the measured results.

## 5. ñü.fidelity: rating sound by what you hear

kbit/s says how many bits were spent, not how good the result sounds: a better codec sounds the same with fewer bits. khensu.nu stops showing kbit/s as a quality measure for audio. The network still uses rates internally (object sizes, `nu-audio.md` 3), but people see ñü.fidelity and the size.

### 5.1 Definition

- **ñü.fidelity (F), 0–100.** 100 means indistinguishable from the master under the test conditions.
- **Stereo and mono.** F = 100 × (MOS − 1) / (4.73 − 1), clipped to 0–100, where MOS is the ViSQOL v3 audio-mode score (Google, Apache-2.0) of the decoded file against the master at 48 kHz. 4.73 is ViSQOL's ceiling in audio mode (estimate, to confirm with the pinned version).
- **Spatial.** The master and the decoded bed are both rendered binaurally with the same open HRTF set (SADIE II, licence to confirm) at eight head orientations (yaw 0° to 315° in 45° steps, level), ViSQOL is computed for each binaural pair, and F is the **lowest** of the eight, so a codec can't hide damage behind the listener.
- **Calibration.** F is checked against MUSHRA listening tests (ITU-R BS.1534-3) with trained listeners; "transparent" is the F at which listeners can't pick the coded file in ABX tests at p < 0.05, expected near F 95 (to be measured).

### 5.2 What people see

| Instead of | People see |
| --- | --- |
| "256 kbit/s" | "ñü.fidelity 97 · 12 MB for 6:40" |
| "Lossless, 1,411 kbit/s" | "Lossless · bit-exact · 44.1 kHz, 16-bit" |
| Codec comparisons in kbit/s | Size per minute at F 95 ("transparent size"), and F at a fixed size |

### 5.3 The efficiency marker

**Transparent size (TS):** megabytes per minute needed to reach F 95 for a given layout and test set. The target for `nu_music_v1` is

TS(best Opus) / TS(`nu_music_v1`) ≥ 2

for stereo, 5.1 and third-order ambisonics separately, with no single test item below 1.5. That's what "double the current Opus 5.1 best" means in this spec.

## 6. Where it appears

- **ñü.sounds page (`khensu-site`).** The spatial player shows the format and size, not kbit/s, and describes auto spatial as an Akashic feature in development.
- **khensu.nu app (`khensu-apple`).** A Sounds settings row "Auto spatial (Akashic)" with a venue override; the now-playing screen shows the chosen venue and an "Original" toggle.
- **Artist upload.** Akashic artists see "Add an auto spatial mix" with a preview on their own device before publishing.

## 7. Privacy and security

- All analysis, separation, mixing, coding and rendering happen on the user's devices. No audio, features, venue choices or head pose leave the device, except a published auto mix, which is a normal encrypted track (`nu-media-protocol.md`).
- Models (`nu_venue_v1`, `nu_sep_v1`, `nu_bwe_music_v1`, `nu_music_v1`) ship inside the signed app, are listed with their hashes in the release manifest archived on the network (`PROTOCOL.md` 12.5), and never download code at run time.
- The Akashic entitlement is checked locally with StoreKit 2. Playback over the mixnet looks the same for every tier; an Akashic listener's traffic isn't distinguishable from anyone else's.
- The listener-side auto mix uses no network at all, so it adds nothing to traffic analysis.

## 8. Platforms

| Platform | Auto spatial | `nu_music_v1` decode |
| --- | --- | --- |
| iPhone 15 Pro and later, iPad and Mac with M1 and later, iOS/iPadOS/macOS 26 | Yes (Neural Engine) | Neural Engine |
| Older Apple devices on 26 | No (too slow to separate in real time); plays the stereo original | Rust integer decoder on the CPU |
| Web (ñü.sounds page) | No; the page plays artist and demo mixes as delivered | Opus and AAC fallback until a WebAssembly decoder ships |

## 9. Benchmark plan

### 9.1 Test material

- EBU SQAM (free for testing), MUSDB18-HQ (research licence) for separation, licensed multichannel and ambisonic music, and khensu-owned recordings such as the ñü.sounds demo.
- Live-recorded venue references: the same performance recorded in a hall, a club and a small room where possible.

### 9.2 Measurements

- ñü.fidelity for every codec and rate (5.1), on stereo, 5.1, 7.1.4 and third-order ambisonics.
- Transparent size (5.3) for Opus 1.5, AAC (AudioToolbox), APAC (where an encoder exists) and `nu_music_v1`.
- Venue choice accuracy against labelled tracks; separation quality (SDR on MUSDB18-HQ); fold-down error (S1).
- Speed and energy on iPhone 17 Pro, iPhone 15 Pro, M1 MacBook Air and M4 Mac mini.

### 9.3 Listening tests

MUSHRA (ITU-R BS.1534-3) and ABX with at least 20 trained listeners, on AirPods Pro, AirPods Max and studio headphones, blind to codec and venue.

### 9.4 Gates

| Gate | Pass |
| --- | --- |
| Efficiency | TS(best Opus) / TS(`nu_music_v1`) ≥ 2 per layout, no item below 1.5 |
| Transparency | No ABX discrimination at p < 0.05 at the shipped size |
| Determinism | Bit-exact decode across Neural Engine, Rust CPU and WebAssembly decoders on every test item |
| Auto spatial preference | MUSHRA preference over the stereo original for at least 70% of listeners on the venue-matched set; no item rated worse than the original by more than 10 points |
| Fold-down | Auto mix folded to stereo within −90 dBFS of the original before the room (`nu-audio.md` 7.4) |
| Venue | At least 85% agreement with labelled venues |
| Speed | The `nu-audio.md` 7.4 budgets (20× real time, under 2.5 s to sound, under 150 mW, model under 40 MB), plus venue analysis under 3 s per track; `nu_music_v1` decode under 5% of one performance core on iPhone 15 Pro |

## 10. Patent assessment

| Candidate | Prior art to search | Assessment |
| --- | --- | --- |
| Venue-classified automatic spatial upmix: on-device sound classification and room-acoustic estimation, reasoned by an on-device language model into a venue, driving stem-wise and band-wise placement with a venue room | Stereo upmixers (Dolby, Apple "Spatialize Stereo", Sony 360 Reality Audio tools, AudioShake, Masterchannel), genre-adaptive upmix papers, Demucs | The combination of a language-model venue decision with band-wise stem placement may be narrow but novel; search first |
| Worst-orientation binaural ViSQOL as a spatial fidelity marker shown to users in place of bitrate | ViSQOL, PEAQ, AMBIQUAL, spatial-audio quality papers | Likely a published method more than a patent; publish it as a spec |
| Deterministic integer neural codec for ambisonic beds with joint inter-channel coding inside constant-rate encrypted objects | EnCodec, SoundStream, DAC, learned image codecs with integer inference, MPEG-H 3D Audio | Possibly patentable in combination with constant-rate carriage; depends on results |

Per the publishing rule, this design is published now and never held for a filing.

## 11. Open questions

1. Which on-device renderer (AVAudioEngine environment node, PHASE or APAC rendering) gives the best head-tracked result for 16-channel beds.
2. Licences for impulse responses and for the venue training set (`nu_sep_v1` is trained only on data we hold rights to, `nu-audio.md` 11.2).
3. Whether `spatial_policy` should also let an artist lock a venue for their track.
4. Whether ñü.fidelity should also show a loudness-normalised figure, and how to rate lossless (always 100 by definition).
5. The exact ViSQOL version, HRTF set and orientations pinned for ñü.fidelity v1.

## Changelog

- 11 October 2026: first version.
