#!/usr/bin/env python3
"""taintview CLI — boot the FastAPI sidecar and open the SPA in a browser.

Usage:
    python bin/taintview.py <target-name> [--port 8765] [--no-open]
"""
from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(REPO_ROOT / "bin"))
from taintview_server import build_app  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="taintview — DOM taint chain viewer")
    p.add_argument("target", help="target name (must exist under targets/)")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--no-open", action="store_true", help="do not open a browser")
    args = p.parse_args()

    targets_root = REPO_ROOT / "targets"
    if not (targets_root / args.target / "chains" / "all.jsonl").exists():
        print(f"error: targets/{args.target}/chains/all.jsonl missing", file=sys.stderr)
        return 2

    spa_dist = REPO_ROOT / "tools" / "taintview" / "dist"
    if not (spa_dist / "index.html").exists():
        print(f"error: SPA not built. Run: cd tools/taintview && npm run build", file=sys.stderr)
        return 2

    import uvicorn

    app = build_app(targets_root=targets_root, spa_dist=spa_dist)
    url = f"http://{args.host}:{args.port}/?target={args.target}"
    if not args.no_open:
        webbrowser.open(url)
    print(f"taintview listening on {url}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
