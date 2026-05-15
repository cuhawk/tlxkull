---
name: browser-confirm
description: Confirm a Opus-flagged true-positive chain in a real browser, either against the live target (chrome-devtools MCP, with Caido proxy capturing) or against TLX's mock backend (playwright MCP + mock_start + mock_confirm). Run per chain that opus-deep-audit marked verdict=true_positive. Writes findings/<id>/confirmed.json + screenshots. Default mode is live; falls back to mock if rate-limited or sensitive.
---

# browser-confirm

## Purpose
Static reasoning + headless mock are necessary but not sufficient. A
finding ships only after we *see it fire in a real browser*. This skill
runs that final proof.

## Inputs
- `targets/<name>/opus/<chain_id>.md` with `verdict: true_positive`.
- `memory.md` for default mode preference.

## Modes

### Live mode (default)
1. Make sure chrome-devtools MCP is running with Caido proxy
   (`caido-capture` should already have set that up).
2. `navigate_page(url=<entry_url from chain>)`.
2a. **DOMLogger++ injection (T2.1).** Immediately after navigation,
    inject the source/sink hook payload:
    ```
    evaluate_script(script=<contents of bin/domlogger_payload.js>)
    ```
    Hooks are idempotent (the payload guards via
    `window.__TLX_DOMLOGGER_INSTALLED`). All source reads + sink calls
    that fire during the rest of the run get appended to
    `window.__TLX_DOMLOGGER_EVENTS`.
2b. **Inline-handler enum (T2.4).** Once:
    ```
    evaluate_script(script=<contents of bin/eventlistener_enum.js>)
    ```
    Returns a JSON object — append to
    `findings/<chain_id>/event_handlers.json`. Cross-reference with
    the static-chain handler list to spot static-only or
    runtime-only handlers.
3. Inject the PoC payload via the channel the chain identifies:
   - URL parameter / fragment
   - form input + submit
   - `postMessage` from a controlled origin (use `evaluate_script` to
     do it from the same tab as origin-spoof)
4. Watch sink:
   - `list_console_messages` for our canary string
   - `list_network_requests` for a callback to our beacon host
   - `evaluate_script` to read the DOM for our injected node
   - `evaluate_script(script="JSON.stringify(window.__TLX_DOMLOGGER_EVENTS||[])")`
     and write to `findings/<chain_id>/domlogger.jsonl` so passive
     source/sink events are captured even when the explicit canary
     check misses.
5. `take_screenshot` of the moment of triggering.

### Mock mode (fallback)
1. `mock_start(session_id=<chain_id>, target_folder="targets/<name>/sources/")`.
2. playwright MCP `browser_navigate` to the returned URL.
3. Trigger the chain analogously.
4. `mock_confirm(session_id, chain_id)` — TLX's hook observes and
   persists.
5. `mock_stop(session_id)`.

## Outputs
- `targets/<name>/findings/<chain_id>/confirmed.json`
- `targets/<name>/findings/<chain_id>/screenshots/*.png`
- `targets/<name>/findings/<chain_id>/network.har` (live mode only)
- `targets/<name>/findings/<chain_id>/domlogger.jsonl` (live mode, T2.1)
- `targets/<name>/findings/<chain_id>/event_handlers.json` (live mode, T2.4)

## Failure modes
- Sink doesn't fire → demote chain to `verdict: undetermined`,
  queue for `autoresearch-loop`.
- Live target has CSP that blocks our payload → record the CSP in
  `findings/<id>/csp_notes.md`; mark `bypass_needed: true`. Don't
  attempt CSP bypass without user OK.
- Target blocks our IP → switch to mock mode; log.

## Result block
```json
"phases": { "browser_confirm": { "status": "done", "ts": "<iso>",
  "confirmed_ids": [...], "failed_ids": [...], "mode_used": "live|mock" } }
```
