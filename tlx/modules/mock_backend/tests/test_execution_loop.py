"""Tests for ExecutionLoop — Phase 7D Task 2."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from modules.mock_backend.core.execution_loop import (
    DiscoveryResult,
    ExecutionLoop,
)
from modules.mock_backend.core.payload_injector import PayloadInjector
from modules.mock_backend.core.sink_monitor import SinkHit, SinkMonitor


class _FakePage:
    def __init__(self, evaluate_return: Any = None) -> None:
        self.handlers: dict[str, list] = {}
        self.fills: list[tuple[str, str]] = []
        self.clicks: list[str] = []
        self._evaluate_return = evaluate_return
        self.evaluate_calls = 0

    def on(self, ev: str, handler: Any) -> None:
        self.handlers.setdefault(ev, []).append(handler)

    def fill(self, sel: str, val: str) -> None:
        self.fills.append((sel, val))

    def click(self, sel: str) -> None:
        self.clicks.append(sel)

    def evaluate(self, js: str) -> Any:
        self.evaluate_calls += 1
        return (
            self._evaluate_return if self._evaluate_return is not None
            else []
        )

    def emit_request(self, url: str) -> None:
        for h in self.handlers.get("request", []):
            req = type("R", (), {"url": url})()
            h(req)

    def close(self) -> None:
        pass


class _FakeMonitor(SinkMonitor):
    def __init__(self, hits: list[SinkHit] | None = None) -> None:
        super().__init__(sentinel="probe", timeout_ms=10)
        self._hits = hits or []

    async def observe(self, url: str) -> list[SinkHit]:
        return list(self._hits)


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "mb.db"


def _patch_loop(monkeypatch: pytest.MonkeyPatch, page: _FakePage,
                url: str = "http://127.0.0.1:9999/") -> dict:
    state = {"booted": 0, "shutdown": 0, "closed": 0}

    async def fake_boot(self: Any, app: Any) -> str:
        state["booted"] += 1
        return url

    async def fake_open(u: str, **kwargs: Any) -> tuple[Any, Any]:
        async def _close() -> None:
            state["closed"] += 1
        return page, _close

    async def fake_shutdown(self: Any) -> None:
        state["shutdown"] += 1

    monkeypatch.setattr(ExecutionLoop, "_boot_server", fake_boot)
    monkeypatch.setattr(
        "modules.mock_backend.core.pw_session.open_page", fake_open,
    )
    monkeypatch.setattr(ExecutionLoop, "_shutdown_server", fake_shutdown)
    return state


@pytest.mark.asyncio
async def test_run_returns_discovery_result(
    db_path: Path, monkeypatch: pytest.MonkeyPatch
):
    page = _FakePage()
    state = _patch_loop(monkeypatch, page)
    monitor = _FakeMonitor()
    loop = ExecutionLoop(db_path, PayloadInjector(), monitor)
    result = await loop.run(
        session_id="s1", route_specs=[], dom_specs=[], interactions=[],
    )
    assert isinstance(result, DiscoveryResult)
    assert result.url.startswith("http://127.0.0.1")
    assert state["booted"] == 1
    assert state["shutdown"] == 1


@pytest.mark.asyncio
async def test_run_dispatches_interactions(
    db_path: Path, monkeypatch: pytest.MonkeyPatch
):
    page = _FakePage()
    _patch_loop(monkeypatch, page)
    loop = ExecutionLoop(db_path, PayloadInjector(), _FakeMonitor())
    interactions = [
        {"type": "fill", "selector": "#email", "value": "a@b.c"},
        {"type": "click", "selector": "#submit"},
    ]
    result = await loop.run(
        session_id="s1", route_specs=[], dom_specs=[],
        interactions=interactions,
    )
    assert len(result.interactions) == 2
    assert result.interactions[0].kind == "form_fill"
    assert result.interactions[1].kind == "click"
    assert ("#email", "a@b.c") in page.fills
    assert "#submit" in page.clicks


@pytest.mark.asyncio
async def test_new_routes_populated_from_observed_requests(
    db_path: Path, monkeypatch: pytest.MonkeyPatch
):
    page = _FakePage()
    _patch_loop(monkeypatch, page, url="http://127.0.0.1:5555/")

    class _ClickyMonitor(SinkMonitor):
        def __init__(self) -> None:
            super().__init__(sentinel="x", timeout_ms=1)

        async def observe(self_inner, u: str) -> list[SinkHit]:
            page.emit_request("http://127.0.0.1:5555/api/hidden")
            page.emit_request("http://127.0.0.1:5555/api/secret")
            return []

    loop = ExecutionLoop(db_path, PayloadInjector(), _ClickyMonitor())
    page.emit_request("http://127.0.0.1:5555/")
    result = await loop.run(
        session_id="s1", route_specs=[], dom_specs=[], interactions=[],
    )
    assert "http://127.0.0.1:5555/api/hidden" in result.new_routes
    assert "http://127.0.0.1:5555/api/secret" in result.new_routes
    assert "http://127.0.0.1:5555/" not in result.new_routes


@pytest.mark.asyncio
async def test_sink_hits_populated_from_monitor(
    db_path: Path, monkeypatch: pytest.MonkeyPatch
):
    page = _FakePage()
    _patch_loop(monkeypatch, page)
    hit = SinkHit(
        chain_id="c1", sentinel="probe", sink_type="dom_mutation",
        detail="len=42", timestamp_ms=1.0,
    )
    monitor = _FakeMonitor(hits=[hit])
    loop = ExecutionLoop(db_path, PayloadInjector(), monitor)
    result = await loop.run(
        session_id="s1", route_specs=[], dom_specs=[], interactions=[],
    )
    assert len(result.sink_hits) == 1
    assert result.sink_hits[0].sink_type == "dom_mutation"


@pytest.mark.asyncio
async def test_server_booted_once_per_run(
    db_path: Path, monkeypatch: pytest.MonkeyPatch
):
    page = _FakePage()
    state = _patch_loop(monkeypatch, page)
    loop = ExecutionLoop(db_path, PayloadInjector(), _FakeMonitor())
    interactions = [{"type": "click", "selector": f"#x{i}"} for i in range(5)]
    await loop.run(
        session_id="s1", route_specs=[], dom_specs=[],
        interactions=interactions,
    )
    assert state["booted"] == 1
    assert state["shutdown"] == 1


@pytest.mark.asyncio
async def test_auto_explore_calls_page_explorer_when_true(
    db_path: Path, monkeypatch: pytest.MonkeyPatch
):
    page = _FakePage(evaluate_return=[
        {"type": "fill", "selector": "#email"},
        {"type": "click", "selector": "#submit"},
    ])
    _patch_loop(monkeypatch, page)
    loop = ExecutionLoop(db_path, PayloadInjector(), _FakeMonitor())
    result = await loop.run(
        session_id="s1", route_specs=[], dom_specs=[], interactions=[],
        auto_explore=True,
    )
    assert page.evaluate_calls == 1
    assert result.auto_explored is True
    assert result.auto_added_count == 2
    assert any(sel == "#email" for sel, _ in page.fills)
    assert "#submit" in page.clicks


@pytest.mark.asyncio
async def test_auto_explore_skipped_when_false_default(
    db_path: Path, monkeypatch: pytest.MonkeyPatch
):
    page = _FakePage(evaluate_return=[
        {"type": "click", "selector": "#submit"},
    ])
    _patch_loop(monkeypatch, page)
    loop = ExecutionLoop(db_path, PayloadInjector(), _FakeMonitor())
    result = await loop.run(
        session_id="s1", route_specs=[], dom_specs=[], interactions=[],
    )
    assert page.evaluate_calls == 0
    assert result.auto_explored is False
    assert result.auto_added_count == 0
    assert page.clicks == []


@pytest.mark.asyncio
async def test_auto_explore_dedupes_against_user_interactions(
    db_path: Path, monkeypatch: pytest.MonkeyPatch
):
    page = _FakePage(evaluate_return=[
        {"type": "fill", "selector": "#email"},
        {"type": "click", "selector": "#submit"},
        {"type": "click", "selector": "#extra"},
    ])
    _patch_loop(monkeypatch, page)
    loop = ExecutionLoop(db_path, PayloadInjector(), _FakeMonitor())
    user = [
        {"type": "click", "selector": "#submit"},
    ]
    result = await loop.run(
        session_id="s1", route_specs=[], dom_specs=[],
        interactions=user, auto_explore=True,
    )
    # user fired #submit once; auto-explore fires #email + #extra
    assert result.auto_added_count == 2
    assert page.clicks.count("#submit") == 1
    assert "#extra" in page.clicks
    assert any(sel == "#email" for sel, _ in page.fills)


@pytest.mark.asyncio
async def test_auto_explore_count_reported_in_result(
    db_path: Path, monkeypatch: pytest.MonkeyPatch
):
    page = _FakePage(evaluate_return=[
        {"type": "fill", "selector": f"#i{i}"} for i in range(3)
    ])
    _patch_loop(monkeypatch, page)
    loop = ExecutionLoop(db_path, PayloadInjector(), _FakeMonitor())
    result = await loop.run(
        session_id="s1", route_specs=[], dom_specs=[], interactions=[],
        auto_explore=True,
    )
    assert result.auto_explored is True
    assert result.auto_added_count == 3
    assert len(result.interactions) == 3
