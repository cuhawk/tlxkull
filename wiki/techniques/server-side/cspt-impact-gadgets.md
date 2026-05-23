---
title: CSPT impact-chaining gadgets cookbook
slug: cspt-impact-gadgets
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [technique/cspt, technique/path-traversal, technique/gadget]
inbound: []
---

# CSPT impact-chaining gadgets cookbook

CT Ep. 175 — Joel Margolis. CSPTs are everywhere (web, mobile,
desktop) but typically present as "I can rewrite the URL on a GET
that does nothing interesting". This page lists the three gadgets
Joel chains in to convert low-impact CSPT into financial / ATO /
data-mod impact. Apply in order; first hit wins.

## Pattern

When a CSPT lets the attacker steer a request but body / verb / headers
are out of reach, lean on **what the target endpoint accepts** —
not what the originating call sends. Most server frameworks dual-
parse query and body; many endpoints accept partial input; redirects
and JSON-hosting gadgets fill the remaining gaps.

## Gadget 1 — query-as-body

Frameworks that read `request.params` (Rails, Sinatra, older Express
middlewares, Spring `@RequestParam` merge) treat `?key=val` and JSON
body keys interchangeably. Even if the originating CSPT'd request has
a fixed body (or no body control), the **query string is yours** —
inject the parameter names the *target* endpoint expects.

```
POST /api/internal/users/<traversed>?role=admin
Content-Type: application/json

{"unrelated":"body"}   ← victim-controlled, attacker doesn't care
```

Hits if the target endpoint reads `role` from query.

## Gadget 2 — body-less endpoint match

If the CSPT's outgoing request *forces* a body the target rejects (415,
"unexpected JSON keys"), pivot to an endpoint that ignores the body.
`/logout`, `/refresh`, `/cancel`, `/confirm`, `/.../resend` are usually
`POST` with no body or with optional body — they look at session + path
+ query only.

Detection: scan the API for POST routes whose handler signature does
**not** declare a body schema; those are CSPT-friendly sinks.

## Gadget 3 — partial-JSON-injection + auxiliary gadget chain

When the target endpoint needs a *specific* JSON shape the CSPT can't
produce, chain:

- **Open redirect** to bounce the CSPT'd request to a different host
  the target trusts.
- **Arbitrary-JSON-hosting endpoint** (any uploaded-JSON / pastebin /
  user-controlled-file-store endpoint on the same origin) to serve the
  exact body the target wants.
- **Partial JSON injection** elsewhere — if you control one key /
  value pair in a downstream JSON request, you can sometimes piece the
  required shape together across two stitched requests.

The combinatorial space is wide; most real CSPTs have *some* impact
gadget reachable from the same origin once you stop demanding the
originating request itself do all the work.

## Method-override fallback

Joel didn't enumerate this on the podcast but it pairs naturally:
`X-HTTP-Method-Override: DELETE`, `_method=DELETE` in query, or path-
suffix-based override (Rails `/users/1.json?_method=delete`) flips the
verb when the CSPT only emits POST. Worth one shot per target.

## Methodology checklist

Per CSPT finding, before declaring it low-impact:

- [ ] Identify all parameter sources the target framework accepts
      (query, body, header, cookie). Try query injection.
- [ ] Enumerate body-less / body-optional endpoints on the same API.
      Pivot path traversal to one of them.
- [ ] Search same-origin for JSON-hosting gadgets (file upload that
      returns a same-origin URL, pastebin-like share, raw-blob endpoint).
- [ ] Search same-origin for open redirects to bounce out-of-host.
- [ ] Try method-override headers + query.

## Seen in the wild

- {date: 2026-05-22, source: CT Ep. 175} — Joel Margolis bundled all
  three into a single CSPT on a mobile app
  ([[../mobile/cspt-mobile-deeplink-stored-params]]) — financial loss,
  account modification, access-request auto-approval.

## Related

- [[../mobile/cspt-mobile-deeplink-stored-params]] — mobile delivery.
- [[../dom-xss/cspt-fetch-hijacking]] — original web CSPT vector.
- [[../dom-xss/cspt-on-desktop-apps]] — desktop variant.
- [[../dom-xss/cspt-react-useparams]] — React-router source.
- [[client-side-path-traversal-csrf]] — CSPT-2-CSRF naming.

## References

- Critical Thinking Podcast Ep. 175 — "Rhyno's Hackbot Setup, Sick Bugs
  and ZDI Drama" (2026-05-21).
  [CT Ep. 175](wiki://podcasts/ct/20260521_v-XhQHy_jHM_Rhyno_s_Hackbot_Setup_Sick_Bugs_and_ZDI_Drama_Ep._175)
- Doyensec — CSPT-2-CSRF write-ups (cross-referenced from
  [[client-side-path-traversal-csrf]]).
