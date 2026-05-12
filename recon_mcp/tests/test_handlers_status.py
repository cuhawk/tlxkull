import pytest
import pytest_asyncio
from recon_mcp.jobs import JobStore, JobStatus
from recon_mcp.handlers.status import handle_status
from recon_mcp.tools import ReconStatusIn


@pytest_asyncio.fixture
async def store(tmp_path):
    s = JobStore(db_path=str(tmp_path / "j.sqlite"))
    await s.init()
    return s


@pytest.mark.asyncio
async def test_status_returns_job(store):
    jid = await store.create(target_spec={"t": 1}, regions=["nyc1"])
    out = await handle_status(ReconStatusIn(job_id=jid), store=store)
    assert out.job_id == jid
    assert out.status == JobStatus.PENDING


@pytest.mark.asyncio
async def test_status_unknown_job(store):
    with pytest.raises(KeyError):
        await handle_status(ReconStatusIn(job_id="nope"), store=store)
