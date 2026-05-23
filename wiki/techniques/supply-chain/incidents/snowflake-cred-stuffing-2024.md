---
title: Snowflake credential-stuffing wave (Apr-May 2024)
slug: snowflake-cred-stuffing-2024
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, surface/cloud-warehouse, technique/info-stealer, technique/credential-stuffing, technique/mfa-not-enforced, actor/unc5537]
inbound: []
---

# Snowflake credential-stuffing wave (Apr-May 2024)

## What happened

Between 2024-04-14 and roughly 2024-05-23 the financially-motivated
actor **UNC5537** (Mandiant) systematically logged into Snowflake
customer tenants using credentials harvested from **info-stealer
logs** dating back as far as November 2020. ~165 Snowflake customer
tenants were accessed -- the only common factor was that none of
those tenants enforced MFA, and Snowflake at the time did not
*require* MFA on the tenant. Stolen data shipped from compromised
tenants showed up for sale within days on hacking forums:
**Ticketmaster (560M records)**, **Santander**, **AT&T (110M call /
SMS records, paid for deletion at ~$370K)**, **Advance Auto Parts**,
**Neiman Marcus**, **LendingTree**, **Bausch Health**, and others.

The credentials themselves came overwhelmingly from contractor and
non-employee laptops infected by Lumma, Vidar, Risepro, Redline, and
Racoon stealers. The same Snowflake tenant credentials had often sat
in `cloud.txt` / `corporate.txt` dumps for years without rotation;
in many cases the employee whose laptop was infected no longer
worked at the victim org. Mandiant's June 10 report established
"info-stealer marketplaces as enterprise-breach precursor" as a
named, recurring kill chain.

## Attack chain

1. **Info-stealer infection on a non-corporate laptop.** A
   contractor or personal device runs a cracked installer / pirated
   game / fake browser extension carrying Lumma/Vidar/Redline. The
   stealer scrapes browser-stored credentials, including Snowflake
   `https://<orgid>.snowflakecomputing.com/`.
2. **Logs uploaded to a stealer-as-a-service C2.** The credential
   triplet `(URL, username, password)` is sorted and indexed by URL
   pattern on the C2. Snowflake URLs are easy to filter -- they share
   a domain suffix.
3. **Resale on stealer marketplaces.** Aggregators (Russian Market,
   2easy, Genesis Market historically) re-sell filtered logs. UNC5537
   bought / scraped Snowflake-tagged credentials in bulk.
4. **Login.** Snowflake's authentication accepted username + password
   with no second factor for tenants that had not opt-in enabled MFA.
   No IP-allowlist, no device-cert binding by default. UNC5537 used
   the `SnowSight` console and `SNOWFLAKE` Python connector from
   commodity VPS exit nodes.
5. **Bulk export.** Once authenticated, the actor ran `COPY INTO
   's3://...'` or `GET @stage` to ship tables to attacker-controlled
   buckets. Often megabytes-to-petabytes within hours; victims with
   query-cost limits noticed -- those without (most) did not.
6. **Extortion / sale.** Data sold on BreachForums (Ticketmaster) or
   ransomed to the victim directly (AT&T paid).

## Lessons for bug hunters

- **Info-stealer logs are public OSINT for attribution and recon.**
  As a hunter, you cannot use them to log in, but you *can* search
  free stealer-log indices (HudsonRock free tier, IntelX free
  endpoints, public Russian Market dumps) to demonstrate that a
  target's employees appear in known stealer corpora. A "your CFO's
  Snowflake session cookie is publicly indexed" report is paid.
  Confirm scope-permissive use first.
- **MFA-not-required != MFA-disabled.** The Snowflake wave hit
  because MFA was *optionally configurable*. When auditing a SaaS
  target, look for any tenant-admin-controlled toggle for second
  factor. If MFA is opt-in, document the per-tenant percentage
  that hasn't opted in -- that's the breach surface size.
- **Stale credentials in browser stores.** A user-controlled `chrome
  password export` is reachable from any LPE/RCE on the workstation
  *and* from any rogue browser extension. When chaining a low-impact
  XSS in a web product to "credential exposure", remember the
  victim's browser is full of *other* products' credentials too.
- **Cloud-warehouse exfil cost is a defender's blindspot.** Snowflake
  bills per-credit; an attacker running unauthorized `COPY INTO`
  burns compute credits whose anomalous pattern is detectable. Any
  target's billing dashboard is a "free" audit log many defenders
  forget about.
- **Contractor laptops are part of scope.** The infected machine
  often belongs to a vendor or ex-employee. Programs with mature
  SCOPE include "credentials owned by anyone who can reach our SaaS
  tenants" -- worth confirming with the vendor's PSIRT. See
  [[okta-lapsus]] for the same lesson in IdP-shaped form.

## Primary sources

- [Mandiant: UNC5537 Targets Snowflake Customer Instances for Data Theft and Extortion](https://cloud.google.com/blog/topics/threat-intelligence/unc5537-snowflake-data-theft-extortion)
  -- Mandiant's June 10 2024 report with the 79.7% info-stealer
  attribution figure and the actor tradecraft.
- [Snowflake: Detecting and Preventing Unauthorized User Access (2024-06-02 advisory)](https://www.snowflake.com/en/blog/detecting-and-preventing-unauthorized-user-access-threats/)
  -- Snowflake's own incident page with IoCs and the post-incident
  enforcement-policy roadmap.

## Related

- [[okta-lapsus]]
- [[oktapus-twilio]]
- [[ms-storm-0558]]
