# incidents · supply-chain

Disclosed post-mortems of supply-chain compromises from 2010-2025. Each
page distils the public timeline + technical attack chain into the
"what would a bug hunter have caught earlier?" lens, with two primary
sources per page (a vendor / discoverer post-mortem and one deep
analyst writeup).

Built 2026-05-22 from a gap-only pass on the wiki RAG: incidents that
had no dedicated page got one, incidents already brushed in PortSwigger
annual roundups or HackTricks were skipped.

## Compiler / language toolchain

- [xz-utils CVE-2024-3094 (Jia Tan)](xz-utils-cve-2024-3094.md)
- [Vyper reentrancy lock → Curve hack](vyper-curve-reentrancy.md)
- [PHP git.php.net backdoor (Mar 2021)](php-git-backdoor.md)
- [Linux UMN "Hypocrite Commits" (Apr 2021)](linux-umn-hypocrite-commits.md)

## Update-channel hijacks

- [SolarWinds Orion SUNBURST](solarwinds-orion-sunburst.md)
- [CCleaner Floxif (2017)](ccleaner-floxif.md)
- [ASUS Live Update / ShadowHammer](asus-shadowhammer.md)
- [NotPetya / M.E.Doc (2017)](notpetya-medoc.md)
- [Kaseya VSA / REvil (2021)](kaseya-vsa-revil.md)
- [3CX DesktopApp (2023, Lazarus)](3cx-desktopapp.md)
- [ShadowPad / NetSarang (2017)](shadowpad-netsarang.md)

## CI / CD ecosystem

- [Codecov bash uploader (2021)](codecov-bash-uploader.md)
- [CircleCI OAuth-token theft (Jan 2023)](circleci-2023-oauth.md)
- [Heroku + Travis → GitHub OAuth (Apr 2022)](heroku-travis-oauth-2022.md)
- [tj-actions/changed-files CVE-2025-30066](tj-actions-changed-files.md)
- [reviewdog/action-setup (Mar 2025)](reviewdog-action-setup.md)

## npm registry

- [event-stream / flatmap-stream (2018)](event-stream-flatmap-stream.md)
- [ua-parser-js (2021)](ua-parser-js.md)
- [eslint-scope (2018)](eslint-scope.md)
- [node-ipc protestware (2022)](node-ipc-protestware.md)
- [@ledgerhq/connect-kit (Dec 2023)](ledger-connect-kit.md)
- [@solana/web3.js (Dec 2024)](solana-web3js.md)
- [xrpl-js (Apr 2025)](xrpl-js-npm-2025.md)
- [@lottiefiles/lottie-player (Oct 2024)](lottie-player-npm-2024.md)
- [polyfill.io CDN sale (2024)](polyfill-io-cdn-2024.md)
- [Nx s1ngularity (Aug 2025)](nx-s1ngularity-2025.md)
- [Shai-Hulud npm worm (Sep 2025)](shai-hulud-npm-worm-2025.md)
- [colors + faker self-sabotage (Jan 2022)](colors-faker-self-sabotage-2022.md)

## PyPI / Python

- [ctx PyPI (May 2022)](ctx-pypi.md)
- [PyTorch torchtriton dep-confusion (Dec 2022)](pytorch-torchtriton.md)
- [Ultralytics PyPI (Dec 2024)](ultralytics-pypi.md)

## Browser / mobile / wallet

- [Bybit / Safe{Wallet} UI compromise (Feb 2025)](bybit-safewallet-ui.md)
- [Operation Triangulation iMessage 0-click](operation-triangulation.md)
- [FORCEDENTRY / Pegasus (CVE-2021-30860)](forcedentry-pegasus.md)

## Crypto bridges

- [Ronin bridge (Mar 2022)](ronin-bridge.md)
- [Wormhole Solana bridge (Feb 2022)](wormhole-solana.md)
- [Nomad bridge (Aug 2022)](nomad-bridge.md)

## Identity providers / cert

- [Okta / Lapsus$ Sitel (2022)](okta-lapsus.md)
- [0ktapus / Scatter Swine (2022)](oktapus-twilio.md)
- [Microsoft Storm-0558 (2023)](ms-storm-0558.md)
- [Mimecast cert breach (SolarWinds cluster)](mimecast-cert-solarwinds-cluster.md)

## SaaS / vendor pushes

- [Snowflake credential-stuffing wave (May 2024)](snowflake-cred-stuffing-2024.md)
- [CrowdStrike Falcon channel file 291 (Jul 2024)](crowdstrike-falcon-channel-file.md)

## Availability / unpublish

- [left-pad unpublish (Mar 2016)](left-pad.md)
