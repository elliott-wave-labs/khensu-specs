---
name: nu-ot-222
description: >-
  Elliott’s weekly Out of Town (OT — rap slang) cadence for khėnsu.ñü. Thursday
  2:00 pm America/Los_Angeles: write/check in the dated MD and status update.
  Thursday 2:22 pm local: hard cutoff — known fixes in, web pushed, apps fixed,
  code + PRs reviewed and auto-merged by the agent, TestFlight, App Store submit
  (or human instructions), beta + GitHub release, sideload install packages
  updated. Use for every personal ship. Pair with nu-harness on skills.agent.
---

# nu.ot.222

**OT = Out of Town** (rap slang). Not overtime.

## Weekly clock (America/Los_Angeles)

| Beat | Time | What |
| --- | --- | --- |
| **Update** | Thursday **2:00 pm** | Chat status + dated MD check-in (`nu.ot/YYYY-MM-DD.md` + `nu.ot.222.md`) → commit → push public. |
| **Cutoff** | Thursday **2:22 pm** local | Hard ship line. Everything below that can land by 2:22 lands. Keep building after. |
| **Name** | **nu.ot.222** | Out of Town + **2:22**. |

## By 2:22 — ship checklist (do in order)

1. **Known fixes** — every open fix Elliott called this week is corrected or listed with a blocker in the MD.
2. **Web pushed** — sites built and published (`publishing-khensu-sites` + `nu-harness`). Verify live with curl.
3. **App fixed** — code changes in `khensu-apple` (and core if needed) compile; device install when possible.
4. **Coded + PR done** — work on a branch; open PR(s) with summary + test plan.
5. **PR reviewed + auto-merged by the agent** — agent runs review (Bugbot/security if asked), addresses clear issues, then merges when green (no waiting on Elliott for routine OT PRs unless he said hold).
6. **TestFlight** — archive → upload to App Store Connect → TestFlight (internal at minimum).
7. **Submit to Apple** — if ASC credentials / notary / transporter work, upload for review. If only a human can click Submit for Review, put **exact click-path instructions** in the MD and in chat — do not fake a submit.
8. **Release to beta** — TestFlight external or named beta group when builds are ready.
9. **Release to GitHub** — `gh release` with IPAs / notes for sideload.
10. **Install packages around the stores** — update get.apps / INSTALL.md / PWA / Sideloadly paths so people can install without App Store / Play.

Private ASC narrative stays in gitignored `docs/CHANGELOG.private.md`. Public OT MDs stay high-level.

## Always: dated MD → commit → public

1. Write **`nu.ot/YYYY-MM-DD.md`** in `khensu-specs`.
2. Refresh **`nu.ot.222.md`** as the week pointer.
3. Mirror bullets in chat at **2:00 pm**.
4. Commit + push. Keep building past **2:22**.

## skills.agent

Public skills: **nu-harness** and **nu-ot-222** — https://khensu.nu/skills-agent  
Skill repo: https://github.com/elliott-wave-labs/nu-ot-222

## Always

- Commands: `~`, never `/`. Flags: `-`.
- Dig before new product hosts; `own_certificate = true`.
- Tips 100% to the person; app commerce flat 10%.

## Do not

- Miss the **2:00** MD check-in or the **2:22** cutoff landing.
- Say OT means overtime.
- Dump private ASC changelog into public MDs.
- Leave PRs unmerged at cutoff when CI is green and review is clear.
