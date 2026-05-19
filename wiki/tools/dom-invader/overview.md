---
title: DOM Invader — overview
slug: dom-invader-overview
created_utc: 2026-05-19T00:00:00Z
updated_utc: 2026-05-19T00:00:00Z
tags: [tool/dom-invader, technique/dom-xss, technique/prototype-pollution]
inbound: []
---

# DOM Invader

Browser extension embedded in Burp Suite's built-in Chromium browser.
Automates discovery of DOM XSS, prototype pollution sources, and
postMessage vulnerabilities. Available in both Community and Pro editions.

## How it works
Injects a random alphanumeric **canary** into request parameters (query
string, hash, postMessage). Instruments DOM sinks (`eval`, `innerHTML`,
`document.write`, `src`, `href`, etc.) to detect when the canary arrives.
Reports source → sink paths in the Augmented DOM view inside DevTools.

## Modes

### 1. DOM XSS (default)
Tracks canary from URL parameters into sinks. Augmented DOM tab shows
which frame, which event, and which sink received the canary.

Callback API: configure a custom JS function that fires on each
source/sink hit — logs structured data to console. Useful for
large-scale at-scale scanning:
```javascript
function callback(data) { console.log(JSON.stringify(data)); return true; }
```

### 2. postMessage interception
Enable "Post Message Interception" → DOM Invader auto-posts messages to
`window.addEventListener('message', ...)` handlers and tracks whether
the canary reaches a sink. Reports frame path (which frame sent the
message, which received it). Toggle "Generate automated messages" off to
see real origin vs. DOM Invader-injected origin.

### 3. Prototype pollution
Enable "Prototype Pollution" in Attack Types settings.

**Source detection**: injects `__proto__` payload into query string,
URL hash, and JSON web messages. Reports sources in Augmented DOM
("inSearch" = query string, etc.).

**Test**: click "Test" next to a source → new tab with injection applied
→ check `Object.prototype.testProperty` in console to confirm pollution.

**Scan for gadgets**: click "Scan for Gadgets" → new window, progress bar
→ DOM Invader tries every known prototype gadget name, waits for the
value to appear in a sink. Reports `{source, gadget, sink}` tuples.

**Exploit**: click "Exploit" → auto-combines source + gadget to produce
XSS payload (alert). Numbers in the report pair sources to gadgets.

**Iframe-per-technique mode**: runs each prototype pollution technique
(query, hash, JSON) in a separate iframe independently. Slower but
avoids breakage when one technique disrupts the page.

**Property scan granularity**: "Auto scale" on = faster but may miss
gadgets that throw exceptions. Disable to manually set properties-per-frame.

## Source/sink filtering
From general settings cog → turn off non-interesting sinks (`JSON.parse`,
`location`, etc.) to reduce noise. Configurable per-session.

## Configuration tips
- Turn off query / hash / JSON injection independently when a site breaks
  on specific injection points.
- Disable prototype pollution for most routine testing (can cause site
  breakage); enable only on suspected targets.
- Frame path column shows cross-frame message routing — useful for
  finding `postMessage` origin bypass where message flows
  `top → child → sink`.

## Limitations
- Only runs in Burp's embedded Chromium (not external browser).
- Prototype pollution scanning can break dynamically rendered pages if
  pollution causes an unhandled exception before all sinks are reached.
- Cannot auto-exploit prototype pollution gadgets that require
  user interaction (e.g., click to trigger innerHTML).

## References
- PortSwigger TV: "DOM Invader: Prototype Pollution" — Gareth Heyes
  (2022) — `wiki/sources/portswigger-tv/whisper/transcripts/GeqVMOUugqY_*.txt`
- PortSwigger TV: "Testing for prototype pollution with DOM Invader"
  — `wiki/sources/portswigger-tv/whisper/transcripts/xQ8poeX1_dI_*.txt`
- Related: [[shazzer-overview]], [[consuming-tags-and-hoisting]]
