---
title: WordPress REST GET-with-body parser confusion
slug: wp-get-body-parse
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/wordpress, technique/parser-confusion, technique/access-control]
inbound: []
---

# WordPress REST: GET-with-body parser confusion

## Pattern

WordPress REST core reads the raw HTTP body for every request method,
including `GET`. JSON in a GET body gets parsed into `WP_REST_Request`
and becomes accessible to the route handler. But the body **does not
appear** in `$_GET`, `$_POST`, or `$_REQUEST` -- only in `php://input`
and through `WP_REST_Request::get_param`.

Plugins that use `WP_REST_Request` for sanitization checks and `$_GET`
for routing decisions (or vice-versa) get a parser-confusion bug:

- Sanitizer reads `$wpReq->get_param('action')` and sees a benign value.
- Routing / capability check reads `$_GET['action']` and sees nothing
  -> falls through to a default path.

Or the opposite -- admin-only fields hidden from `$_REQUEST` may be
silently honoured by the inner handler.

## Preconditions

- WordPress 5.0+ with REST API enabled.
- Plugin handler reads request params via mixed mechanisms
  (`$_GET`/`$_REQUEST` for some, `WP_REST_Request::get_param` for
  others).

## Detection

- Static: in plugin source, hunt for routes registered with
  `register_rest_route` that touch `$_GET` / `$_REQUEST` /
  `$_POST` / `filter_input`. Those are the candidates -- REST should
  read through the request object only.
- Dynamic: send the same param via query-string vs JSON body in a GET
  request; observe differing behaviour:

```http
GET /?rest_route=/some/plugin/route&action=safe HTTP/1.1
Content-Type: application/json
Content-Length: 36

{"action":"privileged","key":"x"}
```

## Triggering

Body-borne params override or stay invisible to legacy `$_GET`-checking
code. Plugins built before WP 5.0 that retroactively added REST routes
are higher-yield.

## Bypasses (of WAFs)

- WAF inspects `$_GET` / query string only -- body content invisible
  to WAF.
- Even if the WAF parses bodies, GET-with-body is unusual enough that
  many rule sets skip it.

## Defence

- Never mix `$_GET` / `$_POST` superglobals inside a REST handler. Use
  `WP_REST_Request::get_param` exclusively.

## Seen in the wild

- {date: 2024-01-25, source: CT Ep 55} -- Ram Gall surfaces this as a
  "weird WordPress shit" gotcha that surprised Justin live on the
  podcast.

## References

- Critical Thinking Podcast Ep 55
- WordPress REST API Handbook -- request lifecycle
- Related: [[wp-rest-route-enum]], [[nonce-as-access-control]]
