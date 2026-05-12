"""Env-driven config for recon-mcp."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class Config:
    do_api_token: str
    shodan_api_key: str | None
    c99_api_key: str | None
    db_path: Path
    ssh_key_dir: Path
    max_droplets_per_job: int
    max_runtime_min: int
    default_scan_region: str
    droplet_size: str


def load_config() -> Config:
    tok = os.environ.get("DO_API_TOKEN", "").strip()
    if not tok:
        raise ConfigError("DO_API_TOKEN not set")
    return Config(
        do_api_token=tok,
        shodan_api_key=(os.environ.get("SHODAN_API_KEY") or None),
        c99_api_key=(os.environ.get("C99_API_KEY") or None),
        db_path=Path(os.environ.get("RECON_DB_PATH", ".recon/jobs.sqlite")),
        ssh_key_dir=Path(os.environ.get("RECON_SSH_KEY_DIR", ".recon/ssh")),
        max_droplets_per_job=int(os.environ.get("RECON_MAX_DROPLETS_PER_JOB", "10")),
        max_runtime_min=int(os.environ.get("RECON_MAX_RUNTIME_MIN", "180")),
        default_scan_region=os.environ.get("RECON_DEFAULT_SCAN_REGION", "nyc1"),
        droplet_size=os.environ.get("RECON_DROPLET_SIZE", "s-2vcpu-4gb"),
    )
