---
title: JSONP callback CSP bypass
slug: jsonp-callback-csp-bypass
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/dom-xss, technique/csp-bypass]
inbound: []
---

# JSONP callback CSP bypass

## Pattern
When a CSP `script-src` allowlists a host that exposes a JSONP endpoint, the
endpoint becomes an arbitrary-JS execution sink under the trusted origin.
Two flavors:

1. **Full function-call callback** — endpoint reflects `?callback=FOO(arg)`
   verbatim into `<script>`-served response. Pass attacker JS as callback.
2. **No-parens dot-chain callback** — endpoint restricts callback to
   `[a-zA-Z.]`. Use a property-access chain ending in a callable (e.g.
   `opener.document.getElementById('approve').click`). Browser invokes the
   chained method; the JSONP-supplied JSON argument is ignored.

## Preconditions
- Target CSP allows a host that runs a JSONP endpoint (very common via
  `*.googleapis.com`, `accounts.google.com`, `youtube.com`, WordPress blogs
  reverse-proxied as `target.com/blog`).
- For dot-chain variant: a same-origin page in `window.opener` (after the
  attacker `window.open`s the target).

## Detection
- Google-dork `site:target.com inurl:callback`.
- Manually inspect every CDN/host listed in `script-src` for `?callback=`
  parameters.
- WordPress installations ship a JSONP endpoint vulnerable to the dot-chain
  by default — flag any `target.com/blog/` reverse-proxy.

## Triggering
Full call:
```
https://maps.googleapis.com/maps/api/.../path?callback=ATTACKER_FN()
```

No-parens dot-chain:
```html
<script>
  w = window.open('https://target.com/page-with-approve-button');
  setTimeout(()=>{
    location = 'https://wordpress-blog/wp-json/...?callback=' +
      'opener.document.querySelector(%22%23approve%22).click';
  }, 2000);
</script>
```

## Bypasses
- Callback chars restricted to alphanumeric + dot → use dot-chain only.
- Length capped → use short property names + `window.opener` shortcut.

## Seen in the wild
- {date: 2024-05-09, target: NahamCon eps content (general)} — Justin Gardner
  Ep 70 reference.
- {date: 2023-11-30, target: H1 LHE chain} — Ep 47 CSP research $70K (uses
  the iframe-without-CSP variant — see [[iframe-without-csp-proxy]]).

## References
- octagon.net "Bypassing CSP using WordPress by abusing same origin method
  execution"
- Wallarm 2018 CSP-bypass research
- Critical Thinking Podcast eps 47, 70
