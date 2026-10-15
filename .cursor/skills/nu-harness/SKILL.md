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

Product hosts (`bi`, `waves`, `create`, `fi`, `webe`, …) share one Google-managed cert (`moqom-products-*`) on the sites HTTPS proxy. **If that cert is PROVISIONING, every product host serves the wrong certificate (e.g. `CN=elliottwave.dev`). Browsers block CSS/JS → bare unstyled HTML. This is a full outage.**

### Never do this

1. **Never** add a hostname to `product_hosts` in `moqom-pq/deploy/envs/web/main.tf` until:
   ```bash
   dig +short HOST A   # must print 34.107.228.246 — not empty, not NXDOMAIN
   dig +short HOST AAAA  # must be empty (or also correct); NXDOMAIN fails the pack
   host HOST             # must not say "not found"
   ```
2. **Never** `terraform apply` a `product_hosts` change that recreates `moqom-products-*` and walk away while status is `PROVISIONING`. Stay until:
   ```bash
   gcloud compute ssl-certificates describe CERT --global --project=moqom-503700 \
     --format='value(managed.status)'   # must be ACTIVE
   curl -sI --max-time 10 https://bi.khensu.nu/ | head -1   # HTTP/2 200
   echo | openssl s_client -connect bi.khensu.nu:443 -servername bi.khensu.nu 2>/dev/null \
     | openssl x509 -noout -subject   # must NOT be CN=elliottwave.dev
   ```
3. **Never** put a brand-new subdomain on the **shared** products pack. Add it with `own_certificate = true` so a DNS mistake cannot take down bi/waves/create:
   ```hcl
   "sla.khensu.nu" = { site = "khensu-nu", page = "sla", own_certificate = true }
   ```
   Only fold it into the shared pack later, after it has been ACTIVE alone.
4. **Never** destroy or replace the products cert to “clean up” while any product host is live without the module’s wait-until-ACTIVE gate (see `modules/sites` `null_resource.products_cert_active`).

### If product HTTPS is already wrong

1. Check: `gcloud compute ssl-certificates list --global --project=moqom-503700 --filter='name~moqom-products'`
2. If PROVISIONING because of a bad host: **remove that host from `product_hosts` immediately**, apply, wait for ACTIVE.
3. Confirm apex still works (`https://khensu.nu/…`) — content is fine; only the product cert SNI is wrong.
4. Do not publish more site builds as a “fix” for SSL — GCS is not the problem.

### Preflight before any sites terraform apply that touches hosts or certs

```bash
dig +short sla.khensu.nu A; host sla.khensu.nu   # example for any new name
gcloud compute ssl-certificates list --global --project=moqom-503700 \
  --filter='name~moqom-products' --format='table(name,managed.status)'
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
- Leave product hosts on a PROVISIONING cert
