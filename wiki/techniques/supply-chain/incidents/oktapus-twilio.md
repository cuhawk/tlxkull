---
title: 0ktapus / Scatter Swine: Twilio + Signal (Aug 2022)
slug: oktapus-twilio
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, technique/sms-phishing, technique/aitm-phishing, surface/idp, surface/sms-gateway, actor/0ktapus]
inbound: []
---

# 0ktapus / Scatter Swine: Twilio + Signal (Aug 2022)

## What happened

Between 2022-08-04 and 2022-08-08 an actor tracked as **0ktapus**
(Group-IB) / **Scatter Swine** (Okta) ran an SMS-phishing campaign
against Twilio employees. Targets received an SMS impersonating
Twilio IT (`twilio-okta.com`, `sso-twilio.com`, etc.) directing them
to a credential-harvest portal that mimicked the Twilio Okta SSO
login. Employees who entered credentials and approved the subsequent
push-MFA prompt handed the attacker a live session into Twilio's
internal admin console.

Inside Twilio the attacker pivoted to two downstream products. From
**Authy** (Twilio's 2FA app), they re-registered devices on **93
Authy accounts** (out of ~75M users). From **Signal's SMS-verify
backend** (Signal contracts Twilio for phone-number verification),
they accessed **1,900 Signal user phone numbers** and re-registered
**6 specific accounts** to attacker-controlled devices. Group-IB
later tied the same kit to attempted compromises of **130+
organisations** -- Cloudflare publicly reported the same SMS landing
on its employees but the attack failed because Cloudflare had
mandatory FIDO2 hardware keys.

## Attack chain

1. **Target enumeration.** Scatter Swine pre-bought employee mobile
   numbers from data brokers (LinkedIn-scrape sellers,
   PeopleDataLabs-style aggregators) keyed by employer.
2. **SMS bait.** Look-alike domains served a faithful clone of the
   target's Okta SSO portal in real time. Common bait text: "Your
   schedule changed, log in to confirm" / "Password expires in 24h".
3. **AiTM credential relay.** The phishing page was an
   **adversary-in-the-middle proxy** -- as the victim typed
   credentials, the kit replayed them to the real Okta tenant in
   parallel. Push-MFA approval on the victim's phone elevated the
   attacker's parallel session.
4. **Internal pivot.** Once inside Twilio's admin console the actor
   searched the customer database for downstream identity products --
   Authy registrations and Signal verification jobs -- and made
   programmatic changes to device registrations.
5. **Cross-tenant lateral attack.** Twilio is the SMS pipe for Okta
   one-time-code delivery, so the same access leaked Okta OTPs in
   transit for ~163 Twilio customer tenants. The campaign was a
   *cascade*: one phish -> SMS gateway -> downstream IdP -> downstream
   apps.
6. **FIDO2 saved Cloudflare.** Cloudflare's published response shows
   the same SMS, same domain pattern, same push-MFA attempt -- defeated
   by hardware keys that perform origin-bound signature. The kit had
   no answer.

## Lessons for bug hunters

- **Push-MFA is not phishing-resistant.** Any target whose login flow
  has an "approve push" step is one AiTM proxy away from session
  takeover. When auditing IdP integrations look for the **`origin`
  binding** -- is the authenticator response bound to the origin the
  user actually visited? If not, write that up.
- **SMS gateway tenancy is a supply-chain attack surface.** When
  your target uses Twilio/Vonage/Plivo/Sinch for OTP delivery, ask:
  who at the gateway can re-route an SMS? Who can read message
  content? The gateway admin console is a real asset, often
  out-of-scope on the target's program but in-scope on the gateway's
  own.
- **Look-alike domain registrations are an early warning.** Tools
  like `urlinsane`, `dnstwist`, and CertStream are cheap. A target
  whose program rewards reports of typo-domains targeting their
  employees has implicitly extended the perimeter.
- **AiTM-resistant MFA is a control to enumerate in scope notes.**
  When triaging a target, grep their auth pages for
  `navigator.credentials.get({publicKey: ...})` (WebAuthn) vs TOTP/SMS
  input fields. A target on TOTP/SMS-only is a softer perimeter.
  Cross-link [[fido2-origin-binding]].
- **Cascade impact pays better than single-target impact.** A finding
  that proves *one* phish-able support tool reaches *N* downstream
  tenants is paid as critical, not high. Document the cascade in your
  PoC with a clear graph. Compare to [[okta-lapsus]].

## Primary sources

- [Group-IB: Roasting 0ktapus -- the phishing campaign going after Okta](https://www.group-ib.com/blog/0ktapus/)
  -- the original IoC dump and kit reverse-engineering write-up.
- [Twilio: Incident Report -- August 4, 2022 (Twilio blog)](https://www.twilio.com/blog/august-2022-social-engineering-attack)
  -- official Twilio post-mortem listing the 163 customer tenants and
  the Authy/Signal downstream impact.

## Related

- [[okta-lapsus]]
- [[fido2-origin-binding]]
- [[ms-storm-0558]]
