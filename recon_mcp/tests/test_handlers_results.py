import json
from pathlib import Path
import pytest
import pytest_asyncio
from recon_mcp.jobs import JobStore, JobStatus
from recon_mcp.handlers.results import handle_results
from recon_mcp.tools import ReconResultsIn


@pytest_asyncio.fixture
async def store(tmp_path):
    s = JobStore(db_path=str(tmp_path / "j.sqlite"))
    await s.init()
    return s


@pytest.mark.asyncio
async def test_returns_summary_when_done(store, tmp_path):
    jid = await store.create(target_spec={"t": 1}, regions=["nyc1"], artifacts_dir=str(tmp_path))
    await store.set_status(jid, JobStatus.DONE)
    (tmp_path / "summary.json").write_text(json.dumps({"1.2.3.4": {"hosts": []}}))
    out = await handle_results(ReconResultsIn(job_id=jid), store=store)
    assert "1.2.3.4" in out.summary


@pytest.mark.asyncio
async def test_rejects_pending(store, tmp_path):
    jid = await store.create(target_spec={"t": 1}, regions=["nyc1"], artifacts_dir=str(tmp_path))
    with pytest.raises(RuntimeError, match="not done"):
        await handle_results(ReconResultsIn(job_id=jid), store=store)
