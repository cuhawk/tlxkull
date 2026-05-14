---
title: Ep 137 - How We Do AI-Assisted Whitebox Review, New CSPT
slug: 20250828-ai-assisted-whitebox-review-new-cspt-ep-137
url: https://www.youtube.com/watch?v=sTG-OX5BbBc
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
fetched_utc: 2026-05-14T00:00:00Z
kind: podcast
extracted: true
extract_model: claude-code-manual
tags: [source, podcast, ct, ai-whitebox, cspt, cache-deception, postmessage, slice, codeql]
inbound: []
---

# Ep 137 - How We Do AI-Assisted Whitebox Review, New CSPT

- Date: 2025-08-28
- video_id: sTG-OX5BbBc
- Speakers: Justin Gardner (JG), Joseph "rez0" Thacker (JT)

## Summary

Justin demonstrates an AI-assisted whitebox review workflow using Gemini
CLI on an SDK spot-check, finding a high/crit in under six hours. The
workflow: have the LLM index every file -> record business function +
primary functions + **security boundaries** -> cross-reference test files
to find what the team actually protects -> look for adjacent functions
missing those same controls. Jorge da Costa's CSPT-plus-cache-deception
chain extracts authenticated CSRF-token-bearing responses by forcing the
victim's browser to fetch `<endpoint>.css` (path-confusion-cached at the
CDN) and reading it back. Zlonser's Caido plugin "Ebka" wraps the Caido
GraphQL API behind MCP for Claude / GPT to drive the proxy. Caleb Gross's
"slice" tool combines CodeQL queries with LLM ranking to reproduce
discovered CVEs (Linux SMB driver, etc.). Side topic: a Google VRP $20K
finding by Jacob Domeraki on Code Assist where the `redirect_uri` page
used `origin` from a JSON state parameter to set a `postMessage`
`targetOrigin` validated only with `endsWith()` - client-side check, easy
bypass with `attacker.com/code-assist.google.com`.

## Techniques extracted

- [[../../techniques/dom-xss/cspt-cache-deception-chain]] - combine CSPT with CDN cache deception to extract responses with authenticated CSRF tokens.
- [[../../techniques/postmessage/endswith-target-origin-bypass]] - `event.origin.endsWith('victim.com')` is bypassable with `attacker.com/victim.com`; client-side post-message target-origin check.
- [[../../techniques/recon/ai-whitebox-source-review]] - repeatable LLM-driven SDK / source review process: index, identify security controls, look for adjacent missing controls.
- [[../../techniques/server-side/codeql-llm-ranking]] - Slice pattern: CodeQL discover -> LLM filter+rank for reproducibility on N-day CVE reproduction.

## Tools mentioned

- [[../../tools/tlx/ai-whitebox-workflow]] - Gemini.md / CLAUDE.md prompting patterns for SDK whitebox.
- [[../../tools/caido/notes]] - Ebka MCP plugin extends Caido to MCP-driven AI agents.

## Quotes

> "Have it look at the tests - what tests are validating a security control? That points you directly to what the team cares about."

> "Look at where security controls are implemented and then look at similar or adjacent functions that might be missing that same control."

> "He ran origin.endsWith('code-assist.google.com') on the client side - attacker.com/code-assist.google.com bypasses it. $20K from Google."

## Cross-links

- [[../README.md]]
- [[../extracts.md]]
