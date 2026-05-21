---
title: GitLab
slug: gitlab
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [target/gitlab, platform/h1, platform/gitlab-bugbounty]
inbound: []
---

# GitLab

## Snapshot

GitLab is a DevOps platform (SaaS at gitlab.com + self-hosted GitLab CE/EE).
Bug bounty program on HackerOne: https://hackerone.com/gitlab

## Scope quirks

- Both gitlab.com (SaaS) and self-hosted GitLab CE/EE installations are in scope.
- Researcher must have own GitLab instance for some attack chains (e.g., import/export,
  federation, SSRF via third-party integrations like Sentry).
- Many high-impact bugs require chaining with an import or integration feature that
  allows attacker-controlled server responses.

## Auth quirks

- Free GitLab.com accounts available for testing.
- Some attacks require group owner or admin privileges on own instance.
- "gitlab.com" is the production instance; use test instances when possible.

## Prior findings (from BBRE)

- DNS rebinding TOCTOU SSRF on `URLBlocker.validate` — $5,000.
  [BBRE](https://www.youtube.com/watch?v=R5WB8h7hkrU)
- DNS rebinding bypass via socket error in `getaddrinfo` — $3,500.
  [BBRE](https://www.youtube.com/watch?v=hozjuAej1mo)
- SSRF via Grafana open redirect → internal metadata — $12,000.
  [BBRE](https://www.youtube.com/watch?v=Uklsk1WZ2EU)
- ExifTool CVE-2021-22204 pre-auth RCE via image upload — $20,000.
  [BBRE](https://www.youtube.com/watch?v=YYLqzj5-N7w)
- Arbitrary file read via symlinks in TAR archive (group import) — $29,000.
  [BBRE](https://www.youtube.com/watch?v=GRDbs-MvDBA)
- Stored XSS → file read via `ReferenceDecorator` in markdown — $16,000.
  [BBRE](https://www.youtube.com/watch?v=5dneugeMSso)
- Client-side path traversal CSRF via Sentry error ID — significant bounty.
  [BBRE](https://www.youtube.com/watch?v=z27bkSMARA8)
- GitLab Analytics Dashboards SSRF (partial read + blind, Kubernetes integration) — Johan Carlsson.
  [BBRE](https://www.youtube.com/watch?v=YQ5ixykKnyY)

## Sub-targets

- gitlab.com — SaaS production
- Grafana integration endpoint
- Sentry integration (self-hosted Sentry as attacker-controlled server)
- Import/export functionality (ZIP/TAR archives)
- Repository migration between instances

## Notes

- GitLab's import/migration flows are historically a goldmine: they handle
  attacker-controlled archives, URLs, and API payloads.
- The Sentry integration client-side path traversal (CSPT) pattern: any
  integration that renders third-party data in a UI action is a CSPT candidate.
- Johan Carlsson (uaxcar) is the top GitLab bug bounty hunter (top 4 as of 2023).
  [See people/johan-carlsson.md](../people/johan-carlsson.md)
