---
title: Salesforce Apex `without sharing` + SOQL injection
slug: salesforce-apex-without-sharing
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/server-side, technique/saas, technique/salesforce, technique/soql-injection]
inbound: []
---

# Salesforce Apex `without sharing` + SOQL injection

## Pattern

Customer-written Apex classes that are Aura-enabled become server-side
RPC endpoints reachable via the Aura API. Two common developer mistakes
unlock data leakage even when object/field ACLs are otherwise tight:

1. **`without sharing` class context** — Apex defaults to `with sharing`
   only if the developer declares it; `without sharing` runs in system
   context and ignores the requesting user's row-level access. A
   community user calling a `without sharing` Apex method that queries
   `User` returns every user record in the org.
2. **SOQL injection** — user input concatenated into a SOQL query.
   SOQL is read-only (no DML), but a `LIKE`-clause injection with a
   wildcard `%` returns the entire table. Injecting in the `WHERE`
   clause can pivot field filters or chain via subqueries on related
   objects.

## Preconditions

- Custom Apex methods exposed via `@AuraEnabled`.
- At least one class declared `without sharing` OR a method that builds
  a dynamic SOQL string from a user-controlled parameter.

## Detection

- Pull the JS bundle of the community site; grep for `controller://`
  paths and method names.
- Read the `params` schema from the JS: identify parameters typed as
  strings.
- Send the standard Aura payload with the candidate Apex descriptor;
  vary the string parameter with SOQL meta-characters (`%`, `'`, `OR
  Id != null`) and observe response size / error.

## Triggering

SOQL `LIKE` injection (wildcard returns all rows):
```
params: { "searchTerm": "%" }
```
in Apex like:
```
String q = 'SELECT Id,Email FROM Contact WHERE Name LIKE \'%' + searchTerm + '%\'';
```
yields every Contact.

`without sharing` system-context dump — no injection needed, just call
the Aura-enabled method that internally `SELECT`s a sensitive table.

## Bypasses

- If sharing rules block direct `User` access, look for an Apex method
  that returns a wrapper DTO including `OwnerId` — chain to person
  records.
- Salesforce admin can deny `Run As System` via the `Apex Security` UI;
  in practice, almost no one toggles this.

## Seen in the wild

- {date: 2025-01-30, source: CT Ep 108} — Aaron Costello: standard part of
  every Salesforce community-site audit; pulls phone numbers, addresses
  in seconds when `without sharing` is present.

## References

- AppOmni Apex whitepaper — `without sharing` + SOQL injection
  examples
- enumerated.ie Salesforce post
- Critical Thinking Podcast Ep 108
- Related: [[salesforce-aura-object-enumeration]]
