# Submitting draft-staffer-nu-media-00 to the IETF

A step-by-step guide for Justin Elliott Staffer, as author and inventor, to submit `proposals/draft-staffer-nu-media-00.md` as an individual Internet-Draft, disclose IPR under BCP 79, and ask a working group to adopt it.

> **Read first.**
> - **Submitting publishes the draft worldwide immediately.** Once posted, an Internet-Draft is public on datatracker.ietf.org and mirrored at once; it can't be withdrawn from the record. Posting is a public disclosure for patent purposes: it starts the 12-month US grace period and ends patentability in most other countries for everything the draft describes.
> - **File the provisional first:** `patents/provisional-nu-media.md`, at USPTO Patent Center, and have the filing receipt (application number and filing date) in hand before step 4. Patent counsel should confirm the provisional covers everything in the draft.
> - **Check what is already public.** khensu.nu has pages on nu-media (`khensu-site`, `media.astro` and the NuMedia components, committed 11 October 2026). If they are deployed, they may already have disclosed the receiver-side enhancement idea; tell counsel the date they went live.

## 1. Install the tools

macOS's built-in Ruby (2.6) is too old for current kramdown-rfc. Use Homebrew Ruby and a Python virtual environment:

```sh
brew install ruby
export PATH="/opt/homebrew/opt/ruby/bin:$PATH"
gem install kramdown-rfc
# If `kdrfc` or `kramdown-rfc` isn't found afterwards, install the engine gem as well:
gem install kramdown-rfc2629
export PATH="$(gem env gemdir)/bin:$PATH"

python3 -m venv ~/.venvs/ietf
source ~/.venvs/ietf/bin/activate
pip install xml2rfc
```

idnits (the IETF's nits checker) has no pip package. Either use the web version at [author-tools.ietf.org/idnits](https://author-tools.ietf.org/idnits), or download the script:

```sh
curl -fLo ~/bin/idnits https://raw.githubusercontent.com/ietf-tools/idnits/main/idnits
chmod +x ~/bin/idnits
```

## 2. Build

From `khensu-specs/proposals/`, either in one step:

```sh
kdrfc -h -t draft-staffer-nu-media-00.md
```

or in two (the form used to test this draft on 11 October 2026):

```sh
kramdown-rfc draft-staffer-nu-media-00.md > draft-staffer-nu-media-00.xml
xml2rfc --text --html draft-staffer-nu-media-00.xml
```

This produces `.xml`, `.txt` and `.html`. kramdown-rfc fetches references from bib.ietf.org and datatracker.ietf.org on the first run, so it needs the internet. Don't commit the build outputs or the `.refcache` folder unless you want them in the repo.

## 3. Check

```sh
idnits draft-staffer-nu-media-00.txt
```

The 11 October build gave 2 errors and 7 warnings, all expected:

| Item | What to do |
| --- | --- |
| Downref: normative reference to Informational RFC 5869 (HKDF) | Normal; HKDF is widely referenced this way. Mention it if the area director asks, or move it to informative |
| Obsolete normative reference RFC 8446 (obsoleted by RFC 9846) | Switch the reference to RFC9846 once bib.ietf.org serves its reference file (it didn't on 11 October) |
| "Weird spacing" in code blocks | The struct definitions are aligned on purpose; ignore |
| Non-RFC normative references (ITU, SMPTE, NIST) | Normal for media and crypto specs; ignore |

Also read the `.txt` once end to end: page breaks, tables and the IANA templates should be readable.

## 4. Datatracker account and upload

1. Create an account at [datatracker.ietf.org/accounts/create/](https://datatracker.ietf.org/accounts/create/) with `hello@elliottwave.studio`, and confirm the email.
2. Confirm the provisional is filed (box at the top of this guide).
3. Go to [datatracker.ietf.org/submit/](https://datatracker.ietf.org/submit/), upload `draft-staffer-nu-media-00.xml` (XML is preferred; Datatracker makes the text and HTML).
4. Check the extracted metadata: name `draft-staffer-nu-media`, revision `00`, title, the author with name, affiliation and email exactly as in the draft.
5. Submit. Datatracker emails the author a confirmation link; the draft is posted when you click it, and is announced on the i-d-announce list.
6. **Meeting cut-off.** Datatracker doesn't accept new drafts for a short period before each IETF meeting. Check the dates at [datatracker.ietf.org/meeting/important-dates/](https://datatracker.ietf.org/meeting/important-dates/).
7. A draft expires after 185 days. Post `-01` before then to keep it alive.

## 5. IPR disclosure under BCP 79

BCP 79 (RFC 8179) requires a contributor who knows of patents or applications they own covering their contribution to disclose them as soon as reasonably possible. As author and inventor, file the disclosure **the same day** the draft is posted.

1. Go to [datatracker.ietf.org/ipr/new-specific/](https://datatracker.ietf.org/ipr/new-specific/) (a specific disclosure, tied to this draft).
2. **Patent holder:** Elliott Wave LLC. **Contact:** Justin Elliott Staffer, hello@elliottwave.studio. **Discloser:** the same.
3. **IETF document:** `draft-staffer-nu-media`, revision `00`; sections: all.
4. **Patent information:** US provisional application, number and filing date from the filing receipt. The form accepts pending and unpublished applications; listing the number is optional for unpublished ones. Describe it briefly: "constant-bitrate media with receiver-side enhancement; progressive images in constant-rate cover; tiled native-resolution delivery; private chunked transfer".
5. **Licensing declaration (recommended):** choose **"Royalty-Free, Reasonable and Non-Discriminatory License to All Implementers"**, and in the text box add:

   > Elliott Wave LLC will license any patent claims essential to implementing this document royalty-free, on reasonable and non-discriminatory terms, to all implementers. The licence is subject to defensive termination: it terminates for any party that, or whose affiliate, asserts a patent claim against Elliott Wave LLC or against any implementation of this document. This declaration is intended to be consistent with the Elliott Wave LLC patent pledge (in preparation).

   Agree the wording with patent counsel first; `LICENSING.md` refers to `PATENT-PLEDGE.md` (draft pending counsel), and the declaration should match it.
6. Submit, then update the disclosure when the non-provisional or PCT application is filed and when the application is published (Datatracker lets you file an update to an existing disclosure).

## 6. Where to present it

The draft combines three things, and dispatch may suggest splitting them:

| Part | Likely home | List |
| --- | --- | --- |
| Whether and where the work fits | Area dispatch: DISPATCH (ART area) or the WIT area's dispatch session | `dispatch@ietf.org`; the ART area list `art@ietf.org` |
| Media format and RTP considerations | AVTCORE (audio/video transport core maintenance) | `avt@ietf.org`, chairs `avtcore-chairs@ietf.org` |
| Constant-rate mapping over MOQT; transfer over MOQ | MOQ (Media over QUIC) | `moq@ietf.org`, chairs `moq-chairs@ietf.org` |
| Media type registrations (review, not adoption) | Media type reviewers, MEDIAMAN | `media-types@ietf.org` |

Suggested order: post the draft, send the dispatch email (template below), and send a shorter note to `avt@ietf.org` and `moq@ietf.org` pointing to the dispatch thread. Area names, list addresses and which area hosts each group have changed in recent reorganisations; confirm them on each group's Datatracker page before sending.

## 7. Asking for agenda time

1. Find the next meeting and its deadlines at [ietf.org/meeting/upcoming/](https://www.ietf.org/meeting/upcoming/) and the important-dates page above.
2. Email the chairs of DISPATCH (and AVTCORE or MOQ) about 4–6 weeks before the meeting: draft name, one-paragraph summary, what you're asking the group to decide, and the time wanted (10 minutes for dispatch is typical).
3. Upload slides to the session's materials page in Datatracker before the session. Remote participation is free with a fee waiver or a remote registration; check the meeting page.
4. Expect questions on scope (is a media container IETF work?), the learned components (how are they specified and tested?), the IPR (the disclosure will be visible beside the draft), and the transfer protocol (is there a home for it?).

## 8. How adoption works

- Only working group chairs can adopt a draft. When a group is interested, the chairs post a **call for adoption** on the list, usually two weeks; list participants say whether they support it and will review it.
- Adoption needs the work to be in the group's charter. If it isn't, the chairs and area director may propose a charter update, a new group, or no IETF work.
- After adoption the draft is renamed `draft-ietf-<wg>-nu-media-00`, **change control passes to the IETF**, and the group decides the text by rough consensus. The author usually stays as editor.
- If dispatch finds no home, the options are an Independent Stream submission (not IETF consensus) or continuing as an individual draft for discussion.
- Known IPR affects adoption: groups weigh licensing terms, and royalty-free with defensive termination is the declaration most groups accept readily.

## 9. Email to the dispatch list

```text
To: dispatch@ietf.org
Subject: Dispatch request: draft-staffer-nu-media-00 (constant-bitrate media with receiver-side enhancement, private bulk transfer)

Hello DISPATCH,

I'd like to ask where this work could go:

  https://datatracker.ietf.org/doc/draft-staffer-nu-media/

It specifies:
  1. nu-media, a media container whose base layer is constant-bitrate HEVC Main 10,
     with receiver-side neural enhancement (super resolution, artefact removal,
     frame interpolation) outside the prediction loop, so it costs no bits and
     can't drift; 1 MHz timestamps up to 2,000 fps; tiles up to 43,008 x 21,504;
     BT.2020 with PQ and HLG; no capture metadata; senders never downscale.
  2. A mapping onto constant-rate transports, including MOQT, with RTP considerations.
  3. nu-transfer, end-to-end sealed, fixed-size, content-addressed chunks with
     erasure coding and receiver pull (ML-KEM-1024, AES-256-GCM, ML-DSA-87).

The bitrates in the draft are design values, not measurements yet.

Possible homes are AVTCORE for the format and MOQ for the mapping and transfer;
I'd welcome advice on whether to split it. I'd like 10 minutes at the next
DISPATCH session if there is room.

An IPR disclosure has been filed (royalty-free, with defensive termination):
  <link to the disclosure>

Thanks,
Justin Elliott Staffer
Elliott Wave LLC
```

## 10. Checklist

- [ ] Provisional `patents/provisional-nu-media.md` reviewed by counsel and **filed**; application number and date recorded in `PATENTS.md`
- [ ] Counsel told what khensu.nu already shows about nu-media, and when it went live
- [ ] Patent pledge and licensing declaration wording agreed with counsel
- [ ] Draft re-read: every figure labelled as an estimate or design value; author block exactly "Justin Elliott Staffer, Elliott Wave LLC, hello@elliottwave.studio"
- [ ] Built with kramdown-rfc and xml2rfc; idnits shows only the expected items (section 3)
- [ ] Datatracker account created and email confirmed
- [ ] Not inside a pre-meeting submission cut-off
- [ ] Draft uploaded, confirmation link clicked, draft visible on Datatracker
- [ ] IPR disclosure filed the same day at /ipr/new-specific/, linked to `draft-staffer-nu-media-00`
- [ ] Dispatch email sent; short pointers sent to `avt@ietf.org` and `moq@ietf.org`
- [ ] Agenda time requested from the chairs; slides uploaded before the session
- [ ] Reminder set to post `-01` within 185 days
- [ ] IPR disclosure updated when the non-provisional or PCT is filed and when it publishes
