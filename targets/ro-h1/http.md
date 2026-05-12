# Ro

> Platform: HackerOne — https://hackerone.com/ro
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 67% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2022-11-16

## Scope

- in:  *.ro.co    # type: wildcard # max: medium # not eligible for bounty
- in:  *.getroman.com    # type: wildcard # max: medium # not eligible for bounty
- in:  *.ropharmacy.com    # type: wildcard # max: medium # not eligible for bounty
- in:  *.hellorory.com    # type: wildcard # max: medium # not eligible for bounty
- in:  *.modernfertility.com    # type: wildcard # max: medium # not eligible for bounty
- in:  *.kit.ro.co    # type: wildcard # max: medium # not eligible for bounty
- in:  *.myplenity.com    # type: wildcard # max: low # not eligible for bounty
- in:  https://*.ro.co/svc/auth-verifications/start.public/phone    # type: wildcard # max: none # not eligible for bounty
- in:  my.ro.co    # type: url # max: critical # not eligible for bounty
- in:  login.ro.co    # type: url # max: critical # not eligible for bounty
- in:  start.ro.co    # type: url # max: critical # not eligible for bounty
- in:  http://ro.co/pharmacy    # type: url # max: medium # not eligible for bounty
- in:  http://ro.co/mind    # type: url # max: medium # not eligible for bounty
- in:  http://ro.co/derm    # type: url # max: medium # not eligible for bounty
- in:  http://ro.co/spermkit    # type: url # max: medium # not eligible for bounty
- in:  1514854156    # type: ios_app # max: critical # not eligible for bounty
- in:  1585858911    # type: ios_app # max: critical # not eligible for bounty
- in:  https://*.kit.com    # type: wildcard # max: medium # not eligible for bounty
- in:  *.kit.com    # type: wildcard # max: medium # not eligible for bounty
- in:  *.workpath.co    # type: wildcard # max: medium # not eligible for bounty
- in:  1179697245    # type: ios_app # max: critical # not eligible for bounty
- in:  com.iggbonow    # type: android_app # max: critical # not eligible for bounty
- out:  https://ro.co/messages/*    # type: wildcard # max: none
- out:  https://*.ro.co/svc/auth-verifications/*/phone/*    # type: wildcard # max: none
- out:  https://ro.co/svc/auth-verifications/*/phone/*    # type: wildcard # max: none
- out:  https://ro.co/weight-loss/supply-tracker/*    # type: wildcard # max: none
- out:  https://ro.co/weight-loss/glp1-insurance-checker/*    # type: wildcard # max: none
- out:  https://*.ro.co/api/members    # type: wildcard # max: none
- out:  community.modernfertility.com    # type: url # max: none
- out:  https://ro.co/api/account-exists    # type: url # max: none
- out:  https://ro.co/api/presigned-upload-url    # type: url # max: none
- out:  https://login.ro.co/authorize    # type: url # max: none
- out:  *.ro.co/svc/auth-verifications/*/phone/start-verification    # type: wildcard # max: none
- out:  *.ro.co/svc/auth-verifications/*/phone/set-number    # type: wildcard # max: none
- out:  ro.co/svc/auth-verifications/*/phone/start-verification    # type: wildcard # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
