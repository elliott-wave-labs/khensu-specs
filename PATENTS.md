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
