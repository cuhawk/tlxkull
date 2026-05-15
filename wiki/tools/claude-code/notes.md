---
title: Claude Code — Operational Gotchas + Skill-Authoring Notes
slug: tools-claude-code-notes
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
tags: [tool/claude-code, tool/ai, tool/agent]
inbound: []
---

# Claude Code — Operational Gotchas

Selective notes about Claude Code itself — pitfalls that are not
obvious from docs but affect every hack-bot setup that uses skills.

## Skill-frontmatter pitfalls (high-impact)

### `description:` is single-line by default

Markdown / YAML frontmatter does **not** treat `description: ...`
as a multi-line block. Anything you write on subsequent lines is
silently ignored by the Claude / Codex agent loaders. Only the first
line reaches the dispatch decision.

**Wrong** (only the first line is sent to the agent):

```yaml
description: This skill checks for IDOR.
  It walks every authenticated endpoint
  and replays each request with another user's cookie.
```

**Wrong** (some Markdown variants accept this, Claude Code does not):

```yaml
description: >
  This skill checks for IDOR.
  It walks every authenticated endpoint.
```

**Right** — block scalar with `>-`:

```yaml
description: >-
  This skill checks for IDOR.
  It walks every authenticated endpoint and replays each request
  with another user's cookie to surface broken-access-control.
```

The `>-` form is parsed correctly and the **entire description** is
passed to the agent's skill-dispatch prompt. Confirmed to massively
improve invocation accuracy on existing skills that had been silently
truncated.

### `snake_case` skill names invoke better than `camelCase`

Empirically (not documented) the agent matches skill names to the
user's request more reliably when the skill `name:` is `snake_case`.
Rename `myCoolSkill` → `my_cool_skill` if you're seeing low
invocation rate.

### The word `Claude` in a skill name is a poison pill

Skills with the word `Claude` (or `claude`) in the `name:` field
underperform — possibly tokenizer / reserved-token interference,
possibly a deliberate filter to prevent recursive self-reference.
Rename:

- `dm_other_claudes` → `dm_other_agents`
- `claude_bridge` → `agent_bridge`

Measured improvement in invocation rate after rename (rezo, CT Ep. 174).

## Training-data opt-out is per-machine / per-install

Disabling "use my data to improve Claude" on the web/console UI does
**not** automatically propagate to a Claude Code install on a fresh
VPS, container, or new dev machine. The setting lives in a local
config file that is created per install. If you scale Claude Code
across machines (CI runners, hack-bot fleet), audit the opt-out on
**every** machine.

**Organization-licensed accounts** are automatically excluded from
training data — preferred posture for hunters who don't want their
hack-bot sessions used as training data.

## Source

- [CT Ep. 174](wiki://podcasts/ct/20260514_qi4dGzjDPI8_Saving_Bug_Bounty_Programs_+_AMPScript_tessl_GPT-5.5_Ep._174)
  — frontmatter / naming / training-data gotchas (rezo + Justin
  Gardner).

## Related

- [[../codex/notes]] — sibling agent, mostly compatible skill format
