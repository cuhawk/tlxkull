"""Per-session path sandbox — real enforcement for Phase 1."""
from __future__ import annotations

import json
from pathlib import Path


class Sandbox:
    def __init__(self, roots: list[Path] | None = None) -> None:
        self._roots: list[Path] = list(roots or [])
        self._allowed_domains: list[str] = []
        self.allowed_capabilities: set[str] = set()

    def add_domain(self, domain: str) -> None:
        d = domain.lower().lstrip("*.")
        if d not in self._allowed_domains:
            self._allowed_domains.append(d)

    def remove_domain(self, domain: str) -> bool:
        d = domain.lower().lstrip("*.")
        if d in self._allowed_domains:
            self._allowed_domains.remove(d)
            return True
        return False

    def list_domains(self) -> list[str]:
        return list(self._allowed_domains)

    def is_domain_allowed(self, url: str) -> bool:
        if not self._allowed_domains:
            return True
        from urllib.parse import urlparse
        hostname = (urlparse(url).hostname or "").lower()
        return any(
            hostname == d or hostname.endswith("." + d)
            for d in self._allowed_domains
        )

    def to_json_domains(self) -> str:
        return json.dumps(self._allowed_domains)

    def to_json_capabilities(self) -> str:
        return json.dumps(list(self.allowed_capabilities))

    def add(self, path: str) -> Path:
        p = Path(path).resolve()
        if p not in self._roots:
            self._roots.append(p)
        return p

    def remove(self, path: str) -> bool:
        p = Path(path).resolve()
        if p in self._roots:
            self._roots.remove(p)
            return True
        return False

    def list_roots(self) -> list[Path]:
        return list(self._roots)

    def is_allowed(self, path: str) -> bool:
        if not self._roots:
            return True
        target = Path(path).resolve()
        return any(target == r or r in target.parents for r in self._roots)

    def to_json(self) -> str:
        return json.dumps([str(r) for r in self._roots])

    @classmethod
    def from_json(cls, data: str) -> Sandbox:
        paths = json.loads(data)
        return cls(roots=[Path(p) for p in paths])
