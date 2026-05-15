---
title: Nick Copi (7urb0)
slug: turbo
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [7urb0, 7urb01, turb0, demo]
role: hunter
primary_focus: client-side
tags: [person, role/hunter, focus/client-side, focus/dom-xss, focus/react, focus/css-injection, focus/electron-rce, focus/request-smuggling]
inbound: []
---

# Nick Copi (7urb0)

## Identity

- Real name: **Nick Copi**. Publishes as **7urb0** (formerly "Demo"; some older content uses "Turbo").
- Day job: AppSec engineer at a Fortune 200 company. Independent security researcher / bug-bounty hunter on the side. Richmond, VA area.
- Background: came up through game-hacking and reverse engineering before pivoting full-time into web. Dubbed "best web hacker in Richmond" by Justin Gardner on the CT show intro to Ep 141.
- Active in the Critical Thinking community; ran a workshop at the DEFCON Bug Bounty Village on React `createElement` exploitation.

## Focus areas

- **Client-side JavaScript exploitation** — DOM XSS, sink discovery in modern SPA stacks (React, Next.js).
- **React `createElement` as an XSS sink** — his signature technique; treats `React.createElement(type, props, children)` as a multi-parameter sink where attacker-controlled `type`, `dangerouslySetInnerHTML`-style props, or coerced children turn into HTML injection.
- **CSS injection for credential exfil** — keyframe-animation timing channels to leak `<script>`-tag contents (e.g. 1,400-char session tokens) using Fontleak-style techniques.
- **Sandbox escapes in expression languages / template engines** — Vega expression sandbox (CVE-2025-59840), JSON Path libraries → RCE.
- **HTTP request/response smuggling** — abbreviated repro of CVE-2025-55315 (ASP.NET Kestrel, CVSS 9.9).
- **Desktop-app pivoting** — turning a Chrome bug into Electron RCE; Discord Desktop as a persistence channel.

## Online presence

- Personal blog: [turb0.one](https://www.turb0.one) — tagline "Bits, bytes, and bad ideas". Static Node.js-generated site, no JS / no cookies.
- X / Twitter: [@7urb01](https://x.com/7urb01).
- HackerOne profile: [hackerone.com/7urb0](https://hackerone.com/7urb0).
- DEFCON workshop challenge index: [defcon.turb0.one](https://defcon.turb0.one/) — React 16 + React 19 `createElement` exploit lab.

> GitHub handle not publicly tied to a confirmed account at time of writing; `github.com/7u0` and `github.com/7I0` showed up in search but neither is verified as Nick. Treat as unconfirmed until a self-linked repo surfaces.

## Key research / posts

- **[From Component to Compromised: XSS via React createElement](https://www.turb0.one/pages/From_Component_to_Compromised:_XSS_via_React_createElement.html)** — Canonical writeup of his signature technique. Untrusted input reaching `React.createElement` (via `type`, props, or coerced children) escalates to DOM XSS even in modern Next.js apps. Seeds `../techniques/dom-xss/react-createelement-sink.md`.
- **[Vega CVE-2025-59840 — Unusual XSS Technique: toString gadget chains](https://www.turb0.one/pages/Vega_CVE-2025-59840:_Unusual_XSS_Technique_toString_gadget_chains.html)** — Escape from Vega's "safe" expression language via `toString` implicit-call gadget chains against object coercion. Pattern transfers to any sandboxed expression evaluator that touches user-supplied objects.
- **[Abbreviated Reproduction of CVE-2025-55315 (ASP.NET Kestrel HTTP Request/Response Smuggling)](https://www.turb0.one/pages/Abbreviated_Reproduction_of_CVE-2025-55315_\(Critical_9.9_ASP.NET_Kestrel_HTTP_Request_and_Response_Smuggling\).html)** — Minimal repro of the 9.9-critical Kestrel desync, with detection notes.
- **[Following The JSON Path: A Road Paved in RCE](https://www.turb0.one/pages/Following_The_JSON_Path:_A_Road_Paved_in_RCE.html)** — JSONPath library sandbox escapes → RCE; companion to the Vega writeup in the "expression-language gadget chain" lineage.
- **[New DOM XSS in Old Swagger UI v2.2.8](https://www.turb0.one/pages/New_DOM_XSS_in_Old_Swagger_UI_v2.2.8.html)** — DOM XSS via vendor-extension properties in OpenAPI specs rendered client-side; lives `?url=`-loaded.
- **[DOM XSS in CyberChef: Traversing Multiple Execution Contexts](https://www.turb0.one/pages/DOM_XSS_in_CyberChef:_Traversing_Multiple_Execution_Contexts.html)** — XSS that hops execution contexts inside CyberChef's chain UI.
- **[Weaponizing Chrome CVE-2023-2033 for RCE in Electron: Some Assembly Required](https://www.turb0.one/pages/Weaponizing_Chrome_CVE-2023-2033_for_RCE_in_Electron:_Some_Assembly_Required.html)** — V8 type-confusion bug turned into Electron RCE; assembly-level exploit chain.
- **[Using Discord Desktop for Backdoor Persistence](https://www.turb0.one/pages/Using_Discord_Desktop_for_Backdoor_Persistence.html)** — Discord's Electron shell as a covert persistence channel.
- **[Discovering RCE in Repository Onboarding Code](https://www.turb0.one/pages/Discovering_RCE_in_Repository_Onboarding_Code.html)** — RCE via repo-onboarding bootstrap path.
- **[Invisible JavaScript Malware](https://www.turb0.one/pages/Invisible_Javascript_Malware.html)** — Obfuscation / hiding techniques in delivered JS payloads.
- **[Burster Shell: Spawn Children of Arbitrary Processes](https://www.turb0.one/pages/Burster_Shell:_Spawn_Children_of_Arbitrary_Processes.html)**, **[Byte Macro: Implementing an Obscure Telnet Option](https://www.turb0.one/pages/Byte_Macro:_Implementing_an_Obscure_Telnet_Option.html)**, **[Multicall Binary Packer](https://www.turb0.one/pages/Multicall_Binary_Packer.html)**, **[Custom Blog CMS](https://www.turb0.one/pages/Custom_Blog_CMS.html)** — Systems / tooling side projects.
- **Google Docs client-side 0-day** (co-discovered with researchers on Justin's prep doc) — inefficient-regex DoS in Docs paste handling. Repro: set conditional breakpoint on `RegExp.prototype.exec`, replace with a Proxy wrapper to enumerate every regex called on paste, then build a payload that triggers catastrophic backtracking. Trivially weaponizable: visit a site → click button → clipboard payload → paste into any Doc → hang. No public blog post; discussed on CT Ep 141 alongside Justin Gardner and the CT team. **Co-discoverer collaboration unconfirmed publicly with Nick Copi vs. the wider CT pod (memory.md notes "co-discovered with Nick Copi"); treat the attribution as: 7urb0 demonstrated the full chain on-air, the bug was found during pod-prep adversarial review of the shared Doc.**

## CT podcast appearances

- [2025-09-25 Ep 141 — Hacking the Pod: Google Docs 0-day & React CreateElement Exploits with Nick Copi (7urb0)](../sources/podcasts/ct/) — Episode page: [criticalthinkingpodcast.io/episode-141-...](https://www.criticalthinkingpodcast.io/episode-141-hacking-the-pod-google-docs-0-day-react-createelement-exploits-with-nick-copi-7urb/). HackerNotes: [blog.criticalthinkingpodcast.io/p/hackernotes-ep-141-...](https://blog.criticalthinkingpodcast.io/p/hackernotes-ep-141-pwning-the-pod-google-docs-0-day-react-createelement-exploits-with-nick-copi-7urb). Topics: Google Docs regex DoS 0-day, React `createElement` XSS, CSPT exploitation, CSS injection / Fontleak for token exfil, his game-hacking origin story. Referenced tools: [regexploit](https://github.com/doyensec/regexploit), [Fontleak](https://adragos.ro/fontleak/), Chrome DevTools [`debug()`](https://developer.chrome.com/docs/devtools/console/utilities#debug-function), [domloggerpp](https://github.com/kevin-mizu/domloggerpp).

## Notes

- **React `createElement` is the signature sink.** If a target is React/Next.js and accepts attacker-influenced object shapes that hit `React.createElement` (directly or via JSX compiled output), 7urb0's writeup is the playbook. Look for: user-controlled `type` strings, prop spreading from untrusted JSON, `dangerouslySetInnerHTML` reachable via prop merge, and children arrays where one element is a stringified object. Pairs with `../techniques/dom-xss/` (when that page exists) and the DEFCON challenge lab at [defcon.turb0.one](https://defcon.turb0.one/) for hands-on practice.
- **Sandbox-escape lineage.** Vega expression sandbox (CVE-2025-59840) and JSONPath RCE share a pattern: "safe" expression evaluators that touch attacker-supplied objects trigger gadget chains via `toString` / `valueOf` / `Symbol.toPrimitive`. Watch for this in any client-side templating / charting / config-DSL library.
- **Worst-crit war story** — JWT cache misconfiguration in a Next.js app leaking other users' auth tokens. Mentioned in HackerNotes Ep 141 as his highest-impact bug; no public blog writeup at this time.
- **Output style** — terse, exploit-first writeups on a deliberately minimal blog (no JS / no cookies / static HTML). Each post is one tight chain end-to-end; the systems-side posts (telnet, packers, Burster shell) reveal the non-web background that makes the Electron / Chrome / smuggling chains land.
- **Collaborators / orbit** — Critical Thinking podcast regular guest / community member. Justin Gardner is the most visible bridge. No confirmed public co-authorship with Kevin Mizu, but topical overlap on DOM XSS sink discovery is high; cross-reference his `createElement` work against Mizu's DOMPurify / GMSGadget catalog when triaging.
- **Cross-refs** — research feeds (planned) `../techniques/dom-xss/react-createelement-sink.md`, `../techniques/dom-xss/swagger-ui-vendor-ext.md`, `../techniques/css-injection/fontleak-token-exfil.md`, `../techniques/sandbox-escape/expression-language-gadget-chain.md`, `../techniques/request-smuggling/kestrel-cve-2025-55315.md`.
