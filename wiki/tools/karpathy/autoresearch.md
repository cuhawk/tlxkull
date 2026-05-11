---
title: Karpathy autoresearch — canonical reference
slug: karpathy-autoresearch
created_utc: 2026-05-11T00:00:00Z
updated_utc: 2026-05-11T00:00:00Z
tags: [tool/karpathy, pattern/loop, meta]
inbound: []
---

# Karpathy autoresearch — canonical reference

**Source:** https://github.com/karpathy/autoresearch

## Idea in one sentence
A framework for an AI agent to autonomously conduct machine-learning
research by iteratively modifying and testing training code, with a
fixed time budget per experiment.

## The three files
- `prepare.py` — fixed constants + one-time data init. Agents don't
  edit this.
- `train.py` — the model + optimizer + training loop. Agents
  actively edit this each iter.
- `program.md` — baseline instructions guiding agent behavior.
  Agents read this every iter.

## How it operates
Agent receives instructions to examine `program.md`, then
autonomously edits `train.py` to experiment with architectural
changes, hyperparameters, optimization strategies. Each experiment
runs for exactly 5 minutes wall-clock — guarantees fair comparison
across configs. Validation metric: bits-per-byte (lower = better).

## Design principles we adopted
1. **Single-file scope** — every iter writes to one append-only file
   (we write `targets/<name>/autoresearch.jsonl`, one line per iter).
2. **Fixed per-iter time budget** — 5 minutes default. Forces
   minimum-viable tests rather than rabbit-holes.
3. **~12 iters / hour, ~100 / overnight** — sets realistic
   expectations for the user about how long a loop should run.
4. **Reviewable** — the user can scroll the jsonl chronologically
   and see every hypothesis + test + verdict.

## How we adapted to bug bounty
- "Model architecture change" → "exploit hypothesis for a chain".
- "Training run" → "run a minimum-viable test" (mock_confirm |
  browser-confirm | caido-replay).
- "Validation metric" → "judge: would this be accepted by the
  triager?" (Opus single-shot judge).
- "Edit train.py" → "append one line to autoresearch.jsonl".

## Where it differs
- We don't fully autonomously rewrite `js_analyzer` internals. The
  loop *uses* the analyzer; it doesn't *modify* it. Karpathy's
  framework has the agent self-modify; ours has the agent operate
  fixed tools and learn through observation.
- The "metric" isn't a clean scalar. Verdict is `{TP, FP,
  undetermined}` plus a confidence. Judge picks the best of three
  hypotheses per chain.
