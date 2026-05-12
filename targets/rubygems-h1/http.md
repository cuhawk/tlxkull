# RubyGems

> Platform: HackerOne — https://hackerone.com/rubygems
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 41% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2022-01-09

## Scope

- in:  rubygems.org    # type: url # max: critical # not eligible for bounty
- in:  shipit.rubygems.org    # type: url # max: critical # not eligible for bounty
- in:  https://github.com/rubygems/rubygems    # type: repo # max: critical # not eligible for bounty
- in:  Malicious or compromised gem    # type: other # max: high # not eligible for bounty
- out:  help.rubygems.org    # type: url # max: none
- out:  support.rubygems.org    # type: url # max: none
- out:  uptime.rubygems.org    # type: url # max: none
- out:  blog.rubygems.org    # type: url # max: none
- out:  guide.rubygems.org    # type: url # max: none
- out:  stats.rubygems.org    # type: url # max: none
- out:  status.rubygems.org    # type: url # max: none
- out:  https://s3-us-west-2.amazonaws.com/rubygems-dumps    # type: url # max: none
- out:  http://rubygems.org/names    # type: api # max: none
- out:  gem server command    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- N/A

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
