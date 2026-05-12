# recroom-og

> Platform: Bugcrowd — https://bugcrowd.com/engagements/recroom-og
> Type: BBP
> Bounty: P1 $2100–$2500 | P2 $1000–$1250 | P3 $450–$600 | P4 $150–$200
> Status: PAUSED (paused 10 Feb 2026, "until further notice")

## Scope

- in: https://rec.net/download   # Rec Room standalone app
- in: https://store.steampowered.com/app/471710/Rec_Room/   # Steam
- in: https://www.oculus.com/experiences/quest/2173678582678296   # Oculus Quest
- in: https://www.oculus.com/experiences/rift/1257029974329451   # Oculus Rift
- in: https://www.nintendo.com/us/store/products/rec-room-switch/   # Nintendo Switch
- in: https://apps.apple.com/app/id1450306065   # iOS
- in: https://play.google.com/store/apps/details?id=com.AgainstGravity.RecRoom   # Android
- in: https://www.xbox.com/en-us/games/store/rec-room/9pgpqk0xthrz   # Xbox
- in: https://store.playstation.com/en-us/product/UP2662-PPSA05532_00-6681199027107223   # PS5
- in: https://store.playstation.com/en-us/product/UP2662-CUSA08481_00-RECROOM000000001   # PS4
- in: https://recroom.com/studio   # Rec Room Studio
- in: https://devportal.rec.net/   # RecNet API Portal
- out: Company email servers
- out: Payment processing (handled by third party)

## Notes

- Game targets are redacted in the Bugcrowd brief; URLs sourced from in-scope description text
- Primary target is the free cross-platform Rec Room game (download required)
- Web app and API also in scope
- Focus: in-game currency manipulation, account takeover, exploits disrupting other users
- Do NOT use vulnerability scanners
- Program paused; resume testing only when reopened

## Auth

- type: session
- creds: env:BUGCROWD_NINJA_EMAIL
- note: Sign up with "Bugcrowd" as first part of username (e.g. BugcrowdNinja)
