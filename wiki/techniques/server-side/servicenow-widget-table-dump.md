---
title: ServiceNow widget API arbitrary table dump
slug: servicenow-widget-table-dump
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/server-side, technique/saas, technique/servicenow]
inbound: []
---

# ServiceNow widget API arbitrary table dump

## Pattern

ServiceNow ships built-in "widgets" — Aura-style front-end components
backed by a Glide-record server method. Several widgets accept a
`table` (and optional column-filter) parameter at runtime and return
rows of that table when the requesting role has read access. The two
canonical record-data widgets are `simple_list` and `order_list`;
several knowledge-base widgets follow the same pattern for KB articles.

Customers misconfigure by:

- Leaving widgets public (default for some).
- Leaving Glide-record ACLs default on tables that should be locked
  (e.g. `sys_user`, `sys_user_grmember`, custom HR tables, knowledge
  bases).
- Storing secrets (API tokens, external-system credentials) inside
  knowledge-base article bodies because "no one knows the widget
  exists."

ServiceNow's 2023 hardening pushed a global default-deny for many of
the record-data widgets, but knowledge-base widgets are still
applicable, and many customers undid the hardening because their
public docs broke.

## Preconditions

- Target is a Service Portal deployment (paths like
  `/sp/?id=`, `*.service-now.com`).
- Widget endpoints reachable (default).
- At least one table with mis-set ACL.

## Detection

- Recon: search captured traffic for `/api/now/sp/widget` or
  `/api/now/table/<name>` against `service-now.com` hosts.
- Send the canonical widget payload (POST to
  `/api/now/sp/widget/<widget_id>` with JSON body including
  `table` and `query`) — see enumerated.ie posts for the exact bodies.
- Iterate a `table=` wordlist of common SN tables: `sys_user`,
  `incident`, `kb_knowledge`, `cmdb_ci`, plus any custom table names
  found in the UI bundle.

## Triggering

`simple_list` body (POST):
```json
{
  "id": "widget-simple-list",
  "table": "sys_user",
  "fields": "user_name,email,phone",
  "filter": "",
  "maximum_entries": 1000
}
```
KB widget body (POST):
```json
{
  "id": "widget-kb-article-listing",
  "table": "kb_knowledge",
  "filter": "active=true",
  "fields": "short_description,text"
}
```

## Bypasses

- After 2023 hardening, customers must flip a system property to expose
  widget data; many turned it on to restore broken docs.
- If the widget you found is blocked, try the `data_broker` UI Builder
  endpoints — same pattern, different surface.
- Default ACLs sometimes allow the `sys_dictionary` table — leak the
  full schema to find custom tables.

## Seen in the wild

- {date: 2025-01-30, source: CT Ep 108} — Aaron Costello: original disclosure
  led to ServiceNow pushing per-customer ACL fixes globally; KB widget
  disclosure separately yielded "millions of records" for one
  government-healthcare customer with API tokens embedded in articles.

## References

- enumerated.ie — ServiceNow widget posts (table data; KB)
- AppOmni research
- Critical Thinking Podcast Ep 108
- Related: [[salesforce-aura-object-enumeration]], [[power-pages-underscore-api]]
