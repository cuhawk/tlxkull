"""Tool name allowlist for the MCP transport (Phase 8D — final v1).

NOT exposed:
  - js_consult_opus       — audit-loop-internal only
  - find_sinks/trace_to_sink/find_pp_chains  — collapsed
  - read_file/write_file/list_dir/shell_exec — Claude Code natives
  - pw_*                  — replaced by Claude Code's playwright-mcp
  - web_search/web_fetch  — Claude Code natives
  - mock_authz/mock_auth/mock_probe/mock_record/mock_observe
                          — re-expose later if needed
  - session_kv_set        — read-only KV access from MCP
"""
from __future__ import annotations

# 16 tools total
TOOL_ALLOWLIST: frozenset[str] = frozenset({
    # js_analyzer (8 tools)
    "js_index_target",
    "js_get_chains",
    "js_examine_chain",
    "js_get_snippet",
    "js_submit_finding",
    "js_export_findings",
    "js_run_audit",
    "js_audit_status",
    # mock_backend (6 tools)
    "mock_extract",
    "mock_start",
    "mock_stop",
    "mock_confirm",
    "mock_run",
    "mock_export",
    # rag / kv (2 tools)
    "docs_query",
    "session_kv_get",
})

assert len(TOOL_ALLOWLIST) == 16, "Phase 8D allowlist must be exactly 16 tools"
