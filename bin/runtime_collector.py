#!/usr/bin/env python3
"""Localhost runtime-event collector.

Plan: plans/ARCHITECTURE_EVOLUTION.md §7.

Tiny stdlib HTTP server that accepts the runtime agent's beacon /
fetch POSTs. Persists each batch as one line per event into:

  targets/<name>/runtime/<utc-iso>/events.jsonl

The run-id is created at collector start (one server invocation =
one run). Eval bodies above the configurable threshold are written
to eval_corpus/<sha256>.js.

Listens on 127.0.0.1 only. Refuses any host that isn't loopback.

Usage:
  bin/runtime_collector.py <target>
  bin/runtime_collector.py <target> --port 38731 --no-eval-corpus
"""
from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import os
import socketserver
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import resolve_target_dir, utcnow  # noqa: E402


HOST = "127.0.0.1"
DEFAULT_PORT = 38731


class _Handler(http.server.BaseHTTPRequestHandler):
    target_dir: Path
    run_dir: Path
    state: dict
    eval_corpus: bool

    def log_message(self, fmt: str, *args) -> None:  # silence default logs
        pass

    def _origin_ok(self) -> bool:
        # Loopback only: we bind to 127.0.0.1 so this is mostly belt-
        # and-braces, but reject Origin headers from non-localhost.
        origin = self.headers.get("Origin", "")
        if not origin:
            return True
        return origin.startswith(("http://127.0.0.1", "http://localhost",
                                  "https://127.0.0.1", "https://localhost",
                                  "null"))

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        if not self._origin_ok():
            self.send_response(403)
            self.end_headers()
            return
        if self.path != "/ingest":
            self.send_response(404)
            self.end_headers()
            return
        size = int(self.headers.get("Content-Length", 0) or 0)
        if size > 4 * 1024 * 1024:  # 4 MB cap per batch
            self.send_response(413)
            self.end_headers()
            return
        try:
            raw = self.rfile.read(size)
            payload = json.loads(raw or b"{}")
        except Exception:
            self.send_response(400)
            self.end_headers()
            return
        batch = payload.get("batch") or []
        out_path = self.run_dir / "events.jsonl"
        with out_path.open("a", encoding="utf-8") as f:
            for ev in batch:
                f.write(json.dumps(ev) + "\n")
                self.state["events_total"] = self.state.get("events_total", 0) + 1
                self.state.setdefault("by_kind", {})
                self.state["by_kind"][ev.get("kind", "?")] = (
                    self.state["by_kind"].get(ev.get("kind", "?"), 0) + 1
                )
                if self.eval_corpus and ev.get("kind") == "eval_source":
                    body = ""
                    for p in (ev.get("args_preview") or []):
                        if isinstance(p, str):
                            body = p
                            break
                    if body and len(body) > 32:
                        digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
                        corpus_dir = self.run_dir / "eval_corpus"
                        corpus_dir.mkdir(parents=True, exist_ok=True)
                        out = corpus_dir / f"{digest}.js"
                        if not out.exists():
                            out.write_text(body, encoding="utf-8")
                            idx = corpus_dir / "_index.json"
                            idx_data: dict = {}
                            if idx.exists():
                                try:
                                    idx_data = json.loads(idx.read_text())
                                except Exception:
                                    idx_data = {}
                            idx_data[digest] = {
                                "first_seen_url": ev.get("url"),
                                "fn_caller": ev.get("fn_caller", []),
                                "taint_match": ev.get("args_taint_match", []),
                                "len": len(body),
                            }
                            idx.write_text(json.dumps(idx_data, indent=2))
        # Periodically rewrite state.json.
        if self.state.get("events_total", 0) % 100 == 0:
            (self.run_dir / "state.json").write_text(json.dumps(self.state, indent=2))
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--no-eval-corpus", action="store_true")
    args = ap.parse_args()

    target = resolve_target_dir(args.target)
    run_id = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    run_dir = target / "runtime" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    state: dict = {
        "target": target.name,
        "started_at": utcnow(),
        "events_total": 0,
        "by_kind": {},
        "run_id": run_id,
    }
    meta = {
        "agent_version": "0.1.0",
        "started_at": utcnow(),
        "host": HOST,
        "port": args.port,
        "eval_corpus": not args.no_eval_corpus,
    }
    (run_dir / "agent_meta.json").write_text(json.dumps(meta, indent=2))

    _Handler.target_dir = target
    _Handler.run_dir = run_dir
    _Handler.state = state
    _Handler.eval_corpus = not args.no_eval_corpus

    with socketserver.ThreadingTCPServer((HOST, args.port), _Handler) as srv:
        print(json.dumps({
            "listening": f"http://{HOST}:{args.port}/ingest",
            "run_dir": str(run_dir),
            "target": target.name,
        }, indent=2))
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            (run_dir / "state.json").write_text(json.dumps(state, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
