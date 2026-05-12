"""tlx kernel — engine-agnostic core."""
from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import structlog

from kernel.compaction import CompactionResult, Compactor
from kernel.config import TlxConfig, load_config
from kernel.engine import Engine
from kernel.logging import configure_logging
from kernel.memory import ProjectMemory
from kernel.modules import ModuleLoader, ServiceRegistry
from kernel.plugins import PluginLoader
from kernel.processes import ProcessRegistry
from kernel.prompt_builder import SystemPromptBuilder
from kernel.sandbox import Sandbox
from kernel.schema import Usage
from kernel.session import Session, SessionStore
from kernel.skills import SkillsRegistry
from kernel.slash import SlashCommand, SlashRegistry
from kernel.tools import Tool, ToolRegistry

__version__ = "0.1.0"

TOOL_SEARCH_THRESHOLD = 20

logger = structlog.get_logger(__name__)


def _default_db_path() -> Path:
    return Path.home() / ".tlx" / "sessions.db"


def _load_sandbox_roots(kernel: Any) -> None:
    try:
        row = kernel.session_store._conn.execute(
            "SELECT value FROM kv WHERE session_id = ? AND key = 'sandbox_roots'",
            (kernel.session_id,),
        ).fetchone()
        if row:
            import json
            for p in json.loads(row["value"]):
                kernel.sandbox.add(p)
    except Exception:
        pass


def _save_sandbox_roots(kernel: Any) -> None:
    data = kernel.sandbox.to_json()
    kernel.session_store._conn.execute(
        "INSERT OR REPLACE INTO kv (session_id, key, value) VALUES (?, 'sandbox_roots', ?)",
        (kernel.session_id, data),
    )
    kernel.session_store._conn.commit()


def _load_sandbox_domains(kernel: Any) -> None:
    try:
        row = kernel.session_store._conn.execute(
            "SELECT value FROM kv WHERE session_id = ? AND key = 'sandbox_domains'",
            (kernel.session_id,),
        ).fetchone()
        if row:
            import json
            for d in json.loads(row["value"]):
                kernel.sandbox.add_domain(d)
    except Exception:
        pass


def _save_sandbox_domains(kernel: Any) -> None:
    data = kernel.sandbox.to_json_domains()
    kernel.session_store._conn.execute(
        "INSERT OR REPLACE INTO kv (session_id, key, value) VALUES (?, 'sandbox_domains', ?)",
        (kernel.session_id, data),
    )
    kernel.session_store._conn.commit()


def _load_sandbox_capabilities(kernel: Any) -> None:
    try:
        row = kernel.session_store._conn.execute(
            "SELECT value FROM kv WHERE session_id = ? AND key = 'sandbox_capabilities'",
            (kernel.session_id,),
        ).fetchone()
        if row:
            import json
            kernel.sandbox.allowed_capabilities = set(json.loads(row["value"]))
    except Exception:
        pass


def _save_sandbox_capabilities(kernel: Any) -> None:
    data = kernel.sandbox.to_json_capabilities()
    kernel.session_store._conn.execute(
        "INSERT OR REPLACE INTO kv (session_id, key, value) VALUES (?, 'sandbox_capabilities', ?)",
        (kernel.session_id, data),
    )
    kernel.session_store._conn.commit()


def _load_routing_budgets(kernel: Any) -> None:
    try:
        row = kernel.session_store._conn.execute(
            "SELECT value FROM kv WHERE session_id = ? AND key = 'routing_budgets'",
            (kernel.session_id,),
        ).fetchone()
        if row:
            import json
            kernel.config.routing.token_budgets.update(json.loads(row["value"]))
    except Exception:
        pass


def _save_routing_budgets(kernel: Any) -> None:
    import json
    data = json.dumps(kernel.config.routing.token_budgets)
    kernel.session_store._conn.execute(
        "INSERT OR REPLACE INTO kv (session_id, key, value) VALUES (?, 'routing_budgets', ?)",
        (kernel.session_id, data),
    )
    kernel.session_store._conn.commit()


def _build_engine(name: str, model: str) -> Engine:
    if name == "claude":
        from kernel.engines.claude import ClaudeEngine

        return ClaudeEngine(model=model)
    if name == "gemini":
        from kernel.engines.gemini import GeminiEngine

        return GeminiEngine(model=model)
    raise ValueError(f"unsupported default engine: {name!r}")


class Kernel:
    config: TlxConfig
    session_store: SessionStore
    session: Session
    session_id: str
    active_engine: str
    active_model: str
    caveman_mode: str
    compaction_threshold: int
    tools: ToolRegistry
    services: ServiceRegistry
    sandbox: Sandbox
    processes: ProcessRegistry
    plugins: PluginLoader
    module_loader: ModuleLoader
    modules: ModuleLoader
    slash: SlashRegistry
    engine: Engine
    costs: dict[str, Any]
    confirm: Callable[[str], Awaitable[bool]] | None
    request_external_edit: Callable[[str], Awaitable[str]] | None
    advisor_pair: tuple[str, str] | None
    compactor: Compactor
    skills: SkillsRegistry
    memory: ProjectMemory
    prompt_builder: SystemPromptBuilder
    version: str
    surface: str
    _shutdown_hooks: list[Callable[[], None]]

    def __init__(self) -> None:
        self.costs = {}
        self.confirm = None
        self.request_external_edit = None
        self.advisor_pair = None
        self.version = __version__
        self._shutdown_hooks = []

    def on_shutdown(self, cb: Callable[[], None]) -> None:
        self._shutdown_hooks.append(cb)

    def shutdown(self) -> None:
        for cb in reversed(self._shutdown_hooks):
            try:
                cb()
            except Exception as e:
                logger.warning(
                    "kernel.shutdown_hook_failed",
                    hook=getattr(cb, "__name__", repr(cb)),
                    error=str(e),
                )
        self._shutdown_hooks.clear()
        try:
            if hasattr(self, "session_store") and self.session_store is not None:
                self.session_store.close()
        except Exception as e:
            logger.warning("kernel.session_store_close_failed", error=str(e))

    def defer_slash_register(self, cmd: SlashCommand) -> None:
        """Module register_fn hook: queue a slash command for the post-boot drain."""
        pending = getattr(self, "_pending_slash", None)
        if pending is None:
            pending = []
            self._pending_slash = pending
        pending.append(cmd)

    def _start_reaper_task(self) -> None:
        """Periodic reaper for finished processes (ui surface only)."""
        async def _reap_loop() -> None:
            while True:
                try:
                    await asyncio.sleep(5)
                    await self.processes.reap_finished()
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    logger.warning("kernel.reaper_iteration_failed", error=str(e))

        task = asyncio.create_task(_reap_loop(), name="tlx.kernel.reaper")
        self._reaper_task = task

        def _cancel_reaper() -> None:
            if not task.done():
                task.cancel()

        self.on_shutdown(_cancel_reaper)

    def report_progress(self, stage: str, detail: str = "") -> None:
        """Push progress event into all UI event queues. No-op when absent."""
        queues = getattr(self, "event_queues", None)
        if not queues:
            return
        evt = {
            "type": "progress",
            "stage": stage,
            "detail": detail,
            "ts": time.time(),
        }
        for q in list(queues):
            try:
                q.put_nowait(evt)
            except Exception as e:
                logger.warning("kernel.report_progress_enqueue_failed", error=str(e))

    async def compact_history(
        self,
        session_id: str,
        usage: Usage | None = None,
    ) -> CompactionResult:
        """Compact session history. If usage given, only run when total > threshold."""
        if usage is not None:
            threshold = getattr(self, "compaction_threshold", 0)
            total = usage.input_tokens + usage.output_tokens
            if not (threshold and total > threshold):
                return CompactionResult(summary="", turns_replaced=0)
        compactor = getattr(self, "compactor", None)
        if compactor is None:
            return CompactionResult(summary="", turns_replaced=0)
        history = list(self.session_store.get_history(session_id))
        _, result = await compactor.compact(history)
        return result

    @classmethod
    async def boot(
        cls,
        *,
        config_path: Path | None = None,
        config: TlxConfig | None = None,
        db_path: Path | None = None,
        plugin_paths: list[Path] | None = None,
        module_paths: list[Path] | None = None,
        engine_factory: Callable[[str, str], Engine] | None = None,
        cwd: Path | None = None,
        surface: str = "ui",
    ) -> Kernel:
        configure_logging()

        kernel = cls()
        kernel.surface = surface

        kernel.config = config if config is not None else load_config(config_path)
        kernel.active_engine = kernel.config.default_engine
        kernel.active_model = kernel.config.default_model
        kernel.caveman_mode = kernel.config.caveman_mode
        kernel.compaction_threshold = kernel.config.compaction_threshold

        kernel.session_store = SessionStore(
            db_path if db_path is not None else _default_db_path()
        )
        kernel.session = kernel.session_store.new_session(
            kernel.active_engine, kernel.active_model
        )
        kernel.session_id = kernel.session.id
        kernel.session_store.set_current_session(kernel.session_id)

        kernel.services = ServiceRegistry()
        kernel.sandbox = Sandbox()
        _load_sandbox_roots(kernel)
        _load_sandbox_domains(kernel)
        _load_sandbox_capabilities(kernel)
        kernel.processes = ProcessRegistry()

        kernel.tools = ToolRegistry()
        from kernel.tools_builtin import register_builtin_tools
        register_builtin_tools(kernel)

        from kernel.embeddings import make_embedder
        try:
            kernel.services.register("embedder", make_embedder(kernel.config))
        except Exception as e:
            logger.warning("kernel.embedder_init_failed", error=str(e))

        kernel.plugins = PluginLoader(paths=plugin_paths)
        kernel.plugins.discover_and_load()

        kernel.module_loader = ModuleLoader(
            kernel=kernel,
            kernel_version=__version__,
            paths=module_paths,
        )
        kernel.modules = kernel.module_loader
        kernel.module_loader.discover()
        kernel.module_loader.load_all(kernel.config.modules)

        loaded_modules = list((kernel.module_loader.loaded or {}).keys())
        module_skill_dirs = [
            Path("modules") / m / "skills" for m in loaded_modules
        ]
        kernel.skills = SkillsRegistry(
            [Path.home() / ".tlx" / "skills", *module_skill_dirs]
        )
        kernel.skills.discover()
        kernel.tools.register(Tool(
            name="skill_read",
            description="Read full content of a skill by name.",
            params={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Skill name."}
                },
                "required": ["name"],
            },
            handler=lambda name: kernel.skills.read_skill(name),
        ))

        kernel.memory = ProjectMemory(cwd=cwd if cwd is not None else Path.cwd())
        await kernel.memory.load()

        async def _memory_write_handler(content: str) -> str:
            await kernel.memory.write(content)
            return "memory updated"

        kernel.tools.register(Tool(
            name="memory_write",
            description=(
                "Overwrite memory.md in the current directory. Use to persist "
                "build commands, debug findings, project conventions."
            ),
            params={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Full new content of memory.md.",
                    }
                },
                "required": ["content"],
            },
            handler=_memory_write_handler,
        ))

        kernel.prompt_builder = SystemPromptBuilder()

        if surface != "mcp":
            from kernel.engines.gemini import GeminiEngine
            kernel.compactor = Compactor(GeminiEngine(model="gemini-2.5-flash-lite"))

            factory = engine_factory if engine_factory is not None else _build_engine
            kernel.engine = factory(kernel.active_engine, kernel.active_model)

            if kernel.config.routing.enabled:
                from kernel.engines.claude import ClaudeEngine
                from kernel.engines.gemini import GeminiEngine
                from kernel.engines.router import RouterEngine
                from kernel.routing import TaskClassifier
                r_cfg = kernel.config.routing
                classifier = TaskClassifier(r_cfg)
                tier_engines: dict[int, Engine] = {
                    0: GeminiEngine(model=r_cfg.tiers[0]),
                    1: ClaudeEngine(model=r_cfg.tiers[1]),
                    2: ClaudeEngine(model=r_cfg.tiers[2]),
                    3: ClaudeEngine(model=r_cfg.tiers[3]),
                }
                kernel.engine = RouterEngine(
                    tier_engines, classifier, r_cfg,
                    prompt_builder=kernel.prompt_builder,
                )
                kernel.active_engine = "router"

            _load_routing_budgets(kernel)

            kernel.slash = SlashRegistry()
            for _cmd in getattr(kernel, "_pending_slash", ()) or ():
                kernel.slash.register(_cmd)
            kernel._pending_slash = []

        if len(kernel.tools.all_real()) > TOOL_SEARCH_THRESHOLD:
            kernel.tools.tool_search_mode = True
            structlog.get_logger(__name__).info(
                "tool_search_mode.auto_enabled",
                tool_count=len(kernel.tools.all_real()),
                threshold=TOOL_SEARCH_THRESHOLD,
            )

        if surface == "ui":
            kernel._start_reaper_task()
        return kernel
