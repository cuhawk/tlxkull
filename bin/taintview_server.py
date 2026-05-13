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
