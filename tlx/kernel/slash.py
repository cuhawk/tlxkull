"""Slash command registry and built-in commands."""
from __future__ import annotations

import asyncio
import inspect
from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import BaseModel, ConfigDict


class UnknownCommandError(Exception):
    """Raised when dispatch receives an unregistered command."""


class SlashCommand(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    description: str
    handler: Callable[..., str | None | Awaitable[str | None]]


def _get(obj: Any, name: str, default: Any) -> Any:
    return getattr(obj, name, default)


def _set(obj: Any, name: str, value: Any) -> None:
    setattr(obj, name, value)


class SlashRegistry:
    def __init__(self) -> None:
        self._commands: dict[str, SlashCommand] = {}
        self._register_builtins()

    def register(self, cmd: SlashCommand) -> None:
        if cmd.name in self._commands:
            raise ValueError(f"slash command already registered: /{cmd.name}")
        self._commands[cmd.name] = cmd

    def all(self) -> list[SlashCommand]:
        return list(self._commands.values())

    def dispatch(self, raw: str, kernel: Any) -> str | None | Awaitable[str | None]:
        text = raw.strip()
        if text.startswith("/"):
            text = text[1:]
        if not text:
            raise UnknownCommandError("empty command")
        parts = text.split(None, 1)
        name = parts[0]
        args = parts[1].strip() if len(parts) > 1 else ""
        cmd = self._commands.get(name)
        if cmd is None:
            raise UnknownCommandError(f"unknown command: /{name}")
        return cmd.handler(args, kernel)

    async def dispatch_async(self, raw: str, kernel: Any) -> str | None:
        """Dispatch a slash command, awaiting the result if it is a coroutine."""
        result = self.dispatch(raw, kernel)
        if inspect.isawaitable(result):
            return await result
        return result

    def _register_builtins(self) -> None:
        registry = self

        def _help(args: str, kernel: Any) -> str:
            lines = ["available commands:"]
            for cmd in sorted(registry.all(), key=lambda c: c.name):
                lines.append(f"  /{cmd.name} — {cmd.description}")
            return "\n".join(lines)

        def _engine(args: str, kernel: Any) -> str:
            if not args:
                return _get(kernel, "active_engine", "unknown")
            tokens = args.split()
            head = tokens[0]
            if head == "router":
                from kernel.engine import Engine
                from kernel.engines.claude import ClaudeEngine
                from kernel.engines.gemini import GeminiEngine
                from kernel.engines.router import RouterEngine
                from kernel.routing import TaskClassifier
                cfg = kernel.config.routing
                classifier = TaskClassifier(cfg)
                tier_engines: dict[int, Engine] = {
                    0: GeminiEngine(model=cfg.tiers[0]),
                    1: ClaudeEngine(model=cfg.tiers[1]),
                    2: ClaudeEngine(model=cfg.tiers[2]),
                    3: ClaudeEngine(model=cfg.tiers[3]),
                }
                builder = _get(kernel, "prompt_builder", None)
                _set(kernel, "engine", RouterEngine(
                    tier_engines, classifier, cfg, prompt_builder=builder
                ))
                _set(kernel, "active_engine", "router")
                return f"router active — tiers: {cfg.tiers}"
            if head == "advisor":
                if len(tokens) < 2 or "+" not in tokens[1]:
                    return "usage: /engine advisor <executor>+<advisor>"
                executor, advisor = tokens[1].split("+", 1)
                model_defaults = {
                    "claude": "claude-sonnet-4-6",
                    "gemini": "gemini-2.5-flash-lite",
                }
                if executor not in model_defaults or advisor not in model_defaults:
                    return f"unknown engine pair: {executor}+{advisor}"
                from kernel import _build_engine
                from kernel.engines.advisor import AdvisorEngine
                exec_engine = _build_engine(executor, model_defaults[executor])
                adv_engine = _build_engine(advisor, model_defaults[advisor])
                _set(kernel, "active_engine", "advisor")
                _set(kernel, "advisor_pair", (executor, advisor))
                _set(kernel, "engine", AdvisorEngine(exec_engine, adv_engine))
                return f"engine set: advisor ({executor}+{advisor})"
            if head not in {"gemini", "claude"}:
                return f"unknown engine: {head}"
            from kernel import _build_engine
            model_defaults = {
                "claude": "claude-sonnet-4-6",
                "gemini": "gemini-2.5-flash-lite",
            }
            model = _get(kernel, "active_model", model_defaults.get(head, head))
            # if switching engine family, reset to that engine's default model
            if _get(kernel, "active_engine", "") != head:
                model = model_defaults.get(head, head)
                _set(kernel, "active_model", model)
            _set(kernel, "active_engine", head)
            _set(kernel, "engine", _build_engine(head, model))
            return f"engine set: {head} ({model})"

        def _model(args: str, kernel: Any) -> str:
            if not args:
                return _get(kernel, "active_model", "unknown")
            value = args.strip()
            _set(kernel, "active_model", value)
            return f"model set: {value}"

        def _cost(args: str, kernel: Any) -> str:
            costs = _get(kernel, "costs", {}) or {}
            if not costs:
                return "no cost recorded — total: $0.0000 USD"
            lines = []
            total = 0.0
            for engine, value in costs.items():
                amount = float(value.total) if hasattr(value, "total") else float(value)
                total += amount
                lines.append(f"  {engine}: ${amount:.4f} USD")
            lines.append(f"total: ${total:.4f} USD")
            return "\n".join(lines)

        def _cache(args: str, kernel: Any) -> str:
            store = _get(kernel, "session_store", None)
            sid = _get(kernel, "session_id", None)
            if store is None or sid is None:
                return "cache hit rate: n/a"
            try:
                rate = store.cache_hit_rate(sid)
            except Exception as e:
                return f"cache hit rate: error — {e}"
            return f"cache hit rate: {rate * 100:.1f}%"

        def _history(args: str, kernel: Any) -> str:
            arg = args.strip()
            try:
                n = int(arg) if arg else 10
            except ValueError:
                return "usage: /history [n]"
            store = _get(kernel, "session_store", None)
            sid = _get(kernel, "session_id", None)
            if store is None or sid is None:
                return "no session"
            history = store.get_history(sid)[-n:]
            if not history:
                return "(empty)"
            lines = []
            for msg in history:
                content = msg.content if isinstance(msg.content, str) else "<blocks>"
                lines.append(f"{msg.role}: {content}")
            return "\n".join(lines)

        def _save(args: str, kernel: Any) -> str:
            name = args.strip()
            if not name:
                return "usage: /save <name>"
            store = _get(kernel, "session_store", None)
            sid = _get(kernel, "session_id", None)
            if store is None or sid is None:
                return "no session"
            store.save_as(sid, name)
            return f"session saved as: {name}"

        def _load(args: str, kernel: Any) -> str:
            name = args.strip()
            if not name:
                return "usage: /load <name>"
            store = _get(kernel, "session_store", None)
            if store is None:
                return "no session store"
            session = store.load(name)
            _set(kernel, "session_id", session.id)
            _set(kernel, "active_engine", session.active_engine)
            _set(kernel, "active_model", session.active_model)
            _set(kernel, "caveman_mode", session.caveman_mode)
            from kernel import _load_sandbox_roots
            kernel.sandbox._roots.clear()
            _load_sandbox_roots(kernel)
            return f"session loaded: {name}"

        async def _sessions(args: str, kernel: Any) -> str:
            if args.strip() == "clear":
                store = _get(kernel, "session_store", None)
                if store is None:
                    return "no session store"
                confirm = _get(kernel, "confirm", None)
                if confirm is None:
                    return "confirmation required — no confirm surface registered"
                ok = bool(await confirm("delete ALL sessions? [y/N] "))
                if not ok:
                    return "aborted"
                store.clear_all()
                engine = _get(kernel, "active_engine", "claude")
                model = _get(kernel, "active_model", "")
                session = store.new_session(engine, model)
                _set(kernel, "session_id", session.id)
                return "all sessions deleted — new session started"
            store = _get(kernel, "session_store", None)
            if store is None:
                return "no session store"
            items = store.list_sessions()
            if not items:
                return "(no saved sessions)"
            return "\n".join(
                f"  {s.name or s.id} ({s.active_engine}/{s.active_model})"
                for s in items
            )

        async def _clear(args: str, kernel: Any) -> str:
            confirm = _get(kernel, "confirm", None)
            if confirm is None:
                return "confirmation required — no confirm surface registered"
            ok = bool(await confirm("clear current session? [y/N] "))
            if not ok:
                return "clear aborted"
            store = _get(kernel, "session_store", None)
            if store is None:
                return "no session store"
            engine = _get(kernel, "active_engine", "claude")
            model = _get(kernel, "active_model", "")
            session = store.new_session(engine, model)
            _set(kernel, "session_id", session.id)
            return "session cleared"

        def _compact(args: str, kernel: Any) -> str:
            sid = _get(kernel, "session_id", None)
            if sid is None:
                return "no session"
            asyncio.ensure_future(kernel.compact_history(sid))
            return "compacting..."

        def _memory(args: str, kernel: Any) -> str:
            mem = _get(kernel, "memory", None)
            if mem is None:
                return "no memory"
            arg = args.strip()
            if not arg:
                return mem.content if mem.content else "(no memory.md in cwd)"
            if arg == "clear":
                mem.path().write_text("", encoding="utf-8")
                mem.content = ""
                return "memory cleared"
            return "usage: /memory [clear]"

        async def _edit(args: str, kernel: Any) -> str:
            cb = _get(kernel, "request_external_edit", None)
            if cb is None:
                return "no editor surface available — set kernel.request_external_edit"
            return await cb(args)

        def _caveman(args: str, kernel: Any) -> str:
            arg = args.strip().lower()
            if not arg:
                return f"caveman: {_get(kernel, 'caveman_mode', 'lite')}"
            if arg not in {"on", "off", "lite", "full", "ultra"}:
                return "usage: /caveman [on|off|lite|full|ultra]"
            mode = "full" if arg == "on" else arg
            _set(kernel, "caveman_mode", mode)
            return f"caveman: {mode}"

        def _modules(args: str, kernel: Any) -> str:
            loader = _get(kernel, "module_loader", None)
            if loader is None:
                return "(no module loader)"
            loaded = getattr(loader, "loaded", {}) or {}
            if not loaded:
                return "(no modules loaded)"
            return "\n".join(f"  {name}" for name in sorted(loaded.keys()))

        def _module(args: str, kernel: Any) -> str:
            tokens = args.split(None, 1)
            if len(tokens) < 2 or tokens[0] != "info":
                return "usage: /module info <name>"
            name = tokens[1].strip()
            loader = _get(kernel, "module_loader", None)
            if loader is None:
                return "(no module loader)"
            failed = getattr(loader, "failed", {}) or {}
            if name in failed:
                return f"module {name!r} failed: {failed[name]}"
            loaded = getattr(loader, "loaded", {}) or {}
            if name not in loaded:
                return f"module {name!r} not loaded"
            reg = loaded[name]
            spec = reg.spec
            tools = ", ".join(t.name for t in reg.tools) or "(none)"
            cfg = reg.config.model_dump() if reg.config is not None else None
            return (
                f"name: {spec.name}\n"
                f"version: {spec.version}\n"
                f"requires_kernel: {spec.requires_kernel}\n"
                f"depends_on: {spec.depends_on}\n"
                f"tools: {tools}\n"
                f"config: {cfg}"
            )

        def _sandbox(args: str, kernel: Any) -> str:
            from kernel import _save_sandbox_domains, _save_sandbox_roots
            tokens = args.strip().split(None, 1)
            sub = tokens[0] if tokens else ""
            path_arg = tokens[1].strip() if len(tokens) > 1 else ""

            if not sub or sub == "status":
                roots = kernel.sandbox.list_roots()
                if not roots:
                    return "sandbox: open (no roots set)"
                return f"sandbox: locked ({len(roots)} roots)"

            if sub == "list":
                roots = kernel.sandbox.list_roots()
                if not roots:
                    return "(no roots)"
                return "\n".join(f"  {r}" for r in roots)

            if sub == "add":
                if not path_arg:
                    return "usage: /sandbox add <path>"
                p = kernel.sandbox.add(path_arg)
                _save_sandbox_roots(kernel)
                return f"sandbox: added {p}"

            if sub == "rm":
                if not path_arg:
                    return "usage: /sandbox rm <path>"
                removed = kernel.sandbox.remove(path_arg)
                if removed:
                    _save_sandbox_roots(kernel)
                    return f"sandbox: removed {path_arg}"
                return f"sandbox: {path_arg} was not a root"

            if sub == "add-domain":
                if not path_arg:
                    return "usage: /sandbox add-domain <domain>"
                kernel.sandbox.add_domain(path_arg)
                _save_sandbox_domains(kernel)
                return f"sandbox: domain added {path_arg}"

            if sub == "rm-domain":
                if not path_arg:
                    return "usage: /sandbox rm-domain <domain>"
                removed = kernel.sandbox.remove_domain(path_arg)
                if removed:
                    _save_sandbox_domains(kernel)
                    return f"sandbox: domain removed {path_arg}"
                return f"sandbox: {path_arg} was not an allowed domain"

            if sub == "domains":
                domains = kernel.sandbox.list_domains()
                if not domains:
                    return "(all domains open)"
                return "\n".join(f"  {d}" for d in domains)

            return "usage: /sandbox [status|list|add <path>|rm <path>|add-domain <domain>|rm-domain <domain>|domains]"

        def _ps(args: str, kernel: Any) -> str:
            procs = kernel.processes.list_live()
            if not procs:
                return "(no processes)"
            lines = []
            for mp in procs:
                elapsed = f"{mp.elapsed:.0f}s"
                lines.append(f"  {mp.label:<20} pid={mp.pid}  elapsed={elapsed}")
            return "\n".join(lines)

        def _spawn(args: str, kernel: Any) -> str:
            if not args:
                return "usage: /spawn <label> <cmd...>  e.g. /spawn s1 sleep 30"
            tokens = args.split()
            label = tokens[0]
            cmd = tokens[1:] if len(tokens) > 1 else ["sleep", "30"]
            import asyncio
            try:
                asyncio.ensure_future(kernel.processes.spawn(cmd, label=label))
                return f"spawned: {label} → {' '.join(cmd)}"
            except Exception as e:
                return f"error: {e}"

        def _allow(args: str, kernel: Any) -> str:
            from kernel import _save_sandbox_capabilities
            cap = args.strip()
            if not cap:
                return "usage: /allow <capability>"
            kernel.sandbox.allowed_capabilities.add(cap)
            _save_sandbox_capabilities(kernel)
            return f"capability enabled: {cap}"

        def _deny(args: str, kernel: Any) -> str:
            from kernel import _save_sandbox_capabilities
            cap = args.strip()
            if not cap:
                return "usage: /deny <capability>"
            kernel.sandbox.allowed_capabilities.discard(cap)
            _save_sandbox_capabilities(kernel)
            return f"capability disabled: {cap}"

        def _kill(args: str, kernel: Any) -> str:
            label = args.strip()
            if not label:
                return "usage: /kill <label>"
            asyncio.ensure_future(kernel.processes.kill(label))
            return f"kill signal sent to: {label}"

        def _route(args: str, kernel: Any) -> str:
            from kernel.engines.router import RouterEngine
            engine = _get(kernel, "engine", None)
            if not isinstance(engine, RouterEngine) or engine.last_decision is None:
                return "router not active — use /engine router"
            d = engine.last_decision
            esc = (
                f" (escalated from tier {d.escalated_from})"
                if d.escalated_from is not None else ""
            )
            return f"tier {d.tier} — {d.model} — {d.reason}{esc} — budget {d.max_tokens} tokens"

        def _recon(args: str, kernel: Any) -> str:
            url = args.strip()
            if not url:
                return "usage: /recon <url>"
            return (
                f"## Recon plan for {url}\n\n"
                f"Step 1 — Crawl\n"
                f'  crawl(url="{url}", depth=2, max_pages=30)\n'
                f"  Save HTML to /tmp/tlx/recon/html/\n\n"
                f"Step 2 — Chunk discovery\n"
                f'  discover_js_chunks(base_url="{url}", '
                f'crawl_output_dir="/tmp/tlx/recon/html/", '
                f'output_path="/tmp/tlx/recon/js/")\n'
                f"  This finds ALL JS chunks including lazy-loaded "
                f"routes — not just <script src> tags.\n\n"
                f"Step 3 — Source map extraction\n"
                f"  For each chunk in the result:\n"
                f"    extract_source_map(js_path=<local_path>, "
                f"base_url=<chunk_url>, "
                f'output_dir="/tmp/tlx/recon/sources/")\n'
                f"  If sources written to /tmp/tlx/recon/sources/ → "
                f"use those for analysis.\n"
                f"  Else → use /tmp/tlx/recon/js/ (raw chunks).\n\n"
                f"Step 4 — Index\n"
                f'  docs_ingest_dir(dir="/tmp/tlx/recon/sources/", '
                f'pattern="**/*.js")\n'
                f'  docs_ingest_dir(dir="/tmp/tlx/recon/html/", '
                f'pattern="**/*.html")\n\n'
                f"Step 5 — JS analysis\n"
                f"  Use /js_analyzer on /tmp/tlx/recon/sources/ "
                f"(or /tmp/tlx/recon/js/ if no sources)\n"
                f"  Then /js_analyzer-report\n\n"
                f"Step 6 — Report\n"
                f"  js_generate_report()\n\n"
                f"Begin with Step 1. Call set_plan_step for each "
                f"step as you complete it.\n"
                f"Do not skip steps. If source maps are found, "
                f"always prefer /tmp/tlx/recon/sources/ over raw JS.\n"
            )

        def _budget(args: str, kernel: Any) -> str:
            parts = args.split()
            if len(parts) != 2 or not parts[0].startswith("tier"):
                return "usage: /budget tier<n> <tokens>"
            key = parts[0]
            try:
                val = int(parts[1])
            except ValueError:
                return "tokens must be an integer"
            kernel.config.routing.token_budgets[key] = val
            from kernel import _save_routing_budgets
            _save_routing_budgets(kernel)
            return f"{key} budget → {val} tokens"

        builtins: list[tuple[str, str, Callable[..., str | None]]] = [
            ("help", "list all slash commands", _help),
            ("engine", "show or set active engine", _engine),
            ("model", "show or set active model", _model),
            ("cost", "token + USD totals per engine this session", _cost),
            ("cache", "session cache hit rate", _cache),
            ("history", "last n turns from session store", _history),
            ("save", "save session under a name", _save),
            ("load", "load saved session by name", _load),
            ("sessions", "list saved sessions", _sessions),
            ("clear", "reset session after confirmation", _clear),
            ("compact", "trigger manual compaction", _compact),
            ("memory", "show project memory or `/memory clear`", _memory),
            ("edit", "open $EDITOR with draft and read back", _edit),
            ("caveman", "show or set caveman mode", _caveman),
            ("modules", "list loaded modules", _modules),
            ("module", "module info <name>", _module),
            ("sandbox", "sandbox [status|list|add <path>|rm <path>]", _sandbox),
            ("ps", "list running processes", _ps),
            ("spawn", "spawn a process by label for testing — /spawn <label> <cmd...>", _spawn),
            ("kill", "kill process by label", _kill),
            ("allow", "enable a capability e.g. shell_exec", _allow),
            ("deny", "disable a capability", _deny),
            ("route", "show last routing decision", _route),
            ("budget", "override tier token budget: /budget tier<n> <tokens>", _budget),
            ("recon", "Start a full JS recon pipeline for a target URL.", _recon),
        ]
        for name, desc, handler in builtins:
            self.register(
                SlashCommand(name=name, description=desc, handler=handler)
            )
