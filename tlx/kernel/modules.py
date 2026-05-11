"""Module discovery, lifecycle, and service registry."""
from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any

import structlog
from pydantic import BaseModel, ConfigDict, Field

from kernel.tools import Tool

logger = structlog.get_logger(__name__)


class ModuleNotFoundError(Exception):
    """Raised when a module declares a dependency that wasn't discovered."""


class CircularDependencyError(Exception):
    """Raised when topological sort can't linearize the dependency graph."""


class KernelVersionError(Exception):
    """Raised when a module's requires_kernel constraint can't be parsed."""


class ModuleSpec(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    version: str
    requires_kernel: str
    depends_on: list[str] = Field(default_factory=list)
    optional_deps: list[str] = Field(default_factory=list)
    config_schema: type[BaseModel] | None = None
    register_fn: Callable[..., Any]


class RegisteredModule(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    spec: ModuleSpec
    tools: list[Tool] = Field(default_factory=list)
    config: BaseModel | None = None


_OPS = (">=", "<=", "==", "!=", ">", "<")


def _parse_version(v: str) -> tuple[int, ...]:
    head = v.split("-", 1)[0].split("+", 1)[0]
    parts = head.split(".")
    try:
        return tuple(int(p) for p in parts)
    except ValueError as e:
        raise KernelVersionError(f"unparseable version: {v}") from e


def _check_constraint(constraint: str, current: str) -> bool:
    c = (constraint or "").strip()
    if not c:
        return True
    for op in _OPS:
        if c.startswith(op):
            target = _parse_version(c[len(op):].strip())
            cur = _parse_version(current)
            n = max(len(target), len(cur))
            target = target + (0,) * (n - len(target))
            cur = cur + (0,) * (n - len(cur))
            if op == ">=":
                return cur >= target
            if op == "<=":
                return cur <= target
            if op == "==":
                return cur == target
            if op == "!=":
                return cur != target
            if op == ">":
                return cur > target
            if op == "<":
                return cur < target
    return _parse_version(c) == _parse_version(current)


class ServiceRegistry:
    def __init__(self) -> None:
        self._services: dict[str, Any] = {}

    def register(self, name: str, obj: Any) -> None:
        if name in self._services:
            raise ValueError(f"service already registered: {name}")
        self._services[name] = obj

    def get(self, name: str, default: Any = None) -> Any:
        return self._services.get(name, default)


def _default_paths() -> list[Path]:
    repo_modules = Path(__file__).resolve().parent.parent / "modules"
    user_modules = Path.home() / ".tlx" / "modules"
    return [repo_modules, user_modules]


class ModuleLoader:
    def __init__(
        self,
        kernel: Any,
        kernel_version: str,
        paths: list[Path] | None = None,
    ) -> None:
        self.kernel = kernel
        self.kernel_version = kernel_version
        self.paths: list[Path] = paths if paths is not None else _default_paths()
        self.available: dict[str, ModuleSpec] = {}
        self.loaded: dict[str, RegisteredModule] = {}
        self.failed: dict[str, Exception] = {}

    def discover(self) -> list[ModuleSpec]:
        specs: list[ModuleSpec] = []
        for base in self.paths:
            if not base.exists() or not base.is_dir():
                continue
            for entry in sorted(base.iterdir()):
                if not entry.is_dir():
                    continue
                module_py = entry / "module.py"
                if not module_py.is_file():
                    continue
                try:
                    spec = self._import_module_py(module_py)
                except Exception as e:
                    logger.warning(
                        "module_import_failed", path=str(module_py), error=str(e)
                    )
                    continue
                if not isinstance(spec, ModuleSpec):
                    logger.warning(
                        "module_missing_spec", path=str(module_py)
                    )
                    continue
                try:
                    ok = _check_constraint(spec.requires_kernel, self.kernel_version)
                except KernelVersionError as e:
                    logger.warning(
                        "module_bad_version_constraint",
                        name=spec.name,
                        constraint=spec.requires_kernel,
                        error=str(e),
                    )
                    continue
                if not ok:
                    logger.warning(
                        "module_kernel_version_mismatch",
                        name=spec.name,
                        requires=spec.requires_kernel,
                        kernel=self.kernel_version,
                    )
                    continue
                self.available[spec.name] = spec
                specs.append(spec)
        return specs

    def load_all(self, config: dict[str, Any]) -> None:
        ordered = self._topo_sort(list(self.available.values()))
        for spec in ordered:
            try:
                mod_cfg: Any = config.get(spec.name)
                if spec.config_schema is not None and mod_cfg is not None:
                    mod_cfg = spec.config_schema.model_validate(mod_cfg)
                registered = spec.register_fn(self.kernel, mod_cfg)
                if not isinstance(registered, RegisteredModule):
                    raise TypeError(
                        f"register_fn() for {spec.name} must return RegisteredModule, "
                        f"got {type(registered).__name__}"
                    )
                self.loaded[spec.name] = registered
            except Exception as e:
                logger.warning("module_register_failed", name=spec.name, error=str(e))
                self.failed[spec.name] = e

    def _import_module_py(self, path: Path) -> Any:
        pkg_dir = path.parent
        suffix = uuid.uuid4().hex[:8]
        pkg_name = f"_tlx_mod_{pkg_dir.name}_{suffix}"
        init_py = pkg_dir / "__init__.py"

        if init_py.is_file():
            pkg_spec = importlib.util.spec_from_file_location(
                pkg_name,
                init_py,
                submodule_search_locations=[str(pkg_dir)],
            )
            if pkg_spec is None or pkg_spec.loader is None:
                raise ImportError(f"cannot create package spec for {pkg_dir}")
        else:
            pkg_spec = importlib.machinery.ModuleSpec(
                pkg_name, loader=None, is_package=True,
            )
            pkg_spec.submodule_search_locations = [str(pkg_dir)]

        pkg_module = importlib.util.module_from_spec(pkg_spec)
        sys.modules[pkg_name] = pkg_module
        if pkg_spec.loader is not None:
            try:
                pkg_spec.loader.exec_module(pkg_module)
            except Exception:
                sys.modules.pop(pkg_name, None)
                raise

        mod_name = f"{pkg_name}.module"
        spec = importlib.util.spec_from_file_location(mod_name, path)
        if spec is None or spec.loader is None:
            sys.modules.pop(pkg_name, None)
            raise ImportError(f"cannot create module spec for {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = module
        try:
            spec.loader.exec_module(module)
        except Exception:
            sys.modules.pop(mod_name, None)
            sys.modules.pop(pkg_name, None)
            raise
        return getattr(module, "MODULE", None)

    def _topo_sort(self, specs: list[ModuleSpec]) -> list[ModuleSpec]:
        by_name = {s.name: s for s in specs}
        in_degree: dict[str, int] = {s.name: 0 for s in specs}
        edges: dict[str, list[str]] = {s.name: [] for s in specs}

        for s in specs:
            for dep in s.depends_on:
                if dep not in by_name:
                    raise ModuleNotFoundError(
                        f"module {s.name!r} depends on unknown module {dep!r}"
                    )
                edges[dep].append(s.name)
                in_degree[s.name] += 1

        queue = sorted(n for n, d in in_degree.items() if d == 0)
        order: list[ModuleSpec] = []
        while queue:
            n = queue.pop(0)
            order.append(by_name[n])
            for nxt in sorted(edges[n]):
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    queue.append(nxt)
            queue.sort()

        if len(order) != len(specs):
            unresolved = [n for n, d in in_degree.items() if d > 0]
            raise CircularDependencyError(
                f"circular dependency among: {sorted(unresolved)}"
            )
        return order
