---
title: Ep 128 — New Research in Blind SSRF and Self-XSS and How to Architect Source-code Review AI Bots
slug: ct-ep-128-blind-ssrf-self-xss-source-code-ai
url: https://www.youtube.com/watch?v=jPN2GE-umJY
fetched_utc: 2026-05-14T00:00:00Z
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
kind: podcast
extracted: true
extract_model: claude-code-manual
tags: [source, podcast, ct, ssrf, self-xss, browser, ai-codereview]
inbound: []
---

# Ep 128 — New Research in Blind SSRF and Self-XSS and How to Architect Source-code Review AI Bots

Date: 2025-06-26
video_id: jPN2GE-umJY
Speakers: Justin Gardner (JG), Joseph Thacker (Joseph, guest co-host)

## Summary

Walks through Slonser's "Make Self-XSS Great Again" research (credentialless iframes
for one-step login-CSRF, CAPTCHA passthrough via WebSocket, the `fetchLater()` API as
a browser-persistence primitive). JG presents original research extending `fetchLater`
persistence to ~90 minutes via stalled 307 redirect loops at the max Chrome timeout.
Covers Shubs/AssetNote blind-SSRF-to-full-SSRF technique exploiting redirect-count vs
HTTP-status mismatch in a libcurl + application double-handler. Touches Chrome's
upcoming frame-busting intervention, the SOME-via-window.opener cross-tab pattern,
the Google URL bar font-ligature spoof, and Harishi's reverse-engineering methodology
for source-code review using Gemini-2.5-Pro long-context sub-agents driven by an
Opus-4 super-agent.

## Techniques extracted

- [[../../techniques/dom-xss/credentialless-iframe-login-csrf]] — credentialless iframes are same-origin with normal iframes; drop a login-CSRF in one to skip the logout step.
- [[../../techniques/dom-xss/captcha-passthrough-websocket]] — pipe the victim's CAPTCHA via WebSocket back to the attacker for solving in real-time.
- [[../../techniques/dom-xss/fetchlater-redirect-persistence]] — `fetchLater()` plus stalled 307 redirect chain extends in-browser persistence to ~90 minutes after tab close.
- [[../../techniques/server-side/blind-ssrf-redirect-count-status-leak]] — N+1 redirects trigger an application-layer 500 that exposes the full response a libcurl-layer 200 would have masked.
- [[../../techniques/dom-xss/url-bar-font-ligature-spoofing]] — Chrome URL-bar font ligatures render `G_LOGO_LIGATURE` codepoints as the Google logo glyphs, enabling URL spoofing.

## Tools mentioned

- [[../../tools/browser]] — frame-busting intervention RFC (Chrome top-level-navigation-from-iframe is going away).

## Quotes

> "Credentialless iframes are same-origin as regular iframes ... so the unauth dude can reach into the authenticated iframe and grab data out, which is super whack."
> — JG, ~00:02:00, on Slonser's primitive.

> "You set the timeout super long ... stall the HTTP response from your own server for the maximum amount of time Chrome can handle, which is like 300 seconds. And then you do that in a redirect loop 20 times. You can get up to an hour and a half."
> — JG, ~00:05:00, original research extending fetchLater persistence.

> "This isn't a single endpoint. It's actually something deeper. There's like a secondary context ... if there was a 500 error HTTP status code, then it would be a full HTTP response."
> — Joseph, ~00:11:00, summarizing Shubs's blind-SSRF technique.

## Cross-links

- [[../README.md]]
- [[../extracts.md]]
