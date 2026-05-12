"""recon_start handler — validates input, persists job, spawns background runner."""
from __future__ import annotations

import asyncio
import json
import os
import subprocess
from pathlib import Path

import structlog

from ..artifacts import summarize
from ..cloud_init import render_user_data
from ..config import Config
from ..do_client import DOClient
from ..droplet import Droplet, push_scripts
from ..input_parser import parse_targets
from ..jobs import JobStatus, JobStore
from ..regions import validate_regions
from ..safety import check_targets
from ..scanner import run_scan
from ..tools import ReconStartIn, ReconStartOut

log = structlog.get_logger(__name__)


def _droplet_plan(targets, scan_region: str, probe_regions: list[str]) -> list[dict]:
    plan = [{"region": scan_region, "purpose": "scan", "targets": len(targets)}]
    for r in probe_regions:
        plan.append({"region": r, "purpose": "probe", "targets": len(targets)})
    return plan


async def handle_start(
    inp: ReconStartIn, *, store: JobStore, cfg: Config, artifacts_root: Path,
) -> ReconStartOut:
    targets = parse_targets(inp.targets)
    check_targets(targets)
    probe_regions = validate_regions(inp.probe_regions) if inp.probe_regions else []
    scan_region = inp.scan_region or cfg.default_scan_region
    plan = _droplet_plan(targets, scan_region, probe_regions)

    job_id = await store.create(
        target_spec={"targets": [{"kind": t.kind.value, "value": t.value} for t in targets],
                     "target_name": inp.target_name},
        regions=[scan_region, *probe_regions],
        artifacts_dir=None,
    )
    final_dir = artifacts_root / inp.target_name / "recon" / job_id
    final_dir.mkdir(parents=True, exist_ok=True)

    asyncio.create_task(_run_job(
        job_id=job_id, targets=targets, scan_region=scan_region,
        probe_regions=probe_regions, store=store, cfg=cfg, out_dir=final_dir,
    ))

    return ReconStartOut(job_id=job_id, target_count=len(targets), droplet_plan=plan)


def _gen_ssh_keypair(ssh_dir: Path, job_id: str) -> tuple[Path, str]:
    ssh_dir.mkdir(parents=True, exist_ok=True)
    priv = ssh_dir / f"{job_id}.key"
    pub = ssh_dir / f"{job_id}.key.pub"
    subprocess.run(
        ["ssh-keygen", "-t", "ed25519", "-N", "", "-C", f"recon-{job_id}", "-f", str(priv)],
        check=True, capture_output=True,
    )
    os.chmod(priv, 0o600)
    return priv, pub.read_text().strip()


async def _run_job(*, job_id, targets, scan_region, probe_regions, store, cfg, out_dir: Path) -> None:
    do = DOClient(token=cfg.do_api_token)
    priv_key, pub_key = _gen_ssh_keypair(cfg.ssh_key_dir, job_id)
    ssh_key = None
    try:
        ssh_key = await do.create_ssh_key(name=f"recon-{job_id}", public_key=pub_key)
    except Exception as e:
        await store.set_error(job_id, f"ssh_key_create: {e}")
        return
    droplets: list[tuple[Droplet, str]] = []
    try:
        await store.set_status(job_id, JobStatus.PROVISIONING)
        user_data = render_user_data(authorized_key=pub_key, job_id=job_id)
        regions = [(scan_region, "scan")] + [(r, "probe") for r in probe_regions]

        async def make(region: str, purpose: str) -> tuple[Droplet, str]:
            d = Droplet(
                do=do, name=f"recon-{job_id}-{purpose}-{region}",
                region=region, size=cfg.droplet_size, image="ubuntu-24-04-x64",
                ssh_key_ids=[ssh_key["id"]], user_data=user_data,
                tags=["recon-mcp", f"job:{job_id}"],
            )
            d.ssh_private_key_path = str(priv_key)
            return (d, purpose)

        droplets = await asyncio.gather(*[make(r, p) for r, p in regions])

        async def with_provision(d: Droplet, purpose: str):
            await d.__aenter__()
            await push_scripts(d)
            await store.attach_droplet(job_id, droplet_id=d.droplet_id, region=d.region)
            return (d, purpose)

        try:
            droplets = await asyncio.gather(*[with_provision(d, p) for d, p in droplets])
            await store.set_status(job_id, JobStatus.RUNNING)
            env = {}
            if cfg.shodan_api_key:
                env["SHODAN_API_KEY"] = cfg.shodan_api_key
            if cfg.c99_api_key:
                env["C99_API_KEY"] = cfg.c99_api_key

            async def per_droplet(d: Droplet, purpose: str):
                local_out = out_dir / f"{purpose}_{d.region}"
                local_out.mkdir(parents=True, exist_ok=True)
                for t in targets:
                    await run_scan(
                        droplet=d, target=t,
                        local_out=local_out / t.value.replace("/", "_"),
                        env=env,
                    )

            await asyncio.gather(*[per_droplet(d, p) for d, p in droplets])

            scan_dir = out_dir / f"scan_{scan_region}"
            summary = {}
            if scan_dir.exists():
                for t_dir in scan_dir.iterdir():
                    if t_dir.is_dir():
                        summary[t_dir.name] = summarize(t_dir)
            (out_dir / "summary.json").write_text(json.dumps(summary, indent=2))

            await store.set_status(job_id, JobStatus.DONE)
        finally:
            for d, _ in droplets:
                try:
                    await d.__aexit__(None, None, None)
                except Exception as e:
                    log.error("teardown_failed", err=str(e))
    except Exception as e:
        log.exception("run_job_failed", err=str(e))
        await store.set_error(job_id, str(e))
    finally:
        if ssh_key:
            try:
                await do.delete_ssh_key(ssh_key["id"])
            except Exception:
                pass
        try:
            os.remove(priv_key)
            os.remove(str(priv_key) + ".pub")
        except Exception:
            pass
