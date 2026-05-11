"""JS preprocessing — deobfuscate + prettify for files without source maps."""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

_UA = "tlx-preprocess/0.1"
_DEOBF_TIMEOUT = 120
_PRETTIER_TIMEOUT = 30


def _is_minified(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    lines = text.splitlines()
    if not lines:
        return False
    avg_len = len(text) / len(lines)
    return avg_len > 300 or (len(lines) == 1 and len(text) > 5000)


def _run_webcrack(
    js_path: Path, output_path: Path
) -> tuple[bool, Path | None]:
    wrapper = (
        Path(__file__).resolve().parent.parent / "deobfuscate_wrapper.js"
    )
    node = shutil.which("node")
    if not node or not wrapper.exists():
        shutil.copy2(js_path, output_path)
        return False, None

    try:
        r = subprocess.run(
            [node, str(wrapper), str(js_path), str(output_path)],
            capture_output=True,
            text=True,
            timeout=_DEOBF_TIMEOUT,
        )
        map_path = output_path.with_suffix(".js.map")
        if r.returncode == 0 and output_path.exists():
            return True, map_path if map_path.exists() else None
    except subprocess.TimeoutExpired:
        pass
    except Exception:
        pass

    shutil.copy2(js_path, output_path)
    return False, None


def _run_prettier(js_path: Path, output_path: Path) -> bool:
    node = shutil.which("node")

    prettier = shutil.which("prettier")
    if prettier:
        try:
            r = subprocess.run(
                [prettier, "--parser", "babel", "--write", str(js_path)],
                capture_output=True,
                text=True,
                timeout=_PRETTIER_TIMEOUT,
            )
            if r.returncode == 0:
                shutil.copy2(js_path, output_path)
                return True
        except Exception:
            pass

    if node:
        try:
            r = subprocess.run(
                [
                    "npx", "--yes", "prettier", "--parser", "babel",
                    str(js_path), "--write",
                ],
                capture_output=True,
                text=True,
                timeout=_PRETTIER_TIMEOUT + 30,
            )
            if r.returncode == 0:
                shutil.copy2(js_path, output_path)
                return True
        except Exception:
            pass

    jsb = shutil.which("js-beautify")
    if jsb:
        try:
            r = subprocess.run(
                [jsb, str(js_path), "-o", str(output_path)],
                capture_output=True,
                text=True,
                timeout=_PRETTIER_TIMEOUT,
            )
            if r.returncode == 0:
                return True
        except Exception:
            pass

    shutil.copy2(js_path, output_path)
    return False


def preprocess_js(
    js_path: str,
    output_dir: str,
) -> dict:
    src = Path(js_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    result: dict = {
        "original": str(src),
        "processed": str(src),
        "method": "passthrough",
        "map_path": None,
        "was_minified": False,
        "line_count_before": 0,
        "line_count_after": 0,
        "error": None,
    }

    try:
        original_text = src.read_text(encoding="utf-8", errors="ignore")
    except OSError as e:
        result["error"] = str(e)
        return result

    lines_before = len(original_text.splitlines())
    result["line_count_before"] = lines_before
    result["was_minified"] = _is_minified(src)

    if not result["was_minified"]:
        result["line_count_after"] = lines_before
        return result

    with tempfile.TemporaryDirectory(prefix="tlx_preprocess_") as tmpdir:
        tmp = Path(tmpdir)
        deobf_path = tmp / src.name

        deobf_ok, map_path = _run_webcrack(src, deobf_path)

        pretty_path = out_dir / f"{src.stem}.pretty.js"
        _run_prettier(deobf_path, pretty_path)

        try:
            lines_after = len(
                pretty_path.read_text(
                    encoding="utf-8", errors="ignore"
                ).splitlines()
            )
        except OSError:
            lines_after = 0

        if map_path and map_path.exists():
            final_map = out_dir / map_path.name
            shutil.copy2(map_path, final_map)
            result["map_path"] = str(final_map)

        result["processed"] = str(pretty_path)
        result["line_count_after"] = lines_after
        result["method"] = "webcrack+prettier" if deobf_ok else "prettier"

    return result
