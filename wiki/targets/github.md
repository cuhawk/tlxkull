---
title: GitHub
slug: github
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [target/github, platform/h1]
inbound: []
---

# GitHub

## Snapshot

GitHub is the world's largest code hosting platform (SaaS at github.com +
GitHub Enterprise). Bug bounty program on HackerOne: https://hackerone.com/github

## Scope quirks

- github.com (SaaS) and GitHub Enterprise Server are in scope.
- GitHub Security Lab: separate program for CodeQL queries that detect
  vulnerability patterns in open-source code — bounties paid per accepted query.
- GitHub Actions and workflow security are in scope.
- Source code of GitHub itself is not publicly available; testing requires
  GitHub Enterprise Server or researcher accounts.

## Auth quirks

- Free GitHub accounts available.
- Some attack chains require organization owner access (can create own org).
- Pull request and Actions testing requires forking public repos.

## Prior findings (from BBRE)

- ZipSlip: CodeQL query detecting ZIP path traversal (CVE pattern) in Java
  frameworks — $5,500 (GitHub Security Lab).
  [BBRE](https://www.youtube.com/watch?v=F95U912u7OQ)
- GitHub Actions PR base ref injection → secret theft via `pull_request_target` — $25,000.
  [BBRE](https://www.youtube.com/watch?v=xbSCRbfMOr4)
- GitHub Pages Jekyll/Kramdown YAML `input` option → Ruby require path traversal → RCE — $25,000.
  [BBRE](https://www.youtube.com/watch?v=Xb2RMtj9qTA) (William Bowling)
- CRLF injection + null byte → stored XSS → cache poisoning on GitHub — $35,000.
  [BBRE](https://www.youtube.com/watch?v=ZriCJNL6c-U)
- Web cache poisoning (GitHub + Firefox case study, James Kettle).
  [BBRE](https://www.youtube.com/watch?v=ZOBwQmfrIOM)
- GitHub Actions DoS via short commit hash reference infinite loop — TeddyCats.
  [BBRE](https://www.youtube.com/watch?v=a5rqWZAIJ2s)

## Sub-targets

- github.com — SaaS production
- GitHub Actions (`.github/workflows/`)
- GitHub Pages (Jekyll static site generation)
- GitHub Security Lab (CodeQL query submission)
- GitHub Enterprise Server
- GitHub API

## Notes

- GitHub Actions supply chain bugs are consistently high-value. Focus on
  `pull_request_target` + code checkout patterns.
- William Bowling has multiple GitHub write-ups; his blog is worth reading.

## Program stats / triage signal (2026-05)

Per the program's monthly transparency tweet, April 2026 looks like a
hackbot-slop collapse:

| Month | Reports | Hackers | Paid (USD) |
|-------|---------|---------|------------|
| Nov 2025 | 162 | — | $78k |
| Dec 2025 | 146 | — | $93k |
| Jan 2026 | 151 | — | $76k |
| Feb 2026 | 182 | — | $48k |
| Mar 2026 | 200 | — | $94k |
| **Apr 2026** | **325** | **226** | **$2,367** |

Read-out (Justin + Joel, CT Ep. 175): payout-per-report collapsed
because volume nearly doubled while the team's actual capacity to
triage didn't. The hypothesis is **not** that GitHub is stiffing
hunters — past months track a $50-90k/month baseline — but that the
backlog of payable reports is sitting unactioned. Long, professional-
looking AI-written reports are harder to weed than short bad ones.

Operational signal:

- Treat GitHub as a long-cycle program right now; pad expectations on
  payout speed.
- Reports describing CI-runner code execution that's actually the
  *researcher's* own runner config (not a GitHub-side bug) are a
  recurring noise pattern on this program. Triple-check before
  submitting any "RCE via Actions" finding.
- Shout-out to `towel` at Bugcrowd (Joel) — different program, same
  era — for grinding through volume; the same individual-triager-
  bottleneck pattern likely applies on the GitHub side too.

[CT Ep. 175](wiki://podcasts/ct/20260521_v-XhQHy_jHM_Rhyno_s_Hackbot_Setup_Sick_Bugs_and_ZDI_Drama_Ep._175)
