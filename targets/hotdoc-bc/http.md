# HotDoc

> Platform: Bugcrowd — https://bugcrowd.com/engagements/hotdoc
> Type: BBP
> Bounty: P1 $4000–$8000 | P2 $2000–$3000 | P3 $500–$1000 | P4 $50–$200
> Status: In progress

## Scope

- in:  https://bugcrowd.hotdoc.com.au/   # type: url
- in:  https://bugcrowd.hotdoc.com.au/dashboard   # type: url
- in:  https://try.hotdoc.com.au/hotdoc-profiles   # type: url

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []

## Notes (appended)

- status: PAUSED (Dec 5 2025 — indefinitely, but still triaging/accepting submissions)
- required_header: Bugcrowd: 38fd3272-b289-4e03-9a90-8adf34cb5d95 (all requests to bugcrowd.hotdoc.com.au)
- test_domain: bugcrowd.hotdoc.com.au (dedicated BB domain — production tests NOT allowed)
- clinic_creds: https://bugcrowd.hotdoc.com.au/clinic_users/new (use @bugcrowdninja.com email)
- patient_creds: https://bugcrowd.hotdoc.com.au/patients/new
- patient_search_api: https://bugcrowd.hotdoc.com.au/api/dashboard/pms_patients?search=
- mfa: TOTP-based MFA available on patient accounts (added Jun 2024)
- routes_file: Available in program resources (routes.txt 392KB — rails routes output)
- focus: Sensitive data exfiltration, PII exposure, Australian notifiable data breach thresholds
