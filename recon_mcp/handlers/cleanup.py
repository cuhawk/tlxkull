"""recon_cleanup_orphans handler — destroys recon-mcp droplets whose owning job is finished/missing."""
from __future__ import annotations

import re

from ..do_client import DOClient
from ..jobs import JobStatus, JobStore
from ..tools import ReconCleanupOrphansOut

_JOB_TAG = re.compile(r"^job:([a-z0-9]+)$")
_TERMINAL = {JobStatus.DONE.value, JobStatus.FAILED.value, JobStatus.CANCELED.value}


async def handle_cleanup_orphans(*, store: JobStore, do: DOClient) -> ReconCleanupOrphansOut:
    drops = await do.list_by_tag("recon-mcp")
    destroyed: list[int] = []
    for d in drops:
        tags = d.get("tags") or []
        job_id = next((m.group(1) for t in tags if (m := _JOB_TAG.match(t))), None)
        if not job_id:
            continue
        row = await store.get(job_id)
        if row is None or row["status"] in _TERMINAL:
            try:
                await do.destroy_droplet(d["id"])
                destroyed.append(d["id"])
            except Exception:
                pass
    return ReconCleanupOrphansOut(destroyed=destroyed)
