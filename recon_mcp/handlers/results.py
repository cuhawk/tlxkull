"""recon_results handler — reads summary.json under artifacts_dir."""
from __future__ import annotations

import json
from pathlib import Path

from ..jobs import JobStatus, JobStore
from ..tools import ReconResultsIn, ReconResultsOut


async def handle_results(inp: ReconResultsIn, *, store: JobStore) -> ReconResultsOut:
    job = await store.get(inp.job_id)
    if not job:
        raise KeyError(f"unknown job: {inp.job_id}")
    if job["status"] != JobStatus.DONE:
        raise RuntimeError(f"job {inp.job_id} not done (status={job['status']})")
    summary_path = Path(job["artifacts_dir"]) / "summary.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
    return ReconResultsOut(job_id=inp.job_id, summary=summary)
