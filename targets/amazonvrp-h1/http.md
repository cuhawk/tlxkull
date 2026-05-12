# Amazon Vulnerability Research Program

> Platform: HackerOne — https://hackerone.com/amazonvrp
> Type: BBP
> Bounty: Low $200 | Medium $600 | High $6,000 | Critical $25,000
> Avg bounty: $350–$400
> Response efficiency: 97% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2025-11-11

## Scope

- in:  *.amazon.cl    # type: wildcard # max: critical
- in:  *.amazon.co.za    # type: wildcard # max: critical
- in:  *.amazon.com.au    # type: wildcard # max: critical
- in:  *.amazon.com.br    # type: wildcard # max: critical
- in:  *.amazon.com.co    # type: wildcard # max: critical
- in:  *.amazon.com.mx    # type: wildcard # max: critical
- in:  *.amazon.com.ng    # type: wildcard # max: critical
- in:  *.amazon.com.tr    # type: wildcard # max: critical
- in:  *.amazon.pl    # type: wildcard # max: critical
- in:  *.amazon.com.be    # type: wildcard # max: critical
- in:  *.amazon.ae    # type: wildcard # max: critical
- in:  *.amazon.ca    # type: wildcard # max: critical
- in:  *.amazon.cn    # type: wildcard # max: critical
- in:  *.amazon.co.jp    # type: wildcard # max: critical
- in:  *.amazon.co.uk    # type: wildcard # max: critical
- in:  *.amazon.de    # type: wildcard # max: critical
- in:  *.amazon.eg    # type: wildcard # max: critical
- in:  *.amazon.es    # type: wildcard # max: critical
- in:  *.amazon.fr    # type: wildcard # max: critical
- in:  *.amazon.in    # type: wildcard # max: critical
- in:  *.amazon.it    # type: wildcard # max: critical
- in:  *.amazon.nl    # type: wildcard # max: critical
- in:  *.amazon.sa    # type: wildcard # max: critical
- in:  *.amazon.se    # type: wildcard # max: critical
- in:  *.amazon.sg    # type: wildcard # max: critical
- in:  *.amazon.com    # type: wildcard # max: critical
- in:  primevideo.com/*    # type: wildcard # max: critical
- in:  www.amazon.*    # type: url # max: critical
- in:  amazonpayinsurance.in    # type: url # max: critical
- in:  https://www.amazonpay.in/*    # type: other # max: critical
- in:  com.amazon.mShop.android.shopping    # type: android_app # max: critical
- in:  amazon.speech.sim    # type: android_app # max: critical
- in:  com.amazon.mShop.android.business.shopping    # type: android_app # max: critical
- in:  com.amazon.mp3    # type: android_app # max: critical
- in:  com.amazon.flex.rabbit    # type: android_app # max: critical
- in:  com.imdbtv.livingroom    # type: android_app # max: critical
- in:  com.amazon.amazonvideo.livingroom    # type: android_app # max: critical
- in:  com.amazon.mp3.automotiveOS    # type: android_app # max: critical
- in:  com.localqueen    # type: android_app # max: critical
- in:  com.amazon.helix.prod    # type: android_app # max: critical
- in:  com.amazon.tahoe.grownups    # type: android_app # max: critical
- in:  com.amazon.sft.rangoli.seller.app    # type: android_app # max: critical
- in:  com.amazon.imdb.tv.mobile.app    # type: android_app # max: critical
- in:  com.amazon.minitv.android.app    # type: android_app # max: critical
- in:  com.amazon.ziggy.android    # type: android_app # max: critical
- in:  com.amazon.music.tv    # type: android_app # max: critical
- in:  in.amazon.mShop.android.business.shopping    # type: android_app # max: critical
- in:  in.amazon.mShop.android.shopping    # type: android_app # max: critical
- in:  com.amazon.relay    # type: android_app # max: critical
- in:  com.amazon.avod.thirdpartyclient    # type: android_app # max: critical
- in:  com.amazon.sellerflexmobile    # type: android_app # max: critical
- in:  com.amazon.shopperpanel.android.mobile.app    # type: android_app # max: critical
- in:  com.amazon.vendormobile.android    # type: android_app # max: critical
- in:  com.amazon.technician.android    # type: android_app # max: critical
- in:  com.amazon.primenow.seller.android    # type: android_app # max: critical
- in:  com.amazon.vendormobile.india.android    # type: android_app # max: critical
- in:  com.amazon.sellermobile.android    # type: android_app # max: critical
- in:  com.amazon.astro    # type: android_app # max: critical
- in:  com.amazon.warhol.android    # type: android_app # max: critical
- in:  com.amazon.amazonone.androidapp    # type: android_app # max: critical
- in:  com.amazon.kisan.app    # type: android_app # max: critical
- in:  com.amazon.aba.application    # type: android_app # max: critical
- in:  com.amazon.enterprise.access.android    # type: android_app # max: critical
- in:  com.amazon.firetv.recast.blaster.aosp    # type: android_app # max: critical
- in:  com.amazon.ihm.candycane    # type: android_app # max: critical
- in:  com.amazon.swa.mobileapp    # type: android_app # max: critical
- in:  297606951    # type: ios_app # max: critical
- in:  1552455423    # type: ios_app # max: critical
- in:  1498197033    # type: ios_app # max: critical
- in:  1265170914    # type: ios_app # max: critical
- in:  510855668    # type: ios_app # max: critical
- in:  6452192521    # type: ios_app # max: critical
- in:  545519333    # type: ios_app # max: critical
- in:  1475021574    # type: ios_app # max: critical
- in:  1454725763    # type: ios_app # max: critical
- in:  1276296103    # type: ios_app # max: critical
- in:  6471528064    # type: ios_app # max: critical
- in:  1532153219    # type: ios_app # max: critical
- in:  1579372261    # type: ios_app # max: critical
- in:  1478350915    # type: ios_app # max: critical
- in:  794141485    # type: ios_app # max: critical
- in:  1494755014    # type: ios_app # max: critical
- in:  342576766    # type: ios_app # max: critical
- in:  358861688    # type: ios_app # max: critical
- in:  348712880    # type: ios_app # max: critical
- in:  374254473    # type: ios_app # max: critical
- in:  335187483    # type: ios_app # max: critical
- in:  1592204907    # type: ios_app # max: critical
- in:  6444868926    # type: ios_app # max: critical
- in:  988788863    # type: ios_app # max: critical
- in:  1057338687    # type: ios_app # max: critical
- in:  1659883691    # type: ios_app # max: critical
- in:  1151746202    # type: ios_app # max: critical
- in:  6479334468    # type: ios_app # max: critical
- in:  6560104638    # type: ios_app # max: critical
- in:  GenAI Apps under *.amazon.*    # type: other # max: critical
- in:  Other Amazon Retail Sites (Please only actively test explicitly stated scope)    # type: other # max: critical # not eligible for bounty
- in:  Other Amazon Retail Mobile Apps (Please only actively test explicitly stated scope)    # type: other # max: critical # not eligible for bounty
- in:  Amazon Subsidiaries (Please only actively test explicitly stated scope)    # type: other # max: critical # not eligible for bounty
- in:  Other Amazon Retail Assets (Please only actively test explicitly stated scope)    # type: other # max: critical # not eligible for bounty
- in:  com.immediasemi.android.blink    # type: android_app # max: critical
- in:  392988420    # type: ios_app # max: critical
- in:  926252661    # type: ios_app # max: critical
- in:  1013961111    # type: ios_app # max: critical
- in:  1023499075    # type: ios_app # max: critical
- in:  1218902777    # type: ios_app # max: critical
- in:  1068014324    # type: ios_app # max: critical
- in:  com.amazon.dee.alexaonwearos    # type: android_app # max: critical
- in:  com.eero.android    # type: android_app # max: critical
- in:  com.ring.neighborhoods    # type: android_app # max: critical
- in:  com.zappos.android.sixpmFlavor    # type: android_app # max: critical
- in:  com.zappos.android    # type: android_app # max: critical
- in:  com.ringapp    # type: android_app # max: critical
- in:  com.amazon.sellermobile.android    # type: other_apk # max: critical
- in:  flex.amazon.*    # type: url # max: critical
- in:  fresh.amazon.*    # type: url # max: critical
- in:  freight.amazon.*    # type: url # max: critical
- in:  smile.amazon.*    # type: url # max: critical
- in:  logistics.amazon.*    # type: url # max: critical
- in:  org.amazon.*    # type: url # max: critical
- in:  primenow.amazon.*    # type: url # max: critical
- in:  pay.amazon.*    # type: url # max: critical
- in:  photos.amazon.*    # type: url # max: critical
- in:  prime.amazon.*    # type: url # max: critical
- in:  manufacturing.amazon.*    # type: url # max: critical
- in:  shopbylook.amazon.*    # type: url # max: critical
- in:  https://www.amazon.com/dppui/*    # type: url # max: critical
- in:  https://www.amazon.com/gp/buy/*    # type: url # max: critical
- in:  payments.amazon.*    # type: url # max: critical
- in:  music.amazon.com    # type: url # max: critical
- in:  chat.amazon.com    # type: url # max: critical
- in:  affiliate-program.amazon.com    # type: url # max: critical
- in:  track.amazon.com    # type: url # max: critical
- in:  api.amazon.com    # type: url # max: critical
- in:  manufacturing.amazon.com    # type: url # max: critical
- in:  http://www.amazon.com/cpe/yourpayments/wallet    # type: url # max: critical
- in:  https://www.amazon.com/amazoncash    # type: url # max: critical
- in:  apay-us.amazon.com    # type: url # max: critical
- in:  aax-us-iad.amazon.com    # type: url # max: critical
- in:  aca-livecards-service.amazon.com    # type: url # max: critical
- in:  address-photos.amazon.com    # type: url # max: critical
- in:  ads-setu-proxy.amazon.com    # type: url # max: critical
- in:  alexa-comms-mobile-service-na.amazon.com    # type: url # max: critical
- in:  cloudaccesstelemetry-us-east-1.amazon.com    # type: url # max: critical
- in:  completion.amazon.com    # type: url # max: critical
- in:  data-na.amazon.com    # type: url # max: critical
- in:  dolphin.amazon.com    # type: url # max: critical
- in:  dss-na.amazon.com    # type: url # max: critical
- in:  ftvmps-na.amazon.com    # type: url # max: critical
- in:  ftvpes-na.amazon.com    # type: url # max: critical
- in:  ftvr-na.amazon.com    # type: url # max: critical
- in:  ftvsacs-na.amazon.com    # type: url # max: critical
- in:  gateway-ink.amazon.com    # type: url # max: critical
- in:  imdbtv-backend-na.amazon.com    # type: url # max: critical
- in:  mas-ext.amazon.com    # type: url # max: critical
- in:  mas-sdk.amazon.com    # type: url # max: critical
- in:  msh.amazon.com    # type: url # max: critical
- in:  music-api.amazon.com    # type: url # max: critical
- in:  music-hints-na.amazon.com    # type: url # max: critical
- in:  musicapp.amazon.com    # type: url # max: critical
- in:  musiccentral.amazon.com    # type: url # max: critical
- in:  pitangui.amazon.com    # type: url # max: critical
- in:  preview-flex-capacity-na.amazon.com    # type: url # max: critical
- in:  prod-dp-discovery-us-east-1.amazon.com    # type: url # max: critical
- in:  rabbitinstruction-na.amazon.com    # type: url # max: critical
- in:  relay.amazon.com    # type: url # max: critical
- in:  sellercentral.amazon.com    # type: url # max: critical
- in:  spapi-na.amazon.com    # type: url # max: critical
- in:  a4k.amazon.com    # type: url # max: critical
- in:  advertising-api.amazon.com    # type: url # max: critical
- in:  advertising.amazon.com    # type: url # max: critical
- in:  appstore-tv-prod-na.amazon.com    # type: url # max: critical
- in:  cscentral.amazon.com    # type: url # max: critical
- in:  av-na.amazon.com    # type: url # max: critical
- in:  dcape-na.amazon.com    # type: url # max: critical
- in:  dna.amazon.com    # type: url # max: critical
- in:  dv-manifest-service-na-prod.amazon.com    # type: url # max: critical
- in:  flex-capacity-na.amazon.com    # type: url # max: critical
- in:  kca.amazon.com    # type: url # max: critical
- in:  kwis-opf.amazon.com    # type: url # max: critical
- in:  mag-na.amazon.com    # type: url # max: critical
- in:  merch.amazon.com    # type: url # max: critical
- in:  mlis.amazon.com    # type: url # max: critical
- in:  music-xray-service.amazon.com    # type: url # max: critical
- in:  na.account.amazon.com    # type: url # max: critical
- in:  paragon-na.amazon.com    # type: url # max: critical
- in:  read.amazon.com    # type: url # max: critical
- in:  updates.amazon.com    # type: url # max: critical
- out:  amazongames.com    # type: url # max: none
- out:  Amazon Web Services (AWS)    # type: other # max: none
- out:  "Contact Us" Functionality    # type: other # max: none
- out:  AWS and AWS customer assets are strictly out of scope    # type: other # max: none
- out:  *.*a2z*.*    # type: other # max: none
- out:  *.dev    # type: other # max: none
- out:  *.aws.*    # type: other # max: none
- out:  Anything considered a non-prod asset    # type: other # max: none
- out:  Anything which redirects to AWS    # type: other # max: none
- out:  learning.logistics.amazon.com    # type: other # max: none
- out:  tsologic.com    # type: url # max: none
- out:  www.twitch.tv    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
