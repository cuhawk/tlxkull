---
title: ORM / query-builder SQL injection
slug: orm-sqli
created_utc: 2026-05-19T00:00:00Z
updated_utc: 2026-05-19T00:00:00Z
tags: [technique/server-side, technique/sqli, sink/database]
inbound: []
---

# ORM / query-builder SQL injection

## Pattern

Modern ORMs (Django, ActiveRecord, Sequelize, Prisma) parameterise
values but still construct SQL operator/column fragments from developer-
or user-supplied strings. When an ORM allows a structural key (operator
name, column name, connector keyword) to come from user input without
allowlisting it, SQL injection occurs despite full value parameterisation
being in place.

Variants:
- **Connector injection** (Django Q): `_connector` attribute in `Q`
  objects flows unsanitised into `WHERE` clause SQL (`AND`/`OR`) via
  string formatting in `WhereNode.as_sql`, allowing arbitrary SQL
  fragments.
- **Column-type/alias injection**: ORM lets callers specify column type
  names or query aliases as strings; if not allowlisted, the string is
  interpolated into the query template.
- **FilteredRelation JOIN condition**: Django `FilteredRelation` field
  names used in `annotate()` were injected into JOIN ON clauses.
- **Raw query misuse**: Developers mix `.raw()` or `.extra()` with
  f-string/format() interpolation, defeating ORM protections.

## Preconditions

- User-controlled input reaches an ORM structural parameter (not just a
  value parameter bound via `?` / `%s`).
- The ORM version has not patched the specific structural injection
  vector — check the CVE list for the ORM version in use.

## Detection

- Look for ORM calls where a user-supplied dict key or object attribute
  becomes a query fragment: `Q(**user_data)`, `filter(**user_kwargs)`,
  `annotate(user_name=...)`.
- Static: grep for `Q(` / `.filter(` / `FilteredRelation` with
  non-constant first arguments.
- Fuzz `_connector` key in Q object payloads: `{"_connector": "OR 1=1--"}`.
- Error-based: send invalid SQL syntax; if the database error leaks,
  confirm injection point.

## Triggering

Django Q connector injection (CVE-2025-26263):
```python
# Attacker controls q_kwargs coming from JSON body
q = Q(**q_kwargs)   # q_kwargs = {"_connector": "OR 1=1-- "}
Model.objects.filter(q)
# → WHERE (... OR 1=1-- ...)
```

Nextcloud column-type injection:
```
POST /ocs/v2.php/apps/tables/api/1/columns
{"type": "text','injected'--"}
```

## Bypasses

- WAFs that only scan value parameters miss structural injection.
- ORM versions patched only specific vectors; test all structural params.

## Seen-in-the-wild

- **2025-11-06 — Django Q objects `_connector` injection** (Django / cyberstan, H1 #3335709, Critical, 75 votes): `WhereNode.as_sql` used unsafe string formatting for the connector keyword. Assigned CVE-2025-26263. Fixed in Django 4.2.x, 5.0.x, 5.1.x patch releases. See [H1 #3335709](../../sources/hacktivity/3335709.md).
- **2026-05-15 — Nextcloud column type parameter SQLi** (Nextcloud / suul, H1 #3462991, High, 52 votes): Column type name supplied to the Tables API was interpolated into a raw query fragment without allowlisting. See [H1 #3462991](../../sources/hacktivity/3462991.md).
- **2026-02-xx — Django FilteredRelation annotation SQLi** (Django, H1 #3417967, High, 82 votes): `FilteredRelation` alias used in `annotate()` was not validated, injecting into JOIN ON clause on PostgreSQL. See [H1 #3417967](../../sources/hacktivity/3417967.md).

## References

- [PortSwigger SQLi](https://portswigger.net/web-security/sql-injection)
- CVE-2025-26263 (Django Q connector)
- [[secondary-context-path-traversal]]
- [Server-side SUMMARY](SUMMARY.md)
