#!/usr/bin/env python3
"""Delete all chunks from a Chroma collection whose source path contains a given substring.

Usage:
    python3 bin/rag_purge_source.py <collection> <path_substring>

Example:
    python3 bin/rag_purge_source.py wiki portswigger-tv
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tlx"))

import chromadb

CHROMA_PATH = str(Path.home() / ".tlx" / "chroma")

def main() -> None:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <collection> <path_substring>")
        sys.exit(1)

    collection_name = sys.argv[1]
    substring = sys.argv[2]

    client = chromadb.PersistentClient(path=CHROMA_PATH)

    try:
        coll = client.get_collection(name=collection_name)
    except Exception:
        print(f"Collection '{collection_name}' not found.")
        sys.exit(1)

    # Fetch all IDs + metadata in batches
    batch = 1000
    offset = 0
    to_delete: list[str] = []

    while True:
        res = coll.get(limit=batch, offset=offset, include=["metadatas"])
        ids = res["ids"]
        metas = res["metadatas"]
        if not ids:
            break
        for id_, meta in zip(ids, metas):
            src = meta.get("source", "") if meta else ""
            if substring in src:
                to_delete.append(id_)
        offset += len(ids)
        if len(ids) < batch:
            break

    if not to_delete:
        print(f"No chunks found matching '{substring}' in collection '{collection_name}'.")
        return

    print(f"Deleting {len(to_delete)} chunks matching '{substring}'...")
    # Chroma delete in batches of 500
    for i in range(0, len(to_delete), 500):
        coll.delete(ids=to_delete[i:i+500])

    print(f"Done. {len(to_delete)} chunks removed.")

if __name__ == "__main__":
    main()
