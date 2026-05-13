---
title: postMessage async origin-swap race
slug: postmessage-async-origin-swap
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/postmessage, technique/race-condition]
inbound: []
---

# postMessage async origin-swap race

Yusuf Sammouda research — Facebook Candy-Crush → Instagram OAuth-token
leak.

## Pattern
Request-response RPC over postMessage: server-side checks `origin` once
for the request, then on response, the page posts back to whatever
`targetOrigin` variable currently holds. While the network request is in
flight, attacker sends a second postMessage that flips the cached
`targetOrigin` on the responder. When the OAuth-token response arrives
it's posted to attacker.com.

## Preconditions
- Target uses postMessage for cross-frame RPC.
- Responder caches origin/targetOrigin in mutable state.
- Network round-trip provides a race window (>50ms typical).

## Detection
- Map every postMessage handler with PostMessage Tracker (Frans Rosén).
- Look for handlers that asynchronously post a response after a fetch.
- Inspect handler source for mutable `targetOrigin` cache between request
  and response.

## Triggering

### Window the race
- Spam hundreds of 5MB postMessages — blocks event loop, widens window vs
  server-side lock (Yusuf's bypass of the original patch).
- Send oversized hash that takes regex non-trivial time to validate; in
  parallel re-trigger via own iframe 100K+ times client-side.

### Win deterministically
- Use CPU asymmetry: attacker substring-extracts (`str.substr(23,...)`)
  while competitor uses `JSON.parse` on deeply-nested payload — substring
  wins.

## Related primitives (also Yusuf, Ep 58)
- postMessage `targetOrigin` as options object `{targetOrigin:'https://x'}`
  smuggles past string-check `arguments[1] === '...'`.
- Transferable objects (ArrayBuffer, MessagePort, ReadableStream,
  ImageBitmap, RTCDataChannel) keep prototype — smuggle properties past
  `typeof === 'string'`.
- MessageChannel ports — one-shot, transferable cross-origin, post-handshake
  bypass all origin checks.
- Iframe-as-window-opener via specific navigation tricks.

## Seen in the wild
- Facebook Candy-Crush → Instagram OAuth-token leak.
- Multiple Meta-family ATO chains.
- Critical Thinking Podcast Ep 58.

## References
- Yusuf Sammouda — Meta postMessage race writeup
- Frans Rosén — PostMessage Tracker extension
- Critical Thinking Podcast Ep 58
- See also: [[scroll-to-text-fragment]], [[math-random-prediction]]
