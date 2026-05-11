"""Sink/source taxonomy loader and matcher.

Loads JSON taxonomy files (taxonomies/sinks.json, taxonomies/sources.json),
compiles each entry's regex once, and exposes a matcher over arbitrary text
or a list of lines.

Layout note: this module sits flat in the project root (alongside callgraph.py)
to match the existing repo layout, not under gemini_agent/ as the spec
template suggests. Import path is just `from taxonomy import Taxonomy`.

Out of scope (later tasks): tagging call graph nodes with matches (Task 4),
source-to-sink flow analysis (Task 5).
"""

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

REQUIRED_FIELDS = ("id", "pattern", "kind", "severity", "description")
ALLOWED_KINDS      = {"sink", "source", "sanitizer"}
ALLOWED_SEVERITIES = {"low", "medium", "high", "critical"}


@dataclass
class Match:
    id: str
    kind: str
    severity: str
    description: str
    line: int          # absolute 1-based line; 0 when match() called on raw text
    line_offset: int   # 0-based char offset within the line/text
    span: tuple        # absolute (start, end) char span in input passed
    text: str          # matched substring

    def to_dict(self) -> dict:
        return asdict(self)


class Taxonomy:
    """Loaded taxonomy. Compiled regexes cached on init."""

    def __init__(self, sinks_path: str | Path, sources_path: str | Path):
        self.entries: list[dict] = []
        self._load(sinks_path)
        self._load(sources_path)

        ids = [e["id"] for e in self.entries]
        dupes = {x for x in ids if ids.count(x) > 1}
        if dupes:
            raise ValueError(f"duplicate taxonomy ids: {sorted(dupes)}")

    def _load(self, path: str | Path) -> None:
        path = Path(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError(f"{path}: expected JSON array")
        for i, e in enumerate(data):
            if not isinstance(e, dict):
                raise ValueError(f"{path}[{i}]: not an object")
            for f in REQUIRED_FIELDS:
                if f not in e:
                    raise ValueError(f"{path}[{i}]: missing field '{f}'")
            if e["kind"] not in ALLOWED_KINDS:
                raise ValueError(f"{path}[{i}]: bad kind '{e['kind']}'")
            if e["severity"] not in ALLOWED_SEVERITIES:
                raise ValueError(f"{path}[{i}]: bad severity '{e['severity']}'")
            try:
                e["_re"] = re.compile(e["pattern"])
            except re.error as err:
                raise ValueError(
                    f"{path}[{i}] id={e['id']}: regex compile error: {err}"
                )
            self.entries.append(e)

    # ── matcher API ──────────────────────────────────────────────────────

    def match(self, text: str) -> list[Match]:
        """Match against arbitrary text. line=0 (no line context)."""
        out = []
        for e in self.entries:
            for m in e["_re"].finditer(text):
                out.append(Match(
                    id=e["id"], kind=e["kind"], severity=e["severity"],
                    description=e["description"],
                    line=0, line_offset=m.start(),
                    span=(m.start(), m.end()), text=m.group(0),
                ))
        return out

    def match_lines(self, lines) -> list[Match]:
        """Match against a list of lines. Returns absolute 1-based line numbers."""
        out = []
        for i, line in enumerate(lines, start=1):
            for e in self.entries:
                for m in e["_re"].finditer(line):
                    out.append(Match(
                        id=e["id"], kind=e["kind"], severity=e["severity"],
                        description=e["description"],
                        line=i, line_offset=m.start(),
                        span=(m.start(), m.end()), text=m.group(0),
                    ))
        return out

    # ── introspection ────────────────────────────────────────────────────

    def ids(self) -> list[str]:
        return [e["id"] for e in self.entries]

    def by_kind(self, kind: str) -> list[dict]:
        return [e for e in self.entries if e["kind"] == kind]

def load_default(repo_root=None):
    root = Path(repo_root) if repo_root else Path(__file__).resolve().parent
    t = Taxonomy(
        root / "taxonomies" / "sinks.json",
        root / "taxonomies" / "sources.json",
    )
    for extra in sorted((root / "taxonomies").glob("extra_*.json")):
        t._load(extra)
    san = root / "taxonomies" / "sanitizers.json"
    if san.exists():
        t._load(san)
    ids = [e["id"] for e in t.entries]
    dupes = {x for x in ids if ids.count(x) > 1}
    if dupes:
        raise ValueError(f"duplicate taxonomy ids after extras: {sorted(dupes)}")
    return t