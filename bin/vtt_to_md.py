#!/usr/bin/env python3
"""Convert YouTube VTT subtitle files to clean markdown transcripts.

Usage:
    python3 bin/vtt_to_md.py <input_dir> <output_dir>

Strips timestamps, WEBVTT header, HTML tags, and deduplicates
consecutive repeated lines (common in YouTube auto-captions).
"""
import re
import sys
from pathlib import Path


def parse_vtt(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    prev = ""
    timestamp_re = re.compile(r"^\d{2}:\d{2}:\d{2}\.\d{3} --> ")
    tag_re = re.compile(r"<[^>]+>")

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:"):
            continue
        if timestamp_re.match(line):
            continue
        # strip inline tags like <00:00:01.234><c>word</c>
        line = tag_re.sub("", line).strip()
        if not line:
            continue
        # deduplicate consecutive repeated fragments
        if line == prev:
            continue
        # partial overlap dedup: skip if new line is a prefix of last
        if prev.startswith(line):
            continue
        out.append(line)
        prev = line

    # join into paragraphs (split on sentence boundaries)
    text = " ".join(out)
    # break on sentence end for readability
    text = re.sub(r"([.!?])\s+", r"\1\n\n", text)
    return text.strip()


def main() -> None:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input_dir> <output_dir>")
        sys.exit(1)

    in_dir = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)

    vtt_files = sorted(in_dir.glob("*.vtt"))
    if not vtt_files:
        print(f"No .vtt files found in {in_dir}")
        sys.exit(1)

    converted = 0
    for vtt in vtt_files:
        try:
            raw = vtt.read_text(encoding="utf-8", errors="replace")
            transcript = parse_vtt(raw)
            if not transcript:
                continue
            # stem = "ID - Title.en" → strip ".en" suffix
            stem = vtt.stem
            if stem.endswith(".en"):
                stem = stem[:-3]
            out_path = out_dir / f"{stem}.md"
            title = stem.split(" - ", 1)[-1] if " - " in stem else stem
            md = f"# {title}\n\n{transcript}\n"
            out_path.write_text(md, encoding="utf-8")
            converted += 1
        except Exception as e:
            print(f"ERROR {vtt.name}: {e}")

    print(f"Converted {converted}/{len(vtt_files)} files → {out_dir}")


if __name__ == "__main__":
    main()
