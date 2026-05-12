# AIG

> Platform: HackerOne — https://hackerone.com/aig
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 96% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2026-05-11

## Scope

- in:  *.aig.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.aig.co.jp    # type: wildcard # max: critical # not eligible for bounty
- in:  http://*.aig.ie    # type: wildcard # max: critical # not eligible for bounty
- in:  www.aig.com.br    # type: url # max: critical # not eligible for bounty
- in:  www.vfis.com    # type: url # max: critical # not eligible for bounty
- in:  www.glatfelters.com    # type: url # max: critical # not eligible for bounty
- in:  services.aig.co.il    # type: url # max: critical # not eligible for bounty
- in:  www.aig.co.il    # type: url # max: critical # not eligible for bounty
- in:  www.rapidcover.ie    # type: url # max: critical # not eligible for bounty
- in:  www.vfisu.com    # type: url # max: critical # not eligible for bounty
- in:  www.vfisal.com    # type: url # max: critical # not eligible for bounty
- in:  www.iafcf.org    # type: url # max: critical # not eligible for bounty
- in:  www-1p.aig.com    # type: url # max: critical # not eligible for bounty
- in:  www.aigportal.de    # type: url # max: critical # not eligible for bounty
- in:  https://mall.aig.com.cn/efapiao/    # type: url # max: critical # not eligible for bounty
- in:  www.americanhome.co.jp    # type: url # max: critical # not eligible for bounty
- in:  wwip.aig.com    # type: url # max: critical # not eligible for bounty
- in:  mall.aig.com.cn    # type: url # max: critical # not eligible for bounty
- in:  www-264.aig.com    # type: url # max: critical # not eligible for bounty
- in:  http://mall.aig.com.cn/efapiao    # type: url # max: critical # not eligible for bounty
- in:  www.mall.aig.com.cn    # type: url # max: critical # not eligible for bounty
- in:  http://www.aiglife.co.uk/insurance/cbs    # type: url # max: critical # not eligible for bounty
- in:  http://www.aiglife.co.uk/insurance/sbs    # type: url # max: critical # not eligible for bounty
- in:  http://www.aiglife.co.uk/insurance/directline/lifeinsurance/    # type: url # max: critical # not eligible for bounty
- in:  http://www.aiglife.co.uk/insurance/natwest/productselection    # type: url # max: critical # not eligible for bounty
- in:  http://www.aiglife.co.uk/insurance/churchill/lifeinsurance/    # type: url # max: critical # not eligible for bounty
- in:  http://www.aiglife.co.uk/insurance/rbs/productselection    # type: url # max: critical # not eligible for bounty
- in:  http://www.aiglife.co.uk/insurance/ybs    # type: url # max: critical # not eligible for bounty
- in:  http://www.aiglife.co.uk/insurance/ulsterbank    # type: url # max: critical # not eligible for bounty
- in:  www.lifeandretirement.aig.com    # type: url # max: critical # not eligible for bounty
- in:  www.layahealthcare.ie    # type: url # max: critical # not eligible for bounty
- in:  *.myretirementmanager.com    # type: wildcard # max: critical # not eligible for bounty
- in:  sales.aig.co.il    # type: url # max: critical # not eligible for bounty
- in:  www-417.aig.ie    # type: url # max: critical # not eligible for bounty
- in:  www.myaig.com    # type: url # max: critical # not eligible for bounty
- in:  www-402.aigdirect.com    # type: url # max: critical # not eligible for bounty
- in:  www.americanhome.co.jp    # type: url # max: critical # not eligible for bounty
- in:  www.aigportal.de    # type: url # max: critical # not eligible for bounty
- in:  www.cropriskservices.com    # type: url # max: critical # not eligible for bounty
- in:  http://cg.cropriskservices.com/customergateway/login?returnurl=%2fcustomergateway    # type: url # max: critical # not eligible for bounty
- in:  shop.vfis.com    # type: url # max: critical # not eligible for bounty
- in:  www.vfisaz.com    # type: url # max: critical # not eligible for bounty
- in:  www.aig.sg    # type: url # max: critical # not eligible for bounty
- in:  http://www-400.aig.com.hk/aiuejb/b2b/login.jsp    # type: url # max: critical # not eligible for bounty
- in:  www.aigdirect.com    # type: url # max: critical # not eligible for bounty
- in:  www.aiginsurance.com    # type: url # max: critical # not eligible for bounty
- in:  *.aiginsurance.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.myaig.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.aigprivateclient.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.aigrs.com    # type: wildcard # max: critical # not eligible for bounty
- out:  *.corebridgefinancial.com    # type: wildcard # max: none
- out:  *.travelguard.com    # type: wildcard # max: none
- out:  travel.aig.co.jp    # type: url # max: none
- out:  www.corebridgefinancial.com    # type: url # max: none
- out:  www-1008.aig.com    # type: url # max: none
- out:  direct-carexcess.co.uk    # type: url # max: none
- out:  www-180.aig.com    # type: url # max: none
- out:  www-280.aig.com    # type: url # max: none
- out:  www.travelguard.com    # type: url # max: none
- out:  *.travelguard.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
