"""Prompt file discovery + frontmatter parsing + validation.

Schema (frontmatter):
    id              str  required, unique across all prompts
    kind            str  one of {"system", "security", "workflow"}
    title           str  required
    tags            list[str] optional, default []
    always_include  bool optional, default False
    priority        int  optional, default 50

Body must be non-empty after frontmatter is stripped.

No PyYAML dependency: a tiny key/value parser handles the strict subset
we use. Lists are written as `[a, b, c]`, scalars are unquoted.
"""

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

VALID_KINDS = {"system", "security", "workflow"}


class LoaderError(Exception):
    """Raised on malformed or duplicated prompt files."""


@dataclass
class Prompt:
    id: str
    kind: str
    title: str
    body: str
    tags: list[str]                 = field(default_factory=list)
    always_include: bool            = False
    priority: int                   = 50
    path: Path | None               = None
    content_hash: str               = ""

    def to_meta(self) -> dict:
        return {
            "id":             self.id,
            "kind":           self.kind,
            "title":          self.title,
            "tags":           ",".join(self.tags),
            "always_include": self.always_include,
            "priority":       self.priority,
            "path":           str(self.path) if self.path else "",
            "content_hash":   self.content_hash,
        }


# ── frontmatter parser ───────────────────────────────────────────────────

_LIST_RE = re.compile(r"^\[(.*)\]$")


def _coerce(raw: str):
    s = raw.strip()
    if s == "":
        return ""
    if (s.startswith('"') and s.endswith('"')) or \
       (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    m = _LIST_RE.match(s)
    if m:
        inner = m.group(1).strip()
        if not inner:
            return []
        return [
            piece.strip().strip('"').strip("'")
            for piece in inner.split(",")
        ]
    if s in ("true", "True"):
        return True
    if s in ("false", "False"):
        return False
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    if re.fullmatch(r"-?\d+\.\d+", s):
        return float(s)
    return s


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return (meta, body). meta is {} if no frontmatter present."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    _, fm_block, body = parts
    meta: dict = {}
    for raw_line in fm_block.strip().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise LoaderError(f"frontmatter line missing ':' → {raw_line!r}")
        key, val = line.split(":", 1)
        meta[key.strip()] = _coerce(val)
    return meta, body.lstrip("\n")


# ── validation ───────────────────────────────────────────────────────────

REQUIRED_FIELDS = ("id", "kind", "title")


def _validate(meta: dict, body: str, source: Path) -> None:
    for f in REQUIRED_FIELDS:
        if f not in meta or meta[f] in ("", None):
            raise LoaderError(
                f"{source}: missing required frontmatter field '{f}'"
            )
    if meta["kind"] not in VALID_KINDS:
        raise LoaderError(
            f"{source}: kind must be one of {sorted(VALID_KINDS)}, "
            f"got {meta['kind']!r}"
        )
    if not body.strip():
        raise LoaderError(f"{source}: body is empty")
    tags = meta.get("tags", [])
    if not isinstance(tags, list):
        raise LoaderError(f"{source}: 'tags' must be a list, got {type(tags).__name__}")
    ai = meta.get("always_include", False)
    if not isinstance(ai, bool):
        raise LoaderError(f"{source}: 'always_include' must be true/false")
    pr = meta.get("priority", 50)
    if not isinstance(pr, int):
        raise LoaderError(f"{source}: 'priority' must be an integer")


# ── discovery ────────────────────────────────────────────────────────────

def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def load_prompts(prompts_dir: Path) -> list[Prompt]:
    """Discover all .md under prompts_dir, parse, validate, dedup ids."""
    prompts_dir = Path(prompts_dir)
    if not prompts_dir.exists():
        raise LoaderError(f"prompts_dir does not exist: {prompts_dir}")

    out: list[Prompt] = []
    seen_ids: dict[str, Path] = {}

    for path in sorted(prompts_dir.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text)
        if not meta:
            raise LoaderError(f"{path}: missing frontmatter")
        _validate(meta, body, path)

        pid = meta["id"]
        if pid in seen_ids:
            raise LoaderError(
                f"duplicate prompt id {pid!r}: {seen_ids[pid]} and {path}"
            )
        seen_ids[pid] = path

        out.append(Prompt(
            id             = pid,
            kind           = meta["kind"],
            title          = meta["title"],
            body           = body.strip(),
            tags           = list(meta.get("tags") or []),
            always_include = bool(meta.get("always_include", False)),
            priority       = int(meta.get("priority", 50)),
            path           = path,
            content_hash   = _hash(text),
        ))
    return out
