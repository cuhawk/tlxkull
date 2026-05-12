---
title: IDOR — summary
slug: idor-summary
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/idor, summary, index]
inbound: []
---

# IDOR — summary

## What this class is

Insecure Direct Object Reference (IDOR) occurs when an application uses a caller-supplied identifier (numeric ID, UUID, filename, email) to look up or modify an object without verifying that the authenticated user is authorized to access that specific object. The access control check is missing or server-side binding is broken, allowing horizontal (same-privilege cross-account) or vertical (lower-to-higher privilege) privilege escalation. IDORs are the most common critical finding in modern API-heavy SPAs and mobile backends.

## When to suspect

- API endpoints that accept `id`, `user_id`, `account_id`, `uuid`, `reference`, `doc_id`, or similar in path (`/api/v1/orders/12345`) or query param (`?invoice=abc-123`)
- Sequential or guessable numeric IDs (BOLA) — increment/decrement by 1
- UUIDs that appear in other users' shareable links or leaked in JS bundles
- Multi-tenant SaaS: `org_id`, `tenant_id`, `workspace_id` embedded in request body
- GraphQL: object resolvers where the query argument bypasses middleware auth
- File download endpoints: `?file=report_12345.pdf`, `?path=user/5/photo.jpg`
- `js_analyzer` source tags: any URL parameter, request body field, or local storage value passed to a fetch/XHR call without a visible ACL wrapper
- Endpoints that return `403` for one account but `200` for another on the same ID — fuzz with two accounts

## External references

| Topic | PayloadsAllTheThings path | HackTricks path | PortSwigger |
|---|---|---|---|
| IDOR techniques and checklist | `../../_external/payloads-all-the-things/Insecure Direct Object References/` | `../../_external/hacktricks/src/pentesting-web/idor.md` | [portswigger-access-control](../../sources/portswigger-access-control.md) |
| Access control / vertical escalation | — | — | [portswigger-access-control](../../sources/portswigger-access-control.md) |
| Account takeover chains | `../../_external/payloads-all-the-things/Account Takeover/` | `../../_external/hacktricks/src/pentesting-web/account-takeover.md` | — |
| Mass assignment (extends IDOR surface) | `../../_external/payloads-all-the-things/Mass Assignment/` | `../../_external/hacktricks/src/pentesting-web/mass-assignment-cwe-915.md` | — |
| Hidden parameters discovery | `../../_external/payloads-all-the-things/Hidden Parameters/` | — | — |
| Business logic errors | `../../_external/payloads-all-the-things/Business Logic Errors/` | — | — |

## Related local pages

- [Race Conditions SUMMARY](../race-conditions/SUMMARY.md) — race conditions can be chained with IDOR to double-spend or bypass one-time checks
- [OAuth SUMMARY](../oauth/SUMMARY.md) — OAuth misconfig can grant tokens that have IDOR access to other users' resources
- (none yet)

## Sub-patterns to expand

- [x] `horizontal-bola.md` — same-privilege cross-account object access
- [x] `vertical-idor.md` — user accessing admin-level object by ID
- [ ] `uuid-idor.md` — UUID IDs that are guessable or leaked in responses
- [ ] `graphql-bola.md` — GraphQL resolver missing per-object auth
- [ ] `file-download-idor.md` — filename/path param that traverses into other users' files
- [ ] `indirect-reference-idor.md` — hashed or encoded IDs that can be decoded/forged
- [ ] `mass-assignment-idor.md` — parameter pollution to set protected fields including owner ID
