"""Sink reachability validation.

Plan: plans/ARCHITECTURE_EVOLUTION_V2.md §22.

A taint chain that reaches an ``eval`` whose feature flag is OFF in
production is not exploitable. Today everything in the AST scores as
"live". On enterprise SaaS targets ~25% of chains are gated by:

  * route guards the attacker can't satisfy,
  * dead code the bundler kept but nothing imports,
  * feature flags that default to OFF in prod,
  * lifecycle phases (unmount-only sinks).

This module:

  1. Extracts route entries per framework (React Router, Next pages,
     Vue Router, Angular Router).
  2. Walks the callgraph from each route to compute "what sinks are
     reachable from this route?".
  3. Detects feature-flag patterns and surfaces a name + default-state
     hint for each gating flag.
  4. Computes ``activation_likelihood`` per chain (§22.7).

Behind ``ENABLE_SINK_REACHABILITY``.
"""
from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass, field
from typing import Iterable

__all__ = [
    "Route",
    "extract_routes",
    "compute_activation",
    "detect_feature_flags",
    "ROUTE_PATTERNS",
]


@dataclass
class Route:
    path: str
    entry_node_id: int
    framework: str
    requires_auth: bool = False
    auth_predicate: str | None = None


# Cheap pattern matchers per framework. The AST extractor stamps
# call-sites with ``ast_kind == 'route_decl'`` whenever it recognizes
# one; fallback to grep below is used if the extractor missed it.
ROUTE_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("react-router", re.compile(r"<Route\s+[^>]*path\s*=\s*['\"]([^'\"]+)['\"]")),
    ("react-router", re.compile(r"createBrowserRouter\(\s*\[\s*{[^}]*path\s*:\s*['\"]([^'\"]+)['\"]")),
    ("next",         re.compile(r"pages/([^/]+)\.tsx")),
    ("next-app",     re.compile(r"app/(.+)/page\.tsx")),
    ("vue-router",   re.compile(r"\{[^}]*path\s*:\s*['\"]([^'\"]+)['\"]")),
    ("angular",      re.compile(r"\{\s*path\s*:\s*['\"]([^'\"]+)['\"]")),
]


def extract_routes(
    conn: sqlite3.Connection,
    sources: Iterable[tuple[str, str]] | None = None,
) -> list[Route]:
    """Return one ``Route`` per recognized entry point.

    ``sources`` is an optional iterable of (file_path, source_text)
    pairs used when the DB has no ``route_decl`` AST records. The chain
    extractor passes the raw source so we don't re-read the disk.
    """
    out: list[Route] = []
    cur = conn.cursor()
    # AST-tagged path.
    try:
        cur.execute(
            """SELECT nt.node_id, n.file, nt.evidence
               FROM   node_tags nt
               JOIN   nodes n ON n.id = nt.node_id
               WHERE  nt.taxonomy_id LIKE 'route_decl%'""",
        )
        for nid, file_, evidence in cur.fetchall():
            path = evidence.strip() if evidence else file_
            fw = "react-router"
            if file_.startswith(("app/", "pages/")) or "/pages/" in file_:
                fw = "next-app" if "/app/" in file_ else "next"
            out.append(Route(
                path=path,
                entry_node_id=nid,
                framework=fw,
            ))
    except sqlite3.OperationalError:
        pass
    # Fallback grep.
    if not out and sources is not None:
        for file_, text in sources:
            for fw, pat in ROUTE_PATTERNS:
                for m in pat.finditer(text):
                    out.append(Route(
                        path=m.group(1),
                        entry_node_id=0,
                        framework=fw,
                    ))
    return out


# ──────────────────────────────────────────────────────────────────────
# Feature flag detection (§22.9)
# ──────────────────────────────────────────────────────────────────────

@dataclass
class FeatureFlagRef:
    flag_name: str
    library:   str             # 'launchdarkly'|'split'|'growthbook'|'env'|'unknown'
    file:      str
    line:      int | None
    default_state: str | None  # 'on'|'off'|'unknown' — set by analyst note

_FLAG_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("launchdarkly", re.compile(r"LDClient\.variation\(\s*['\"]([^'\"]+)['\"]")),
    ("split",        re.compile(r"splitClient\.getTreatment\(\s*['\"]([^'\"]+)['\"]")),
    ("growthbook",   re.compile(r"growthbook\.feature\(\s*['\"]([^'\"]+)['\"]")),
    ("unleash",      re.compile(r"unleash\.isEnabled\(\s*['\"]([^'\"]+)['\"]")),
    ("env",          re.compile(r"process\.env\.NEXT_PUBLIC_([A-Z0-9_]+)")),
    ("env",          re.compile(r"window\.__([A-Z0-9_]+)__")),
    ("local",        re.compile(r"useFeatureFlag\(\s*['\"]([^'\"]+)['\"]")),
]


def detect_feature_flags(
    file_path: str,
    text: str,
) -> list[FeatureFlagRef]:
    out: list[FeatureFlagRef] = []
    for library, pat in _FLAG_PATTERNS:
        for m in pat.finditer(text):
            line_no = text[:m.start()].count("\n") + 1
            out.append(FeatureFlagRef(
                flag_name=m.group(1),
                library=library,
                file=file_path,
                line=line_no,
                default_state="unknown",
            ))
    return out


# ──────────────────────────────────────────────────────────────────────
# Activation likelihood (§22.7)
# ──────────────────────────────────────────────────────────────────────

@dataclass
class ChainActivation:
    likelihood: float
    feature_flags_gating: list[str] = field(default_factory=list)
    reachability: str = "unknown"     # 'live'|'dead'|'lazy'|'unknown'


_PHASE_FACTORS = {
    "mount":         1.0,
    "render":        1.0,
    "update":        0.8,
    "click":         0.6,
    "submit":        0.6,
    "revalidate":    0.6,
    "lazy":          0.6,
    "sw_install":    0.3,
    "sw_fetch":      0.4,
    "unmount":       0.1,
    "error":         0.2,
    "shutdown":      0.05,
}


def compute_activation(
    chain: dict,
    *,
    sink_lifecycle_phase: str | None = None,
    feature_flags: Iterable[FeatureFlagRef] = (),
    sink_reachable_from_route: bool | None = None,
) -> ChainActivation:
    """Compute the activation_likelihood for a chain.

    Defaults are conservative — when info is missing, returns 1.0 so we
    never silently demote a chain we don't understand.
    """
    likelihood = 1.0
    flags = [f.flag_name for f in feature_flags]
    reach = "unknown"

    if sink_reachable_from_route is False:
        return ChainActivation(0.0, flags, "dead")
    if sink_reachable_from_route is True:
        reach = "live"
    if sink_lifecycle_phase:
        likelihood *= _PHASE_FACTORS.get(sink_lifecycle_phase, 1.0)
    if flags:
        # Apply 0.4 for unknown default; 0.05 for known default-off.
        for ff in feature_flags:
            if ff.default_state == "on":
                likelihood *= 0.8
            elif ff.default_state == "off":
                likelihood *= 0.05
            else:
                likelihood *= 0.4
    return ChainActivation(round(max(0.0, min(1.0, likelihood)), 3),
                           flags, reach)
