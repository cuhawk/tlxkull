"""taintview FastAPI sidecar.

Serves the built taintview SPA and a small JSON API backed by pure
filesystem reads of targets/<name>/{chains,index,sources,opus}/ plus
an append-only verdicts.jsonl. No MCP dependency.

Run:
    python bin/taintview_server.py --target <name>
or via bin/taintview.py.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

import json
from fastapi import HTTPException


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def build_app(*, targets_root: Path) -> FastAPI:
    app = FastAPI(title="taintview")
    app.state.targets_root = targets_root

    @app.get("/api/health")
    def health() -> dict:
        return {"ok": True}

    @app.get("/api/targets")
    def list_targets() -> dict:
        root: Path = app.state.targets_root
        if not root.exists():
            return {"targets": []}
        names = sorted(
            d.name for d in root.iterdir()
            if d.is_dir() and (d / "chains" / "all.jsonl").exists()
        )
        return {"targets": names}

    @app.get("/api/target/{name}/chains")
    def get_chains(name: str) -> dict:
        target_dir = app.state.targets_root / name
        all_path = target_dir / "chains" / "all.jsonl"
        if not all_path.exists():
            raise HTTPException(404, f"target {name!r} has no chains/all.jsonl")
        hot_ids = {c["id"] for c in _read_jsonl(target_dir / "chains" / "hot.jsonl")}
        reachable_ids = {c["id"] for c in _read_jsonl(target_dir / "chains" / "dom_reachable.jsonl")}
        unreachable_ids = {c["id"] for c in _read_jsonl(target_dir / "chains" / "dom_unreachable.jsonl")}
        chains = []
        for c in _read_jsonl(all_path):
            cid = c["id"]
            if cid in reachable_ids:
                reach = "reachable"
            elif cid in unreachable_ids:
                reach = "unreachable"
            else:
                reach = "unknown"
            c["is_hot"] = cid in hot_ids
            c["reach"] = reach
            chains.append(c)
        return {"chains": chains}

    return app


def main() -> None:
    import argparse
    import uvicorn

    p = argparse.ArgumentParser()
    p.add_argument("--targets-root", default="targets")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    args = p.parse_args()

    app = build_app(targets_root=Path(args.targets_root).resolve())
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
