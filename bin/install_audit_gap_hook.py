#!/usr/bin/env python3
"""Install the SessionStart audit-gap hook into .claude/settings.json.

Wires `bin/audit_gap_check.py` to fire at every Claude Code session
boot so the hot->audited workflow gap surfaces at the top of the
conversation. Documented in notes/pipeline_calibration_2026-05-18.md.

Idempotent. Run with `--uninstall` to remove. Run with `--dry-run` to
print the edit without writing.

This is a separate script (not an auto-edit by Claude) because
modifying settings.json is self-modification and requires explicit
user opt-in.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SETTINGS = REPO / ".claude" / "settings.json"
HOOK_CMD = (
    "/usr/bin/env python3 "
    f"{REPO / 'bin' / 'audit_gap_check.py'} 2>/dev/null || true"
)
HOOK_COMMENT = (
    "SessionStart audit-gap detector. Surfaces targets stuck at "
    "hot->audited per notes/pipeline_calibration_2026-05-18.md."
)


def _load() -> dict:
    if not SETTINGS.exists():
        sys.exit(f"missing {SETTINGS}")
    return json.loads(SETTINGS.read_text())


def install(data: dict) -> bool:
    hooks = data.setdefault("hooks", {})
    if "$comment" not in hooks:
        hooks["$comment"] = HOOK_COMMENT
    ss = hooks.setdefault("SessionStart", [])
    for entry in ss:
        for h in entry.get("hooks", []):
            if h.get("command") == HOOK_CMD:
                return False  # already installed
    ss.append({"hooks": [{"type": "command", "command": HOOK_CMD}]})
    return True


def uninstall(data: dict) -> bool:
    hooks = data.get("hooks")
    if not hooks:
        return False
    ss = hooks.get("SessionStart", [])
    new_ss = []
    for entry in ss:
        kept = [h for h in entry.get("hooks", []) if h.get("command") != HOOK_CMD]
        if kept:
            new_ss.append({"hooks": kept})
    changed = len(new_ss) != len(ss)
    if not new_ss:
        hooks.pop("SessionStart", None)
    else:
        hooks["SessionStart"] = new_ss
    if not hooks.get("SessionStart") and set(hooks.keys()) <= {"$comment"}:
        data.pop("hooks", None)
    return changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--uninstall", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    data = _load()
    if a.uninstall:
        changed = uninstall(data)
        verb = "uninstalled" if changed else "not installed"
    else:
        changed = install(data)
        verb = "installed" if changed else "already installed"

    if a.dry_run:
        print(json.dumps(data, indent=2))
        print(f"# would be: {verb}", file=sys.stderr)
        return 0

    if changed:
        SETTINGS.write_text(json.dumps(data, indent=2) + "\n")
    print(f"audit-gap hook: {verb}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
