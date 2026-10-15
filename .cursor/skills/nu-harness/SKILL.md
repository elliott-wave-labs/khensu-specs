---
name: nu-harness
description: >-
  Agent harness for khėnsu.ñü across Cursor and other open agents: always-live
  HTTPS, publish sites immediately, keep repos public, install without stores,
  mobile-only CSS when desktop is perfect, SLA at khensu.nu/sla. Use for khensu
  site, GitHub, SSL, product_hosts, sideload, dead-man's switch, PUBLIC.md or
  nu.harness work.
---

# nu.harness

Companion: `~/Documents/GitHub/khensu/khensu-specs/nu.harness.md` · `PUBLIC.md` · live [khensu.nu/sla](https://khensu.nu/sla).

## ALWAYS LIVE (hard — never break product HTTPS)

Product hosts (`bi`, `waves`, `create`, `fi`, `webe`, …) share one Google-managed cert (`moqom-products-*`) on the sites HTTPS proxy. **If that cert is PROVISIONING, or any NXDOMAIN / wrong-A cert sits on the proxy, every product host can serve `CN=elliottwave.dev`.** Browsers block CSS/JS → bare unstyled HTML. Full outage.

### Never do this

0. **Never** leave an **NXDOMAIN / wrong-A** certificate on `moqom-sites`. That is what makes Google ignore SNI and serve `elliottwave.dev` for bi/waves. Remove those hosts from terraform immediately.
1. **Never** add a hostname to shared `product_hosts` until:
   ```bash
   dig +short HOST A   # must print 34.107.228.246
   dig +short HOST AAAA  # must be empty (or also correct)
   host HOST             # must not say "not found"
   ```
2. **Never** put a brand-new subdomain on the **shared** products pack. Use `own_certificate = true`.
3. **Never** claim product-host HTTPS done from apex alone (`khensu.nu/avatars` ≠ `avatars.khensu.nu`).
4. **Never** wait for an own-cert to be `ACTIVE` *before* attaching it — Google requires attachment + DNS → LB. Waiting first = `FAILED_NOT_VISIBLE` deadlock.
5. **Never** walk away from a products-pack recreate while `PROVISIONING`.

### own_certificate bootstrap (correct order)

Project SSL cert quota is **10 global**. Delete stuck unused certs before creating new ones.

1. Dig preflight (above). Multi-label hosts (`indra.og.khensu.nu`) need an **explicit** A — `*.khensu.nu` does not cover them. Mirror on Hover and Cloud DNS zone `khensu-nu`.
2. Create the own managed cert; attach it to `moqom-sites` **keeping every existing ACTIVE cert**.
3. Stay until own cert `ACTIVE`. Every 30s: bi must stay `CN=bi.khensu.nu` + HTTP 200. If bi breaks, detach the new certs immediately.
4. Ship only when:
   ```bash
   echo | openssl s_client -connect HOST:443 -servername HOST 2>/dev/null \
     | openssl x509 -noout -subject   # must contain HOST
   curl -sI --max-time 10 https://HOST/ | head -1   # HTTP/2 200
   ```

### If product HTTPS is already wrong

1. `gcloud compute ssl-certificates list --global --project=moqom-503700`
2. Remove NXDOMAIN / wrong-A hosts from the proxy and from terraform; wait for products cert ACTIVE.
3. Confirm bi/waves CN + 200. Apex content is separate from product-host SNI.

### Preflight before sites terraform that touches hosts or certs

```bash
dig +short HOST A; dig +short HOST AAAA; host HOST
gcloud compute ssl-certificates list --global --project=moqom-503700 \
  --format='table(name,managed.status)'
for h in bi.khensu.nu waves.khensu.nu create.khensu.nu; do
  echo | openssl s_client -connect "$h:443" -servername "$h" 2>/dev/null \
    | openssl x509 -noout -subject
done
```

## Other fixed rules

1. **Publish sites immediately.** Never hold for a patent filing. Pair with `publishing-khensu-sites`.
2. **Keep code public.** elliott-wave-labs `khensu-*` repos stay public.
3. **Install without stores.** PWA, GitHub IPA, `xcodegen` / Xcode. Team `LHS49D8RYY`. Hub: https://khensu.nu/app
4. **Desktop vs mobile.** Desktop perfect → change only `@media` mobile rules.
5. **Display names.** People see khėnsu.ñü / ñü.ŵævẽš / …; code/URLs stay ASCII.
6. **Commands** start with `~`, never `/`.
7. **Wording.** Gift of freedom, privacy, basic income — never “can't be stopped”.
8. **SLA** at `khensu.nu/sla` until `sla.khensu.nu` has dig A → LB **and** its own cert is ACTIVE.
9. **Multi-root** under `~/Documents/GitHub/khensu/`.
10. **Licences.** core Apache-2.0, specs CC BY 4.0, others AGPL-3.0.

## Do not

- Hold site deploys for patents
- Make repos private by default
- Change desktop when only mobile was requested
- Phrase the network as unstoppable
- Add NXDOMAIN / wrong-A hosts to the shared products certificate
- Claim product HTTPS shipped without matching openssl CN
- Deadlock own certs (wait ACTIVE before attach)
