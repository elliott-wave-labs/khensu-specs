# Stealth relay and media

How khensu.nu's relays and media stack hide what calls, streams and public fetches are doing, without adding latency. Wire rules are in `PROTOCOL.md` 7.1; this document maps them to code.

khensu's relay is an evolution of MOQOM, built in khensu repos from MOQOM's Apache-2.0 crates (`moqom-proto`, `moqom-transport`, `moqom-client`, `moqom-media`, `moqom-security`, and MoqomKit in Swift). None of this goes back into MOQOM, which stays a separate product aimed at replacing Agora or being sold to it. Nothing is copied from the proprietary `moqom-relay` or `moqom-recorder`.

Status: design. Nothing here is implemented yet.

## What it protects

| Observer | Plain MOQOM today | khensu |
| --- | --- | --- |
| Relay | Object sizes and timing (speech activity, scene changes, keyframes); both endpoints' IPs when a direct path is used | Constant-size objects at a constant rate; one relay never sees both IPs |
| Local network or ISP | A MOQ-specific ALPN on port 4443, variable bitrate | What looks like Safari or Chrome talking HTTP/3 to an ordinary website, at a constant rate |
| Relay operator | Whole sessions | Fragments: edge relays rotate at random during every session |
| Global observer | Exact call start, end, duration, and who is talking when | Start and end blurred by random padding; speech patterns hidden. Long-term edge correlation remains |

Variable-bitrate audio leaks speech even when encrypted: published attacks recover spoken phrases from packet sizes alone. Constant bitrate is the core.

## Rules

1. **Constant-rate media.** Each track sends fixed-size objects at a fixed rate for the whole session.

   | Track | Object size | Rate | Encoder |
   | --- | --- | --- | --- |
   | Audio | 160 B | 50/s (20 ms) | Opus CBR 32 kbit/s, DTX off |
   | Video L | 1,200 B | 60/s | constant rate, about 500 kbit/s |
   | Video M | 1,200 B | 160/s | constant rate, about 1.5 Mbit/s |
   | Video H | 1,200 B | 400/s | constant rate, about 3.8 Mbit/s |

   - The encoder targets just under the tier rate; output is split into fixed objects, short frames are padded, empty slots carry padding objects.
   - Padding is inside the SFrame ciphertext, so the relay can't tell padding from media.
   - Video uses periodic intra refresh, never IDR keyframes; keyframe requests trigger a faster refresh sweep at the same rate.
   - Camera off keeps the video track at its tier with padding; mute keeps the audio track running.
   - Tier changes at most every 30 s, adjacent tiers only, with hysteresis.
2. **Relay only.** No direct peer-to-peer over the internet. Direct media only on a local link (same Wi-Fi network or Wi-Fi Aware), with addresses exchanged over the mixnet-delivered setup, never by broadcast or STUN.
3. **Two relays from different operators.** Each side connects to its own nearby relay; the relays connect over a trunk. Different operator, autonomous system and jurisdiction.
4. **Padded trunks.** Relay-to-relay sessions are long-lived, multiplex everything between the two relays (calls, streams, public fetches), and send fixed-size objects at a constant rate sized to the link's capacity class, independent of load.
5. **Edge blurring.** Clients open the relay stream and start padding a uniformly random 2–8 s before media is expected, and keep padding a uniformly random 2–8 s after leaving.
6. **Camouflaged transport.** WebTransport over HTTP/3 on UDP 443, ALPN `h3` only, MOQT negotiated inside. The outer handshake matches current Safari or Chrome, to a node that looks like an ordinary website; the node is authenticated inside with ML-KEM-1024 and ML-DSA-87, bound to the outer session (`design/camouflage.md`).
7. **Group calls and streams.** Relays act as forwarders; every publisher follows rule 1.
8. **Stealth access to public content (webË).** Public content isn't secret, but who reads it is. A fetch goes through two relays like a call: the entry relay knows the reader's IP but not what is fetched (the request is encrypted to the exit relay with ML-KEM-1024); the exit relay or cache knows the object but not the reader. The hop between them rides a padded trunk, and responses are padded to size buckets. Small objects can also ride the stealth ticks.
9. **Relay rotation.** Every participant switches its edge relay at its own random times (mean about 4 minutes, at least 60 s apart), make-before-break with a random padded tail, announced over the trunks. No relay sees a whole session, and participants never switch together.

## Gaps in the MOQOM code khensu starts from

| Rule | MOQOM today | Change in khensu | Where |
| --- | --- | --- | --- |
| 1, audio | Opus at a target rate (VBR); silence shrinks (stub encoder emits 3 bytes) | Opus CBR, DTX off, fixed 20 ms frames, padding objects | `khensu-apple`, from MoqomKit `Platform/PlatformAudioEncoder.swift`, `Publish/AudioEncoder.swift`, `Publish/AudioPublication.swift` |
| 1, video | `AverageBitRate` with `DataRateLimits`, keyframes | Constant-rate mode, intra refresh, fixed-size packetiser with padding | `khensu-apple`, from MoqomKit `Platform/VideoEncoder.swift`, `MoqomCore/Video.swift`; nu-media later |
| 1, padding inside SFrame | SFrame encrypts payload as is | Pad plaintext to the object size before SFrame; strip after decrypt | `khensu-core` (SFrame keys from MLS already live there) |
| 1, pacing | Objects sent as produced | Constant-rate pacer per track | client publish path in `khensu-core`, exposed through UniFFI |
| 2 | Direct paths automatic by default; STUN and hole punching; SNI `moqom-direct` | Relay-only, plus a local-link-only direct mode with no STUN | `khensu-apple`; MoqomKit `Direct/` is not carried over except the local-link parts |
| 3 | Not a policy | Relay selection by operator, AS and jurisdiction from the epoch's node list | `khensu-core` route selection |
| 4 | Edge↔parent links in the proprietary relay; no padding or pacing | Trunk mode: multiplexed, constant-rate, padded | `khensu-tatenan` relay, written fresh on the Apache transport |
| 5 | Absent | Pre-roll and post-roll padding with random lengths | client publish path in `khensu-core` |
| 6 | Default `[::]:4443`; raw-QUIC ALPNs `moqt-22`, `moqt-19`; WebTransport via `h3`; rustls | Listen on 443, offer `h3` only, negotiate MOQT inside WebTransport; camouflage outer stack (Network.framework on Apple, BoringSSL elsewhere) with the inner handshake | `khensu-tatenan`, `khensu-core`, client transport config |
| 9 | Absent | Independent random edge-relay rotation, make-before-break, announced over trunks | `khensu-core` session layer, `khensu-tatenan` relay |
| 8 | Absent | Two-relay encrypted fetch with size buckets | `khensu-tatenan` and `khensu-core` |

## Costs

- Bandwidth: constant rate at the tier, even when silent or still (about 32 kbit/s audio; 0.5–3.8 Mbit/s video).
- Battery: the radio stays fully active for the call, which it largely does anyway.
- Relay capacity: trunks run at their class rate around the clock.
- Latency: none added by padding or pacing beyond one object interval (20 ms audio, 2.5–17 ms video); one extra relay hop for public fetches.

## Tests

- Wire-level: object sizes and inter-object gaps are identical between a silent call and a talking call, and between camera on and off.
- Fingerprint: JA4 and QUIC fingerprints match the current Safari or Chrome capture for the profile; a wrong knock returns the node's normal website response; no STUN traffic.
- Rotation: participants' switch times are uncorrelated; no audio or video gap across a switch.
- Trunk: relay-to-relay byte rate is flat whether 0 or 500 sessions are active.
- Public fetch: the entry relay never sees an object address in the clear; response sizes fall only on bucket boundaries.
- Latency: glass to glass with two relays stays under 150 ms within a region.
