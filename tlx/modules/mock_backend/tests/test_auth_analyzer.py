"""Tests for AuthAnalyzer — Phase 7D Task 3."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pytest

from modules.mock_backend.core.auth_analyzer import (
    AuthAnalyzer,
    AuthObservation,
    record_auth_observations,
)
from modules.mock_backend.core.reporter import init_session_db


class _FakeContext:
    def __init__(self, cookies: list[dict]) -> None:
        self._cookies = cookies

    def cookies(self) -> list[dict]:
        return list(self._cookies)


class _FakePage:
    def __init__(
        self,
        storage: dict[str, dict[str, str]] | None = None,
        cookies: list[dict] | None = None,
        request_headers: list[dict] | None = None,
        console_msgs: list[str] | None = None,
    ) -> None:
        self._storage = storage or {}
        self._handlers: dict[str, list] = {}
        self.context = _FakeContext(cookies or [])
        self._request_headers = request_headers or []
        self._console_msgs = console_msgs or []

    def on(self, ev: str, handler: Any) -> None:
        self._handlers.setdefault(ev, []).append(handler)

    def goto(self, url: str, **kw: Any) -> None:
        for h in self._request_headers:
            req = type("R", (), {"url": url, "headers": h})()
            for fn in self._handlers.get("request", []):
                fn(req)
        for text in self._console_msgs:
            msg = type("M", (), {"text": text})()
            for fn in self._handlers.get("console", []):
                fn(msg)

    def wait_for_timeout(self, ms: int) -> None:
        return None

    def evaluate(self, script: str, kind: str | None = None) -> Any:
        if "kind" in script and kind in ("localStorage", "sessionStorage"):
            store = self._storage.get(kind, {})
            return [[k, v] for k, v in store.items()]
        return None


@pytest.mark.asyncio
async def test_observe_returns_list_of_auth_observations():
    page = _FakePage()
    a = AuthAnalyzer(page)
    out = await a.observe("http://x/", duration_ms=1)
    assert isinstance(out, list)


@pytest.mark.asyncio
async def test_jwt_in_console_detected_as_observation():
    jwt = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.signature_xx"
    page = _FakePage(console_msgs=[f"got token: {jwt}"])
    a = AuthAnalyzer(page)
    out = await a.observe("http://x/", duration_ms=1)
    jwt_obs = [o for o in out if o.kind == "postmessage_token"]
    assert jwt_obs
    assert jwt_obs[0].value_snippet.startswith("eyJ")


@pytest.mark.asyncio
async def test_localstorage_item_captured():
    page = _FakePage(storage={"localStorage": {"jwt": "abcd1234"}})
    a = AuthAnalyzer(page)
    out = await a.observe("http://x/", duration_ms=1)
    ls = [o for o in out if o.kind == "localStorage"]
    assert ls
    assert ls[0].key == "jwt"
    assert ls[0].value_snippet == "abcd1234"


@pytest.mark.asyncio
async def test_sessionstorage_item_captured():
    page = _FakePage(storage={"sessionStorage": {"sid": "ZZZZ"}})
    a = AuthAnalyzer(page)
    out = await a.observe("http://x/", duration_ms=1)
    ss = [o for o in out if o.kind == "sessionStorage"]
    assert ss and ss[0].key == "sid"


@pytest.mark.asyncio
async def test_cookie_captured_from_context():
    page = _FakePage(cookies=[{"name": "session", "value": "deadbeef"}])
    a = AuthAnalyzer(page)
    out = await a.observe("http://x/", duration_ms=1)
    ck = [o for o in out if o.kind == "cookie"]
    assert ck and ck[0].key == "session"
    assert ck[0].value_snippet == "deadbeef"


@pytest.mark.asyncio
async def test_request_authorization_header_captured():
    page = _FakePage(
        request_headers=[{"authorization": "Bearer abc.def.ghi"}]
    )
    a = AuthAnalyzer(page)
    out = await a.observe("http://x/", duration_ms=1)
    hdr = [o for o in out if o.kind == "header"]
    assert hdr and hdr[0].key == "authorization"


@pytest.mark.asyncio
async def test_value_snippet_capped_at_32_chars():
    long = "x" * 200
    page = _FakePage(storage={"localStorage": {"k": long}})
    a = AuthAnalyzer(page)
    out = await a.observe("http://x/", duration_ms=1)
    ls = [o for o in out if o.kind == "localStorage"]
    assert ls
    assert len(ls[0].value_snippet) == 32


def test_mock_auth_obs_table_created_on_init_db(tmp_path: Path):
    db_path = tmp_path / "mb.db"
    conn = init_session_db(db_path)
    try:
        cols = {
            r[1] for r in conn.execute(
                "PRAGMA table_info(mock_auth_obs)"
            ).fetchall()
        }
    finally:
        conn.close()
    assert {"id", "session_id", "kind", "key", "value_snippet",
            "observed_at"}.issubset(cols)


def test_record_auth_observations_persists_rows(tmp_path: Path):
    db_path = tmp_path / "mb.db"
    init_session_db(db_path).close()
    conn = sqlite3.connect(str(db_path))
    try:
        n = record_auth_observations(
            conn, "s1",
            [AuthObservation(
                kind="localStorage", key="jwt",
                value_snippet="x" * 32, timestamp_ms=1.0,
            )],
        )
        assert n == 1
        rows = conn.execute(
            "SELECT kind, key FROM mock_auth_obs WHERE session_id='s1'"
        ).fetchall()
        assert rows == [("localStorage", "jwt")]
    finally:
        conn.close()
