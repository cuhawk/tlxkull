"""Source map remapper — converts deobfuscated line numbers to original.

Supports source map v3 format. Uses the `sourcemap` PyPI package when
available; falls back to an inline Base64 VLQ decoder (stdlib only).

Usage:
    remapper = SourceMapRemapper(Path("output.js.map"))
    orig = remapper.remap(generated_line=14, generated_col=0)
    # → {"file": "src/app.js", "line": 847, "col": 0}
    # → {"file": None, "line": 14, "col": 0}  ← when unavailable
"""

import json
from pathlib import Path

# Base64 alphabet used by VLQ
_B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
_B64_MAP = {c: i for i, c in enumerate(_B64)}
_VLQ_BASE = 32          # 2^5
_VLQ_CONTINUATION = 32  # bit 5 set


def _decode_vlq(text: str, pos: int) -> tuple[int, int]:
    """Decode one Base64-VLQ integer starting at pos.
    Returns (value, new_pos)."""
    result = 0
    shift = 0
    while True:
        if pos >= len(text):
            raise ValueError(f"Unexpected end of VLQ at pos {pos}")
        digit = _B64_MAP.get(text[pos], -1)
        if digit < 0:
            raise ValueError(f"Invalid Base64 char {text[pos]!r} at pos {pos}")
        pos += 1
        has_continuation = digit & _VLQ_CONTINUATION
        digit &= _VLQ_CONTINUATION - 1   # lower 5 bits
        result |= digit << shift
        shift += 5
        if not has_continuation:
            break
    # LSB of result is the sign bit
    if result & 1:
        return -(result >> 1), pos
    return result >> 1, pos


def _parse_mappings(mappings: str, sources: list) -> dict:
    """Parse the mappings field into {generated_line: (source_file, original_line)}.

    generated_line is 1-indexed. Only records the first segment per line
    (sufficient for line-level remapping of function start/end).
    Uses running state across segments as required by the spec.
    """
    line_map: dict = {}
    generated_line = 1   # 1-indexed for consistency with node line numbers
    # Running state (carry across segments within and across lines)
    source_idx = 0
    original_line = 0    # 0-indexed per spec
    original_col = 0

    for line_str in mappings.split(";"):
        if line_str:
            raw = line_str
            i = 0
            while i < len(raw):
                # Skip commas
                if raw[i] == ",":
                    i += 1
                    continue
                # Decode up to 5 VLQ fields per segment
                fields: list = []
                try:
                    j = i
                    while j < len(raw) and raw[j] != "," and len(fields) < 5:
                        v, j = _decode_vlq(raw, j)
                        fields.append(v)
                    i = j
                except ValueError:
                    break

                # 4-field segment: generated_col, source_idx_delta,
                #                  original_line_delta, original_col_delta
                if len(fields) >= 4:
                    source_idx    += fields[1]
                    original_line += fields[2]
                    original_col  += fields[3]
                    # Record first segment for this line only
                    if generated_line not in line_map:
                        src_file = (sources[source_idx]
                                    if 0 <= source_idx < len(sources) else None)
                        line_map[generated_line] = (src_file, original_line + 1)  # 1-indexed

        generated_line += 1

    return line_map


class SourceMapRemapper:
    """Load a v3 source map and remap generated line → original (file, line).

    Falls back gracefully: if no map is available or parsing fails,
    remap() returns the input line unchanged with file=None.
    """

    def __init__(self, map_path):
        self.available = False
        self._line_map: dict = {}
        self._sm = None   # sourcemap package object if available

        if map_path is None:
            return
        map_path = Path(map_path)
        if not map_path.exists():
            return
        self._load(map_path)

    def _load(self, map_path: Path) -> None:
        # Try PyPI sourcemap package first (more robust). Guard against
        # importing this very module — its name clashes with the PyPI one.
        try:
            import sourcemap as sm_lib
            if (hasattr(sm_lib, "loads")
                    and getattr(sm_lib, "__file__", "") != __file__):
                self._sm = sm_lib.loads(map_path.read_text(encoding="utf-8"))
                self.available = True
                return
        except Exception:
            pass

        # Inline VLQ fallback
        try:
            data = json.loads(map_path.read_text(encoding="utf-8"))
            if data.get("version") != 3:
                return
            sources = data.get("sources") or []
            mappings = data.get("mappings", "")
            self._line_map = _parse_mappings(mappings, sources)
            self.available = bool(self._line_map)
        except Exception:
            pass

    def remap(self, generated_line: int, generated_col: int = 0) -> dict:
        """Return original position for a generated line/col.

        Returns:
            {"file": str|None, "line": int, "col": int}
        On any failure returns {"file": None, "line": generated_line, "col": generated_col}.
        """
        if not self.available:
            return {"file": None, "line": generated_line, "col": generated_col}

        try:
            if self._sm is not None:
                token = self._sm.lookup(generated_line - 1, generated_col)
                return {
                    "file": token.src,
                    "line": token.src_line + 1,
                    "col":  token.src_col,
                }
        except Exception:
            pass

        entry = self._line_map.get(generated_line)
        if entry:
            return {"file": entry[0], "line": entry[1], "col": 0}

        return {"file": None, "line": generated_line, "col": generated_col}
