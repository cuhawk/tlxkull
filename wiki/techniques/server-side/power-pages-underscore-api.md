---
title: Microsoft Power Pages `/_api/<table>` anonymous OData dump
slug: power-pages-underscore-api
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/server-side, technique/saas, technique/power-pages, technique/odata]
inbound: []
---

# Microsoft Power Pages `/_api/<table>` anonymous OData dump

## Pattern

Microsoft Power Pages (low-code Dataverse-backed sites, hosted at
`*.powerappsportals.com`, `*.microsoftcrmportals.com`, and US-gov
custom domains) exposes its OData feed on **two** paths:

- `/api/<table>` — authenticated OData feed (path without leading
  underscore).
- `/_api/<table>` — **anonymous-role OData feed** (path with leading
  underscore).

The underscore form serves rows of `<table>` to the anonymous role if
the customer has granted that role access. Configuring access requires
four UI steps (table-level, column-level, role-grant, record-filter),
and customers shortcut by wildcarding the column list — every column
of every made-public table becomes anonymously readable.

Error messages are diagnostic:

- `Resource not found` — table not exposed at all.
- `Wildcard is not supported` — table exposed, but caller must specify
  `$select=<column>`; brute-force per column.
- `You do not have sufficient permissions` — table exposed only to
  authenticated; sign up as the lowest privilege user and retry.

## Preconditions

- Target site hosts on `powerappsportals.com` /
  `microsoftcrmportals.com` / a Power Pages custom domain.
- Customer has misconfigured anonymous-role table-data access.

## Detection

- DNS / fingerprint by hostname; `/Account/Login` page returns Power
  Pages templating.
- Send `GET /_api/account?$select=name`.
- Iterate `<table>` with both built-in names (export schema from a
  free Power Pages developer tenant) and likely custom names
  (`<prefix>_<entity>` based on app branding).

## Triggering

```
GET /_api/contact?$select=firstname,lastname,emailaddress1,telephone1 HTTP/1.1
Host: target.powerappsportals.com
```

If wildcard error returns: brute-force columns via repeated
`$select=<candidate>` until non-error.

If "insufficient permissions": sign up at any signup form (force-browse
to `/signin` if missing from the nav) and retry with the resulting
auth cookie.

## Bypasses

- Custom-table prefix is per-tenant (e.g. `myco_account` instead of
  `account`); harvest by reading the bundled JS that references the
  embedded entities.
- `/_services/<service>` — secret path for custom server-side service
  endpoints; same anonymous-role concern.
- `/_layout/<template>` — load custom HTML templates; potential SSRF /
  XSS surface.

## Seen in the wild

- {date: 2025-01-30, source: CT Ep 108} — Aaron Costello: NHS-UK leaked over 1
  million records via `/_api`; pattern same as Salesforce / ServiceNow
  research — public default + customer misconfig.

## References

- AppOmni Power Pages writeup (2024)
- Microsoft Power Pages documentation — `/_api` Web API
- Critical Thinking Podcast Ep 108
- Related: [[servicenow-widget-table-dump]], [[salesforce-aura-object-enumeration]]
