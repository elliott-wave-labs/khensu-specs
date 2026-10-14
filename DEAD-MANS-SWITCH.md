# Dead-man's switch

**Status: fired by FounderHandover.**  
**Spec:** `PROTOCOL.md` §12.5–12.7 (founder succession), §14.1 (per-user deadman role).  
**Handover record:** [`FOUNDER-HANDOVER.md`](FOUNDER-HANDOVER.md).  
**Open source map:** [`OPEN-SOURCE.md`](OPEN-SOURCE.md).

| Field | Value |
| --- | --- |
| Fired | 2026-10-14T14:27:57Z |
| Local (PDT) | 2026-10-14 07:27 |
| Path | Signed **FounderHandover** (not 42 days of silence) |
| Effect | Every founder power ends for good; private escrow opens as public GitHub |
| One-way | Nothing restores a founder role (`PROTOCOL.md` §12.5) |

The network is a gift to humanity and all beings: freedom, privacy and a path to universal basic income, so people everywhere can create, build and live securely. Never phrase the switch as “can't be stopped” (`AGENTS.md`).

---

## 1. What it is

The founder held powers the committee does not: co-signature on rule changes, veto on new operators, and the release-signing key. The dead-man's switch makes sure those powers cannot die with the founder or stay locked in one person.

Two ways it fires (`PROTOCOL.md` §12.5):

| Path | Trigger |
| --- | --- |
| **Silence** | No valid `FounderCheckIn` for 1,008 network epochs (42 days / six missed weekly check-ins) |
| **Handover** | A valid signed `FounderHandover` (this firing) |

When it fires:

1. Founder powers end (`founder_cosig` empty; admission veto gone; founder key dropped from pinned release keys).
2. Release signing passes to the committee's 14-of-21 threshold key (when that path ships).
3. Private code escrow opens: patented material included (`PROTOCOL.md` §12.7).
4. The archive goes to every node, the founder's friends list, the press (WSJ, Forbes), Wikimedia Commons and the Internet Archive.

Wire shapes (for when the chain accepts them):

```
FounderCheckIn  { network_epoch, archive_root, escrow_root, signature }
FounderHandover { network_epoch, signature }   // label "founder handover"
```

---

## 2. What fired on 14 October 2026

Elliott Wave LLC, by Elliott, published a **FounderHandover** intent. That is enough to fire the switch under the human-readable path in [`FOUNDER-HANDOVER.md`](FOUNDER-HANDOVER.md).

| Spec step | Today |
| --- | --- |
| Founder role ends | Yes — no co-signature, admission veto or founder-only release key |
| Repositories public | Yes — every `khensu-*` repo under [elliott-wave-labs](https://github.com/elliott-wave-labs) is **public** |
| Patent grant | Yes — irrevocable royalty-free grant in `FOUNDER-HANDOVER.md` §3 |
| On-chain `FounderHandover` + epoch header | Not yet — cite **2026-10-14T14:27:57Z** and this file when committee escrow ships |
| Sealed escrow opened by 14-of-21 shares | N/A for now — there is nothing left sealed in the `khensu-*` trees; GitHub public is the release |
| Delivery to press / Wikimedia / Internet Archive | Anyone may mirror; committee `gateway` proofs come with the chain |

Until the network countersigns: **public git history, `FOUNDER-HANDOVER.md` and this file are the record.**

---

## 3. Weekly check-in (no longer required)

Before handover, the founder posted a `FounderCheckIn` at least every 168 epochs (7 days), attesting that `archive_root` and `escrow_root` covered every repo head and release.

After this firing, check-ins do not restore founder powers and are not required to keep the code public. Archive continuity passes to automatic CI archive and, later, to epoch headers (`PROTOCOL.md` §12.6).

---

## 4. Recipients (`PROTOCOL.md` §12.7)

| Recipient | How (when chain ships) | How today |
| --- | --- | --- |
| Every node | Archive objects on the network | Clone the public repos |
| Founder's friends | Mixnet message with archive + notice | Share this notice and the org URL |
| Press (WSJ, Forbes, …) | Tip lines + on-chain TLS transcript proof | Press note in `FOUNDER-HANDOVER.md` §7 |
| Wikimedia Commons | Upload under open licences | Anyone may deposit |
| Internet Archive | Public item with notice and releases | Anyone may save https://github.com/elliott-wave-labs |

---

## 5. Not this switch

- **Per-user deadman** (`PROTOCOL.md` §14.1, role `deadman`): a person's own timed release to mailboxes — unrelated to founder succession.
- **Unrelated Elliott Wave LLC repos** (non-`khensu-*`): unchanged.
- **MOQOM proprietary crates** outside khėnsu.ñü trees: stay out (`LICENSING.md`).

---

## 6. Signature block

| Field | Value |
| --- | --- |
| Entity | Elliott Wave LLC |
| Actor | Elliott (founder) |
| Action | Dead-man's switch fired via FounderHandover |
| Time | 2026-10-14T14:27:57Z |
| Spec | `PROTOCOL.md` §12.5–12.7 |
| Companion | `FOUNDER-HANDOVER.md`, `OPEN-SOURCE.md` |

Cryptographic founder-threshold signature on the on-chain `FounderHandover` attaches when the chain accepts that message.
