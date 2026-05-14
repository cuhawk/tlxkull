"""recon_start handler — validates input, persists job, spawns background runner."""
from __future__ import annotations

import asyncio
import json
import os
import secrets
import tempfile
from pathlib import Path

import asyncssh
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

# Strong refs so spawned tasks survive GC, plus per-job handles for cancel.
_BG_TASKS: set[asyncio.Task] = set()
_JOB_TASKS: dict[str, asyncio.Task] = {}


_NAME_PREFIXES = ("apt", "web", "dev", "svc", "node", "vm", "host", "edge")


def _gen_droplet_name() -> str:
    """Inconspicuous random droplet name. No tool/job/purpose/region leakage."""
    return f"{secrets.choice(_NAME_PREFIXES)}-{secrets.token_hex(3)}"


def _droplet_plan(targets, scan_region: str, probe_regions: list[str]) -> list[dict]:
    # Generic plan — collapse purpose/region detail to avoid leaking intent in tool output.
    return [{"droplets": 1 + len(probe_regions), "targets": len(targets)}]


async def handle_start(
    inp: ReconStartIn, *, store: JobStore, cfg: Config, artifacts_root: Path,
) -> ReconStartOut:
    targets = parse_targets(inp.targets)
    check_targets(targets)
    probe_regions = validate_regions(inp.probe_regions) if inp.probe_regions else []
    scan_region = inp.scan_region or cfg.default_scan_region

    # Enforce max_droplets at request time so callers cannot bypass via probe_regions.
    total = 1 + len(probe_regions)
    if total > inp.max_droplets:
        raise ValueError(
            f"plan needs {total} droplets, exceeds max_droplets={inp.max_droplets}"
        )

    plan = _droplet_plan(targets, scan_region, probe_regions)

    job_id = await store.create(
        target_spec={"targets": [{"kind": t.kind.value, "value": t.value} for t in targets],
                     "target_name": inp.target_name},
        regions=[scan_region, *probe_regions],
        artifacts_dir=None,
    )
    final_dir = artifacts_root / inp.target_name / "recon" / job_id
    final_dir.mkdir(parents=True, exist_ok=True)
    await store.set_artifacts_dir(job_id, str(final_dir))

    task = asyncio.create_task(_run_job(
        job_id=job_id, targets=targets, scan_region=scan_region,
        probe_regions=probe_regions, store=store, cfg=cfg, out_dir=final_dir,
    ))
    _BG_TASKS.add(task)
    _JOB_TASKS[job_id] = task

    def _done(t: asyncio.Task) -> None:
        _BG_TASKS.discard(t)
        _JOB_TASKS.pop(job_id, None)

    task.add_done_callback(_done)

    return ReconStartOut(job_id=job_id, target_count=len(targets), droplet_plan=plan)


def get_job_task(job_id: str) -> asyncio.Task | None:
    return _JOB_TASKS.get(job_id)


async def _gen_ssh_keypair(ssh_dir: Path, job_id: str) -> tuple[Path, str]:
    ssh_dir.mkdir(parents=True, exist_ok=True)
    priv = ssh_dir / f"{job_id}.key"
    pub_path = ssh_dir / f"{job_id}.key.pub"

    def _gen() -> None:
        import subprocess
        subprocess.run(
            ["ssh-keygen", "-t", "ed25519", "-N", "", "-C", secrets.token_hex(4), "-f", str(priv)],
            check=True, capture_output=True,
        )
        os.chmod(priv, 0o600)

    await asyncio.to_thread(_gen)
    return priv, pub_path.read_text().strip()


async def _gen_host_keypair() -> tuple[str, str]:
    """Generate an ed25519 host keypair locally. Returns (openssh_private, openssh_public)."""
    def _gen() -> tuple[str, str]:
        import subprocess
        with tempfile.TemporaryDirectory() as td:
            kp = Path(td) / "hk"
            subprocess.run(
                ["ssh-keygen", "-t", "ed25519", "-N", "", "-C", "recon-host", "-f", str(kp)],
                check=True, capture_output=True,
            )
            return kp.read_text(), (Path(str(kp) + ".pub")).read_text()
    return await asyncio.to_thread(_gen)


async def _run_job(*, job_id, targets, scan_region, probe_regions, store, cfg, out_dir: Path) -> None:
    do = DOClient(token=cfg.do_api_token)
    priv_key, pub_key = await _gen_ssh_keypair(cfg.ssh_key_dir, job_id)
    ssh_key = None
    droplets: list[tuple[Droplet, str]] = []
    canceled = False
    try:
        try:
            ssh_key = await do.create_ssh_key(name=f"k-{secrets.token_hex(4)}", public_key=pub_key)
        except Exception as e:
            await store.set_error(job_id, f"ssh_key_create: {e}")
            return

        await store.set_status(job_id, JobStatus.PROVISIONING)
        host_priv, host_pub = await _gen_host_keypair()
        user_data = render_user_data(
            authorized_key=pub_key,
            job_id=job_id,
            host_private_key=host_priv,
            host_public_key=host_pub,
        )
        # Parse the OpenSSH public key once so each droplet can pin it without re-parsing.
        try:
            pinned_host_key = asyncssh.import_public_key(host_pub)
        except Exception as e:
            log.error("host_pubkey_parse_failed", err=str(e))
            pinned_host_key = None
        regions = [(scan_region, "scan")] + [(r, "probe") for r in probe_regions]

        async def make(region: str, purpose: str) -> tuple[Droplet, str]:
            d = Droplet(
                do=do, name=_gen_droplet_name(),
                region=region, size=cfg.droplet_size, image="ubuntu-24-04-x64",
                ssh_key_ids=[ssh_key["id"]], user_data=user_data,
                tags=["recon-mcp", f"job:{job_id}"],
            )
            d.ssh_private_key_path = str(priv_key)
            if pinned_host_key is not None:
                d._pinned_host_keys = [pinned_host_key]
            return (d, purpose)

        droplets = await asyncio.gather(*[make(r, p) for r, p in regions])

        async def with_provision(d: Droplet, purpose: str):
            await d.__aenter__()
            await push_scripts(d)
            await store.attach_droplet(job_id, droplet_id=d.droplet_id, region=d.region)
            return (d, purpose)

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
            tag = f"{purpose}_{d.region}"
            for t in targets:
                await run_scan(
                    droplet=d, target=t,
                    local_out=local_out / t.value.replace("/", "_"),
                    env=env,
                    on_phase=lambda phase, _tag=tag: store.set_phase(
                        job_id, droplet_tag=_tag, phase=phase
                    ),
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
    except asyncio.CancelledError:
        canceled = True
        log.info("run_job_canceled", job_id=job_id)
        await store.set_status(job_id, JobStatus.CANCELED)
        raise
    except Exception as e:
        log.exception("run_job_failed", err=str(e))
        await store.set_error(job_id, str(e))
    finally:
        # Tear down every droplet that was created, regardless of which exception we hit.
        for entry in droplets:
            d = entry[0] if isinstance(entry, tuple) else entry
            try:
                await asyncio.shield(_destroy(d))
            except Exception as e:
                log.error("teardown_failed", err=str(e))
        if ssh_key:
            try:
                await asyncio.shield(do.delete_ssh_key(ssh_key["id"]))
            except Exception as e:
                log.error("ssh_key_delete_failed", err=str(e))
        # Best-effort SSH-key file cleanup; log so on-disk leaks are visible.
        for p in (priv_key, Path(str(priv_key) + ".pub")):
            try:
                if p.exists():
                    p.unlink()
            except Exception as e:
                log.error("ssh_keyfile_unlink_failed", path=str(p), err=str(e))
        if canceled:
            log.info("run_job_canceled_cleanup_done", job_id=job_id)


async def _destroy(d) -> None:
    if d is None:
        return
    if hasattr(d, "__aexit__"):
        await d.__aexit__(None, None, None)
