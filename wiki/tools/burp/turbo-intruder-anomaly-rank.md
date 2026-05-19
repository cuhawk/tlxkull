---
title: Turbo Intruder — Anomaly Rank
slug: turbo-intruder-anomaly-rank
created_utc: 2026-05-19T00:00:00Z
updated_utc: 2026-05-19T00:00:00Z
tags: [tool/burp, tool/turbo-intruder, technique/recon]
inbound: []
---

# Turbo Intruder — Anomaly Rank

## Purpose
After sending thousands of requests (directory brute-force, parameter
fuzzing, etc.), Anomaly Rank sorts the entire result table by how unique
each response is. The rarest responses surface at the top — without
manual column-sorting through thousands of rows.

## How it works
Local algorithm (no AI, no external calls) computes a uniqueness score
for each response across all received responses. Score is based on
statistical rarity of the response's properties (length, status code,
content fingerprint). High score = highly anomalous = interesting.

Burp sorts the Turbo Intruder result table by Anomaly Rank by default
when the attack finishes.

## Use cases
- **Directory/file brute-force**: instantly surfaces `/404 → 200`,
  `/error → 200`, different backend fingerprints, unusual response sizes.
- **Parameter fuzzing**: finds values that trigger different behavior
  (debug modes, error stacktraces, auth bypasses).
- **AI-assisted triage**: feed top 20 anomalous results to an LLM instead
  of all 3,000 — stays within context window, focuses AI on interesting
  cases.

## Usage
In a Turbo Intruder script, to sort by a different column instead:
```python
table.setorder("Response")
```
Anomaly Rank is the default; the above overrides it.

## Integration in workflow
- After `js-index` + directory brute of a target: run Turbo Intruder
  with a wordlist, let Anomaly Rank surface unusual paths.
- Before manual review: export top-20 anomalous results, paste into
  Claude/GPT for pattern analysis.

## References
- PortSwigger TV: "HTTP Anomaly Rank — a new Turbo Intruder feature"
  — James Kettle — `wiki/sources/portswigger-tv/whisper/transcripts/z92GobdN40Y_*.txt`
