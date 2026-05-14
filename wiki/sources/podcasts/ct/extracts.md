---
title: Critical Thinking Podcast — Extraction Notes
slug: ct-extracts
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [source, podcast, ct]
inbound: []
---

# CT Podcast — Per-Episode Extraction Notes

Records extraction decisions for each episode reviewed.

## Ep 173 — Is Bug Bounty Dead? (2026-05-07)

File: `20260507_ZQJ2uTJWYlk_Is_Bug_Bounty_Dead_Ep._173.en.vtt`

**Reviewed 2026-05-12. No extraction — meta-only.**

Entire episode is a debate about the state of the bug-bounty industry (AI
agents commoditizing pentesting, program volume overload, report-fee
experiments at $5/$10 to reduce AI slop). No concrete exploit patterns,
payloads, CVEs, or technical techniques discussed. Not extractable to technique
or tool pages.

## Ep 159 -- Tips for Crushing It on Google Cloud VRP (2026-01-29)

File: `20260129_7u6xpVhEpBA_Tips_for_crushing_it_on_Google_Cloud_VRP_With_Michael_Cote_and_Darby_Hopkins_Ep._159.txt`

**Reviewed 2026-05-14. No extraction -- program-meta only.**

Pure Google Cloud VRP process content: severity buckets (S0/S1/S2/C0/C1),
product tiering (T1/T2/T3A/T3B), panel-and-DJ process, panel shopping,
downgrade reasons, 1.2x report-quality bonus. No exploit patterns or
payloads.

## Group D (2026-05-14) ingest summary

- Ep 26 (2023-07-06) -- Client-side Quirks and Browser Hacks. Extracted.
  New techniques: popover-target-xss, math-element-clickable-firefox,
  dynamic-import-xss-gadget. Cross-link to existing base-tag-anywhere,
  dom-clobbering-to-xss (Seen-in-the-wild updated), nginx-alias-traversal.
- Ep 55 (2024-01-25) -- Popping WordPress Plugins with Ram Gall. Extracted.
  New techniques folder `techniques/wordpress/`: admin-ajax-unauth-action,
  nonce-as-access-control, wp-rest-route-enum, wp-get-body-parse.
- Ep 58 (2024-02-15) -- Youssef Sammouda -- Client-Side ATO War Stories.
  Extracted. All techniques (postmessage/async-origin-swap-race,
  xs-leaks/scroll-to-text-fragment, xs-leaks/math-random-prediction) were
  already created from prior extractions of this same episode; source page
  added for archival.
- Ep 74 (2024-06-06) -- Supply Chain Attack Primer with 0xLupin / Ronnie.
  Extracted. New techniques folder `techniques/supply-chain/`:
  dependency-confusion, maintainer-domain-takeover, npm-cache-poisoning-404,
  npx-binary-package-confusion. Plus recon/supply-chain-package-enum.
- Ep 159 (2026-01-29) -- Google Cloud VRP tips. No extraction; program-meta.
