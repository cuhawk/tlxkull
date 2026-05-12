from unittest.mock import AsyncMock, MagicMock
import pytest


@pytest.mark.asyncio
async def test_push_scripts_uploads_phase_scripts():
    from recon_mcp.droplet import push_scripts
    d = MagicMock()
    d.push = AsyncMock()
    d.run = AsyncMock(return_value=(0, "", ""))
    await push_scripts(d)
    pushed = [c.args[1] for c in d.push.await_args_list]
    assert any("phase_scan.sh" in p for p in pushed)
    assert any("phase_ferox.sh" in p for p in pushed)
    d.run.assert_any_await("chmod +x /opt/recon/scripts/*.sh", check=True)
