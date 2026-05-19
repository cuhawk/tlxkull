"""V2 §21 — Multi-target correlation engine.

Bundle / SDK fingerprinting + cross-target reuse detection. Stores
fingerprints under ``~/.tlx/corr/``. Read/write helpers only; the
correlation queries happen via the CLI driver.

Off by default; ``JS_ENABLE_MULTI_TARGET_CORR=1`` to enable.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

__all__ = [
    "BundleFingerprint",
    "compute_fingerprint",
    "save_fingerprint",
    "load_target_fingerprints",
    "match_against_corpus",
    "shingles_of",
    "shingle_jaccard",
    "find_shared_sanitizers",
    "find_shared_gadgets",
    "CORPUS_ROOT",
]


CORPUS_ROOT = Path(os.environ.get(
    "JS_CORR_CORPUS_ROOT",
    str(Path.home() / ".tlx" / "corr"),
))


@dataclass
class BundleFingerprint:
    bundle_id: str
    target: str
    file: str
    size_bytes: int = 0
    qname_top_100: list[str] = field(default_factory=list)
    framework_set: list[str] = field(default_factory=list)
    framework_versions: dict[str, str] = field(default_factory=dict)
    sanitizer_set: list[dict] = field(default_factory=list)
    # Trigram shingle hashes over the qname sequence — used for the
    # content-shingle Jaccard distance below.
    qname_shingles: list[str] = field(default_factory=list)
    # Gadget catalog key_paths matched against this bundle.
    pp_gadget_keys: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def shingles_of(qnames: list[str], *, k: int = 3) -> list[str]:
    """SHA-256 trigram shingles over the qname leaf tokens."""
    if not qnames:
        return []
    leaves = [q.split("::")[-1] for q in qnames]
    out: list[str] = []
    for i in range(0, max(0, len(leaves) - k + 1)):
        token = "|".join(leaves[i : i + k])
        out.append(_sha256_str(token))
    # Cap so absurd bundles don't bloat the on-disk fingerprint.
    return out[:5000]


def shingle_jaccard(a: list[str], b: list[str]) -> float:
    if not (a and b):
        return 0.0
    sa, sb = set(a), set(b)
    inter = len(sa & sb)
    if not inter:
        return 0.0
    return inter / len(sa | sb)


def _sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="ignore")).hexdigest()


def compute_fingerprint(
    conn: sqlite3.Connection,
    *,
    target_name: str,
    bundle_file: str | None = None,
    frameworks: list[str] | None = None,
    library_versions: dict[str, str] | None = None,
) -> list[BundleFingerprint]:
    """One BundleFingerprint per distinct file in nodes."""
    files = [f for (f,) in conn.execute(
        "SELECT DISTINCT file FROM nodes WHERE file IS NOT NULL"
    )]
    if bundle_file is not None:
        files = [bundle_file]
    pp_keys = _pp_gadget_keys(conn)
    out: list[BundleFingerprint] = []
    for file in files:
        rows = conn.execute(
            "SELECT qualified_name FROM nodes WHERE file = ? "
            "ORDER BY id",
            (file,),
        ).fetchall()
        qnames = [q for (q,) in rows]
        if not qnames:
            continue
        # Bundle id: sha256 of the qname list (stable across re-indexes
        # unless the bundle truly changed).
        bid = _sha256_str("\n".join(qnames))
        ctr = Counter(q.split("::")[-1] for q in qnames)
        top100 = [name for name, _ in ctr.most_common(100)]
        fp = BundleFingerprint(
            bundle_id=bid,
            target=target_name,
            file=file,
            size_bytes=0,
            qname_top_100=top100,
            framework_set=list(frameworks or []),
            framework_versions=dict(library_versions or {}),
            sanitizer_set=_sanitizer_set(conn),
            qname_shingles=shingles_of(qnames),
            pp_gadget_keys=pp_keys,
        )
        out.append(fp)
    return out


def _pp_gadget_keys(conn: sqlite3.Connection) -> list[str]:
    try:
        rows = conn.execute("SELECT key_path FROM pp_gadgets").fetchall()
    except sqlite3.OperationalError:
        return []
    return sorted({r[0] for r in rows if r[0]})


def _sanitizer_set(conn: sqlite3.Connection) -> list[dict]:
    out: list[dict] = []
    try:
        for taxid, n in conn.execute(
            "SELECT taxonomy_id, COUNT(*) FROM node_sanitizers GROUP BY taxonomy_id"
        ):
            out.append({"name": taxid, "count": int(n)})
    except sqlite3.OperationalError:
        pass
    return out


def save_fingerprint(fp: BundleFingerprint) -> Path:
    CORPUS_ROOT.mkdir(parents=True, exist_ok=True)
    (CORPUS_ROOT / "bundles").mkdir(parents=True, exist_ok=True)
    p = CORPUS_ROOT / "bundles" / f"{fp.bundle_id}.json"
    p.write_text(json.dumps(fp.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return p


def load_target_fingerprints(target_name: str) -> list[BundleFingerprint]:
    out: list[BundleFingerprint] = []
    if not CORPUS_ROOT.exists():
        return out
    for f in (CORPUS_ROOT / "bundles").glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if data.get("target") != target_name:
            continue
        out.append(BundleFingerprint(**{
            k: v for k, v in data.items()
            if k in BundleFingerprint.__dataclass_fields__
        }))
    return out


def match_against_corpus(fp: BundleFingerprint, *, threshold: float = 0.3) -> list[dict]:
    """Match bundles in the corpus against ``fp`` using two distances:

      * Jaccard over the top-100 qname sets (cheap, broad)
      * Trigram-shingle Jaccard (content-aware; ranks first)

    Returns matches with both scores and the shared sanitizers + gadget
    keys for downstream reuse-detection.
    """
    if not (CORPUS_ROOT / "bundles").exists():
        return []
    own_top = set(fp.qname_top_100)
    if not own_top:
        return []
    matches: list[dict] = []
    for f in (CORPUS_ROOT / "bundles").glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if data.get("bundle_id") == fp.bundle_id and data.get("target") == fp.target:
            continue
        other_top = set(data.get("qname_top_100") or [])
        if not other_top:
            continue
        overlap = own_top & other_top
        top_jaccard = len(overlap) / len(own_top | other_top) if overlap else 0.0
        shingle = shingle_jaccard(fp.qname_shingles, data.get("qname_shingles") or [])
        score = max(top_jaccard, shingle)
        if score < threshold:
            continue
        matches.append({
            "bundle_id": data["bundle_id"],
            "target": data.get("target"),
            "file": data.get("file"),
            "score": round(score, 3),
            "top_jaccard": round(top_jaccard, 3),
            "shingle_jaccard": round(shingle, 3),
            "overlap_count": len(overlap),
            "shared_sanitizers": find_shared_sanitizers(fp, data),
            "shared_gadgets": find_shared_gadgets(fp, data),
            "shared_frameworks": sorted(
                set(fp.framework_set) & set(data.get("framework_set") or [])
            ),
        })
    matches.sort(key=lambda m: -m["score"])
    return matches


def find_shared_sanitizers(
    fp: BundleFingerprint, other_data: dict
) -> list[str]:
    own = {s.get("name") for s in (fp.sanitizer_set or []) if isinstance(s, dict)}
    oth = {s.get("name") for s in (other_data.get("sanitizer_set") or [])
           if isinstance(s, dict)}
    return sorted(x for x in (own & oth) if x)


def find_shared_gadgets(fp: BundleFingerprint, other_data: dict) -> list[str]:
    own = set(fp.pp_gadget_keys or [])
    oth = set(other_data.get("pp_gadget_keys") or [])
    return sorted(own & oth)
