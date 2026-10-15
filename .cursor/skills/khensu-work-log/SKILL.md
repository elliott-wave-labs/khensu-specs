---
name: khensu-work-log
description: >-
  Maintain khensu work-completed.md and work-ip.md after a shipping session:
  commit links, live URLs, App Store / GitHub install status, product naming
  (nu.*), and IP notes. Use when Elliott asks for work-completed, work-ip,
  session wrap, or “what did we push”; also after multi-repo ship days.
---

# khensu work log

## Files (khensu-specs, repo root)

| File | Purpose |
| --- | --- |
| `work-completed.md` | What shipped: live URLs, GitHub release assets, **commit links**, Organizer archives, holds |
| `work-ip.md` | In progress: tonight’s submit plan, App IDs / App Groups, blockers, IP rows |

Update both at end of a multi-repo session. Prefer editing in place over rewriting from scratch.

## Rules Elliott set (15 Oct 2026)

- **App names:** store/product apps are `nu.<product>` (nu.waves, nu.create, nu.moments). Features like ñü.ævätåřş live *inside* create/moments/calls — not a separate App Store app unless decided.
- **Xcode “Ptah”** = messenger target; people see **khensu.nu**; bundle today `nu.khensu.ptah`.
- **App Group:** nu.moments, nu.create, and nu.waves share the messenger App Group (`group.nu.khensu.ptah` today).
- **nu.moments** = Templify-class editor; better than IG/TT clipping; share to nu.network feed; includes nu.avatars.
- After wrap: **do not push code** unless asked; **publish** (sites/SSL) is allowed.
- Never say “patent pending” on site pages; IP notes go in `work-ip.md` / `PATENTS.md`.

## How to fill `work-completed.md`

1. One short section “What Ptah is” if Organizer naming confused anyone.
2. Table of live URLs (apex + product hosts + dig/SSL status).
3. GitHub install: release URL + each IPA download URL.
4. **Commits pushed** — full GitHub commit URLs, grouped by repo (`khensu-specs`, `khensu-site`, `khensu-apple`, `moqom` if infra).
5. Behaviour shipped (bullets).
6. Hold / open (SSL, IETF, ASC key, missing IPAs).

## How to fill `work-ip.md`

1. Naming + App Group table (target vs today).
2. Per-product status (moments, create, messenger, waves, avatars-as-feature).
3. Tonight / next submit checklist (numbered).
4. IP/patent pointer table.
5. Blockers table.
6. Link to `work-completed.md`.

## Commit links

Always use:

```text
https://github.com/elliott-wave-labs/<repo>/commit/<full-sha>
```

Get SHAs with `git log -N --format='%H %s'` in each repo. Include infra (`moqom-cloud/moqom`) when `product_hosts` / SSL changed.

## Do not

- Push `work-*.md` unless Elliott asks to commit them.
- Invent ASC credentials or use AuthKeys from other products (Evergram/Unify).
- Add NXDOMAIN hosts to the shared products SSL pack (`nu-harness`).
