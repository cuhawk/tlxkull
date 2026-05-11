"""Slash command dispatch for /mock-backend."""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from kernel.slash import SlashCommand

from .tools.mock_auth import mock_auth_async
from .tools.mock_authz import mock_authz_async
from .tools.mock_confirm import (
    load_chains,
    mock_confirm_async,
)
from .tools.mock_observe import mock_observe_async
from .tools.mock_probe import mock_probe_async
from .tools.mock_record import mock_record_async
from .tools.mock_run import mock_run_async
from .tools.mock_start import mock_start_async, mock_stop_async

_HELP = (
    "/mock-backend usage:\n"
    "  /mock-backend extract <target_dir>      — extract routes + scaffold (7A)\n"
    "  /mock-backend export <session_id> <fmt> [--host <host>]\n"
    "                                          — formats: "
    "openapi|ffuf|burp|hidden\n"
    "  /mock-backend confirm <session_id> [chain_id]\n"
    "                                          — run sink confirmation (7B)\n"
    "  /mock-backend run    <session_id>       — batch chain confirmation (7C)\n"
    "  /mock-backend status <session_id>       — chain confirmation summary (7C)\n"
    "  /mock-backend report <session_id> [--format text|json]\n"
    "                                          — finding report (7C)\n"
    "  /mock-backend probe  <session_id> [--auto] [--interactions FILE]\n"
    "                                          — execution-driven discovery "
    "(7D + auto-explore 7I)\n"
    "  /mock-backend record <session_id> <method> <path> "
    "[--body-file PATH | --body-stdin | <body_json>] [--status N]\n"
    "                                          — store a response in mock_flow "
    "(manual override; usually unnecessary after /probe)\n"
    "  /mock-backend start  <session_id> [port] [--ad-hoc]\n"
    "                                          — boot mock server "
    "(--ad-hoc creates session if unknown)\n"
    "  /mock-backend stop   <session_id>       — shutdown mock server (7D)\n"
    "  /mock-backend authz  <session_id> <route> <field>\n"
    "                                          — flip role/flag and diff (7D)\n"
    "  /mock-backend auth   <session_id> <url> — observe tokens (7D)\n"
    "  /mock-backend observe <session_id> <url> [--duration MS]\n"
    "                                          — observe SW/WS traffic"
)


def _run_k(kernel: Any, coro: Any) -> Any:
    return _run(coro, kernel)


def _run(coro: Any, kernel: Any = None) -> Any:
    """Execute coroutine on the long-running mock_backend bg loop.

    Slash-command dispatch is sync; using ``asyncio.run`` per call
    would kill any uvicorn server we booted between mock_start and
    mock_stop. The bg loop persists for the kernel lifetime.
    """
    if kernel is not None:
        from .tools.mock_start import _bg_loop
        loop = _bg_loop(kernel)
        fut = asyncio.run_coroutine_threadsafe(coro, loop)
        return fut.result()

    try:
        existing = asyncio.get_event_loop()
        if existing.is_running():
            import nest_asyncio  # type: ignore[import-not-found]
            nest_asyncio.apply(existing)
            return existing.run_until_complete(coro)
    except RuntimeError:
        pass
    return asyncio.run(coro)


def _format_confirm_row(chain_id: str, sink_type: str, confirmed: bool) -> str:
    mark = "✓" if confirmed else "✗"
    return f"  {chain_id:>4} | {sink_type:<24} | {mark}"


def _handle_confirm(rest: list[str], kernel: Any) -> str:
    if not rest:
        return "usage: /mock-backend confirm <session_id> [chain_id]"
    session_id = rest[0]

    if len(rest) >= 2:
        payload = _run_k(kernel, mock_confirm_async(kernel, session_id, rest[1]))
        return json.dumps(payload, indent=2)

    cg = kernel.services.get("js_analyzer_callgraph")
    if cg is None:
        return "[/mock-backend confirm] js_analyzer not initialised"
    chains = load_chains(cg)
    if not chains:
        return f"[/mock-backend confirm] no chains found for session {session_id}"

    chain_by_id = {
        str(c.get("id") or c.get("chain_id") or ""): c
        for c in chains
    }

    payload = _run_k(kernel, mock_run_async(kernel, session_id))
    if "error" in payload:
        return f"[/mock-backend confirm] {payload['error']}"

    lines = [
        f"chain_id | sink_type                | "
        f"confirmed (session {session_id})"
    ]
    for r in payload.get("results", []):
        cid = r["chain_id"]
        chain = chain_by_id.get(cid) or {}
        sink_obj = chain.get("sink") or {}
        sink = str(sink_obj.get("taxonomy_id") or "")
        lines.append(_format_confirm_row(
            cid, sink, bool(r["confirmed"])
        ))
    return "\n".join(lines)


def _findings_for(db: Any, session_id: str) -> list[dict]:
    rows = db.execute(
        "SELECT chain_id, confirmed, probe_value, hits_json, created_at "
        "FROM mock_findings WHERE session_id=? ORDER BY confirmed DESC, chain_id",
        (session_id,),
    ).fetchall()
    out: list[dict] = []
    for chain_id, confirmed, probe, hits_json, created_at in rows:
        try:
            hits = json.loads(hits_json) if hits_json else []
        except Exception:
            hits = []
        out.append({
            "chain_id":    chain_id,
            "confirmed":   bool(confirmed),
            "probe_value": probe or "",
            "hits":        hits,
            "created_at":  created_at,
        })
    return out


def _last_session_meta(db: Any, session_id: str) -> tuple[str, int]:
    row = db.execute(
        "SELECT MAX(created_at) FROM mock_findings WHERE session_id=?",
        (session_id,),
    ).fetchone()
    last = (row[0] if row else None) or "never"
    port_row = db.execute(
        "SELECT port FROM mock_sessions WHERE id=?", (session_id,),
    ).fetchone()
    port = int(port_row[0]) if port_row and port_row[0] else 0
    return last, port


def _handle_status(rest: list[str], kernel: Any) -> str:
    if not rest:
        return "usage: /mock-backend status <session_id>"
    session_id = rest[0]
    db = kernel.services.get("mock_backend_db")
    if db is None:
        return "[/mock-backend status] mock_backend not registered"

    findings = _findings_for(db, session_id)
    confirmed = sum(1 for f in findings if f["confirmed"])
    total = len(findings)
    last, port = _last_session_meta(db, session_id)
    server = str(port) if port else "—"
    return (
        f"Total chains confirmed: {confirmed} / {total}\n"
        f"Last run: {last}\n"
        f"Server: {server}"
    )


def _hit_top_sink(hits: list[dict]) -> str:
    for h in hits or []:
        if isinstance(h, dict):
            v = h.get("sink_type")
            if v:
                return str(v)
    return "—"


def _handle_report(rest: list[str], kernel: Any) -> str:
    if not rest:
        return "usage: /mock-backend report <session_id> [--format text|json]"
    session_id = rest[0]
    fmt = "text"
    for tok in rest[1:]:
        if tok == "--format":
            continue
        if tok in ("text", "json"):
            fmt = tok

    db = kernel.services.get("mock_backend_db")
    if db is None:
        return "[/mock-backend report] mock_backend not registered"

    findings = _findings_for(db, session_id)

    if fmt == "json":
        return json.dumps(findings, indent=2)

    confirmed = [f for f in findings if f["confirmed"]]
    unconfirmed = [f for f in findings if not f["confirmed"]]

    lines: list[str] = [f"# /mock-backend report — session {session_id}", ""]
    lines.append(f"**confirmed:** {len(confirmed)} / {len(findings)}")
    lines.append("")
    lines.append("| chain_id | sink_type | probe_value | hits |")
    lines.append("|----------|-----------|-------------|------|")
    for f in confirmed + unconfirmed:
        sink = _hit_top_sink(f["hits"])
        lines.append(
            f"| {f['chain_id']} | {sink} | "
            f"{f['probe_value']} | {len(f['hits'])} |"
        )
    if not findings:
        lines.append("| — | — | — | — |")
    return "\n".join(lines)


def _handle_run(rest: list[str], kernel: Any) -> str:
    if not rest:
        return "usage: /mock-backend run <session_id>"
    session_id = rest[0]
    payload = _run_k(kernel, mock_run_async(kernel, session_id))
    return json.dumps(payload, indent=2)


def _handle_start(rest: list[str], kernel: Any) -> str:
    if not rest:
        return "usage: /mock-backend start <session_id> [port] [--ad-hoc]"
    session_id = rest[0]
    port = 0
    ad_hoc = False
    for tok in rest[1:]:
        if tok == "--ad-hoc":
            ad_hoc = True
            continue
        try:
            port = int(tok)
        except ValueError:
            return f"[/mock-backend start] invalid arg: {tok}"
    payload = _run_k(
        kernel, mock_start_async(kernel, session_id, port, ad_hoc=ad_hoc),
    )
    if "error" in payload:
        return f"[/mock-backend start] {payload['error']}"
    suffix = " (already running)" if payload.get("already_running") else ""
    return f"Server running at {payload['url']}{suffix}"


def _handle_stop(rest: list[str], kernel: Any) -> str:
    if not rest:
        return "usage: /mock-backend stop <session_id>"
    payload = _run_k(kernel, mock_stop_async(kernel, rest[0]))
    if payload.get("stopped"):
        return "Server stopped."
    return f"[/mock-backend stop] {payload.get('reason', 'no running server')}"


def _handle_authz(rest: list[str], kernel: Any) -> str:
    if len(rest) < 3:
        return "usage: /mock-backend authz <session_id> <route> <field>"
    payload = _run_k(kernel, mock_authz_async(kernel, rest[0], rest[1], rest[2]))
    if "error" in payload:
        return f"[/mock-backend authz] {payload['error']}"
    diff = payload.get("ui_diff") or "(no DOM change)"
    return (
        f"route:           {payload['route']}\n"
        f"field:           {payload['field']}\n"
        f"original_value:  {payload['original_value']}\n"
        f"flipped_value:   {payload['flipped_value']}\n"
        f"ui_diff:\n{diff}"
    )


def _handle_auth(rest: list[str], kernel: Any) -> str:
    if len(rest) < 2:
        return "usage: /mock-backend auth <session_id> <url>"
    payload = _run_k(kernel, mock_auth_async(kernel, rest[0], rest[1]))
    if "error" in payload:
        return f"[/mock-backend auth] {payload['error']}"
    obs = payload.get("observations") or []
    lines = [f"observations: {payload.get('count', 0)}", ""]
    lines.append("| kind             | key             | value_snippet           |")
    lines.append("|------------------|-----------------|-------------------------|")
    for o in obs:
        lines.append(
            f"| {o.get('kind',''):<16} | {o.get('key',''):<15} | "
            f"{o.get('value_snippet',''):<23} |"
        )
    return "\n".join(lines)


def _parse_probe_args(
    rest: list[str],
) -> tuple[str, str | None, bool]:
    session_id = rest[0]
    interactions_file: str | None = None
    auto = False
    i = 1
    while i < len(rest):
        if rest[i] == "--interactions" and i + 1 < len(rest):
            interactions_file = rest[i + 1]
            i += 2
        elif rest[i] == "--auto":
            auto = True
            i += 1
        else:
            i += 1
    return session_id, interactions_file, auto


def _handle_export(rest: list[str], kernel: Any) -> str:
    if len(rest) < 2:
        return (
            "usage: /mock-backend export <session_id> "
            "<openapi|ffuf|burp|hidden> [--host <host>]"
        )
    sid, fmt = rest[0], rest[1]
    host = "127.0.0.1"
    if "--host" in rest:
        idx = rest.index("--host")
        if idx + 1 < len(rest):
            host = rest[idx + 1]
    cfg = kernel.services.get("mock_backend_config")
    db = kernel.services.get("mock_backend_db")
    if cfg is None or db is None:
        return "[/mock-backend export] mock_backend not registered"
    from .module import _mock_export_handler
    handler = _mock_export_handler(kernel)
    return handler(session_id=sid, format=fmt, host=host)


def _handle_probe(rest: list[str], kernel: Any) -> str:
    if not rest:
        return (
            "usage: /mock-backend probe <session_id> [--auto] "
            "[--interactions interactions.json]"
        )
    session_id, ifile, auto = _parse_probe_args(rest)
    interactions: list[dict] = []
    if ifile:
        try:
            text = Path(ifile).expanduser().read_text(encoding="utf-8")
            data = json.loads(text)
            if isinstance(data, list):
                interactions = [d for d in data if isinstance(d, dict)]
        except (OSError, json.JSONDecodeError) as exc:
            return f"[/mock-backend probe] cannot read {ifile}: {exc}"

    payload = _run_k(
        kernel,
        mock_probe_async(kernel, session_id, interactions, auto=auto),
    )
    if "error" in payload:
        return f"[/mock-backend probe] {payload['error']}"
    unknown_n = payload.get("unknown_interactions_count", 0)
    lines = [
        f"interactions fired: {payload['interactions_fired']}",
        f"sink hits:          {payload['sink_hits_count']}",
        f"new routes:         {payload['new_routes_count']}",
    ]
    if payload.get("auto_explored"):
        lines.append(
            f"auto-added:         {payload.get('auto_added_count', 0)} "
            f"interactions"
        )
    if unknown_n > 0:
        lines.append(f"unknown:            {unknown_n}")
        for u in payload.get("unknown_interactions", []):
            t = u.get("type") if isinstance(u, dict) else u
            lines.append(f"  ! ignored: type={t!r}")
    if payload.get("new_routes"):
        for u in payload["new_routes"]:
            lines.append(f"  - {u}")
    return "\n".join(lines)


def _handle_observe(rest: list[str], kernel: Any) -> str:
    if len(rest) < 2:
        return (
            "usage: /mock-backend observe <session_id> <url> "
            "[--duration MS]"
        )
    sid = rest[0]
    url = rest[1]
    duration_ms = 5000
    remaining = rest[2:]
    if "--duration" in remaining:
        idx = remaining.index("--duration")
        if idx + 1 < len(remaining):
            try:
                duration_ms = int(remaining[idx + 1])
            except ValueError:
                return (
                    "[/mock-backend observe] invalid duration: "
                    f"{remaining[idx + 1]}"
                )
    payload = _run_k(
        kernel, mock_observe_async(kernel, sid, url, duration_ms),
    )
    if "error" in payload:
        return f"[/mock-backend observe] {payload['error']}"
    sw = payload.get("sw_observations") or []
    ws = payload.get("ws_frames") or []
    lines = [
        f"sw_count: {payload.get('sw_count', 0)}",
        f"ws_count: {payload.get('ws_count', 0)}",
    ]
    if sw:
        lines.append("")
        lines.append("ServiceWorker registrations:")
        for o in sw[:10]:
            lines.append(
                f"  - scope={o.get('scope', '')} "
                f"script={o.get('script_url', '')}"
            )
    if ws:
        lines.append("")
        lines.append("WebSocket frames:")
        for f in ws[:10]:
            snippet = (f.get("payload_snippet") or "")[:60]
            lines.append(
                f"  [{f.get('direction', '')}] "
                f"{f.get('url', '')}: {snippet}"
            )
    return "\n".join(lines)


_RECORD_USAGE = (
    "usage: /mock-backend record <session_id> <method> <path> "
    "[--body-file PATH | --body-stdin | <body_json>] [--status N]"
)


def _handle_record(rest: list[str], kernel: Any) -> str:
    if len(rest) < 3:
        return _RECORD_USAGE
    sid = rest[0]
    method = rest[1]
    path = rest[2]

    tail = rest[3:]
    body: str | None = None
    body_file: str | None = None
    body_stdin = False
    status = 200
    i = 0
    while i < len(tail):
        tok = tail[i]
        if tok == "--body-file":
            if i + 1 >= len(tail):
                return "[/mock-backend record] --body-file requires PATH"
            body_file = tail[i + 1]
            i += 2
            continue
        if tok == "--body-stdin":
            body_stdin = True
            i += 1
            continue
        if tok == "--status":
            if i + 1 >= len(tail):
                return "[/mock-backend record] --status requires N"
            try:
                status = int(tail[i + 1])
            except ValueError:
                return (
                    "[/mock-backend record] invalid status: "
                    f"{tail[i + 1]}"
                )
            i += 2
            continue
        if body is None:
            body = tok
            i += 1
            continue
        i += 1

    if body_file is not None and body_stdin:
        return (
            "[/mock-backend record] specify only one of "
            "--body-file / --body-stdin"
        )
    if body_file is not None and body is not None:
        return (
            "[/mock-backend record] specify only one of "
            "--body-file / positional body"
        )
    if body_stdin and body is not None:
        return (
            "[/mock-backend record] specify only one of "
            "--body-stdin / positional body"
        )

    if body_file is not None:
        try:
            body = Path(body_file).expanduser().read_text(encoding="utf-8")
        except OSError as exc:
            return f"[/mock-backend record] cannot read {body_file}: {exc}"
    elif body_stdin:
        body = sys.stdin.read()

    if body is None:
        return _RECORD_USAGE

    payload = _run_k(
        kernel,
        mock_record_async(
            kernel,
            session_id=sid,
            method=method,
            path=path,
            response_body=body,
            status_code=status,
        ),
    )
    if "error" in payload:
        return f"[/mock-backend record] {payload['error']}"
    return (
        f"recorded: {payload['method']} {payload['path']} "
        f"(status={payload['status_code']}) for session "
        f"{payload['session_id']}"
    )


def _handle_mock_backend(args: list[str], kernel: Any) -> str:
    if not args:
        return _HELP

    sub = args[0]
    rest = args[1:]

    if sub == "extract":
        if not rest:
            return "usage: /mock-backend extract <target_dir>"
        tool = kernel.tools.get("mock_extract")
        if tool is None:
            return "[/mock-backend] mock_extract tool missing"
        return tool.handler(target_dir=rest[0])

    if sub == "export":
        return _handle_export(rest, kernel)

    if sub == "confirm":
        return _handle_confirm(rest, kernel)

    if sub == "run":
        return _handle_run(rest, kernel)

    if sub == "status":
        return _handle_status(rest, kernel)

    if sub == "report":
        return _handle_report(rest, kernel)

    if sub == "start":
        return _handle_start(rest, kernel)

    if sub == "stop":
        return _handle_stop(rest, kernel)

    if sub == "authz":
        return _handle_authz(rest, kernel)

    if sub == "auth":
        return _handle_auth(rest, kernel)

    if sub == "probe":
        return _handle_probe(rest, kernel)

    if sub == "record":
        return _handle_record(rest, kernel)

    if sub == "observe":
        return _handle_observe(rest, kernel)

    return f"[/mock-backend] unknown subcommand: {sub}\n\n{_HELP}"


def _slash_handler(args: str, kernel: Any) -> str:
    parts = args.split() if args else []
    return _handle_mock_backend(parts, kernel)


def register_slash_commands(kernel: Any) -> None:
    kernel.defer_slash_register(SlashCommand(
        name="mock-backend",
        description=(
            "extract API routes + DOM scaffold from js_analyzer-indexed "
            "targets. Subcommands: extract, export, confirm, run, status, "
            "report, probe, record, start, stop, authz, auth, observe."
        ),
        handler=_slash_handler,
    ))
