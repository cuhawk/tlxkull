---
title: Live Hacking Event (LHE) Workflow — Korea/Google 2026 Takeaways
slug: lhe-workflow
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [tool/karpathy, workflow, lhe]
inbound: []
---

# Live Hacking Event (LHE) Workflow

Distilled from CT Ep. 170 (Korea/Google back-to-back events, 2026).

## Claude Code + tmux for reverse shell / deep recon

When you have shell access (e.g. an intended reverse shell pivot or an RCE
chain), run the shell inside a named tmux pane and point Claude Code at it:

```bash
# In terminal: catch your shell in tmux pane 0 of session "hack"
tmux new-session -s hack
nc -lvnp 4444   # or whatever listener

# In Claude Code system prompt / task:
# "Use tmux send-keys to window hack:0 to run commands in the active shell."
```

Claude Code uses `tmux send-keys` under the hood to write into the pane and
`tmux capture-pane` to read output — giving it full interactive shell control
without any escaping or pipe issues.

**Caveats:**
- Speed gain is real; knowledge retention is lower (you are directing rather
  than executing). Budget extra time after the event to review what was found.
- Best used for multi-step post-exploitation or deep source analysis once an
  initial lead is established.

## protoscope for binary protobuf

Google uses binary protobuf widely. Without a schema, use protoscope:
→ See `../protoscope/notes.md` for the full workflow.

Caido integration: base64-encode the blob, add a base64-decode workflow step
in Caido so the binary arrives correctly in the request body.

## OAuth scope expansion on MCP / SDK integrations

Two classes of bug found at the Korea LHE on OAuth grants for MCP servers and
AI integrations:

1. **Scope expansion**: AI agent / MCP server takes actions outside the
   OAuth scopes explicitly granted during consent. The access token has
   `scope=calendar.read` but the server issues calls to `drive.write` or
   similar.
2. **Token pass-through / confused deputy**: Full-privilege user token is
   forwarded agent-to-agent (no scope reduction per hop). RFC 8693 token
   exchange aims to fix this, but targets are not yet compliant.

Test methodology:
1. Perform the OAuth consent flow; note checked scopes.
2. Observe what API calls the MCP server or SDK actually makes.
3. Compare requested scopes vs observed calls — any call outside declared
   scope is a finding.
4. Also test: does modifying the SDK's user-facing parameter (e.g. `userId`)
   cause a scope-expanding API call? SDK wrappers often pass parameters
   straight into REST paths without checking whether the resulting endpoint is
   in scope.

## SDK path traversal via user-supplied parameters

SDKs are often thin wrappers around REST APIs. If a user-supplied parameter
ends up in a URL path segment without sanitization:

```
// SDK call:
sdk.getUser({ userId: "../../organization" })
// → GET /api/users/../../organization
// → GET /api/organization  (if server path-normalizes)
```

Feed SDK code to Claude Code and ask specifically:
> "Find all places where a user-controlled SDK parameter is interpolated into
> a URL path or HTTP header without sanitization."

## Webhook architecture fuzzing

Webhooks are public endpoints by design. Commonly under-tested because of
perceived cryptographic complexity (HMAC signature on payload).

Claude Code removes the friction:

```
"Here is the webhook signature algorithm (HMAC-SHA256 over JSON body with key X).
Please compute the correct signature for this tampered payload body."
```

Then test:
- Is the signature actually verified? (skip it entirely)
- Is the JSON parsed before or after signature check? (JSON smuggling)
- Are hash-extension attacks viable on the signing scheme?
- Does changing the JSON structure change what gets processed downstream?

## Regression testing for AI features

AI chat features frequently regress because:
- New "render preview" or "fetch link" capabilities are added.
- Old exfiltration paths that were fixed become re-enabled when new rendering
  modes arrive.

Set a recurring reminder or a Claude Code script to re-run previously-found
AI prompt injection / exfiltration PoCs after every significant product
release from your target. Google AI VRP is paying well for regressions.

## Report quality (Google VRP-specific)

Google VRP triage team feedback (CT Ep. 170):
- **Write reports yourself** (or heavily curate AI output). AI slop buries
  valid findings.
- **Concise is a formal quality criterion**. One technique: after drafting,
  ask Claude "cut everything that isn't directly technical impact or
  reproduction step."
- **Video PoC is now table stakes**, not optional. Record immediately on
  discovery — even if you don't write the report yet.
- After a verbal agreement at the event that a bug is high/crit, **comment it
  on the report** immediately so there's a written trail.

## Sources

- CT Ep. 170: `../../sources/podcasts/ct/20260416_1hef7eS-GIk_Claude_Code_+_Tmux_Websockets_and_Other_Korea_LHE_Takeaways_Ep._170.en.vtt`
- Podcast: "Claude Code + Tmux, Websockets, and Other Korea LHE Takeaways (Ep. 170)" — <https://www.youtube.com/watch?v=1hef7eS-GIk>
