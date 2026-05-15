"""Shared helpers for bin/ scripts.

Status-file writes, scope parsing, target resolution, and TLX sys.path
setup. Keeps each script under ~150 LoC and ensures consistent locking
+ scope semantics across the pipeline.

Convention: scripts import via ``from _lib import ...`` after
``sys.path.insert(0, str(Path(__file__).resolve().parent))``.
"""
from __future__ import annotations

import fcntl
import json
import re
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parents[1]
TLX_DIR = ROOT / "tlx"
TARGETS_DIR = ROOT / "targets"


def utcnow() -> str:
    return (
        datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    )


def tlx_sys_path() -> None:
    """Add tlx/ to sys.path so ``from modules.js_analyzer... import ...`` works."""
    if str(TLX_DIR) not in sys.path:
        sys.path.insert(0, str(TLX_DIR))


def resolve_target_dir(name_or_path: str) -> Path:
    """Accept either an absolute/relative path or a bare target name."""
    p = Path(name_or_path).resolve()
    if p.exists() and p.is_dir():
        return p
    candidate = (TARGETS_DIR / name_or_path).resolve()
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"target dir not found: {name_or_path}")


def per_target_db(target: Path) -> Path:
    return target / "db" / "js_analyzer.db"


@contextmanager
def status_lock(target: Path) -> Iterator[dict]:
    """Yield a mutable dict; on exit, atomically write back as status.json.

    Holds an exclusive flock for the duration of the block so concurrent
    bin/ scripts don't clobber each other's writes.
    """
    sj = target / "status.json"
    sj.touch(exist_ok=True)
    with sj.open("r+") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            data = json.loads(f.read() or "{}")
            yield data
            f.seek(0)
            f.truncate()
            f.write(json.dumps(data, indent=2, default=str))
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def write_status_phase(target: Path, phase: str, fragment: dict) -> None:
    with status_lock(target) as data:
        data.setdefault("phases", {})[phase] = fragment


def append_status_error(
    target: Path, skill: str, error: str | Exception, **extra
) -> None:
    with status_lock(target) as data:
        data.setdefault("errors", []).append(
            {
                "ts": utcnow(),
                "skill": skill,
                "error": str(error),
                **extra,
            }
        )


def read_scope(target: Path) -> dict:
    """Return ``{"in": [hosts], "out": [hosts]}`` from status.json or http.md.

    Patterns may use ``*`` as a single-label wildcard (matches one DNS
    label, not multiple). ``host`` matches itself and any subdomain.
    """
    sj = target / "status.json"
    if sj.exists():
        try:
            data = json.loads(sj.read_text() or "{}")
            scope = data.get("scope") or {}
            if scope.get("in"):
                return scope
        except json.JSONDecodeError:
            pass
    md = target / "http.md"
    in_, out_ = [], []
    if md.exists():
        section = None
        for line in md.read_text().splitlines():
            stripped = line.strip()
            low = stripped.lower()
            if low.startswith(("# in scope", "## in scope")):
                section = "in"
                continue
            if low.startswith(("# out of scope", "## out of scope")):
                section = "out"
                continue
            if stripped.startswith("#"):
                section = None
                continue
            if section and stripped.startswith("- "):
                m = re.match(r"`?(?:https?://)?([^/\s`]+)", stripped[2:].strip())
                if m:
                    (in_ if section == "in" else out_).append(m.group(1).lower())
    return {"in": in_, "out": out_}


def _match_scope_pattern(host: str, pattern: str) -> bool:
    pat = pattern.lower()
    if "*" in pat:
        regex = "^" + re.escape(pat).replace(r"\*", "[^.]+") + "$"
        if re.match(regex, host):
            return True
    return host == pat or host.endswith("." + pat)


def host_in_scope(host: str, scope: dict) -> bool:
    # Strip path AND port — patterns are bare hosts.
    h = host.lower().split("/", 1)[0].split(":", 1)[0]
    for pat in scope.get("out", []):
        if _match_scope_pattern(h, pat):
            return False
    for pat in scope.get("in", []):
        if _match_scope_pattern(h, pat):
            return True
    return False


def pick_chain_input(target: Path, override: str | None = None) -> Path | None:
    """Locate a chain JSONL input — explicit override, else
    chains/dom_reachable.jsonl, else chains/hot.jsonl, else None.
    """
    if override:
        p = Path(override) if Path(override).is_absolute() else (target / override)
        return p if p.exists() else None
    for name in ("chains/dom_reachable.jsonl", "chains/hot.jsonl"):
        p = target / name
        if p.exists():
            return p
    return None
