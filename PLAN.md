---
name: MOQOM Messenger
overview: "A Signal replacement built on MOQOM: post-quantum MLS end-to-end encryption for every message, call, attachment and profile, carried by an open, decentralized network of operator nodes (always-on, scheduled, N-hour and idle-time, down to a Raspberry Pi 5) with a post-quantum mixnet that hides who talks to whom. The node list comes from our own lightweight consensus (a rotating committee drawn by lottery, no permanent ledger), with founder safeguards until the network is established. You keep a fixed share of subscription proceeds; the rest buys and burns the network's post-quantum token for capacity, and the protocol mints rewards to operators (burn and mint). Users can send money anonymously over the mixnet through a STARK-based shielded pool whose records expire."
todos:
  - id: threat-model
    content: "Write moqom-messenger/docs/THREAT-MODEL.md and PROTOCOL.md: adversaries, guarantees (including founder trust during launch), wire formats for messages, Outfox packets, mailbox IDs, leases, receipts, epoch headers"
    status: pending
  - id: mls-hardening
    content: "moqom-security: ML-KEM-1024 + ML-DSA-65 suite (pure post-quantum, no classical KEM), PrivateMessage with secret tree, identity-signed device credentials, Update policy; vectors in Swift/Go/Rust"
    status: pending
  - id: treekem
    content: "moqom-security: RFC 9420 ratchet tree (TreeKEM) in Swift/Go/Rust, passing mlswg tree-math, tree-validation, treekem and secret-tree vectors; groups up to 1,000 devices"
    status: pending
  - id: licensing
    content: "AGPL-3.0 headers and LICENSING.md for moqom-messenger node and apps, Apache-2.0 for protocol libraries, CLA bot for outside contributions, separate grant for the App Store build"
    status: pending
  - id: formal-model
    content: Tamarin/ProVerif model of add, message, remove, Outfox routing and the epoch-header consensus; fix any findings in the specs
    status: pending
  - id: node-core
    content: "moqom-messenger/node: open-source moqom-node with mailbox, sequencer and relay roles, signed leases and draining, on moqom-proto/transport/client; runs on Raspberry Pi 5"
    status: pending
  - id: consensus
    content: "Own consensus layer in moqom-node: weighted sortition (reputation x stake) of a 21-member BFT committee per epoch, ML-DSA-65 epoch headers, light-node header checks, account state root with pruned history, loop-traffic measurement scored by median"
    status: pending
  - id: token-chain
    content: "Token on our chain: ML-DSA-65 accounts, transfers, stake/unstake and slashing, protocol mint to operators from work receipts with a declining emission schedule, burn for capacity credits, per-epoch burn auction for launch liquidity; genesis allocation and token name set with counsel"
    status: pending
  - id: shielded-payments
    content: "Shielded payments in v1: STARK-proved note pool with ML-KEM-1024 note encryption, fixed denominations, eras that expire and drop their spent lists, transfers as mixnet messages, on-device proving on iPhone and Mac; external audit"
    status: pending
  - id: legal-review
    content: "Counsel sign-off before mint and before payments launch: token classification under the March 2026 SEC/CFTC interpretation, Regulation Crypto Assets if any sale, money-transmission analysis of the shielded pool, MiCA white paper, App Store 3.1.5 region licensing, sanctions screening at pool entry and exit"
    status: pending
  - id: governance
    content: "Founder safeguards: 3-of-5 ML-DSA founder threshold key and key ceremony, staged powers (genesis, open candidacy, established) with step-down signed by the founder, dual-approval rule changes with 30-day timelock and 48-hour tighten-only emergency path"
    status: pending
  - id: outfox-paper
    content: "Outfox extensions (epoch-bound replay protection for low-memory nodes, ML-KEM-1024 instantiation, unlinkable work receipts, loop-measurement indistinguishability, SURBs for mailbox fetch) with proofs and Pi 5 evaluation; arXiv paper by Justin Elliott Staffer, Elliott Wave LLC, after a patent decision"
    status: pending
  - id: mixnet-credentials
    content: Outfox (ML-KEM) packets and three-layer Loopix mixing with cover traffic; blind-signature anonymous credential issuer; node work receipts
    status: pending
  - id: key-transparency
    content: Key transparency log in the C2SP tlog-checkpoint format, cosigned by the transparency-dev and Sigsum witness networks; username registration, KeyPackage publishing, lookups over the mixnet
    status: pending
  - id: identity
    content: "Identity layer: 32-byte bech32m addresses, KERI-style pre-rotation in the log, permanent handle claims with anonymous credentials, VRF-stored handles, SIWE wallet links, ENS CCIP-Read resolver with log proofs, four-word check phrase"
    status: pending
  - id: push
    content: "Push: stateless gateway at push.khensu.nu with encrypted wake capabilities, random delay and merging, Notification Service Extension fetch into the CompleteUnlessOpen queue, Anonymous/Off/Previews modes, PushKit plus CallKit with calls kept out of Recents"
    status: pending
  - id: summaries
    content: "KhensuMemory (iOS 26+/macOS 26+): Hindsight-style local engine on the encrypted SQLite store: FTS5 keyword index, NLContextualEmbedding vectors, Foundation Models fact/entity extraction, four-way recall with rank fusion and token budgets, observation consolidation, reflect with tool calling and citations, Catch me up summaries; derived data deleted with its messages, never backed up; no Private Cloud Compute"
    status: pending
  - id: typing
    content: "Typing indicator stream: per-member ephemeral MOQ track encrypted with an MLS exporter key, fixed-size Outfox packets sent in place of cover traffic, start/stop events with 10 s refresh and 30 s expiry, never stored; reciprocal switches for typing and read receipts; presence off by default"
    status: pending
  - id: apple-platform-v1
    content: "v1 Apple features: Wi-Fi Aware offline nearby relay of sealed packets, tap-to-add/verify (Tap to Share, NFC), Push to Talk over the mixnet, CarPlay calls only (no Siri, so no CarPlay messaging), default messaging/calling app, Communication Notifications in Previews mode, App Attest feeding blind-token issuance, on-device voice (SpeechAnalyzer dictation, AVSpeechSynthesizer read-aloud), Writing Tools off and third-party keyboards blocked in the composer, Declared Age Range teen defaults, StoreKit external purchases; file Apple entitlement requests early"
    status: pending
  - id: apple-client
    content: "moqom-messenger/apple: khensu.nu app (bundle nu.khensu.ptah), SwiftUI on Liquid Glass with a monochrome, spacey identity (connected-dot networks, crescent icon, moon-phase timers) and a Telegram-like layout (folder tabs, swipe actions, Chats/Calls/Search/Settings tabs), MessengerKit and iOS/macOS apps: Face ID/Touch ID access policies per key, app lock, CompleteUnlessOpen incoming queue, passcode-only coercion setting; 1:1 and group chat, attachments, disappearing messages, safety numbers, QR device linking, encrypted store and backups, wake-only push gateway"
    status: pending
  - id: calls
    content: Integrate MoqomKit calls over two-hop node relays, direct paths opt-in per contact
    status: pending
  - id: operator-economy
    content: macOS node app and Raspberry Pi 5 image with idle/scheduled/N-hour modes; reputation scoring; token staking as the operator bond, slashed by consensus; operator wallet in the node app showing protocol rewards
    status: pending
  - id: export-compliance
    content: "Encryption export: mass-market classification with export counsel, App Store Connect answers, French ANSSI declaration, published classification for node software"
    status: pending
  - id: entities-docs
    content: "Entities and documents: operating company with organization Apple account, separate token/network entity with counsel, terms, privacy policy, operator terms, token disclosures, law-enforcement guidelines, security.txt and bug bounty"
    status: pending
  - id: trust-safety
    content: "Trust and safety: block/report with message franking, message requests, NCMEC reporting of user-reported CSAM, transparency report and warrant canary, UK OSA and EU DSA assessments, no client-side scanning policy"
    status: pending
  - id: bootstrap
    content: "Network bootstrap: 9+ genesis nodes across clouds and countries, consensus-enforced private-network threshold, Early network banner in the app"
    status: pending
  - id: battery-budget
    content: "Battery and data: foreground-only cover traffic, small and bulk packet lanes, Wi-Fi/cellular/Low Power rates, 3% battery and 50 MB cellular daily budget verified with MetricKit"
    status: pending
  - id: discovery-growth
    content: "Discovery and growth: invite links with keys in the URL fragment, group invites, public channel handles, profile links; no phone/email discovery in v1"
    status: pending
  - id: pricing-token-numbers
    content: "Pricing tiers (Free, Plus, Family, Business), free-user cost model validated on testnet, token supply/emission/allocation proposal for counsel"
    status: pending
  - id: ops
    content: "Operations: opt-in scrubbed crash reports over the mixnet, public status page from epoch headers, reproducible signed node builds, binary transparency for app releases, incident runbooks"
    status: pending
  - id: platforms
    content: "Platforms: Linux/Pi and macOS nodes at testnet, Windows node later; Android client 6-9 months after v1; no web client"
    status: pending
  - id: design-mocks
    content: "Design canvas: iOS screen mocks in the monochrome Liquid Glass style plus architecture, charts, comparison tables and links for the plan"
    status: completed
  - id: audit-launch
    content: Fuzzing for all new decoders, release hashes in the transparency log, hardware keys on Apple/GitHub accounts, external audit, bug bounty, launch
    status: pending
isProject: false
---

# khensu.nu: decentralized, post-quantum Signal replacement on MOQOM

## Goals and non-negotiables

- Every byte a user creates is end-to-end encrypted: messages, attachments, calls, profile names and avatars, group names, read receipts, typing indicators and backups. No server, node, validator or you ever holds a key that decrypts them.
- Metadata is protected, not just content. No single node, and not you, learns who talks to whom, when, or how often (every message, receipt and typing event goes through the post-quantum mixnet, with no faster path; calls use two-hop relays).
- Post-quantum from day one, for confidentiality, authentication and consensus. Key exchange is pure ML-KEM-1024 (FIPS 203, the highest security category), with no classical algorithm; signatures everywhere, including the consensus, are ML-DSA-65 (FIPS 204).
- Decentralized at launch: independent operators run the nodes, the node list is agreed by a rotating committee drawn from those nodes, and the user directory is an append-only transparency log anyone can audit. Founder safeguards protect the network from capture until it is established.
- Light enough to run a node on a Raspberry Pi 5.
- iOS and macOS first, in a new top-level `moqom-messenger/`, reusing `moqom-security` (MLS, proof, token) and MoqomKit (calls, direct paths, transport).

## Why it's better than Signal

Signal is the bar, and on content encryption it is very good: the Double Ratchet, PQXDH (hybrid X25519 + ML-KEM for the first key agreement), SPQR (post-quantum added to the ongoing ratchet), sealed sender, and zero-knowledge group credentials that keep group membership hidden from its servers, all with published formal analyses. The advantages below are specific; each one is a requirement this plan must meet, not marketing.

1. **Post-quantum authentication, not just post-quantum secrecy.** Signal's identity keys and signatures are Curve25519/XEdDSA, which are classical. A future quantum computer could not read recorded Signal messages, but it could impersonate a contact or forge identity keys. Here every identity key, device credential, KeyPackage, commit, message signature and consensus vote is ML-DSA-65, so impersonation is quantum-resistant too.
2. **The network hides who talks to whom; Signal's server sees much of it.** Sealed sender hides the sender of a message from Signal, but Signal still sees the recipient, the sender's IP address, and exact timing. Published research (Martiny et al., NDSS 2021) shows that over time those let a server link senders to recipients anyway. Here messages go through a three-layer mixnet with random delays and constant cover traffic, using a post-quantum packet format (Outfox with ML-KEM), mailboxes are unlinkable and rotate every epoch, and no node, validator, or you sees sender, recipient and timing together.
3. **No single operator to compel, breach, block or shut down.** Signal runs every server, so one legal order, one breach, one funding crisis, or one national firewall rule (Signal has been blocked in Iran, China, Russia and elsewhere) affects everyone. Here independent operators in many countries run the nodes, a different randomly drawn committee agrees the node list each epoch, and blocking means blocking thousands of changing node addresses, many of them on home connections.
4. **No phone number, ever.** Signal still requires a phone number to register, even with usernames hiding it from contacts, so your carrier and Signal can link the account to a SIM. Here identity is a key in the Secure Enclave plus an optional username. Phone and email lookup are optional and come only with private contact discovery.
5. **No trust in Intel hardware enclaves.** Signal's contact discovery and PIN-based key backup (Secure Value Recovery) rely on Intel SGX and similar enclaves, and SGX has a history of side-channel breaks. Here there is no contact discovery server to trust, and backups are encrypted with a recovery key only the user holds.
6. **Key verification that works for every contact, with more witnesses and private lookups.** Signal shipped key transparency as "Automatic Key Verification" in 2026 (on for all users since Android 8.21.6, iOS 8.22.0 and Desktop 8.21.0; [Signal blog, 11 Aug 2026](https://signal.org/blog/automatic-key-verification/)). Its limits, from Signal's own documentation: it works only when you have the contact's phone number, so username-only contacts (the most privacy-conscious users) fall back to comparing safety numbers by hand; it relies on two hand-picked auditors (Cloudflare and Trail of Bits); and clients accept auditor signatures up to seven days old, so a malicious server could keep a split view for up to a week ([Trail of Bits, 11 Aug 2026](https://blog.trailofbits.com/2026/08/11/how-trail-of-bits-helps-verify-the-integrity-of-your-signal-chats/)). Here identity is a key, not a phone number, so every contact is verified automatically; the log is cosigned by a quorum from the public transparency-dev and Sigsum witness networks; entries are signed with ML-DSA-65; clients require cosignatures no older than 24 hours; and lookups go through the mixnet, so the log never learns whose key you checked.
7. **Calls that hide IPs from everyone, not just the other person.** Signal's "always relay calls" hides your IP from the person you call, but Signal's relay sees both IPs. Here every call goes through two relays run by different operators, so no single machine sees both ends.
8. **Group security that heals.** Signal groups use sender keys, which rotate only when membership changes, so a key stolen from one phone keeps decrypting that sender's group messages until then. MLS here has every device refresh its key every 24 hours or 1,000 messages, so a group recovers from a compromised device automatically. Group membership is hidden from the network: the sequencer sees only an opaque group ID and encrypted commits that arrive over the mixnet.
9. **Encrypted at rest by the Secure Enclave on every platform.** The local message store key is wrapped by the Secure Enclave on iPhone and Mac, not kept in a config file, which is a mistake Signal Desktop made until 2024.

Where Signal is equal or still ahead, stated in the threat model so the claims stay honest:
- **Parity:** content encryption strength, formal verification, push notifications that carry no content.
- **Signal ahead:** a decade of audits and real-world testing, a huge user base, Android, Windows and Linux clients at launch, and a nonprofit trusted by journalists.
- **Costs of the mixnet:** messages arrive in seconds rather than milliseconds, and cover traffic uses more battery and data. Live calls can't use the mixnet, so a global observer could still correlate call timing; calls are protected against single nodes, not against a global adversary.
- **Launch trust:** until the founder steps down, users trust the founder not to approve malicious validators. That is trust about routing integrity, never about message content.

## Telegram's features, end-to-end encrypted

Telegram's appeal is its features, not its security: ordinary chats and all groups are "cloud chats" Telegram can read, and only 1:1 Secret Chats on a single device are end-to-end encrypted ([Telegram FAQ](https://telegram.org/faq)). Its E2EE group calls (up to 200 people) are the exception. The goal is every Telegram feature with nothing readable by us or any node.

| Telegram feature | How we build it, encrypted |
| --- | --- |
| Instant sync on every device, full history on a new device | MLS multi-device; history copied encrypted from an existing device when linking, or restored from an encrypted backup on mailbox nodes |
| Groups up to 200,000 | Encrypted groups up to 1,000 devices with TreeKEM, which is the cap (decided: no larger groups); anything bigger is a channel |
| Channels with unlimited subscribers | MOQOM broadcasts: public channels are public content served by relays; private channels encrypt each post and seal keys to subscribers with MOQOM's audience envelopes (keys rotate every 5 minutes) |
| Channel comments, reactions, view counts | Comments as a linked encrypted group; reactions as encrypted messages; view counts approximated with anonymous tokens so nobody learns who viewed |
| Topics / forums in groups | Threads inside one MLS group, carried in the encrypted message metadata |
| Group voice chats, video calls, live streams | MOQOM's core: rooms and broadcasts with thousands of viewers at sub-second latency, end-to-end encrypted, recording only by an agent every member can see (beyond Telegram's 200-person E2EE calls) |
| Secret chat self-destruct | Disappearing messages in every chat, with a per-chat timer |
| Edit, delete for everyone, pin, reply, forward, polls, quizzes, scheduled messages | Encrypted control messages; poll results counted on devices; scheduled messages held sealed by mailbox nodes until the send time |
| Saved Messages, chat folders, archive, multiple accounts | Note-to-self MLS group; folders and archive synced encrypted between your devices; multiple personas per app |
| Cloud search | On-device full-text search over the encrypted local store; public channel discovery through an opt-in public directory |
| Usernames and t.me links | Permanent `@handles`, links and QR codes, ENS subnames; handles can't be traded (unlike Telegram's username marketplace) |
| Files up to 2 GB (4 GB Premium) | Chunked, encrypted attachments on mailbox nodes; the size limit is set by storage cost (2 GB free, larger with a subscription) |
| Stickers, GIFs, emoji | Sticker packs as public, content-addressed files; GIF search goes through the mixnet so providers don't see who searched |
| Voice and round video messages, transcription, translation | Transcription and translation on the device (Apple Speech and Translation frameworks), never on a server |
| Stories | Encrypted to the chosen audience with audience envelopes, expiring |
| Live location | End-to-end encrypted, building on MOQOM's live map work ([live-map guide](sites/moqom-dev/src/content/docs/guides/live-map.md)) |
| Bots | Bots join as visible members of the encrypted group, like MOQOM agents; they only see chats they were added to, and every member sees that they're there (Telegram bots read through Telegram's servers) |
| Mini Apps | Sandboxed web apps with no access to keys, opened by user action, talking to the chat only through a narrow, permissioned API |
| Payments, Stars, tips, gifts | MOTOM credits and creator tips (already built), opt-in stablecoin payments to linked wallets; Apple's in-app purchase rules for digital goods |
| Admin tools: roles, slow mode, bans, anti-spam | Roles and permissions are signed into the encrypted group state (MOQOM's capability model); every member's app enforces them; spam handled by message requests, rate-limit tokens, and verifiable abuse reports (message franking, which lets a recipient prove what an abusive message said without breaking encryption for anyone else) |
| Web version | Desktop apps first; a web client is hard to secure for E2EE because the server delivers the code each time |

Beyond Telegram: everything above is end-to-end encrypted and post-quantum by default, metadata is hidden by the mixnet, no phone number is needed, wallet and ENS links, creator tipping in live rooms, AR spaces from MOQOM ([ar-space guide](sites/moqom-dev/src/content/docs/guides/ar-space.md)), on-device AI summaries, and anyone can earn by running a node.

What we won't copy: sponsored messages in channels, server-side access to chats, and tradeable usernames.

## What exists and what has to change

Reusable today:
- PQ MLS in Swift/Go/Rust with cross-language vectors: [moqom-security/docs/moqom-mls.md](moqom-security/docs/moqom-mls.md) (suite `0xF0AA` ML-KEM-768 + ML-DSA-65, plus X-Wing `0xF0A1`).
- Device keys in the Secure Enclave and proof of possession: [moqom-security/docs/moqom-proof.md](moqom-security/docs/moqom-proof.md), `MoqomKit/Security/DeviceKey.swift`.
- 1:1 and small-room calls, direct paths, fallback, GOAWAY-style relay migration: `moqom-swift-pq/Sources/MoqomKit/Direct/`, [peer-to-peer guide](sites/moqom-dev/src/content/docs/guides/peer-to-peer.md).
- Record format for app-data tracks: [moqom-pq/docs/data-format.md](moqom-pq/docs/data-format.md).
- Fiat money layer (Stripe purchases for MOQOM Cloud customers, burn auction seller payouts): [motom/docs/README.md](motom/docs/README.md).

Gaps that block "solid everywhere" (from [moqom-pq/docs/E2EE-KEY-MANAGEMENT.md](moqom-pq/docs/E2EE-KEY-MANAGEMENT.md) "Not done" and the MLS subset list):
- No `PrivateMessage` / secret tree: no per-message keys, so no forward secrecy inside an epoch. Messaging needs it.
- No per-sender signatures on application data (SFrame has none). Every message must be signed inside the ciphertext.
- Basic credentials only (`username/device`). Needs identity-key-signed device credentials tied to the transparency log.
- Flat member list (linear commits). Replaced by the RFC 9420 ratchet tree (TreeKEM) before launch, so groups reach 1,000 devices and the library passes the MLS working group's public `tree-math`, `tree-validation`, `treekem`, `secret-tree` and `message-protection` vectors, which it can't use today.
- The delivery service is room-scoped and ephemeral (groups dropped when nobody is online, messages pruned after 10 minutes). Conversations must be persistent and ordered without a central server.
- `moqom-relay` is proprietary ([moqom-engine-pq/LICENSING.md](moqom-engine-pq/LICENSING.md)). Operators and auditors need open node code, so the node is a new binary built on the Apache crates (`moqom-proto`, `moqom-transport`, `moqom-client`), not on the relay.

Licensing (decided): the node and the apps are AGPL-3.0, as Signal's server and apps are, so a modified node or app has to publish its changes and nobody can run a closed fork of the network. Protocol libraries (`moqom-security`, Outfox, credentials, consensus wire format, vectors) stay Apache-2.0 so independent implementations can exist. Outside contributors sign a CLA, which keeps you able to publish the iOS build under a separate grant (Apple's terms conflict with AGPL) and to sell commercial licences.

## Architecture

```mermaid
flowchart LR
    subgraph client [iPhone or Mac]
        App[Messenger app]
        MK[MessengerKit]
        SE[Secure Enclave keys]
    end
    subgraph network [Operator nodes, Pi 5 and up]
        Mix1[Mix layer 1]
        Mix2[Mix layer 2]
        Mix3[Mix layer 3]
        Mailbox[Mailbox replicas]
        Seq[Group sequencer]
        Relay[Call relay]
        Committee["Epoch committee, 21 drawn by lottery"]
    end
    subgraph services [Thin services]
        KT[Key transparency log plus public witnesses]
        Issuer[Anonymous credential issuer]
        Push[Push gateway, wake-only]
        Motom[MOTOM fiat side and burn auction payouts]
    end
    Founder["Founder 3-of-5 key, launch safeguards"]
    App --> MK
    MK --> SE
    MK -->|"Outfox packets"| Mix1 --> Mix2 --> Mix3 --> Mailbox
    Mix3 --> Seq
    MK -->|"two-hop MOQT"| Relay
    Committee -->|"signed epoch header"| MK
    MK -->|"lookups via mixnet"| KT
    MK -->|"blind-signed tokens"| Issuer
    Mailbox -->|"opaque wake"| Push
    Committee -->|"burn auction results"| Motom
    MK -->|"shielded spends via mixnet"| Committee
    Founder -.->|"co-signs rules, approves validators until step-down"| Committee
```

Roles and trust:
- **Mix nodes** (Loopix-style, three layers, fixed-size Outfox packets using ML-KEM, Poisson delays, cover traffic from clients and nodes). They see only the previous and next hop. Standard Sphinx uses classical X25519, so it is not used.
- **Mailbox nodes** hold sealed packets per device under unlinkable mailbox IDs, replicated across at least three operators in different networks. They cannot read or attribute anything.
- **Group sequencers** order MLS commits per group: first commit per epoch wins, as the current delivery service does. The sequencer is chosen deterministically from the group ID over the epoch's node list and has a standby. It can delay or drop (detected and failed over) but cannot forge, since members verify signatures and confirmation tags. A sequencer that signs two different commits for the same group epoch is provably misbehaving and penalized. It sees only an opaque group ID and encrypted commits that arrive over the mixnet, so it never learns who is in a group.
- **Call relays** carry MOQT media. A call uses two relays (caller's entry and callee's entry) so no single node sees both IPs. Direct paths stay off by default and are opt-in per contact.
- **Epoch committee** (see Consensus below) agrees and signs each epoch's header. It never sees user traffic.
- **Key transparency log** maps usernames to identity keys and device lists. It is append-only and publishes checkpoints in the C2SP `tlog-checkpoint` format, cosigned (`tlog-cosignature`) by the existing transparency-dev and Sigsum witness networks, so independent witnesses exist from day one without recruiting. Clients require a quorum of witness cosignatures and verify inclusion and consistency proofs, so even the log operator cannot show different keys to different people.
- **Credential issuer** blind-signs anonymous access tokens after payment. Nodes check that a token is valid without learning who bought it.
- **Push gateway** (`push.khensu.nu`): the one unavoidable central piece, because APNs is tied to your developer key. It receives only an encrypted wake capability and sends a content-free "New message" alert. It never learns the sender, the conversation or the user's address. See Push notifications below.

## Consensus: our own lightweight post-quantum chain

Nodes relay and replicate data. Consensus agrees on these things per epoch (one hour). Only token balances and stakes persist; everything else is dropped after the dispute window:

1. The node list root: who is in, with which roles and leases.
2. The reliability scores root, from measurement.
3. The work receipts root, for paying operators.
4. Evidence of provable misbehaviour (conflicting leases, a sequencer signing two commits for one epoch, persistently failed measurement).
5. The account state root (token balances and stakes) and the shielded pool's note commitment root for the current eras.

Design:
- **Sortition.** Every eligible node is in a weighted lottery each epoch, and about 21 are drawn to form that epoch's committee. Eligible means a lease covering the whole epoch, enough reputation, and good measured reliability. A Pi 5 on an always-on or scheduled lease qualifies; idle-time machines do not. The draw uses randomness from the previous epoch's header and caps how many seats any one operator, network provider (autonomous system) or country can hold.
- **BFT agreement.** The committee runs a HotStuff-family protocol and produces one epoch header signed by at least 2/3 of its members with ML-DSA-65. The consensus is post-quantum, which Ethereum and most chains are not.
- **Light nodes and clients.** Everyone else checks about 14 ML-DSA signatures per epoch and keeps only the current node list (a few hundred KB for 10,000 nodes). The full list is fetched from any node or mirror and checked against the header's root, so mirrors are untrusted.
- **State, not history.** Validators keep the current account state (balances, stakes) and the current shielded eras, plus the last few epochs of blocks for disputes. Older blocks are dropped; a new node syncs from a committee-signed state snapshot. Anyone may archive history; the network does not need it, and shielded transfers reveal nothing even when archived.
- **Measurement.** Loop cover traffic (packets a node routes back to itself) doubles as measurement and looks exactly like real traffic. A random, weighted set of measurers each epoch sign reports; a node's score is the median across measurers; measurers far from consensus lose reputation and bond.
- **Sybil resistance (decided).** Weight is reputation multiplied by staked tokens. Reputation is earned by measured, honest service over weeks, so buying tokens alone can't buy influence, and an attacker loses both reputation and a slice of stake when the consensus records provable misbehaviour. Per-operator, per-network-provider and per-country seat caps still apply.

## Governance and founder safeguards

Rule changes (fees, eligibility, penalties, cipher suites):
- Need both the founder signature and 2/3 of the epoch committee.
- Take effect only after a 30-day timelock, during which the committee can veto.
- Emergency fixes take 48 hours but may only tighten rules (disable a cipher, raise requirements). Nothing that loosens rules or touches money can use the fast path.

Founder key: a 3-of-5 threshold of ML-DSA-65 keys on separate hardware: two offline (air-gapped laptops, backups in separate safes), one in a cloud HSM if it supports ML-DSA (check Google Cloud KMS), and two with trusted people or counsel for recovery. Any 3 shares can revoke and replace the founder key, behind the timelock. The founder key is pinned in the app with the genesis validator keys. Because founder changes also wait the 30-day timelock, a thief with 3 shares still cannot loosen rules or move money before the key is rotated.

Founder powers by stage:
1. **Genesis.** The committee is drawn only from validators you run and partners you approve. Your co-signature is needed for every committee admission and every rule change.
2. **Open candidacy.** Any node with enough reputation enters the lottery; you can veto admissions.
3. **Established.** When objective thresholds hold for 90 days (for example at least 500 nodes, 100 independent operators, 20 countries, 50 network providers and 63 eligible committee candidates), the network shows that the step-down is available, and it takes effect when you sign it with the founder key (decided: manual sign-off). Your admission veto then ends; the dual-approval co-signature on rule changes remains.

What the founder can never do, at any stage: read content, unmask users, skip the timelock except for tighten-only emergencies, or change payouts and penalties without the timelock.

App and supply-chain takeover (a separate, bigger real-world risk): hardware security keys on the Apple developer and GitHub accounts; release signing only from locked-down CI; every app and node release hash published to the transparency log so nodes and outside watchers can see an unexpected release; reproducible builds for the node and the Pi image.

## Identity, addresses and handles (decided)

- **Permanent address.** Each account's address is SHA3-256 of its first identity key and that key's commitment to the next key: 32 bytes, unique by construction, never changes, needs no registry to stay unique. Displayed as bech32m with an app prefix and checksum (`khensu1q8f...`), shared mostly by QR code and link. Users may create several unlinked addresses (personas).
- **Key rotation by pre-rotation (KERI-style).** Every identity key publishes the hash of the next key, which stays offline. Rotating reveals the next key, which must match; a thief holding only the current key cannot rotate the owner out. Each rotation is an entry in the transparency log, batched per epoch.
- **Handles: optional, unique, permanent.** A handle such as `@elliott` is claimed first-come in the log with an anonymous credential and is bound to its address forever: it can never be renamed, transferred or reissued, even after an account is abandoned, so a handle always means the same person. Claiming shows a clear "this can never be changed" confirmation. A short list of reserved words and trademarks, and a dispute policy that can mark a handle "disputed" or stop serving it, but never reassign it.
- **Wallet links for web3.** Opt-in, per wallet, revocable: the user signs a Sign-In with Ethereum (EIP-4361) statement linking a wallet to their address, published in the log, optionally also as an ENS text record. Wallet keys are never reused as messenger keys (they are classical secp256k1). The app warns that a linked wallet's public transaction history becomes associated with the address.
- **Account deletion in the app (App Store guideline 5.1.1(v)).** Settings has a "Delete account" item. It signs a tombstone into the log (the address and handle are retired forever and never reissued), tells your groups you left, asks mailbox nodes to drop your mailboxes and backups, revokes push capabilities, and wipes keys and data on every linked device.
- **No third-party login (App Store guideline 4.8).** Identity is the app's own key-based sign-up, so the guideline's "own account setup and sign-in" exception applies and Sign in with Apple isn't required. Wallet links stay an optional profile feature, never a way to sign in; otherwise 4.8 could apply.
- **Human-friendly layers over the address.** Three layers, all pointing at the permanent address:
  - The `@handle` resolves to the address through the log.
  - The handle's full form is a subname of our own domain: `elliott.khensu.nu`. It is shown on profiles and in share links, and the app resolves it from the key transparency log over the mixnet, never through DNS, so lookups don't leak who is looking up whom.
  - For wallets and dapps outside khensu, `khensu.nu` is imported into ENS as a DNS name (DNSSEC-signed) and served by an off-chain resolver (ERC-3668 CCIP-Read) that answers from our log, with no per-name on-chain fees. The resolver returns log proofs, so it can't lie about which address a handle maps to. No public DNS records or web pages are created per user.
  - A spoken check phrase of four words derived from the address, for confirming a contact out loud. It's for verification only and never used to look anyone up, because four words aren't unique.
- **Anonymous registry.** Registration and lookups go through the mixnet, paid with blind-signed credentials. Log entries are stored under a VRF so the log can't be enumerated or scraped, and handles are stored as VRF outputs with commitments rather than plaintext, so a handle can stop being served (for disputes or erasure requests) without rewriting the append-only log. Profiles are encrypted with a profile key shared only with contacts. Device counts are padded. First contact goes through message requests and costs an anonymous rate-limit token.

## On-device biometrics (Face ID, Touch ID)

Biometrics never leave the device and never reach us; the Secure Enclave matches the face or fingerprint and then releases a key operation. Each key gets its own access policy (`SecAccessControl` with LocalAuthentication):

| Key or action | Policy | Why |
| --- | --- | --- |
| Identity key (rotation, claiming a handle, linking a wallet, linking a new device, approving a removal) | Face ID or Touch ID every time, `.biometryCurrentSet` | The most powerful key. Bound to the currently enrolled biometrics, so adding a new face or finger invalidates it, which defeats someone who learns the passcode and enrolls their own face. Recovery is through the pre-rotated next key |
| Pre-rotated next key | Offline: a recovery kit (printed code or a second device), never on the phone | A stolen or coerced phone can't rotate the account away |
| Backup recovery key export | Face ID or Touch ID plus device passcode | Rare and high-impact |
| App unlock | Face ID or Touch ID, passcode fallback; on by default with a short grace period | Protects an unlocked phone handed to someone else |
| Local store key | Released after app unlock, wiped from memory when the app locks | Message history is unreadable while the app is locked |
| Device (MLS) key for routine messaging and calls | No per-message prompt; available only while the app is unlocked or after first unlock, per the setting below | Prompting for every message is unusable, and receiving needs the key |

Receiving while locked: incoming packets go into a queue file with `NSFileProtectionCompleteUnlessOpen`, which can be written while the phone is locked but read only after unlock, so new messages are stored safely without exposing history. Lock-screen previews need decryption while locked, so they are off by default and the notification says only "New message".

Coercion: a setting can require the passcode instead of Face ID for app unlock, because a face can be forced in a way a passcode can't. iOS's emergency SOS gesture already disables biometrics until the next passcode entry, and the app explains this. Touch ID on Macs (Apple silicon, or a Magic Keyboard with Touch ID) uses the same policies; Android's StrongBox with BiometricPrompt is the equivalent later.

Panic wipe: iOS doesn't let third-party apps read side-button or volume-button press patterns (the Side Button Access entitlement is only for launching voice assistants in Japan). Instead:
- A "Panic" App Intent that the user can put on the Action Button, a Control Center or Lock Screen control, or a Back Tap shortcut. App Intents run on the device; this doesn't involve Siri.
- A duress passcode on the app unlock screen that wipes while appearing to open an empty app.
- An optional wipe after a set number of failed app-unlock attempts.
- The wipe is a crypto-erase: delete the Secure Enclave key that wraps the database key and the identity and device keys, so the encrypted store becomes unreadable at once, then delete the files. Behavior when triggered while the phone is locked (the keychain may refuse deletes) must be tested on devices; the fallback is to lock the app and finish the wipe on the next unlock without showing anything first.

## App design (decided)

- **Native first.** SwiftUI on iOS 26 Liquid Glass components (glass tab bar, toolbars, sheets), one codebase for iPhone, iPad and Mac with a three-column split view on iPad and Mac. Dynamic Type, VoiceOver and Reduce Motion supported from the start.
- **No custom chrome.** Default `NavigationStack` bars with large titles and glass toolbar buttons, the stock `TabView` with a search-role tab, `Menu` for pull-down menus, `.contextMenu` with previews on long press (reactions sit above the menu), `.swipeActions` on chat rows (leading Pin and Read, trailing Mute and Archive) and `.searchable`. The brand shows up only in content: colors, the crescent mark and moon-phase timers.
- **Monochrome, spacey identity.** Khensu is the Egyptian moon god, "the traveller":
  - Monochrome: true-black and graphite surfaces, silver for your bubbles, starlight white for actions, verified badges, unread counts and mentions. Red only for destructive actions and ending calls. Dark and true-black themes first, plus a light theme.
  - Connected-dot node networks, in the style of moqom.cloud's relay web, are the recurring motif: spatial-audio calls show each voice as a lit node on a sphere around you, the lock-screen and empty-state wallpapers are slowly turning dot networks, and the node app shows the live mixnet the same way. Motion respects Reduce Motion.
  - The app icon is a white ring whose left side fills into a pointed crescent, with no gap, on a black tile, in the default, dark and tinted icon styles.
  - Moon phases show disappearing-message timers (the moon wanes as a message nears expiry).
  - Typography: SF Pro for the interface, with a display face for the wordmark only.
- **Telegram-like layout.** Chat folders as tabs at the top of the chat list (All, Personal, Groups, Channels, Unread, custom folders); swipe to pin, mute, archive or mark read; replies, reactions, threads, polls, stickers and voice and video notes in the chat view. Bottom tabs: Chats, Calls, Search ("Ask khensu"), Settings.
- **Visible but quiet security.** A white check on verified contacts, the four-word check phrase on profiles, and a Face ID unlock screen styled like the lock screen. There's no crypto jargon in the main interface; details live under "Encryption" on each chat.
- **Node app (`nu.khensu.tatenan`).** A macOS menu-bar app in the same palette, showing node status, schedule and earnings.

## Local search and memory: a Hindsight-style engine on the device (iOS 26+, macOS 26+)

Search can't use a server: no node ever holds plaintext. So the device runs its own memory engine modeled on [Hindsight](https://hindsight.vectorize.io/) (MIT-licensed, so its design and extraction prompts can be adapted with attribution). Hindsight itself is Python on Postgres with pgvector, so this is a Swift reimplementation in a new package, `KhensuMemory`, on the app's encrypted SQLite store. Minimum OS is iOS 26 and macOS 26 (Foundation Models' first release); iOS 27 features are used when available.

```mermaid
flowchart LR
    Msg[Decrypted messages, voice notes, images] --> Retain
    Retain -->|"FTS5 + embeddings"| Index[Search index]
    Retain -->|"Foundation Models, @Generable"| Facts[Facts and entities]
    Facts --> Consolidate[Observations]
    Query[Search or question] --> Recall
    Index --> Recall
    Facts --> Recall
    Consolidate --> Recall
    Recall -->|"token-budgeted context"| Reflect[Reflect: answer with citations]
```

- **Retain** (on unlock, as messages arrive):
  - Every message goes into an FTS5 full-text index (BM25) immediately. Exact search works on every iOS 26 device, offline, with no AI.
  - Conversation windows are embedded on the device with Apple's `NLContextualEmbedding` (multilingual, no model to ship) and stored as int8 vectors in the same database (sqlite-vec or a small HNSW index).
  - On Apple Intelligence devices, Foundation Models extracts typed facts with `@Generable` structs: plans and dates, decisions, addresses, links, things people asked you, and the entities they mention (people, places, organizations). Each fact links to its source message IDs.
  - Voice notes are transcribed with `SpeechTranscriber` and images get on-device text recognition and labels from Vision (iOS 27's multimodal on-device model adds image descriptions), so both are searchable.
- **Recall** runs four searches in parallel, as Hindsight does: keyword (BM25), semantic (vectors), graph (facts sharing an entity, up to two hops) and temporal ("last spring" parsed into a date window). Results are fused by rank (reciprocal rank fusion), then cut to a token budget rather than a fixed count, which suits the on-device model's 4,096-token context.
- **Observations**: while the app is open, or unlocked and charging, a worker merges related facts into durable observations ("Ana moved the Lisbon trip to 12–19 May") with evidence links and history, and marks them stale when new facts arrive.
- **Reflect** ("Ask khensu"): a Foundation Models session with tool calling (`Tool` protocol) over recall, which gathers evidence in a few rounds and answers with citations to the exact messages. It reads observations first, then facts, then raw messages. "Catch me up" summaries for chats with many unread messages are a reflect query scoped to the unread range, summarized in chunks to fit the context.
- **Privacy rules:**
  - On-device model only; the Private Cloud Compute entitlement is never requested, and a build check fails if `PrivateCloudComputeLanguageModel` appears in the code.
  - Runs only after Face ID unlock. The database uses Complete Protection, so nothing is indexed or readable while locked; the notification extension never touches it.
  - Facts, observations and embeddings count as message content: deleting or expiring a message deletes every fact and vector derived only from it and re-checks observations citing it. Derived data inherits the chat's shortest disappearing timer.
  - The index is never backed up or synced. A new or linked device rebuilds it from the restored messages.
  - A per-chat switch excludes a chat from memory. Members are told this only controls their own device, since anyone who can read a chat can index it.
- **Devices:** keyword and semantic search work on every iOS 26 device. Facts, observations, reflect and "Catch me up" need Apple Intelligence (iPhone 15 Pro and later, M-series Macs and iPads); other devices just don't show those features.
- **Later:** Hindsight's mental models and knowledge pages, such as a pinned "Lisbon trip" page that updates itself, and a small Core ML cross-encoder reranker if recall quality needs it.

## Push notifications

No message content, sender or conversation ever goes through Apple or our push gateway. Three user-selectable modes:

| Mode | What the lock screen shows | What Apple and our gateway learn |
| --- | --- | --- |
| **Anonymous** (default) | "New message", no sender, no preview | That this device got a wake at about this time |
| **Off** | Nothing; messages arrive when the app opens or during background refresh | Nothing |
| **Previews** (opt-in) | Sender and text, decrypted on the device | Same as Anonymous; the content stays on the device but is visible on the lock screen |

How Anonymous works:
1. The app registers with the push gateway (`push.khensu.nu`) through the mixnet. The gateway returns a **wake capability**: the APNs device token encrypted to the gateway's own key. The app gives this capability, sealed, to its mailbox replicas.
2. When a packet arrives, a mailbox node passes the capability to the gateway. The gateway decrypts it and sends APNs a fixed "New message" alert with `mutable-content`. The mailbox never learns the device token; the gateway never learns the mailbox, the sender or the address.
3. On the phone, the Notification Service Extension wakes, fetches the sealed packets, writes them to the `CompleteUnlessOpen` queue (writable while locked), and leaves the text as "New message". Nothing is decrypted while locked, so Apple Intelligence's own notification summaries have nothing to read.
4. The gateway delays wakes by a random 0 to 20 seconds and merges several into one, so push timing reveals less about message timing. Wake capabilities and mailbox IDs rotate every epoch, so even a gateway colluding with a mailbox node only links them briefly. If Apple grants the notification-filtering entitlement, the extension can also drop random dummy wakes (cover pushes).
5. The gateway is stateless, keeps no logs, and is open source. It is the one service we must run, because APNs is tied to our developer account.

Calls: a PushKit VoIP push wakes the app and CallKit shows "khensu.nu call" (the caller's name only in Previews mode). `includesCallsInRecents` is off, so calls never appear in the Phone app's history, which iCloud syncs.

## Typing indicators and presence

- **Typing stream.** Each member has an ephemeral typing stream per conversation, encrypted with a key from the MLS exporter for the current epoch. Phones only send events for, and only listen to, the chat on screen. Groups show "Ana and 2 others are typing".
- **Over the mixnet, like everything else.** Typing events are ordinary fixed-size Outfox packets that replace cover packets in the client's constant-rate stream, so sending one doesn't change how much traffic a phone emits. They are coarse (start, stop, and a refresh every 10 seconds) and arrive with the same few seconds of mix delay as messages, so receivers expire the indicator after 30 seconds of silence. They are never stored in mailboxes and never trigger a push.
- **Settings.** Turning typing indicators off stops sending yours and showing others', as on Signal. Read receipts are encrypted messages with the same reciprocal switch. "Online" presence is off by default.

## Apple platform features in v1

Capabilities and reasons are listed in [khensu-app-id-capabilities.md](khensu-app-id-capabilities.md). Features that ship in v1:

- **Offline nearby mode (Wi-Fi Aware).** When there's no internet, phones carry each other's sealed Outfox packets and hand them to the mixnet once any of them reaches the internet. Content stays end-to-end encrypted and carriers can't tell sender or recipient, but nearby phones can tell a khensu.nu user is close by, so this mode is opt-in.
- **Tap to add and verify.** Touch phones (Tap to Share / NFC) to exchange addresses and confirm safety numbers, alongside QR codes.
- **Push to Talk.** Walkie-talkie mode for groups using Apple's PTT framework; voice clips travel through the mixnet like any message.
- **Spatial audio in calls and voice rooms.** Each speaker is placed at their own position around the listener with `AVAudioEngine`'s spatial mixer, using the user's Personalized Spatial Audio profile (Spatial Audio Profile capability) and AirPods head tracking (Head Pose capability). Mixing happens on the device after decryption, so relays still carry only encrypted per-speaker streams.
- **Nothing is processed on anyone's servers (decided).** No Siri, no Private Cloud Compute, no cloud speech or translation. Voice features are our own and on-device: dictation with `SpeechAnalyzer`/`SpeechTranscriber` (on-device models), read-aloud with `AVSpeechSynthesizer`, summaries and smart replies with Foundation Models on-device. The composer sets `writingToolsBehavior = .none`, because Apple's Writing Tools can use Private Cloud Compute, and the app refuses third-party keyboard extensions (`shouldAllowExtensionPointIdentifier`), which could log keystrokes. Apple services that remain only ever see content-free data: APNs (a fixed "New message" alert), StoreKit (purchases), App Attest (a one-time device check before blind tokens), Declared Age Range (an age bracket).
- **CarPlay: calls only.** Apple requires SiriKit messaging intents for any messaging in CarPlay, so there is no CarPlay messaging. Calls use the CarPlay Communication entitlement with CallKit; `INStartCallIntent` is handled from the contact list and Recents without enabling Siri. Whether Apple approves calls-only without Siri voice commands is confirmed in the entitlement request.
- **Default messaging and calling app** where iOS allows it (EU first).
- **Communication Notifications** (sender avatar and name) in Previews mode only.
- **Anti-spam without identity.** App Attest is checked once at the credential issuer, then the issuer hands out blind tokens, so the attestation can't be linked to later messages. Trust Insights is not used: Apple's documentation doesn't confirm that its evaluation never involves Apple's servers.
- **Age assurance.** Declared Age Range applies teen defaults (no messages from strangers, sensitive images blurred); Sensitive Content Analysis blurs unsolicited explicit images for everyone who opts in.
- **Web subscriptions.** StoreKit External Purchases links to `khensu.nu` checkout where allowed, alongside In-App Purchase.
- **Not used:** Background Inference, Background GPU Access, Sustained Execution, Increased (Debugging) Memory Limit, Extended Virtual Addressing. Foundation Models runs in Apple's system process, and memory work runs only while the app is unlocked. Sustained Execution would cap performance. Revisit Background Inference only if a shipped Core ML model (such as a reranker) needs the Neural Engine in the background.
- **Apple requests to file early:** notification filtering, CarPlay communication, default messaging/calling app, external purchase.

## Mix packet format: Outfox, extended (decided)

Base: Outfox (Rial, Piotrowska, Halpin, WPES 2025; [arXiv 2412.19937](https://arxiv.org/abs/2412.19937)), a KEM-based redesign of Sphinx for fixed-length layered mixnets with a UC security proof. Nym's Rust implementation, `nym-outfox`, is Apache-2.0, which is compatible with our Apache protocol libraries. Nym has not yet enabled it in its live network.

Outfox leaves replay protection, mixing and cover traffic to the surrounding system. Our extensions, which are the candidate contributions of the paper:
1. **Epoch-bound replay protection for low-memory nodes.** Mix keys rotate with each consensus epoch, so a replay filter only has to remember one epoch, with memory bounds analysed for a Raspberry Pi 5.
2. **A concrete ML-KEM-1024 instantiation**, stating exactly which KEM properties the Outfox proof needs (including ciphertext anonymity, so a header doesn't reveal which node's key it was made for) and showing that ML-KEM-1024 provides them, with the header-size and bandwidth cost measured: about 1.6 KB of KEM ciphertext per hop.
3. **Unlinkable work receipts.** Nodes prove how much mixing they did, for payment, without the receipts helping anyone link packets.
4. **Loop-measurement indistinguishability.** Measurement packets provably look like user traffic, so a node cannot behave well only while being measured.
5. **Post-quantum reply blocks (SURBs) bound to mailbox epochs**, for acknowledgements and mailbox fetches.
6. **Evaluation** on Raspberry Pi 5 and iPhone: throughput, latency, bandwidth with cover traffic, battery.

Paper: "Justin Elliott Staffer, Elliott Wave LLC". It is written after the implementation and evaluation exist, credits the Outfox authors as the base, and has its proofs reviewed by an outside cryptographer before submission. First-time arXiv submitters in cs.CR need an endorsement from an established author. Publishing starts a 12-month US patent clock and ends patentability in most other countries, so the patent decision comes first (the same rule as hindsight-code-brain's `PATENTS.md`).

## Cryptographic design (the parts that must be right)

- **Cipher suite (decided: pure post-quantum).** Messenger groups use ML-KEM-1024, AES-256-GCM, SHA-384 and ML-DSA-65 signatures. Today `0xF0AA` is ML-KEM-768 + ML-DSA-65 and `0xF0A1` is X-Wing + Ed25519, so this is one new suite in all three MLS implementations, with vectors (a private-use value unless draft-ietf-mls-pq-ciphersuites defines it). The mixnet's Outfox headers use ML-KEM-1024 too. To verify: the key transparency log's VRF, since standard VRFs (ECVRF, RFC 9381) are classical and there is no standardized post-quantum VRF yet. A break would only expose lookup privacy, not messages.
- **Cost of no classical fallback, and how we cover it.** With no X25519 alongside, an implementation bug in ML-KEM (like the 2024 KyberSlash timing leak) would expose messages directly. So: use a formally verified ML-KEM-1024 implementation in each language where one exists (for example libcrux or mlkem-native) rather than hand-written code; run NIST's test vectors plus Wycheproof-style negative tests; check constant-time behaviour on iPhone and Pi 5; fuzz every decoder. ML-KEM-1024 keys are 1,568 bytes and ciphertexts 1,568 bytes (vs 1,184 and 1,088 for ML-KEM-768), which only matters for KeyPackages and mix headers.
- **Signatures.** ML-DSA-65 only, by earlier decision. If ML-DSA were broken, an attacker could impersonate going forward, but recorded traffic stays confidential because ML-KEM protects it.
- **Identity.** Per account: an identity key held in the Secure Enclave. Per device: a device key signed by the identity key (the MLS credential). The KT log binds username to identity key. The safety number is the fingerprint of the identity key, checked against the KT proof.
- **Messages.** MLS `PrivateMessage` with the secret tree: per-message keys deleted after use, a sender signature inside the ciphertext, a generation counter for replay protection, and padding to fixed size buckets. Each device sends an Update commit every 24 hours or 1,000 messages, for post-compromise security.
- **Sealed sending.** The outer packet carries no sender. The mailbox ID is derived per conversation and rotated per epoch from the MLS exporter, so mailboxes cannot be linked across epochs.
- **Adding offline contacts.** Directory-published one-time KeyPackages plus a last-resort package (the current `PUT/claim` design, moved onto the KT log and nodes), each signed by the device credential.
- **Attachments.** A random key per file. The file is chunked, padded and stored on mailbox nodes by content hash, and the key and hash travel inside the MLS message.
- **Local storage.** An SQLite store encrypted with a key wrapped by the Secure Enclave and released only after Face ID or Touch ID app unlock, Data Protection class Complete, excluded from iCloud backup. Incoming packets wait in a `CompleteUnlessOpen` queue until unlock. Optional backups are encrypted with a user-held recovery key.
- **Assurance.** A Tamarin or ProVerif model of the add, message and remove flows, Outfox routing and the epoch-header consensus. Fuzzing of every decoder (following the existing `fuzz/` practice). Cross-language vectors for every new wire format. An external audit before public launch.

## Node software, hardware and schedules

A single open-source Rust binary `moqom-node`. Operators pick roles; the epoch header assigns work based on signed leases.

- **Hardware (decided).** Minimum is a Raspberry Pi 5 with an NVMe SSD for all roles; a Pi 4 only for mixing, because it lacks ARM's hardware AES instructions and the suite uses AES-256-GCM. No AI HAT is needed: consensus is limited by messages and network delay, and the cryptography runs on the CPU. A Pi 5 with an AI HAT+ or AI HAT+ 2 can still run a node, but both the HAT and an NVMe HAT need the Pi 5's single PCIe connector: put the SSD in a USB 3 enclosure (which gets its own bandwidth through the RP1 chip) or use a PCIe switch board (shared bandwidth, 5 W power limit on the connector). Use the official 27 W power supply and active cooler. Microcontrollers are out of scope (not enough memory for QUIC plus post-quantum TLS). Ship a ready-to-flash Pi image alongside the macOS app.
- **Lease modes:** always-on (long, auto-renewing), scheduled (recurring windows), N-hours (one fixed lease), idle-time (short, renewed while idle, using HID idle time, AC power, thermal state, and unmetered network, with a sleep assertion on opt-in; the same launchd pattern as hindsight-code-brain).
- **Role eligibility by lease:** committee duty, call relays and sequencers need a lease covering the whole epoch (always-on or scheduled). Mixing needs the lease to cover a whole epoch. Mailbox replicas and cover traffic accept any lease mode.
- **Draining before a lease ends:** stop taking new calls and send GOAWAY; hand mailbox contents to other replicas; hand sequencer duty to the standby; enter only lotteries and epochs that fit inside the lease.
- **Path selection:** spreads hops across operators, network providers and countries, weighted by reputation and capped per operator.
- **Desktop app:** a notarized macOS menu-bar app (outside the Mac App Store) wrapping the node, with an idle throttle and earnings view.
- **Operator site and bootstrap:** `tatenan.khensu.nu` hosts the node software, Pi image, operator docs and a seed list. Apps and nodes pin the genesis keys and ship an embedded seed list, so the network keeps working if that domain is blocked or seized.

## Money

- **Subscriptions.** Users buy a subscription (App Store, web, or the token) and receive a batch of blind-signed access credentials, so payment is never linked to usage. Subscribers never receive tokens.
- **Burn and mint (decided).**
  1. Example: $4.99 a month, minus Apple's 15% (Small Business Program, or after the first subscription year), is about $4.24.
  2. A fixed share (for example 50%, about $2.12) is your revenue.
  3. The rest buys the token and burns it for capacity credits, priced in dollars, the same way any customer pays for bandwidth.
  4. The protocol mints new tokens to operators each epoch in proportion to the work receipts root (packets mixed, bytes stored over time, relay minutes, committee duty), on a declining emission schedule. The company never pays operators directly.
  5. Your costs are a fixed share of net revenue, so the business is profitable once that share covers fixed costs; price swings affect operators' token income, not your margin. More usage means more burned, which is where the token's value comes from.
- **The world's media.** MOQOM Cloud customers pay in dollars for delivery on operator nodes, and that money is burned the same way, so demand comes from all MOQOM traffic, not just messenger subscriptions. MOTOM keeps handling the fiat side (Stripe) for these customers.
- **Launch liquidity: the burn auction.** Before any exchange lists the token, each epoch runs a sealed-bid batch auction on our chain: the burn buyers (khensu.nu and MOQOM Cloud) post a dollar budget, operators and holders offer tokens, everything clears at one price, the tokens are burned, and sellers are paid through MOTOM or a stablecoin. This gives price discovery from day one.
- **Rules that keep it a utility token** (the March 2026 SEC/CFTC interpretation treats a token as a digital commodity when its value comes from a functional network and supply and demand, and as a digital security when it conveys rights to a business's income):
  - Never promise a price or returns; no revenue share, dividends or company-funded yield for holders.
  - The token's uses are staking (operator bond), paying for capacity, and shielded payments.
  - Phones never earn tokens (App Store guidelines 2.4.2 and 3.1.5(ii)); there are no referral or task rewards (3.1.5(v)).
  - Any token sale needs an exemption (Regulation Crypto Assets is still a proposal); an EU listing needs a MiCA white paper; your own genesis nodes' rewards are disclosed.
  - Counsel signs off before anything is minted.
- **Also:** enterprise and self-hosted networks are paid in dollars.

## Shielded payments over the mixnet (v1, decided)

Users send money to each other with no record of who paid whom, and no lasting record at all beyond what prevents double-spending.

- **Notes, not balances.** Money inside the pool exists as notes of fixed denominations (1, 2, 5, 10, ...), so amounts are hidden too. Each note is a commitment on our chain; its contents are encrypted to the owner with ML-KEM-1024.
- **Spending.** The phone proves with a STARK (hash-based, so post-quantum) that it owns an unspent note in the current commitment tree, and publishes only that note's nullifier (a spend tag that can't be linked to the note) plus the new notes. Proving takes a few seconds on an iPhone or Mac.
- **Transfers are mixnet messages.** The new note's secrets go to the recipient as an ordinary end-to-end encrypted message, and the spend is submitted to the committee through the mixnet, so no node sees sender, recipient, amount or IP.
- **Expiring eras.** Notes belong to an era (for example one month). The wallet refreshes notes into the next era automatically, in the background while unlocked, within a grace period. When an era closes, its commitment tree and nullifier list are deleted from every validator. Only the current eras are kept.
- **Entering and leaving.** Tokens enter and leave the pool from public accounts; only those deposits and withdrawals are visible. Sanctions screening applies at that boundary. Funding is from outside wallets or exchanges, never through In-App Purchase.
- **Non-custodial.** Nobody, including you and the committee, holds users' funds or can freeze a note; the committee only checks proofs and nullifiers. That is the legally safer category (the Justice Department said in April 2025 it would stop charging non-custodial software developers as unlicensed money transmitters without evidence of intent), but it still needs counsel and per-region App Store licensing (3.1.5(iii)).
- **In the app.** "Send money" in any chat, a Wallet screen with notes and history kept only on the device (deleted with the chat's timer if set), Face ID for every spend, and the recovery phrase also restores notes.

## Compared with existing post-quantum coins

Existing post-quantum coins each solve one layer. khensu.nu's chain is designed to be post-quantum at every layer, with privacy that doesn't depend on a permanent record:

| | QRL | Algorand | Abelian | Zcash / Monero | khensu.nu chain |
| --- | --- | --- | --- | --- | --- |
| Signatures | XMSS (stateful: an address can only sign a fixed number of times) | Falcon opt-in; accounts still Ed25519 | Lattice (custom) | Classical | ML-DSA-65 (FIPS 204, stateless) everywhere, including consensus |
| Payment privacy | None | None | Yes, lattice-based | Yes, but classical: a future quantum computer could decrypt archived note data | STARK proofs (hash-based) plus ML-KEM-1024 note encryption |
| Network privacy (who sent it, IP) | None | None | None | Partial (Dandelion++ in Monero) | Post-quantum mixnet with cover traffic |
| History | Permanent | Permanent | Permanent | Permanent: anything broken later exposes all of history | Shielded eras deleted; only balances persist |
| Demand | Speculative | Smart contracts | Payments | Payments | Burned for real media and messaging capacity |
| Node hardware | Server | Server | Server | Server | Raspberry Pi 5; light clients check about 14 signatures per epoch |

Where we're behind and must earn it: a new chain has no track record (QRL has run since 2018), no liquidity until the burn auction and listings, and larger transactions (ML-DSA-65 signatures are 3.3 KB and STARK proofs tens of KB, so proofs are aggregated per block and dropped with old blocks). The plan's answer is formal models, external audits of the chain and the pool, and a long public testnet before mainnet.

## Launch readiness

### 1. Encryption export compliance
- The app and node software contain non-exempt encryption: set `ITSAppUsesNonExemptEncryption = YES` and answer App Store Connect's export questions as mass-market encryption (classified 5D992.c once it qualifies under License Exception ENC §740.17(b)(1)).
- Confirm with export counsel which reports still apply after BIS's 2021 simplification (self-classification report; email notice for publicly posted source code if any algorithm counts as non-standard, which our Outfox extensions might).
- France: Apple asks for the French encryption declaration (ANSSI) before distribution there. File it with the first App Store submission.
- Node binaries and source on GitHub fall under the same classification; publish the classification on `tatenan.khensu.nu`.

### 2. Legal entities and documents
- **Operating company:** Elliott Wave LLC, or a dedicated khensu company. It holds the Apple developer account (enrolled as an organization, which App Store guideline 3.1.5(i) requires for wallets), runs the push gateway and credential issuer, and receives App Store proceeds.
- **Network and token:** the token issuer and network treasury sit in a separate entity chosen with counsel (a foundation, or a Wyoming DUNA for the network once it reaches the "established" stage). The company is then one burn buyer among others.
- **Documents:** terms of service, a privacy policy matching the App Store privacy label ("Data Not Collected" is the target), operator terms, token disclosures, law-enforcement guidelines, and a security disclosure policy (`security.txt`, bug bounty).

### 3. Trust and safety without reading messages
- **Built in:** block and report in every chat. Reports carry message franking, so a reported message is provably what was sent without breaking anyone else's encryption. Strangers land in message requests with media blurred and links inert until accepted. Rate-limit tokens and App Attest throttle spam, teen defaults come from Declared Age Range, and Sensitive Content Analysis blurs unsolicited explicit images.
- **Child safety:** no scanning of encrypted content. Content a user reports that is child sexual abuse material is reported to NCMEC, as US law requires once a provider has actual knowledge. Public channels and handles are moderated like any public content.
- **Law enforcement:** we hold almost nothing (no phone numbers, no contacts, no message metadata, no push logs). Publish law-enforcement guidelines, a twice-yearly transparency report, and a warrant canary.
- **Regulation:** the EU Digital Services Act mostly applies to public channels; the UK Online Safety Act needs illegal-content and children's risk assessments. Stated policy, like Signal's: we will not add client-side scanning, and would withdraw from a market rather than weaken encryption. Track the EU's CSAM regulation.

### 4. Network bootstrap and minimum anonymity
- **Genesis:** at least 9 founder nodes across 3 cloud providers and 3 countries, plus invited operators on testnet.
- **"Private network" threshold** before the app drops its "early network" notice: at least 30 mix nodes, 10 independent operators, 5 countries and 5 network providers, with no operator holding more than 20% of mixing capacity, all enforced by consensus.
- **Honest UI:** until the threshold holds, the app shows an "Early network" banner explaining that anonymity grows with operators and users. Content encryption is full strength from day one.
- **Testnet incentives:** any testnet reward that converts to tokens is an airdrop question for counsel; default to none.

### 5. Battery and data budget
- **iOS limits:** iOS suspends background apps, so phones send cover traffic only while the app is open. In the background, the Notification Service Extension only fetches. Queued messages leave at the cover rate when the app next opens, or immediately in the extension if the user replies from a notification.
- **Two packet sizes,** both mixed: a small packet (about 10 KB on the wire: roughly 8 KB of ML-KEM-1024 headers for 5 hops plus a 2 KB payload) for messages, receipts and typing, and a bulk packet (about 72 KB, with a 64 KB payload) for attachment chunks. Each size has its own cover traffic, so attachments stay in the mixnet.
- **Rates (to tune on devices):**

| | Wi-Fi | Cellular | Low Power Mode |
| --- | --- | --- | --- |
| Small-packet cover, app open | 1 every 2 s (about 18 MB per hour) | 1 every 10 s (about 3.6 MB per hour) | Real traffic only |
| Bulk lane | On | Off by default; attachments wait for Wi-Fi unless the user taps send now | Off |

- **Budget:** under 3% battery and under 50 MB of cellular data a day for typical use. MetricKit (on the device only) verifies this in beta.

### 6. Contact discovery, invites and growth
- **No phone or email discovery in v1.** It needs SMS verification (a central party) and phone hashes are easy to reverse. People connect by handle, QR code, tap to add, or invite link.
- **Invite links:** `khensu.nu/i/#...` with a one-time key in the URL fragment, which browsers never send to the server. The link opens the App Store; the app picks up the invite after install and connects both people.
- **Growth loops:** group invite links, channels with public handles, "message me on khensu" profile links, and ENS names for web3 users. Signal and Telegram history import is a later option.

### 7. Pricing and token numbers (starting proposal)

| Tier | Price | Includes |
| --- | --- | --- |
| Free | $0 | 1:1 and groups, calls, 100 MB attachments, 30-day mailbox history, 3 devices |
| Plus | $4.99/month | 2 GB attachments, encrypted backups, 10 devices, custom icons and themes |
| Family | $9.99/month | Plus for 6 people |
| Business | Per seat | Admin roles, compliance exports done on members' own devices, self-hosted network option |

- **Free users carried per subscriber (estimate):** a text-heavy free user generates about 2 GB a month on the mixnet, or about 6 GB of node bandwidth across three hops. At about $0.005 per GB for operators, that's about $0.03 a month. One Plus subscriber's operator share (about $2.12) covers roughly 70 free users. Validate on testnet.
- **Token (proposal for counsel):** 1 billion at genesis. Emission starts at 8% a year and halves every 2 years. Net supply falls once burns exceed emission. Allocation: 20% company with a 4-year vest, 15% ecosystem and grants, 5% burn auction liquidity reserve, and the rest held by the network treasury with time locks.

### 8. Operations without telemetry
- **Crash reports:** opt-in, using MetricKit diagnostics, scrubbed on the device and sent through the mixnet. No third-party SDKs.
- **Network health** comes from consensus measurement itself, which is public: a status page at `status.khensu.nu` built from epoch headers.
- **Build integrity:** node binaries are reproducible (Go and Rust) and signed with the founder threshold key. App releases publish source tags and build hashes in a binary transparency log; App Store encryption prevents byte-for-byte reproduction on iOS, so this is documented honestly.
- **Incidents:** on-call runbooks for the push gateway, credential issuer, KT log and committee. Key compromise and emergency procedures follow the 48-hour tighten-only path.

### 9. Platforms
- **Nodes:** Linux (Raspberry Pi image and Docker) at testnet; macOS app at testnet; Windows app about 6 months later.
- **Clients:** iOS, iPadOS and macOS at v1; Android about 6 to 9 months after v1 (StrongBox keys, BiometricPrompt, UnifiedPush or FCM wake-only). There's no web client: web apps re-download their code on every visit, so the server could ship a backdoor at any time. Linux and Windows desktop clients follow Android.

### 10. Team, budget, timeline and scope cuts
- **Phases (estimate):**
  - Months 0–3: threat model, protocol spec, legal and export work, design mocks.
  - Months 3–12: MLS hardening and TreeKEM, node core, consensus testnet, app alpha.
  - Months 12–18: mixnet, Outfox paper, shielded payments, key transparency, audits.
  - Months 18–24: public testnet, mainnet, App Store launch.
- **Team:** 2 iOS engineers, 2 protocol engineers (Go and Rust), 1 cryptographer, 1 zero-knowledge and chain engineer, 1 SRE, a designer, plus part-time counsel. Roughly $2.5M–$4M over 24 months including audits ($300k–$1M across MLS, chain, shielded pool and app).
- **What can slip to v1.1 if the schedule needs it:** shielded payments, Wi-Fi Aware offline mode, CarPlay, Push to Talk, knowledge pages. Messaging, calls, the mixnet, key transparency and the token stay in v1.

## Repository layout

- `moqom-messenger/docs/` – `THREAT-MODEL.md`, `PROTOCOL.md` (wire formats), `NODE.md`, `CONSENSUS.md`, `GOVERNANCE.md`, `KEY-TRANSPARENCY.md`, `CREDENTIALS.md`, `PUSH.md`
- `moqom-messenger/node/` – Rust workspace: `moqom-node` binary; crates `outfox`, `mix`, `mailbox`, `sequencer`, `lease`, `consensus` (sortition, BFT, epoch headers, light verification), `measure`, `receipts`, `governance`
- `moqom-messenger/services/` – Go: KT log, credential issuer, push gateway, MOTOM integration for fiat purchases and burn auction payouts (Go to match `moqom-pq` and `motom`)
- `moqom-messenger/apple/` – `MessengerKit` Swift package plus the iOS and macOS apps and the macOS node app
- `moqom-messenger/pi/` – reproducible Raspberry Pi 5 image build
- `moqom-messenger/vectors/` – Outfox, mailbox ID, epoch header, sortition, receipts and credentials vectors, checked in Rust, Go and Swift
- `moqom-security/` – the new suite, TreeKEM, `PrivateMessage` with the secret tree, signed credentials, and their vectors in all three languages

## Milestones

1. **Specs and threat model.** The adversaries covered (a global passive observer, malicious nodes up to a threshold, a captured committee minority, a malicious log, a stolen founder share, a seized device, a quantum adversary harvesting now to decrypt later) and the ones explicitly out of scope (endpoint malware, a global active adversary for live calls). Wire formats frozen before code.
2. **MLS hardening in `moqom-security`:** the ML-KEM-1024 + ML-DSA-65 suite with verified ML-KEM implementations, the ratchet tree (TreeKEM), PrivateMessage and secret tree, signed credentials, Update policy. Vectors in three languages plus the public mlswg tree and message vectors, Tamarin model.
3. **Network core:** `moqom-node` with mailbox, sequencer and relay roles, leases and draining; the consensus layer (sortition, BFT, epoch headers, measurement); founder key ceremony and genesis; a testnet with at least 3 outside operators, including Pi 5 nodes.
4. **Mixnet and anonymous credentials:** Outfox, three-layer mixing, cover traffic, the blind-signature issuer, node receipts.
5. **Directory:** KT log with witnesses, usernames, KeyPackage publishing, lookups over the mixnet. Phone and email discovery deferred until a private contact discovery design is approved.
6. **Apple clients:** MessengerKit, chat (1:1 and groups up to 1,000 devices), attachments, disappearing messages, safety numbers, multi-device linking by QR code, encrypted local store and backups, the push gateway integration.
7. **Calls on the network:** MoqomKit calls over two-hop node relays, direct paths opt-in per contact.
8. **Operator economy:** the macOS node app and Pi image with idle, scheduled and N-hour modes; reputation scoring; token staking and slashing; protocol rewards; burn auction. Shielded payments ship in the same v1 release after legal review.
9. **Audit and launch:** external crypto, protocol and consensus audit, a bug bounty, supply-chain hardening, then public launch in the genesis stage.

## Decisions

Decided:
- Licence: AGPL-3.0 node and apps with a CLA, Apache-2.0 protocol libraries.
- KT witnesses: the existing transparency-dev and Sigsum witness networks.
- Groups: TreeKEM before launch, up to 1,000 devices.
- Signatures: ML-DSA-65 only. Key exchange: pure ML-KEM-1024, no classical KEM (chosen over the hybrid recommendation, with the mitigations in Cryptographic design).
- Routing: every message, receipt and typing event goes through the mixnet; there is no instant path for chat. Calls are the one exception and use two relays run by different operators, because a mixnet's delays can't carry live audio.
- Consensus: our own lightweight post-quantum chain; weighted sortition of a 21-member committee per epoch; only balances and stakes persist, history is pruned.
- Token: burn and mint on our own chain; a fixed share of net proceeds is revenue, the rest buys and burns the token for capacity; the protocol mints operator rewards from work receipts; burn auction for launch liquidity. Name, supply and genesis allocation set with counsel.
- Sybil resistance: reputation multiplied by staked tokens, with slashing.
- Payments: non-custodial shielded pool with STARK proofs and ML-KEM-1024 note encryption, expiring eras, transfers over the mixnet; ships in v1, region by region after legal review.
- Rule changes: founder plus 2/3 of the committee, 30-day timelock with veto, 48-hour tighten-only emergencies.
- Founder safeguards: 3-of-5 ML-DSA threshold key; staged powers; step-down signed by the founder once thresholds have held for 90 days.
- Hardware: Raspberry Pi 5 with NVMe minimum; Pi 4 for mixing only.
- Mix packets: Outfox with our extensions, published as an arXiv paper after a patent decision.
- Names: the app is **khensu.nu** (website `khensu.nu`, already owned), iOS and macOS bundle ID `nu.khensu.ptah`, node network and operator site at `tatenan.khensu.nu`; code name `moqom-messenger`. Addresses use the bech32m prefix `khensu`; permanent handles are `name.khensu.nu` (resolvable in ENS through a DNSSEC import of `khensu.nu`). Trademark and App Store name searches for "khensu" still to run.
- Groups: capped at 1,000 devices; no larger groups.
- Minimum OS: iOS 26 and macOS 26; iOS 27 features used when available.
- Search and memory: a Hindsight-style engine running entirely on the device with Foundation Models; the Private Cloud Compute entitlement is never requested.
- Biometrics: Face ID or Touch ID required for every identity-key action and for app unlock; identity key bound to the enrolled biometrics; no per-message prompts.
- Identity: permanent 32-byte bech32m addresses with KERI-style pre-rotation; optional permanent unique handles that also resolve as ENS subnames through a CCIP-Read resolver; a four-word check phrase for verification; opt-in wallet links via Sign-In with Ethereum and ENS.

Verified (9 Oct 2026):
- Signal key transparency: shipped to all users in 2026 as Automatic Key Verification; phone-number contacts only; Cloudflare and Trail of Bits as auditors; up to 7-day split-view window. Advantage 6 reworded accordingly.
- Signal SPQR: enforced for new registrations from 6 March 2026, with accounts lacking SPQR support being unregistered (reported by signal-cli maintainers). Signal's message encryption is post-quantum; its identity signatures are still classical, so advantage 1 stands.

To verify in milestone 1:
- Which signature scheme Signal's key transparency log uses, before claiming post-quantum log signatures as a difference.
- ML-DSA support in Google Cloud KMS for the founder HSM share.

Competitor facts live in a dated, sourced table in `THREAT-MODEL.md` and are re-checked before launch and before any public comparison is published.
