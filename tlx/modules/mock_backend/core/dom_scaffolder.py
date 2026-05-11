"""Build a deterministic host HTML document from a js_analyzer callgraph.

Output is a complete HTML5 document containing framework mount points,
elements for getElementById/querySelector targets, a synthetic form, and
script tags pointing to /static/<entry>.js for detected entry files.

Element ordering is sorted lexically so tests can assert exact content.
"""
from __future__ import annotations

import html
import json
import re
from collections import OrderedDict
from pathlib import Path
from typing import Any

_GETBYID_RE = re.compile(
    r"""getElementById\s*\(\s*['"`]([^'"`]+)['"`]\s*\)"""
)
_QUERY_SEL_RE = re.compile(
    r"""querySelector(?:All)?\s*\(\s*['"`]([^'"`]+)['"`]\s*\)"""
)
_FORM_HINTS_RE = re.compile(
    r"""\b(?:document\.forms|FormData\s*\(|\bform\.submit\s*\()"""
)


_FRAMEWORKS_FROM_IMPORTS = {
    "react": "react",
    "react-dom": "react",
    "next": "react",
    "vue": "vue",
    "@vue/core": "vue",
    "nuxt": "vue",
    "@angular/core": "angular",
    "@angular/common": "angular",
}


def _detect_frameworks(cg: Any) -> set[str]:
    """Read import_edges and node_tags to detect framework presence.

    The callgraph stores `import_edges.source_module` for every JS import
    seen during indexing — we map known package names to a coarse tag set.
    """
    out: set[str] = set()
    if cg is None or not hasattr(cg, "conn"):
        return out
    try:
        rows = cg.conn.execute(
            "SELECT DISTINCT source_module FROM import_edges"
        ).fetchall()
    except Exception:
        rows = []
    for r in rows:
        mod = (r[0] or "").strip()
        if not mod:
            continue
        tag = _FRAMEWORKS_FROM_IMPORTS.get(mod)
        if tag:
            out.add(tag)
        # Sub-imports like `@angular/core/testing` should still match.
        for prefix, t in _FRAMEWORKS_FROM_IMPORTS.items():
            if mod == prefix or mod.startswith(prefix + "/"):
                out.add(t)
    # Tags persisted by template_analyzer also indicate framework presence.
    try:
        tag_ids = cg.conn.execute(
            "SELECT DISTINCT taxonomy_id FROM node_tags"
        ).fetchall()
    except Exception:
        tag_ids = []
    for r in tag_ids:
        tid = r[0] or ""
        if tid.startswith("angular_"):
            out.add("angular")
        elif tid.startswith("vue_"):
            out.add("vue")
        elif tid == "dangerouslySetInnerHTML":
            out.add("react")
    return out


def _collect_element_ids(cg: Any, project_root: Path) -> tuple[set[str], set[str], set[str], bool]:
    """Walk source files for getElementById / querySelector / form hints.

    Returns (ids, classes, tags, has_form).
    """
    ids: set[str] = set()
    classes: set[str] = set()
    tags: set[str] = set()
    has_form = False

    files = _project_js_files(cg, project_root)

    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in _GETBYID_RE.finditer(text):
            ids.add(m.group(1))
        for m in _QUERY_SEL_RE.finditer(text):
            sel = m.group(1).strip()
            if not sel:
                continue
            if sel.startswith("#"):
                ids.add(sel[1:])
            elif sel.startswith("."):
                classes.add(sel[1:])
            elif re.match(r"^[a-zA-Z][a-zA-Z0-9-]*$", sel):
                tags.add(sel.lower())
        if not has_form and _FORM_HINTS_RE.search(text):
            has_form = True

    return ids, classes, tags, has_form


def _project_js_files(cg: Any, project_root: Path) -> list[Path]:
    """Resolve indexed files (from cg.nodes.file) to absolute paths."""
    if cg is None or not hasattr(cg, "conn"):
        return []
    try:
        rows = cg.conn.execute(
            "SELECT DISTINCT file FROM nodes "
            "WHERE file IS NOT NULL AND file != ''"
        ).fetchall()
    except Exception:
        return []
    out: list[Path] = []
    for r in rows:
        rel = r[0]
        p = Path(rel)
        if not p.is_absolute():
            p = project_root / rel
        if p.is_file():
            out.append(p)
    return out


def _detect_entries(cg: Any, project_root: Path) -> list[str]:
    """Pick entry-script filenames to wire as <script src='/static/X.js'>.

    Sources, in order of preference:
    1. package.json `main` and (for parity with bundlers) `module`/`browser`.
    2. Top-level .js files at project root (depth = 1).

    Returns a list of basename-only filenames (e.g. ['index.js', 'app.js']),
    sorted alphabetically and deduplicated.
    """
    out: set[str] = set()
    pkg = project_root / "package.json"
    if pkg.is_file():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8", errors="replace"))
        except (OSError, json.JSONDecodeError):
            data = {}
        for key in ("main", "module", "browser"):
            val = data.get(key) if isinstance(data, dict) else None
            if isinstance(val, str) and val:
                out.add(Path(val).name)

    if project_root.is_dir():
        for p in sorted(project_root.iterdir()):
            if p.is_file() and p.suffix == ".js":
                out.add(p.name)

    return sorted(out)


def _mount_points(frameworks: set[str]) -> list[str]:
    """Emit framework-specific mount nodes."""
    nodes: list[str] = []
    if "react" in frameworks:
        nodes.append('<div id="root"></div>')
    if "vue" in frameworks:
        nodes.append('<div id="app"></div>')
    if "angular" in frameworks:
        nodes.append("<app-root></app-root>")
    return nodes


_BEACON_SCRIPT = (
    "<script>"
    "window.__tlxBeacon = function(token) {"
    " console.log('TLX_BEACON:' + token);"
    "};"
    "</script>"
)


def build_host_html(cg: Any, project_root: Path) -> str:
    """Produce a single deterministic HTML5 document for browser hosting."""
    project_root = Path(project_root).expanduser().resolve() if project_root else Path.cwd()

    frameworks = _detect_frameworks(cg)
    ids, classes, tags, has_form = _collect_element_ids(cg, project_root)
    entries = _detect_entries(cg, project_root)

    # Build body content in deterministic order.
    body_parts: list[str] = []
    body_parts.extend(_mount_points(frameworks))

    # Framework tag (e.g. <app-root>) implies an id by convention; skip dup.
    used_ids = set()
    if "react" in frameworks:
        used_ids.add("root")
    if "vue" in frameworks:
        used_ids.add("app")

    for elem_id in sorted(ids):
        if elem_id in used_ids:
            continue
        body_parts.append(f'<div id="{html.escape(elem_id, quote=True)}"></div>')
        used_ids.add(elem_id)

    for cls in sorted(classes):
        body_parts.append(f'<div class="{html.escape(cls, quote=True)}"></div>')

    used_tags = {"app-root"} if "angular" in frameworks else set()
    for tg in sorted(tags):
        if tg in used_tags or tg in {"div", "span", "html", "body", "head"}:
            continue
        body_parts.append(f"<{tg}></{tg}>")
        used_tags.add(tg)

    if has_form:
        body_parts.append(
            '<form id="tlx-form">'
            '<input type="text" name="name">'
            '<input type="email" name="email">'
            '<input type="password" name="password">'
            '<input type="text" name="search">'
            '<button type="submit">Submit</button>'
            "</form>"
        )

    for entry in entries:
        body_parts.append(f'<script src="/static/{html.escape(entry, quote=True)}"></script>')

    body_parts.append(_BEACON_SCRIPT)

    body = "\n  ".join(body_parts)
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        "  <title>tlx mock_backend</title>\n"
        "</head>\n"
        "<body>\n"
        f"  {body}\n"
        "</body>\n"
        "</html>\n"
    )


# Re-export ordered dict for tests that want predictable structure.
_ = OrderedDict
