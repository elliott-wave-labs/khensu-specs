# Pull request draft: add `webe` to the safelisted schemes

For `github.com/whatwg/html`. Not yet submitted: file after the patent check in `design/browser.md` section 3. WHATWG requires interest from at least two browser engines before merging, so open it alongside the WebExtensions Community Group proposal (`proposals/webext-scheme-providers.md`).

## Change

In the HTML standard, section "Custom scheme handlers", add `webe` to the list of safelisted schemes, next to `ipfs`, `ipns`, `dweb`, `ssb`, `cabal` and `hyper`.

## Pull request text

> **Add `webe` to the safelisted schemes for `registerProtocolHandler()`**
>
> webE̊ is an open protocol for websites, feeds and media delivered over a post-quantum stealth network instead of DNS and HTTP servers. Its URLs are `webe://name.khensu.nu/path` and `webe://h/<hash>` (immutable objects). Adding `webe` lets sites and extensions register handlers for it the same way they can for `ipfs` and `dweb`, so `webe:` links work in any browser that has a handler installed.
>
> - Specification: webE̊, draft 0.1 (to be published with this request).
> - Clients: the khensu.nu app (iOS, iPadOS, macOS), browser extensions for Chromium, Firefox and Safari.
> - Tests: web-platform-tests update to `html/webappapis/system-state-and-capabilities/the-navigator-object/protocol.https.html` adding `webe`.
> - Implementer interest: to be linked.
