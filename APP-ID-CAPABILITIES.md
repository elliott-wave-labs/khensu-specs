# khensu.nu App ID capabilities

App ID: **`nu.khensu.ptah`** (explicit, not wildcard), Team ID **`LHS49D8RYY`**. You can turn capabilities on or off later; each change just needs new provisioning profiles.

## Certificates and keys

Certificates belong to the team, not to a bundle ID; the bundle ID is tied in by provisioning profiles. Let Xcode's automatic signing create the development and distribution certificates and profiles.

| What | Create it | Used for |
| --- | --- | --- |
| Apple Development | Xcode → Settings → Accounts → Manage Certificates (automatic) | Running on your devices |
| Apple Distribution | Same, or Certificates → + | TestFlight and App Store builds of `nu.khensu.ptah` (iOS, iPadOS, macOS) |
| Developer ID Application | Certificates → + → Developer ID Application (Account Holder only) | Signing and notarizing the `nu.khensu.tatenan` Mac node app, distributed outside the Mac App Store |
| APNs auth key (.p8) | Keys → + → Apple Push Notifications service | Team-wide push for every bundle ID; use this instead of a per-app push certificate. Download once and put it straight into Secret Manager for `push.khensu.nu`. |

The Raspberry Pi node needs nothing from Apple.

**Ask** = Apple must approve a request before the capability works in a shipping build. Tick the box now anyway, and send the request early, because approvals can take weeks.

## Enable now

Everything here ships in v1; there is no separate core release.

| Capability | What it does | Why khensu.nu needs it |
| --- | --- | --- |
| **App Groups** | Shared container and keychain group between the app and its extensions | The Notification Service Extension writes sealed packets into the shared `CompleteUnlessOpen` queue while the phone is locked. Create `group.nu.khensu.ptah`. |
| **Associated Domains** | Universal links and web credentials for your domains | `khensu.nu/@handle` profile links, group invite links, and device-link QR codes open in the app. Add `applinks:khensu.nu`. |
| **Data Protection** → *Complete Protection* | Default file encryption class for the app's files | Everything is unreadable while locked by default; the incoming queue alone is set to `CompleteUnlessOpen` in code. |
| **Enhanced Security** | Pointer authentication, typed allocators, and hardware memory tagging (Memory Integrity Enforcement on iPhone 17 and later) | Apple recommends it specifically for messaging apps, because they are the main target for spyware exploits. Ship in soft mode during beta, then turn on enforcement. |
| **Push Notifications** (no Broadcast) | APNs alerts, plus PushKit VoIP pushes for calls | The anonymous "New message" wake and incoming calls. Leave *Broadcast Capability* off. |
| **In-App Purchase** | StoreKit purchases and subscriptions | Already on by default. Needed for paid tiers and supporter subscriptions. |
| **Sensitive Content Analysis** | Apple's on-device nudity detection for images and video | Blurs unsolicited explicit images from strangers. It runs fully on the device and also respects the user's Sensitive Content Warning and Communication Safety (child account) settings. |
| **App Attest** | The device proves the app is genuine and unmodified, using a key in the Secure Enclave | Anti-spam: the credential issuer checks the attestation once, then issues **blind** tokens, so Apple's attestation can't be linked to later messages. |
| **Declared Age Range** | Asks the OS for the user's age bracket without seeing a birthdate | Age-assurance laws (several US states, UK, Australia) now reach messaging apps. Used to apply teen defaults (no messages from strangers, sensitive content blurred). |
| **Default Messaging App** / **Default Calling App** | Lets users pick khensu.nu as the system default for messages and calls (region-limited, starting with the EU) | Offered in Settings where the OS allows it. **Ask**: Apple's eligibility requirements apply. |
| **CarPlay Communication App** | Calls (and, with SiriKit, messaging) in CarPlay | **Ask** (CarPlay request form). **Calls only**: Apple requires Siri for any CarPlay messaging, and we don't use Siri. Calls go through CallKit and start from the CarPlay contact list or Recents. Leave the older *CarPlay Messaging App* and *CarPlay VoIP Calling App* boxes off; Apple lists them as deprecated (iOS 13 and earlier). |
| **Communication Notifications** | Shows the sender's avatar and name on notifications | Previews mode only. Anonymous mode never donates sender intents to the system. |
| **Wi-Fi Aware** | Direct Wi-Fi links between nearby devices with no router or internet | Offline nearby mode: phones carry each other's sealed packets until one reaches the internet (protests, outages, flights). Opt-in, because nearby phones can tell a khensu.nu user is close by. |
| **Tap to Share** / **NFC Tag Reading** | Exchange data by holding phones together or reading tags | Add a contact and verify their safety number by touching phones, alongside the QR code. |
| **StoreKit External Purchases or Offers** (and the EU variant) | Link out to your own website for payment where allowed | Subscriptions on `khensu.nu` in allowed regions, so Apple's commission doesn't apply there. **Ask**: region-specific entitlement requests. |
| **Push to Talk** | System walkie-talkie UI, background audio and a PTT push type | Walkie-talkie mode for groups. Voice clips go through the mixnet like any message, so a few seconds of delay is expected. |
| **Spatial Audio Profile** | Applies the user's Personalized Spatial Audio profile (made in Settings from a TrueDepth head scan) to audio the app renders with `AVAudioEngine`, `AUSpatialMixer` or PHASE | Group calls and voice rooms place each speaker at their own position around you, tuned to your ears. The system applies the profile; the app never sees the head scan. |
| **Head Pose** | Lets head movement from AirPods steer the app's spatial audio | Voices stay fixed in space when you turn your head, as in FaceTime. Head tracking is handled by the system audio engine and never leaves the device. |
## On-device only: nothing is processed on servers

These need no checkbox; they are code rules in the app.

| Feature | How it stays on the device |
| --- | --- |
| Summaries, smart replies | Foundation Models on-device model only; the Private Cloud Compute entitlement is never requested. |
| Voice dictation | In-app mic button using `SpeechAnalyzer` / `SpeechTranscriber` with on-device models, instead of Siri or keyboard dictation. |
| Read messages aloud | `AVSpeechSynthesizer`, which synthesizes on the device. |
| Message composer | `writingToolsBehavior = .none`, because Apple's Writing Tools can send text to Private Cloud Compute. |
| Keyboard | Third-party keyboard extensions are refused (`application(_:shouldAllowExtensionPointIdentifier:)`), since they could log keystrokes. |

Apple services that remain only see content-free data: APNs (a fixed "New message" alert), StoreKit (purchases), App Attest (a one-time device check before blind tokens), and Declared Age Range (an age bracket).

## Separate requests to Apple (not on this page)

| Entitlement | Why |
| --- | --- |
| `com.apple.developer.usernotifications.filtering` (Notification Service Extension filtering) | Lets the extension silently drop dummy "cover" wakes, so push timing reveals less. Request it through Apple's form, explaining the privacy reason. |
| CarPlay communication entitlement | Required for CarPlay calls. Say up front that the app is calls-only and doesn't use Siri. |
| Default messaging / calling app, StoreKit external purchase | Region-specific requests in the developer account. |

## Background and memory capabilities: leave off

| Capability | What it actually does | Why not |
| --- | --- | --- |
| **Background Inference** | Lets the app's own Core ML / Core AI / Metal models use the Neural Engine while backgrounded | Foundation Models (summaries) and Sensitive Content Analysis run inside Apple's system services and don't need it. We ship no Core ML models. Running inference in the background would also mean decrypted messages in memory while the user isn't looking. |
| **Background GPU Access** | GPU work during a user-started continued background task | No GPU workload; crypto runs on the CPU. |
| **Sustained Execution** | *Caps* the app's burst performance so it runs at a steady, lower speed (made for game benchmarking) | It would make launch, unlock, decryption and scrolling slower. |
| **Increased Memory Limit** | Raises the app's memory ceiling on some devices | A messenger stays well under the normal limit; summaries use the system's memory, not ours. It doesn't apply to the notification extension, which is the tight one. |
| **Increased Debugging Memory Limit** | Higher memory limit only while debugging | No benefit in a shipped app. |
| **Extended Virtual Addressing** | 64-bit address space beyond the default, for huge datasets or games | Nothing we do needs it. |

If testing shows a real need (for example, an on-device spam classifier in Core ML), add the one capability that need requires.

**Configured in Xcode, not here:** Background Modes (`remote-notification`, `voip`, `processing`), Keychain Sharing, Hardened Runtime (macOS), CallKit, Foundation Models (no capability needed for the on-device model). The Private Cloud Compute entitlement is **never requested**.

## Don't enable

| Capability | What it does | Why not |
| --- | --- | --- |
| iCloud / iCloud Extended Share Access | CloudKit, iCloud Drive and key-value sync | Backups go encrypted to mailbox nodes, not Apple. Keys use `ThisDeviceOnly`; the data store is excluded from iCloud backup. |
| Sign In with Apple | Apple ID login | Not required: guideline 4.8 only applies when an app offers a third-party login (Google, Facebook, etc.), and our sign-up is our own key-based system. Adding it would tie your identity to your Apple ID. Account deletion in the app (guideline 5.1.1(v)) *is* required and is in the plan. |
| Account Creation Requires Phone Number | Declares that sign-up always requires a phone number | We never require one. |
| AutoFill Credential Provider | Act as a password/passkey manager | Not a password manager. |
| Siri, CarPlay Messaging App, CarPlay VoIP Calling App | SiriKit voice commands; deprecated CarPlay categories | Siri requests can be processed on Apple's servers. Voice features are our own and on-device instead (see below). |
| Trust Insights | Apple's behavioral abuse signals (iOS 27) | Apple's documentation doesn't confirm its evaluation never involves Apple's servers. App Attest plus blind tokens covers anti-spam. |
| Suggested Actions, Shared with You, Journaling Suggestions, Messages Collaboration | Surface app content to Siri, Spotlight and other Apple apps | Would leak chat content or contacts into system features. |
| Time Sensitive Notifications, Critical Messaging | Break through Focus modes; Critical Messaging sends SMS through a special API | Anonymous alerts shouldn't override Focus, and we don't send SMS. |
| Group Activities (SharePlay) | Shared FaceTime sessions | Calls run on our own encrypted relays. |
| Location Push Service Extension, Maps | Location queried by push; act as a routing app | Live location is shared inside chats. MapKit needs no capability. |
| Access Wi-Fi Information, Hotspot, Wi-Fi Network Sharing, Network Topology Observation, Wireless Insights Service Predictions, 5G Network Slicing, Carrier-Constrained Network | Read network names; manage hotspots; see real MAC addresses of devices on the local network (Topology Observation, iOS and macOS 27); carrier network features | Leak location-like data or aren't relevant. Scanning the user's local network is the opposite of what a privacy app should do. |
| Network Extensions, Personal VPN, Custom Network Protocol, Multipath | VPNs, content filters, DNS proxies, local push on specific Wi-Fi networks, custom transports, MPTCP | We don't route the device's traffic, and the app's own QUIC needs none of these. QUIC handles Wi-Fi/cellular handover itself. A "route all traffic through the mixnet" VPN could be a later product, not v1. |
| Low Latency HLS, Low-Latency Streaming, HLS Interstitial Previews, Media Extension Format Reader / Video Decoder, Media Sharing Extension, Media Device Extension, Media Device Discovery, Inter-App Audio | Apple streaming and media system features | MOQOM handles media itself. Low-Latency Streaming is for visionOS game streaming. |
| Default Carrier Messaging App, Default Dialer App, SIM Inserted for Wireless Carriers | Carrier SMS and phone dialer roles | Carrier-only. |
| Default Navigation App, Default Translation App | System default for maps or translation | Not relevant. |
| Apple Pay Payment Processing, Wallet, FinanceKit Transaction Picker UI, Accessibility Merchant API Control, ID Verifier, Digital Credentials API - Mobile Document Provider | Payments, passes, finance data, ID documents | Not part of the app. Money comes through In-App Purchase and MOTOM. |
| HealthKit, HealthKit Estimate Recalibration, HomeKit, Matter Allow Setup Payload, Manage Thread Network Credentials, EnergyKit, EnergyKit LoadEvents, WeatherKit, ClassKit, Game Center, Fonts, Shallow Depth and Pressure | Health, home, energy, weather, education, games, fonts, diving sensors | Unrelated. |
| Accessory Data Provider / Setup Extension / Transport Extension / Transport Security, Wireless Accessory Configuration, Claim USB Accessory, Device Discovery Pairing Access, Nearby Interaction DL-TDoA | Hardware accessories, UWB positioning | Unrelated. |
| Side Button Access | Lets users in Japan set the side button to launch a voice assistant app | It can't read press patterns, so it can't trigger a wipe. The panic wipe uses an App Intent on the Action Button, Control Center, Lock Screen or Back Tap instead (no entitlement needed). |
| DriverKit (all), System Extension, FSKit Module / Mounter, FileProvider Testing Mode, Virtualization, VMNet, Cross-architecture Compatibility Framework | Drivers, file systems, VMs (mostly macOS) | Unrelated. The node app doesn't need them either. |
| Family Controls, User Management, MDM Managed Associated Domains, Managed App Installation UI, App Identifier for OS Data Transfer, On Demand Install Capable for App Clip Extensions, App Attest Opt-In, Multitasking Camera Access, Live Assistance | Parental controls, MDM, tvOS users, App Clips, enterprise/legacy, iPad camera multitasking, assistance | Not needed. (App Attest Opt-In and Live Assistance are new and thinly documented; revisit only if a feature needs them.) |
| Mac Catalyst | Run the iPad app on Mac | The Mac app will be a native SwiftUI multiplatform target instead. |

## Other identifiers to register

| Identifier | Type | Capabilities |
| --- | --- | --- |
| `nu.khensu.ptah` | iOS + macOS app (universal purchase) | The "Enable now" list above |
| `nu.khensu.ptah.notification-service` | Notification Service Extension | App Groups, Data Protection, Enhanced Security |
| `nu.khensu.ptah.share` | Share Extension | App Groups, Data Protection, Enhanced Security |
| `group.nu.khensu.ptah` | App Group | Shared by the app and its extensions |
| `nu.khensu.tatenan` | macOS node app (Developer ID, outside the Mac App Store) | None required; Hardened Runtime and notarization are set in Xcode |
| APNs auth key (.p8) | Key | Used only by the push gateway at `push.khensu.nu`; store it in Secret Manager, never in the app |
