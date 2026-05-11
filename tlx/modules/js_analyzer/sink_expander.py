"""LLM-powered sink taxonomy expander — Phase 12b.

Samples JS files from the target codebase, sends representative
code chunks to Claude Sonnet, and asks it to identify novel sink
patterns not already in the taxonomy. Validated entries are merged
into taxonomies/extra_sinks.json. Opt-in via EXPAND_SINKS=1.

CLI:
    python sink_expander.py --target <dir> [--dry-run] [--chunks N]

The module is also importable for use from main.py.
"""

import argparse
import json
import re
import sys
import warnings
from pathlib import Path

import anthropic
import structlog

ROOT = Path(__file__).resolve().parent
EXTRA_SINKS_PATH = ROOT / "taxonomies" / "extra_sinks.json"

from modules.js_analyzer.js_analyzer_config import (  # noqa: E402
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
)

logger = structlog.get_logger(__name__)

_EXPANDER_SYSTEM = """\
You are a JavaScript security researcher specialising in DOM XSS, prototype
pollution, and client-side injection sinks.

You will be shown representative JavaScript code chunks from a real codebase.
Identify any sink patterns — places where attacker-controlled data could reach
a dangerous API — that are NOT in the provided existing taxonomy.

Respond ONLY with a JSON array (no preamble, no markdown fences). Each entry:
{
  "id":          "snake_case_unique_id",
  "pattern":     "regex_string_matching_the_sink",
  "kind":        "sink",
  "severity":    "high" | "medium" | "low",
  "description": "One sentence describing the sink and the risk.",
  "cwe":         "CWE-NNN"
}

Rules:
- Only include patterns genuinely absent from the existing taxonomy.
- The regex must be a valid Python re pattern (tested with re.compile).
- Do not include sources, sanitisers, or informational patterns.
- If you find nothing new, respond with an empty array: []
- No markdown, no explanation outside the JSON array.
"""

_EXPANDER_USER_TEMPLATE = """\
Existing taxonomy IDs (do NOT reproduce these):
{existing_ids}

Code samples from the target codebase:
{code_chunks}

Identify any NEW sink patterns not in the existing taxonomy.
"""


def _load_existing_ids() -> set[str]:
    """Load all current sink IDs from sinks.json and extra_sinks.json."""
    ids = set()
    for fname in ("sinks.json", "extra_sinks.json"):
        path = ROOT / "taxonomies" / fname
        if path.exists():
            try:
                for entry in json.loads(path.read_text(encoding="utf-8")):
                    ids.add(entry.get("id", ""))
            except Exception:
                pass
    return ids


def sample_codebase(target_path: str, n_chunks: int = 20) -> str:
    """Sample JS file chunks from the target directory.

    Walks target_path, collects up to n_chunks non-empty JS files,
    reads the first 80 lines of each. Returns them concatenated with
    file headers. Pure filesystem operation — no RAG required.
    """
    target = Path(target_path)
    js_files = sorted(target.rglob("*.js"))[:n_chunks]
    chunks = []
    for f in js_files:
        try:
            lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
            sample = "\n".join(lines[:80])
            if sample.strip():
                rel = f.relative_to(target)
                chunks.append(f"// === {rel} ===\n{sample}")
        except Exception:
            continue
    return "\n\n".join(chunks) if chunks else "(no JS files found)"


def _validate_entry(entry: dict, existing_ids: set[str]) -> str | None:
    """Validate a proposed sink entry. Returns None if valid, error string if not."""
    required = {"id", "pattern", "kind", "severity", "description"}
    missing = required - set(entry.keys())
    if missing:
        return f"missing fields: {missing}"

    if entry.get("kind") != "sink":
        return f"kind must be 'sink', got {entry.get('kind')!r}"

    if entry["id"] in existing_ids:
        return f"duplicate id: {entry['id']!r}"

    if not re.match(r"^[a-z][a-z0-9_]*$", entry["id"]):
        return f"id must be snake_case: {entry['id']!r}"

    if entry.get("severity") not in ("high", "medium", "low"):
        return f"severity must be high/medium/low, got {entry.get('severity')!r}"

    try:
        re.compile(entry["pattern"])
    except re.error as e:
        return f"invalid regex {entry['pattern']!r}: {e}"

    return None


def expand_sinks(
    target_path: str,
    dry_run: bool = False,
    n_chunks: int = 20,
) -> list[dict]:
    """Call Claude to discover new sinks in target_path.

    Args:
        target_path: Path to the JS codebase to sample.
        dry_run:     If True, print proposed entries but don't write to disk.
        n_chunks:    Number of JS files to sample (default 20).

    Returns:
        List of validated new sink entries (empty if none found or API unavailable).
    """
    if not ANTHROPIC_API_KEY:
        warnings.warn("[sink_expander] ANTHROPIC_API_KEY not set — skipping", stacklevel=2)
        return []

    existing_ids = _load_existing_ids()
    code_chunks  = sample_codebase(target_path, n_chunks)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    user_msg = _EXPANDER_USER_TEMPLATE.format(
        existing_ids="\n".join(sorted(existing_ids)),
        code_chunks=code_chunks[:12_000],
    )

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2048,
            system=_EXPANDER_SYSTEM,
            messages=[{"role": "user", "content": user_msg}],
        )
        raw = "".join(
            b.text for b in response.content if hasattr(b, "text")
        ).strip()
    except Exception as exc:
        warnings.warn(f"[sink_expander] API call failed: {exc}", stacklevel=2)
        return []

    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"```\s*$", "", raw, flags=re.MULTILINE).strip()

    try:
        proposed: list[dict] = json.loads(raw)
    except json.JSONDecodeError as exc:
        warnings.warn(f"[sink_expander] JSON parse failed: {exc}\nraw={raw[:200]}", stacklevel=2)
        return []

    if not isinstance(proposed, list):
        warnings.warn(f"[sink_expander] expected list, got {type(proposed)}", stacklevel=2)
        return []

    valid: list[dict] = []
    for entry in proposed:
        err = _validate_entry(entry, existing_ids)
        if err:
            logger.warning(
                "sink_expander_invalid",
                error=err,
                entry_id=entry.get("id", "?"),
            )
        else:
            valid.append(entry)
            logger.info(
                "sink_expander_accepted",
                entry_id=entry["id"],
                severity=entry["severity"],
            )

    if not valid:
        logger.info("sink_expander_no_new_sinks")
        return []

    if dry_run:
        logger.info("sink_expander_dry_run", count=len(valid))
        logger.info("sink_expander_dry_run_entries", entries=valid)
        return valid

    existing_entries = []
    if EXTRA_SINKS_PATH.exists():
        existing_entries = json.loads(EXTRA_SINKS_PATH.read_text(encoding="utf-8"))

    existing_file_ids = {e["id"] for e in existing_entries}
    to_add = [e for e in valid if e["id"] not in existing_file_ids]

    if to_add:
        existing_entries.extend(to_add)
        EXTRA_SINKS_PATH.write_text(
            json.dumps(existing_entries, indent=2), encoding="utf-8"
        )
        logger.info("sink_expander_wrote", count=len(to_add))

    return to_add


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM sink expander")
    parser.add_argument("--target",   required=True, help="Path to JS codebase")
    parser.add_argument("--dry-run",  action="store_true", default=False)
    parser.add_argument("--chunks",   type=int, default=20,
                        help="Number of JS files to sample (default 20)")
    args = parser.parse_args()

    results = expand_sinks(args.target, dry_run=args.dry_run, n_chunks=args.chunks)
    if results:
        sys.exit(0)
    else:
        sys.exit(1)
