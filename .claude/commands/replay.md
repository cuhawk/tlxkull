---
description: Re-run a Caido replay batch for a specific request id. Usage: /replay <request_id> [variant-spec-json].
argument-hint: "<request_id> [json]"
---

# /replay

Trigger `caido-replay` skill against a specific captured request:

1. Parse `$ARGUMENTS`: first token is `request_id`, remainder (if any)
   is a JSON variant-spec.
2. If no variant-spec, use the default spec from
   `.claude/skills/caido-replay/SKILL.md` (no-auth, user-B, method-swap,
   param-fuzz on first numeric/UUID/email param).
3. Invoke `caido-replay` skill with that input.
4. Print the summary of diffs (count of interesting variants, top 3
   with one-line evidence each).
5. Persisted output lives at
   `targets/<current>/caido/replays/<request_id>/diffs.json`.
