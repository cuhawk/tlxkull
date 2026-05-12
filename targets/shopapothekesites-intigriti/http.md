# Redcare Pharmacy Sites (Shop Apotheke)

> Platform: Intigriti — https://app.intigriti.com/researcher/programs/shopapotheke/shopapothekesites/detail
> Type: BBP | Public | Open
> Bounty: Low €250 | Medium €1,500 | High €3,000 | Critical €4,000 | Exceptional €4,000 (Tier 2); min €50
> Avg payout: N/A | Total paid: N/A
> Response: avg first response < 2 weeks | avg to decide +3 weeks
> Last scope update: unknown

## Scope

- in:  *.sa-tech.de   # type: wildcard | tier: Tier 2
- in:  api.shop-apotheke.at   # type: url | tier: Tier 2
- in:  api.shop-apotheke.com   # type: url | tier: Tier 2
- in:  now.shop-apotheke.com   # type: url | tier: Tier 2
- in:  payment.shop-apotheke.com   # type: url | tier: Tier 2
- in:  redcare-apotheke.ch   # type: url | tier: Tier 2
- in:  redcare-pharmacie.fr   # type: url | tier: Tier 2
- in:  services-acc22.shop-apotheke.com/subse/backoffice/index   # type: url | tier: Tier 2
- in:  services.shop-apotheke.com   # type: url | tier: Tier 2
- in:  shared-services-prod.redteclab.de   # type: url | tier: Tier 2
- in:  shop-apotheke iOS (id1104967519)   # type: ios_app | tier: Tier 2
- in:  shop.shop_apotheke.com.shopapotheke (Android)   # type: android_app | tier: Tier 2
- in:  sso.shop-apotheke.com   # type: url | tier: Tier 2
- in:  studio.shop-apotheke.com   # type: url | tier: Tier 2
- in:  www.redcare.it   # type: url | tier: Tier 2
- in:  www.shop-apotheke.at   # type: url | tier: Tier 2
- in:  www.shop-apotheke.com   # type: url | tier: Tier 2
- in:  as.shop-apotheke.com   # type: url | tier: No bounty
- in:  cdn.shop-apotheke.com   # type: url | tier: No bounty
- in:  dbt.shop-apotheke.com   # type: url | tier: No bounty
- in:  info.shop-apotheke.com   # type: url | tier: No bounty
- in:  is.shop-apotheke.com   # type: url | tier: No bounty
- in:  personal.shop-apotheke.com   # type: url | tier: No bounty
- in:  vt.shop-apotheke.com   # type: url | tier: No bounty

## Auth

- type: session
- creds: env:INTIGRITI_SESSION_TOKEN
- note: self-registration available on shop sites; use @intigriti.me address

## Notes

- payout speed: avg to decide +3 weeks
- online pharmacy; sites share high % source code — report once per vuln
- CSRF temporarily out of scope
- report identical vulns across endpoints only once
- focus: sensitive data extraction (email/password/order/billing/CC), unauthorized infrastructure access, payment bypass
- severity: Exceptional=RCE/full DB/infra; Critical=user data/privesc; High=random user data/stored XSS; Medium=reflected XSS

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
