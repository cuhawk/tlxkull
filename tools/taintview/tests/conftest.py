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
