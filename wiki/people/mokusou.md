---
title: Mokusou (So Sakaguchi)
slug: mokusou
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [mokusou, mokusou4]
role: hunter
primary_focus: web
tags: [person, role/hunter, focus/web, focus/client-side, focus/sanitizer-bypass, focus/japan, focus/ct-mentee]
inbound: []
---

## Identity

- **Real name:** So Sakaguchi
- **Primary handle:** `Mokusou` (HackerOne: `mokusou`, X: `Mokusou4`)
- **Role:** Bug-bounty hunter. Came up through Critical Thinking mentorship (Justin Gardner) — went from mentee on early-career episode to working hunter by 2025.
- **Location:** Yokohama, Japan.
- **Languages:** Japanese, English, French.

## Focus areas

- Web application security (HackerOne primary platform)
- HTML/CSS sanitizer bypass research (Rails ActionView / Rails::HTML::Sanitizer)
- Client-side / XSS
- Open-source library research (Ruby on Rails ecosystem)

## Online presence

- HackerOne: [hackerone.com/mokusou](https://hackerone.com/mokusou)
- X / Twitter: [@Mokusou4](https://x.com/Mokusou4)
- LinkedIn: [in/so-sakaguchi-398691210](https://jp.linkedin.com/in/so-sakaguchi-398691210)

(No public blog or GitHub-research-repo found as of 2026-05-15. Disclosures live on HackerOne.)

## Key research / posts

- **ActionView sanitize helper bypass with math-related tags** (Rails / Ruby on Rails, 2025-02-06, HackerOne disclosure) — XSS in Rails::HTML::Sanitizer when HTML5 sanitization is enabled and developers override allowed tags to include both `math` and `style` (or `svg` and `style`). Mitigations: drop `style` / `math` / `svg` from override list, or downgrade to HTML4 sanitization, or upgrade Nokogiri. Disclosure mirror: [redpacketsecurity.com/...-math-related-tags-mokusou](https://www.redpacketsecurity.com/hackerone-bugbounty-disclosure-actionview-sanitize-helper-bypass-with-math-related-tags-mokusou/).
- **ActionView sanitize helper bypass with style and math** (Rails, 2025-02-06, companion report) — Sibling disclosure expanding the same sanitizer-override primitive. Mirror: [redpacketsecurity.com/...-with-style-and-math-mokusou](https://www.redpacketsecurity.com/hackerone-bugbounty-disclosure-actionview-sanitize-helper-bypass-with-style-and-math-mokusou/).

## CT podcast appearances

- [2025-03-20 Ep 115 — Mentee to Career Hacker - Mokusou (So Sakaguchi)](../sources/podcasts/ct/20250320_zELFGXP6oeA_Mentee_to_Career_Hacker_-_Mokusou_So_Sakaguchi_Ep_115.en.vtt) — live mentorship session with Justin; bonus segment recorded in Japanese. Episode page: [criticalthinkingpodcast.io/episode-115](https://www.criticalthinkingpodcast.io/episode-115-mentee-to-career-hacker-mokusou-so-sakaguchi/) ([rss.com mirror](https://rss.com/podcasts/ctbbpodcast/1942544/)).

## Notes

- Japanese hunter; one of the few CT-graduated mentees with a public success arc traceable across multiple episodes. Justin lived in Yokohama and has a long-running JP hunter network (see also `0xlupin.md` for the Tokyo/JP connection).
- Signature work to date is library-level sanitizer-bypass research against Rails — the kind of finding that ships as a CVE + upstream patch rather than a per-program bounty. Worth watching for follow-ups against other HTML-sanitizer libraries (sanitize-html, DOMPurify ports, Rails HTML5 path).
- No personal blog yet. Track HackerOne disclosures and X for new writeups; revisit this page on each CT re-appearance.
- Cross-ref: `wiki/techniques/xss/sanitizer-bypass.md` (queued) should cite the math+style Rails sanitizer pattern when written.
