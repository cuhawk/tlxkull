#!/usr/bin/env python3
"""Generic IDOR + BAC sweep orchestrator.

Two phases, decoupled from MCP I/O so the pure logic is testable:

  plan     <target> --requests <jsonl>   [--peer-ids <json>] [--max-mutations N]
       Reads a JSONL dump of captured requests, extracts ID candidates
       via ``id_patterns``, and emits a variant *plan* — every (request,
       mutation) pair we'd want Caido to send. Writes
       ``targets/<name>/caido/idor/plan.jsonl``.

  consume  <target>  [--plan <jsonl>] [--results <jsonl>]
       Reads ``plan.jsonl`` + a parallel ``results.jsonl`` produced by
       the Caido execution layer (skill / agent), runs the
       ``response_diff`` classifier, writes
       ``targets/<name>/findings/idor-candidates.md`` +
       ``targets/<name>/caido/idor/candidates.jsonl``.

The Caido execution layer (skill or agent) is responsible for actually
sending each variant via ``mcp__caido__caido_send_request`` /
``mcp__caido__caido_batch_send`` and recording results — that's
trivially scriptable from a Claude Code session and stays out of this
pure-Python driver.

Request-dump JSONL shape (per line):
  {
    "id":      "<caido-request-id>",
    "method":  "GET",
    "url":     "https://...",
    "headers": {"Cookie": "...", ...},
    "body":    "..."   (str | dict | null)
  }

Result JSONL shape (per line):
  {
    "request_id":  "<caido-request-id>",   # from plan.jsonl
    "variant":     "<variant-name>",       # from plan.jsonl
    "status":      200,
    "body":        "..."                   # text body
  }

Identity model:

- Baseline = the request as captured (user-A auth).
- "no_auth" variant = drop Cookie + Authorization headers. BAC probe.
- "swap_auth:<env>" variant = replace Cookie/Authorization with the
  alternate identity's value taken from ``identities`` (a dict
  loaded from CLI or from ``targets/<name>/caido/identities.json``).
- "mutate:<location>:<name>:<mutation>" variants = mutate one ID
  field at a time keeping auth.

This script never sends traffic.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    resolve_target_dir,
    utcnow,
    write_status_phase,
)
from id_patterns import (  # noqa: E402
    IdCandidate,
    enumerate_mutations,
    extract_candidates,
)
from response_diff import classify_variant  # noqa: E402


_AUTH_HEADERS_LC = {"cookie", "authorization", "x-auth-token", "x-session-id"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _drop_auth(headers: dict[str, str]) -> dict[str, str]:
    return {k: v for k, v in (headers or {}).items()
            if k.lower() not in _AUTH_HEADERS_LC}


def _swap_auth(headers: dict[str, str], identity_headers: dict[str, str]) -> dict[str, str]:
    out = _drop_auth(headers or {})
    out.update(identity_headers or {})
    return out


def _set_url_path_seg(url: str, idx: int, value: Any) -> str:
    from urllib.parse import urlparse, urlunparse, quote
    p = urlparse(url)
    segs = p.path.split("/")
    # Path always starts with "" because of leading slash; account for that.
    leading = segs[0]
    real = segs[1:] if leading == "" else segs
    if idx >= len(real):
        return url
    real[idx] = quote(str(value), safe="")
    new_path = "/".join(([leading] + real) if leading == "" else real)
    return urlunparse(p._replace(path=new_path))


def _set_query_param(url: str, name: str, value: Any) -> str:
    from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
    p = urlparse(url)
    items = parse_qsl(p.query, keep_blank_values=True)
    out: list[tuple[str, str]] = []
    replaced = False
    for k, v in items:
        if k == name and not replaced:
            out.append((k, "" if value is None else str(value)))
            replaced = True
        else:
            out.append((k, v))
    if not replaced:
        out.append((name, "" if value is None else str(value)))
    return urlunparse(p._replace(query=urlencode(out)))


def _set_json_pointer(body: Any, pointer: str, value: Any) -> Any:
    """Set ``pointer`` (JSONPath-style produced by id_patterns) to ``value``."""
    if not isinstance(body, (dict, list)):
        try:
            body = json.loads(body) if isinstance(body, str) else body
        except (ValueError, TypeError):
            return body
    if not pointer.startswith("$.body"):
        return body
    rest = pointer[len("$.body"):]
    tokens: list[str | int] = []
    i = 0
    while i < len(rest):
        if rest[i] == ".":
            j = i + 1
            while j < len(rest) and rest[j] not in ".[":
                j += 1
            tokens.append(rest[i + 1:j])
            i = j
        elif rest[i] == "[":
            j = rest.index("]", i)
            tokens.append(int(rest[i + 1:j]))
            i = j + 1
        else:
            break
    node = body
    for t in tokens[:-1]:
        try:
            node = node[t]
        except (KeyError, IndexError, TypeError):
            return body
    if tokens:
        try:
            node[tokens[-1]] = value
        except (TypeError, IndexError):
            pass
    return body


def _set_form_field(body: str, name: str, value: Any) -> str:
    from urllib.parse import parse_qsl, urlencode
    items = parse_qsl(body or "", keep_blank_values=True)
    out: list[tuple[str, str]] = []
    replaced = False
    for k, v in items:
        if k == name and not replaced:
            out.append((k, "" if value is None else str(value)))
            replaced = True
        else:
            out.append((k, v))
    if not replaced:
        out.append((name, "" if value is None else str(value)))
    return urlencode(out)


def _apply_mutation(
    req: dict,
    cand: IdCandidate,
    new_value: Any,
) -> dict:
    """Return a *new* request dict with the candidate field set to new_value."""
    out = json.loads(json.dumps(req, default=str))  # deep copy via JSON
    loc = cand.location
    if loc == "path":
        try:
            idx = int(cand.pointer.split("[")[-1].rstrip("]"))
        except ValueError:
            return out
        out["url"] = _set_url_path_seg(out.get("url", ""), idx, new_value)
    elif loc == "query":
        out["url"] = _set_query_param(out.get("url", ""), cand.name, new_value)
    elif loc == "header":
        out.setdefault("headers", {})[cand.name] = (
            "" if new_value is None else str(new_value)
        )
    elif loc == "body.json":
        body = out.get("body")
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except (ValueError, TypeError):
                return out
        body = _set_json_pointer(body, cand.pointer, new_value)
        out["body"] = body
    elif loc == "body.form":
        body = out.get("body") or ""
        if not isinstance(body, str):
            return out
        out["body"] = _set_form_field(body, cand.name, new_value)
    return out


# ---------------------------------------------------------------------------
# Plan phase
# ---------------------------------------------------------------------------

def build_variants(
    req: dict,
    *,
    identities: dict[str, dict[str, str]] | None = None,
    peer_values: Iterable[Any] = (),
    max_mutations_per_id: int = 6,
) -> list[dict]:
    """Return a list of variant dicts for one captured request."""
    identities = identities or {}
    base_id = req.get("id") or req.get("request_id") or ""
    variants: list[dict] = []

    # Always include the baseline as "self" — lets the consume phase
    # compute a baseline response without an extra dance.
    variants.append({
        "request_id": base_id,
        "variant": "baseline",
        "auth_dropped": False,
        "request": json.loads(json.dumps(req, default=str)),
    })

    # Auth probes.
    variants.append({
        "request_id": base_id,
        "variant": "no_auth",
        "auth_dropped": True,
        "request": {**json.loads(json.dumps(req, default=str)),
                    "headers": _drop_auth(req.get("headers") or {})},
    })
    for env_name, hdrs in identities.items():
        variants.append({
            "request_id": base_id,
            "variant": f"swap_auth:{env_name}",
            "auth_dropped": False,
            "request": {
                **json.loads(json.dumps(req, default=str)),
                "headers": _swap_auth(req.get("headers") or {}, hdrs),
            },
        })

    # ID mutations — keep auth unchanged so we isolate the bug class.
    cands = extract_candidates(req)
    for cand in cands:
        muts = enumerate_mutations(cand, peer_values=peer_values)[:max_mutations_per_id]
        for m in muts:
            try:
                mutated_req = _apply_mutation(req, cand, m.value)
            except Exception:  # pragma: no cover — defensive
                continue
            variants.append({
                "request_id": base_id,
                "variant": f"mutate:{cand.location}:{cand.name}:{m.name}",
                "auth_dropped": False,
                "candidate": {
                    "location": cand.location,
                    "name": cand.name,
                    "pointer": cand.pointer,
                    "shape": cand.shape.name,
                    "score": round(cand.score, 3),
                },
                "mutation": {
                    "name": m.name,
                    "value": m.value,
                    "rationale": m.rationale,
                },
                "request": mutated_req,
            })
    return variants


def plan(args: argparse.Namespace) -> int:
    target = resolve_target_dir(args.target)
    requests_path = Path(args.requests).resolve()
    if not requests_path.exists():
        print(f"missing requests file: {requests_path}", file=sys.stderr)
        return 2

    identities: dict[str, dict[str, str]] = {}
    if args.identities:
        identities = json.loads(Path(args.identities).read_text())
    else:
        ident_file = target / "caido" / "identities.json"
        if ident_file.exists():
            try:
                identities = json.loads(ident_file.read_text())
            except json.JSONDecodeError:
                identities = {}

    peer_values: list[Any] = []
    if args.peer_ids:
        peer_values = json.loads(Path(args.peer_ids).read_text())
    else:
        peer_file = target / "caido" / "peer_ids.json"
        if peer_file.exists():
            try:
                data = json.loads(peer_file.read_text())
                if isinstance(data, list):
                    peer_values = data
                elif isinstance(data, dict):
                    peer_values = list(data.values())
            except json.JSONDecodeError:
                pass

    out_dir = target / "caido" / "idor"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "plan.jsonl"

    n_reqs = 0
    n_variants = 0
    with out_path.open("w") as fh:
        for line in requests_path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
            except json.JSONDecodeError:
                continue
            n_reqs += 1
            for v in build_variants(
                req,
                identities=identities,
                peer_values=peer_values,
                max_mutations_per_id=args.max_mutations,
            ):
                fh.write(json.dumps(v, default=str) + "\n")
                n_variants += 1

    summary = {
        "target": target.name,
        "requests": n_reqs,
        "variants": n_variants,
        "plan_path": str(out_path),
        "identities": list(identities),
        "peer_values": len(peer_values),
    }
    print(json.dumps(summary, indent=2))
    write_status_phase(
        target,
        "idor_sweep_plan",
        {"status": "done", "ts": utcnow(), **summary},
    )
    return 0


# ---------------------------------------------------------------------------
# Consume phase
# ---------------------------------------------------------------------------

def _load_jsonl(path: Path) -> list[dict]:
    out = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def consume(args: argparse.Namespace) -> int:
    target = resolve_target_dir(args.target)
    plan_path = Path(args.plan) if args.plan else target / "caido" / "idor" / "plan.jsonl"
    results_path = Path(args.results) if args.results else target / "caido" / "idor" / "results.jsonl"
    if not plan_path.exists():
        print(f"missing plan: {plan_path}", file=sys.stderr)
        return 2
    if not results_path.exists():
        print(f"missing results: {results_path}", file=sys.stderr)
        return 2

    plan_rows = _load_jsonl(plan_path)
    result_rows = _load_jsonl(results_path)

    # Index plan rows by (request_id, variant). Index results the same way.
    plan_idx: dict[tuple[str, str], dict] = {
        (p["request_id"], p["variant"]): p for p in plan_rows
    }
    result_idx: dict[tuple[str, str], dict] = {
        (r["request_id"], r["variant"]): r for r in result_rows
    }

    # Baselines per request_id.
    baselines: dict[str, dict] = {
        r["request_id"]: r for r in result_rows if r.get("variant") == "baseline"
    }

    candidates: list[dict] = []
    for key, plan_row in plan_idx.items():
        req_id, variant = key
        if variant == "baseline":
            continue
        baseline = baselines.get(req_id)
        result = result_idx.get(key)
        if not baseline or not result:
            continue
        cls = classify_variant(
            baseline={"status": baseline.get("status", 0),
                      "body": baseline.get("body", "")},
            variant={"status": result.get("status", 0),
                     "body": result.get("body", "")},
            variant_name=variant,
            auth_dropped=bool(plan_row.get("auth_dropped")),
        )
        if cls.category in ("idor_candidate", "bac_candidate", "leak_partial"):
            candidates.append({
                "request_id": req_id,
                "variant": variant,
                "category": cls.category,
                "confidence": round(cls.confidence, 3),
                "rationale": cls.rationale,
                "diff": asdict(cls.diff),
                "candidate": plan_row.get("candidate"),
                "mutation": plan_row.get("mutation"),
                "request_url": (plan_row.get("request") or {}).get("url"),
                "request_method": (plan_row.get("request") or {}).get("method"),
            })

    findings_dir = target / "findings"
    findings_dir.mkdir(parents=True, exist_ok=True)
    cand_path = target / "caido" / "idor" / "candidates.jsonl"
    cand_path.parent.mkdir(parents=True, exist_ok=True)
    with cand_path.open("w") as fh:
        for c in candidates:
            fh.write(json.dumps(c, default=str) + "\n")

    md_path = findings_dir / "idor-candidates.md"
    md_path.write_text(_render_markdown(target.name, candidates))

    summary = {
        "target": target.name,
        "plan_rows": len(plan_rows),
        "result_rows": len(result_rows),
        "candidates": len(candidates),
        "by_category": _count_by_category(candidates),
        "findings_md": str(md_path),
        "candidates_jsonl": str(cand_path),
    }
    print(json.dumps(summary, indent=2))
    write_status_phase(
        target,
        "idor_sweep_consume",
        {"status": "done", "ts": utcnow(), **summary},
    )
    return 0


def _count_by_category(cands: list[dict]) -> dict[str, int]:
    out: dict[str, int] = {}
    for c in cands:
        out[c["category"]] = out.get(c["category"], 0) + 1
    return out


_CATEGORY_RANK = {"bac_candidate": 0, "idor_candidate": 1, "leak_partial": 2}


def _render_markdown(target_name: str, cands: list[dict]) -> str:
    cands_sorted = sorted(
        cands,
        key=lambda c: (_CATEGORY_RANK.get(c["category"], 99), -c["confidence"]),
    )
    lines = [
        f"# IDOR / BAC candidates — {target_name}",
        f"\nGenerated: {utcnow()}",
        f"\nTotal: {len(cands_sorted)}",
        "",
        "## Summary",
        "",
        "| Category | Count |",
        "| --- | --- |",
    ]
    counts = _count_by_category(cands)
    for cat in sorted(counts, key=lambda c: _CATEGORY_RANK.get(c, 99)):
        lines.append(f"| {cat} | {counts[cat]} |")
    lines.append("")
    lines.append("## Candidates")
    lines.append("")

    for c in cands_sorted:
        diff = c.get("diff") or {}
        lines.append(f"### {c['category']} — `{c['request_method']} {c['request_url']}`")
        lines.append("")
        lines.append(f"- **Variant:** `{c['variant']}`")
        lines.append(f"- **Confidence:** {c['confidence']}")
        lines.append(f"- **Rationale:** {c['rationale']}")
        if c.get("mutation"):
            m = c["mutation"]
            lines.append(f"- **Mutation:** `{m['name']}` → `{m['value']!r}` "
                         f"({m['rationale']})")
        if c.get("candidate"):
            k = c["candidate"]
            lines.append(
                f"- **ID candidate:** {k['location']} `{k['name']}` "
                f"(shape={k['shape']}, score={k['score']})"
            )
        lines.append(
            f"- **Diff:** parity={diff.get('parity', 0):.2f}, "
            f"status {diff.get('baseline_status')}→{diff.get('variant_status')}, "
            f"body {diff.get('baseline_len')}→{diff.get('variant_len')} bytes"
        )
        if diff.get("pii"):
            lines.append(f"- **PII present:** {', '.join(diff['pii'])}")
        lines.append("")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("plan", help="Build variant plan from a captured-request JSONL")
    p.add_argument("target")
    p.add_argument("--requests", required=True,
                   help="JSONL of captured requests (caido_list_requests output)")
    p.add_argument("--identities", default=None,
                   help="JSON {<env-name>: {<header>: <value>, ...}, ...}")
    p.add_argument("--peer-ids", default=None,
                   help="JSON list of known peer-user identifier values")
    p.add_argument("--max-mutations", type=int, default=6,
                   help="Max mutations per ID candidate (default 6)")
    p.set_defaults(func=plan)

    c = sub.add_parser("consume", help="Diff results against baselines, emit findings")
    c.add_argument("target")
    c.add_argument("--plan", default=None)
    c.add_argument("--results", default=None)
    c.set_defaults(func=consume)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
