---
title: Horizontal BOLA — same-privilege cross-account object access
slug: horizontal-bola
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-19T00:00:00Z
tags: [technique/idor, technique/access-control, sink/unauthorized-read]
inbound: []
---

# Horizontal BOLA — same-privilege cross-account object access

## Pattern

An API endpoint accepts a caller-supplied object identifier (numeric ID, UUID, slug, filename) and returns or modifies the corresponding resource without verifying that the authenticated user owns or is authorized to access that specific object. A regular user can substitute another user's object ID to read or modify their data.

## Preconditions

- The endpoint accepts an object identifier in path, query param, or request body.
- Server-side authorization checks only that the caller is authenticated (valid session/token), not that they own the requested object.
- Object IDs are guessable, sequential, or leaked elsewhere (shared links, JS bundles, error messages).

## Detection

- Path parameters: `/api/v1/orders/12345`, `/users/456/profile`, `/invoices/abc-123`
- Query parameters: `?id=789`, `?account_id=101`, `?doc=report_5.pdf`
- Two-account test: register Account A and Account B; capture Account A's object IDs; access them authenticated as Account B — compare responses.
- PortSwigger canonical test: `https://insecure-website.com/myaccount?id=123` → change to `?id=456` — if you see another user's account, it's BOLA.
- `js_analyzer`: locate `fetch('/api/resource/' + userId)` or similar patterns where an ID from URL/storage flows into a sensitive fetch without visible ACL wrapper.

## Triggering

Direct ID substitution in URL path:
```
GET /api/v1/orders/12346 HTTP/1.1
Authorization: Bearer <attacker_token>
```
(Attacker increments victim's order ID by 1.)

Query parameter substitution:
```
GET /myaccount?id=456 HTTP/1.1
Cookie: session=attacker_session
```

UUID-based (leaked from shared link or JS):
```
GET /documents/550e8400-e29b-41d4-a716-446655440000/download HTTP/1.1
Authorization: Bearer <attacker_token>
```

Admin endpoint via role parameter:
```
GET /login/home.jsp?admin=true HTTP/1.1
GET /login/home.jsp?role=1 HTTP/1.1
```

## Bypasses

- Encoded / hashed IDs: decode Base64, reverse hash if weak (MD5 of integer), or brute-force small space.
- GUIDs: check if predictable (v1 UUIDs are time-based; v4 may be leaked in responses, logs, or Referer headers).
- Wildcard/glob IDs: try `*`, `%`, `../`, `.` as the ID value — some frameworks match unexpectedly.
- Header override: `X-Original-URL: /admin/deleteUser` or `X-Rewrite-URL: /admin/resource` — platform-level rewrite may bypass app-layer checks.
- HTTP method variation: endpoint restricts `POST` but not `GET` (or vice versa) on the same resource.
- Multi-tenant: try substituting `org_id`, `tenant_id`, `workspace_id` in the request body alongside a valid object ID.

## Seen-in-the-wild

- **2026-01-20 — Stripo AI Hub cross-tenant access via deleted project** (Stripo Inc / srcode, H1 #3459285, Critical, 137 votes): After deleting a project, associated campaign data remained accessible by other tenants by referencing the old project ID. Soft-delete didn't revoke authorisation checks on child resources. See [H1 #3459285](../../sources/hacktivity/3459285.md).
- **2026-05-19 — GitHub cross-repository IDOR in security_analysis/bypass** (GitHub / H1 #3592387, High): Settings endpoint accepted a repository identifier without validating org membership, exposing security analysis bypass settings across repositories. See [H1 #3592387](../../sources/hacktivity/3592387.md).
- **2024-07-xx — IDOR exposes PII of tens of thousands of users** (H1 #2967032, High, 92 votes): Direct object reference in a user listing endpoint returned supervisor PII by iterating numeric user IDs. See [H1 #2967032](../../sources/hacktivity/2967032.md).
- **2026-01-xx — Missing access control in MigrationFile allows upload to any workspace** (H1 #3506183, High): File upload endpoint accepted a `migration_file_id` without verifying the caller owned the target workspace. Classic BOLA on a resource-creation endpoint. See [H1 #3506183](../../sources/hacktivity/3506183.md).

## References

- [PortSwigger Access control vulnerabilities](../../sources/portswigger-access-control.md) — horizontal privilege escalation, IDOR sections
- [IDOR SUMMARY](SUMMARY.md)
