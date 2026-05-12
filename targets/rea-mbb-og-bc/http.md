# REA Group | realestate.com.au, realcommercial.com.au, property.com.au

> Platform: Bugcrowd — https://bugcrowd.com/engagements/rea-mbb-og
> Type: BBP
> Bounty: P1 $3500–$4500 | P2 $1500–$2500 | P3 $500–$750 | P4 $50–$200
> Status: In progress (started Dec 05, 2024)

## Scope

- in:  rea-group.com   # type: domain
- in:  reastatic.net   # type: domain
- in:  *.api.id.realestate.com.au   # type: wildcard
- in:  *.id.realestate.com.au   # type: wildcard
- in:  *.accounts.realestate.com.au   # type: wildcard
- in:  https://play.google.com/store/apps/details?id=au.com.realestate.app   # type: android_app
- in:  https://apps.apple.com/au/app/realestate-com-au-property/id404667893   # type: ios_app
- in:  *.realestate.com.au   # type: wildcard
- in:  *.realcommercial.com.au   # type: wildcard
- in:  www.property.com.au   # type: domain
- in:  next.flatmates.com.au   # type: domain
- in:  api-next.flatmates.com.au   # type: domain
- out: *.email.rea-group.com   # type: wildcard
- out: autodiscover.rea-group.com   # type: domain
- out: garage.rea-group.com   # type: domain
- out: help.enterprise.rea-group.com   # type: domain
- out: help.rea-group.com   # type: domain
- out: university.rea-group.com   # type: domain
- out: analytics[.e2e].realestate.com.au   # type: domain
- out: *.realestate.com.au/homeloans   # type: wildcard
- out: homeloans.realestate.com.au   # type: domain
- out: realestate.com.au/advice   # type: domain
- out: realestate.com.au/insights   # type: domain
- out: realestate.com.au/lifestyle   # type: domain
- out: realestate.com.au/news   # type: domain
- out: realestate.com.au/podcasts   # type: domain
- out: sasinator.realestate.com.au   # type: domain
- out: smetrics.realestate.com.au   # type: domain
- out: video.realestate.com.au   # type: domain
- out: help.realestate.com.au   # type: domain
- out: *.propertypanel.realestate.com.au   # type: wildcard
- out: realtair-sell.realestate.com.au   # type: domain
- out: realtair-buy.realestate.com.au   # type: domain
- out: *.realtair.realestate.com.au   # type: wildcard
- out: adslot.realestate.com.au   # type: domain
- out: everest.realestate.com.au   # type: domain
- out: images.media-comms.realestate.com.au   # type: domain
- out: images.mediateam.realestate.com.au   # type: domain
- out: metrics.realestate.com.au   # type: domain
- out: stg-api.realtair.gateway.ignite.realestate.com.au   # type: domain
- out: support.realestate.com.au   # type: domain
- out: stg-pitch.realtair.gateway.ignite.realestate.com.au   # type: domain
- out: tags.realestate.com.au   # type: domain
- out: api.leads.developersites.devlob-staging.realestate.com.au   # type: domain
- out: *.agent.realcommercial.com.au   # type: wildcard
- out: *.email.realcommercial.com.au   # type: wildcard
- out: abmail.campaign.realcommercial.com.au   # type: domain
- out: autodiscover.realcommercial.com.au   # type: domain
- out: metrics.realcommercial.com.au   # type: domain
- out: propertypanelcontent.realcommercial.com.au   # type: domain
- out: realcommercial.com.au/building/enquiry   # type: domain
- out: realcommercial.com.au/contact-agency-commercial/*   # type: domain
- out: realcommercial.com.au/listing-ui/enquiry   # type: domain
- out: realcommercial.com.au/mobile/enquiries/*/*   # type: domain
- out: research.surveys.realcommercial.com.au   # type: domain
- out: smetrics.realcommercial.com.au   # type: domain
- out: support.realcommercial.com.au   # type: domain
- out: propertypanel.realcommercial.com.au   # type: domain
- out: autodiscover.property.com.au   # type: domain
- out: email.property.com.au   # type: domain
- out: help.property.com.au   # type: domain
- out: info.property.com.au   # type: domain
- out: *.mortgagechoice.com.au   # type: wildcard
- out: *.realtair.com   # type: wildcard
- out: *.campaignagent.com.au   # type: wildcard
- out: *.simpology.com.au   # type: wildcard
- out: *.athena.com.au   # type: wildcard
- out: *.housing.com   # type: wildcard
- out: *.proptiger.com   # type: wildcard
- out: *.makaan.com   # type: wildcard
- out: *.easiloan.com   # type: wildcard
- out: *.proptrack.com.au   # type: wildcard
- out: *.realtor.com   # type: wildcard
- out: *.proptrack.com   # type: wildcard
- out: *.spacely.com.au   # type: wildcard
- out: *.flatmates.com.au   # type: wildcard
- out: www.flatmates.com.au   # type: domain
- out: api.flatmates.com.au   # type: domain
- out: flatmates-experience-api.flatmates.com.au   # type: domain
- out: help.flatmates.com.au   # type: domain
- out: email.flatmates.com.au   # type: domain
- out: sasinator.flatmates.com.au   # type: domain

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

## Flatmates Staging Access

Required headers for next.flatmates.com.au access:
- bugcrowd-id: <your Bugcrowd email OR user ID>
- flatmates-bugcrowd: E277D811-7BE0-4DC1-BDF8-C3B9394E5C69

Test card for payment: 4242 4242 4242 4242 / exp 04/26 / CVV 424
DB wiped nightly — recreate accounts each session.
Server down 4-8 AM AEST; search unavailable 4-9 AM AEST.

## Testing Notes

- Use @bugcrowdninja.com email when signing up
- Include "Test" or "Bugcrowd" in form submissions
- DNI: renters, brokers, agents, property managers, REA employees, third parties
- No automated scripts (Burp Intruder etc.) on forms
- CNAME records to other domains: stay in-scope only
- Anti-bot/WAF active; 429 or blank page = blocked
- Only www.property.com.au in scope for PCA (not *.property.com.au)
- Production flatmates.com.au NOT in scope (staging only)
