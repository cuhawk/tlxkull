"""mcp surface boot smoke."""
from __future__ import annotations

from pathlib import Path

import pytest

from kernel import Kernel


async def _boot_mcp(tmp_path: Path) -> Kernel:
    return await Kernel.boot(
        config_path=tmp_path / "missing-config.toml",
        db_path=tmp_path / "sessions.db",
        plugin_paths=[tmp_path / "no-plugins"],
        module_paths=[tmp_path / "no-modules"],
        surface="mcp",
    )


@pytest.mark.asyncio
async def test_mcp_boot_without_anthropic_key(tmp_path: Path, monkeypatch) -> None:
    """mcp surface boots without ANTHROPIC_API_KEY (no engine instantiated)."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    kernel = await _boot_mcp(tmp_path)
    try:
        assert kernel.surface == "mcp"
        assert kernel.session_id
        # mcp surface skips engine, compactor, slash router
        assert not hasattr(kernel, "engine") or getattr(kernel, "engine", None) is None
        assert not hasattr(kernel, "compactor") or getattr(kernel, "compactor", None) is None
        assert not hasattr(kernel, "slash") or getattr(kernel, "slash", None) is None
        # core systems still present
        assert kernel.tools is not None
        assert kernel.sandbox is not None
        assert kernel.processes is not None
        assert kernel.prompt_builder is not None
    finally:
        kernel.shutdown()


@pytest.mark.asyncio
async def test_mcp_boot_no_reaper_task(tmp_path: Path) -> None:
    """mcp surface must not start the reaper (ui-only)."""
    kernel = await _boot_mcp(tmp_path)
    try:
        assert not hasattr(kernel, "_reaper_task")
    finally:
        kernel.shutdown()


@pytest.mark.asyncio
async def test_shutdown_hooks_fire(tmp_path: Path) -> None:
    """kernel.shutdown() invokes registered on_shutdown hooks (LIFO)."""
    kernel = await _boot_mcp(tmp_path)
    order: list[str] = []
    kernel.on_shutdown(lambda: order.append("first"))
    kernel.on_shutdown(lambda: order.append("second"))
    kernel.shutdown()
    assert order == ["second", "first"]


@pytest.mark.asyncio
async def test_shutdown_hook_failure_isolated(tmp_path: Path) -> None:
    """A failing shutdown hook must not block other hooks."""
    kernel = await _boot_mcp(tmp_path)
    fired: list[str] = []

    def boom() -> None:
        raise RuntimeError("hook failure")

    kernel.on_shutdown(lambda: fired.append("before"))
    kernel.on_shutdown(boom)
    kernel.on_shutdown(lambda: fired.append("after"))
    kernel.shutdown()
    assert "before" in fired
    assert "after" in fired
