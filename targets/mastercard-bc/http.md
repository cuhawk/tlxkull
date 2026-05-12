# Mastercard Public Bug Bounty

> Platform: Bugcrowd — https://bugcrowd.com/engagements/mastercard
> Type: BBP
> Bounty: P1 $700–$2500 | P2 $300–$1000 | P3 $150–$500 | P4 $50–$150
> Status: In progress

## Scope

- in:  https://www.mastercard.us/en-us.html   # type: url
- in:  https://www.mastercard.ch/de-ch.html   # type: url
- in:  https://www.mastercard.ch/fr-ch.html   # type: url
- in:  https://www.mastercard.com.au/en-au.html   # type: url
- in:  https://www.mastercard.nl/nl-nl.html   # type: url
- in:  https://developer.mastercard.com   # type: url
- in:  https://donate.mastercard.com   # type: url
- in:  https://demo.priceless.com/   # type: url
- in:  https://priceless.com/golf/   # type: url
- in:  https://performancemarketing.mastercard.com/portal/   # type: url
- in:  https://src.mastercard.com/profile/enroll   # type: url
- in:  https://src.mastercard.com/*   # type: url
- in:  https://www.finicity.com   # type: url
- in:  https://consumer.finicityreports.com   # type: url
- in:  https://pioneer.truata.com/   # type: url
- out: demo.priceless.com/travel   # type: domain
- out: https://masterpassteststore.com/   # type: url
- out: https://www.mastercard.us/en-us/personal/ways-to-pay/click-to-pay.html   # type: url
- out: https://checkout.mastercard.com/   # type: url
- out: https://secure.checkout.visa.com/*   # type: url

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- safe harbor: yes
- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []

## Test Credentials / Access

- Priceless (demo.priceless.com): HTTP auth user=mastercard / pass=priceLESS; test card 5555 5555 5555 4444
- Mastermind: sign up with @bugcrowdninja.com email at https://performancemarketing.mastercard.com/portal/
- DXP/Donate: use card 5333170000000008 or 5333170000000057, exp 09/24, CVC 464
- Finicity consumer portal: sign up at https://consumer.finicityreports.com/signup with @bugcrowdninja.com email; test SSN 777777777 DOB 1997-07-07 or SSN 222222222 DOB 2002-02-02
- SRC: test store https://masterpassteststore.com/ (store itself OOS, only Masterpass checkout in scope)
- MDES CS API: Insomnia collection + P12 file in resources tab; test account ranges 5204245250000000000–5204245259999999999 and 5204490310000000000–5204490319999999999
- Use @bugcrowdninja.com email for all signups (GDPR requirement — failure risks getting blocked)

## "Public Other Targets" tier

For Mastercard assets not listed under main in-scope but clearly Mastercard-owned: P1 $700–$2,500 / P2 $300–$1,000 / P3 $150–$500 / P4 $50–$150. Vendor/partner sites (www.mastercard-*.com) also fall here. Lower-env (stage/dev/test/sandbox) vendor apps: 50% of vendor table rates.

## Notes

- No automated scanners/scripted form testing
- RCE reports: must include source IP, timestamp (TZ), full req/res, uploaded filenames must contain "bugbounty" + timestamp
- Subdomain takeover: High Impact P2 $900, Basic P3 $300, Concession P4 $100
- Recorded Future has separate BBP — OOS here
- biz360.mastercard.com and mybiz360.mastercard.com OOS
- Simplify Commerce (www.simplify.com/commerce/) now OOS (as of Aug 2025)
- All Mastercard Developer APIs (developer portal) OOS for testing
- Nondisclosure
