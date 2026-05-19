"""Line-windowed snippet extraction for ChainIR.

Plan: plans/ARCHITECTURE_EVOLUTION.md §11.

Replaces whole-function snippets in the LLM payload. For each chain
hop we extract:

  * a window around the call site (default ±3 lines),
  * the source line for any source / sink / sanitizer landmark,
  * (optionally) the immediately-enclosing function header line so the
    LLM still knows scope.

Token impact: typical whole-function snippet is 50-200 lines; the
window is 7-15 lines per hop. For an 8-hop chain that's ~80 lines vs
~800-1600 — roughly a 10x reduction without losing the lines the
auditor needs.

Pure module — string slicing only. No DB. No LLM.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

__all__ = [
    "WindowSpec",
    "SnippetWindow",
    "extract_window",
    "extract_chain_windows",
]


@dataclass(frozen=True)
class WindowSpec:
    file: str
    landmark_line: int
    context_before: int = 3
    context_after: int = 5
    include_function_header: bool = True
    note: str = ""           # free-form label ("call_site", "source", "sink", "sanitizer")


@dataclass
class SnippetWindow:
    file: str
    note: str
    landmark_line: int
    start_line: int
    end_line: int
    header_line: int | None
    text: str

    def to_dict(self) -> dict:
        return asdict(self)


def _read_file_lines(path: str | Path) -> list[str] | None:
    p = Path(path)
    if not p.exists() or not p.is_file():
        return None
    try:
        return p.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return None


_FN_HEADER_PATTERNS = (
    "function ", "function(", "function*", "async function",
    "=> {", " => {", "class ", "constructor(",
)


def _find_function_header(lines: list[str], target_line: int) -> int | None:
    """Walk backward from ``target_line`` looking for the nearest function
    header / class block opener / lambda opener.

    Returns 1-based line number or ``None``.
    """
    idx = min(max(0, target_line - 1), len(lines) - 1)
    for i in range(idx, -1, -1):
        line = lines[i]
        stripped = line.lstrip()
        for pat in _FN_HEADER_PATTERNS:
            if pat in stripped:
                return i + 1
        # Bail if we run too far without finding anything.
        if (idx - i) > 80:
            break
    return None


def extract_window(spec: WindowSpec, *, source_root: str | Path | None = None) -> SnippetWindow | None:
    """Extract a single window around ``spec.landmark_line`` in ``spec.file``.

    ``source_root`` is prepended to relative file paths.
    """
    path = Path(spec.file)
    if not path.is_absolute() and source_root is not None:
        path = Path(source_root) / spec.file
    lines = _read_file_lines(path)
    if lines is None:
        return None
    if spec.landmark_line <= 0 or spec.landmark_line > len(lines):
        # Treat 0 as "first line" gracefully — at least surface something.
        lm = max(1, min(spec.landmark_line, len(lines))) if lines else 1
    else:
        lm = spec.landmark_line
    start = max(1, lm - spec.context_before)
    end = min(len(lines), lm + spec.context_after)
    header = _find_function_header(lines, lm) if spec.include_function_header else None
    body = []
    if header and header < start:
        body.append(f"{header:5d}: {lines[header - 1]}")
        if header + 1 < start:
            body.append("       ...")
    for i in range(start, end + 1):
        marker = ">>" if i == lm else "  "
        body.append(f"{i:5d}: {marker} {lines[i - 1]}")
    text = "\n".join(body)
    return SnippetWindow(
        file=str(path),
        note=spec.note,
        landmark_line=lm,
        start_line=start,
        end_line=end,
        header_line=header,
        text=text,
    )


def extract_chain_windows(
    *,
    source_landmark: tuple[str, int],
    sink_landmark: tuple[str, int],
    path_hops: list[tuple[str, int]],
    sanitizer_landmarks: list[tuple[str, int]] | None = None,
    source_root: str | Path | None = None,
    context_before: int = 3,
    context_after: int = 5,
) -> list[dict]:
    """Build the per-chain window bundle.

    Order: source → path hops in order → sanitizers (in path order) →
    sink. Duplicates collapsed by (file, landmark_line)."""
    specs: list[WindowSpec] = []
    seen: set[tuple[str, int]] = set()

    def _push(file: str, line: int, note: str):
        key = (file, line)
        if key in seen:
            return
        seen.add(key)
        specs.append(WindowSpec(
            file=file,
            landmark_line=line,
            context_before=context_before,
            context_after=context_after,
            note=note,
        ))

    if source_landmark:
        _push(source_landmark[0], source_landmark[1], "source")
    for i, (file, line) in enumerate(path_hops):
        _push(file, line, f"hop_{i}")
    for file, line in (sanitizer_landmarks or []):
        _push(file, line, "sanitizer")
    if sink_landmark:
        _push(sink_landmark[0], sink_landmark[1], "sink")

    out = []
    for spec in specs:
        w = extract_window(spec, source_root=source_root)
        if w is not None:
            out.append(w.to_dict())
    return out
