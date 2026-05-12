"""recon_list_jobs handler."""
from __future__ import annotations

from ..jobs import JobStore
from ..tools import ReconListJobsOut


async def handle_list_jobs(*, store: JobStore) -> ReconListJobsOut:
    jobs = await store.list_all()
    return ReconListJobsOut(jobs=[
        {k: v for k, v in j.items() if k not in ("target_spec",)} for j in jobs
    ])
