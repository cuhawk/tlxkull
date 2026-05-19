---
title: Inti De Ceukelaire (securinti)
slug: inti-de-ceukelaire
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-19T14:42:00Z
handles: [securinti, intidc]
role: dual
primary_focus: social-engineering
tags: [person, role/hunter, role/vendor-eng, vendor/intigriti, focus/social-engineering, focus/oauth, focus/osint, focus/email-auth]
inbound: []
---

# Inti De Ceukelaire (securinti)

## Identity

- **Real name:** Inti De Ceukelaire
- **Primary handle:** `securinti` (X) / `intidc` (GitHub, Facebook, LinkedIn, HackerOne)
- **Role:** Chief Hacker Officer at [Intigriti](https://www.intigriti.com) (Europe's largest crowdsourced vulnerability disclosure platform); ethical hacker, cybercrime investigator, founding member of the Hacker Policy Council.
- **Location:** Aalst, Belgium.
- **Track record:** Las Vegas H1 Live Hacking Event "Most Valuable Hacker" 2018; first researcher to legally report a vulnerability under Belgium's 2023 safe-harbor framework; voted Belgian "IT Person of the Year" 2020; widely covered in BBC, Wired, The Verge, CNET, Mashable, NY Magazine. Famous for the *Ticket Trick* (hacking hundreds of Fortune 500 companies via helpdesk email aliases) and for media-bait stunts like manipulating a pinned Donald Trump tweet.

## Focus areas

- Social-engineering and logic-flaw chains (helpdesks, email bounces, autoresponders, expired-domain takeover of linked tweets).
- OAuth / federated-login abuse — see [../techniques/oauth/SUMMARY.md](../techniques/oauth/SUMMARY.md), particularly Facebook Account Kit and identity-provider confusion ([facebook-implicit-flow-app-confusion.md](../techniques/oauth/facebook-implicit-flow-app-confusion.md), [redirect-uri-bypass.md](../techniques/oauth/redirect-uri-bypass.md)).
- OSINT and privacy weaponisation (Stalkscan, expired-link forensics).
- Email-auth abuse: SPF/DKIM bounce leaks, autoresponder oracles, ticket-via-email primitives.
- Public-interest hacking / policy: lobbied for and shipped the Belgian ethical-hacker safe-harbor law.

## Online presence

- Personal site: [inti.io](https://inti.io) / [inti.io/about](https://inti.io/about)
- Substack newsletter: [inti.io](https://inti.io) ("Ethical hacker & cybercrime investigator")
- X / Twitter (primary): [@securinti](https://x.com/securinti)
- X / Twitter (personal): [@intidc](https://x.com/intidc)
- Medium archive: [medium.com/@intideceukelaire](https://medium.com/@intideceukelaire) and the Intigriti pub [medium.com/intigriti](https://medium.com/intigriti/latest)
- Intigriti author page: [intigriti.com/researchers/blog/author/inti-de-ceukelaire](https://www.intigriti.com/researchers/blog/author/inti-de-ceukelaire)
- GitHub: [github.com/IntiDC](https://github.com/IntiDC)
- HackerOne: [hackerone.com/intidc](https://hackerone.com/intidc)
- LinkedIn: [linkedin.com/in/intidc](https://www.linkedin.com/in/intidc/)
- Bug Bounty Forum AMA: [bugbountyforum.com/blog/ama/inti](https://bugbountyforum.com/blog/ama/inti/)
- SecurityWeek interview: [Hacker Conversations: Inti De Ceukelaire](https://www.securityweek.com/hacker-conversations-inti-de-ceukelaire-raging-against-the-machine-creatively/)
- Side project: [stalkscan.com](https://stalkscan.com) (Facebook Graph-Search privacy demo, 2017).

## Key research / posts

- **[How I hacked hundreds of companies through their helpdesk](https://medium.com/intigriti/how-i-hacked-hundreds-of-companies-through-their-helpdesk-b7680ddc2d4c)** (2017, "Ticket Trick") — Sign up to a SaaS (Slack, Yammer, GitLab, Vimeo, Kayako, Zendesk) using `support@victim.com`; the email-verification link lands in the company's *public* helpdesk thread, granting access to internal team chat, intranets, and social accounts. Forced Slack to randomise verification email addresses. Canonical example of an email-routing logic flaw bypassing identity.
- **[How I hacked Tinder accounts using Facebook's Account Kit and earned $6,250](https://www.freecodecamp.org/news/hacking-tinder-accounts-using-facebook-accountkit-d5cc813340d1)** (Feb 2018) — Tinder's API accepted any Facebook Account Kit access token without validating the originating `client_id`, so a token issued for an unrelated AccountKit app could log into Tinder as that user. Classic IdP audience-confusion bug. Cross-links to [../techniques/oauth/facebook-implicit-flow-app-confusion.md](../techniques/oauth/facebook-implicit-flow-app-confusion.md).
- **[Abusing autoresponders and email bounces](https://medium.com/intigriti/abusing-autoresponders-and-email-bounces-9b1995eb53c2)** (Feb 2019) — Out-of-office replies, SMTP bounce messages, and ticket-system autoresponders routinely echo full headers (To/From/X-Original-To/UID-in-Message-ID), turning innocuous email exchanges into oracles that leak hidden recipient addresses, internal IDs, or reset tokens. Pairs with the Ticket Trick to build identity-pivot chains.
- **[GOTCHA: Taking phishing to a whole new level](https://medium.com/intigriti/gotcha-taking-phishing-to-a-whole-new-level-72eda9e30bef)** — Live demo of "consent-phishing": instead of stealing passwords, get the victim to OAuth-authorise an attacker-controlled app, then read mailbox / contacts / drive at will. Foundational reference for OAuth-consent abuse before Microsoft popularised the term "illicit consent grant".
- **Trump pinned-tweet manipulation** (Jan 2017) — Bought an expired domain (`nationalachieverscongress.com`, ~€10) that one of Donald Trump's 2012 tweets still embedded; redirected it to a Belgian carnival video, mutating the tweet's media card. Coverage: [VRT NWS](https://www.vrt.be/vrtnws/en/2017/01/23/fleming_hacks_trumptweet-1-2872836/). Pure social-engineering / expired-link takeover — not a server hack — yet became a textbook case of how mutable embeds and TwitterCards trust DNS over content provenance.
- **Hacking your way into Metallica** (~2010s, retold in talks/podcasts) — As a teenager found a flaw on metallica.com, reported it without a formal disclosure program; the band rewarded him with backstage passes, concert tickets, and a backing-vocal spot on stage. The origin story he tells in nearly every keynote; covered on the CT podcast Ep 33 (see below).
- **Vatican website manipulation prank** (2018) — Demonstrated content injection on the official Vatican site as a security-awareness piece; widely covered in mainstream press. Mentioned in [inti.io/about](https://inti.io/about) and SecurityWeek.
- **[Stalkscan.com](https://stalkscan.com)** (Feb 2017) — Reanimated Facebook Graph Search after Facebook hid it from end users; let anyone build hyper-specific "events attended by X", "photos liked by X" queries against public Facebook data. Forced Facebook to tighten Graph Search defaults. Coverage: [Vice](https://www.vice.com/en/article/facebooks-creepiest-search-tool-is-back-thanks-to-this-site/), [The Outline](https://theoutline.com/post/1084/stalkscan-facebook-graph-still-creepy).
- **Belgian ethical-hacker safe-harbor law** (2023) — Lobbied for and was the *first* researcher to legally report a vulnerability under the new Belgian whistleblower-style framework that permits good-faith unauthorised testing. Background: [Intigriti — Safe harbor legal framework officially launches in Belgium](https://www.intigriti.com/researchers/blog/hacker-spotlight/eu-whistleblower-directive-officially-launches-in-belgium).

## CT podcast appearances

- [2023-08-24 Ep 33 — Inti De Ceukelaire: Hacking your way into Metallica](../sources/podcasts/ct/20230824_MSXf2fSobv8_Inti_De_Ceukelaire_-_Hacking_your_way_into_Metallica_Ep._33.en.vtt) — origin story plus a deep dive on creative chains (Ticket Trick, autoresponders, OAuth-consent phishing).

## Notes

- **Role:** "CHO" / Chief Hacker Officer at Intigriti — vendor-eng-adjacent hunter. Public face of the platform, recurring keynote speaker, frequent media commentator on Belgian/European disclosure policy.
- **Signature chain pattern:** *Identity-by-email-routing*. Repeatedly weaponises the implicit trust between "email address" and "identity" — helpdesk-as-mailbox (Ticket Trick), bounce-as-oracle (autoresponders), AccountKit-as-IdP (Tinder), expired-domain-as-content-provenance (Trump tweet). Worth screening any target whose login flow trusts an email address it didn't itself send to.
- **Media-bait MO:** Picks targets the press will report on — Metallica, Trump, Vatican, Tinder, Belgian government — and engineers low-severity-but-high-visibility flaws into stunt-grade disclosures. Drives mainstream awareness of bug bounty as a profession; the actual technical primitives are usually mundane (expired DNS, missing audience check, mail bounce headers).
- **Policy footprint:** Founding member of the Hacker Policy Council; instrumental in Belgium's safe-harbor law, which is now cited across the EU as a template. When ingesting any Belgian-target finding, check whether disclosure went through `cert.be` under the new framework — it changes how we handle scope.
- **Personality:** SecurityWeek interview frames him as "raging against the machine creatively"; preference for *one creative chain* over *N automated dupes*. Aligns with the wiki's bias toward technique-depth over breadth.
- **Collab patterns:** Frequent on-stage partner of Renniepak (also Intigriti); recurring CT-podcast guest pairings with Justin Gardner ([justin-gardner.md](justin-gardner.md)) per CT host's collab notes. Intigriti runs the H1-equivalent LHE circuit covered in CT Ep 42 (Intigriti LHE Recap with renniepak).
- **Tools / repos:** GitHub [IntiDC](https://github.com/IntiDC) — `clintool` (Gmail confidential-mail leak-tracer), `twitter-verified` (Nov 2022 verified-user dump), `marypoppit` (data-hiding-in-data), `klassenjustitie`. Less code-output than infrastructure-hunter peers; output is mostly write-ups and policy work.
- **Cross-references:** Ticket Trick / autoresponder primitives belong in any future `wiki/techniques/social-engineering/` subtree (not yet created); OAuth-flavoured work cross-links to [../techniques/oauth/](../techniques/oauth/) — especially [facebook-implicit-flow-app-confusion.md](../techniques/oauth/facebook-implicit-flow-app-confusion.md) and [redirect-uri-bypass.md](../techniques/oauth/redirect-uri-bypass.md).

<!-- sources:auto:start -->
## Ingested blog posts

- [p hacking a sushi restaurant video](../sources/blogs/personal/inti/p-hacking-a-sushi-restaurant-video.md)
- [p how brands like orange downplay security](../sources/blogs/personal/inti/p-how-brands-like-orange-downplay-security.md)
- [p how i infiltrated phishing panels](../sources/blogs/personal/inti/p-how-i-infiltrated-phishing-panels.md)
- [p info and booking](../sources/blogs/personal/inti/p-info-and-booking.md)
- [p inti cardreveal privacy policy](../sources/blogs/personal/inti/p-inti-cardreveal-privacy-policy.md)
- [p scan to scam how thieves can steal](../sources/blogs/personal/inti/p-scan-to-scam-how-thieves-can-steal.md)
- [p when privacy expires how i got access](../sources/blogs/personal/inti/p-when-privacy-expires-how-i-got-access.md)
- [p why subscribe](../sources/blogs/personal/inti/p-why-subscribe.md)

<!-- sources:auto:end -->

## Wiki RAG ingestion

Blog bodies ingested 2026-05-19 into the `wiki` Chroma collection.
Source files:

- `wiki/sources/blogs/personal/inti/`

Query via `docs_query(collection="wiki", query="...")` instead of WebFetch.

