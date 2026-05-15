---
title: Ryan Barnett (B0N3)
slug: ryan-barnett
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [ryancbarnett, rcbarnett, b0n3]
role: vendor-eng
primary_focus: waf-defense
tags: [person, role/vendor-eng, focus/waf-defense, focus/unicode-normalization, focus/modsecurity, focus/owasp-crs, focus/virtual-patching, focus/client-side]
inbound: []
---

# Ryan Barnett (B0N3)

## Identity

- **Real name:** Ryan C. Barnett.
- **Primary handle:** `ryancbarnett` (X), `rcbarnett` (GitHub), shows up as `B0N3` in some community contexts.
- **Based:** Falls Church, Virginia, USA.
- **Role:** Vendor-eng / researcher. Principal / Senior Threat Research
  Manager on **Akamai**'s Threat Research Team, supporting App & API
  Protector. Joined Akamai by way of Trustwave SpiderLabs (acquired the
  ModSecurity team from Breach Security). Former SANS Institute faculty.
- **Defender-side credentials:** WASC Board member; long-time OWASP
  Project Leader for the **ModSecurity Core Rule Set (CRS)**, **Web
  Hacking Incident Database (WHID)**, and **Distributed Web
  Honeypots**. Drove the CRS anomaly-scoring redesign (rules no longer
  block individually — they raise a score and a decision threshold
  acts) that became the basis for CRS v3 and shipped under OWASP.
- **Books:** *Preventing Web Attacks with Apache* (Pearson, 2006) and
  *The Web Application Defender's Cookbook: Battling Hackers and
  Defending Users* (Wiley, 2013).

## Focus areas

- WAF defense engineering — detection rules, virtual patching, anomaly
  scoring, false-positive triage at internet scale.
- Unicode normalization attacks (visual confusables, overlong UTF-8,
  truncation, combining characters, collation surprises).
- HTTP-protocol attacks — request smuggling (HTTP/1.1 + HTTP/2),
  header-parsing edge cases.
- Client-side threats — Magecart / web-skimmer detection, PCI DSS v4
  client-side controls.
- Honeypots & threat intel — distributed web honeypots, WHID dataset.

## Online presence

- [X / Twitter — @ryancbarnett](https://x.com/ryancbarnett)
- [GitHub — rcbarnett](https://github.com/rcbarnett)
- [LinkedIn](https://www.linkedin.com/in/ryan-barnett-b27635/)
- [Akamai author archive (legacy SITR blog)](https://blogs.akamai.com/sitr/author/ryan-barnett/)
- [Akamai author archive (new blog)](https://blogs.akamai.com/author/ryan-barnett/)
- [Dark Reading author archive](https://www.darkreading.com/author/ryan-barnett)
- [Security Boulevard author archive](https://securityboulevard.com/author/ryan-barnett/)
- [Tactical Web App Security blog (personal, archival)](https://tacticalwebappsec.blogspot.com/)
- [Web App Defender blog (personal, archival)](https://webappdefender.blogspot.com/)
- [Black Hat speaker page (US 2015)](https://www.blackhat.com/us-15/presenters/Ryan-Barnett.html)
- [Black Hat Arsenal (US 2014)](https://www.blackhat.com/us-14/arsenal/Ryan-Barnett.html)

## Key research / posts

- [Lost in Translation: Exploiting Unicode Normalization (Black Hat USA 2025)](https://i.blackhat.com/BH-USA-25/Presentations/USA-25-Barnett-Lost-In-Translation-Exploiting-Unicode-compressed.pdf)
  — With his daughter Isabella Barnett (`@4ng3lhacker`); first
  father-daughter pairing on a Black Hat main-stage briefing.
  ([talk listing](https://www.blackhat.com/us-25/briefings/schedule/#lost-in-translation-exploiting-unicode-normalization-44923))
  Covers visual confusables (e.g. fullwidth `<` U+FF1C bypassing a WAF
  that's only looking for ASCII `<`), overlong UTF-8 (Nimda-style),
  Unicode truncation, combining-character expansion, and database
  collation surprises (MySQL default `utf8mb4_0900_ai_ci` ignores
  accents and case). Ships updates to **ActiveScan++** for Unicode
  detection and leans on **Recollapse** / **Shazzer** for fuzzing
  normalization tables. Voted into PortSwigger's
  [Top 10 Web Hacking Techniques of 2025](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025).
- [HTTP/2 Request Smuggling (Akamai SITR, 2021-08-05)](https://blogs.akamai.com/sitr/2021/08/http2-request-smuggling.html)
  — Akamai's defender-side analysis of Kettle's HTTP/2 desync work;
  walks the CL/TE → HTTP/2 translation layer and the resulting smuggling
  primitives, with detection signatures.
- [Stopping Active Attacks with Penalty Box (Akamai)](https://www.akamai.com/blog/security/penalty-box)
  — Detection-then-temporary-block pattern. Cited in CT Ep 135 as the
  "right" alternative to instant outright blocking, since instant
  blocking gives attackers a fast oracle.
- [The Dark Side of APIs: Part 1 — API Overview (Akamai, 2018)](https://blogs.akamai.com/sitr/2018/04/the-dark-side-of-apis-part-1-api-overview.html)
  — Series framing API attack surface for defenders. Precursor to
  Akamai's App & API Protector positioning.
- [Magecart series — *Protecting Your Website Visitors From Magecart*](https://www.akamai.com/blog/security/protect-website-visitors-from-megacart),
  [*New Magecart-Style Campaign Abusing Legitimate Websites*](https://www.akamai.com/blog/security-research/new-magecart-hides-behind-legit-domains),
  [*The Art of Concealment: 404-Page Skimmer*](https://www.akamai.com/blog/security-research/magecart-new-technique-404-pages-skimmer)
  — Client-side skimmer detection patterns Akamai's Client-Side
  Protection & Compliance ships against. Useful for understanding what
  a major CDN/WAF actually catches vs misses on client-side compromise.
- [What You Should Know About BreakingWAF (Akamai)](https://www.akamai.com/blog/security-research/what-you-should-know-about-breakingwaf)
  — Akamai's response to the "BreakingWAF" research wave: triage of
  which classes of bypass actually work in production WAF deployments
  vs default/demo configs.
- [XSS Street-Fight (Black Hat DC 2011)](https://media.blackhat.com/bh-dc-11/Barnett/BlackHat_DC_2011_Barnett_XSS%20Streetfight-Slides.pdf)
  — Pre-CSP-era practical XSS detection/mitigation talk; still cited
  for context on WAF-driven XSS defenses.
- [Accidental Stored XSS in Zemanta "Related Posts" TypePad Plugin (2013)](https://webappdefender.blogspot.com/2013/04/accidental-stored-xss-flaw-in-zemanta.html)
  — Classic third-party-analytics-pixel injection write-up; Ryan tells
  this story in CT Ep 135 as the moment "watching your traffic"
  surfaces a bug nobody else can see.
- ModSecurity Core Rule Set — [OWASP CRS project](https://coreruleset.org/),
  [SpiderLabs/owasp-modsecurity-crs](https://github.com/SpiderLabs/owasp-modsecurity-crs)
  (anomaly-scoring redesign).
- [LWN feature on CRS 3.0 (2016)](https://lwn.net/Articles/709693/) —
  Independent write-up crediting Barnett with steering CRS to OWASP and
  introducing anomaly scoring.

## CT podcast appearances

- [2025-08-14 Ep 135 — Akamai's Ryan Barnett on WAFs, Unicode Confusables, and Triage Stories](../sources/podcasts/ct/20250814_rr5VvMx4dT0_Akamai_s_Ryan_Barnett_on_WAFs_Unicode_Confusables_and_Triage_Stories_Ep._135.en.vtt)
  — Show notes: [criticalthinkingpodcast.io/episode-135](https://www.criticalthinkingpodcast.io/episode-135-akamais-ryan-barnett-on-wafs-unicode-confusables-and-triage-stories/).
  Topics: virtual-patching workflow at WAF-vendor scale, AWS API
  Gateway whitelisting, Unicode normalization exploitation, CSP at the
  WAF layer, and the "sources world vs sinks world" framing for why
  WAFs structurally lag offensive technique.

## Notes

- **The "sources vs sinks" framing (from Ep 135).** Defenders live in
  the sources world (inspecting incoming bytes); attackers live in the
  sinks world (knowing how the backend will normalize, decode, parse,
  and evaluate). This asymmetry is *the* reason WAF bypasses keep
  working — and why his Unicode work is so productive: it lives
  precisely on the normalization mismatch between WAF input view and
  backend output view. Mental model for any bug-hunter probing a WAFed
  target: enumerate every transformation step between Akamai/Cloudflare
  edge and the origin app, look for one where the WAF saw one string
  and the sink saw another.
- **Virtual patching is the bread and butter.** Akamai's customer
  workflow is: bug-hunter or pentester reports a flaw → app owner needs
  weeks/months to patch → Akamai ships a custom WAF rule that blocks
  the specific exploit shape in hours. Understanding this is useful
  when reporting a bug on a CDN-fronted asset: the "fix" you see in
  production may be a virtual patch (WAF rule), not a code fix —
  variant-hunt aggressively, because the rule was written against the
  exact payload in your report.
- **Penalty Box > instant block.** Ryan's preferred posture: detect
  → score → temporary block, rather than block-on-first-match.
  Instant block gives an attacker a binary oracle (`did my payload trip
  the rule? yes/no` in <50ms) that accelerates bypass research.
- **Unicode is the rich seam right now.** Pair his Black Hat 2025 deck
  with CT Ep 103 (*Getting ANSI about Unicode Normalization*) and Ep 73
  (*Sandboxed IFrames and WAF Bypasses*) — together they're a complete
  toolkit. The fuzzing approach is: instrument every Unicode
  transformation function reachable from a sink (NFC/NFD/NFKC/NFKD,
  case folding, `toLowerCase` per-locale, idna), enumerate confusables
  via the official Unicode confusables.txt, then synthesise payloads
  whose canonical form is the malicious string but whose surface form
  evades signature WAFs.
- **CRS anomaly scoring is his lasting WAF-defender contribution.**
  Before his redesign, each ModSecurity rule blocked individually,
  producing famously high FP rates. The scoring model (each rule
  contributes a weighted score, decision happens at a configurable
  threshold) is now standard across modern WAFs and the conceptual
  ancestor of "paranoia level" tuning. Knowing this matters when
  bypassing CRS-derived rule sets: a single sub-threshold trigger is
  not blocked, so payloads engineered to fire only one weak rule slip
  through.
- **Father-daughter ops.** Isabella Barnett (`@4ng3lhacker`) co-authored
  the BHUSA 2025 talk and the precursor `BugBountyDEFCON` workshop the
  year prior. Worth tracking as a separate emerging researcher once she
  publishes solo work.
- **Cross-links to wiki techniques** (when those pages exist):
  Unicode-normalization → `../techniques/normalization/unicode-confusables.md`;
  WAF-bypass framing → `../techniques/waf-bypass/sources-vs-sinks.md`;
  HTTP/2 smuggling → `../techniques/smuggling/http2-desync.md`.
