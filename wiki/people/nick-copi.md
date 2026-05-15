---
title: Nick Copi (7urb0)
slug: nick-copi
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [7urb0, 7urb01, nickcopi, demo]
role: hunter
primary_focus: client-side
tags: [person, role/hunter, focus/client-side, focus/react, focus/dom-xss, focus/css-injection]
inbound: []
---

# Nick Copi (7urb0)

## Identity

- **Real name:** Nick Copi
- **Primary handle:** `7urb0` (formerly `Demo`)
- **Role:** hunter / dual (AppSec engineer + independent researcher)
- **Day job:** Cyber Security Engineer at CarMax (Fortune 200) per LinkedIn; self-describes as "AppSec engineer by day, independent security researcher by night."
- **Based in:** Richmond, Virginia. Justin Gardner called him "the best web hacker in Richmond."

## Focus areas

- React internals as exploit surface (`React.createElement`, JSX, useState gadgets)
- DOM XSS through unusual gadget chains (`toString` overrides, serializer quirks)
- CSS injection for data exfiltration (fontleak, keyframe-timed exfil)
- JavaScript prototype/deserialization gadgets (`js-yaml` → React state setter)
- Electron / desktop-app exploitation, HTTP request smuggling (Kestrel)

## Online presence

- [Personal blog — turb0.one ("Bits, Bytes, and Bad Ideas")](https://www.turb0.one)
- [Site mirror — nickcopi.site](https://nickcopi.site/)
- [X / Twitter — @7urb01](https://x.com/7urb01)
- [GitHub — nickcopi](https://github.com/nickcopi) (mirror of GitLab)
- [GitLab — NickCopi](https://gitlab.com/NickCopi)
- [LinkedIn — nick-copi-548611175](https://www.linkedin.com/in/nick-copi-548611175/)
- [DEFCON React XSS lab — defcon.turb0.one](https://defcon.turb0.one/)

## Key research / posts

- [Vega CVE-2025-59840: Unusual XSS Technique — `toString` gadget chains (2025-11-29)](https://www.turb0.one/pages/Vega_CVE-2025-59840:_Unusual_XSS_Technique_toString_gadget_chains.html) — XSS via overriding `toString` on objects fed into stringifying sinks; seeds `techniques/dom-xss/`.
- [Abbreviated Reproduction of CVE-2025-55315 — ASP.NET Kestrel HTTP Smuggling, 9.9 critical (2025-10-16)](https://www.turb0.one/pages/Abbreviated_Reproduction_of_CVE-2025-55315_\(Critical_9.9_ASP.NET_Kestrel_HTTP_Request_and_Response_Smuggling\).html) — companion repo: [CVE-2025-55315-detection-playground](https://github.com/nickcopi/CVE-2025-55315-detection-playground).
- [From Component to Compromised: XSS via React createElement (2025-10-11)](https://www.turb0.one/pages/From_Component_to_Compromised:_XSS_via_React_createElement.html) — full write-up backing the DEFCON workshop; tainted `type` / `props` / `children` arguments to `React.createElement` yield arbitrary tag injection, prop-smuggled `dangerouslySetInnerHTML`, and `href=javascript:` reflection. Should seed a `techniques/dom-xss/react-createelement.md` page.
- [Following The JSON Path: A Road Paved in RCE (2025-06-03)](https://www.turb0.one/) — JSONPath library sandbox escapes leading to RCE.
- [New DOM XSS in Old Swagger UI v2.2.8 (2025-02-18)](https://www.turb0.one/) — DOM XSS in legacy Swagger UI; live repro at `https://www.turb0.one/files/swaggerv2.2.8/index.html`.
- DOM XSS in CyberChef: Traversing Multiple Execution Contexts — escapes between CyberChef iframes/workers.
- Weaponizing Chrome CVE-2023-2033 for RCE in Electron: Some Assembly Required — V8 type-confusion turned into Electron RCE.
- Burster Shell — process-tree manipulation primitive for arbitrary parent spawning.
- "Using Discord Desktop for Backdoor Persistence" and "Invisible JavaScript Malware" — older offensive-tooling posts.
- DEFCON Bug Bounty Village workshop: "XSS via React createElement" — slides + lab tarball at [defcon.turb0.one](https://defcon.turb0.one/) (slides.pdf, reactlab.tgz; React 16 + React 19 sandboxes, levels 0–3).

## CT podcast appearances

- [2025-09-25 Ep 141 — Hacking the Pod: Google Docs 0-day & React CreateElement Exploits with Nick Copi (7urb0)](../sources/podcasts/ct/20250925_4bSP_Iu4Vfs_Hacking_the_Pod_-_Google_Docs_0-day_React_CreateElement_Exploits_with_Nick_Copi_7urb0_Ep._141.en.vtt)
  - Companion HackerNotes: [blog.criticalthinkingpodcast.io/p/hackernotes-ep-141…](https://blog.criticalthinkingpodcast.io/p/hackernotes-ep-141-pwning-the-pod-google-docs-0-day-react-createelement-exploits-with-nick-copi-7urb)
  - Episode page: [criticalthinkingpodcast.io — Ep 141](https://www.criticalthinkingpodcast.io/episode-141-hacking-the-pod-google-docs-0-day-react-createelement-exploits-with-nick-copi-7urb/)
  - Topics covered: Google Docs client-side DoS (RegExp.prototype.exec breakpoint + Proxy-wrapped enumeration of unique regexes); React `createElement` XSS taxonomy; `js-yaml` deserialized-function → React useState setter RCE-as-state-updater; CSS injection session-token exfil via fontleak + keyframes (~1,400-char token); `window.location.replace` 200-call throttle bypass via cross-origin nav sync; JWT leak via Next.js checkout cache misconfig.

## Notes

- **Signature technique:** treat framework primitives (`React.createElement`, useState setters, JSX runtime) as sinks. Goal is not "find XSS in app code" but "find a code path where user input reaches a framework internal that React itself will then render or execute." This is the through-line across the React workshop, the toString gadget post, and the js-yaml/useState gadget.
- **Style:** patient, low-level. Routinely drops a Chrome DevTools breakpoint on a built-in (`RegExp.prototype.exec`) and proxies it, then enumerates surface area — closer to native reverse-engineering than typical web-pentest workflow. Background in Flash game RE and rails CTFs shows.
- **CSS injection specialty:** uses font-based timing exfiltration (fontleak with custom keyframes) to drain long secrets where one-char-at-a-time sequential leaks would normally be blocked or too slow. Worth a dedicated `techniques/css-injection/fontleak-keyframes.md` page when ingested.
- **Output venue:** posts long-form, code-heavy write-ups on `turb0.one`, often with a live vulnerable instance hosted under `/files/`. Useful for reproducing his bugs locally without standing up the target.
- **Not on HackerOne hall-of-fame leaderboards visibly** — work surfaces through CVEs (Vega, Kestrel), DEFCON, and CT, not platform ranking.
- Calls his account "Demo" historically — if old write-ups reference "Demo" / `7urb01` / `7urb0` interchangeably, it's the same person.
