---
title: Prototype Pollution — summary
slug: prototype-pollution-summary
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/prototype-pollution, summary, index]
inbound: []
---

# Prototype Pollution — summary

## What this class is

Prototype Pollution occurs when an attacker can inject properties into `Object.prototype` (or another base prototype) via a deep-merge, clone, or path-set operation that does not sanitize keys like `__proto__`, `constructor`, or `prototype`. Client-side PP can be chained with DOM XSS gadgets (e.g. polluting `innerHTML` used as a default elsewhere in the app). Server-side PP (Node.js) can lead to RCE via gadgets in popular packages (`lodash`, `qs`, `express`), privilege escalation, or DoS.

## When to suspect

- `js_analyzer` source tags: URL query params or fragment parsed with `qs.parse`, `JSON.parse` of untrusted input, `_.merge`, `_.defaultsDeep`, `$.extend(true, ...)`, `Object.assign` on untrusted keys
- Sink patterns (client): `document.createElement` config, template strings using polluted defaults, any code that reads `options.x || defaultOptions.x` where `defaultOptions` is a plain object
- Sink patterns (server): `child_process.spawn` / `exec` via polluted env, `require()` path resolution, express route handler options
- Deep-merge utility usage: `lodash.merge`, `lodash.defaultsDeep`, `deepmerge`, `extend`, `qs.parse` with default `allowPrototypes: false` not set
- URL shapes: query parameters that use bracket notation (`?a[__proto__][x]=1`) or JSON body with nested `__proto__` key
- Node.js apps: `npm ls lodash` — older versions are gadget-rich

## External references

| Topic | PayloadsAllTheThings path | HackTricks path | PortSwigger |
|---|---|---|---|
| Prototype pollution payloads | `../../_external/payloads-all-the-things/Prototype Pollution/` | `../../_external/hacktricks/src/pentesting-web/deserialization/nodejs-proto-prototype-pollution/` | [portswigger-prototype-pollution](../../sources/portswigger-prototype-pollution.md) |
| Client-side prototype pollution | `../../_external/payloads-all-the-things/Prototype Pollution/` | `../../_external/hacktricks/src/pentesting-web/deserialization/nodejs-proto-prototype-pollution/client-side-prototype-pollution.md` | [portswigger-prototype-pollution](../../sources/portswigger-prototype-pollution.md) |
| Express gadgets | — | `../../_external/hacktricks/src/pentesting-web/deserialization/nodejs-proto-prototype-pollution/express-prototype-pollution-gadgets.md` | — |
| PP to RCE | — | `../../_external/hacktricks/src/pentesting-web/deserialization/nodejs-proto-prototype-pollution/prototype-pollution-to-rce.md` | — |
| XSS via PP gadgets | `../../_external/payloads-all-the-things/XSS Injection/` | `../../_external/hacktricks/src/pentesting-web/xss-cross-site-scripting/dom-xss.md` | — |

## Related local pages

- [DOM XSS SUMMARY](../dom-xss/SUMMARY.md) — client-side PP gadgets commonly reach DOM XSS sinks
- [Server-Side SUMMARY](../server-side/SUMMARY.md) — server-side PP can chain to SSTI or RCE via gadgets
- (none yet)

## Sub-patterns to expand

- [x] `client-side-pp-gadget.md` — browser PP gadget scan and exploitation
- [ ] `server-side-pp-lodash.md` — lodash deep merge pollution
- [ ] `pp-to-dom-xss.md` — specific gadget chains from PP to innerHTML/eval
- [ ] `pp-to-rce.md` — Node.js PP gadgets leading to code execution
- [x] `qs-parse-pollution.md` — bracket-notation query string parsed by qs without protection
- [ ] `angular-pp-gadget.md` — Angular-specific PP gadgets
