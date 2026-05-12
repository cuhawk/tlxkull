from unittest.mock import AsyncMock, MagicMock
import pytest
import pytest_asyncio
from recon_mcp.jobs import JobStore, JobStatus
from recon_mcp.handlers.cleanup import handle_cleanup_orphans


@pytest_asyncio.fixture
async def store(tmp_path):
    s = JobStore(db_path=str(tmp_path / "j.sqlite"))
    await s.init()
    return s


@pytest.mark.asyncio
async def test_destroys_droplets_for_unknown_or_finished_jobs(store):
    j_done = await store.create(target_spec={"t": 1}, regions=["nyc1"])
    await store.set_status(j_done, JobStatus.DONE)
    j_active = await store.create(target_spec={"t": 2}, regions=["nyc1"])
    await store.set_status(j_active, JobStatus.RUNNING)

    do = MagicMock()
    do.list_by_tag = AsyncMock(return_value=[
        {"id": 100, "tags": ["recon-mcp", f"job:{j_done}"]},
        {"id": 200, "tags": ["recon-mcp", f"job:{j_active}"]},
        {"id": 300, "tags": ["recon-mcp", "job:ghostid"]},
    ])
    do.destroy_droplet = AsyncMock()

    out = await handle_cleanup_orphans(store=store, do=do)
    assert set(out.destroyed) == {100, 300}
    do.destroy_droplet.assert_any_await(100)
    do.destroy_droplet.assert_any_await(300)
