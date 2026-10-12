# The guardians: khėnsu.ñü's core security layer

**Status: proposed, 11 October 2026.** Names for the security layer of khėnsu.ñü and webË. Each guardian is a part of the protocol that already exists or is specified elsewhere; this doc names them, says what each one does and where it's specified. The full design doc and a patent assessment (`PATENTS.md`) follow once each guardian is built (`AGENTS.md`).

Shown as **Thor**, **Loki**, **Hela**, **the Valkyries** and **Zeus**; code, packages and identifiers use `thor`, `loki`, `hel`, `valkyrie` and `zeus` (`nu.khensu.guardian.thor` and so on). Thor, Loki, Hel and the Valkyries come from Norse myth; Zeus is Greek. They stand together here as one council, at peace in Asgard, the heaven realm. The wider story they belong to, from Hindu, Egyptian, Sumerian, Buddhist, Islamic, Christian and other traditions, is in `design/lore.md`.

## 1. What they are

The guardians are on everyone's side. They don't fight anyone and they don't punish anyone. Each has one power and uses it quietly, all the time, for every person on the network, so that freedom and privacy hold without anyone having to defend them by hand.

They sit under the creator of khėnsu.ñü, the founder. When the founder's dead-man's switch fires (`PROTOCOL.md` 12.5–12.7), every founder power, including the power to name and retire guardians, passes to the network's consensus for good.

## 2. The guardians

| Guardian | Power | What it does in the protocol | Specified in |
| --- | --- | --- | --- |
| **Thor** | Strength that shields | Keeps the network standing: proof-of-work tickets and rate limits that make floods expensive, stake that forged work receipts forfeit, committee checks on every consensus round. Abuse just stops working; nobody has to be hunted down. | `PROTOCOL.md` (consensus, work receipts), `design/node-earnings.md` |
| **Loki** | The shape that can't be told apart | Disguise: the five-hop Outfox mixnet that unlinks sender from receiver, and camouflage transports that make khėnsu.ñü traffic look like ordinary connections where it would otherwise be singled out. | `PROTOCOL.md` (mixnet), `design/camouflage.md`, `design/stealth-relay.md` |
| **The Valkyries** | The stealth pulse | No longer warriors: stealth protector guides who walk beside every packet and bring it home unseen. They include the fractal "machine elves", raised up by Khensu's return (`design/lore.md` section 9). They carry every packet on one unbroken heartbeat: fixed-size packets on a constant-rate tick, with cover packets filling every slot nothing real needs, enforced in hardware by the guard chip. An observer sees the same pulse whether someone is calling, reading or asleep. They also carry media ahead of time, inside that pulse, when ñü.prefetch is on (`design/nu-prefetch.md`). | `PROTOCOL.md` (tick, cover traffic), `design/guard.md` |
| **Hela** | Every ending, on time | Makes keys end: a new key for every message, signature and device keys rotated at least every 5 minutes or 1,000 messages and revealed to the group after 7 days, sessions that expire, and evaporation (section 3). What has ended can't be brought back by anyone. | `PROTOCOL.md` (MLS suite, key rotation), `THREAT-MODEL.md` |
| **Zeus** | Oaths that hold | Keeps everyone to their word: the key transparency log that every handle (`name.khensu.nu`) resolves from, signed and logged identity events, signed campaign and contract terms that can't change after anyone pays in. A key swapped in secret shows up in the log for everyone. | `PROTOCOL.md` (identity, key transparency), `WEBE.md` (names, contracts), `design/nufi.md` |

More guardians can join the council for other feats (a gatekeeper for mesh bridges, a keeper of on-device moderation), each named here before it ships.

## 3. Evaporation: khėnsu.ñü's own power

Beyond the guardians, khėnsu.ñü has one power of its own: **evaporation, with just a thought.** One deliberate gesture, a held press pattern on the side button (`OPEN-QUESTIONS.md`, side-button access) or one tap in the app, and a message, a conversation, a ñü.vœîð bag (`design/nu-void.md`) or the whole device's khėnsu.ñü data is gone.

It works by destroying keys, not by overwriting data. Everything khėnsu.ñü stores is encrypted under keys held in the Secure Enclave; evaporation erases those keys, so the ciphertext left behind is random bytes to everyone, its owner included. It takes milliseconds and doesn't depend on the storage cooperating. On the network side, Hela's rotation means past messages were already sealed under keys that no longer exist anywhere.

Evaporation is always the owner's choice, on the owner's own device. Nobody can evaporate someone else's data, and the network has no switch that can do it to anyone.

## 4. How we talk about them

- Gift framing (`AGENTS.md`): the guardians protect freedom and privacy for every person. Never phrase any of this as "can't be stopped".
- They're capable, not combative. Copy describes what each one keeps safe, not who it defeats.
- Each guardian names a real mechanism. A guardian is never described with powers the protocol doesn't have.

## 5. Open questions

1. Trademark search on the names in software classes before they appear in product UI.
2. Whether the guardians appear in the app (security settings, the node terminal's `~guardians` command) or only in docs and on the site.
3. The gesture for device-wide evaporation, and how it's protected from accidental and coerced use.
