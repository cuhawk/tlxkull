"""Node + Babel AST extractor bridge. Falls back gracefully when Node missing."""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import structlog

from modules.js_analyzer.sourcemap import SourceMapRemapper

logger = structlog.get_logger(__name__)


AST_SCRIPT_NAME    = "ast_extractor.js"
AST_DEOBF_NAME     = "deobfuscate_wrapper.js"
AST_PACKAGE_NAME   = "package.json"
AST_MAX_FILE_BYTES = 5_000_000      # files above this use regex fallback
AST_BATCH_SIZE     = 100            # files per Node subprocess invocation
AST_TIMEOUT_SEC    = 300
AST_DEOBF_TIMEOUT  = 120            # per-file webcrack budget


class ASTExtractor:
    """Bridge to a Node.js subprocess running Babel parser.

    Expects ast_extractor.js and package.json next to main.py. On first use,
    if node_modules is missing, runs `npm install` automatically. Any failure
    (Node not found, install fails, subprocess crash) flips `self.ready` off
    and the caller falls back to regex-based chunking — no hard dependency."""

    def __init__(self, disabled: bool = False, deobfuscate: bool = False):
        self.script_dir   = Path(__file__).parent.resolve()
        self.script       = self.script_dir / AST_SCRIPT_NAME
        self.deobf_script = self.script_dir / AST_DEOBF_NAME
        self.pkg          = self.script_dir / AST_PACKAGE_NAME
        self.node_modules = self.script_dir / "node_modules"
        self.node         = shutil.which("node")
        self.npm          = shutil.which("npm")
        self.ready        = False
        self.reason       = None
        self.deobfuscate  = deobfuscate
        self.artifacts_dir = self.script_dir / "output" / "deobfuscated"
        # Framework tags forwarded to ast_extractor.js as a 4th positional arg.
        # `node` is always implied — extractor seeds it when missing.
        self.frameworks: frozenset[str] = frozenset({"node"})

        if disabled:
            self.reason = "disabled via --no-ast"
            return
        self._setup()

    def set_frameworks(self, tags) -> None:
        """Update the framework tags forwarded to the AST extractor."""
        cleaned = {str(t).strip() for t in (tags or ()) if str(t).strip()}
        if not cleaned:
            cleaned = {"node"}
        cleaned.add("node")
        self.frameworks = frozenset(cleaned)

    def _setup(self):
        if not self.node:
            self.reason = "node not in PATH"
            return
        if not self.script.exists():
            self.reason = f"{AST_SCRIPT_NAME} not found next to main.py"
            return

        babel_parser = self.node_modules / "@babel" / "parser"
        if not babel_parser.exists():
            if not (self.npm and self.pkg.exists()):
                self.reason = "npm or package.json missing, cannot install babel"
                return
            logger.info("ast_npm_install", path=str(self.script_dir))
            try:
                r = subprocess.run(
                    [self.npm, "install", "--silent", "--no-audit", "--no-fund"],
                    cwd=str(self.script_dir),
                    capture_output=True, text=True, timeout=300,
                )
                if r.returncode != 0:
                    self.reason = f"npm install failed (exit {r.returncode})"
                    logger.warning(
                        "ast_npm_install_failed",
                        reason=self.reason,
                        stderr=r.stderr[:200],
                    )
                    return
            except subprocess.TimeoutExpired:
                self.reason = "npm install timed out after 5min"
                return
            except Exception as e:
                self.reason = f"npm install error: {e}"
                return

        self.ready = True

    def extract(self, files: list) -> dict:
        """files: list of {'abs': str, 'rel': str}.
        Returns {rel: {'ok': bool, 'functions': list} | {'ok': False, 'error': str}}.
        Oversized files (> AST_MAX_FILE_BYTES) are silently omitted so the
        caller falls through to its regex fallback for them."""
        if not self.ready or not files:
            return {}

        candidates = []
        oversized  = []
        for entry in files:
            try:
                size = Path(entry["abs"]).stat().st_size
            except Exception:
                continue
            if size > AST_MAX_FILE_BYTES:
                oversized.append(entry["rel"])
                continue
            candidates.append(entry)

        if oversized:
            logger.info(
                "ast_oversized_fallback",
                count=len(oversized),
                threshold_mb=AST_MAX_FILE_BYTES // 1_000_000,
            )

        deobf_dir = None
        if self.deobfuscate and candidates:
            candidates, deobf_dir = self._deobfuscate_batch(candidates)

        # Build rel → map_path index before the tmpdir is cleaned up
        map_by_rel: dict = {}
        if self.deobfuscate:
            for entry in candidates:
                raw_map = entry.get("map")
                map_by_rel[entry["rel"]] = Path(raw_map) if raw_map else None

        results = {}
        try:
            for i in range(0, len(candidates), AST_BATCH_SIZE):
                batch = candidates[i:i + AST_BATCH_SIZE]
                results.update(self._run_batch(batch))

            # Remap line numbers while map files still exist in deobf_dir
            if self.deobfuscate and map_by_rel:
                results = self._apply_remapping(results, map_by_rel)
        finally:
            if deobf_dir is not None:
                shutil.rmtree(deobf_dir, ignore_errors=True)
        return results

    def _apply_remapping(
        self,
        results: dict,
        map_by_rel: dict,
    ) -> dict:
        """Apply source-map line remapping to AST extraction results.

        For each rel path that has an associated .map file, creates a
        SourceMapRemapper and updates fn["original_line"] and fn["original_file"]
        on every function node. Falls back silently per file if map missing/invalid.
        """
        for rel, entry in results.items():
            map_path = map_by_rel.get(rel)
            if not map_path:
                continue
            if not isinstance(entry, dict) or not entry.get("ok"):
                continue

            remapper = SourceMapRemapper(map_path)
            if not remapper.available:
                continue

            for fn in entry.get("functions", []) or []:
                if not isinstance(fn, dict):
                    continue
                start = fn.get("start")
                if start:
                    orig = remapper.remap(start)
                    fn["original_line"] = orig["line"]
                    fn["original_file"] = orig["file"]   # may be None

        return results

    def _deobfuscate_batch(self, candidates: list) -> tuple:
        """Run webcrack on each candidate. Return (rewritten_list, tmpdir).

        On per-file failure the wrapper writes the original source as fallback,
        so extraction proceeds either way. Deobfuscated source is also copied
        to the artifacts directory for inspection.
        """
        if not self.deobf_script.exists():
            logger.warning(
                "ast_deobf_script_missing",
                script=AST_DEOBF_NAME,
            )
            return candidates, None

        deobf_dir = Path(tempfile.mkdtemp(prefix="gem_deobf_"))
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        rewritten = []
        ok_count = 0
        fail_count = 0

        for i, entry in enumerate(candidates):
            abs_path  = Path(entry["abs"])
            deobf_path = deobf_dir / f"{i}_{abs_path.name}"
            try:
                assert self.node is not None
                r = subprocess.run(
                    [self.node, str(self.deobf_script),
                     str(abs_path), str(deobf_path)],
                    capture_output=True, text=True,
                    timeout=AST_DEOBF_TIMEOUT,
                )
                if r.returncode == 0 and deobf_path.exists():
                    ok_count += 1
                    artifact = self.artifacts_dir / f"{abs_path.name}.deobf.js"
                    try:
                        shutil.copy2(deobf_path, artifact)
                    except Exception:
                        pass
                else:
                    fail_count += 1
                    shutil.copy2(abs_path, deobf_path)
            except subprocess.TimeoutExpired:
                fail_count += 1
                logger.warning("ast_webcrack_timeout", file=abs_path.name)
                shutil.copy2(abs_path, deobf_path)
                r = None
            except Exception as e:
                fail_count += 1
                logger.warning(
                    "ast_webcrack_error",
                    file=abs_path.name,
                    error=str(e),
                )
                shutil.copy2(abs_path, deobf_path)
                r = None

            # Parse map path from stderr — wrapper emits "sourcemap: <path>" or "sourcemap: none"
            map_path = None
            stderr = (r.stderr if r is not None else "") or ""
            for line in stderr.splitlines():
                if line.startswith("sourcemap: ") and not line.endswith("none"):
                    candidate = Path(line[len("sourcemap: "):].strip())
                    if candidate.exists():
                        map_path = candidate
                    break

            rewritten.append({
                "abs":     str(deobf_path),
                "rel":     entry["rel"],
                "map":     str(map_path) if map_path else None,
            })

        logger.info("ast_webcrack_done", ok=ok_count, fallback=fail_count)
        return rewritten, deobf_dir

    def _run_batch(self, batch: list) -> dict:
        in_fd,  in_path  = tempfile.mkstemp(suffix=".json", prefix="gem_ast_in_")
        out_fd, out_path = tempfile.mkstemp(suffix=".json", prefix="gem_ast_out_")
        os.close(in_fd)
        os.close(out_fd)

        try:
            with open(in_path, "w", encoding="utf-8") as f:
                json.dump(batch, f)

            fw_arg = ",".join(sorted(self.frameworks)) or "node"
            assert self.node is not None
            r = subprocess.run(
                [self.node, str(self.script), in_path, out_path, fw_arg],
                capture_output=True, text=True, timeout=AST_TIMEOUT_SEC,
            )
            if r.returncode != 0:
                logger.warning(
                    "ast_extractor_exit",
                    returncode=r.returncode,
                    stderr=r.stderr[:300],
                )
                return {}
            try:
                with open(out_path, encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning("ast_output_parse_failed", error=str(e))
                return {}
        except subprocess.TimeoutExpired:
            logger.warning("ast_batch_timeout")
            return {}
        except Exception as e:
            logger.warning("ast_subprocess_error", error=str(e))
            return {}
        finally:
            for p in (in_path, out_path):
                try:
                    os.unlink(p)
                except Exception:
                    pass
