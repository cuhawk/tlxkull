"""Tests for page_explorer — Phase 7I."""
from __future__ import annotations

from typing import Any

import pytest

from modules.mock_backend.core.page_explorer import (
    dedup_against,
    enumerate_interactions,
)


class _FakePage:
    def __init__(self, ret: Any = None, raises: bool = False) -> None:
        self._ret = ret
        self._raises = raises
        self.calls: list[str] = []

    def evaluate(self, js: str) -> Any:
        self.calls.append(js)
        if self._raises:
            raise RuntimeError("boom")
        return self._ret


@pytest.mark.asyncio
async def test_enumerate_returns_fill_specs_for_form_inputs() -> None:
    page = _FakePage(ret=[
        {"type": "fill", "selector": "#email"},
        {"type": "fill", "selector": "#pwd"},
    ])
    out = await enumerate_interactions(page, "SENTINEL_X")
    assert out == [
        {"type": "fill", "selector": "#email", "value": "SENTINEL_X"},
        {"type": "fill", "selector": "#pwd", "value": "SENTINEL_X"},
    ]


@pytest.mark.asyncio
async def test_enumerate_returns_click_specs_for_buttons() -> None:
    page = _FakePage(ret=[
        {"type": "click", "selector": "#submit"},
        {"type": "click", "selector": "button.primary"},
    ])
    out = await enumerate_interactions(page, "X")
    assert out == [
        {"type": "click", "selector": "#submit"},
        {"type": "click", "selector": "button.primary"},
    ]


@pytest.mark.asyncio
async def test_enumerate_returns_empty_when_evaluate_raises() -> None:
    page = _FakePage(raises=True)
    out = await enumerate_interactions(page, "X")
    assert out == []


@pytest.mark.asyncio
async def test_enumerate_returns_empty_when_evaluate_returns_non_list() -> None:
    page = _FakePage(ret={"not": "a list"})
    out = await enumerate_interactions(page, "X")
    assert out == []


@pytest.mark.asyncio
async def test_enumerate_caps_at_50_by_default() -> None:
    ret = [
        {"type": "fill", "selector": f"#i{i}"} for i in range(100)
    ]
    page = _FakePage(ret=ret)
    out = await enumerate_interactions(page, "S")
    assert len(out) == 50
    assert out[0]["selector"] == "#i0"
    assert out[-1]["selector"] == "#i49"


@pytest.mark.asyncio
async def test_enumerate_caps_at_custom_value() -> None:
    ret = [
        {"type": "click", "selector": f"#b{i}"} for i in range(10)
    ]
    page = _FakePage(ret=ret)
    out = await enumerate_interactions(page, "S", cap=3)
    assert len(out) == 3


@pytest.mark.asyncio
async def test_enumerate_skips_entries_missing_type_or_selector() -> None:
    page = _FakePage(ret=[
        {"type": "fill"},
        {"selector": "#x"},
        {"type": "fill", "selector": ""},
        {"type": "fill", "selector": 123},
        "garbage",
        None,
        {"type": "fill", "selector": "#valid"},
    ])
    out = await enumerate_interactions(page, "S")
    assert out == [
        {"type": "fill", "selector": "#valid", "value": "S"},
    ]


@pytest.mark.asyncio
async def test_enumerate_injects_sentinel_into_fill_values() -> None:
    page = _FakePage(ret=[
        {"type": "fill", "selector": "#a"},
        {"type": "click", "selector": "#b"},
    ])
    out = await enumerate_interactions(page, "MY_SENTINEL_VALUE")
    assert out[0]["value"] == "MY_SENTINEL_VALUE"
    assert "value" not in out[1]


def test_dedup_against_removes_kind_selector_collisions() -> None:
    discovered = [
        {"type": "fill", "selector": "#a", "value": "x"},
        {"type": "click", "selector": "#b"},
        {"type": "click", "selector": "#c"},
    ]
    user = [
        {"type": "click", "selector": "#b"},
    ]
    out = dedup_against(discovered, user)
    assert out == [
        {"type": "fill", "selector": "#a", "value": "x"},
        {"type": "click", "selector": "#c"},
    ]


def test_dedup_against_treats_fill_and_form_fill_aliases_as_same() -> None:
    discovered = [{"type": "fill", "selector": "#a", "value": "x"}]
    user = [{"type": "form_fill", "selector": "#a", "value": "y"}]
    assert dedup_against(discovered, user) == []

    discovered = [{"type": "form_fill", "selector": "#z"}]
    user = [{"type": "fill", "selector": "#z"}]
    assert dedup_against(discovered, user) == []


def test_dedup_against_preserves_order_of_discovered() -> None:
    discovered = [
        {"type": "fill", "selector": "#a"},
        {"type": "fill", "selector": "#b"},
        {"type": "click", "selector": "#c"},
        {"type": "click", "selector": "#d"},
    ]
    user = [{"type": "fill", "selector": "#b"}]
    out = dedup_against(discovered, user)
    assert [s["selector"] for s in out] == ["#a", "#c", "#d"]


def test_dedup_against_empty_user_list_returns_full_discovered() -> None:
    discovered = [
        {"type": "fill", "selector": "#a"},
        {"type": "click", "selector": "#b"},
    ]
    assert dedup_against(discovered, []) == discovered
    assert dedup_against(discovered, None) == discovered  # type: ignore[arg-type]


def test_dedup_against_empty_discovered_returns_empty() -> None:
    user = [{"type": "fill", "selector": "#a"}]
    assert dedup_against([], user) == []
    assert dedup_against(None, user) == []  # type: ignore[arg-type]
