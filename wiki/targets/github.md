---
title: GitHub
slug: github
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
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
