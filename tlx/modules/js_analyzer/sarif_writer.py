"""SARIF 2.1.0 writer.

Converts a Phase 3 findings payload + the Markdown report Claude produces
into a SARIF document that GitHub Code Scanning, VS Code's Problems panel,
and Burp Suite Pro can ingest directly.

Pure stdlib — no anthropic / google / chromadb / project imports. Safe to
call from any output sink.
"""

import re
from pathlib import Path  # noqa: F401  (Path is used for type hints by callers)

SARIF_SCHEMA = (
    "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/"
    "master/Schemata/sarif-schema-2.1.0.json"
)
SARIF_VERSION   = "2.1.0"
TOOL_NAME       = "tlx-js-analyzer"
TOOL_VERSION    = "0.1.0"
TOOL_URI        = "https://github.com/cuhawk/tlx"

_SEVERITY_TO_LEVEL: dict[str, str] = {
    "high":   "error",
    "medium": "warning",
    "low":    "note",
}
_LEVEL_ORDER: dict[str, int] = {"note": 0, "warning": 1, "error": 2}


# ── Markdown parsing ────────────────────────────────────────────────────────

_SECTION_RE = re.compile(r"^##\s+(.+?)\s*$")
_CHAIN_RE   = re.compile(r"^###\s+\[CHAIN-(\d+)\]\s*(.*)$")
_PROOF_RE   = re.compile(r"^\*\*Proof:\*\*\s*(.*)$")


def _parse_true_positives(report: str) -> list[dict]:
    """Walk the Markdown report and pull true-positive chain entries.

    Returns a list of dicts: {chain_id, severity, vuln_class?, proof?}.
    Never raises. Malformed [CHAIN-N] headers are skipped silently.
    """
    if not report:
        return []

    out: list[dict] = []
    current_severity: str | None = None
    in_false_positives = False
    current: dict | None = None

    for line in report.splitlines():
        section = _SECTION_RE.match(line)
        if section:
            heading = section.group(1).strip().lower()
            in_false_positives = heading.startswith("false positive")
            if heading.endswith("severity"):
                first = heading.split()[0]
                current_severity = first if first in _SEVERITY_TO_LEVEL else None
            else:
                current_severity = None
            current = None
            continue

        if in_false_positives or current_severity is None:
            continue

        chain_match = _CHAIN_RE.match(line)
        if chain_match:
            try:
                cid = int(chain_match.group(1))
            except ValueError:
                print(f"[sarif] warning: malformed chain id in: {line!r}")
                current = None
                continue
            tail = (chain_match.group(2) or "").strip()
            vuln_class = tail.split(" — ", 1)[0].strip() if tail else ""
            current = {
                "chain_id":   cid,
                "severity":   current_severity,
                "vuln_class": vuln_class or None,
                "proof":      None,
            }
            out.append(current)
            continue

        if current is not None:
            proof = _PROOF_RE.match(line)
            if proof:
                current["proof"] = proof.group(1).strip()

    return out


# ── Helpers ─────────────────────────────────────────────────────────────────

def _pascal_case(rule_id: str) -> str:
    """innerHTML_assign → InnerhtmlAssign."""
    parts = re.split(r"[_\-\s]+", rule_id or "")
    return "".join(p[:1].upper() + p[1:].lower() for p in parts if p) or rule_id


def _short_description(rule_id: str) -> str:
    return (rule_id or "").replace("_", " ").strip() or rule_id


def _physical_location(file: str, line) -> dict:
    try:
        line_int = int(line)
    except (TypeError, ValueError):
        line_int = 1
    if line_int < 1:
        line_int = 1
    return {
        "artifactLocation": {"uri": file or "", "uriBaseId": "%SRCROOT%"},
        "region":           {"startLine": line_int},
    }


def _bump_level(current: str, candidate: str) -> str:
    if _LEVEL_ORDER.get(candidate, 0) > _LEVEL_ORDER.get(current, 0):
        return candidate
    return current


# ── Public API ──────────────────────────────────────────────────────────────

def build_sarif(findings: dict, report: str) -> dict:
    """Produce a SARIF 2.1.0 dict from a findings payload + Markdown report.

    Always returns a valid SARIF document. An empty / missing input yields
    a run with empty results — never raises.
    """
    findings = findings or {}
    chains_by_id: dict[int, dict] = {
        c["id"]: c
        for c in findings.get("chains", []) or []
        if isinstance(c, dict) and isinstance(c.get("id"), int)
    }

    true_positives = _parse_true_positives(report or "")

    results: list[dict] = []
    rule_levels: dict[str, str] = {}
    artifact_uris: set[str] = set()

    for tp in true_positives:
        chain = chains_by_id.get(tp["chain_id"])
        if chain is None:
            print(f"[sarif] warning: CHAIN-{tp['chain_id']} not present in findings; skipped")
            continue

        sink   = chain.get("sink")   or {}
        source = chain.get("source") or {}
        sink_id   = sink.get("taxonomy_id") or ""
        sink_file = sink.get("file") or ""
        if not sink_id or not sink_file:
            print(f"[sarif] warning: CHAIN-{tp['chain_id']} missing sink id/file; skipped")
            continue

        level = _SEVERITY_TO_LEVEL.get(tp.get("severity") or "", "warning")
        message_text = (
            tp.get("proof")
            or tp.get("vuln_class")
            or f"Chain {tp['chain_id']} reaches sink {sink_id}"
        )

        result = {
            "ruleId":  sink_id,
            "level":   level,
            "message": {"text": message_text},
            "locations": [{
                "physicalLocation": _physical_location(sink_file, sink.get("line")),
                "logicalLocations": [{
                    "name": sink.get("qname") or sink_id,
                    "kind": "function",
                }],
            }],
            "partialFingerprints": {
                "chainId/v1": str(tp["chain_id"]),
            },
        }

        src_file = source.get("file") or ""
        if src_file:
            result["relatedLocations"] = [{
                "id":      1,
                "message": {"text": "Source"},
                "physicalLocation": _physical_location(src_file, source.get("line")),
            }]
            artifact_uris.add(src_file)

        artifact_uris.add(sink_file)
        rule_levels[sink_id] = _bump_level(rule_levels.get(sink_id, "note"), level)
        results.append(result)

    # Rules: every unique taxonomy_id referenced anywhere in findings.
    rule_ids: set[str] = set(rule_levels)
    for chain in chains_by_id.values():
        for endpoint_key in ("source", "sink"):
            tid = (chain.get(endpoint_key) or {}).get("taxonomy_id") or ""
            if tid:
                rule_ids.add(tid)

    rules = [
        {
            "id":   rid,
            "name": _pascal_case(rid),
            "shortDescription":     {"text": _short_description(rid)},
            "defaultConfiguration": {"level": rule_levels.get(rid, "warning")},
        }
        for rid in sorted(rule_ids)
    ]

    artifacts = [
        {"location": {"uri": uri, "uriBaseId": "%SRCROOT%"}}
        for uri in sorted(artifact_uris)
    ]

    return {
        "$schema": SARIF_SCHEMA,
        "version": SARIF_VERSION,
        "runs": [{
            "tool": {
                "driver": {
                    "name":           TOOL_NAME,
                    "version":        TOOL_VERSION,
                    "informationUri": TOOL_URI,
                    "rules":          rules,
                },
            },
            "results":   results,
            "artifacts": artifacts,
        }],
    }
