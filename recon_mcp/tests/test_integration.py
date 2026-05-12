import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from recon_mcp.config import Config
from recon_mcp.jobs import JobStore, JobStatus
from recon_mcp.handlers.start import handle_start
from recon_mcp.tools import ReconStartIn


@pytest.mark.asyncio
async def test_end_to_end_smoke(tmp_path, monkeypatch):
    db = tmp_path / "j.sqlite"
    ssh = tmp_path / "ssh"
    cfg = Config(
        do_api_token="t", shodan_api_key=None, c99_api_key=None,
        db_path=db, ssh_key_dir=ssh,
        max_droplets_per_job=5, max_runtime_min=30,
        default_scan_region="nyc1", droplet_size="s-2vcpu-4gb",
    )
    store = JobStore(db_path=str(db))
    await store.init()

    fake_droplet_info = {
        "id": 1, "status": "active",
        "networks": {"v4": [{"type": "public", "ip_address": "9.9.9.9"}]},
    }
    async def _fake_keypair(d, j):
        return (d / f"{j}.key", "ssh-ed25519 AAA== test")

    async def _fake_host_keypair():
        return (
            "-----BEGIN OPENSSH PRIVATE KEY-----\nAAAA\n-----END OPENSSH PRIVATE KEY-----\n",
            "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIH+nope nope",
        )

    monkeypatch.setattr("recon_mcp.handlers.start._gen_ssh_keypair", _fake_keypair)
    monkeypatch.setattr("recon_mcp.handlers.start._gen_host_keypair", _fake_host_keypair)
    monkeypatch.setattr(
        "recon_mcp.handlers.start.asyncssh.import_public_key", lambda s: object()
    )

    with patch("recon_mcp.handlers.start.DOClient") as DO, \
         patch("recon_mcp.handlers.start.Droplet") as DropCls, \
         patch("recon_mcp.handlers.start.push_scripts", new=AsyncMock()):
        do_inst = DO.return_value
        do_inst.create_ssh_key = AsyncMock(return_value={"id": 7})
        do_inst.delete_ssh_key = AsyncMock()
        do_inst.create_droplet = AsyncMock(return_value=fake_droplet_info)
        do_inst.get_droplet = AsyncMock(return_value=fake_droplet_info)
        do_inst.destroy_droplet = AsyncMock()

        drop_inst = DropCls.return_value
        drop_inst.droplet_id = 1
        drop_inst.region = "nyc1"
        drop_inst.__aenter__ = AsyncMock(return_value=drop_inst)
        drop_inst.__aexit__ = AsyncMock(return_value=None)
        drop_inst.run = AsyncMock(return_value=(0, "", ""))
        drop_inst.push = AsyncMock()
        drop_inst.pull = AsyncMock()

        out = await handle_start(
            ReconStartIn(targets=["1.2.3.4"], target_name="acme"),
            store=store, cfg=cfg, artifacts_root=tmp_path,
        )
        # Poll for completion (max 5s wall, 0.05s ticks)
        row = None
        for _ in range(100):
            await asyncio.sleep(0.05)
            row = await store.get(out.job_id)
            if row["status"] in (JobStatus.DONE, JobStatus.FAILED):
                break
        assert row is not None
        assert row["status"] == JobStatus.DONE, row.get("error")

        sm = tmp_path / "acme" / "recon" / out.job_id / "summary.json"
        assert sm.exists()
