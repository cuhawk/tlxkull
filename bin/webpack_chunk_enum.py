#!/usr/bin/env python3
"""Webpack lazy-loaded chunk URL enumeration helper.

Generates a JS snippet that, when run via @browser javascript_tool on a live
target page with webpack runtime loaded, iterates `__webpack_require__.u(id)`
across an ID space to produce every chunk URL the bundle knows about — not
just the chunks loaded on-visit.

Bundlers may gate __webpack_require__ behind a closure. If so, we sniff the
chunk push array (webpackChunk_N_E / webpackChunk) for any module-id keys
already populated, then attempt to call require.u via patched ref.

Usage:
  python3 bin/webpack_chunk_enum.py --snippet > /tmp/wp.js
  # paste into @browser javascript_tool; or use orchestrator that calls
  # mcp__claude-in-chrome__javascript_tool with the snippet text.

  python3 bin/webpack_chunk_enum.py --persist <result_json_path> <target_name>
      writes the discovered URLs to:
          targets/<name>/runtime/<ts>/webpack_chunks.json
      and appends new URLs (not already in any url_list_v*.txt under
          raw/www.coolblue.de/_log/) to:
          targets/<name>/raw/www.coolblue.de/_log/url_list_v3_delta.txt
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# JS that walks every known way to reach the webpack chunk URL function.
# Returns a JSON-stringified array of {id, url} plus diagnostic info.
JS_SNIPPET = r"""
(() => {
  function safe(fn, fallback) { try { return fn(); } catch (e) { return fallback; } }

  // Strategy 1: window.__webpack_require__ direct (older webpack builds)
  let wpr = window.__webpack_require__ || null;

  // Strategy 2: Hijack a freshly-resolved push call to capture __webpack_require__
  // (Next.js App Router gates it inside an IIFE closure)
  if (!wpr) {
    const chunks = window.webpackChunk_N_E || window.webpackChunk || null;
    if (chunks && typeof chunks.push === 'function') {
      try {
        chunks.push([
          ['__tlx_probe_' + Date.now()],
          {},
          (req) => { window.__tlx_wpr = req; }
        ]);
        wpr = window.__tlx_wpr || null;
      } catch (e) {}
    }
  }

  // Strategy 3: scan loaded scripts for require.u inline expressions
  // (only used as a fallback hint, not enumeration)

  const diag = {
    wpr_present: !!wpr,
    wpr_u_present: !!(wpr && wpr.u),
    wpr_p: wpr && wpr.p ? wpr.p : null,
    chunk_array_length: safe(() => (window.webpackChunk_N_E || window.webpackChunk || []).length, 0),
  };

  if (!wpr || !wpr.u) {
    return JSON.stringify({ diag, urls: [], error: 'webpack_require_u_unreachable' });
  }

  // Iterate IDs. Webpack typically uses 4-5 digit numeric IDs but a contiguous
  // range search is wasteful. Instead: walk known IDs from the chunk array's
  // already-pushed modules + brute the 0..20000 range and dedupe.
  const seen = new Set();
  const results = [];

  // Seed from already-pushed module IDs (these are usually valid chunk IDs too)
  const seedIds = [];
  safe(() => {
    const arr = window.webpackChunk_N_E || window.webpackChunk || [];
    for (const tuple of arr) {
      if (Array.isArray(tuple[0])) {
        for (const id of tuple[0]) seedIds.push(id);
      }
      if (tuple[1] && typeof tuple[1] === 'object') {
        for (const k of Object.keys(tuple[1])) {
          const n = Number(k);
          if (Number.isFinite(n)) seedIds.push(n);
        }
      }
    }
  });

  // Brute 0..20000 — webpack URLs return undefined or throw for unknown IDs;
  // we keep only resolutions that look like a real chunk URL.
  for (let i = 0; i < 20000; i++) {
    if (i >= 20000) break;
    let u;
    try { u = wpr.u(i); } catch (e) { continue; }
    if (!u || typeof u !== 'string') continue;
    if (!/\.js/.test(u)) continue;
    if (seen.has(u)) continue;
    seen.add(u);
    results.push({ id: i, url: u });
  }
  // Also iterate the seed set in case it has larger IDs
  for (const i of seedIds) {
    let u;
    try { u = wpr.u(i); } catch (e) { continue; }
    if (!u || typeof u !== 'string') continue;
    if (seen.has(u)) continue;
    seen.add(u);
    results.push({ id: i, url: u });
  }

  // Build full URLs by prefixing with wpr.p when present and the chunk URL is
  // relative.
  const base = (wpr.p || '').replace(/\/?$/, '/');
  const full = results.map(r => ({
    id: r.id,
    url: /^https?:\/\//.test(r.url) ? r.url : (base + r.url)
  }));

  return JSON.stringify({ diag, urls: full });
})()
"""


def cmd_snippet() -> int:
    sys.stdout.write(JS_SNIPPET)
    return 0


def cmd_persist(state_json_path: str, target_name: str) -> int:
    p = Path(state_json_path)
    if not p.is_file():
        print(f"state path not found: {p}", file=sys.stderr)
        return 2
    try:
        raw = p.read_text()
        parsed = json.loads(raw)
        if isinstance(parsed, str):
            parsed = json.loads(parsed)
    except json.JSONDecodeError as e:
        print(f"bad JSON: {e}", file=sys.stderr)
        return 2

    urls = [u["url"] for u in (parsed.get("urls") or [])]
    diag = parsed.get("diag", {})

    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_dir = ROOT / "targets" / target_name / "runtime" / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "webpack_chunks.json").write_text(json.dumps(parsed, indent=2))

    # Compute delta vs any url_list_v*.txt
    log_dir = ROOT / "targets" / target_name / "raw"
    known: set[str] = set()
    for f in log_dir.rglob("url_list_v*.txt"):
        for line in f.read_text().splitlines():
            line = line.strip()
            if line:
                known.add(line)

    delta = [u for u in urls if u not in known]
    delta_path = ROOT / "targets" / target_name / "raw" / "www.coolblue.de" / "_log" / "url_list_v3_delta.txt"
    delta_path.parent.mkdir(parents=True, exist_ok=True)
    with open(delta_path, "w") as f:
        for u in sorted(set(delta)):
            f.write(u + "\n")

    summary = {
        "ts": ts,
        "diag": diag,
        "total_enumerated": len(urls),
        "delta_vs_known": len(delta),
        "delta_file": str(delta_path.relative_to(ROOT)),
        "out": str((out_dir / "webpack_chunks.json").relative_to(ROOT)),
    }
    print(json.dumps(summary, indent=2))
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--snippet", action="store_true", help="Emit JS snippet")
    p.add_argument("--persist", nargs=2, metavar=("STATE_JSON", "TARGET_NAME"))
    args = p.parse_args()
    if args.snippet:
        return cmd_snippet()
    if args.persist:
        return cmd_persist(args.persist[0], args.persist[1])
    p.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
