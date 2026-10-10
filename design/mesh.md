# Mesh, push and the khensu shell

How khensu.nu can carry messages, feeds and calls without a telecom carrier: a mesh of phones, shells, home nodes and portals, with satellites where there is nothing else. Status: design, with estimates to be replaced by measurements. Open questions in `OPEN-QUESTIONS.md` section J.

## 1. Architecture: home nodes are the towers

A pure phone-to-phone mesh can't replace telecom: in a shared radio medium, each device's usable throughput falls as the mesh grows (Gupta and Kumar, 2000), and every extra hop costs capacity and latency. So the design is layered, and multi-hop is the fallback, not the normal path:

| Layer | Devices | Radio | Range | Role |
| --- | --- | --- | --- | --- |
| Personal | Phone and its shell | Bluetooth, Wi-Fi Aware | touching | The shell is the phone's radio and node |
| Neighbourhood | Shells, home nodes, portals | Wi-Fi HaLow (802.11ah, sub-GHz); Wi-Fi 6 at short range | about 1 km (HaLow), about 100 m (Wi-Fi) | Home nodes and portals act as community access points |
| Backhaul | Home nodes, portals, servers | Fiber, cable, fixed wireless | the internet | Joins neighbourhoods to the global node network |
| Sky | Large shells, home stations | Satellite (section 5) | global | Backhaul where there is no ground link |

- **Normal case:** shell → nearest home node or portal over HaLow (one hop) → internet → mixnet. This is a community-run access network: every home node with a HaLow radio is a small cell tower that earns from token burning.
- **No backhaul nearby:** shells relay over several HaLow or Wi-Fi hops until one reaches a home node, a portal or a satellite link.
- **Internet shut down:** neighbourhoods keep working locally; store-and-forward and public-feed gossip carry data between them as people move (PLAN, Public square); satellite links bridge to the global network.

## 2. Capacity on the mesh (estimates)

- **Absolute cover on the internet** uses about 160 kbit/s each way per open phone (2 s ticks, 4-packet bursts).
- **A HaLow cell** shares roughly 1–15 Mbit/s near the access point and about 0.15–1 Mbit/s at 1 km. At the internet tick rate, one cell carries only about 10–30 open phones.
- **So the mesh has its own constant tick:** 1 small packet every 2 s each way (about 40 kbit/s), still constant and therefore still stealthy, carrying text, receipts, typing, nu-media previews and feed updates. A cell then carries about 40–120 open phones, and more with Wi-Fi 6 at short range.
- **What runs on the mesh:** messaging, feeds, forums, voice calls within a few hops (Opus at low constant bitrate). **What doesn't:** Places 360° video and large originals, which wait for backhaul.
- **Density:** in a city, one HaLow home node per few hundred people covers messaging for everyone nearby; rural areas need more hops or satellites.
- **Spectrum:** unlicensed bands have power limits (for example 1 W EIRP in the US 902–928 MHz band, much less in parts of Europe), which set the ranges above.

## 3. Push without Apple

Today the push gateway is the network's one central piece, because waking an iPhone app needs APNs (`THREAT-MODEL.md` 4.5). The shell removes that dependency for its owner:

- The shell keeps its own constant tick with the network (internet through a home node, or the mesh) and receives the owner's mailbox items in its downstream slots. "Push" is just the downstream of the tick: the network delivers into slots that are sent anyway, so pushing reveals nothing.
- The shell is a Bluetooth accessory. When it has something for the phone, it sends a Core Bluetooth notification, which wakes the app in the background (bluetooth-central background mode with state restoration). No APNs, no push gateway, no wake capability.
- Public content is pushed too: popular feed items and followed accounts are gossiped outward through home nodes and shells, so the feed is current before the app opens.
- The shell holds an encrypted outbox and inbox, so messages queue and arrive even while the phone is off.

## 4. The shell as a node

- **Relay:** forwards sealed mesh packets and, when backhauled, takes node roles that tolerate mobility (cover, mailbox replica for its own neighbourhood, cache).
- **Content:** caches and serves public objects (feeds, nu-media, map tiles) to nearby devices.
- **Committee:** eligible for committee duty only while its lease is met: backhauled, charged and expected to stay so for the whole epoch, with the same stake and slashing as any node. Most shells will qualify only at home on a charger.
- **Earnings:** from token burning in proportion to verified work, like any node.

## 5. Satellites

Phones' built-in satellite features only reach the networks Apple or the carrier choose (Globalstar for iPhone). The shell can carry its own satellite radio, in the large-capacity version or a separate home station, because useful satellite radios don't fit within a camera bump:

| Option | Speed | Size | Notes |
| --- | --- | --- | --- |
| Iridium SBD | about 340 B up, 270 B down per message | about 32 × 30 × 8 mm module | Global, including oceans; a 5 KB signed message needs about 15 messages, so text only, at high cost per byte |
| Iridium Certus 100 | about 22–88 kbit/s | larger module and antenna | Global; fits the large shell or a home station |
| NB-NTN (3GPP Release 17), for example Skylo | a few kbit/s | small chipsets | Standards-based and multi-operator, but needs operator agreements |
| Starlink | 50–200+ Mbit/s | dish (home station only) | Backhaul for home nodes and portals; its direct-to-cell service runs only through carrier partners |

- **Stealth over satellite is weaker:** the satellite operator sees the terminal and its traffic volume, and a constant 2 s tick costs too much there, so satellite links carry sealed mixnet packets at a low constant rate.
- **Legal:** satellite terminals need authorisation in many countries, and some ban or restrict them. The app enables satellite only where it is legal.

## 6. Hardware: the khensu shell

- **Shape.** A curved, organic shell that fills the back of the phone up to the height of the camera bump, so the back becomes flat and the shell looks like part of the phone. Phones without a camera bump get a full back cover. Held by a MagSafe-compatible magnet ring plus a micro-suction layer.
- **Styles and battery (from the CAD model in `hardware/shell`).** Cells fill the cavity around the MagSafe ring, the board and the antenna window, at about 0.45 Wh/cm³. Phone dimensions are placeholders until Apple's accessory drawings replace them.

  | Style | Pro phone (camera plateau) | Standard phone (camera island) |
  | --- | --- | --- |
  | Card (Pocket-size, 56 × 86 × 5.2 mm) | 4.1 Wh, 46 g | 4.1 Wh, 46 g |
  | Fill (below the bump) | 2.2 Wh, 3.5 mm, flush | 2.0 Wh, 3.4 mm, 0.8 mm proud |
  | Wrap (whole back around the bump) | 2.8 Wh, 3.5 mm, flush | 4.8 Wh, 3.4 mm, 0.8 mm proud |
  | Wrap XL (3 mm proud) | 11.4 Wh, 93 g | 17.0 Wh, 128 g |

  The slim styles can't be thinner than about 3.4 mm (suction film, base, board, skin), so on phones with a lower bump they sit slightly proud of it. The board and radios draw roughly 1 W while relaying (estimate), so a slim shell relays for 2–5 hours alone and then falls back to the phone; the XL relays all day.
- **Power.** The shell runs on its own battery. MagSafe on iPhone only receives power, so the fallback to the phone's battery uses USB-C (iPhone 15 and later can supply about 4.5 W): the fill, wrap and case versions include a USB-C plug. The shell charges from a Qi2 receiver coil on its outer face, like Apple's MagSafe battery, and charges the phone over USB-C. The card has no plug and covers the phone's MagSafe coil, so the phone charges with the card removed.
- **Radios.** Bluetooth LE and Wi-Fi (to the phone and nearby devices), Wi-Fi HaLow (neighbourhood), optional satellite in the large version.
- **Board (decided).** One Linux system-on-module with the radios, always on while attached, running full node software (tatenan) in a reduced profile. No separate low-power controller. The mesh tick stays at 2 s whatever the battery level.
- **Materials and versions.** Slim, large-capacity, titanium, shockproof case and dive case. Titanium blocks radio and wireless charging, so the titanium version needs antenna windows (like the bands on the phone itself) and a non-metal area over the coil. The dive case protects the phone; radio doesn't travel underwater, so the mesh works only at the surface.
- **Per-model shells.** One core module (board, radios, battery) with model-specific shells, because every camera bump is different.
- **Heat.** About 1 W spread over the whole back is a few degrees of rise; charging is the main heat source. A graphite sheet spreads heat from the board and coil across the outer skin (aluminium or titanium), and above a 41 °C skin temperature or when the phone reports thermal pressure the shell cuts its charging rate first, then pauses optional work (cache serving, committee duty). The 2 s tick and cover never change. It never charges the phone and itself at full rate at once.

## 7. Not a carrier

The network carries data, not phone numbers. It doesn't connect to the phone network, so it can't place emergency calls, and it shouldn't be marketed as a phone service, which would bring carrier regulation and emergency-call obligations. Emergency calls use Apple's emergency calling and Emergency SOS via satellite, which work well (decided 9 Oct 2026); khensu never gets in their way. Everything else runs on our own network and our own satellite links, with no dependence on Apple.

## 8. Phones as nodes

Phones are nodes too (decided 9 Oct 2026): any iPhone on iOS 26 (iPhone 11 and later) runs node mode while the app is open, plugged in and on Wi-Fi. Old phones are often faster than a Pi 5 (an A13 beats it on CPU), have Wi-Fi 6 and their own battery as a UPS.

- **Foreground only.** iOS doesn't let apps relay in the background, so node mode keeps the app open: idle timer off, screen dimmed to black with a minimal status display (no OLED burn-in), Guided Access recommended so it stays open.
- **Battery care.** Uses iOS's charging limit where available (80% on iPhone 15 and later), shows battery temperature, and pauses relaying if the phone gets hot.
- **Roles.** Phones behind home routers usually can't accept inbound connections, so they take roles that dial out (cover, mailbox replica, cache, PIR mirror, mesh relay over Wi-Fi Aware and Bluetooth); with a reachable IPv6 address they can also mix. Committee duty only with an epoch lease, like any node.
- **Earnings.** From token burning in proportion to verified work, like any node.
- **Never on cellular.** Node mode stops when Wi-Fi or power is lost.
- **Capacity:** counts against the home connection's upload, like any node in the same home.
