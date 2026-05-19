"""Agent-facing call graph tools (Task 6).

Six tools surfaced to the Gemini agent:
    find_sinks, list_entry_points, trace_to_sink,
    get_callers, get_callees, get_function_source

Universal contract:
    * Truncate at MAX_RESULTS, set truncated=True when cut.
    * Return JSON-serializable dicts only.
    * On error return {"error": "<message>"} — never raise.
    * qname format: "<file>::<parent>.<name>" or "<file>::<name>".
"""

import fnmatch
import json
from pathlib import Path

from modules.js_analyzer.js_analyzer_config import ALLOWED_ROOTS
from modules.js_analyzer.pathfind import find_paths

MAX_RESULTS = 50


_CG = None
_BASE_PATHS: list[Path] = []


def set_callgraph(cg, base_paths=None) -> None:
    """Wire the CallGraph + roots used to resolve <file> rel paths."""
    global _CG, _BASE_PATHS
    _CG = cg
    if base_paths is None:
        _BASE_PATHS = list(ALLOWED_ROOTS)
    else:
        _BASE_PATHS = [Path(p) for p in base_paths]


def _truncate(items, limit: int = MAX_RESULTS):
    return list(items[:limit]), len(items) > limit


def _glob_ok(file: str, pattern: str | None) -> bool:
    if not pattern:
        return True
    if fnmatch.fnmatch(file, pattern):
        return True
    # Permissive fallbacks for patterns the agent often emits that don't
    # line up with our flat rel paths:
    #   '**/x.js'                → match basename against 'x.js'
    #   '~/abs/path/x.js'        → match basename against 'x.js'
    # A pattern like 'src/*.js' (relative directory prefix) is NOT
    # permissively expanded — that intent is "only files under src/".
    if pattern.startswith("**/") or pattern.startswith("~/") or pattern.startswith("/"):
        base     = file.rsplit("/", 1)[-1]
        pat_base = pattern.rsplit("/", 1)[-1]
        return fnmatch.fnmatch(base, pat_base)
    return False


def _require_cg():
    if _CG is None:
        return {"error": "Call graph not initialised."}
    return None


def _resolve_file(rel: str) -> Path | None:
    for root in _BASE_PATHS:
        root_r = Path(root).resolve()
        cand = (root_r / rel).resolve()
        # Containment check: cand must live under root_r
        try:
            cand.relative_to(root_r)
        except ValueError:
            continue
        if cand.exists():
            return cand
    return None


# ── tools ────────────────────────────────────────────────────────────────


def find_sinks(severity: str | None = None,
               file_glob: str | None = None) -> dict:
    # Tracked sink categories include DOM XSS sinks (innerHTML_assign,
    # outerHTML_assign, document_write, eval_call, new_Function, etc.),
    # navigation/open-redirect sinks (location_href_assign, location_assign_call),
    # and SSRF / outbound HTTP sinks (fetch_call, xhr_open_call, axios_call).
    err = _require_cg()
    if err:
        return err
    try:
        sql = (
            "SELECT n.qualified_name, n.file, t.line, t.taxonomy_id, t.severity "
            "FROM nodes n JOIN node_tags t ON n.id = t.node_id "
            "WHERE t.kind='sink'"
        )
        params: list = []
        if severity:
            sql += " AND t.severity=?"
            params.append(severity)
        sql += " ORDER BY n.file, t.line, t.taxonomy_id"
        rows = _CG.conn.execute(sql, params).fetchall()
        rows = [r for r in rows if _glob_ok(r[1], file_glob)]
        items, truncated = _truncate(rows)
        return {
            "sinks": [
                {"qname": r[0], "file": r[1], "line": r[2],
                 "taxonomy_id": r[3], "severity": r[4]}
                for r in items
            ],
            "truncated": truncated,
        }
    except Exception as e:
        return {"error": str(e)}


def list_entry_points(file_glob: str | None = None) -> dict:
    err = _require_cg()
    if err:
        return err
    try:
        rows = _CG.conn.execute(
            "SELECT n.qualified_name, n.file, t.line, t.taxonomy_id "
            "FROM nodes n JOIN node_tags t ON n.id = t.node_id "
            "WHERE t.kind='source' "
            "ORDER BY n.file, t.line, t.taxonomy_id"
        ).fetchall()
        rows = [r for r in rows if _glob_ok(r[1], file_glob)]
        items, truncated = _truncate(rows)
        return {
            "sources": [
                {"qname": r[0], "file": r[1], "line": r[2], "taxonomy_id": r[3]}
                for r in items
            ],
            "truncated": truncated,
        }
    except Exception as e:
        return {"error": str(e)}


def trace_to_sink(
    from_qname: str,
    max_depth: int = 8,
    severity: str | None = None,
    exclude_sanitised: bool = False,
) -> dict:
    err = _require_cg()
    if err:
        return err
    try:
        if not _CG.find_node(from_qname):
            return {"error": f"Unknown qname: {from_qname}"}
        paths = find_paths(
            _CG.conn, from_qname, to_kind="sink",
            severity=severity, max_depth=max_depth,
            max_paths=MAX_RESULTS + 1,
            exclude_sanitised=exclude_sanitised,
        )
        items, truncated = _truncate(paths)
        return {
            "paths": [
                {
                    "nodes":              p.qualified_names,
                    "terminal_tag":       p.tag,
                    "depth":              p.depth,
                    "sanitisers_in_path": p.sanitisers_in_path,
                    "edge_kinds":         list(p.edge_kinds or []),
                }
                for p in items
            ],
            "truncated": truncated,
        }
    except Exception as e:
        return {"error": str(e)}


def get_callers(qname: str) -> dict:
    err = _require_cg()
    if err:
        return err
    try:
        node = _CG.find_node(qname)
        if not node:
            return {"error": f"Unknown qname: {qname}"}
        rows = _CG.conn.execute(
            "SELECT n.qualified_name, n.file, e.line, e.resolved_kind "
            "FROM edges e JOIN nodes n ON n.id = e.caller_id "
            "WHERE e.callee_id=? ORDER BY n.qualified_name, e.line",
            (node["id"],),
        ).fetchall()
        return {
            "callers": [
                {"qname": r[0], "file": r[1], "line": r[2],
                 "resolved_kind": r[3]}
                for r in rows
            ],
        }
    except Exception as e:
        return {"error": str(e)}


def get_callees(qname: str) -> dict:
    err = _require_cg()
    if err:
        return err
    try:
        node = _CG.find_node(qname)
        if not node:
            return {"error": f"Unknown qname: {qname}"}
        rows = _CG.conn.execute(
            "SELECT e.callee_raw, n.qualified_name, e.line, e.resolved_kind "
            "FROM edges e LEFT JOIN nodes n ON n.id = e.callee_id "
            "WHERE e.caller_id=? ORDER BY e.line",
            (node["id"],),
        ).fetchall()
        return {
            "callees": [
                {"qname_or_raw": r[1] if r[1] else r[0],
                 "line": r[2],
                 "resolved_kind": r[3]}
                for r in rows
            ],
        }
    except Exception as e:
        return {"error": str(e)}


def get_function_source(qname: str) -> dict:
    err = _require_cg()
    if err:
        return err
    try:
        node = _CG.find_node(qname)
        if not node:
            return {"error": f"Unknown qname: {qname}"}
        rel = node["file"]
        start, end = node["start_line"], node["end_line"]
        original_line = node.get("original_line")
        original_file = node.get("original_file")
        if not start or not end or end < start:
            return {"error": f"Invalid line range for {qname}"}
        path = _resolve_file(rel)
        if path is None:
            return {"error": f"File not found in allowed roots: {rel}"}
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        source = "\n".join(lines[start - 1:end])
        result = {
            "file": rel,
            "start_line": start,
            "end_line": end,
            "source": source,
        }
        if original_line:
            result["original_line"] = original_line
            result["original_file"] = original_file or rel
        return result
    except Exception as e:
        return {"error": str(e)}


def list_extracted_urls(
    file_glob: str | None = None,
    url_type: str | None = None,
    method: str | None = None,
) -> dict:
    err = _require_cg()
    if err:
        return err
    try:
        sql = (
            "SELECT file, url_template, type, method, "
            "       query_params, body_params, line, in_function "
            "FROM url_refs"
        )
        params: list = []
        conditions = []
        if url_type:
            conditions.append("type=?")
            params.append(url_type)
        if method:
            conditions.append("method=?")
            params.append(method.upper())
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY file, line"

        rows = _CG.conn.execute(sql, params).fetchall()
        if file_glob:
            rows = [r for r in rows if _glob_ok(r[0], file_glob)]

        items, truncated = _truncate(rows)
        return {
            "urls": [
                {
                    "file":         r[0],
                    "url":          r[1],
                    "type":         r[2],
                    "method":       r[3],
                    "query_params": json.loads(r[4]) if r[4] else [],
                    "body_params":  json.loads(r[5]) if r[5] else [],
                    "line":         r[6],
                    "in_function":  r[7],
                }
                for r in items
            ],
            "truncated": truncated,
        }
    except Exception as e:
        return {"error": str(e)}


def find_intra_function_flows(
    qualified_name: str | None = None,
    source_rule: str | None = None,
    sink_rule: str | None = None,
    include_sanitised: bool = True,
) -> dict:
    err = _require_cg()
    if err:
        return err
    try:
        sql = (
            "SELECT n.qualified_name, n.file, "
            "       f.source_rule, f.source_line, f.sink_rule, f.sink_line, "
            "       f.via_vars, f.sanitised_by "
            "FROM node_taint_flows f JOIN nodes n ON n.id = f.node_id"
        )
        params: list = []
        conditions = []
        if qualified_name:
            conditions.append("n.qualified_name=?")
            params.append(qualified_name)
        if source_rule:
            conditions.append("f.source_rule=?")
            params.append(source_rule)
        if sink_rule:
            conditions.append("f.sink_rule=?")
            params.append(sink_rule)
        if not include_sanitised:
            conditions.append("f.sanitised_by IS NULL")
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY n.file, f.source_line"

        rows = _CG.conn.execute(sql, params).fetchall()
        items, truncated = _truncate(rows)
        return {
            "flows": [
                {
                    "qname": r[0],
                    "file": r[1],
                    "source_rule": r[2],
                    "source_line": r[3],
                    "sink_rule": r[4],
                    "sink_line": r[5],
                    "via_vars": r[6].split(",") if r[6] else [],
                    "sanitised_by": r[7],
                }
                for r in items
            ],
            "truncated": truncated,
        }
    except Exception as e:
        return {"error": str(e)}


def dump_dataflow(qualified_name: str) -> dict:
    """Dump variables and dataflow edges for a function.

    Diagnostic only — does NOT perform inter-procedural taint propagation.
    See TODO.md for the planned solver.
    """
    err = _require_cg()
    if err:
        return err
    try:
        node = _CG.find_node(qualified_name)
        if not node:
            return {"error": f"Unknown qname: {qualified_name}"}
        node_id = node["id"]

        vars_rows = _CG.conn.execute(
            "SELECT id, name, first_line FROM variables "
            "WHERE node_id=? ORDER BY first_line, name",
            (node_id,),
        ).fetchall()

        edges_rows = _CG.conn.execute(
            "SELECT from_var, to_var, edge_kind, line, sanitiser "
            "FROM dataflow_edges "
            "WHERE to_var IN (SELECT id FROM variables WHERE node_id=?) "
            "ORDER BY line, edge_kind",
            (node_id,),
        ).fetchall()

        return {
            "qname": qualified_name,
            "variables": [
                {"id": r[0], "name": r[1], "first_line": r[2]}
                for r in vars_rows
            ],
            "dataflow": [
                {
                    "from_var":  r[0],
                    "to_var":    r[1],
                    "edge_kind": r[2],
                    "line":      r[3],
                    "sanitiser": r[4],
                }
                for r in edges_rows
            ],
        }
    except Exception as e:
        return {"error": str(e)}


def find_interprocedural_flows(
    source_rule: str | None = None,
    sink_rule:   str | None = None,
    include_sanitised: bool = True,
) -> dict:
    """Query cross-function taint flows from interprocedural_taint_flows table.

    Filters: source_rule (taxonomy id), sink_rule (taxonomy id),
    include_sanitised (default True — set False to hide flows with
    a sanitiser in path). Returns source/sink qnames, rules, and
    the path of variable IDs. Truncates at MAX_RESULTS.
    """
    err = _require_cg()
    if err:
        return err
    try:
        sql = (
            "SELECT f.source_rule, f.sink_rule, f.via_var_ids, f.sanitised_by, "
            "       sn.qualified_name AS source_qname, "
            "       sk.qualified_name AS sink_qname "
            "FROM interprocedural_taint_flows f "
            "JOIN nodes sn ON sn.id = f.source_node_id "
            "JOIN nodes sk ON sk.id = f.sink_node_id"
        )
        params: list = []
        conditions = []
        if source_rule:
            conditions.append("f.source_rule=?")
            params.append(source_rule)
        if sink_rule:
            conditions.append("f.sink_rule=?")
            params.append(sink_rule)
        if not include_sanitised:
            conditions.append("f.sanitised_by IS NULL")
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY f.source_rule, f.sink_rule"

        rows = _CG.conn.execute(sql, params).fetchall()
        items, truncated = _truncate(rows)
        return {
            "flows": [
                {
                    "source_rule":   r[0],
                    "sink_rule":     r[1],
                    "via_var_ids":   r[2],
                    "sanitised_by":  r[3],
                    "source_qname":  r[4],
                    "sink_qname":    r[5],
                }
                for r in items
            ],
            "truncated": truncated,
        }
    except Exception as e:
        if "no such table" in str(e).lower():
            return {"flows": [], "truncated": False,
                    "info": "interprocedural_taint_flows table not yet built — run index_codebase first"}
        return {"error": str(e)}


def find_pp_chains_tool(max_depth: int = 8) -> dict:
    """Find prototype pollution gadget chains.

    Returns PP write nodes → call graph path → gadget sink nodes.
    A chain means: if an attacker can control __proto__ or a merge call's input,
    they can reach the gadget sink (innerHTML, eval, etc.) without direct taint flow.

    Args:
        max_depth: max call graph hops between PP write and gadget sink (default 8)

    Returns dict with:
        chains: list of chain dicts (id, source, sink, path, depth, score, cross_file)
        total: int
        truncated: bool
        message: human-readable summary
    """
    err = _require_cg()
    if err:
        return err
    try:
        from modules.js_analyzer.pp_chains import find_pp_chains
        chains = find_pp_chains(_CG.conn, max_depth=max_depth)
        items, trunc = _truncate(chains)
        suffix = ""
        if trunc:
            suffix += " Results truncated to 50."
        if not chains:
            suffix += (
                " No chains found — either no PP write sources tagged, no reachable "
                "gadget sinks, or no call graph path between them."
            )
        msg = f"Found {len(chains)} PP gadget chain(s)." + suffix
        return {"chains": items, "total": len(chains),
                "truncated": trunc, "message": msg}
    except Exception as exc:
        return {"error": str(exc)}


CALLGRAPH_HANDLERS = {
    "find_sinks":          find_sinks,
    "list_entry_points":   list_entry_points,
    "trace_to_sink":       trace_to_sink,
    "get_callers":         get_callers,
    "get_callees":         get_callees,
    "get_function_source": get_function_source,
    "list_extracted_urls": list_extracted_urls,
    "find_intra_function_flows": find_intra_function_flows,
    "find_interprocedural_flows": find_interprocedural_flows,
    "dump_dataflow":       dump_dataflow,
    "find_pp_chains":      find_pp_chains_tool,
}


def callgraph_tool_declarations():
    """Gemini FunctionDeclarations for the six call graph tools."""
    from google.genai import types

    return [
        types.FunctionDeclaration(
            name="find_sinks",
            description=(
                "List all sink-tagged nodes in the call graph. "
                "Filter by severity ('high'/'medium'/'low') and/or file_glob "
                "(fnmatch pattern over rel path). Truncates at 50."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "severity":  types.Schema(type="STRING"),
                    "file_glob": types.Schema(type="STRING"),
                },
            ),
        ),
        types.FunctionDeclaration(
            name="list_entry_points",
            description=(
                "List all source-tagged nodes (taint entry points). "
                "Optional file_glob restricts by rel path. Truncates at 50."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "file_glob": types.Schema(type="STRING"),
                },
            ),
        ),
        types.FunctionDeclaration(
            name="trace_to_sink",
            description=(
                "BFS call paths from from_qname to any sink-tagged node. "
                "Skips dynamic/unresolved edges. Returns shortest paths first. "
                "Each path includes sanitisers_in_path listing any sanitiser "
                "nodes traversed. Truncates at 50."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "from_qname": types.Schema(type="STRING"),
                    "max_depth":  types.Schema(type="INTEGER"),
                    "severity":   types.Schema(type="STRING"),
                    "exclude_sanitised": types.Schema(
                        type="BOOLEAN",
                        description=(
                            "When true, drop paths that pass through a known "
                            "sanitiser. Use for a quick sweep to find only "
                            "unsanitised chains. Leave false (default) in "
                            "exploratory mode to see all chains, including "
                            "those with potentially misconfigured sanitisers."
                        ),
                    ),
                },
                required=["from_qname"],
            ),
        ),
        types.FunctionDeclaration(
            name="get_callers",
            description="Direct callers of qname (in-edges).",
            parameters=types.Schema(
                type="OBJECT",
                properties={"qname": types.Schema(type="STRING")},
                required=["qname"],
            ),
        ),
        types.FunctionDeclaration(
            name="get_callees",
            description=(
                "Direct callees of qname (out-edges). qname_or_raw shows "
                "raw call expression when callee is unresolved or dynamic."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={"qname": types.Schema(type="STRING")},
                required=["qname"],
            ),
        ),
        types.FunctionDeclaration(
            name="get_function_source",
            description=(
                "Source text of the function/method identified by qname, "
                "including its full body line range."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={"qname": types.Schema(type="STRING")},
                required=["qname"],
            ),
        ),
        types.FunctionDeclaration(
            name="find_intra_function_flows",
            description=(
                "Direct intra-function source→sink flows with variable-level tracking. "
                "Highest confidence findings — much stronger than BFS reachability. "
                "Filter by qualified_name (single function), source_rule, sink_rule, "
                "or include_sanitised (default True). Truncates at 50."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "qualified_name":    types.Schema(type="STRING"),
                    "source_rule":       types.Schema(type="STRING"),
                    "sink_rule":         types.Schema(type="STRING"),
                    "include_sanitised": types.Schema(type="BOOLEAN"),
                },
            ),
        ),
        types.FunctionDeclaration(
            name="list_extracted_urls",
            description=(
                "List URLs extracted from the codebase by the AST extractor. "
                "Includes fetch(), XHR, jQuery calls, and location assignments. "
                "URL templates use EXPR placeholders for non-static parts. "
                "Filter by file_glob (fnmatch), url_type (fetch/xhr/$.ajax/etc.), "
                "or method (GET/POST/etc.). Truncates at 50."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "file_glob": types.Schema(type="STRING"),
                    "url_type":  types.Schema(type="STRING"),
                    "method":    types.Schema(type="STRING"),
                },
            ),
        ),
        types.FunctionDeclaration(
            name="find_interprocedural_flows",
            description=(
                "Query cross-function taint flows produced by the inter-procedural "
                "solver. Returns source qname, sink qname, source/sink taxonomy IDs, "
                "and variable path. Requires index_codebase to have run first. "
                "Filter by source_rule or sink_rule (taxonomy ID strings). "
                "Set include_sanitised=False to hide flows with a sanitiser in path."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "source_rule":       types.Schema(type="STRING"),
                    "sink_rule":         types.Schema(type="STRING"),
                    "include_sanitised": types.Schema(type="BOOLEAN"),
                },
            ),
        ),
        types.FunctionDeclaration(
            name="find_pp_chains",
            description=(
                "Find prototype pollution gadget chains — PP write nodes "
                "(assignments to __proto__, constructor.prototype, or deep-merge "
                "helpers) that have a call graph path to dangerous sink nodes "
                "(innerHTML, eval, setTimeout string, etc.). Returns chains ranked "
                "by exploitability. Use this after index_codebase when the target "
                "uses lodash, jQuery, or any utility library with merge/extend/"
                "assign patterns."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "max_depth": types.Schema(
                        type="INTEGER",
                        description=(
                            "Maximum call graph hops to search between PP write "
                            "and gadget sink (default 8)."
                        ),
                    ),
                },
            ),
        ),
        types.FunctionDeclaration(
            name="dump_dataflow",
            description=(
                "Dump variables and dataflow edges for a function (Phase 6 "
                "schema diagnostic). Returns variable rows (parameters, "
                "locals, ':return') and edges (assign / return). Does NOT "
                "perform inter-procedural taint propagation — that is "
                "deferred follow-up work."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={"qualified_name": types.Schema(type="STRING")},
                required=["qualified_name"],
            ),
        ),
    ]
