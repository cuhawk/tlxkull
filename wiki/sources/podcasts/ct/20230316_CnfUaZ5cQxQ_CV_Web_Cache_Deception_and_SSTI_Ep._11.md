---
title: Ep 11 — CV, Web Cache Deception and SSTI
slug: 20230316-cv-web-cache-deception-and-ssti-ep-11
url: https://www.youtube.com/watch?v=CnfUaZ5cQxQ
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
fetched_utc: 2026-05-14T00:00:00Z
kind: podcast
extracted: true
extract_model: claude-code-manual
tags: [source, podcast, ct, web-cache-deception, ssti, jinjava, cvss, paypal]
inbound: []
---

# Ep 11 — CV, Web Cache Deception and SSTI

- Date: 2023-03-16
- video_id: CnfUaZ5cQxQ
- Speakers: Justin Gardner (JG), Joel Margolis (JM)

## Summary

CVSS gaming tips from a top H1 hunter: argue privilege-required none for self-signup or guest/ghost accounts (cite the standard); use attack-vector physical/local for hardware bugs without losing much severity; pump attack-complexity high for UUID-IDORs to defuse "but it's not enumerable" pushback. Joel describes a PayPal SSTI worth $26k on Jinjava (CVE-2020-12668) found while sending payment messages with curly braces — the payload rendered server-side and was visible in iOS notifications. Three distinct Web Cache Deception patterns: cache-prevention query parameter that gets dropped before caching, the `.aspx%3Frandom.js` trick that makes the cache see a JS file extension, and the path-append `index.aspx/poc-<rand>.png` style that exploits cache rules that key only on suffix. Hard rule: always add a unique parameter so production caches do not collide with real users.

## Techniques extracted

- [[../../techniques/server-side/web-cache-deception]] — three keying-by-extension WCD variants: cache-prevention param, `%3F` smuggled question mark in ASPX, and path-append `.png`/`.js`.
- [[../../techniques/server-side/jinjava-ssti-paypal]] — Jinjava (Java template engine) reachable from PayPal payment-message field; CVE-2020-12668 lets an injected template load arbitrary Java methods.
- [[../../techniques/idor/cvss-uuid-ac-high]] — convention for scoring UUID-IDORs: keep CVSS submission but bump attack-complexity high; chains with a UUID-leak Oracle remove the AC modifier.

## Tools mentioned

(none with novel quirks)

## Quotes

> "Just make sure that you're not using the standard URL because you're going to get some angry program emails probably."

> "Privilege-required low for a self-signup account makes no sense — there is no barrier; the barrier is one extra step that requires me to do something for free with no verification."

> "Your threat model isn't built around protecting these IDs and these being sensitive pieces of information, so you shouldn't treat them like they are."

## Cross-links

- [[../README.md]]
- [[../extracts.md]]
