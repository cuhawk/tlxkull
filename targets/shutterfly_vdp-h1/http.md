# Shutterfly VDP

> Platform: HackerOne — https://hackerone.com/shutterfly_vdp
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 79% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2026-04-13

## Scope

- in:  *.shutterfly.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.snapfish.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.sf-cdn.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.lifetouch.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.photoccino.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.sbs.shutterfly.com    # type: wildcard # max: critical # not eligible for bounty
- in:  lifetouch.com    # type: url # max: critical # not eligible for bounty
- in:  jcpportraits.com    # type: url # max: critical # not eligible for bounty
- in:  prestigeportraits.com    # type: url # max: critical # not eligible for bounty
- in:  preschoolsmiles.com    # type: url # max: critical # not eligible for bounty
- in:  shutterfly.com    # type: url # max: critical # not eligible for bounty
- in:  tinyprints.com    # type: url # max: critical # not eligible for bounty
- in:  snapfish.com    # type: url # max: critical # not eligible for bounty
- in:  snapfish.de    # type: url # max: critical # not eligible for bounty
- in:  snapfish.fr    # type: url # max: critical # not eligible for bounty
- in:  snapfish.ie    # type: url # max: critical # not eligible for bounty
- in:  snapfish.it    # type: url # max: critical # not eligible for bounty
- in:  snapfish.co.uk    # type: url # max: critical # not eligible for bounty
- in:  snapfish.com.au    # type: url # max: critical # not eligible for bounty
- in:  snapfish.co.nz    # type: url # max: critical # not eligible for bounty
- in:  photo.walgreens.com    # type: url # max: critical # not eligible for bounty
- in:  www.spoonflower.com    # type: url # max: critical # not eligible for bounty
- in:  admin.spoonflower.com    # type: url # max: critical # not eligible for bounty
- in:  staging.spoonflower.com    # type: url # max: critical # not eligible for bounty
- in:  blog.spoonflower.com    # type: url # max: critical # not eligible for bounty
- in:  wgwebservices.snapfish.com    # type: url # max: critical # not eligible for bounty
- in:  https://www.cvs.com/photo/    # type: url # max: critical # not eligible for bounty
- in:  shutterfly-prod.auth.us-east-1.amazoncognito.com    # type: url # max: critical # not eligible for bounty
- in:  api-gateway.spoonflower.com    # type: url # max: critical # not eligible for bounty
- in:  cart.spoonflower.com    # type: url # max: critical # not eligible for bounty
- in:  com.shutterfly    # type: android_app # max: critical # not eligible for bounty
- in:  Snapfish: Prints + Photo Books / com.snapfish.mobile    # type: android_app # max: critical # not eligible for bounty
- in:  com.shutterfly.ShutterflyUploader    # type: ios_app # max: critical # not eligible for bounty
- in:  Snapfish: Photos Cards & Books / com.hp.Snapfish    # type: ios_app # max: critical # not eligible for bounty
- in:  Snapfish Photo Tile Wall Decor / com.snapfish-llc.SnapfishExpress    # type: ios_app # max: critical # not eligible for bounty
- in:  www.borrowlenses.com    # type: url # max: critical # not eligible for bounty
- in:  http://*.sbs.shutterfly.com    # type: wildcard # max: critical # not eligible for bounty
- in:  http://*.photoccino.com    # type: wildcard # max: critical # not eligible for bounty
- in:  http://*.lifetouch.com    # type: wildcard # max: critical # not eligible for bounty
- in:  http://www.cvs.com/photo/    # type: url # max: critical # not eligible for bounty
- in:  com.photoupload    # type: android_app # max: critical # not eligible for bounty
- in:  lifetouchrewards.com    # type: url # max: critical # not eligible for bounty
- in:  businesssolutions.shutterfly.com    # type: url # max: critical # not eligible for bounty
- in:  com.shutterfly.sharesitesapp    # type: ios_app # max: critical # not eligible for bounty
- in:  com.shutterfly.android.sharesites    # type: android_app # max: critical # not eligible for bounty
- in:  com.dotgraphics.groovebook    # type: ios_app # max: critical # not eligible for bounty
- in:  com.shutterfly.sharesitesapp    # type: url # max: critical # not eligible for bounty
- out:  https://*.cvs.com/    # type: wildcard # max: none
- out:  https://*.walgreens.com/    # type: wildcard # max: none
- out:  fulfillment-platform.shutterfly.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
