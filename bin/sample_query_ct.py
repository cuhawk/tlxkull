"""Phase 1 verification: run 3 sample queries against wiki collection.

Reports top-K hits per query, filtered to source=ct_podcast.
Prints a Markdown table of {query, top_ep, score, snippet} for the summary doc.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tlx"))


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


QUERIES = [
    "hop by hop headers smuggling",
    "CSS injection text node leak",
    "WordPress plugin methodology",
]


async def main() -> None:
    _load_env()
    if not os.environ.get("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY missing", file=sys.stderr)
        sys.exit(1)

    import chromadb
    from kernel.embedders.google import GoogleEmbedder

    embedder = GoogleEmbedder()
    client = chromadb.PersistentClient(
        path=str(Path.home() / ".tlx" / "chroma"),
    )
    coll = client.get_or_create_collection(name="wiki")

    out = []
    for q in QUERIES:
        qvec = (await embedder.embed([q]))[0]
        res = await asyncio.to_thread(
            coll.query, query_embeddings=[qvec], n_results=8
        )
        docs = (res.get("documents") or [[]])[0]
        metas = (res.get("metadatas") or [[]])[0]
        dists = (res.get("distances") or [[]])[0]
        # filter to ct_podcast
        ct = []
        for d, m, dist in zip(docs, metas, dists):
            if m.get("source") == "ct_podcast":
                ct.append({
                    "ep": m.get("ep_no"),
                    "title": m.get("title"),
                    "date": m.get("date"),
                    "score": round(1 - dist, 4),
                    "snippet": d[:200].replace("\n", " "),
                    "uri": m.get("source_uri"),
                })
        out.append({"query": q, "ct_hits": len(ct), "top": ct[:3]})

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
