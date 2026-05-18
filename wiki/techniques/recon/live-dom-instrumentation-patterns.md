---
title: Live DOM instrumentation — patterns, next-step recipes, per-pattern hit rates
slug: live-dom-instrumentation-patterns
created_utc: 2026-05-18T17:30:00Z
updated_utc: 2026-05-18T17:30:00Z
tags: [technique/recon, technique/dom-xss, technique/live-confirm, pattern/dom-instrumentation]
inbound: []
---

# Live DOM instrumentation — observed patterns

## Why live instrumentation

Static analysis surfaces every `innerHTML =`, `setTimeout(...)`,
`new Function(...)` callsite in the bundle. Live DOMLogger
instrumentation answers a different question: **which of those
callsites actually fire on this target's pages, with what data, from
what code path?**

The static layer is a candidate generator. The live layer is the FP
filter. On a modern React SPA, the FP filter eliminates 95%+ of
static candidates within seconds, leaving the 1–5% worth manual audit.

## DOMLogger payload coverage (canonical version at `bin/domlogger_payload.js`)

### Sources hooked
- `URLSearchParams.prototype.get`
- `Location.prototype.{href,search,hash,pathname}` getters
- `Document.prototype.referrer` getter
- `History.prototype.{pushState,replaceState}`
- `EventTarget.prototype.addEventListener('message', ...)` wrap

### Sinks hooked
- `Element.prototype.{innerHTML,outerHTML}` setters
- `Element.prototype.insertAdjacentHTML`
- `Element.prototype.setAttribute('on*', ...)` (event handlers)
- `Document.prototype.{write,writeln}`
- `window.{setTimeout,setInterval}` (string arg only)
- `window.Function` constructor
- `window.eval`
- HTMLScriptElement `.src` setter (added 2026-05-18 from live obs)
- `window.fetch` URL argument (added 2026-05-18 for auth probes)

### Sources/sinks NOT yet hooked but worth adding
- `Range.createContextualFragment(...)` — HTML-parses to DocumentFragment
- `DOMParser.parseFromString(html, 'text/html')` — string → DOM tree
- `XMLHttpRequest.prototype.open` — URL arg
- `WebSocket` ctor URL arg
- `Worker` ctor URL arg
- `import(...)` dynamic ES module — URL arg
- `el.outerHTML` getter (read-side; not currently hooked)
- React `dangerouslySetInnerHTML` prop interception (would need React internals hook)

## Pattern catalog (observed 2026-05-18 across netlify-h1 + coolblue-intigriti)

### Pattern 1 — 3rd-party CDN scripts dominate `script.src` and `innerHTML` fires

**Observed:** 33 of 53 sink fires on app.netlify.com landing were
`script.src` from `js.hubspot.com`, `js.stripe.com`, `cdn.segment.com`,
`cdn.sift.com`, `gstatic.com`, plus own-bundle imports. 17 of 17
innerHTML fires were static template strings from these same scripts.

**Interpretation:** Aggregate sink-rate dominated by 3rd-party
analytics + payment + captcha. Each sink fire individually is safe
(URLs/templates are hardcoded), but the supply-chain risk is real —
any compromise of these CDNs results in app-origin code execution.

**Next-step recipe:**
- Snapshot the 3rd-party script hosts loaded on landing.
- For each, record the SRI hash status and version pinning.
- File supply-chain risk note in `wiki/targets/<program>.md` under
  "3rd-party blast radius".
- For each script host, check program scope — most BBPs exclude
  "issues in 3rd-party libraries we cannot fix" but accept
  "improper SRI / version pinning of 3rd-party JS".

### Pattern 2 — React JSX renders user data as text nodes universally

**Observed:** 4 user-controllable fields on netlify dashboard (OAuth
app name, description, redirect URI, PAT description) across 4
rendering surfaces (list, accordion, edit form, OAuth consent screen).
Every canary landed in `<h4>`, `<p>`, `<dd>`, `<strong>`, `<code>` as
**textContent** via React `createTextNode`. Zero attribute landings.
Zero payload executions.

**Interpretation:** Pure React JSX apps (where `dangerouslySetInnerHTML`
is unused) are XSS-safe by default. Stored-XSS hunting on the
application's own rendering paths is largely a dead end.

**Next-step recipe:**
- `grep -rn 'dangerouslySetInnerHTML' <sources>/` first. If 0 matches,
  drop stored-XSS sweep priority and focus on:
  - 3rd-party integration render paths (less likely to use JSX)
  - Server-rendered admin pages (audit log, deploy summary)
  - Markdown / WYSIWYG content rendering (often raw HTML)
- If matches found, audit each callsite for source provenance.

### Pattern 3 — SPA history.pushState routing makes location.hash chains dead

**Observed:** Sent 3 hashchange events with XSS-canary payloads on
netlify `/teams/<x>/projects`. Zero new events in DOMLogger. Zero
canary fires.

**Interpretation:** Modern React Router / Next.js / Relay-driven SPAs
use `history.pushState` for navigation and ignore `location.hash`
entirely. Static chains tagged `location_hash → DOM-sink` mostly fire
on legacy routes or fragment-anchor scrolling.

**Next-step recipe:**
- Before live-probing hash chains, grep sources for
  `addEventListener('hashchange'` or `window.onhashchange`.
- If 0 hashchange listeners, drop all 57+ location_hash hot chains
  to FP archive without live probe.
- If listeners exist, identify the route that registers them; probe
  that specific route only.

### Pattern 4 — URL params on auth-related routes land in safe contexts

**Observed:** 10 URL params + hash canary on `/login`. Canary landed
in:
- `<a href="/sso?redirect=<URL-encoded>">` — SSO redirect link
- `<iframe src="https://js.stripe.com/v3/m-outer-*.html#url=<URL-encoded>">` — Stripe init

Both safe (href = URL parsing context; iframe = cross-origin sandboxed).

**Interpretation:** Login/auth pages typically reflect URL params
into SSO redirect URLs and 3rd-party iframe init parameters. React's
href={ url } JSX prop calls setAttribute('href', url) which doesn't
HTML-parse.

**Next-step recipe:**
- On auth routes, redirect the live-probe canary search toward:
  - `<form action="...">` attribute — does it use the URL param?
  - Hidden input `<input value="...">` populated from URL param?
  - Open-redirect on `?redirect=` / `?return_to=` / `?next=`
- Stop expecting XSS on `/login` itself — wrong surface.

### Pattern 5 — Internal cross-frame postMessages dominate listener traffic

**Observed:** 26 of 30 `source.postMessage` events on coolblue.de were
internal cross-frame chatter from origin `https://www.coolblue.de`
(Stripe / recaptcha / Sift / Segment iframes ↔ parent). Sending 11
attacker-shape postMessages did not produce a single sink fire on
netlify.

**Interpretation:** App's postMessage handlers filter by `event.origin
=== window.location.origin` (or equivalent). Attacker-origin postMessage
data simply doesn't reach the listener's body — proper origin gating.

**Next-step recipe:**
- Don't expect postMessage XSS on apps with strict origin gating.
- If postMessage listener exists, look for **origin bypass** patterns:
  `origin.indexOf(trusted) >= 0`, `origin.endsWith(trusted)`,
  `origin.startsWith('https://') && origin.includes('trusted.com')`
- These bypass-prone patterns get matched by static; live-confirm
  with `attacker.trusted-domain.evil.com` origin.

### Pattern 6 — localStorage JWT presence = XSS severity escalator

**Observed:** Netlify dashboard stores `nf-session` JWT in
localStorage. Any DOM XSS in `app.netlify.com` origin = automatic
session-token theft.

**Interpretation:** Even a tiny self-XSS becomes critical if auth
state is XSS-readable. Inverse: cookies marked HttpOnly + Secure are
not XSS-readable, reducing XSS severity.

**Next-step recipe:**
- On first auth state probe, dump `Object.keys(localStorage)` and
  `Object.keys(sessionStorage)`. Note presence of jwt/token/session/auth
  keys.
- In any XSS finding writeup, mention that the origin stores
  XSS-readable auth → bumps severity from medium to critical.

### Pattern 7 — Unbeautified bundles → static self-flow chain noise

**Observed (2026-05-18 netlify-h1):** 20/20 hot chains were depth=0
self-flows on minified webpack chunks `$.set / $.validate / $1 / $V`
in `6932.bundle.js` indexed at line=1. Live probe → ZERO sinks
fired from listener paths.

**Interpretation:** Function-boundary detection failed on unbeautified
bundles. Static regex matched source-tag AND sink-tag patterns inside
the same opaque function body without inter-procedural verification.

**Next-step recipe:**
- See [[beautify-before-index]]. Pre-flight check on every target:
  ```
  for f in raw/*.js; do
    l=$(wc -l < "$f"); b=$(wc -c < "$f");
    [ $((b / (l+1))) -gt 500 ] && echo "MINIFIED: $f"
  done
  ```
- Refuse `js-index` if any file fails the ratio.

## Per-chain-class live-probe recipes

| Chain shape | Recipe | Browser MCP | Pre-load needed? |
|------|------|-----|------|
| `URLSearchParams_*` → `innerHTML/setTimeout-string/eval/Function` | Navigate with `?canary=TLXCANARY<svg/onload>` URL params for each param name | chrome-devtools | YES (initScript) |
| `location_hash` → DOM sink | Dispatch hashchange events with canary payload | claude-in-chrome OR chrome-devtools | NO (events post-load) |
| `onmessage_handler` → DOM sink | Send 11+ shape postMessages (string, object, `__proto__`, redux, react-devtools, graphiql, webpack-msg) | claude-in-chrome | NO (postMessage post-load) |
| Stored field → list/detail render | Create entity with canary name; navigate to render route; walk DOM for canary | claude-in-chrome (auth needed) | NO |
| `proto_assign_merge` → `pp_gadget_*` | Diff Object.prototype keys before/after postMessage flood + URL probe | claude-in-chrome | NO |
| `fetch_with_user_input` sink | Hook `window.fetch`, log every URL, search for canary | claude-in-chrome | NO |
| `script_src_setter` (live-observed) | Hook `el.src = ` on script elements; navigate; log URLs; match canary | chrome-devtools | YES (initScript) |
| `documentElement_innerHTML` | Highest priority — initScript-hook outerHTML/innerHTML on `<html>`; navigate; probe URL params | chrome-devtools | YES (initScript) |

## MCP selection heuristic

```
if (chain.source in {URLSearchParams_*, location_*, document_referrer}):
    needs initScript injection (hooks miss page-load-time sinks)
    → use chrome-devtools (no auth carryover)
elif (auth state required):
    → use claude-in-chrome (cookies + extensions + Caido proxy)
    → accept page-load blindness; trigger post-load via interaction
elif (chain.source in {onmessage_handler, location_hash, stored fields}):
    → either MCP; claude-in-chrome preferred for Caido capture
```

See also [[initscript-pre-load-injection]] for the trade-off
mechanics.

## Related

- [[beautify-before-index]] — prerequisite for live-probing to be
  worthwhile
- [[initscript-pre-load-injection]] — MCP-choice trade-off
- [[scope-aware-chain-triage]] — execution origin vs file host
- [[adjacent-function-gap]] — orthogonal static technique
