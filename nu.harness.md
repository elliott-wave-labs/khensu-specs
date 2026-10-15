# nu.harness

Agent harness for khėnsu.ñü work across Cursor and other open agents. Skill: `nu-harness` (`~/.cursor/skills/nu-harness` and `.cursor/skills/nu-harness` in this repo).

## ALWAYS LIVE — product HTTPS

Product hosts share `moqom-products-*` on the sites HTTPS proxy. A **PROVISIONING** products cert makes every product host (bi, waves, create, …) present the wrong certificate (`CN=elliottwave.dev`). Browsers then block CSS/JS and the site looks like unstyled HTML. **Treat that as a full outage.**

Rules:

1. Before adding any host to shared `product_hosts`, `dig +short HOST A` must return `34.107.228.246` (not NXDOMAIN).
2. New subdomains use `own_certificate = true` so they cannot recreate the shared pack.
3. Never leave an apply that replaced `moqom-products-*` until `managed.status` is `ACTIVE` and `openssl s_client -servername bi.khensu.nu` is not `elliottwave.dev`.
4. The sites module waits for ACTIVE before pointing the proxy at a new products cert (`null_resource.products_cert_active`). Do not bypass it.

SLA page: [https://khensu.nu/sla](https://khensu.nu/sla) (`sla.khensu.nu` only after DNS + own cert ACTIVE). Full public notice: [`PUBLIC.md`](PUBLIC.md).

## When to use

khensu.nu sites, product hosts, GitHub repos under elliott-wave-labs, App Store / sideload install, dead-man's switch, SLA, SSL/terraform for sites.

## Fixed rules

1. **Publish sites immediately.** Never hold for a patent filing.
2. **Keep code public.** First-party `khensu-*` repos stay public.
3. **Install without stores.** Safari PWA, GitHub IPA sideload, `xcodegen` / Xcode. Team ID `LHS49D8RYY`.
4. **Desktop vs mobile.** Desktop perfect → only `@media` mobile rules.
5. **Display names.** People see khėnsu.ñü, ñü.ŵævẽš, …; code/URLs stay ASCII.
6. **Commands** start with `~`, never `/`.
7. **Wording.** Gift of freedom, privacy, basic income — never “can't be stopped”.
8. **Multi-root** under `~/Documents/GitHub/khensu/`.
9. **Licences.** core Apache-2.0, specs CC BY 4.0, others AGPL-3.0.

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
- Add NXDOMAIN hosts to the shared products certificate
- Leave product hosts on a PROVISIONING cert
