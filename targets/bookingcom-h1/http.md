# Booking.com

> Platform: HackerOne — https://hackerone.com/bookingcom
> Type: BBP
> Bounty: Low $150 | Medium $500 | High $1,500 | Critical $3,000
> Avg bounty: $350–$500
> Response efficiency: 94% | Avg first response: N/A | Total paid: $700,000
> Last scope update: 2025-07-15

## Scope

- in:  *.fareharbor.com    # type: wildcard # max: critical
- in:  *.booking.com    # type: wildcard # max: critical
- in:  *.rentalcars.com    # type: wildcard # max: critical
- in:  *.fareharbor.engineering    # type: wildcard # max: critical
- in:  booking.com    # type: url # max: critical
- in:  secure.booking.com    # type: url # max: critical
- in:  careers.booking.com    # type: url # max: critical
- in:  https://iphone-xml.booking.com/json/    # type: url # max: critical
- in:  https://secure-iphone-xml.booking.com/json/    # type: url # max: critical
- in:  account.booking.com    # type: url # max: critical
- in:  kyc-onboarding.booking.com    # type: url # max: critical
- in:  taxi.booking.com    # type: url # max: critical
- in:  widget.rentalcars.com    # type: url # max: critical
- in:  cars.booking.com    # type: url # max: critical
- in:  supplier.auth.toag.booking.com    # type: url # max: critical
- in:  paymentcomponent.booking.com    # type: url # max: critical
- in:  metasearch-api.booking.com    # type: url # max: critical
- in:  experiences.booking.com    # type: url # max: critical
- in:  webhooks.booking.com    # type: url # max: critical
- in:  taxis.booking.com    # type: url # max: critical
- in:  paybridge.booking.com    # type: url # max: critical
- in:  phone-validation.taxi.booking.com    # type: url # max: critical
- in:  indicative-pricing.taxi.booking.com    # type: url # max: critical
- in:  admin.booking.com    # type: url # max: critical
- in:  chat.booking.com    # type: url # max: critical
- in:  autocomplete.booking.com    # type: url # max: critical
- in:  distribution-xml.booking.com    # type: url # max: critical
- in:  paynotifications.booking.com    # type: url # max: critical
- in:  supply-xml.booking.com    # type: url # max: critical
- in:  accommodations.booking.com    # type: url # max: critical
- in:  portal.taxi.booking.com    # type: url # max: critical
- in:  flights.booking.com    # type: url # max: critical
- in:  secure-supply-xml.booking.com    # type: url # max: critical
- in:  http://secure-iphone-xml.booking.com/json/    # type: url # max: critical
- in:  spark.fareharbor.com    # type: url # max: critical
- in:  www.fareharbor.com    # type: url # max: critical
- in:  teleport.fareharbor.engineering    # type: url # max: critical
- in:  demo.fareharbor.com    # type: url # max: critical
- in:  readonly.fareharbor.com    # type: url # max: critical
- in:  marketing.fareharbor.com    # type: url # max: critical
- in:  sites.fareharbor.com    # type: url # max: critical
- in:  compass.fareharbor.com    # type: url # max: critical
- in:  fhdn.fareharbor.com    # type: url # max: critical
- in:  tableau.fareharbor.engineering    # type: url # max: critical
- in:  fareharborsites.com    # type: url # max: critical
- in:  https://play.google.com/store/apps/details?id=com.booking&hl=en    # type: android_app # max: critical
- in:  https://play.google.com/store/apps/details?id=com.booking.hotelmanager&hl=en    # type: android_app # max: critical
- in:  https://apps.apple.com/us/app/booking-com-hotels-travel/id367003839    # type: ios_app # max: critical
- in:  https://apps.apple.com/us/app/pulse-for-booking-com-partners/id992795726    # type: ios_app # max: critical
- in:  cruises.booking.com    # type: url # max: critical
- in:  dispatch-api.rideways.com    # type: url # max: critical
- in:  *.fareharbor.me    # type: wildcard # max: critical # not eligible for bounty
- in:  com.booking    # type: android_app # max: critical
- in:  bstatic.com    # type: url # max: critical
- in:  367003839    # type: ios_app # max: critical
- in:  xsecure.rentalcars.com    # type: url # max: critical
- in:  www.rentalcars.com    # type: url # max: critical
- in:  secure.rentalcars.com    # type: url # max: critical
- in:  https://www.rentalcars.com/take-off    # type: url # max: critical
- in:  secure-distribution-xml.booking.com    # type: url # max: critical
- in:  secure-admin.booking.com    # type: url # max: critical
- in:  portal.cars.booking.com    # type: url # max: critical
- in:  chat.booking.com    # type: url # max: critical
- out:  www.booking.com/bbmanage/*    # type: wildcard # max: none
- out:  www.booking.com/bbmanage/data/*    # type: wildcard # max: none
- out:  secure.booking.com/company/*    # type: wildcard # max: none
- out:  secure.booking.com/orgnode/*    # type: wildcard # max: none
- out:  spadmin.booking.com/    # type: url # max: none
- out:  business.booking.com/    # type: url # max: none
- out:  https://www.booking.com/bbm.html    # type: url # max: none
- out:  https://secure.booking.com/companyjoin.html    # type: url # max: none
- out:  https://secure.booking.com/enterprise/signon.en-gb.html    # type: url # max: none
- out:  https://ugcupload.booking.com/upload_bbtool_company_logo    # type: url # max: none
- out:  https://fareharbor.com/demo/    # type: url # max: none
- out:  jobs.booking.com    # type: url # max: none
- out:  welcomekit.booking.com/    # type: url # max: none
- out:  cpass.booking.com    # type: url # max: none
- out:  awscpasslab.booking.com    # type: url # max: none
- out:  ams.merchandise.booking.com    # type: url # max: none
- out:  medialibrary.booking.com    # type: url # max: none
- out:  www.sustainability.booking.com    # type: url # max: none
- out:  procurement.booking.com    # type: url # max: none
- out:  workforce.booking.com    # type: url # max: none
- out:  workforce-dev.voicedqs.booking.com    # type: url # max: none
- out:  surveys.booking.com    # type: url # max: none
- out:  partnerfeedback.booking.com    # type: url # max: none
- out:  recruitmentsurveys.booking.com    # type: url # max: none
- out:  desk-demo.fareharbor.engineering    # type: url # max: none
- out:  desk-demo-api.fareharbor.engineering    # type: url # max: none
- out:  app.business.booking.com    # type: url # max: none
- out:  admin.booking.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $700,000
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
