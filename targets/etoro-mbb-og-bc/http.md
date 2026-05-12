# eToro Managed Bug Bounty Engagement

> Platform: Bugcrowd — https://bugcrowd.com/engagements/etoro-mbb-og
> Type: BBP | Expedited triage
> Bounty: P1 $6,000–$15,000 | P2 $1,500–$6,000 | P3 $500–$1,000 | P4 $100–$500
> Status: In Progress | Started: Mar 03 2026
> Last scope update: 27 Mar 2026

## Scope

- in:  www.etoro.com                                        # type: domain
- in:  watchlistapi.etoro.com                               # type: domain
- in:  wallet.etoro.com                                     # type: domain
- in:  uapi-front.etoro.com                                 # type: domain
- in:  tapi-real.etoro.com                                  # type: domain
- in:  tapi-demo.etoro.com                                  # type: domain
- in:  sts.etoro.com                                        # type: domain
- in:  streams.etoro.com                                    # type: domain
- in:  rankings.etoro.com                                   # type: domain
- in:  r.etoro.com                                          # type: domain
- in:  push-real-hk-lightstreamer.cloud.etoro.com           # type: domain
- in:  push-n-hap.cloud.etoro.com                           # type: domain
- in:  push-lightstreamer.cloud.etoro.com                   # type: domain
- in:  push-hap.cloud.etoro.com                             # type: domain
- in:  push-dn-hap.cloud.etoro.com                          # type: domain
- in:  push-demo-lightstreamer.cloud.etoro.com              # type: domain
- in:  push-demo-hk-lightstreamer.cloud.etoro.com           # type: domain
- in:  push-d-hap.cloud.etoro.com                           # type: domain
- in:  push-d-gw.cloud.etoro.com                            # type: domain
- in:  partners.etoro.com                                   # type: domain
- in:  kyc.etoro.com                                        # type: domain
- in:  kyc-src.etoro.com                                    # type: domain
- in:  io.getdelta.ios                                      # type: ios_app
- in:  io.getdelta.android                                  # type: android_app
- in:  etoropartners.com                                    # type: domain
- in:  etorologsapi.etoro.com                               # type: domain
- in:  delta.app                                            # type: domain
- in:  com.etoro.wallet (iOS + Android)                     # type: ios_app
- in:  com.etoro.openbook (iOS + Android)                   # type: ios_app
- in:  charts.etoro.com                                     # type: domain
- in:  cashier.etoro.com                                    # type: domain
- in:  cashier-src.etoro.com                                # type: domain
- in:  candle.etoro.com                                     # type: domain
- in:  candle-src.etoro.com                                 # type: domain
- in:  billing.etoro.com                                    # type: domain
- in:  billing-pci.etoro.com                                # type: domain
- in:  api.etoro.com                                        # type: api
- in:  aggregator.etoro.com                                 # type: domain
- in:  templates.etoro.com                                  # type: domain
- in:  etorox.com                                           # type: domain
- in:  api-portal.etoro.com                                 # type: api
- out: any eToro domain not listed above                    # type: wildcard

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL    # use @bugcrowdninja.com email for testing
- note: register at https://www.etoro.com using @bugcrowdninja.com address

## Notes

- payout speed: validation within 3 days
- status: ACTIVE
- Finance industry; social trading / investment platform
- Safe harbor: yes (CFAA + DMCA exemptions)
- request header required: X-Bug-Bounty:<bugcrowdusername>
- out-of-scope: Clickjacking/CORS on mobile (Cordova framework), Facebook SDK, WP low/medium, rate-limit, CSRF on login/logout, username enumeration, self-XSS, MITM-only attacks
- subdomain takeover treated as Low (minimum bounty only, until further notice)
- N-day policy: in-scope 30 days after public release
- no automated mass requests / stress testing
- file upload bugs in scope but max 75 files per test
- do not interact with other accounts without written consent
- record IP, user-agent, and usernames before testing (may be requested)

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
