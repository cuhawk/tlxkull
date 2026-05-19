---
title: Web Cache Poisoning — summary
slug: cache-poisoning-summary
created_utc: 2026-05-19T00:00:00Z
updated_utc: 2026-05-19T00:00:00Z
tags: [technique/cache-poisoning, technique/cache, summary, index]
inbound: []
---

# Web Cache Poisoning — summary

## What this class is

Web Cache Poisoning tricks a caching layer (CDN, reverse-proxy cache, Varnish, Cloudflare, Fastly, Akamai, nginx `proxy_cache`, Cloudfront, application-tier cache) into storing an attacker-controlled response under a cache key that legitimate users will later request. Every subsequent visitor to that key receives the poisoned response until the cache entry expires or is purged.

Cache poisoning attacks the **store**, not the parser. It typically exploits one of two surfaces:

1. **Key generation** — some part of the request that influences the response is *not* included in the cache key (an "unkeyed input"). Attacker controls the unkeyed input, sets the response, then a legitimate user requests the same keyed inputs and is served the attacker's response.
2. **Cache rule analysis** — the cache stores a response it should not have stored (dynamic content marked cacheable, sensitive responses cached under public keys, URL-normalization disagreements between cache and origin).

Distinct from but often confused with:

- **Web Cache Deception** — tricks the cache into storing a *victim's private* response under a public-looking URL. Confidentiality attack, not integrity.
- **HTTP Response Splitting** — CRLF injection that lets attacker forge an entire second response; one of the older delivery mechanisms for cache poisoning.
- **HTTP Request Smuggling** — desync attack that can be chained to feed the cache an attacker-controlled response under any URL. See [`smuggling-to-cache.md`](smuggling-to-cache.md).

## When to suspect

- Any response with `Cache-Control: public`, `s-maxage`, `Age:` header, `X-Cache: HIT`, `CF-Cache-Status: HIT`, `Via:` proxy chain.
- Application reflects header values (`X-Forwarded-Host`, `X-Original-URL`, `X-Forwarded-Proto`, `X-Rewrite-URL`, custom `X-*`) into the response body, redirects, or `<base>` href.
- Cache key normalizes paths (`/foo/` vs `/foo` vs `/foo;jsessionid=x` vs `/foo?cb=1`) differently than the origin.
- Different response for `?utm_source=poison` than for `?` — query-parameter cloaking opportunities.
- Vary header omits the input that actually changes the response.
- Cookie-driven content with no `Vary: Cookie`.

## Failure modes (class taxonomy)

| Variant | Unkeyed / mis-analyzed input | Effect |
|---|---|---|
| Unkeyed header | `X-Forwarded-Host`, `X-Forwarded-Scheme`, custom `X-*` | Attacker's header value reflected in response (links, redirects, `<script src>`) and cached |
| Unkeyed query param | Specific param dropped from key but consumed by app | Reflected XSS / open redirect cached under clean URL |
| Cache key normalization | Cache lowercases / strips trailing `;sessionid=x`, origin doesn't (or vice versa) | Static-extension cloaking (request `/api/profile;.js` returns `/api/profile`, gets cached as static) |
| URL-parser discrepancy | RFC ambiguity between cache and origin parser | Static path deception, semicolon / dot-segment / param-pollution variants — see [`url-parser-discrepancy.md`](url-parser-discrepancy.md) |
| Smuggling delivery | None directly — smuggling provides the malicious response | Persistent JS hijacking on any URL (PayPal-class) — see [`smuggling-to-cache.md`](smuggling-to-cache.md) |
| Response splitting | CRLF in unsanitized header value | Forge an entire second HTTP response that the cache stores against the request URL |
| DoS via poisoning | Oversized response, malformed headers, parser-crash | Cache stores an unusable response → effective DoS of the cached resource — see [`cache-poisoning-to-dos`](../../_external/hacktricks/src/pentesting-web/cache-deception/cache-poisoning-to-dos.md) |
| Fat GET / parameter cloaking | Origin reads body of GET, cache ignores body | Inconsistent inputs between key and content |

## Methodology (PortSwigger "Practical Web Cache Poisoning")

1. **Identify unkeyed inputs.** Send the same request with one header / param varied; if the cached response (look at `Age:`, `X-Cache:`) differs, that input is unkeyed.
2. **Find a gadget.** An unkeyed input is useless without a *gadget* — application code that reflects the input into the response somewhere harmful (`<base>` href, redirect Location, `<script src>`, JSON config). PortSwigger calls this "unkeyed input that meets a gadget".
3. **Confirm the cache stores it.** Send the poisoning request, then a clean request, check the clean response contains your payload. Inspect `Age:` / `X-Cache:` to confirm it's a true cache hit, not just the back-end echoing your header on every request.
4. **Maximize cache hit window.** Add `?cb=<rand>` to scope to a unique key, or align timing to the cache TTL boundary.
5. **Burst poisoning** — fire many parallel requests to outrun cache TTL.

## External references

| Topic | PayloadsAllTheThings | HackTricks | PortSwigger |
|---|---|---|---|
| Cache poisoning theory | — | [`cache-deception/README.md`](../../_external/hacktricks/src/pentesting-web/cache-deception/README.md) | [research-practical-web-cache-poisoning](../../sources/blogs/personal/portswigger-research/research-practical-web-cache-poisoning.md) |
| Cache poisoning via URL discrepancy | — | [`cache-poisoning-via-url-discrepancies.md`](../../_external/hacktricks/src/pentesting-web/cache-deception/cache-poisoning-via-url-discrepancies.md) | [research-gotta-cache-em-all](../../sources/blogs/personal/portswigger-research/research-gotta-cache-em-all.md) |
| Static Path Deception / Hat Trick | — | — | [research-a-hacking-hat-trick](../../sources/blogs/personal/portswigger-research/research-a-hacking-hat-trick-previewing-three-portswigger-research-publications-coming-to-def-con-amp-black-hat-usa.md) |
| Web Cache Deception (sibling class) | [`Web Cache Deception/`](../../_external/payloads-all-the-things/Web%20Cache%20Deception/README.md) | [`cache-deception/README.md`](../../_external/hacktricks/src/pentesting-web/cache-deception/README.md) | — |
| Cache poisoning to DoS | — | [`cache-poisoning-to-dos.md`](../../_external/hacktricks/src/pentesting-web/cache-deception/cache-poisoning-to-dos.md) | — |
| Detectify primer | — | — | [Detectify — 10 missed vulns (#7 Web Cache Poisoning)](../../sources/blogs/detectify/security-guidance-10-types-of-web-vulnerabilities-that-are-often-missed.md) |
| Response splitting (delivery vector) | [`CRLF Injection/`](../../_external/payloads-all-the-things/CRLF%20Injection/README.md) | [`crlf-0d-0a.md`](../../_external/hacktricks/src/pentesting-web/crlf-0d-0a.md) | — |

## Related local pages

- [Request smuggling SUMMARY](../request-smuggling/SUMMARY.md) — the highest-impact delivery vector for cache poisoning.
- [DOM XSS — cspt-cache-deception-chain](../dom-xss/cspt-cache-deception-chain.md) — client-side path traversal that lands in a cacheable URL.
- [CSP SUMMARY](../csp/_index.md) — CSP bypass classes get amplified once they land in a poisoned cached asset.
- [server-side / web-cache-deception](../server-side/web-cache-deception.md) — sibling class (confidentiality, not integrity)
- [server-side / cache-parameter-cloaking](../server-side/cache-parameter-cloaking.md) — Kettle's Web Cache Entanglement parameter cloaking
- [server-side / cloudflare-cache-key-header-overflow](../server-side/cloudflare-cache-key-header-overflow.md) — Cloudflare cache-key boundary discrepancy
- [server-side / akamai-edge-smuggling](../server-side/akamai-edge-smuggling.md) — Akamai edge → cache delivery

## Sub-patterns to expand

- [x] [`unkeyed-header.md`](unkeyed-header.md) — classic `X-Forwarded-Host` / `X-Original-URL` poisoning
- [x] [`url-parser-discrepancy.md`](url-parser-discrepancy.md) — cache and origin disagree on URL normalization
- [x] [`smuggling-to-cache.md`](smuggling-to-cache.md) — chain smuggling into persistent cached XSS
- [ ] `fat-get.md` — origin reads body of GET, cache ignores
- [ ] `cache-key-injection-via-header-bypass.md` — `X-HTTP-Method-Override`, `X-Original-URL` rewriting key
- [ ] `cdn-fingerprints-cache.md` — Cloudflare / Fastly / Akamai / Cloudfront quirks
- [ ] `cookie-poisoning-cached.md` — Set-Cookie cached when it shouldn't be
