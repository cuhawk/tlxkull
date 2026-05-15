---
title: Tommy DeVoss (dawgyg)
slug: tommy-devoss
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [dawgyg, thedawgyg]
role: hunter
primary_focus: server-side
tags: [person, role/hunter, focus/server-side, focus/ssrf, focus/rce, focus/recon]
inbound: []
---

# Tommy DeVoss (dawgyg)

## Identity

- **Real name:** Thomas "Tommy" DeVoss.
- **Primary handle:** `dawgyg` (HackerOne); `thedawgyg` on X/Twitter.
- **Based:** Richmond, Virginia, US.
- **Role:** Bug bounty hunter. Former black hat (World of Hell crew,
  early 2000s). One of the first six hackers to cross the $1M earnings
  threshold on HackerOne; total reported lifetime earnings >$2M.
- **Public-facing personality:** Open about the prison-to-millionaire
  arc; recurring podcast guest and live-hacking-event regular. MVH
  (Most Valuable Hacker) on the Verizon Media program.

## Focus areas

- Server-side: SSRF (signature class — ~$1M lifetime on SSRF alone).
- Remote code execution (ImageMagick-era, deserialization, file
  upload).
- Large-scope corporate targets (Yahoo / Verizon Media / Oath, US DoD).
- Bypass tradecraft: IP-encoding (octal/hex/decimal/IPv6-mapped),
  blacklist-vs-allowlist abuse, redirect chains.
- Live-hacking-event methodology: focus 1–2 programs deeply, escalate
  severity once payout speed and triage quality are validated.

## Online presence

- [HackerOne profile — dawgyg](https://hackerone.com/dawgyg)
- [HackerOne hacktivity (disclosed reports)](https://hackerone.com/dawgyg/hacktivity?type=user)
- [HackerOne badges](https://hackerone.com/dawgyg/badges)
- [X / Twitter — @thedawgyg](https://x.com/thedawgyg)
- [LinkedIn — Thomas DeVoss](https://www.linkedin.com/in/thomas-devoss-802a8976)
- [HackerOne blog — Hacker Spotlight: Interview with dawgyg](https://www.hackerone.com/blog/hacker-spotlight-interview-dawgyg)

## Key research / posts

Tommy is primarily a hunter rather than a blogger; his public record
lives in interviews, podcasts, and HackerOne hacktivity rather than
long-form writeups. Anchor sources below.

- [Daily Swig profile — "As long as people are writing code, there's going to be insecure code"](https://portswigger.net/daily-swig/as-long-as-people-are-the-ones-writing-code-theres-going-to-be-insecure-code-tommy-devoss-on-his-post-jail-bug-bounty-exploits)
  — Post-prison career profile; covers the SSRF specialization, the
  Yahoo program relationship, and methodology heuristics.
- [Daily Swig — Bug bounty leaders: Six hackers cross $1m earnings threshold](https://portswigger.net/daily-swig/bug-bounty-leaders-six-hackers-cross-1m-earnings-threshold)
  — Names him in the original six-figure cohort with cosmic, mlitchfield,
  mayonaise, todayisnew, and nnwakelam.
- [Darknet Diaries Ep 60 — "dawgyg" (transcript)](https://darknetdiaries.com/transcript/60/)
  — The canonical biographical record: World of Hell, Bank Colo
  defacement, the 10-year computer ban, ImageMagick RCE as the gateway
  back into hacking via bounties. Read this before any other source.
- [SentinelOne summary of Darknet Diaries Ep 60](https://www.sentinelone.com/blog/darknet-diaries-how-dawgyg-made-over-100000-in-a-single-day-from-hacking/)
  — Condensed version of the $100k+/day arc.
- [Investec — From Prison to Private Security](https://www.investec.com/en_za/focus/innovation/how-a-hacker-went-from-prison-to-private-security-professional.html)
  — General-audience profile; useful for the rehabilitation framing
  he gives in talks.
- [BeyondTrust Phishy Business Ep 71 — From Prison to Millions](https://www.beyondtrust.com/podcast/ep-71-from-prison-to-millions-the-hacker-who-struck-yahoo-bug-bounty-gold-tommy-devoss)
  and [Ep 83 — The Bug Bounty That Bought a Mini Donkey](https://www.beyondtrust.com/podcast/ep-83-the-bug-bounty-that-bought-a-mini-donkey-tommy-devoss-dawgyg)
  — Long-form interviews on methodology and lifestyle.
- [Hacker Valley Studio — From Black Hat to Bug Bounties Pt 1](https://hackervalleystudio.podbean.com/e/from-black-hat-to-bug-bounties-pt-1-with-tommy-devoss/)
  / [Pt 2](https://hackervalleystudio.podbean.com/e/from-black-hat-to-bug-bounties-pt-2-with-thomas-devoss/)
  — Two-parter covering the same arc with more tradecraft detail.
- [Raconteur — How I became an ethical hacker](https://www.raconteur.net/technology/how-i-became-an-ethical-hacker)
  — Short first-person piece.

### Signature finding — Yahoo $180k SSRF

Sourced via Critical Thinking Ep 164 / Daily Swig profile (no
self-published writeup exists). Bypassed Yahoo's
`169.254.169.254` blacklist by **octal-encoding only the first octet**
(`0251.254.169.254`), an asymmetric encoding the validator failed to
canonicalize. The bypass applied cleanly across **18 separate
endpoints** that shared the same SSRF validator, each paying $10k =
$180k in one sitting. Cross-link: `../techniques/ssrf/` (octal-first-octet
bypass; blacklist-vs-allowlist anti-pattern).

## CT podcast appearances

- [2026-03-05 Ep 164 — Tommy DeVoss: From Black Hat to Bug Bounty LEGEND](../sources/podcasts/ct/20260305_kpFfde3rNFs_Tommy_DeVoss_-_From_Black_Hat_to_Bug_Bounty_LEGEND_Ep._164.en.vtt)

## Notes

- **Prison-to-millionaire arc.** Learned to hack at 10. Joined World
  of Hell (UNIX-only, government/military/Fortune 500 targets).
  Arrested 2002 at age 19 for the Bank Colo defacement; 27 months +
  10-year computer ban + $100k restitution under the CFAA. Probation
  violation 2006 added 14 months. Released 2008. Drifted through
  software dev, then in March 2016 stumbled into HackerOne and got a
  $300 info-disclosure bounty on Yahoo. By Oct 18 2018: $160k bounties
  in a single day. By 2019: crossed $1M cumulative.
- **Why server-side.** Trained on early-2000s remote-host attacks
  (defacements, RFI, command injection); the mental model maps
  directly onto modern SSRF/RCE. He explicitly says client-side
  (XSS, CSRF, postMessage) is not his game.
- **Methodology heuristic (from HackerOne interview).** Open at low
  severity to test the program's triage culture; abandon programs that
  mark legitimate bugs as duplicates or slow-pay. Pick 1–2 programs and
  go wide+deep rather than spraying everything.
- **Public-facing personality.** Comfortable telling the prison story
  on-record; this is unusual in the hunter community and makes him a
  go-to media interview. Treat citations as plentiful — most of his
  technique disclosure is verbal (podcasts, live-hacking-event
  commentary), not written. For deep technique extraction, transcribe
  the CT Ep 164 episode and `../sources/podcasts/ct/` neighbors.
- **Lifestyle artifacts.** The "mini donkey" episode title is literal
  — he reportedly bought one with a bounty payout. Useful as a marker
  when scanning podcast catalogs for his appearances.
- **Not a blogger.** Unlike Frans Rosén or James Kettle, there's no
  Detectify-Labs-equivalent archive. The wiki should treat his
  contributions as oral tradition — captured via podcast transcripts
  and HackerOne hacktivity, not blog ingestion.
