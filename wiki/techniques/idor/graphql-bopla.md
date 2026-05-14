---
title: GraphQL Broken Object-Property-Level Authorization (BOPLA)
slug: graphql-bopla
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/idor, technique/graphql, technique/authz]
inbound: []
---

# GraphQL BOPLA — Broken Object-*Property*-Level Authorization

## Pattern
OWASP API Top-10 distinguishes **BOLA** (Broken Object-Level Auth — you
shouldn't see this whole object) from **BFLA** (Broken Function-Level
Auth — you shouldn't call this operation). DEFCON-33 GraphQL field study
spotlighted a third axis particularly common in GraphQL: **BOPLA**.

Auth allows fetching the `User` object (e.g. for the profile page) but
authorization is enforced object-wide — every field inside `User`
returns. Sensitive sub-properties (`password`, `mfaSecret`, `salt`,
`paymentMethodTokens`, internal `editorEmails`, `auditLogs`) leak
because the resolver authz check ran at `User` level, not per-field.

GraphQL hides this even better than REST because the client picks
which fields it wants — defenders rarely test all permutations.

## Preconditions
- Target uses GraphQL with object-level authz only.
- Resolver returns the underlying ORM row whole-cloth and lets the
  GraphQL schema filter visible fields.

## Detection
- Introspection-enabled? Walk every type's fields, then try fetching
  the sensitive-looking ones (`password`, `secret`, `key`, `internal*`,
  `audit*`, `*Token`) as a low-priv user.
- Compare admin-role response vs viewer-role response for the same
  object query — diff for fields only admins should see.
- Field study presenter found dating-app bugs by grep'ing for
  `password`, `private*`, `verified_phone` etc.

## Triggering
```graphql
query LeakUser($id: ID!) {
  user(id: $id) {
    id email
    password           # <-- BOPLA if resolver returns it
    mfa_secret
    audit_log { event ip }
  }
}
```

## Bypasses / hardening
- Per-field resolver authz: each sensitive field has its own
  `@auth(requires: ADMIN)` directive.
- Allow-list of low-priv fields, deny-by-default elsewhere.

## Seen in the wild
- {date: 2025-08, source: CT Ep 149} — DEFCON 33 GraphQL field study,
  dating-app target leaking property-level data.

## References
- DEFCON 33 — "Examining access control vulnerabilities in GraphQL"
- OWASP API Security Top 10 (BOLA, BFLA terminology)
- Critical Thinking Podcast Ep 149
- Related: [[horizontal-bola]], [[vertical-idor]]
