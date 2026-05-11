"""js_analyzer module — Phase 4 port of GFA call-graph analyzer."""
from __future__ import annotations

import hashlib
import json
import json as _json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog
from pydantic import BaseModel

from kernel.modules import ModuleSpec, RegisteredModule
from kernel.slash import SlashCommand
from kernel.tools import Tool
from modules.js_analyzer.tools.preprocess_js import preprocess_js
from modules.js_analyzer.tools.sourcemap_extractor import extract_source_map

_logger = structlog.get_logger(__name__)


def _emit_progress(kernel: Any, stage: str, detail: str = "") -> None:
    fn = getattr(kernel, "report_progress", None)
    if callable(fn):
        try:
            fn(stage, detail)
        except Exception:
            pass


@dataclass
class JsAnalyzerState:
    # Set by /js_analyzer-report before the loop
    last_findings: dict | None = None

    # Set by js_generate_report tool
    last_report: str | None = None

    # Live audit state — reset on each /js_analyzer-report call
    verdicts:     dict        = field(default_factory=dict)
    reviewed:     set         = field(default_factory=set)
    hypotheses:   dict        = field(default_factory=dict)  # int → dict
    audit_status: str         = "idle"   # "idle" | "running" | "done"
    total_chains: int         = 0

    # Cost telemetry — set on each audit completion
    last_audit_cost_usd: float = 0.0
    last_audit_tokens:   int   = 0

    # js_consult_opus telemetry — set on each audit completion
    last_consult_log:        list[dict] = field(default_factory=list)
    last_consult_cost_usd:   float       = 0.0
    last_consults_used:      int         = 0


class JsAnalyzerConfig(BaseModel):
    db_path: str = str(Path.home() / ".tlx" / "js_analyzer.db")
    target: str = ""
    deobfuscate: bool = False
    exploit_mode: bool = False
    max_chains: int = 20
    severity: str = "high"
    exclude_dirs: list[str] = [
        "node_modules", ".angular", ".next", ".nuxt", ".cache",
        "dist", "build", "out", "vendor", "bower_components",
        "coverage", ".turbo",
    ]


def _walk_js_files(root: Path, exclude_dirs: list[str]) -> list[dict]:
    excludes = set(exclude_dirs)
    out: list[dict] = []
    for p in root.rglob("*.js"):
        if not p.is_file():
            continue
        if any(part in excludes for part in p.parts):
            continue
        out.append({"abs": str(p.resolve()), "rel": str(p.relative_to(root))})
    return out


def _chain_signature(chain: dict) -> str:
    src = chain.get("source", {}) or {}
    sink = chain.get("sink", {}) or {}
    raw = (
        f"{src.get('qname', '')}|{src.get('line', '')}|"
        f"{sink.get('qname', '')}|{sink.get('line', '')}"
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _save_hypotheses_kv(kernel: Any, hypotheses_by_sig: dict) -> None:
    """Persist hypotheses (sig-keyed) to session KV."""
    try:
        payload = _json.dumps(
            {str(k): v for k, v in hypotheses_by_sig.items()}
        )
        kernel.session_store.set("js_analyzer_hypotheses", payload)
    except Exception:
        _logger.warning("js_analyzer.hypothesis_kv_save_failed", exc_info=True)


def _load_hypotheses_kv(kernel: Any) -> dict:
    """Load sig-keyed hypotheses from session KV. Returns {} if absent.

    If old chain_id-keyed payloads are encountered (any key parses as int),
    drop them silently and emit a structlog info event.
    """
    try:
        raw = kernel.session_store.get("js_analyzer_hypotheses")
        if raw is None:
            return {}
        decoded = _json.loads(raw)
        if not isinstance(decoded, dict):
            return {}
        legacy = False
        for k in decoded.keys():
            try:
                int(k)
                legacy = True
                break
            except (TypeError, ValueError):
                continue
        if legacy:
            _logger.info("js_analyzer.hypothesis_kv_legacy_dropped")
            return {}
        return {str(k): v for k, v in decoded.items()}
    except Exception:
        _logger.warning("js_analyzer.hypothesis_kv_load_failed", exc_info=True)
        return {}


def _persist_hypotheses(kernel: Any, state: Any) -> None:
    """Translate runtime chain_id-keyed hypotheses to sig-keyed and save."""
    sigs: dict = dict(getattr(state, "sigs_by_id", {}) or {})
    if not sigs and state.last_findings is not None:
        sigs = {
            c["id"]: _chain_signature(c)
            for c in state.last_findings.get("chains", [])
        }
    out: dict[str, dict] = {}
    for cid, hyp in state.hypotheses.items():
        sig = sigs.get(cid)
        if sig is None:
            continue
        out[sig] = hyp
    _save_hypotheses_kv(kernel, out)


def _save_verdicts_kv(kernel: Any, verdicts: dict) -> None:
    try:
        payload = _json.dumps({str(k): v for k, v in verdicts.items()})
        kernel.session_store.set("js_analyzer_verdicts_inflight", payload)
    except Exception:
        _logger.warning("js_analyzer.verdicts_kv_save_failed", exc_info=True)


def _load_verdicts_kv(kernel: Any) -> dict:
    try:
        raw = kernel.session_store.get("js_analyzer_verdicts_inflight")
        if raw is None:
            return {}
        decoded = _json.loads(raw)
        if not isinstance(decoded, dict):
            return {}
        return {int(k): v for k, v in decoded.items()}
    except Exception:
        _logger.warning("js_analyzer.verdicts_kv_load_failed", exc_info=True)
        return {}


def _clear_verdicts_kv(kernel: Any) -> None:
    try:
        kernel.session_store.set("js_analyzer_verdicts_inflight", "{}")
    except Exception:
        pass


def _tool_examine_chain(kernel: Any, chain_id: int) -> str:
    state = kernel.services.get("js_analyzer_state")
    if state is None or state.last_findings is None:
        return _json.dumps({"error": "no findings — run /js_analyzer-report first"})
    findings = state.last_findings
    chain = next((c for c in findings["chains"] if c["id"] == chain_id), None)
    if not chain:
        ids = [c["id"] for c in findings["chains"]]
        return _json.dumps({"error": f"chain {chain_id} not found", "valid_ids": ids})
    snippets = {
        q: findings["snippets"].get(q, "<unavailable>")
        for q in chain["path"]
    }
    return _json.dumps({"chain": chain, "snippets": snippets})


def _tool_get_snippet(kernel: Any, qname: str) -> str:
    state = kernel.services.get("js_analyzer_state")
    if state is None or state.last_findings is None:
        return _json.dumps({"error": "no findings cached"})
    snippet = state.last_findings["snippets"].get(qname)
    if snippet is None:
        available = list(state.last_findings["snippets"].keys())[:10]
        return _json.dumps({"error": f"no snippet for {qname!r}",
                            "available_sample": available})
    return _json.dumps({"qname": qname, "source": snippet})


def _tool_submit_finding(
    kernel: Any,
    chain_id: int,
    verdict: str,
    proof: str,
    severity: str = "n/a",
    vuln_class: str = "",
) -> str:
    state = kernel.services.get("js_analyzer_state")
    if state is None:
        return _json.dumps({"error": "state missing"})
    state.verdicts[chain_id] = {
        "chain_id":   chain_id,
        "verdict":    verdict,
        "severity":   severity,
        "vuln_class": vuln_class,
        "proof":      proof,
    }
    state.reviewed.add(chain_id)
    remaining = state.total_chains - len(state.reviewed)
    _persist_hypotheses(kernel, state)
    _save_verdicts_kv(kernel, state.verdicts)
    return _json.dumps({
        "ok": True,
        "verdict_recorded": verdict,
        "chains_remaining": remaining,
    })


def _tool_generate_report(kernel: Any) -> str:
    state = kernel.services.get("js_analyzer_state")
    if state is None or state.last_findings is None:
        return _json.dumps({"error": "no findings"})
    findings = state.last_findings
    by_id = {c["id"]: c for c in findings["chains"]}
    tp = {cid: v for cid, v in state.verdicts.items()
          if v["verdict"] == "true_positive"}
    fp = {cid: v for cid, v in state.verdicts.items()
          if v["verdict"] == "false_positive"}

    lines = [
        "# Security Analysis Report",
        f"**Target:** {findings['target_folder']}",
        (f"**Chains analysed:** {state.total_chains}  |  "
         f"**True positives:** {len(tp)}  |  "
         f"**False positives:** {len(fp)}"),
        "",
        "---",
    ]
    for severity in ("high", "medium", "low"):
        bucket = [v for v in tp.values() if v.get("severity") == severity]
        lines.append(f"\n## {severity.capitalize()} Severity\n")
        if not bucket:
            lines.append("_No findings._")
            continue
        for v in bucket:
            chain = by_id.get(v["chain_id"], {})
            src  = chain.get("source", {})
            sink = chain.get("sink", {})
            path = " → ".join(chain.get("path", []))
            lines += [
                f"### [CHAIN-{v['chain_id']}] {v['vuln_class']} — "
                f"{src.get('file','')}:{src.get('line','')}",
                f"**Source:** `{src.get('qname','')}` at "
                f"`{src.get('file','')}:{src.get('line','')}`",
                f"**Sink:**   `{sink.get('qname','')}` at "
                f"`{sink.get('file','')}:{sink.get('line','')}`",
                f"**Path:** `{path}`",
                f"**Proof:** {v['proof']}",
                "",
                "---",
            ]
    lines.append("\n## False Positives\n")
    if not fp:
        lines.append("_None._")
    else:
        for v in fp.values():
            lines.append(f"### [CHAIN-{v['chain_id']}] {v['proof']}")

    consult_log = list(getattr(state, "last_consult_log", []) or [])
    if consult_log:
        consult_total = float(getattr(state, "last_consult_cost_usd", 0.0))
        lines.append("\n## Opus consultations\n")
        lines.append("| # | Chain | Confidence | Tokens | Cost |")
        lines.append("|---|-------|------------|--------|------|")
        for i, entry in enumerate(consult_log, 1):
            tok = entry.get("tokens_in", 0) + entry.get("tokens_out", 0)
            lines.append(
                f"| {i} | {entry.get('chain_id','?')} | "
                f"{entry.get('confidence','?')} | {tok} | "
                f"${entry.get('cost_usd', 0.0):.4f} |"
            )
        lines.append(f"\n**Consult total:** ${consult_total:.4f}")

    report = "\n".join(lines)
    state.last_report   = report
    state.audit_status  = "done"
    _clear_verdicts_kv(kernel)
    return _json.dumps({"report": report, "ok": True})


def _tool_update_hypothesis(
    kernel: Any,
    chain_id: int,
    status: str = "open",
    note: str = "",
    confidence: float = 0.5,
    tested_path: str = "",
) -> str:
    state = kernel.services.get("js_analyzer_state")
    if state is None:
        return _json.dumps({"error": "state missing"})
    existing = state.hypotheses.get(chain_id, {
        "status": "open", "notes": [], "tested_paths": [], "confidence": 0.5,
    })
    existing["status"]     = status
    existing["confidence"] = max(0.0, min(1.0, confidence))
    if note:
        existing["notes"].append(note)
    if tested_path and tested_path not in existing["tested_paths"]:
        existing["tested_paths"].append(tested_path)
    state.hypotheses[chain_id] = existing
    _persist_hypotheses(kernel, state)
    return _json.dumps({"ok": True, "chain_id": chain_id, "hypothesis": existing})


def _tool_get_hypothesis(kernel: Any, chain_id: int) -> str:
    state = kernel.services.get("js_analyzer_state")
    if state is None:
        return _json.dumps({"error": "state missing"})
    hyp = state.hypotheses.get(chain_id, {
        "status": "open", "notes": [], "tested_paths": [], "confidence": 0.5,
    })
    return _json.dumps(hyp)


def _make_tools(kernel: Any, cfg: JsAnalyzerConfig) -> list[Tool]:
    """Build kernel Tool wrappers for the call-graph handlers."""
    from modules.js_analyzer import callgraph_tools as ct

    return [
        Tool(
            name="find_sinks",
            description=(
                "List sink-tagged nodes from the JS call graph. "
                "Filter by severity ('high'/'medium'/'low') and/or file_glob "
                "(fnmatch). Truncates at 50."
            ),
            params={
                "type": "object",
                "properties": {
                    "severity":  {"type": "string"},
                    "file_glob": {"type": "string"},
                },
            },
            handler=lambda severity=None, file_glob=None: ct.find_sinks(
                severity=severity, file_glob=file_glob
            ),
        ),
        Tool(
            name="list_entry_points",
            description=(
                "List source-tagged nodes (taint entry points). "
                "Optional file_glob restricts by rel path. Truncates at 50."
            ),
            params={
                "type": "object",
                "properties": {"file_glob": {"type": "string"}},
            },
            handler=lambda file_glob=None: ct.list_entry_points(file_glob=file_glob),
        ),
        Tool(
            name="trace_to_sink",
            description=(
                "BFS call paths from from_qname to any sink-tagged node. "
                "Returns shortest paths first. Truncates at 50."
            ),
            params={
                "type": "object",
                "properties": {
                    "from_qname":        {"type": "string"},
                    "max_depth":         {"type": "integer"},
                    "severity":          {"type": "string"},
                    "exclude_sanitised": {"type": "boolean"},
                },
                "required": ["from_qname"],
            },
            handler=lambda from_qname, max_depth=8, severity=None,
                          exclude_sanitised=False: ct.trace_to_sink(
                from_qname=from_qname, max_depth=max_depth,
                severity=severity, exclude_sanitised=exclude_sanitised,
            ),
        ),
        Tool(
            name="get_callers",
            description="Direct callers of qname (in-edges).",
            params={
                "type": "object",
                "properties": {"qname": {"type": "string"}},
                "required": ["qname"],
            },
            handler=lambda qname: ct.get_callers(qname=qname),
        ),
        Tool(
            name="get_callees",
            description="Direct callees of qname (out-edges).",
            params={
                "type": "object",
                "properties": {"qname": {"type": "string"}},
                "required": ["qname"],
            },
            handler=lambda qname: ct.get_callees(qname=qname),
        ),
        Tool(
            name="get_function_source",
            description="Source text of the function/method identified by qname.",
            params={
                "type": "object",
                "properties": {"qname": {"type": "string"}},
                "required": ["qname"],
            },
            handler=lambda qname: ct.get_function_source(qname=qname),
            requires=["path_access"],
        ),
        Tool(
            name="find_intra_function_flows",
            description=(
                "Direct intra-function source→sink flows with variable-level "
                "tracking. Filter by qualified_name, source_rule, sink_rule, "
                "or include_sanitised. Truncates at 50."
            ),
            params={
                "type": "object",
                "properties": {
                    "qualified_name":    {"type": "string"},
                    "source_rule":       {"type": "string"},
                    "sink_rule":         {"type": "string"},
                    "include_sanitised": {"type": "boolean"},
                },
            },
            handler=lambda qualified_name=None, source_rule=None,
                          sink_rule=None, include_sanitised=True:
                ct.find_intra_function_flows(
                    qualified_name=qualified_name,
                    source_rule=source_rule,
                    sink_rule=sink_rule,
                    include_sanitised=include_sanitised,
                ),
        ),
        Tool(
            name="dump_dataflow",
            description=(
                "Dump variables and dataflow edges for a function "
                "(diagnostic — no inter-procedural propagation)."
            ),
            params={
                "type": "object",
                "properties": {"qualified_name": {"type": "string"}},
                "required": ["qualified_name"],
            },
            handler=lambda qualified_name: ct.dump_dataflow(
                qualified_name=qualified_name
            ),
        ),
        Tool(
            name="find_pp_chains",
            description=(
                "Find prototype pollution gadget chains: PP write nodes that "
                "reach dangerous sink nodes via the call graph."
            ),
            params={
                "type": "object",
                "properties": {
                    "max_depth": {"type": "integer"},
                },
            },
            handler=lambda max_depth=8: ct.find_pp_chains_tool(max_depth=max_depth),
        ),
        Tool(
            name="js_export_findings",
            description=(
                "Export the last js_analyzer report. format must be 'sarif' or "
                "'markdown'. out_path must be inside the sandbox. Run "
                "/js_analyzer-report first to populate findings."
            ),
            params={
                "type": "object",
                "properties": {
                    "format":   {"type": "string", "enum": ["sarif", "markdown"]},
                    "out_path": {"type": "string"},
                },
                "required": ["format", "out_path"],
            },
            handler=lambda format, out_path: _export_findings(
                kernel, format, out_path
            ),
            requires=["path_access"],
        ),
        Tool(
            name="js_examine_chain",
            description=(
                "Get full details for a specific chain: source node, sink node, "
                "call path, and source-code snippet for every function in the path. "
                "Call before submit_finding."
            ),
            params={
                "type": "object",
                "properties": {
                    "chain_id": {"type": "integer"},
                },
                "required": ["chain_id"],
            },
            handler=lambda chain_id: _tool_examine_chain(kernel, chain_id),
        ),
        Tool(
            name="js_get_snippet",
            description=(
                "Return source code for any function by qualified name "
                "(e.g. 'file.js::Foo.bar'). Use for functions not in a chain path."
            ),
            params={
                "type": "object",
                "properties": {"qname": {"type": "string"}},
                "required": ["qname"],
            },
            handler=lambda qname: _tool_get_snippet(kernel, qname),
        ),
        Tool(
            name="js_submit_finding",
            description=(
                "Record your verdict for a chain. Call exactly once per chain "
                "after examining evidence."
            ),
            params={
                "type": "object",
                "properties": {
                    "chain_id": {"type": "integer"},
                    "verdict":  {"type": "string", "enum": ["true_positive", "false_positive"]},
                    "severity": {"type": "string", "enum": ["high", "medium", "low", "n/a"]},
                    "vuln_class": {"type": "string"},
                    "proof":    {"type": "string"},
                },
                "required": ["chain_id", "verdict", "proof"],
            },
            handler=lambda chain_id, verdict, proof, severity="n/a", vuln_class="":
                _tool_submit_finding(kernel, chain_id, verdict, proof, severity, vuln_class),
        ),
        Tool(
            name="js_generate_report",
            description=(
                "Build the final Markdown security report from all submitted findings. "
                "Call ONLY after every chain has been reviewed with submit_finding."
            ),
            params={"type": "object", "properties": {}},
            handler=lambda: _tool_generate_report(kernel),
        ),
        Tool(
            name="js_update_hypothesis",
            description=(
                "Record or update your working hypothesis for a chain. "
                "Persists across loop iterations and restarts."
            ),
            params={
                "type": "object",
                "properties": {
                    "chain_id":    {"type": "integer"},
                    "status":      {"type": "string",
                                    "enum": ["open", "dead_end", "confirmed", "needs_more_data"]},
                    "note":        {"type": "string"},
                    "confidence":  {"type": "number"},
                    "tested_path": {"type": "string"},
                },
                "required": ["chain_id"],
            },
            handler=lambda chain_id, status="open", note="", confidence=0.5, tested_path="":
                _tool_update_hypothesis(kernel, chain_id, status, note, confidence, tested_path),
        ),
        Tool(
            name="preprocess_js",
            description=(
                "Deobfuscate and unminify a JS file that has no source map. "
                "Runs webcrack (bundle deobfuscation) then prettier "
                "(formatting). Falls back to js-beautify if prettier "
                "unavailable. Passthrough for already-readable files. "
                "Run before js_analyzer indexing when no source map was "
                "found."
            ),
            params={
                "type": "object",
                "properties": {
                    "js_path": {
                        "type": "string",
                        "description": "Local path to the JS file to preprocess.",
                    },
                    "output_dir": {
                        "type": "string",
                        "description": (
                            "Directory to write the preprocessed "
                            ".pretty.js file."
                        ),
                    },
                },
                "required": ["js_path", "output_dir"],
            },
            handler=lambda js_path, output_dir: json.dumps(
                preprocess_js(js_path, output_dir)
            ),
            requires=["path_access"],
        ),
        Tool(
            name="extract_source_map",
            description=(
                "Fetch and extract a JavaScript source map for a given JS "
                "file. Checks //# sourceMappingURL comment, SourceMap HTTP "
                "header, and sibling .map URL. Writes reconstructed original "
                "sources to output_dir. Run before js_analyzer indexing when "
                "source maps are available."
            ),
            params={
                "type": "object",
                "properties": {
                    "js_path": {
                        "type": "string",
                        "description": "Local path to the downloaded JS file.",
                    },
                    "base_url": {
                        "type": "string",
                        "description": (
                            "Original server URL of the JS file "
                            "(for resolving relative map URLs)."
                        ),
                    },
                    "output_dir": {
                        "type": "string",
                        "description": (
                            "Directory to write reconstructed source files "
                            "into."
                        ),
                    },
                },
                "required": ["js_path", "base_url", "output_dir"],
            },
            handler=lambda js_path, base_url, output_dir: json.dumps(
                extract_source_map(js_path, base_url, output_dir)
            ),
            requires=["network_access", "path_access"],
        ),
        Tool(
            name="js_get_hypothesis",
            description=(
                "Return your current hypothesis for a chain. Call at the START "
                "of examining any chain to skip dead ends from prior runs."
            ),
            params={
                "type": "object",
                "properties": {"chain_id": {"type": "integer"}},
                "required": ["chain_id"],
            },
            handler=lambda chain_id: _tool_get_hypothesis(kernel, chain_id),
        ),
    ]


def _index_target_payload(
    kernel: Any, target: Path, cfg: JsAnalyzerConfig,
    *, force: bool = False,
) -> dict:
    """Index a JS target; return structured payload (dict).

    Single source of truth for both the slash legacy string and the
    js_index_target tool. On error returns {"error": str, ...}.
    """
    from modules.js_analyzer import callgraph_tools as ct
    from modules.js_analyzer.ast_bridge import ASTExtractor
    from modules.js_analyzer.framework_detect import detect_frameworks
    cg = kernel.services.get("js_analyzer_callgraph")
    if cg is None:
        return {
            "error": "js_analyzer: callgraph service missing",
            "target": str(target),
        }

    _emit_progress(kernel, "js_analyzer.scan", f"target={target}")
    all_files = _walk_js_files(target, cfg.exclude_dirs)
    if not all_files:
        return {
            "error": f"js_analyzer: no .js files under {target}",
            "target": str(target),
        }

    files = [
        f for f in all_files
        if not cg.is_file_unchanged(f["rel"], Path(f["abs"]), force=force)
    ]
    skipped = len(all_files) - len(files)

    _emit_progress(
        kernel, "js_analyzer.framework_detect", f"{len(all_files)} files"
    )
    pkg_json = target / "package.json"
    frameworks = detect_frameworks(
        file_list=[f["abs"] for f in all_files],
        pkg_json_path=pkg_json if pkg_json.is_file() else None,
    )

    excludes = set(cfg.exclude_dirs)
    template_files: dict[str, str] = {}
    for p in target.rglob("*"):
        if not p.is_file():
            continue
        if any(part in excludes for part in p.parts):
            continue
        if p.suffix.lower() not in (".vue", ".html", ".htm"):
            continue
        try:
            rel = str(p.relative_to(target))
            template_files[rel] = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            pass

    fw_list = sorted(frameworks - {"node"})

    if not files and not template_files:
        ct.set_callgraph(cg, base_paths=[target])
        _emit_progress(kernel, "js_analyzer.done", str(target))
        return {
            "target": str(target),
            "nodes": cg.node_count(),
            "edges": cg.edge_count(),
            "tags": cg.tag_count(),
            "frameworks": fw_list,
            "itp": {"arg_edges": 0, "flows": 0},
            "cached_unchanged": skipped,
            "files_total": len(all_files),
        }

    extractor = ASTExtractor(deobfuscate=cfg.deobfuscate)
    extractor.set_frameworks(frameworks)
    if not extractor.ready:
        _emit_progress(kernel, "js_analyzer.done", "extractor unavailable")
        return {
            "error": (
                f"js_analyzer: AST extractor unavailable ({extractor.reason})"
            ),
            "target": str(target),
            "frameworks": fw_list,
        }

    _emit_progress(
        kernel, "js_analyzer.parsing", f"{len(files)} files to parse"
    )
    results = extractor.extract(files) if files else {}
    cg.index_batch(
        results,
        root_dir=target,
        template_files=template_files or None,
    )

    for f in files:
        cg.record_file_hash(f["rel"], Path(f["abs"]))

    _emit_progress(kernel, "js_analyzer.taint_analysis", "interprocedural")
    arg_edges, itp_flows = _run_interprocedural_taint(cg)
    _emit_progress(
        kernel, "js_analyzer.itp", f"{arg_edges} edges, {itp_flows} flows"
    )

    ct.set_callgraph(cg, base_paths=[target])

    _emit_progress(kernel, "js_analyzer.done", str(target))
    return {
        "target": str(target),
        "nodes": cg.node_count(),
        "edges": cg.edge_count(),
        "tags": cg.tag_count(),
        "frameworks": fw_list,
        "itp": {"arg_edges": arg_edges, "flows": itp_flows},
        "cached_unchanged": skipped,
        "files_total": len(all_files),
    }


def _format_index_summary(payload: dict) -> str:
    """Render legacy /js_analyzer string from an index payload dict."""
    if "error" in payload:
        if "frameworks" in payload:
            fw_str = ", ".join(payload["frameworks"]) or "none detected"
            return f"{payload['error']}  |  frameworks: {fw_str}"
        return payload["error"]
    fw_str = ", ".join(payload["frameworks"]) or "none detected"
    itp = payload.get("itp", {"arg_edges": 0, "flows": 0})
    return (
        f"js_analyzer indexed {payload['target']}: "
        f"{payload['nodes']} nodes, {payload['edges']} edges, "
        f"{payload['tags']} tags  |  frameworks: {fw_str}  |  "
        f"itp: {itp['arg_edges']} arg→param edges, "
        f"{itp['flows']} cross-fn flows  |  "
        f"cached: {payload['cached_unchanged']}/"
        f"{payload['files_total']} files unchanged"
    )


def _index_target(
    kernel: Any, target: Path, cfg: JsAnalyzerConfig,
    *, force: bool = False,
) -> str:
    return _format_index_summary(
        _index_target_payload(kernel, target, cfg, force=force)
    )


def _run_interprocedural_taint(cg: Any) -> tuple[int, int]:
    """Post-index pass: build arg→param edges, solve cross-function taint.

    Both callees are idempotent. Failures are logged and demoted to (0, 0)
    so an indexing run never aborts on solver issues.
    """
    from modules.js_analyzer.interprocedural_taint import (
        build_arg_to_param_edges,
        solve_interprocedural_taint,
    )
    try:
        arg_edges = build_arg_to_param_edges(cg.conn)
    except Exception:
        _logger.warning("js_analyzer.itp_arg_edges_failed", exc_info=True)
        return 0, 0
    try:
        flows = solve_interprocedural_taint(cg.conn)
    except Exception:
        _logger.warning("js_analyzer.itp_solver_failed", exc_info=True)
        return arg_edges, 0
    return arg_edges, len(flows)


async def _slash_js_analyzer(
    args: str, kernel: Any, cfg: JsAnalyzerConfig,
) -> str:
    """Slash wrapper. Dispatches through the js_index_target tool — the
    tool is the single source of truth for the indexing payload."""
    from modules.js_analyzer import callgraph_tools as ct
    cg = kernel.services.get("js_analyzer_callgraph")
    if cg is not None:
        ct.set_callgraph(cg, base_paths=kernel.sandbox.list_roots() or None)
    tokens = args.split() if args else []
    mock_extract = False
    positional: list[str] = []
    for tok in tokens:
        if tok == "--mock-extract":
            mock_extract = True
            continue
        positional.append(tok)
    if not positional:
        return "usage: /js_analyzer <target_folder> [--mock-extract]"
    target = Path(positional[0]).expanduser().resolve()
    if not kernel.sandbox.is_allowed(str(target)):
        return f"js_analyzer: path outside sandbox roots: {target}"
    if not target.exists() or not target.is_dir():
        return f"js_analyzer: not a directory: {target}"

    payload_json = await kernel.tools.dispatch(
        "js_index_target", {"target_folder": str(target)},
    )
    try:
        payload = _json.loads(payload_json) if isinstance(
            payload_json, str
        ) else payload_json
    except (TypeError, ValueError):
        return str(payload_json)
    out = _format_index_summary(payload)

    if mock_extract:
        tool = kernel.tools.get("mock_extract")
        if tool is None:
            out += (
                "\n\n(--mock-extract requested but mock_backend module "
                "is not registered)"
            )
        else:
            try:
                extract_out = tool.handler(target_dir=str(target))
            except Exception as exc:
                extract_out = f"[mock_extract] {exc}"
            out += f"\n\n--- mock_extract ---\n{extract_out}"
    return out


async def _slash_js_analyzer_report(
    args: str, kernel: Any, cfg: JsAnalyzerConfig
) -> str:
    from modules.js_analyzer import callgraph_tools as ct
    cg = kernel.services.get("js_analyzer_callgraph")
    if cg is not None:
        ct.set_callgraph(cg, base_paths=kernel.sandbox.list_roots() or None)
    if cg is None:
        return "js_analyzer: callgraph service missing"
    if not cfg.target:
        return "js_analyzer: no target indexed — run /js_analyzer <folder> first"

    from modules.js_analyzer.reporter import (
        extract_findings,
        handoff_to_claude_async,
    )

    findings = extract_findings(
        gemini_reply="",
        target_folder=cfg.target,
        callgraph=cg,
        severity=cfg.severity,
    )
    if findings is None:
        return "js_analyzer: no source→sink chains found"

    state = kernel.services.get("js_analyzer_state")
    if state is not None:
        state.last_findings = findings

    try:
        report = await handoff_to_claude_async(findings, kernel)
    except Exception as e:
        return f"js_analyzer: analysis failed: {e}"

    state = kernel.services.get("js_analyzer_state")
    if state is not None:
        consult_part = ""
        if getattr(state, "last_consults_used", 0):
            consult_part = (
                f" · consults: {state.last_consults_used} "
                f"(${state.last_consult_cost_usd:.4f})"
            )
        report += (
            f"\n\n---\n"
            f"*audit: ${state.last_audit_cost_usd:.4f} · "
            f"{state.last_audit_tokens:,} tokens{consult_part}*"
        )

    return report


def _export_findings(kernel: Any, fmt: str, out_path: str) -> str:
    state = kernel.services.get("js_analyzer_state")
    if state is None or state.last_findings is None or state.last_report is None:
        return "js_analyzer: no findings cached — run /js_analyzer-report first"

    out = Path(out_path).expanduser().resolve()
    if not kernel.sandbox.is_allowed(str(out.parent)):
        return f"js_analyzer: output path outside sandbox: {out}"

    try:
        if fmt == "sarif":
            from modules.js_analyzer.sarif_writer import build_sarif
            doc = build_sarif(state.last_findings, state.last_report)
            out.write_text(json.dumps(doc, indent=2), encoding="utf-8")
            return f"js_analyzer: sarif written to {out}"
        if fmt == "markdown":
            out.write_text(state.last_report, encoding="utf-8")
            return f"js_analyzer: markdown written to {out}"
        return f"js_analyzer: unsupported format: {fmt}"
    except Exception as e:
        return f"js_analyzer: export failed: {e}"


def _register(kernel: Any, config: Any) -> RegisteredModule:
    cfg = config if isinstance(config, JsAnalyzerConfig) else JsAnalyzerConfig()

    from modules.js_analyzer import callgraph_tools as ct
    from modules.js_analyzer.callgraph import CallGraph

    cg = CallGraph(Path(cfg.db_path))
    ct.set_callgraph(cg, base_paths=kernel.sandbox.list_roots() or None)
    kernel.services.register("js_analyzer_callgraph", cg)

    state = JsAnalyzerState()
    state.hypotheses = _load_hypotheses_kv(kernel)
    kernel.services.register("js_analyzer_state", state)

    from modules.js_analyzer.tools_extra import make_extra_tools
    tools = _make_tools(kernel, cfg) + make_extra_tools(kernel, cfg)
    for t in tools:
        kernel.tools.register(t)

    kernel.defer_slash_register(SlashCommand(
        name="js_analyzer",
        description=(
            "index a folder of JS into the call graph; pass "
            "--mock-extract to also run mock_extract on the same dir"
        ),
        handler=lambda a, k: _slash_js_analyzer(a, k, cfg),
    ))
    kernel.defer_slash_register(SlashCommand(
        name="js_analyzer-report",
        description="build report from indexed call graph (export via tool)",
        handler=lambda a, k: _slash_js_analyzer_report(a, k, cfg),
    ))

    return RegisteredModule(spec=MODULE, tools=tools, config=cfg)


MODULE = ModuleSpec(
    name="js_analyzer",
    version="0.1.0",
    requires_kernel=">=0.1.0",
    depends_on=[],
    config_schema=JsAnalyzerConfig,
    register_fn=_register,
)
