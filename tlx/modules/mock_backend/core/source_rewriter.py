"""JS source rewriting for probe injection.

Two modes:
- regex (default): cheap identifier substitution via word-boundary regex.
- ast: precise rewrite via Node + @babel/parser. Falls back to regex on
  any subprocess failure.

Never touches files on disk except for short-lived tempfiles handed to
the Node subprocess.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Literal

import structlog

log = structlog.get_logger(__name__)

_AST_SCRIPT = (
    Path(__file__).resolve().parents[1] / "js" / "ast_rewrite.js"
)
_AST_TIMEOUT_SEC = 10


def rewrite_js(source: str, rewrite_map: dict[str, str]) -> str:
    """Replace standalone identifiers with literal replacements (regex).

    Each rewrite_map value is already a JSON-serialised literal — the
    caller (PayloadInjector) handles quoting.
    """
    if not source or not rewrite_map:
        return source
    out = source
    for ident, replacement in rewrite_map.items():
        if not ident:
            continue
        pattern = re.compile(rf"\b{re.escape(ident)}\b")
        out = pattern.sub(lambda _m, _r=replacement: _r, out)
    return out


def rewrite_js_ast(source: str, rewrite_map: dict[str, str]) -> str:
    """Precise AST-based rewrite via Node + @babel/parser.

    Falls back to ``rewrite_js`` on any subprocess failure (Node missing,
    babel not installed, parse error, timeout, non-zero exit).
    """
    if not source or not rewrite_map:
        return source

    node_bin = shutil.which("node")
    if not node_bin or not _AST_SCRIPT.exists():
        log.warning(
            "ast_rewrite_fallback",
            reason="node_or_script_missing",
            node=bool(node_bin),
            script=str(_AST_SCRIPT),
        )
        return rewrite_js(source, rewrite_map)

    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".js", delete=False, encoding="utf-8",
        ) as tf:
            tf.write(source)
            tmp_path = Path(tf.name)

        proc = subprocess.run(
            [node_bin, str(_AST_SCRIPT), str(tmp_path),
             json.dumps(rewrite_map)],
            capture_output=True, text=True, timeout=_AST_TIMEOUT_SEC,
        )
        if proc.returncode != 0:
            log.warning(
                "ast_rewrite_fallback",
                reason="non_zero_exit",
                returncode=proc.returncode,
                stderr=proc.stderr[:200],
            )
            return rewrite_js(source, rewrite_map)
        return proc.stdout
    except subprocess.TimeoutExpired:
        log.warning("ast_rewrite_fallback", reason="timeout")
        return rewrite_js(source, rewrite_map)
    except Exception as e:
        log.warning(
            "ast_rewrite_fallback", reason="exception", error=str(e),
        )
        return rewrite_js(source, rewrite_map)
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except OSError:
                pass


def inject_probe_in_response(
    body: bytes,
    content_type: str,
    rewrite_map: dict[str, str],
    *,
    mode: Literal["regex", "ast"] = "regex",
) -> bytes:
    """Apply the chosen rewrite to JS responses; pass everything else through."""
    ct = (content_type or "").lower()
    if "javascript" not in ct:
        return body
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError:
        return body
    if mode == "ast":
        rewritten = rewrite_js_ast(text, rewrite_map)
    else:
        rewritten = rewrite_js(text, rewrite_map)
    return rewritten.encode("utf-8")
