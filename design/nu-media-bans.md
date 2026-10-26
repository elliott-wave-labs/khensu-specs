# nu.media bans and wallet receive lock

**Status: decided, 14 October 2026.** Product rule for public media on nu.media (`media.khensu.nu`, code `nu.media`). Shown as **ñü.media** where people see it; code, hosts and identifiers keep `nu.media` / `media`. Wallet behaviour builds on `PAYMENTS.md` (ñü.wallet) and `design/nufi.md`.

## 1. What a ban is

Trust and safety can ban a persona (public handle or unlinkable persona) from nu.media for abuse that App Review rule 1.2 and the public-content rules require action on: illegal content, severe harassment, fraud, spam that breaks rate limits after warnings, and the narrow illegal-content list (`PLAN.md`, Public square; `COMPLIANCE.md` 4).

A ban is a signed **BanRecord** (ML-DSA-87) logged in the key transparency log and mirrored to every stock app. It is public and auditable. It never reads private messages. Device-side label lists and block/report stay as they are; a BanRecord is the app-level action that removes the account from stock distribution and locks receiving.

| Field | Meaning |
| --- | --- |
| `persona_id` | The banned persona's public key hash |
| `payment_owner` | The `owner` committed in notes for that persona's media earnings address |
| `starts_at` | UTC instant the ban takes effect |
| `ends_at` | UTC instant the ban lifts, or null if permanent |
| `kind` | `temporary` (default) or `permanent` |
| `reason_code` | Short public code (spam, fraud, illegal, harassment, other); no private report text |
| `ban_id` | Unique id; extensions reference the same `ban_id` |

Default duration: **one month** from `starts_at`. A ban may be **extended** (new `ends_at`, same `ban_id`) or converted to **permanent** (`kind = permanent`, `ends_at = null`) before it lifts. Each change is a new signed BanRecord version; clients use the latest for that `ban_id`.

## 2. What the ban does on nu.media

While a ban is active for a persona:

- Stock apps hide the persona from discovery, search, For You and public profiles, and stop serving new posts, live rooms and media under that persona.
- Existing posts stay content-addressed on the network (webË does not delete for unpopularity); stock clients refuse to show them while the ban is active, the same way they refuse illegal-content hashes.
- The persona cannot publish new public media through the stock app.
- Private messaging is unchanged (block/report and franking still apply there).

After `ends_at`, stock clients treat the BanRecord as inactive unless a later extension or permanent record replaced it. A permanent ban stays until an explicit lift record is published (appeal).

## 3. Wallet: spend stays open, receive locks

ñü.wallet remains non-custodial (`PAYMENTS.md` §3): **nobody can freeze, seize or spend an existing note**. A ban must not break that.

| Balance | During ban | After temporary ban lifts |
| --- | --- | --- |
| **Spendable** (notes already owned before the ban, and any notes received outside the lock) | Fully spendable: tips out, P2P, card withdrawal, era refresh | Unchanged |
| **Held** (earned while receive-locked) | Visible in the wallet; not spendable | Becomes spendable (eligible) |

### 3.1 What receive lock covers

While banned, **inbound value addressed to that persona's media payment address** does not land as spendable notes. It accumulates as **held earnings**:

- Creator pay: 1¢ per view minute or play (`OPEN-QUESTIONS.md` 89)
- Tips, gifts and live-room tickets to that persona through nu.media
- Creator subscriptions and sales settled to that media payment address

**Not locked by a nu.media ban:**

- Node operator pay for verified work (separate from the persona's media address)
- Notes the person already holds (spendable stays spendable)
- Sanctions screening at pool deposit/withdrawal boundaries (unchanged, `PAYMENTS.md` §10)

Senders' wallets and the creator-pay path check the active BanRecord before building outputs. If locked, they pay into a **held envelope** for that `ban_id` instead of a normal owner note. The banned person's wallet still learns the amount (viewing path / encrypted memo) so the Held line can update.

### 3.2 Held envelope (how it stays non-custodial)

Held value is an escrow note class in the shielded pool, same shape as other notes on the wire:

- Commitment binds `payment_owner`, `ban_id` and value; the spend authority is a **release condition**, not the company's key.
- **Release on lift:** when the active BanRecord for that `ban_id` has passed `ends_at` (or an explicit lift is logged), the owner's device can spend the held notes into ordinary owner notes with a proof that includes the BanRecord expiry (or lift) as a public input the committee already accepts from the log.
- **Nobody else can spend held notes.** Elliott Wave LLC and the committee cannot move them to themselves. The committee only checks proofs and nullifiers, as today.
- **Extend:** extending `ends_at` keeps the same held envelope; new earnings keep appending; nothing becomes spendable early.
- **Permanent:** `kind = permanent` means no automatic release. Held stays visible as "earned while banned — not eligible while permanently banned". On an explicit lift after appeal, held becomes eligible like a temporary lift. If policy later forfeits permanent held value, it goes only to that epoch's **node pay pool** (operators), never to the company; any forfeit rule needs a separate counsel-signed BanRecord field and a transparency-report line. Default until then: **hold forever until lift**, no silent forfeit.

Era refresh applies to held notes the same way as ordinary notes so they do not expire out of the pool while a long ban runs.

### 3.3 Wallet UI

On the Wallet screen, while banned (and afterward until held is claimed into spendable):

```
Spendable     $12.40     ← can send, tip, withdraw
Held          $3.17      ← earned while banned; eligible after ban lifts
Ban ends      14 Nov 2026   or   Permanent
```

Copy rules:

- Held is labelled **"Earned while banned"** and **"Eligible after ban lifts"** (or **"Not eligible while permanently banned"**).
- Spending spendable never requires clearing held.
- Extending the ban updates "Ban ends" and does not zero held.
- When the ban lifts, held shows a one-tap **Make spendable** (or auto-releases on next wallet open) into ordinary notes; then Held goes to zero.

## 4. Who may issue BanRecords

Until founder powers fully sit with consensus (`PROTOCOL.md` 12.5–12.7, `FOUNDER-HANDOVER.md`), BanRecords for the stock app are signed by the trust-and-safety key held by Elliott Wave LLC (hardware-backed), with co-sign threshold as for releases once that path ships. After succession, the same power is a committee (or guardian) capability named in `design/guardians.md`. Every BanRecord, extension, permanent mark and lift appears in the twice-yearly transparency report counts (`PLAN.md`, Trust and safety).

Appeals: a lift is a BanRecord version with `ends_at` in the past (or a `lifted` flag). There is no silent rewrite of history; versions append.

## 5. What this is not

- Not a freeze of the shielded pool or of other people's notes.
- Not a block on spending money already earned.
- Not client-side scanning of private messages.
- Not a platform cut: held value is still the creator's when released; khensu.nu takes nothing extra for the lock.

## 6. Public forum offenses (decided 25 Oct 2026)

The public name is the violet flame, the transmuting fire of Lumeria. Nudity, gore, and an attack on a person or a group for who they are (race, colour, ethnic or national origin, sex, gender, sexual orientation, religion, disability, age), including racism, misogyny, bullying, and drama, ban the persona from the public forum. The page is `safety.khensu.nu`. `khensu.nu/safety` redirects there. flame and violet are names, not hosts.

The picture check stays on the device. The BanRecord carries a reason code, not the frame.

| Offense count for that persona | Ban |
| --- | --- |
| 1st offense | 1-month ban |
| 2nd strike | 3-month ban |
| 3rd offense | 1-year ban on public discourse and interaction |
| 4th strike | Permanent ban on public discourse for that person, that wallet, and that device |

The count never resets, even years later. The 4th strike is `kind = permanent` and names the device as well as the persona and the media payment wallet. It bars those three from public discourse. They keep the wallet and can send and receive money, including on the media payment address: this strike does not apply the receive lock in §3. They are isolated from the community after multiple infractions.

While a ban is active:

- Stock apps block the persona from the public forum (discovery, feed, forums, live rooms). From the 3rd offense, that block is public discourse and community interaction.
- nu.waves playback is refused except the sound healing tones, First Attempt, and the classical composers (`artist` kind `composer`).
- Private messages are unchanged.
- Existing posts stay content-addressed. Stock clients do not show that persona in public discourse until `ends_at`. A permanent ban does not end.
- The 1st, 2nd, and 3rd bans still use the §3 receive lock on the media payment address. The 4th does not.

## 7. Cross-links

- `PAYMENTS.md` — non-custodial notes; held envelope to be specified in the spend AIR when built
- `design/nufi.md` — creator economics
- `PLAN.md` — Public square, Creators, Trust and safety
- `COMPLIANCE.md` — App Review 1.2, DSA notice and action
- `OPEN-QUESTIONS.md` — permanent-held forfeit (if ever) vs hold-until-lift
