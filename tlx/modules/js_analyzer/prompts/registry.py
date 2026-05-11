"""Prompt registry — assembly + lookup.

Combines:
  - scanner/prompt.md  : mandatory per-run user entry (read fresh each call)
  - prompts/**/*.md    : the migrated library
  - PromptRAG          : top-k retrieval keyed on the task

API:
  PromptRegistry(scanner_root, engine=None)
  .startup() → loads prompts, refreshes RAG, returns banner stats
  .assemble_system_prompt(task_query=None, extra_ids=None,
                          exclude_ids=None, top_k=3) → str
  .get_security_prompt(vuln_class) → str | None
  .list_available(kind=None) → list[dict]

Singleton helpers: set_registry(r) / get_registry()
"""

from pathlib import Path

from .loader import LoaderError, Prompt, load_prompts
from .rag import PromptRAG

USER_ENTRY_FILENAME = "prompt.md"
DUMP_FILENAME       = ".last_assembled_prompt.md"
PROMPTS_DIRNAME     = "prompts"


class PromptRegistry:

    def __init__(self, scanner_root: Path, engine=None):
        self.scanner_root = Path(scanner_root)
        self.user_entry   = self.scanner_root / USER_ENTRY_FILENAME
        self.prompts_dir  = self.scanner_root / PROMPTS_DIRNAME
        self.dump_path    = self.scanner_root / DUMP_FILENAME
        self.engine       = engine
        self.prompts: list[Prompt] = []
        self.by_id:    dict[str, Prompt] = {}
        self.rag: PromptRAG | None = None

    # ── lifecycle ───────────────────────────────────────────────────────

    def startup(self) -> dict:
        """Validate user entry, load library, build/refresh RAG.

        Raises LoaderError if scanner/prompt.md is missing.
        Returns banner stats dict.
        """
        if not self.user_entry.exists():
            raise LoaderError(
                f"missing mandatory user entry: {self.user_entry} "
                f"— create it before running the agent"
            )

        self.prompts = load_prompts(self.prompts_dir)
        self.by_id   = {p.id: p for p in self.prompts}

        self.rag = PromptRAG(self.engine, self.prompts_dir)
        rag_stats = self.rag.reindex(self.prompts) if self.rag.enabled else None

        return {
            "total":     len(self.prompts),
            "system":    sum(1 for p in self.prompts if p.kind == "system"),
            "security":  sum(1 for p in self.prompts if p.kind == "security"),
            "workflow":  sum(1 for p in self.prompts if p.kind == "workflow"),
            "rag":       rag_stats,
        }

    # ── lookup ──────────────────────────────────────────────────────────

    def list_available(self, kind: str | None = None) -> list[dict]:
        out = []
        for p in self.prompts:
            if kind and p.kind != kind:
                continue
            out.append({
                "id":             p.id,
                "kind":           p.kind,
                "title":          p.title,
                "tags":           list(p.tags),
                "always_include": p.always_include,
                "priority":       p.priority,
            })
        return out

    def get_security_prompt(self, vuln_class: str) -> str | None:
        p = self.by_id.get(vuln_class)
        if not p or p.kind != "security":
            return None
        return p.body

    def get_prompt(self, prompt_id: str) -> Prompt | None:
        return self.by_id.get(prompt_id)

    # ── assembly ────────────────────────────────────────────────────────

    def _read_user_entry(self) -> str:
        """Read scanner/prompt.md fresh on every call."""
        return self.user_entry.read_text(encoding="utf-8").strip()

    def assemble_system_prompt(
        self,
        task_query: str | None = None,
        extra_ids:  list[str] | None = None,
        exclude_ids: list[str] | None = None,
        top_k: int = 3,
        dump: bool = False,
    ) -> str:
        excluded = set(exclude_ids or [])
        sections: list[str] = []

        # 1. always_include prompts, priority desc, then id asc for stability
        always = sorted(
            (p for p in self.prompts
             if p.always_include and p.id not in excluded),
            key=lambda p: (-p.priority, p.id),
        )
        for p in always:
            sections.append(self._render(p))

        # 2. RAG retrieval — only ids not already included
        included_ids = {p.id for p in always}
        if task_query and self.rag and self.rag.enabled:
            for hit in self.rag.query(task_query, top_k=top_k):
                pid = hit.get("id")
                if not pid or pid in included_ids or pid in excluded:
                    continue
                rag_p = self.by_id.get(pid)
                if not rag_p:
                    continue
                sections.append(self._render(rag_p))
                included_ids.add(pid)

        # 3. Extras explicitly requested (e.g., a specific vuln class)
        for pid in (extra_ids or []):
            if pid in included_ids or pid in excluded:
                continue
            extra_p = self.by_id.get(pid)
            if not extra_p:
                continue
            sections.append(self._render(extra_p))
            included_ids.add(pid)

        # 4. User entry — last so it overrides earlier blocks
        user_block = self._read_user_entry()
        if user_block:
            sections.append(f"# User entry ({USER_ENTRY_FILENAME})\n\n{user_block}")

        assembled = "\n\n---\n\n".join(sections)

        if dump:
            try:
                self.dump_path.write_text(assembled, encoding="utf-8")
            except OSError:
                pass
        return assembled

    @staticmethod
    def _render(p: Prompt) -> str:
        return f"# [{p.kind}] {p.title} (id: {p.id})\n\n{p.body}"


# ── module-level singleton ──────────────────────────────────────────────

_REGISTRY: PromptRegistry | None = None


def set_registry(reg: PromptRegistry) -> None:
    global _REGISTRY
    _REGISTRY = reg


def get_registry() -> PromptRegistry | None:
    return _REGISTRY
