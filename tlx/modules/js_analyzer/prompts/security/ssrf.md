---
id: ssrf
kind: security
title: Server-side request forgery
tags: [ssrf, server, fetch, http-client]
always_include: false
priority: 50
---

SSRF analysis (when the target ships a Node.js / server side).

Sources (URLs the user controls):
  req.body, req.query, req.params, parsed JSON fields like {url, callback,
  webhook, image_url, redirect}, multipart fields.

Sinks (outbound HTTP / DNS):
  fetch, axios, got, request, http.get, https.request, node-fetch, url.parse
  followed by net.connect, child_process spawning curl/wget.

Bypasses to flag:
  - Allow-list by string match on hostname (DNS rebinding bypass).
  - URL parser inconsistencies (Node WHATWG vs `url.parse` legacy).
  - Decimal / hex / IPv6 / 0.0.0.0 / 127.x / 169.254.169.254 bypasses.
  - Following redirects without re-checking the target.
  - Internal-only services (metadata, admin) reached via SSRF.

Trace pattern:
  1. semantic_search for fetch / axios / request constructors.
  2. Walk back to the URL argument's source.
  3. Confirm allow-list / IP filtering happens *after* DNS resolution and
     covers redirects.
