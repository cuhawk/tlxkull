---
title: Ep 150 — ASP.NET MVC Patterns, Popping Oracle Identity, and Esoteric Subdomain Enumeration
slug: 20251127-aspnet-mvc-oracle-identity-subdomain-enumeration-ep-150
url: https://www.youtube.com/watch?v=VjuU6uDdwL4
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
fetched_utc: 2026-05-14T00:00:00Z
kind: podcast
extracted: true
extract_model: claude-code-manual
tags: [source, podcast, ct, aspnet-mvc, oracle, java, recon, dns, subdomain-enum, csv-injection, google-docs, cloudflare]
inbound: []
---

# Ep 150 — ASP.NET MVC Patterns, Popping Oracle Identity, and Esoteric Subdomain Enumeration

- Date: 2025-11-27
- video_id: VjuU6uDdwL4
- Speakers: Justin Gardner (JG), Joseph Thacker / rez0 (JT)

## Summary

Five disjoint research items rolled into one episode. (1) Searchlight
Cyber's pre-auth RCE in Oracle Identity Manager (CVE-2025-61757): central
servlet auth filter with a "let waddle through" rule, bypass with
`<route>;.waddle` Java path-parameter; landing on a Groovy compile-error
endpoint that nominally only reports errors, but custom Java annotations
fire at *compile time*, giving RCE. (2) CloudFlare cache-key header
overflow (94+ headers exceeds the 100-header cache-key window, lets
attacker smuggle an `X-HTTP-Method-Override` past the cache-key boundary
and poison cached responses with that override). (3) Google Docs CSV
`IMPORTHTML` exfil for blind XSS replacement — payload sprayed at
public Salesforce/HubSpot forms, surfaces months later when Zapier-style
automation imports the row into Google Sheets that an employee opens.
(4) FSI's CTBB-research-lab post on ASP.NET MVC view-engine path patterns:
the framework reads a default `Views/<Controller>/<Action>.cshtml` (and
several variants) based on the request path; an arbitrary file-write
gadget that targets one of those default paths gives code exec even when
the configured allow-list permits only "no-extension" files. (5) DNS
subdomain enumeration deep cuts — ENTs (empty non-terminals / NOERROR
with descendants) tell you a node has children worth fuzzing, NSEC zone
walking + the NSEC3 hashed variant (use `nsec3map` to crack), and the
ICANN CZDS (Centralized Zone Data Service) for zone-file requests for
participating TLDs (great for obscure ccTLDs). Final tangent: AI tooling
(Gemini 3 free in `aistudio.google.com`, Anti-Gravity rebranded
Windsurf-IP, "heretic" repo that strips safety alignment from open
weights for security research).

## Techniques extracted

- [[../../techniques/server-side/oracle-identity-waddle-bypass]] — Oracle Identity Manager pre-auth RCE: Java path-parameter `;.waddle` bypasses a central filter; lands on Groovy compile endpoint where Java annotations execute at compile time. CVE-2025-61757.
- [[../../techniques/server-side/cloudflare-cache-key-header-overflow]] — submit 94+ headers to push attacker-controlled headers past the 100-header cache-key window; cache stores the poisoned response keyed on the prefix headers only.
- [[../../techniques/dom-xss/google-docs-importhtml-csv-injection]] — sprayed `=IMPORTHTML(...)` blind injection through public forms; surfaces months later when Zapier/Workato auto-imports the row into Google Sheets and an employee opens the spreadsheet.
- [[../../techniques/server-side/aspnet-mvc-view-engine-path]] — arbitrary file-write that lands the file at a path the ASP.NET MVC view engine reads by default (`/Views/<Controller>/<Action>.cshtml`); even strict web.config allow-lists for "no-extension files" still hit because cshtml is read implicitly.
- [[../../techniques/recon/dns-ents-zone-walk]] — DNS subdomain-enum deep cuts: ENT NOERROR-with-descendants, NSEC zone walking, NSEC3 hashed-name cracking via nsec3map, ICANN CZDS for zone-file requests.

## Tools mentioned

(none with novel quirks beyond the technique pages)

## Quotes

> "Java comes to the rescue with path parameters — so they were able to just do semicolon dot waddle and then get RCE."

> "Java annotations are processed at compile time — even though the code wasn't actually run, the annotation that they defined was being run at compile time."

> "Underscore as a prefix is the secret path" — context-shift quote on `/_api` style misconfigurations, applied here to `/cdn-cgi`, ASP.NET internal routes, and Power Pages anonymous OData.

## Cross-links

- [[../README.md]]
- [[../extracts.md]]
