---
title: Ep 149 — DEFCON Breakdown - Wildcards, Passkeys and DOM-Clobbering and More
slug: ct-ep-149-defcon-breakdown
url: https://www.youtube.com/watch?v=XVb8U6Wcdjg
fetched_utc: 2026-05-14T00:00:00Z
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
kind: podcast
extracted: true
extract_model: claude-code-manual
tags: [source, podcast, ct, defcon, dom-clobbering, passkey, saml, android, ai, sso]
inbound: []
---

# Ep 149 — DEFCON Breakdown: Wildcards, Passkeys and DOM-Clobbering and More

Date: 2025-11-20
video_id: XVb8U6Wcdjg
Speakers: Justin Gardner (JG), Joseph Thacker (Rezo, co-host)

## Summary

Roundup of DEFCON-33 bug-bounty-relevant talks. JG opens with a CT Research
Lab micro-blog on Unicode surrogate → question-mark → Solr/Elasticsearch
wildcard. The bulk: XBOW's "PromptScan" architecture takeaways (cost
trajectory, vector-embedding dedup, model-rotation, scope-DNS), David Cash
& Rich Warren on zScaler/Netskope SAML & pre-auth config bugs, GraphQL
broken-object-property-level-authz field-study, WebAuthn passkey shimming
via XSS / malicious extension, Android intent TOCTOU launch-anywhere, the
Gemini-via-calendar-invite suggested-prompt + intent:// chain, and the
Hulk DOM-clobbering automated framework that landed ~500 zero-days across
webpack/rspack/vite/astro.

## Techniques extracted

- [[../../techniques/server-side/unicode-surrogate-wildcard]] — DC2A surrogate normalizes to `?` which is then interpreted as a wildcard by Solr/Elasticsearch.
- [[../../techniques/recon/saas-preauth-config-enum]] — multi-tenant SaaS often exposes a pre-auth config endpoint keyed on org name/id leaking internal hosts, routes, keys.
- [[../../techniques/saml/cross-tenant-signature-reuse]] — signed by a valid IdP, fields not bound to the consumer org — sign your own assertion in your own tenant, use it against a victim tenant.
- [[../../techniques/idor/graphql-bopla]] — broken object-property-level authz: object read allowed, sub-property (e.g. `password`, `mfaSecret`, `editorEmails`) leaked.
- [[../../techniques/dom-xss/webauthn-passkey-shim-via-xss]] — XSS shims `navigator.credentials.get/create` to either capture victim auth material or silently register an attacker-owned passkey.
- [[../../techniques/mobile/android-intent-toctou-launch-anywhere]] — TOCTOU between intent security check and intent launch; widened by oversized AndroidManifest forcing slow resolution.
- [[../../techniques/dom-xss/ai-suggested-prompt-injection-mirror]] — match the AI's expected response prefix (e.g. "Here are your events for the week") to maximize the chance prompt-injection lands in the trusted-prompt path.
- [[../../techniques/mobile/llm-browser-intent-uri-redirect]] — prompt-inject an AI chat to open an HTTP URL that 30x-redirects to `intent://` and the embedded browser auto-launches it.

## Tools mentioned

- [[../../tools/caido]] — Bevix `auth-swap` plugin (user-A / user-B session swap in replay).
- Hulk + `dom-clobbering-collection` (Jack-fromeast) — AST taint + payload synth.

## Quotes

> "Suggested prompts that the user can click — `summarize my day`, `what are my calendar events` — that's a better PoC if you can pwn that versus the user saying hello hi."
> — Joseph, on AI-app prompt-injection PoC fidelity.

> "Prompt injection to opening a URL and then swapping that URL via redirect to an intent URI. That is such a good idea."
> — JG, on the Gemini Android intent-launch chain.

> "They formalized DOM-clobbering: figured out exactly what things we can overwrite, hooked them, did taint analysis, built the AST tree and correlated to the HTML payload."
> — JG on the Hulk framework.

## Cross-links

- [[../README.md]]
- [[../extracts.md]]
