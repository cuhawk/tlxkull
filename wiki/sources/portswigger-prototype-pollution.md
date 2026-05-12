---
title: PortSwigger — Prototype pollution
slug: portswigger-prototype-pollution
url: https://portswigger.net/web-security/prototype-pollution
fetched_utc: 2026-05-12T00:00:00Z
kind: article
extracted: true
extract_model: sonnet
tags: [source, technique/prototype-pollution, ref/portswigger]
inbound: []
---

# PortSwigger — Prototype pollution

## TL;DR

- Prototype pollution allows attackers to add arbitrary properties to `Object.prototype` via deep-merge operations that don't sanitize keys like `__proto__`, `constructor`, or `prototype`.
- Not directly exploitable alone — requires a gadget: a code path that reads the polluted property unsafely.
- Client-side PP chains with DOM XSS gadgets; server-side PP (Node.js) can yield RCE via gadgets in popular packages.
- Primary sources: URL query strings with bracket notation (`?__proto__[x]=y`) and JSON bodies with nested `__proto__` keys.
- Script source hijacking is a key client-side gadget pattern: polluting a `transport_url` or `src` property to load attacker JS.

## Sub-sections

- How do prototype pollution vulnerabilities arise?
- Prototype pollution sources
  - Prototype pollution via the URL
  - Prototype pollution via JSON input
- Prototype pollution sinks
- Prototype pollution gadgets
  - Example of a prototype pollution gadget
  - What next?
