---
title: Electron ASAR Credential Leak (.env in packaged app)
slug: electron-asar-credential-leak
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/supply-chain, technique/electron, technique/secret-leak]
inbound: []
---

# Electron ASAR Credential Leak (.env in packaged app)

## Pattern

Electron desktop applications package their source code (HTML, CSS,
JavaScript, config files) into an ASAR archive. ASAR is a concatenation
format similar to `tar`, with no encryption or obfuscation. Despite
Electron's historical documentation falsely implying ASAR provides source-code
protection, any user can extract the archive in seconds using
`npx asar extract app.asar .`. If developers include `.env` files or
hard-coded API tokens in the bundle (a common mistake when local dev
configs are committed), those secrets are trivially readable.

## Preconditions

- Target ships an Electron (or similar bundled JS) desktop application.
- Source code is packaged inside an ASAR archive rather than compiled to
  native code.
- A `.env`, `config.js`, or similar credential-bearing file is present
  inside the bundle.

## Detection

1. Download the application's installer (DMG, EXE, AppImage).
2. Extract with `7z x installer.dmg` or equivalent.
3. Navigate to `Contents/Resources/` and run:
   ```
   npx asar extract app.asar .
   ```
4. Search for `.env`, `token`, `secret`, `api_key`, `GITHUB_TOKEN`, etc.
5. Validate any found credentials against their respective APIs.

## Triggering

- If a GitHub token is found, query the GitHub API to enumerate repository
  access: `curl -H "Authorization: token <TOKEN>" https://api.github.com/user/orgs`
- Confirm push access to private repositories of the owning company.

## Bypasses

N/A — this is a static extraction technique, no live exploitation needed.

## Seen in the wild

- 2021-09-26 — Shopify, $50,000. Third-party Electron app (not official Shopify)
  shipped with a developer's GitHub API token bundled in its ASAR archive.
  The token had push access to numerous Shopify private repositories, allowing
  backdoor code injection. Found accidentally by Augusto Zanellato while
  reverse-engineering the application to understand its features.
  [BBRE](https://www.youtube.com/watch?v=TOgIgD0KUVs)

## References

- Electron ASAR documentation — no confidentiality guarantee
- `npx asar` — official Electron archive tool
- See also: [dependency-confusion](../supply-chain/dependency-confusion.md)
