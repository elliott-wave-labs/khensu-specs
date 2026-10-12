# ñü.vœîð: the bag

**Decided 11 October 2026. Chunks fixed at 64 KiB with ñü.fêět on 12 October 2026.** Shown as **ñü.vœîð**. Code, URLs and the host use `nu.void` (`void.khensu.nu`). Commands stay `~node void`. It is not a vault. A vault is a room in someone else's building. ñü.vœîð is a bag that opens into another place: what you put in it lives as nameless 64 KiB pieces, and only your memory of the bag knows how they go back together. Elliott first built this shape in 2010. This is that design on the khėnsu.ñü network.

This sits on nu-transfer (`design/nu-media-protocol.md` 11) and KhensuMemory (`PLAN.md`, Local search and memory). It does not replace a one-shot send of a file. A send still uses nu-transfer. ñü.vœîð is the place those bytes live, on your devices and on the network, when they are yours to keep.

## 1. What you can count on

| Property | What is true |
| --- | --- |
| No names on disk | A stored object is a random 32-byte id. The name exists only inside a memory record |
| No names on the network | A node stores fixed-size ciphertext. It has no file name, type, length or owner |
| Your map only | The order of the pieces, the length of each, and the key for each live in KhensuMemory, wrapped by the Secure Enclave. Lose the map and the pieces do not open |
| A different map for a person | Handing something to one person seals a new map to their key and writes new ciphertext. Their pieces do not share addresses with yours |
| View once | That map opens once. The device then deletes it and asks the network to drop their copies |
| Capture buffer stays blank | View-once and disappearing objects are drawn on a surface the screenshot and screen-recording buffer does not include |
| Eight copies | Each sealed piece is stored on eight nodes that have not opted out |
| No direct connection | Every upload and every download is its own mixnet path. The next piece takes a different set of relays |

A seized disk, a single node and a single relay each see ciphertext and ids. They do not see the map. A global observer who watches every link still learns that a device is sending cover, which the mixnet already assumes (`THREAT-MODEL.md` 4.2, 5.3). An unlocked phone in someone else's hands can open the bag, because the map is meant to open for you. A second camera pointed at the screen still sees it (`PLAN.md`, disappearing messages).

## 2. Names become ids

Anything the app stores — a photo, a song, a PDF, a voice note, a transfer it is keeping — is an id, including objects that never leave the phone.

```
object_id = random 32
```

On device the bytes sit in the encrypted SQLite store, keyed by `object_id`. There is no file in the app container named `contract.pdf`, and Spotlight is not given one. The directory a forensic image sees is a list of random ids and fixed-size blobs.

The name, the type and the note you wrote live in one KhensuMemory record, `void_object`. Full-text search and embeddings index that name and that note, so you can ask for "the contract" and memory finds the id. The chunk keys are a separate column. The memory engine's tools cannot select it, and it is never embedded. Derived facts still die with the object they came from (`PLAN.md`, memory).

Panic wipe deletes the Secure Enclave wrapping key first (`THREAT-MODEL.md` L5). Without it the map does not open, and the blobs on the phone and the eight copies on the network stay ciphertext.

## 3. 64 KiB chunks, one key each

The file is cut into chunks of **65,472 bytes** of file data. Each chunk has its own key. The pieces are the same size on purpose: a variable size on the network would tell an observer the cut (`design/nu-media-protocol.md` 11.5). What is random is where each chunk is stored, not how long it is (section 5).

```
k_chunk = random 32          // stored only in the map
```

The last chunk is padded with zeros up to 65,472 bytes. Every chunk then grows a 48-byte footer, **ñü.fêět** (code `nu.feet`): the headers sit at the tail, inside the encryption. On the wire, and on every disk, the sealed object is **65,536 bytes**.

```
struct {
  opaque body[65472];        // file bytes, then zeros
  uint32 magic;              // 0x74656566, the bytes of "feet"
  uint32 used;               // file bytes in body, 0..65472
  uint32 index;              // this chunk, from 0
  uint32 count;              // chunks in the file
  opaque object_id[32];
} ChunkPlain;                // 65,520 bytes

sealed     = AEAD(k_chunk, zero_nonce, ChunkPlain, aad = object_id || uint32(index))
chunk_addr = H256(Label("nv chunk addr") || sealed)
```

`sealed` is 65,536 bytes: the 65,520-byte plaintext plus a 16-byte AES-256-GCM tag. One key encrypts one chunk, so the zero nonce is safe. The AEAD is AES-256-GCM. The chunk key is random, and a map handed to someone else is sealed to their identity key with ML-KEM-1024. There is no convergent encryption: the same file stored twice, or by two people, produces unrelated addresses.

A wrong key fails the tag check. That chunk does not become bytes, and the file cannot be assembled from it. A right key for one chunk opens only that chunk. The footer then says where those bytes sit and where the padding ends. It does not contain the next chunk's address or key. Order across chunks lives in the map.

The map for an object, sealed inside `void_object`, is the ordered list:

```
struct {
  uint32 used;              // real bytes in this chunk
  opaque k_chunk[32];
  opaque chunk_addr[32];   // the address each of the eight nodes was asked to hold
} ChunkEntry;
```

Eight nodes hold the same sealed bytes, so they share one `chunk_addr`. The map records that address once. Placement (section 5) records which eight nodes were asked; the client does not need that list later, because a fetch asks the network for the address and any replica may answer.

## 4. A different map for one person

Your map never leaves your devices. Sending an object to one person does not send your map, and it does not tell them your chunk addresses.

1. Draw a fresh `transfer_secret` and new chunk keys.
2. Re-seal every chunk. The new ciphertext has new addresses. A node that holds your copies cannot recognise theirs.
3. Seal the new map to their identity key with ML-KEM-1024, inside an ordinary MLS message. The message carries the map and nothing else they can use to point at your bag.
4. Store their sealed chunks on eight nodes, on the same rules as yours.

Their eight and your eight are different ciphertext. Deleting theirs does not touch yours.

### 4.1 View once

A view-once map has `openings = 1`. The recipient's device decrypts it into memory, draws it, then deletes the map, the plaintext and the local blobs in the same database transaction. It sends a delete for each of their chunk addresses (`del_i` from the transfer secret, as in nu-transfer). Their copies are also retained for at most one epoch, so a delete that never arrives still expires.

The owner's bag is unchanged. View once spends their map, not yours.

### 4.2 The capture buffer

View-once objects, and any ñü.vœîð object under a disappearing timer, are drawn on a capture-excluded surface:

- iOS and iPadOS: the view is hosted in the secure-text layer, so the screenshot buffer and the screen-recording buffer receive a blank frame.
- Android: `FLAG_SECURE`, which blanks screenshots, recording and the recents thumbnail.
- macOS: the window's sharing type excludes it from capture where the OS allows.

Where the OS reports that a screenshot was taken, the app tells the other person, as it already does for disappearing messages. A camera in the room is outside the device (`PLAN.md`). The app does not say the picture cannot be seen. It says the capture buffer was blank, and the map is gone from their device if they have not saved it.

## 5. Eight copies, scattered

Every sealed chunk is stored on **eight** nodes that still accept ñü.vœîð. Storage is on unless the operator turns it off:

```
~node void off
~node void on
```

Opting out removes the node from the next epoch's eligible set. Chunks it already holds stay until they expire or a delete arrives; it stops taking new ones.

Placement, for each `chunk_addr`, over the eligible nodes in the epoch directory:

1. Rank nodes by `H256(Label("nv place") || chunk_addr || node_id || epoch)`.
2. Walk that ranking and take a node when its operator is not already chosen, then prefer a network and a country not already chosen.
3. Stop at eight. If the eligible set cannot fill eight distinct operators, the object stays on the device and the upload waits. The devnet may run with fewer and must say so in the client; a production client must not.

A fetch asks for the address through a SURB. Any of the eight may answer. The client picks the replica attempt at random and tries another if the first is missing. It does not open a session to a node, and it does not keep a favourite.

## 6. Hopping on the way up and the way down

ñü.vœîð never uses the direct-session option nu-transfer allows. Each `chunk_put` and each `chunk_get` is one mixnet message, padded into the constant-rate cover, with its own route.

- The relay set for piece *i* is drawn independently of piece *i−1*.
- No relay from the previous piece is reused for the next.
- Puts for the eight replicas of one piece are themselves eight separate messages, spread across cover slots, not a burst.
- The phone does not open a connection to a storage node. The node sees a mailbox-style put or a SURB fetch, the same shape as every other bulk object.

An observer on one relay sees fixed-size packets that look like the rest of the cover. An observer who follows one piece to one node sees one ciphertext of 65,536 bytes. They do not see the other seven, the neighbouring chunks, or the name, because those took other paths and the map never left the phone.

## 7. What memory is allowed to know

| In the memory record | Indexed for recall | Held, not indexed |
| --- | --- | --- |
| The name you gave it | Yes | |
| A note you wrote | Yes | |
| `object_id` | No (it is the key) | Yes |
| Span order, `used`, keys, addresses | No | Yes, enclave-wrapped |

Opening an object is a memory lookup that returns an id, then a local unwrap of the map, then fetches for any chunks that are not already in the local store. The model can be shown the name. It is not shown the keys. If you ask it to read the document, the app opens the object for you first, and that read is ordinary message content: it expires with the object.

The recall index stays unreplicated, as memory already requires: a new device rebuilds search from the names it is allowed to read. The wrapped chunk keys cannot be rebuilt from ciphertext, so they travel with the phone-to-phone transfer and, when backups are on, inside the encrypted backup under the recovery key. The chunks themselves stay on the eight nodes. A restore without the map restores nothing of the bag. A restore with the recovery kit unwraps the map and the pieces open again.

## 8. Sizes

One chunk costs 65,536 bytes on each of eight nodes: 524,288 bytes of ciphertext per chunk, which is 512 KiB. A 10 MiB file is 10,485,760 / 65,472 = 160.15, so 161 chunks, and 80.5 MiB of ciphertext across the network, before the cover traffic that hides the puts. The ratio is 8.01 times the file: eight copies, plus 64 bytes of footer and tag in each 64 KiB. That overhead is the price of equal sizes and eight copies. It is not a promise about a particular file.

AES-256-GCM on one 65,520-byte plaintext, measured 12 October 2026 on an M1 Pro MacBook Pro (MacBookPro18,3) with Python `cryptography`: seal 10.9 µs (6.00 GB/s), open 11.7 µs (5.62 GB/s). A wrong key was rejected on 200 of 200 opens, in 12.4 µs, and produced no plaintext. This is the cipher on that machine. It is not a measurement of a phone or of the network.

## 9. What this does not do

- It does not make a seized, unlocked, app-unlocked phone unreadable. The map opens for the person who can unlock it.
- It does not stop a camera, a modified recipient app, or malware on the device (`THREAT-MODEL.md` 5.1, 5.5).
- It does not hide from an observer who watches every link that the device is online and sending cover.
- It does not deduplicate. The same photo in two bags is two sets of addresses.
- It does not store the map on a node, a relay, or a server we run.

## 10. Open

- The exact retention cap for ordinary ñü.vœîð objects, against the token tier's mailbox retention.
- Whether a second linked device holds a replica of the map by the phone-to-phone transfer only, or also fetches it from the encrypted backup. Rec: transfer and backup both carry the wrapped map; the chunks are not copied device to device in full.
- Patent assessment before any public detail beyond this spec (`PATENTS.md`).
