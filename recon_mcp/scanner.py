"""Drive the per-target phase pipeline on a single droplet."""
from __future__ import annotations

import shlex
from dataclasses import dataclass, field
from pathlib import Path

import structlog

from .input_parser import Target, TargetKind

log = structlog.get_logger(__name__)


@dataclass
class PhaseResult:
    name: str
    status: str  # "ok" | "failed" | "skipped"
    stdout: str = ""
    stderr: str = ""


@dataclass
class ScanResult:
    target: Target
    phases: list[PhaseResult] = field(default_factory=list)


_PHASE_BIN = "/opt/recon/scripts"


def _phases_for(target: Target) -> list[str]:
    if target.kind is TargetKind.WILDCARD:
        return ["subdomains", "resolve", "httpx", "ferox"]
    return ["scan", "subdomains", "resolve", "httpx", "ferox"]


def _input_payload(target: Target) -> dict[str, str]:
    if target.kind is TargetKind.IP:
        return {"ips.txt": target.value, "domains.txt": ""}
    if target.kind is TargetKind.CIDR:
        return {"ips.txt": target.value, "domains.txt": ""}
    return {"ips.txt": "", "domains.txt": target.value}


async def run_scan(
    *, droplet, target: Target, local_out: Path, env: dict[str, str],
    on_phase=None,
) -> ScanResult:
    result = ScanResult(target=target)

    await droplet.run("mkdir -p /opt/recon/in /opt/recon/out /opt/recon/scripts", check=True)
    for name, content in _input_payload(target).items():
        path = f"/opt/recon/in/{name}"
        # Use base64 + decode on the remote side so the payload survives every shell
        # quoting edge case (heredoc-terminator collision, embedded $, backticks, …).
        import base64
        b64 = base64.b64encode(content.encode()).decode()
        await droplet.run(
            f"echo {shlex.quote(b64)} | base64 -d > {shlex.quote(path)}",
            check=True,
        )

    env_prefix = " ".join(f"{k}={shlex.quote(v)}" for k, v in env.items())
    for phase in _phases_for(target):
        if on_phase is not None:
            try:
                res = on_phase(phase)
                if hasattr(res, "__await__"):
                    await res
            except Exception as e:
                log.debug("on_phase_callback_failed", err=str(e))
        cmd = f"{env_prefix} bash {_PHASE_BIN}/phase_{phase}.sh"
        rc, out, err = await droplet.run(cmd, check=False, timeout=3600)
        status = "ok" if rc == 0 else "failed"
        result.phases.append(PhaseResult(name=phase, status=status, stdout=out, stderr=err))
        if rc != 0:
            log.warning("phase_failed", target=target.value, phase=phase, stderr=err[:500])

    local_out.mkdir(parents=True, exist_ok=True)
    try:
        await droplet.pull("/opt/recon/out", str(local_out / "out"))
    except Exception as e:
        log.error("pull_failed", err=str(e))
        result.phases.append(PhaseResult(name="pull", status="failed", stderr=str(e)))

    return result
