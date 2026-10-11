# Patent assessments

Each component gets an assessment here once it's built, written from the real code and measurements. Each assessment covers what is new compared with published prior art, a prior-art search summary, draft claim themes, and a recommendation: file, publish defensively, or neither. Patent counsel makes the filing decision.

**Disclosure rule.** Publishing the code, the Outfox paper or a detailed public description counts as disclosure. It starts the 12-month US grace period and ends patentability in most other countries. A component's assessment, and any filing, must be finished before its repo goes public or the paper is submitted.

| Component | Repo | Known prior art to compare against | Status |
| --- | --- | --- | --- |
| KhensuMemory: on-device Hindsight-style memory (recall fusion, observations, reflect with citations, derived-data deletion tied to message expiry) | `khensu-core`, `khensu-apple` | Hindsight (MIT, public), retrieval-augmented generation literature, Apple on-device search | Not built |
| Outfox extensions: epoch-bound replay protection, ML-KEM-1024 instantiation, unlinkable work receipts, loop-measurement indistinguishability, mailbox-epoch SURBs | `khensu-core`, `khensu-tatenan` | Outfox (WPES 2025), Sphinx, Loopix, Nym | Not built |
| Rotating message signatures with delayed key reveal | `khensu-core` | OTR MAC-key publication, MLS (RFC 9420), deniable messaging literature | Not built |
| Signed frame manifests for group calls | `khensu-core`, `khensu-apple` | SFrame (RFC 9605), stream-signing and batch-signing schemes | Not built |
| Expiring-era shielded pool with dropped nullifier lists | `khensu-chain` | Zcash, Monero, Penumbra, STARK-based pools | Not built |
| Burn and mint driven by unlinkable work receipts | `khensu-chain` | Helium, Factom, Nym rewards | Not built |
| Reputation-and-stake sortition with loop measurement | `khensu-chain`, `khensu-tatenan` | Algorand sortition, Nym, Tor bandwidth authorities | Not built |
| Lease-based scheduling for idle-time, scheduled and N-hour nodes | `khensu-tatenan`, `khensu-apple` | BOINC, volunteer computing, Tor relay scheduling | Not built |
| Anonymous push wake capabilities with delay and merging | `khensu-services`, `khensu-apple` | Signal and other wake-only push designs | Not built |
| Identity devices with the 72-hour removal window and recovery-kit rotation | `khensu-core`, `khensu-services` | KERI pre-rotation, Keybase sigchains, Signal linked devices | Not built |
| Out-of-band ratchet tree delivery for large post-quantum groups | `khensu-core`, `khensu-tatenan` | RFC 9420 tree extensions, MLS delivery-service designs | Not built |
| Panic wipe (App Intent triggers, duress passcode, crypto-erase) | `khensu-apple` | Duress PIN features in other apps, crypto-erase practice | Not built |
| Mixnet-delivered sharded PIR directory with log proofs and scheduled dummy lookups | `khensu-core`, `khensu-tatenan` | SimplePIR, YPIR, Keybase/KT lookups, Tor directory design | Not built |
| Constant-tick bursts carrying fetch, sends and retries (absolute cover with durable replay) | `khensu-core`, `khensu-apple` | Loopix, Nym clients, constant-rate padding literature | Not built |
| nu-media: progressive learned image delivery inside constant-rate cover; hybrid video with receiver-side Neural Engine enhancement for constant-bitrate calls | `nu-media`, `khensu-apple` | Learned image codecs (HiFiC, ELIC), DCVC family, neural super-resolution | Not built |
| Stealth attachments through the user's own node over the local network | `khensu-tatenan`, `khensu-apple` | Tor bridges, home-relay designs | Not built |
| Stealth call profile: constant-rate fixed-size media, padded relay trunks, edge blurring, two relays per call | `khensu-tatenan`, `khensu-core` | VBR-leak papers (Wright et al.), Tor, Signal relays, MOQ | Not built |
| webE: transparency-log naming, signed content-addressed sites and feeds over MOQ, two-relay stealth fetch | `khensu-tatenan`, `khensu-core`, `khensu-browser` | IPFS, Tor onion services, I2P, Hyphanet, Veilid, Handshake, ENS | Not built |
| Public square: anonymous Sybil-resistant bridging labels computed on every device; threshold pledges with anonymous tallies | `khensu-core`, `khensu-apple` | X Community Notes, Bluesky labelers, assurance contracts | Not built |
| Mesh gossip of a public feed and sealed packets under internet shutdown | `khensu-apple` | Briar, Bitchat, Bridgefy, FireChat, delay-tolerant networking | Not built |
| Places: live 360° and spatial broadcasts pinned to real places, browsed by moving or teleporting on a map, viewport-adaptive delivery over a stealth network | `khensu-apple`, `nu-media`, `khensu-tatenan` | Periscope and Snap Map, Facebook Live Map, NextVR, Meta Horizon venues, Google Street View, viewport-adaptive 360° streaming (MPEG OMAF) | Not built |
| khensu camouflage: browser-identical outer QUIC/TLS (native browser stacks, consensus-distributed profiles) with a channel-bound inner ML-KEM-1024/ML-DSA-87 handshake to directory-pinned node keys and probe-indistinguishable website fallback | `khensu-core`, `khensu-tatenan`, `khensu-apple` | obfs4, meek, Snowflake, uTLS, Trojan, ShadowTLS, REALITY, NaïveProxy, TapDance and Conjure, RFC 9266 channel binding, ECH | Not built |
| Independent random relay rotation during live sessions, make-before-break with padded tails, announced over padded trunks | `khensu-core`, `khensu-tatenan` | Tor circuit rotation, multipath and moving-target defences, QUIC connection migration | Not built |
| khensu guard: a separate chip that owns all radios and enforces fixed-size, fixed-schedule cover with committee-signed parameters, so a compromised host can't break the traffic pattern | `khensu-hardware` (new), `khensu-tatenan` | Red/black separation in government crypto devices (HAIPE), data diodes, hardware traffic shapers, constant-rate padding (Loopix, Nym), TEE network gating | Not built |
| Portal hardware: magnetically attached phone mesh radio bridging a stealth mixnet; public 360° portal pairs on a stealth network | `khensu-hardware` (new), `khensu-apple` | goTenna, Meshtastic devices, Bridgefy, the 2014 Portals art installations, video-wall telepresence | Not built |
