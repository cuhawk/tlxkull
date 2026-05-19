---
title: Michał Bentkowski
slug: michal-bentkowski
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-19T14:42:00Z
tags: [person, role/researcher, focus/client-side, focus/xss, focus/html-sanitizers, focus/prototype-pollution, vendor/securitum]
handles: [securitymb]
role: researcher
primary_focus: client-side
inbound: []
---

# Michał Bentkowski

## Identity

- **Real name:** Michał Bentkowski
- **Primary handle:** `SecurityMB` (X/GitHub/HackerOne/Mastodon — all lowercase)
- **Role:** researcher (Chief Security Researcher at Securitum; later also Information Security Engineer at Google)
- **Affiliation:** [Securitum](https://securitum.com/) — Polish pentest/training firm — since 2013.

## Focus areas

- Client-side / browser security
- Mutation XSS (mXSS) — arguably the foremost public researcher on the topic
- HTML sanitizer bypasses (DOMPurify, Ruby Sanitize, others)
- [Prototype pollution](../techniques/prototype-pollution/) → XSS / RCE chains
- Obscure HTML/CSS parsing quirks and namespace confusion ([DOM XSS](../techniques/dom-xss/))

## Online presence

- [Personal site](https://www.bentkowski.info/) — landing page + research index
- [Research index (bentkowski.info)](https://www.bentkowski.info/research/) — curated post list
- [Securitum author page](https://research.securitum.com/authors/michal-bentkowski/) — full Securitum blog archive
- [X / Twitter — @SecurityMB](https://x.com/securitymb)
- [Mastodon — @securitymb@infosec.exchange](https://infosec.exchange/@securitymb)
- [GitHub — securityMB](https://github.com/securityMB)
- [HackerOne — securitymb](https://hackerone.com/securitymb)
- [XSS Academy](https://xss.academy/) — training course he authored
- [SECURE 2018 talk (YouTube)](https://www.youtube.com/watch?v=HtoO3KSGR9E) — early Securitum conference talk

## Key research / posts

- [Write-up of DOMPurify 2.0.0 bypass using mutation XSS](https://research.securitum.com/dompurify-bypass-using-mxss/) — the seminal mXSS-against-DOMPurify post, fixed in 2.0.1. Seeds [../techniques/dom-xss/](../techniques/dom-xss/) sanitizer-bypass material.
- [Mutation XSS via namespace confusion — DOMPurify < 2.0.17 bypass](https://research.securitum.com/mutation-xss-via-mathml-mutation-dompurify-2-0-17-bypass/) — MathML/SVG namespace re-parenting trick; foundational mXSS pattern.
- [Helping secure DOMPurify (part 1)](https://research.securitum.com/helping-secure-dompurify-part-1/) — defender-side writeup of multiple bypass classes he found and helped patch.
- [Prototype pollution and bypassing client-side HTML sanitizers](https://research.securitum.com/prototype-pollution-and-bypassing-client-side-html-sanitizers/) — original `ALLOWED_ATTR` / `CONFIG` gadget research; cross-links [../techniques/prototype-pollution/](../techniques/prototype-pollution/) ↔ sanitizer-bypass.
- [Exploiting prototype pollution — RCE in Kibana (CVE-2019-7609)](https://research.securitum.com/prototype-pollution-rce-kibana-cve-2019-7609/) — the canonical client-side-PP→RCE example; widely cited.
- [XSS in GMail's AMP4Email via DOM Clobbering](https://research.securitum.com/xss-in-amp4email-dom-clobbering/) — DOM clobbering popularized as a real attack vector against a hardened target.
- [HTML sanitization bypass in Ruby Sanitize < 5.2.1](https://research.securitum.com/html-sanitization-bypass-in-ruby-sanitize-5-2-1/) — shows the same mXSS class generalizes beyond JS sanitizers.
- [Marginwidth/marginheight — the unexpected cross-origin communication channel](https://research.securitum.com/marginwidth-marginheight-the-unexpected-cross-origin-communication-channel/) — novel cross-origin side-channel via legacy HTML attributes.
- [CSS data exfiltration in Firefox via a single injection point](https://research.securitum.com/css-data-exfiltration-in-firefox-via-single-injection-point/) — CSS-only exfil from a single sink; relevant to [../techniques/css-injection/](../techniques/css-injection/).
- [The Curious Case of Copy & Paste](https://research.securitum.com/the-curious-case-of-copy-paste/) — paste-from-clipboard attack surface in browsers.
- [Security analysis of `<portal>` element](https://research.securitum.com/security-analysis-of-portal-element/) — early review of an experimental embedding primitive.
- [Server-Side Template Injection — Pebble](https://research.securitum.com/server-side-template-injection-on-the-example-of-pebble/) — rare server-side post from him; SSTI walkthrough in the Pebble engine.
- [DOMPurify bypass — HackerOne IBB #1024734](https://hackerone.com/reports/1024734) — disclosed report tying mXSS research to an IBB payout.
- [Prototype Pollution in Kibana (slides)](https://slides.com/securitymb/prototype-pollution-in-kibana) — talk deck companion to the Kibana post.

## CT podcast appearances

- None confirmed as of 2026-05-15. Bentkowski has not (yet) appeared as a guest on Critical Thinking. He is, however, a regular voter in the PortSwigger Top 10 Web Hacking Techniques community panel — which CT covers most years — and his own research has repeatedly been nominated/ranked in that list. See [PortSwigger Top 10](https://portswigger.net/research/top-10-web-hacking-techniques) for the annual archive.
- Adjacent interview (not CT, but a similar long-form): [Bug Bounty Reports Explained — "From reporting self-XSSes to improving browser security mechanisms"](https://www.bugbountyexplained.com/from-reporting-self-xsses-to-improving-browser-security-mechanisms-michal-bentkowski/).

## Notes

- **Mutation XSS pioneer.** Heiderich et al. coined mXSS in 2013, but Bentkowski is the researcher who turned it into a repeatable attack toolkit against modern sanitizers. Every DOMPurify hardening cycle from 2.0.x → 2.5.x has at least one CVE/credit traceable to him.
- **DOMPurify breaker turned co-defender.** Cure53 (DOMPurify maintainers) routinely credit him; his "Helping secure DOMPurify" series is essentially the defender's-eye view of his own attacks.
- **Signature trick:** namespace re-parenting — moving a node between HTML / MathML / SVG namespaces so the parser re-serializes the subtree differently than the sanitizer saw it. Generalizes beyond DOMPurify (see Ruby Sanitize post).
- **Prototype-pollution gadget framing.** He (with BlackFan) popularized the "PP-to-XSS via sanitizer config gadgets" pattern — overwrite `Object.prototype.ALLOWED_ATTR` etc. to disable filtering. Now standard PP exploitation material.
- **Output style:** technical, terse, lots of minimal HTML/JS PoCs inline. Reads like a sanitizer regression-test suite in prose form. Worth re-reading whole posts when hunting any HTML-sanitizer target — payloads usually generalize.
- **Trigger to consult his blog:** anytime a target ships DOMPurify, sanitize-html, Ruby Sanitize, or any allow-list HTML filter — and especially when the app stores HTML then re-renders it (mXSS thrives on re-parse).
- **Trigger from prototype pollution:** if a target has PP and any client-side sanitizer/template config, his work is the playbook. See [../techniques/prototype-pollution/](../techniques/prototype-pollution/).

## Wiki RAG ingestion

Blog bodies ingested 2026-05-19 into the `wiki` Chroma collection.
Source files:

- `wiki/sources/blogs/personal/securitum-research/`

Query via `docs_query(collection="wiki", query="...")` instead of WebFetch.

