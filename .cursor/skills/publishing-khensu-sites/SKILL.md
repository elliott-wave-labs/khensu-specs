---
name: publishing-khensu-sites
description: Publishes khėnsu.ñü site work (khensu-site, elliottwave-studio) as soon as it's built, without waiting for patent filings, and applies the khensu display names. Use whenever khensu.nu, khensu-site, tatenan.khensu.nu, elliottwave.studio or a site change, publish, deploy or patent hold comes up.
---

# Publishing khensu sites

## Rules

- **Publish everything. Never hold site work for a patent filing** or a filing receipt, and never ask whether to wait. The user decided this on 11 Oct 2026 and doesn't want to repeat it.
- Publish to **all** sites, including the studio (elliottwave.studio), after each finished change.
- Specs are public on dev.khensu.nu/specs (PROTOCOL, WEBE, THREAT-MODEL, WORK, COMPLIANCE, app-commerce, nu-media), synced with `python3 tools/sync-specs.py` in khensu-site before building khensu-dev. Only the provisional patent applications stay private.
- Launch tone everywhere: present tense, as shipped. Never 'planned', 'coming', 'proposed', 'draft', 'design target' or 'before launch' on a site.
- Launch wording: never "before launch" or "targets" as a launch phrase. Measured figures are **benchmarks**; only hardware figures may be "design targets", carefully calculated. Anything else unmeasured is an estimate, projection or example.

## Display names (text people see; code, URLs, domains, files and data keys stay ASCII)

| Shown | In code |
| --- | --- |
| khėnsu.ñü (e with dot above, U+0117: the dot is Elliott's E; also Ask khėnsu, the khėnsu token), ñü.media, ñü.mømëntš, ñüCode, ñü.ŵævẽš | `khensu.nu`, `khensu-core`, `nu-media`, `moments` (`moments.khensu.nu`), `nucode`, `waves` (`waves.khensu.nu`). Addresses are `nu:` plus the host, as in `nu:waves.khensu.nu`. |
| ñũ.Fî, ñũ.Bî (u with tilde U+0169 and i with circumflex, in nav, headings, titles and labels only; running text keeps nu.Fi and nu.bi) | `nufi` → `fi.khensu.nu`, `nu.bi` → `bi.khensu.nu` |
| ñü.řåł, ñü.ċřêæțẽ | `nu.ral` (page `/memory`), `nu.create` (page `/creators`) |
| Marketing cards and link previews | `src/data/og.ts` and `components/khensu/OgCard.astro`; `sh tools/og.sh` renders the 1200 × 630 stills, the squares, the link thumbnail and the transparent word overlays, then `sh tools/og-anim.sh` makes the 3-second GIF/MP4/HEVC squares into `~/Desktop/khensu-instagram/` and `public/og/<slug>-square.mp4`. Run both before publishing when a card changed. The cards spell the names in full: kħėñšü.ñü, šûñüłîñk.šħîēłð, ñü.îšħẽřü |
| ñü.ÊQ | `eq` |
| webË | `webe` |
| suñůlink.shield | `sunu` |

Diacritics stay in navigation, headings, buttons and labels. Running text uses the ASCII form: nu.waves, nu.void, nu.media, nu.moments, webe, nufi, nu.bi, nu.ral, nu.create, sunulink.shield, nu.network, nu.eq.


## ALWAYS LIVE — do not break product SSL

Product hosts (`bi.khensu.nu`, `waves.khensu.nu`, …) share one managed cert. **Never** add a hostname to `product_hosts` / run sites terraform that recreates `moqom-products-*` as part of a “publish” unless:

1. `dig +short HOST A` → `34.107.228.246` (not NXDOMAIN)
2. New hosts use `own_certificate = true` (never join the shared pack on day one)
3. After apply, wait until the products cert is `ACTIVE` and `https://bi.khensu.nu` returns HTTP 200 with the right cert

**Nav hosts.** A main-nav item is `https://<product>.khensu.nu`, never `https://khensu.nu/<product>` and never a path href. That stays true while DNS or the cert is missing. The apex page can remain as a fallback. It is not the link. Header label → host: e.u → `https://nueu.khensu.nu`, devices → `https://devices.khensu.nu`, eyes → `https://eyes.khensu.nu`, feed → `https://feed.khensu.nu`, vegan → `https://vegan.khensu.nu`, kronos → `https://kronos.khensu.nu`, glass → `https://design.quantumglass.khensu.nu`, skills.music.theory → `https://skills.music.theory.khensu.nu`. A host with no DNS is a Hover record to give Elliott: type A, hostname the product label (`nueu`, `devices`, …), value `34.107.228.246`, no AAAA, no CNAME. Do not add that name to the shared products cert. After `dig +short HOST A` returns the load balancer, attach `own_certificate = true`. Flame and violet are names, not hosts. The violet flame host is `safety.khensu.nu`.

**Product-host HTTPS is not done until openssl CN matches that host.** Apex (`https://khensu.nu/avatars`) is a redirect fallback, not a nav href and not a ship. Pair with `nu-harness` own_certificate bootstrap: dig → create → **attach** → wait ACTIVE (never wait before attach). Multi-label hosts need an explicit A (`indra.og` ≠ `*.khensu.nu`). Project SSL cert quota is 10 — delete stuck unused certs first.

If waves/bi look unstyled (no CSS), check SSL first — not the publish. Cause: products cert PROVISIONING, or an **NXDOMAIN / wrong-A** cert left on the https proxy.


## Build and publish

```bash
cd ~/Documents/GitHub/khensu/khensu-site/sites/khensu-nu && pnpm -s build > /tmp/b.log 2>&1; rg -i "error|Complete!" /tmp/b.log
while pgrep -f publish-sites.sh >/dev/null; do sleep 5; done
cd ~/Documents/GitHub/moqom-cloud && MOQOM_SITES_SKIP_BUILD=1 MOQOM_SITES_DIR=$HOME/Documents/GitHub/khensu/khensu-site/sites sh moqom-pq/deploy/tools/publish-sites.sh khensu-nu
```

- The publish deletes remote files missing from `dist/`, so publish from the full working tree, not a partial checkout.
- Then sync shared components and data to elliottwave-studio and publish it the same way.
- Commit the site work in `khensu-site` with a plain message after publishing.
- Verify live with `curl -s "https://khensu.nu/?v=$RANDOM" | rg <something new>`.
