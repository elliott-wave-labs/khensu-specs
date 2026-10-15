# nu.harness

Agent harness for khėnsu.ñü work across Cursor and other open agents. Install as a skill (`nu-harness`) or keep this file at the workspace root of `khensu-specs`.

## When to use

Any task that touches khensu.nu sites, product hosts, GitHub repos under elliott-wave-labs, App Store / sideload install paths, the dead-man's switch, SLA, or the open archive.

## Fixed rules

1. **Publish sites immediately.** Site work ships as soon as it builds — every host including the studio. Never hold for a patent filing.
2. **Keep code public.** First-party `khensu-*` repos stay public on GitHub. Prefer clear links to source and Releases over store-only install.
3. **Install without stores.** Document Safari PWA, GitHub IPA sideload and `xcodegen` / Xcode build. Apple Team ID `LHS49D8RYY`. App Store is optional.
4. **Desktop vs mobile.** When the user says desktop is perfect, change only `@media` mobile rules. Do not restyle desktop.
5. **Display names.** People see khėnsu.ñü, ñü.ŵævẽš, suñůlink.shield, webË, spacetime bubble™. Code, URLs, hosts and identifiers stay ASCII (`khensu`, `waves`, `sunu`, `webe`).
6. **Commands.** Private AI and node terminal commands start with `~`, never `/`.
7. **Wording.** The network is a gift: freedom, privacy, basic income. Never “can't be stopped”.
8. **SLA host.** Public notice lives at `sla.khensu.nu` (and `/sla` on the apex). Marketing + install walkthroughs + repo links.
9. **Multi-root.** Specs in `khensu-specs`; sites in `khensu-site`; Apple in `khensu-apple`; core in `khensu-core`. Clone side by side under `~/Documents/GitHub/khensu/`.
10. **Licences.** `khensu-core` Apache-2.0, `khensu-specs` CC BY 4.0, other repos AGPL-3.0.

## Default workflow

```text
1. Read AGENTS.md + PLAN.md for fixed decisions.
2. Change the owning repo only (site CSS → khensu-site, protocol → khensu-specs).
3. For waves: fix mobile inside @media (max-width: 860px); leave desktop alone.
4. Build and publish sites (publishing-khensu-sites skill / tools/publish.sh).
5. Push GitHub; verify repos are public; link Releases for IPAs.
6. Point install copy at GitHub + PWA, not store-only.
```

## Install walkthroughs (short)

| Path | Steps |
| --- | --- |
| PWA | waves.khensu.nu → Share → Add to Home Screen |
| Sideload | Download `nu.waves.ipa` from khensu-apple Releases → Sideloadly / AltServer |
| Source | clone khensu-apple + khensu-core → `xcodegen generate` → scheme Waves or Ptah → Run |
| Hub | https://khensu.nu/app |

Full text: [`PUBLIC.md`](PUBLIC.md) · live: [https://khensu.nu/sla](https://khensu.nu/sla)

## Do not

- Hold site deploys for patents
- Make repos private by default
- Change desktop layout when only mobile was requested
- Phrase the network as unstoppable
- Put message signatures outside ciphertext or skip the mixnet for messages
