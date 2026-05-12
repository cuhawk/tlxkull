import asyncio
from unittest.mock import AsyncMock, MagicMock
import pytest

from recon_mcp.droplet import Droplet, ProvisionError


@pytest.fixture
def fake_do():
    do = MagicMock()
    do.create_droplet = AsyncMock(return_value={"id": 111, "status": "new"})
    do.get_droplet = AsyncMock(side_effect=[
        {"id": 111, "status": "new",   "networks": {"v4": []}},
        {"id": 111, "status": "active","networks": {"v4": [{"type": "public", "ip_address": "9.9.9.9"}]}},
    ])
    do.destroy_droplet = AsyncMock()
    return do


@pytest.mark.asyncio
async def test_provision_waits_for_active(fake_do, monkeypatch):
    monkeypatch.setattr("asyncio.sleep", AsyncMock())
    d = Droplet(do=fake_do, name="t", region="nyc1", size="s-2vcpu-4gb",
                image="ubuntu-24-04-x64", ssh_key_ids=[1], user_data="x", tags=["t"])
    ip = await d._provision_and_wait(poll_interval=0)
    assert ip == "9.9.9.9"
    assert d.droplet_id == 111


@pytest.mark.asyncio
async def test_destroy_called_on_exception(fake_do, monkeypatch):
    monkeypatch.setattr("asyncio.sleep", AsyncMock())
    # Make _wait_bootstrap a no-op via monkeypatch so __aenter__ succeeds.
    from recon_mcp import droplet as _dm
    monkeypatch.setattr(_dm.Droplet, "_wait_bootstrap", AsyncMock())
    d = Droplet(do=fake_do, name="t", region="nyc1", size="s",
                image="i", ssh_key_ids=[1], user_data="x", tags=["t"])
    async def boom():
        async with d:
            raise RuntimeError("kaboom")
    with pytest.raises(RuntimeError):
        await boom()
    fake_do.destroy_droplet.assert_awaited_once_with(111)


@pytest.mark.asyncio
async def test_destroy_called_when_bootstrap_fails(fake_do, monkeypatch):
    monkeypatch.setattr("asyncio.sleep", AsyncMock())
    from recon_mcp import droplet as _dm
    monkeypatch.setattr(
        _dm.Droplet, "_wait_bootstrap",
        AsyncMock(side_effect=ProvisionError("bootstrap timeout")),
    )
    d = Droplet(do=fake_do, name="t", region="nyc1", size="s",
                image="i", ssh_key_ids=[1], user_data="x", tags=["t"])
    with pytest.raises(ProvisionError, match="bootstrap timeout"):
        async with d:
            pass
    fake_do.destroy_droplet.assert_awaited_once_with(111)


@pytest.mark.asyncio
async def test_provision_timeout(monkeypatch):
    do = MagicMock()
    do.create_droplet = AsyncMock(return_value={"id": 1, "status": "new"})
    do.get_droplet = AsyncMock(return_value={"id": 1, "status": "new", "networks": {"v4": []}})
    do.destroy_droplet = AsyncMock()
    monkeypatch.setattr("asyncio.sleep", AsyncMock())
    d = Droplet(do=do, name="t", region="nyc1", size="s", image="i",
                ssh_key_ids=[1], user_data="x", tags=["t"], max_wait_sec=0.01)
    with pytest.raises(ProvisionError, match="timeout"):
        await d._provision_and_wait(poll_interval=0)
