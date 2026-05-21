---
title: Universal XSS via Web Archive (.webarchive) Format — Safari
slug: uxss-web-archive-safari
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/xss, technique/browser, technique/safari, technique/uxss]
inbound: []
---

# Universal XSS via Web Archive (.webarchive) Format — Safari

## Pattern

Safari's `.webarchive` format stores entire web pages (HTML, CSS, JS, images)
in a single XML-based file that includes an `WebResourceURL` field specifying
the document's origin. In 2013, if an attacker controlled a `.webarchive` file,
they could set `WebResourceURL` to any origin (e.g., `https://facebook.com`)
and embed XSS payloads — executing JS in the context of any domain. This is
Universal XSS (uXSS) because it affects every website, not just one.

Ryan Pickren's 2022 chain ($100,500) shows how uXSS still works when multiple
Safari security mechanisms must be bypassed:

1. Victim visits attacker's website.
2. Attacker forces a download of a crafted `.webarchive` file (exploiting
   Safari's automatic file-opening behavior for trusted MIME types from same-
   site origins, combined with macOS Gatekeeper bypass via quarantine attribute
   manipulation).
3. Safari opens the `.webarchive`, setting the origin to an attacker-specified
   domain (`facebook.com`, `gmail.com`, etc.).
4. JavaScript in the `.webarchive` runs with that domain's origin, accessing
   cookies, localStorage, and making same-origin API calls.

## Preconditions

- Victim uses Safari on macOS.
- Attacker can serve a `.webarchive` file that Safari opens automatically (or
  tricks the user into opening it).
- In the 2022 chain: requires bypassing Gatekeeper's quarantine + Safari's
  automatic file download restrictions — achieved via a chain of bugs.

## Detection

- This is a browser vulnerability, not an application vulnerability.
- For application testing: check if the application serves `.webarchive` files
  with `Content-Disposition: inline` on a subdomain where an attacker can
  control the content (file upload + `.webarchive` MIME type).

## Triggering

The 2022 Ryan Pickren chain (simplified):
1. Craft `.webarchive` with `WebResourceURL = https://victim-site.com` and
   embedded JS payload.
2. Use a blob URL or data URI on the attacker site to construct the download.
3. Exploit macOS sandbox + Gatekeeper bypass to make Safari auto-open the file.
4. JS executes with `victim-site.com` origin.

## Seen in the wild

- 2022 — Apple, $100,500. Ryan Pickren chained multiple Safari/macOS zero-days
  to achieve uXSS via `.webarchive`. The chain required bypassing Gatekeeper
  and Safari's download restrictions. Apple patched the underlying `.webarchive`
  origin trust mechanism.
  [BBRE](https://www.youtube.com/watch?v=Yt1a3j-U2zI)

## References

- Ryan Pickren's blog post on the 2022 Safari uXSS chain
- WebKit `.webarchive` format specification
- See also: [../dom-xss/_index.md](../dom-xss/_index.md)
