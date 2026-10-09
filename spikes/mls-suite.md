# Spike: MLS on ML-KEM-1024 + ML-DSA-87

Date: 9 October 2026. Code: `khensu-core/crates/khensu-mls`. Machine: Apple silicon Mac, release build.

## Result

`MLS_256_MLKEM1024_AES256GCM_SHA512_MLDSA87` works end to end on OpenMLS 0.9.1 with a thin provider; no fork. Create, add with a Welcome that carries no tree, application messages, signature-key rotation by full-path update, rejection of the retired key, removal, and exporter-derived mailbox IDs all pass.

## Measurements

| Item | Size or time |
| --- | --- |
| Welcome (2 joiners) | 8,464 B |
| Ratchet tree, 3 members | 29,889 B |
| Short `PrivateMessage` (11-byte text) | 4,926 B, fits the 3-fragment bucket (6,068 B usable) |
| 100 devices: add all in one commit | 164 ms; tree 877 KB in 14 chunks |
| 100 devices: first full-path update | 77 KB, processed in 36 ms |
| 1,000 devices: add all in one commit | 1.83 s; tree 8.7 MB in 136 chunks |
| 1,000 devices: first full-path update | 813 KB, processed in 341 ms |

## Findings that change the specs

1. **Commit size after bulk adds.** Right after a large add, most parent nodes are blank, so the next update encrypts to nearly every leaf (813 KB at 1,000 devices, about 12 bulk packets). Commits shrink towards about 10 path secrets (~20 KB) as members update. PROTOCOL.md should state the worst case and send commits over the bulk lane when they exceed the small-lane bucket. Groups above 100 devices should add members in batches with an update after each, so the tree fills before it gets large.
2. **Tree download at 1,000 devices is 8.7 MB.** A joiner fetches 136 chunks; on cellular this is a noticeable one-off cost. Mitigation to evaluate: a compact tree encoding that omits parent hashes the joiner can recompute.
3. **Content room in bucket 3** is about 1,100 bytes after the ML-DSA-87 signature and framing, matching the estimate in PROTOCOL.md 5.3.
4. **Time-based skipped-key expiry** (7 days) is not an OpenMLS setting; the app purges past-epoch secrets and skipped keys on a timer.

## Not yet covered

- mlswg interop vectors: the published vectors don't include suite `0x0906`. OpenMLS's own CI runs them for its other suites; we will generate and publish vectors for `0x0906` once the draft codepoint is final.
- iPhone and Pi 5 timings (needs the Swift bindings and the Pi image).
