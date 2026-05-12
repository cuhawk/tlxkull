"""recon_cleanup_orphans handler — destroys recon-mcp droplets whose owning job is finished/missing/stale."""
from __future__ import annotations

import re
import time

import structlog

from ..do_client import DOClient
from ..jobs import JobStatus, JobStore
from ..tools import ReconCleanupOrphansOut

log = structlog.get_logger(__name__)

_JOB_TAG = re.compile(r"^job:([a-z0-9]+)$")
_TERMINAL = {JobStatus.DONE.value, JobStatus.FAILED.value, JobStatus.CANCELED.value}
_NONTERMINAL_STUCK = {JobStatus.PROVISIONING.value, JobStatus.RUNNING.value, JobStatus.PENDING.value}

# Anything still in a non-terminal state past this age is treated as orphan — the
# MCP process must have crashed mid-run, since recon never takes this long.
_STALE_AGE_SEC = 3 * 60 * 60  # 3h


async def handle_cleanup_orphans(*, store: JobStore, do: DOClient) -> ReconCleanupOrphansOut:
    drops = await do.list_by_tag("recon-mcp")
    now = time.time()
    destroyed: list[int] = []
    for d in drops:
        tags = d.get("tags") or []
        job_id = next((m.group(1) for t in tags if (m := _JOB_TAG.match(t))), None)
        if not job_id:
            continue
        row = await store.get(job_id)
        if row is None:
            should_destroy = True
        elif row["status"] in _TERMINAL:
            should_destroy = True
        elif row["status"] in _NONTERMINAL_STUCK and (now - row["created_at"]) > _STALE_AGE_SEC:
            log.warning(
                "stale_job_orphaned", job_id=job_id, status=row["status"],
                age_sec=int(now - row["created_at"]),
            )
            await store.set_error(job_id, "orphaned: exceeded stale threshold")
            should_destroy = True
        else:
            should_destroy = False
        if should_destroy:
            try:
                await do.destroy_droplet(d["id"])
                destroyed.append(d["id"])
            except Exception as e:
                log.warning("destroy_failed", droplet_id=d["id"], err=str(e))
    return ReconCleanupOrphansOut(destroyed=destroyed)
