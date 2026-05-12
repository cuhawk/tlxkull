# Truecaller 

> Platform: HackerOne — https://hackerone.com/truecaller
> Type: BBP
> Bounty: Low $250 | Medium $750 | High $3,000 | Critical $6,000
> Avg bounty: $300–$400
> Response efficiency: 100% | Avg first response: N/A | Total paid: $24,220
> Last scope update: 2024-12-06

## Scope

- in:  *-asia-south1.truecaller.com    # type: wildcard # max: critical
- in:  *-eu.truecaller.com    # type: wildcard # max: critical
- in:  *-noneu.truecaller.com    # type: wildcard # max: critical
- in:  business.truecaller.com    # type: url # max: critical
- in:  web.truecaller.com    # type: url # max: high
- in:  www.truecaller.com    # type: url # max: high
- in:  business-resources.truecaller.com    # type: url # max: medium
- in:  com.truecaller    # type: android_app # max: critical
- in:  448142450    # type: ios_app # max: critical
- in:  url-metadata-noneu.truecaller.com    # type: url # max: critical
- in:  user-archive-asia-south1.truecaller.com    # type: url # max: critical
- in:  valid-names-noneu.truecaller.com    # type: url # max: critical
- in:  verification-noneu.truecaller.com    # type: url # max: critical
- in:  video-callerid-noneu.truecaller.com    # type: url # max: critical
- in:  voip-asia-south1.truecaller.com    # type: url # max: critical
- in:  web-consent-noneu.truecaller.com    # type: url # max: critical
- in:  webdirectory-noneu.truecaller.com    # type: url # max: critical
- in:  webonboarding-noneu.truecaller.com    # type: url # max: critical
- in:  account-onboarding-eu.truecaller.com    # type: url # max: critical
- in:  ads-segment-profile-eu.truecaller.com    # type: url # max: critical
- in:  apple-subscription-monitor-eu.truecaller.com    # type: url # max: critical
- in:  comments-eu.truecaller.com    # type: url # max: critical
- in:  company-profile-eu.truecaller.com    # type: url # max: critical
- in:  contact-lists-eu.truecaller.com    # type: url # max: critical
- in:  contact-request-stateless-eu.truecaller.com    # type: url # max: critical
- in:  email-verification-eu.truecaller.com    # type: url # max: critical
- in:  enterprise-auth-eu.truecaller.com    # type: url # max: critical
- in:  insights-categorizer-eu.truecaller.com    # type: url # max: critical
- in:  insights-registry-eu.truecaller.com    # type: url # max: critical
- in:  messenger-eu.truecaller.com    # type: url # max: critical
- in:  messenger-previews-eu.truecaller.com    # type: url # max: critical
- in:  messenger-web-eu.truecaller.com    # type: url # max: critical
- in:  messenger-web-relay-compat-eu.truecaller.com    # type: url # max: critical
- in:  messenger-web-relay-eu.truecaller.com    # type: url # max: critical
- in:  messenger-web-relay-europe-west4.truecaller.com    # type: url # max: critical
- in:  otp-callback-eu.truecaller.com    # type: url # max: critical
- in:  partner-account-eu.truecaller.com    # type: url # max: critical
- in:  phone-gateway-eu.truecaller.com    # type: url # max: critical
- in:  premium-eu.truecaller.com    # type: url # max: critical
- in:  presence-grpc-eu.truecaller.com    # type: url # max: critical
- in:  push-callerid-eu.truecaller.com    # type: url # max: critical
- in:  request3-eu.truecaller.com    # type: url # max: critical
- in:  search-warnings-eu.truecaller.com    # type: url # max: critical
- in:  subscription-monitor-eu.truecaller.com    # type: url # max: critical
- in:  survey-eu.truecaller.com    # type: url # max: critical
- in:  truehelper-eu.truecaller.com    # type: url # max: critical
- in:  unlist5-eu.truecaller.com    # type: url # max: critical
- in:  unwanted-communication-extension-eu.truecaller.com    # type: url # max: critical
- in:  valid-names-eu.truecaller.com    # type: url # max: critical
- in:  verification-eu.truecaller.com    # type: url # max: critical
- in:  video-callerid-eu.truecaller.com    # type: url # max: critical
- in:  webdirectory-eu.truecaller.com    # type: url # max: critical
- in:  webonboarding-eu.truecaller.com    # type: url # max: critical
- in:  openid-noneu.truecaller.com    # type: url # max: critical
- in:  opt-out-noneu.truecaller.com    # type: url # max: critical
- in:  otp-callback-noneu.truecaller.com    # type: url # max: critical
- in:  outline-asia-south1.truecaller.com    # type: url # max: critical
- in:  outline-noneu.truecaller.com    # type: url # max: critical
- in:  partner-account-asia-south1.truecaller.com    # type: url # max: critical
- in:  partner-account-noneu.truecaller.com    # type: url # max: critical
- in:  partners-search.truecaller.com    # type: url # max: critical
- in:  phone-gateway-noneu.truecaller.com    # type: url # max: critical
- in:  phonebook5-asia-south1.truecaller.com    # type: url # max: critical
- in:  phonebook5.truecaller.com    # type: url # max: critical
- in:  pixel-noneu.truecaller.com    # type: url # max: critical
- in:  pixel.truecaller.com    # type: url # max: critical
- in:  placement-rules-noneu.truecaller.com    # type: url # max: critical
- in:  premium-noneu.truecaller.com    # type: url # max: critical
- in:  presence-grpc-noneu.truecaller.com    # type: url # max: critical
- in:  presence-grpc.truecaller.com    # type: url # max: critical
- in:  profile-view-asia-south1.truecaller.com    # type: url # max: critical
- in:  profile-view.truecaller.com    # type: url # max: critical
- in:  profile4-asia-south1.truecaller.com    # type: url # max: critical
- in:  profile4.truecaller.com    # type: url # max: critical
- in:  push-callerid-noneu.truecaller.com    # type: url # max: critical
- in:  pushid-asia-south1.truecaller.com    # type: url # max: critical
- in:  recommended-contacts-noneu.truecaller.com    # type: url # max: critical
- in:  referrals-asia-south1.truecaller.com    # type: url # max: critical
- in:  request3-asia-south1.truecaller.com    # type: url # max: critical
- in:  request3-noneu.truecaller.com    # type: url # max: critical
- in:  sdk-apps-noneu.truecaller.com    # type: url # max: critical
- in:  sdk-otp-verification-noneu.truecaller.com    # type: url # max: critical
- in:  search-external-features-asia-south1.truecaller.com    # type: url # max: critical
- in:  search-external-features-noneu.truecaller.com    # type: url # max: critical
- in:  search-warnings-asia-south1.truecaller.com    # type: url # max: critical
- in:  search-warnings-noneu.truecaller.com    # type: url # max: critical
- in:  search5-asia-south1.truecaller.com    # type: url # max: critical
- in:  search5.truecaller.com    # type: url # max: critical
- in:  stores-api-noneu.truecaller.com    # type: url # max: critical
- in:  survey-asia-south1.truecaller.com    # type: url # max: critical
- in:  survey-noneu.truecaller.com    # type: url # max: critical
- in:  tagging5-asia-south1.truecaller.com    # type: url # max: critical
- in:  telecom-operator-data-asia-south1.truecaller.com    # type: url # max: critical
- in:  telecom-operator-data-noneu.truecaller.com    # type: url # max: critical
- in:  telecom-operator-data.truecaller.com    # type: url # max: critical
- in:  topspammers-asia-south1.truecaller.com    # type: url # max: critical
- in:  truehelper-noneu.truecaller.com    # type: url # max: critical
- in:  unlist5-asia-south1.truecaller.com    # type: url # max: critical
- in:  unlist5-noneu.truecaller.com    # type: url # max: critical
- in:  unlist5.truecaller.com    # type: url # max: critical
- in:  unwanted-communication-extension-noneu.truecaller.com    # type: url # max: critical
- in:  upload3-asia-south1.truecaller.com    # type: url # max: critical
- in:  upload3-noneu.truecaller.com    # type: url # max: critical
- in:  batchlogging4.truecaller.com    # type: url # max: critical
- in:  callkit-asia-south1.truecaller.com    # type: url # max: critical
- in:  comments-asia-south1.truecaller.com    # type: url # max: critical
- in:  comments-noneu.truecaller.com    # type: url # max: critical
- in:  company-profile-asia-south1.truecaller.com    # type: url # max: critical
- in:  company-profile-noneu.truecaller.com    # type: url # max: critical
- in:  contact-lists-noneu.truecaller.com    # type: url # max: critical
- in:  contact-request-stateless-noneu.truecaller.com    # type: url # max: critical
- in:  contact-upload4-asia-south1.truecaller.com    # type: url # max: critical
- in:  contact-upload4.truecaller.com    # type: url # max: critical
- in:  device-safety-asia-south1.truecaller.com    # type: url # max: critical
- in:  duo-eu.truecaller.com    # type: url # max: critical
- in:  duo-invite-eu.truecaller.com    # type: url # max: critical
- in:  duo-invite-noneu.truecaller.com    # type: url # max: critical
- in:  duo-invite.truecaller.com    # type: url # max: critical
- in:  duo-noneu.truecaller.com    # type: url # max: critical
- in:  duo.truecaller.com    # type: url # max: critical
- in:  edge-locations5.truecaller.com    # type: url # max: critical
- in:  email-verification-noneu.truecaller.com    # type: url # max: critical
- in:  enterprise-account-management-noneu.truecaller.com    # type: url # max: critical
- in:  enterprise-accounts-noneu.truecaller.com    # type: url # max: critical
- in:  enterprise-auth-noneu.truecaller.com    # type: url # max: critical
- in:  enterprise-bizengage-noneu.truecaller.com    # type: url # max: critical
- in:  enterprise-biznumbers-noneu.truecaller.com    # type: url # max: critical
- in:  enterprise-feedback-noneu.truecaller.com    # type: url # max: critical
- in:  enterprise-portal-noneu.truecaller.com    # type: url # max: critical
- in:  enterprise-reports-noneu.truecaller.com    # type: url # max: critical
- in:  enterprise-service-management-noneu.truecaller.com    # type: url # max: critical
- in:  enterprise-survey-asia-south1.truecaller.com    # type: url # max: critical
- in:  enterprise-survey-noneu.truecaller.com    # type: url # max: critical
- in:  enterprise-userfeedback-noneu.truecaller.com    # type: url # max: critical
- in:  enterprise-webhooks-noneu.truecaller.com    # type: url # max: critical
- in:  feedback-asia-south1.truecaller.com    # type: url # max: critical
- in:  filter-store4-asia-south1.truecaller.com    # type: url # max: critical
- in:  filter-store4.truecaller.com    # type: url # max: critical
- in:  images-asia-south1.truecaller.com    # type: url # max: critical
- in:  images.truecaller.com    # type: url # max: critical
- in:  insights-categorizer-noneu.truecaller.com    # type: url # max: critical
- in:  leadgen-asia-south1.truecaller.com    # type: url # max: critical
- in:  messenger-previews-asia-south1.truecaller.com    # type: url # max: critical
- in:  messenger-previews-noneu.truecaller.com    # type: url # max: critical
- in:  messenger-previews.truecaller.com    # type: url # max: critical
- in:  messenger-web-relay-compat-noneu.truecaller.com    # type: url # max: critical
- in:  messenger-web-relay-noneu.truecaller.com    # type: url # max: critical
- in:  nationalidverification-noneu.truecaller.com    # type: url # max: critical
- in:  notifications5-asia-south1.truecaller.com    # type: url # max: critical
- in:  notifications5.truecaller.com    # type: url # max: critical
- in:  oauth-account-asia-south1.truecaller.com    # type: url # max: critical
- in:  oauth-portal-asia-south1.truecaller.com    # type: url # max: critical
- in:  oauth-portal-noneu.truecaller.com    # type: url # max: critical
- in:  account-noneu.truecaller.com    # type: url # max: critical
- in:  account-onboarding-noneu.truecaller.com    # type: url # max: critical
- in:  ads-audience-ingestion-noneu.truecaller.com    # type: url # max: critical
- in:  ads-audience-uploader.truecaller.com    # type: url # max: critical
- in:  ads-config-engine-noneu.truecaller.com    # type: url # max: critical
- in:  ads-partner-noneu.truecaller.com    # type: url # max: critical
- in:  ads-rules-asia-south1.truecaller.com    # type: url # max: critical
- in:  ads-rules-noneu.truecaller.com    # type: url # max: critical
- in:  ads5-asia-south1.truecaller.com    # type: url # max: critical
- in:  api4-asia-south1.truecaller.com    # type: url # max: critical
- in:  apigw-noneu.truecaller.com    # type: url # max: critical
- in:  assure-noneu.truecaller.com    # type: url # max: critical
- in:  audience-uploader-asia-south1.truecaller.com    # type: url # max: critical
- in:  audience-uploader-noneu.truecaller.com    # type: url # max: critical
- in:  audience-uploader.truecaller.com    # type: url # max: critical
- in:  auth4-asia-south1.truecaller.com    # type: url # max: critical
- in:  auth4-noneu.truecaller.com    # type: url # max: critical
- in:  backup.truecaller.com    # type: url # max: critical
- in:  api4-noneu.truecaller.com    # type: url # max: critical
- in:  api4.truecaller.com    # type: url # max: critical
- in:  search5-noneu.truecaller.com    # type: url # max: critical
- in:  account-eu.truecaller.com    # type: url # max: critical
- in:  ads5-eu.truecaller.com    # type: url # max: critical
- in:  api4-eu.truecaller.com    # type: url # max: critical
- in:  backup-eu.truecaller.com    # type: url # max: critical
- in:  batchlogging4-eu.truecaller.com    # type: url # max: critical
- in:  callkit-eu.truecaller.com    # type: url # max: critical
- in:  callmeback-eu.truecaller.com    # type: url # max: critical
- in:  contact-request-eu.truecaller.com    # type: url # max: critical
- in:  contact-upload4-eu.truecaller.com    # type: url # max: critical
- in:  device-safety-eu.truecaller.com    # type: url # max: critical
- in:  edge-locations5-eu.truecaller.com    # type: url # max: critical
- in:  feedback-eu.truecaller.com    # type: url # max: critical
- in:  filter-store4-eu.truecaller.com    # type: url # max: critical
- in:  flash-eu.truecaller.com    # type: url # max: critical
- in:  images-eu.truecaller.com    # type: url # max: critical
- in:  lastactivity-eu.truecaller.com    # type: url # max: critical
- in:  leadgen-eu.truecaller.com    # type: url # max: critical
- in:  notifications5-eu.truecaller.com    # type: url # max: critical
- in:  opt-out-eu.truecaller.com    # type: url # max: critical
- in:  phonebook5-eu.truecaller.com    # type: url # max: critical
- in:  premium-se1.truecaller.com    # type: url # max: critical
- in:  profile-view-eu.truecaller.com    # type: url # max: critical
- in:  profile4-eu.truecaller.com    # type: url # max: critical
- out:  community.truecaller.com    # type: url # max: none
- out:  adsmanager.truecaller.com    # type: url # max: none
- out:  support.truecaller.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $24,220
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
