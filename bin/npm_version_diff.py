#!/usr/bin/env python3
"""npm-package patch diff (T3.1).

Pull two versions of an npm package via ``npm pack``, unpack into a temp
dir, and diff the two trees with attention to security-control
invocations (auth checks, sanitizers, CSRF, role gates). Surfaces
ADDED / REMOVED control calls per file as actionable signal.

Usage:
  bin/npm_version_diff.py <target_dir> <package> <old_version> <new_version>

Output:
    targets/<name>/diffs/<package>_<old>_<new>.md
    status.json.phases.patch_diff_<package>

Requires: ``npm`` in PATH. Skips with ``status: skipped`` otherwise.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import resolve_target_dir, utcnow, write_status_phase  # noqa: E402


CONTROL_PATTERNS = [
    re.compile(r"\b(?:require|requires?)Role\s*\(", re.IGNORECASE),
    re.compile(r"\bDOMPurify\.sanitize\s*\("),
    re.compile(r"\bcsrf\.(?:verify|protect|check)\s*\("),
    re.compile(r"\bisAuthenticated\s*\("),
    re.compile(r"\bcheckPermission\s*\("),
    re.compile(r"\bencodeURIComponent\s*\("),
    re.compile(r"\bsanitize(?:Html|HTML|Url|URL)?\s*\("),
    re.compile(r"\brateLimit\s*\("),
]


def npm_pack(pkg: str, version: str, out_dir: Path) -> Path | None:
    proc = subprocess.run(
        ["npm", "pack", f"{pkg}@{version}", "--silent"],
        capture_output=True,
        text=True,
        cwd=out_dir,
        timeout=120,
    )
    if proc.returncode != 0:
        return None
    tarball = (proc.stdout.strip().splitlines() or [""])[-1]
    p = out_dir / tarball
    return p if p.exists() else None


def extract(tarball: Path, dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tarball) as tf:
        # filter='data' rejects absolute paths and `..` traversal members.
        # Required: npm tarballs are externally controlled.
        tf.extractall(dest, filter="data")
    pkg_dir = dest / "package"
    return pkg_dir if pkg_dir.exists() else dest


_VER_SAFE = re.compile(r"[^a-zA-Z0-9._-]")


def _safe_ver(v: str) -> str:
    return _VER_SAFE.sub("_", v)[:40] or "unknown"


def control_hits(content: str) -> dict[str, int]:
    hits: dict[str, int] = {}
    for rx in CONTROL_PATTERNS:
        n = len(rx.findall(content))
        if n:
            hits[rx.pattern] = n
    return hits


def walk_js(root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for p in root.rglob("*"):
        if p.is_file() and p.suffix in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}:
            try:
                out[str(p.relative_to(root))] = p.read_text(
                    encoding="utf-8", errors="replace"
                )
            except OSError:
                continue
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target_dir")
    ap.add_argument("package")
    ap.add_argument("old_version")
    ap.add_argument("new_version")
    args = ap.parse_args()

    try:
        target = resolve_target_dir(args.target_dir)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2
    if not shutil.which("npm"):
        skipped = {"status": "skipped", "ts": utcnow(), "reason": "npm not in PATH"}
        write_status_phase(target, f"patch_diff_{args.package}", skipped)
        print(json.dumps(skipped, indent=2))
        return 0

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        old_tb = npm_pack(args.package, args.old_version, td_path)
        new_tb = npm_pack(args.package, args.new_version, td_path)
        if not (old_tb and new_tb):
            err = {
                "status": "error",
                "ts": utcnow(),
                "reason": f"npm pack failed for {args.package}@{args.old_version} or {args.new_version}",
            }
            write_status_phase(target, f"patch_diff_{args.package}", err)
            print(json.dumps(err, indent=2))
            return 4
        old_tree = walk_js(extract(old_tb, td_path / "old"))
        new_tree = walk_js(extract(new_tb, td_path / "new"))

        files_added = sorted(set(new_tree) - set(old_tree))
        files_removed = sorted(set(old_tree) - set(new_tree))
        common = sorted(set(old_tree) & set(new_tree))

        delta_controls: list[dict] = []
        for f in common:
            o_hits = control_hits(old_tree[f])
            n_hits = control_hits(new_tree[f])
            keys = set(o_hits) | set(n_hits)
            for k in keys:
                d = n_hits.get(k, 0) - o_hits.get(k, 0)
                if d != 0:
                    delta_controls.append({"file": f, "control": k, "delta": d})
        for f in files_added:
            for k, n in control_hits(new_tree[f]).items():
                delta_controls.append({"file": f, "control": k, "delta": n, "kind": "added_file"})
        for f in files_removed:
            for k, n in control_hits(old_tree[f]).items():
                delta_controls.append({"file": f, "control": k, "delta": -n, "kind": "removed_file"})

        diffs_dir = target / "diffs"
        diffs_dir.mkdir(parents=True, exist_ok=True)
        safe_pkg = _safe_ver(args.package.replace("/", "__"))
        out_md = diffs_dir / f"{safe_pkg}_{_safe_ver(args.old_version)}_{_safe_ver(args.new_version)}.md"
        with out_md.open("w") as f:
            f.write(f"# {args.package} {args.old_version} → {args.new_version}\n\n")
            f.write(f"Generated: {utcnow()}\n\n")
            f.write(f"## Files\n- added: {len(files_added)}\n- removed: {len(files_removed)}\n- common: {len(common)}\n\n")
            f.write("## Security control delta\n\n")
            if not delta_controls:
                f.write("No control invocations changed.\n\n")
            else:
                f.write("| file | control | delta |\n|---|---|---|\n")
                for d in sorted(delta_controls, key=lambda x: -abs(x.get("delta", 0))):
                    f.write(
                        f"| `{d['file']}` | `{d['control']}` | {d['delta']:+d} |\n"
                    )

        result = {
            "status": "done",
            "ts": utcnow(),
            "package": args.package,
            "old": args.old_version,
            "new": args.new_version,
            "files_added": len(files_added),
            "files_removed": len(files_removed),
            "files_common": len(common),
            "control_changes": len(delta_controls),
            "output": str(out_md.relative_to(target)),
        }
        write_status_phase(target, f"patch_diff_{args.package.replace('/', '__')}", result)
        print(json.dumps(result, indent=2))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
