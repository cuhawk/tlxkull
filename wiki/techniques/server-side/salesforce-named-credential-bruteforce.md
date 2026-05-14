---
title: Salesforce named-credential brute-force via community user Apex
slug: salesforce-named-credential-bruteforce
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/server-side, technique/saas, technique/salesforce, technique/credential-reuse]
inbound: []
---

# Salesforce named-credential brute-force via community user Apex

## Pattern

A Salesforce **named credential** is a labeled object — `{label, endpoint,
auth}` — that admins create to let Apex call external APIs without
embedding secrets in code. When `Identity Type = Named Principal`, the
*credentials* (OAuth token / basic-auth tuple) are shared across all
users; Apex code calls `HTTP r = req.send(); req.setEndpoint('callout:<label>/<path>')`
and the platform substitutes the admin's credentials at runtime.

A community user who signs up to any public Lightning community can
execute Apex in their own (low-privilege) user context. Because the
credentials are *shared*, calling `callout:<label>` with a brute-forced
label name returns the admin-authenticated response. Attacker:

1. Signs up at a public community signup form.
2. Hits the `execute anonymous` Apex endpoint with their session
   cookie.
3. Iterates a wordlist of common named-credential labels (e.g.
   `Amazon`, `AWS_Prod`, `SalesforceCDN`, `SFTP_Customer_Backup`,
   `Slack`, `Workday`, harvested from public GitHub).
4. For each label, sends a callout with `setEndpoint('callout:<label>/')`
   and reads the response.

Path is attacker-controlled, so once a valid label hits, arbitrary
external paths inside the authenticated external system become
accessible.

## Preconditions

- Public Lightning community signup is enabled.
- At least one Named Credential exists with `Identity Type = Named
  Principal` (the default; per-user requires explicit setup almost no
  one does).
- Apex `execute anonymous` reachable to community users (default).

## Detection

- Sign up for a community user.
- Send a minimal `executeAnonymous` Apex payload calling
  `HttpRequest req = new HttpRequest(); req.setEndpoint('callout:NONEXISTENT/');
  req.setMethod('GET'); Http h = new Http(); h.send(req);`
- Observe the error: "Named credential `NONEXISTENT` does not exist" =
  oracle.

## Triggering

```apex
HttpRequest req = new HttpRequest();
req.setEndpoint('callout:<CANDIDATE_LABEL>/<ATTACKER_PATH>');
req.setMethod('GET');
Http h = new Http();
HttpResponse res = h.send(req);
System.debug(res.getBody());
```
Wrap in a loop over a wordlist of candidate labels; non-error responses
reveal valid named credentials and authenticated external data.

## Bypasses

- If `executeAnonymous` is locked, look for any Aura-enabled Apex
  method that takes a string parameter and uses it in a callout.
- The attacker controls the `<ATTACKER_PATH>` portion; chain to
  external IDOR by manipulating it to reach unintended resources.

## Seen in the wild

- {date: 2025-01-30, source: CT Ep 108} — Aaron Costello + Joseph Thacker; fixed
  by Salesforce after disclosure but residual exposure on customers who
  haven't migrated to per-user named credentials.

## References

- AppOmni Apex whitepaper
- Critical Thinking Podcast Ep 108
- Related: [[salesforce-aura-object-enumeration]], [[salesforce-apex-without-sharing]]
