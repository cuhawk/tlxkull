# Spotify

> Platform: HackerOne — https://hackerone.com/spotify
> Type: BBP
> Bounty: Low $100–$500 | Medium $200–$700 | High $400–$4,000 | Critical $600–$8,000
> Avg bounty: $300–$300
> Response efficiency: 95% | Avg first response: N/A | Total paid: $679,662
> Last scope update: 2026-05-08

## Scope

- in:  *.spotify.com    # type: wildcard # max: critical
- in:  *.spotify.net    # type: wildcard # max: critical
- in:  *.withspotify.com    # type: wildcard # max: low
- in:  *.byspotify.com    # type: wildcard # max: low
- in:  *.atspotify.com    # type: wildcard # max: low
- in:  *.avecspotify.com    # type: wildcard # max: low
- in:  *.enspotify.com    # type: wildcard # max: low
- in:  *.forspotify.com    # type: wildcard # max: low
- in:  *.fromspotify.com    # type: wildcard # max: low
- in:  *.tospotify.com    # type: wildcard # max: low
- in:  assets.spotify.com    # type: url # max: critical
- in:  api.spotify.com    # type: url # max: critical
- in:  https://www.whosampled.com/    # type: url # max: critical
- in:  backstage.io    # type: url # max: medium
- in:  Spotify SDKs    # type: repo # max: critical
- in:  iOS SDK    # type: repo # max: critical
- in:  Android SDK    # type: repo # max: critical
- in:  Web Playback SDK    # type: repo # max: critical
- in:  Core Backstage source code    # type: repo # max: critical
- in:  https://github.com/backstage/backstage    # type: repo # max: medium
- in:  Other Spotify websites    # type: other # max: critical
- in:  Anchor    # type: other # max: critical
- in:  Megaphone    # type: other # max: critical
- in:  Podsights    # type: other # max: critical
- in:  Sonantic    # type: other # max: critical
- in:  Core Assets    # type: other # max: critical
- in:  Non-Core Assets    # type: other # max: critical
- in:  GHE    # type: other # max: critical
- in:  Jira    # type: other # max: critical
- in:  Okta    # type: other # max: critical
- in:  VPN    # type: other # max: critical
- in:  Wrapped    # type: other # max: critical
- in:  DRM (Digital Rights Management) System    # type: other # max: critical
- in:  com.spotify.tv.android    # type: android_app # max: critical
- in:  com.spotify.s4a    # type: android_app # max: critical
- in:  com.spotify.music    # type: android_app # max: critical
- in:  com.spotify.kids    # type: android_app # max: critical
- in:  fm.anchor.android    # type: android_app # max: critical
- in:  Spotify desktop application (Windows and Mac)    # type: downloadable_executables # max: critical
- in:  Save to Spotify CLI    # type: downloadable_executables # max: critical
- in:  com.spotify.client    # type: ios_app # max: critical
- in:  com.spotify.s4a    # type: ios_app # max: critical
- in:  com.spotify.kids    # type: ios_app # max: critical
- in:  com.anchorfminc.Anchor    # type: ios_app # max: critical
- in:  api-partner.spotify.com    # type: api # max: critical
- in:  com.spotify.lite    # type: android_app # max: critical
- in:   api.spotify.com, api-partner.spotify.com    # type: api # max: critical
- in:  Chartable    # type: other # max: critical
- in:  api.spotify.com, api-partner.spotify.com    # type: api # max: critical
- in:  api.spotify.com    # type: url # max: critical
- in:  Whooshkaa    # type: other # max: critical
- in:  com.spotify.soundtrap.dreamcatcher    # type: ios_app # max: critical
- in:  api.sonantic.io    # type: url # max: critical
- in:  app.sonantic.io    # type: url # max: critical
- in:  label-studio-public.sonantic.io    # type: url # max: critical
- in:  com.spotify.zerotap    # type: android_app # max: critical
- in:  com.spotify.stations    # type: ios_app # max: critical
- in:  io.bettylabs.disco    # type: android_app # max: critical
- in:  io.bettylabs.Disco    # type: ios_app # max: critical
- in:  Greenroom Endpoints    # type: other # max: critical
- in:  heardle.app    # type: url # max: critical
- in:  http://*.spotifyforbrands.com    # type: wildcard # max: critical
- in:  http://*.spotify.net    # type: wildcard # max: critical
- in:  http://*.spotify.com    # type: wildcard # max: critical
- in:  developers.megaphone-staging.fm    # type: other # max: critical
- in:  cms.megaphone-staging.fm    # type: other # max: critical
- in:  developers.megaphone.fm    # type: other # max: critical
- in:  cms.megaphone.fm    # type: other # max: critical
- in:  Locker Room / Greenroom    # type: other # max: critical # not eligible for bounty
- in:  com.spotify.kids    # type: url # max: critical
- in:  *.gimletmedia.com    # type: wildcard # max: critical
- in:  *.soundtrap.com    # type: wildcard # max: critical
- in:  *.loudr.com    # type: wildcard # max: critical
- in:  *.loudr.fm    # type: wildcard # max: critical
- in:  test.spotify.com    # type: url # max: critical
- in:  com.spotify.music    # type: ios_app # max: critical
- out:  example.com    # type: url # max: none
- out:  everynoise.com    # type: url # max: none
- out:  Preact    # type: other # max: none
- out:  Soundtrap    # type: other # max: none
- out:  The Ringer    # type: other # max: none
- out:  Findaway    # type: other # max: none
- out:  com.soundtrap.studioapp    # type: android_app # max: none
- out:  com.soundtrap.studioapp    # type: ios_app # max: none
- out:  Parcast    # type: other # max: none
- out:  Loudr    # type: other # max: none
- out:  Gimlet    # type: other # max: none
- out:  Niland    # type: other # max: none
- out:  passport.findaway.com    # type: url # max: none
- out:  promotionapi.findaway.com    # type: url # max: none
- out:  cube.findaway.com    # type: url # max: none
- out:  passport-api.findaway.com    # type: url # max: none
- out:  sftp.findaway.com    # type: url # max: none
- out:  cubeapi.findaway.com    # type: url # max: none
- out:  auth.findaway.com    # type: url # max: none
- out:  voicesapi-prod.findawayworld.com    # type: url # max: none
- out:  api.findawayworld.com    # type: url # max: none
- out:  dailyplanet.findawayworld.com    # type: url # max: none
- out:  voicesmarketplace-prod.findawayworld.com    # type: url # max: none
- out:  my.findawayvoices.com    # type: url # max: none
- out:  http://*.findaway.com    # type: wildcard # max: none
- out:  Soundbetter    # type: other # max: none
- out:  Megaphone    # type: other # max: none
- out:  Other    # type: other # max: none
- out:  anchor.fm    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $679,662
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
