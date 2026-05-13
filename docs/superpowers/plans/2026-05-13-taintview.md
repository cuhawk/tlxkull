# taintview Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a BloodHound-style local SPA + FastAPI sidecar that visualizes DOM taint chains for a single TLX target, lets the operator inspect snippets/Opus verdicts, animate source→sink propagation, and write manual verdicts back to disk.

**Architecture:** Two processes started by one CLI. (1) FastAPI sidecar (`bin/taintview_server.py`) serves a built React SPA and a small JSON API backed by pure filesystem reads of `targets/<name>/{chains,index,sources,opus}/` plus an append-only `verdicts.jsonl`. (2) SPA (`tools/taintview/`, Vite + React + TypeScript + Cytoscape.js + Tailwind) renders a force-directed graph, a filter rail, a chain table, and a node-detail rail. Build output is checked into `tools/taintview/dist/` so the sidecar can serve it without a Node toolchain at runtime.

**Tech Stack:** Python 3.11 + FastAPI + uvicorn (already in `tlx/.venv`); Vite + React 18 + TypeScript + Cytoscape.js (cose-bilkent + dagre layouts) + Tailwind + Vitest + React Testing Library.

**Reference spec:** `docs/superpowers/specs/2026-05-13-taintview-design.md`

---

## File Structure

| Path | Responsibility |
|---|---|
| `bin/taintview.py` | CLI launcher: validates target, starts uvicorn, opens browser |
| `bin/taintview_server.py` | FastAPI app: target listing, chains, opus, snippet, verdicts, static SPA |
| `tools/taintview/package.json` | SPA deps + scripts |
| `tools/taintview/vite.config.ts` | Vite config (base path, output to `dist/`) |
| `tools/taintview/tsconfig.json` | TypeScript config |
| `tools/taintview/tailwind.config.ts` | Tailwind config (dark theme) |
| `tools/taintview/postcss.config.js` | PostCSS for Tailwind |
| `tools/taintview/index.html` | Vite entry |
| `tools/taintview/src/main.tsx` | React bootstrap |
| `tools/taintview/src/App.tsx` | Top-level composition |
| `tools/taintview/src/api.ts` | Typed fetch wrappers |
| `tools/taintview/src/state/chains.ts` | Chain model + graph derivation (pure) |
| `tools/taintview/src/state/filters.ts` | Filter predicate (pure) |
| `tools/taintview/src/components/Graph.tsx` | Cytoscape mount + layout switch |
| `tools/taintview/src/components/FilterRail.tsx` | Left rail UI |
| `tools/taintview/src/components/ChainTable.tsx` | Bottom dock table |
| `tools/taintview/src/components/NodeDetail.tsx` | Right rail container |
| `tools/taintview/src/components/SnippetView.tsx` | Source slice viewer |
| `tools/taintview/src/components/OpusView.tsx` | Opus markdown renderer |
| `tools/taintview/src/components/VerdictEditor.tsx` | TP/FP/undet + note form |
| `tools/taintview/src/util/animate.ts` | Path-pulse animation helper (pure) |
| `tools/taintview/dist/` | Vite build output (checked in) |
| `tools/taintview/tests/test_server.py` | pytest suite for sidecar |
| `tools/taintview/tests/fixtures/` | Synthetic target fixture (chains, index, sources, opus) |
| `tools/taintview/src/__tests__/chains.test.ts` | vitest for state/chains |
| `tools/taintview/src/__tests__/filters.test.ts` | vitest for state/filters |
| `tools/taintview/src/__tests__/animate.test.ts` | vitest for animate.ts |

Each task below is self-contained: it lists the files it touches, the test it adds, the code to write, the command to run, and a commit.

---

## Task 1: Sidecar scaffold + health endpoint

**Files:**
- Create: `bin/taintview_server.py`
- Create: `tools/taintview/tests/__init__.py`
- Create: `tools/taintview/tests/conftest.py`
- Create: `tools/taintview/tests/test_server.py`
- Create: `tools/taintview/tests/fixtures/.gitkeep`

- [ ] **Step 1: Install pytest into the tlx venv**

Run:
```bash
cd /Users/soural/Documents/TLX/tlx
uv pip install -e ".[dev]"
```
Expected: pytest, pytest-asyncio installed. Verify:
```bash
/Users/soural/Documents/TLX/tlx/.venv/bin/python -c "import pytest, httpx; print(pytest.__version__, httpx.__version__)"
```

- [ ] **Step 2: Write conftest.py with a `client` fixture**

Create `tools/taintview/tests/conftest.py`:
```python
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "bin"))

from taintview_server import build_app  # noqa: E402


@pytest.fixture
def targets_root(tmp_path: Path) -> Path:
    root = tmp_path / "targets"
    root.mkdir()
    return root


@pytest.fixture
def client(targets_root: Path) -> TestClient:
    app = build_app(targets_root=targets_root)
    return TestClient(app)
```

- [ ] **Step 3: Write the failing test**

Create `tools/taintview/tests/test_server.py`:
```python
def test_health_returns_ok(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"ok": True}
```

- [ ] **Step 4: Run test to verify it fails**

Run:
```bash
cd /Users/soural/Documents/TLX
/Users/soural/Documents/TLX/tlx/.venv/bin/python -m pytest tools/taintview/tests/test_server.py -v
```
Expected: ImportError on `taintview_server`.

- [ ] **Step 5: Implement minimal sidecar**

Create `bin/taintview_server.py`:
```python
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
```

- [ ] **Step 6: Run test to verify it passes**

Run: `/Users/soural/Documents/TLX/tlx/.venv/bin/python -m pytest tools/taintview/tests/test_server.py -v`
Expected: 1 passed.

- [ ] **Step 7: Commit**

```bash
git add bin/taintview_server.py tools/taintview/tests/__init__.py tools/taintview/tests/conftest.py tools/taintview/tests/test_server.py tools/taintview/tests/fixtures/.gitkeep
git commit -m "taintview: scaffold FastAPI sidecar with health endpoint"
```

---

## Task 2: Sidecar — list targets

**Files:**
- Modify: `bin/taintview_server.py`
- Modify: `tools/taintview/tests/test_server.py`

- [ ] **Step 1: Write failing test**

Append to `tools/taintview/tests/test_server.py`:
```python
def test_list_targets_returns_only_targets_with_chains(client, targets_root):
    (targets_root / "alpha" / "chains").mkdir(parents=True)
    (targets_root / "alpha" / "chains" / "all.jsonl").write_text("")
    (targets_root / "beta").mkdir()  # no chains/all.jsonl -- excluded
    (targets_root / "gamma" / "chains").mkdir(parents=True)
    (targets_root / "gamma" / "chains" / "all.jsonl").write_text("")

    r = client.get("/api/targets")
    assert r.status_code == 200
    assert sorted(r.json()["targets"]) == ["alpha", "gamma"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `/Users/soural/Documents/TLX/tlx/.venv/bin/python -m pytest tools/taintview/tests/test_server.py::test_list_targets_returns_only_targets_with_chains -v`
Expected: 404 on `/api/targets`.

- [ ] **Step 3: Implement endpoint**

In `bin/taintview_server.py`, inside `build_app` after the health endpoint:
```python
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
```

- [ ] **Step 4: Run test, verify pass**

Run: `/Users/soural/Documents/TLX/tlx/.venv/bin/python -m pytest tools/taintview/tests/test_server.py -v`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add bin/taintview_server.py tools/taintview/tests/test_server.py
git commit -m "taintview: add /api/targets endpoint"
```

---

## Task 3: Sidecar — fixture builder

**Files:**
- Modify: `tools/taintview/tests/conftest.py`

- [ ] **Step 1: Add a `target_factory` fixture**

Append to `tools/taintview/tests/conftest.py`:
```python
import json
from dataclasses import dataclass


@dataclass
class TargetBuilder:
    root: Path
    name: str

    def chains(self, *, all_: list[dict], hot: list[dict] | None = None,
               reachable: list[dict] | None = None,
               unreachable: list[dict] | None = None) -> "TargetBuilder":
        d = self.root / self.name / "chains"
        d.mkdir(parents=True, exist_ok=True)
        (d / "all.jsonl").write_text("\n".join(json.dumps(c) for c in all_) + "\n")
        if hot is not None:
            (d / "hot.jsonl").write_text("\n".join(json.dumps(c) for c in hot) + "\n")
        if reachable is not None:
            (d / "dom_reachable.jsonl").write_text("\n".join(json.dumps(c) for c in reachable) + "\n")
        if unreachable is not None:
            (d / "dom_unreachable.jsonl").write_text("\n".join(json.dumps(c) for c in unreachable) + "\n")
        return self

    def index(self, *, nodes: list[dict]) -> "TargetBuilder":
        d = self.root / self.name / "index"
        d.mkdir(parents=True, exist_ok=True)
        (d / "nodes.jsonl").write_text("\n".join(json.dumps(n) for n in nodes) + "\n")
        return self

    def source(self, file: str, text: str) -> "TargetBuilder":
        path = self.root / self.name / "sources" / file
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return self

    def opus(self, chain_id: int, md: str) -> "TargetBuilder":
        d = self.root / self.name / "opus"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{chain_id}.md").write_text(md)
        return self


@pytest.fixture
def target_factory(targets_root):
    def make(name: str) -> TargetBuilder:
        return TargetBuilder(root=targets_root, name=name)
    return make
```

- [ ] **Step 2: Commit (no test run; fixtures are exercised by later tasks)**

```bash
git add tools/taintview/tests/conftest.py
git commit -m "taintview: add TargetBuilder test fixture"
```

---

## Task 4: Sidecar — chains endpoint with hot/reach annotation

**Files:**
- Modify: `bin/taintview_server.py`
- Modify: `tools/taintview/tests/test_server.py`

- [ ] **Step 1: Write failing test**

Append to `tools/taintview/tests/test_server.py`:
```python
def _chain(cid: int) -> dict:
    return {
        "id": cid,
        "source": {"qname": f"a.js::src{cid}", "file": "a.js", "line": 1, "taxonomy_id": "url_query"},
        "sink": {"qname": f"b.js::sink{cid}", "file": "b.js", "line": 2, "taxonomy_id": "dom_innerHTML"},
        "depth": 1,
        "path": [f"a.js::src{cid}", f"b.js::sink{cid}"],
        "score": 70.0 + cid,
        "scoring": {},
        "variants": [],
    }


def test_chains_endpoint_returns_hot_and_reach_flags(client, target_factory):
    target_factory("t1").chains(
        all_=[_chain(1), _chain(2), _chain(3)],
        hot=[_chain(1), _chain(2)],
        reachable=[_chain(1)],
        unreachable=[_chain(2)],
    )
    r = client.get("/api/target/t1/chains")
    assert r.status_code == 200
    body = r.json()
    by_id = {c["id"]: c for c in body["chains"]}
    assert by_id[1]["is_hot"] is True
    assert by_id[1]["reach"] == "reachable"
    assert by_id[2]["is_hot"] is True
    assert by_id[2]["reach"] == "unreachable"
    assert by_id[3]["is_hot"] is False
    assert by_id[3]["reach"] == "unknown"


def test_chains_endpoint_404_for_missing_target(client):
    r = client.get("/api/target/nope/chains")
    assert r.status_code == 404
```

- [ ] **Step 2: Run test, expect fail**

Run: `/Users/soural/Documents/TLX/tlx/.venv/bin/python -m pytest tools/taintview/tests/test_server.py -v -k chains_endpoint`
Expected: 404 on `/api/target/t1/chains` (route undefined).

- [ ] **Step 3: Implement endpoint**

In `bin/taintview_server.py`, add helper above `build_app`:
```python
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
```

Inside `build_app`, add:
```python
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
```

- [ ] **Step 4: Run tests, expect pass**

Run: `/Users/soural/Documents/TLX/tlx/.venv/bin/python -m pytest tools/taintview/tests/test_server.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add bin/taintview_server.py tools/taintview/tests/test_server.py
git commit -m "taintview: add /api/target/{name}/chains with hot+reach flags"
```

---

## Task 5: Sidecar — opus markdown endpoint

**Files:**
- Modify: `bin/taintview_server.py`
- Modify: `tools/taintview/tests/test_server.py`

- [ ] **Step 1: Write failing test**

Append:
```python
def test_opus_endpoint_returns_markdown(client, target_factory):
    target_factory("t1").chains(all_=[_chain(1)]).opus(1, "# verdict: FP\nreason: setTimeout callback fn")
    r = client.get("/api/target/t1/opus/1")
    assert r.status_code == 200
    assert r.json() == {"chain_id": 1, "markdown": "# verdict: FP\nreason: setTimeout callback fn"}


def test_opus_endpoint_404_when_missing(client, target_factory):
    target_factory("t1").chains(all_=[_chain(1)])
    r = client.get("/api/target/t1/opus/1")
    assert r.status_code == 404
```

- [ ] **Step 2: Run test, expect fail**

Run: `/Users/soural/Documents/TLX/tlx/.venv/bin/python -m pytest tools/taintview/tests/test_server.py -v -k opus_endpoint`
Expected: 2 failures (route undefined → 404 on both, but second test wants 404 for a different reason; first will get 404 wrongly).

- [ ] **Step 3: Implement**

In `bin/taintview_server.py` inside `build_app`:
```python
    @app.get("/api/target/{name}/opus/{chain_id}")
    def get_opus(name: str, chain_id: int) -> dict:
        path = app.state.targets_root / name / "opus" / f"{chain_id}.md"
        if not path.exists():
            raise HTTPException(404, f"no opus writeup for chain {chain_id}")
        return {"chain_id": chain_id, "markdown": path.read_text()}
```

- [ ] **Step 4: Run tests, expect pass**

Run: `/Users/soural/Documents/TLX/tlx/.venv/bin/python -m pytest tools/taintview/tests/test_server.py -v`
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add bin/taintview_server.py tools/taintview/tests/test_server.py
git commit -m "taintview: add /api/target/{name}/opus/{chain_id} endpoint"
```

---

## Task 6: Sidecar — snippet endpoint (filesystem)

**Files:**
- Modify: `bin/taintview_server.py`
- Modify: `tools/taintview/tests/test_server.py`

- [ ] **Step 1: Write failing tests**

Append:
```python
def test_snippet_returns_source_slice(client, target_factory):
    src = "\n".join(f"line{i}" for i in range(1, 21))
    target_factory("t1").chains(all_=[_chain(1)]).index(
        nodes=[{"qname": "a.js::foo", "file": "a.js", "line": 8, "end_line": 12,
                "kind": "function", "parent": None, "name": "foo"}]
    ).source("a.js", src)
    r = client.get("/api/target/t1/snippet", params={"qname": "a.js::foo"})
    assert r.status_code == 200
    body = r.json()
    assert body["qname"] == "a.js::foo"
    assert body["file"] == "a.js"
    assert body["line"] == 8
    assert body["end_line"] == 12
    # ±3 lines of context => lines 5..15 inclusive
    assert body["start"] == 5
    assert body["end"] == 15
    assert body["source"].splitlines() == [f"line{i}" for i in range(5, 16)]


def test_snippet_404_when_qname_not_indexed(client, target_factory):
    target_factory("t1").chains(all_=[_chain(1)]).index(nodes=[])
    r = client.get("/api/target/t1/snippet", params={"qname": "a.js::missing"})
    assert r.status_code == 404
    assert "qname not indexed" in r.json()["detail"]


def test_snippet_404_when_source_file_missing(client, target_factory):
    target_factory("t1").chains(all_=[_chain(1)]).index(
        nodes=[{"qname": "a.js::foo", "file": "a.js", "line": 1, "end_line": 2,
                "kind": "function", "parent": None, "name": "foo"}]
    )  # no .source() call
    r = client.get("/api/target/t1/snippet", params={"qname": "a.js::foo"})
    assert r.status_code == 404
    assert "source file missing" in r.json()["detail"]
```

- [ ] **Step 2: Run, expect fail**

Run: `/Users/soural/Documents/TLX/tlx/.venv/bin/python -m pytest tools/taintview/tests/test_server.py -v -k snippet`
Expected: 3 failures (route undefined).

- [ ] **Step 3: Implement endpoint**

Add module-level helper:
```python
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
```

Inside `build_app`:
```python
    @app.get("/api/target/{name}/snippet")
    def get_snippet(name: str, qname: str) -> dict:
        target_dir = app.state.targets_root / name
        nodes = _load_nodes_index(target_dir / "index" / "nodes.jsonl")
        rec = nodes.get(qname)
        if rec is None:
            raise HTTPException(404, "qname not indexed")
        src_path = target_dir / "sources" / rec["file"]
        if not src_path.exists():
            raise HTTPException(404, f"source file missing: {rec['file']}")
        lines = src_path.read_text().splitlines()
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
```

- [ ] **Step 4: Run tests, expect pass**

Run: `/Users/soural/Documents/TLX/tlx/.venv/bin/python -m pytest tools/taintview/tests/test_server.py -v`
Expected: 9 passed.

- [ ] **Step 5: Commit**

```bash
git add bin/taintview_server.py tools/taintview/tests/test_server.py
git commit -m "taintview: add /api/target/{name}/snippet (filesystem read)"
```

---

## Task 7: Sidecar — verdicts (POST + GET with last-write-wins)

**Files:**
- Modify: `bin/taintview_server.py`
- Modify: `tools/taintview/tests/test_server.py`

- [ ] **Step 1: Write failing tests**

Append:
```python
def test_post_verdict_appends_and_get_returns_latest(client, target_factory, targets_root):
    target_factory("t1").chains(all_=[_chain(1)])
    r1 = client.post("/api/target/t1/verdict/1", json={"verdict": "fp", "note": "first"})
    assert r1.status_code == 200
    r2 = client.post("/api/target/t1/verdict/1", json={"verdict": "tp", "note": "second"})
    assert r2.status_code == 200
    r3 = client.get("/api/target/t1/verdicts")
    assert r3.status_code == 200
    body = r3.json()
    assert body["verdicts"]["1"]["verdict"] == "tp"
    assert body["verdicts"]["1"]["note"] == "second"
    # And the underlying file is append-only (two lines)
    lines = (targets_root / "t1" / "verdicts.jsonl").read_text().strip().splitlines()
    assert len(lines) == 2


def test_post_verdict_rejects_unknown_verdict_value(client, target_factory):
    target_factory("t1").chains(all_=[_chain(1)])
    r = client.post("/api/target/t1/verdict/1", json={"verdict": "maybe", "note": ""})
    assert r.status_code == 422
```

- [ ] **Step 2: Run, expect fail**

Run: `/Users/soural/Documents/TLX/tlx/.venv/bin/python -m pytest tools/taintview/tests/test_server.py -v -k verdict`
Expected: 404 (route undefined).

- [ ] **Step 3: Implement**

Add at top of file (after existing imports):
```python
from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel


class VerdictIn(BaseModel):
    verdict: Literal["tp", "fp", "undet"]
    note: str = ""
```

Inside `build_app`:
```python
    @app.post("/api/target/{name}/verdict/{chain_id}")
    def post_verdict(name: str, chain_id: int, payload: VerdictIn) -> dict:
        target_dir = app.state.targets_root / name
        target_dir.mkdir(parents=True, exist_ok=True)
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
        path = app.state.targets_root / name / "verdicts.jsonl"
        collapsed: dict[str, dict] = {}
        if path.exists():
            for line in path.read_text().splitlines():
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                collapsed[str(rec["chain_id"])] = rec
        return {"verdicts": collapsed}
```

- [ ] **Step 4: Run tests, expect pass**

Run: `/Users/soural/Documents/TLX/tlx/.venv/bin/python -m pytest tools/taintview/tests/test_server.py -v`
Expected: 11 passed.

- [ ] **Step 5: Commit**

```bash
git add bin/taintview_server.py tools/taintview/tests/test_server.py
git commit -m "taintview: add /api/target/{name}/verdict POST + GET"
```

---

## Task 8: Sidecar — static SPA mount

**Files:**
- Modify: `bin/taintview_server.py`
- Modify: `tools/taintview/tests/test_server.py`
- Create: `tools/taintview/dist/index.html` (placeholder for test)

- [ ] **Step 1: Create placeholder dist**

```bash
mkdir -p /Users/soural/Documents/TLX/tools/taintview/dist
printf '<!doctype html><title>taintview</title><div id=root></div>\n' > /Users/soural/Documents/TLX/tools/taintview/dist/index.html
```

- [ ] **Step 2: Write failing test**

Append to `tools/taintview/tests/test_server.py`:
```python
def test_root_serves_spa_index_html(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "<div id=root>" in r.text


def test_unknown_non_api_route_falls_through_to_index_html(client):
    r = client.get("/some/spa/route")
    assert r.status_code == 200
    assert "<div id=root>" in r.text
```

- [ ] **Step 3: Run, expect fail**

Run: `/Users/soural/Documents/TLX/tlx/.venv/bin/python -m pytest tools/taintview/tests/test_server.py -v -k spa`
Expected: 404 on `/`.

- [ ] **Step 4: Implement static mount**

At top of `bin/taintview_server.py` add:
```python
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
```

Change `build_app` signature to accept the dist path:
```python
def build_app(*, targets_root: Path, spa_dist: Path | None = None) -> FastAPI:
    app = FastAPI(title="taintview")
    app.state.targets_root = targets_root
    if spa_dist is None:
        spa_dist = Path(__file__).resolve().parent.parent / "tools" / "taintview" / "dist"
    app.state.spa_dist = spa_dist

    # ... existing api routes here ...
```

After all `/api/*` routes are registered, add at the end of `build_app`:
```python
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
```

Update `conftest.py` `client` fixture to pass through `spa_dist`:
```python
@pytest.fixture
def client(targets_root: Path) -> TestClient:
    spa_dist = REPO_ROOT / "tools" / "taintview" / "dist"
    app = build_app(targets_root=targets_root, spa_dist=spa_dist)
    return TestClient(app)
```

- [ ] **Step 5: Run all tests, expect pass**

Run: `/Users/soural/Documents/TLX/tlx/.venv/bin/python -m pytest tools/taintview/tests/test_server.py -v`
Expected: 13 passed.

- [ ] **Step 6: Commit**

```bash
git add bin/taintview_server.py tools/taintview/tests/conftest.py tools/taintview/tests/test_server.py tools/taintview/dist/index.html
git commit -m "taintview: serve SPA from tools/taintview/dist with catchall"
```

---

## Task 9: SPA scaffold

**Files:**
- Create: `tools/taintview/package.json`
- Create: `tools/taintview/vite.config.ts`
- Create: `tools/taintview/tsconfig.json`
- Create: `tools/taintview/tsconfig.node.json`
- Create: `tools/taintview/tailwind.config.ts`
- Create: `tools/taintview/postcss.config.js`
- Create: `tools/taintview/index.html`
- Create: `tools/taintview/src/main.tsx`
- Create: `tools/taintview/src/App.tsx`
- Create: `tools/taintview/src/index.css`
- Create: `tools/taintview/src/vite-env.d.ts`
- Create: `tools/taintview/.gitignore`

- [ ] **Step 1: package.json**

Create `tools/taintview/package.json`:
```json
{
  "name": "taintview",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "dependencies": {
    "cytoscape": "^3.30.0",
    "cytoscape-cose-bilkent": "^4.1.0",
    "cytoscape-dagre": "^2.5.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-markdown": "^9.0.1"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.4.6",
    "@testing-library/react": "^16.0.0",
    "@types/cytoscape": "^3.21.4",
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "autoprefixer": "^10.4.19",
    "happy-dom": "^14.12.3",
    "postcss": "^8.4.39",
    "tailwindcss": "^3.4.4",
    "typescript": "^5.5.3",
    "vite": "^5.3.3",
    "vitest": "^2.0.2"
  }
}
```

- [ ] **Step 2: tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "useDefineForClassFields": true,
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "types": ["vitest/globals"]
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

- [ ] **Step 3: tsconfig.node.json**

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true,
    "strict": true
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **Step 4: vite.config.ts**

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "./",
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
  test: {
    environment: "happy-dom",
    globals: true,
  },
});
```

- [ ] **Step 5: tailwind.config.ts**

```ts
import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        src: "#dc2626",
        sink: "#9f1239",
        hop: "#475569",
      },
    },
  },
  plugins: [],
} satisfies Config;
```

- [ ] **Step 6: postcss.config.js**

```js
export default {
  plugins: { tailwindcss: {}, autoprefixer: {} },
};
```

- [ ] **Step 7: index.html**

```html
<!doctype html>
<html lang="en" class="dark">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>taintview</title>
  </head>
  <body class="bg-zinc-950 text-zinc-100">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 8: src/index.css**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

html,
body,
#root {
  height: 100%;
  margin: 0;
}
```

- [ ] **Step 9: src/main.tsx**

```tsx
import React from "react";
import ReactDOM from "react-dom/client";
import { App } from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
```

- [ ] **Step 10: src/App.tsx**

```tsx
export function App() {
  return <div className="p-4">taintview boot ok</div>;
}
```

- [ ] **Step 11: src/vite-env.d.ts**

```ts
/// <reference types="vite/client" />
```

- [ ] **Step 12: tools/taintview/.gitignore**

```
node_modules/
.vite/
*.tsbuildinfo
```

Note: `dist/` is checked in deliberately (see spec). Do not add it to gitignore.

- [ ] **Step 13: Install + build**

```bash
cd /Users/soural/Documents/TLX/tools/taintview
npm install
npm run build
```
Expected: `dist/index.html` and `dist/assets/*.js` produced.

- [ ] **Step 14: Smoke the sidecar serves the new dist**

```bash
cd /Users/soural/Documents/TLX
/Users/soural/Documents/TLX/tlx/.venv/bin/python -m pytest tools/taintview/tests/test_server.py -v
```
Expected: all green. The placeholder `dist/index.html` is overwritten by the real build, but the catchall test only asserts `200` and that the body contains `<div id="root"`. Adjust assertion if needed:

If `test_root_serves_spa_index_html` or `test_unknown_non_api_route_falls_through_to_index_html` now fail because the real built `index.html` doesn't contain the exact placeholder string, relax both assertions to:
```python
    assert 'id="root"' in r.text
```

- [ ] **Step 15: Commit**

```bash
git add tools/taintview/package.json tools/taintview/package-lock.json tools/taintview/vite.config.ts tools/taintview/tsconfig.json tools/taintview/tsconfig.node.json tools/taintview/tailwind.config.ts tools/taintview/postcss.config.js tools/taintview/index.html tools/taintview/src/ tools/taintview/.gitignore tools/taintview/dist/
git commit -m "taintview: scaffold Vite+React+TS+Tailwind SPA"
```

---

## Task 10: SPA — chain → graph model (TDD)

**Files:**
- Create: `tools/taintview/src/state/chains.ts`
- Create: `tools/taintview/src/__tests__/chains.test.ts`

- [ ] **Step 1: Write failing test**

`tools/taintview/src/__tests__/chains.test.ts`:
```ts
import { describe, expect, it } from "vitest";
import { buildGraphModel, type Chain } from "../state/chains";

const c = (id: number, path: string[]): Chain => ({
  id,
  source: { qname: path[0], file: "f.js", line: 1, taxonomy_id: "url_query" },
  sink: { qname: path[path.length - 1], file: "g.js", line: 2, taxonomy_id: "dom_innerHTML" },
  depth: path.length - 1,
  path,
  score: 80,
  scoring: {},
  variants: [],
  is_hot: true,
  reach: "unknown",
});

describe("buildGraphModel", () => {
  it("dedupes nodes across chains and tags source/sink/hop roles", () => {
    const chains = [c(1, ["A", "M", "Z"]), c(2, ["B", "M", "Z"])];
    const g = buildGraphModel(chains);
    expect(new Set(g.nodes.map((n) => n.id))).toEqual(new Set(["A", "B", "M", "Z"]));
    const role = (id: string) => g.nodes.find((n) => n.id === id)!.role;
    expect(role("A")).toBe("source");
    expect(role("B")).toBe("source");
    expect(role("M")).toBe("hop");
    expect(role("Z")).toBe("sink");
  });

  it("marks a node both when it is source in one chain and sink in another", () => {
    const chains = [c(1, ["A", "B"]), c(2, ["B", "C"])];
    const g = buildGraphModel(chains);
    const role = (id: string) => g.nodes.find((n) => n.id === id)!.role;
    expect(role("B")).toBe("both");
  });

  it("aggregates edge weights as count of chains that traverse the edge", () => {
    const chains = [c(1, ["A", "M", "Z"]), c(2, ["B", "M", "Z"]), c(3, ["C", "M", "Z"])];
    const g = buildGraphModel(chains);
    const mz = g.edges.find((e) => e.source === "M" && e.target === "Z")!;
    expect(mz.weight).toBe(3);
    expect(new Set(mz.chainIds)).toEqual(new Set([1, 2, 3]));
  });
});
```

- [ ] **Step 2: Run, expect fail**

```bash
cd /Users/soural/Documents/TLX/tools/taintview
npm test -- chains
```
Expected: import error on `../state/chains`.

- [ ] **Step 3: Implement**

`tools/taintview/src/state/chains.ts`:
```ts
export type TaintEnd = {
  qname: string;
  file: string;
  line: number;
  taxonomy_id: string;
};

export type Chain = {
  id: number;
  source: TaintEnd;
  sink: TaintEnd;
  depth: number;
  path: string[];
  score: number;
  scoring: Record<string, unknown>;
  variants: unknown[];
  is_hot: boolean;
  reach: "reachable" | "unreachable" | "unknown";
};

export type GraphNode = {
  id: string;
  role: "source" | "sink" | "hop" | "both";
  chainCount: number;
};

export type GraphEdge = {
  id: string;
  source: string;
  target: string;
  weight: number;
  chainIds: number[];
};

export type GraphModel = {
  nodes: GraphNode[];
  edges: GraphEdge[];
};

export function buildGraphModel(chains: Chain[]): GraphModel {
  const isSource = new Set<string>();
  const isSink = new Set<string>();
  const isHop = new Set<string>();
  const chainsByNode = new Map<string, Set<number>>();
  const edgeMap = new Map<string, { source: string; target: string; chainIds: Set<number> }>();

  for (const ch of chains) {
    if (ch.path.length === 0) continue;
    const src = ch.path[0];
    const sink = ch.path[ch.path.length - 1];
    isSource.add(src);
    isSink.add(sink);
    for (let i = 1; i < ch.path.length - 1; i++) isHop.add(ch.path[i]);
    for (const node of ch.path) {
      if (!chainsByNode.has(node)) chainsByNode.set(node, new Set());
      chainsByNode.get(node)!.add(ch.id);
    }
    for (let i = 0; i < ch.path.length - 1; i++) {
      const a = ch.path[i];
      const b = ch.path[i + 1];
      const key = `${a}>>${b}`;
      if (!edgeMap.has(key)) edgeMap.set(key, { source: a, target: b, chainIds: new Set() });
      edgeMap.get(key)!.chainIds.add(ch.id);
    }
  }

  const allIds = new Set<string>([...isSource, ...isSink, ...isHop]);
  const nodes: GraphNode[] = [...allIds].map((id) => {
    const src = isSource.has(id);
    const snk = isSink.has(id);
    let role: GraphNode["role"];
    if (src && snk) role = "both";
    else if (src) role = "source";
    else if (snk) role = "sink";
    else role = "hop";
    return { id, role, chainCount: chainsByNode.get(id)?.size ?? 0 };
  });

  const edges: GraphEdge[] = [...edgeMap.entries()].map(([key, e]) => ({
    id: key,
    source: e.source,
    target: e.target,
    chainIds: [...e.chainIds],
    weight: e.chainIds.size,
  }));

  return { nodes, edges };
}
```

- [ ] **Step 4: Run, expect pass**

```bash
cd /Users/soural/Documents/TLX/tools/taintview
npm test -- chains
```
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/taintview/src/state/chains.ts tools/taintview/src/__tests__/chains.test.ts
git commit -m "taintview: chain->graph model derivation (deduped nodes, weighted edges)"
```

---

## Task 11: SPA — filter predicate (TDD)

**Files:**
- Create: `tools/taintview/src/state/filters.ts`
- Create: `tools/taintview/src/__tests__/filters.test.ts`

- [ ] **Step 1: Failing test**

```ts
import { describe, expect, it } from "vitest";
import { applyFilters, type FilterState } from "../state/filters";
import type { Chain } from "../state/chains";

const c = (overrides: Partial<Chain> = {}): Chain => ({
  id: 1,
  source: { qname: "a.js::s", file: "a.js", line: 1, taxonomy_id: "url_query" },
  sink: { qname: "b.js::k", file: "b.js", line: 2, taxonomy_id: "dom_innerHTML" },
  depth: 1,
  path: ["a.js::s", "b.js::k"],
  score: 80,
  scoring: {},
  variants: [],
  is_hot: false,
  reach: "unknown",
  ...overrides,
});

const base: FilterState = {
  sourceTaxonomies: new Set(),
  sinkTaxonomies: new Set(),
  files: new Set(),
  scoreMin: 0,
  depthMax: 99,
  verdicts: new Set(["tp", "fp", "undet", "none"]),
};

describe("applyFilters", () => {
  it("returns all chains when filters are wide open", () => {
    const xs = [c({ id: 1 }), c({ id: 2, score: 30 })];
    expect(applyFilters(xs, base, {})).toHaveLength(2);
  });

  it("filters by sourceTaxonomies (empty set = no filter)", () => {
    const xs = [
      c({ id: 1, source: { qname: "a", file: "a", line: 1, taxonomy_id: "url_query" } }),
      c({ id: 2, source: { qname: "a", file: "a", line: 1, taxonomy_id: "JSON_parse_call" } }),
    ];
    const out = applyFilters(xs, { ...base, sourceTaxonomies: new Set(["url_query"]) }, {});
    expect(out.map((c) => c.id)).toEqual([1]);
  });

  it("filters by scoreMin and depthMax", () => {
    const xs = [c({ id: 1, score: 50, depth: 2 }), c({ id: 2, score: 90, depth: 6 })];
    const out = applyFilters(xs, { ...base, scoreMin: 70, depthMax: 5 }, {});
    expect(out).toHaveLength(0);
  });

  it("filters by verdict using the verdicts map", () => {
    const xs = [c({ id: 1 }), c({ id: 2 })];
    const out = applyFilters(
      xs,
      { ...base, verdicts: new Set(["tp"]) },
      { 1: { verdict: "tp" }, 2: { verdict: "fp" } },
    );
    expect(out.map((c) => c.id)).toEqual([1]);
  });

  it("treats unrecorded chains as verdict 'none'", () => {
    const xs = [c({ id: 1 }), c({ id: 2 })];
    const out = applyFilters(xs, { ...base, verdicts: new Set(["none"]) }, { 1: { verdict: "fp" } });
    expect(out.map((c) => c.id)).toEqual([2]);
  });
});
```

- [ ] **Step 2: Run, expect fail**

```bash
cd /Users/soural/Documents/TLX/tools/taintview
npm test -- filters
```

- [ ] **Step 3: Implement**

`tools/taintview/src/state/filters.ts`:
```ts
import type { Chain } from "./chains";

export type Verdict = "tp" | "fp" | "undet" | "none";

export type VerdictRecord = { verdict: Exclude<Verdict, "none">; note?: string; ts?: string };

export type FilterState = {
  sourceTaxonomies: Set<string>;
  sinkTaxonomies: Set<string>;
  files: Set<string>;
  scoreMin: number;
  depthMax: number;
  verdicts: Set<Verdict>;
};

export function applyFilters(
  chains: Chain[],
  f: FilterState,
  verdictByChain: Record<number, { verdict: Exclude<Verdict, "none"> }>,
): Chain[] {
  return chains.filter((c) => {
    if (c.score < f.scoreMin) return false;
    if (c.depth > f.depthMax) return false;
    if (f.sourceTaxonomies.size > 0 && !f.sourceTaxonomies.has(c.source.taxonomy_id)) return false;
    if (f.sinkTaxonomies.size > 0 && !f.sinkTaxonomies.has(c.sink.taxonomy_id)) return false;
    if (f.files.size > 0 && !(f.files.has(c.source.file) || f.files.has(c.sink.file))) return false;
    const recorded = verdictByChain[c.id]?.verdict;
    const v: Verdict = recorded ?? "none";
    if (!f.verdicts.has(v)) return false;
    return true;
  });
}
```

- [ ] **Step 4: Run, expect pass (5)**

- [ ] **Step 5: Commit**

```bash
git add tools/taintview/src/state/filters.ts tools/taintview/src/__tests__/filters.test.ts
git commit -m "taintview: pure filter predicate over chains"
```

---

## Task 12: SPA — path-pulse animation (TDD)

**Files:**
- Create: `tools/taintview/src/util/animate.ts`
- Create: `tools/taintview/src/__tests__/animate.test.ts`

- [ ] **Step 1: Failing test**

```ts
import { describe, expect, it, vi } from "vitest";
import { pulsePath } from "../util/animate";

describe("pulsePath", () => {
  it("calls visit(node) and visit(edge) in chronological order", async () => {
    const visits: string[] = [];
    const visit = vi.fn((id: string) => visits.push(id));
    await pulsePath(["A", "B", "C"], visit, { stepMs: 1 });
    expect(visits).toEqual(["A", "A>>B", "B", "B>>C", "C"]);
  });

  it("returns immediately on empty or single-node paths", async () => {
    const visit = vi.fn();
    await pulsePath([], visit, { stepMs: 1 });
    await pulsePath(["solo"], visit, { stepMs: 1 });
    expect(visit).not.toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: Run, expect fail**

- [ ] **Step 3: Implement**

`tools/taintview/src/util/animate.ts`:
```ts
export type Visitor = (id: string) => void;

export async function pulsePath(
  path: string[],
  visit: Visitor,
  opts: { stepMs?: number } = {},
): Promise<void> {
  if (path.length < 2) return;
  const step = opts.stepMs ?? 250;
  const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < path.length; i++) {
    visit(path[i]);
    if (i < path.length - 1) {
      await sleep(step);
      visit(`${path[i]}>>${path[i + 1]}`);
      await sleep(step);
    }
  }
}
```

- [ ] **Step 4: Run, expect 2 pass**

- [ ] **Step 5: Commit**

```bash
git add tools/taintview/src/util/animate.ts tools/taintview/src/__tests__/animate.test.ts
git commit -m "taintview: path-pulse animation helper"
```

---

## Task 13: SPA — typed API client

**Files:**
- Create: `tools/taintview/src/api.ts`

- [ ] **Step 1: Implement (no tests; thin fetch wrappers)**

`tools/taintview/src/api.ts`:
```ts
import type { Chain } from "./state/chains";
import type { Verdict, VerdictRecord } from "./state/filters";

const base = ""; // same-origin

async function getJson<T>(url: string): Promise<T> {
  const r = await fetch(base + url);
  if (!r.ok) throw new Error(`${r.status} ${r.statusText} on ${url}`);
  return (await r.json()) as T;
}

export async function listTargets(): Promise<string[]> {
  const { targets } = await getJson<{ targets: string[] }>("/api/targets");
  return targets;
}

export async function getChains(name: string): Promise<Chain[]> {
  const { chains } = await getJson<{ chains: Chain[] }>(`/api/target/${encodeURIComponent(name)}/chains`);
  return chains;
}

export async function getOpus(name: string, chainId: number): Promise<string | null> {
  const r = await fetch(`/api/target/${encodeURIComponent(name)}/opus/${chainId}`);
  if (r.status === 404) return null;
  if (!r.ok) throw new Error(`${r.status} on opus/${chainId}`);
  const body = (await r.json()) as { markdown: string };
  return body.markdown;
}

export type SnippetPayload = {
  qname: string;
  file: string;
  line: number;
  end_line: number;
  start: number;
  end: number;
  source: string;
};

export async function getSnippet(name: string, qname: string): Promise<SnippetPayload | { error: string }> {
  const r = await fetch(`/api/target/${encodeURIComponent(name)}/snippet?qname=${encodeURIComponent(qname)}`);
  if (r.status === 404) return { error: (await r.json()).detail };
  if (!r.ok) throw new Error(`${r.status} on snippet`);
  return (await r.json()) as SnippetPayload;
}

export async function getVerdicts(name: string): Promise<Record<string, VerdictRecord>> {
  const { verdicts } = await getJson<{ verdicts: Record<string, VerdictRecord> }>(
    `/api/target/${encodeURIComponent(name)}/verdicts`,
  );
  return verdicts;
}

export async function postVerdict(
  name: string,
  chainId: number,
  verdict: Exclude<Verdict, "none">,
  note: string,
): Promise<VerdictRecord> {
  const r = await fetch(`/api/target/${encodeURIComponent(name)}/verdict/${chainId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ verdict, note }),
  });
  if (!r.ok) throw new Error(`${r.status} on verdict POST`);
  return (await r.json()) as VerdictRecord;
}
```

- [ ] **Step 2: Commit**

```bash
git add tools/taintview/src/api.ts
git commit -m "taintview: typed API client"
```

---

## Task 14: SPA — ChainTable component

**Files:**
- Create: `tools/taintview/src/components/ChainTable.tsx`

- [ ] **Step 1: Implement**

```tsx
import type { Chain } from "../state/chains";
import type { Verdict, VerdictRecord } from "../state/filters";

type Props = {
  chains: Chain[];
  selectedId: number | null;
  verdictByChain: Record<string, VerdictRecord>;
  onSelect: (id: number) => void;
  onAnimate: (id: number) => void;
};

function verdictLabel(v: VerdictRecord | undefined): Verdict {
  return v?.verdict ?? "none";
}

export function ChainTable({ chains, selectedId, verdictByChain, onSelect, onAnimate }: Props) {
  return (
    <div className="h-full overflow-auto text-xs font-mono">
      <table className="w-full border-collapse">
        <thead className="sticky top-0 bg-zinc-900 text-zinc-300">
          <tr>
            <th className="text-left px-2 py-1">id</th>
            <th className="text-left px-2 py-1">src tax</th>
            <th className="text-left px-2 py-1">sink tax</th>
            <th className="text-right px-2 py-1">depth</th>
            <th className="text-right px-2 py-1">score</th>
            <th className="text-left px-2 py-1">verdict</th>
            <th className="text-left px-2 py-1">reach</th>
            <th className="text-left px-2 py-1">hot</th>
          </tr>
        </thead>
        <tbody>
          {chains.map((c) => {
            const v = verdictLabel(verdictByChain[c.id]);
            const isSel = c.id === selectedId;
            return (
              <tr
                key={c.id}
                className={`cursor-pointer ${isSel ? "bg-zinc-800" : "hover:bg-zinc-900"}`}
                onClick={() => onSelect(c.id)}
                onDoubleClick={() => onAnimate(c.id)}
              >
                <td className="px-2 py-1">{c.id}</td>
                <td className="px-2 py-1">{c.source.taxonomy_id}</td>
                <td className="px-2 py-1">{c.sink.taxonomy_id}</td>
                <td className="px-2 py-1 text-right">{c.depth}</td>
                <td className="px-2 py-1 text-right">{c.score.toFixed(0)}</td>
                <td className="px-2 py-1">{v}</td>
                <td className="px-2 py-1">{c.reach}</td>
                <td className="px-2 py-1">{c.is_hot ? "yes" : ""}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add tools/taintview/src/components/ChainTable.tsx
git commit -m "taintview: ChainTable component"
```

---

## Task 15: SPA — FilterRail component

**Files:**
- Create: `tools/taintview/src/components/FilterRail.tsx`

- [ ] **Step 1: Implement**

```tsx
import type { Chain } from "../state/chains";
import type { FilterState, Verdict } from "../state/filters";

type Props = {
  chains: Chain[];
  filters: FilterState;
  setFilters: (f: FilterState) => void;
};

function uniq(xs: Iterable<string>): string[] {
  return [...new Set(xs)].sort();
}

function toggle<T>(set: Set<T>, v: T): Set<T> {
  const out = new Set(set);
  if (out.has(v)) out.delete(v);
  else out.add(v);
  return out;
}

export function FilterRail({ chains, filters, setFilters }: Props) {
  const srcTax = uniq(chains.map((c) => c.source.taxonomy_id));
  const sinkTax = uniq(chains.map((c) => c.sink.taxonomy_id));
  const verdicts: Verdict[] = ["tp", "fp", "undet", "none"];

  return (
    <aside className="h-full overflow-auto p-3 space-y-4 text-xs">
      <section>
        <h3 className="text-zinc-400 mb-1">source taxonomy</h3>
        {srcTax.map((t) => (
          <label key={t} className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={filters.sourceTaxonomies.size === 0 || filters.sourceTaxonomies.has(t)}
              onChange={() =>
                setFilters({ ...filters, sourceTaxonomies: toggle(filters.sourceTaxonomies, t) })
              }
            />
            <span>{t}</span>
          </label>
        ))}
      </section>

      <section>
        <h3 className="text-zinc-400 mb-1">sink taxonomy</h3>
        {sinkTax.map((t) => (
          <label key={t} className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={filters.sinkTaxonomies.size === 0 || filters.sinkTaxonomies.has(t)}
              onChange={() =>
                setFilters({ ...filters, sinkTaxonomies: toggle(filters.sinkTaxonomies, t) })
              }
            />
            <span>{t}</span>
          </label>
        ))}
      </section>

      <section>
        <h3 className="text-zinc-400 mb-1">score &gt;= {filters.scoreMin}</h3>
        <input
          type="range"
          min={0}
          max={100}
          value={filters.scoreMin}
          onChange={(e) => setFilters({ ...filters, scoreMin: Number(e.target.value) })}
          className="w-full"
        />
      </section>

      <section>
        <h3 className="text-zinc-400 mb-1">depth &lt;= {filters.depthMax}</h3>
        <input
          type="range"
          min={1}
          max={20}
          value={filters.depthMax}
          onChange={(e) => setFilters({ ...filters, depthMax: Number(e.target.value) })}
          className="w-full"
        />
      </section>

      <section>
        <h3 className="text-zinc-400 mb-1">verdict</h3>
        {verdicts.map((v) => (
          <label key={v} className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={filters.verdicts.has(v)}
              onChange={() => setFilters({ ...filters, verdicts: toggle(filters.verdicts, v) })}
            />
            <span>{v}</span>
          </label>
        ))}
      </section>
    </aside>
  );
}
```

Note: the "empty set = no filter" semantic means the checkbox shows checked when the set is empty. Clicking it adds the taxonomy to the explicit-include set; clicking again removes it.

- [ ] **Step 2: Commit**

```bash
git add tools/taintview/src/components/FilterRail.tsx
git commit -m "taintview: FilterRail component"
```

---

## Task 16: SPA — SnippetView, OpusView, VerdictEditor

**Files:**
- Create: `tools/taintview/src/components/SnippetView.tsx`
- Create: `tools/taintview/src/components/OpusView.tsx`
- Create: `tools/taintview/src/components/VerdictEditor.tsx`

- [ ] **Step 1: SnippetView**

```tsx
import { useEffect, useState } from "react";
import { getSnippet, type SnippetPayload } from "../api";

type Props = { target: string; qname: string };

export function SnippetView({ target, qname }: Props) {
  const [state, setState] = useState<"loading" | { ok: SnippetPayload } | { err: string }>("loading");

  useEffect(() => {
    setState("loading");
    getSnippet(target, qname).then((r) => {
      if ("error" in r) setState({ err: r.error });
      else setState({ ok: r });
    }, (e) => setState({ err: String(e) }));
  }, [target, qname]);

  if (state === "loading") return <pre className="text-zinc-500">loading snippet…</pre>;
  if ("err" in state) return <pre className="text-amber-400">snippet unavailable: {state.err}</pre>;

  const { source, start, line, end_line, file } = state.ok;
  const lines = source.split("\n");
  return (
    <div className="text-xs font-mono">
      <div className="text-zinc-400 mb-1">{file} lines {start}–{start + lines.length - 1}</div>
      <pre className="bg-zinc-900 p-2 rounded overflow-auto">
        {lines.map((l, i) => {
          const lineNo = start + i;
          const isHi = lineNo >= line && lineNo <= end_line;
          return (
            <div key={lineNo} className={isHi ? "bg-amber-900/40" : ""}>
              <span className="text-zinc-500 select-none mr-3">{lineNo.toString().padStart(4)}</span>
              {l}
            </div>
          );
        })}
      </pre>
    </div>
  );
}
```

- [ ] **Step 2: OpusView**

```tsx
import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { getOpus } from "../api";

type Props = { target: string; chainId: number };

export function OpusView({ target, chainId }: Props) {
  const [md, setMd] = useState<string | null | "loading">("loading");
  useEffect(() => {
    setMd("loading");
    getOpus(target, chainId).then(setMd, () => setMd(null));
  }, [target, chainId]);
  if (md === "loading") return <div className="text-zinc-500 text-xs">loading opus…</div>;
  if (md === null) return <div className="text-zinc-500 text-xs">no opus writeup</div>;
  return (
    <div className="prose prose-invert prose-sm max-w-none">
      <ReactMarkdown>{md}</ReactMarkdown>
    </div>
  );
}
```

- [ ] **Step 3: VerdictEditor**

```tsx
import { useState } from "react";
import { postVerdict } from "../api";
import type { Verdict, VerdictRecord } from "../state/filters";

type Props = {
  target: string;
  chainId: number;
  current: VerdictRecord | undefined;
  onSaved: (rec: VerdictRecord) => void;
};

const choices: Exclude<Verdict, "none">[] = ["tp", "fp", "undet"];

export function VerdictEditor({ target, chainId, current, onSaved }: Props) {
  const [verdict, setVerdict] = useState<Exclude<Verdict, "none">>(current?.verdict ?? "undet");
  const [note, setNote] = useState(current?.note ?? "");
  const [busy, setBusy] = useState(false);

  async function save() {
    setBusy(true);
    try {
      const rec = await postVerdict(target, chainId, verdict, note);
      onSaved(rec);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-2 text-xs">
      <div className="flex gap-2">
        {choices.map((c) => (
          <label key={c} className="flex items-center gap-1">
            <input
              type="radio"
              checked={verdict === c}
              onChange={() => setVerdict(c)}
            />
            {c}
          </label>
        ))}
      </div>
      <textarea
        value={note}
        onChange={(e) => setNote(e.target.value)}
        className="w-full h-20 bg-zinc-900 p-2 rounded font-mono"
        placeholder="note…"
      />
      <button
        disabled={busy}
        onClick={save}
        className="px-3 py-1 bg-zinc-800 hover:bg-zinc-700 rounded disabled:opacity-50"
      >
        {busy ? "saving…" : "save verdict"}
      </button>
    </div>
  );
}
```

- [ ] **Step 4: Commit**

```bash
git add tools/taintview/src/components/SnippetView.tsx tools/taintview/src/components/OpusView.tsx tools/taintview/src/components/VerdictEditor.tsx
git commit -m "taintview: SnippetView, OpusView, VerdictEditor components"
```

---

## Task 17: SPA — NodeDetail right rail

**Files:**
- Create: `tools/taintview/src/components/NodeDetail.tsx`

- [ ] **Step 1: Implement**

```tsx
import type { Chain } from "../state/chains";
import type { VerdictRecord } from "../state/filters";
import { OpusView } from "./OpusView";
import { SnippetView } from "./SnippetView";
import { VerdictEditor } from "./VerdictEditor";

type Props = {
  target: string;
  selectedChain: Chain | null;
  selectedQname: string | null;
  verdict: VerdictRecord | undefined;
  onVerdictSaved: (rec: VerdictRecord) => void;
};

export function NodeDetail({ target, selectedChain, selectedQname, verdict, onVerdictSaved }: Props) {
  if (!selectedChain && !selectedQname) {
    return <div className="p-3 text-zinc-500 text-xs">select a chain or node</div>;
  }
  const qname = selectedQname ?? selectedChain?.sink.qname ?? null;
  return (
    <div className="h-full overflow-auto p-3 space-y-4">
      {qname && (
        <section>
          <h3 className="text-zinc-400 text-xs mb-1">node</h3>
          <div className="font-mono text-xs break-all">{qname}</div>
        </section>
      )}
      {qname && (
        <section>
          <h3 className="text-zinc-400 text-xs mb-1">snippet</h3>
          <SnippetView target={target} qname={qname} />
        </section>
      )}
      {selectedChain && (
        <section>
          <h3 className="text-zinc-400 text-xs mb-1">opus verdict</h3>
          <OpusView target={target} chainId={selectedChain.id} />
        </section>
      )}
      {selectedChain && (
        <section>
          <h3 className="text-zinc-400 text-xs mb-1">manual verdict</h3>
          <VerdictEditor
            target={target}
            chainId={selectedChain.id}
            current={verdict}
            onSaved={onVerdictSaved}
          />
        </section>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add tools/taintview/src/components/NodeDetail.tsx
git commit -m "taintview: NodeDetail right-rail composition"
```

---

## Task 18: SPA — Graph (Cytoscape) component

**Files:**
- Create: `tools/taintview/src/components/Graph.tsx`

- [ ] **Step 1: Implement**

```tsx
import { useEffect, useRef } from "react";
import cytoscape, { type Core, type ElementDefinition } from "cytoscape";
import coseBilkent from "cytoscape-cose-bilkent";
import dagre from "cytoscape-dagre";
import type { GraphModel } from "../state/chains";

cytoscape.use(coseBilkent);
cytoscape.use(dagre);

type Props = {
  model: GraphModel;
  layout: "cose-bilkent" | "dagre";
  highlightedNodes: Set<string>;
  highlightedEdges: Set<string>;
  onNodeClick: (qname: string) => void;
  registerPulser: (visit: (id: string) => void) => void;
};

export function Graph({
  model,
  layout,
  highlightedNodes,
  highlightedEdges,
  onNodeClick,
  registerPulser,
}: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const cyRef = useRef<Core | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    const elements: ElementDefinition[] = [
      ...model.nodes.map((n) => ({
        data: { id: n.id, role: n.role, count: n.chainCount, label: n.id.split("::").slice(-1)[0] },
      })),
      ...model.edges.map((e) => ({
        data: { id: e.id, source: e.source, target: e.target, weight: e.weight },
      })),
    ];
    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        {
          selector: "node",
          style: {
            label: "data(label)",
            "background-color": "#475569",
            color: "#e5e7eb",
            "font-size": 10,
            "text-valign": "bottom",
            "text-margin-y": 4,
            width: "mapData(count, 1, 50, 12, 56)" as unknown as number,
            height: "mapData(count, 1, 50, 12, 56)" as unknown as number,
          },
        },
        { selector: "node[role = 'source']", style: { "background-color": "#dc2626" } },
        { selector: "node[role = 'sink']", style: { "background-color": "#9f1239" } },
        { selector: "node[role = 'both']", style: { "background-color": "#f97316" } },
        {
          selector: "edge",
          style: {
            "curve-style": "bezier",
            "target-arrow-shape": "triangle",
            "line-color": "#3f3f46",
            "target-arrow-color": "#3f3f46",
            width: "mapData(weight, 1, 20, 1, 6)" as unknown as number,
            opacity: 0.7,
          },
        },
        { selector: ".dim", style: { opacity: 0.1 } },
        { selector: ".hi", style: { opacity: 1, "line-color": "#fbbf24", "target-arrow-color": "#fbbf24" } },
        { selector: ".pulse", style: { "background-color": "#fbbf24", "line-color": "#fbbf24" } },
      ],
      layout: { name: layout, animate: false } as cytoscape.LayoutOptions,
      wheelSensitivity: 0.2,
    });
    cy.on("tap", "node", (evt) => onNodeClick(evt.target.id()));
    cyRef.current = cy;

    const pulse = (id: string) => {
      const ele = cy.getElementById(id);
      if (!ele.empty()) {
        ele.addClass("pulse");
        setTimeout(() => ele.removeClass("pulse"), 800);
      }
    };
    registerPulser(pulse);

    return () => {
      cy.destroy();
      cyRef.current = null;
    };
  }, [model, layout]);

  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;
    if (highlightedNodes.size === 0 && highlightedEdges.size === 0) {
      cy.elements().removeClass("dim").removeClass("hi");
      return;
    }
    cy.elements().addClass("dim").removeClass("hi");
    highlightedNodes.forEach((id) => cy.getElementById(id).removeClass("dim").addClass("hi"));
    highlightedEdges.forEach((id) => cy.getElementById(id).removeClass("dim").addClass("hi"));
  }, [highlightedNodes, highlightedEdges]);

  return <div ref={containerRef} className="w-full h-full bg-zinc-950" />;
}
```

- [ ] **Step 2: Commit**

```bash
git add tools/taintview/src/components/Graph.tsx
git commit -m "taintview: Cytoscape Graph component with cose-bilkent + dagre"
```

---

## Task 19: SPA — App composition + URL params + data load

**Files:**
- Modify: `tools/taintview/src/App.tsx`

- [ ] **Step 1: Replace App.tsx**

```tsx
import { useEffect, useMemo, useRef, useState } from "react";
import { getChains, getVerdicts } from "./api";
import { ChainTable } from "./components/ChainTable";
import { FilterRail } from "./components/FilterRail";
import { Graph } from "./components/Graph";
import { NodeDetail } from "./components/NodeDetail";
import { buildGraphModel, type Chain } from "./state/chains";
import { applyFilters, type FilterState, type VerdictRecord } from "./state/filters";
import { pulsePath } from "./util/animate";

const DEFAULT_FILTERS: FilterState = {
  sourceTaxonomies: new Set(),
  sinkTaxonomies: new Set(),
  files: new Set(),
  scoreMin: 70,
  depthMax: 20,
  verdicts: new Set(["tp", "fp", "undet", "none"]),
};

export function App() {
  const params = new URLSearchParams(window.location.search);
  const target = params.get("target") ?? "";
  const initialSelected = Number(params.get("selected") ?? "") || null;

  const [chains, setChains] = useState<Chain[]>([]);
  const [verdicts, setVerdicts] = useState<Record<string, VerdictRecord>>({});
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);
  const [selectedChainId, setSelectedChainId] = useState<number | null>(initialSelected);
  const [selectedQname, setSelectedQname] = useState<string | null>(null);
  const [layout, setLayout] = useState<"cose-bilkent" | "dagre">("cose-bilkent");
  const [highlightedNodes, setHighlightedNodes] = useState<Set<string>>(new Set());
  const [highlightedEdges, setHighlightedEdges] = useState<Set<string>>(new Set());
  const pulserRef = useRef<(id: string) => void>(() => {});

  useEffect(() => {
    if (!target) return;
    getChains(target).then(setChains).catch((e) => console.error(e));
    getVerdicts(target).then(setVerdicts).catch((e) => console.error(e));
  }, [target]);

  const verdictByChainNum = useMemo(() => {
    const out: Record<number, { verdict: "tp" | "fp" | "undet" }> = {};
    for (const [k, v] of Object.entries(verdicts)) out[Number(k)] = { verdict: v.verdict };
    return out;
  }, [verdicts]);

  const filteredChains = useMemo(
    () => applyFilters(chains, filters, verdictByChainNum),
    [chains, filters, verdictByChainNum],
  );

  const model = useMemo(() => buildGraphModel(filteredChains), [filteredChains]);

  const selectedChain = selectedChainId != null
    ? filteredChains.find((c) => c.id === selectedChainId) ?? null
    : null;

  useEffect(() => {
    if (!selectedChain) {
      setHighlightedNodes(new Set());
      setHighlightedEdges(new Set());
      return;
    }
    const nodes = new Set(selectedChain.path);
    const edges = new Set<string>();
    for (let i = 0; i < selectedChain.path.length - 1; i++) {
      edges.add(`${selectedChain.path[i]}>>${selectedChain.path[i + 1]}`);
    }
    setHighlightedNodes(nodes);
    setHighlightedEdges(edges);
  }, [selectedChain]);

  // Auto-animate on URL ?selected=<id>
  const autoAnimatedRef = useRef(false);
  useEffect(() => {
    if (autoAnimatedRef.current || initialSelected == null || filteredChains.length === 0) return;
    const ch = filteredChains.find((c) => c.id === initialSelected);
    if (!ch) return;
    autoAnimatedRef.current = true;
    pulsePath(ch.path, (id) => pulserRef.current(id)).catch(() => {});
  }, [filteredChains, initialSelected]);

  function animate(chainId: number) {
    const ch = filteredChains.find((c) => c.id === chainId);
    if (!ch) return;
    pulsePath(ch.path, (id) => pulserRef.current(id)).catch(() => {});
  }

  if (!target) {
    return <div className="p-4">missing ?target=&lt;name&gt; query param</div>;
  }

  return (
    <div className="grid h-screen" style={{ gridTemplateColumns: "240px 1fr 360px", gridTemplateRows: "40px 1fr 240px" }}>
      <header className="col-span-3 flex items-center px-3 gap-4 border-b border-zinc-800 text-sm">
        <span className="font-semibold">taintview</span>
        <span className="text-zinc-400">target: {target}</span>
        <span className="text-zinc-400">chains: {filteredChains.length}/{chains.length}</span>
        <button
          className="ml-auto text-xs px-2 py-1 bg-zinc-800 rounded"
          onClick={() => setLayout(layout === "cose-bilkent" ? "dagre" : "cose-bilkent")}
        >
          layout: {layout}
        </button>
      </header>
      <div className="border-r border-zinc-800 overflow-hidden">
        <FilterRail chains={chains} filters={filters} setFilters={setFilters} />
      </div>
      <main className="overflow-hidden">
        <Graph
          model={model}
          layout={layout}
          highlightedNodes={highlightedNodes}
          highlightedEdges={highlightedEdges}
          onNodeClick={setSelectedQname}
          registerPulser={(p) => (pulserRef.current = p)}
        />
      </main>
      <div className="border-l border-zinc-800 overflow-hidden">
        <NodeDetail
          target={target}
          selectedChain={selectedChain}
          selectedQname={selectedQname}
          verdict={selectedChainId != null ? verdicts[String(selectedChainId)] : undefined}
          onVerdictSaved={(rec) =>
            setVerdicts((prev) => ({ ...prev, [String(rec.chain_id)]: rec }))
          }
        />
      </div>
      <div className="col-span-3 border-t border-zinc-800 overflow-hidden">
        <ChainTable
          chains={filteredChains}
          selectedId={selectedChainId}
          verdictByChain={verdicts}
          onSelect={setSelectedChainId}
          onAnimate={animate}
        />
      </div>
    </div>
  );
}
```

Note: `VerdictRecord` shape from sidecar uses `chain_id` field on POST responses. Update the type in `src/state/filters.ts` if needed by adding the optional `chain_id?: number` field. Add it now:

In `tools/taintview/src/state/filters.ts`, change:
```ts
export type VerdictRecord = { verdict: Exclude<Verdict, "none">; note?: string; ts?: string };
```
to:
```ts
export type VerdictRecord = {
  verdict: Exclude<Verdict, "none">;
  note?: string;
  ts?: string;
  chain_id?: number;
};
```

- [ ] **Step 2: Build SPA**

```bash
cd /Users/soural/Documents/TLX/tools/taintview
npm run build
```
Expected: no TS errors. `dist/` updated.

- [ ] **Step 3: Run vitest suite to confirm pure-logic tests still pass**

```bash
cd /Users/soural/Documents/TLX/tools/taintview
npm test
```
Expected: 10 tests passed (3 chains + 5 filters + 2 animate).

- [ ] **Step 4: Re-run sidecar tests**

```bash
cd /Users/soural/Documents/TLX
/Users/soural/Documents/TLX/tlx/.venv/bin/python -m pytest tools/taintview/tests/test_server.py -v
```
Expected: 13 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/taintview/src/App.tsx tools/taintview/src/state/filters.ts tools/taintview/dist/
git commit -m "taintview: App composition with filter/graph/table/detail wiring"
```

---

## Task 20: CLI launcher

**Files:**
- Create: `bin/taintview.py`

- [ ] **Step 1: Implement**

```python
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
```

- [ ] **Step 2: Make executable**

```bash
chmod +x /Users/soural/Documents/TLX/bin/taintview.py
```

- [ ] **Step 3: Commit**

```bash
git add bin/taintview.py
git commit -m "taintview: CLI launcher"
```

---

## Task 21: End-to-end smoke against coralbug3-syn

- [ ] **Step 1: Start it**

```bash
cd /Users/soural/Documents/TLX
/Users/soural/Documents/TLX/tlx/.venv/bin/python bin/taintview.py coralbug3-syn --no-open &
sleep 2
curl -s http://127.0.0.1:8765/api/targets | head -c 200
echo
curl -s http://127.0.0.1:8765/api/target/coralbug3-syn/chains | python3 -c "import sys, json; d=json.load(sys.stdin); print('chains:', len(d['chains']))"
curl -s http://127.0.0.1:8765/api/target/coralbug3-syn/opus/103 | head -c 200
echo
curl -sI http://127.0.0.1:8765/ | head -3
kill %1
```
Expected:
- `/api/targets` lists `coralbug3-syn` among others.
- `/api/target/coralbug3-syn/chains` returns a non-empty `chains` array, each chain has `is_hot` and `reach` fields populated.
- `/api/target/coralbug3-syn/opus/103` returns markdown (chain 103 exists per status.json).
- `/` returns 200 with HTML.

- [ ] **Step 2: Manually open in browser**

```bash
/Users/soural/Documents/TLX/tlx/.venv/bin/python bin/taintview.py coralbug3-syn
```
Verify in the browser:
- Filter rail lists taxonomies present in `coralbug3-syn` (`location_search`, `JSON_parse_call`, `angular_modern_bypassSecurityTrust`, `setTimeout_string`).
- Chain table shows 4 chains (matches `status.json.phases.triage.hot=4`), all marked `is_hot=yes`, `reach=unreachable`.
- Clicking a chain row highlights the path in the graph.
- Double-click animates the pulse from source to sink.
- Right rail loads opus markdown for the chain.
- "Show snippet" works for the chain's source qname.
- Saving a verdict creates `targets/coralbug3-syn/verdicts.jsonl` with one line; saving again appends.

- [ ] **Step 3: Commit any tweaks discovered during smoke**

If everything works without tweaks, do not create an empty commit. If you fix anything, commit with a message like:
```bash
git commit -am "taintview: smoke-test fixes for coralbug3-syn"
```

---

## Self-Review Notes

- **Spec coverage:**
  - Filters (source tax, sink tax, file, score, depth, verdict) → FilterRail (Task 15). Note: file-filter UI is not implemented in v1; the predicate supports it (Task 11) but no UI widget. Acceptable cut — bottom-table sort gives the same access. Document this in commit message.
  - Graph (sources red, sinks crimson, both striped, hops gray, size by chain count, edge weight) → Graph (Task 18). Note: spec says "both" is striped red/crimson; v1 paints it solid orange (`#f97316`) because Cytoscape striping requires SVG patterns. This is a deliberate simplification. Document in commit message.
  - Animate source→sink along path → animate.ts (Task 12) + pulser bridge (Task 18 + 19).
  - Right-rail node detail + snippet + opus + verdict → NodeDetail (Task 17).
  - Sidecar endpoints (targets, chains, opus, snippet, verdict POST+GET) → Tasks 2, 4, 5, 6, 7.
  - Static SPA mount + catchall → Task 8.
  - CLI launcher → Task 20.
  - Smoke test → Task 21.
  - Filter defaults to `score >= 70` on initial load → `DEFAULT_FILTERS.scoreMin = 70` in App.tsx (Task 19).
  - URL params `?target` and `?selected` → App.tsx (Task 19), auto-animate once on load.
  - Verdict last-write-wins on read → sidecar `/api/target/{name}/verdicts` (Task 7) + test asserts behavior.
- **No placeholders.** All steps contain complete code.
- **Type consistency.** `Verdict`, `VerdictRecord`, `FilterState`, `Chain`, `GraphNode`, `GraphEdge`, `GraphModel` defined once in `state/chains.ts` and `state/filters.ts`, imported everywhere consistently. The sidecar verdict response includes `chain_id` and `VerdictRecord` was extended in Task 19 to match.
- **Cut features documented:** file-filter UI; striped two-color "both" node coloring; multi-target merged view; "shortest path between two nodes" interaction (filter predicate supports it but no UI gesture wired in v1). These match the spec's non-goals or are explicitly tagged here as v1 cuts.
