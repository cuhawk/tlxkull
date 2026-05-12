# Jora Bug Bounty

> Platform: Bugcrowd — https://bugcrowd.com/engagements/jora
> Type: BBP
> Bounty: See program page
> Status: In progress

## Scope

- in:  *.jora.com Ruby-on-Rails Website-Testing Ruby   # type: wildcard
- in:  https://apps.apple.com/us/app/jora-jobs-job-search-app/id917565665 Objective-C SwiftUI Swift iOS   # type: ios_app
- in:  https://play.google.com/store/apps/details?id=com.jora.android&hl=en_US Java Mobile-Application-Testing Kotlin Android   # type: android_app
- out: *.joralocal.com.au Website-Testing   # type: wildcard

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

## Notes (appended)

- status: ACTIVE (since Nov 2019)
- Job site (Australia-based, job seekers profiles/resumes are main sensitive data)
- Signup at https://www.jora.com/ using @bugcrowdninja.com email
- IMPORTANT job posting rules — must use these exact details or real users may see/apply:
  - Job Title (must contain): "Bugcrowd - Do Not Apply"
  - Country: United States
  - Business address: 1 Coyote Rd, Teller, Alaska, USA
  - Email: Your @bugcrowdninja.com address
  - DO NOT post jobs in other regions
- Regional sites (au.jora.com, us.jora.com) share same codebase — treated as one site
- Pre-authentication account takeover OOS (since Apr 2023)
- No automated scanners
- Nondisclosure: public disclosure NOT allowed
