"""js_analyzer config constants.

Holds env-derived model/key constants and ALLOWED_ROOTS
used by callgraph_tools. ALLOWED_ROOTS is set at module
register time via callgraph_tools.set_callgraph(base_paths=…)
from kernel.sandbox roots. Empty default is intentional
(fail-closed if set_callgraph never runs).
"""
from __future__ import annotations

import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY    = os.environ.get("GOOGLE_API_KEY", "")
CLAUDE_MODEL      = "claude-sonnet-4-6"
CLAUDE_OPUS_MODEL = os.environ.get("CLAUDE_OPUS_MODEL", "claude-opus-4-7")

# callgraph_tools imports ALLOWED_ROOTS at module top. Real roots come
# from kernel.sandbox via ct.set_callgraph(base_paths=...) at register
# and slash-handler time; this empty default just satisfies the import.
ALLOWED_ROOTS: list = []

# js_consult_opus bounds — per-audit-run caps for the second-opinion tool
MAX_CONSULTS       = int(os.environ.get("JS_MAX_CONSULTS", "5"))
CONSULT_BUDGET_USD = float(os.environ.get("JS_CONSULT_BUDGET_USD", "1.50"))
