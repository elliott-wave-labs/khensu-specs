# Submitting draft-staffer-link-preview-media-00

Companion to `IETF-SUBMISSION.md` (nu-media). This draft is **informational**: it profiles Open Graph + mute-loop client behaviour. It does **not** claim Apple’s Messages playback path as invention.

## Before posting

1. Read the draft: `proposals/draft-staffer-link-preview-media-00.md`.
2. Confirm with counsel that the public Indra cards (live since 12 Oct 2026) and this draft’s overlap with `WEBE.md` 7.1 / `PATENTS.md` (nu:preview + hash) are intentional disclosures.
3. Build with the same toolchain as nu-media (`kdrfc`, `xml2rfc`, idnits).

## One-liner for ART / DISPATCH

> Link Preview Media: a mute-loop, hash-checked motion twin beside `og:image`, so unfurlers beyond Apple Messages can play direct MP4 previews without host allowlists.

## Hack path until clients adopt it

| Surface | Until they implement the draft |
| --- | --- |
| Slack | Paste `https://khensu.nu/og/waves.mp4` as a file (plays). Or a custom unfurl app + video block → `https://khensu.nu/og/embed/?src=waves` once the LB allows framing that path (today: `X-Frame-Options: DENY`) |
| Android Messages | Still only for arbitrary sites; keep shipping H.264 `og:video` / `preview:url` |
| Discord | Often already plays `og:video` |
| Apple Messages | Already works (TN3156) |
