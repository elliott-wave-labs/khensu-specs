# Open questions

Decisions still needed before building, numbered so they can be answered by number. Each has the owner's direction (where given), a recommendation, and a status. Once a question is decided it moves into `PLAN.md` (Decisions), `PROTOCOL.md` and `THREAT-MODEL.md`, and is marked **Decided** here with the date.

Status values: **Open** (no direction yet), **Recommended** (direction given, recommendation written, awaiting confirmation), **Decided**.

Estimates are marked as such and are replaced by measurements as spikes finish.

## A. Scale and network (answered 9 Oct 2026, awaiting confirmation)

### 1. Scale target
- **Direction:** support 10 billion daily active users.
- **Recommendation:** treat this as 10 billion daily active *accounts* (more than the world's population, so it covers personas, several devices and machine accounts), with no central component whose cost grows faster than linearly. Every number below is sized for 10B.
- **Status:** Recommended.

### 2. Cover traffic rate on cellular
- **What it is:** while the app is open, the phone sends dummy packets at a steady pace and real messages replace dummies, so nobody watching can tell when you actually send. A faster pace means better privacy and lower latency (a message waits at most one gap), but more battery and more load on nodes. The old plan used 1 packet every 2 s on Wi-Fi and every 10 s on cellular, to save data. With no data budget, the only reasons left for a different cellular rate are battery and node capacity.
- **Battery.** On cellular, the cost comes from keeping the radio awake, not from the bytes. After each transmission an LTE or 5G modem stays in its high-power state for a carrier-set tail of roughly 5–15 s, so any steady rate faster than about one send every 10 s keeps it awake the whole time the app is open. Published LTE measurements put that at 0.3–1 W, or about 2–7% of an iPhone battery per hour the app is open on cellular (modern modems should be near the low end). Wi-Fi power save costs about 0.5% per hour. Encrypting cover packets costs well under 1% of one CPU core.
- **Recommendation (revised): nodes carry the cover, phones send fixed bursts.**
  - **Nodes** send constant cover between themselves around the clock (node-to-node cover and loop packets on mains power), sized so every link carries a steady rate whatever the real load. This keeps the anonymity set large and costs phones nothing.
  - **Phones** still need a steady pattern on their own link, because node cover can't hide when a phone itself transmits from its carrier or Wi-Fi network. So the phone sends one fixed-size burst per tick: its mailbox fetch plus any outgoing fragments, padded with cover to the same size every time. Fetching has to happen anyway to receive messages, so sending adds almost nothing.
  - **Tick length** depends only on things an observer could learn anyway: 2 s on Wi-Fi, 20 s on cellular (one radio wake per tick), 60 s in Low Power Mode, below 20% battery or when the phone is hot. No cover at all in the background (iOS suspends the app).
  - **Energy governor.** The app measures its own radio and CPU energy on the device. If cover reaches 1.5% of the battery in a day, ticks step down to the Low Power rate until the next day.
  - **Estimated cost:** about 1–2% per hour the app is open on cellular, about 0.5% per hour on Wi-Fi, capped at 1.5% a day by the governor. Typical use of 30–60 minutes a day stays under 1.5%. Device tests in the battery-budget to-do confirm or correct these numbers before launch.
  - **Trade-off:** on cellular a message waits for the next tick, about 10 s on average plus mixing delay. Tick lengths stay tunable consensus parameters.
- **Status:** Recommended (revised for battery). PLAN.md and PROTOCOL.md 8.8 still list older, inconsistent rates; they get fixed in the decisions pass.

### 3. Directory lookups at global scale
- **Direction:** complete global scale at launch; the node delivery system is likely patentable.
- **Analysis (estimate):** a handle database for 10B accounts is about 640 GB (64-byte records). Full-database PIR touches every byte for every query: about 64 core-seconds each. At 0.1 lookups per account per day (about 11,600 per second) that is roughly 7 PB/s of memory scanning, or several hundred thousand machines doing nothing else. No PIR scheme without client-side preprocessing can avoid touching every record, and the preprocessing schemes need each client to stream the whole database once. So full-database PIR at 10B isn't feasible on any fleet.
- **Recommendation:** sharded PIR, which is global at launch because capacity grows linearly with nodes:
  - 1,024 shards by hash prefix, about 10M handles each (about 640 MB, fits a Pi's RAM); each shard served by many mirrors; batched queries.
  - What leaks: a mirror learns "an unknown person looked up one of these 10 million handles". The mixnet hides who asked; scheduled dummy queries (7) hide when.
  - Lookups stay rare: invite links and QR codes carry keys, credentials prove themselves (5), and contacts' key changes arrive inside the conversation.
- **Patents:** mixnet-delivered sharded PIR with log proofs and scheduled dummy lookups goes into `PATENTS.md` as a candidate. The disclosure rule applies: assess before any public description.
- **Status:** Recommended.

### 4. Handle privacy in the log
- **Question:** which is more secure and future-proof, a VRF or hash commitments plus PIR?
- **Answer:** commitments plus PIR. Deployed VRFs (ECVRF, RFC 9381) are elliptic-curve: a future quantum computer could invert archived VRF outputs and list every handle ever registered ("harvest now, enumerate later"). Lattice VRFs exist only in research, aren't standardized, and are large. Hash commitments (`H(handle || address)`) rely only on hash functions, and PIR relies on lattice assumptions (the same family as ML-KEM). Nothing classical is left.
- **Recommendation:** remove the VRF from the plan; the log stores commitments, and PIR mirrors serve handle records.
- **Status:** Recommended.

### 5. MLS credentials
- **Question:** which is more secure and private?
- **Answer:** self-proving credentials. With pointers, every member looks up every other member's log entry, which creates lookups (privacy cost), a dependency on mirrors (availability cost), and a window where a member sees a stale or different answer.
- **Recommendation:**
  - The log keeps a verifiable map (a sparse Merkle tree of each account's current state: identity keys, device keys, revocations), committed in every witnessed checkpoint.
  - Each device holds a proof bundle: its `bind_device_key` entry, the account's current identity key set, and map proofs against a checkpoint no older than 24 hours. Revocation shows up as a failed or missing proof.
  - Bundles travel alongside the group, not inside the ratchet tree: refreshed with every update commit (at most 24 hours apart) and delivered to joiners as extra content-addressed chunks next to the tree. This keeps the tree small (bundles are estimated at 12–17 KB each, which would double a 1,000-device tree if embedded).
  - Revocation takes effect within 24 hours plus the next commit; groups remove a device whose bundle stops verifying.
- **Status:** Recommended.

### 6. First contact
- **Direction:** novel, secure, private, fast, scalable, no footprint, zero trust, post-quantum.
- **Recommendation: recipient-created groups over sealed intro requests.**
  1. Each account's map entry holds an ML-KEM-1024 intro key, signed by an identity device and rotated weekly; the old private key is deleted after a 7-day grace period.
  2. The sender looks up the recipient (sharded PIR), or reads keys from an invite link or QR code (no lookup at all). The sender verifies the map proof against a witnessed checkpoint (zero trust).
  3. The sender seals a request to the intro key containing: its own KeyPackage with its proof bundle, the first message, and a rate-limit proof (anonymous, so no identity or phone number is needed to stop spam).
  4. The request travels through the mixnet to the recipient's intro mailbox: one trip, a few seconds.
  5. The recipient sees a message request. On accept, the recipient's phone creates the MLS group and sends the sender a Welcome. From then on it's a normal MLS conversation with full forward secrecy and post-compromise security.
  - **No footprint:** no server holds KeyPackages, nothing is claimed or deleted on any server, and the sealed request is deleted from the intro mailbox once fetched.
  - **Trade-offs:**
    - The first message is protected by a key that lives up to two weeks, not a per-message key (comparable to Signal's signed prekey); everything after acceptance gets full MLS protection.
    - The recipient keeps a replay cache of request IDs for each intro key's lifetime.
  - **Leak to fix:** anyone who knows a recipient's public intro key can compute their intro mailbox and, by colluding with that mailbox's operators, count how many requests they get per hour (never from whom). Options:
    - cover deposits: clients drop dummy requests into random intro mailboxes as part of scheduled traffic;
    - oblivious message retrieval (lattice-based, post-quantum; nodes detect requests for you without learning which are yours), heavier and research-grade;
    - for invite links and QR codes, a pre-shared rendezvous mailbox with no leak at all.

    Recommended: cover deposits at launch, oblivious message retrieval as a research track.
  - **Patents:** recipient-created groups with sealed intro requests and no server-held KeyPackages is a candidate for `PATENTS.md`.
- **Status:** Recommended.

### 7. Hiding when lookups happen
- **Recommendation:**
  - PIR queries are ordinary mix packets sent in place of cover packets, so the entry node can't tell a lookup from cover traffic.
  - Real lookups go immediately (fast): at 10B users, one extra query in a mirror's aggregate rate is invisible.
  - Each client also sends background refresh queries for its contacts' records on a Poisson schedule while the app is open (mean one every 10 minutes), so per-mirror query volume stays flat.
  - The first-contact request leaves after a random 0–30 s delay, so a lookup and its first message can't be paired by timing.
  - Search never queries the directory while typing; only "Start chat" does.
- **Status:** Recommended.

### 8. SURBs in mailbox fetches
- **Recommendation:**
  - Every fetch carries exactly 8 SURBs, and the mailbox answers all 8, with padding where there are fewer items. An encrypted "more waiting" flag tells the phone to fetch again.
  - Fetches run on the phone's normal schedule (in place of cover packets) and on every push wake.
  - The mailbox learns nothing about how much you expected.
- **Status:** Recommended.

### 9. Mailbox storage
- **Direction:** more secure is best, but people must not lose data unless they chose expiring or view-once content.
- **Recommendation:**
  - **Delivery:** one mailbox per device; an item is deleted when that device acknowledges it. There's no fixed 30/90-day cut-off; undelivered items wait as long as the device is alive (it has checked in within 12 months and isn't revoked in the log).
  - **Expiring and view-once content:** the mailbox TTL equals the content's expiry. View-once items are deleted on the acknowledgement of first open. The client enforces expiry on every device.
  - **Durability:** the store holding history is your devices, so losing all devices loses history unless backed up. To match "no data loss", encrypted backups become free for everyone for text and small media, with larger media quotas on paid tiers. (This changes the pricing table; see 33.)
  - **At scale:** 3 full replicas for small items; Reed–Solomon erasure coding (for example 6-of-9 across distinct operators) for attachments over 1 MB, cutting storage about 2× at the same durability.
- **Status:** Recommended.

### 10. Is a 50,000-Pi network enough?
- **Question:** do we only need 50,000 Pis to power global, untraceable, end-to-end encrypted communications?
- **Answer: not for 10B.** Estimate (to be measured on real Pis):
  - **Per user, per day,** with 1 hour of app-open time:
    - 1,800 small packets (cover plus messages, about 18 MB);
    - about 300 bulk packets (about 22 MB);
    - each packet crosses 5 hops.
  - **Network-wide at 10B DAU:** about 1.2 billion packet-hops per second, about 23 TB/s in and the same out.
  - **One Pi 5 on symmetric gigabit fiber,** limited by bandwidth (the CPU is fine), handles about 3,000 packet-hops per second at full load.
  - **So 10B DAU needs about 400,000 fully used gigabit Pis,** or roughly 1 million with headroom, or about 40,000–100,000 server-class nodes at 10–25 Gbit/s.
  - **50,000 Pis carry roughly 1 billion DAU** at full load with no headroom.
  - **Home connections often upload at 20–50 Mbit/s,** a small fraction of gigabit, so a home Pi carries far less.
- **Encryption doesn't depend on node count:** content is end-to-end encrypted and post-quantum regardless.
- **Untraceability does:**
  - Messages are unlinkable against single nodes, colluding nodes below the threshold, and a global passive observer, as long as cover traffic runs and the network is large.
  - A global *active* adversary is out of scope (`THREAT-MODEL.md`).
  - Live calls can be correlated by a global observer, because they can't take mixnet delays.
- **Biggest levers** (see 30):
  - the cover rate;
  - packet geometry: headers are 8.2 KB of a 10.25 KB small packet, so a bigger small payload carries one message per packet instead of three;
  - the number of hops.
- **Recommendation:**
  - Pi 5 stays the minimum and does every role.
  - The protocol has no ceiling on node count (see 30 for the node-directory problem this creates).
  - Plan capacity per 1B DAU at about 40,000 gigabit Pi-equivalents.
  - Fix packet geometry before freezing `PROTOCOL.md` section 8.
- **Status:** Recommended.

## B. STARKs and payments (open)

11. **Proof system.** Rec: Plonky3 with hand-written circuits, benchmarking Stwo in the spike. Alternatives: Stwo alone; a zkVM (RISC Zero, SP1), easier but much slower. **Open.**
12. **Elliptic-curve SNARK wrap.** Rec: never; proofs of about 100 KB travel on the bulk lane. **Open.**
13. **In-circuit hash.** Rec: Poseidon2 with conservative rounds, swappable per era; alternatives Rescue-Prime or SHA-256 in circuit. **Open.**
14. **Soundness.** Rec: proven 128-bit soundness over conjectured. **Open.**
15. **Spends at scale.** Rec: recursive STARK aggregation, one proof per block covering all spends. **Open.**
16. **Merkle paths.** Rec: tracked locally from public tree updates, PIR as fallback. At 10B, tree depth and per-era sizes need recomputing (depth 34 or more). **Open.**
17. **Access tokens.** Rec: STARK credentials, the same circuit family as payments and rate limits, over lattice blind signatures. **Open.**
18. **Work receipts.** Rec: probabilistic hop tickets in each header layer, only winners redeemed, in batches with STARK proofs (scales to billions of packet-hops per second). Alternatives: all-redeemed per-hop tokens; the current pairwise counts. **Open.**
19. **Tickets on cover packets.** Rec: funded by protocol emission so cover looks like paid traffic. **Open.**
20. **Patent route for burn-and-mint receipts.** Rec: add HOPR, Orchid and the Tor incentive papers (BRAIDS, LIRA, TEARS) as prior art; lean towards defensive publication; counsel decides. **Open.**
21. **Freedom to operate** on HOPR, Nym and StarkWare patents. Rec: before building those parts. **Open.**
22. **STARK spike** (depth-32+ membership plus nullifier; proof size, iPhone proving time, Pi verification time; Plonky3 vs Stwo). Rec: now. **Open.**
23. **`PAYMENTS.md`.** Rec: write draft 0.1 once 11–19 are decided. **Open.**

## C. Dead man's switch (open)

24. **Release delivery.** Rec: a hidden release mailbox; recipients silently told at setup. **Open.**
25. **Re-split on every check-in** to current holders. Rec: yes. **Open.**
26. **Duress passcode triggers the release.** Rec: yes. **Open.**
27. **Defaults.** Rec: 3-of-5 holders, 7-day period; alternative 4-of-7. **Open.**

## D. Process (open)

28. **Build order.** Rec: a vertical slice first (1:1 chat end to end on devnet: app, mixnet, mailbox, log), then widen. Alternative: the to-do list in order. **Open.**
29. **Where decisions go.** Rec: `PLAN.md`, the Cursor plan file, `PROTOCOL.md` and `THREAT-MODEL.md` in one pass once A is confirmed. **Open.**

## E. New questions raised by 10 billion users

30. **Node directory and packet geometry at a million nodes.** A node list of 1M entries at about 9 KB each (ML-DSA key, ML-KEM keys, signature) is about 9 GB; hourly mix keys would multiply that. Clients can't download it, and letting each client know a different subset enables route-fingerprinting attacks. Options:
    - (a) an active set chosen per epoch by consensus, which caps capacity at the active set's size;
    - (b) mixnet zones by hash, each with its own active set (each anonymity set is one zone's users, still hundreds of millions);
    - (c) clients fetch the keys of their chosen hops through PIR, so nobody knows anyone's subset, and reuse a privately chosen subset for a day. This is probably novel.

    Also: rotate mix keys daily instead of hourly (the replay filter grows to about 600 MB on a Pi, which fits), and enlarge the small payload so one signed message fits one packet. Rec: (c) with daily keys, measured against (b). **Open.**
31. **Mixnet bandwidth budget per user.** Set a target (for example, 40 MB per app-open hour) and tune the cover rate, hops and geometry to it. **Open.**
32. **Intro mailbox counting leak** (see 6): cover deposits now, oblivious message retrieval as research. **Open.**
33. **Free encrypted backups for everyone** (see 9), which changes the pricing table and storage costs. **Open.**
34. **Consensus and the chain at 10B.** The 21-member committee and hourly headers are fine. Questions:
    - the size of the account-state map;
    - whether the verifiable map for credentials (5) is committed in epoch headers or only in KT checkpoints;
    - spend throughput (see 15).

    **Open.**
35. **Push gateway at 10B.** It stays one logical service (APNs is tied to our team key), stateless and horizontally scaled across regions; billions of wakes a day is APNs-scale traffic. It's still the one central dependency. **Open.**
36. **Key transparency log at 10B.** About 100 billion entries a year (estimate); inclusion proofs of about 37 hashes; witnesses cosign checkpoints, not entries. The log becomes a sharded, multi-operator log (several logs, one checkpoint each, all witnessed). **Open.**

## F. Housekeeping

37. **`PROTOCOL.md` sections 13 and 14** say "frozen in `PAYMENTS.md`" and "each frozen in its own spec"; those files don't exist yet. Reword to "to be written". **Open.**
38. **Tamarin run:** the first run printed nothing because macOS has no `timeout` command; rerun without it and record results in `formal/README.md`. **Open (mine).**
39. **`PLAN.md` still has the 50 MB cellular budget** and the VRF; both change once 2 and 4 are confirmed. **Open.**
