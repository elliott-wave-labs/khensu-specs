# webË

Draft 0.1, 9 Oct 2026. Status: design; the basis for a family of Internet-Drafts.

webË is an internet run by the people on the khensu.nu node network: names without DNS, content without CDNs, websites, public feeds, forums and live media, all delivered over a post-quantum stealth network with no metered bandwidth. Nodes only relay, cache and count; encoding, encryption, ranking, moderation and rendering happen on devices. The khensu.nu app is the first webË application: primarily a messenger, with a Feed tab, public forums and site hosting from day one.

Wire primitives, encodings and the mixnet are as in `PROTOCOL.md` (sections 1, 3, 8, 9); this document adds the webË layers. Stealth rules are in `PLAN.md` (Stealth) and `design/stealth-relay.md`.

## 1. Goals

1. **No central naming.** Names resolve from the key transparency log, never from DNS, registrars or certificate authorities.
2. **No central hosting.** Content is content-addressed, signed by its publisher, erasure-coded across operators and served by any node.
3. **Stealth access.** Nobody learns who published or who read what, even for public content.
4. **Speech stays up.** Nothing is removed from the network for being unpopular; the only network-level exception is the illegal-content hash list (`OPEN-QUESTIONS.md` 40).
5. **Runs itself.** Operators are paid by the protocol from work receipts; users never pay per byte.
6. **Post-quantum throughout.** ML-KEM-1024 and ML-DSA-87 only.

## 2. Layers

| Layer | What it does | Spec |
| --- | --- | --- |
| Transport | Outfox mixnet (stealth ticks), two-relay MOQ paths over padded trunks | `PROTOCOL.md` 7.1, 8 |
| Naming | `name.khensu.nu` resolved from the transparency log through PIR | 3 |
| Objects | Content-addressed chunks, manifests, signed roots | 4 |
| Fetch and publish | Two-relay stealth fetch, publish through ticks or the owner's node | 5, 6 |
| Applications | Sites, feeds, forums, live tracks | 7–10 |
| Clients | khensu.nu app viewer, Chromium extension and patch | 11 |

## 3. Names

### 3.1 Form

A webË name is a khensu handle: `name.khensu.nu`, with optional subnames (`blog.name.khensu.nu`) controlled by the same identity. Names are permanent, non-tradeable and resolved only from the log. Content can also be addressed directly by hash (3.4).

### 3.2 Name record

The log (`PROTOCOL.md` 3, entry types) gains a webË record, signed by the identity key:

```
struct {
  opaque handle<V>;              // "name" or "blog.name"
  uint64 sequence;               // strictly increasing per handle
  opaque site_root[32];          // H256 of the current SiteManifest, or zero
  opaque feed_head[32];          // H256 of the newest FeedEntry, or zero
  opaque forum_roots<V>;         // H256 of ForumManifest records
  opaque track_namespace<V>;     // MOQ namespace for live tracks, or empty
  opaque publish_key[2592];      // ML-DSA-87 key that signs this name's content
  opaque signature<V>;           // Sign(identity key, "webe name", fields above)
} NameRecord;
```

`publish_key` lets the owner's devices sign content without using the identity key; rotating it is a new record.

### 3.3 Resolution

1. The client hashes the handle to its PIR shard (`OPEN-QUESTIONS.md` 3) and queries a mirror inside the stealth ticks.
2. The mirror returns the latest `NameRecord` with an inclusion proof against a witnessed checkpoint no older than 24 hours.
3. The client verifies the proof, the checkpoint cosignatures and the record signature, then caches the record for its validity (default 10 minutes for sites, 1 minute for feeds).

No resolver is trusted: a wrong answer fails the proof.

### 3.4 URLs

- `webe://name.khensu.nu/path?query`: a site path, resolved through the name record.
- `webe://h/<base32 hash>`: an immutable object or manifest.
- `https://name.khensu.nu/path`: the same resource for links shared outside webË. webË clients treat it as `webe://`; ordinary browsers reach an optional gateway (3.5).

### 3.5 Gateways (optional)

Operators may run gateways that serve public webË content to ordinary browsers over the public web, under `*.khensu.nu` DNS. Gateways are not stealthy (they see the reader's IP and request) and show a banner saying so. They are a bridge for reach, not part of webË. Whether to run any is `OPEN-QUESTIONS.md` 56.

## 4. Objects

### 4.1 Chunks

Content is split into chunks of at most 64 KiB. A chunk's address is `H256(Label("webe chunk") || chunk)`. Files larger than one chunk are a tree of chunk lists:

```
struct {
  uint64 total_length;
  opaque chunk_addresses<V>;     // 32 bytes each, in order; or addresses of further lists
  uint8  depth;                  // 0 = leaves
} ChunkList;
```

### 4.2 Site manifest

```
struct {
  opaque handle<V>;
  uint64 version;
  opaque previous[32];           // previous manifest address, or zero
  struct {
    opaque path<V>;              // "/index.html"
    opaque content_type<V>;
    opaque root[32];             // ChunkList or chunk address
    uint64 length;
  } entries<V>;
  opaque policy<V>;              // headers: CSP, allowed APIs (11.3)
  uint64 published_at;
  opaque signature<V>;           // Sign(publish_key, "webe site", fields above)
} SiteManifest;
```

### 4.3 Storage

- Objects are erasure-coded (Reed–Solomon, 10 data plus 6 parity shards by default) across `channel_cache` nodes from at least 6 operators.
- The publisher's own node (if any) pins everything it published; caches keep popular objects by anonymous demand counts.
- Storage is bounded by anonymous publish quotas per persona per epoch (rate-limit proofs), raised by stake and reputation. Quota sizes are `OPEN-QUESTIONS.md` 57.
- Objects on the illegal-content hash list are refused by caches and by clients.

## 5. Fetch

### 5.1 Two-relay stealth fetch

1. The client picks an entry relay near itself and an exit relay (or cache) holding the object, from different operators, networks and jurisdictions.
2. It opens a WebTransport session to the entry relay (`PROTOCOL.md` 7.1 transport rules) and sends a `FetchRequest` encrypted to the exit relay's ML-KEM-1024 key:

```
struct {
  opaque kem_ciphertext[1568];   // to the exit relay
  opaque sealed_request<V>;      // AEAD: { address[32], range_start, range_end, response_key[32] }
} FetchRequest;
```

3. The entry relay forwards it over the padded trunk to the exit relay. The entry relay knows who, not what; the exit relay knows what, not who.
4. The exit relay returns the object encrypted under `response_key`, padded to the next size bucket (powers of two from 4 KiB), over the trunk and back through the entry relay.

### 5.2 Fetch through the ticks

Name resolution, feed heads and objects up to 8 KiB may instead ride the stealth ticks through the mixnet, which also hides timing from a global observer.

### 5.3 Caching and integrity

Every object is verified against its address before use; manifests are verified against the name record's `publish_key`. Clients cache verified objects locally, encrypted at rest.

## 6. Publish

- Small objects (posts, manifests, name records) ride the stealth ticks to caches and the log.
- Larger objects go through the owner's node stream or the charging window, never as a visible burst (`PLAN.md`, Stealth).
- A publish is complete when shards are confirmed by caches from at least 6 operators (signed store receipts as in `PROTOCOL.md` 6.7) and, for sites and feeds, the new `NameRecord` is in a witnessed checkpoint.

## 7. Sites

- A site is a `SiteManifest` plus its objects: static files and optional WebAssembly. There is no server-side code at launch (`OPEN-QUESTIONS.md` 50).
- The origin for browser security is the name (`webe://name.khensu.nu`). Sites can't fetch from the ordinary web or from other names unless their policy lists them; this blocks third-party tracking by construction.
- Sites can embed feeds, forums and live tracks by reference.

## 8. Feeds

The Feed tab in the khensu.nu app and the public square in `PLAN.md`.

```
struct {
  opaque author_publish_key[2592];
  uint64 sequence;
  opaque previous[32];           // previous FeedEntry address, or zero
  uint8  kind;                   // 1 post, 2 repost, 3 reply, 4 delete-request, 5 profile update
  opaque body<V>;                // text, nu-media references, links, quoted address
  opaque in_reply_to[32];        // or zero
  opaque topics<V>;              // hub tags
  uint64 created_at;
  opaque signature<V>;           // Sign(publish_key, "webe feed", fields above)
} FeedEntry;
```

- Each persona's feed is a hash chain; its head is in the persona's `NameRecord`, so following means watching one record.
- Live updates: a feed head change is also published as an object on the MOQ track `name.khensu.nu/feed`, delivered through two-relay paths, so timelines update in seconds.
- Timelines, replies and threads are assembled on the device. Ranking is the user's own (chronological by default, plus on-device models they choose).
- Likes, reposts and views are anonymous tallies (one rate-limit proof per person per entry), counted by nodes and published per entry per epoch.
- A delete-request entry asks caches to drop an earlier entry; copies already on other devices remain, and the app says so.

## 9. Forums

```
struct {
  opaque name<V>;                // forum name under the owner's handle
  opaque owner_publish_key[2592];
  opaque moderator_keys<V>;      // ML-DSA-87 keys
  opaque rules<V>;
  opaque label_list[32];         // the forum's own LabelList address
  opaque signature<V>;
} ForumManifest;
```

- Threads and posts are `FeedEntry` records with the forum's address in `topics`.
- Forum moderators publish a label list; readers' devices apply it by default when viewing the forum, and any reader can switch to the unfiltered view. Moderation shapes the forum's view; it never removes content from the network.
- Private forums are encrypted groups (up to 1,000 devices) or private channels.

## 10. Labels

```
struct {
  opaque target[32];             // entry or object address
  uint8  label;                  // 1 factual-with-sources, 2 opinion, 3 misleading, 4 fraud-or-scam, 5 spam,
                                 // 6 adult, 7 graphic-violence, 8 satire, 9 ai-generated
  opaque note<V>;                // reason and sources
  opaque proposer_publish_key[2592];
  opaque signature<V>;
} LabelProposal;
```

- Label lists are signed manifests of proposals, published by anyone; users subscribe to any number.
- Consensus labels: anonymous raters (one rating credential per person, `OPEN-QUESTIONS.md` 41) submit ratings as rate-limited proofs; a bridging algorithm shows a label only when raters who usually disagree agree. Ratings and the algorithm are public and deterministic, so every device computes the same result.

## 11. Clients

### 11.1 khensu.nu app

Feed tab, forums inside Feed, and a site viewer: a `WKWebView` with a `WKURLSchemeHandler` for `webe://`, which serves verified objects from the local daemon in `khensu-core`. iOS doesn't let apps intercept `https` in web views, so shared `https://name.khensu.nu` links are rewritten to `webe://` when opened in the app.

### 11.2 Chromium

- **Extension (first):** one WebExtensions codebase for Chrome, Edge, Firefox and Safari. It runs the webË client itself (`khensu-core` in WebAssembly over WebTransport; in Safari, the khensu.nu app through native messaging), so no local daemon or proxy is needed. It catches `https://*.khensu.nu` and `webe://` before they reach the network and shows sites in its own viewer until browsers let extensions serve `webe://` origins. Design and the upstream proposal in `design/browser.md`.
- **Patch (second):** a native webË network service, `webe://` as a standard secure scheme, and stealth defences: fixed window sizes, WebRTC off, restricted high-entropy APIs, no third-party requests.

### 11.3 Site policy

The manifest `policy` lists allowed APIs and other names a site may reference. Clients enforce a strict default: no network access outside webË, no WebRTC, no persistent cross-site storage.

## 12. Standards

Planned Internet-Drafts. Patent assessment and any filings come first, because submitting a draft is public disclosure (`PATENTS.md`):

1. Outfox with ML-KEM-1024: a post-quantum mix packet format (with the Outfox paper).
2. A stealth profile for MOQ: constant-rate media, padded trunks, two-relay paths.
3. Naming from a transparency log: `NameRecord`, resolution and proofs.
4. Signed content-addressed sites and feeds over MOQ.
5. Two-relay stealth fetch.

## 13. Security considerations

- **Global observer:** stealth ticks hide timing for small objects; two-relay fetches hide who fetched what from single relays, and padded trunks plus size buckets hide flows from link observers, but long-term volume correlation at the edges remains (THREAT-MODEL 5.2).
- **Scripts:** a site's code runs in the reader's browser; policy defaults and the Chromium patch limit fingerprinting, as in Tor Browser.
- **Names:** squatting is limited by registration rules in the log; impersonation by look-alike names is countered by safety numbers, verified badges from label lists and on-device warnings.
- **Storage abuse:** quotas, stake and the illegal-content list.
- **Cache poisoning:** impossible for content-addressed objects; manifests and name records are signed and logged.
