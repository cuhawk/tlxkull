# directly — Directly (Bugcrowd BBP)

> **STATUS: PAUSED** (Apr 24, 2026) — "Pausing until further notice" per announcement.
> Scope is sandbox environment only; production testing will get IP banned.

## Program info
- URL: https://bugcrowd.com/engagements/directly
- Type: bug_bounty (CX Automation platform)
- Scope rating: 1/4
- Started: May 03, 2018
- Paused: 24 Apr 2026

## Rewards
- P1: $2,500 – $3,000
- P2: $1,500 – $2,000
- P3: $500 – $750
- P4: $250 – $300

## In scope
- type: web
  url: https://sandbox.directly.com
  notes: Primary testing environment; mirrors production but sandbox
- type: web
  url: https://*.sandbox.directly.com
  notes: All discoverable subdomains

## Focus area endpoints
- sandbox.directly.com (insidr)
- eapps.sandbox.directly.com
- cai.sandbox.directly.com (cai-auto-responder)
- api.sandbox.directly.com (messaging-api)
- assets.sandbox.directly.com (static-assets)
- triageapi.sandbox.directly.com (ds_pr)
- dre.sandbox.directly.com (routing engine)
- https://report-connector.sandbox.directly.com
- https://url-shortener.sandbox.directly.com
- https://expert-dashboard.sandbox.directly.com/

## Out of scope
- www.directly.com (production)
- *.directly.com/schedule-a-demo/ or /product/* /careers/* /about/* /legal/* /trust/*
- resources.directly.com/* (HubSpot blog)
- Any WordPress related URLs (wp-content, wp-includes, etc.)
- Production version of app (sandbox only)
- Submitting requests to Salesforce via *.directly.com/schedule-a-demo/

## Credentials
- Register at: https://area-51.sandbox.directly.com/apply
- Login at: https://app.sandbox.directly.com/login/auth
- Test Q&A page: https://directly.github.io/demosite/qa/rtm/sandbox.html (3rd party, not attack surface)
