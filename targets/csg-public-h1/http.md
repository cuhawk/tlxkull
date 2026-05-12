# Cloud Software Group

> Platform: HackerOne — https://hackerone.com/csg-public
> Type: BBP
> Bounty: Low N/A | Medium $250 | High $2,000 | Critical $5,000
> Avg bounty: $200–$200
> Response efficiency: 90% | Avg first response: N/A | Total paid: $541,249
> Last scope update: 2026-05-01

## Scope

- in:  ap-s.cloud.com    # type: url # max: critical
- in:  eu.cloud.com    # type: url # max: critical
- in:  us.cloud.com    # type: url # max: critical
- in:  *.citrixworkspacesapi.net    # type: url # max: critical
- in:  onboarding.cloud.com    # type: url # max: critical
- in:  onboarding-*.cloud.com    # type: url # max: critical
- in:  accounts.cloud.com    # type: url # max: critical
- in:  adm.cloud.com    # type: url # max: critical
- in:  api.adm.cloud.com    # type: url # max: critical
- in:  Citrix Secure Access client for Windows    # type: other # max: critical
- in:  Citrix Secure Access client for iOS    # type: other # max: critical
- in:  Citrix Secure Access client for Linux    # type: other # max: critical
- in:  Citrix End Point Analysis (EPA) client for Linux    # type: other # max: critical
- in:  Citrix End Point Analysis (EPA) client for Windows    # type: other # max: critical
- in:  Citrix Secure Access client for Android    # type: android_app # max: critical
- in:  Citrix Secure Access client for macOS    # type: ios_app # max: critical
- in:  *developer.cloud.com    # type: url # max: none # not eligible for bounty
- in:  (yoursubdomain).sf-api.com    # type: url # max: critical
- in:  (yoursubdomain).sf-api.eu    # type: url # max: critical
- in:  (yoursubdomain).sharefile.eu    # type: url # max: critical
- in:  secure.sharefile.eu    # type: url # max: critical
- in:  api.sharefile.eu    # type: url # max: critical
- in:  sf-rp-eu.sharefile.com    # type: url # max: critical
- in:  (yoursubdomain).sharefile.com    # type: url # max: critical
- in:  sf-rp-us.sharefile.com    # type: url # max: critical
- in:  secure.sharefile.com    # type: url # max: critical
- in:  sf-rp.sharefile.com    # type: url # max: critical
- in:  api.sharefile.com    # type: url # max: critical
- in:  http://(yoursubdomain).sharefile.com/sf/v3/    # type: url # max: critical
- out:  citrix.cloud.com    # type: url # max: none
- out:  www.cloud.com    # type: url # max: none
- out:  accounts-internal.cloud.com    # type: url # max: none
- out:  launch.cloud.com    # type: url # max: none
- out:  *.citrix*.com    # type: url # max: none
- out:  *.cloudburrito.com    # type: url # max: none
- out:  *.securevdr.com    # type: url # max: none
- out:  *.podio.com    # type: url # max: none
- out:  (yoursubdomain).us.iws.cloud.com    # type: url # max: none
- out:  (yoursubdomain).ap.iws.cloud.com    # type: url # max: none
- out:  (yoursubdomain).eu.iws.cloud.com    # type: url # max: none
- out:  (youriwssubdomain).cloud.com    # type: url # max: none
- out:  *.xmtest.cloud.com    # type: url # max: none
- out:  *.xmqa.cloud.com    # type: url # max: none
- out:  *.xmdev.cloud.com    # type: url # max: none
- out:  *.browser.cloud.com    # type: other # max: none
- out:  *.sharefile.com    # type: url # max: none
- out:  *.sharefile.eu    # type: url # max: none
- out:  *.sharefile*.com    # type: url # max: none
- out:  *.sharefile*.eu    # type: url # max: none
- out:  Enterprise Sync, ShareFile Desktop for Mac, ShareFile Desktop Widget    # type: downloadable_executables # max: none
- out:  citrixworkflows.sharefile.eu    # type: url # max: none
- out:  http://(subdomain).sharefile.com/rest/    # type: url # max: none
- out:  citrixworkflows.sharefile.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $541,249
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
