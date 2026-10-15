---
name: nu-harness
description: >-
  Agent harness for khėnsu.ñü across Cursor and other open agents: publish sites
  immediately, keep repos public, install without Apple/Google stores, mobile-only
  CSS when desktop is perfect, SLA at khensu.nu/sla. Use for khensu site, GitHub,
  sideload, dead-man's switch, PUBLIC.md or nu.harness work.
---

# nu.harness

Source: [`nu.harness.md`](../../../nu.harness.md) · [`PUBLIC.md`](../../../PUBLIC.md) · live [sla.khensu.nu](https://khensu.nu/sla).

## Fixed rules

1. **Publish sites immediately.** Never hold for a patent filing. Pair with `publishing-khensu-sites`.
2. **Keep code public.** First-party `khensu-*` repos on elliott-wave-labs stay public. Link source and Releases, not store-only install.
3. **Install without stores.** Safari PWA, GitHub IPA sideload, `xcodegen` / Xcode. Team ID `LHS49D8RYY`. Hub: https://khensu.nu/app
4. **Desktop vs mobile.** When desktop is perfect, change only `@media` mobile rules.
5. **Display names.** People see khėnsu.ñü, ñü.ŵævẽš, suñůlink.shield, webË, spacetime bubble™. Code/URLs stay ASCII.
6. **Commands** start with `~`, never `/`.
7. **Wording.** Gift of freedom, privacy, basic income — never “can't be stopped”.
8. **SLA** at `khensu.nu/sla` (`sla.khensu.nu` when DNS A → sites LB): marketing + install walkthroughs + repo links.
9. **Multi-root** under `~/Documents/GitHub/khensu/`: specs, site, apple, core, …
10. **Licences.** core Apache-2.0, specs CC BY 4.0, others AGPL-3.0.

## Default workflow

```text
1. Read AGENTS.md + PLAN.md.
2. Change the owning repo only.
3. Waves: mobile only inside @media (max-width: 860px).
4. Build + publish (publishing-khensu-sites).
5. Push GitHub; verify public; link Releases for IPAs.
6. Point install copy at GitHub + PWA.
```

## Install (short)

| Path | Steps |
| --- | --- |
| PWA | waves.khensu.nu → Share → Add to Home Screen |
| Sideload | `nu.waves.ipa` from khensu-apple Releases → Sideloadly / AltServer |
| Source | clone apple + core → `xcodegen generate` → scheme Waves or Ptah → Run |
| Hub | https://khensu.nu/app |

## Do not

- Hold site deploys for patents
- Make repos private by default
- Change desktop when only mobile was requested
- Phrase the network as unstoppable
