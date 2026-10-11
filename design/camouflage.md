# khensu camouflage: an ordinary handshake outside, pure post-quantum inside

Draft 0.1, 10 October 2026. **Decided** (`OPEN-QUESTIONS.md` 78, option a).

## 1. The problem

Censors block encrypted networks without breaking them, by recognising them. The usual giveaways are in the first packets of a connection:

- the TLS ClientHello: cipher suites, extensions and their order, key-share groups, ALPN (fingerprints such as JA3 and JA4);
- the QUIC transport parameters and Initial packet sizes;
- the server's certificate, its signature algorithm and how the server answers strangers;
- the traffic pattern after the handshake.

A handshake with a pure ML-KEM-1024 key share and an ML-DSA-87 certificate is unique to khensu today. No browser sends it, so one rule in a firewall would block every khensu connection.

## 2. The idea

Split the job between two layers:

1. **Outer layer: camouflage.** The connection is a real TLS 1.3 and QUIC handshake that matches a mainstream browser byte for byte on the wire, to a server that looks and behaves like an ordinary website. Its key exchange is the browsers' own hybrid post-quantum group (X25519MLKEM768), so even the outer layer resists a future quantum computer.
2. **Inner layer: khensu.** Inside that session the client runs its own handshake with pure ML-KEM-1024 to the node's key from the signed node directory, and the node proves itself with ML-DSA-87. The inner handshake is bound to the outer session, so the two can't be separated or replayed.

Nothing in khensu relies on the outer layer for secrecy. Every message, fetch and stream is already sealed inside with pure ML-KEM-1024 (Outfox, MLS, `FetchRequest`) and signed with ML-DSA-87. The outer layer exists to look ordinary and to add a second wall.

## 3. Outer layer

**3.1 Client profiles: be the real thing where possible**

| Device | Outer profile | How |
| --- | --- | --- |
| iPhone, iPad, Mac app | Safari on the same OS | Use Apple's own Network.framework QUIC and TLS stack, which is Safari's, so the fingerprint is genuine rather than imitated (iOS 26 and macOS 26 offer X25519MLKEM768 by default; to verify) |
| tatenan on Linux, Pi, home node, shell | Chrome stable on Linux or Android | BoringSSL (Chrome's TLS library) with a QUIC stack configured to Chrome's ClientHello, extension-order randomisation, GREASE, transport parameters and Initial padding |
| Node-to-node trunks | Chrome, or a common server-to-server HTTP/3 client | Same as above |

**3.2 Profiles track the browsers.** The exact outer profile (versions, extension sets, transport parameters, padding) is a **camouflage profile** published as a consensus parameter in the epoch header and signed by the committee. When Chrome or Safari changes, a new profile ships to every client and node within days, with no app update. Clients never mix profiles within a session.

**3.3 Servers look like websites.**
- Each node has an ordinary hostname and an ordinary WebPKI certificate (ECDSA P-256 from a public CA such as Let's Encrypt), chosen by its operator. The hostname doesn't contain "khensu".
- The client sends that hostname as SNI, as a browser would, with ECH where the node supports it and ECH GREASE otherwise (as Chrome does).
- The node serves a real static website on every path. Operators pick their own site, or use one of several stock sites.
- The server's own fingerprint (TLS settings, QUIC parameters, HTTP/3 headers) matches a common web server profile from the same camouflage profile set.

This replaces the earlier rule of dialling relays by address with no SNI: a browser connecting to a bare IP address with no SNI is rare enough to stand out.

## 4. Inner layer

**4.1 The knock.** After the outer handshake the client opens a WebTransport session over HTTP/3 to a path that changes every epoch (derived from the epoch and the node's directory key, so it looks like any other URL). Its first message is the inner handshake:

```text
struct {
  uint64 network_epoch;
  opaque kem_ciphertext[1568];   // ML-KEM-1024 encapsulation to the node's directory KEM key
  opaque client_nonce[32];
  opaque tag[32];                // HMAC over the fields above, keyed from the KEM secret and the outer exporter
} InnerHello;
```

- `outer_exporter` = TLS exporter of the outer session, label `"khensu camouflage v1"`, 64 bytes (RFC 8446 §7.5). This is the channel binding.
- The tag proves the client holds the shared secret for this exact outer session. A recorded `InnerHello` replayed into another connection fails, because the exporter differs.

**4.2 Probe-indistinguishable failure.** If the path, epoch or tag is wrong, the node answers exactly as its website answers any unknown path (the same status, headers, body and timing), and keeps serving the site. A censor probing a suspected node with its own connections, replays or guesses sees an ordinary website.

**4.3 The node proves itself.** On success the node replies:

```text
struct {
  opaque node_nonce[32];
  opaque signature<V>;           // ML-DSA-87 over (InnerHello, node_nonce, outer_exporter), node's directory signing key
} InnerAccept;
```

The client checks the signature against the node's key in the current signed node directory. A man in the middle with a forged or stolen outer certificate can't produce it, so the client aborts.

**4.4 Inner keys.**

```text
inner_secret = HKDF-Extract(salt = outer_exporter, ikm = mlkem_shared_secret)
c2n_key, n2c_key = HKDF-Expand(inner_secret, "khensu inner c2n" / "khensu inner n2c", 32)
```

All khensu traffic in the session (mixnet packets, relay media, fetches) is sealed again with AES-256-GCM under these keys before entering the outer stream. The client stays anonymous to the node: there's no client certificate.

## 5. After the handshake

- **Sizes.** khensu datagrams are padded to the camouflage profile's sizes, which sit within ordinary QUIC datagram sizes (about 1,200–1,350 bytes). Small and bulk packets span whole datagrams.
- **Pattern.** The 2 s tick and constant call streams are fixed, by design. A constant-rate flow is plausible for streaming, games and live web apps, but a trained traffic classifier may still single it out (section 8).
- **Hardware.** On khensu hardware the guard (`design/guard.md`) enforces the profile's frame sizes and the tick; the camouflage stack runs on the main computer and can't send anything the guard doesn't allow.

## 6. What it guarantees

| Attack | Result |
| --- | --- |
| Passive fingerprinting of the handshake | Matches the current Safari or Chrome profile |
| Active probing of a suspected node | An ordinary website; wrong knocks get the site's normal "not found" |
| Replay of a recorded knock | Fails: bound to the outer exporter |
| Man in the middle with a mis-issued or stolen outer certificate | Fails: the node's ML-DSA-87 signature over the exporter can't be forged |
| Future quantum computer recording the outer handshake | The outer layer is hybrid post-quantum (ML-KEM-768); the inner layer and all content are ML-KEM-1024 |
| Bug in the outer TLS stack | Content still sealed by the inner layer and by Outfox and MLS |

## 7. Implementation notes

- **Apple:** Network.framework with a QUIC parameters object, custom certificate verification (the outer certificate is checked against the WebPKI as a browser would, then the inner handshake decides trust) and the TLS exporter from the security protocol metadata. Verify exporter availability for QUIC in iOS 26 in the first spike.
- **Rust (tatenan, khensu-core):** BoringSSL through the `boring` crate with a QUIC implementation that uses it, configured per profile. The inner handshake (ML-KEM-1024, ML-DSA-87, HKDF, AES-256-GCM) lives in `khensu-core` on libcrux, shared by app and node.
- **Profile tests:** CI captures each build's handshakes and compares JA4 and QUIC fingerprints against real Chrome and Safari captures for the current profile; a mismatch fails the build.

## 8. Limits

- **IP blocking.** Camouflage hides what a connection is, not where it goes. A censor that enumerates the public node directory can block those addresses. Answers: unlisted entry nodes handed out a few at a time (like Tor bridges), home nodes and phones as entry points, and the mesh. Open item.
- **Traffic classifiers** trained on khensu's constant patterns can flag flows with some error rate. Varying the profile's datagram sizes within browser-like ranges and keeping the tick jittered raise their error rate, but don't remove the risk.
- **Profile lag.** Between a browser update and the next profile, khensu looks like a slightly older browser, which is common and normally unremarkable.

## 9. Patent assessment notes

To be completed once built (`PATENTS.md`). Closest prior art: Tor pluggable transports (obfs4, meek, Snowflake), uTLS fingerprint mimicry, Trojan, ShadowTLS and REALITY (TLS camouflage with probe resistance), NaïveProxy, refraction networking (TapDance, Conjure), TLS channel binding (RFC 9266) and Encrypted Client Hello. Candidate novelty, for counsel:

1. An inner pure post-quantum handshake (ML-KEM-1024 to a key pinned from a consensus-signed node directory, ML-DSA-87 node proof) channel-bound to a browser-indistinguishable outer session through the TLS exporter, with probe-indistinguishable failure.
2. Camouflage profiles distributed as committee-signed consensus parameters so a whole network tracks browser releases without app updates.
3. Using each platform's native browser stack as the outer layer (genuine rather than imitated fingerprints) beneath a shared inner protocol.
4. The combination with constant-tick cover and a hardware guard that enforces the profile's sizes and schedule below the operating system.

Filing must happen before this document, the code or any talk about it goes public.
