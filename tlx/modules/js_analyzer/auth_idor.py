"""IDOR + state-desync detectors.

Plan: plans/ARCHITECTURE_EVOLUTION_V2.md §23.4d / §23.4e.

Two complementary heuristics:

1. **IDOR API over-fetch detector** — flags fetch/axios calls that
   return more data than the downstream code reads. The pattern is
   ``response.data.users`` (all-users) consumed by a UI that only
   renders the current user; the bug class is "the API hands back every
   user object, the client picks one — bypass by reading the others".

2. **State-desync detector** — flags chains whose end-sink reads
   client-side auth state (e.g. ``user.isAdmin``) but the path contains
   no fetch / RPC re-verification. The bug class is "feature flag is
   purely client-side; flip the redux store value via DevTools to
   bypass".

Both run against the per-target snapshot DB and write to
``chains/idor.jsonl`` + ``chains/state_desync.jsonl``. Off by default;
enabled via ``JS_ENABLE_AUTH_ABUSE=1`` together with the existing
``v2.auth_abuse`` stage.
"""
from __future__ import annotations

import json
import re
import sqlite3
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path


__all__ = ["detect_idor", "detect_state_desync", "write_sidecars"]


# ---------------------------------------------------------------------------
# IDOR over-fetch detector
# ---------------------------------------------------------------------------

# API call sites that return collections of records.
_COLLECTION_FETCH_RE = re.compile(
    r"\b(?:fetch|axios|api|http)\s*(?:\.[a-z]+)?\s*\("
    r"\s*[`'\"][^`'\"]*?(?P<endpoint>/(?:users?|members?|orgs?|"
    r"accounts?|customers?|teams?|projects?|tenants?|sessions?|"
    r"comments?|posts?|messages?|tickets?|invoices?|payments?|"
    r"orders?))\b",
    re.IGNORECASE,
)

# Indices that strongly suggest the result is consumed as a collection
# but indexed to one element — over-fetch tell-tale.
_COLLECTION_INDEX_RE = re.compile(
    r"(?:response|resp|res|data|result)"
    r"(?:\.(?:data|body|users|members|results|items|records))*"
    r"(?:\.find\s*\(|\.filter\s*\(|\[\s*(?:0|\d+|user\.?id)\s*\]"
    r"|\.\s*find\s*\()",
    re.IGNORECASE,
)


@dataclass
class IDORFinding:
    file: str
    line: int
    endpoint: str
    raw: str
    confidence: float
    rationale: str


def detect_idor(conn: sqlite3.Connection) -> list[IDORFinding]:
    """Return one IDORFinding per (file, line) where a collection-shaped
    endpoint is consumed via single-element indexing.
    """
    rows = conn.execute(
        "SELECT n.file, e.line, e.raw "
        "FROM edges e JOIN nodes n ON n.id = e.caller_id "
        "WHERE e.raw IS NOT NULL"
    ).fetchall()
    findings: list[IDORFinding] = []
    seen: set[tuple[str, int]] = set()
    for file, line, raw in rows:
        if not raw:
            continue
        m = _COLLECTION_FETCH_RE.search(raw)
        if not m:
            continue
        ep = m.group("endpoint")
        # Look for a single-element index on the same line; the AST
        # extractor doesn't capture multi-line edges so this is
        # intentionally conservative.
        if not _COLLECTION_INDEX_RE.search(raw):
            continue
        key = (file or "", int(line or 0))
        if key in seen:
            continue
        seen.add(key)
        findings.append(
            IDORFinding(
                file=file or "",
                line=int(line or 0),
                endpoint=ep,
                raw=raw[:240],
                confidence=0.55,
                rationale="collection endpoint indexed to a single record",
            )
        )
    return findings


# ---------------------------------------------------------------------------
# State-desync detector
# ---------------------------------------------------------------------------

_AUTH_STATE_READ_RE = re.compile(
    r"\b(?:user|currentUser|me|session|auth)\."
    r"(?:isAdmin|isAuthenticated|isOwner|isStaff|isSuperuser|"
    r"permissions|roles|role|canAccess|hasPermission)\b",
    re.IGNORECASE,
)

_SERVER_VERIFY_RE = re.compile(
    r"\b(?:fetch|axios|api|http|grpc)\s*\(",
    re.IGNORECASE,
)

# Chain "ends" at a sensitive action: navigation / state-write /
# privileged effect.
_SENSITIVE_ACTION_RE = re.compile(
    r"\b(?:Router\.(?:push|replace)|navigate\s*\(|location\.assign|"
    r"location\.href\s*=|"
    r"setState\s*\(\s*\{[^}]*(?:admin|owner|elevated|superuser)|"
    r"dispatch\s*\(\s*\{[^}]*type\s*[:=]\s*['\"](?:GRANT|UPDATE|DELETE|"
    r"ADMIN|ELEVATE))",
    re.IGNORECASE,
)


@dataclass
class StateDesyncFinding:
    auth_read_file: str
    auth_read_line: int
    action_file: str
    action_line: int
    function_qname: str
    confidence: float
    rationale: str
    raw_action: str


def detect_state_desync(conn: sqlite3.Connection) -> list[StateDesyncFinding]:
    """For each function (nodes row), inspect every edge raw text inside
    the function body. If it contains both an auth-state read AND a
    sensitive action AND no fetch/axios in between, flag the function.
    """
    # Group edges by caller_id (function).
    edges_by_caller: dict[int, list[tuple[int, str]]] = defaultdict(list)
    rows = conn.execute(
        "SELECT caller_id, line, raw FROM edges WHERE raw IS NOT NULL "
        "ORDER BY caller_id, line"
    ).fetchall()
    for cid, line, raw in rows:
        if cid is None or raw is None:
            continue
        edges_by_caller[int(cid)].append((int(line or 0), raw))
    if not edges_by_caller:
        return []

    nodes = {nid: (qname, file) for nid, qname, file in conn.execute(
        "SELECT id, qualified_name, file FROM nodes"
    )}

    findings: list[StateDesyncFinding] = []
    for caller_id, lines in edges_by_caller.items():
        auth_read: tuple[int, str] | None = None
        server_after_read = False
        for ln, raw in lines:
            if auth_read is None:
                if _AUTH_STATE_READ_RE.search(raw):
                    auth_read = (ln, raw)
                continue
            if _SERVER_VERIFY_RE.search(raw):
                server_after_read = True
                continue
            if _SENSITIVE_ACTION_RE.search(raw):
                if server_after_read:
                    continue
                qname, file = nodes.get(caller_id, ("?", ""))
                findings.append(
                    StateDesyncFinding(
                        auth_read_file=file or "",
                        auth_read_line=auth_read[0],
                        action_file=file or "",
                        action_line=ln,
                        function_qname=qname,
                        confidence=0.6,
                        rationale=(
                            "client-side auth state read on line "
                            f"{auth_read[0]} followed by sensitive "
                            f"action on line {ln} with no server "
                            "verification between them"
                        ),
                        raw_action=raw[:240],
                    )
                )
                break
    return findings


# ---------------------------------------------------------------------------
# Sidecar writers
# ---------------------------------------------------------------------------


def write_sidecars(
    target_dir: Path,
    idor: list[IDORFinding],
    state_desync: list[StateDesyncFinding],
) -> dict:
    out_dir = target_dir / "chains"
    out_dir.mkdir(parents=True, exist_ok=True)
    idor_p = out_dir / "idor.jsonl"
    desync_p = out_dir / "state_desync.jsonl"
    idor_p.write_text(
        "\n".join(json.dumps({"kind": "idor", **asdict(f)}) for f in idor)
        + ("\n" if idor else "")
    )
    desync_p.write_text(
        "\n".join(json.dumps({"kind": "state_desync", **asdict(f)}) for f in state_desync)
        + ("\n" if state_desync else "")
    )
    return {
        "idor_rows": len(idor),
        "state_desync_rows": len(state_desync),
        "outputs": {"idor": str(idor_p), "state_desync": str(desync_p)},
    }
