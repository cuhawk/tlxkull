#!/usr/bin/env python3
"""Dump live browser tab state from DOMLogger++ + postMessage-tracker + Gecko.

Designed to be invoked from a Claude Code skill that has @browser
(claude-in-chrome MCP) available. This script does NOT call @browser itself —
it generates the JS snippet that Claude should pass to
`mcp__claude-in-chrome__javascript_tool`, and parses the JSON result.

Usage from a skill:
  1. snippet = subprocess.check_output(["python3", "bin/dump_browser_state.py", "--snippet"])
  2. result = call mcp__claude-in-chrome__javascript_tool with that snippet
  3. result_json = json.loads(result)
  4. python3 bin/dump_browser_state.py --persist <result_json_path> <target_name>

For a one-shot CLI flow without the orchestrator:
  python3 bin/dump_browser_state.py --snippet > /tmp/dump.js
  # paste /tmp/dump.js into devtools console, copy result, save to /tmp/state.json
  python3 bin/dump_browser_state.py --persist /tmp/state.json coolblue-intigriti

Output layout:
  targets/<name>/runtime/<utc-iso>/state.json
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# JS snippet executed in the live tab. Returns a JSON string capturing every
# instrumented store we know about. Idempotent + safe — read-only.
JS_SNIPPET = r"""
(() => {
  function safe(fn, fallback) { try { return fn(); } catch (e) { return fallback; } }
  function hostsOf(urls) {
    const s = new Set();
    for (const u of (urls||[])) {
      try { s.add(new URL(u).host); } catch (e) {}
    }
    return [...s];
  }
  const out = {
    ts: new Date().toISOString(),
    location: location.href,
    title: document.title,

    // --- DOMLogger++ ---
    // Default global is window.DomLog or window.domlogger++ data. The
    // extension does not have a stable public API; we sniff multiple shapes.
    domlogger: safe(() => {
      const candidates = [
        window.__DOMLogger__,
        window.DomLog,
        window.__domLogger,
        window.DOMLogger,
        window.__DOMLOGGER__,
      ];
      for (const c of candidates) {
        if (c && typeof c === 'object') {
          return {
            shape: Object.keys(c).slice(0, 30),
            log: Array.isArray(c.log) ? c.log.slice(-200) : (Array.isArray(c.entries) ? c.entries.slice(-200) : null),
            count: (c.log && c.log.length) || (c.entries && c.entries.length) || 0,
          };
        }
      }
      // Also check our own injected payload globals (T2.1 fallback)
      if (window.__TLX_DOMLOGGER_EVENTS) {
        return {
          shape: ['__TLX_DOMLOGGER_EVENTS'],
          log: (window.__TLX_DOMLOGGER_EVENTS || []).slice(-200),
          count: (window.__TLX_DOMLOGGER_EVENTS || []).length,
          source: 'tlx_injected'
        };
      }
      return null;
    }, {error: 'sniff_failed'}),

    // --- postMessage-tracker (Frans Rosén) ---
    // The extension renders into its popup via background message-passing.
    // We can probe addEventListener overrides it installs on Window.prototype.
    postmessage_tracker: safe(() => {
      // Common globals the tracker exposes when installed
      const candidates = [
        window.__postMessageTrackerLog,
        window.postMessageListeners,
        window._pmtLog,
        window.__PMT__,
      ];
      for (const c of candidates) {
        if (c) return { shape: Object.keys(c).slice(0,30), data: c };
      }
      // Probe: count addEventListener('message') call sites by scanning
      // Window.prototype.addEventListener for wrapped marker
      const ael = Window.prototype.addEventListener;
      return {
        installed: !!ael.__pmt_wrapped,
        listener_count_hint: null,
      };
    }, {error: 'sniff_failed'}),

    // --- Gecko (Caleb Gross) ---
    // Gecko marks payload candidates on detected sinks. Sniff for namespace.
    gecko: safe(() => {
      const candidates = [
        window.__gecko,
        window.GECKO,
        window.geckoSinks,
        window.__GECKO_PAYLOADS__,
      ];
      for (const c of candidates) {
        if (c) return { shape: Object.keys(c).slice(0,30), data: c };
      }
      return null;
    }, {error: 'sniff_failed'}),

    // --- Resource enumeration (free, always works) ---
    resources: {
      total: performance.getEntriesByType('resource').length,
      js: performance.getEntriesByType('resource').filter(r => /\.js(\?|$)/.test(r.name)).map(r => r.name),
      api: performance.getEntriesByType('resource').filter(r => /\/(api|graphql)\/?/.test(r.name)).map(r => r.name).slice(0,200),
    },

    // --- Framework + bundle introspection ---
    frameworks: {
      react: !!window.React,
      vue: !!window.Vue,
      angular: !!window.angular || !!document.querySelector('[ng-version]'),
      next: !!window.__NEXT_DATA__ || !!window.next,
      nuxt: !!window.__NUXT__,
      svelte: !!document.querySelector('[class*=svelte]'),
    },
    webpack: safe(() => ({
      chunk_count: (window.webpackChunk_N_E || window.webpackChunk || []).length,
      runtime_present: typeof window.__webpack_require__ === 'function',
    }), null),

    // --- Listeners + handlers (cheap snapshot) ---
    listeners: safe(() => ({
      inline_handlers: [...document.querySelectorAll('*')].slice(0,5000).reduce((acc, el) => {
        for (const attr of el.attributes) {
          if (attr.name.startsWith('on') && attr.value) {
            acc.push({tag: el.tagName, attr: attr.name, snippet: attr.value.slice(0,120)});
            if (acc.length >= 50) return acc;
          }
        }
        return acc;
      }, []),
      script_count: document.querySelectorAll('script').length,
      iframe_count: document.querySelectorAll('iframe').length,
    }), null),

    // --- Form fields (sources for stored XSS) ---
    forms: safe(() => [...document.querySelectorAll('form')].slice(0,20).map(f => ({
      action: f.action,
      method: f.method,
      inputs: [...f.querySelectorAll('input,textarea')].map(i => ({
        name: i.name, type: i.type, id: i.id, maxlength: i.maxLength
      })).slice(0,20)
    })), null),

    // --- URL surface seen ---
    urls: safe(() => ({
      links_internal: [...document.querySelectorAll('a[href]')].map(a => a.href).filter(h => h.includes(location.hostname)).slice(0,100),
      links_external: [...document.querySelectorAll('a[href]')].map(a => a.href).filter(h => !h.includes(location.hostname) && h.startsWith('http')).slice(0,30),
    }), null),
  };
  // Return as JSON string (browser MCP usually stringifies result anyway, but
  // explicit is safer).
  return JSON.stringify(out);
})()
"""


def cmd_snippet() -> int:
    sys.stdout.write(JS_SNIPPET)
    return 0


def cmd_persist(state_json_path: str, target_name: str) -> int:
    state_path = Path(state_json_path)
    if not state_path.is_file():
        print(f"state.json not found: {state_path}", file=sys.stderr)
        return 2
    try:
        # Accept either a literal JSON or a JSON-encoded string
        raw = state_path.read_text()
        parsed = json.loads(raw)
        if isinstance(parsed, str):
            parsed = json.loads(parsed)
    except json.JSONDecodeError as e:
        print(f"bad JSON: {e}", file=sys.stderr)
        return 2

    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_dir = ROOT / "targets" / target_name / "runtime" / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "state.json"
    out_path.write_text(json.dumps(parsed, indent=2))

    # Append a one-line summary to the rolling log
    log_path = ROOT / "targets" / target_name / "runtime" / "_log.jsonl"
    summary = {
        "ts": parsed.get("ts"),
        "location": parsed.get("location"),
        "title": parsed.get("title"),
        "dom_events": (parsed.get("domlogger") or {}).get("count", 0),
        "pmt_installed": (parsed.get("postmessage_tracker") or {}).get("installed", False),
        "webpack_chunks": (parsed.get("webpack") or {}).get("chunk_count", 0),
        "resource_count": (parsed.get("resources") or {}).get("total", 0),
        "js_count": len((parsed.get("resources") or {}).get("js", [])),
        "inline_handlers": len((parsed.get("listeners") or {}).get("inline_handlers", [])),
        "out_path": str(out_path.relative_to(ROOT)),
    }
    with open(log_path, "a") as f:
        f.write(json.dumps(summary) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--snippet", action="store_true", help="Emit the JS snippet to stdout")
    p.add_argument("--persist", nargs=2, metavar=("STATE_JSON", "TARGET_NAME"),
                   help="Persist a captured state JSON into targets/<name>/runtime/")
    args = p.parse_args()

    if args.snippet:
        return cmd_snippet()
    if args.persist:
        return cmd_persist(args.persist[0], args.persist[1])
    p.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
