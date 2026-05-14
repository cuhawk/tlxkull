---
title: CSPT + CDN Cache Deception Chain
slug: cspt-cache-deception-chain
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/cspt, technique/cache-deception]
inbound: []
---

# CSPT + CDN Cache Deception Chain

## Pattern

Classic web cache deception extracts an authenticated response by tricking
a CDN to cache it under a key like `/profile.css` (CDN sees `.css`,
origin still serves the authenticated content). The standard limitation:
the response often contains short-lived state (CSRF token, anti-replay
nonce) that the **victim must trigger themselves** - but the victim has
no reason to navigate to `/profile.css`.

Client-Side Path Traversal (CSPT) closes that gap. An attacker controls
a path component used by client-side JS to build a `fetch` URL. The JS
adds the session cookies + CSRF token automatically. If the attacker
manipulates the CSPT path to end with `.css` (or any other CDN-cacheable
suffix), the authenticated fetch lands at a CDN-cache key the attacker can
later read cross-origin.

**Flow:**
1. Attacker links victim to a page that does `fetch(\`/api/me/${param}\`)`
   with `param = ../../../../../../some-public.css`.
2. Victim's browser sends the request with cookies + CSRF token.
3. CDN sees the path ends `.css` -> caches.
4. Attacker fetches `https://victim.com/some-public.css` cross-origin ->
   reads the cached, authenticated body.

Researcher: Jorge da Costa (2025).

## Preconditions

- A client-side fetch builds a URL from a user-controlled path component.
- The CDN's cache key rules include the path suffix-based static-asset
  shortcut (.css, .js, .png, .pdf - common Cloudflare/Akamai default).
- Origin returns the authenticated response regardless of suffix
  (i.e., does not 404 the `.css` extension).
- Cookies are not `SameSite=Strict` on the relevant cookie (because the
  client-side JS runs same-site to the fetch target - most CSPT
  scenarios satisfy this automatically; this is precisely the gap CSPT
  fills relative to plain CSRF).

## Detection

- `js_analyzer`: tag fetch calls where the URL is built by string
  concatenation including user input.
- For each candidate, attempt to inject `../../something.css` and observe:
  (a) does the fetch reach the origin? (b) does the CDN cache the
  response (visible via `Cache-Control` and `Age` headers on a follow-up
  uncredentialed request)?

## Triggering

```html
<!-- attacker.com -->
<a href="https://victim.com/page?next=../../../static/anyname.css">
  click for cute kittens
</a>
```

```js
// on victim.com/page - vulnerable code
fetch(`/api/me/${params.get('next')}`)  // resolves to /static/anyname.css
  .then(r => r.json()).then(render);
```

Attacker then loads `https://victim.com/static/anyname.css` (no auth) and
parses the cached JSON body containing the CSRF token + user PII.

## Bypasses

- CDN caches by full URL including query string - append `?nocache=1` per
  visit, or strip the query via `?` in the CSPT injection.
- Surrogate-Control / Cache-Control negotiation - even if the origin sends
  `private`, some CDNs cache static-suffix paths regardless.

## Seen in the wild

- {date: 2025-08-28, source: CT Ep 137} - Jorge da Costa published the chain; affected target undisclosed, but technique generalises across any CSPT-capable single-page-app on a static-asset-caching CDN.

## References

- Jorge da Costa writeup - Cache Deception + CSPT (referenced in episode).
- Matan Berenstein - CSPT introduction (cited).
- Maxence Schmidt - CSPT talk (cited).
- Critical Thinking Podcast Ep 137 - <https://www.youtube.com/watch?v=sTG-OX5BbBc>
- Related: [[cspt-fetch-hijacking]], [[cspt-react-useparams]]
