---
title: GraphQL Authorization Bypass — Field-Level and Object-Level Access Control Flaws
slug: graphql-authorization-bypass
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/server-side, technique/idor, technique/graphql, technique/authorization]
inbound: []
---

# GraphQL Authorization Bypass — Field-Level and Object-Level Access Control Flaws

## Pattern

GraphQL APIs expose a flexible query interface where clients specify exactly
which fields to return. Authorization is often implemented at the resolver
level, but common mistakes include:

1. **Missing field-level auth**: a type's root resolver checks object ownership,
   but sub-field resolvers (nested relations) do not — querying a nested object
   from a different user's record bypasses the check.
2. **IDOR via node ID**: global object IDs (base64-encoded `Type:id`) are
   guessable; if the `node(id: ...)` query doesn't check object ownership,
   any object is accessible.
3. **Batch query abuse**: issuing 100 aliases for different IDs in one query
   bypasses per-endpoint rate limits.
4. **Introspection leakage**: `__schema` and `__type` queries reveal all types,
   fields, and mutations — including undocumented admin mutations.
5. **Mutation authorization gap**: queries check auth but mutations to the same
   object do not (or vice versa).

The BBRE episode on GraphQL covered the pattern of querying nested relations
through a root object the attacker owns to read data from other users' objects
without authorization errors.

## Preconditions

- Application exposes a GraphQL API with user-owned objects.
- Authorization is implemented inconsistently across resolvers.
- At least one root query/resolver grants partial access that enables traversal.

## Detection

- Enable introspection (`__schema`); dump the full schema.
- Map all types and their relations; identify cross-user relations.
- Craft queries that traverse from an attacker-owned object into relations
  belonging to victim objects.
- Try `node(id: <base64("Type:victimId")>)` with any accessible ID.
- Look for batch alias support and whether rate limits apply per-alias.

## Triggering

```graphql
# Attacker owns Project 123; checks if member list of other projects is accessible
query {
  project(id: 456) {        # victim's project ID
    members {
      id
      email
      role
    }
  }
}

# Nested relation bypass
query {
  me {                      # returns attacker's user object (authorized)
    organization {          # follows relation to attacker's org
      allProjects {         # but returns ALL projects in the org, not just attacker's
        members { email }   # leaks all member emails
      }
    }
  }
}
```

## Seen in the wild

- 2021–2022 — Multiple programs. BBRE episode covered GraphQL authorization
  patterns as a class, citing cases where field-level auth gaps and IDOR via
  node IDs were found at HackerOne, GitLab, and Shopify-ecosystem targets.
  [BBRE](https://www.youtube.com/watch?v=9tNUPpB1gto)

## References

- InQL — Burp Suite GraphQL extension for schema enumeration and testing
- GraphQL Security Cheat Sheet (OWASP)
- See also: [../../idor/_index.md](../../idor/_index.md)
