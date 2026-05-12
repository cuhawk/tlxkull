import pytest
import pytest_asyncio
from recon_mcp.jobs import JobStore, JobStatus


@pytest_asyncio.fixture
async def store(tmp_path):
    s = JobStore(db_path=str(tmp_path / "j.sqlite"))
    await s.init()
    return s


@pytest.mark.asyncio
async def test_create_and_get(store):
    jid = await store.create(target_spec={"targets": ["1.2.3.4"]}, regions=["nyc1"])
    job = await store.get(jid)
    assert job["status"] == JobStatus.PENDING
    assert job["regions"] == ["nyc1"]


@pytest.mark.asyncio
async def test_update_status(store):
    jid = await store.create(target_spec={"targets": ["1.2.3.4"]}, regions=["nyc1"])
    await store.set_status(jid, JobStatus.RUNNING)
    assert (await store.get(jid))["status"] == JobStatus.RUNNING


@pytest.mark.asyncio
async def test_attach_droplet(store):
    jid = await store.create(target_spec={"targets": ["x"]}, regions=["nyc1"])
    await store.attach_droplet(jid, droplet_id=42, region="nyc1")
    job = await store.get(jid)
    assert {"id": 42, "region": "nyc1"} in job["droplets"]


@pytest.mark.asyncio
async def test_list_active(store):
    j1 = await store.create(target_spec={"t": 1}, regions=["nyc1"])
    j2 = await store.create(target_spec={"t": 2}, regions=["nyc1"])
    await store.set_status(j2, JobStatus.DONE)
    active = await store.list_active()
    assert [j["id"] for j in active] == [j1]


@pytest.mark.asyncio
async def test_set_error(store):
    jid = await store.create(target_spec={"t": 1}, regions=["nyc1"])
    await store.set_error(jid, "boom")
    job = await store.get(jid)
    assert job["status"] == JobStatus.FAILED
    assert job["error"] == "boom"
