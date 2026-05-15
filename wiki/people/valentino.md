---
title: Valentino Massaro
slug: valentino
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [valent1nee, valent1ne]
role: hunter
primary_focus: web
tags: [person, role/hunter, focus/web, focus/client-side, focus/xss, focus/sanitizer-bypass, focus/google-vrp]
inbound: []
---

## Identity

- **Real name:** Valentino Massaro
- **Primary handle:** `valent1nee`
- **Role:** Bug-bounty hunter focused on Google VRP and client-side web research. CT Ep 130 guest (2025-07-10).
- **Location:** Buenos Aires, Argentina. Computer Science student at the University of Buenos Aires.
- **Track record:** "Best Newcomer" at Google bugSWAT Las Vegas. Confirmed Google VRP payouts include $3,133.70 (Vertex AI command injection) and $20,000 (Hacking Gemini multi-layered sanitizer chain). Origin story is the title of his CT episode: hacking Minecraft servers at ~12 (bypassing the auth flow on internal minigame servers) into bug bounty proper.

## Focus areas

- Client-side web / XSS
- HTML sanitizer bypasses (markdown → HTML pipelines, mXSS-adjacent)
- Google VRP — Google Cloud (Vertex AI), Gemini, Colaboratory
- .NET deserialization (discussed on CT Ep 130)
- Creative / unusual attack chains — explicitly called out by Justin on CT 130 as "hyper creative"

## Online presence

- Blog: [buganizer.cc](https://buganizer.cc/) ("Valentino's issue tracker") — primary writeup venue.
- RSS: [buganizer.cc/feed.xml](https://buganizer.cc/feed.xml)
- X / Twitter: [@valent1nee](https://x.com/valent1nee)
- GitHub: [github.com/valent1nee](https://github.com/valent1nee) — pinned: `blog`, `vulnz`, `ReverseShell-Java` (fork), `awesome-google-vrp-writeups` (fork of xdavidhu), `ct-search` (CT podcast transcript search tool).
- CT guest page: [criticalthinkingpodcast.io/guests/valentino](https://www.criticalthinkingpodcast.io/guests/valentino/)
- Talk announcement (ekoparty 2025 Bug Bounty Village Turbo Talk, "Hunting in Google Cloud: Command injection in Vertex AI"): [Bug Bounty Argentina post](https://x.com/BugBountyArg/status/1975632433518436819)

## Key research / posts

- **Hacking Gemini: A Multi-Layered Approach** ([buganizer.cc/hacking-gemini-a-multi-layered-approach-md](https://buganizer.cc/hacking-gemini-a-multi-layered-approach-md.html), 2025-11) — Gemini markdown sanitizer bypass chained with a Colaboratory markdown sanitizer bypass. $20,000 Google VRP payout. Canonical reference for AI-product markdown→HTML sanitizer attack surface.
- **My first bug in Google Cloud: Command injection in Vertex AI** ([buganizer.cc/bug_vertex_ai](https://buganizer.cc/bug_vertex_ai), 2025-07) — unescaped `fileUri` field embedded into generated code snippets in Vertex AI Studio leading to command injection. $3,133.70. Subject of his ekoparty 2025 Turbo Talk.
- **XSS allows account takeover in DeepSeek Chat** ([buganizer.cc/deepseek_xss](https://buganizer.cc/deepseek_xss), 2025-03) — client-side XSS pivot to ATO on DeepSeek's chat product. AI-product client-side surface, same family as the Gemini work.
- **Bypassing the sanitizer: Wormable XSS in MercadoLibre** ([buganizer.cc/chatxss](https://buganizer.cc/chatxss), 2024-09) — HackerOne #1675516. Wrapping disallowed tags inside enough unclosed `<p>` tags tricked the sanitizer; wormable propagation via MercadoLibre chat. The signature "patient sanitizer fuzzing" finding referenced on CT 130.
- **A Journey Into Finding Vulnerabilities in the PMB Library Management System** ([buganizer.cc/pmb](https://buganizer.cc/pmb), 2024-02) — earlier CVE-style writeup on an open-source library system; first public buganizer.cc post.

## CT podcast appearances

- [2025-07-10 Ep 130 — Minecraft Hacks to Google Hacking Star - Valentino](../sources/podcasts/ct/20250710_cHQXlF4p-Ro_Minecraft_Hacks_to_Google_Hacking_Star_-_Valentino_Ep_130.en.vtt)

## Notes

- **Origin story** — got into hacking around age 12 via Minecraft: ran servers, reverse-engineered how minigames were wired together, first real bug was connecting directly to internal minigame servers and skipping the public-facing auth flow. The "Minecraft → Google" arc is the framing of CT 130.
- **Signature style** — patient sanitizer fuzzing on markdown/HTML pipelines, especially in AI products (Gemini, Colab, DeepSeek). Pairs sanitizer bypass with downstream impact (wormable propagation, ATO, source-code leak). The Vertex AI command-injection bug shows he also exploits non-XSS server-side surface when the AI product generates code from user-controlled fields.
- **Hyper-creative framing** — Justin's CT 130 framing. Look at his writeups before reaching for known payloads on AI-product sanitizers; he often finds a class of bypass rather than a single payload.
- **bugSWAT Best Newcomer (Vegas)** — entered the Google VRP regular-collaborator circle via the in-person Vegas event. Tracks alongside `0xlupin` / `rez0` / `rhynorater` as Google VRP / AI VRP regulars; expect future collabs.
- **`ct-search` repo** — he himself wrote a CT podcast transcript search tool. Useful pointer for our own `wiki/sources/podcasts/ct/` corpus.
- **Spanish-language community ties** — Bug Bounty Argentina / ekoparty Bug Bounty Village. If we ever need a SP-language pivot for AI-VRP research, this is the node.
