# Ring codes, contact cards and Apple Wallet

Proposed 11 Oct 2026. Status: design; nothing built. Open decisions are `OPEN-QUESTIONS.md` 86–88.

## 1. Ring code (replaces QR codes in the app)

A ring code is a circle of points joined by lines into a network, with pulses running along the lines. It looks like Apple's Quick Start point cloud, but the arrangement carries data. Every ring is different, because the points come from the data they carry.

### Layout

- Six concentric rings with 54, 62, 70, 78, 86 and 94 points: 444 points in total (decided 11 Oct 2026), roughly eleven times the 40 or so dots in a typical "network" illustration.
- A fixed orientation mark (a gap in the outer ring at 12 o'clock and three larger anchor points) gives rotation, scale and perspective, the same way QR finder patterns do.
- Each data point has four angular offsets and two brightness levels, so it carries 3 bits. A single frame holds 1,332 raw bits; with Reed–Solomon over GF(2⁸) at 50% redundancy, that leaves about 83 bytes of payload per frame and survives a quarter of the points being misread.
- Lines join each point to its two nearest neighbours on the next ring inward. They carry no data and are only there for the look; the decoder ignores them.
- Pulses run along the lines at random, also without data. In static mode they're absent.

### Live mode (in the app)

- The code changes 12 times a second. The frames are fountain-coded (RaptorQ, RFC 6330), so the scanner can start at any moment and needs any 21 or so frames, not a particular sequence.
- Payload: a fresh ML-KEM-1024 encapsulation key (1,568 bytes), the account address (32 bytes) and a 16-byte one-time invite. With framing that is about 1.7 KB, read in about 2 seconds at 30 fps.
- The scanner encapsulates to that key and sends the ciphertext back over Wi-Fi Aware or, if the phones aren't close, over the mixnet to the invite's mailbox. Both phones derive the same secret and exchange profiles encrypted under it with AES-256-GCM. Both then check the address against the key transparency log.
- Every showing generates a new key, so each live ring is unique and works once. A photo or screen recording of a ring is useless after its 5-minute expiry or its first use, whichever comes first.
- The same flow replaces the QR codes in device linking and phone transfer (`PLAN.md`, Identity), which already carry a one-time ML-KEM-1024 key.

### Static mode (Wallet pass, contact photo, print)

- One frame, no animation: the address (32 bytes), a 16-byte invite that can be revoked, and a 4-byte checksum, in one 83-byte frame.
- The scanner looks up the address in the key transparency log over the mixnet to get the ML-KEM-1024 key, then proceeds as in live mode. The ring itself holds no secret; the invite only rate-limits strangers and can be revoked in Settings.
- Each person's static ring is unique, because its points are their address.

### Decoding

- Only the khensu.nu app reads ring codes, using `AVCaptureSession` and Vision for the anchor points. Decoding runs on the device; nothing is uploaded.
- The system camera won't recognise a ring, so the Wallet pass and contact card also carry the profile link (`khensu.nu/@name` opens the app or the App Store page; the page is static and has no per-user content).
- Accessibility: VoiceOver reads "Ring code for @name", and the Share button and Tap to Share (NFC) do the same job without a camera.

### Prior art and patents

Circular codes already exist: Apple App Clip Codes, Snapcodes, Spotify Codes, Messenger Codes and Apple's Quick Start pattern. Run the patent check before anything is published or shipped (`PATENTS.md`). The likely novel parts are the fountain-coded animated ring that carries a one-time post-quantum key, and the point-cloud styling with decorative pulses that carry no data.

## 2. Your profile as a contact card

- Settings → Profile → "Add to My Card" writes a `CNSocialProfile` (service "khensu.nu", username `name`, URL `khensu.nu/@name`) and, optionally, your static ring as the contact photo onto your own card in Contacts. NameDrop and Contact sharing then carry your khensu.nu profile to anyone you share your card with.
- From a chat, "Add to Contacts" does the same for another person, with their consent recorded in the chat. Only the public handle and static ring are written: no keys, no messages, no safety number.
- Contacts are stored in whichever account the user's contacts use. If that's iCloud, Apple stores the handle, so the sheet says "Your contacts sync with iCloud; Apple will see this handle". It defaults to "On My iPhone" where that account exists. Keys and chats never touch Contacts.
- The app never reads Contacts in bulk (`PLAN.md`: no phone or email discovery). It writes with the iOS 18 limited-access contact picker, one card at a time.

## 3. Apple Wallet

### Profile pass

- A generic `PKPass` with the static ring as the strip image, the display name and handle, and the profile link on the back.
- Wallet passes can't animate and only scan as QR, Aztec, PDF417 or Code 128. So the pass shows the static ring for khensu.nu users to scan and sets no barcode at all, which means there's no QR. An NFC pass would need Apple's NFC pass certificate, which Apple grants case by case; ask for it (`OPEN-QUESTIONS.md` 87).
- Passes must be signed with our Pass Type ID certificate. Shipping that private key in the app would let anyone sign passes as us, so the options are an operator-run signer that sees only public data (the handle and the ring, both already in the log) and is reached over the mixnet, or Apple's certificate rules permitting a per-device approach. `OPEN-QUESTIONS.md` 87.
- No pass web service, no update pushes and no `webServiceURL`: the pass never phones home. Updates mean re-adding it.

### Payment card

- A debit card in Apple Wallet for tap to pay, funded from the shielded pool with conversion to USDC at authorisation (`PLAN.md`, Spending with Apple Pay; `OPEN-QUESTIONS.md` 82).
- Not on Visa or Mastercard. Apple Pay only provisions cards on networks it supports. The options that aren't Visa or Mastercard are Discover Global Network (Discover, Diners Club International and the Pulse debit network, owned by Capital One since May 2025), American Express, JCB and UnionPay, plus domestic networks such as Interac, eftpos, Cartes Bancaires, girocard, mada and Elo.
- Rec: Discover Global Network. It accepts third-party issuers and debit through Pulse, and its reciprocal deals with JCB, UnionPay, RuPay and others give acceptance abroad. Confirm that it will take a stablecoin-funded programme and which issuing partner sponsors it. Fallback: JCB or UnionPay for regions where Discover acceptance is thin. `OPEN-QUESTIONS.md` 88.
- "A card number that works": the card has a real 16-digit primary account number in the network's range, shown only inside the app behind Face ID for online purchases. Apple Wallet holds a separate device account number (the network's token), so the real number never goes to merchants on tap.
- Card art is ours: the crescent on dark glass with the network mark Apple requires. The card is a product of the issuing partner, and the app says so.
