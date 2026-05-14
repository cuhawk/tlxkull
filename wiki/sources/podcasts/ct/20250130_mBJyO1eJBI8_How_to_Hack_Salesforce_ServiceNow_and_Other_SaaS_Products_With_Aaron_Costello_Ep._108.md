---
title: Ep 108 — How to Hack Salesforce, ServiceNow and Other SaaS Products with Aaron Costello
slug: 20250130-how-to-hack-salesforce-servicenow-saas-aaron-costello-ep-108
url: https://www.youtube.com/watch?v=mBJyO1eJBI8
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
fetched_utc: 2026-05-14T00:00:00Z
kind: podcast
extracted: true
extract_model: claude-code-manual
tags: [source, podcast, ct, salesforce, servicenow, power-pages, saas, misconfiguration, aura, apex, soql]
inbound: []
---

# Ep 108 — How to Hack Salesforce, ServiceNow and Other SaaS Products with Aaron Costello

- Date: 2025-01-30
- video_id: mBJyO1eJBI8
- Speakers: Justin Gardner (JG), Joseph Thacker (rez0), Aaron Costello (guest, AppOmni / enumerated.ie)

## Summary

Aaron Costello's full SaaS misconfiguration playbook. Three platforms, one
pattern: a public-by-design API + customer-managed access controls that are
trivially mis-set + a stable cross-tenant payload that works for years. On
Salesforce, the Aura API (`/s/sfsites/aura`, `/aura`) accepts a fixed two-payload
glossary to enumerate objects then dump records when access-controls are wide;
custom Apex classes pair Aura-enabled methods with insecure `without sharing`
context and SOQL injection in `LIKE`-clause inputs. On ServiceNow, the
`simple_list` / `order_list` widgets dump arbitrary tables when widget ACLs are
default; the related knowledge-base widgets still work after the 2023 server-side
hardening. On Microsoft Power Pages, the *underscore-prefixed* `/_api/<table>`
path serves the anonymous OData feed; customers misconfigure by wildcarding
columns and granting the anonymous role on every table. Costello's
"signup-as-community-user" pivot — register through any public Salesforce
Lightning community to gain Apex execution under the named-credential context,
then brute-force credential names against the external system. Sandbox / data-broker
endpoints in ServiceNow UI Builder are the next undisclosed surface. Bonus: a
Salesforce file-attachment chain abusing App Cache manifest fallback +
cookie-bombing to deny the original asset and redirect a support engineer's
browser through an attacker-controlled HTML page that exfils the signed CDN key.

## Techniques extracted

- [[../../techniques/server-side/salesforce-aura-object-enumeration]] — fixed Aura API payload pair enumerates objects then dumps records when access-controls are mis-set.
- [[../../techniques/server-side/salesforce-apex-without-sharing]] — Aura-enabled custom Apex methods running `without sharing` ignore the requesting user's row-level ACLs; SOQL `LIKE` injection in user input opens partial-data exfiltration.
- [[../../techniques/server-side/salesforce-named-credential-bruteforce]] — community-user signup unlocks `execute anonymous` Apex; brute-force the named-credential label to reuse admin-stored API credentials against arbitrary external paths.
- [[../../techniques/server-side/servicenow-widget-table-dump]] — `simple_list` / `order_list` and knowledge-base widgets accept a `table` + `column` parameter; default access controls leak users, KB articles, embedded API tokens.
- [[../../techniques/server-side/power-pages-underscore-api]] — `/_api/<table>` (underscore = anonymous OData feed) enumerable by error-message signature; wildcarded column exposure leaks PII across thousands of tenants.
- [[../../techniques/dom-xss/appcache-cookie-bomb-chain]] — App Cache manifest `FALLBACK:` + cookie-bombing makes the original asset inaccessible, forcing the browser to serve the attacker's fallback HTML which exfils the next-clicked file's signed CDN URL.

## Tools mentioned

- [[../../tools/caido/notes]] — search captured projects for `/aura`, `/s/sfsites`, `powerappsportals.com`, `microsoftcrmportals.com` to fingerprint targets.

## Quotes

> "Legacy is where the gold is — let's not forget the stuff that's been sitting there 10, 15 years."

> "Signup as a community user — you get extra privileges just by signing up. And now you can run Apex in your user context."

> "Slash api with no underscore is the authenticated one. Underscore as a prefix is the secret path."

## Cross-links

- [[../README.md]]
- [[../extracts.md]]
