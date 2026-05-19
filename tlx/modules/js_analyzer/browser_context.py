"""Browser-context inference for a target.

Plan reference: plans/ARCHITECTURE_EVOLUTION.md §4.

Reads evidence from a target folder and emits
``targets/<name>/browser_context.json`` describing the runtime browser
context the sinks land in:

- CSP (parsed from captured response headers + ``<meta http-equiv>`` in
  any indexed HTML).
- Trusted Types policies (presence and policy bodies).
- Rendering model (SSR / CSR / hybrid) from framework detection plus
  filesystem fingerprints (``.next/``, ``__sapper__/``, ``svelte-kit``).
- Sandbox-iframe evidence (presence of ``<iframe sandbox=>`` in indexed
  HTML).

The output is pure metadata — consumed by ``sink_viability.compute()``
to multiply chain scores. Failure mode: missing inputs → empty
``BrowserContext`` (every factor defaults to 1.0).

This module has no MCP / network / LLM side effects. Pure file IO. Safe
to call from a skill driver or from a CLI tool.
"""
from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import asdict, dataclass, field
from pathlib import Path

__all__ = [
    "BrowserContext",
    "CSPDirectives",
    "TrustedTypesInfo",
    "RenderingInfo",
    "infer",
    "load",
    "save",
]

# ── Parsed CSP ────────────────────────────────────────────────────────────


@dataclass
class CSPDirectives:
    raw: str = ""
    default_src: list[str] = field(default_factory=list)
    script_src: list[str] = field(default_factory=list)
    style_src: list[str] = field(default_factory=list)
    connect_src: list[str] = field(default_factory=list)
    frame_src: list[str] = field(default_factory=list)
    trusted_types_required: bool = False
    trusted_types_directive: list[str] = field(default_factory=list)
    require_trusted_types_for: list[str] = field(default_factory=list)
    unsafe_inline_allowed: bool = False
    unsafe_eval_allowed: bool = False
    strict_dynamic: bool = False
    nonce_required: bool = False
    report_only: bool = False
    source: str = ""  # 'header' | 'meta' | ''
    # confidence: 1.0 when parsed from a real header, 0.7 from meta tag,
    # 0.4 when inferred indirectly.
    confidence: float = 0.0


@dataclass
class TrustedTypesInfo:
    enforced: bool = False       # CSP has require-trusted-types-for 'script'
    policies: list[str] = field(default_factory=list)   # named policies created in bundle
    has_default_policy: bool = False
    policy_evidence: list[dict] = field(default_factory=list)


@dataclass
class RenderingInfo:
    model: str = "csr"                 # 'csr' | 'ssr' | 'ssr_then_csr' | 'static'
    framework: str = ""
    hydration: bool = False
    evidence: list[str] = field(default_factory=list)


@dataclass
class BrowserContext:
    csp: CSPDirectives = field(default_factory=CSPDirectives)
    trusted_types: TrustedTypesInfo = field(default_factory=TrustedTypesInfo)
    rendering: RenderingInfo = field(default_factory=RenderingInfo)
    sandbox_iframes: list[dict] = field(default_factory=list)
    evidence_files: list[str] = field(default_factory=list)
    # Free-form notes consumed by viability scorer (e.g. presence of
    # known JSONP endpoints on the allowlisted origin).
    notes: list[str] = field(default_factory=list)
    schema_version: int = 1


# ── CSP parsing ───────────────────────────────────────────────────────────

_CSP_DIRECTIVE_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9-]*)\s+(.*)$")


def parse_csp(raw: str, *, report_only: bool = False, source: str = "") -> CSPDirectives:
    """Parse a Content-Security-Policy header value into a CSPDirectives.

    Tolerant — unknown directives are ignored. Multiple identical
    directives merge their sources.
    """
    out = CSPDirectives(raw=raw, report_only=report_only, source=source)
    if not raw:
        return out

    for clause in (c for c in raw.split(";") if c.strip()):
        m = _CSP_DIRECTIVE_RE.match(clause)
        if not m:
            continue
        directive, rest = m.group(1).lower(), m.group(2).strip()
        sources = [s for s in rest.split() if s]

        if directive == "default-src":
            out.default_src.extend(sources)
        elif directive == "script-src":
            out.script_src.extend(sources)
        elif directive == "style-src":
            out.style_src.extend(sources)
        elif directive == "connect-src":
            out.connect_src.extend(sources)
        elif directive == "frame-src":
            out.frame_src.extend(sources)
        elif directive == "trusted-types":
            out.trusted_types_directive.extend(sources)
            out.trusted_types_required = True
        elif directive == "require-trusted-types-for":
            out.require_trusted_types_for.extend(sources)
            if any(s.strip("'\"") == "script" for s in sources):
                out.trusted_types_required = True

    # Roll-up flags. script-src falls back to default-src per spec.
    effective_script = out.script_src or out.default_src
    effective_script_lower = [s.lower().strip("'\"") for s in effective_script]
    out.unsafe_inline_allowed = "unsafe-inline" in effective_script_lower
    out.unsafe_eval_allowed = "unsafe-eval" in effective_script_lower
    out.strict_dynamic = "strict-dynamic" in effective_script_lower
    out.nonce_required = any(s.startswith("'nonce-") for s in effective_script)

    out.confidence = 1.0 if source == "header" else 0.7 if source == "meta" else 0.4
    return out


_META_CSP_RE = re.compile(
    r"""<meta\s+[^>]*http-equiv\s*=\s*["']?Content-Security-Policy(?:-Report-Only)?["']?[^>]*content\s*=\s*["']([^"']+)["']""",
    re.IGNORECASE,
)


def extract_meta_csp(html: str) -> list[tuple[str, bool]]:
    """Return list of (raw_csp, report_only) from <meta http-equiv> tags."""
    out: list[tuple[str, bool]] = []
    for m in _META_CSP_RE.finditer(html):
        report_only = "Report-Only" in html[max(0, m.start() - 200):m.start() + 200]
        out.append((m.group(1), report_only))
    return out


# ── Response-header parsing ───────────────────────────────────────────────


def parse_response_headers_file(path: Path) -> list[CSPDirectives]:
    """Parse a flat ``Header: value`` text file or a JSON object of
    request→headers. Returns one CSPDirectives per CSP header found."""
    out: list[CSPDirectives] = []
    if not path.exists():
        return out
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return out

    # JSON map shape: { url: { headers: { ... } } } or just { headers: {} }
    try:
        obj = json.loads(text)
        out.extend(_csps_from_json(obj))
        return out
    except json.JSONDecodeError:
        pass

    # Flat header lines (one per line, "Name: Value")
    for line in text.splitlines():
        if ":" not in line:
            continue
        name, _, value = line.partition(":")
        name = name.strip().lower()
        value = value.strip()
        if name == "content-security-policy":
            out.append(parse_csp(value, report_only=False, source="header"))
        elif name == "content-security-policy-report-only":
            out.append(parse_csp(value, report_only=True, source="header"))
    return out


def _csps_from_json(obj) -> list[CSPDirectives]:
    found: list[CSPDirectives] = []
    if isinstance(obj, dict):
        # Search for a "headers" map at any depth (bounded).
        headers = obj.get("headers")
        if isinstance(headers, dict):
            for k, v in headers.items():
                if not isinstance(v, str):
                    continue
                kl = k.lower()
                if kl == "content-security-policy":
                    found.append(parse_csp(v, report_only=False, source="header"))
                elif kl == "content-security-policy-report-only":
                    found.append(parse_csp(v, report_only=True, source="header"))
        # Recurse one level into common child shapes.
        for v in obj.values():
            if isinstance(v, (dict, list)):
                found.extend(_csps_from_json(v))
    elif isinstance(obj, list):
        for item in obj:
            found.extend(_csps_from_json(item))
    return found


def merge_csps(csps: list[CSPDirectives]) -> CSPDirectives:
    """Pick the strictest CSP we observed.

    Heuristic: prefer header over meta, enforced over report-only, then
    by smallest script-src allowlist (proxies most-restrictive).
    """
    enforced = [c for c in csps if not c.report_only and c.raw]
    pool = enforced or [c for c in csps if c.raw]
    if not pool:
        return CSPDirectives()

    def score(c: CSPDirectives) -> tuple[int, int, int]:
        # Lower is stricter / more authoritative.
        source_pri = {"header": 0, "meta": 1, "": 2}.get(c.source, 2)
        # script-src 'none' wins over script-src 'self' wins over wildcard.
        script_set = {s.lower() for s in (c.script_src or c.default_src)}
        if "'none'" in script_set:
            permissiveness = 0
        elif "*" in script_set:
            permissiveness = 4
        elif c.unsafe_inline_allowed or c.unsafe_eval_allowed:
            permissiveness = 3
        else:
            permissiveness = len(script_set)
        # Trusted Types enforced wins.
        tt_pri = 0 if c.trusted_types_required else 1
        return (source_pri, permissiveness, tt_pri)

    pool.sort(key=score)
    return pool[0]


# ── Trusted Types policy inference from indexed bundle ───────────────────


def collect_trusted_types(conn: sqlite3.Connection | None) -> TrustedTypesInfo:
    """Look for ``trusted_types_create_policy`` tags in node_tags.

    The static taxonomy already tags every ``trustedTypes.createPolicy``
    call. We just count and pull the host files for evidence.
    """
    out = TrustedTypesInfo()
    if conn is None:
        return out
    try:
        rows = conn.execute(
            "SELECT n.qualified_name, n.file, t.line "
            "FROM node_tags t JOIN nodes n ON n.id = t.node_id "
            "WHERE t.taxonomy_id = 'trusted_types_create_policy' "
            "ORDER BY n.file, t.line"
        ).fetchall()
    except sqlite3.OperationalError:
        return out
    for qname, file, line in rows:
        out.policy_evidence.append({"qname": qname, "file": file, "line": line})
    out.policies = sorted({e["qname"].split("::")[-1] for e in out.policy_evidence})
    out.has_default_policy = "default" in out.policies
    return out


# ── Rendering / framework heuristics ─────────────────────────────────────


def infer_rendering(target_dir: Path, frameworks: list[str]) -> RenderingInfo:
    """Infer SSR vs CSR from framework set + filesystem markers."""
    out = RenderingInfo()
    fset = {f.lower() for f in frameworks}
    evidence: list[str] = []

    if "next" in fset or "nextjs" in fset:
        out.framework = "nextjs"
        out.model = "ssr_then_csr"
        out.hydration = True
        evidence.append("frameworks.json:nextjs")
    elif "nuxt" in fset:
        out.framework = "nuxt"
        out.model = "ssr_then_csr"
        out.hydration = True
        evidence.append("frameworks.json:nuxt")
    elif "svelte" in fset:
        out.framework = "svelte"
        out.model = "ssr_then_csr"
        out.hydration = True
        evidence.append("frameworks.json:svelte")
    elif "react" in fset:
        out.framework = "react"
        out.model = "csr"
        out.hydration = True
        evidence.append("frameworks.json:react")
    elif "vue" in fset:
        out.framework = "vue"
        out.model = "csr"
        out.hydration = True
        evidence.append("frameworks.json:vue")
    elif "angular" in fset:
        out.framework = "angular"
        out.model = "csr"
        out.hydration = True
        evidence.append("frameworks.json:angular")

    # Filesystem markers (cheap secondary evidence).
    for marker, label in (
        (".next", "fs:.next"),
        ("__sapper__", "fs:__sapper__"),
        (".nuxt", "fs:.nuxt"),
        ("svelte-kit", "fs:svelte-kit"),
    ):
        if (target_dir / "raw" / marker).exists() or (target_dir / marker).exists():
            evidence.append(label)

    out.evidence = evidence
    return out


# ── Iframe sandbox harvest ───────────────────────────────────────────────


_IFRAME_SANDBOX_RE = re.compile(
    r"<iframe\b[^>]*?\bsandbox\s*(?:=\s*[\"']([^\"']*)[\"'])?[^>]*>",
    re.IGNORECASE,
)


def collect_sandbox_iframes(html_paths: list[Path]) -> list[dict]:
    out: list[dict] = []
    for p in html_paths:
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for m in _IFRAME_SANDBOX_RE.finditer(txt):
            tokens = (m.group(1) or "").split()
            out.append({"file": str(p), "tokens": tokens, "raw": m.group(0)[:200]})
    return out


# ── Top-level driver ─────────────────────────────────────────────────────


def infer(
    target_dir: str | Path,
    *,
    db_path: str | Path | None = None,
    explicit_csp_header: str | None = None,
) -> BrowserContext:
    """Build a BrowserContext for ``target_dir``.

    Inputs scanned (all optional — missing inputs degrade gracefully):
      - ``target_dir/raw/_response_headers.txt`` or ``.json``
      - ``target_dir/raw/**/*.html`` (only top-level + index-shaped names
        — we don't open the whole crawl tree)
      - ``target_dir/index/frameworks.json``
      - ``target_dir/runtime/*/state.json`` (passive-listen evidence)
      - ``target_dir/db/js_analyzer.db`` (per-target snapshot) for
        Trusted Types tag evidence
    """
    target_dir = Path(target_dir)
    bctx = BrowserContext()
    csps: list[CSPDirectives] = []

    # 1. Explicit user-supplied CSP (e.g. captured manually).
    if explicit_csp_header:
        csps.append(parse_csp(explicit_csp_header, source="header"))
        bctx.evidence_files.append("<explicit-csp-arg>")

    # 2. Response-header dumps (Caido / passive-listen sinks).
    for hdr_name in ("_response_headers.txt", "_response_headers.json", "response_headers.json"):
        p = target_dir / "raw" / hdr_name
        if p.exists():
            found = parse_response_headers_file(p)
            csps.extend(found)
            if found:
                bctx.evidence_files.append(str(p.relative_to(target_dir)))

    # 3. Runtime / passive-listen state.json (one or more dated dirs).
    runtime_root = target_dir / "runtime"
    if runtime_root.exists():
        for state in sorted(runtime_root.glob("*/state.json")):
            try:
                state_obj = json.loads(state.read_text(encoding="utf-8"))
            except Exception:
                continue
            csps.extend(_csps_from_json(state_obj))
            bctx.evidence_files.append(str(state.relative_to(target_dir)))

    # 4. Meta CSP from indexed HTML (top-level + index*.html only — keep
    #    the scan cheap; deep crawl trees risk noise).
    html_paths = _candidate_html(target_dir)
    for p in html_paths:
        try:
            html = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for raw, report_only in extract_meta_csp(html):
            csps.append(parse_csp(raw, report_only=report_only, source="meta"))
            bctx.evidence_files.append(str(p.relative_to(target_dir)))

    bctx.csp = merge_csps(csps)

    # 5. Trusted Types policies (from per-target DB).
    conn = None
    db_p = Path(db_path) if db_path else target_dir / "db" / "js_analyzer.db"
    if db_p.exists():
        try:
            conn = sqlite3.connect(f"file:{db_p}?mode=ro", uri=True)
        except sqlite3.OperationalError:
            conn = None
    bctx.trusted_types = collect_trusted_types(conn)
    if conn is not None:
        conn.close()

    # Cross-link CSP enforcement → TT info. Report-only CSPs publish
    # violations but never block, so Trusted Types are not actually
    # enforced even though the directive parses.
    if bctx.csp.trusted_types_required and not bctx.csp.report_only:
        bctx.trusted_types.enforced = True

    # 6. Rendering / framework.
    frameworks: list[str] = []
    fjson = target_dir / "index" / "frameworks.json"
    if fjson.exists():
        try:
            frameworks = json.loads(fjson.read_text(encoding="utf-8"))
            if isinstance(frameworks, dict):
                frameworks = list(frameworks.get("frameworks") or frameworks.keys())
        except Exception:
            frameworks = []
    bctx.rendering = infer_rendering(target_dir, frameworks)

    # 7. Sandbox iframes (cheap scan).
    bctx.sandbox_iframes = collect_sandbox_iframes(html_paths)

    return bctx


def _candidate_html(target_dir: Path) -> list[Path]:
    """Return a bounded list of HTML files worth scanning.

    We deliberately skip ``raw/`` deep crawl artifacts and keep the
    surface small: top-level *.html / index*.html / app.html.
    """
    out: list[Path] = []
    for root in (target_dir, target_dir / "raw", target_dir / "sources"):
        if not root.exists():
            continue
        for name in ("index.html", "app.html", "main.html"):
            p = root / name
            if p.exists():
                out.append(p)
        # Top-level *.html only (no recursive glob).
        for p in root.glob("*.html"):
            if p not in out:
                out.append(p)
        if len(out) > 12:
            break
    return out[:12]


# ── persistence ──────────────────────────────────────────────────────────


def save(ctx: BrowserContext, target_dir: str | Path, *, filename: str = "browser_context.json") -> Path:
    out_path = Path(target_dir) / filename
    payload = asdict(ctx)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return out_path


def load(target_dir: str | Path, *, filename: str = "browser_context.json") -> BrowserContext:
    """Reload a previously-saved context, or return an empty one."""
    p = Path(target_dir) / filename
    if not p.exists():
        return BrowserContext()
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return BrowserContext()
    return _from_dict(raw)


def _from_dict(d: dict) -> BrowserContext:
    csp = d.get("csp", {}) or {}
    tt = d.get("trusted_types", {}) or {}
    rd = d.get("rendering", {}) or {}
    return BrowserContext(
        csp=CSPDirectives(**{k: v for k, v in csp.items() if k in CSPDirectives.__dataclass_fields__}),
        trusted_types=TrustedTypesInfo(**{k: v for k, v in tt.items() if k in TrustedTypesInfo.__dataclass_fields__}),
        rendering=RenderingInfo(**{k: v for k, v in rd.items() if k in RenderingInfo.__dataclass_fields__}),
        sandbox_iframes=d.get("sandbox_iframes") or [],
        evidence_files=d.get("evidence_files") or [],
        notes=d.get("notes") or [],
        schema_version=int(d.get("schema_version", 1)),
    )
