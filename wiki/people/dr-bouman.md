---
title: Dr. Jonathan Bouman
slug: dr-bouman
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [jonathanbouman]
role: dual
primary_focus: web
tags: [person, role/hunter, role/dual, focus/web, focus/amazon, focus/mobile, focus/healthcare, focus/ssti, focus/file-upload]
inbound: []
---

# Dr. Jonathan Bouman

## Identity

- **Real name:** Jonathan Bouman
- **Primary handle:** `jonathanbouman` (HackerOne, Medium, X).
- **Based:** Netherlands.
- **Role:** Dual career — practicing medical doctor / healthcare
  professional and full-spectrum bug bounty hunter. Elite-level
  Live Hacking Event (LHE) participant.
- **Domain specialty:** Web application security with a healthcare /
  high-stakes-infrastructure lens. Long-running Amazon hunter (~6+
  years on the program as of Ep 93).

## Focus areas

- Web application vulnerabilities (XSS, SSTI, SQLi, LFI, unrestricted
  file upload, leaked secrets).
- Amazon platform (web + Android app) — primary target for years.
- Mobile application testing (Android via `apk-mitm`, iOS via
  `checkra1n` jailbreak for cert pinning bypass).
- Healthcare / medical-system security — applies clinical domain
  knowledge to threat-model EHRs, doctor workflows, ransomware
  exposure.
- Burp Suite customization (custom Scanner profiles, Param Miner for
  hidden-parameter discovery).

## Online presence

- [Medium — @jonathanbouman](https://medium.com/@jonathanbouman)
- [X / Twitter — @JonathanBouman](https://x.com/jonathanbouman)
- [HackerOne — jonathanbouman](https://hackerone.com/jonathanbouman)

## Key research / posts

- [Unrestricted File Upload at Apple.com](https://medium.com/@jonathanbouman/how-i-hacked-apple-com-unrestricted-file-upload-bcda047e27e3)
  — Misconfigured S3 bucket granting full write access to an
  apple.com subdomain.
- [Reflected XSS at Philips.com](https://medium.com/@jonathanbouman/reflected-xss-at-philips-com-e48bf8f9cd3c)
  — Classic reflected XSS writeup; full disclosure chain.
- [Blind SQL Injection at fasteditor.hema.com](https://medium.com/@jonathanbouman/blind-sql-injection-at-fasteditor-hema-com-6ac140c0d1a3)
  — Time-based blind SQLi with `SLEEP()` exfiltration walkthrough on
  a HEMA subdomain.
- [Persistent XSS at AH.nl](https://medium.com/@jonathanbouman/persistent-xss-at-ah-nl-198fe7b4c781)
  — Stored XSS on Dutch grocery giant Albert Heijn, fired for every
  visitor.
- [Leaked Salesforce API access token at IKEA.com](https://medium.com/@jonathanbouman/leaked-salesforce-api-access-token-at-ikea-com-132eea3844e0)
  — Step-by-step token discovery → data exposure.
- LFI in IKEA.com PDF library (linked from his
  [X announcement](https://x.com/JonathanBouman/status/1042531450451648512))
  — Local file inclusion via a PDF generator; doubled as a
  responsible-disclosure case study.
- **CVE-2024-45186** — Unauthenticated SSTI in FileSender exposing
  database and S3 credentials; a ~10-year-old latent bug.
- **Dutch healthcare RCE** — Arbitrary executable upload to "doctor's
  notes" attachment surface, any user could register and ship a
  malicious file to a clinician, achieving RCE on the physician's
  device. Discussed on Ep 93.
- Stored XSS in WordPress Paytium payment plugin enabling privilege
  escalation to admin (older finding from his Medium archive).

## CT podcast appearances

- [2024-10-17 Ep 93 — A Chat with Dr. Bouman - Life as a Hacker and a Doctor](../sources/podcasts/ct/20241017_wBfON--LkYY_A_Chat_with_Dr._Bouman_-_Life_as_a_Hacker_and_a_Doctor_Ep.93.en.vtt)
  — HackerNotes recap:
  [blog.criticalthinkingpodcast.io/p/hackernotes-ep-93-a-chat-with-dr-bouman-life-as-a-hacker-and-a-doctor](https://blog.criticalthinkingpodcast.io/p/hackernotes-ep-93-a-chat-with-dr-bouman-life-as-a-hacker-and-a-doctor).
  Episode page:
  [criticalthinkingpodcast.io/episode-93-a-chat-with-dr-bouman-life-as-a-hacker-and-a-doctor](https://www.criticalthinkingpodcast.io/episode-93-a-chat-with-dr-bouman-life-as-a-hacker-and-a-doctor/).
  Covers: dual physician + hunter career; origin story (Amazon
  affiliate program → dissecting the Amazon Android app → first XSS);
  ethics of hunting while practicing medicine; healthcare-system
  security; LHE collaboration with ZSeano (placed 1st / 3rd at a
  recent event).

## Notes

- **Dual career as a methodology multiplier.** Domain knowledge of
  clinical workflows lets him reason about which vulnerabilities
  actually matter in healthcare (ransomware-relevant RCE vs noisy
  low-impact issues). Worth modeling: hunters with non-security domain
  expertise can out-recon generalists in those verticals.
- **Amazon depth specialist.** ~6 years on one program. Implication:
  long-tail depth beats breadth for big static programs; he keeps
  finding novel surface in mobile clients and edge features.
- **Mobile tooling stack (Ep 93).** `apk-mitm` for Android cert
  unpinning; `checkra1n` jailbreak for iOS pinning bypass; Param Miner
  for hidden parameter discovery; custom Burp Scanner profiles tuned
  per bug-class. Useful for the `tools/` corner when we write up
  mobile-testing playbook.
- **Responsible disclosure ethic.** Multiple writeups frame the
  vendor-comms process as part of the story — not just the pop.
  Reflects his physician background: harm-reduction posture.
- **SSTI lens.** CVE-2024-45186 (FileSender) is a high-impact
  unauth-to-RCE-adjacent SSTI in an open-source academic-network tool
  used widely in EU research/edu — worth a cross-link if/when we add
  `techniques/ssti/` pages.
