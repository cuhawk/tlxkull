"""Cross-origin trust + origin provenance modeling.

Plan: plans/ARCHITECTURE_EVOLUTION_V2.md §12.

postMessage origin validation is the highest-value, lowest-modeled
attack surface on modern SPAs. This module:

  * Classifies an ``onmessage`` handler's origin validation into
    {strict, loose, none, library} with a list of bypass classes.
  * Catalogs ``postMessage`` send-sites with their ``targetOrigin``.
  * Categorizes the *shape* of each handler (command-bus, state-mirror,
    routing, js-injection) to drive sink-severity scoring.

Inputs come from ast_extractor.js records tagged
``ast_kind == 'postMessage_handler'`` (handlers, with their guard
expressions) and ``ast_kind == 'postMessage_send'`` (calls).

Public API:
  * ``classify_validation(expr_repr: str)`` → ValidationKind + bypasses.
  * ``categorize_handler(handler_body_repr: str)`` → handler category.
  * ``ingest(conn, records)`` → fills ``node_provenance``.
  * ``trust_score(chain_path)`` → §12.8 multiplier in [0, 1].

Behind ``ENABLE_ORIGIN_TRUST``.
"""
from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from typing import Iterable

__all__ = [
    "classify_validation",
    "categorize_handler",
    "ingest",
    "trust_score",
    "ValidationKind",
    "HandlerCategory",
]


ValidationKind = str   # 'strict' | 'loose' | 'none' | 'library'
HandlerCategory = str  # 'command-bus' | 'state-mirror' | 'routing' | 'js-injection' | 'other'


# ──────────────────────────────────────────────────────────────────────
# Validation classification
# ──────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ValidationVerdict:
    kind: ValidationKind
    bypass_classes: tuple[str, ...]
    rationale: str | None = None


# Regex pattern → (kind, bypass_classes). Order matters — first match
# wins. Patterns are anchored on canonical ``event.origin`` access.
_VALIDATION_PATTERNS: list[tuple[re.Pattern, ValidationVerdict]] = [
    # Strict: equality to a single literal.
    (re.compile(r"event\.origin\s*===\s*['\"][^'\"]+['\"]"),
     ValidationVerdict("strict", (), "single-origin === literal")),
    (re.compile(r"event\.origin\s*==\s*['\"][^'\"]+['\"]"),
     ValidationVerdict("strict", ("loose-equality",), "== instead of ===")),

    # Set-membership.
    (re.compile(r"\[[^\]]*\]\.includes\(\s*event\.origin\s*\)"),
     ValidationVerdict("strict", (), "Array.includes literal allowlist")),
    (re.compile(r"\.indexOf\(\s*event\.origin\s*\)\s*[!=]==?\s*-?1"),
     ValidationVerdict("strict", (), "indexOf allowlist")),

    # Loose: prefix / suffix / substring checks.
    (re.compile(r"event\.origin\.startsWith\("),
     ValidationVerdict("loose", ("subdomain_prefix",), "startsWith — wildcard subdomain")),
    (re.compile(r"event\.origin\.endsWith\("),
     ValidationVerdict("loose", ("suffix_match",), "endsWith — attacker.example.com")),
    (re.compile(r"event\.origin\.includes\("),
     ValidationVerdict("loose", ("substring_match",), "includes — partial-domain")),
    (re.compile(r"event\.origin\.indexOf\("),
     ValidationVerdict("loose", ("substring_match",), "indexOf substring match")),

    # Regex.
    (re.compile(r"\.test\(\s*event\.origin\s*\)"),
     ValidationVerdict("loose", ("regex-leak",), "RegExp.test of event.origin")),
    (re.compile(r"event\.origin\.match\("),
     ValidationVerdict("loose", ("regex-leak",), "match on event.origin")),

    # Library calls.
    (re.compile(r"is(?:Allowed|Trusted)Origin\(\s*event\.origin"),
     ValidationVerdict("library", (), "isAllowedOrigin/isTrustedOrigin lib")),
    (re.compile(r"originAllowed\(\s*event\.origin"),
     ValidationVerdict("library", (), "originAllowed lib")),
]


def classify_validation(guard_expr: str | None) -> ValidationVerdict:
    """Classify the guard expression for an ``onmessage`` handler.

    A ``None`` or empty expression means no validation at all.
    """
    if not guard_expr:
        return ValidationVerdict("none", (), "no guard expression")
    for pat, verdict in _VALIDATION_PATTERNS:
        if pat.search(guard_expr):
            return verdict
    # Anything referencing event.origin at all is at least "loose";
    # otherwise treat as no validation.
    if "event.origin" in guard_expr or "msg.origin" in guard_expr:
        return ValidationVerdict("loose", ("unclassified",),
                                 "event.origin referenced but pattern unknown")
    return ValidationVerdict("none", (), "no event.origin reference")


# ──────────────────────────────────────────────────────────────────────
# Handler categorization
# ──────────────────────────────────────────────────────────────────────

def categorize_handler(handler_body: str | None) -> HandlerCategory:
    """Pragmatic substring-and-pattern matcher. Body is the textual JS
    of the handler's function body (or a structural summary).
    """
    if not handler_body:
        return "other"
    b = handler_body
    # JS injection — highest severity first.
    if re.search(r"\b(eval|Function|setTimeout|setInterval)\s*\(", b) \
       and ("event.data" in b or "msg.data" in b):
        return "js-injection"
    if re.search(r"\.innerHTML\s*=\s*[A-Za-z_]*(event|msg)\.data", b):
        return "js-injection"

    # Routing.
    if re.search(r"router\.(push|replace|navigate)\s*\(", b):
        return "routing"
    if re.search(r"\blocation\.(href|assign)\s*=", b):
        return "routing"

    # State-mirror.
    if re.search(r"\bdispatch\s*\(", b) or "store.commit" in b or "useStore" in b:
        return "state-mirror"

    # Command-bus.
    if re.search(r"switch\s*\(\s*(event|msg)\.data\.(type|cmd|action)", b):
        return "command-bus"
    if re.search(r"(event|msg)\.data\.type", b) and "case" in b:
        return "command-bus"

    return "other"


# ──────────────────────────────────────────────────────────────────────
# DB ingest
# ──────────────────────────────────────────────────────────────────────

def ingest(
    conn: sqlite3.Connection,
    records: Iterable[dict],
) -> int:
    """Fill ``node_provenance`` for postMessage handlers + sends.

    Record shape::

        {
          "ast_kind": "postMessage_handler" | "postMessage_send",
          "node_id":  int,
          "channel":  "postMessage" | "BroadcastChannel" | ...,
          "guard_expr": str | None,        # handlers only
          "target_origin": str | None,     # sends only
          "origin_label": str,             # 'iframe:0' | 'self' | 'opener' | ...
        }
    """
    cur = conn.cursor()
    inserted = 0
    for rec in records:
        kind = rec.get("ast_kind")
        if kind not in ("postMessage_handler", "postMessage_send"):
            continue
        node_id = rec.get("node_id")
        if not node_id:
            continue
        if kind == "postMessage_handler":
            verdict = classify_validation(rec.get("guard_expr"))
            cur.execute(
                """INSERT OR REPLACE INTO node_provenance
                   (node_id, origin_label, channel, validation_kind,
                    validation_expr_node, bypass_classes, confidence)
                   VALUES (?,?,?,?,?,?,?)""",
                (node_id, rec.get("origin_label") or "unknown",
                 rec.get("channel") or "postMessage",
                 verdict.kind,
                 rec.get("validation_expr_node"),
                 ",".join(verdict.bypass_classes),
                 0.8),
            )
            inserted += cur.rowcount
        else:
            tgt = rec.get("target_origin")
            bypass = ("targetOrigin=wildcard",) if tgt == "*" else ()
            cur.execute(
                """INSERT OR REPLACE INTO node_provenance
                   (node_id, origin_label, channel, validation_kind,
                    bypass_classes, confidence)
                   VALUES (?,?,?,?,?,?)""",
                (node_id, rec.get("origin_label") or "self",
                 rec.get("channel") or "postMessage",
                 "send",
                 ",".join(bypass),
                 0.9),
            )
            inserted += cur.rowcount
    conn.commit()
    return inserted


# ──────────────────────────────────────────────────────────────────────
# Trust scoring (§12.8)
# ──────────────────────────────────────────────────────────────────────

_TRUST_MULTIPLIER = {
    "none":    0.80,
    "loose":   0.50,
    "library": 0.30,
    "strict":  0.20,
    "send":    1.00,    # send-sites don't gate inbound trust
}


def trust_score(
    chain_path: Iterable[dict],
    conn: sqlite3.Connection | None = None,
) -> float:
    """Walk the chain path looking for origin boundaries. The earliest
    boundary on the chain determines the multiplier (subsequent
    boundaries are absorbed).

    ``chain_path`` rows should expose ``node_id`` (preferred); if a row
    carries an inlined ``validation_kind`` it's used directly without a
    DB lookup.
    """
    seen_kind: str | None = None
    for hop in chain_path:
        kind = hop.get("validation_kind")
        if kind is None and conn is not None and hop.get("node_id"):
            cur = conn.cursor()
            cur.execute(
                "SELECT validation_kind FROM node_provenance WHERE node_id=?",
                (hop["node_id"],),
            )
            row = cur.fetchone()
            if row:
                kind = row[0]
        if kind in _TRUST_MULTIPLIER:
            seen_kind = kind
            break
    if seen_kind is None:
        return 1.0
    return _TRUST_MULTIPLIER[seen_kind]
