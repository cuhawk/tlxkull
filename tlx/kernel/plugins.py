"""Plugin discovery and pipeline execution for kernel hooks."""
from __future__ import annotations

import importlib.util
import sys
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any

import structlog
from pydantic import BaseModel, ConfigDict

logger = structlog.get_logger(__name__)


class Plugin(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    version: str
    pre_message: Callable[[str], str] | None = None
    post_response: Callable[[str], str] | None = None
    pre_tool: Callable[[str, dict], tuple[str, dict]] | None = None
    post_tool: Callable[[str, dict, Any], Any] | None = None


def _default_plugin_paths() -> list[Path]:
    repo_plugins = Path(__file__).resolve().parent.parent / "plugins"
    user_plugins = Path.home() / ".tlx" / "plugins"
    return [repo_plugins, user_plugins]


class PluginLoader:
    def __init__(self, paths: list[Path] | None = None) -> None:
        self.paths: list[Path] = paths if paths is not None else _default_plugin_paths()
        self.loaded: dict[str, Plugin] = {}
        self.failed: dict[str, Exception] = {}

    def discover_and_load(self) -> None:
        for base in self.paths:
            if not base.exists() or not base.is_dir():
                continue
            for entry in sorted(base.iterdir()):
                if not entry.is_dir():
                    continue
                plugin_py = entry / "plugin.py"
                if not plugin_py.is_file():
                    continue
                try:
                    plugin = self._import_plugin_py(plugin_py)
                except Exception as e:
                    logger.warning(
                        "plugin_import_failed", path=str(plugin_py), error=str(e)
                    )
                    continue
                if not isinstance(plugin, Plugin):
                    logger.warning("plugin_missing_spec", path=str(plugin_py))
                    continue
                if plugin.name in self.loaded:
                    logger.warning("plugin_duplicate_name", name=plugin.name)
                    continue
                self.loaded[plugin.name] = plugin

    def run_pre_message(self, msg: str) -> str:
        cur = msg
        for plugin in self.loaded.values():
            if plugin.pre_message is None:
                continue
            try:
                cur = plugin.pre_message(cur)
            except Exception as e:
                self._record_failure(plugin.name, "pre_message", e)
        return cur

    def run_post_response(self, text: str) -> str:
        cur = text
        for plugin in self.loaded.values():
            if plugin.post_response is None:
                continue
            try:
                cur = plugin.post_response(cur)
            except Exception as e:
                self._record_failure(plugin.name, "post_response", e)
        return cur

    def run_pre_tool(self, name: str, args: dict) -> tuple[str, dict]:
        cur_name, cur_args = name, args
        for plugin in self.loaded.values():
            if plugin.pre_tool is None:
                continue
            try:
                cur_name, cur_args = plugin.pre_tool(cur_name, cur_args)
            except Exception as e:
                self._record_failure(plugin.name, "pre_tool", e)
        return cur_name, cur_args

    def run_post_tool(self, name: str, args: dict, result: Any) -> Any:
        cur = result
        for plugin in self.loaded.values():
            if plugin.post_tool is None:
                continue
            try:
                cur = plugin.post_tool(name, args, cur)
            except Exception as e:
                self._record_failure(plugin.name, "post_tool", e)
        return cur

    def _record_failure(self, plugin_name: str, hook: str, exc: Exception) -> None:
        logger.warning(
            "plugin_hook_failed", plugin=plugin_name, hook=hook, error=str(exc)
        )
        self.failed[plugin_name] = exc

    def _import_plugin_py(self, path: Path) -> Any:
        mod_name = f"_tlx_plugin_{uuid.uuid4().hex}"
        spec = importlib.util.spec_from_file_location(mod_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot create plugin spec for {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = module
        try:
            spec.loader.exec_module(module)
        except Exception:
            sys.modules.pop(mod_name, None)
            raise
        return getattr(module, "PLUGIN", None)
