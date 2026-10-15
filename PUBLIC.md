# Public network — khėnsu.ñü

**Live:** [https://sla.khensu.nu](https://sla.khensu.nu) · [https://khensu.nu/sla](https://khensu.nu/sla)  
**Org:** [https://github.com/elliott-wave-labs](https://github.com/elliott-wave-labs)  
**Status:** Founder handover fired 14 October 2026. Dead-man's switch **ACTIVE** from Venice, CA at 2:22 pm PDT. Every first-party repo is **public**.

Companions: [`DEAD-MANS-SWITCH.md`](DEAD-MANS-SWITCH.md) · [`FOUNDER-HANDOVER.md`](FOUNDER-HANDOVER.md) · [`OPEN-SOURCE.md`](OPEN-SOURCE.md) · [`LICENSING.md`](LICENSING.md)

The network is a gift to humanity and all beings: freedom, privacy and a basic income. Never phrase it as “can't be stopped” (`AGENTS.md`).

---

## 1. SLA

| Promise | Detail |
| --- | --- |
| **100% uptime** | Public site, product hosts and the open archive on the edge |
| **Dead-man's switch** | Weekly keep-alive; 42 days of silence escalates the archive |
| **Code public** | All `khensu-*` repos under elliott-wave-labs |
| **No founder off-switch** | Founder powers ended at handover; nothing restores them |

**Activated:** 14 October 2026 · 2:22 pm PDT · Venice, California · `2026-10-14T21:22:00Z`  
**Keep-alive:** [e@khensu.nu](mailto:e@khensu.nu?subject=FounderCheckIn&body=khensu%20dead-man%20check-in%20alive) · SMS [310-351-4089](sms:+13103514089&body=FounderCheckIn%20alive)

---

## 2. Public repositories

| Repo | Licence | What |
| --- | --- | --- |
| [khensu-specs](https://github.com/elliott-wave-labs/khensu-specs) | CC BY 4.0 | Plan, protocol, threat model, this file |
| [khensu-core](https://github.com/elliott-wave-labs/khensu-core) | Apache-2.0 | MLS, Outfox, UniFFI |
| [khensu-apple](https://github.com/elliott-wave-labs/khensu-apple) | AGPL-3.0 | `nu.khensu.ptah`, `nu.khensu.waves` |
| [khensu-tatenan](https://github.com/elliott-wave-labs/khensu-tatenan) | AGPL-3.0 | Node (Mac / Pi 5) |
| [khensu-chain](https://github.com/elliott-wave-labs/khensu-chain) | AGPL-3.0 | Chain, token, shielded pool |
| [khensu-services](https://github.com/elliott-wave-labs/khensu-services) | AGPL-3.0 | KT log, credentials, push |
| [khensu-devnet](https://github.com/elliott-wave-labs/khensu-devnet) | AGPL-3.0 | One-machine network |
| [khensu-site](https://github.com/elliott-wave-labs/khensu-site) | AGPL-3.0 | Sites including sla.khensu.nu |

Clone (side by side):

```bash
git clone https://github.com/elliott-wave-labs/khensu-specs.git
git clone https://github.com/elliott-wave-labs/khensu-core.git
git clone https://github.com/elliott-wave-labs/khensu-apple.git
git clone https://github.com/elliott-wave-labs/khensu-tatenan.git
git clone https://github.com/elliott-wave-labs/khensu-chain.git
git clone https://github.com/elliott-wave-labs/khensu-services.git
git clone https://github.com/elliott-wave-labs/khensu-devnet.git
git clone https://github.com/elliott-wave-labs/khensu-site.git
```

---

## 3. Install without Apple or Google stores

Apple’s App Store and Google Play are optional. The code and IPAs stay on GitHub.

### 3.1 nu.waves in Safari (no install)

1. Open [https://waves.khensu.nu](https://waves.khensu.nu) in Safari on iPhone or iPad.
2. Share → **Add to Home Screen**.
3. Play; drag sounds in the spacetime bubble. Nothing is processed on servers.

### 3.2 Sideload an IPA (iPhone)

1. On a Mac, install [Sideloadly](https://sideloadly.io/) or [AltServer](https://altstore.io/).
2. Download the latest IPA from [khensu-apple Releases](https://github.com/elliott-wave-labs/khensu-apple/releases) (`nu.waves.ipa`).
3. Plug in the unlocked iPhone, sideload with your Apple ID. Signing stays on your Mac.
4. Free Apple IDs need a re-sign about every 7 days; a paid Developer account lasts a year for registered devices.

Current release: [waves-0.1.0](https://github.com/elliott-wave-labs/khensu-apple/releases/tag/waves-0.1.0).

### 3.3 Build from source (Xcode 26.2+)

```bash
git clone https://github.com/elliott-wave-labs/khensu-apple.git
git clone https://github.com/elliott-wave-labs/khensu-core.git
cd khensu-apple
xcodegen generate
open Ptah.xcodeproj
```

Select scheme **Waves** (`nu.khensu.waves`) or **Ptah** (`nu.khensu.ptah`), your team, a device, Run. Full steps: [docs/INSTALL.md](https://github.com/elliott-wave-labs/khensu-apple/blob/main/docs/INSTALL.md).

### 3.4 Android / Google Play

No Play listing is required to use the open web. Use [waves.khensu.nu](https://waves.khensu.nu) and [khensu.nu](https://khensu.nu) in Chrome; Add to Home screen for a PWA icon. Native Android builds ship from the same public org when the tree is ready — watch Releases.

### 3.5 Get-the-apps hub

[https://khensu.nu/app](https://khensu.nu/app) — App Store when listed, otherwise GitHub install, Releases and the nu.waves PWA.

---

## 4. Live product hosts

| Host | Product |
| --- | --- |
| [khensu.nu](https://khensu.nu) | Home |
| [waves.khensu.nu](https://waves.khensu.nu) | nu.waves |
| [sla.khensu.nu](https://sla.khensu.nu) | SLA + this public notice |
| [dev.khensu.nu](https://dev.khensu.nu) | Specs and repositories |
| [webe.khensu.nu](https://webe.khensu.nu) | webË |
| [create.khensu.nu](https://create.khensu.nu) | nu.create |
| [fi.khensu.nu](https://fi.khensu.nu) / [bi.khensu.nu](https://bi.khensu.nu) | nu.Fi / nu.bi |
| [avatars.khensu.nu](https://avatars.khensu.nu) | ñü.ævätåřş (nu.avatars) |
| [indra.og.khensu.nu](https://indra.og.khensu.nu) | îňðřæ.ōġ (nu.indra.og) |

Address form: `nu:` plus the host, e.g. `nu:waves.khensu.nu`, `nu:sla.khensu.nu`.

---

## 5. Agent harness

Open agents (Cursor and others) use [`nu.harness.md`](nu.harness.md) / the `nu-harness` skill: publish sites immediately, keep repos public, prefer GitHub install paths, never hold site work for patents, never phrase the network as unstoppable.

Live SLA page: [https://khensu.nu/sla](https://khensu.nu/sla).
