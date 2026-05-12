"""recon_status handler — reads job row from store."""
from __future__ import annotations

from ..jobs import JobStore
from ..tools import ReconStatusIn, ReconStatusOut


async def handle_status(inp: ReconStatusIn, *, store: JobStore) -> ReconStatusOut:
    job = await store.get(inp.job_id)
    if not job:
        raise KeyError(f"unknown job: {inp.job_id}")
    return ReconStatusOut(
        job_id=job["id"],
        status=job["status"],
        droplets=job["droplets"],
        artifacts_dir=job["artifacts_dir"],
        error=job["error"],
    )
