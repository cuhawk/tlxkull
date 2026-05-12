# APNIC

> Platform: HackerOne — https://hackerone.com/apnic
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 92% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2023-03-24

## Scope

- in:  *.apnic.net    # type: wildcard # max: critical # not eligible for bounty
- in:  *.apnic.foundation    # type: wildcard # max: critical # not eligible for bounty
- in:  *.isif.asia    # type: wildcard # max: critical # not eligible for bounty
- in:  *.seedalliance.net    # type: wildcard # max: critical # not eligible for bounty
- in:  *.apidt.org    # type: wildcard # max: critical # not eligible for bounty
- in:  orbit.apnic.net    # type: url # max: critical # not eligible for bounty
- in:  ftp.apnic.net    # type: url # max: critical # not eligible for bounty
- in:  stats.labs.apnic.net    # type: url # max: critical # not eligible for bounty
- in:  aso.apnic.net    # type: url # max: critical # not eligible for bounty
- in:  nori.apnic.net    # type: url # max: critical # not eligible for bounty
- in:  rsync.apnic.net    # type: url # max: critical # not eligible for bounty
- in:  registry-testbed.apnic.net    # type: url # max: critical # not eligible for bounty
- in:  rpki.apnic.net    # type: url # max: critical # not eligible for bounty
- in:  submission.apnic.net    # type: url # max: medium # not eligible for bounty
- in:  * IPv4 addresses    # type: other # max: critical # not eligible for bounty
- in:  * IPv6 addresses    # type: other # max: critical # not eligible for bounty
- in:  203.119.102.40/32    # type: cidr # max: critical # not eligible for bounty
- in:  203.133.248.0/22    # type: cidr # max: critical # not eligible for bounty
- in:  * IP addresses for whois servers hosted outside APNIC networks    # type: other # max: critical # not eligible for bounty
- out:  login.apnic.net    # type: url # max: none
- out:  upload.apnic.net    # type: url # max: none
- out:  autodiscover.apnic.net    # type: url # max: none
- out:  enterpriseenrollment.apnic.net    # type: url # max: none
- out:  enterpriseregistration.apnic.net    # type: url # max: none
- out:  help.apnic.net    # type: url # max: none
- out:  info.apnic.net    # type: url # max: none
- out:  lyncdiscover.apnic.net    # type: url # max: none
- out:  sip.apnic.net    # type: url # max: none
- out:  community.apnic.net    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
