---
title: Joel Margolis (teknogeek)
slug: joel-margolis
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [teknogeek, 0xteknogeek]
role: hunter
primary_focus: tooling
tags: [person, role/host, role/hunter, focus/tooling, focus/recon, focus/mobile]
inbound: []
---

# Joel Margolis (teknogeek)

## Identity

- **Real name:** Joel Margolis
- **Primary handle:** `teknogeek` (GitHub, HackerOne); `0xteknogeek` on X/Twitter
- **Role:** Hunter + ex-cohost of Critical Thinking podcast (Eps 1–100). Full-time security engineer at Yahoo / The Paranoids.
- **Location:** Connecticut / New York, USA
- **Self-description (GitHub bio):** "Hacker, Engineer"

Joel cut his teeth reverse-engineering mobile apps as a contractor, then
broke into bug bounty at HackerOne's H1-702 live event where his first
report — a high-severity bug on Uber — was also his first paid bounty.
He has hacked on Yahoo, Uber, Airbnb, and many private programs. He is
employed full-time on Yahoo's internal red-team / product-security org
(historically branded "The Paranoids").

## Focus areas

- **Mobile app security** — Android/iOS reverse engineering, deep-link
  abuse, hardcoded secrets, certificate-pinning bypass. See
  [../techniques/mobile/](../techniques/mobile/).
- **SSRF detection** — author of `ssrf-sheriff`, the canonical
  collaborator-style SSRF beacon. See
  [../techniques/server-side/](../techniques/server-side/).
- **Recon tooling** — DNS resolution at scale, subdomain enumeration,
  Android URL-scheme extraction. See [../techniques/recon/](../techniques/recon/).
- **Open-source security tooling** — primary creative output is
  code, not blog posts. Tools are usually born from a specific live-event
  need (e.g. SSRF Sheriff for Uber H1-4420) then open-sourced.

## Online presence

- [GitHub — teknogeek](https://github.com/teknogeek) — 100+ repos, 561+ followers
- [X / Twitter — @0xteknogeek](https://x.com/0xteknogeek)
- [HackerOne — teknogeek](https://hackerone.com/teknogeek)
- [Bug Bounty Forum AMA (2018-ish)](https://bugbountyforum.com/blog/ama/teknogeek/) — origin story + methodology
- [HackerOne Hacker Interview (YouTube)](https://www.youtube.com/watch?v=nv_a5KwtmbA)

## Key research / posts

- **[ssrf-sheriff](https://github.com/teknogeek/ssrf-sheriff)** (Go, ~338★) —
  A configurable SSRF "sheriff" / out-of-band responder. Responds to any
  HTTP method, returns a configured secret token embedded in JSON, XML,
  HTML, CSV, TXT, PNG, JPEG, GIF, MP3, MP4 payloads — so the same beacon
  fires regardless of which content-type the target's SSRF sink expects.
  Built for the Uber **H1-4420** London 2019 live-hacking event; inspired
  by Frans Rosén's BountyCon '19 Singapore talk. Has become a standard
  reference SSRF receiver alongside `interactsh` / Collaborator.
  See [../techniques/server-side/](../techniques/server-side/).

- **[get_schemas](https://github.com/teknogeek/get_schemas)** (Python, ~130★) —
  Dumps every URL scheme / deep-link handler declared by an Android APK.
  Useful for surfacing intent-based attack surface (custom schemes, app
  links) before dynamic analysis with Frida. Cross-link:
  [../techniques/mobile/](../techniques/mobile/).

- **[fresh.py](https://github.com/teknogeek/fresh.py)** (Python, ~87★) —
  Multi-threaded DNS resolver validator. Front-end of a recon pipeline:
  feed it a subdomain word-list, get back only the ones that resolve, with
  resolver rotation to avoid wildcard poisoning. Cross-link:
  [../techniques/recon/](../techniques/recon/).

- **[DisARMPy](https://github.com/teknogeek/DisARMPy)** (Python) — ARM
  disassembler with pseudo-code generation. Older tool, reflects Joel's
  reverse-engineering roots before bug bounty.

- **HackerOne interview & AMA (Bug Bounty Forum)** — methodology distilled:
  decompile mobile apps before installing, proxy through Charles/Burp,
  hunt for hardcoded keys + certificate-pinning gaps; on web, prioritise
  20–30 min of "use the product like a normal user" before automated
  recon.

## CT podcast appearances

Joel co-hosted **Critical Thinking — Bug Bounty Podcast** with Justin
Gardner (rhynorater) from launch through Ep 100. He stepped away from
the cohost seat in Dec 2024 to refocus on full-time work at Yahoo, with
Shift (the AI-tooling project) and later gr3pme taking the cohost role.

Selected episodes (CT host seat was every-episode through Ep 100, only
guest-episodes are listed individually below):

- **2024-12-05 Ep 100 — 8 Fav Bugs of 2024, Farewell Joel, Hello Shift**:
  [local transcript](../sources/podcasts/ct/20241205_ANYtLQrT-F0_8_Fav_Bugs_of_2024_Farewell_Joel_Hello_Shift_-_Cursor_of_Hacking_Ep._100.en.vtt)
  — milestone + Joel's official farewell as cohost; unveils Shift, the
  AI-assisted hacking tool.
- **2023-02-?? Ep 6 — Mobile Hacking Attack Vectors with Teknogeek**:
  [Critical Thinking site](https://www.criticalthinkingpodcast.io/episode-6-mobile-hacking-attack-vectors-with-teknogeek-joel-margolis/)
  / [Spotify](https://open.spotify.com/episode/7hNkE6A8SvjhuCs5SJCt1o)
  — deep dive on his mobile methodology (transcript not in local
  `sources/podcasts/ct/`; cite external link).

(All other Eps 1–99 had Joel as cohost; not enumerated here. When a
specific Ep is ingested via `ctbb-ingest`, add it to this list.)

## Notes

- **Working style:** ships tools, not blog posts. If you're looking for
  Joel's research, look at his GitHub repos and live-event credits, not a
  personal blog (he doesn't keep one).
- **Live-event presence:** built a reputation through HackerOne live
  events (H1-702 debut, H1-4420 London where SSRF Sheriff was born).
- **Departure from CT (2024-12):** explicitly returning as a guest, not
  a permanent exit from the bug-bounty scene; the framing on Ep 100 is
  "farewell as cohost, hello Shift" — Shift (Cursor of Hacking) is
  introduced as the next chapter for the pod, not as Joel's replacement
  in his hunting career.
- **Day job:** Yahoo / The Paranoids product security. This narrows the
  programs he can publicly hack — expect more vendor-side tooling
  output and less Yahoo-target output going forward.
- **Wiki cross-refs to seed when relevant techniques are written:**
  - `techniques/server-side/ssrf-out-of-band.md` → link `ssrf-sheriff`.
  - `techniques/mobile/android-deep-link-enum.md` → link `get_schemas`.
  - `techniques/recon/dns-resolver-validation.md` → link `fresh.py`.
