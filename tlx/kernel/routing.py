"""Per-message routing — task classifier + routing config + decision."""
from __future__ import annotations

import re
from dataclasses import dataclass

from pydantic import BaseModel

from kernel.schema import Message

SECURITY_KEYWORDS = frozenset({
    "vulnerability", "vuln", "exploit", "payload", "bypass",
    "injection", "xss", "sqli", "rce", "lfi", "ssrf", "idor",
    "deserialization", "overflow", "cve", "poc", "shellcode",
    "privesc", "escalation", "ssti", "xxe", "csrf",
})

JS_EXTENSIONS = frozenset({".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs"})

_LARGE_FILE_EXTENSIONS = frozenset({
    ".js", ".ts", ".jsx", ".tsx", ".mjs",
    ".html", ".htm", ".pdf", ".json",
})

_LARGE_FILE_PATH_RE = re.compile(
    r"(?:^|[\s\"'])"
    r"(?:/[\w.\-/]+|~/[\w.\-/]+|\.{1,2}/[\w.\-/]+)"
    r"(?:" + "|".join(re.escape(e) for e in _LARGE_FILE_EXTENSIONS) + r")",
    re.MULTILINE,
)


def _has_large_file_path(text: str) -> bool:
    """True if message contains a file path with a large-file extension."""
    return bool(_LARGE_FILE_PATH_RE.search(text))

SIMPLE_VERBS = frozenset({
    "format", "convert", "extract", "summarize", "list",
    "rename", "count", "parse", "sort", "filter", "translate",
})


class RoutingConfig(BaseModel):
    enabled: bool = False
    tiers: list[str] = [
        "gemini-2.5-flash",
        "claude-haiku-4-5",
        "claude-sonnet-4-6",
        "claude-opus-4-7",
    ]
    token_budgets: dict[str, int] = {
        "tier0": 8192,
        "tier1": 2048,
        "tier2": 8192,
        "tier3": 4096,
    }
    large_context_threshold: int = 50_000
    large_code_block_lines: int = 200
    security_keyword_min_tokens: int = 200
    max_escalations: int = 2


@dataclass
class RoutingDecision:
    tier: int
    model: str
    max_tokens: int
    reason: str
    escalated_from: int | None = None


class TaskClassifier:
    def __init__(self, config: RoutingConfig) -> None:
        self._cfg = config

    def classify(
        self,
        messages: list[Message],
        recent_tool_names: list[str] | None = None,
    ) -> RoutingDecision:
        cfg = self._cfg
        last_text = _last_user_text(messages)
        token_est = _estimate_tokens(messages)

        if token_est > cfg.large_context_threshold:
            return self._d(0, "large context", cfg)
        if _has_large_code_block(last_text, cfg.large_code_block_lines):
            return self._d(0, "large code block", cfg)
        if _has_large_file_path(last_text):
            return self._d(0, "large file path", cfg)
        if any(ext in last_text for ext in JS_EXTENSIONS):
            return self._d(0, "JS/TS file", cfg)
        if recent_tool_names and any(
            t in recent_tool_names
            for t in ("docs_query", "docs_ingest", "docs_ingest_dir")
        ):
            return self._d(2, "RAG synthesis", cfg)

        last_tokens = _estimate_tokens([messages[-1]]) if messages else 0
        words = set(last_text.lower().split())
        if words & SECURITY_KEYWORDS and last_tokens > cfg.security_keyword_min_tokens:
            return self._d(3, "security task", cfg)
        if last_tokens < 100 and words & SIMPLE_VERBS:
            return self._d(1, "simple task", cfg)
        return self._d(2, "default", cfg)

    def _d(self, tier: int, reason: str, cfg: RoutingConfig) -> RoutingDecision:
        model = cfg.tiers[tier] if tier < len(cfg.tiers) else cfg.tiers[-1]
        budget = cfg.token_budgets.get(f"tier{tier}", 4096)
        return RoutingDecision(tier=tier, model=model, max_tokens=budget, reason=reason)


def _last_user_text(messages: list[Message]) -> str:
    for m in reversed(messages):
        if m.role == "user":
            return m.content if isinstance(m.content, str) else ""
    return ""


def _estimate_tokens(messages: list[Message]) -> int:
    total = 0
    for m in messages:
        text = m.content if isinstance(m.content, str) else str(m.content)
        total += len(text) // 4
    return total


def _has_large_code_block(text: str, min_lines: int) -> bool:
    import re
    blocks = re.findall(r"```.*?```", text, re.DOTALL)
    return any(b.count("\n") >= min_lines for b in blocks)
