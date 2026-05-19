---
title: Shazzer — browser fuzzer
slug: shazzer-overview
created_utc: 2026-05-19T00:00:00Z
updated_utc: 2026-05-19T00:00:00Z
tags: [tool/shazzer, tool/fuzzing, technique/dom-xss, technique/waf-bypass]
inbound: []
---

# Shazzer

Browser fuzzer built by Gareth Heyes (PortSwigger) for discovering XSS
vectors, browser parsing quirks, and WAF bypass opportunities.

## Purpose

- Cross-browser comparison of HTML/JS parsing behavior.
- Identify vectors that work in one browser but not others.
- Find filter/sanitizer bypasses by testing consuming-tag behavior and
  attribute parsing edge cases.
- Fuzz postMessage / webMessage origin-validation weaknesses.

## Fuzzing modes

### 1. Existing-behavior fuzzing
Takes known XSS vectors (from a built-in library) and tests them across
browsers to surface inconsistencies. Use case: "does this vector work in
Safari but not Chrome? Find the delta."

### 2. Novel fuzz
Generates random / mutated HTML fragments and runs them through the
browser parser to detect unexpected script execution or attribute parsing.
Surfaces entirely new vectors not in any existing database.

### 3. webMessage / postMessage fuzzing
Fuzzes `event.source` and `event.origin` validation logic in
`window.addEventListener('message', ...)` handlers. Targets:
- Missing `event.source` check (any window can spoof).
- `startsWith` / `includes` checks bypassable with
  `https://attacker.com?legitimate.origin.com`.
- `event.origin` spoofing via `null` origin (sandboxed iframe).

## Key findings from Heyes' research
- **Consuming-tag bypass**: tags like `<script>` "consume" following
  content, preventing sibling tags from being parsed. Shazzer found nested
  tag sequences where this behavior differs per browser, enabling filter
  bypass (see [[consuming-tags-and-hoisting]]).
- **webMessage origin bypass**: several real-world apps checked
  `event.origin` with `indexOf` rather than strict equality, bypassable
  with `https://legit.example.com.attacker.com`.
- **Attribute injection via exotic delimiters**: `<a href=` without quotes
  behaves differently in old Trident vs Blink when the value contains
  backtick or grave accent.

## Usage
Access at [shazzer.co.uk](https://shazzer.co.uk). Select a fuzz category,
run across target browsers (own machines or BrowserStack), export results
as CSV / HTML.

For WAF bypass: identify a vector Shazzer shows works in the target
browser but is not in common WAF signature databases. Cross-reference
against `payloads/xss/`.

## Integration in workflow
- During `dom-xss-hunt`: when a sink is confirmed but straight payloads
  are blocked, run Shazzer "existing-behavior" mode against the target
  browser to find browser-specific bypasses.
- During `browser-confirm` mock run: test postMessage handlers with
  Shazzer's webMessage mode against the mock backend.

## References
- PortSwigger TV: "Shazzer: A Tool for Finding XSS" — Gareth Heyes
  (2022) — `wiki/sources/portswigger-tv/whisper/transcripts/mLzxwmNoAI4_*.txt`
- Related: [[consuming-tags-and-hoisting]], [[dompurify-allowed-uri-regex-anchor]]
- People: [[gareth-heyes]]
