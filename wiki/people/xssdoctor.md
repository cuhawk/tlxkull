---
title: Jonathan Dunn (XSSDoctor)
slug: xssdoctor
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [xssdoctor]
role: hunter
primary_focus: client-side
tags: [person, role/hunter, focus/client-side, focus/cspt, focus/xss, focus/postmessage, focus/framework-routing]
inbound: []
---

# Jonathan Dunn (XSSDoctor)

## Identity

- Real name: **Jonathan Dunn**. Handle **XSSDoctor**.
- Day-job cardiologist; bug-bounty hunter on the side. GitHub bio: "Hacker and cardiologist. Not necessarily in that order."
- Started hacking during COVID (~2020–2021) on Hack The Box / CTFs, transitioned to bug bounty after consuming the Critical Thinking podcast end-to-end.
- Runs the monthly **CTBB Discord hackalongs** with BusFactor — community-facing role inside the CTBB orbit.

## Focus areas

- **Client-side path traversal (CSPT)** — the signature topic. Comprehensive comparison of how frontend routers decode `%2F` in path params, and how that turns into CSPT/CSRF/XSS depending on the sink.
- **Client-side XSS chains** — postMessage handlers, third-party iframe trust, hash-routing sinks. CT's "Bug Drop" episode showcases a chained `*.target.com` postMessage trust → AI assistant takeover.
- **Framework fingerprinting** — passive detection of React Router, Next.js, Vue Router, Nuxt, Angular, SvelteKit, Astro, Ember, SolidStart, Remix from client artifacts, used to gate the right CSPT primitive.
- **GraphQL recon** — `graphqlMaker` extracts GraphQL operations out of bundled JS for further fuzz.
- **AI-assisted recon tooling** — `multidoc`, `jscollab`, `ai_subdomain`: small LLM-glue utilities for hunter workflows.

## Online presence

- X / Twitter: [@xssdoctor](https://x.com/xssdoctor).
- GitHub: [github.com/xssdoctor](https://github.com/xssdoctor).
- HackerOne: [hackerone.com/xssdoctor](https://hackerone.com/xssdoctor).
- Threads: [@xssdoctor](https://www.threads.com/@xssdoctor).

> No standalone blog at xssdoctor.com or medium.com/@xssdoctor turned up in search. Long-form research lives on the CTBB research lab (lab.ctbb.show) and in the `cspt_research` GitHub README.

## Key research / posts

- **[The Dot-Dot-Slash That Frameworks Hand You: CSPT Across Every Major Frontend Framework](https://lab.ctbb.show/research/the-dot-dot-slash-that-frameworks-hand-you)** (2026-04-02, CTBB lab) — Decoding pipeline audit across 10 frontend frameworks. Headline findings: React Router and Vue Router fully decode `%2F` in path params before handing them to dev code (clean CSPT); Angular decodes after matching (still exploitable); SolidStart never calls `decodeURIComponent` on path params (only safe one); Next.js page components re-encode but route handlers auto-decode (secondary traversal); SvelteKit / Nuxt decode universally and expose server-side SSRF; Ember dynamic vs wildcard routes differ in final decoding. All frameworks decode query params unconditionally. Escalates to XSS via `dangerouslySetInnerHTML` / `v-html` / `{@html}` sinks.
- **[cspt_research GitHub repo](https://github.com/xssdoctor/cspt_research)** — Runnable per-framework labs (`*-cspt-lab/`), per-framework research notes (`*-research/`), the 54 KB `cspt-framework-notes.md` master reference, plus two tools: `cspt-analyzer` (Caido plugin: framework detection + route extraction) and `cspt-devtools-extension` (Chrome DevTools panel for in-browser CSPT detection). Seeds `../techniques/cspt/framework-decode-differential.md` (and per-framework siblings) and `../tools/caido/cspt-analyzer.md`.
- **[HackerNotes Ep. 168 — Client-Side Path Traversals Across Every Framework, with XSSDoctor](https://blog.criticalthinkingpodcast.io/p/hackernotes-ep-168-client-side-path-traversals-across-every-framework-with-xssdoctor)** (2026-04-02) — Written companion to Ep 168. Includes the React Router `matchPath` case-sensitivity quirk: `%252F` (uppercase hex) triggers double-decode, `%252f` (lowercase) does not, due to a missing regex flag. Methodology section: three URL injection sources ranked by impact (path > query > hash); parameter substitution + proxy rule-matching to confirm HTML injection via CSPT.
- **Bug Drop: Sick XSS Chain** ([CT video page](https://www.criticalthinkingpodcast.io/videos/bug-drop-xssdoctors-sick-xss-chain/) / [YouTube](https://www.youtube.com/watch?v=oA1kooSC5pU)) (2025-02-19) — Home-automation platform with an AI assistant that controlled locks, garage doors, alarms. PostMessage listener on the AI interface trusted any `*.target.com` origin; chained subdomain XSS into full home takeover. The "client-side XSS into real-world impact" reference chain in CT's catalogue.
- **[graphqlMaker](https://github.com/xssdoctor/graphqlMaker)** — Pulls GraphQL operations and types out of bundled JS, optionally uses an LLM to synthesize valid queries from the extracted schema fragments. Useful pre-fuzz step on SPA targets.
- **DoctorScan** (mentioned on Ep 168 but no public repo URL found at time of writing) — Framework-fingerprinting + CSPT source-to-sink chainer. Pipes Caido traffic through framework detection then enumerates likely CSPT sinks.

## Tooling

- **[cspt-analyzer](https://github.com/xssdoctor/cspt_research)** (in `cspt_research`) — Caido proxy plugin. Passive fingerprints the framework on captured HTTP traffic, extracts client-side route tables, and flags routes whose path-param decoding profile matches a known CSPT primitive.
- **[cspt-devtools-extension](https://github.com/xssdoctor/cspt_research)** (in `cspt_research`) — Chrome DevTools panel. In-page CSPT detection at runtime (watches `fetch` / `XHR` calls correlated with route-param origins).
- **[graphqlMaker](https://github.com/xssdoctor/graphqlMaker)** — GraphQL operation harvester for SPA bundles.
- **[multidoc](https://github.com/xssdoctor/multidoc)** — Fans a prompt to OpenAI + Claude + Gemini concurrently, then summary-diffs the responses. Hunter-side LLM ensembling.
- **[jscollab](https://github.com/xssdoctor/jscollab)** — AI-assisted collaborative JS review utility.
- **[vhostawesome](https://github.com/xssdoctor/vhostawesome)** — Virtual host scanning utility (recon phase).
- **[ai_subdomain](https://github.com/xssdoctor/ai_subdomain)** — LLM-generated candidate subdomains piped through `httpx` for live filtering.

## CT podcast appearances

- [2025-02-19 Bug Drop — XSSDoctor's Sick XSS Chain](../sources/podcasts/ct/20250219_oA1kooSC5pU_Bug_Drop_XSSDoctor_s_Sick_XSS_Chain.en.vtt) — Home-automation AI assistant takeover via subdomain XSS into a permissive `*.target.com` postMessage listener. Video: [criticalthinkingpodcast.io/videos/bug-drop-xssdoctors-sick-xss-chain](https://www.criticalthinkingpodcast.io/videos/bug-drop-xssdoctors-sick-xss-chain/); YouTube: [youtube.com/watch?v=oA1kooSC5pU](https://www.youtube.com/watch?v=oA1kooSC5pU).
- [2026-04-02 Ep 168 — XSSDoctor: Client-side Path Traversal Research](../sources/podcasts/ct/20260402_dDURWRV12Sg_XSSDoctor_-_Client-side_Path_Traversal_Research_Ep.168.en.vtt) — Walks the 10-framework decoding audit, the React Router `%252F` case-sensitivity finding, and his hunter workflow (path > query > hash, parameter substitution, Caido rule-matching). Episode page: [criticalthinkingpodcast.io/episode-168-the-doctor-is-in-devtools](https://www.criticalthinkingpodcast.io/episode-168-the-doctor-is-in-devtools/); YouTube: [youtube.com/watch?v=dDURWRV12Sg](https://www.youtube.com/watch?v=dDURWRV12Sg); HackerNotes: [blog.criticalthinkingpodcast.io/p/hackernotes-ep-168-client-side-path-traversals-across-every-framework-with-xssdoctor](https://blog.criticalthinkingpodcast.io/p/hackernotes-ep-168-client-side-path-traversals-across-every-framework-with-xssdoctor).

## Notes

- **CSPT-across-frameworks specialist.** Where Mizu is the DOMPurify person, XSSDoctor is the frontend-router-decoding person. If a target is an SPA, his per-framework notes tell you whether path-param `%2F` round-trips into a `fetch()` and at what stage.
- **Sink-chain temperament** — favours real impact chains over isolated alert(1). The Bug Drop chain (postMessage trust → AI-assistant → real-world automation) and the CSPT-to-XSS pivots both reflect that.
- **Tooling-first** — every research stream ships a tool (`cspt-analyzer`, `cspt-devtools-extension`, DoctorScan). Treat the tools as primary research output.
- **Collab orbit** — CTBB lab member, runs the monthly Discord hackalongs with BusFactor. Bridges to Justin Gardner (@Rhynorater), Joel Margolis (@gr3pme), Joseph Thacker (@rez0__).
- **Cross-refs** — feeds the CSPT technique cluster (to be authored): `../techniques/cspt/framework-decode-differential.md`, `../techniques/cspt/react-router-double-decode.md`, `../techniques/cspt/cspt-to-xss-pivot.md`, plus `../techniques/dom-xss/postmessage-wildcard-origin-trust.md` for the Bug Drop chain.
