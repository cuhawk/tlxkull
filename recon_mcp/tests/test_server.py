import pytest
from recon_mcp.server import build_server


@pytest.mark.asyncio
async def test_server_advertises_six_tools(monkeypatch, tmp_path):
    monkeypatch.setenv("DO_API_TOKEN", "x")
    monkeypatch.setenv("RECON_DB_PATH", str(tmp_path / "j.sqlite"))
    monkeypatch.setenv("RECON_SSH_KEY_DIR", str(tmp_path / "ssh"))
    # Prevent the boot-time orphan sweep from hitting the real DO API
    from unittest.mock import AsyncMock
    monkeypatch.setattr(
        "recon_mcp.server.handle_cleanup_orphans",
        AsyncMock(return_value=None),
    )
    srv = await build_server()
    from mcp.types import ListToolsRequest
    handler = srv.request_handlers.get(ListToolsRequest)
    assert handler is not None, (
        f"no ListToolsRequest handler registered: {srv.request_handlers.keys()}"
    )
    result = await handler(ListToolsRequest(method="tools/list"))
    names = {t.name for t in result.root.tools}
    assert names == {
        "recon_start",
        "recon_status",
        "recon_results",
        "recon_cancel",
        "recon_list_jobs",
        "recon_cleanup_orphans",
    }
