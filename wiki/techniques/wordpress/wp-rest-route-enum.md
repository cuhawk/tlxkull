---
title: WordPress REST route enumeration via rest_route=/
slug: wp-rest-route-enum
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/wordpress, technique/recon, technique/info-disclosure]
inbound: []
---

# WordPress REST route enumeration

## Pattern

Every WordPress install exposes a complete catalogue of registered REST
routes via `?rest_route=/` (works even when permalinks are not
"pretty"). Unauthenticated. Returns JSON with every namespace, every
route, every accepted method, and every parameter schema. Equivalent to
finding a fully-documented Swagger / OpenAPI on a target -- but for
WordPress.

## Preconditions

- WordPress with REST API enabled (default; very few sites disable it).
- No auth required.

## Detection / triggering

```http
GET /?rest_route=/
GET /wp-json/                 # alternate, only when pretty permalinks on
```

Response is a single huge JSON object:

```json
{
  "namespaces": ["wp/v2", "contact-form-7/v1", "wc/v3", ...],
  "routes": {
    "/contact-form-7/v1/contact-forms/(?P<id>\\d+)": {
      "namespace": "contact-form-7/v1",
      "methods": ["GET", "POST", "DELETE"],
      "endpoints": [...]
    },
    ...
  }
}
```

Each namespace ~= one plugin. Drilling further:

```http
GET /?rest_route=/<namespace>/
```

## Recon value

- Every namespace maps to a plugin -> version -> CVE lookup.
- Routes that don't appear in plugin docs are private internal routes
  worth focusing on.
- Schema lists accepted parameters -- saves you fuzzing.

## REST-route-specific gotchas

- `permission_callback` defaulting to `__return_true` makes a route
  fully unauthenticated.
- WordPress core attempts to parse the request body for **any HTTP
  method including GET** when called via `?rest_route=/`. So a
  `GET ?rest_route=/x/y { "secret": "..."}` with a JSON body works. The
  body bypasses `$_GET` / `$_POST` / `$_REQUEST` superglobals; plugins
  using only `$_GET` for sanitization while the REST core reads from
  `WP_REST_Request` get a parser-confusion bug class. See
  [[wp-get-body-parse]].

## Seen in the wild

- {date: 2024-01-25, source: CT Ep 55} -- Ram Gall walks Justin through
  it live; both surprised this is not behind a "weird WordPress shit"
  warning.

## References

- Critical Thinking Podcast Ep 55
- WordPress Developer Resources -- REST API Handbook
- Related: [[nonce-as-access-control]], [[wp-get-body-parse]]
