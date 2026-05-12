"""recon_cancel handler."""
from __future__ import annotations

from ..do_client import DOClient
from ..jobs import JobStatus, JobStore
from ..tools import ReconCancelIn, ReconCancelOut


async def handle_cancel(inp: ReconCancelIn, *, store: JobStore, do: DOClient) -> ReconCancelOut:
    job = await store.get(inp.job_id)
    if not job:
        raise KeyError(f"unknown job: {inp.job_id}")
    destroyed: list[int] = []
    for drop in job["droplets"]:
        try:
            await do.destroy_droplet(drop["id"])
            destroyed.append(drop["id"])
        except Exception:
            pass
    await store.set_status(inp.job_id, JobStatus.CANCELED)
    return ReconCancelOut(job_id=inp.job_id, destroyed_droplets=destroyed)
