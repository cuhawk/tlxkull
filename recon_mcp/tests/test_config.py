import os
import pytest
from recon_mcp.config import load_config, ConfigError


def test_loads_defaults_when_env_present(monkeypatch, tmp_path):
    monkeypatch.setenv("DO_API_TOKEN", "do_v1_xxx")
    monkeypatch.setenv("RECON_DB_PATH", str(tmp_path / "jobs.sqlite"))
    monkeypatch.setenv("RECON_SSH_KEY_DIR", str(tmp_path / "ssh"))
    cfg = load_config()
    assert cfg.do_api_token == "do_v1_xxx"
    assert cfg.max_droplets_per_job == 10
    assert cfg.max_runtime_min == 180
    assert cfg.default_scan_region == "nyc1"


def test_rejects_missing_do_token(monkeypatch):
    monkeypatch.delenv("DO_API_TOKEN", raising=False)
    with pytest.raises(ConfigError, match="DO_API_TOKEN"):
        load_config()


def test_overrides_from_env(monkeypatch, tmp_path):
    monkeypatch.setenv("DO_API_TOKEN", "x")
    monkeypatch.setenv("RECON_DB_PATH", str(tmp_path / "j.sqlite"))
    monkeypatch.setenv("RECON_SSH_KEY_DIR", str(tmp_path / "ssh"))
    monkeypatch.setenv("RECON_MAX_DROPLETS_PER_JOB", "25")
    monkeypatch.setenv("RECON_DROPLET_SIZE", "s-4vcpu-8gb")
    cfg = load_config()
    assert cfg.max_droplets_per_job == 25
    assert cfg.droplet_size == "s-4vcpu-8gb"
