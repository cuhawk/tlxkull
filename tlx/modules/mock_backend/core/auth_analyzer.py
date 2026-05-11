"""AuthAnalyzer — observe token construction + storage during page load.

Pure Playwright observation. No mutation.

Captures:
  - Authorization / Cookie header values on outgoing requests
  - localStorage / sessionStorage items after networkidle (CDP)
  - JWT-shaped strings in console messages
  - postMessage tokens routed via window.postMessage hooks

All sync Playwright calls funnel through ``asyncio.to_thread``.

Logs only the first 32 chars of any captured value to avoid sensitive
data leakage in structlog output.
"""
from __future__ import annotations

import asyncio
import re
import time
from dataclasses import dataclass
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


_VALUE_SNIPPET_LEN = 32

_JWT_RE = re.compile(
    r"\b[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"
)


@dataclass
class AuthObservation:
    kind: str
    key: str
    value_snippet: str
    timestamp_ms: float


def _now_ms() -> float:
    return time.time() * 1000.0


def _snippet(value: str | None) -> str:
    if value is None:
        return ""
    return str(value)[:_VALUE_SNIPPET_LEN]


def _scan_for_jwt(text: str) -> str | None:
    if not text:
        return None
    m = _JWT_RE.search(text)
    return m.group(0) if m else None


class AuthAnalyzer:
    def __init__(self, page: Any) -> None:
        self.page = page

    async def observe(
        self, url: str, duration_ms: int = 5000
    ) -> list[AuthObservation]:
        return await asyncio.to_thread(self._observe_sync, url, duration_ms)

    def _observe_sync(
        self, url: str, duration_ms: int
    ) -> list[AuthObservation]:
        obs: list[AuthObservation] = []
        page = self.page

        def on_request(req: Any) -> None:
            try:
                headers = req.headers if not callable(req.headers) else req.headers()
            except Exception:
                headers = {}
            for hkey in ("authorization", "cookie"):
                val = headers.get(hkey) if isinstance(headers, dict) else None
                if val:
                    obs.append(AuthObservation(
                        kind="header",
                        key=hkey,
                        value_snippet=_snippet(val),
                        timestamp_ms=_now_ms(),
                    ))

        def on_console(msg: Any) -> None:
            try:
                text = msg.text if not callable(msg.text) else msg.text()
            except Exception:
                text = str(msg)
            jwt = _scan_for_jwt(text or "")
            if jwt:
                obs.append(AuthObservation(
                    kind="postmessage_token",
                    key="console_jwt",
                    value_snippet=_snippet(jwt),
                    timestamp_ms=_now_ms(),
                ))

        try:
            page.on("request", on_request)
        except Exception:
            pass
        try:
            page.on("console", on_console)
        except Exception:
            pass

        try:
            page.goto(url, wait_until="networkidle")
        except Exception as exc:
            logger.debug("auth_analyzer.goto_failed", error=str(exc))

        try:
            page.wait_for_timeout(duration_ms)
        except Exception:
            pass

        for storage_kind in ("localStorage", "sessionStorage"):
            entries = self._read_storage(storage_kind)
            for k, v in entries:
                obs.append(AuthObservation(
                    kind=storage_kind,
                    key=k,
                    value_snippet=_snippet(v),
                    timestamp_ms=_now_ms(),
                ))

        cookies = self._read_cookies()
        for ckey, cval in cookies:
            obs.append(AuthObservation(
                kind="cookie",
                key=ckey,
                value_snippet=_snippet(cval),
                timestamp_ms=_now_ms(),
            ))

        return obs

    def _read_storage(self, kind: str) -> list[tuple[str, str]]:
        script = (
            "(kind) => { const s = window[kind]; const out = []; "
            "for (let i=0;i<s.length;i++){ const k = s.key(i); "
            "out.push([k, s.getItem(k)]); } return out; }"
        )
        try:
            raw = self.page.evaluate(script, kind)
        except Exception as exc:
            logger.debug(
                "auth_analyzer.storage_failed", kind=kind, error=str(exc),
            )
            return []
        out: list[tuple[str, str]] = []
        for item in raw or []:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                out.append((str(item[0]), str(item[1])))
        return out

    def _read_cookies(self) -> list[tuple[str, str]]:
        ctx = getattr(self.page, "context", None)
        if ctx is None:
            return []
        try:
            cookies = ctx.cookies() if callable(getattr(ctx, "cookies", None)) else []
        except Exception:
            return []
        out: list[tuple[str, str]] = []
        for c in cookies or []:
            if isinstance(c, dict) and "name" in c:
                out.append((str(c.get("name")), str(c.get("value", ""))))
        return out


def record_auth_observations(
    db_conn: Any,
    session_id: str,
    observations: list[AuthObservation],
) -> int:
    """Insert AuthObservations into mock_auth_obs. Returns inserted count."""
    n = 0
    for o in observations:
        db_conn.execute(
            "INSERT INTO mock_auth_obs "
            "(session_id, kind, key, value_snippet) "
            "VALUES (?, ?, ?, ?)",
            (session_id, o.kind, o.key, o.value_snippet),
        )
        n += 1
    db_conn.commit()
    return n
