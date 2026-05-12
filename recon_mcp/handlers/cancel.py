"""recon_cancel handler — signals the background task and (if absent) tears down droplets directly."""
from __future__ import annotations

import asyncio

import structlog

from ..do_client import DOClient
from ..jobs import JobStatus, JobStore
from ..tools import ReconCancelIn, ReconCancelOut
from .start import get_job_task

log = structlog.get_logger(__name__)


async def handle_cancel(inp: ReconCancelIn, *, store: JobStore, do: DOClient) -> ReconCancelOut:
    job = await store.get(inp.job_id)
    if not job:
        raise KeyError(f"unknown job: {inp.job_id}")

    # Preferred path: signal the background task so it tears down droplets + SSH key + key files
    # in its own `finally`, then transitions status to CANCELED itself.
    task = get_job_task(inp.job_id)
    if task is not None and not task.done():
        task.cancel()
        try:
            await asyncio.wait_for(task, timeout=120)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass
        except Exception as e:
            log.warning("cancel_task_raised", err=str(e))
        refreshed = await store.get(inp.job_id)
        return ReconCancelOut(
            job_id=inp.job_id,
            destroyed_droplets=[d["id"] for d in (refreshed or {}).get("droplets", [])],
        )

    # Fallback: task is gone (process restarted). Destroy any attached droplets directly.
    destroyed: list[int] = []
    for drop in job["droplets"]:
        try:
            await do.destroy_droplet(drop["id"])
            destroyed.append(drop["id"])
        except Exception as e:
            log.warning("destroy_failed", droplet_id=drop["id"], err=str(e))
    await store.set_status(inp.job_id, JobStatus.CANCELED)
    return ReconCancelOut(job_id=inp.job_id, destroyed_droplets=destroyed)
