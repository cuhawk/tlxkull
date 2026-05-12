# VMware by Broadcom — VCF vCenter Server

> Platform: Intigriti — https://app.intigriti.com/researcher/programs/vmware/vcf-management/detail
> Type: BBP | Public | Suspended
> Bounty: Low $100 | Medium $500 | High $3,000 | Critical $10,000 | Exceptional $10,000 (Tier 1); Low $100 | Medium $500 | High $3,000 | Critical $8,000 | Exceptional $8,000 (Tier 2)
> Avg payout: $3,412 | Total paid: $58,000
> Response: N/A
> Last scope update: unknown

## Scope

- in:  vCenter Server   # type: other | tier: Tier 1 | skills: 5
- out: brute force login attacks   # type: other
- out: missing security headers / cookie flags   # type: other
- out: known OSS vulns without working PoC   # type: other
- out: SSL/TLS misconfiguration   # type: other
- out: DoS of guest VM by local admin   # type: other
- out: clickjacking on non-sensitive pages   # type: other
- out: content spoofing / text injection   # type: other
- out: server-side DoS in hosted environment   # type: other
- out: outdated browser vulns   # type: other
- out: version disclosure / banner grabbing   # type: other
- out: unlikely user interaction required   # type: other
- out: CSV injection   # type: other
- out: LPE based on abusing sudo privileges   # type: other

## Auth

- type: session
- creds: env:INTIGRITI_SESSION_TOKEN
- note: @intigriti.me required; ID check required; no custom user agent or request header; testing only on provided Test Environments or own lab — NOT on production; contact: vmware.psirt@broadcom.com

## Notes

- payout speed: CURRENTLY SUSPENDED (last activity Dec 2024)
- VMware by Broadcom; vCenter Server management platform; Software category
- test environments only — participants MUST NOT test production
- one vuln per report unless chaining required for impact
- retest bonus: $50 for verifying a resolved issue
- LPE via sudo abuse is OOS
- provide product name and version when submitting
- duplicate policy: first received report wins
- known-to-VMware issues receive no bounty

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
