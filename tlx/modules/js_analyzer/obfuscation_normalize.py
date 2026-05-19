"""Obfuscation normalization passes — string/text level.

Plan: plans/ARCHITECTURE_EVOLUTION_V2.md §16.4.

The base v2/deobfuscation_normalize.py records *evidence* of obfuscation
(string-unfold patterns, wrapper aliases, dead branches, flattened
CFG markers, runtime decoders, constant assembly). This module performs
the actual normalization on a *snippet* basis — producing a denoised
text view that downstream consumers (LLM prompts, regex sinks) can
match against without re-implementing the unfolding logic.

Five conservative passes:

  1. string_unfold      — decode \\xNN and \\uNNNN escape sequences.
  2. constant_fold      — concatenate adjacent string literals.
  3. alias_resolve      — inline ``var x = <dangerous>`` style aliases
                          inside the same snippet scope.
  4. dead_branch_prune  — drop ``if (false) { ... }`` and
                          ``if ('a' === 'b')`` style blocks.
  5. wrapper_peel       — strip outer ``(function(){ ... }())`` and
                          ``+ function(){ ... }()`` IIFE wrappers.

Each pass is idempotent. The pipeline runs deterministically in the
order above. Anything we cannot prove safe stays untouched.

Output of :func:`normalize_snippet` is a dict:

  {
    "normalized": str,
    "passes_applied": list[str],
    "confidence": float,   # 0-1 ratio of size reduction vs aggressiveness
  }

Persistence: :func:`normalize_all_nodes` writes one row per node into
``obfuscation_normalized`` (added in v2_schema when present, but the
module ALSO works standalone without DB persistence — useful for
the LLM snippet enrichment path).
"""
from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


__all__ = [
    "normalize_snippet",
    "ensure_schema",
    "normalize_all_nodes",
    "PASSES",
]


# ---------------------------------------------------------------------------
# Pass implementations
# ---------------------------------------------------------------------------


_HEX_ESC_RE = re.compile(r"\\x([0-9a-fA-F]{2})")
_UNI_ESC_RE = re.compile(r"\\u([0-9a-fA-F]{4})")


def _string_unfold(text: str) -> str:
    """Decode `\\xNN` / `\\uNNNN` escapes inside double / single / template
    literals. Conservative: only unfolds when the decoded char is ASCII
    printable (so we never corrupt UTF-8 byte sequences mid-string).
    """
    def hex_sub(m: re.Match) -> str:
        c = chr(int(m.group(1), 16))
        return c if c.isprintable() and ord(c) < 128 else m.group(0)

    def uni_sub(m: re.Match) -> str:
        cp = int(m.group(1), 16)
        if cp >= 0x110000:
            return m.group(0)
        c = chr(cp)
        return c if c.isprintable() and ord(c) < 128 else m.group(0)

    out = _HEX_ESC_RE.sub(hex_sub, text)
    out = _UNI_ESC_RE.sub(uni_sub, out)
    return out


# Conservative constant-fold: 'a' + 'b' → 'ab' (same quote style).
_CONCAT_DBL_RE = re.compile(r'"((?:[^"\\]|\\.){0,128})"\s*\+\s*"((?:[^"\\]|\\.){0,128})"')
_CONCAT_SGL_RE = re.compile(r"'((?:[^'\\]|\\.){0,128})'\s*\+\s*'((?:[^'\\]|\\.){0,128})'")


def _constant_fold(text: str) -> str:
    prev = None
    out = text
    for _ in range(8):
        new = _CONCAT_DBL_RE.sub(lambda m: f'"{m.group(1)}{m.group(2)}"', out)
        new = _CONCAT_SGL_RE.sub(lambda m: f"'{m.group(1)}{m.group(2)}'", new)
        if new == prev or new == out:
            return new
        prev = out
        out = new
    return out


# Alias resolve: capture `var X = <name>;` and re-substitute X with name
# in the rest of the snippet. Bounded — too aggressive in deeply
# obfuscated bundles. Only the safe alias case: identifier-only RHS.
_ALIAS_DECL_RE = re.compile(
    r"\b(?:var|let|const)\s+(?P<lhs>[A-Za-z_$][\w$]*)\s*=\s*"
    r"(?P<rhs>(?:[A-Za-z_$][\w$]*\.)*[A-Za-z_$][\w$]*)\s*;"
)
_DANGEROUS_RHS = re.compile(
    r"\b(?:innerHTML|outerHTML|insertAdjacentHTML|eval|setTimeout|setInterval|"
    r"Function|document\.write|writeln|location\.href|location\.assign)\b"
)


def _alias_resolve(text: str) -> str:
    aliases: dict[str, str] = {}
    for m in _ALIAS_DECL_RE.finditer(text):
        rhs = m.group("rhs")
        lhs = m.group("lhs")
        # Only resolve aliases that point at dangerous APIs; arbitrary
        # rename would change semantics.
        if _DANGEROUS_RHS.search(rhs):
            aliases[lhs] = rhs
    if not aliases:
        return text
    # Substitute every alias use. Word-boundary keyed.
    out = text
    for lhs, rhs in aliases.items():
        out = re.sub(rf"\b{re.escape(lhs)}\b", rhs, out)
    return out


# Dead-branch prune: if (false) { ... } and if ('a' === 'b') { ... }.
_DEAD_IF_BLOCK_RE = re.compile(
    r"if\s*\(\s*(?:false|0|!\s*1)\s*\)\s*"
    r"\{(?:[^{}]|\{[^{}]*\}){0,4000}\}",
    re.DOTALL,
)
_DEAD_IF_STRING_RE = re.compile(
    r"if\s*\(\s*['\"`](?P<a>[^'\"`]*)['\"`]\s*(?:===|==)\s*['\"`](?P<b>[^'\"`]*)['\"`]\s*\)\s*"
    r"\{(?:[^{}]|\{[^{}]*\}){0,4000}\}",
    re.DOTALL,
)


def _dead_branch_prune(text: str) -> str:
    out = _DEAD_IF_BLOCK_RE.sub("", text)
    def strcmp_sub(m: re.Match) -> str:
        return "" if m.group("a") != m.group("b") else m.group(0)
    out = _DEAD_IF_STRING_RE.sub(strcmp_sub, out)
    return out


# Wrapper peel: !function(){ ... }() / (function(){ ... }()) IIFE that
# wrap the whole snippet.
_IIFE_PAREN_RE = re.compile(
    r"^\s*[!+~\-]?\s*\(?\s*function\s*\([^)]*\)\s*\{\s*"
    r"(?P<body>[\s\S]*)"
    r"\s*\}\s*\(\s*\)\s*\)?\s*;?\s*$",
    re.MULTILINE,
)


def _wrapper_peel(text: str) -> str:
    text_stripped = text.strip()
    m = _IIFE_PAREN_RE.match(text_stripped)
    if m:
        return m.group("body").strip()
    return text


PASSES: list[tuple[str, Callable[[str], str]]] = [
    ("string_unfold",     _string_unfold),
    ("constant_fold",     _constant_fold),
    ("alias_resolve",     _alias_resolve),
    ("dead_branch_prune", _dead_branch_prune),
    ("wrapper_peel",      _wrapper_peel),
]


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


@dataclass
class NormalizeResult:
    normalized: str
    passes_applied: list[str] = field(default_factory=list)
    original_size: int = 0
    final_size: int = 0
    confidence: float = 0.0


def normalize_snippet(text: str) -> NormalizeResult:
    """Apply every safe pass once. Returns a NormalizeResult."""
    out = text
    applied: list[str] = []
    for name, fn in PASSES:
        try:
            new = fn(out)
        except Exception:
            continue
        if new != out:
            applied.append(name)
            out = new
    orig = len(text)
    final = len(out)
    # Confidence: weight by reduction ratio capped at 0.9 (we never claim
    # full normalization — analyst still owns judgement).
    reduction = max(0.0, (orig - final) / orig) if orig else 0.0
    confidence = round(min(0.9, 0.4 + reduction * 0.5), 3) if applied else 0.0
    return NormalizeResult(
        normalized=out,
        passes_applied=applied,
        original_size=orig,
        final_size=final,
        confidence=confidence,
    )


# ---------------------------------------------------------------------------
# DB persistence (optional — only when the obfuscation_normalized table
# exists; we don't add it to v2_schema by default because not every
# pipeline wants per-node normalized text).
# ---------------------------------------------------------------------------


_CREATE_SCHEMA = """
CREATE TABLE IF NOT EXISTS obfuscation_normalized (
    node_id          INTEGER PRIMARY KEY,
    passes_applied   TEXT NOT NULL,
    original_size    INTEGER NOT NULL,
    final_size       INTEGER NOT NULL,
    confidence       REAL NOT NULL,
    normalized       TEXT NOT NULL
);
"""


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(_CREATE_SCHEMA)


def normalize_all_nodes(conn: sqlite3.Connection, target_dir: str | Path) -> dict:
    """Walk every node, read its source slice [start_line..end_line],
    run :func:`normalize_snippet`, persist the result.
    """
    ensure_schema(conn)
    conn.execute("DELETE FROM obfuscation_normalized")
    target_root = Path(target_dir)
    rows = conn.execute(
        "SELECT id, file, start_line, end_line FROM nodes"
    ).fetchall()
    by_pass: dict[str, int] = {}
    saved = 0
    for nid, file, start, end in rows:
        if not file or not start or not end:
            continue
        snippet = _read_snippet(target_root, file, int(start), int(end))
        if not snippet:
            continue
        res = normalize_snippet(snippet)
        if not res.passes_applied:
            continue
        conn.execute(
            "INSERT INTO obfuscation_normalized "
            "(node_id, passes_applied, original_size, final_size, "
            " confidence, normalized) VALUES (?, ?, ?, ?, ?, ?)",
            (int(nid), ",".join(res.passes_applied),
             res.original_size, res.final_size, res.confidence,
             res.normalized),
        )
        saved += 1
        for p in res.passes_applied:
            by_pass[p] = by_pass.get(p, 0) + 1
    conn.commit()
    return {"rows_saved": saved, "by_pass": by_pass}


def _read_snippet(
    target_root: Path, file: str, start_line: int, end_line: int
) -> str | None:
    for candidate in (
        target_root / "sources" / file,
        target_root / "raw" / file,
        Path(file),
    ):
        if candidate.exists() and candidate.is_file():
            try:
                text = candidate.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            lines = text.splitlines()
            return "\n".join(lines[start_line - 1 : end_line])
    return None
