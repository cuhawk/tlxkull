from unittest.mock import AsyncMock, MagicMock
import pytest
import pytest_asyncio
from recon_mcp.jobs import JobStore, JobStatus
from recon_mcp.handlers.cancel import handle_cancel
from recon_mcp.tools import ReconCancelIn


@pytest_asyncio.fixture
async def store(tmp_path):
    s = JobStore(db_path=str(tmp_path / "j.sqlite"))
    await s.init()
    return s


@pytest.mark.asyncio
async def test_cancel_destroys_attached_droplets(store):
    jid = await store.create(target_spec={"t": 1}, regions=["nyc1"])
    await store.attach_droplet(jid, droplet_id=11, region="nyc1")
    await store.attach_droplet(jid, droplet_id=22, region="fra1")
    do = MagicMock()
    do.destroy_droplet = AsyncMock()
    out = await handle_cancel(ReconCancelIn(job_id=jid), store=store, do=do)
    assert set(out.destroyed_droplets) == {11, 22}
    do.destroy_droplet.assert_any_await(11)
    do.destroy_droplet.assert_any_await(22)
    job = await store.get(jid)
    assert job["status"] == JobStatus.CANCELED
