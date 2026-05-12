# LastPass

> Platform: Bugcrowd — https://bugcrowd.com/engagements/lastpass
> Type: BBP
> Bounty: See program page
> Status: In progress

## Scope

- in:  https://lastpass.com   # type: url
- in:  https://lastpass.com/misc_download2.php   # type: url
- in:  https://support.lastpass.com   # type: url
- in:  https://blog.lastpass.com   # type: url
- in:  https://admin.lastpass.com   # type: url
- in:  https://auth.lastpass.com   # type: url
- in:  https://accounts.lastpass.com   # type: url
- in:  https://www.lastpass.com   # type: url
- in:  https://play.google.com/store/apps/details?id=com.lastpass.lpandroid   # type: android_app
- in:  https://play.google.com/store/apps/details?id=com.lastpass.authenticator   # type: android_app
- in:  https://apps.apple.com/us/app/lastpass-password-manager/id324613447   # type: ios_app
- in:  https://apps.apple.com/us/app/lastpass-authenticator/id1079110004   # type: ios_app
- out: https://identity.lastpass.com   # type: url
- out: https://info.lastpass.com   # type: url
- out: https://forums.lastpass.com   # type: url

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
