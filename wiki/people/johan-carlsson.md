---
title: Johan Carlsson (joaxcar)
slug: johan-carlsson
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [joaxcar]
role: hunter
primary_focus: client-side
tags: [person, role/hunter, focus/client-side, focus/xss, focus/csp, focus/gitlab, focus/browser-quirks, focus/prototype-pollution]
inbound: []
---

# Johan Carlsson (joaxcar)

## Identity

- **Real name:** Johan Carlsson
- **Primary handle:** `joaxcar`
- **Role:** Full-time bug bounty hunter (left employment for full-time bounties early 2024 after a three-month unpaid-leave trial run).
- **Based:** Sweden.
- **Background:** Web developer turned hunter; framework-fluency (Rails/Hotwire, Angular, jQuery, Vue) is a recurring thread in his research.
- **Focus:** Client-side and JavaScript-layer bugs — XSS, CSP bypass, prototype pollution, browser-API quirks — with a heavy specialisation in GitLab. Top-1 ranked hunter on GitLab's HackerOne program at the time of his CT podcast appearance, having crossed $100k in GitLab bounties.

## Focus areas

- Client-side XSS in large Rails / Hotwire apps (GitLab)
- CSP nonce / `strict-dynamic` / allow-listed-host bypass
- Prototype pollution gadget hunting in third-party libraries (jQuery, etc.)
- Browser-API quirks (Chrome Navigation API, sandbox iframes, `document.baseURI`)
- Framework-specific exploitation (Turbo/Hotwire, Angular gadgets, jQuery sinks)
- Code-golf style minimal XSS payloads / sideloading under CSP

## Online presence

- [Blog — joaxcar.com](https://joaxcar.com/blog/)
- [X / Twitter — @joaxcar](https://x.com/joaxcar)
- [Bluesky — @joaxcar.bsky.social](https://bsky.app/profile/joaxcar.bsky.social)
- [GitHub — @joaxcar](https://github.com/joaxcar)
- [HackerOne — joaxcar](https://hackerone.com/joaxcar)
- [BBRE interview (2023-01-27)](https://www.bugbountyexplained.com/from-0-to-a-top-bug-bounty-hunter-johan-carlssons-journey-to-gitlab-top1-on-hackerone/)
- [GitLab AMA on YouTube — Live "Ask a Hacker" w/ Johan Carlsson](https://www.youtube.com/watch?v=3LF8fpAX6Xk)

## Key research / posts

- **[GitLab: CVE-2023-5009](https://joaxcar.com/blog/2023/09/18/gitlab-cve-2023-5009/)** (2023-09-18) — Critical pipeline-execution bug allowing pipelines to run as an arbitrary user via a security-pipeline bot trigger; the bug took ~2 years and 100+ reports to land. The canonical GitLab CI/CD privilege-escalation case study.
- **[CVE-2022-4908: SOP bypass in Chrome using Navigation API](https://joaxcar.com/blog/2023/10/06/cve-2022-4908-sop-bypass-in-chrome-using-navigation-api/)** (2023-10-06) — Same-origin-policy bypass via `navigation.entries()` + `about:blank` letting a same-site subdomain leak full cross-window URL history. Practical impact: OAuth-token exfil from URL fragments / query strings. Lesson: method-return values on new browser APIs need the same SOP scrutiny as static properties.
- **[Having some fun with JavaScript hoisting](https://joaxcar.com/blog/2023/12/13/having-some-fun-with-javascript-hoisting/)** (2023-12-13) — XSS via function/var hoisting reordering execution under restricted character sets. Seeds `../techniques/dom-xss/js-hoisting-xss.md` and the consuming-tags angle in `../techniques/dom-xss/consuming-tags-and-hoisting.md`.
- **[Hunting for Prototype Pollution gadgets in jQuery (Intigriti 0124 challenge)](https://joaxcar.com/blog/2024/01/26/hunting-for-prototype-pollution-gadgets-in-jquery-intigriti-0124-challenge/)** (2024-01-26) — Bottom-up sink hunt in jQuery: polluting `selector`, `handler`, `delegateType`, `needsContext` reaches `sel = handleObj.selector + " "` where array-to-string coercion turns `["<img onerror=…>"]` into executable HTML. Cross-link `../techniques/prototype-pollution/client-side-pp-gadget.md` and `../techniques/dom-xss/prototype-pollution-xss.md`.
- **[CSP bypass on PortSwigger.net using Google script resources](https://joaxcar.com/blog/2024/02/19/csp-bypass-on-portswigger-net-using-google-script-resources/)** (2024-02-19) — Nonce-based CSP without `strict-dynamic` defeated by abusing AngularJS hosted on `www.google.com/recaptcha/...` + `www.gstatic.com/recaptcha/...`. Nonce lifted via `document.querySelector("[nonce]").nonce` then re-used with an `ng-on-error` gadget. Reinforces `../techniques/csp/path-csp-redirect-bypass.md` and motivates a future `csp/whitelisted-host-angular-gadget.md`.
- **[Sandbox-iframe XSS challenge solution](https://joaxcar.com/blog/2024/05/16/sandbox-iframe-xss-challenge-solution/)** (2024-05-16) — Leaks a parent-window hash from a `sandbox` iframe (no `allow-same-origin`) by chaining a CSP path redirect to a CDN-hosted library, then reading `document.baseURI`. Direct seed for `../techniques/dom-xss/sandbox-srcdoc-base-uri-leak.md` and `../techniques/csp/path-csp-redirect-bypass.md`.
- **[Sideloading external scripts: a code golf challenge](https://joaxcar.com/blog/2024/12/20/sideloading-external-scripts-a-code-golf-challenge/)** (2024-12-20) — Minimal payloads to pull and run external JS under restrictive CSP: ``fetch`/url` `` + `location=javascript:` (0-click) vs `open()` (1-click). Useful for tight XSS where only a few dozen characters of sink fit.
- **[Confetti: Solution to my Intigriti May 2025 XSS Challenge](https://joaxcar.com/blog/2025/05/20/confetti-solution-to-my-intigriti-may-xss-challenge/)** (2025-05-20) — His own XSS challenge writeup; canonical "author's intended solution" for the May 2025 Intigriti monthly.
- **[Solving Turb0's XSS challenge using recursive object attributes](https://joaxcar.com/blog/2025/12/02/solving-turb0s-xss-challenge-using-recursive-object-attributes/)** (2025-12-02) — Recursive-attribute trick on object/attribute traversal; another framework-coercion gadget pattern.
- **[Grafana: CVE-2023-1387](https://joaxcar.com/blog/2023/04/26/grafana-cve/)** (2023-04-26) — Grafana advisory writeup; demonstrates that his client-side eye carries beyond GitLab.

### GitLab issues (public)

- [#461328 — 1-click ATO via XSS in the code editor](https://gitlab.com/gitlab-org/gitlab/-/issues/461328) — `parentOrigin` validation flaw in the Web IDE; basis for CVE-2024-4835.
- [#463408 — Bypass of CVE-2024-4835](https://gitlab.com/gitlab-org/gitlab/-/issues/463408) — Multi-parameter `parentOrigin=…&bparentOrigin=…` trick; classic "patch fixed the example, not the class" follow-up.
- [#353370 — Stored XSS in Notes with CSP bypass for gitlab.com](https://gitlab.com/gitlab-org/gitlab/-/issues/353370) — Stored-XSS + gitlab.com-specific CSP bypass chain.

## CT podcast appearances

- [2024-05-02 Ep 69 — Johan Carlsson - 3 Month Check-in on Full-time Bug Bounty](../sources/podcasts/ct/20240502_Env8L2SlayM_Johan_Carlsson_-_3_Month_Check-in_on_Full-time_Bug_Bounty._Ep._69.en.vtt)

## Notes

- **GitLab obsession is a feature, not a bug.** His top-1 ranking and CVE-2023-5009 came from staying with one target for years. The pattern in the BBRE interview and CT Ep 69: read every public security advisory the program has published, then look for the same class one source-file over.
- **Framework fluency as a primitive.** Repeated theme — Rails/Hotwire/Turbo on GitLab, Angular on whitelisted Google CDNs, jQuery for PP gadgets. He treats "know the framework's coercion rules and event lifecycle" as a first-class skill, not a side note.
- **Patch-bypass discipline.** The CVE-2024-4835 → #463408 bypass is the canonical example: he reads the patch diff, mutates the input slightly, refiles. Hunters working GitLab should diff every security release and check his report queue for the follow-up.
- **Client-side + protocol-quirk balance.** Although his public surface is XSS/CSP/PP heavy, he also tracks browser-protocol weirdness — Navigation API SOP, sandbox iframe `baseURI`, redirect-through-allowed-host CSP. The blog skews "browser engineer who hunts" rather than "appsec pentester".
- **Swedish hunter cohort.** Adjacent to the Detectify/Mathias Karlsson / Frans Rosén lineage geographically; collaborates loosely with that scene. See [mathias-karlsson](mathias-karlsson.md) and [frans-rosen](frans-rosen.md).
- **Publication cadence.** Roughly one post per quarter on the blog; heavier output via Intigriti challenge writeups and GitLab HackerOne reports. No conference-talk circuit — output is blog + reports + X/Bluesky threads.
- **Methodology cues from CT Ep 69 / BBRE interview:**
  - Pick a single high-payout program with deep code and old open-source history; read the changelog, not just the docs.
  - Build a buffer (he took 3 months unpaid leave before committing to full-time) — bounty cashflow is lumpy.
  - Treat every CSP / sanitizer / sandbox primitive as "what gadget makes this safe assumption false?" rather than "is there a direct XSS sink?".
- **Wiki cross-links seeded by his work:** `../techniques/dom-xss/sandbox-srcdoc-base-uri-leak.md`, `../techniques/dom-xss/js-hoisting-xss.md`, `../techniques/dom-xss/prototype-pollution-xss.md`, `../techniques/csp/path-csp-redirect-bypass.md`, `../techniques/prototype-pollution/client-side-pp-gadget.md`. Future technique pages worth seeding from his catalogue: `csp/whitelisted-host-angular-gadget.md`, `dom-xss/navigation-api-sop-leak.md`, `server-side/gitlab-pipeline-bot-impersonation.md`.
