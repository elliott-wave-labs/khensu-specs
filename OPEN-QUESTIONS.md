# Open questions

Decisions still needed before building, numbered so they can be answered by number. Each has the owner's direction (where given), a recommendation, and a status. Once a question is decided it moves into `PLAN.md` (Decisions), `PROTOCOL.md` and `THREAT-MODEL.md`, and is marked **Decided** here with the date.

Status values: **Open** (no direction yet), **Recommended** (direction given, recommendation written, awaiting confirmation), **Decided**.

Estimates are marked as such and are replaced by measurements as spikes finish.

## A. Scale and network (answered 9 Oct 2026, awaiting confirmation)

### 1. Scale target
- **Direction:** support 10 billion daily active users.
- **Recommendation:** treat this as 10 billion daily active *accounts* (more than the world's population, so it covers personas, several devices and machine accounts), with no central component whose cost grows faster than linearly. Every number below is sized for 10B.
- **Status:** **Decided** 9 Oct 2026: 10B daily active accounts at launch, and the design must keep scaling beyond that.

### 2. Cover traffic rate on cellular
- **What it is:** while the app is open, the phone sends dummy packets at a steady pace and real messages replace dummies, so nobody watching can tell when you actually send. A faster pace means better privacy and lower latency (a message waits at most one gap), but more battery and more load on nodes. The old plan used 1 packet every 2 s on Wi-Fi and every 10 s on cellular, to save data. With no data budget, the only reasons left for a different cellular rate are battery and node capacity.
- **Battery.** On cellular, the cost comes from keeping the radio awake, not from the bytes. After each transmission an LTE or 5G modem stays in its high-power state for a carrier-set tail of roughly 5–15 s, so any steady rate faster than about one send every 10 s keeps it awake the whole time the app is open. Published LTE measurements put that at 0.3–1 W, or about 2–7% of an iPhone battery per hour the app is open on cellular (modern modems should be near the low end). Wi-Fi power save costs about 0.5% per hour. Encrypting cover packets costs well under 1% of one CPU core.
- **Recommendation (revised): nodes carry the cover, phones send fixed bursts.**
  - **Nodes** send constant cover between themselves around the clock (node-to-node cover and loop packets on mains power), sized so every link carries a steady rate whatever the real load. This keeps the anonymity set large and costs phones nothing.
  - **Phones** still need a steady pattern on their own link, because node cover can't hide when a phone itself transmits from its carrier or Wi-Fi network. So the phone sends one fixed-size burst per tick: its mailbox fetch plus any outgoing fragments, padded with cover to the same size every time. Fetching has to happen anyway to receive messages, so sending adds almost nothing.
  - **Tick length:** 2 s on every network and in every power state (decided in 2a). No cover at all in the background (iOS suspends the app).
  - **Estimated cost at a 2 s tick:** about 2–7% battery per hour the app is open on cellular (the radio never sleeps while open) and about 0.5% per hour on Wi-Fi, with no cap. The app still measures its own energy use on the device, for reporting only. Device tests in the battery-budget to-do confirm or correct these numbers before launch.
  - **Trade-off:** on cellular a message waits for the next tick, about 10 s on average plus mixing delay. Tick lengths stay tunable consensus parameters.
- **Decided 9 Oct 2026:**
  - Protection against a global passive observer is required; on-demand-only sending is rejected, and there is no setting to switch to it.
  - Nodes carry constant cover between themselves; phones send one fixed burst per tick while the app is open, and every real send rides a tick.
  - No battery cap: the energy governor is removed so cover never degrades.
- **Still open:** the cellular tick length (2a below).
- **Status:** Partly decided. PLAN.md and PROTOCOL.md 8.8 still list older, inconsistent rates; they get fixed in the decisions pass.

### 2a. Cellular tick length
- **Question:** 2 s on cellular, the same as Wi-Fi, or a longer tick?
- **What changes:** cover quality is the same at any fixed tick, because the pattern never depends on what you do. The tick sets latency and battery: at 2 s the cellular radio never sleeps while the app is open (estimated 2–7% battery per hour open); at 20 s it wakes once per tick (estimated 1–2% per hour) and a message waits about 10 s on average.
- **Status:** **Decided** 9 Oct 2026: 2 s ticks on every network. Messages should feel real-time; a delay of one to a few seconds across tick and hops is acceptable. No exceptions: the tick stays at 2 s in Low Power Mode, at low battery and when the phone is hot.

### 2b. Attachments and the cover pattern
- **Problem:** the small-lane tick carries about 2 KB per 2 s, far too slow for photos and video. Sending bulk data faster than the tick shows an observer of the phone's link that something large moved. Hiding bulk transfers in time with real-time speed would need every phone to stream several hundred KB/s around the clock while the app is open (about 1 GB per hour), which no phone or 10B-user network can carry.
- **Recommendation (two modes):**
  - **Default (fast):** an observer can see that the phone moved a large amount of data, but not to whom, when the message was sent, or the exact size.
    - Uploads start as soon as an attachment is picked, before send; the message itself (key and hash) rides a normal tick, so upload time is not send time.
    - Attachments are padded to size buckets (powers of two above 64 KB), erasure-coded, and sent as bulk packets through the mixnet with mixing delays, so no node can link upload to recipient.
    - Phones also make dummy bulk uploads and downloads drawn from the same size distribution (more on Wi-Fi and while charging), and ordinary bulk traffic (encrypted backups, tree chunks, sticker and model downloads) looks identical, so "a large transfer happened" says little.
    - Recipients download through the bulk lane at their own time, with automatic download on Wi-Fi and dummy downloads.
    - What remains visible to a global observer: long-term volume (a heavy media user looks like one) and loose correlation between a large upload and a large download elsewhere, weakened by dummies and delays.
  - **Hidden (per attachment or per chat):** the attachment trickles through the spare capacity of the normal tick bursts, so the link pattern doesn't change at all. It is slow: a few KB/s, so a 2 MB photo takes several minutes, depending on the burst size (2c). A faster hidden mode would need a bulk packet in every tick for everyone (about 130 MB per open hour each way), which is not recommended at 10B scale.
  - **Stealth through your own node (candidate):** a user's Mac or Pi node already sends constant cover around the clock on mains power and a home connection, so it can afford a large constant bulk rate (for example 1 MB/s). On the home network the phone hands the attachment to its node over the local network, which no outside observer sees; the node sends it inside its constant stream. The recipient's node downloads it the same way and the phone pulls it locally. Totally stealth and fast for anyone with a node on their network. Away from home, stealth attachments either trickle (above) or wait for the home node. This would also be a patent candidate.
  - **Tiny stealth images (nu-media):** photos are re-encoded on the device into a custom compact format small enough to ride the normal ticks.
    - **Codec:** a learned image codec running on the Neural Engine, tuned for fidelity rather than generated detail (generative codecs invent faces and text, which is unacceptable for testimony and evidence), with text regions kept sharp. Target about 15–40 KB for a full-screen photo, against 25–60 KB for AVIF or JPEG XL at the same quality and 2–4 MB for the camera original. The networks use integer arithmetic so every device decodes identically.
    - **Progressive:** a recognisable preview of about 2 KB arrives in the first tick and sharpens over the following ticks. At about 3 KB/s of spare tick capacity (with the burst size in 2c), a 30 KB photo is complete in about 10 s, with no change to the link pattern.
    - **Privacy side effects:** all metadata (location, device, time) is dropped, and re-encoding weakens the camera sensor fingerprint that can link a photo to the phone that took it.
    - **Originals:** full-quality originals and video use your own node, the charging window or the trickle.
    - **Patent candidate:** progressive learned-codec delivery inside constant-rate mixnet cover.
  - **Stealth window (candidate):** phones without a node run a constant bulk stream while on Wi-Fi and charging (overnight), where battery and data cost nothing; stealth attachments queue until then.
- **Decided 9 Oct 2026:**
  - Stealth is a foundation of the whole system, not a setting. Every message, receipt and attachment rides the constant pattern; there is no opt-in, opt-out or "send now, not stealthy" mode. The fast default mode above is dropped.
  - Images use the tiny format, named **nu-media**, inside the ticks. Originals and video go through your node, the charging window or the trickle, whichever is fastest, and may take a while.
  - Video in nu-media is a later question.
- **Status:** **Decided** 9 Oct 2026.

### 2d. Offline mesh
- **Today's plan:** Wi-Fi Aware nearby mode, opt-in, carrying sealed Outfox packets between phones until one reaches the internet.
- **What Apple offers:** Wi-Fi Aware (iOS 26, fast direct links), Multipeer Connectivity (Bluetooth plus peer-to-peer Wi-Fi) and Core Bluetooth, which keeps working in the background with limits. Apple provides links, not multi-hop routing, so khensu builds store-and-forward on top (as Briar and Bitchat do).
- **Recommendation:**
  - **App open:** Wi-Fi Aware and Bluetooth, carrying the same fixed-size sealed packets on the same constant 2 s tick, so mesh traffic has no pattern either.
  - **Background:** Bluetooth only, at a low constant rate (enough for text, receipts and nu-media previews); whether Wi-Fi Aware runs in the background is checked in a spike.
  - **Multi-hop:** each phone holds others' sealed packets (capped, for example 50 MB, oldest first) and passes them on until one reaches the internet or the recipient; packets are deduplicated by `item_id` and expire with the mailbox rules.
  - **Turns on automatically** when no node is reachable, and off when the internet is back.
- **The limit stealth can't remove:** anyone with a radio scanner in range can tell that a device nearby is running the mesh, even with rotating random identifiers, and iOS background Bluetooth advertising is detectable by design. Content, sender and recipient stay hidden; local presence does not. This matters most in shutdowns, which is when mesh is needed.
- **Status:** Recommended.

### 2c. Tick burst size
- **Problem:** a signed message is about 4.9 KB, which needs 3 small packets, and the fixed buckets go up to 8. If each tick carries only one small packet, a typical message takes three ticks (6 s) to leave, which isn't real-time.
- **Recommendation:** each tick carries a fixed burst of 4 small packets (one mailbox fetch plus three slots), so a typical message leaves in a single tick. Cost: about 20 KB/s up while the app is open (about 72 MB per open hour), and four times the cover load on nodes compared with one packet per tick. Battery changes little, since the radio is awake at a 2 s tick anyway; the bigger cost is node bandwidth at 10B scale (see 10 and 31).
- **Status:** Open.

### 2e. Live calls: stealth at MOQOM latency
- **Today's plan:** calls carry MOQT media through two relays from different operators (caller's entry and callee's entry), so no single machine sees both IPs; direct paths are opt-in per contact.
- **What it protects:** single relays, nodes, operators and local observers learn nothing about who is calling whom. A global observer can still match the two edges (Alice's stream to relay A and Bob's stream from relay B start, stop and run at the same moments). Removing that needs mixing delays, which live media can't take.
- **Recommendation (adds stealth without adding latency):**
  - **Constant bitrate, fixed packet size.** Audio and video are encoded at a constant rate and padded to fixed-size packets, including silence and still scenes. Variable bitrate leaks speech: published attacks recover spoken phrases from encrypted packet sizes.
  - **Call setup over the mixnet.** Ringing, accept, keys and relay choice ride the normal ticks, so no node sees who called whom; relays are paid with anonymous credentials.
  - **Each side picks its own relay** near itself, from a different operator, AS and jurisdiction than the other side's relay.
  - **Relay trunks.** Relays exchange constant, padded traffic between themselves and carry many calls on each trunk, so the relay-to-relay leg can't be separated into calls.
  - **Blurred edges.** Each phone starts its stream to its relay a random few seconds before the call connects and keeps it running with padding a random few seconds after hangup, so start and stop times don't line up exactly.
  - **Looks like ordinary web traffic.** Media rides QUIC on port 443 (as MOQ over WebTransport does), so a local observer sees an HTTPS-like stream to an IP, not a recognisable call protocol.
  - **No direct internet paths.** Direct phone-to-phone over the internet reveals each side's IP to the other, so it is removed (stealth has no opt-out). Direct links stay only on local links with no internet observer: Wi-Fi Aware and the same Wi-Fi network.
  - **Group calls** fan out through relays as MOQ forwarders, with media keys from MLS (post-quantum end to end).
- **Latency:** two relays near each side add roughly 5–30 ms over a direct path; the target is under 150 ms glass to glass within a region. To be measured.
- **What remains:** long-term edge correlation by a global observer (5.2 in THREAT-MODEL.md), stated plainly in the app.
- **Status:** **Decided** 9 Oct 2026. Written into PLAN.md (Stealth), PROTOCOL.md 7.1 and THREAT-MODEL.md 5.2; MOQOM gets the same profile as an option (`moqom/docs/STEALTH-PROFILE.md`).

### 3. Directory lookups at global scale
- **Direction:** complete global scale at launch; the node delivery system is likely patentable.
- **Analysis (estimate):** a handle database for 10B accounts is about 640 GB (64-byte records). Full-database PIR touches every byte for every query: about 64 core-seconds each. At 0.1 lookups per account per day (about 11,600 per second) that is roughly 7 PB/s of memory scanning, or several hundred thousand machines doing nothing else. No PIR scheme without client-side preprocessing can avoid touching every record, and the preprocessing schemes need each client to stream the whole database once. So full-database PIR at 10B isn't feasible on any fleet.
- **Recommendation:** sharded PIR, which is global at launch because capacity grows linearly with nodes:
  - 1,024 shards by hash prefix, about 10M handles each (about 640 MB, fits a Pi's RAM); each shard served by many mirrors; batched queries.
  - What leaks: a mirror learns "an unknown person looked up one of these 10 million handles". The mixnet hides who asked; scheduled dummy queries (7) hide when.
  - Lookups stay rare: invite links and QR codes carry keys, credentials prove themselves (5), and contacts' key changes arrive inside the conversation.
- **Patents:** mixnet-delivered sharded PIR with log proofs and scheduled dummy lookups goes into `PATENTS.md` as a candidate. The disclosure rule applies: assess before any public description.
- **Status:** **Decided** 9 Oct 2026.

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
  - **Update after 2, 2a, 2b and 2c:** absolute cover with a 2 s tick, a 4-packet burst and a matching constant downstream is about 8 times the load above: roughly 3 million fully used Pis for 10B (about 8 million with headroom), or about 300,000–800,000 server-class nodes. 50,000 Pis carry roughly 100–150 million DAU. Levers: burst size (2c), hop count, packet header size, and faster nodes. To be revisited once 2c is decided.
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

## G. Public square (proposed 9 Oct 2026; design in `PLAN.md`, Public square)

40. **Illegal-content exception.** Rec: node operators refuse to cache, and the app refuses to display, content whose hash is on a public, append-only, consensus-maintained list limited to child sexual abuse material and content illegal everywhere (hashes from NCMEC, IWF and peers). Without it, operators carry legal risk for hosting it, the App Store rejects the app (rule 1.2), and the network becomes a target for shutdown. Everything else is handled on each device. **Open.**
41. **Rater Sybil resistance.** One rating credential per person without identity checks. Options: stake plus reputation (rec at launch), invitation trees, an optional proof-of-personhood credential later. **Open.**
42. **Label set.** Rec: factual claim with sources, opinion, misleading, fraud or scam, spam, adult, graphic violence, satire, AI-generated. **Open.**
43. **Name** for the public square in the app. **Open.**
44. **Persona model.** Rec: every account can post from its public handle or from any number of unlinkable personas, each with its own reach history. **Open.**
45. **Reading at 10B.** Timeline fetches inside the ticks: how many feeds and posts a phone can refresh per minute at the 2c burst size, and whether hot posts are pushed to phones as part of the downstream. **Open.**
46. **Shutdown sync.** Satellite (Starlink and others) and cross-border mesh bridges as upstream paths; how much feed each phone carries (rec 200 MB, recent and followed first). **Open.**
47. **Threshold pledges.** Rec: anonymous tallies with a reveal only when the threshold is met, built on the same rate-limit proofs. **Open.**

## H. webE and nu-media (proposed 9 Oct 2026; design in `PLAN.md`)

48. **MOQOM relay in khensu nodes.** `moqom-relay` is proprietary, nodes are AGPL, and the rule today is that tatenan copies nothing from it. Options:
    - (a) MOQOM releases a forwarding-only relay core under Apache-2.0 for nodes; MOQOM Cloud keeps its product features (console, recording, metering, multi-tenant control plane) proprietary. Rec.
    - (b) nodes ship the proprietary relay as a separate licensed binary, which breaks reproducible, fully open nodes.
    - (c) tatenan writes its own relay on the Apache MOQOM transport, as planned.
    **Open.**
49. **Reader privacy for public content.** Public mode is fast but a relay sees which public object an IP fetched. Options: accept it for public content (rec, with the publisher choosing the mode), route public fetches through the user's own node, or a fast lane through two relays like calls. **Open.**
50. **Site model.** Static bundles plus WebAssembly only (rec at launch), or server-side code on the owner's node. **Open.**
51. **Browser route.** Extension plus local daemon first, Chromium patch second (rec); upstreaming to Chromium versus a khensu browser build. **Open.**
52. **Codec name and scope.** Confirm "nu-media" for images, video and later 3D. Confirm the Microsoft codec meant (the DCVC family from Microsoft Research, including DCVC-RT?). **Open.**
53. **Video codec spike.** Measure the hybrid design on iPhone 18 Pro (iOS 27) and an iOS 26 baseline device: quality at each stealth call tier, Neural Engine time per frame, battery, glass-to-glass latency. **Open.**
54. **IETF plan.** Which drafts first: Outfox-PQ packet format, stealth MOQ profile, transparency-log naming, signed site bundles. **Open.**
55. **New repos.** `khensu-browser` (extension, daemon, Chromium patch) and `nu-media` (codec, Apache-2.0 like `khensu-core`?). **Open.**

## F. Housekeeping

37. **`PROTOCOL.md` sections 13 and 14** say "frozen in `PAYMENTS.md`" and "each frozen in its own spec"; those files don't exist yet. Reword to "to be written". **Open.**
38. **Tamarin run:** the first run printed nothing because macOS has no `timeout` command; rerun without it and record results in `formal/README.md`. **Open (mine).**
39. **`PLAN.md` still has the 50 MB cellular budget** and the VRF; both change once 2 and 4 are confirmed. **Open.**
