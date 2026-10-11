# Node earnings model

Internal estimate, 11 Oct 2026. Every number here is an **estimate** built on assumptions that are not decided (price, paying share, media demand, node count). Nothing in this document goes on a public page, campaign or app screen: earnings claims about a token and a device are what the SEC's 2025 case against Nova Labs (Helium) was about, and `PLAN.md` keeps node earnings factual and amount-free until counsel signs off (`OPEN-QUESTIONS.md` 84).

## 1. Where operator money comes from

Operators are paid only from real demand, through burn and mint (`PLAN.md`, Token):

1. **Subscriptions.** Price after Apple's 15%, with half burned for capacity.
2. **Media and web delivery.** MOQOM Cloud customers, creators' paid content, sites and social hubs on webE̊ pay in dollars for delivery, and that money is burned for capacity.
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

- **Example:** paying 1 million operators 5,000 MAD each takes about $540 million a month (about $6.5 billion a year) in burns. Messaging alone at $0.06 per daily user would need about 9 billion daily users to fund that. A level like that needs MOQOM Cloud and webE̊ media delivery at the scale of a large CDN.
- **A basic income for everyone who runs a node is therefore not something the design can promise.** What it can honestly say: every node is paid for the work it does at one worldwide rate, there's no cut taken in between, and a dollar earned buys more where living costs are lower.

## 6. Levers that raise earnings per node

- Media and web delivery volume (MOQOM Cloud, creators, webE̊ sites): the biggest lever.
- Paying share and regional prices.
- Fewer cover bytes per message (burst size, hops; `OPEN-QUESTIONS.md` 2c and 31), which raises pay per byte for messaging.
- Node admission: the committee can cap new operators per region when utilization is low, so incomes don't dilute below running costs. This is a governance choice with fairness trade-offs.

## 7. One 1-minute video: what creators and nodes earn per view

Assumptions, all estimates:

- **Bytes per view.** nu-media at 500 kbit/s plus 32 kbit/s Opus is about 4.0 MB a minute. Instagram's own file for the benchmark reel is 2.51 Mbit/s, about 18.8 MB a minute.
- **Node work per view.** Each view crosses three node hops (cache to viewer through the mixnet), so 12 MB of node bandwidth per view.
- **Node pay.** $0.002–0.005 per GB (section 3, low and high media cases).
- **Creator pay (proposed, `OPEN-QUESTIONS.md` 89).** A creator pool takes 30% of each subscription after Apple's 15% ($1.27 of Plus at $4.99). Each subscriber's share goes to the creators they actually watched, split by minutes (user-centric, so nobody's money goes to creators they never watch). A Plus subscriber who watches 1,000 minutes in a month pays creators $0.00127 a minute. Free viewers add nothing to the pool, so the blended rate depends on the paying share. Tips and subscriptions to the creator come on top, with no cut.

| Views of a 1-minute video | 1 thousand | 1 million | 1 billion | 1 trillion (network-wide total) |
| --- | --- | --- | --- | --- |
| Delivered with nu-media | 4 GB | 4 TB | 4 PB | 4 EB |
| Delivered as Instagram's file | 18.8 GB | 18.8 TB | 18.8 PB | 18.8 EB |
| Node bandwidth (3 hops) | 12 GB | 12 TB | 12 PB | 12 EB |
| Paid to nodes, all together | $0.02–0.06 | $24–60 | $24,000–60,000 | $24–60 million |
| Creator pool, 5% of viewers paying | about $0.06 | about $64 | about $64,000 | about $64 million |
| Creator pool, all viewers paying | about $1.27 | about $1,270 | about $1.27 million | about $1.27 billion |

For comparison (commonly reported, not verified by us): YouTube Shorts pays creators roughly $0.01–0.07 per 1,000 views and TikTok's Creator Rewards roughly $0.40–1.00 per 1,000 for videos over a minute. Per view, the creator pool at 5% paying is Shorts-level; it reaches TikTok-level and beyond as the paying share rises, and no platform takes a cut of tips.

What this says: per video, node earnings are small, because nu-media makes delivery cheap; that is the point. A node earns a living only from aggregate demand (section 5). A trillion views is roughly a large platform's total short-video traffic over days to weeks, not one video.

## 8. A basic income across countries: options

The design pays for work. A basic income is money paid to people for being people, and paying it without a central registry of persons is an unsolved problem. Options, none decided (`OPEN-QUESTIONS.md` 84, 89):

1. **Work-based, as designed.** One worldwide rate per unit of work. A dollar earned buys about 2.5 times more in Morocco than in Germany, so the same node supports more of a living where costs are lower. Honest, but it's income for work, not a basic income.
2. **A network dividend.** A fixed share of protocol emission split equally among unique people each month. Needs proof that each person counts once without identifying them: anonymous credentials over a one-time check by a partner (Sybil resistance is the hard part; iris scanning, as Worldcoin does, conflicts with the threat model). Its dollar value depends on the token price, so it's an earnings claim about a token and needs counsel.
3. **A dividend funded by revenue.** A share of company revenue paid equally to every active account with a recovery kit, in USDC. No token-price claim, but small until revenue is large, and still needs Sybil resistance.

Rec: ship (1), research (3) as the long-term basic-income path, publish nothing about amounts until counsel signs off.

## 9. To validate

Testnet measurements of bytes per daily user, real media demand, utilization by region, and operator churn at each income level; final pricing and token parameters with counsel (`PLAN.md`, pricing-token-numbers).
