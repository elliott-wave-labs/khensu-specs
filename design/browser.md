# webE̊ in ordinary browsers

How `name.khensu.nu` sites open in Chrome, Edge, Firefox and Safari with the name in the address bar, full stealth, and no separate router (no local daemon or proxy app). Status: design. Extends `WEBE.md` section 11. Open questions in `OPEN-QUESTIONS.md` 55 and 81.

## 1. The constraint

Today no browser lets an extension serve a page **as** `https://name.khensu.nu` without that request going over the network. Any page under that address leaves the browser as a DNS lookup and a TLS connection naming the site, so some server learns who read what. That breaks webE̊'s rule that reading leaves no trace (`WEBE.md` 1.3).

| Approach | Address bar shows the name | Stealth | Separate router | Works today |
| --- | --- | --- | --- | --- |
| Gateway or service-worker loader on real `*.khensu.nu` DNS | Yes | **No:** the host sees the reader's IP and the site name | No | Yes |
| Extension plus local proxy and a local certificate authority | Yes | Yes | **Yes**, and a local CA weakens TLS for everything | Yes |
| Extension that runs the webE̊ client itself and shows the site in its own viewer page | No: the extension's address | Yes | No | **Yes: stage 1** |
| Browser API for extension-served schemes (`webe://name.khensu.nu`) | Yes | Yes | No | **Needs the proposal: stage 2** |
| Our own Chromium build with a native webE̊ network service | Yes | Yes | No | **Stage 3**, as in `WEBE.md` 11.2 |

We don't ship the first two. Gateways stay governed by `OPEN-QUESTIONS.md` 56 and are never used by the extension.

## 2. Stage 1: one extension for four browsers

One WebExtensions codebase in `khensu-browser`, published to the Chrome Web Store (Chrome, Brave, Opera), Microsoft Edge Add-ons, Firefox Add-ons, and inside the khensu.nu app for Safari.

- **The webE̊ client runs in the browser.** `khensu-core` compiles to WebAssembly with the webE̊ client: naming through PIR, two-relay stealth fetch, signature and hash checks, ML-KEM-1024 and ML-DSA-87. Transport is WebTransport over HTTPS to entry relays, falling back to TCP as in `PROTOCOL.md` 7.1. That makes the local daemon `WEBE.md` 11.2 assumed unnecessary.

| Browser | Where the client runs | Notes |
| --- | --- | --- |
| Chrome, Edge, Brave, Opera | An offscreen document (Manifest V3) | Keeps the client alive past the service worker's idle limit; stealth ticks run while the browser is open |
| Firefox | The background page | Same code; Firefox keeps WebExtensions background pages alive |
| Safari (Mac, iPhone, iPad) | The khensu.nu app, through native messaging | Safari web extensions ship inside an app, so the app's native `khensu-core` does the work; nothing extra to install |

- **Opening sites:**
  - The extension catches navigations to `https://*.khensu.nu` **before they reach the network**, using declarativeNetRequest rules (Safari: the same rules through its content blocker). It also catches `webe://` links through `protocol_handlers` where the browser supports them. The DNS lookup and TLS connection never happen.
  - It opens the site in its own viewer page, which shows `name.khensu.nu` in a top bar with a verified badge from the name record. The site runs in a sandboxed iframe with an opaque origin, so sites can't read each other's data or the extension's.
  - Every object is checked against its hash and the signed manifest before it is shown.
- **Limits until stage 2:**
  - The address bar shows the extension's address, not the name.
  - Sites get no persistent storage (an opaque origin has none).
  - Bookmarks and history record the viewer's address.
- **Stealth while the browser is open:** the same 2 s ticks as the app, always on, with no setting. When the browser closes, the cover stops, as it does when the app closes; a suñůlink.shield or node keeps it going.

## 3. Stage 2: the upstream proposal

Ask the browsers for one narrow capability: **an extension may register a custom scheme and serve its responses**, and each host under that scheme becomes its own secure origin. Then `webe://name.khensu.nu` shows in the address bar, behaves like a real site (its own storage, cookies, service workers), and never touches DNS.

- **API shape:** a manifest key plus fetch events in the extension's service worker, reusing service-worker semantics that browsers already have.

```json
"scheme_providers": [
  { "scheme": "webe", "secure": true, "description": "webE̊ sites" }
]
```

```js
self.addEventListener("schemefetch", (event) => {
  event.respondWith(webe.fetch(event.request)); // a Response, streamed
});
```

- **Scope kept narrow, so it can be accepted:**
  - Only schemes the browser allowlists for extensions. `webe` joins the WHATWG safelist, which already includes `ipfs`, `ipns`, `dweb` and others for `registerProtocolHandler`.
  - The extension can't touch `http` or `https`.
  - The user approves the scheme at install.
  - Origins are `webe://<host>`, isolated per host.
  - The address bar shows the scheme and host, with the extension's name.
- **Precedents:**
  - Chromium already serves `chrome-extension://` through a non-network URL loader and dispatches its fetch events to the extension's service worker.
  - Electron exposes `protocol.handle` to apps.
  - Firefox extensions have `protocol_handlers` (redirect only), and Mozilla's libdweb experiment (2018) let extensions implement `dweb://` and `ipfs://` with real origins.
  - WebKit gives apps `WKURLSchemeHandler`, which the khensu.nu app already uses for `webe://`.
  - Brave shipped native `ipfs://`.
- **Where it goes:** each browser takes contributions differently, so there is no single PR.

| Step | Venue | What we send |
| --- | --- | --- |
| 1 | W3C WebExtensions Community Group (`github.com/w3c/webextensions`) | The cross-browser proposal: `proposals/webext-scheme-providers.md`. Chrome, Edge, Safari and Firefox all review here |
| 2 | WHATWG HTML (`github.com/whatwg/html`) | A pull request adding `webe` to the safelisted schemes for `registerProtocolHandler`, with implementer interest: `proposals/whatwg-safelist-webe.md` |
| 3 | Chromium | An explainer and an Intent to Prototype on blink-dev, then Gerrit changes behind a flag. Chromium takes Gerrit changes, not GitHub pull requests. Edge inherits it |
| 4 | Firefox | A Bugzilla bug and a Phabricator patch, building on libdweb and `protocol_handlers` |
| 5 | WebKit | A GitHub pull request for Safari Web Extensions |

- **Disclosure first:** a public proposal is public disclosure. File any patent applications first (`PATENTS.md`), as for the Internet-Drafts in `WEBE.md` 12.

## 4. Stage 3: our own Chromium build

Until the API lands, the Chromium patch in `WEBE.md` 11.2 ships the same capability natively: a webE̊ network service, `webe://` as a standard secure scheme, and the stealth defences (fixed window sizes, WebRTC off, restricted high-entropy APIs, no third-party requests). Once stage 2 ships in a browser, the extension uses it there and the patched build is only needed for the extra defences.

## 5. Work items

1. `khensu-core`: webE̊ client (naming, two-relay fetch, verification) compiled to WebAssembly, with a WebTransport transport.
2. `khensu-browser`: the extension for Chrome, Edge, Firefox and Safari (stage 1), and the Chromium patch (stage 3).
3. Patent check on the scheme-provider idea, then publish the WebExtensions Community Group proposal and the WHATWG pull request.
4. Chromium explainer and prototype; Firefox and WebKit patches.
