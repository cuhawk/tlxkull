#!/usr/bin/env python3
"""Bulk target-init: parse every targets/<name>/http.md into status.json.

Implements the target-init skill contract:
- Reads ## Scope (in:/out: lines, optional `# type: <kind>` tag)
- Reads ## Auth (type: + creds: lines)
- Reads ## Notes (raw markdown body)
- Writes targets/<name>/status.json; merges if one already exists
  (preserves existing phases.* entries).
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = ROOT / "targets"

SUPPORTED_AUTH = {
    "session", "bearer", "mtls", "oauth", "api_key", "mobile_token", "none",
    # bugcrowd/program-specific auth shapes seen in real http.md files
    "signup", "web_app", "device", "appliance", "self-registered",
    "atlassian_cloud_instance", "self_registered",
}
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$")
INLINE_TAG_RE = re.compile(r"#\s*type:\s*([a-z0-9_]+)", re.I)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def infer_type(value: str) -> str:
    v = value.strip()
    if "*" in v:
        return "wildcard"
    if re.match(r"^[0-9a-fA-F:.]+/\d+$", v):
        return "cidr"
    if v.startswith(("http://", "https://")):
        return "url"
    if re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
        return "domain"
    return "other"


def parse_scope_line(line: str) -> dict | None:
    """Parse one `- in:` / `- out:` line. Strip inline tags, capture type."""
    s = line.strip()
    if not s.startswith("-"):
        return None
    s = s.lstrip("-").strip()
    if s.startswith("in:"):
        direction, rest = "in", s[3:].strip()
    elif s.startswith("out:"):
        direction, rest = "out", s[4:].strip()
    else:
        return None
    # Split on first `#` not preceded by URL fragment; keep value side.
    tag_match = INLINE_TAG_RE.search(rest)
    declared_type = tag_match.group(1).lower() if tag_match else None
    # Strip everything from the first `#` to end (entire comment block).
    value = rest.split("#", 1)[0].strip()
    if not value:
        return None
    return {
        "direction": direction,
        "value": value,
        "type": declared_type or infer_type(value),
    }


def wildcard_to_regex(pattern: str) -> str:
    """Convert `*.example.com` style glob to anchored regex."""
    esc = re.escape(pattern).replace(r"\*", r"[^.]+")
    return f"^{esc}$"


def parse_http_md(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        m = SECTION_RE.match(line)
        if m:
            current = m.group(1).strip().lower()
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(line)

    # Scope: scan ALL lines globally — many real http.md files split scope
    # across sub-headers (### Web / Network, ### Hardware, etc.) rather
    # than keeping everything under one ## Scope block. The `- in:` /
    # `- out:` prefix is unambiguous, so section context is unnecessary.
    in_entries: list[dict] = []
    out_entries: list[dict] = []
    for line in text.splitlines():
        parsed = parse_scope_line(line)
        if not parsed:
            continue
        entry = {"value": parsed["value"], "type": parsed["type"]}
        # Generate regex for any wildcard-shaped value regardless of declared
        # type. Seeds often tag `*.foo.com` as `url` or `wildcard`
        # interchangeably; downstream scope matching needs the regex either way.
        if "*" in parsed["value"]:
            # Use only the first whitespace-delimited token — many seeds append
            # free-text after the glob ("*.foo.com Web Apps") which would
            # otherwise pollute the regex.
            head = parsed["value"].split()[0]
            if "*" in head:
                entry["regex"] = wildcard_to_regex(head)
        (in_entries if parsed["direction"] == "in" else out_entries).append(entry)

    # Auth lines: restrict to the ## Auth section if it exists, else global.
    auth_lines = sections.get("auth", []) or text.splitlines()
    auth_type: str | None = None
    creds: list[str] = []
    for line in auth_lines:
        s = line.strip()
        if not s.startswith("-"):
            continue
        s = s.lstrip("-").strip()
        if s.startswith("type:") and auth_type is None:
            rest = s[5:].strip()
            auth_type = rest.split()[0] if rest else None
        elif s.startswith("creds:"):
            creds.append(s[6:].strip().split("#", 1)[0].strip())

    notes_lines = sections.get("notes", [])
    notes = "\n".join(notes_lines).strip()

    return {
        "scope": {"in": in_entries, "out": out_entries},
        "auth": {"type": auth_type, "creds": creds},
        "notes": notes,
    }


def build_status(name: str, parsed: dict) -> dict:
    ts = now_iso()
    return {
        "name": name,
        "created_utc": ts,
        "scope": parsed["scope"],
        "auth": parsed["auth"],
        "notes": parsed["notes"],
        "phase": "init",
        "phases": {
            "init": {
                "status": "done",
                "ts": ts,
                "scope_in": len(parsed["scope"]["in"]),
                "scope_out": len(parsed["scope"]["out"]),
            }
        },
        "errors": [],
    }


def merge_status(existing: dict, fresh: dict) -> dict:
    """Preserve existing phases.* entries; overwrite scope/auth/notes."""
    merged = dict(existing)
    merged["scope"] = fresh["scope"]
    merged["auth"] = fresh["auth"]
    merged["notes"] = fresh["notes"]
    existing_phases = existing.get("phases", {}) or {}
    fresh_phases = fresh.get("phases", {}) or {}
    merged_phases = dict(existing_phases)
    merged_phases.update(fresh_phases)
    merged["phases"] = merged_phases
    merged.setdefault("errors", existing.get("errors", []))
    merged["name"] = fresh["name"]
    return merged


def process_target(target_dir: Path) -> tuple[str, str]:
    """Return (status, detail). status in {ok, skip, fail}."""
    name = target_dir.name
    http_md = target_dir / "http.md"
    if not http_md.exists():
        return "skip", "no http.md"
    try:
        parsed = parse_http_md(http_md)
    except Exception as e:
        return "fail", f"parse error: {e}"

    warnings: list[str] = []
    if not parsed["scope"]["in"]:
        warnings.append("empty in-scope — only out: entries or free-text scope; resolve before running js-harvest")

    auth_type = parsed["auth"]["type"]
    if auth_type and auth_type not in SUPPORTED_AUTH:
        warnings.append(f"unknown auth type: {auth_type}")

    fresh = build_status(name, parsed)
    if warnings:
        fresh["errors"] = warnings
    status_path = target_dir / "status.json"
    if status_path.exists():
        try:
            existing = json.loads(status_path.read_text(encoding="utf-8"))
            fresh = merge_status(existing, fresh)
        except Exception as e:
            return "fail", f"existing status.json malformed: {e}"

    status_path.write_text(json.dumps(fresh, indent=2), encoding="utf-8")
    suffix = f" warnings={len(warnings)}" if warnings else ""
    return "ok", f"in={len(parsed['scope']['in'])} out={len(parsed['scope']['out'])} auth={auth_type}{suffix}"


def main(argv: list[str]) -> int:
    only = set(argv[1:])
    target_dirs = sorted(p for p in TARGETS.iterdir() if p.is_dir())
    ok = skip = fail = 0
    failures: list[tuple[str, str]] = []
    for d in target_dirs:
        if only and d.name not in only:
            continue
        status, detail = process_target(d)
        if status == "ok":
            ok += 1
        elif status == "skip":
            skip += 1
        else:
            fail += 1
            failures.append((d.name, detail))
    print(f"ok={ok} skip={skip} fail={fail}")
    if failures:
        print("--- failures ---")
        for name, detail in failures:
            print(f"  {name}: {detail}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
