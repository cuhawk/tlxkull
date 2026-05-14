---
title: AI-Assisted Whitebox Source Review Workflow
slug: ai-whitebox-source-review
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/recon, technique/whitebox, technique/ai]
inbound: []
---

# AI-Assisted Whitebox Source Review Workflow

## Pattern

Repeatable LLM-driven workflow to ingest an SDK / repo and surface
candidate vulnerabilities in hours instead of days. Justin Gardner used
Gemini CLI with Pro to find a high/crit in <6 hours on a HackerOne spot
check SDK. The same prompt pattern works with Claude Code, Cursor agent,
or any agentic CLI that can read every file in a tree.

The workflow is not "ask the LLM to find bugs" - it's structured indexing
that produces a code architecture document the human hacker then reads.

## Preconditions

- Access to the source (SDK, GitHub repo, decompiled app).
- An agentic LLM CLI: Claude Code, Gemini CLI, Cursor, or similar.
- A prompt file (`CLAUDE.md`, `GEMINI.md`) checked into the repo root.

## Detection / Application

The workflow itself is the deliverable; here is the four-pass structure
Justin uses:

### Pass 1 - per-file summary

For each file, have the LLM write:

1. **Business function** - what does this file do for the product?
2. **Primary functions** - bullet list of exported / public functions.
3. **Security boundaries** - what trust boundary does this file sit on
   (network, auth, IPC, file system, ORM)?

### Pass 2 - summary of summaries

Roll all per-file summaries into a single `ARCHITECTURE.md` that captures:
- Overall data flow.
- Core security components (auth, crypto, input validation, etc.).
- One sentence: "the security of this app hinges on function X in file Y."

### Pass 3 - test-file mining

Have the LLM read every test file and list which security controls have
tests against them. The presence of a test signals "this is what the team
cares about" - the inverse, security-relevant code lacking a test, is
often where bugs hide.

### Pass 4 - adjacent-function gap analysis

Have the LLM list every place a security control is invoked, then find
**adjacent or similar functions that omit the same control**. This is the
single highest-yield prompt - it pointed Justin directly to the
vulnerable function in his Ep 137 finding.

## Triggering

Example `GEMINI.md` skeleton:

```markdown
# SDK Whitebox Review

For each .py / .js / .go file under src/:
1. Summarize the business function.
2. List exported functions.
3. Identify security boundaries crossed (network, auth, FS, crypto).
4. Note any security control invoked (auth check, sanitizer, ACL).

Then write src/ARCHITECTURE.md covering: data flow, core security
components, the single "pivot" function security hinges on.

Then list every security control invocation and find functions that
share the call site / parent module but skip the control.
```

## Bypasses

Not applicable.

## Seen in the wild

- {date: 2025-08-28, source: CT Ep 137} - Justin Gardner used this exact workflow with Gemini Pro on an SDK spot-check; found high/crit in under 6 hours; the "adjacent functions missing the same control" pass was the discovery vector.

## References

- Critical Thinking Podcast Ep 137 - <https://www.youtube.com/watch?v=sTG-OX5BbBc>
- Daniel Miessler - Fabric / context-files pattern (referenced in episode).
- Related: [[codeql-llm-ranking]], [[threat-intel-creds-residential]]
