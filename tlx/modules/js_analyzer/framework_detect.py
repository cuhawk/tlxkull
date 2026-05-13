"""Framework detection for the JS security scanner.

Inspects package.json (when present) and a list of source files to figure
out which JS framework / runtime tags apply. The result is a frozenset of
short string tags consumed by:

- ast_extractor.js (gates framework-specific AST visitors)
- callgraph.ACTIVE_FRAMEWORKS (gates regex tagging via taxonomy)
- template_analyzer.analyze_template (gates Vue / Angular template scans)

Tags are intentionally coarse:
    node, node_http, express, react, next, vue, nuxt, gatsby, remix,
    angular, svelte, electron, socketio, db, aws

`node` is always added — every JS runtime hosts it.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

PKG_TAG_MAP: dict[str, str] = {
    "express":          "express",
    "koa":              "node_http",
    "fastify":          "node_http",
    "hapi":             "node_http",
    "@hapi/hapi":       "node_http",
    "react":            "react",
    "react-dom":        "react",
    "next":             "next",
    "vue":              "vue",
    "@vue/core":        "vue",
    "@angular/core":    "angular",
    "nuxt":             "nuxt",
    "gatsby":           "gatsby",
    "remix":            "remix",
    "svelte":           "svelte",
    "electron":         "electron",
    "socket.io":        "socketio",
    "mongoose":         "db",
    "sequelize":        "db",
    "prisma":           "db",
    "pg":               "db",
    "mysql2":           "db",
    "better-sqlite3":   "db",
    "aws-sdk":          "aws",
}

PKG_IMPLIES: dict[str, set[str]] = {
    "next":   {"react"},
    "nuxt":   {"vue"},
    "gatsby": {"react"},
    "remix":  {"react"},
}

_NEXT_PATH_RE   = re.compile(r"(?:^|/)(?:pages|app)/.*\.(?:tsx|ts|jsx|js)$")
_EXPRESS_IMP_RE = re.compile(
    r"""(?:require\s*\(\s*['"]express['"]\s*\)|from\s+['"]express['"])""",
    re.MULTILINE,
)
_NGMODULE_RE    = re.compile(r"@NgModule\s*\(")
# Ivy/AOT runtime markers — prebuilt Angular bundles where @NgModule decorator
# is compiled away. Hits any of: ɵɵdefineNgModule, ɵɵdefineComponent,
# ɵɵdefineDirective, ɵɵdefineInjectable, bootstrapApplication, NG_PROV.
_NG_IVY_RE      = re.compile(
    r"ɵɵ(?:defineNgModule|defineComponent|defineDirective|defineInjectable|definePipe|defineInjector)"
    r"|\bbootstrapApplication\s*\("
    r"|\bplatformBrowser(?:Dynamic)?\s*\("
)
_VUE_DEFINE_RE  = re.compile(r"\bdefineComponent\s*\(")
_VUE_TEMPLATE_RE = re.compile(r"<template[\s>]")
# Browser-DOM marker — anything that touches window/document/location at module
# scope or via clearly browser-only globals. Used to force `browser` tag so the
# DOM XSS taxonomy fires on framework-free or compiled-away bundles.
_BROWSER_RE     = re.compile(
    r"\b(?:window\.|document\.|location\.|history\.pushState|XMLHttpRequest"
    r"|HTMLElement\b|customElements\.|navigator\.userAgent)"
)
# React markers — hooks and JSX runtime entry points. Catches prod bundles
# where the `react` import name is preserved-and-mangled but hooks survive.
_REACT_RE       = re.compile(
    r"\b(?:useState|useEffect|useRef|useMemo|useCallback|useReducer|useContext|useLayoutEffect)\s*\("
    r"|React\.createElement\s*\("
    r"|\bcreateRoot\s*\(\s*[a-zA-Z_$]"
    r"|\bhydrateRoot\s*\("
    r"|\bjsx\(s?\)?\s*\("
)
_VUE_CREATEAPP_RE = re.compile(r"\bcreateApp\s*\(")


def _scan_pkg_json(pkg_path: Path | str) -> set[str]:
    """Return tags discovered in a package.json. Always safe — never raises."""
    found: set[str] = set()
    try:
        path = Path(pkg_path)
        if not path.is_file():
            return found
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return found
    if not isinstance(data, dict):
        return found

    deps: dict[str, str] = {}
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        section = data.get(key)
        if isinstance(section, dict):
            for name in section:
                if isinstance(name, str):
                    deps[name] = section.get(name) or ""

    for name in deps:
        # Exact match first
        if name in PKG_TAG_MAP:
            found.add(PKG_TAG_MAP[name])
            continue
        # @aws-sdk/* family
        if name.startswith("@aws-sdk/"):
            found.add("aws")

    return found


def _scan_files(file_list: list[str] | None) -> set[str]:
    """Heuristic file-content + path checks. Reads files lazily."""
    found: set[str] = set()
    if not file_list:
        return found

    for entry in file_list:
        if not isinstance(entry, str):
            continue
        path = Path(entry)
        rel  = entry.replace("\\", "/")

        # Path-based heuristics — Next.js convention
        if _NEXT_PATH_RE.search(rel):
            found.add("next")

        suffix = path.suffix.lower()
        # Cheap content heuristics — only read text-like JS / TS / Vue / HTML
        if suffix not in (".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx",
                          ".vue", ".html"):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        if _EXPRESS_IMP_RE.search(text):
            found.add("express")
        if _NGMODULE_RE.search(text) or _NG_IVY_RE.search(text):
            found.add("angular")
        if suffix == ".vue":
            if _VUE_DEFINE_RE.search(text) or _VUE_TEMPLATE_RE.search(text):
                found.add("vue")
        elif _VUE_DEFINE_RE.search(text) or _VUE_CREATEAPP_RE.search(text):
            found.add("vue")
        if _REACT_RE.search(text):
            found.add("react")
        if _BROWSER_RE.search(text):
            found.add("browser")

    return found


def detect_frameworks(
    file_list: list[str] | None,
    pkg_json_path: str | Path | None = None,
) -> frozenset[str]:
    """Return frozenset of framework tags inferred from package.json + files.

    package.json takes priority — file heuristics fill gaps when no
    package.json is supplied or readable. `node` is always present.
    """
    tags: set[str] = {"node"}

    if pkg_json_path is not None:
        tags |= _scan_pkg_json(pkg_json_path)
    else:
        # Auto-locate package.json next to the first file, if any
        if file_list:
            for entry in file_list:
                try:
                    p = Path(entry).parent
                except Exception:
                    continue
                # Walk up a few levels looking for package.json
                for _ in range(6):
                    candidate = p / "package.json"
                    if candidate.is_file():
                        tags |= _scan_pkg_json(candidate)
                        break
                    if p.parent == p:
                        break
                    p = p.parent
                if "express" in tags or "next" in tags or "angular" in tags:
                    break

    tags |= _scan_files(file_list)

    # Apply implications (next → react, nuxt → vue, …)
    for tag in list(tags):
        for implied in PKG_IMPLIES.get(tag, ()):
            tags.add(implied)

    return frozenset(tags)
