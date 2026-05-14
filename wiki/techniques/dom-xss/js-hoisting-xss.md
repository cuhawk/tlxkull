---
title: JS hoisting XSS recovery for undefined-callable sinks
slug: js-hoisting-xss
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss]
inbound: []
---

# JS hoisting XSS — recover from undefined-call TypeError

## Pattern
Injection lands inside a script as `x.y(1, INJECTION)` where `x` is
undefined → engine TypeErrors before INJECTION runs. Inject a hoisted
function declaration to satisfy `x`.

```js
function x(){}; x.y(1, alert(1));
```

`function x(){}` declarations are hoisted (both declaration AND
initialization). `var x = function(){}` only hoists declaration → does
NOT work. After hoisting, `x.y` evaluates to `undefined`; engine parses
the argument list (executing `alert(1)`) **before** TypeErroring on the
`undefined()` call.

## Preconditions
- Injection point is inside `<script>` source where attacker controls one
  argument of a function call on an undefined symbol.
- Engine evaluates argument expressions before checking call target.

## Detection
- Trace reflected param into `<script>` body.
- Test: inject `console.log(1)` payload. If you see TypeError but NO log,
  the sink is pre-evaluation — hoisting will recover it.

## Triggering
Original sink:
```js
foo.bar(1, REFLECTED);
```

Inject:
```js
1)};function foo(){};foo.bar(1, alert(1)
```

Or, if injection point lets you append:
```js
;function foo(){};
```

## Bypasses
- `let`/`const` declarations are hoisted but in TDZ — they DON'T satisfy
  undefined references. Use `function`.

## Seen in the wild
- {date: 2023-07-06, target: client-side quirks} — Ep 26.
- {date: 2023-11-30, target: undisclosed} — Ep 47.
- {date: 2024-01-04, target: 2023 recap} — Ep 52.
- {date: 2023-11-30, source: CT Ep 47} — JG community-DM puzzle: injection at `x.y(1, INJ)` where neither `x` nor `y` defined; `function x(){};x.y(1, alert(1))` resolved by hoisting and argument-eval order.

## References
- Critical Thinking Podcast Eps 26, 47, 52
- MDN — Function declarations hoisting semantics
