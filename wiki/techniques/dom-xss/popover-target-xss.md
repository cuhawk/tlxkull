---
title: Popover-target attribute XSS on arbitrary tags
slug: popover-target-xss
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/event-handler, technique/waf-bypass]
inbound: []
---

# Popover-target attribute XSS

## Pattern

Chrome's `popover` API (shipped 2023) adds the `popovertarget="<id>"`
attribute. Setting it on any element turns the element into a click
trigger for the target popover -- including elements that are not natively
clickable and have no event handler. The target element can be hidden or
disabled; it's still resolved by id. The button click invokes the
popover machinery which fires JS handlers / `:popover-open` CSS / `toggle`
events on the target.

Two attack shapes:

1. **New universal click sink.** `<x popovertarget=p>click</x>` makes
   `<x>` a click target even though `<x>` is not a real HTML element.
   Combined with a `<input type=hidden id=p toggle...>` style target, you
   smuggle JS execution through tags a sanitizer treats as inert.
2. **Equals-equals attribute confusion.** Saurush's payload
   `<button popovertarget=="..."` uses two `=` signs -- the first defines
   the attribute, the second is the attribute value (so the attribute name
   is `popovertarget` with value `=`), and the `<input id="==<!--">` pairs
   up. Regex-based WAFs / HTML sanitizers that look for `attr="..."` miss
   the second `=` as the quote opener and skip into what looks like an
   HTML comment.

## Preconditions

- Modern Chrome (popover API behind no flag since v114).
- HTML injection where you can place attributes on at least one element
  and reference a sibling element by id.
- Often requires one or two clicks -- model as click-jacking-style PoC for
  triage credit.

## Detection

- Try `<x popovertarget=p>X</x><x id=p popover onbeforetoggle=alert(1)>`
  inside the injection -- does X become clickable?
- Burp Match-and-Replace `popovertarget=` to "x=" to see if sanitizers
  even recognise the attribute.

## Triggering

```html
<button popovertarget="p">click me</button>
<div id="p" popover ontoggle="alert(1)">x</div>
```

Hidden-element variant (Cure53 follow-up):
```html
<button popovertarget="p">click</button>
<input id="p" popover hidden ontoggle="alert(1)">
```

Equals-equals WAF bypass (Saurush):
```html
<button popovertarget=="><input id="==<!--" popover ontoggle=alert(1)>
```

## Bypasses

- Chrome was the only browser shipping popover at the time of Ep 26
  (2023-07); Firefox/Safari payloads need separate research.
- Two-click impact: pair with a plausible UX (cookie-consent overlay,
  GDPR-prompt double-click) to argue full PoC.

## Related

- [[event-handler-matrix]]
- [[base-tag-anywhere]]
- [[waf-bypass]]

## Seen in the wild

- {date: 2023-07-06, source: CT Ep 26} -- "Don't forget about the magical
  popovertarget attribute which can make any HTML element clickable."

## References

- Critical Thinking Podcast Ep 26
- PortSwigger Research -- popover attribute XSS tweet (2023-06)
- Cure53 follow-up -- disabled/hidden target element trick
- Saurush -- popovertarget== WAF-bypass payload variant
