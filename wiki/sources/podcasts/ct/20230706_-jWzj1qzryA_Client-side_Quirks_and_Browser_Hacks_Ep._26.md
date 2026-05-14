---
title: Ep 26 -- Client-side Quirks and Browser Hacks
slug: ct-ep-26-client-side-quirks-browser-hacks
url: https://www.youtube.com/watch?v=-jWzj1qzryA
fetched_utc: 2026-05-14T00:00:00Z
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
kind: podcast
extracted: true
extract_model: claude-code-manual
tags: [source, podcast, ct, dom-xss, browser-quirks, csp, sanitizer-bypass, recon]
inbound: []
---

# Ep 26 -- Client-side Quirks and Browser Hacks

- Date: 2023-07-06
- video_id: -jWzj1qzryA
- Speakers: Justin Gardner (JG), Joel Margolis (JM)

## Summary

News-heavy episode covering nginx alias-traversal applied via GitHub code
search by Hawkeye Labs (Bitwarden + Google bounty pop on five-year-old Orange
research), the new Chrome `popovertarget` XSS sink (any element becomes
clickable; Cure53 + Saurush extend with hidden-target + `==` regex-bypass
variants), the Firefox MathML quirk where `<math><xss href=javascript:...>`
fires on click, plus a LiveOverflow video on `<?` and `<` + number HTML
comment quirks. Discussion of patch-diffing methodology via Mr Tux Racer's
WooCommerce Payments writeup (CVE 9.8, single header `X-WC-Pay-Platform-Checkout-User: 1`
creates admin). Covers dynamic `import()` as a length-limited XSS payload
plus the `then`-export implicit-call MDN warning. Re-reads Gareth Heyes's
JavaScript-for-Hackers: HTML comments inside JS, `#!` shebang as JS comment,
unicode en-dash auto-correct gotcha. DOM-clobbering example walked through
PortSwigger Academy: two `<a>` with same id collapse to an HTMLCollection,
`name` attribute on second clobbers sub-property, `.toString()` on the anchor
returns href. Closes by demonstrating that `<base>` tag works in `<body>` in
Chrome and Safari (HTML spec says head-only); meta tags `http-equiv=refresh`
as no-JS redirect and `Content-Type` charset-flip for HTML-injection-only XSS
escalation. CSS-only Doom and Gareth's CSS-only homepage as side note for the
power of pure-CSS XS-leak primitives.

## Techniques extracted

- [[../../techniques/dom-xss/popover-target-xss]] -- Chrome `popovertarget` makes any tag a click sink; `==` regex-bypass variant; hidden target works.
- [[../../techniques/dom-xss/math-element-clickable-firefox]] -- Firefox `<math>` makes any child with `href` clickable, including unknown tags.
- [[../../techniques/dom-xss/dynamic-import-xss-gadget]] -- ECMAScript dynamic `import()` in browser as ultra-short XSS payload; `then` export implicit-call gotcha.
- [[../../techniques/dom-xss/base-tag-anywhere]] -- `<base>` in body (not just head) hijacks relative URLs in Chrome and Safari; HTML spec says head-only but browsers ignore.
- [[../../techniques/dom-xss/dom-clobbering-to-xss]] -- duplicate-id HTMLCollection + second-element `name` attribute clobbers sub-property; anchor `.toString()` returns href.
- [[../../techniques/server-side/nginx-alias-traversal]] -- Orange Tsai's 2018 nginx `alias` off-by-slash applied via GitHub code search five years later.

## Tools mentioned

- jsluice (Tom Nom Nom) -- go-tree-sitter-based JS URL/secret extractor; better than LinkFinder.
- GitHub code search (`cs.github.com`) -- free regex search across all indexed repos; used for nginx-alias hunting.
- CSP Evaluator (Google) -- 2016-vintage tool; still useful but list of JSONP gadgets is stale.
- Source-graph -- alternative; self-hostable for per-bounty-program org scoping.

## Quotes

> "Don't forget about the magical math element which can make any HTML
> element clickable within the Firefox browser."
> -- JM, quoting `@theRCEguy`.

> "[`<base>`] in the body works. The HTML spec says specifically it has to
> be in the head, and it works perfectly fine in the body tag in lots of
> browsers."
> -- JG, after live-testing on Chrome and Safari.

> "Import is one of those things where it kind of blows the mind how it
> actually works in the browser ... extremely counterintuitive."
> -- JM, on dynamic `import()`.

## Cross-links

- [[../README.md]]
- [[../extracts.md]]
