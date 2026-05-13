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
