---
title: PortSwigger — DOM-based vulnerabilities
slug: portswigger-dom-based
url: https://portswigger.net/web-security/dom-based
fetched_utc: 2026-05-12T00:00:00Z
kind: article
extracted: true
extract_model: sonnet
tags: [source, technique/dom-xss, ref/portswigger]
inbound: []
---

# PortSwigger — DOM-based vulnerabilities

## TL;DR

- DOM-based vulnerabilities occur when JavaScript unsafely passes attacker-controlled data (sources) to potentially dangerous functions (sinks), entirely client-side.
- Common sources: `location.hash`, `document.cookie`, `location.search`, `document.referrer`, `window.name`.
- Common sinks: `eval()`, `innerHTML`, `window.location`, `document.write`, `setTimeout(string)`.
- Taint-flow analysis tracks how untrusted data moves from sources to sinks; prevention requires avoiding raw tainted data reaching sinks.
- Vulnerability types covered: DOM XSS, open redirection, cookie manipulation, and DOM clobbering.

## Sub-sections

- What is the DOM?
- Taint-flow vulnerabilities
  - What is taint flow?
  - Sources
  - Sinks
  - Common sources
  - Which sinks can lead to DOM-based vulnerabilities?
  - How to prevent DOM-based taint-flow vulnerabilities
  - Read more
  - Find DOM-based vulnerabilities using Burp Suite
- DOM clobbering
