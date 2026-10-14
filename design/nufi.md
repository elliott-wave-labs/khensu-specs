# nu.Fi: the khėnsu.ñü finance platform

**Status: proposed, 11 October 2026.** Design sketch; the full design doc and a patent assessment (`PATENTS.md`) follow once it's built (`AGENTS.md`). Shown as **nu.Fi**; code, packages and identifiers use `nufi` (`nu.khensu.nufi`). The address is `nu:fi.khensu.nu` (host `fi.khensu.nu`; code stays `nufi`).

## 1. What it is

nu.Fi is all of the money on khėnsu.ñü: the basic income, what creators and node operators earn, what subscriptions pay for, and the ways people fund each other. Everything moves through the shielded pool (`PLAN.md`, Shielded payments) with no platform cut. In order of priority:

### 1.1 ñü.bi, the ñü basic income

The first thing nu.Fi does, and the reason the network exists (`AGENTS.md`). Stage one, at launch: everyone who runs a node is paid in USDC for verified work, at one worldwide rate. Stage two, in research: an equal dividend for every unique person, proven without identity or biometrics. Detail in `design/node-earnings.md` 8 and on khensu.nu/bi.

### 1.2 Creator economics

Every view (one minute watched) or play pays the creator 1¢, $10 per 1,000, with no platform cut (decided 11 Oct 2026, `OPEN-QUESTIONS.md` 89). Tips, the creator's own subscriptions and their sales of albums, downloads and tickets go to them whole. Apps on webË pay a flat 10% on in-app purchases and subscriptions, never scaled up or down; tips stay 100% to the person (`design/app-commerce.md`).

### 1.3 Node contributor economics

Anyone can join: a Mac or a Raspberry Pi 5 on an ordinary internet connection is a node, and a suñůlink.shield joins the radio mesh (`design/mesh.md`). Nodes are paid every epoch for verified work (packets mixed, bytes stored and challenged, relay minutes, media delivered), shared by work at one worldwide rate, never by location (`design/node-earnings.md`).

### 1.4 Subscriptions fund the network

Pro, Ultra and Akashic subscriptions pay for everything above. After Apple's 15%, half goes to the network in USDC and half to the founder's company (decided 11 Oct 2026, `PLAN.md` 7): Pro $4.24 ($2.12 each), Ultra $170 ($85 each), Akashic $850 ($425 each).

- **No shareholders.** There are no outside shareholders taking a share of either half. The founder's half goes to Elliott Wave LLC, solely owned by the founder; at the dead-man's switch, founder powers pass to consensus (`PROTOCOL.md` 12.5–12.7).
- **The network is paid more than it costs.** Prices are set so the network's half exceeds what it costs to run. That surplus is the income: it pays node operators beyond their costs (stage one of ñü.bi) and, as it grows, funds the equal dividend for every person (stage two).
- **No cut anywhere else:** not on views, engagement, hosting, network work, gifts, or creators' own sales and subscriptions.

### 1.5 Payments and tickets

Private payments between people, tap to pay at the till, and private ticketing: tickets for festivals, local and big music shows, retreats and events are anonymous, unlinkable tokens (the `ticket` contract, `WEBE.md` 14), bought with nu.Fi and scanned at the door with ñü.code (`design/ring-code.md`).

### 1.6 Funding each other

| Product | What happens | Closest existing service |
| --- | --- | --- |
| **nu.Fi Give** (microgiving) | Gifts to people, causes and communities, from cents up | GoFundMe, Kiva's donation side |
| **nu.Fi Back** (crowdfunding) | Back a project for a reward or pre-order, released only if the goal is met by the deadline | Kickstarter |
| **nu.Fi Invest** (investment network) | Buy shares, revenue shares or notes in startups and local businesses | Wefunder, Republic, StartEngine |

Each campaign is a webË site (`name.khensu.nu/...`) and a public-square post, and the network fee goes to node operators like any other transfer.

### 1.7 Microlending, last

| Product | What happens | Closest existing service |
| --- | --- | --- |
| **nu.Fi Lend** (microlending) | Small loans between people or to small businesses, repaid in instalments | Kiva, Zidisha |

Lending comes last: it carries the most regulation and the most risk to the people using it (section 4).

## 2. How it uses the network

- **Campaigns are signed objects.** A campaign is a content-addressed webË document signed by its creator's ML-DSA-87 key and logged in the key transparency log, so its terms (goal, deadline, rewards, interest, share terms) can't change after anyone pays in. Updates are new signed versions; the history is public.
- **All-or-nothing without a custodian.** Backers' payments go into an escrow note that only releases to the creator if the consensus records that the goal was met by the deadline. Otherwise every backer's note refunds automatically. No company, khensu.nu included, holds the money; the committee only checks proofs (non-custodial, as in the shielded pool). *Design question:* whether threshold-released escrow notes keep the pool's unlinkability; see section 6.
- **Private between people, public where it has to be.** Who backed or gave what stays private by default: the creator sees totals and the pledges' reward choices, not identities, unless a backer chooses to share. Regulated products (Lend, Invest) need identity checks, but a licensed partner holds that identity, not khensu.nu, and the network never links it to messages (section 4).
- **Reputation without surveillance.** Creators and borrowers can show verifiable facts (past campaigns delivered, loans repaid on time) as zero-knowledge credentials from the consensus record, without a credit bureau or a public history of everyone they've dealt with.
- **Repayments ride the tick.** Loan instalments and investor distributions are scheduled transfers sent as mixnet messages on the constant-rate tick, so timing doesn't reveal who owes whom.

## 3. Economics

- **No platform cut** on Give and Back. The only charge is the network fee per transfer (a fraction of a cent, design target), paid to node operators.
- Lend and Invest carry the licensed partner's fees (identity checks, compliance, filings), shown before anyone commits. khensu.nu takes no spread on loans and no carry on investments.
- **Operators earn** from nu.Fi traffic like any other node work, so the network itself is paid for carrying the money.

## 4. Regulation by product (to confirm with counsel per country)

These products sit in very different legal categories. That's why the rollout below starts with the least regulated ones.

| Product | US category | What it needs |
| --- | --- | --- |
| Give | Donations | Gifts between people are lightly regulated. Soliciting for charities triggers state charitable-solicitation registration, and tax-deductible giving needs a 501(c)(3) or a fiscal sponsor. Platform anti-fraud duties apply |
| Back | Pre-orders and rewards, not securities | Consumer protection (deliver or refund; FTC rules on mail-order timing), clear terms that a backer isn't buying equity. Kickstarter-style campaigns must never promise returns |
| Lend | Consumer or business lending | Lending is licensed state by state (or done through a partner bank), with usury caps, Truth in Lending disclosures and fair-lending rules. Peer-to-peer lending notes were treated as securities in the US (Prosper and LendingClub registered with the SEC). Kiva-style 0% loans to borrowers abroad go through local microfinance partners |
| Invest | Securities | Reg CF (up to $5 million a year per issuer) must run through a registered funding portal or broker-dealer that is a FINRA member. Reg A+ and Reg D 506(c) are alternatives. Investor limits, issuer disclosure (Form C) and annual reports apply |
| All | Money movement | Money-transmission analysis, which the non-custodial design helps with but doesn't settle. Sanctions screening at pool entry and exit. AML and KYC wherever a licensed partner is involved. App Store 3.1.5 per region for crypto and 3.2.1 for donations |

Outside the US, the equivalents differ: EU ECSP Regulation for crowdfunding (one licence passported across the EU), UK FCA rules, and local microfinance laws (Morocco has its own microcredit regime; *verify*).

**Conflict rule:** a funding portal can't host offerings in which it has a financial interest. The khensu.nu coin sale and any Elliott Wave raise therefore never run on nu.Fi Invest (`business/FUNDING.md`).

## 5. Rollout

1. **At launch:** ñü.bi stage one (node pay), creator pay at 1¢ a view or play, the subscription split, private payments and tickets.
2. **Give**, then **Back**: no securities and no lending licence. Both use the shielded pool and escrow notes as they are.
3. **Invest** through a registered funding portal partner first; register our own funding portal (or the EU ECSP equivalent) once volume justifies it.
4. **Lend**, last: at 0% between people and through microfinance partners abroad (Kiva's model), then interest-bearing loans through a licensed lending partner.
5. **ñü.bi stage two**, the equal dividend, once personhood without identity is solved (`design/node-earnings.md` 8).

## 6. Open questions

- Escrow notes released by the consensus on goal and deadline: can they keep the pool's unlinkability and era expiry, with automatic refunds?
- How a licensed partner verifies identity for Lend and Invest without khensu.nu ever holding it, and without linking it to the user's messaging identity.
- Loss handling for Lend (defaults) without a credit bureau: reputation credentials only, or a pooled reserve?
- Whether nu.Fi Back should become the checkout for suñůlink.shield once Back is live (site is email pre-order now, then ñü.wallet when invoiced; no Stripe; `PLAN.md`).
- Patent assessment: consensus-released all-or-nothing escrow in a shielded pool, and repayments hidden in constant-rate cover traffic, may be new; assess before any public detail (`PATENTS.md`).
- "No shareholders" (1.4) against `business/FUNDING.md` and the token allocation in `PLAN.md` 7, which mention a company raise and a company token share: confirm they're consistent before either is published.
- How plays beyond what a subscriber's plan covers are paid for (`OPEN-QUESTIONS.md` 89).
