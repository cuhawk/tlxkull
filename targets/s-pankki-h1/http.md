# S-Pankki

> Platform: HackerOne — https://hackerone.com/s-pankki
> Type: BBP
> Bounty: Low $500 | Medium $1,000 | High $2,000 | Critical $5,000
> Avg bounty: $500–$500
> Response efficiency: 90% | Avg first response: N/A | Total paid: $120,000
> Last scope update: 2026-04-24

## Scope

- in:  online.s-pankki.fi    # type: url # max: critical
- in:  www.s-pankki.fi    # type: url # max: critical
- in:  https://crosskey.io/stores/s-pankki/apis    # type: url # max: critical
- in:  mobile.s-pankki.fi    # type: url # max: critical
- in:  www.s-kaupat.fi    # type: url # max: critical
- in:  extranet.s-pankki.fi    # type: url # max: critical
- in:  tunnistus.s-ryhma.fi    # type: url # max: critical
- in:  digili.s-cloud.fi    # type: url # max: critical
- in:  www.prisma.fi    # type: url # max: critical
- in:  www.sokos.fi    # type: url # max: critical
- in:  api.sokos.fi    # type: url # max: critical
- in:  api.s-kaupat.fi    # type: url # max: critical
- in:  fi.spankki    # type: android_app # max: critical
- in:  740514933    # type: ios_app # max: critical
- in:  cfapi.voikukka.fi    # type: url # max: critical
- out:  external e-salary pages in netbank    # type: other # max: none
- out:  www.s-kanava.fi    # type: url # max: none
- out:  www.fim.com    # type: url # max: none
- out:  online.fim.com    # type: url # max: none
- out:  Netposti iFrame in netbank    # type: other # max: none
- out:  740514933    # type: ios_app # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $120,000
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
