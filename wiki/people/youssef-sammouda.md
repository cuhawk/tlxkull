---
title: Youssef Sammouda
slug: youssef-sammouda
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [samm0uda, ysamm, sam0, ysammouda]
role: hunter
primary_focus: client-side
tags: [person, role/hunter, focus/client-side, focus/oauth, focus/postmessage, focus/meta-facebook]
inbound: []
---

# Youssef Sammouda

## Identity

- **Real name:** Youssef Sammouda (alias `sam0`)
- **Primary handle:** `samm0uda` (X/Twitter, GitHub)
- **Nationality / base:** Tunisia
- **Role:** independent bug-bounty hunter; penetration tester (web + mobile)
- **Notoriety:** Top-ranked Facebook/Meta Whitehat hunter in 2020, 2021 and 2022. 100+ resolved Meta reports, 200+ valid vulnerabilities disclosed across Meta-owned properties.

## Focus areas

- Client-side ATO on Meta properties (Facebook, Instagram, Oculus, Canvas/Comet, Oversight Board)
- OAuth / FXAuth flow abuse — redirect/callback gadgets, token leakage
- postMessage origin-validation bugs and cross-window messaging
- DOM XSS in the Facebook JavaScript SDK and third parties that include it
- CSRF chained into account linking / partial ATO
- Cryptographic weaknesses in client SDKs (Math.random PRNG state recovery)

## Online presence

- [ysamm.com](https://ysamm.com/) — personal blog, primary outlet for Meta bounty writeups
- [About page](https://ysamm.com/about/)
- [X / Twitter — @samm0uda](https://twitter.com/samm0uda)
- [GitHub — samm0uda](https://github.com/samm0uda)
- [Malwarebytes interview (2021)](https://www.malwarebytes.com/blog/news/2021/04/interview-with-a-bug-bounty-hunter-youssef-sammouda)
- [SecurityWeek "Hacker Conversations" interview](https://www.securityweek.com/hacker-conversations-youssef-sammouda-bug-bounty-hunter/)
- [BBRD Podcast Ep. 5 — Inside the Mind of the TOP1 Facebook Bug Bounty Hunter](http://www.bugbountyexplained.com/inside-the-mind-of-the-top1-facebook-bug-bounty-hunter-youssef-sammouda-bbrd-podcast-5/)
- [Bugreader interview — "The Account Takeover Ace"](https://bugreader.com/social/hackers-spotlight-general-interview-with-youssef-sammouda-the-account-takeover-ace-100969)
- Contact: `ysamm@proton.me`

## Key research / posts

Selected from ysamm.com; emphasis on the deep ATO chains he's best known for.

- [Account Takeover via cryptographically weak RNG and XSS (Jan 2026)](https://ysamm.com/uncategorized/2026/01/17/math-random-facebook-sdk.html) — Facebook SDK used `Math.random()` for cross-origin message callback IDs; forced iframe reinits to leak PRNG outputs, reconstruct V8 state, predict callback tokens and inject XSS into victim sessions. See [../techniques/dom-xss/](../techniques/dom-xss/).
- [FXAuth Token leakage → 2-click ATO (Jan 2026)](https://ysamm.com/uncategorized/2026/01/16/leaking-fxauth-token.html) — Meta's unified FXAuth token leaked through a sibling-flow gadget; two-click compromise across Meta properties. See [../techniques/oauth/](../techniques/oauth/).
- [Instagram ATO via Meta Pixel (fbevents.js) abuse (Jan 2026)](https://ysamm.com/uncategorized/2026/01/16/leaking-fbevents-ato.html) — abusing the third-party Meta Pixel script's tracking behaviour to siphon authenticated state into Instagram ATO.
- [Canvas-apps ATO via reversed `isSameOrigin()` (Jan 2023)](https://ysamm.com/uncategorized/2023/01/29/account-takeover-in-canvas-apps-served-in-comet-due-to-failure-in-cross-window-message-origin-validation.html) — Comet code compared `b.isSameOrigin(a)` with `b` = sandboxed null-origin iframe; all checks passed because protocol/host/port were undefined → leaked OAuth `state` + `cquick_token` → ATO. See [../techniques/postmessage/](../techniques/postmessage/).
- [DOM XSS in Facebook page_proxy via postMessage (Nov 2020)](https://ysamm.com/uncategorized/2020/11/07/facebook-dom-based-xss-using-postmessage.html) — chained origin bypass on `our.alpha.facebook.com` with a form whose `action` attribute came directly from `message.data.params.appTabUrl`; `javascript:` URI fired on submit. See [../techniques/postmessage/](../techniques/postmessage/) and [../techniques/dom-xss/](../techniques/dom-xss/).
- [Bad regex in Facebook JS SDK → cross-site ATO (Dec 2020)](https://ysamm.com/uncategorized/2020/12/31/bad-regex-in-facebook-javascript-sdk-leads-to-account-takeovers-in-third-party-websites-that-included-it.html) — origin check `/^https:\/\/.*facebook\.com$/` had an unescaped dot; `testpocfacebook.com` matched, attacker iframed SDK-using sites and read `window.location.href` to harvest OAuth redirect URIs across the third-party Facebook-login ecosystem.
- [OAuth unsafe-redirects → Facebook ATO (Apr 2021)](https://ysamm.com/uncategorized/2021/04/30/facebook-account-takeover-due-to-unsafe-redirects-after-the-oauth-flow.html) — redirect-cookie tamper + Crowdtangle access token + GraphQL-pulled CSRF tokens + device-login flow elevation → no-interaction full ATO. See [../techniques/oauth/](../techniques/oauth/).
- [OAuth callback-URL allowlist bypass (Apr 2021)](https://ysamm.com/uncategorized/2021/04/02/facebook-account-takeover-due-to-a-bypass-of-allowed-callback-urls-in-the-oauth-flow.html) — missing path validation on `fallback_redirect_uri` allowed redirecting OAuth response to attacker domain. See [../techniques/oauth/](../techniques/oauth/).
- [Generate access tokens for ANY Facebook user (Jan 2019)](https://ysamm.com/uncategorized/2019/01/22/generate-access-tokens-for-any-facebook-user.html) — Rights Manager endpoint trusted `page_id` parameter without type-checking; substituting an arbitrary user ID minted a valid token for that user.
- [Facebook CSRF protection bypass → ATO (Feb 2019)](https://ysamm.com/uncategorized/2019/02/12/facebook-csrf-protection-bypass-which-leads-to-account-takeover.html) — bypass of `fb_dtsg` checks composed with linked-account flow.
- [Oversightboard.com site-wide CSRF (Jun 2021)](https://ysamm.com/uncategorized/2021/06/27/oversightboard-com-site-wide-csrf-due-to-missing-checking.html) — entire Oversight Board property missing CSRF token validation.
- [Multiple XSS in Meta Conversion API Gateway (Jan 2026)](https://ysamm.com/uncategorized/2026/01/13/capig-xss.html) — server-side Meta ad infra surface, several XSS sinks in CAPIG admin.
- [DOM-XSS in Instant Games (Jan 2023)](https://ysamm.com/uncategorized/2023/01/29/dom-xss-in-instant-games-due-to-improper-verification-of-supplied-urls.html) — improper URL verification in the Instant Games host frame. See [../techniques/dom-xss/](../techniques/dom-xss/).

## CT podcast appearances

- [2024-02-15 Ep. 58 — Youssef Sammouda – Client-Side ATO War Stories](../sources/podcasts/ct/20240215_U8lZKlz9bN0_Youssef_Sammouda_-_Client-Side_ATO_War_Stories_Ep._58.en.vtt)

## BBRE appearances

- Interview episode covering his background and journey to becoming the top Facebook bug bounty hunter.
  [BBRE](https://www.youtube.com/watch?v=MXH1HqTFNm0)
- Facebook postMessage ATO via Canvas App page_proxy ($25,000).
  [BBRE](https://www.youtube.com/watch?v=jPMaZt9ZJes)
- Facebook ATO chain via OAuth + CSRF + captcha lockout + sandbox iframe leak ($44,625).
  [BBRE](https://www.youtube.com/watch?v=pk7oYuz4x0Q)
- Facebook three-bug chain: endpoint ATO + ASPX shared keys + path bypass ($54,800 combined).
  [BBRE](https://www.youtube.com/watch?v=JiMzpjgAXv8)

## Notes

- One of the most prolific Facebook/Meta bounty earners ever — pipelined output on ysamm.com is unusually high for a solo hunter, with multi-post drops every January and frequent in-year follow-ups when Meta ships regressions.
- Signature pattern: deep client-side chains that compose at least 2-3 primitives (origin bypass + state leak + redirect gadget + token mint). Almost never a single-step bug.
- Heavy focus on the Facebook JS SDK and FXAuth — both are surface-massive enough that small regressions ship to production constantly. Worth re-reading whenever Meta touches FXAuth, Comet, Canvas/Instant Games, or third-party SDK validation logic.
- Reads as a regex-and-stringop microscopist: many of his bugs are off-by-one origin checks, missing `\.` escapes, reversed comparison operands, or unvalidated query params. Static-scan the SDK for these patterns when triaging Meta scope.
- Writeup style: terse, code-snippet-heavy, minimal narrative. Each post is essentially a PoC chain laid out top-to-bottom — good template for our own findings format.
