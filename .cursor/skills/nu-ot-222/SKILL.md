---
name: nu-ot-222
description: >-
  Elliott’s weekly Out of Town (OT — rap slang) cadence for khėnsu.ñü. Thursday
  2:00 pm America/Los_Angeles status update; hard ship cutoff 2:22 pm local.
  Always write a dated public MD, check it in, publish. Private release changelog
  stays private. Use for every personal ship, site publish, app install, Apple
  submit, and deadline request. Pair with nu-harness (only skill on skills.agent).
---

# nu.ot.222

**OT = Out of Town** (rap slang). Not overtime. Not “operating tempo.”

Elliott’s personal ship cadence while he’s OT. Apply on **every** khėnsu task for him unless he says otherwise.

## Weekly clock (America/Los_Angeles)

| Beat | Time | What |
| --- | --- | --- |
| **Update** | Thursday **2:00 pm** | Status in chat + dated MD (what shipped, what’s open). |
| **Cutoff** | Thursday **2:22 pm** local | Hard ship line. Land what’s ready. Keep building after. |
| **Name** | **nu.ot.222** | Out of Town + 2:22 (same beat as the dead-man’s switch activation). |

## Always: dated MD → commit → public

Every Thursday (and any OT ship Elliott calls):

1. Write **`nu.ot/YYYY-MM-DD.md`** in `khensu-specs` (ISO date in his local timezone).
2. Also keep / refresh **`nu.ot.222.md`** as the rolling “this week” pointer (same content or a short link to the dated file).
3. Mirror the bullets in the agent chat at **2:00 pm**.
4. **`git add` + commit** those MDs in `khensu-specs` and **push** so they stay public.
5. Keep building past **2:22 pm** — the MD is a checkpoint, not a stop.

Filename examples: `nu.ot/2026-10-15.md`, pointer `nu.ot.222.md`.

## Private release changelog

- Maintain **`CHANGELOG.private.md`** only in places that stay **private** (gitignored under `khensu-apple/docs/` and/or Elliott’s personal store).
- App Store / TestFlight release notes, review replies, and unreleased version notes go there — **never** on the public skills.agent site and **never** in public commit messages that dump the full private log.
- Public `nu.ot/*.md` may say “ASC submit attempted / build N” without private reviewer narrative.

## Priority when the clock is short

1. **Sites live** — publish what is built (`publishing-khensu-sites` + `nu-harness`).
2. **Apps on device** — Wi‑Fi install before App Store.
3. **Apple submit** — upload archive-ready builds by **2:22**; incomplete stay GitHub IPA / TestFlight.
4. **Code** — public repos stay public post-handover; do not privatize.
5. **New hosts** — dig A → `34.107.228.246`, then `own_certificate = true`.

## Always

- Commands: `~`, never `/`. Flags: `-`.
- **skills.agent** publishes **nu-harness** and **nu-ot-222**. Public OT MDs also live in khensu-specs (`nu.ot/`).
- Display names: people see the marks; code/hosts stay ASCII.

## Do not

- Miss the Thursday **2:00 pm** update or the **2:22 pm** dated MD + commit.
- Put private release changelog text on skills.agent or in public release notes wholesale.
- Block the cutoff waiting on perfect parity — ship the slice, note the rest in the MD.
- Add NXDOMAIN hosts to the shared products SSL pack.
- Call OT “overtime” or “operating tempo.”

## Companion

- skills.agent: https://khensu.nu/skills-agent
- Skill repo (public): https://github.com/elliott-wave-labs/nu-ot-222
- Harness: `nu-harness` · `nu.harness.md`
