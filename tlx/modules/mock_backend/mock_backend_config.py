"""Configuration for the mock_backend module."""
from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel


class MockBackendConfig(BaseModel):
    db_path: str = "~/.tlx/mock_backend.db"
    workspace_dir: str = "~/.tlx/mock_backend"
    default_port: int = 0
    bind_host: str = "127.0.0.1"

    @property
    def db_path_resolved(self) -> Path:
        return Path(self.db_path).expanduser().resolve()

    @property
    def workspace_dir_resolved(self) -> Path:
        return Path(self.workspace_dir).expanduser().resolve()
