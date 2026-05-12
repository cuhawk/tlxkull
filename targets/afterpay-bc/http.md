# Afterpay Bug Bounty Program

> Platform: Bugcrowd — https://bugcrowd.com/engagements/afterpay
> Type: BBP
> Bounty: See program page
> Status: In progress (started Jan 17, 2023)

## Scope

- in:  https://apps.apple.com/au/app/afterpay-shop-now-pay-later/id1230286588   # type: ios_app
- in:  https://play.google.com/store/apps/details?id=com.afterpaymobile.us&hl=en_US&gl=US   # type: android_app
- in:  https://portal.afterpay.com   # type: url
- in:  https://afterpay.com   # type: url
- in:  https://mobileapi.afterpay.com   # type: url
- in:  https://portalapi.us.afterpay.com   # type: url
- in:  https://developers.afterpay.com   # type: url
- in:  https://apps.apple.com/gb/app/clearpay-buy-now-pay-later/id1474022186   # type: ios_app
- in:  https://play.google.com/store/apps/details?id=com.afterpaymobile.uk   # type: android_app
- in:  https://clearpay.co.uk   # type: url
- in:  https://clearpay.com   # type: url
- in:  https://portal.clearpay.com   # type: url
- in:  https://portal.clearpay.co.uk   # type: url
- in:  https://mobileapi.clearpay.com   # type: url
- in:  https://portalapi.eu.clearpay.co.uk   # type: url
- in:  https://api.clearpay.com   # type: url
- in:  afterpaytechblog.com   # type: domain
- in:  genderfree.afterpay.com   # type: domain
- in:  moneybyafterpay.com   # type: domain

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- safe harbor: yes
- disclosure: NOT allowed
- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []

## Sandbox API Credentials (Program-Provided)

| Name | Region | Merchant ID | API Key |
|---|---|---|---|
| Bug Bounty AU Sandbox 1 | AU | 43181 | 984fa120a16b5b8a3f6d674ce64b030c010153ff3ac7d2c144bd4041c4fb5c44baaa623f4a1d22ef1dc0048b4c0c142d4f5abd381a21b59057a5ab7b7701ca93 |
| Bug Bounty AU Sandbox 2 | AU | 43483 | 3923852fa665cd3ddb2bffaac9d828da4e2d03c371a6af9c8d7a00b2a40fb005cd86c91021b004c11b3a739b1b70f538cd4de6b75883b4b303379a2c5893dda7 |
| Bug Bounty CA Sandbox | CA | 100203785 | a7f9395b115dae49d1ff2b776e21be55920c4b16b800f8a8d67c519860f28586cd2f1309db0cef3b3d8896a1430f422d7df62e2ac5bc64ebc1966e65f26c21a7 |
| Bug Bounty US Sandbox | US | 100203697 | 80f50c878828e2daad38bbe986d5373638926ccfd9ebfcd8a9b754d1720014104757fbdf0bf8609acf1d0258852be8f2f43a2acc6616ae6080e54f5a9a032395 |
| Bug Bounty UK Sandbox 1 | UK | 400248332 | 15850c90f4362e53a38ceba5eb874f379745016fbd6fc74c948c0be71b84fc041cb212d93f19aef423b5fb7f3c4b8057d04f465339ddba93557ea9210b8aeb97 |
| Bug Bounty UK Sandbox 2 | UK | 400248333 | 42febb9dcd41368bcb0b5ef9a460fe3698b13d8a98d15c763caa14ed07615f62c775a53845a04f7437ed54caf7a58e6bee2301fa35e86e4c3d80adef8801fb8 |

Sandbox docs: https://developers.afterpay.com/afterpay-online/docs/test-environment

## Notes

- Part of Block, Inc.; Block products (Square, Cash App, Tidal) = separate programs
- Nondisclosure
- Safe harbor (CFAA + DMCA)
- Testing in Sandbox recommended; no support for reversing production transactions
- No test merchant portal accounts provided
- Mobile bugs must be proven in latest app version
- Average payout $537.50; validation within 4 days

## OOS

- afterpaytechblog.com, genderfree.afterpay.com, moneybyafterpay.com
- Rate limiting, open redirect, merchant site vulns, social engineering
- Logout CSRF, clickjacking, content spoofing, missing headers
- SSL issues without demonstrable impact, self-XSS
- Email bombing, broken links, leaked user credentials
