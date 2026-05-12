from pathlib import Path
from unittest.mock import AsyncMock, patch
import pytest
import pytest_asyncio

from recon_mcp.tools import ReconStartIn
from recon_mcp.handlers.start import handle_start
from recon_mcp.jobs import JobStore, JobStatus


@pytest_asyncio.fixture
async def store(tmp_path):
    s = JobStore(db_path=str(tmp_path / "j.sqlite"))
    await s.init()
    return s


@pytest.fixture
def cfg(tmp_path):
    from recon_mcp.config import Config
    return Config(
        do_api_token="t", shodan_api_key=None, c99_api_key=None,
        db_path=tmp_path / "j.sqlite", ssh_key_dir=tmp_path / "ssh",
        max_droplets_per_job=10, max_runtime_min=180,
        default_scan_region="nyc1", droplet_size="s-2vcpu-4gb",
    )


@pytest.mark.asyncio
async def test_start_returns_job_id_and_plan(store, cfg, tmp_path):
    inp = ReconStartIn(targets=["1.2.3.4", "*.x.com"], target_name="acme")
    with patch("recon_mcp.handlers.start._run_job", new=AsyncMock()):
        out = await handle_start(inp, store=store, cfg=cfg, artifacts_root=tmp_path)
    assert out.job_id
    assert out.target_count == 2
    assert any(p["purpose"] == "scan" for p in out.droplet_plan)


@pytest.mark.asyncio
async def test_start_persists_pending_job(store, cfg, tmp_path):
    inp = ReconStartIn(targets=["1.2.3.4"], target_name="acme")
    with patch("recon_mcp.handlers.start._run_job", new=AsyncMock()):
        out = await handle_start(inp, store=store, cfg=cfg, artifacts_root=tmp_path)
    job = await store.get(out.job_id)
    assert job["status"] == JobStatus.PENDING


@pytest.mark.asyncio
async def test_start_rejects_huge_cidr(store, cfg, tmp_path):
    inp = ReconStartIn(targets=["10.0.0.0/8"], target_name="acme")
    with pytest.raises(Exception, match="too large"):
        await handle_start(inp, store=store, cfg=cfg, artifacts_root=tmp_path)


@pytest.mark.asyncio
async def test_start_with_probe_regions(store, cfg, tmp_path):
    inp = ReconStartIn(targets=["*.x.com"], target_name="x", probe_regions=["fra1", "sgp1"])
    with patch("recon_mcp.handlers.start._run_job", new=AsyncMock()):
        out = await handle_start(inp, store=store, cfg=cfg, artifacts_root=tmp_path)
    regions = {p["region"] for p in out.droplet_plan}
    assert {"nyc1", "fra1", "sgp1"}.issubset(regions)
