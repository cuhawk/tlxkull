# Crowdstrike

> Platform: HackerOne — https://hackerone.com/crowdstrike
> Type: BBP
> Bounty: Low $350 | Medium $1,500 | High $8,000 | Critical $10,000
> Avg bounty: $250–$250
> Response efficiency: 100% | Avg first response: N/A | Total paid: $126,449
> Last scope update: 2023-08-07

## Scope

- in:  *.crowdstrike.com    # type: wildcard # max: critical
- in:  *.humio.com    # type: wildcard # max: critical
- in:  *.securecircle.com    # type: wildcard # max: critical
- in:  *.preempt.com    # type: wildcard # max: critical
- in:  *.preemptsecurity.com    # type: wildcard # max: critical
- in:  *.reposify.com    # type: wildcard # max: critical
- in:  *.bionic.ai    # type: wildcard # max: critical
- in:  *.flowsecurity.app    # type: wildcard # max: critical
- in:  *.adaptive-shield.com    # type: wildcard # max: critical
- in:  www.crowdstrike.org    # type: url # max: critical
- in:  falcon-sandbox.com    # type: url # max: critical
- in:  hybrid-analysis.com    # type: url # max: critical
- in:  www.crowdstrike.com    # type: url # max: critical
- in:  onum.com    # type: url # max: critical
- in:  onum-labs.com    # type: url # max: critical
- in:  pangea.cloud    # type: url # max: critical
- in:  CrowdStrike public infrastructure    # type: other # max: critical
- in:  play.google.com/store/apps/details?id=com.crowdstrike.falconmobile    # type: android_app # max: critical
- in:  apps.apple.com/us/app/crowdstrike-falcon/id1458815656    # type: ios_app # max: critical
- in:  crowdstrike.co.uk    # type: url # max: critical
- in:  crowdstrike.fr    # type: url # max: critical
- in:  crowdstrike.jp    # type: url # max: critical
- in:  crowdstrike.com.br    # type: url # max: critical
- in:  crowdstrike.com.au    # type: url # max: critical
- in:  crowdstrikeracing.com    # type: url # max: critical
- in:  www.reverse.it    # type: url # max: critical
- in:  blog.crowdstrike.com    # type: url # max: critical
- out:  www.humio.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $126,449

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
