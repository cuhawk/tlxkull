"""Pydantic request/response models for recon-mcp tools."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ReconStartIn(_Strict):
    targets: list[str] = Field(..., description="IPs, CIDRs, or *.domain.tld entries")
    target_name: str = Field(..., description="Engagement name (used for artifact dir)")
    scan_region: str = Field("nyc1", description="DO region for scan-heavy phases")
    probe_regions: list[str] = Field(
        default_factory=list,
        description="Additional regions to run httpx+feroxbuster from (geo-block detection)",
    )
    max_droplets: int = Field(10, ge=1, le=50)


class ReconStartOut(_Strict):
    job_id: str
    target_count: int
    droplet_plan: list[dict]


class ReconStatusIn(_Strict):
    job_id: str


class ReconStatusOut(_Strict):
    job_id: str
    status: str
    droplets: list[dict]
    artifacts_dir: str | None
    error: str | None
    phase_progress: dict[str, str] = Field(default_factory=dict)


class ReconResultsIn(_Strict):
    job_id: str


class ReconResultsOut(_Strict):
    job_id: str
    summary: dict


class ReconCancelIn(_Strict):
    job_id: str


class ReconCancelOut(_Strict):
    job_id: str
    destroyed_droplets: list[int]


class ReconListJobsOut(_Strict):
    jobs: list[dict]


class ReconCleanupOrphansOut(_Strict):
    destroyed: list[int]
