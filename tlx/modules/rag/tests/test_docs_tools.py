"""Tests for modules/rag/tools.py — chromadb fully mocked."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from modules.rag.tools import _chunk, _load_text


class _Cfg(BaseModel):
    chroma_path: str = "/tmp/test_chroma"
    collection: str = "default"
    top_k: int = 5
    chunk_size: int = 800
    chunk_overlap: int = 100


# _chunk
def test_chunk_basic():
    chunks = _chunk("a" * 30, size=10, overlap=2)
    assert len(chunks) == 4  # step=8, 0,8,16,24
    assert all(len(c) <= 10 for c in chunks)


def test_chunk_overlap_content():
    text = "abcdefghij"
    chunks = _chunk(text, size=6, overlap=2)
    assert chunks[0] == "abcdef"
    assert chunks[1] == "efghij"


def test_chunk_single_when_text_fits():
    assert _chunk("hello", size=100, overlap=10) == ["hello"]


# _load_text
def test_load_text_unsupported_raises(tmp_path):
    p = tmp_path / "x.xyz"
    p.write_text("hi")
    with pytest.raises(ValueError, match="Unsupported"):
        _load_text(str(p))


def test_load_text_md(tmp_path):
    p = tmp_path / "x.md"
    p.write_text("# heading")
    assert _load_text(str(p)) == "# heading"


# docs_ingest
@pytest.mark.asyncio
async def test_docs_ingest_calls_col_upsert():
    from modules.rag.tools import docs_ingest
    cfg = _Cfg()
    mock_col = MagicMock()
    mock_col.upsert = MagicMock()
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_col

    with patch("modules.rag.tools.chromadb", create=True) as mock_chroma, \
         patch("modules.rag.tools._load_text", return_value="x" * 1000):
        mock_chroma.PersistentClient.return_value = mock_client
        result = json.loads(await docs_ingest("/fake/doc.md", "default", cfg))

    assert result["ingested"] > 0
    assert mock_col.upsert.called
    call_kwargs = mock_col.upsert.call_args.kwargs
    assert len(call_kwargs["documents"]) == result["ingested"]


# docs_query
@pytest.mark.asyncio
async def test_docs_query_returns_formatted_list():
    from modules.rag.tools import docs_query
    cfg = _Cfg()
    mock_col = MagicMock()
    mock_col.query.return_value = {
        "documents": [["chunk text"]],
        "metadatas": [[{"source": "/fake/doc.md", "chunk_idx": 0}]],
        "distances": [[0.1]],
    }
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_col

    with patch("modules.rag.tools.chromadb", create=True) as mock_chroma:
        mock_chroma.PersistentClient.return_value = mock_client
        result = json.loads(await docs_query("test question", "default", 1, cfg))

    assert len(result) == 1
    assert result[0]["text"] == "chunk text"
    assert result[0]["source"] == "/fake/doc.md"
    assert result[0]["score"] == pytest.approx(0.9)


# docs_list
@pytest.mark.asyncio
async def test_docs_list_returns_collection_names():
    from modules.rag.tools import docs_list
    cfg = _Cfg()
    col1 = MagicMock()
    col1.name = "default"
    col1.count.return_value = 42
    mock_client = MagicMock()
    mock_client.list_collections.return_value = [col1]

    with patch("modules.rag.tools.chromadb", create=True) as mock_chroma:
        mock_chroma.PersistentClient.return_value = mock_client
        result = json.loads(await docs_list(cfg))

    assert result[0]["name"] == "default"
    assert result[0]["count"] == 42


@pytest.mark.asyncio
async def test_docs_ingest_wraps_col_upsert_in_to_thread():
    from modules.rag import tools as docs_tools
    cfg = _Cfg()
    mock_col = MagicMock()
    mock_col.upsert = MagicMock()
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_col

    real_to_thread = docs_tools.asyncio.to_thread
    calls = []

    async def spy_to_thread(fn, *args, **kwargs):
        calls.append(fn)
        return await real_to_thread(fn, *args, **kwargs)

    with patch("modules.rag.tools.chromadb", create=True) as mock_chroma, \
         patch("modules.rag.tools._load_text", return_value="x" * 1000), \
         patch("modules.rag.tools.asyncio.to_thread", side_effect=spy_to_thread):
        mock_chroma.PersistentClient.return_value = mock_client
        await docs_tools.docs_ingest("/fake/doc.md", "default", cfg)

    assert mock_col.upsert in calls


@pytest.mark.asyncio
async def test_docs_ingest_load_failure_returns_json_error():
    from modules.rag.tools import docs_ingest
    cfg = _Cfg()
    with patch(
        "modules.rag.tools._load_text",
        side_effect=FileNotFoundError("nope"),
    ):
        result = json.loads(await docs_ingest("/missing.md", "default", cfg))
    assert "error" in result
    assert result["error"].startswith("load_failed:")
    assert result["path"] == "/missing.md"


@pytest.mark.asyncio
async def test_docs_ingest_chroma_failure_returns_json_error():
    from modules.rag.tools import docs_ingest
    cfg = _Cfg()
    mock_col = MagicMock()
    mock_col.upsert = MagicMock(side_effect=RuntimeError("chroma boom"))
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_col

    with patch("modules.rag.tools.chromadb", create=True) as mock_chroma, \
         patch("modules.rag.tools._load_text", return_value="x" * 1000):
        mock_chroma.PersistentClient.return_value = mock_client
        result = json.loads(await docs_ingest("/fake/doc.md", "default", cfg))

    assert "error" in result
    assert result["error"].startswith("chroma_failed:")
    assert result["chunks"] > 0


@pytest.mark.asyncio
async def test_docs_ingest_js_file_uses_code_chunker(tmp_path):
    from modules.rag.tools import docs_ingest
    js_text = (
        "// header\n\n"
        + "function foo() {\n  return 1;\n}\n\n"
        + "function bar() {\n  return 2;\n}\n"
    )
    p = tmp_path / "app.js"
    p.write_text(js_text)

    cfg = _Cfg(chunk_size=50, chunk_overlap=5)
    mock_col = MagicMock()
    mock_col.upsert = MagicMock()
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_col

    with patch("modules.rag.tools.chromadb", create=True) as mock_chroma:
        mock_chroma.PersistentClient.return_value = mock_client
        await docs_ingest(str(p), "default", cfg)

    docs = mock_col.upsert.call_args.kwargs["documents"]
    joined = "".join(docs)
    assert joined == js_text
    assert any("function foo" in d and "function bar" not in d for d in docs)
    assert any("function bar" in d and "function foo" not in d for d in docs)


@pytest.mark.asyncio
async def test_docs_ingest_dir_ingests_multiple_files(tmp_path):
    from modules.rag.tools import docs_ingest_dir
    (tmp_path / "a.js").write_text("function a() {}\n")
    (tmp_path / "b.js").write_text("function b() {}\n")

    cfg = _Cfg()
    mock_col = MagicMock()
    mock_col.upsert = MagicMock()
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_col

    with patch("modules.rag.tools.chromadb", create=True) as mock_chroma:
        mock_chroma.PersistentClient.return_value = mock_client
        result = json.loads(
            await docs_ingest_dir(str(tmp_path), "*.js", "default", cfg)
        )

    assert result["files_processed"] == 2
    assert result["total_chunks"] >= 2
    names = sorted(r["file"] for r in result["results"])
    assert names == ["a.js", "b.js"]


def test_chunk_code_splits_on_function_boundary():
    from modules.rag.tools import _chunk_code
    text = "// preamble\nfunction foo() {\n  return 1;\n}\n\nfunction bar() {\n  return 2;\n}\n"
    chunks = _chunk_code(text, size=50, overlap=5)
    assert len(chunks) >= 2
    assert any("function foo" in c and "function bar" not in c for c in chunks)
    assert any("function bar" in c and "function foo" not in c for c in chunks)


def test_chunk_code_falls_back_on_oversized_declaration():
    from modules.rag.tools import _chunk_code
    body = "x" * 300
    text = f"\nfunction huge() {{\n{body}\n}}\n"
    chunks = _chunk_code(text, size=100, overlap=10)
    assert len(chunks) > 1
    assert all(len(c) <= 100 for c in chunks)


def test_load_text_js_returns_content(tmp_path):
    p = tmp_path / "app.js"
    p.write_text("const x = 1;\n")
    assert _load_text(str(p)) == "const x = 1;\n"


def test_load_text_ts_returns_content(tmp_path):
    p = tmp_path / "app.ts"
    p.write_text("const x: number = 1;\n")
    assert _load_text(str(p)) == "const x: number = 1;\n"


def test_load_pdf_handles_none_pages(tmp_path):
    from modules.rag.tools import _load_pdf

    class _FakePage:
        def extract_text(self):
            return None

    class _FakePdf:
        pages = [_FakePage(), _FakePage()]

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    fake_pdfplumber = MagicMock()
    fake_pdfplumber.open.return_value = _FakePdf()

    with patch.dict("sys.modules", {"pdfplumber": fake_pdfplumber}):
        result = _load_pdf(tmp_path / "x.pdf")
    assert result == "\n"


# module registration
def test_module_registers_four_tools():
    import types

    from modules.rag.module import MODULE, _register
    registered = []

    class _Reg:
        def register(self, t):
            registered.append(t)

    kernel = types.SimpleNamespace(tools=_Reg())
    _register(kernel, None)
    names = sorted(t.name for t in registered)
    assert names == [
        "docs_ingest",
        "docs_ingest_dir",
        "docs_list",
        "docs_query",
    ]
    assert MODULE.name == "docs"


@pytest.mark.asyncio
async def test_docs_ingest_dir_excludes_node_modules(tmp_path):
    from modules.rag.tools import docs_ingest_dir

    (tmp_path / "app.js").write_text("const x = 1;\n")
    nm = tmp_path / "node_modules" / "lib"
    nm.mkdir(parents=True)
    (nm / "vendor.js").write_text("vendor code\n")

    cfg = _Cfg()
    mock_col = MagicMock()
    mock_col.upsert = MagicMock()
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_col

    with patch("modules.rag.tools.chromadb", create=True) as mock_chroma:
        mock_chroma.PersistentClient.return_value = mock_client
        result = json.loads(
            await docs_ingest_dir(str(tmp_path), "**/*.js", "default", cfg)
        )

    assert result["files_processed"] == 1
    assert result["results"][0]["file"] == "app.js"


@pytest.mark.asyncio
async def test_docs_ingest_dir_skips_minified(tmp_path):
    from modules.rag.tools import docs_ingest_dir

    (tmp_path / "app.js").write_text("const x = 1;\n")
    (tmp_path / "app.min.js").write_text("const x=1;\n")

    cfg = _Cfg()
    mock_col = MagicMock()
    mock_col.upsert = MagicMock()
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_col

    with patch("modules.rag.tools.chromadb", create=True) as mock_chroma:
        mock_chroma.PersistentClient.return_value = mock_client
        result = json.loads(
            await docs_ingest_dir(str(tmp_path), "*.js", "default", cfg)
        )

    assert result["files_processed"] == 1
    assert result["results"][0]["file"] == "app.js"


@pytest.mark.asyncio
async def test_docs_ingest_dir_too_many_files_returns_error(tmp_path):
    from modules.rag.tools import docs_ingest_dir

    for i in range(201):
        (tmp_path / f"f{i}.js").write_text("x\n")

    cfg = _Cfg()
    result = json.loads(
        await docs_ingest_dir(str(tmp_path), "*.js", "default", cfg)
    )

    assert result["error"] == "too_many_files"
    assert result["count"] == 201
    assert "hint" in result


@pytest.mark.asyncio
async def test_docs_ingest_upsert_on_reingest(tmp_path):
    """Ingesting the same file twice must not raise — uses upsert.

    Each ingest does 2 upserts (sentinel marker + chunks). With MagicMock
    col.get not returning a real dict, the sha256 cache check returns None
    so both ingests proceed.
    """
    from modules.rag.tools import docs_ingest
    cfg = _Cfg()
    mock_col = MagicMock()
    mock_col.upsert = MagicMock()
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_col

    with patch("modules.rag.tools.chromadb", create=True) as mock_chroma, \
         patch("modules.rag.tools._load_text", return_value="hello world content"):
        mock_chroma.PersistentClient.return_value = mock_client
        await docs_ingest("/fake/doc.md", "default", cfg)
        await docs_ingest("/fake/doc.md", "default", cfg)

    assert mock_col.upsert.call_count == 4
    assert not hasattr(mock_col, 'add') or mock_col.add.call_count == 0


# --- Phase 7C Task 3: incremental ingest via sha256 ---


@pytest.mark.asyncio
async def test_docs_ingest_first_call_upserts(tmp_path):
    from modules.rag.tools import docs_ingest
    cfg = _Cfg()
    mock_col = MagicMock()
    mock_col.upsert = MagicMock()
    mock_col.get.return_value = {"metadatas": []}
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_col

    with patch("modules.rag.tools.chromadb", create=True) as mock_chroma, \
         patch("modules.rag.tools._load_text", return_value="content v1"):
        mock_chroma.PersistentClient.return_value = mock_client
        result = json.loads(
            await docs_ingest("/fake/doc.md", "default", cfg)
        )

    assert mock_col.upsert.called
    assert result.get("ingested", 0) > 0


@pytest.mark.asyncio
async def test_docs_ingest_skips_when_sha256_matches(tmp_path):
    """When stored sha256 == current, upsert must be skipped entirely."""
    import hashlib

    from modules.rag.tools import docs_ingest
    cfg = _Cfg()

    text = "content v1"
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()

    mock_col = MagicMock()
    mock_col.upsert = MagicMock()
    mock_col.get.return_value = {
        "ids": ["/fake/doc.md"],
        "metadatas": [{"sha256": digest, "marker": True}],
    }
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_col

    with patch("modules.rag.tools.chromadb", create=True) as mock_chroma, \
         patch("modules.rag.tools._load_text", return_value=text):
        mock_chroma.PersistentClient.return_value = mock_client
        result = json.loads(
            await docs_ingest("/fake/doc.md", "default", cfg)
        )

    assert mock_col.upsert.called is False
    assert result.get("skipped") is True


@pytest.mark.asyncio
async def test_docs_ingest_modified_content_triggers_upsert(tmp_path):
    """Different content sha256 → not unchanged → upsert proceeds."""
    from modules.rag.tools import docs_ingest
    cfg = _Cfg()

    mock_col = MagicMock()
    mock_col.upsert = MagicMock()
    mock_col.get.return_value = {
        "ids": ["/fake/doc.md"],
        "metadatas": [{"sha256": "stale-hash-value", "marker": True}],
    }
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_col

    with patch("modules.rag.tools.chromadb", create=True) as mock_chroma, \
         patch("modules.rag.tools._load_text", return_value="content v2"):
        mock_chroma.PersistentClient.return_value = mock_client
        await docs_ingest("/fake/doc.md", "default", cfg)

    assert mock_col.upsert.called is True


@pytest.mark.asyncio
async def test_docs_list_uses_to_thread(tmp_path):
    """docs_list must not call c.count() on the event loop thread."""
    from modules.rag.tools import docs_list
    cfg = _Cfg()

    with patch("modules.rag.tools.asyncio.to_thread") as mock_to_thread:
        mock_to_thread.return_value = [("default", 5)]
        result = json.loads(await docs_list(cfg))

    assert mock_to_thread.called
    assert result == [{"name": "default", "count": 5}]
