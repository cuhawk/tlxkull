---
title: Prototype pollution via qs.parse bracket notation
slug: qs-parse-pollution
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/prototype-pollution, sink/object-prototype]
inbound: []
---

# Prototype pollution via qs.parse bracket notation

## Pattern

The `qs` library (and similar query-string parsers) parse bracket-notation keys like `?a[__proto__][x]=y` into nested object structures. In versions prior to 6.7.3 (and without `allowPrototypes: false`), this allows an attacker to inject properties directly onto `Object.prototype` through the parsed result when it is subsequently merged into a plain object. Server-side use in Express apps is particularly dangerous.

## Preconditions

- The server or client uses `qs.parse()` (or equivalent: `querystring`, `URLSearchParams` under certain Node.js versions, hand-rolled parsers) on attacker-controlled query strings.
- The parsed result is passed to a merge or assign operation that propagates `__proto__` keys upward.
- A gadget exists downstream that reads a property from an object that inherits from `Object.prototype`.

## Detection

- `npm ls qs` — check for qs < 6.7.3 in the dependency tree
- Grep source for `qs.parse(` or `require('qs')` — check if `allowPrototypes: false` or `allowDots` is set
- Server-side: Express routes that accept query params and pass them into `Object.assign`, `_.merge`, `deepmerge`
- Probe: `GET /?__proto__[x]=injected` — check server response or subsequent requests for unexpected `x` property behavior

## Triggering

URL query string via `qs` bracket notation:
```
/?__proto__[x]=injected
/?a[__proto__][x]=injected
/?constructor[prototype][x]=injected
```

If the parsed object is merged into another plain object:
```javascript
const params = qs.parse(req.query); // { __proto__: { x: "injected" } }
const config = Object.assign({}, defaults, params); // pollutes Object.prototype.x
```

Resulting behavior: `({}).x === "injected"` for any plain object in the process.

## Bypasses

- `__proto__` key blocked in parser → use `constructor.prototype`: `?constructor[prototype][x]=y`
- Dot-notation parsers: `?__proto__.x=y` may work depending on parser implementation
- URL encoding: `%5F%5Fproto%5F%5F` may bypass string-based denylist on `__proto__`

## Seen-in-the-wild

(none yet)

## References

- [PortSwigger Prototype pollution](../../sources/portswigger-prototype-pollution.md)
- [Prototype Pollution SUMMARY](SUMMARY.md)
- [Client-side PP gadget](client-side-pp-gadget.md)
