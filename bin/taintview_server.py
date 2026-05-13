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
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import json
from fastapi import HTTPException
from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel


class VerdictIn(BaseModel):
    verdict: Literal["tp", "fp", "undet"]
    note: str = ""


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def _resolve_target(targets_root: Path, name: str) -> Path:
    """Resolve a target dir under targets_root, rejecting path-escape attempts."""
    candidate = (targets_root / name).resolve()
    root_resolved = targets_root.resolve()
    if not candidate.is_relative_to(root_resolved):
        raise HTTPException(400, "invalid target name")
    return candidate


_node_cache: dict[tuple[str, float], dict[str, dict]] = {}


def _load_nodes_index(nodes_path: Path) -> dict[str, dict]:
    if not nodes_path.exists():
        return {}
    key = (str(nodes_path), nodes_path.stat().st_mtime)
    cached = _node_cache.get(key)
    if cached is not None:
        return cached
    by_qname: dict[str, dict] = {}
    for line in nodes_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        by_qname[rec["qname"]] = rec
    _node_cache[key] = by_qname
    return by_qname


def build_app(*, targets_root: Path, spa_dist: Path | None = None) -> FastAPI:
    app = FastAPI(title="taintview")
    app.state.targets_root = targets_root
    if spa_dist is None:
        spa_dist = Path(__file__).resolve().parent.parent / "tools" / "taintview" / "dist"
    app.state.spa_dist = spa_dist

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
        target_dir = _resolve_target(app.state.targets_root, name)
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

    @app.get("/api/target/{name}/opus/{chain_id}")
    def get_opus(name: str, chain_id: int) -> dict:
        target_dir = _resolve_target(app.state.targets_root, name)
        path = target_dir / "opus" / f"{chain_id}.md"
        if not path.exists():
            raise HTTPException(404, f"no opus writeup for chain {chain_id}")
        return {"chain_id": chain_id, "markdown": path.read_text()}

    @app.get("/api/target/{name}/snippet")
    def get_snippet(name: str, qname: str) -> dict:
        target_dir = _resolve_target(app.state.targets_root, name)
        nodes = _load_nodes_index(target_dir / "index" / "nodes.jsonl")
        rec = nodes.get(qname)
        if rec is None:
            raise HTTPException(404, "qname not indexed")
        src_path = target_dir / "sources" / rec["file"]
        sources_root = (target_dir / "sources").resolve()
        try:
            resolved = src_path.resolve(strict=False)
        except OSError:
            raise HTTPException(400, "invalid file path")
        if not resolved.is_relative_to(sources_root):
            raise HTTPException(400, "invalid file path")
        if not resolved.exists():
            raise HTTPException(404, f"source file missing: {rec['file']}")
        lines = resolved.read_text().splitlines()
        line = rec["line"]
        end_line = rec.get("end_line") or line
        start = max(1, line - 3)
        end = min(len(lines), end_line + 3)
        slice_ = "\n".join(lines[start - 1:end])
        return {
            "qname": qname,
            "file": rec["file"],
            "line": line,
            "end_line": end_line,
            "start": start,
            "end": end,
            "source": slice_,
        }

    @app.post("/api/target/{name}/verdict/{chain_id}")
    def post_verdict(name: str, chain_id: int, payload: VerdictIn) -> dict:
        target_dir = _resolve_target(app.state.targets_root, name)
        if not (target_dir / "chains" / "all.jsonl").exists():
            raise HTTPException(404, f"target {name!r} not found")
        rec = {
            "chain_id": chain_id,
            "verdict": payload.verdict,
            "note": payload.note,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        with (target_dir / "verdicts.jsonl").open("a") as f:
            f.write(json.dumps(rec) + "\n")
        return rec

    @app.get("/api/target/{name}/verdicts")
    def get_verdicts(name: str) -> dict:
        target_dir = _resolve_target(app.state.targets_root, name)
        path = target_dir / "verdicts.jsonl"
        collapsed: dict[str, dict] = {}
        if path.exists():
            for line in path.read_text().splitlines():
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                collapsed[str(rec["chain_id"])] = rec
        return {"verdicts": collapsed}

    if (spa_dist / "assets").exists():
        app.mount("/assets", StaticFiles(directory=spa_dist / "assets"), name="assets")

    index_html = spa_dist / "index.html"

    @app.get("/", include_in_schema=False)
    def root() -> FileResponse:
        return FileResponse(index_html)

    @app.get("/{spa_path:path}", include_in_schema=False)
    def spa_catchall(spa_path: str) -> FileResponse:
        if spa_path.startswith("api/"):
            raise HTTPException(404)
        return FileResponse(index_html)

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
