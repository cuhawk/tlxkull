# Twilio

> Platform: HackerOne — https://hackerone.com/twilio
> Type: BBP | Self-managed | Standard safe harbor
> Bounty: $50 - $8000 | Response efficiency: 87%
> Last scope update: March 28, 2026

## Scope

- in:  Twilio APIs   # type: api
- in:  static*.twilio.com   # type: wildcard
- in:  smtp.sendgrid.net   # type: other
- in:  signup.sendgrid.com   # type: domain
- in:  sendgrid.com   # type: domain
- in:  mc.sendgrid.com   # type: domain
- in:  https://www.twilio.com/login   # type: url
- in:  https://www.twilio.com/en-us/blog/get-started-webrtc   # type: other
- in:  https://www.twilio.com/docs/verify/api   # type: api
- in:  https://www.twilio.com/docs/libraries   # type: other
- in:  https://www.twilio.com/docs/authy/api   # type: api
- in:  https://www.authy.com/download/ (Android)   # type: android_app
- in:  https://www.authy.com/download/ (iOS)   # type: ios_app
- in:  https://segment.com/docs/connections/sources/   # type: url
- in:  http://twilio.com/blog   # type: url
- in:  http://tsock.us1.twilio.com   # type: url
- in:  http://help.twilio.com   # type: url
- in:  app.sendgrid.com   # type: domain
- in:  app.segment.com   # type: domain
- in:  api.twilio.com   # type: api
- in:  api.sendgrid.com   # type: domain
- in:  api.segment.io   # type: api
- in:  Any host/web property verified to be owned by Twilio et al.   # type: other
- in:  *.sip.*.twilio.com   # type: wildcard
- out: zipwhip.com   # type: domain
- out: Ytica and its assets   # type: other
- out: webinars.twilio.com   # type: domain
- out: webinars.segment.com   # type: domain
- out: TwimlBins   # type: other
- out: twiliotraining.com   # type: domain
- out: Twilio Wireless   # type: other
- out: Twilio Quest   # type: other
- out: twil.io   # type: domain
- out: transform.twilio.com   # type: domain
- out: Third-party services   # type: other
- out: talks.twilio.com   # type: domain
- out: surveys.twilio.com   # type: domain
- out: support.twilio.com   # type: domain
- out: support.sendgrid.com   # type: domain
- out: store.twilio.com   # type: domain
- out: status.twilio.com   # type: domain
- out: status.sendgrid.com   # type: domain
- out: status.segment.com   # type: domain
- out: signal.twilio.com   # type: domain
- out: lab.authy.com   # type: domain
- out: jobs.twilio.com   # type: domain
- out: http://twilio.com/labs   # type: url
- out: http://twilio.com/en-us/company/jobs   # type: url
- out: http://segment.com/jobs   # type: url
- out: http://segment.com/contact   # type: url
- out: http://events.cdpweek.com   # type: url
- out: http://apjevents.twilio.com   # type: url
- out: Electric Imp and its assets   # type: other
- out: community.segment.com   # type: domain
- out: All Twilio acquisitions until explicitly noted under the in-scope targets   # type: other
- out: All Kurento domains   # type: other

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- payout speed: unknown
- Launched: Jan 2026

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
