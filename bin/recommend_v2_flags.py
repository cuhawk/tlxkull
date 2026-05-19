#!/usr/bin/env python3
"""Recommend V2 feature flags for a target based on detected signals.

V2 stages (plans/ARCHITECTURE_EVOLUTION_V2.md §11-§24) ship behind env
flags and default off. That makes them invisible to operators who don't
know what to enable. This script reads:

  - targets/<name>/index/frameworks.json (detected framework set)
  - targets/<name>/chains/triage.json (sink/source taxonomies present)
  - targets/<name>/sources/ (cheap grep for postMessage / localStorage /
    service-worker / heavy minification signals)

…and writes:

  - targets/<name>/v2_flags.env  (sourceable: `export JS_ENABLE_X=1`)
  - status.json.phases.v2_recommend.flags (machine-readable)

Run after js-index + extract_chains_bounded so signals are populated.
Idempotent. Read-only against TLX DB. No LLM calls — pure heuristic.

Usage:
  python3 bin/recommend_v2_flags.py <target>
  source targets/<target>/v2_flags.env  # then run v2-pipeline
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    resolve_target_dir,
    utcnow,
    write_status_phase,
)


# Flag → list of reasons. Reasons are recorded for the audit trail in
# v2_flags.env header + status.json so the operator can see why a flag
# fired. Off by default: only added if at least one trigger matched.
def recommend(target: Path) -> tuple[dict[str, list[str]], dict]:
    frameworks_path = target / "index" / "frameworks.json"
    triage_path = target / "chains" / "triage.json"
    sources_dir = target / "sources"

    frameworks: list[str] = []
    if frameworks_path.exists():
        try:
            data = json.loads(frameworks_path.read_text())
            if isinstance(data, list):
                frameworks = [str(x).lower() for x in data]
            elif isinstance(data, dict):
                frameworks = [str(x).lower() for x in data.get("detected", [])]
        except (json.JSONDecodeError, OSError):
            pass

    sink_dist: dict[str, int] = {}
    src_dist: dict[str, int] = {}
    if triage_path.exists():
        try:
            triage = json.loads(triage_path.read_text())
            sink_dist = triage.get("sink_dist") or {}
            src_dist = triage.get("source_dist") or {}
        except (json.JSONDecodeError, OSError):
            pass

    # Cheap source scan — bounded to first 200 JS files to stay sub-second.
    signals = {
        "postmessage": False,
        "localstorage": False,
        "service_worker": False,
        "trusted_types": False,
        "minified_heavy": False,
    }
    if sources_dir.exists():
        pm_re = re.compile(r"\b(postMessage|onmessage|addEventListener\(['\"]message)")
        ls_re = re.compile(r"\b(localStorage|sessionStorage)\b")
        sw_re = re.compile(r"\b(serviceWorker|importScripts|self\.skipWaiting)\b")
        tt_re = re.compile(r"\btrustedTypes\.createPolicy\b")
        scanned = 0
        long_lines = 0
        total_lines = 0
        for js in sources_dir.rglob("*.js"):
            if scanned >= 200:
                break
            try:
                txt = js.read_text(errors="ignore")
            except OSError:
                continue
            scanned += 1
            if not signals["postmessage"] and pm_re.search(txt):
                signals["postmessage"] = True
            if not signals["localstorage"] and ls_re.search(txt):
                signals["localstorage"] = True
            if not signals["service_worker"] and sw_re.search(txt):
                signals["service_worker"] = True
            if not signals["trusted_types"] and tt_re.search(txt):
                signals["trusted_types"] = True
            lines = txt.splitlines()
            total_lines += len(lines)
            long_lines += sum(1 for ln in lines if len(ln) > 500)
        if total_lines and long_lines / max(1, total_lines) > 0.05:
            signals["minified_heavy"] = True

    flags: dict[str, list[str]] = {}

    def _add(flag: str, reason: str) -> None:
        flags.setdefault(flag, []).append(reason)

    # Always-recommend (safe + cheap):
    _add("JS_ENABLE_PARSER_CONTEXT", "default-on; explicit confirmation")
    _add("JS_ENABLE_CHAIN_COMPRESSION", "default-on; LLM token cost reduction")

    # Framework-driven:
    fw_set = set(frameworks)
    if fw_set & {"react", "vue", "svelte", "next", "nuxt", "angular", "solid"}:
        _add("JS_ENABLE_AUTH_ABUSE",
             f"modern SPA framework detected: {sorted(fw_set)}")
    # Origin trust whenever postMessage usage observed:
    if signals["postmessage"]:
        _add("JS_ENABLE_ORIGIN_TRUST",
             "postMessage / onmessage references present in sources")
    # Persistent taint when storage APIs used:
    if signals["localstorage"]:
        _add("JS_ENABLE_PERSISTENT_TAINT",
             "localStorage / sessionStorage references present in sources")
    # Worker semantics when service worker code present:
    if signals["service_worker"]:
        _add("JS_ENABLE_WORKER_SEMANTICS",
             "serviceWorker / importScripts / skipWaiting references in sources")
    # Sink-distribution-driven:
    if any("pp_" in s or "proto" in s for s in sink_dist):
        _add("JS_ENABLE_PP_GADGETS",
             f"prototype-pollution sinks present: "
             f"{[s for s in sink_dist if 'pp_' in s or 'proto' in s][:3]}")
    if any("clobber" in s for s in sink_dist):
        _add("JS_ENABLE_DOM_CLOBBER",
             "DOM-clobber-related sinks present")
    # Deobfuscation: turn on for heavily minified targets w/ no sourcemaps.
    if signals["minified_heavy"]:
        _add("JS_ENABLE_DEOBFUSCATION_NORMALIZE",
             "heavy minification detected (>5% lines >500 chars) — "
             "deobfuscation pre-pass likely helpful")
    # Sink reachability: always useful on big targets to prune dead paths.
    if sink_dist and sum(sink_dist.values()) >= 500:
        _add("JS_ENABLE_SINK_REACHABILITY",
             f"large chain corpus ({sum(sink_dist.values())} sinks) — "
             "lifecycle/route gating worth the cost")

    summary = {
        "frameworks": frameworks,
        "signals": signals,
        "sink_dist_top": dict(list(sink_dist.items())[:5]),
        "source_dist_top": dict(list(src_dist.items())[:5]),
    }
    return flags, summary


def write_env(target: Path, flags: dict[str, list[str]], summary: dict) -> Path:
    out = target / "v2_flags.env"
    lines = [
        "# V2 feature-flag recommendation — auto-generated.",
        f"# Generated: {utcnow()}",
        "# Source this file before running v2-pipeline or chain-bestfirst:",
        "#   source v2_flags.env",
        "# Override individual flags by exporting after sourcing.",
        f"# Signals: {json.dumps(summary['signals'])}",
        f"# Frameworks: {json.dumps(summary['frameworks'])}",
        "",
    ]
    for flag, reasons in sorted(flags.items()):
        for reason in reasons:
            lines.append(f"# {flag}: {reason}")
        lines.append(f"export {flag}=1")
        lines.append("")
    out.write_text("\n".join(lines).rstrip() + "\n")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--no-status", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        target = resolve_target_dir(args.target)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    t0 = time.monotonic()
    flags, summary = recommend(target)
    env_path = write_env(target, flags, summary)
    elapsed = time.monotonic() - t0

    result = {
        "target": target.name,
        "env_path": str(env_path.relative_to(target.parent.parent)),
        "flags": {f: reasons for f, reasons in sorted(flags.items())},
        "summary": summary,
        "elapsed_s": round(elapsed, 3),
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"wrote {env_path} ({len(flags)} flags, {elapsed:.2f}s)")
        for f, reasons in sorted(flags.items()):
            print(f"  {f}  ← {reasons[0]}")

    if not args.no_status:
        write_status_phase(target, "v2_recommend", {
            "status": "done",
            "ts": utcnow(),
            "env_path": str(env_path.relative_to(target)),
            "flags": list(flags.keys()),
            "signals": summary["signals"],
            "frameworks": summary["frameworks"],
        })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
