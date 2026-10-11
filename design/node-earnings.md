# Node earnings model

Internal estimate, 11 Oct 2026. Every number here is an **estimate** built on assumptions that are not decided (price, paying share, media demand, node count). Nothing in this document goes on a public page, campaign or app screen: earnings claims about a token and a device are what the SEC's 2025 case against Nova Labs (Helium) was about, and `PLAN.md` keeps node earnings factual and amount-free until counsel signs off (`OPEN-QUESTIONS.md` 84).

## 1. Where operator money comes from

Operators are paid only from real demand, through burn and mint (`PLAN.md`, Token):

1. **Subscriptions.** Price after Apple's 15%, with half burned for capacity.
2. **Media and web delivery.** MOQOM Cloud customers, creators' paid content, sites and social hubs on webE pay in dollars for delivery, and that money is burned for capacity.
3. **Network fees** on shielded payments (fractions of a cent; small).

Protocol emission (8% a year, halving every 2 years) also mints tokens to operators, but its dollar value depends on the token price. It is left out of every figure below, because counting it would be an earnings claim about the token.

## 2. Weighting by traffic

- **Users pay by region.** Subscription prices follow purchasing power, as App Store price tiers already do. Example: $4.99 a month in high-income countries and $1.99 in Morocco and similar markets.
- **Nodes are paid by the work they carry, at one global rate per unit of work** (packet-hops, byte-hours stored, relay minutes, bytes served). A node therefore earns in proportion to the traffic it carries. Countries with more paying traffic put more money into the pool, so the pool is weighted by traffic and by local prices.
- **Why not pay nodes less by country.** Location-based rates would require the network to know where each node is, which works against stealth, and anyone could fake a high-pay location with a VPN. One rate per unit of work is simpler and can't be gamed that way. It also favours low-cost countries: a node in Morocco earns the same dollars for the same work as one in Germany, and those dollars buy about two and a half times as much locally.
- **Locality still matters for media.** Mailbox, cache and media roles are served near the people requesting them, so a region's own media demand mostly flows to its own nodes. Mixing is spread worldwide for anonymity.

## 3. Rates per unit of capacity

Capacity is the upload a node contributes (50% of the connection by default; `OPEN-QUESTIONS.md` 10). 1 Mbit/s fully used for a month is about 329 GB.

| Source | Operator pay | Per Mbit/s-month at full use |
| --- | --- | --- |
| Messaging only, blended price ($0.06 per daily user per month to operators: 5% paying, about 70% of users at lower regional prices) | about $0.0006/GB | about $0.20 |
| Media and web delivery, low case | $0.002/GB | about $0.66 |
| Media and web delivery, high case (current wholesale CDN rates in Europe and North America) | $0.005/GB | about $1.64 |

Messaging alone pays little per gigabyte because cover traffic is most of the bytes. **Media delivery is what can make a node pay a living.**

## 4. Monthly estimate per node (dirhams at about 9.2 per dollar)

Three cases, all after the operator's own electricity (a Pi 5 uses about 5 kWh a month, under 10 MAD):

- **Low:** messaging only, nodes 100% used.
- **Middle:** mostly media at $0.003/GB, nodes used 30% of the time on average.
- **High:** media at $0.005/GB, nodes fully used. This is an upper bound, not an expectation.

| Node (capacity shared) | Low | Middle | High |
| --- | --- | --- | --- |
| Home broadband, 20 Mbit/s shared | about 40 MAD | about 55 MAD | about 300 MAD |
| Fibre, 100 Mbit/s shared | about 190 MAD | about 270 MAD | about 1,500 MAD |
| Gigabit fibre Pi 5 or Mac, 500 Mbit/s shared | about 940 MAD | about 1,400 MAD | about 7,500 MAD |
| Server, 7 Gbit/s | about 13,000 MAD | about 19,000 MAD | about 105,000 MAD |

**5,000 MAD a month (about $540)** takes about 330 Mbit/s of fully used media delivery at the high rate, or about 1.8 Gbit/s at the middle case. Today that means a gigabit-fibre node fully used by media demand, or a small server. An ordinary home connection earns tens to hundreds of dirhams.

## 5. The network-wide ceiling

Operators share one pool. Per-node income equals the total pool divided by everyone's work, so more nodes than demand means less each.

- **Example:** paying 1 million operators 5,000 MAD each takes about $540 million a month (about $6.5 billion a year) in burns. Messaging alone at $0.06 per daily user would need about 9 billion daily users to fund that. A level like that needs MOQOM Cloud and webE media delivery at the scale of a large CDN.
- **A basic income for everyone who runs a node is therefore not something the design can promise.** What it can honestly say: every node is paid for the work it does at one worldwide rate, there's no cut taken in between, and a dollar earned buys more where living costs are lower.

## 6. Levers that raise earnings per node

- Media and web delivery volume (MOQOM Cloud, creators, webE sites): the biggest lever.
- Paying share and regional prices.
- Fewer cover bytes per message (burst size, hops; `OPEN-QUESTIONS.md` 2c and 31), which raises pay per byte for messaging.
- Node admission: the committee can cap new operators per region when utilization is low, so incomes don't dilute below running costs. This is a governance choice with fairness trade-offs.

## 7. To validate

Testnet measurements of bytes per daily user, real media demand, utilization by region, and operator churn at each income level; final pricing and token parameters with counsel (`PLAN.md`, pricing-token-numbers).
