---
title: Deterministic Prompt-Injection → XSS via Client-Side Feedback Loops
slug: deterministic-prompt-injection-feedback-loop
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
tags: [technique/dom-xss, technique/prompt-injection, technique/ai]
inbound: []
---

# Deterministic Prompt-Injection → XSS via Feedback Loops

## Problem this solves

An LLM-backed chatbot has a `?q=` parameter that fires a prompt
injection. The injection lands → XSS, but only **20–50% of the time**
because the model is non-deterministic. Triage clicks the PoC link
once, the injection doesn't fire, the report gets NM'd, the bounty
gets reduced. Some programs explicitly downgrade non-deterministic AI
exploits.

The trick: turn a probabilistic primitive into a **near-100%
deterministic** one by re-trying inside the same victim session until
the XSS callback is observed.

## Setup

1. Attacker page pops a **small window** for the victim (target).
2. Both windows must stay **in view** to dodge the cross-origin
   postMessage rate limit — the small attacker window stays in front
   (or beside) the victim window. Browsers tightly throttle
   postMessages from backgrounded windows; keeping both visible removes
   that bottleneck. (Technique originally surfaced in CTBB's Adobe
   hack-along.)
3. Attacker window sends the prompt-injection payload into the chatbot
   iframe.
4. Attacker window registers an XSS-callback listener (e.g.,
   `window.addEventListener('message', ...)` on a beacon).
5. Every **10 seconds**: if no callback observed, re-inject. With 3
   retries (30s on page), per-attempt P(success) ≥ 20% yields ≥ 95%
   cumulative.

## Back-reference problem

When the chatbot iframe fires the XSS in the *victim* window, the
victim window has no built-in handle to the *attacker* window. Two
ways to fix:

### (a) Mutual-opener (what the writeup used)

Make each window the `window.opener` of the other. There's a known
trick to do this — see the original writeup for the
`open()`-into-an-`<iframe>` dance.

### (b) `event.source` (simpler, recommended)

When the attacker window posts the injection into the chatbot iframe,
the chatbot's postMessage handler receives an `event` object with
`event.source` set to the **attacker window's `Window` reference**.
Register an event listener in the XSS payload that captures
`event.source` from the next incoming postMessage, then post results
back through it. No mutual-opener gymnastics needed.

## Confirmation signal

If the victim window receives a "ready" beacon from the attacker
window within `(retries × 10s)`, the chain is deterministic.

## Where this generalises

Any non-deterministic primitive in the victim browser:

- LLM-based features (chatbots, autosuggest, summarization).
- Race conditions (the same retry pattern lifts a 1-in-N race to a
  near-deterministic one — already covered by the `client-side
  feedback loop` framing).
- Server-side AI features rendered into a DOM sink (chat completions
  rendered as Markdown / HTML).

## Seen in the wild

- **2026-05 — Star Strike (starstrike.ai) writeup, "Achieving
  Deterministic Prompt Injection Through Client-Side Feedback Loops"**
  by XSS Doctor (XSS Doc) and Monke. Q-parameter prompt injection
  into a chatbot lifted from ~30% → near-100% deterministic via this
  pattern.
  Source: [CT Ep. 174](wiki://podcasts/ct/20260514_qi4dGzjDPI8_Saving_Bug_Bounty_Programs_+_AMPScript_tessl_GPT-5.5_Ep._174).

## Related

- [[../dom-xss/SUMMARY]]
- [[../dom-xss/coop-iframe-injection-bypass]]
- [[../dom-xss/coop-allow-popups-callback]] (popup-keep-in-front pattern)
