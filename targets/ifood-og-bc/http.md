# iFood: Bug Bounty Program

> Platform: Bugcrowd — https://bugcrowd.com/engagements/ifood-og
> Type: BBP
> Bounty: P1 $2100–$3750 | P2 $1000–$1875 | P3 $450–$900 | P4 $150–$400
> Status: In progress (started Aug 25, 2020)

## Scope

- in:  https://play.google.com/store/apps/details?id=br.com.brainweb.ifood&hl=pt_BR   # type: android_app
- in:  https://apps.apple.com/br/app/ifood-pedir-comida-e-mercado/id483017239   # type: ios_app
- in:  https://www.ifood.com.br   # type: url
- in:  https://marketplace.ifood.com.br   # type: url
- in:  https://gestordepedidos.ifood.com.br   # type: url
- in:  https://wsloja.ifood.com.br   # type: url
- in:  https://*.movilepay.com   # type: url
- in:  https://*.movilepay.com.br   # type: url
- in:  https://shop.ifood.com.br   # type: url
- in:  https://static-images.ifood.com.br   # type: url
- in:  https://developer.ifood.com.br   # type: url
- in:  https://api.fstr.rocks   # type: url
- in:  https://rc.fstr.rocks   # type: url
- in:  https://www.zoop.com.br   # type: url
- in:  https://www.zoop.ws   # type: url
- in:  https://www.minhaconta.zoop.com.br   # type: url
- in:  https://dash.zoop.com.br/   # type: url
- in:  https://contadigital.ifoodpago.com.br/   # type: url
- in:  https://play.google.com/store/apps/details?id=br.com.movilepay.banking.application&hl=pt_BR   # type: android_app
- in:  https://portal.iFoodpago.com.br   # type: url
- out: blog-empresas.ifood.com.br   # type: domain
- out: blog-parceiros.ifood.com.br   # type: domain
- out: *.ecomanda.com.br   # type: wildcard
- out: *.ecomanda.app   # type: wildcard
- out: *.allin.movilepay.com   # type: wildcard
- out: *.starsoft.movilepay.com   # type: wildcard
- out: *.openfinance.ifood.com.br   # type: wildcard
- out: *.openfinance.ifoodpago.com.br   # type: wildcard

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- validation within: 6 days
- avg payout: $345 (last 3 months)
- vulns rewarded: 177
- safe harbor: yes
- industry: Retail
- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
