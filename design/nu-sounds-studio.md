# ñü.sounds studio: instruments in space and time, for musicians and listeners

Status: design, 12 October 2026. Code identifier `nusounds` (`nu.khensu.sounds`). Builds on `nu-audio.md` (profiles, rules A1–A6) and `nu-spatial.md` (separation, placement, ñü.fidelity).

ñü.sounds studio takes a finished song, splits it into its instruments, places them in spatial audio automatically, and lets the artist shape and lock how the song sounds. Listeners can then add their own copies of tracks in space and time without touching the artist's mix. Everything runs on the device; no audio, voice or setting is processed on a server.

## 1. Who does what

| | Artist (owner of the song) | Listener or viewer |
| --- | --- | --- |
| Split into instruments | Yes, automatic, then corrects names and splits by hand | No; hears the artist's split |
| Place tracks in space | Yes | Only their own duplicates |
| Room, reverb, echo, delay, distortion, 8-bit, pedals | Yes, per track and per song | Only on their own duplicates, and only effects the artist leaves unlocked |
| Lock a profile | Yes, per song (2) | No |
| Duplicate tracks | Yes, any number | Yes, any number: duplicates in space and time only (4) |
| Voice effects and "speak as an instrument" | Yes | Yes, on their own voice (5) |
| Stereo, original and ñü.wæve | Chooses the default | Switches freely between them unless locked |

## 2. Locked profiles

A profile is the artist's sound for one song. It's a small document carried inside the song's encrypted `.nu` container and signed by the artist's ML-DSA-87 key, so players can check it hasn't been changed.

Contents:

- **Tracks.** Name, instrument family, position (x right, y ahead, z up, metres), width, gain, mute and solo defaults.
- **Atmosphere.** Room (named venue or ñü.aura's choice), reverb mix, echo length (decay to −60 dB), pre-delay, early reflections, EQ tilt.
- **Effects per track.** Echo (delay time, feedback, mix), distortion (drive, tone, mix), 8-bit (bit depth 1–16, sample-rate reduction, mix), pedal chain (5.2).
- **Default mode.** Original, ñü.wæve, or stereo.
- **Lock map.** One flag per parameter: locked (listeners can't change it) or open. "Lock everything" plays the song exactly as the artist set it.

The player starts every song on its profile. With no profile, it starts on "Match original" (`khensu.nu/sounds`): loudness matched to the original file, measured live, with reverb added on top of the clean instruments.

## 3. Splitting into instruments

### 3.1 Pipeline

1. **First pass.** A source-separation model (htdemucs 6-stem today, Demucs is MIT-licensed) gives drums, bass, piano, vocals, and two catch-all stems. The labels of the catch-alls are not trusted: on First Attempt the model's "guitar" and "other" stems hold strings and winds, and the song has no guitar or synth.
2. **Families.** Catch-alls are split further: strings by register (cello below about 260 Hz fundamental, viola about 130–1,000 Hz, violin above about 200 Hz, with overlap resolved by pitch tracking), and drums into kit pieces (kick, snare, toms, hi-hat and cymbals) with a drum-separation model (candidate: drumsep, licence to check).
3. **Many takes of one instrument.** Orchestral parts recorded as many tracks (First Attempt layers several violin, viola and cello takes) can't be fully pulled apart from a stereo mix. The studio gives one track per family and register and labels it "violins (several takes)". Exact takes need the artist's original project files, which the studio imports directly (GarageBand, Logic and stem WAVs).
4. **Winds.** Separating winds from strings in a mix is an open research problem. Until a model passes the gates in 7, winds stay in a "winds and strings" track the artist can rename.
5. **Artist correction.** The artist renames tracks, merges them, or splits one by drawing a frequency or time region.

### 3.2 Clean tracks

Separated tracks are kept clean: no added room, no noise reduction artefacts added back. Room and effects are applied on top at playback, so "Clean" always means the separated track as it is.

## 4. Duplicates in space and time

Any track can be duplicated any number of times. A duplicate shares the original's audio (no extra download) and has its own:

- **Place.** Position, and an optional path through space over the song (keyframes with ease in and out).
- **Time.** An offset (earlier or later, to the millisecond), and a speed map: keyframes at timecodes, each with a speed (0.25× to 4×) and how quickly it gets there (velocity, as an ease curve). Pitch follows speed by default, like tape; "keep pitch" uses time-stretching.
- **Sound.** Gain, and the effects the artist left open.

Viewers can only create duplicates. They can't move, mute or change the artist's tracks, and their duplicates live only on their own device unless they share them as a remix the artist allows. A shared remix is a list of duplicates (track, place, time map, effects), a few kilobytes, never a new copy of the audio.

## 5. Voice

### 5.1 Voice modulation

On the device, live and in recordings: pitch shift (±24 semitones), formant shift (independent of pitch), robot, whisper, and harmoniser (up to four voices). Used in calls and live rooms only when the person turns it on, and labelled for the other side as "voice effect on" (`nu-audio.md` A4: nothing is added that the speaker didn't choose).

### 5.2 Guitar pedals on voice

A pedalboard for any track or a live voice: overdrive, fuzz, distortion, compressor, wah, chorus, flanger, phaser, tremolo, octaver, delay and spring reverb, in any order.

### 5.3 Speak as an instrument

- **Play it.** The voice is pitch-tracked (YIN-style, on device), each syllable becomes a note with its loudness envelope, and a piano, violin, cello or flute model plays the melody of the speech.
- **Sound like it.** Cross-synthesis: the instrument is the carrier and the voice shapes it (a vocoder), so the words stay understandable but sound bowed or struck.

## 6. Formats and sizes

### 6.1 First Attempt, measured 12 October 2026

All three are 400.06 s (6:40). Fidelity is measured against the original 2008 file, decoded and level-matched, after time alignment, mono.

| | Original 2008 | Lossless (FLAC of the original) | Opus 5.1 (old upmix) | ñü.wæve today |
| --- | --- | --- | --- | --- |
| Codec | AAC-LC | FLAC, level 12 | Opus | Opus, one stream per instrument |
| Channels | 2 (stereo) | 2 | 6 (5.1, fixed speakers) | 5 mono objects, placed in 3D |
| Sample rate | 44.1 kHz | 44.1 kHz, 16-bit | 48 kHz | 48 kHz |
| Size | 9.6 MB | 28.6 MB | 13.0 MB | 9.1 MB |
| SNR against the original | reference | bit-exact | 18.6 dB | 15.6 dB |
| Spectral distance (lower is better) | 0 | 0.7 dB | 12.0 dB | 19.3 dB |

What this says:

- **Lossless is the ceiling.** FLAC is bit-exact, so no format can be more faithful to the 2008 file than lossless. "Better than lossless" can only mean more you can do with it (instruments, space, time) or smaller, never closer to the source.
- **ñü.wæve today is smaller but not yet as faithful as Opus 5.1.** It's 30% smaller than Opus 5.1 and 3.1× smaller than FLAC, but separation leaks between instruments, mono objects lose the original's stereo picture, and the instruments run at 20–48 kbit/s each.
- **A lossless correction layer doesn't pay off yet.** Coding the difference between the instruments and the original as FLAC (so the original can be rebuilt exactly) takes 28.7 MB on its own, because today's mono, low-rate instruments capture only 6.5 dB of the original's energy.

These are interim measures. The spec's score is ñü.fidelity (`nu-spatial.md` 5, ViSQOL v3 against the master), which needs ViSQOL built from source; it replaces SNR and spectral distance here once it runs.

### 6.2 Targets

| Target | Measure | Status |
| --- | --- | --- |
| Smaller than Opus 5.1 | Size | Met: 9.1 MB against 13.0 MB |
| Twice Opus 5.1 | Transparent size at ñü.fidelity 95 is half Opus 5.1's (`nu-spatial.md` 5.3) | Not met; needs stereo objects and `nu_music_v1` |
| Lossless and smaller than FLAC | Instruments plus correction layer rebuild the original bit-exactly in less than FLAC's size | Not met; correction layer is FLAC-sized today |
| 10× smaller than FLAC at transparent quality | 2.9 MB for 6:40 at ñü.fidelity ≥ 95 | Research target |

### 6.3 How to get there

1. **Stereo objects.** Each instrument keeps its own stereo image (mid plus side), so the room and width in the recording survive.
2. **Separation residual.** The part of the mix no instrument claimed travels as its own small track, so instruments plus residual sum back to the original.
3. **Shared prediction.** The correction layer predicts from all decoded instruments at once (per band, not five fixed weights), then codes only what's left.
4. **`nu_music_v1`.** The Neural Engine codec (`nu-spatial.md` 4) for each object, rated by ñü.fidelity, not kbit/s.

Each step is measured on First Attempt and the benchmark set before any number appears on a page.

## 7. Gates

- A separated track is labelled with an instrument name only if listeners in a blind test name it correctly at least 80% of the time.
- A size or quality claim on a page needs the measurement in 6, run on the published files, with the date.
- No effect, profile or duplicate is processed or stored on a server.

## 8. Patent assessment

Candidate claims: viewer-only duplicates that share the source audio and carry a place, a time offset and a speed map with per-keyframe velocity; signed per-song profiles with a per-parameter lock map; a lossless correction layer predicted from spatial instrument objects. Prior art to search: object-based audio (MPEG-H, Dolby Atmos ADM), stem players (Stems, Spotify's karaoke and stem features), DJ time-stretch and tempo maps. Assessment goes in `PATENTS.md` once built.

## 9. Open questions

- Winds-versus-strings separation: which model, and does it pass the 80% naming gate on First Attempt?
- Should the artist's profile be able to forbid duplicates for a song?
- Remix sharing: does a shared remix pay the artist per play like the song itself (1¢ a play), and does the remixer get anything?
