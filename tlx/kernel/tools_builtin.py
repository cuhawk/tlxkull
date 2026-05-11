"""Built-in agent tools — process control gated by capabilities."""
from __future__ import annotations

import asyncio
import json
from typing import Any

from kernel.tools import Tool


def register_builtin_tools(kernel: Any) -> None:
    tools = [
        _make_shell_exec(kernel),
        _make_shell_bg(kernel),
        _make_process_list(kernel),
        _make_process_kill(kernel),
        _make_switch_engine(kernel),
    ]
    for t in tools:
        kernel.tools.register(t)


_ENGINE_DEFAULTS = {
    "claude": "claude-sonnet-4-6",
    "gemini": "gemini-2.5-flash-lite",
}


def _make_switch_engine(kernel: Any) -> Tool:
    async def _impl(engine: str, model: str = "") -> str:
        engine = (engine or "").strip().lower()
        if engine not in _ENGINE_DEFAULTS:
            return json.dumps({
                "ok": False,
                "error": f"unsupported engine: {engine!r}. Use 'claude' or 'gemini'.",
            })
        target_model = (model or "").strip() or _ENGINE_DEFAULTS[engine]
        if "opus" in target_model.lower():
            return json.dumps({
                "ok": False,
                "error": (
                    "opus models are not switchable via tool. "
                    "Use /engine advisor claude+claude for bounded Opus access."
                ),
            })
        from kernel import _build_engine

        try:
            new_engine = _build_engine(engine, target_model)
        except Exception as e:
            return json.dumps({"ok": False, "error": f"build failed: {e}"})
        kernel.engine = new_engine
        kernel.active_engine = engine
        kernel.active_model = target_model
        return json.dumps({
            "ok": True,
            "active_engine": engine,
            "active_model": target_model,
            "note": "switch takes effect on next assistant turn",
        })

    return Tool(
        name="switch_engine",
        description=(
            "Switch the active LLM engine. Use to move between 'claude' and "
            "'gemini' for cost/quality tradeoffs. Optional 'model' picks a "
            "specific model id (defaults: claude-sonnet-4-6, "
            "gemini-2.5-flash-lite). Opus models are blocked here — use the "
            "/engine advisor slash command for bounded Opus access. The new "
            "engine activates on the next user turn; current turn finishes "
            "with the previous engine."
        ),
        params={
            "type": "object",
            "properties": {
                "engine": {
                    "type": "string",
                    "enum": ["claude", "gemini"],
                    "description": "Engine family.",
                },
                "model": {
                    "type": "string",
                    "description": (
                        "Optional model id. Omit for engine default."
                    ),
                },
            },
            "required": ["engine"],
        },
        handler=_impl,
        requires=[],
    )


def _make_shell_exec(kernel: Any) -> Tool:
    async def _impl(cmd: str, timeout: int = 30) -> str:  # noqa: ASYNC109
        if "shell_exec" not in kernel.sandbox.allowed_capabilities:
            return "PermissionError: shell_exec capability not enabled. Use /allow shell_exec"
        try:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=timeout
                )
                return json.dumps({
                    "stdout": stdout.decode(errors="replace"),
                    "stderr": stderr.decode(errors="replace"),
                    "returncode": proc.returncode,
                })
            except TimeoutError:
                proc.kill()
                return json.dumps({"stdout": "", "stderr": "timeout", "returncode": -1})
        except Exception as e:
            return json.dumps({"stdout": "", "stderr": str(e), "returncode": -1})

    return Tool(
        name="shell_exec",
        description="Execute a shell command. Requires shell_exec capability (/allow shell_exec).",
        params={
            "type": "object",
            "properties": {
                "cmd": {"type": "string", "description": "Shell command to run."},
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds.",
                    "default": 30,
                },
            },
            "required": ["cmd"],
        },
        handler=_impl,
        requires=["shell_exec"],
    )


def _make_shell_bg(kernel: Any) -> Tool:
    async def _impl(cmd: str, label: str) -> str:
        if "shell_exec" not in kernel.sandbox.allowed_capabilities:
            return "PermissionError: shell_exec capability not enabled."
        mp = await kernel.processes.spawn(cmd.split(), label=label)
        return json.dumps({"label": label, "pid": mp.proc.pid})

    return Tool(
        name="shell_bg",
        description="Spawn a background process by label.",
        params={
            "type": "object",
            "properties": {
                "cmd": {"type": "string", "description": "Command to run."},
                "label": {"type": "string", "description": "Label for process tracking."},
            },
            "required": ["cmd", "label"],
        },
        handler=_impl,
        requires=["shell_exec"],
    )


def _make_process_list(kernel: Any) -> Tool:
    async def _impl() -> str:
        procs = kernel.processes.list_live()
        return json.dumps([
            {"label": mp.label, "pid": mp.pid, "elapsed_s": round(mp.elapsed, 1)}
            for mp in procs
        ])

    return Tool(
        name="process_list",
        description="List running background processes.",
        params={"type": "object", "properties": {}},
        handler=_impl,
        requires=[],
    )


def _make_process_kill(kernel: Any) -> Tool:
    async def _impl(label: str) -> str:
        if "shell_exec" not in kernel.sandbox.allowed_capabilities:
            return "PermissionError: shell_exec capability not enabled."
        killed = await kernel.processes.kill(label)
        return json.dumps({"killed": killed, "label": label})

    return Tool(
        name="process_kill",
        description="Kill a background process by label.",
        params={
            "type": "object",
            "properties": {
                "label": {"type": "string", "description": "Process label."},
            },
            "required": ["label"],
        },
        handler=_impl,
        requires=["shell_exec"],
    )
