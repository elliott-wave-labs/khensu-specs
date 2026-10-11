# Proposal: extension scheme providers

Draft for the W3C WebExtensions Community Group. Not yet submitted: file after the patent check in `design/browser.md` section 3.

## Summary

Let an extension register a custom scheme from an allowlist and serve every request under it from its service worker. Each host under the scheme is its own secure origin, shown in the address bar.

## Motivation

Decentralised and peer-to-peer webs (webE̊, IPFS, Hypercore, Secure Scuttlebutt) fetch content from networks that aren't HTTP servers. Extensions can already run those clients in WebAssembly over WebTransport, but they have no way to present the result as a real site:

- Redirecting to an extension page shows the extension's address, gives every site the same origin, and breaks bookmarks, history and storage.
- Serving through a local proxy needs a separate program and often a local certificate authority, which weakens TLS for everything.
- Serving through a public gateway on real DNS tells the gateway who read what.

## Use cases

1. A webE̊ extension shows `webe://name.khensu.nu` as its own site, with storage and service workers isolated per name, and no DNS lookup.
2. An IPFS extension serves `ipfs://<cid>` with content verified against the CID, without trusting a gateway.
3. A developer serves a local test scheme from an extension without running a server.

## Proposed API

Manifest:

```json
"scheme_providers": [
  { "scheme": "webe", "secure": true, "description": "webE̊ sites" }
]
```

Service worker:

```js
self.addEventListener("schemefetch", (event) => {
  // event.request: a Request for webe://host/path, any destination (document, script, image, fetch)
  event.respondWith(handle(event.request)); // Promise<Response>, body may stream
});
```

- `scheme` must be on the browser's allowlist: the WHATWG safelisted schemes for `registerProtocolHandler` (which already include `ipfs`, `ipns`, `dweb`, `ssb`, `cabal` and `hyper`) plus browser-approved additions. `http`, `https`, `file`, `data`, `blob` and browser-internal schemes are never allowed.
- `secure: true` makes documents under the scheme secure contexts.
- One provider per scheme; the user chooses if two extensions ask for the same scheme.

## Semantics

- **Origin:** `scheme://host`, a tuple origin with the same isolation as `https` origins (storage, cookies, service workers, permissions).
- **Navigation:** top-level navigations and subresources under the scheme go to the provider's `schemefetch` handler. Nothing goes to DNS or the network unless the provider makes its own requests.
- **Address bar:** shows `scheme://host/path` and identifies the providing extension.
- **Mixed content:** documents under the scheme may load their own scheme and `https`; `http` is blocked.
- **Lifetime:** the browser wakes the service worker for `schemefetch` like any extension event.
- **Uninstall:** origins under the scheme stop resolving; their stored data is cleared.

## Security and privacy

- The user approves the scheme at install, with the description shown.
- Providers can't observe or alter requests for any other scheme.
- Content under the scheme is as trustworthy as the extension; browsers may show the extension's name next to the address.
- No new fingerprinting surface: the scheme list is not exposed to web pages.

## Alternatives considered

- **`protocol_handlers` (redirect):** keeps the extension's address and a shared origin.
- **declarativeNetRequest redirects:** same problem, and they can't serve bodies.
- **Local proxy:** needs a separate program; a local CA is a security risk.
- **Public gateways:** reveal readers.

## Precedents and implementation notes

- Chromium serves `chrome-extension://` through a non-network URL loader factory and dispatches its fetch events to the extension's service worker; scheme providers can reuse that path for allowlisted schemes.
- Electron's `protocol.handle` and WebKit's `WKURLSchemeHandler` give the same capability to apps.
- Mozilla's libdweb experiment (2018) implemented protocol handlers with real origins for `dweb://` and `ipfs://` in Firefox extensions.
- Brave shipped native `ipfs://`.
