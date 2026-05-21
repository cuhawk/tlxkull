"""Re-embed Phase 2 wiki pages (CT source pages + new technique pages)
into the `wiki` Chroma collection so docs_query reflects fresh content.

Skips _external/ and _lint_*.md.
Uses docs_ingest_dir per class folder to stay under 200-file cap.
"""
import asyncio
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TLX = REPO / "tlx"
sys.path.insert(0, str(TLX))


def _load_env() -> None:
    env_path = REPO / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


async def main() -> None:
    _load_env()
    if not os.environ.get("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY missing", file=sys.stderr)
        sys.exit(1)

    from modules.rag.module import DocsConfig
    from modules.rag.tools import docs_ingest_dir
    from kernel.embedders.google import GoogleEmbedder
    from kernel.embedders.chroma_adapter import make_chroma_adapter

    cfg = DocsConfig(collection="wiki")
    embedder = GoogleEmbedder()
    ef = make_chroma_adapter(embedder)

    targets = [
        (str(REPO / "wiki" / "sources" / "podcasts" / "ct"), "*.md"),
        (str(REPO / "wiki" / "sources" / "podcasts" / "bbre"), "*.md"),
        (str(REPO / "wiki" / "techniques" / "dom-xss"), "*.md"),
        (str(REPO / "wiki" / "techniques" / "oauth"), "*.md"),
        (str(REPO / "wiki" / "techniques" / "saml"), "*.md"),
        (str(REPO / "wiki" / "techniques" / "server-side"), "*.md"),
        (str(REPO / "wiki" / "techniques" / "csp"), "*.md"),
        (str(REPO / "wiki" / "techniques" / "csrf"), "*.md"),
        (str(REPO / "wiki" / "techniques" / "css-injection"), "*.md"),
        (str(REPO / "wiki" / "techniques" / "idor"), "*.md"),
        (str(REPO / "wiki" / "techniques" / "jwt"), "*.md"),
        (str(REPO / "wiki" / "techniques" / "mobile"), "*.md"),
        (str(REPO / "wiki" / "techniques" / "postmessage"), "*.md"),
        (str(REPO / "wiki" / "techniques" / "prototype-pollution"), "*.md"),
        (str(REPO / "wiki" / "techniques" / "race-conditions"), "*.md"),
        (str(REPO / "wiki" / "techniques" / "recon"), "*.md"),
        (str(REPO / "wiki" / "techniques" / "supply-chain"), "*.md"),
        (str(REPO / "wiki" / "techniques" / "wordpress"), "*.md"),
        (str(REPO / "wiki" / "techniques" / "xs-leaks"), "*.md"),
        (str(REPO / "wiki" / "tools"), "**/*.md"),
        (str(REPO / "wiki" / "targets"), "*.md"),
    ]

    total = 0
    skipped = 0
    for directory, glob in targets:
        if not Path(directory).exists():
            print(f"SKIP (missing): {directory}")
            continue
        print(f"INGEST {directory} {glob}")
        try:
            result = await docs_ingest_dir(
                directory=directory,
                glob=glob,
                collection="wiki",
                cfg=cfg,
                embedding_function=ef,
            )
            import json
            r = json.loads(result)
            if "error" in r:
                print(f"  ERR: {r['error']}")
                continue
            total += r.get("total_chunks", 0)
            for fr in r.get("results", []):
                if fr.get("skipped"):
                    skipped += 1
            print(f"  -> files={r.get('files_processed')} chunks={r.get('total_chunks')} skipped={skipped}")
        except Exception as exc:
            print(f"  EX: {exc}")

    print(f"\n[done] total_new_chunks={total}")


if __name__ == "__main__":
    asyncio.run(main())
