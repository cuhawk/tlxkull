#!/usr/bin/env python3
"""Run BishopFox jsluice and ingest URL skeletons + secrets as node tags.

Per IMPL_TIER123.md T1.4. URL skeletons with EXPR placeholders surface as
separate finding candidates in chain-triage; secret hits trigger a
finding draft into ``targets/<name>/findings/`` (no auto-submit).

Usage:
  bin/run_jsluice.py <target_dir> [--db <path>] [--jsluice <bin>]

Requires:
  - jsluice binary in PATH (https://github.com/BishopFox/jsluice).
    Install: ``go install github.com/BishopFox/jsluice/cmd/jsluice@latest``

If jsluice is missing the script writes a ``status: skipped`` result with
install instructions and exits 0 — does not fail the surrounding pipeline.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    per_target_db,
    resolve_target_dir,
    tlx_sys_path,
    utcnow,
    write_status_phase,
)

tlx_sys_path()


SECRET_SEVERITY = {
    "aws_access_key_id": "high",
    "aws_secret_access_key": "high",
    "github_token": "high",
    "github_pat": "high",
    "stripe_api_key": "high",
    "stripe_publishable_key": "low",
    "google_api_key": "medium",
    "google_oauth_client_secret": "high",
    "slack_token": "high",
    "slack_webhook": "medium",
    "private_key": "high",
    "jwt": "medium",
    "generic": "low",
}


def jsluice_run(jsluice_bin: str, mode: str, files: list[Path]) -> list[dict]:
    if not files:
        return []
    cmd = [jsluice_bin, mode, "-j"] + [str(f) for f in files]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, check=False, timeout=600
        )
    except subprocess.TimeoutExpired:
        return []
    out: list[dict] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def relpath_for_node_lookup(
    abs_path: Path, raw_root: Path, sources_root: Path
) -> str | None:
    for root in (sources_root, raw_root):
        try:
            return str(abs_path.relative_to(root))
        except ValueError:
            continue
    return None


def collect_js_files(target: Path) -> list[Path]:
    out: list[Path] = []
    for sub in ("sources", "raw"):
        root = target / sub
        if not root.exists():
            continue
        for p in root.rglob("*.js"):
            if p.is_file() and not p.name.endswith(".min.js"):
                out.append(p)
    return out


def write_audit(target: Path, urls: list[dict], secrets: list[dict]) -> Path:
    out_dir = target / "index"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "jsluice.jsonl"
    with out.open("w") as f:
        for r in urls:
            f.write(json.dumps({"_kind": "url", **r}) + "\n")
        for r in secrets:
            f.write(json.dumps({"_kind": "secret", **r}) + "\n")
    return out


def write_secret_drafts(target: Path, secrets: list[dict]) -> int:
    if not secrets:
        return 0
    findings_dir = target / "findings"
    findings_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for sec in secrets:
        kind = sec.get("kind") or "generic"
        filename = sec.get("filename") or "unknown"
        data = sec.get("data") or ""
        sid = hashlib.sha256(
            f"{kind}|{filename}|{data[:8]}".encode()
        ).hexdigest()[:12]
        fdir = findings_dir / f"jsluice_secret_{sid}"
        if fdir.exists():
            continue
        fdir.mkdir()
        (fdir / "draft.json").write_text(
            json.dumps(
                {
                    "kind": "leaked_secret",
                    "auto_submit": False,
                    "requires_user_review": True,
                    "ts": utcnow(),
                    "secret_kind": kind,
                    "filename": filename,
                    "severity": SECRET_SEVERITY.get(kind, "low"),
                    "data_preview": data[:32] + ("…" if len(data) > 32 else ""),
                    "source": "jsluice",
                },
                indent=2,
            )
        )
        written += 1
    return written


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target_dir")
    ap.add_argument("--db", default=None)
    ap.add_argument("--jsluice", default=os.environ.get("JSLUICE", "jsluice"))
    args = ap.parse_args()

    try:
        target = resolve_target_dir(args.target_dir)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2

    if not shutil.which(args.jsluice):
        skipped = {
            "status": "skipped",
            "ts": utcnow(),
            "reason": f"jsluice binary not found in PATH ({args.jsluice!r})",
            "install": "go install github.com/BishopFox/jsluice/cmd/jsluice@latest",
        }
        write_status_phase(target, "jsluice", skipped)
        print(json.dumps(skipped, indent=2))
        return 0

    db_path = Path(args.db) if args.db else per_target_db(target)
    if not db_path.exists():
        print(f"per-target DB missing: {db_path}", file=sys.stderr)
        print(
            "run js-index then `bin/db-isolate.py snapshot ...` first.",
            file=sys.stderr,
        )
        return 3

    files = collect_js_files(target)
    if not files:
        empty = {"status": "done", "ts": utcnow(), "files_scanned": 0}
        write_status_phase(target, "jsluice", empty)
        print(json.dumps(empty, indent=2))
        return 0

    urls = jsluice_run(args.jsluice, "urls", files)
    secrets = jsluice_run(args.jsluice, "secrets", files)
    audit_file = write_audit(target, urls, secrets)
    n_drafts = write_secret_drafts(target, secrets)

    from modules.js_analyzer.tag_ingest import TagFinding, ingest

    raw_root = target / "raw"
    sources_root = target / "sources"

    findings: list[TagFinding] = []
    for u in urls:
        f_path = u.get("filename") or u.get("location", {}).get("filename")
        if not f_path:
            continue
        rel = relpath_for_node_lookup(Path(f_path), raw_root, sources_root) or f_path
        line = u.get("line") or u.get("location", {}).get("line") or 1
        url_str = u.get("url") or ""
        is_skeleton = "EXPR" in url_str
        findings.append(
            TagFinding(
                file=rel,
                line=line,
                taxonomy_id="jsluice_url",
                kind="url_skeleton" if is_skeleton else "url_literal",
                severity="medium" if is_skeleton else "low",
                source="jsluice",
            )
        )
    for s in secrets:
        f_path = s.get("filename")
        if not f_path:
            continue
        rel = relpath_for_node_lookup(Path(f_path), raw_root, sources_root) or f_path
        line = s.get("line") or 1
        kind = s.get("kind") or "generic"
        findings.append(
            TagFinding(
                file=rel,
                line=line,
                taxonomy_id="jsluice_secret",
                kind=kind,
                severity=SECRET_SEVERITY.get(kind, "low"),
                source="jsluice",
            )
        )

    conn = sqlite3.connect(str(db_path))
    try:
        stats, orphans = ingest(conn, findings)
    finally:
        conn.close()

    result = {
        "status": "done",
        "ts": utcnow(),
        "files_scanned": len(files),
        "urls_found": len(urls),
        "url_skeletons": sum(
            1 for u in urls if "EXPR" in (u.get("url") or "")
        ),
        "secrets_found": len(secrets),
        "tags_inserted": stats.inserted,
        "tags_duplicate": stats.duplicate,
        "tags_orphan": stats.orphan,
        "secret_drafts_written": n_drafts,
        "audit_file": str(audit_file.relative_to(target)),
    }
    if orphans:
        result["orphan_files_sample"] = sorted({o.file for o in orphans})[:5]

    write_status_phase(target, "jsluice", result)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
