---
title: Ciarán Cotter (MonkeHack)
slug: ciaran-cotter
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [monkehack, monke]
role: researcher
primary_focus: client-side
tags: [person, role/researcher, role/hunter, focus/client-side, focus/oauth, focus/postmessage, focus/websockets, focus/csti]
inbound: []
---

# Ciarán Cotter (MonkeHack)

## Identity

- Real name: Ciarán Cotter. Publishes under handle **MonkeHack** (often shortened to "Monke").
- Irish-Japanese web hacker based in Scotland. Full-time bug bounty hunter since April 2024.
- Founder of **Simian Security**. Previously a SaaS security researcher at **AppOmni**.
- Researcher in the **Critical Thinking Bug Bounty Podcast research lab** (Critical Research Lab / CT lab).
- HackerOne ambassador (Ireland). Four-time Team Ireland participant in the European Cybersecurity Challenge (ECSC).

## Focus areas

- **Client-side web hacking** — primary lane: DOM XSS, postMessage abuse, iframe context-hopping, devtools-driven sink discovery.
- **OAuth attack chains** — dirty redirect paths, double-URL-hash tricks, state fixation against COOP/COEP-protected flows.
- **Client-Side Template Injection (CSTI)** — leveraging CSTI as an unauthenticated ATO primitive in conjunction with postMessage / frame-ancestors bypasses.
- **WebSockets** — handshake-body / frame-confusion research, including WebSocket-flavored request smuggling against chunked-encoding back ends.
- **AI hacking** — secondary focus; speaks publicly on AI/LLM application security alongside client-side topics.

## Online presence

- Newsletter / blog: [monke.ie](https://www.monke.ie/) (weekly newsletter "MonkeHacks", currently ~#97).
- X / Twitter: [@monkehack](https://x.com/monkehack).
- LinkedIn: [linkedin.com/in/ciarán-cotter](https://www.linkedin.com/in/ciar%C3%A1n-cotter/).
- Speaker profile: [sessionize.com/monkehack](https://sessionize.com/monkehack/).
- Company: Simian Security (sole proprietor; no separate site indexed at time of writing).

## Key research / posts

- **[Monke's Guide to Bug Bounty Methodology](https://www.monke.ie/)** (2024-08-23, ~30-min read) — Long-form methodology piece on his bug-bounty workflow end-to-end; the most-cited entry point to his content. Announced on X at [status/1827019863304384831](https://x.com/monkehack/status/1827019863304384831).
- **[Exfiltrating Data from Sandboxed Documents](https://www.monke.ie/)** (2024-06-14, ~7-min read) — Technique writeup on extracting data from documents loaded under `sandbox` / restrictive frame contexts. Relevant to client-side data exfiltration patterns.
- **[Don't Become The Hallucination](https://www.monke.ie/)** (2024-05-16, ~7-min read) — Reflective post on bug-bounty mindset / verification discipline (avoiding self-deception while triaging).
- **Cognitive biases in bug bounty** — short post on bias traps in hunting; announced at [x.com/monkehack/status/1640199742939381762](https://x.com/monkehack/status/1640199742939381762).
- **Salesforce Chat-Widget postMessage → OAuth-code leak** (Bugcrowd target, discussed in CT Ep 112) — Chain: `window.open` to fixate state → redirect with double URL hash fragment → smuggle a `code` parameter in the hash → postMessage into the Salesforce Chat Widget (overly trusting origin check) → iframe-hop between frames → hijack the logging frame containing the OAuth code → exfiltrate to attacker origin. Reference example of postMessage XSS chained into OAuth-code exfiltration.
- **WebSocket-handshake body misinterpretation** (research discussed in CT Ep 112) — Sending a body during the WebSocket Upgrade request causes the back end to consume that body as the first WebSocket frame; combined with `Transfer-Encoding: chunked` on the response, this creates a WebSocket-flavored request-smuggling primitive at the proxy/back-end boundary.

## Talks / workshops

- **Workshop: Client-Side Hacking with Devtools** (Sessionize listing) — Devtools-first workflow for spotting client-side vulnerabilities: common sinks, gadget chaining, live triage with the browser's built-in tooling.
- **HackAIcon 2025 speaker** (announced via [@ethiack on X](https://x.com/ethiack/status/1947665439691039047)) — Client-side and AI hacking.

## CT podcast appearances

- [2025-02-27 Ep 112 — Interview with Ciarán Cotter (MonkeHack) Critical Lab Researcher and Full-time Hunter](../sources/podcasts/ct/20250227_Wb7SRLIYWAk_Interview_with_Ciaran_Cotter_MonkeHack_Critical_Lab_Researcher_and_Full-time_Hunter_Ep._112.en.vtt) — Bug-hunting journey, transition to full-time, two detailed chains (Salesforce-Chat-Widget postMessage → OAuth-code leak; WebSocket-handshake body / chunked-encoding smuggling). Episode page: [criticalthinkingpodcast.io/episode-112-interview-with-ciaran-cotter-critical-lab-researcher-h1-irish-ambassador](https://www.criticalthinkingpodcast.io/episode-112-interview-with-ciaran-cotter-critical-lab-researcher-h1-irish-ambassador/); HackerNotes: [blog.criticalthinkingpodcast.io/p/hackernotes-ep-112-interview-with-monkehack-critical-lab-researcher-and-full-time-hunt](https://blog.criticalthinkingpodcast.io/p/hackernotes-ep-112-interview-with-monkehack-critical-lab-researcher-and-full-time-hunt); YouTube: [youtube.com/watch?v=Wb7SRLIYWAk](https://www.youtube.com/watch?v=Wb7SRLIYWAk); Spotify: [open.spotify.com/episode/7p6T3Pd2OZBoyJilCxjFo0](https://open.spotify.com/episode/7p6T3Pd2OZBoyJilCxjFo0).

## Notes

- **Critical Research Lab affiliation.** One of the named full-time researchers operating under the Critical Thinking / Critical Research Lab umbrella (Justin Gardner's research org around the podcast). Lab affiliation is the bridge between his independent publishing on monke.ie and the CT podcast network.
- **Signature style — chain over single-bug.** Both publicly-discussed bugs (Salesforce widget OAuth leak; WebSocket handshake body smuggling) are multi-stage chains stitching small client-side primitives (postMessage trust, iframe traversal, hash fragment quirks, handshake framing) into a deliverable impact. Treat his content as chain-construction lessons, not isolated-bug writeups.
- **Devtools-first triage** — his workshop pitch and methodology post both lead with browser DevTools as the primary client-side instrumentation surface (sinks, breakpoints, frame structure) rather than external proxies/tools. Useful pairing with our static-taint output: js_analyzer points at the sink, DevTools confirms reachability.
- **Newsletter cadence** — `MonkeHacks #NN` is roughly weekly; periodic methodology / mindset posts in between. The numbered issues are short notes; the named long-form posts (`Monke's Guide…`, `Don't Become The Hallucination`, `Exfiltrating Data from Sandboxed Documents`) are where the techniques live.
- **No public GitHub profile** identified for the MonkeHack handle at time of writing; the `MonKe`, `projectmonke`, and other "monke"-named GitHub orgs that surface in search are unrelated. Tooling output (if any) currently ships through blog posts, not a public repo.
- **Hive Five profile** at [hivefive.community/p/buzz-boost-ciaran-cotter-aka-monkehack](https://www.hivefive.community/p/buzz-boost-ciaran-cotter-aka-monkehack) gives biographical context (Irish-Japanese, Scotland-based, full-time since April 2024).
