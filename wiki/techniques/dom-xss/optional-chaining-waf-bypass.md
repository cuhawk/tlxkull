---
title: Optional-Chaining `?.()` WAF Bypass
slug: optional-chaining-waf-bypass
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/waf-bypass, technique/syntax-trick]
inbound: []
---

# Optional-Chaining `?.()` WAF Bypass

## Pattern

JavaScript's optional-chaining operator `?.` is valid not only for
property access (`obj?.prop`) but also for **function calls**
(`fn?.(args)`). Many WAFs signature-match on `identifier(` as a function-
call indicator. Inserting `?.` between the identifier and the parenthesis
breaks that signature:

```js
alert(1)        // blocked
alert?.(1)      // common WAF misses this
```

Researcher: Johan Carlsson (publicly corrected Justin Gardner on Twitter
in May 2024 - "I'm surprised you're surprised, good sir").

## Preconditions

- Injection lands in a JavaScript context where the optional-chaining
  operator is valid (modern JS; ES2020+; not in JSON or strict CSP-eval
  contexts).
- WAF pattern uses `identifier(` or function-name-then-paren signature.

## Detection

- Send the same payload twice: once as `alert(1)`, once as `alert?.(1)`.
  A WAF block on the first and pass on the second confirms.

## Triggering

```html
<svg/onload=alert?.(1)>
<img src=x onerror=eval?.('al'+'ert(1)')>
```

Also chains with hex-escape and global-object obfuscation:

```js
window?.['ale'+'rt']?.(1)
```

## Bypasses

Not applicable - this is itself a bypass.

## Seen in the wild

- {date: 2024-05-30, source: CT Ep 73} - Johan Carlsson publicly demonstrated the technique; multiple WAFs (named in his Twitter thread) miss the operator.

## References

- MDN - optional chaining `?.` with function calls.
- Critical Thinking Podcast Ep 73 - <https://www.youtube.com/watch?v=uHOxsmdsXUA>
- Related: [[waf-bypass]], [[no-parens-jsonp-callback]]
