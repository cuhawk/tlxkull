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


# ─── Sanitizer-adequacy reasoning ────────────────────────────────────────
#
# Each sink ID is mapped to one or more taint flavors. Sanitizer entries
# in taxonomies/sanitizers.json carry a `clears` list of flavor categories.
# A sanitizer is "adequate" for a sink iff the intersection of the
# sanitizer's clears set and the sink's flavor set is non-empty.
#
# Flavor categories:
#   html         — HTML element body context (innerHTML, document.write, …)
#   attribute    — HTML attribute context (setAttribute on event/href/src)
#   url          — URL context (location.href, fetch URL, navigation)
#   code         — JavaScript-code context (eval, new Function, setTimeout str)
#   sqli         — SQL query construction
#   nosql        — NoSQL query (Mongo $where, etc.)
#   command      — shell / OS command (exec, spawn)
#   path         — filesystem path (fs.read, traversal)
#   open_redirect — navigation away to attacker-controlled URL
#   xxe          — XML parser fed user input
#   prototype    — prototype pollution gadget reach
#   ssrf         — server-side request forgery
SINK_FLAVOR_MAP: dict[str, tuple[str, ...]] = {
    # html / DOM XSS
    "innerHTML_assign":               ("html",),
    "outerHTML_assign":               ("html",),
    "srcdoc_assign":                  ("html",),
    "iframe_srcdoc_assign":           ("html",),
    "document_write":                 ("html",),
    "document_writeln":               ("html",),
    "insertAdjacentHTML_call":        ("html",),
    "dangerouslySetInnerHTML":        ("html",),
    "jquery_html":                    ("html",),
    "jquery_parseHTML":               ("html",),
    "jquery_append":                  ("html",),
    "jquery_before":                  ("html",),
    "jquery_after":                   ("html",),
    "jquery_prepend":                 ("html",),
    "jquery_replaceWith":             ("html",),
    "jquery_replaceAll":              ("html",),
    "jquery_wrap_family":             ("html",),
    "jquery_insertBefore_after":      ("html",),
    "angular_inner_html_binding":     ("html",),
    "angular_bypass_trust_html":      ("html",),
    "angular_legacy_trustAs":         ("html",),
    "angular_modern_bypassSecurityTrust": ("html",),
    "vue_compile":                    ("html",),
    "angular_compile":                ("html",),
    "vue_v_html_sink":                ("html",),
    "createContextualFragment":       ("html",),
    "trusted_types_create_policy":    ("html",),
    "dom_clobbering_or_fallback":     ("html",),
    # attribute XSS
    "event_handler_attr_assign":      ("attribute", "code"),
    "setAttribute_dangerous_attr":    ("attribute",),
    "setAttribute_dynamic_attr":      ("attribute",),
    "jquery_attr_dangerous":          ("attribute",),
    "jquery_selector_with_user_input": ("html",),
    # url / navigation
    "location_href_assign":           ("url", "open_redirect"),
    "location_assign_call":           ("url", "open_redirect"),
    "location_replace_call":          ("url", "open_redirect"),
    "location_bare_assign":           ("url", "open_redirect"),
    "frame_location_assign":          ("url", "open_redirect"),
    "window_navigate_legacy":         ("url", "open_redirect"),
    "window_open":                    ("url", "open_redirect"),
    "script_src_assign":              ("url", "code"),
    "script_text_assign":             ("code",),
    # code execution
    "eval_call":                      ("code",),
    "eval_indirect":                  ("code",),
    "new_Function":                   ("code",),
    "setTimeout_string":              ("code",),
    "setInterval_string":             ("code",),
    "setImmediate_string":            ("code",),
    "execScript_legacy":              ("code",),
    "vm_runIn_family":                ("code",),
    "vm_Script_ctor":                 ("code",),
    "require_dynamic":                ("code",),
    # network / SSRF
    "fetch_call":                     ("url", "ssrf"),
    "xhr_open_call":                  ("url", "ssrf"),
    "axios_call":                     ("url", "ssrf"),
    # backend
    "sql_injection_sink":             ("sqli",),
    "nosql_injection_sink":           ("nosql",),
    "path_traversal_sink":            ("path",),
    "child_process_exec":             ("command",),
    "child_process_exec_sink":        ("command",),
    "child_process_spawn_sink":       ("command",),
    "electron_shell_openexternal":    ("url", "command"),
    "electron_nodeintegration_sink":  ("code",),
    # prototype pollution gadgets
    "lodash_merge_set":               ("prototype",),
    "jquery_extend_deep":             ("prototype",),
    "object_setPrototypeOf":          ("prototype",),
    "reflect_setPrototypeOf":         ("prototype",),
    "computed_proto_assign":          ("prototype",),
    # misc
    "postMessage_send":               ("html", "code"),
    "document_domain_assign":         ("html",),
}


def infer_sink_flavor(sink_id: str) -> tuple[str, ...]:
    """Map a sink taxonomy_id to its taint flavor(s).

    Returns an empty tuple for unknown sinks (caller treats this as
    'unknown flavor' — sanitizer adequacy cannot be judged).
    """
    return SINK_FLAVOR_MAP.get(sink_id, ())


def parse_sanitizer_clears(clears_csv: str | list | None) -> tuple[str, ...]:
    """Normalize the sanitizer.clears field (CSV string OR list) to a tuple."""
    if clears_csv is None:
        return ()
    if isinstance(clears_csv, (list, tuple)):
        return tuple(str(c).strip() for c in clears_csv if str(c).strip())
    return tuple(c.strip() for c in str(clears_csv).split(",") if c.strip())


def sanitizer_covers_sink(
    sanitizer_clears: str | list | None,
    sink_id: str,
) -> tuple[bool, list[str]]:
    """Return (adequate, intersecting_flavors).

    A sanitizer is adequate for a sink iff its `clears` set intersects
    with the sink's inferred flavor set. Unknown sinks always return
    (False, []) — caller treats this as 'cannot judge adequacy'.
    """
    clears = set(parse_sanitizer_clears(sanitizer_clears))
    if not clears:
        return False, []
    flavors = set(infer_sink_flavor(sink_id))
    if not flavors:
        return False, []
    overlap = sorted(clears & flavors)
    return bool(overlap), overlap