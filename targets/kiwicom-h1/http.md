# Kiwi.com

> Platform: HackerOne — https://hackerone.com/kiwicom
> Type: BBP
> Bounty: Low $200 | Medium $500 | High $2,000 | Critical $5,000
> Avg bounty: $200–$256
> Response efficiency: 84% | Avg first response: N/A | Total paid: $140,168
> Last scope update: 2025-05-07

## Scope

- in:  *.kiwi.com    # type: wildcard # max: critical
- in:  *.skypicker.com    # type: wildcard # max: critical
- in:  www.kiwi.com    # type: url # max: critical
- in:  auth.skypicker.com    # type: url # max: critical
- in:  tequila.kiwi.com    # type: url # max: critical
- in:  http://www.kiwi.com/stories    # type: url # max: high
- in:  jobs.kiwi.com    # type: url # max: medium
- in:  https://github.com/kiwicom/*    # type: repo # max: high
- in:  com.skypicker.main    # type: android_app # max: critical
- in:  com.skypicker.Skypicker    # type: ios_app # max: critical
- in:  api.skypicker.com    # type: url # max: critical
- in:  booking-api.skypicker.com    # type: url # max: critical
- in:  holidays.kiwi.com    # type: url # max: none # not eligible for bounty
- in:  clickout.kiwi.com    # type: url # max: none # not eligible for bounty
- out:  *ov.kiwi.com    # type: wildcard # max: none
- out:  *sg.kiwi.com    # type: wildcard # max: none
- out:  *._domainkey.kiwi.com    # type: wildcard # max: none
- out:  email*skypicker.com    # type: wildcard # max: none
- out:  email*kiwi.com    # type: wildcard # max: none
- out:  *_domainkey.skypicker.com    # type: wildcard # max: none
- out:  *citi-sign.kiwi.com    # type: wildcard # max: none
- out:  *cars.kiwi.com    # type: wildcard # max: none
- out:  *code.kiwi.com    # type: wildcard # max: none
- out:  *parking.kiwi.com    # type: wildcard # max: none
- out:  *learn.kiwi.com    # type: wildcard # max: none
- out:  *.coupons.kiwi.com    # type: wildcard # max: none
- out:  *experiences.kiwi.com    # type: wildcard # max: none
- out:  vacation.kiwi.com    # type: url # max: none
- out:  outbound.intercom.kiwi.com    # type: url # max: none
- out:  mail.skypicker.com    # type: url # max: none
- out:  packages.kiwi.com    # type: url # max: none
- out:  nyrujhhu3yuk.nest.skypicker.com    # type: url # max: none
- out:  status.kiwi.com    # type: url # max: none
- out:  rooms.kiwi.com    # type: url # max: none
- out:  retool.skypicker.com    # type: url # max: none
- out:  kiwistore.kiwi.com    # type: url # max: none
- out:  link.kiwi.com    # type: url # max: none
- out:  https://github.com/kiwicom/pytest-recording    # type: repo # max: none
- out:  https://github.com/kiwicom/pytest-recording    # type: url # max: none
- out:  merch.kiwi.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $140,168
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
