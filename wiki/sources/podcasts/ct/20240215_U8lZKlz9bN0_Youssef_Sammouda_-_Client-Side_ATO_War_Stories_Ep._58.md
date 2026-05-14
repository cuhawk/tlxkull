---
title: Ep 58 -- Youssef Sammouda -- Client-Side ATO War Stories
slug: ct-ep-58-youssef-sammouda-client-side-ato
url: https://www.youtube.com/watch?v=U8lZKlz9bN0
fetched_utc: 2026-05-14T00:00:00Z
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
kind: podcast
extracted: true
extract_model: claude-code-manual
tags: [source, podcast, ct, postmessage, ato, xs-leaks, math-random, message-channel, oauth, js-monitoring]
inbound: []
---

# Ep 58 -- Youssef Sammouda -- Client-Side ATO War Stories

- Date: 2024-02-15
- video_id: U8lZKlz9bN0
- Speakers: Justin Gardner (JG), Joel Margolis (JM), guest Youssef Sammouda

## Summary

Live interview with Meta-focused client-side ATO hunter Youssef Sammouda. Walks
through a postMessage async-origin-swap race on the Facebook Candy-Crush apps
sandbox where the OAuth token leaks to attacker.com because the responder
caches `targetOrigin` between the origin check and the network response; the
Facebook patch added a server-side lock and was bypassed by spamming 5MB
postMessages to widen the race. Covers a multi-step xs-leak using Chrome's
scroll-to-text-fragment (`#:~:text=`) plus an iframe-scroll propagation bug
that lets an iframed page leak whether a search-text exists in a cross-origin
DOM, plus charset/UTF-16 abuse to walk character-by-character through CSRF
tokens served as `text/plain`. Predicts a Math.random-derived chat-plugin
callback ID via cross-origin `iframe.name` reads on a page Frame-able due to
deprecated `X-Frame-Options: ALLOW-FROM`. Demonstrates postMessage's
two-argument-vs-options-object overload (`{targetOrigin:'...'}`) and
Transferable objects as primitives that bypass string-typed origin checks and
preserve object prototypes through transfer. Discusses MessageChannel ports
as a post-handshake trust path that skips origin checks entirely. Closes with
Yusuf's custom JS-monitoring pipeline that hashes per-function bodies (with
variable-name normalization) to diff Facebook React modules over time.

## Techniques extracted

- [[../../techniques/postmessage/async-origin-swap-race]] -- async postMessage RPC mutates targetOrigin between origin check and response; spam 5MB messages or oversized regex inputs to widen race; transferable + options-object smuggle past string check (Ep 58 was the original source of this page).
- [[../../techniques/xs-leaks/scroll-to-text-fragment]] -- Chrome STTF iframe-scroll leak + same-origin redirect-with-hash gadget + UTF-16 charset abuse for character-level CSRF-token exfil (Ep 58 was the original source).
- [[../../techniques/xs-leaks/math-random-prediction]] -- Facebook chat plugin iframe-name leaks Math.random; refresh via no-callback API to harvest samples; recover V8 xorshift128+ seed; predict callback ID for DOM XSS (Ep 58 was the original source).

## Tools mentioned

- PostMessage Tracker (Frans Rosen) -- used to enumerate `addEventListener('message')` handlers across all loaded frames.

## Quotes

> "I just send a lot of post-message requests, like a ton of them with each one with five megabytes... that did the trick."
> -- Yusuf, on bypassing Facebook's server-side lock added after his original race fix.

> "Chrome also scrolled the parent window. So I can have a confirmation if a word is found in the iframe or not."
> -- Yusuf, on the iframe -> parent scroll propagation that turned STTF into a cross-origin oracle.

> "You can do it from attacker.com window.opener.location.href and only change the hash. It won't work because if it's cross-origin domain, it would require each time to change user gesture."
> -- Yusuf, on the same-origin gadget requirement for STTF.

## Cross-links

- [[../README.md]]
- [[../extracts.md]]
