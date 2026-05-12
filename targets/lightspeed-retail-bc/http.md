# Lightspeed Retail Bug Bounty

- platform: bugcrowd
- program_url: https://bugcrowd.com/engagements/lightspeed-retail
- category: Retail
- safe_harbor: full
- nondisclosure: false
- scope_rating: 3/4
- started: 2022-09-27

## Rewards

| Priority | X-Series (Retail) | E-Series (Ecommerce) |
|---|---|---|
| P1 | $4000-$6250 | $1000-$2000 |
| P2 | $1000-$2000 | $500-$750 |
| P3 | $300-$500 | $200-$450 |
| P4 | $20-$150 | $20-$100 |

## Targets

### Lightspeed Retail X-Series
- in: https://retail.lightspeedhq.com/  # type: url  # X-Series main app (targets loading — use your test store)
- in: *.lightspeedhq.com  # type: wildcard  # Retail X-Series platform

### Lightspeed Ecommerce E-Series
- in: https://my.ecwid.com  # type: url  # Control Panel
- in: *.company.site  # type: wildcard  # Storefront Panel ([yourstore].company.site)
- in: https://app.ecwid.com/api/v3/  # type: url  # E-Series API
- in: https://apps.apple.com/us/app/ecwid-ecommerce/id626731456  # type: ios_app
- in: https://play.google.com/store/apps/details?id=com.ecwid.android  # type: android_app

## Out of Scope
- out: x-series-support.lightspeedhq.com  # type: domain
- out: vendhq.force.com  # type: domain
- out: vendimageuploadcdn.global.ssl.fastly.net  # type: domain
- out: partners.vendhq.com  # type: domain
- out: track.api.vendhq.com  # type: domain
- out: your-store.vendecommerce.com  # type: domain
- out: partnerportal.vendhq.com  # type: domain
- out: https://support.ecwid.com/hc/en-us  # type: url
- out: https://www.ecwid.com/  # type: url

## Auth / Testing Notes

- X-Series: create test account using YourUsername@bugcrowdninja.com; create non-admin users with your own emails only
- E-Series: register at https://my.ecwid.com/cp/#register with @bugcrowd.com email; add "bugbounty" to your store domain
- No automated scanners (will result in removal)
- Testing only against stores you created — never other customer stores
- IDOR with read-only access within same store = OOS; cross-store = in scope
- X-Series focus: unauthorized write access (create/update/delete) on permission areas
- E-Series: XSS in admin storefront = OOS; Stored XSS targeting another admin user = in scope
