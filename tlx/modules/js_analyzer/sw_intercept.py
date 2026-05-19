"""Service Worker fetch interception + cache taint modeling.

Plan: plans/ARCHITECTURE_EVOLUTION_V2.md §24.4c / §24.4d / §24.8.

Builds on top of v2/worker_semantics.py (which discovers worker pairs
and message channels) by adding three semantic layers:

  1. **Fetch-handler interception** — every ``self.addEventListener
     ("fetch", ev => ...)`` registered inside a Service-Worker file is a
     network-rewrite primitive. The handler body classifies into:
       - ``passthrough`` — calls ``fetch(ev.request)`` and replies.
       - ``cache_first``  — ``caches.match(...)`` first, then network.
       - ``network_first``— fetch first, falls back to cache.
       - ``rewrite``      — replies with a different URL / body.
       - ``inject``       — replies with attacker-controlled HTML/JS.
     ``rewrite`` and ``inject`` are the bug-bounty primitives.

  2. **Cache taint** — every ``cache.put(req, response)`` where
     ``response`` carries a tainted body OR ``request`` URL is attacker
     controlled persists attacker content in the Cache API. Future
     fetches against that origin return the poisoned response.

  3. **Message origin validation** — ``self.addEventListener("message",
     ev => ...)`` handlers gated by ``ev.origin === ...`` or unguarded.
     Unguarded SW message handlers are post-message-into-SW XSS
     vectors.

Output tables:
  - sw_fetch_handlers
  - sw_cache_writes
  - sw_message_origin

Driver: bin/sw_intercept.py
"""
from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path


__all__ = ["run", "discover_handlers", "discover_cache_writes",
           "discover_message_origin", "ensure_schema"]


_CREATE_SCHEMA = """
CREATE TABLE IF NOT EXISTS sw_fetch_handlers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id         INTEGER NOT NULL,
    handler_class   TEXT NOT NULL,    -- passthrough|cache_first|network_first|rewrite|inject|unknown
    has_url_rewrite INTEGER NOT NULL DEFAULT 0,
    has_html_inject INTEGER NOT NULL DEFAULT 0,
    has_origin_check INTEGER NOT NULL DEFAULT 0,
    rationale       TEXT,
    file            TEXT,
    line            INTEGER
);

CREATE TABLE IF NOT EXISTS sw_cache_writes (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id       INTEGER NOT NULL,
    cache_name    TEXT,
    request_origin TEXT,             -- 'attacker_controlled' | 'same_origin' | 'unknown'
    response_source TEXT,            -- 'fetch_response' | 'constructed' | 'unknown'
    file          TEXT,
    line          INTEGER
);

CREATE TABLE IF NOT EXISTS sw_message_origin (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id       INTEGER NOT NULL,
    has_origin_check INTEGER NOT NULL DEFAULT 0,
    origin_pattern TEXT,             -- substring of the comparison
    handler_class TEXT,              -- 'message' | 'install' | 'activate' | 'sync' | 'push'
    file          TEXT,
    line          INTEGER
);
"""


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(_CREATE_SCHEMA)


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

# Worker / SW files: we detect "SW-ness" by either:
#   * filename contains 'service-worker' / 'sw.js' / 'sw-' / .worker.js
#   * file content has `self.addEventListener(...)` AND references
#     `clients` or `registration`.
_SW_FILENAME_RE = re.compile(
    r"(?:service[-_]?worker|sw[-_.]|worker)\b", re.IGNORECASE
)

_FETCH_HANDLER_RE = re.compile(
    r"""(?:self\.)?addEventListener\s*\(\s*['"]fetch['"]\s*,\s*"""
    r"""(?:async\s*)?(?:function\s*)?\(?[\w$, ]*\)?\s*=>?\s*"""
    r"""(?P<body>\{(?:[^{}]|\{[^{}]*\}){0,8000}\})""",
    re.DOTALL,
)

_RESPOND_WITH_FETCH_RE = re.compile(r"respondWith\s*\(\s*fetch\s*\(", re.IGNORECASE)
_RESPOND_WITH_CACHE_RE = re.compile(r"respondWith\s*\(\s*caches", re.IGNORECASE)
_RESPOND_WITH_NEW_RESP_RE = re.compile(
    r"respondWith\s*\(\s*new\s+Response\s*\(",
    re.IGNORECASE,
)
_URL_REWRITE_RE = re.compile(
    r"\bnew\s+(?:URL|Request)\s*\(|\.\s*replace\s*\(",
    re.IGNORECASE,
)
_HTML_INJECT_RE = re.compile(
    r"<\s*script\b|<\s*iframe\b|new\s+Blob\s*\(\s*\[`?<\s*html",
    re.IGNORECASE,
)
_ORIGIN_CHECK_RE = re.compile(
    r"\b(?:event|ev|e|message)\.origin\s*(?:===|==|!==|!=)\s*",
    re.IGNORECASE,
)

_CACHE_PUT_RE = re.compile(
    r"\bcaches?\b(?:\.[\w$]+)*\.\s*put\s*\(",
    re.IGNORECASE,
)
_CACHE_OPEN_RE = re.compile(
    r"\bcaches\.open\s*\(\s*[`'\"](?P<name>[^`'\"]+)[`'\"]",
    re.IGNORECASE,
)

_MESSAGE_HANDLER_RE = re.compile(
    r"""(?:self\.)?addEventListener\s*\(\s*['"](?P<evt>message|install|activate|sync|push)['"]"""
    r"""\s*,\s*(?:async\s*)?(?:function\s*)?\(?[\w$, ]*\)?\s*=>?\s*"""
    r"""(?P<body>\{(?:[^{}]|\{[^{}]*\}){0,4000}\})""",
    re.DOTALL,
)


def _is_sw_file(file: str | None) -> bool:
    if not file:
        return False
    return bool(_SW_FILENAME_RE.search(Path(file).name))


@dataclass
class _Row:
    node_id: int
    file: str
    line: int


def _candidate_rows(conn: sqlite3.Connection) -> list[tuple[int, str, int, str]]:
    """Return (node_id, file, line, raw) for every edge inside a SW
    file. We use the file-level heuristic since the AST extractor's
    function-level scope is too narrow for SW lifecycle.
    """
    try:
        rows = conn.execute(
            "SELECT e.caller_id, n.file, e.line, e.raw "
            "FROM edges e JOIN nodes n ON n.id = e.caller_id "
            "WHERE e.raw IS NOT NULL"
        ).fetchall()
    except sqlite3.OperationalError:
        return []
    return [
        (cid, file or "", int(line or 0), raw)
        for cid, file, line, raw in rows
        if _is_sw_file(file) and raw
    ]


def _classify_fetch_handler(body: str) -> tuple[str, dict]:
    has_url_rewrite = bool(_URL_REWRITE_RE.search(body))
    has_html_inject = bool(_HTML_INJECT_RE.search(body))
    has_origin = bool(_ORIGIN_CHECK_RE.search(body))
    if has_html_inject:
        cls = "inject"
    elif has_url_rewrite and _RESPOND_WITH_FETCH_RE.search(body):
        cls = "rewrite"
    elif _RESPOND_WITH_NEW_RESP_RE.search(body):
        cls = "rewrite"
    elif _RESPOND_WITH_CACHE_RE.search(body) and _RESPOND_WITH_FETCH_RE.search(body):
        cls = "cache_first"
    elif _RESPOND_WITH_FETCH_RE.search(body):
        cls = "network_first" if _RESPOND_WITH_CACHE_RE.search(body) else "passthrough"
    else:
        cls = "unknown"
    return cls, {
        "has_url_rewrite": has_url_rewrite,
        "has_html_inject": has_html_inject,
        "has_origin_check": has_origin,
    }


def discover_handlers(conn: sqlite3.Connection) -> list[dict]:
    out: list[dict] = []
    seen: set[tuple[int, int]] = set()
    for node_id, file, line, raw in _candidate_rows(conn):
        for m in _FETCH_HANDLER_RE.finditer(raw):
            body = m.group("body")
            cls, flags = _classify_fetch_handler(body)
            rationale = (
                f"SW fetch handler classified as {cls}"
                + (" (URL rewrite present)" if flags["has_url_rewrite"] else "")
                + (" (HTML inject present)" if flags["has_html_inject"] else "")
                + (" (origin check)" if flags["has_origin_check"] else "")
            )
            key = (node_id, line)
            if key in seen:
                continue
            seen.add(key)
            out.append(
                {
                    "node_id": node_id,
                    "handler_class": cls,
                    "has_url_rewrite": int(flags["has_url_rewrite"]),
                    "has_html_inject": int(flags["has_html_inject"]),
                    "has_origin_check": int(flags["has_origin_check"]),
                    "rationale": rationale,
                    "file": file,
                    "line": line,
                }
            )
    return out


def discover_cache_writes(conn: sqlite3.Connection) -> list[dict]:
    out: list[dict] = []
    for node_id, file, line, raw in _candidate_rows(conn):
        if not _CACHE_PUT_RE.search(raw):
            continue
        cache_name = None
        opn = _CACHE_OPEN_RE.search(raw)
        if opn:
            cache_name = opn.group("name")
        # Lightweight origin classification.
        if "event.request" in raw or "ev.request" in raw or "fetchEvent" in raw:
            request_origin = "attacker_controlled"
        elif "new Request" in raw:
            request_origin = "constructed"
        else:
            request_origin = "unknown"
        if "fetch(" in raw or "fetchResponse" in raw:
            response_source = "fetch_response"
        elif "new Response" in raw:
            response_source = "constructed"
        else:
            response_source = "unknown"
        out.append(
            {
                "node_id": node_id,
                "cache_name": cache_name,
                "request_origin": request_origin,
                "response_source": response_source,
                "file": file,
                "line": line,
            }
        )
    return out


def discover_message_origin(conn: sqlite3.Connection) -> list[dict]:
    out: list[dict] = []
    seen: set[tuple[int, int]] = set()
    for node_id, file, line, raw in _candidate_rows(conn):
        for m in _MESSAGE_HANDLER_RE.finditer(raw):
            body = m.group("body")
            evt = m.group("evt")
            origin_match = _ORIGIN_CHECK_RE.search(body)
            origin_pattern = None
            if origin_match:
                # Capture the right-hand side of the comparison
                # heuristically (next 80 chars).
                start = origin_match.end()
                origin_pattern = body[start : start + 80].strip()
            key = (node_id, line)
            if key in seen:
                continue
            seen.add(key)
            out.append(
                {
                    "node_id": node_id,
                    "has_origin_check": int(origin_match is not None),
                    "origin_pattern": origin_pattern,
                    "handler_class": evt,
                    "file": file,
                    "line": line,
                }
            )
    return out


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run(conn: sqlite3.Connection, target_dir: str | Path) -> dict:
    ensure_schema(conn)
    handlers = discover_handlers(conn)
    cache_writes = discover_cache_writes(conn)
    msg_handlers = discover_message_origin(conn)

    # Clear and repopulate (idempotent).
    conn.execute("DELETE FROM sw_fetch_handlers")
    conn.execute("DELETE FROM sw_cache_writes")
    conn.execute("DELETE FROM sw_message_origin")
    cur = conn.cursor()
    for h in handlers:
        cur.execute(
            "INSERT INTO sw_fetch_handlers "
            "(node_id, handler_class, has_url_rewrite, has_html_inject, "
            " has_origin_check, rationale, file, line) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (h["node_id"], h["handler_class"], h["has_url_rewrite"],
             h["has_html_inject"], h["has_origin_check"], h["rationale"],
             h["file"], h["line"]),
        )
    for c in cache_writes:
        cur.execute(
            "INSERT INTO sw_cache_writes "
            "(node_id, cache_name, request_origin, response_source, "
            " file, line) VALUES (?, ?, ?, ?, ?, ?)",
            (c["node_id"], c["cache_name"], c["request_origin"],
             c["response_source"], c["file"], c["line"]),
        )
    for m in msg_handlers:
        cur.execute(
            "INSERT INTO sw_message_origin "
            "(node_id, has_origin_check, origin_pattern, handler_class, "
            " file, line) VALUES (?, ?, ?, ?, ?, ?)",
            (m["node_id"], m["has_origin_check"], m["origin_pattern"],
             m["handler_class"], m["file"], m["line"]),
        )
    conn.commit()

    sidecar = {
        "fetch_handlers": len(handlers),
        "by_handler_class": _count(handlers, "handler_class"),
        "cache_writes": len(cache_writes),
        "by_request_origin": _count(cache_writes, "request_origin"),
        "message_handlers": len(msg_handlers),
        "unvalidated_message_handlers": sum(
            1 for m in msg_handlers if not m["has_origin_check"]
        ),
    }
    out_dir = Path(target_dir) / "v2"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "sw_intercept.json").write_text(json.dumps(sidecar, indent=2))
    return sidecar


def _count(rows: list[dict], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for r in rows:
        k = r.get(key) or "unknown"
        out[k] = out.get(k, 0) + 1
    return out
