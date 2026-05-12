from unittest.mock import AsyncMock, MagicMock
import pytest
from recon_mcp.input_parser import Target, TargetKind
from recon_mcp.scanner import run_scan, PhaseResult


def fake_droplet():
    d = MagicMock()
    d.ip = "1.2.3.4"
    d.run = AsyncMock(return_value=(0, "ok", ""))
    d.push = AsyncMock()
    d.pull = AsyncMock()
    return d


@pytest.mark.asyncio
async def test_ip_target_runs_all_phases(tmp_path):
    d = fake_droplet()
    res = await run_scan(
        droplet=d, target=Target(TargetKind.IP, "9.9.9.9"),
        local_out=tmp_path, env={},
    )
    phases = [c.args[0] for c in d.run.await_args_list if "phase_" in str(c.args[0])]
    assert any("phase_scan.sh" in p for p in phases)
    assert any("phase_subdomains.sh" in p for p in phases)
    assert any("phase_resolve.sh" in p for p in phases)
    assert any("phase_httpx.sh" in p for p in phases)
    assert any("phase_ferox.sh" in p for p in phases)


@pytest.mark.asyncio
async def test_wildcard_target_skips_scan(tmp_path):
    d = fake_droplet()
    await run_scan(
        droplet=d, target=Target(TargetKind.WILDCARD, "example.com"),
        local_out=tmp_path, env={},
    )
    phases = [str(c.args[0]) for c in d.run.await_args_list]
    assert not any("phase_scan.sh" in p for p in phases)
    assert any("phase_subdomains.sh" in p for p in phases)
    assert any("phase_httpx.sh" in p for p in phases)


@pytest.mark.asyncio
async def test_cidr_runs_scan(tmp_path):
    d = fake_droplet()
    await run_scan(
        droplet=d, target=Target(TargetKind.CIDR, "10.0.0.0/24"),
        local_out=tmp_path, env={},
    )
    phases = [str(c.args[0]) for c in d.run.await_args_list]
    assert any("phase_scan.sh" in p for p in phases)


@pytest.mark.asyncio
async def test_pulls_artifacts_into_local_out(tmp_path):
    d = fake_droplet()
    await run_scan(
        droplet=d, target=Target(TargetKind.WILDCARD, "ex.com"),
        local_out=tmp_path, env={},
    )
    d.pull.assert_awaited()


@pytest.mark.asyncio
async def test_phase_failure_recorded_not_raised(tmp_path):
    d = fake_droplet()
    async def run_side(cmd, *, check=False, **kw):
        if "phase_subdomains.sh" in cmd:
            return (2, "", "amass crashed")
        return (0, "ok", "")
    d.run.side_effect = run_side
    res = await run_scan(
        droplet=d, target=Target(TargetKind.WILDCARD, "ex.com"),
        local_out=tmp_path, env={},
    )
    sub = [p for p in res.phases if p.name == "subdomains"][0]
    assert sub.status == "failed"
    assert "amass crashed" in sub.stderr
