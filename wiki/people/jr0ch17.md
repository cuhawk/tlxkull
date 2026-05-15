---
title: Jasmin Landry (JR0ch17)
slug: jr0ch17
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [jr0ch17]
role: hunter
primary_focus: server-side
tags: [person, role/hunter, focus/server-side, focus/oauth, focus/ssrf, focus/ssti, focus/recon]
inbound: []
---

## Identity

- **Real name:** Jasmin Landry
- **Primary handle:** `JR0ch17`
- **Role:** Part-time bug-bounty hunter; full-time security leadership at Nasdaq ("a hacker on Wall Street"). Frequently described in finance-meets-bounty terms — the day job is corporate security on the trading-venue side, bounty is evenings/weekends.
- **Location:** Canada.
- **Background:** ~10 years in IT before pivoting fully to security — started as a sysadmin (Windows/Linux, VMware, Cisco; MCSA/CCNA/VCP), moved to junior security analyst, then pentester after his then-boss spotted his bounty results. First paid bounty was a stored XSS in a Microsoft application three months into the security role.
- **Track record:** Multiple HackerOne Live Hacking Event awards and Bugcrowd Bug Bash wins; quoted in Yahoo and Forbes coverage. Consistent top-of-leaderboard finisher on private programs.

## Focus areas

- Server-side web (RCE, SSRF, SSTI, path traversal, file-upload chains)
- OAuth / SSO flow abuse — deep RFC-driven approach, often chained with HTML-injection
- GraphQL access-control / authorization at scale
- XXE via lesser-known W3 XML standards parsed across many endpoints
- Reconnaissance with light tooling but heavy manual application diving

## Online presence

- Blog: [blog.jr0ch17.com](http://blog.jr0ch17.com/) (HTTP, intermittent; archived posts indexed via search)
- X / Twitter: [@JR0ch17](https://twitter.com/JR0ch17)
- GitHub: [github.com/JR0ch17](https://github.com/JR0ch17) — bio: "Working from home". Notable repos:
  - [S3Cruze](https://github.com/JR0ch17/S3Cruze) — all-in-one AWS S3 bucket enumeration tool for pentesters
  - [rdse](https://github.com/JR0ch17/rdse) — recon.dev subdomain extractor
- HackerOne: [hackerone.com/jr0ch17](https://hackerone.com/jr0ch17) ([badges](https://hackerone.com/jr0ch17/badges), [hacktivity](https://hackerone.com/jr0ch17/hacktivity?type=user))
- Bugcrowd: [bugcrowd.com/JR0ch17](https://bugcrowd.com/JR0ch17)
- Talks:
  - DEF CON 33 Creator Stage 3 — ["Sometimes you find bugs, sometimes bugs find you"](https://defcon.org/html/defcon-33/dc-33-schedule.html) (2025-12-12)
  - Bugcrowd LevelUpX — ["How to Find Better Bugs with JR0ch17"](https://www.bugcrowd.com/resources/levelup/how-to-find-better-bugs-with-jr0ch17/)

## Key research / posts

- [No RCE? Then SSH to the box!](http://blog.jr0ch17.com/2018/No-RCE-then-SSH-to-the-box/) (2018-01-25) — CMS with default creds + LFD chained with file-upload path-traversal (`/../../tmp/test.txt`); service running as root let him drop a key into `~/.ssh/authorized_keys` and SSH in. Canonical example of "RCE without an RCE primitive."
- **HTML-injection + DOM Purify bypass via referrer-policy meta in detached DOM** — Discussed on CT Ep 61: chained an unpatched Chrome behaviour (referrer policies honoured from non-DOM-attached `<meta>` tags) with HTML injection and an OAuth redirect path-traversal to leak auth tokens, surviving DOM Purify sanitisation. Seeds [../techniques/oauth/](../techniques/) and [../techniques/dom-xss/](../techniques/) cross-link when those pages exist.
- **OAuth refresh-token race condition** — Concurrent requests without valid refresh tokens returned valid tokens belonging to other users; unconventional ATO primitive.
- **GraphQL broken-access-control chain to multi-tenant compromise** — External user → verbose-error admin-cred leak → tenant pivot. Methodology example of "stack low-impact findings into critical."
- **SSTI in email field → Ansible config injection → one-shot Jenkins RCE** — SSTI evaluated when the platform rendered the signup email into an Ansible playbook. Used Ansible's `lookup('pipe', ...)` to execute OS commands; hex-encoded the payload to bypass character filters; final payload was a one-shot RCE against an internal Jenkins instance executed on click. Configuration-file injection as a sink class.
- **Mass XXE via obscure W3 XML standards** — Reading platform docs surfaced a lesser-known XML spec accepted by nearly every endpoint; produced platform-wide XXE.
- **Multi-chain exploit (reflected XSS → cookie-based XSS → cookie stuffing → CORS bypass → cache poisoning)** — Exposed PII + financial data; cited in the Medium interview as a personal favourite.
- **Unauthenticated SSRF → AWS metadata → production keys** — Full production access from a single SSRF; same interview.

## CT podcast appearances

- [2024-03-07 Ep 61 — A Hacker on Wall Street - JR0ch17](../sources/podcasts/ct/20240307_eBKuDxH9B4k_A_Hacker_on_Wall_Street_-_JR0ch17_Ep._61.en.vtt) ([show notes](https://www.criticalthinkingpodcast.io/episode-61-a-hacker-on-wall-street-jr0ch17/), [HackerNotes](https://blog.criticalthinkingpodcast.io/p/jr0ch17-jasmin-landry-hacker-on-wallstreet), [YouTube](https://www.youtube.com/watch?v=eBKuDxH9B4k))

## Notes

- **Day-job / bounty split.** Full-time finance-sector security leadership; bounty is a deliberately part-time pursuit. Workflow optimised for high-signal sessions rather than time-on-glass — recon is light, app-diving is deep.
- **Methodology signature** (from LevelUpX + Ep 61):
  - Skip broad subdomain enumeration; go straight at the *core* app where functionality density is highest.
  - Intercept everything while browsing, then map auth, caching, CSRF, file-upload, password-reset, integrations, HTTP version, template engines.
  - Read product documentation and developer-facing material (LinkedIn job posts, engineering blogs, GitHub orgs of staff) for hints about internal stacks.
  - Rename Burp Repeater tabs aggressively; group multi-step chains; export to ElasticSearch for tech-fingerprint search.
  - Stack low-impact bugs into chains — most of his top-payout reports are chains, not single primitives.
- **OAuth depth.** Long server-side focus eventually pulled him into OAuth because of "the amount of room there is for error." Studies the RFCs and PortSwigger / Auth0 / Frans Rosén's *Dirty Dancing OAuth* materials.
- **Tone.** Quiet, collaborative; explicitly credits collab as a multiplier in the LevelUpX talk.
- **No major Yelp/Snapchat disclosed reports surfaced under his handle** during this pass — disclosed-report sleuthing inconclusive. Most of his public reports remain private to programs.

## References

- HackerOne interview/profile: [hackerone.com/jr0ch17](https://hackerone.com/jr0ch17)
- Medium interview: [Smith3dx — Interview with Veteran Hacker/Bug Bounty Hunter — Jasmin Landry](https://igbinosuneric.medium.com/interview-with-veteran-hacker-bug-bounty-hunter-meet-jasmin-landry-7351108e7f7)
- CT Ep 61 HackerNotes: [blog.criticalthinkingpodcast.io/p/jr0ch17-jasmin-landry-hacker-on-wallstreet](https://blog.criticalthinkingpodcast.io/p/jr0ch17-jasmin-landry-hacker-on-wallstreet)
