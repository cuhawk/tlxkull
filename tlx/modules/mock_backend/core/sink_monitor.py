"""Headless-browser sink-confirmation observer.

Boots Playwright Chromium in headless mode, navigates to a URL served
by the per-session mock_server, and watches for the probe sentinel
showing up in any sink-firing context (console, DOM, network).

Playwright sync API is wrapped in asyncio.to_thread to avoid blocking
the event loop. No anthropic / google.genai imports.

Runtime-static merge:
    `merge_runtime_hits_into_callgraph()` writes each SinkHit as a
    dataflow edge with edge_kind='runtime_confirmed', giving downstream
    tooling (chain extraction, scoring) a high-confidence signal that
    the static-graph path was traversed end-to-end at runtime.
"""
from __future__ import annotations

import asyncio
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SinkHit:
    chain_id: str
    sentinel: str
    sink_type: str
    detail: str
    timestamp_ms: float
    extra: dict[str, Any] = field(default_factory=dict)


# ─── Runtime → static merge ──────────────────────────────────────────────

_RUNTIME_HITS_SCHEMA = """
CREATE TABLE IF NOT EXISTS runtime_sink_hits (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    chain_id      TEXT NOT NULL,
    sink_qname    TEXT,
    sink_node_id  INTEGER,
    sink_type     TEXT NOT NULL,
    sentinel      TEXT NOT NULL,
    detail        TEXT,
    timestamp_ms  REAL NOT NULL,
    extra_json    TEXT
);
CREATE INDEX IF NOT EXISTS idx_runtime_hits_chain ON runtime_sink_hits(chain_id);
CREATE INDEX IF NOT EXISTS idx_runtime_hits_sink  ON runtime_sink_hits(sink_node_id);
"""


def merge_runtime_hits_into_callgraph(
    db_path: Path | str,
    hits: list[SinkHit],
    *,
    chain_index: dict[str, dict] | None = None,
) -> dict:
    """Persist runtime sink-hits as `runtime_confirmed` dataflow edges.

    For each hit:
      1. Insert a row into runtime_sink_hits (always).
      2. If chain_index resolves chain_id → {source_qname, sink_qname},
         look up the corresponding node ids and write a dataflow_edges
         row with edge_kind='runtime_confirmed' (idempotent — uses INSERT
         OR IGNORE on the existing PK).

    Returns a small stats dict.

    chain_index format expected:
      {chain_id: {"source_qname": str, "sink_qname": str, "source_var": str?,
                  "sink_var": str?}}

    Where *_var entries are optional. When absent, a synthetic variable
    name '__runtime_confirmed__' is used so the edge has somewhere to
    land. Callers that already track per-chain source/sink variable IDs
    should pass them in for a precise wire-up.
    """
    chain_index = chain_index or {}
    stats = {"hits_recorded": 0, "edges_added": 0, "edges_skipped": 0}
    if not hits:
        return stats

    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(_RUNTIME_HITS_SCHEMA)
        for hit in hits:
            meta = chain_index.get(hit.chain_id, {}) or {}
            sink_qname = meta.get("sink_qname")
            sink_node_id = None
            if sink_qname:
                row = conn.execute(
                    "SELECT id FROM nodes WHERE qualified_name=?",
                    (sink_qname,),
                ).fetchone()
                if row:
                    sink_node_id = row[0]

            extra_json = None
            if hit.extra:
                import json as _json
                extra_json = _json.dumps(hit.extra, default=str)
            conn.execute(
                "INSERT INTO runtime_sink_hits "
                "(chain_id, sink_qname, sink_node_id, sink_type, sentinel, "
                " detail, timestamp_ms, extra_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (hit.chain_id, sink_qname, sink_node_id, hit.sink_type,
                 hit.sentinel, hit.detail, hit.timestamp_ms, extra_json),
            )
            stats["hits_recorded"] += 1

            source_qname = meta.get("source_qname")
            if not (sink_node_id and source_qname):
                stats["edges_skipped"] += 1
                continue
            source_row = conn.execute(
                "SELECT id FROM nodes WHERE qualified_name=?",
                (source_qname,),
            ).fetchone()
            if not source_row:
                stats["edges_skipped"] += 1
                continue
            source_node_id = source_row[0]

            # Find or create synthetic source/sink variable rows so the
            # dataflow edge has FK-valid endpoints. Existing per-chain
            # variable wiring (when caller supplies it) wins.
            source_var = meta.get("source_var") or "__runtime_source__"
            sink_var   = meta.get("sink_var")   or "__runtime_sink__"

            def _ensure_var(node_id: int, name: str) -> int | None:
                conn.execute(
                    "INSERT OR IGNORE INTO variables (node_id, name, first_line) "
                    "VALUES (?, ?, 0)",
                    (node_id, name),
                )
                row = conn.execute(
                    "SELECT id FROM variables WHERE node_id=? AND name=?",
                    (node_id, name),
                ).fetchone()
                return row[0] if row else None

            from_var_id = _ensure_var(source_node_id, source_var)
            to_var_id   = _ensure_var(sink_node_id, sink_var)
            if not (from_var_id and to_var_id):
                stats["edges_skipped"] += 1
                continue

            cur = conn.execute(
                "INSERT OR IGNORE INTO dataflow_edges "
                "(from_var, to_var, edge_kind, line, sanitiser) "
                "VALUES (?, ?, 'runtime_confirmed', 0, NULL)",
                (from_var_id, to_var_id),
            )
            if cur.rowcount > 0:
                stats["edges_added"] += 1
            else:
                stats["edges_skipped"] += 1
        conn.commit()
    finally:
        conn.close()
    return stats


_DOM_PROBE_JS = """
(sentinel) => {
  window.__tlxDomHits = window.__tlxDomHits || [];
  const seen = new Set();
  const scan = () => {
    try {
      const html = document.documentElement
        ? document.documentElement.innerHTML
        : '';
      if (html && html.includes(sentinel) && !seen.has(html.length)) {
        seen.add(html.length);
        window.__tlxDomHits.push({
          ts: Date.now(),
          len: html.length
        });
      }
    } catch (e) { /* ignore */ }
  };
  const obs = new MutationObserver(scan);
  obs.observe(document.documentElement, {
    subtree: true, childList: true, attributes: true, characterData: true
  });
  scan();
}
"""


class SinkMonitor:
    def __init__(
        self,
        sentinel: str,
        timeout_ms: int = 8000,
        chain_id: str = "",
    ) -> None:
        self.sentinel = sentinel
        self.timeout_ms = timeout_ms
        self.chain_id = chain_id

    async def observe(self, url: str) -> list[SinkHit]:
        return await asyncio.to_thread(self._observe_sync, url)

    def _observe_sync(self, url: str) -> list[SinkHit]:
        from playwright.sync_api import sync_playwright

        hits: list[SinkHit] = []
        sentinel = self.sentinel
        chain_id = self.chain_id

        def _now_ms() -> float:
            return time.time() * 1000.0

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            def on_console(msg: Any) -> None:
                try:
                    text = msg.text
                except Exception:
                    text = str(msg)
                if sentinel in (text or ""):
                    hits.append(SinkHit(
                        chain_id=chain_id,
                        sentinel=sentinel,
                        sink_type="console",
                        detail=text or "",
                        timestamp_ms=_now_ms(),
                    ))

            def on_response(resp: Any) -> None:
                try:
                    rurl = resp.url
                except Exception:
                    rurl = ""
                if sentinel in (rurl or ""):
                    hits.append(SinkHit(
                        chain_id=chain_id,
                        sentinel=sentinel,
                        sink_type="network",
                        detail=rurl,
                        timestamp_ms=_now_ms(),
                    ))
                    return
                try:
                    body = resp.body()
                    if body and sentinel.encode("utf-8") in body:
                        hits.append(SinkHit(
                            chain_id=chain_id,
                            sentinel=sentinel,
                            sink_type="network",
                            detail=rurl,
                            timestamp_ms=_now_ms(),
                        ))
                except Exception:
                    pass

            page.on("console", on_console)
            page.on("response", on_response)

            try:
                cdp = context.new_cdp_session(page)
                cdp.send("DOM.enable")
            except Exception:
                pass

            try:
                page.goto(url, wait_until="networkidle",
                          timeout=self.timeout_ms)
            except Exception:
                pass

            try:
                page.evaluate(_DOM_PROBE_JS, sentinel)
            except Exception:
                pass

            page.wait_for_timeout(self.timeout_ms)

            try:
                dom_hits = page.evaluate("() => window.__tlxDomHits || []")
            except Exception:
                dom_hits = []
            for h in dom_hits or []:
                hits.append(SinkHit(
                    chain_id=chain_id,
                    sentinel=sentinel,
                    sink_type="dom_mutation",
                    detail=f"len={h.get('len', 0)}",
                    timestamp_ms=float(h.get("ts", _now_ms())),
                ))

            context.close()
            browser.close()
        return hits
