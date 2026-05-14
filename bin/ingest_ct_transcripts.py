"""Phase 1: Ingest Critical Thinking podcast transcripts into wiki Chroma collection.

Per-chunk metadata:
  source: "ct_podcast"
  source_uri: wiki://podcasts/ct/<base>#chunk-N
  ep_no: int | None
  video_id: 11-char yt id
  title: human title (spaces)
  date: YYYY-MM-DD
  asr_quality: "low" | "normal"

Idempotency: deterministic IDs ctpod:<base>:chunk-<N>.
If first chunk ID exists in coll, episode is skipped.

Chunking: 6000 chars window, 800 overlap (≈1500/200 tokens). Skip <200-char chunks.

Progress log: append-only JSONL at wiki/sources/podcasts/ct/whisper/_rag_log.jsonl
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TRANSCRIPTS = REPO / "wiki" / "sources" / "podcasts" / "ct" / "whisper" / "transcripts"
LOG_PATH = REPO / "wiki" / "sources" / "podcasts" / "ct" / "whisper" / "_rag_log.jsonl"
COLLECTION = "wiki"
CHROMA_PATH = str(Path.home() / ".tlx" / "chroma")

CHUNK_CHARS = 6000
OVERLAP_CHARS = 800
MIN_CHUNK_CHARS = 200

# Whisper hallucination heuristic: high density of capitalized tokens
# suggests fabricated proper nouns. Threshold tuned for 6000-char chunks.
CAP_TOKEN_THRESHOLD = 25

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
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        os.environ.setdefault(k, v)


_FILENAME_RE = re.compile(
    r"^(?P<date>\d{8})_(?P<vid>[A-Za-z0-9_-]{11})_(?P<rest>.+)$"
)
_EP_RE = re.compile(r"_(?:Ep\.?|EP\.?)_?(\d+)$")
_CAP_TOKEN_RE = re.compile(r"\b[A-Z][a-zA-Z]{2,}\b")


def parse_filename(stem: str) -> dict | None:
    m = _FILENAME_RE.match(stem)
    if not m:
        return None
    date_raw = m.group("date")
    vid = m.group("vid")
    rest = m.group("rest")
    ep = None
    em = _EP_RE.search(rest)
    if em:
        ep = int(em.group(1))
        rest = rest[: em.start()]
    title = rest.replace("_", " ").strip()
    date_iso = f"{date_raw[:4]}-{date_raw[4:6]}-{date_raw[6:]}"
    return {
        "date": date_iso,
        "video_id": vid,
        "title": title,
        "ep_no": ep,
        "base": stem,
    }


def chunk_text(text: str) -> list[str]:
    if not text:
        return []
    text = text.strip()
    if len(text) <= CHUNK_CHARS:
        return [text] if len(text) >= MIN_CHUNK_CHARS else []
    out: list[str] = []
    step = CHUNK_CHARS - OVERLAP_CHARS
    i = 0
    while i < len(text):
        c = text[i:i + CHUNK_CHARS]
        if len(c) >= MIN_CHUNK_CHARS:
            out.append(c)
        i += step
    return out


def asr_quality_for(chunk: str) -> str:
    caps = _CAP_TOKEN_RE.findall(chunk)
    unique = set(caps)
    return "low" if len(unique) > CAP_TOKEN_THRESHOLD else "normal"


def log_event(ev: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a") as f:
        f.write(json.dumps(ev) + "\n")


async def main() -> None:
    _load_env()
    if not os.environ.get("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY missing in env/.env", file=sys.stderr)
        sys.exit(1)

    import chromadb
    from kernel.embedders.google import GoogleEmbedder

    embedder = GoogleEmbedder()
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    coll = client.get_or_create_collection(name=COLLECTION)

    files = sorted(TRANSCRIPTS.glob("*.txt"))
    print(f"[ingest] found {len(files)} transcripts")

    only_count = os.environ.get("CT_INGEST_LIMIT")
    if only_count:
        files = files[: int(only_count)]
        print(f"[ingest] limited to first {len(files)} for test run")

    started = time.time()
    total_chunks = 0
    embedded_chunks = 0
    skipped_eps = 0
    failed_eps = 0

    for path in files:
        stem = path.stem
        meta_base = parse_filename(stem)
        if not meta_base:
            print(f"[skip] unparsable filename: {stem}")
            log_event({
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "base": stem, "status": "skip_unparseable",
            })
            continue

        base = meta_base["base"]
        first_id = f"ctpod:{base}:chunk-0"
        try:
            existing = await asyncio.to_thread(
                coll.get, ids=[first_id], include=[]
            )
            if existing.get("ids"):
                skipped_eps += 1
                print(f"[skip-exist] {base}")
                continue
        except Exception:
            pass

        try:
            raw = path.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            failed_eps += 1
            log_event({"base": base, "status": "read_failed", "error": str(e)})
            continue

        chunks = chunk_text(raw)
        if not chunks:
            log_event({"base": base, "status": "no_content", "chunks": 0})
            continue

        ids: list[str] = []
        docs: list[str] = []
        metas: list[dict] = []
        for i, ch in enumerate(chunks):
            ids.append(f"ctpod:{base}:chunk-{i}")
            docs.append(ch)
            metas.append({
                "source": "ct_podcast",
                "source_uri": f"wiki://podcasts/ct/{base}#chunk-{i}",
                "ep_no": meta_base["ep_no"] if meta_base["ep_no"] is not None else -1,
                "video_id": meta_base["video_id"],
                "title": meta_base["title"],
                "date": meta_base["date"],
                "asr_quality": asr_quality_for(ch),
                "chunk_idx": i,
            })

        total_chunks += len(chunks)
        ep_started = time.time()
        try:
            vecs = await embedder.embed(docs)
        except Exception as e:
            failed_eps += 1
            print(f"[FAIL embed] {base}: {e}")
            log_event({
                "base": base, "status": "embed_failed",
                "error": f"{type(e).__name__}: {e}",
            })
            continue

        UPSERT_BATCH = 5000
        try:
            for s in range(0, len(ids), UPSERT_BATCH):
                e = s + UPSERT_BATCH
                await asyncio.to_thread(
                    coll.upsert,
                    ids=ids[s:e],
                    embeddings=vecs[s:e],
                    documents=docs[s:e],
                    metadatas=metas[s:e],
                )
        except Exception as e:
            failed_eps += 1
            print(f"[FAIL upsert] {base}: {e}")
            log_event({
                "base": base, "status": "upsert_failed",
                "error": f"{type(e).__name__}: {e}",
                "chunks": len(chunks),
            })
            continue

        embedded_chunks += len(chunks)
        elapsed = time.time() - ep_started
        print(
            f"[ok] {base} chunks={len(chunks)} t={elapsed:.1f}s "
            f"ep={meta_base['ep_no']} date={meta_base['date']}"
        )
        log_event({
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "base": base,
            "status": "ingested",
            "ep_no": meta_base["ep_no"],
            "date": meta_base["date"],
            "title": meta_base["title"],
            "video_id": meta_base["video_id"],
            "chunks": len(chunks),
            "elapsed_sec": round(elapsed, 1),
        })

    total = time.time() - started
    print(
        f"\n[done] eps_total={len(files)} embedded_chunks={embedded_chunks} "
        f"skipped={skipped_eps} failed={failed_eps} elapsed={total:.0f}s"
    )
    log_event({
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "summary": True,
        "eps_total": len(files),
        "embedded_chunks": embedded_chunks,
        "total_chunks_seen": total_chunks,
        "skipped_eps": skipped_eps,
        "failed_eps": failed_eps,
        "elapsed_sec": round(total, 0),
    })


if __name__ == "__main__":
    asyncio.run(main())
