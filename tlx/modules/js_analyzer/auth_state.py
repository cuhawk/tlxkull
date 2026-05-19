"""Client-side authorization / state abuse detection.

Plan: plans/ARCHITECTURE_EVOLUTION_V2.md §23.

Detects four overlapping client-side bug classes that today's analyzer
mostly misses:

  * client-side IDOR (API returns more than the UI shows),
  * route-guard bypass (client-only auth checks),
  * permission-state poisoning (attacker-influenced auth state),
  * token misuse (where do JWTs / access tokens live and leak).

Two main outputs:
  * ``auth_state_nodes`` table — every variable / hook / store-slice
    that carries an auth role / identity / token + trust score.
  * ``route_guards`` classification — per route entry, whether the
    guard is client-only / server-validated / mixed.

The auth taxonomy is intentionally narrow: we tag the framework-
canonical entry points (useSession, useAuth0, useUser, NextAuth,
Redux ``auth`` slice, Vuex/Pinia auth modules, Angular AuthService)
plus the cookie + storage entry points already covered by §11.

Behind ``ENABLE_AUTH_ABUSE``.
"""
from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from typing import Iterable

__all__ = [
    "AuthStateNode",
    "RouteGuard",
    "ingest_auth_nodes",
    "classify_route_guard",
    "AUTH_HOOK_PATTERNS",
]


# Patterns that produce an auth state node when found in the AST.
AUTH_HOOK_PATTERNS: list[tuple[str, str, str]] = [
    # (regex, role, source)
    (r"\buseSession\s*\(",           "identity",   "nextauth"),
    (r"\buseAuth0\s*\(",             "identity",   "auth0"),
    (r"\buseUser\s*\(",              "identity",   "hook"),
    (r"\buseCurrentUser\s*\(",       "identity",   "hook"),
    (r"\buseIdentity\s*\(",          "identity",   "hook"),
    (r"\bgetSession\s*\(",           "identity",   "nextauth"),
    (r"\bauth0\.getAccessToken",     "token",      "auth0"),
    (r"\blocalStorage\.getItem\(\s*['\"]token['\"]",          "token", "storage"),
    (r"\blocalStorage\.getItem\(\s*['\"]access_?token['\"]",  "token", "storage"),
    (r"\bcookies\.get\(\s*['\"]session['\"]",                 "identity", "cookie"),
    (r"\bcookies\.get\(\s*['\"]jwt['\"]",                     "token",    "cookie"),
    (r"\bstate\.auth\.user",         "identity",   "redux"),
    (r"\bstate\.auth\.token",        "token",      "redux"),
    (r"\bstore\.auth\.user",         "identity",   "pinia"),
    (r"\bAuthService\.getCurrentUser",  "identity", "angular"),
    (r"\bisAdmin\b",                 "role-claim", "state"),
    (r"\bhasPermission\(",           "permission", "state"),
]


@dataclass(frozen=True)
class AuthStateNode:
    node_id: int
    role: str        # 'identity'|'token'|'role-claim'|'permission'
    source: str      # 'nextauth'|'auth0'|'hook'|'cookie'|'storage'|'redux'|'pinia'|'angular'|'state'
    trust: float     # 0..1; lower = client-only / spoofable
    framework: str | None = None
    derives_from: int | None = None
    consumer_node: int | None = None


_TRUST_BY_SOURCE = {
    "nextauth": 0.7,
    "auth0":    0.7,
    "hook":     0.5,
    "cookie":   0.5,
    "storage":  0.3,
    "redux":    0.3,
    "pinia":    0.3,
    "angular":  0.5,
    "state":    0.2,
}


def ingest_auth_nodes(
    conn: sqlite3.Connection,
    records: Iterable[dict],
) -> int:
    """Populate ``auth_state_nodes`` from AST records.

    The AST extractor stamps each match with ``ast_kind ==
    'auth_state'`` plus ``role``, ``source``, ``framework``,
    ``consumer_node``, ``node_id``. If the extractor hasn't been taught
    auth detection yet, callers can pre-filter by regex over snippets
    and call here with synthesised records.
    """
    cur = conn.cursor()
    inserted = 0
    for rec in records:
        if rec.get("ast_kind") != "auth_state":
            continue
        role = rec.get("role")
        if role not in ("identity", "token", "role-claim", "permission"):
            continue
        source = rec.get("source") or "state"
        trust = float(rec.get("trust") or _TRUST_BY_SOURCE.get(source, 0.3))
        cur.execute(
            """INSERT OR REPLACE INTO auth_state_nodes
               (node_id, role, source, framework, trust,
                derives_from, consumer_node)
               VALUES (?,?,?,?,?,?,?)""",
            (rec.get("node_id") or 0,
             role,
             source,
             rec.get("framework"),
             trust,
             rec.get("derives_from"),
             rec.get("consumer_node")),
        )
        inserted += cur.rowcount
    conn.commit()
    return inserted


# ──────────────────────────────────────────────────────────────────────
# Route-guard classification (§23.6)
# ──────────────────────────────────────────────────────────────────────

@dataclass
class RouteGuard:
    route_path: str
    kind: str   # 'client-only' | 'server-validated' | 'mixed' | 'none'
    guard_qname: str | None
    rationale: str
    severity_hint: str   # 'low'|'medium'|'high'


def classify_route_guard(
    guard_body: str | None,
    *,
    route_path: str = "",
    guard_qname: str | None = None,
) -> RouteGuard:
    """Classify a guard function body.

    Heuristics:
      * Contains ``await`` of a fetch/axios that hits the server →
        ``server-validated``.
      * Reads from Redux/Pinia/Vuex auth state ONLY → ``client-only``.
      * Both → ``mixed``.
      * No recognized auth checks → ``none``.
    """
    if not guard_body:
        return RouteGuard(route_path, "none", guard_qname,
                          "no guard body", "medium")
    body = guard_body
    server = bool(re.search(r"await\s+(fetch|axios|api)\.", body)) \
             or "validateSession" in body \
             or "verifyToken" in body
    client_only = bool(re.search(r"\b(state\.|store\.|useStore\(|useSelector\()", body)) \
                  or "useUser(" in body or "useSession(" in body
    is_admin_path = bool(re.search(r"(admin|owner|root|super)", route_path, re.I))
    sev = "high" if is_admin_path else "medium"
    if server and client_only:
        return RouteGuard(route_path, "mixed", guard_qname,
                          "client check + server fetch",
                          "low" if not is_admin_path else "medium")
    if server:
        return RouteGuard(route_path, "server-validated", guard_qname,
                          "server-side check observed", "low")
    if client_only:
        return RouteGuard(route_path, "client-only", guard_qname,
                          "client-state-only auth check", sev)
    return RouteGuard(route_path, "none", guard_qname,
                      "no recognized auth check", sev)
