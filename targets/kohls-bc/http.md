# Kohls

> Platform: Bugcrowd — https://bugcrowd.com/engagements/kohls
> Type: VDP
> Bounty: P1 $3000–$4500 | P2 $2000–$3000 | P3 $300–$1500 | P4 $100–$300
> Status: In progress (started Apr 10, 2018)

## Scope

- in:  https://www.kohls.com   # type: url
- in:  https://www.kohls.com/feature/app.jsp   # type: url
- out: apply.kohls.com   # type: domain
- out: *kohls.com/kohlscredit/prequal   # type: wildcard
- out: *kohlsecommerce.com/kohlscredit/prequal   # type: wildcard
- out: corporate.kohls.com   # type: domain
- out: productchampions.kohls.com   # type: domain
- out: link-preprod.kohls.com   # type: domain
- out: developer.kohls.com   # type: domain
- out: lclive.kohls.com   # type: domain
- out: author-mykohls.kohls.com   # type: domain
- out: mykohls-origin.kohls.com   # type: domain
- out: origin-stage65-corporate.kohls.com   # type: domain
- out: origin-stage65-mykohls.kohls.com   # type: domain
- out: author-stage65-mykohls.kohls.com   # type: domain
- out: stage65-corporate.kohls.com   # type: domain
- out: stage65-mykohls.kohls.com   # type: domain
- out: author-qa65-mykohls.kohls.com   # type: domain
- out: mykohls.kohls.com   # type: domain
- out: *kohls.com/feature/pre-qual/prequal_inquiry.jsp   # type: wildcard
- out: *kohls.com/checkout/prequal_inquiry.jsp   # type: wildcard
- out: *kohlsecommerce.com/feature/pre-qual/prequal_inquiry.jsp   # type: wildcard
- out: *kohlsecommerce.com/checkout/prequal_inquiry.jsp   # type: wildcard
- out: vp-*.kohls.com   # type: domain
- out: *qa*.kohls.com   # type: wildcard
- out: wfh*.kohls.com   # type: domain
- out: kconnect.kohls.com   # type: domain
- out: connection.kohls.com   # type: domain
- out: kohlsmerch.kohls.com/   # type: domain
- out: http://www.b2b.kohls.com   # type: url

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- safe harbor: yes
- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
