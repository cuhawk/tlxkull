# 20 Minuten

> Platform: Bugcrowd — https://bugcrowd.com/engagements/twentyminuten
> Type: BBP
> Bounty: See program page
> Status: In progress

## Scope

- in:  https://www.20min.ch   # type: url
- in:  https://cm.20min.ch/   # type: url
- in:  https://api.20min.ch/   # type: url
- in:  https://videoplayer.20min.ch   # type: url
- in:  https://partner-feeds.20min.ch   # type: url
- in:  https://screenplayer.20min.ch   # type: url
- in:  https://audio.20min.ch   # type: url
- out: https://tgt.tamedia.ch   # type: url
- out: http://auth.20min.ch   # type: url
- out: https://cre-api.tamedia.ch   # type: url
- out: https://track.20min.ch   # type: url
- out: https://*.connect.ringier.ch   # type: url
- out: *.onelog.ch   # type: wildcard
- out: *.20min-tv.ch   # type: wildcard
- out: *.newsnetz.tv   # type: wildcard
- out: *.appuser.ch   # type: wildcard
- out: *.iagentur.ch   # type: wildcard
- out: *.streamboat.ch   # type: wildcard
- out: *.streamboatserver.ch   # type: wildcard

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
