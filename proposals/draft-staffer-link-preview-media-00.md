---
title: "Link Preview Media: Mute-Loop Motion Beside Open Graph Stills"
abbrev: "link-preview-media"
docname: draft-staffer-link-preview-media-00
category: info
submissiontype: IETF
ipr: trust200902
area: ART
keyword:
  - open graph
  - link preview
  - og:video
  - messaging
  - mute loop
  - content hash
v: 3
stand_alone: yes
pi: [toc, sortrefs, symrefs]

author:
  -
    fullname: Justin Elliott Staffer
    organization: Elliott Wave LLC
    email: hello@elliottwave.studio

normative:
  RFC2119:
  RFC8174:
  RFC9110:
  RFC6234:

informative:
  OGP:
    title: "The Open Graph protocol"
    target: https://ogp.me/
    date: 2024
  TN3156:
    title: "TN3156: Create rich previews for Messages"
    author:
      - org: Apple Inc.
    target: https://developer.apple.com/documentation/technotes/tn3156-create-rich-previews-for-messages
    date: 2023
  TechTalk205:
    title: "Ensuring Beautiful Rich Links (Tech Talk 205)"
    author:
      - org: Apple Inc.
    target: https://developer.apple.com/videos/play/tech-talks/205/
    date: 2017-12-21
  WEBE:
    title: "webË: A people-run web on a stealth network"
    author:
      - ins: J. E. Staffer
    target: https://dev.khensu.nu/specs/WEBE.md
    date: 2026

--- abstract

Many messaging and collaboration clients unfurl shared URLs using Open Graph
metadata. Almost every client shows `og:image`. Only a few download and play a
direct media file from `og:video`, and none share a common contract for mute,
loop, duration, size, or integrity. This document defines Link Preview Media:
rules for emitting a short, downloadable motion twin beside a still, and for
clients that choose to play it. It profiles existing Open Graph video tags and
defines optional `preview:*` (and interoperable `nu:preview:*`) properties so
Android messengers, Slack-class unfurlers, and browser extensions can adopt the
same mute-loop behaviour Apple Messages already demonstrates for direct MP4s.

--- middle

# Introduction

# Background

When a person pastes a URL into a chat, the receiving client often fetches the
page and builds a rich preview. The Open Graph protocol {{OGP}} defines
`og:image` and `og:video`. In practice:

* Almost every unfurl shows `og:image`.
* Animated GIF, APNG, and animated WebP values for `og:image` are commonly
  frozen to the first frame.
* `og:video` pointing at an HTML player page or HLS playlist usually becomes
  tap-to-play or is ignored.
* A small set of clients, notably Apple Messages on iOS, iPadOS, macOS, and
  visionOS when given a direct downloadable MP4 ({{TN3156}}, {{TechTalk205}} —
  21 December 2017), download the file and autoplay it muted.
* Major collaboration unfurlers (for example Slack DMs and channels) show the
  still for arbitrary sites and reserve inline video for allowlisted providers.
* Consumer Android SMS/RCS clients typically show website stills; video autoplay
  is often limited to a few allowlisted hosts (for example YouTube).
* Instagram DMs and TikTok DMs typically show a still thumbnail for ordinary
  HTTPS pages and do not mute-loop arbitrary `og:video` files today.

The result is a referral experience that works as living motion on one popular
messenger and as a frozen card everywhere else, even when the publisher shipped
a correct direct MP4. Publishers cannot fix that with tags alone. A shared
client contract is required.

# Target unfurlers

This profile is written so the same tags work everywhere the publisher already
ships a direct H.264 MP4. Clients SHOULD adopt mute-loop playback for
`preview:policy` containing `mute`, `loop`, and `autoplay` when the file passes
the hash and size checks in this document:

* Apple Messages (iOS, iPadOS, macOS, visionOS) — already behaves per
  {{TN3156}} / {{TechTalk205}} for direct MP4 `og:video`.
* Google Messages and other Android SMS/RCS unfurlers — today still-only for
  arbitrary sites; this draft is the shared contract.
* Slack (direct messages and channels) — today still-only / allowlist; this
  draft removes the need for a host allowlist when `preview:hash` verifies.
* Instagram DMs, TikTok DMs, and similar consumer chat unfurlers — today
  still-only for ordinary sites; same contract.
* Discord, Telegram, and other clients that already play some `og:video` —
  SHOULD honour `preview:policy` and `preview:hash` when present.

# Goals

1. Make mute-loop motion the interoperable default for short preview media.
2. Keep `og:image` as the universal still fallback.
3. Let clients verify the bytes they show (`preview:hash`).
4. Stay deployable on ordinary HTTPS sites without a private API.
5. Remain compatible with Apple's documented direct-MP4 path ({{TN3156}}).

# Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in BCP 14 {{RFC2119}} {{RFC8174}}
when, and only when, they appear in all capitals, as shown here.

* Preview still: the image resource identified by `og:image`.
* Preview motion: a short downloadable media resource intended to play inside
  the unfurl surface without navigating away.
* Unfurler: any client that builds a rich preview from a shared URL.

# Publisher requirements

A page that offers Link Preview Media MUST emit a preview still and SHOULD emit
preview motion.

## Still

Publishers MUST emit:

~~~~ html
<meta property="og:image" content="https://example.example/og/page.jpg" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
~~~~

The still SHOULD be JPEG or PNG, HTTPS, and large enough for a wide card
(1200 × 630 is RECOMMENDED).

## Motion (Open Graph profile)

When motion is offered, publishers MUST emit a direct, downloadable file:

~~~~ html
<meta property="og:video" content="https://example.example/og/page.mp4" />
<meta property="og:video:secure_url" content="https://example.example/og/page.mp4" />
<meta property="og:video:type" content="video/mp4" />
<meta property="og:video:width" content="1200" />
<meta property="og:video:height" content="630" />
~~~~

The `og:video` URL MUST:

* Use HTTPS ({{RFC9110}}).
* Return `Content-Type: video/mp4` (or another type listed in {{codec}}) with a
  real media body — not an HTML document, not a player page.
* Be fetchable without cookies, login, or a personalized query string.
* Be short: RECOMMENDED duration is at most 6 seconds; MUST NOT exceed 10
  seconds for automatic playback.
* Be small: RECOMMENDED total of still + motion under 8 MiB; MUST NOT exceed
  10 MiB for automatic playback.

The primary motion resource for broad unfurlers SHOULD be H.264 (`avc1`) in MP4
so current mobile decoders can play it. An additional higher-quality twin (for
example HEVC) MAY be advertised with the properties in {{preview-props}}.

Publishers MUST NOT rely on HLS, DASH, or an embeddable iframe URL as the only
`og:video` value if they want mute-loop unfurls.

## Optional preview properties {#preview-props}

To carry the contract Open Graph leaves implicit, publishers SHOULD also emit:

~~~~ html
<meta property="preview:url" content="https://example.example/og/page.mp4" />
<meta property="preview:type" content="video/mp4; codecs=avc1.42E01E" />
<meta property="preview:duration" content="4" />
<meta property="preview:size" content="1200x630" />
<meta property="preview:bytes" content="3677893" />
<meta property="preview:hash" content="sha-256=3a646c50…" />
<meta property="preview:policy" content="mute loop autoplay inline no-fullscreen no-download pointer-events-none tap-opens-link" />
<meta property="preview:interactive" content="false" />
<meta property="preview:hit-test" content="false" />
<meta property="preview:action" content="https://example.example/" />
~~~~

Property names under the `preview:` prefix are defined by this document.
Implementations that already ship the webË tags in {{WEBE}} MAY emit the same
values under `nu:preview`, `nu:preview:type`, `nu:preview:duration`,
`nu:preview:size`, `nu:preview:bytes`, `nu:preview:hash`, `nu:preview:policy`,
`nu:preview:interactive`, `nu:preview:hit-test`, and `nu:preview:href`. Clients
that understand this document MUST treat `nu:preview*` as synonyms of `preview*`
when the `preview*` forms are absent.

* `preview:url` — absolute HTTPS URL of the motion file. When absent, clients
  use `og:video`.
* `preview:type` — media type, optionally with a codecs parameter.
* `preview:duration` — integer seconds, rounded up.
* `preview:size` — `WIDTHxHEIGHT` in pixels.
* `preview:bytes` — exact byte length of the file.
* `preview:hash` — `sha-256=` followed by the lowercase hex SHA-256 of the file
  bytes ({{RFC6234}}).
* `preview:policy` — space-separated tokens. For Link Preview Media the
  RECOMMENDED value is `mute loop autoplay inline no-fullscreen no-download pointer-events-none tap-opens-link`.
* `preview:interactive` / `preview:hit-test` — when `"false"`, the motion layer
  MUST NOT capture pointer or touch events (`allowsHitTesting(false)` /
  `pointer-events: none`), MUST NOT expand fullscreen, and MUST NOT offer a
  direct video download; tapping the preview opens the canonical page URL.

Several `preview:url` (or `nu:preview`) tags MAY appear; a client uses the first
entry it can decode and that passes the hash check.

# Client requirements

## Baseline (all unfurlers)

Every unfurler that shows a rich preview MUST be able to show `og:image` when
present and fetchable.

## Motion-capable unfurlers

An unfurler that claims Link Preview Media support MUST:

1. Prefer a direct downloadable motion URL from `preview:url`, else `og:video`,
   else `twitter:player:stream` when that URL is a media file.
2. Reject player pages, HLS playlists, and opaque redirects to HTML.
3. Fetch the motion file without sending cookies or a page referrer that
   identifies the viewer to the origin.
4. If `preview:hash` is present, verify the SHA-256 of the response body and
   discard the motion on mismatch, falling back to the still.
5. Autoplay muted, looping, without sound, for files within the duration and
   size limits in this document.
6. Honour the platform reduced-motion or data-saver setting by showing the still
   instead of autoplaying.
7. On user tap of the motion surface, open the canonical page URL directly.
   When `preview:policy` includes `no-fullscreen`, `no-download`,
   `pointer-events-none`, or `tap-opens-link` (or `preview:hit-test="false"`),
   the motion surface MUST disable hit-testing (`allowsHitTesting(false)` /
   `pointer-events: none`), MUST NOT expand into a fullscreen media player, and
   MUST NOT expose a video download action; the video plays strictly at preview
   card size and tapping anywhere on the preview opens the link.

Clients MUST NOT require a site-specific partnership, oEmbed allowlist, or app
install for HTTPS origins that meet {{codec}} and the publisher rules above.

## Collaboration clients (Slack-class)

Unfurlers that historically allowlist video hosts SHOULD treat a page that
emits valid Link Preview Media as eligible for the same inline mute-loop
surface they use for allowlisted providers, or SHOULD offer an equivalent
custom unfurl that plays `preview:url` / `og:video` in an embed whose poster is
`og:image`. Showing only the still when a valid direct MP4 is present is
compatible with today's deployed Slack behaviour but is NOT RECOMMENDED for
implementations of this document.

# Codecs and containers {#codec}

Motion-capable clients MUST support H.264 High or Main Profile in MP4
(`video/mp4`, codec `avc1`). Clients SHOULD also support HEVC (`hvc1` / `hev1`)
when the platform decoder exists. Audio tracks in preview motion SHOULD be
absent; if present, clients MUST keep playback muted for automatic preview.

# Privacy considerations

Fetching a preview MUST NOT become a tracking channel. Clients SHOULD fetch
through a privacy-preserving path when available, MUST strip cookies, and MUST
NOT send a referrer that includes the viewer's identity. Personalized preview
URLs (per-recipient signed query strings) are NOT RECOMMENDED; when used, they
break cache sharing and hash stability.

# Security considerations

Clients MUST treat preview media as untrusted content: no script execution from
the media file, no automatic navigation on load, and hash mismatch MUST drop
the motion. Executable types advertised as previews (for example Android APKs)
MUST NOT autoplay or auto-open; they require an explicit, warned user action
(see {{WEBE}} section 7.1).

# IANA considerations

This document requests registration of the following HTML meta property names
in a specification-required registry of link-preview properties, or as
provisional entries until such a registry exists:

* `preview:url`
* `preview:type`
* `preview:duration`
* `preview:size`
* `preview:bytes`
* `preview:hash`
* `preview:policy`

# Relationship to deployed practice

Apple Messages already implements the essential playback rule for direct MP4
`og:video` values ({{TN3156}}). This document does not change that behaviour; it
asks other unfurlers to converge on it and adds hash, policy, and dual-quality
hooks so the open web and privacy-preserving clients can share one contract.
The `nu:preview*` tags deployed on khensu.nu are a living profile of this
document ({{WEBE}}).

--- back

# Acknowledgements

Discussions around Indra cards on khensu.nu and Apple TN3156 informed this
draft.
