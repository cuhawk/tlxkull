"""Tests for AuthzFlipper — Phase 7K.2 (middleware + override-dict)."""
from __future__ import annotations

from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from modules.mock_backend.core.authz_flipper import (
    AuthzFlipper,
    AuthzFlipResult,
    _flip_value,
    _patch_field,
)


def _build_app() -> FastAPI:
    app = FastAPI()

    @app.get("/api/me")
    def me() -> dict:
        return {"role": "viewer"}

    @app.post("/api/me")
    def me_post() -> dict:
        return {"role": "viewer"}

    @app.get("/api/other")
    def other() -> dict:
        return {"k": "v"}

    return app


class _FakePage:
    def __init__(self, htmls: list[str]) -> None:
        self._htmls = list(htmls)
        self.reloads = 0

    def reload(self, **kw: Any) -> None:
        self.reloads += 1

    def evaluate(self, script: str) -> str:
        return self._htmls.pop(0) if self._htmls else ""


def test_flip_value_bool() -> None:
    assert _flip_value(True) is False
    assert _flip_value(False) is True


def test_flip_value_string_role() -> None:
    assert _flip_value("user") == "admin"
    assert _flip_value("viewer") == "admin"
    assert _flip_value("guest") == "admin"


def test_flip_value_int_or_with_0xFFFF() -> None:
    assert _flip_value(0) == 0xFFFF
    assert _flip_value(1) == 0xFFFF
    assert _flip_value(0xFF00) == 0xFFFF


def test_patch_field_nested() -> None:
    body = {"user": {"role": "viewer", "active": True}}
    out = _patch_field(body, "user.role", "admin")
    assert out["user"]["role"] == "admin"
    assert body["user"]["role"] == "viewer"


@pytest.mark.asyncio
async def test_flip_returns_result_with_diff() -> None:
    app = _build_app()
    page = _FakePage(["<div>viewer</div>", "<div>admin</div>"])
    f = AuthzFlipper(app)
    result = await f.flip(
        page=page, route="/api/me",
        response_body={"role": "viewer"}, field="role",
    )
    assert isinstance(result, AuthzFlipResult)
    assert result.original_value == "viewer"
    assert result.flipped_value == "admin"
    assert result.ui_diff
    assert "viewer" in result.ui_diff
    assert "admin" in result.ui_diff


@pytest.mark.asyncio
async def test_flip_with_bool_field() -> None:
    app = _build_app()
    page = _FakePage(["<x/>", "<y/>"])
    f = AuthzFlipper(app)
    result = await f.flip(page, "/api/me", {"is_admin": False}, "is_admin")
    assert result.original_value is False
    assert result.flipped_value is True


@pytest.mark.asyncio
async def test_flip_with_int_flag_field() -> None:
    app = _build_app()
    page = _FakePage(["<x/>", "<y/>"])
    f = AuthzFlipper(app)
    result = await f.flip(page, "/api/me", {"perm": 0}, "perm")
    assert result.flipped_value == 0xFFFF


@pytest.mark.asyncio
async def test_flip_normalizes_route_leading_slash() -> None:
    app = _build_app()
    page = _FakePage(["<x/>", "<y/>"])
    f = AuthzFlipper(app)
    result = await f.flip(page, "api/me", {"role": "user"}, "role")
    assert result.route == "/api/me"


@pytest.mark.asyncio
async def test_flip_ui_diff_nonempty_when_dom_changes() -> None:
    app = _build_app()
    page = _FakePage([
        "<div>You are: viewer</div>",
        "<div>You are: admin</div>",
    ])
    f = AuthzFlipper(app)
    result = await f.flip(page, "/api/me", {"role": "viewer"}, "role")
    assert result.ui_diff.strip()


@pytest.mark.asyncio
async def test_flip_overrides_dict_during_call_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _build_app()
    page = _FakePage(["<a/>", "<b/>"])
    f = AuthzFlipper(app)
    captured: dict = {}

    def _spy_reload(self: Any, p: Any) -> None:
        captured["overrides"] = dict(f._overrides)

    monkeypatch.setattr(AuthzFlipper, "_reload", _spy_reload)
    await f.flip(page, "/api/me", {"role": "viewer"}, "role")
    assert ("GET", "/api/me") in captured["overrides"]
    assert captured["overrides"][("GET", "/api/me")] == {"role": "admin"}
    assert f._overrides == {}


@pytest.mark.asyncio
async def test_flip_leaves_overrides_dict_empty() -> None:
    app = _build_app()
    page = _FakePage(["<a/>", "<b/>"])
    f = AuthzFlipper(app)
    await f.flip(page, "/api/me", {"role": "user"}, "role")
    assert f._overrides == {}


def test_middleware_passes_through_when_no_override() -> None:
    app = _build_app()
    AuthzFlipper(app)
    client = TestClient(app)
    r = client.get("/api/me")
    assert r.status_code == 200
    assert r.json() == {"role": "viewer"}


def test_middleware_returns_flipped_body_when_override_set() -> None:
    app = _build_app()
    flipper = AuthzFlipper(app)
    flipper._overrides[("GET", "/api/me")] = {"role": "admin"}
    client = TestClient(app)
    r = client.get("/api/me")
    assert r.status_code == 200
    assert r.json() == {"role": "admin"}


@pytest.mark.asyncio
async def test_flip_supports_post_method() -> None:
    app = _build_app()
    page = _FakePage(["<a/>", "<b/>"])
    f = AuthzFlipper(app)
    f._overrides[("POST", "/api/me")] = {"role": "admin"}
    client = TestClient(app)
    r = client.post("/api/me")
    assert r.status_code == 200
    assert r.json() == {"role": "admin"}
    f._overrides.pop(("POST", "/api/me"), None)
    r2 = client.post("/api/me")
    assert r2.json() == {"role": "viewer"}


def test_concurrent_flips_on_different_routes_independent() -> None:
    app = _build_app()
    flipper = AuthzFlipper(app)
    flipper._overrides[("GET", "/api/me")] = {"role": "admin"}
    flipper._overrides[("GET", "/api/other")] = {"k": "FLIPPED"}
    client = TestClient(app)
    assert client.get("/api/me").json() == {"role": "admin"}
    assert client.get("/api/other").json() == {"k": "FLIPPED"}
    flipper._overrides.pop(("GET", "/api/me"), None)
    assert client.get("/api/me").json() == {"role": "viewer"}
    assert client.get("/api/other").json() == {"k": "FLIPPED"}


def test_multiple_flippers_each_guard_own_dict() -> None:
    app = _build_app()
    f1 = AuthzFlipper(app)
    f2 = AuthzFlipper(app)
    assert f1._overrides is not f2._overrides
    f1._overrides[("GET", "/api/me")] = {"role": "from_f1"}
    client = TestClient(app)
    r = client.get("/api/me")
    assert r.json() == {"role": "from_f1"}
