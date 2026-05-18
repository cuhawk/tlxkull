---
title: initScript pre-load DOMLogger injection (chrome-devtools MCP)
slug: initscript-pre-load-injection
created_utc: 2026-05-18T16:35:00Z
updated_utc: 2026-05-18T16:35:00Z
tags: [technique/recon, technique/instrumentation, pattern/dom-xss-confirm, tool/chrome-devtools-mcp, tool/claude-in-chrome]
inbound: []
---

# initScript pre-load injection vs post-navigate injection

## The problem

When live-confirming DOM-XSS chains, you want to catch sinks that
fire **during page load** — innerHTML assignments, eval calls,
setTimeout-string calls, Function-constructor calls, etc. These
happen between the navigation request and the page's `load` event.

Naïve workflow:

1. Navigate to URL
2. Inject DOMLogger payload via javascript exec
3. Check captured events

This **misses all page-load-time sinks** because the DOMLogger
isn't installed yet when the bundle's bootstrap code runs. Many
high-value chains (URL param → innerHTML in bundle init, URL hash →
setTimeout-string in router init) fire during this window.

## The two MCPs in the workspace

- **`claude-in-chrome`** (user's real Chrome with extensions
  installed + Caido proxy): `javascript_tool` runs AFTER page load.
  Window globals get wiped on navigation. No pre-load hook
  installation. Good for: post-load interactions, deep navigation,
  extension-dependent recon (DOMLogger++ extension itself, Caido
  browser, Wappalyzer), gif recording.

- **`chrome-devtools`** (fresh Chromium): `navigate_page` accepts an
  `initScript` parameter that maps to Chrome DevTools Protocol's
  `Page.addScriptToEvaluateOnNewDocument`. The script runs **before
  any page script** on every new document. Good for: page-load-time
  sink capture, DOM-XSS chain live-confirm.

## When to use which

| Scenario | MCP |
|----------|-----|
| Probe URL param / hash → innerHTML/setTimeout/eval | chrome-devtools (initScript) |
| Probe postMessage from external origin → sink | chrome-devtools (initScript, then evaluate_script to send postMessages) |
| Replay captured Caido request through real browser session | claude-in-chrome |
| Verify finding under real auth cookies | claude-in-chrome |
| Use installed Chrome extensions (DOMLogger++, Caido, Wappalyzer) | claude-in-chrome |
| Record a PoC GIF | claude-in-chrome (gif_creator) |
| Cold-start probe in isolated state | chrome-devtools |

Don't blanket-pick claude-in-chrome just because memory mentions it as
default — for page-load-time DOM-XSS probes, chrome-devtools wins on
correctness.

## Recipe — page-load-time DOM-XSS chain confirm

```python
# Pseudo — chrome-devtools MCP call
navigate_page(
    url="https://app.example.com/?canary=TLXCANARY<svg/onload>",
    type="url",
    timeout=30000,
    initScript="""(function () {
        window.__TLX_DOMLOGGER_EVENTS = [];
        window.__TLX_CANARY_FIRES = [];
        const CANARIES = ['TLXCANARY'];
        const log = (kind, payload) => {
          const v = String(payload.value_preview||'');
          if (CANARIES.some(c=>v.includes(c)))
            window.__TLX_CANARY_FIRES.push({kind, ts: Date.now(), value: v.slice(0,500)});
          window.__TLX_DOMLOGGER_EVENTS.push({kind, ts: Date.now(), ...payload});
        };
        // ... innerHTML/outerHTML/insertAdjacentHTML/eval/Function/setTimeout/setInterval/setAttribute hooks
        // (full payload pattern in bin/domlogger_payload.js)
    })()"""
)

# Wait + read fires
evaluate_script(function="""
async () => {
  await new Promise(r => setTimeout(r, 4000));
  return {
    fires: window.__TLX_CANARY_FIRES,
    sink_kinds: Object.fromEntries(Object.entries(
      (window.__TLX_DOMLOGGER_EVENTS||[]).reduce((a,e)=>{a[e.kind]=(a[e.kind]||0)+1;return a;},{})
    ))
  };
}
""")
```

## Caveats

- The fresh Chromium has no extensions and no Caido proxy. If the
  finding needs Caido capture, dual-test: chrome-devtools for the
  sink-fire confirmation, then re-fire through claude-in-chrome for
  the network record.
- Auth cookies don't carry from real Chrome to chrome-devtools'
  fresh Chromium. Authenticated-state probes need claude-in-chrome OR
  Caido session-cookie injection via Tamper rules.
- `initScript` runs on every navigation in the tab — re-fires for
  redirects. Use `window.__TLX_DOMLOGGER_INSTALLED` guards if needed.

## Canary design

Use a high-entropy canary that won't appear in any framework code or
3rd-party blob:

```
TLXCANARY_<context>_<short-random>
```

Reserve `TLXCANARY` as the unmistakable prefix. Per-probe suffixes
let you tell which URL param landed where. Avoid characters that get
URL-encoded (use ASCII letters + digits + underscores in the canary
itself; put the XSS payload separately):

```
?error=TLXCANARY_ERR_001<svg/onload=1>
```

The canary `TLXCANARY_ERR_001` survives URL encoding unchanged; the
attached payload `<svg/onload=1>` is the actual XSS-bait that, IF
landed in a dangerous sink, would trigger DOM XSS. Two checks:

1. Does the canary appear in any sink? (chain reachability)
2. Does the payload survive into a dangerous context? (exploitability)

## Seen in the wild

- {date: 2026-05-18, target: netlify-h1, chain: 188, verdict: FP_unauth}
  First post-beautify chain audited. chrome-devtools initScript
  captured 73 sink invocations across `/` and `/login`. Zero canary
  fires. URL params land in safe contexts (URL-encoded href, sandboxed
  Stripe iframe). Details:
  [`targets/netlify-h1/findings/188/confirmed.json`](../../../targets/netlify-h1/findings/188/confirmed.json).

## Related

- [[beautify-before-index]] — without beautify, you don't get real
  DOM-XSS chains to confirm in the first place
- [[scope-aware-chain-triage]] — execution origin vs file host
  distinction
- [[../../tools/karpathy/source-code-review]] — Karpathy's prompt
  template for static review; live-confirm is the second pass

## References

- Chrome DevTools Protocol —
  <https://chromedevtools.github.io/devtools-protocol/tot/Page#method-addScriptToEvaluateOnNewDocument>
- TLX `bin/domlogger_payload.js` — canonical hook set
- TLX `targets/netlify-h1/findings/188/notes.md` — full reproduction
