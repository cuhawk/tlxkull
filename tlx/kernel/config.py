"""User config loaded from ~/.tlx/config.toml."""
from __future__ import annotations

import tomllib
from pathlib import Path

from pydantic import BaseModel, Field

from kernel.routing import RoutingConfig


class TlxConfig(BaseModel):
    default_engine: str = "gemini"
    default_model: str = "gemini-2.5-flash-lite"
    caveman_mode: str = "lite"
    compaction_threshold: int = 120000
    embedder: str = "google"
    modules: dict[str, dict] = Field(default_factory=dict)
    routing: RoutingConfig = RoutingConfig()


def _default_config_path() -> Path:
    return Path.home() / ".tlx" / "config.toml"


def load_config(path: Path | None = None) -> TlxConfig:
    cfg_path = path if path is not None else _default_config_path()
    if not cfg_path.is_file():
        return TlxConfig()
    with cfg_path.open("rb") as fh:
        data = tomllib.load(fh)
    return TlxConfig.model_validate(data)
